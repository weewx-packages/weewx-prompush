#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Modified 2026-10-22 by weewx-packages: compatibility and tracker repairs.

"""
setup for weewx prometheus pushgateway pusher
"""

__title__ = 'PromPush'
__version__ = '1.1.1'
__author__ = 'steve ulrich <sulrich@botwerks.org>'
__license__ = 'Apache License, Version 2.0'


from weecfg.extension import ExtensionInstaller

def loader():
    """install PromPush extension"""
    return WeewxPromPushInstaller()


class WeewxPromPushInstaller(ExtensionInstaller):
    """installs weewx PromPush extension"""

    def __init__(self):
        super(WeewxPromPushInstaller, self).__init__(
            version=__version__,
            name=__title__,
            description='post weather data to prometheus pushgateway.',
            author='steve ulrich',
            author_email='sulrich@botwerks.org',
            restful_services='user.prompush.PromPush',
            config={
                'StdRESTful': {
                    'PromPush': {
                        'host': 'PUSH_GW_HOST',
                        'port': 'PUSH_GW_PORT',
                        'job': 'PROMETHEUS_JOB_NAME',
                        'instance': 'PROMETHEUS_INSTANCE_NAME'
                    }
                }
            },
            files=[('bin/user', ['bin/user/prompush.py'])]
        )
