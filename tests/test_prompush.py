import http.server
import queue
import threading

import pytest
import requests
import weewx.restx
from prometheus_client.parser import text_string_to_metric_families
import prompush


def test_post_to_pushgateway_and_preserve_missing():
    received = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            received.append((self.path, self.rfile.read(int(self.headers['Content-Length'])).decode()))
            self.send_response(202)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        worker = prompush.PromPushThread(queue.Queue(), None, host='127.0.0.1', port=str(server.server_port), job='weather', instance='roof', timeout=1)
        worker.process_record({'dateTime':1700000000, 'outTemp':0, 'windDir':None}, None)
        assert received[0][0] == '/metrics/job/weather/instance/roof'
        samples = {s.name:s.value for f in text_string_to_metric_families(received[0][1]) for s in f.samples}
        assert samples['outTemp'] == 0
        assert 'windDir' not in samples
        worker.skip_post = True
        worker.process_record({'outTemp':99}, None)
        assert len(received) == 1
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_failures_are_not_silently_successful(monkeypatch):
    worker = prompush.PromPushThread(queue.Queue(), None, timeout=1, retry_wait=0)
    response = requests.Response()
    response.status_code = 500
    monkeypatch.setattr(requests, 'post', lambda **kw: response)
    with pytest.raises(weewx.restx.FailedPost):
        worker.post_metrics('outTemp 0\n')


def test_failed_post_is_retried(monkeypatch):
    calls = []
    sleeps = []
    response = requests.Response()
    response.status_code = 202

    def post(**kw):
        calls.append(kw['url'])
        if len(calls) == 1:
            raise requests.ConnectionError('Connection refused')
        return response

    monkeypatch.setattr(requests, 'post', post)
    monkeypatch.setattr(prompush.time, 'sleep', sleeps.append)
    worker = prompush.PromPushThread(queue.Queue(), None, max_tries=2, retry_wait=7)
    worker.post_metrics('outTemp 0\n')
    assert len(calls) == 2
    assert sleeps == [7]


def start_service(monkeypatch, tmp_path, options):
    import configobj
    logged = []

    class Engine:
        def bind(self, *args):
            pass

    config = configobj.ConfigObj({'StdRESTful': {'PromPush': options}, 'DataBindings': {'wx_binding': {'database': 'archive_sqlite'}}, 'Databases': {'archive_sqlite': {'driver': 'weedb.sqlite', 'root': str(tmp_path), 'database_name': 'archive.sdb'}}})
    monkeypatch.setattr(prompush.PromPushThread, 'start', lambda self: None)
    monkeypatch.setattr(prompush.syslog, 'syslog', lambda level, message: logged.append((level, message)))
    return prompush.PromPush(Engine(), config), logged


def test_missing_port_is_logged_and_skips_uploader(monkeypatch, tmp_path):
    service, logged = start_service(monkeypatch, tmp_path, {'host': 'localhost'})
    assert not hasattr(service, 'loop_thread')
    assert (prompush.syslog.LOG_ERR, 'prom-push: data will not be posted: missing option port') in logged


def test_unknown_options_are_logged_and_ignored(monkeypatch, tmp_path):
    service, logged = start_service(monkeypatch, tmp_path, {'host': 'localhost', 'port': '9091', 'enable': 'true', 'post_interval': '60'})
    assert service.loop_thread.host == 'localhost'
    assert (prompush.syslog.LOG_WARNING, "prom-push: unknown option 'post_interval' ignored") in logged
