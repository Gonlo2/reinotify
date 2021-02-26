#!/usr/bin/env python3
import logging
import socket
import struct
import zlib
from threading import Thread

from .types import InotifyEvent

logger = logging.getLogger(__name__)


class CorruptedMsgException(Exception):
    pass


class InvalidPathException(Exception):
    pass


class Server:
    def __init__(self, ip_and_port, callback):
        self._ip_and_port = ip_and_port
        self._callback = callback
        self._thread = None

    def start(self):
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(self._ip_and_port)

        while True:
            try:
                data, addr = sock.recvfrom(2048)
                e = self._parse_msg(data)
                logger.debug(f"Received event (mask: {e.mask}, cookie: {e.cookie}, path: '{e.path}', filename: '{e.name}')")
                self._callback(e)
            except CorruptedMsgException:
                logger.warning("Received corrupted inotify msg")
            except:
                logger.exception(f"Some error take place processing the remote watcher message of {addr}")

    def _parse_msg(self, data):
        wid_l, name_l, path_l, mask, cookie = struct.unpack("!BBHII", data[:12])
        wid, name, path, crc32 = struct.unpack(f"!{wid_l}s{name_l}s{path_l}sI",
                                               data[12:])

        body_size = 12 + wid_l + name_l + path_l
        if crc32 != zlib.crc32(data[:body_size]):
            raise CorruptedMsgException

        wid = wid[:-1].decode()
        path = path[:-1].decode()
        name = name[:-1].decode()

        if '..' in path.split('/') or '/' in name or name == '..':
            raise InvalidPathException

        return InotifyEvent(wid=wid, mask=mask, cookie=cookie,
                            path=path, name=name)
