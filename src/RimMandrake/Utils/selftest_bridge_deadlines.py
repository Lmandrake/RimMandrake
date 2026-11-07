#!/usr/bin/env python3
"""Offline fault suite for the ONE deadline policy and the bridge transport (BRIDGE_DEADLINES_UNIFY_ONE_ABSOLUTE_POLICY;
GPT review 2026-10-10 s4.4, N01, N04, s7 row 9).

    python3 src/RimMandrake/Utils/selftest_bridge_deadlines.py

A scripted fake socket on a fake monotonic clock drives rimbridge_client.RimBridge's real framing code:
 1. event flood / byte trickle: traffic that keeps arriving cannot carry a request past its absolute deadline (N04);
 2. every byte split of a valid stream (events + replies, Unicode, CRLF and LF-only headers), and a one-byte-at-a-time
    feed, yields exactly the reference results;
 3. a timeout mid-frame keeps the parser state; the late reply is dropped as abandoned; no request is sent twice (N01);
 4. EOF, bad/negative/oversize Content-Length, a runaway header, bad JSON or bad UTF-8: a bounded RimBridgeError, the
    connection closed, the next request refused before it sends anything (no false result, no duplicate dispatch);
 5. every deadline-exceeded message states the game process ALIVE / DEAD / UNKNOWN and that nothing was killed;
 6. load_policy.json is versioned and refused when it turns a clock into a kill or a call deadline into a per-read one;
    each declared reader reads it;
 7. grep: every code site that kills RimWorld is a kill-before-launch on the allowlist, none guarded by elapsed time.
"""
import json
import os
import re
import socket
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
os.environ["RIMBRIDGE_ALIVE_PROBE"] = "off"
_tmp = tempfile.mkdtemp(prefix="bdu_selftest_")
os.environ.setdefault("RIMBRIDGE_SESSION_LOG", os.path.join(_tmp, "sessions.jsonl"))
os.environ.setdefault("RIMBRIDGE_EVIDENCE_LOG", os.path.join(_tmp, "evidence.jsonl"))
import load_policy as LP  # noqa: E402
import rimbridge_client as rb  # noqa: E402

FAILS, N = [], [0]


def check(cond, msg):
    N[0] += 1
    print("%s  %s" % ("ok  " if cond else "FAIL", msg))
    if not cond:
        FAILS.append(msg)


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class FakeSock:
    """recv follows a script of (delay_s, bytes); a delay longer than the socket's timeout raises socket.timeout after
    advancing the clock by that timeout (the rest of the delay stays owed). An empty script is EOF."""

    def __init__(self, clock, script):
        self.clock, self.script, self.to, self.sent, self.closed = clock, list(script), None, [], False

    def settimeout(self, t):
        self.to = t

    def sendall(self, data):
        self.sent.append(data)

    def recv(self, n):
        if not self.script:
            return b""
        delay, data = self.script[0]
        if self.to is not None and delay > self.to:
            self.clock.t += self.to
            self.script[0] = (delay - self.to, data)
            raise socket.timeout("timed out")
        self.clock.t += delay
        out, rest = data[:n], data[n:]
        if rest:
            self.script[0] = (0.0, rest)
        else:
            self.script.pop(0)
        return out

    def shutdown(self, how):
        pass

    def close(self):
        self.closed = True


def frame(obj, lf=False):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    sep = "\n" if lf else "\r\n"
    return ("Content-Length: %d%sContent-Type: application/json%s%s" % (len(body), sep, sep, sep)).encode() + body


def client(script, timeout=30.0, ids=("RID1", "RID2", "RID3")):
    clock = Clock()
    b = rb.RimBridge(timeout=timeout)
    b.sock = FakeSock(clock, script)
    seq = iter(ids)
    rb.uuid = types.SimpleNamespace(uuid4=lambda: next(seq))
    rb.load_policy = types.SimpleNamespace(Deadline=lambda s: LP.Deadline(s, clock=clock),
                                           deadline_exceeded=LP.deadline_exceeded, game_alive=lambda: None)
    return b, clock


def err_of(fn):
    try:
        fn()
    except rb.RimBridgeError as ex:
        return str(ex)
    return None


EV = {"type": "event", "channel": "log", "payload": {"msg": "Ünïcødé ✓ 🚀 ж"}}


def reply(rid, val):
    return {"type": "response", "id": rid, "result": {"v": val, "text": "ответ ✓ 🚀"}}


# ---------------------------------------------------------------- 1. flood and trickle
def t_flood():
    flood = [(1.0, frame(EV))] * 1000                     # one event per second, for 1000 s; the reply never comes
    b, clock = client(flood, timeout=30.0)
    t0 = clock.t
    e = err_of(lambda: b._request("tools/call"))
    took = clock.t - t0
    check(e is not None and e.startswith("timed out"), "event flood: the request times out (%r)" % (e or "")[:90])
    check(took <= 30.0 + 1e-6, "event flood: stopped at its absolute deadline, %.1f s of 30 (per-read would be 1000)"
          % took)
    check(29 <= len(b.events) <= 31, "the flood's events were parked, not lost: %d" % len(b.events))
    check(e and "deadline exceeded" in e and "game process UNKNOWN" in e and "nothing was killed" in e,
          "the message is the policy's deadline-exceeded sentence with the process state: %r" % (e or "")[:160])
    check(len(b.sock.sent) == 1, "one request sent, never retried: %d" % len(b.sock.sent))

    data = frame(reply("RID1", 1))
    trickle = [(0.5, data[i:i + 1]) for i in range(len(data))]   # a byte every 0.5 s: ~%d s for the whole frame
    b, clock = client(trickle, timeout=30.0)
    t0 = clock.t
    e = err_of(lambda: b._request("tools/call"))
    check(e is not None and e.startswith("timed out") and clock.t - t0 <= 30.0 + 1e-6,
          "byte trickle (%d bytes x 0.5 s): timed out at %.1f s of 30" % (len(data), clock.t - t0))

    b, clock = client([(10.0, frame(EV))] * 2 + [(5.0, frame(reply("RID1", 7)))], timeout=30.0)
    r = b._request("tools/call")
    check(r and r.get("v") == 7, "events then a reply inside the deadline: answered (%r)" % r)
    check(b._deadline is None, "the deadline is cleared once the request ends")


def t_pipeline_flood():
    """northstar_driver's pipelined call_many reads frames itself: its batch gets one absolute deadline too."""
    sys.path.insert(0, os.path.join(HERE, "northstar_driver"))
    import transport as TR
    b, clock = client([(1.0, frame(EV))] * 1000, timeout=10.0)
    b.check_params = lambda tool, params: None
    real = LP.Deadline
    LP.Deadline = lambda s: real(s, clock=clock)
    try:
        t0 = clock.t
        try:
            TR.TimedTransport(b, pipeline=True).call_many([("get_a", {}), ("get_b", {})])
            e = None
        except rb.RimBridgeError as ex:
            e = str(ex)
    finally:
        LP.Deadline = real
    check(e is not None and e.startswith("timed out") and clock.t - t0 <= 20.0 + 1e-6 and len(b.sock.sent) == 2,
          "pipelined batch of 2 x 10 s under an event flood: stopped at %.1f s of 20, 2 sends (%r)"
          % (clock.t - t0, (e or "")[:60]))
    check(b._deadline is None and len(b.abandoned) == 2, "the batch deadline is cleared, its ids abandoned")


# ---------------------------------------------------------------- 2. every split
def t_splits():
    for lf in (False, True):
        stream = frame(EV, lf) + frame(reply("RID1", 1), lf) + frame(EV, lf) + frame(reply("RID2", 2), lf)

        def run(chunks):
            b, _ = client([(0.0, c) for c in chunks], timeout=30.0)
            a = b._request("x")
            c = b._request("y")
            return a, c, len(b.events), b.buf

        ref = run([stream])
        check(ref[0]["v"] == 1 and ref[1]["v"] == 2 and ref[2] == 2 and ref[0]["text"] == "ответ ✓ 🚀",
              "%s reference: two replies, two events, Unicode intact" % ("LF" if lf else "CRLF"))
        bad = [k for k in range(1, len(stream)) if run([stream[:k], stream[k:]]) != ref]
        check(not bad, "%s: all %d two-chunk splits give the reference (bad at %s)" % (
            "LF" if lf else "CRLF", len(stream) - 1, bad[:5]))
        check(run([stream[i:i + 1] for i in range(len(stream))]) == ref,
              "%s: a one-byte-at-a-time feed gives the reference" % ("LF" if lf else "CRLF"))
    b, _ = client([(0.0, frame(reply("RID1", 1), lf=True) + frame(reply("RID2", 2)))])
    check(b._request("x")["v"] == 1 and b._request("y")["v"] == 2,
          "an LF-only frame followed by a CRLF frame: the earlier separator ends each header")


# ---------------------------------------------------------------- 3. partial-frame timeout
def t_partial_timeout():
    late = frame(reply("RID1", 1))
    half = len(late) // 2
    b, clock = client([(0.0, late[:half]), (40.0, late[half:]), (0.0, frame(reply("RID2", 2)))], timeout=30.0)
    e = err_of(lambda: b._request("first"))
    check(e is not None and e.startswith("timed out"), "a reply stalled mid-body times out: %r" % (e or "")[:80])
    check(b.buf == late[:half], "parser state preserved: the half frame is still buffered, never re-parsed mid-frame")
    check("RID1" in b.abandoned, "the timed-out request is marked abandoned (its outcome is the caller's to settle)")
    r = b._request("second")
    check(r and r.get("v") == 2, "the next request gets ITS reply; the late one is dropped, not taken as the answer")
    check(len(b.sock.sent) == 2, "two requests, two sends: nothing was dispatched twice (%d)" % len(b.sock.sent))


# ---------------------------------------------------------------- 4. EOF and malformed frames
def t_malformed():
    cases = {
        "EOF mid-frame": [(0.0, frame(reply("RID1", 1))[:20])],
        "Content-Length abc": [(0.0, b"Content-Length: abc\r\n\r\n{}")],
        "Content-Length -5": [(0.0, b"Content-Length: -5\r\n\r\n{}")],
        "Content-Length oversize": [(0.0, b"Content-Length: 99999999999\r\n\r\n{}")],
        "no Content-Length": [(0.0, b"Content-Type: application/json\r\n\r\n{}")],
        "runaway header": [(0.0, b"X-Junk: " + b"a" * 20000)],
        "body not JSON": [(0.0, b"Content-Length: 5\r\n\r\nnot{}")],
        "body not UTF-8": [(0.0, b"Content-Length: 4\r\n\r\n\"\xff\xfe\"")],
    }
    for name, script in cases.items():
        tail = [] if name.startswith("EOF") else [(0.0, frame(reply("RID1", 1)))] * 3   # EOF: the script ends
        b, clock = client(script + tail, timeout=30.0)
        t0 = clock.t
        e = err_of(lambda: b._request("x"))
        check(e is not None and clock.t - t0 < 30.0 and b.sock is None,
              "%s: bounded RimBridgeError, connection closed (%r)" % (name, (e or "")[:70]))
        e2 = err_of(lambda: b._request("y"))
        check(e2 is not None and "closed" in e2, "%s: the next request refuses without sending (%r)" % (name, (e2 or "")[:50]))
    b, _ = client([(0.0, b"Content-Length: 3\r\n\r\n")])
    check("closed the connection" in (err_of(lambda: b._request("x")) or ""), "EOF after a header: 'closed', no result")


# ---------------------------------------------------------------- 5. alive / dead in every message
def t_alive_messages():
    for alive, word in ((True, "ALIVE"), (False, "DEAD"), (None, "UNKNOWN")):
        m = LP.deadline_exceeded("x", 31.0, 30.0, alive=alive)
        check("deadline exceeded" in m and "game process %s" % word in m and "nothing was killed" in m,
              "deadline_exceeded(alive=%r) says %s: %r" % (alive, word, m))
    for alive, word in ((True, "ALIVE"), (False, "DEAD")):
        b, _ = client([(100.0, b"")], timeout=5.0)
        rb.load_policy.game_alive = lambda a=alive: a
        os.environ["RIMBRIDGE_ALIVE_PROBE"] = "on"
        e = err_of(lambda: b._request("x"))
        os.environ["RIMBRIDGE_ALIVE_PROBE"] = "off"
        check(e and "game process %s" % word in e, "client timeout with the probe answering %r says %s" % (alive, word))
    src = open(os.path.join(REPO, "src/RimMandrake/bridgetools/launch_ready.py"), encoding="utf-8").read()
    check(re.search(r'"DEADLINE_ALIVE", "deadline exceeded:.*?game "\s*"process ALIVE', src, re.S) is not None,
          "launch_ready's deadline verdict states the process ALIVE and left running")


# ---------------------------------------------------------------- 6. the policy file
def t_policy():
    pol = LP.load()
    check(pol["version"] == LP.VERSION == 2 and pol["call_deadline"] == "absolute_monotonic"
          and pol["kill_on_deadline"] is False, "load_policy.json is v2, absolute call deadline, no kill on deadline")
    for bad, why in (({"version": 1}, "an old version"), ({"kill_on_deadline": True}, "a deadline that kills"),
                     ({"call_deadline": "per_read"}, "a per-read call deadline")):
        p = os.path.join(_tmp, "pol.json")
        with open(p, "w") as fh:
            json.dump(dict(pol, **bad), fh)
        try:
            LP.load(p)
            refused = False
        except LP.PolicyError:
            refused = True
        check(refused, "the loader refuses %s" % why)
    for rel in LP.READERS:
        txt = open(os.path.join(REPO, rel), encoding="utf-8").read()
        check(re.search(r"\bimport load_policy\b|load_policy\.", txt) is not None, "reader %s reads load_policy" % rel)
    rg = open(os.path.join(REPO, "src/RimMandrake/rimflow/relentless_game.py"), encoding="utf-8").read()
    check("load_policy" in rg and "load_unknown_s" not in rg and "load_per_mod_s" not in rg,
          "relentless_game's cold-load bound is the policy's, the rival per-mod budget is gone")
    pr = open(os.path.join(REPO, "src/RimMandrake/FlowWorks/northstar/playtest_runner.py"), encoding="utf-8").read()
    check("playtest_run_wall_s" in pr and "default=1500" not in pr, "playtest_runner's wall limit is the policy's")
    d = LP.Deadline(10, clock=Clock())
    d.clock.t += 4
    check(abs(d.remaining() - 6) < 1e-9 and not d.expired(), "Deadline counts down on its clock")
    d.clock.t += 6
    check(d.expired(), "Deadline expires at its absolute instant")


# ---------------------------------------------------------------- 7. no clock-only game kill
GAME_KILL = re.compile(r"taskkill[^\n]*RimWorld|Stop-Process[^\n]*RimWorld|kill_pid\(|RimWorldWin64[^\n]*\.kill\("
                       r"|game_instance\.py[^\n]* stop\b|game_instance\.stop\(|instance\(\)\.stop\(", re.I)   # stopping now goes through this
CLOCK_GUARD = re.compile(r"time\.time\(\)\s*-|monotonic\(\)\s*-|\belapsed\b|\bdeadline\b|\bage\s*[<>]|-gt\s+\d{3}|\bbound\b")
# Every site that kills RimWorld, and why it is not a clock: each kills a game BEFORE a launch it was asked to make.
ALLOW = {
    "src/RimMandrake/bridgetools/launch_ready.py": "step 1 replaces a pre-existing game before launching",
    "src/RimMandrake/Utils/northstar_driver/live_session.py": "stop_game() before the session's own launch",
    "src/RimMandrake/Utils/loadsweep/sweep_load.sh": "kills before each batch's launch",
    "src/RimMandrake/Utils/loadsweep/biome_load_proof.sh": "kills before each biome's tier write and launch",
    "src/RimMandrake/Utils/rimbench/gl_sheet_run.sh": "kills before each record's launch",
    "src/RimMandrake/rimflow/relentless_stage.py": "game_down() before the staging's deploy and launch",
    "src/RimMandrake/Utils/game_instance.py": "the stopping tool itself: acts when asked, by pid, on no clock",
}


def t_no_clock_kill():
    hits = {}
    for root in ("src", "infrastructure/hooks"):
        for dp, dn, fn in os.walk(os.path.join(REPO, root)):
            dn[:] = [d for d in dn if d not in ("arena", "__pycache__", "bin", "obj", ".git")]
            for f in fn:
                if not f.endswith((".py", ".sh", ".ps1")) or f.startswith("selftest"):
                    continue
                p = os.path.join(dp, f)
                try:
                    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
                except OSError:
                    continue
                for i, ln in enumerate(lines):
                    if GAME_KILL.search(ln) and not ln.lstrip().startswith(("#", "def ")):
                        hits.setdefault(os.path.relpath(p, REPO).replace(os.sep, "/"), []).append((i, lines))
    check(len(hits) >= 3 and "src/RimMandrake/bridgetools/launch_ready.py" in hits,
          "sanity: the scan sees the known kill sites (%d files)" % len(hits))
    stray = sorted(set(hits) - set(ALLOW))
    check(not stray, "every game-kill site is an allowlisted kill-before-launch: unlisted %s" % stray)
    guarded = []
    for rel, sites in hits.items():
        for i, lines in sites:
            ctx = "\n".join(lines[max(0, i - 3):i])
            if CLOCK_GUARD.search(ctx):
                guarded.append("%s:%d" % (rel, i + 1))
    check(not guarded, "no game kill sits under an elapsed-time test: %s" % guarded)
    probe = CLOCK_GUARD.search("        if time.time() - t0 > 1500:")
    check(probe is not None, "sanity: the clock-guard pattern sees an elapsed-time test")


def main():
    for t in (t_flood, t_pipeline_flood, t_splits, t_partial_timeout, t_malformed, t_alive_messages, t_policy, t_no_clock_kill):
        print("-- %s" % t.__name__)
        t()
    print("selftest_bridge_deadlines: %s (%d checks, %d failed)" % ("FAIL" if FAILS else "PASS", N[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
