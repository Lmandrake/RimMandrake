#!/usr/bin/env python3
"""arena_critic_relay: the critic sandbox's only way out (CRITIC_SANDBOX_HARDEN_NETWORK_RESIDUAL).

WHY. A critic in a shared network namespace could reach RimPulse on loopback (the unauthenticated ledger: every item's
spec and close note), the Windows host's ports and the public internet (remote history). It needs one thing from the
network: the model API.

HOW. bwrap --unshare-net: the sandbox has its own lo and nothing else. The host side of this module listens on a unix
socket, the one thing that crosses the namespace, and honours only `CONNECT host:port` for a host:port on the allow-list.
Inside, BRIDGE forwards a port on the sandbox's own 127.0.0.1 to that socket and runs the critic with HTTPS_PROXY pointing
at it. TLS runs end to end, so the relay sees hosts, never content.

The allow-list comes from the environment (ALLOW_ENV: comma-separated host:port), else from the machine-local ALLOW_FILE
for launchers that carry no shell environment, never from code. Neither set refuses: the critic does not fall back to a
shared network. Everything refused is kept in Relay.denied.

Residual: an allowed host is a channel out, and this relay cannot see what crosses it.
"""
from __future__ import annotations

import atexit
import os
import shutil
import socket
import tempfile
import threading
from pathlib import Path

ALLOW_ENV = "ARENA_CRITIC_RELAY_ALLOW"
ALLOW_FILE = Path.home() / ".config" / "rimmandrake" / "critic_relay_allow"
HEAD_MAX = 8192
CONNECT_TIMEOUT = 30

# Runs inside the sandbox: argv = [socket, command...]. Stdio is inherited (the prompt arrives on stdin).
BRIDGE = r"""
import os, socket, subprocess, sys, threading
path, argv = sys.argv[1], sys.argv[2:]
srv = socket.socket()
srv.bind(("127.0.0.1", 0))
srv.listen(64)
def pump(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except OSError:
        pass
    try:
        b.shutdown(socket.SHUT_WR)
    except OSError:
        pass
def serve():
    while True:
        c, _ = srv.accept()
        u = socket.socket(socket.AF_UNIX)
        u.connect(path)
        threading.Thread(target=pump, args=(c, u), daemon=True).start()
        threading.Thread(target=pump, args=(u, c), daemon=True).start()
threading.Thread(target=serve, daemon=True).start()
url = "http://127.0.0.1:%d" % srv.getsockname()[1]
env = dict(os.environ)
for k in ("NO_PROXY", "no_proxy"):
    env.pop(k, None)
for k in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
    env[k] = url
env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
sys.exit(subprocess.call(argv, env=env))
"""


class RelayRefused(Exception):
    pass


def allow_list() -> set:
    raw = os.environ.get(ALLOW_ENV)
    if raw is None and ALLOW_FILE.exists():
        raw = ALLOW_FILE.read_text()
    raw = (raw or "").replace("\n", ",")
    out = {x.strip().lower() for x in raw.split(",") if x.strip()}
    bad = [x for x in out if x.rpartition(":")[2] == x or not x.rpartition(":")[2].isdigit()]
    if bad:
        raise RelayRefused("%s entries must be host:port: %s" % (ALLOW_ENV, bad))
    if not out:
        raise RelayRefused("neither %s nor %s sets an allow-list: the critic has no route to its model, and never runs "
                           "on a shared network" % (ALLOW_ENV, ALLOW_FILE))
    return out


def _pipe(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except OSError:
        pass
    try:
        b.shutdown(socket.SHUT_WR)
    except OSError:
        pass


class Relay:
    """One listener per process; the socket lives in a private directory under `base`."""

    def __init__(self, allow: set, base: Path):
        self.allow = set(allow)
        self.denied: list = []
        base = Path(base)
        base.mkdir(parents=True, exist_ok=True)
        self.dir = tempfile.mkdtemp(prefix="r.", dir=str(base))
        self.path = os.path.join(self.dir, "s")
        self.srv = socket.socket(socket.AF_UNIX)
        self.srv.bind(self.path)
        self.srv.listen(64)
        threading.Thread(target=self._serve, daemon=True).start()

    def close(self):
        self.srv.close()
        shutil.rmtree(self.dir, ignore_errors=True)

    def _serve(self):
        while True:
            try:
                c, _ = self.srv.accept()
            except OSError:
                return
            threading.Thread(target=self._one, args=(c,), daemon=True).start()

    def _one(self, c):
        up = None
        try:
            c.settimeout(CONNECT_TIMEOUT)
            head = b""
            while b"\r\n\r\n" not in head and len(head) < HEAD_MAX:
                d = c.recv(HEAD_MAX)
                if not d:
                    return
                head += d
            parts = head.split(b"\r\n", 1)[0].decode("latin-1").split()
            target = parts[1].lower() if len(parts) == 3 and parts[0] == "CONNECT" else None
            if target not in self.allow:
                self.denied.append(target or parts[:2])
                c.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n")
                return
            host, _, port = target.rpartition(":")
            up = socket.create_connection((host, int(port)), CONNECT_TIMEOUT)
            up.settimeout(None)      # CONNECT_TIMEOUT bounds the connect: a model silent for 30 s is not a dead link
            c.settimeout(None)
            c.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            early = head.split(b"\r\n\r\n", 1)[-1] if b"\r\n\r\n" in head else b""
            if early:                    # a client may send its first tunnel bytes with the CONNECT
                up.sendall(early)
            t = threading.Thread(target=_pipe, args=(up, c), daemon=True)
            t.start()
            _pipe(c, up)
            t.join()
        except (OSError, ValueError):
            pass
        finally:
            c.close()
            if up is not None:
                up.close()


_lock = threading.Lock()
_relay: Relay | None = None


def relay(base: Path) -> Relay:
    """This process's relay; a changed allow-list starts a new one."""
    global _relay
    allow = allow_list()
    with _lock:
        if _relay is None or _relay.allow != allow or not os.path.exists(_relay.path):
            if _relay is not None:
                _relay.close()
            _relay = Relay(allow, base)
            atexit.register(_relay.close)
        return _relay
