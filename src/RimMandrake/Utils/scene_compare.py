#!/usr/bin/env python3
"""scene_compare - one scene played in several arms (PLAY speed 1, PLAY speed 3, PLAY Ultrafast, STEP), traces compared tick by tick.

Item RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED. Promises, limits and what is not promised:
design/specs/2026-11-23-bridge-v2/boundary.md §PLAY AGAINST STEP. The rule it serves: an arm that was not compared with the reference
counts for no bar (src/RimMandrake/Utils/scene_contracts/run.md).

    python.exe scene.py compare --plan <plan.py> --arms play1,play3,ultra,step --n 5 [--game ArchSmall]

The core (everything above `run_live`) is pure: it reads traces (schema scene_trace_v1) and sample records, and writes nothing.
A comparison answers EQUAL, DIVERGED (with the first tick, what and both values) or COULD_NOT_COMPARE (with why). A missing tick
range is COULD_NOT_COMPARE, never EQUAL. Wall time is never compared.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import scene_hands as hands  # noqa: E402

REFERENCE = "play1"
# arm -> the speed that jawa/run_until takes, in order of trust (05_build_design.md §Time modes)
ARMS = (("play1", "Normal"), ("play3", "Superfast"), ("ultra", "Ultrafast"), ("step", "Step"))
SPEED = dict(ARMS)
EQUAL, DIVERGED, COULD_NOT = "EQUAL", "DIVERGED", "COULD_NOT_COMPARE"
# fields that carry wall time, frame numbers, sequence or identity, never the game's state: never compared
WALL = frozenset(("seq", "n", "run", "ms", "msMax", "cost", "costliest", "wallS", "wall", "alloc", "lockReads", "frame", "frameFrom",
                  "frameTo", "at", "mono", "utc", "elapsedMs"))
# bookkeeping records: compared by their own rule below, not field by field
OWN_RULE = ("open", "track", "end", "close")
# an end of the run's own (the game's state decided it); any other end leaves the rest of the range unseen
OWN_ENDS = ("hit", "done", "limit", "unknown")


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def _offset(r, t0):
    return int(r["tick"]) - t0


def _open(rows):
    return next((r for r in rows if r.get("rec") == "open"), None)


def timeline(rows):
    """The trace as the game's state on each tick, offset from the start. Pure.
    -> {"from": tick, "to": offset of the end, "tracks": {name: [(offset, st, v), ...]} (on change), "events": [(offset, sig)],
        "end": (state, hit offset or None, executed)}"""
    o = _open(rows)
    t0 = int(o["tick"])
    tracks, events, end = {}, [], None
    for r in sorted(rows, key=lambda r: r.get("n") or 0):
        k = r.get("rec")
        if k == "track":
            tracks.setdefault(r["name"], []).append((_offset(r, t0), r.get("st"), r.get("v")))
        elif k == "end":
            hit = r.get("hitTick")
            end = (r.get("state"), int(hit) - t0 if hit is not None else None, r.get("executed"))
        elif k == "act":
            events.append((_offset(r, t0), _canon({"rec": "act", "name": r.get("name"), "ok": r.get("ok")})))
        elif k == "fault":
            events.append((_offset(r, t0), _canon({"rec": "fault", "what": r.get("what")})))
        elif k not in OWN_RULE:
            # a tap, and any record kind that comes later: every field but wall time, so no kind is ignored
            events.append((_offset(r, t0), _canon({f: v for f, v in r.items() if f not in WALL and f not in ("tick", "phase")})))
    last = max([_offset(r, t0) for r in rows if r.get("rec") in ("track", "end", "act", "fault")] + [0])
    return {"from": t0, "to": last, "tracks": tracks, "events": events, "end": end}


def _value_at(changes, off):
    """The track's (st, v) at the end of tick `off`: its last change at or before it."""
    cur = None
    for o, st, v in changes:
        if o > off:
            break
        cur = (st, v)
    return cur


def compare(ref_rows, arm_rows):
    """Two traces of one scene, tick by tick. Pure. -> {"verdict", "tick" (offset), "what", "ref", "arm", "why", "ticks"}"""
    for name, rows in (("reference", ref_rows), ("arm", arm_rows)):
        bad = hands.trace_fault(rows) if rows else "no trace"
        if bad:
            return {"verdict": COULD_NOT, "why": "the %s trace is not whole: %s" % (name, bad)}
    a, b = timeline(ref_rows), timeline(arm_rows)
    if set(a["tracks"]) != set(b["tracks"]):
        return {"verdict": COULD_NOT, "why": "the tracks differ: only in the reference %s, only in the arm %s" % (
            sorted(set(a["tracks"]) - set(b["tracks"])), sorted(set(b["tracks"]) - set(a["tracks"])))}
    own_a, own_b = a["end"][0] in OWN_ENDS, b["end"][0] in OWN_ENDS
    span = min(a["to"], b["to"])
    first = None
    for name in sorted(a["tracks"]):
        ca, cb = a["tracks"][name], b["tracks"][name]
        ticks = sorted({o for o, _s, _v in ca} | {o for o, _s, _v in cb})
        for off in ticks:
            if off > span:
                break
            va, vb = _value_at(ca, off), _value_at(cb, off)
            if va != vb:
                if first is None or off < first["tick"]:
                    first = {"tick": off, "what": "track %s" % name, "ref": va, "arm": vb}
                break
    ea = [(o, s) for o, s in a["events"] if o <= span]
    eb = [(o, s) for o, s in b["events"] if o <= span]
    for x, y in zip(ea + [None], eb + [None]):
        if x == y:
            if x is None:
                break
            continue
        off = min(z[0] for z in (x, y) if z is not None)
        if first is None or off < first["tick"]:
            first = {"tick": off, "what": "event", "ref": x[1] if x else None, "arm": y[1] if y else None}
        break
    if first is not None:
        first.update(verdict=DIVERGED, ticks=span + 1)
        return first
    if own_a and own_b:
        if a["end"] != b["end"]:
            return {"verdict": DIVERGED, "tick": min(a["to"], b["to"]), "what": "end", "ref": list(a["end"]), "arm": list(b["end"]),
                    "ticks": span + 1}
        return {"verdict": EQUAL, "ticks": span + 1}
    if a["to"] == b["to"] and a["end"] == b["end"]:
        return {"verdict": EQUAL, "ticks": span + 1}
    who = "reference" if not own_a else "arm"
    return {"verdict": COULD_NOT, "why": "the %s ended %s on offset %s, so ticks %s..%s are in one trace only" % (
        who, (a if who == "reference" else b)["end"][0], (a if who == "reference" else b)["to"], span + 1, max(a["to"], b["to"])),
        "ticks": span + 1}


# ------------------------------------------------------------------------------------------------- samples
def refuse(sample, origin):
    """None when the sample may be compared, else (name, why). `origin` is the save identity and the random state that every run
    starts from: {"save": {"name", "sha256"}, "tick": start tick, "rand": decimal string}. Pure."""
    if sample.get("failed"):
        return ("COULD_NOT_LOOK", "the run gave no trace: %s" % sample["failed"])
    if sample.get("replayed"):
        return ("REPLAY", "the reply was a replay of an earlier request: it is not a new run")
    rows = sample.get("rows") or []
    o = _open(rows)
    if o is None:
        return ("NO_TRACE", "the run has no open record")
    save = sample.get("save") or {}
    if not save.get("sha256") or save != origin.get("save") or int(o["tick"]) != origin.get("tick"):
        return ("NOT_ONE_SAVE", "the run started from %s on tick %s; the comparison starts from %s on tick %s" % (
            save or "an unknown save", o.get("tick"), origin.get("save"), origin.get("tick")))
    if not origin.get("rand") or sample.get("rand_want") != origin["rand"] or str(o.get("rand")) != origin["rand"]:
        return ("RAND_NOT_WRITTEN", "the random state at arm is %s; the comparison writes back %s" % (o.get("rand"), origin.get("rand")))
    return None


def judge_arms(samples, origin, n):
    """Every sample against the reference: its arm's first counted run. Pure. -> {arm: summary}"""
    seen, counted, out = set(), {}, {}
    for s in samples:
        why = refuse(s, origin)
        run = _open(s["rows"])["run"] if why is None else None      # refuse() said NO_TRACE when there is no open record
        if why is None and run in seen:
            why = ("REPLAY", "run %s was counted already" % run)
        s["refused"] = why
        if why is None:
            seen.add(run)
            counted.setdefault(s["arm"], []).append(s)
    # the reference: the first counted reference run that ended by its own condition or limit (a run whose clock was stopped from
    # outside covers only part of the range); None: no counted reference, so every arm is COULD_NOT_COMPARE
    refs = counted[REFERENCE] if REFERENCE in counted else []
    whole = [s for s in refs if timeline(s["rows"])["end"][0] in OWN_ENDS]
    ref = whole[0] if whole else (refs[0] if refs else None)
    for arm, _speed in ARMS:
        got = counted.get(arm, [])
        refused = [s for s in samples if s["arm"] == arm and s.get("refused")]
        rows = []
        for s in got:
            if s is ref:                        # run 1 of the reference is what the others are compared with, not a comparison
                s["comparison"] = {"verdict": "REFERENCE"}
                continue
            c = compare(ref["rows"], s["rows"]) if ref is not None else {"verdict": COULD_NOT, "why": "no counted reference run"}
            s["comparison"] = c
            rows.append(c)
        want = n - 1 if arm == REFERENCE else n
        if not got and not refused:
            continue
        div = [c for c in rows if c["verdict"] == DIVERGED]
        cnc = [c for c in rows if c["verdict"] == COULD_NOT]
        if arm == REFERENCE and div:
            line = "the reference is not repeatable: %d of its %d other runs diverge from run 1, first on tick %s (%s): run 1 %s, other %s" % (
                len(div), len(rows), div[0]["tick"], div[0]["what"], div[0]["ref"], div[0]["arm"])
        elif div:
            line = "first diverging tick %s (%s): reference %s, arm %s" % (div[0]["tick"], div[0]["what"], div[0]["ref"], div[0]["arm"])
        elif cnc:
            line = "could not compare %d of %d runs: %s" % (len(cnc), len(rows), cnc[0]["why"])
        elif len(got) < n:
            line = "only %d counted runs of %d (refused: %s)" % (len(got), n, "; ".join("%s %s" % s["refused"] for s in refused) or "none")
        elif arm == REFERENCE:
            line = "no divergence observed in %d runs (runs 2 to %d compared with run 1)" % (len(got), len(got))
        else:
            line = "no divergence observed in %d runs" % len(rows)
        tps = [s["ticks"] / s["wall_s"] for s in got if s.get("wall_s") and s.get("ticks")]
        pairs = [compare(x["rows"], y["rows"]) for i, x in enumerate(got) for y in got[i + 1:]]
        same = sum(1 for c in pairs if c["verdict"] == EQUAL)
        firsts = sorted({c["tick"] for c in pairs if c["verdict"] == DIVERGED})
        own = "%d of %d pairs of its own runs equal%s" % (same, len(pairs), "; its own runs first differ on ticks %s" % firsts if firsts else "")
        # the reference counts by being the reference (PLAY at speed 1 is the game); its own repeatability is reported beside it
        counts = len(got) >= 1 if arm == REFERENCE else (not div and not cnc and len(rows) >= want and len(got) >= n)
        out[arm] = {"line": line, "counts": counts, "runs": len(got), "self": own, "refused": len(refused),
                    "tps": (min(tps), sum(tps) / len(tps), max(tps)) if tps else None}
    return out


# ------------------------------------------------------------------------------------------------- the key and the store
def key(plan_sha, mods, companion, mod_list, arm):
    """The identity a comparison holds for. A change of any part makes the comparison owed again. Pure."""
    k = {"plan": plan_sha, "mods": mods, "companion": companion, "mod_list": mod_list, "arm": arm}
    return {"key": k, "id": hashlib.sha256(_canon(k).encode()).hexdigest()[:16]}


def record(store, k, summary):
    """Write one arm's comparison into the store (a dict). Pure."""
    store[k["id"]] = {"key": k["key"], "counts": bool(summary["counts"]), "line": summary["line"]}
    return store


def counts_for_bar(store, k):
    """True only for an arm whose comparison under exactly this key agreed with the reference. Another key's comparison is not used;
    the reference counts by being the reference. Pure."""
    if k["key"]["arm"] == REFERENCE:
        return True
    rec = store.get(k["id"])
    return bool(rec and rec.get("key") == k["key"] and rec.get("counts"))


# ------------------------------------------------------------------------------------------------- the result page
def render(plan, origin, samples, judged, keys, full_list):
    lines = ["# PLAY against STEP: the result of `scene.py compare`", "",
             "Item `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`. Written by `scene_compare.py`; every run's trace is in",
             "`<this page's name>_samples.jsonl` beside it. Wall time is never compared; ticks per second are measured from the driver.", "",
             "- plan: `%s` (sha %s)" % (plan["path"], plan["sha"]),
             "- start: save `%s` (sha256 %s), tick %s, random state %s written back before every run" % (
                 origin["save"]["name"], origin["save"]["sha256"], origin["tick"], origin["rand"]),
             "- game: %s; mod list fingerprint %s" % (plan.get("game"), plan.get("mod_list")), "",
             "| run | arm | speed | refused | verdict | first difference | ticks | wall s | ticks/s |", "|---|---|---|---|---|---|---|---|---|"]
    for i, s in enumerate(samples, 1):
        c = s.get("comparison") or {}
        diff = "" if c.get("verdict") in (None, EQUAL) else ("%s at tick %s" % (c.get("what"), c.get("tick")) if c.get("verdict") == DIVERGED
                                                              else c.get("why", ""))
        lines.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, s["arm"], SPEED[s["arm"]], "%s: %s" % s["refused"] if s.get("refused") else "", c.get("verdict", ""), diff.replace("|", "/"),
            s.get("ticks"), "%.1f" % s["wall_s"] if s.get("wall_s") else "", "%.0f" % (s["ticks"] / s["wall_s"]) if s.get("wall_s") else ""))
    lines += ["", "## Each arm", ""]
    for arm, _sp in ARMS:
        j = judged.get(arm)
        if j:
            t = tuple("%.0f" % x for x in j["tps"]) if j["tps"] else ("UNMEASURED",) * 3
            lines.append("- **%s**: against the reference: %s. Repeatability: %s. Ticks/s min %s, mean %s, max %s (%s); key `%s`" % (
                (arm, j["line"], j["self"]) + t + (plan.get("list_size", "this run's mod list"), keys[arm]["id"])))
    lines += ["", "- full mod list: %s" % full_list, "",
              "arms that count for a bar: %s" % (", ".join(a + (" (the reference)" if a == REFERENCE else "") for a, _s in ARMS
                                                           if judged.get(a, {}).get("counts")) or "none"), ""]
    return "\n".join(lines)


# ------------------------------------------------------------------------------------------------- the live driver (game needed)
def _load_plan(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("compare_plan", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()[:16]
    for need in ("SAVE", "LIMIT", "plan"):
        if not hasattr(m, need):
            raise SystemExit("REFUSED: the plan %s has no %s (a plan holds SAVE, LIMIT and plan(c) -> dict(until=..., record=[...]))" % (path, need))
    return m, sha


def _save_sha(s, name):
    folder = getattr(s, "_saves", None)
    if not folder:
        s._has_save(name)
        folder = s._saves
    for p in (os.path.join(folder, name + ".rws"), os.path.join(folder, name)):
        if os.path.isfile(p):
            with open(p, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
    return None


def run_live(plan_path, arms, n, game, out_md, store_path):
    import scene
    m, plan_sha = _load_plan(plan_path)
    from scene import cond as c
    p = m.plan(c)
    needs = {"map": m.SAVE}
    if getattr(m, "CALM", None):
        needs["calm"] = m.CALM

    log = os.path.splitext(out_md)[0] + "_samples.jsonl"
    with open(log, "w"):
        pass

    def one(arm, rand):
        """One run, or a sample that names why it gave no trace. An open refused in its lock phase changed nothing, so it is asked
        again: the WSL child that holds the lock for a Windows driver has died silently (exit -1) on this machine (2026-11-24)."""
        for attempt in (1, 2, 3):
            try:
                got = _one(arm, rand)
                break
            except (scene.Fault, scene.Refused) as e:
                rep = getattr(e, "report", None) or []
                lock_only = bool(rep) and rep[0].get("state") == "refused" and all(x.get("state") == "not reached" for x in rep[1:])
                if lock_only and attempt < 3:
                    time.sleep(5)
                    continue
                got = {"arm": arm, "rows": [], "failed": "%s: %s" % (type(e).__name__, str(e).splitlines()[0]), "rand_want": rand,
                       "save": {"name": m.SAVE, "sha256": None}, "attempts": attempt}
                break
        with open(log, "a") as f:
            f.write(json.dumps({k: v for k, v in got.items() if k != "build"}, default=str) + "\n")
        return got

    def _one(arm, rand):
        with scene.open(game, needs=needs) as s:
            sha = _save_sha(s, m.SAVE)
            t0 = time.monotonic()
            r = s.run(until=p["until"], limit=m.LIMIT, speed=SPEED[arm], record=p.get("record"), rand=rand)
            wall = time.monotonic() - t0
            with open(r.trace) as f:
                rows = [json.loads(x) for x in f if x.strip()]
            build = s.build
        return {"arm": arm, "rows": rows, "save": {"name": m.SAVE, "sha256": sha}, "rand_want": rand, "wall_s": wall,
                "ticks": (r.tick - r.tick_from) if r.tick_from is not None else None, "trace": r.trace,
                "replayed": bool(getattr(r, "replayed", False)), "build": build}

    first = one(REFERENCE, None)            # the arming run: records the random state; it is not a sample
    if first.get("failed"):
        raise SystemExit("COULD NOT LOOK: the arming run gave no trace: %s" % first["failed"])
    o = _open(first["rows"])
    origin = {"save": first["save"], "tick": int(o["tick"]), "rand": str(o.get("rand")) if o.get("rand") is not None else None}
    if origin["rand"] is None:
        raise SystemExit("COULD NOT LOOK: the open record has no random state (a companion older than this item)")
    samples = []
    for arm in arms:
        for _i in range(n):
            samples.append(one(arm, origin["rand"]))
    judged = judge_arms(samples, origin, n)
    b = first["build"]
    mods = {k: v.get("sha256") for k, v in sorted((b.get("dlls") or {}).items()) if k != "JawaBench.BridgeTools"}
    keys = {arm: key(plan_sha, mods, (b.get("companion") or {}).get("source_hash"), b.get("list"), arm) for arm, _s in ARMS}
    store = {}
    if os.path.isfile(store_path):
        with open(store_path) as f:
            store = json.load(f)
    for arm, j in judged.items():
        record(store, keys[arm], j)
    with open(store_path, "w") as f:
        json.dump(store, f, indent=1, sort_keys=True)
    page = render({"path": os.path.relpath(plan_path, os.path.join(HERE, "..", "..", "..")).replace("\\", "/"), "sha": plan_sha, "game": game,
                   "mod_list": b.get("list"), "list_size": "%s active mods" % b.get("mods")}, origin, samples, judged, keys,
                  "UNMEASURED: no full-list load was scheduled to ride (full-list testing is retired until integration)")
    with open(out_md, "w") as f:
        f.write(page)
    print(page)
    return 0 if all(j["runs"] for j in judged.values()) else 1


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="scene.py compare")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--arms", default=",".join(a for a, _s in ARMS))
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--game", default="ArchSmall")
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    exp = os.path.join(root, "design", "specs", "2026-11-23-bridge-v2", "experiments")
    ap.add_argument("--out", default=os.path.join(exp, "play_vs_step_result.md"))
    ap.add_argument("--store", default=os.path.join(exp, "play_vs_step_comparisons.json"))
    a = ap.parse_args(argv)
    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    bad = [x for x in arms if x not in SPEED]
    if bad or REFERENCE not in arms:
        print("REFUSED: arms are %s and include %s; not %s" % (", ".join(SPEED), REFERENCE, bad or arms))
        return 3
    return run_live(a.plan, arms, a.n, a.game, a.out, a.store)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
