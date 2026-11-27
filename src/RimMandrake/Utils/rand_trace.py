#!/usr/bin/env python3
"""rand_trace - the live driver of the Verse.Rand draw tracer (`jawa/rand_trace`) over a scene_compare plan.

Item RIMMANDRAKE_FIND_RAND_DRAWS_PARTING_RUNS_EVEN_STEP. One arming run (PLAY speed 1, no write-back) gives the random state;
then each sample run loads the plan's fixture save fresh, arms the tracer, writes that random state back (the write-back opens
the tracer's window), plays, and reads the trace. The verdict is rand_trace_verdict.py's, over the JSON this writes.

    python.exe rand_trace.py --plan scene_compare_plans/colony_drift_rand.py --arms step,play1 --n 3 [--game ArchSmall]
                             [--window 40] [--depth 4] [--isolate Verse.FishShadowComponent:MapComponentTick] [--out <runs.json>]

`--isolate` is the fix experiment: the tracer wraps each named method in Rand.PushState/PopState while armed.

Exit 0: every sample gave a trace; 1: a sample failed (named in the JSON); 2: could not look (the arming run gave nothing).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import scene_compare as sc  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "design", "specs", "2026-11-23-bridge-v2", "experiments", "rand_trace_runs.json")


def _reply(r):
    """The tool's own fields, whether the bridge wrapped them or not."""
    d = dict(r or {})
    for k in ("result", "structuredContent", "data"):
        if isinstance(d.get(k), dict) and ("ticks" in d[k] or "state" in d[k]):
            return d[k]
    return d


def run(plan_path, arms, n, game, window, depth, out, isolate=""):
    import scene
    m, plan_sha = sc._load_plan(plan_path)
    from scene import cond as c
    p = m.plan(c)
    needs = {"map": m.SAVE}
    if getattr(m, "CALM", None):
        needs["calm"] = m.CALM

    def one(arm, rand, trace):
        got = {"arm": arm, "rand_want": rand}
        for attempt in (1, 2, 3):
            try:
                with scene.open(game, needs=needs) as s:
                    if trace:
                        a = _reply(s.raw("jawa/rand_trace", action="arm", window=window, depth=depth, isolate=isolate))
                        if a.get("success") is not True:
                            got["failed"] = "arm refused: %s" % a.get("message")
                            return got
                    t0 = time.monotonic()
                    r = s.run(until=p["until"], limit=m.LIMIT, speed=sc.SPEED[arm], record=p.get("record"), rand=rand)
                    got["wall_s"] = time.monotonic() - t0
                    if trace:
                        got["trace"] = _reply(s.raw("jawa/rand_trace", action="read", maxRows=200000))
                        s.raw("jawa/rand_trace", action="off")
                    with open(r.trace) as f:
                        got["rows"] = [json.loads(x) for x in f if x.strip()]
                    got["why"], got["trace_file"] = r.why, r.trace
                    got["build"] = s.build
                return got
            except (scene.Fault, scene.Refused) as e:
                rep = getattr(e, "report", None) or []
                lock_only = bool(rep) and rep[0].get("state") == "refused" and all(x.get("state") == "not reached" for x in rep[1:])
                if lock_only and attempt < 3:
                    time.sleep(5)
                    continue
                got["failed"] = "%s: %s" % (type(e).__name__, str(e).splitlines()[0])
                return got
        return got

    first = one(sc.REFERENCE, None, False)
    if first.get("failed"):
        print("COULD NOT LOOK: the arming run gave no trace: %s" % first["failed"])
        return 2
    o = sc._open(first["rows"])
    rand = str(o.get("rand")) if o.get("rand") is not None else None
    if rand is None:
        print("COULD NOT LOOK: the open record has no random state")
        return 2
    runs = []
    for arm in arms:
        for _i in range(n):
            got = one(arm, rand, True)
            got["scene_rows"] = len(got.pop("rows", []))       # the scene trace stays in its own file (got["trace_file"])
            got.pop("build", None)
            runs.append(got)
            tr = got.get("trace") or {}
            print("run %d %s: %s ticks traced, %s seen, draws %s, pushed %s, foreign %s, faults %s%s" % (
                len(runs) - 1, arm, tr.get("ticksTraced"), tr.get("ticksSeen"), tr.get("draws"), tr.get("pushed"), tr.get("foreign"),
                tr.get("faults"), (" FAILED " + got["failed"]) if got.get("failed") else ""))
            sys.stdout.flush()
    data = {"plan": os.path.relpath(plan_path, ROOT).replace("\\", "/"), "plan_sha": plan_sha, "game": game, "window": window,
            "depth": depth, "isolate": isolate, "origin_rand": rand, "build": first.get("build"), "runs": runs}
    with open(out, "w") as f:
        json.dump(data, f, indent=1, default=str)
    print("wrote %s" % out)
    return 1 if any(r.get("failed") for r in runs) else 0


def main(argv):
    ap = argparse.ArgumentParser(prog="rand_trace.py")
    ap.add_argument("--plan", default=os.path.join(HERE, "scene_compare_plans", "colony_drift_rand.py"))
    ap.add_argument("--arms", default="step")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--game", default="ArchSmall")
    ap.add_argument("--window", type=int, default=40)
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--isolate", default="")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    bad = [x for x in arms if x not in sc.SPEED]
    if bad:
        print("REFUSED: arms are %s, not %s" % (", ".join(sc.SPEED), bad))
        return 3
    return run(a.plan, arms, a.n, a.game, a.window, a.depth, a.out, a.isolate)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
