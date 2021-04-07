#!/usr/bin/env python3
import logging
import os
import time
from threading import Thread

import inotify.constants as iconst
from inotify.adapters import InotifyTree
from inotify.calls import InotifyError

from .types import InotifyEvent

logger = logging.getLogger(__name__)

DEFAULT_MASK = (iconst.IN_CLOSE_WRITE | iconst.IN_CREATE |
                iconst.IN_DELETE |
                iconst.IN_MOVED_FROM | iconst.IN_MOVED_TO)

class Watcher:
    def __init__(self, wid, path, proxy, mask=DEFAULT_MASK):
        self._wid = wid
        self._path = path
        self._proxy = proxy
        self._mask = mask
        self._thread = None

    def start(self):
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while True:
            time_limit = time.time() + 1
            try:
                self._watch()
            except InotifyError:
                logger.exception("Raised InotifyError")
                time.sleep(max(time_limit - time.time(), 0))

    def _watch(self):
        for e in self._get_event():
            logger.debug(f"Received event (mask: {e.mask}, cookie: {e.cookie}, path: '{e.path}', name: '{e.name}')")
            try:
                self._proxy.notify(e)
            except:
                logger.exception(f"Received exception notifing (mask: {e.mask}, cookie: {e.cookie}, path: '{e.path}', name: '{e.name}')")

    def _get_event(self):
        logger.debug(f"Watching path '{self._path}' with mask {self._mask}")
        inotify = InotifyTree(self._path, self._mask)

        logger.debug(f"Starting watcher loop in '{self._path}'")
        try:
            for header, _, path, name in inotify.event_gen(yield_nones=False):
                path = os.path.relpath(path, start=self._path)
                if path == '.':
                    path = ''
                yield InotifyEvent(wid=self._wid, path=path, name=name,
                                   mask=header.mask, cookie=header.cookie)
        finally:
            del inotify
