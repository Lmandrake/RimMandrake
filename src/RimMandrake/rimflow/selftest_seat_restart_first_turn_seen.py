#!/usr/bin/env python3
"""A fresh Conductor window that ended its first turn is verified, even when new input follows that end at once
(OPS_RESTART_UNSTICK_BENCH_YCVY_ZEXY).

Measured on Archmagi, 2026-11-26: the relaunched Conductor window aba7072f ended its first turn at 23:21:45.556Z and he
typed "Ready for stuck items" 0.8 s later. The verify step read only the transcript's LAST record (tx_summary
last_kind), so no Dispatcher tick ever saw the window at an ended turn; a 15-min question card later left the transcript
silent for arm_s, restart:BENCH:firstturn failed it at 23:57:35Z, and restart_reconcile alarmed BENCH unmatched until
the next kill verified at 03:04Z. The real tx_summary reads a real transcript here; decide() judges it.

    python3 src/RimMandrake/rimflow/selftest_seat_restart_first_turn_seen.py      exit 0 PASS, 1 FAILED
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_seat_restart as T  # noqa: E402  (its fixtures: schedule, sessions, one tick)

SR = T.SR
KILL = T.T0 + 200


def iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"


def transcript(name, recs):
    p = os.path.join(T.TMP, name + ".jsonl")
    with open(p, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    return p


def user(t, text):
    return {"type": "user", "timestamp": iso(t), "origin": {"kind": "human"},
            "message": {"role": "user", "content": text}}


def assistant(t, stop, **kw):
    return dict({"type": "assistant", "timestamp": iso(t),
                 "message": {"role": "assistant", "stop_reason": stop, "content": [{"type": "text", "text": "x"}],
                             "usage": {"input_tokens": 10}}}, **kw)


def system(t, sub):
    return {"type": "system", "subtype": sub, "timestamp": iso(t)}


def tick(recs, now):
    """The fresh window relaunched after the kill; one tick at now reads this transcript with the real tx_summary."""
    st = T.fresh()
    st["seat_restart"] = {"BENCH": {"state": "killed", "session_id": "sid-old", "pid": 4242, "killed_at": KILL,
                                    "ts": T.T0, "source": "backstop", "ticket": None}}
    new = [T.bsess(sid="sid-new", pid=5555)]
    sch = T.bsched()
    T.run(sch, st, T.obs(sessions=new, intile={"at": KILL + 5}), KILL + 30)
    T.check(T.bstate(st) == "relaunched", "fixture: the fresh window is relaunched")
    tx = SR.tx_summary(transcript("tx%d" % len(os.listdir(T.TMP)), recs))
    acts = T.run(sch, st, T.obs(sessions=new, tx=tx), now)
    return T.bstate(st), acts


def t_first_turn_end_then_his_input_is_verified():
    s, a = tick([user(KILL + 40, "[RimFlow seat restart] wake"), assistant(KILL + 300, "end_turn"),
                 system(KILL + 300.5, "stop_hook_summary"), user(KILL + 301, "Ready for stuck items"),
                 assistant(KILL + 305, "tool_use")], KILL + 360)
    T.check(s == "verified" and "restart_verified" in T.dos(a),
            "an ended first turn followed at once by his input -> verified (%s, %s)" % (s, T.dos(a)))


def t_first_turn_end_then_long_card_is_verified_not_failed():
    late = KILL + 30 + SR.DEFAULTS["arm_s"] + 600
    s, a = tick([user(KILL + 40, "wake"), assistant(KILL + 300, "end_turn"), user(KILL + 301, "go on"),
                 assistant(KILL + 320, "tool_use")], late)
    T.check(s == "verified" and not [x for x in a if x["do"] == "alarm"],
            "an ended first turn, then a question card silent past arm_s -> verified, no firstturn alarm (%s, %s)"
            % (s, T.dos(a)))


def t_controls_still_hold():
    s, _ = tick([user(KILL + 40, "wake"), assistant(KILL + 300, "tool_use")], KILL + 360)
    T.check(s == "relaunched", "control: no ended turn yet -> not verified (%s)" % s)
    s, _ = tick([assistant(KILL - 50, "end_turn"), user(KILL + 40, "wake"), assistant(KILL + 300, "tool_use")],
                KILL + 360)
    T.check(s == "relaunched", "control: an ended turn from before the kill is not the new window's (%s)" % s)
    s, _ = tick([user(KILL + 40, "wake"), assistant(KILL + 300, "stop_sequence", isApiErrorMessage=True,
                                                    error="rate_limit")], KILL + 360)
    T.check(s == "relaunched", "control: a turn an API error ended is no proof (%s)" % s)
    late = KILL + 60 + SR.DEFAULTS["arm_s"] + 1       # past arm_s since the relaunch AND since the last record
    s, a = tick([user(KILL + 40, "wake"), assistant(KILL + 60, "tool_use")], late)
    T.check(s == "failed" and any(x["do"] == "alarm" for x in a),
            "control: never ended a turn and silent for arm_s -> failed + alarm (%s)" % s)


def main():
    SR.UNFILED = lambda t: None
    for fn in (t_first_turn_end_then_his_input_is_verified, t_first_turn_end_then_long_card_is_verified_not_failed,
               t_controls_still_hold):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            T.check(False, "%s raised %s: %s" % (fn.__name__, type(e).__name__, e))
    print("\n%s: %d failure(s)" % ("FAIL" if T.FAILS else "PASS", len(T.FAILS)))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        T.shutil.rmtree(T.TMP, ignore_errors=True)
    sys.exit(rc)
