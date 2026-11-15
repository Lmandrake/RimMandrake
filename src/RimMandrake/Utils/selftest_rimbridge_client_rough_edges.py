"""selftest_rimbridge_client_rough_edges.py - the four defects of BRIDGE_CLIENT_HARDEN_FOUR_ROUGH_EDGES (GPT full-file
review, job consult-20261102-223828-1349121), each held by a case. No game, no real socket:
  1 a failed INDETERMINATE marker write still refuses a retry in the SAME live process, until reconciled;
  2 --list-tools beside --call does not skip the --yes-i-know-this-is-live acknowledgment;
  3 a timeout mid-body leaves the frame parseable: the next read gets it whole, and a later request drops it as abandoned;
  4 a marker whose pid is alive but was reused (another process start) reads as orphaned.
"""
import atexit
import json
import os
import shutil
import socket
import sys
import tempfile

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_rimbridge_client_rough_edges_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
D = tempfile.mkdtemp()
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(D, "bridge_calls.jsonl")
os.environ["RIMBRIDGE_SESSION_LOG"] = ""
os.environ["RIMBRIDGE_ALIVE_PROBE"] = "off"
os.environ["RIMFLOW_DRIVER_LOCK"] = os.path.join(D, "no_driver_lock.json")   # a real holder must not redden this
for _k in ("GABP_TOKEN", "GABP_SERVER_PORT", "RIMBRIDGE_HOST"):
    os.environ.pop(_k, None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as C  # noqa: E402


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, "" if cond else detail))
    return bool(cond)


def clear_markers():
    for x in C.outstanding_indeterminate():
        C.reconcile_resolve(x["cid"], "not-applied", "selftest cleanup")


def bridge(reply):
    b = C.RimBridge(token="t")

    def req(method, params=None):
        if isinstance(reply, BaseException):
            raise reply
        return reply
    b._request = req
    return b


def defect1():
    good = []
    real_write = C._inflight_write

    def failing(rec):
        if rec.get("status") == "INDETERMINATE":
            raise OSError("disk full (simulated)")
        return real_write(rec)
    for label, exc in (("timeout", C.RimBridgeError("timed out after 30s waiting for the bridge")),
                       ("interrupt", KeyboardInterrupt())):
        clear_markers()
        C._inflight_write = failing
        try:
            try:
                bridge(exc).call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
            except BaseException:  # noqa: BLE001
                pass
        finally:
            C._inflight_write = real_write
        pend = C.outstanding_indeterminate()
        good.append(case("1/%s: an unwritable INDETERMINATE marker still reads UNKNOWN in this live process" % label,
                         len(pend) == 1 and pend[0].get("tool") == "jawa/spawn_pawn", pend))
        try:
            bridge({"success": True}).call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
            refused = False
        except C.IndeterminateError:
            refused = True
        good.append(case("1/%s: the retry is refused" % label, refused))
        if pend:
            C.reconcile_resolve(pend[0]["cid"], "not-applied", "selftest")
        good.append(case("1/%s: reconcile clears it" % label, not C.outstanding_indeterminate(),
                         C.outstanding_indeterminate()))
    return good


def defect2():
    import io
    import contextlib
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        rc = C._main(["--host", "127.0.0.1", "--port", "1", "--token", "t", "--list-tools",
                      "--call", "rimworld/load_game", "--json", '{"fileName":"x"}'])
    return [case("2: --list-tools --call <mutation> without the acknowledgment refuses (exit 3, no connect)",
                 rc == 3 and "REFUSING" in err.getvalue(), (rc, err.getvalue()[-300:]))]


def frame(obj):
    body = json.dumps(obj).encode("utf-8")
    return b"Content-Length: %d\r\n\r\n" % len(body) + body


class FakeSock:
    """recv() plays a script: bytes, socket.timeout, or a callable(sent_envelopes) -> bytes."""

    def __init__(self, script):
        self.script = list(script)
        self.sent = []

    def settimeout(self, t):
        pass

    def sendall(self, data):
        self.sent.append(json.loads(data.split(b"\r\n\r\n", 1)[1]))

    def recv(self, n):
        step = self.script.pop(0)
        if isinstance(step, BaseException):
            raise step
        return step(self.sent) if callable(step) else step

    def shutdown(self, how):
        pass

    def close(self):
        pass


def defect3():
    good = []
    f1, f2 = frame({"id": "a", "type": "response", "result": {"n": 1}}), frame({"id": "b", "type": "response"})
    cut = f1.index(b"\r\n\r\n") + 4 + 5                       # header plus 5 body bytes
    b = C.RimBridge(token="t", timeout=0.01)
    b.sock = FakeSock([f1[:cut], socket.timeout(), f1[cut:] + f2])
    try:
        b._recv_raw()
        timed = False
    except C.RimBridgeError as ex:
        timed = "timed out" in str(ex)
    good.append(case("3: a timeout mid-body raises timed out", timed))
    try:
        m1, m2 = b._recv_raw(), b._recv_raw()
    except Exception as ex:  # noqa: BLE001
        m1 = m2 = repr(ex)
    good.append(case("3: the next reads get the cut frame whole, then the next one", m1 == json.loads(f1.split(
        b"\r\n\r\n", 1)[1]) and isinstance(m2, dict) and m2.get("id") == "b", (m1, m2)))

    # through _request: the first call times out mid-body; the second gets the late tail (dropped as abandoned) first
    b = C.RimBridge(token="t", timeout=5.0)
    late = {}

    def head(sent):
        late["f"] = frame({"id": sent[-1]["id"], "type": "response", "result": {"late": True}})
        return late["f"][:len(late["f"]) - 3]

    def tail_then_answer(sent):
        return late["f"][-3:] + frame({"id": sent[-1]["id"], "type": "response", "result": {"ok": 2}})
    b.sock = FakeSock([head, socket.timeout(), tail_then_answer])
    try:
        b._request("tools/call", {})
        first = None
    except C.RimBridgeError as ex:
        first = str(ex)
    try:
        second = b._request("tools/call", {})
    except Exception as ex:  # noqa: BLE001
        second = repr(ex)
    good.append(case("3: after a mid-body timeout the next request still reads its own answer",
                     first is not None and first.startswith("timed out") and second == {"ok": 2}, (first, second)))
    return good


def defect4():
    good = []
    clear_markers()
    me = os.getpid()
    st = C._proc_start(me)
    good.append(case("4: sanity - this OS reads a process start for a live pid", st is not None, st))
    if st is None:
        return good
    good.append(case("4: a live pid with its own start reads alive", C._pid_alive(me, st)))
    good.append(case("4: a live pid with another start reads gone (reused)", not C._pid_alive(me, st + 1)))
    C._inflight_write({"cid": "reuse1", "tool": "jawa/destroy_batch", "pid": me, "pid_start": st + 1, "os": os.name,
                       "status": "in-flight", "t": "x"})
    C._inflight_write({"cid": "mine1", "tool": "jawa/destroy_batch", "pid": me, "pid_start": st, "os": os.name,
                       "status": "in-flight", "t": "x"})
    C._inflight_write({"cid": "old1", "tool": "jawa/destroy_batch", "pid": me, "os": os.name,
                       "status": "in-flight", "t": "x"})
    cids = sorted(x["cid"] for x in C.outstanding_indeterminate())
    good.append(case("4: only the reused-pid marker reads orphaned (own start and pre-start-field markers stay live)",
                     cids == ["reuse1"], cids))
    for c in ("reuse1", "mine1", "old1"):
        C._inflight_clear(c)
    b = bridge({"success": True})
    b.call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
    with open(os.environ["RIMBRIDGE_EVIDENCE_LOG"]) as fh:
        last_start = [json.loads(l) for l in fh if '"start"' in l][-1]
    good.append(case("4: a start row records pid_start", last_start.get("pid_start") == st, last_start))
    return good


def defect5():
    """RIMMANDRAKE_FAIL_CLIENT_CLOSED_ON_UNREADABLE p1.F2: the driver lock is asked for every spelling of this machine,
    and a guard that cannot be read refuses (CROSS_ENV still crosses on purpose); another machine's game is not judged."""
    import io
    import contextlib
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rimflow"))
    import host_guard
    good = []
    real = host_guard.crossing

    def broken():
        raise RuntimeError("lock module half-imported (simulated)")
    try:
        host_guard.crossing = lambda path=None: "the driver lock is held by OWNER (simulated)"
        for host in ("127.0.0.1", "LOCALHOST", "localhost.", "127.0.0.2", "::1", "::ffff:127.0.0.1"):
            good.append(case("5: a held lock is asked for host %r" % host, C._driver_crossing(host) is not None,
                             C._driver_crossing(host)))
        good.append(case("5: another machine's game (192.0.2.7) is not judged by this lock",
                         C._driver_crossing("192.0.2.7") is None))
        host_guard.crossing = broken
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            why = C._driver_crossing("127.0.0.1")
        good.append(case("5: a guard that raises refuses, naming the error", why is not None and "RuntimeError" in why,
                         (why, err.getvalue())))
        clear_markers()
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                bridge({"success": True}).call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
            refused = False
        except C.DriverHeldError:
            refused = True
        good.append(case("5: ... so a mutation is refused", refused))
        os.environ[C.CROSS_ENV] = "selftest crossing on purpose"
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                bridge({"success": True}).call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
            crossed = True
        except C.DriverHeldError:
            crossed = False
        finally:
            os.environ.pop(C.CROSS_ENV, None)
        good.append(case("5: ... and %s still crosses it on purpose" % C.CROSS_ENV, crossed))
        with contextlib.redirect_stderr(io.StringIO()):
            good.append(case("5: a read is never refused by it",
                             bridge({"success": True}).call("jawa/map_info", {}, check=False) == {"success": True}))
    finally:
        host_guard.crossing = real
    good.append(case("5: the real guard on no lock file passes", C._driver_crossing("127.0.0.1") is None,
                     C._driver_crossing("127.0.0.1")))
    return good


def defect6():
    """p1.F3: an inflight directory that cannot be listed refuses (named), where one never made reads empty."""
    good = []
    clear_markers()
    d = C._inflight_dir()
    if os.path.isdir(d):
        shutil.rmtree(d)
    good.append(case("6: no inflight directory yet: nothing outstanding", C.outstanding_indeterminate() == [],
                     C.outstanding_indeterminate()))
    os.makedirs(d)
    real_listdir = os.listdir

    def denied(path="."):     # chmod 000 is no test as root; this is the same refusal on every OS and user
        if os.path.abspath(path) == os.path.abspath(d):
            raise PermissionError(13, "Permission denied (simulated)", path)
        return real_listdir(path)
    os.listdir = denied
    try:
        pend = C.outstanding_indeterminate()
        good.append(case("6: an unlistable inflight directory reads as one UNREADABLE marker, the error named",
                         len(pend) == 1 and pend[0].get("status") == "UNREADABLE marker"
                         and "PermissionError" in str(pend[0].get("error")), pend))
        try:
            bridge({"success": True}).call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
            refused = None
        except (C.RimBridgeError, C.IndeterminateError) as ex:
            refused = "%s: %s" % (type(ex).__name__, ex)
        good.append(case("6: ... and a mutation is refused as UNKNOWN before any intent is written, saying why",
                         refused and refused.startswith("IndeterminateError") and "could not be listed" in refused, refused))
    finally:
        os.listdir = real_listdir
    good.append(case("6: listable again: nothing outstanding", C.outstanding_indeterminate() == [],
                     C.outstanding_indeterminate()))
    return good


class FakeCliBridge(C.RimBridge):
    """RimBridge for _main --call with no socket: tools/call answers REPLY."""
    REPLY = None

    def connect(self):
        self.welcome = {}

    def close(self):
        pass

    def _request(self, method, params=None):
        return {"tools": []} if method == "tools/list" else FakeCliBridge.REPLY


def defect7():
    """p1.F8: a reply saying success:false is recorded as reply_fail when MCP-wrapped too, and the CLI exits 1 on it."""
    import io
    import contextlib
    good = []
    wrapped_false = {"content": [{"type": "text", "text": json.dumps({"success": False, "error": "no such pawn"})}]}
    wrapped_true = {"content": [{"type": "text", "text": json.dumps({"success": True})}]}
    bridge(wrapped_false).call("jawa/map_info", {}, check=False)
    with open(os.environ["RIMBRIDGE_EVIDENCE_LOG"]) as fh:
        end = [json.loads(l) for l in fh if '"end"' in l][-1]
    good.append(case("7: a wrapped success:false is recorded as reply_fail", end.get("outcome") == "reply_fail"
                     and end.get("success") is False, end))
    real = C.RimBridge
    C.RimBridge = FakeCliBridge
    try:
        for reply, want, label in ((wrapped_false, 1, "wrapped success:false"), ({"success": False}, 1, "success:false"),
                                   (wrapped_true, 0, "wrapped success:true"), ({"ok": 1}, 0, "a reply with no success")):
            FakeCliBridge.REPLY = reply
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = C._main(["--host", "127.0.0.1", "--port", "1", "--token", "t", "--call", "jawa/map_info"])
            good.append(case("7: CLI --call answered %s exits %d" % (label, want), rc == want, (rc, err.getvalue()[-300:])))
    finally:
        C.RimBridge = real
    return good


def main():
    good = defect1() + defect2() + defect3() + defect4() + defect5() + defect6() + defect7()
    clear_markers()
    print("%d/%d ok" % (sum(good), len(good)))
    return 0 if all(good) else 1


if __name__ == "__main__":
    sys.exit(main())
