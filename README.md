# WeeWX observations for Prometheus Pushgateway

Send LOOP observations to a Prometheus Pushgateway using the text exposition
format. Prometheus must scrape that gateway separately to retain time series.

This is the weewx-packages continuation, release **1.1.0**.
[Origin](ORIGIN.md) records the upstream revision; [repair notes](REPAIR_NOTES.md)
describe the maintenance changes.

The catalog archive targets WeeWX `>=5.5.2,<5.7` and Python `>=3.10,<3.15`.

## Requirements

You need a reachable Pushgateway and Requests `>=2.32.5,<3` in the Python
environment running WeeWX. Activate that WeeWX virtual environment before
running these commands, so `python` and `weectl` use the same environment:

```sh
python -m pip install 'requests>=2.32.5,<3'
```

For a system installation, use your distribution's Requests package in WeeWX's
Python environment and check that its version meets that range. The archive
installer does not install Python dependencies. No source checkout is needed.

## Install

Replace `/path/to/weewx.conf` with your existing station configuration. Use
`weectl` from the Python environment running WeeWX to install the archive:

```sh
weectl extension install https://github.com/weewx-packages/weewx-prompush/releases/download/v1.1.0/weewx-prompush-1.1.0.tar.gz --config /path/to/weewx.conf
```

You can also download that URL and pass the local archive to the same command.
Use elevated permissions only when your station files require them.

## Configure the gateway

```ini
[StdRESTful]
    [[PromPush]]
        host = pushgateway.example.com
        port = 9091
        job = weewx
        instance = garden
```

The installer registers `user.prompush.PromPush`. Restart WeeWX yourself and
look for the job on the gateway after a LOOP packet. Configure Prometheus to
scrape that gateway. Job and instance are URL path components; use values
without slashes or spaces.

## Units and limits

The worker posts to `http://HOST:PORT/metrics/job/JOB/instance/INSTANCE`.
There are no TLS or authentication settings. Restrict access to the gateway
according to your network setup. Requests use the worker's timeout and HTTP
failures reach the WeeWX REST worker.

Values retain the incoming packet's unit system. The uploader sends non-null
packet values, including metadata such as `usUnits`; zero remains a value.
Known observations are annotated as gauges, other fields are untyped. Numeric
LOOP data is expected. There is no archive replay or built-in Prometheus server.
The service also resolves `wx_binding` at startup.

Copyright and authorship: Steve Ulrich <sulrich@botwerks.org>.
[Apache License 2.0](LICENSE). The original source is
[sulrich/weewx-prompush](https://github.com/sulrich/weewx-prompush).
