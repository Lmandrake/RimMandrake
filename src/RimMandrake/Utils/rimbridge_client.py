#!/usr/bin/env python3
"""
rimbridge_client.py - talk to a LIVE RimWorld through the RimBridgeServer GABP bridge.

*** THIS DRIVES A RUNNING GAME. THERE IS NO UNDO. ***
=====================================================
Every call goes straight into the RimWorld process that is on screen right now.
A colony that took twenty minutes to load can be wrecked by one careless call.
This module deliberately does NOT enforce read-only - it cannot, because the
bridge decides what a tool does, not us - so the discipline is yours:

  SAFE   rimbridge/ping, get_bridge_status, list_capabilities, list_logs,
         rimworld/get_game_info, list_*, get_*, search_debug_actions
  NEVER  rimworld/execute_debug_action, spawn_thing, save_game, load_game,
         set_*, rimbridge/run_lua, run_script - these mutate or destroy state

Searching for and DESCRIBING a debug action is free. EXECUTING one is not.

READ-ONLY IS NOT THE SAME AS HARMLESS
=====================================
2026-08-10: `rimworld/list_debug_action_roots` and `rimworld/search_debug_actions`
killed a live 562-mod colony. Neither tool changes game state - both build
RimWorld's debug node graph on the main thread, and on a load order this size
that build never returned. Unity stopped pumping, Windows raised AppHangB1, and
the process was terminated ~4 minutes later; 23 minutes of load time went with
it. There was no exception in Player.log, just silence.

So: on a heavily modded install, treat the four `*_debug_action*` discovery
tools as dangerous, not as reads. If you must call them, save the game first,
give them a multi-minute timeout, and expect that a timeout means the game is
already gone rather than merely slow. Everything else in the safe list above
returned in 7-15ms on that same install.

WHY THIS EXISTS
===============
The bridge is only reachable while the game is up, and the token changes on
every launch, so anything hardcoded is stale within one restart. This module
scrapes the live token out of Player.log so a session never starts with a
paste-the-token step that silently uses last launch's value and then fails with
a bare "Invalid authentication token".

WIRE FORMAT (derived from the shipped assemblies, not guessed)
==============================================================
Transport is raw TCP on 127.0.0.1 with LSP-style header framing. Everything
below was read out of the metadata/#US heaps of the DLLs RimWorld actually
loaded, at
  <Workshop>/294100/3727949765/1.6/Assemblies/{Lib.GAB.dll, Gabp.Runtime.dll}

  * Lib.GAB.dll #US heap: "Content-Length: {0}", "Content-Type: application/json",
    "\r\n\r\n"  ->  headers, blank line, then a UTF-8 JSON body of exactly
    Content-Length bytes. Reader prefix literal is "Content-Length:".
  * Gabp.Runtime.dll custom-attribute blob (JsonProperty names, in declaration
    order): v, id, type, method, params, result, error  ->  the request/response
    envelope. Events use: v, id, type, channel, seq, payload.
  * Lib.GAB.dll #US heap: "gabp/1" (envelope v), "request"/"response"/"event"
    (envelope type), and the method names "session/hello", "tools/list",
    "tools/call", "events/subscribe", "events/unsubscribe", "attention/current",
    "attention/ack".
  * Gabp.Runtime.dll blob, session/hello params: token, bridgeVersion, platform,
    launchId, clientInfo{name, version, author}. Welcome result: agentId, app,
    capabilities, schemaVersion, serverInfo{name, version}.
  * tools/call params: {name, arguments}. tools/list result: {tools:[...]}.
  * Server rejects anything before the handshake with "Session not established.
    Send session/hello first." and a bad token with "Invalid authentication
    token" (Lib.GAB.dll #US heap).

Tool names are canonical GABP form ^[a-z][a-z0-9_-]*(/[a-z][a-z0-9_-]*)+$ -
"rimworld/get_game_info", never the dotted MCP adapter spelling
"rimworld.get_game_info". Lib.GAB rejects the dotted form outright.

USAGE
=====
    python rimbridge_client.py --list-tools
    python rimbridge_client.py --call rimbridge/get_bridge_status
    python rimbridge_client.py --call rimworld/search_debug_actions \
        --json '{"query": "pawn", "limit": 50}'

    from rimbridge_client import RimBridge, discover_from_log
    host, port, token = discover_from_log()
    with RimBridge(host, port, token) as rb:
        print(rb.call("rimbridge/ping"))

Host/port/token resolve in this order: CLI flag, then environment
(RIMBRIDGE_HOST / GABP_SERVER_PORT / GABP_TOKEN - the same names Lib.GAB reads),
then the newest pair scraped from Player.log, then the built-in defaults.

Dependency-free: Python 3.8+ stdlib only. Keep it that way.
"""

import argparse
import json
import os
import re
import socket
import sys
import uuid

__all__ = ["RimBridge", "RimBridgeError", "discover_from_log", "DEFAULT_PLAYER_LOG"]

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5174
DEFAULT_TOKEN = ""

DEFAULT_PLAYER_LOG = os.path.join(
    os.path.expanduser("~"), "AppData", "LocalLow", "Ludeon Studios",
    "RimWorld by Ludeon Studios", "Player.log")

# Under WSL, expanduser("~") is /home/<user>, so DEFAULT_PLAYER_LOG points at a
# Linux path that will never exist and discovery silently finds nothing. The
# symptom is "no bridge token in Player.log - is RimWorld up?" while the token
# is sitting in the real log and the game is running perfectly.
#
# ⚠️ Finding the log does NOT make WSL work. RimBridge binds Windows loopback
# and WSL2 is NAT-mode, so the socket is refused regardless. The fallback exists
# so the error you get is the TRUE one (connection refused, wrong interpreter)
# instead of a false one that sends you looking at the game. Reported by a retired seat,
# 2026-08-12, after it cost them the hunt twice.
WSL = sys.platform.startswith("linux") and os.path.isdir("/mnt/c")


def _player_log_candidates():
    """Every place Player.log might be, best first."""
    yield DEFAULT_PLAYER_LOG
    if WSL:
        import glob
        for base in sorted(glob.glob("/mnt/c/Users/*/AppData/LocalLow/"
                                     "Ludeon Studios/RimWorld by Ludeon Studios")):
            yield os.path.join(base, "Player.log")

GABP_VERSION = "gabp/1"
BRIDGE_VERSION = "1.0"

# Anything not on this list is assumed to mutate the game until proven otherwise.
READ_ONLY_PREFIXES = ("list_", "get_", "search_", "find_", "compile_", "ping")


class RimBridgeError(RuntimeError):
    """A GABP-level failure: bad handshake, transport break, or tool error."""


# --------------------------------------------------------------------------
# token discovery
# --------------------------------------------------------------------------

_PORT_RE = re.compile(r"\[RimBridge\].*?on port\s+(\d+)")
_TOKEN_RE = re.compile(r"\[RimBridge\]\s*Bridge token:\s*([0-9A-Za-z._\-]+)")


def discover_from_log(path=None):
    """Scrape the NEWEST '[RimBridge] ... on port N' / 'Bridge token: X' pair.

    Returns (host, port, token); port/token are None if the log has no bridge
    lines. Last match wins on purpose - Player.log is append-only across
    restarts, so the first match is usually a dead session from hours ago.
    """
    paths = [path] if path else list(_player_log_candidates())
    port = token = None
    for candidate in paths:
        port = token = None
        try:
            with open(candidate, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "[RimBridge]" not in line:
                        continue
                    m = _PORT_RE.search(line)
                    if m:
                        port = int(m.group(1))
                    m = _TOKEN_RE.search(line)
                    if m:
                        token = m.group(1)
        except OSError:
            continue
        if token:
            break
    if token is None and port is None:
        return DEFAULT_HOST, None, None
    return DEFAULT_HOST, port, token


def resolve_endpoint(host=None, port=None, token=None, log_path=None):
    """CLI arg > env > Player.log > module default, per field independently."""
    log_host = log_port = log_token = None
    if host is None or port is None or token is None:
        log_host, log_port, log_token = discover_from_log(log_path)

    host = host or os.environ.get("RIMBRIDGE_HOST") or log_host or DEFAULT_HOST
    if port is None:
        env_port = os.environ.get("GABP_SERVER_PORT")
        port = int(env_port) if env_port else (log_port or DEFAULT_PORT)
    token = token or os.environ.get("GABP_TOKEN") or log_token or DEFAULT_TOKEN
    return host, int(port), token


# --------------------------------------------------------------------------
# the bridge
# --------------------------------------------------------------------------

class RimBridge:
    """One GABP session over one TCP socket.

    Not thread-safe and not meant to be: the bridge serialises onto RimWorld's
    main thread anyway, so a second concurrent caller buys nothing but
    interleaved frames.
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, token="",
                 timeout=30.0, connect_timeout=5.0, client_name="rimbridge_client.py"):
        self.host = host
        self.port = int(port)
        self.token = token or ""
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.client_name = client_name
        self.sock = None
        self.buf = b""
        self.welcome = None
        self.events = []          # unsolicited event envelopes seen while reading

    # -- lifecycle ---------------------------------------------------------

    def connect(self):
        """Open the socket and complete session/hello. Raises on refusal."""
        try:
            self.sock = socket.create_connection((self.host, self.port),
                                                 timeout=self.connect_timeout)
        except OSError as ex:
            # Under WSL this is never "the game is down" -- RimBridge binds
            # Windows loopback and WSL2 is NAT-mode, so there is no route at
            # all. Saying "is RimWorld running?" here sends the reader to check
            # a game that is running fine. Name the real cause instead.
            if WSL:
                raise RimBridgeError(
                    "cannot reach the bridge from WSL, and no amount of "
                    "retrying will fix it.\n"
                    "  RimBridge binds Windows loopback; WSL2 is NAT-mode, so "
                    "%s:%s has no route from here.\n"
                    "  This says NOTHING about whether RimWorld is running.\n"
                    "  Re-run under Windows Python:  python.exe %s"
                    % (self.host, self.port,
                       " ".join(sys.argv) or "<your script>")) from ex
            raise RimBridgeError(
                "cannot reach the bridge at %s:%s (%s) - is RimWorld running "
                "with RimBridgeServer enabled?" % (self.host, self.port, ex)) from ex
        self.sock.settimeout(self.timeout)
        self.welcome = self._hello()
        return self

    def close(self):
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

    def __enter__(self):
        if self.sock is None:
            self.connect()
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    # -- framing -----------------------------------------------------------

    def _send(self, envelope):
        body = json.dumps(envelope, separators=(",", ":")).encode("utf-8")
        head = ("Content-Length: %d\r\nContent-Type: application/json\r\n\r\n"
                % len(body)).encode("ascii")
        self.sock.sendall(head + body)

    def _recv_raw(self):
        """Read exactly one framed JSON message. Tolerates LF-only headers."""
        while b"\r\n\r\n" not in self.buf and b"\n\n" not in self.buf:
            self._fill()
        sep = b"\r\n\r\n" if b"\r\n\r\n" in self.buf else b"\n\n"
        head, _, rest = self.buf.partition(sep)
        length = None
        for line in head.decode("ascii", "replace").splitlines():
            if line.lower().startswith("content-length:"):
                length = int(line.split(":", 1)[1].strip())
        if length is None:
            raise RimBridgeError("framed message had no Content-Length header: %r"
                                 % head[:200])
        self.buf = rest
        while len(self.buf) < length:
            self._fill()
        body, self.buf = self.buf[:length], self.buf[length:]
        return json.loads(body.decode("utf-8"))

    def _fill(self):
        try:
            chunk = self.sock.recv(65536)
        except socket.timeout as ex:
            raise RimBridgeError(
                "timed out after %ss waiting for the bridge; RimWorld may be in a "
                "long event or the call may be frame-bound" % self.timeout) from ex
        if not chunk:
            raise RimBridgeError("bridge closed the connection")
        self.buf += chunk

    def _recv_response(self, want_id):
        """Read until the response with our id arrives; park events aside."""
        while True:
            msg = self._recv_raw()
            if msg.get("type") == "event":
                self.events.append(msg)
                continue
            if msg.get("id") == want_id or want_id is None:
                return msg
            # A response for some other id means the stream desynced.
            raise RimBridgeError("unexpected response id %r (wanted %r)"
                                 % (msg.get("id"), want_id))

    def _request(self, method, params=None):
        rid = str(uuid.uuid4())
        self._send({
            "v": GABP_VERSION,
            "id": rid,
            "type": "request",
            "method": method,
            "params": params or {},
        })
        msg = self._recv_response(rid)
        err = msg.get("error")
        if err:
            raise RimBridgeError("%s failed: %s" % (
                method, err.get("message") if isinstance(err, dict) else err))
        return msg.get("result")

    # -- handshake ---------------------------------------------------------

    def _hello(self):
        params = {
            "token": self.token,
            "bridgeVersion": BRIDGE_VERSION,
            "platform": sys.platform,
            "clientInfo": {
                "name": self.client_name,
                "version": "1.0.0",
                "author": "rimworld-project",
            },
        }
        try:
            return self._request("session/hello", params)
        except RimBridgeError as ex:
            if "Invalid session/hello parameters" not in str(ex):
                raise
            # Fall back to the minimum the server documents as required.
            return self._request("session/hello", {"token": self.token})

    # -- public API --------------------------------------------------------

    def list_tools(self):
        """tools/list -> the live tool descriptors. Never mutates."""
        result = self._request("tools/list") or {}
        return result.get("tools", [])

    def call(self, tool, params=None):
        """tools/call. NOTHING here stops you calling a destructive tool."""
        return self._request("tools/call", {"name": tool, "arguments": params or {}})

    def looks_read_only(self, tool):
        """Cheap heuristic only - a False here is a warning, a True is not a promise."""
        leaf = tool.split("/", 1)[-1]
        return leaf.startswith(READ_ONLY_PREFIXES)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _main(argv=None):
    ap = argparse.ArgumentParser(
        description="Query a live RimWorld through the RimBridgeServer GABP bridge.")
    ap.add_argument("--host")
    ap.add_argument("--port", type=int)
    ap.add_argument("--token")
    ap.add_argument("--log", dest="log_path", help="Player.log to scrape for port/token")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--list-tools", action="store_true")
    ap.add_argument("--call", metavar="TOOL")
    ap.add_argument("--json", dest="params", default="{}",
                    help="JSON object of tool arguments")
    ap.add_argument("--raw", action="store_true", help="dump the full envelope result")
    ap.add_argument("--yes-i-know-this-is-live", action="store_true",
                    help="required to call a tool that fails the read-only heuristic")
    args = ap.parse_args(argv)

    host, port, token = resolve_endpoint(args.host, args.port, args.token, args.log_path)
    if not token:
        print("no bridge token found (CLI, env GABP_TOKEN, or Player.log)", file=sys.stderr)
        return 2

    if args.call and not args.list_tools:
        probe = RimBridge(host, port, token, timeout=args.timeout)
        if not probe.looks_read_only(args.call) and not args.yes_i_know_this_is_live:
            print("REFUSING '%s': it does not look read-only. This drives a LIVE game.\n"
                  "Pass --yes-i-know-this-is-live if you really mean it." % args.call,
                  file=sys.stderr)
            return 3

    try:
        with RimBridge(host, port, token, timeout=args.timeout) as rb:
            if args.list_tools:
                tools = rb.list_tools()
                print(json.dumps({"count": len(tools), "tools": tools}, indent=2))
            if args.call:
                out = rb.call(args.call, json.loads(args.params))
                print(json.dumps(out, indent=2))
            if not args.list_tools and not args.call:
                print(json.dumps({"welcome": rb.welcome}, indent=2))
    except RimBridgeError as ex:
        print("bridge error: %s" % ex, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
