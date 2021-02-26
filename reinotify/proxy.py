#!/usr/bin/env python3
import logging
import socket
import struct
import zlib

logger = logging.getLogger(__name__)


class Proxy:
    def __init__(self, ip_and_port):
        self._ip_and_port = ip_and_port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # MESSAGE FORMAT
    # wid size  : u8
    # name size : u8
    # path size : u16
    # mask      : u32
    # cookie    : u32
    # wid       : cstr
    # name      : cstr
    # path      : cstr
    # crc32     : u32
    def notify(self, e):
        wid = e.wid.encode() + b'\0'
        path = e.path.encode() + b'\0'
        name = e.name.encode() + b'\0'

        body = struct.pack(f"!BBHII{len(wid)}s{len(name)}s{len(path)}s",
                           len(wid), len(name), len(path), e.mask,
                           e.cookie, wid, name, path)
        crc32 = zlib.crc32(body)
        data = struct.pack(f"!{len(body)}sI", body, crc32)
        self._sock.sendto(data, self._ip_and_port)
