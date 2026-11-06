#!/usr/bin/env python3
"""selftest_station_port_live_connects -- GAMEENV_FIX_PROOFSITE_6C84B4B3_ITEMS_WAIT: the live proof of
HOSE_END_FIX_CELL_SHORT_OF_PORT stopped at "map size unreadable ... bridge connection is closed" on a healthy game, because
station_port_live.py built its RimBridge and never connected it, and the supervisor could only read that as the environment.

Drives the real script through the real client over a real local socket (a fake GABP server, no game), so a never-opened
client cannot pass; then guards the class: no live script under src/ builds a bridge and calls it without opening it.
Exit 0 = all rows hold.
"""
import ast
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRIPT = os.path.join(HERE, "station_port_live.py")
STATIONS = ("RM_PumpingStation_Kludged", "RM_PumpingStation_Repaired")
MAP = 250
fails = []


def check(name, cond, detail=""):
    print("%-4s %s%s" % ("ok" if cond else "FAIL", name, "" if cond else "  -- %s" % str(detail)[:400]))
    if not cond:
        fails.append(name)


def joints_good():
    """The two rows HoseJointProbe writes for the staged scene: each at its reel (x0 + 12 i + 8, z0), naming the station."""
    x0, z0 = MAP // 2 - 12, MAP // 2
    return {"success": True, "tolerance": 0.05, "reels": 2, "joints": [
        {"kind": "free_port_end", "ok": True, "gap": 0.01, "at": [x0 + 12 * i + 8, z0], "where": "w", "reel": i,
         "note": "%s port at (0,0)" % d} for i, d in enumerate(STATIONS)]}


class Fake(threading.Thread):
    """A GABP server: one client at a time, answers the tools the proof uses, records what it was asked."""

    def __init__(self, joints):
        super().__init__(daemon=True)
        self.joints, self.tools, self.serial, self.result, self.hellos = joints, [], 0, "", 0
        self.srv = socket.create_server(("127.0.0.1", 0))
        self.port = self.srv.getsockname()[1]

    def answer(self, tool, a):
        self.tools.append(tool)
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": MAP, "sizeZ": MAP}
        if tool == "jawa/build_batch":
            return {"success": True, "placed": 2, "failed": 0}
        if tool == "jawa/mod_settings_field":
            if a.get("action") == "set":
                self.serial += 1
                self.result = json.dumps(self.joints if a.get("value") == "joints" else {"success": True})
                return {"success": True}
            return {"success": True, "value": self.serial if a.get("field") == "serial" else self.result}
        return {"success": True}

    def serve(self, conn):
        buf = b""
        while True:
            while b"\r\n\r\n" not in buf:
                got = conn.recv(65536)
                if not got:
                    return
                buf += got
            head, _, buf = buf.partition(b"\r\n\r\n")
            n = int(head.decode().split("Content-Length:")[1].split("\r\n")[0])
            while len(buf) < n:
                buf += conn.recv(65536)
            msg, buf = json.loads(buf[:n]), buf[n:]
            m = msg.get("method")
            if m == "session/hello":
                self.hellos += 1
                res = {"sessionId": "fake"}
            elif m == "tools/list":
                res = {"tools": []}
            else:
                p = msg.get("params") or {}
                res = self.answer(p.get("name"), p.get("arguments") or {})
            body = json.dumps({"v": "gabp/1", "id": msg["id"], "type": "response", "result": res}).encode()
            conn.sendall(b"Content-Length: %d\r\nContent-Type: application/json\r\n\r\n" % len(body) + body)

    def run(self):
        while True:
            try:
                conn, _ = self.srv.accept()
            except OSError:
                return
            with conn:
                try:
                    self.serve(conn)
                except OSError:
                    pass


def run_script(port, tmp, script=SCRIPT):
    """The script as the live round runs it (the real client, a real socket), with the client's bridge-lock check and evidence
    logs stubbed: the fake bridge is no game, and its calls must not cross a live holder's lock or write to the real logs."""
    shim = os.path.join(tmp, "shim.py")
    with open(shim, "w") as f:
        f.write("import runpy, sys\nsys.path.insert(0, %r)\nimport rimbridge_client as C\n"
                "C._driver_crossing = lambda host: None\nC._evidence = lambda *a, **k: None\n"
                "C._inflight_write = lambda *a, **k: None\nC._inflight_clear = lambda *a, **k: None\n"
                "C.outstanding_indeterminate = lambda *a, **k: []\nC.reconcile_auto = lambda *a, **k: (0, [])\n"
                "C._log_session = lambda *a, **k: None\nsys.path.append(%r)\n"
                "sys.argv = [%r, '--out', %r]\nrunpy.run_path(%r, run_name='__main__')\n"
                % (os.path.join(REPO, "src", "RimMandrake", "Utils"), HERE, script, os.path.join(tmp, "out.json"), script))
    env = dict(os.environ, RIMBRIDGE_HOST="127.0.0.1", GABP_SERVER_PORT=str(port), GABP_TOKEN="t", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, shim], env=env, capture_output=True, text=True, timeout=120, cwd=tmp,
                       stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr


def client_message():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    import rimbridge_client as C
    b = C.RimBridge(token="t")
    try:
        b._send({})
        said = ""
    except C.RimBridgeError as ex:
        said = str(ex)
    check("an unopened client says it never connected", "never connected" in said and "closed" not in said, said)
    b.sock = socket.socket()                # opened once, socket gone since: that IS a closed connection
    b.close()
    try:
        b._send({})
        said = ""
    except C.RimBridgeError as ex:
        said = str(ex)
    check("a client that lost its socket still says closed", "connection is closed" in said, said)


BUILDERS = ("RimBridge", "_bridge", "open_bridge")
OPENED = ("connect", "__enter__")


def _unopened(tree):
    """-> [(line, name)]: `x = RimBridge(...)` / `x = M._bridge()` in one scope, then x.call(...), with no x.connect(), no
    `with x`. A helper that only RETURNS the client, or hands it to a wrapper, makes no x.call and is not flagged."""
    out = []
    scopes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module))]
    for sc in scopes:
        for n in ast.walk(sc):
            if not (isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and len(n.targets) == 1
                    and isinstance(n.targets[0], ast.Name)):
                continue
            f = n.value.func
            if getattr(f, "attr", getattr(f, "id", None)) not in BUILDERS:
                continue
            v = n.targets[0].id
            called = opened = False
            for m in ast.walk(sc):
                if isinstance(m, ast.Attribute) and isinstance(m.value, ast.Name) and m.value.id == v:
                    called |= m.attr == "call"
                    opened |= m.attr in OPENED
                if isinstance(m, ast.withitem) and isinstance(m.context_expr, ast.Name) and m.context_expr.id == v:
                    opened = True
            if called and not opened and (n.lineno, v) not in out:
                out.append((n.lineno, v))
    return out


def class_guard():
    bad_fixture = "def main():\n    B = J._bridge()\n    return B.call('x', {})\n"
    good_fixture = "def main():\n    B = J._bridge().connect()\n    return B.call('x', {})\n"
    with_fixture = "def main():\n    B = J._bridge()\n    with B:\n        return B.call('x', {})\n"
    check("the guard sees the shape that stopped this proof", _unopened(ast.parse(bad_fixture)) == [(2, "B")])
    check("the guard passes connect()", not _unopened(ast.parse(good_fixture)))
    check("the guard passes `with`", not _unopened(ast.parse(with_fixture)))
    r = subprocess.run(["git", "ls-files", "-z", "src/*.py"], cwd=REPO, capture_output=True, text=True, timeout=60)
    files = [p for p in r.stdout.split("\0") if p and not os.path.basename(p).startswith(("selftest", "test_"))]
    check("the scan sees the repo (over 500 scripts, station_port_live among them)",
          len(files) > 500 and any(p.endswith("/station_port_live.py") for p in files), len(files))
    hits = []
    for p in files:
        try:
            with open(os.path.join(REPO, p), encoding="utf-8") as f:
                src = f.read()
            if "bridge" not in src.lower():
                continue
            tree = ast.parse(src)
        except (OSError, ValueError, SyntaxError):
            continue
        hits += ["%s:%d %s" % (p, ln, v) for ln, v in _unopened(tree)]
    check("no script calls a bridge it never opened", not hits, hits[:10])


def main():
    with tempfile.TemporaryDirectory() as tmp:
        fk = Fake(joints_good())
        fk.start()
        rc, out = run_script(fk.port, tmp)
        check("both couplings: exit 0", rc == 0, out[-400:])
        check("the proof opened a session", fk.hellos == 1, fk.hellos)
        check("the map size is read, no bridge-closed stop", "jawa/map_info" in fk.tools and "unreadable" not in out, out[-300:])
        check("it staged both stations", fk.tools.count("jawa/build_batch") == 2, fk.tools[:8])
        check("--out holds the joints", os.path.isfile(os.path.join(tmp, "out.json")))

        fk2 = Fake({"success": True, "tolerance": 0.05, "reels": 2, "joints": []})
        fk2.start()
        rc, out = run_script(fk2.port, tmp)
        check("no free_port_end row: exit 1 (still catches the S5 defect)", rc == 1, out[-400:])

        s = socket.create_server(("127.0.0.1", 0))
        dead = s.getsockname()[1]
        s.close()
        rc, out = run_script(dead, tmp)
        check("nothing listening: exit 2, UNMEASURED on one line, no traceback",
              rc == 2 and out.startswith("UNMEASURED: the bridge never answered") and "Traceback" not in out, out[-400:])

        # red on the pre-fix shape: the same script with its connect taken out stops as the live run did, before any session
        with open(SCRIPT) as f:
            src = f.read()
        pre = src.replace("J._bridge().connect()", "J._bridge()")
        check("the pre-fix mutant differs from the script", pre != src)
        mutant = os.path.join(tmp, "station_port_live_prefix.py")
        with open(mutant, "w") as f:
            f.write(pre.replace("B.close()", "pass"))
        fk3 = Fake(joints_good())
        fk3.start()
        rc, out = run_script(fk3.port, tmp, mutant)
        check("pre-fix mutant: no session, exit 2, the stop now names the cause",
              rc == 2 and fk3.hellos == 0 and "never connected" in out and "map size unreadable" in out, (rc, fk3.hellos, out[-300:]))
    client_message()
    class_guard()
    print("selftest_station_port_live_connects: %s" % ("FAIL %d" % len(fails) if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
