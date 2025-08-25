from __future__ import annotations

import os
import shutil
import socketserver
import threading
import time
from shutil import copyfile
from typing import Any


def copy_html_template(
    name: str,
    new_string: bytes | None = None,
    old_string: bytes | None = None,
    path: str = "core/srv/html_templates",
    tmp_path: str = "core/srv/tmp"
) -> None:
    """ Copies a file from html_templates/ to tmp/ and replaces a string
        in the contents if it finds it.
    """
    filepath = f"{os.getcwd()}/{path}/{name}"

    tmp_filepath = f"{os.getcwd()}/{tmp_path}/{name}"

    copyfile(filepath, tmp_filepath)

    if all([new_string, old_string]):
        with open(tmp_filepath, "w+b") as fout, open(filepath, "r+b") as fin:
            for line in fin:
                fout.write(line.replace(old_string, new_string))

def save_string_in_tmp_folder(
    data: bytes,
    filename: str,
    path: str = "core/srv/tmp"
) -> None:
    filepath = f"{os.getcwd()}/{path}/{filename}"
    with open(filepath, "w+b") as text_file:
        text_file.write(data)

def open_tmp_file(filename: str) -> Any:
    filepath = f"{os.getcwd()}/core/srv/tmp/{filename}"
    return open(filepath, "r+b")

def cleanup_tmp_folder() -> None:
    folder = f"{os.getcwd()}/core/srv/tmp"
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception:
            pass
            # print e

def is_port_taken(host: str, port: int) -> bool:
    """ Return True/False depending on if the port is taken or not"""
    socket = socketserver.socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.shutdown(1)
        time.sleep(2)
        return True
    except OSError:
        return False

def shutdown_server(server_target: Any) -> None:
    """ Spawns a thread that triggers the TCPServer.shutdown method """
    assassin = threading.Thread(target=server_target.shutdown)
    assassin.daemon = True
    assassin.start()

def print_server_message(host: str, port: int, handler: Any) -> None:
    print("Quantipy http server version 1.0")
    print(f"Serving at: http://{host}:{port}")
    print(f"Handler : {handler.__name__}")

def start_server(host: str, port: int, handler: Any) -> None:
    """ Starts a SimpleHTTPServer with a speciffic handler.

        The handler needs to trigger the TCPServer.shutdown method or
        else the server runs until doomsday.
    """
    httpd = socketserver.TCPServer((host, port), handler)
    print_server_message(host, port, handler)
    httpd.serve_forever() # This is stopped by using the handler
