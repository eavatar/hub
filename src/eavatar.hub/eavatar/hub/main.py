# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

"""
The entry-point for the hub.
"""

import sys
import gevent
from gevent import pywsgi


from eavatar.hub.app import api
import eavatar.hub.routes
from eavatar.hub import (
    avatar
)


def _mygetfilesystemencoding():
    old = sys.getfilesystemencoding

    def inner_func():
        ret = old()
        if ret is None:
            return 'UTF-8'
        else:
            return ret
    return inner_func


def patch_sys_getfilesystemencoding():
    # sys.getfilesystemencoding() always returns None when frozen on Ubuntu systems.
    patched_func = _mygetfilesystemencoding()
    sys.getfilesystemencoding = patched_func


class Main(object):
    def __init__(self):
        self._server = None
        patch_sys_getfilesystemencoding()

    def run(self):
        print("Starting hub node")
        self._server = pywsgi.WSGIServer(('', 5000), api)

        self._server.serve_forever()


if __name__ == "__main__":
    launcher = Main()
    srv = gevent.spawn(launcher.run)
    gevent.joinall([srv])