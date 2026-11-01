"""Something for btop to show, at levels like a desktop's: CPU in waves on every core, memory in
use, traffic on lo, and a few named processes."""

import functools
import math
import multiprocessing
import os
import tempfile
import threading
import time
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

TICK = 0.05  # s
MEMORY = 900 << 20  # bytes held, about half of what the container sees


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:  # stderr is btop's screen
        pass


def named(name: str) -> None:
    """The name btop lists for this process."""
    with open("/proc/self/comm", "w") as f:
        f.write(name)


def burn(core: int) -> None:
    named(f"render-{core}")
    while True:
        load = 0.5 + 0.2 * math.sin(time.time() / 2 + core * 1.5)
        end = time.time() + TICK * load
        while time.time() < end:
            pass
        time.sleep(TICK * (1 - load))


def hold() -> None:
    named("cache")
    block = bytearray(MEMORY)
    block[:: 1 << 12] = b"x" * len(block[:: 1 << 12])  # touch every page, so it counts as used
    while True:
        time.sleep(60)


def idle(name: str) -> None:
    named(name)
    while True:
        time.sleep(1)


def traffic() -> None:
    named("sync")
    while True:
        for _ in range(round(3 + 2 * math.sin(time.time()))):
            with urllib.request.urlopen("http://127.0.0.1:8000/blob") as r:
                r.read()
        time.sleep(0.4)


if __name__ == "__main__":
    named("serve")
    served = tempfile.mkdtemp()
    with open(os.path.join(served, "blob"), "wb") as f:
        f.write(os.urandom(1 << 18))
    server = ThreadingHTTPServer(("127.0.0.1", 8000), functools.partial(Quiet, directory=served))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    jobs = [(burn, (core,)) for core in range(os.cpu_count() or 1)]
    jobs += [(hold, ()), (traffic, ()), *((idle, (name,)) for name in ("watch", "index", "backup", "notify"))]
    for target, args in jobs:
        multiprocessing.Process(target=target, args=args, daemon=True).start()
    while True:
        time.sleep(60)
