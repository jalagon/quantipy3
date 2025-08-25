"""HTTP server implementations for quantipy3 web-based functionality.

This module provides server implementations for interactive web editing of
quantipy objects, including browser integration and JSON data exchange.
"""

from __future__ import annotations

import builtins
import contextlib
import json
import webbrowser
from collections import OrderedDict

from .core import cleanup_tmp_folder, copy_html_template, open_tmp_file, start_server
from .handlers import WebEditHandler


def webeditor(obj, host="localhost", port=8000):
    cleanup_tmp_folder()
    url = f"http://{host}:{port}/core/srv/tmp/webedit.html"

    json_string = json.dumps(obj, sort_keys=True)
    copy_html_template('webedit.html', json_string, "REPLACEJSON")
    webbrowser.open_new_tab(url)

    # This runs forever and can only be shut down in the handler or by
    # ctr+c
    start_server(host=host, port=port, handler=WebEditHandler)

    with contextlib.suppress(builtins.BaseException):
        obj = json.loads(
            open_tmp_file('obj.json').readline(),
            object_pairs_hook=OrderedDict)

    cleanup_tmp_folder()
    return obj
