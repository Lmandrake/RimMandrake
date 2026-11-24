#!/usr/bin/env python3
"""Live proof of jawa/act_batch. Page: design/specs/2026-11-23-bridge-v2-hands/boundary.md. Item
RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH.

    python.exe prove_act_batch.py [--out DIR]      on a TEST-profile game, a scratch quicktest map. It spawns and hurts one animal.
    python3 prove_act_batch.py --selfcheck         the judges, good and planted; no game

Rows: 1 no frame between two acts: a per-frame counter that the batch does not write (JawaBenchVitals.FrameSerial, read by the first and
the last act of the batch) is equal, and the same counter moved between two calls  2 a repeated damage request leaves the victim's health
as after one hit, while a new id hits again  3 a changed repeat does nothing  4 a batch whose second act says no keeps the first and
does not try the third  5 a tool that waits, a tool of the host and a nested hand are refused by name, with nothing done  6 the census of the
tools that can be in a batch  7 a batch on a running game is refused.
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED."""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prove_run_until as R  # noqa: E402
W = R.W

COUNTER = {"id": None, "tool": "jawa/read_paths", "args": {"reads": [{"of": "static:JawaBench.BridgeTools.JawaBenchVitals", "path": "FrameSerial"}]}}


# ------------------------------------------------------------------------------------------------ the judges (pure)
def counter(act):
    v = ((act.get("reply") or {}).get("values") or [{}])[0] if act.get("state") == "done" else {}
    return v.get("v") if v.get("state") == "ok" else None


def judge_frames(reply, before, after):
    """Equal inside the batch, and NOT equal across two calls: a counter that never moves proves nothing."""
    acts = reply.get("acts") or []
    if len(acts) != 4 or None in (before, after) or any(a.get("state") != "done" for a in acts):
        return None, "acts %s, counter before %s after %s, %s" % ([(a.get("id"), a.get("state"), str(a.get("error"))[:80]) for a in acts], before, after, R.brief(reply))
    a, b = counter(acts[0]), counter(acts[3])
    if None in (a, b) or not before < after:
        return None, "the counter does not count: %s" % [before, a, b, after]
    return a == b and reply["frameFrom"] == reply["frameTo"], "counter in the batch %s and %s; before %s, after %s; frames %s to %s" % (a, b, before, after, reply["frameFrom"], reply["frameTo"])


def judge_hits(h0, h1, h2, h3):
    """Health before, after one hit, after the repeat, after a new id."""
    if None in (h0, h1, h2, h3):
        return None, "health not read: %s" % [h0, h1, h2, h3]
    if not h1 > h0:
        return None, "the first hit did nothing: %s" % [h0, h1]
    return h2 == h1 and h3 > h2, "injuries (count, severity): before %s, one hit %s, the repeat %s, a new id %s" % (h0, h1, h2, h3)


def selfcheck():
    def rep(a=7, b=7, f=3, state="done"):
        def rd(n):
            return {"id": "r", "state": "done", "reply": {"values": [{"state": "ok", "v": n}]}}
        return {"acts": [rd(a), {"id": "x", "state": state}, {"id": "y", "state": "done"}, rd(b)], "frameFrom": 3, "frameTo": f}
    cases = [
        ("frames good", judge_frames(rep(), 5, 9)[0], True), ("one frame between", judge_frames(rep(b=8), 5, 9)[0], False),
        ("the reply's frames differ", judge_frames(rep(f=4), 5, 9)[0], False), ("a dead counter", judge_frames(rep(), 7, 7)[0], None),
        ("an act not done", judge_frames(rep(state="failed"), 5, 9)[0], None), ("no batch", judge_frames({}, 5, 9)[0], None),
        ("hits good", judge_hits((0, 0), (1, 5), (1, 5), (2, 9))[0], True), ("hit twice by the repeat", judge_hits((0, 0), (1, 5), (2, 9), (3, 12))[0], False),
        ("a new id does nothing", judge_hits((0, 0), (1, 5), (1, 5), (1, 5))[0], False), ("no hit", judge_hits((0, 0), (0, 0), (0, 0), (0, 0))[0], None),
        ("unread", judge_hits((0, 0), None, (1, 5), (2, 9))[0], None),
    ]
    bad = [n for n, got, want in cases if got is not want]
    for n, got, want in cases:
        print("%s %s -> %s" % ("ok  " if got is want else "FAIL", n, got))
    print("prove_act_batch judges: %d of %d" % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------- the game
def batch(*acts):
    return W.call("jawa/act_batch", driver=R.DRIVER, acts=json.dumps(list(acts)))


def health(pid):
    """(number of injuries, sum of their severities) by the private fields, or None."""
    n = R.read(("thing:" + pid, "health.hediffSet.hediffs._size"))
    if not n or n[0]["state"] != "ok":
        return None
    sev = R.read(*[("thing:" + pid, "health.hediffSet.hediffs[%d].severityInt" % i) for i in range(int(n[0]["v"]))])
    return None if any(s["state"] != "ok" for s in sev) else (int(n[0]["v"]), round(sum(s["v"] for s in sev), 4))


def act(tool, rid=None, **args):
    return {"id": rid or R.req("act"), "tool": tool, "args": args}


def frames():
    v = R.read(("static:JawaBench.BridgeTools.JawaBenchVitals", "FrameSerial"))
    return v[0]["v"] if v and v[0]["state"] == "ok" else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    os.makedirs(a.out, exist_ok=True)
    W.connect()
    row = W.row
    if not R.start_map():
        return 2
    s = R.open_session()
    pl = [p for p in W.call("jawa/pawn_get", limit=200).get("pawns") or [] if p.get("faction") == "PlayerColony"][0]
    x, z = pl.get("x"), pl.get("z")
    if x is None:
        x, z = pl["position"]["x"], pl["position"]["z"]
    pid, sp = R.animal(x + 6, z + 3)
    if not pid:
        row("victim", None, sp)
        return 2

    def hit(rid=None, amount=4):
        return act("jawa/damage", rid, damageDef="Cut", amount=amount, thingId=pid, armorPenetration=9, bodyPart="Torso")
    f0 = frames()
    time.sleep(0.5)
    r = batch(dict(COUNTER, id=R.req("c")), act("jawa/map_info"), act("jawa/pawn_get", pawn=pid), dict(COUNTER, id=R.req("c")))
    time.sleep(0.5)
    v, d = judge_frames(r, f0, frames())
    row("1 no frame between two acts", v, d)

    h0, one = health(pid), hit()
    r1 = batch(one)
    h1 = health(pid)
    time.sleep(0.3)
    r2 = batch(one)
    h2 = health(pid)
    r3 = batch(hit())
    h3 = health(pid)
    v, d = judge_hits(h0, h1, h2, h3)
    row("2 a repeated hit is done once", v and (r2.get("acts") or [{}])[0].get("replayed") is True if v is not None else None, "%s; %s" % (d, [R.brief(x_) or (x_.get("acts") or [{}])[0].get("state") for x_ in (r1, r2, r3)]))
    bad = batch(act("jawa/map_info"), dict(one, args=dict(one["args"], amount=9)))
    row("3 a changed repeat does nothing", None if bad.get("_error") else bad.get("refused") == "REQUEST_CONFLICT" and health(pid) == h3, R.brief(bad))
    mix = batch(hit(), act("jawa/damage", damageDef="Cut", amount=1, thingId="NoSuchThing"), act("jawa/map_info"))
    st = [m.get("state") for m in mix.get("acts") or []]
    row("4 the acts before a refused one stay", None if len(st) != 3 else st in (["done", "refused", "not_tried"], ["done", "failed", "not_tried"]) and health(pid) > h3, "%s %s" % (st, R.brief(mix)))
    h4 = health(pid)
    want = {"NOT_ONE_HOP": act("jawa/pawn_use_ability", pawn=pid), "UNKNOWN_TOOL": act("rimworld/get_ui_state"), "NESTED_HAND": act("jawa/run_until"), "BAD_ARGS": act("jawa/map_info", nonsense=1)}
    got = {k: batch(hit(), w).get("refused") for k, w in want.items()}
    waits = batch(hit(), act("jawa/ordered_job", pawn=pid)).get("refused")
    row("5 refusals by name, nothing done", None if None in got.values() else all(k == g for k, g in got.items()) and waits == "NOT_ONE_HOP" and health(pid) == h4, "%s, ordered_job with its wait: %s" % (got, waits))
    c = W.call("jawa/act_batch", action="census")
    row("6 the census", None if not c.get("success") else c["tools"] > 400 and 0 < len(c["notOneHop"]) < 40, "%s tools, not one hop %s, only with no wait %s" % (c.get("tools"), c.get("notOneHop"), c.get("oneHopWithNoWait")))
    rid = R.req("play")
    W.call("jawa/run_until", action="start", driver=R.DRIVER, request=rid, until=json.dumps(R.at_tick(R.tick() + 5000)), limit=5000)
    run = batch(hit())
    W.call("jawa/run_until", action="cancel", driver=R.DRIVER, request=rid)
    row("7 a batch on a running game", None if run.get("_error") else run.get("refused") in ("RUN_ACTIVE", "GAME_RUNNING") and health(pid) == h4, R.brief(run))
    done = R.end_session()
    tr = R.read_session(done, s["session"])
    with open(os.path.join(a.out, "act_batch.json"), "w", encoding="utf-8") as f:
        json.dump({"census": c, "trace": tr}, f, indent=1)
    why = R.whole(tr)
    row("8 the trace is whole", None if not tr else why is None, why or "%d rows, %d acts" % (len(tr), len(R.recs(tr, "act_end"))))
    n = dict((v_, sum(1 for _r, x_ in W.ROWS if x_ == v_)) for v_ in ("PASS", "FAIL", "UNMEASURED"))
    print("act batch live: %d PASS, %d FAIL, %d UNMEASURED" % (n["PASS"], n["FAIL"], n["UNMEASURED"]))
    return 1 if n["FAIL"] else (2 if n["UNMEASURED"] or not W.ROWS else 0)


if __name__ == "__main__":
    sys.exit(R.closing(main))
