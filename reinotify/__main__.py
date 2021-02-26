import logging
import os
import signal
import sys

from .proxy import Proxy
from .watcher import Watcher

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

def main():
    ip = sys.argv[1]
    port = int(sys.argv[2])
    ids_and_paths = sys.argv[3:]

    watchers = []
    for x in ids_and_paths:
        watch_id, path = x.split(':', 1)
        path = os.path.abspath(path)
        proxy = Proxy(ip, port)
        watcher = Watcher(watch_id, path, proxy)
        watcher.start()
        watchers.append(watcher)

    signal.sigwait((signal.SIGINT,))

if __name__ == '__main__':
    main()
