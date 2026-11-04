#!/usr/bin/env python3
"""selftest_seat_restart_send_again.py — B4 'send it again' line on the Conductor's goodbye wake
(CONDUCTOR_PROMPT_WIRE_SEND_IT_AGAIN_LINE; design/RimMandrake/conductor_briefing_2026-10-28.md B4).

  S1 a real goodbye-restart wake prints SAY FIRST + the exact B4 line, before his recovered messages
  S2 the line is printed even when the old transcript is unreadable (the UNMEASURED path)
  S3 NEGATIVE: no restart record, or an aborted restart (nobody was killed), prints no such line
  S4 cmd_wake's Conductor branch reaches _wake_conductor (the line is on the wake path, not dead code)
All in a temp dir; no window is killed or launched.
"""
import contextlib
import io
import inspect
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_send_again_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_SEAT_LOG_DIR"] = os.path.join(TMP, "seat_log")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import seat_restart as SR  # noqa: E402

FAILS = []
LINE = "If you wrote in the last few minutes and I do not answer it, send it again."
CFG = {"kind": "conductor", "grace_s": 120, "goodbye_quiet_s": 600}


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def _tx(name, recs):
    p = os.path.join(TMP, name + ".jsonl")
    with open(p, "w") as f:
        f.write("\n".join(json.dumps(r) for r in recs) + "\n")
    return p


def _u(ts, text):
    return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": text},
            "origin": {"kind": "human"}, "promptSource": "typed"}


def _wake(rec, root):
    os.makedirs(os.path.join(root, "restart"), exist_ok=True)
    out = io.StringIO()
    real = SR.transcript_for
    try:
        SR.transcript_for = lambda me, cfg: "/tx/" + me["sessionId"]
        with contextlib.redirect_stdout(out):
            SR._wake_conductor("BENCH", CFG, rec, root=root, me={"sessionId": "fresh"})
    finally:
        SR.transcript_for = real
    return out.getvalue()


def test_s1_line_on_real_wake():
    old = _tx("s1_old", [_u("1970-01-12T13:45:00Z", "goodbye")])
    off = os.path.getsize(old)
    with open(old, "a") as f:
        f.write(json.dumps(_u("1970-01-12T13:46:00Z", "LATE_MESSAGE_H1")) + "\n")
    rec = {"seat": "BENCH", "session_id": "sid-old", "killed_at": 1e6, "req_ts": 1e6, "gen": "g1",
           "tx_path": old, "tx_offset": off}
    got = _wake(rec, os.path.join(TMP, "s1"))
    check(LINE in got and "SAY FIRST" in got, "S1 a goodbye wake prints the B4 line (%r)" % got[:300])
    check(SR.SEND_IT_AGAIN == LINE, "S1 the constant is the B4 text word for word")
    check(LINE in got and "LATE_MESSAGE_H1" in got and got.index(LINE) < got.index("LATE_MESSAGE_H1"),
          "S1 the line comes before his recovered messages")


def test_s2_line_when_unreadable():
    rec = {"seat": "BENCH", "session_id": "sid-old", "killed_at": 1e6, "req_ts": 1e6, "gen": "g2",
           "tx_path": os.path.join(TMP, "missing.jsonl"), "tx_offset": 10}
    got = _wake(rec, os.path.join(TMP, "s2"))
    check("UNMEASURED" in got and LINE in got, "S2 the line is said even when the old transcript is unreadable (%r)" % got[:300])


def test_s3_negative_no_restart():
    got = _wake({}, os.path.join(TMP, "s3a"))
    check(LINE not in got and "no restart record" in got, "S3 no restart record: no line (%r)" % got[:200])
    got = _wake({"seat": "BENCH", "gen": "g3", "aborted": "held by a helper"}, os.path.join(TMP, "s3b"))
    check(LINE not in got and "ABORTED" in got, "S3 an aborted restart: no line (%r)" % got[:200])


def test_s4_on_the_wake_path():
    src = inspect.getsource(SR.cmd_wake)
    check('cfg.get("kind") == "conductor"' in src and "_wake_conductor(" in src,
          "S4 cmd_wake's Conductor branch calls _wake_conductor")
    check("SAY_FIRST" in inspect.getsource(SR._wake_conductor), "S4 _wake_conductor prints SAY_FIRST")


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (name, type(e).__name__, e))
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
