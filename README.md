# WeeWX Prometheus Pushgateway uploader

Sends every LOOP packet to a Prometheus Pushgateway in the text exposition
format. Prometheus must scrape the gateway to keep the time series. The
extension has no archive replay and no built-in Prometheus endpoint.

This is the weewx-packages continuation of
[sulrich/weewx-prompush](https://github.com/sulrich/weewx-prompush). See
[ORIGIN.md](ORIGIN.md) and [REPAIR_NOTES.md](REPAIR_NOTES.md).

## Requirements

- A reachable Prometheus Pushgateway.
- The Python package Requests in the environment that runs WeeWX. The
  installer does not install Python packages. Activate the WeeWX virtual
  environment, then run:

  ```sh
  python -m pip install 'requests>=2.32.5,<3'
  ```

  For a system installation of WeeWX, use your distribution's Requests
  package and check that its version is in that range.

## Installation

Install `prompush` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/prompush.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The installer adds `user.prompush.PromPush` to `restful_services` and writes
a `[[PromPush]]` section with the placeholders `PUSH_GW_HOST`,
`PUSH_GW_PORT`, `PROMETHEUS_JOB_NAME` and `PROMETHEUS_INSTANCE_NAME`.
Replace them, then restart WeeWX.

## Configuration

```ini
[StdRESTful]
    [[PromPush]]
        host = pushgateway.example.com
        port = 9091
        job = weewx
        instance = garden
```

After the next LOOP packet, the job appears on the gateway. Configure
Prometheus to scrape the gateway. Depending on its configuration, Prometheus
may relabel `job` and `instance`.

| Option | Default | Meaning |
|---|---|---|
| `host` | required | Pushgateway host. |
| `port` | required | Pushgateway port, usually `9091`. |
| `job` | `weewx` | Job name in the push URL. |
| `instance` | empty | Instance name in the push URL. Empty leaves it out. |
| `stale` | `60` | Packets older than this many seconds are skipped. |
| `max_backlog` | unlimited | Queue length before old packets are dropped. |
| `timeout` | `10` | HTTP timeout in seconds. |
| `log_success` | `True` | Log each uploaded packet. |
| `log_failure` | `True` | Log failed uploads. |
| `skip_post` | `False` | Do not send packets. |

The uploader posts to `http://<host>:<port>/metrics/job/<job>/instance/<instance>`.
Each field of the packet with a value becomes one metric, including
`dateTime` and `usUnits`. Zero is sent. Values keep the packet's unit system.
Common weather observations are typed as `gauge`, all other fields are left
untyped. The service always reads the `wx_binding` data binding.

## Limitations

- A missing `host` or `port` stops WeeWX at startup with a `KeyError`.
  Options other than those in the table, such as `enable` or
  `post_interval`, stop it with a `TypeError`.
- There are no TLS or authentication settings. Restrict access to the
  gateway in your network.
- `job` and `instance` are inserted into the URL path without escaping. Use
  values without slashes or spaces.
- `max_tries` and `retry_wait` are accepted but have no effect. A failed
  post is logged and the packet is dropped.
- The tests use a local HTTP receiver. They do not replace a check against a
  real Pushgateway.

## Development

```sh
python -m pytest -q tests
```

Run the tests in an environment with WeeWX, Requests and pytest.

## License

Written by Steve Ulrich <sulrich@botwerks.org>.

Apache License, Version 2.0. See [LICENSE](LICENSE).

Modified 2026-10-23 by weewx-packages.
