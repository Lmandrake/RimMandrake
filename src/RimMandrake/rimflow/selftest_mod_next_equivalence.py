#!/usr/bin/env python3
"""selftest_mod_next_equivalence.py: the old paths and mod_next.next_for, on the same recorded inputs.

Item RIMMANDRAKE_MERGE_NEXT_STEP_AND_MAY_RUN_THREE_ANSWERS_ONE_MOD; page design/specs/2026-11-22-mod-next/boundary.md.
The OLD paths are the code at BASE (read with `git show`, never a copy kept here):

  1. maturation.dispatch_overlay (the `maturation.py next` overlay) against every (decision, klass) pair that the
     Dispatch tick recorded in ticks.jsonl (the counts are in recorded_inputs.json beside the page).
  2. control.why (`./pipe why`) against the control store at every revision of the committed acts export
     (infrastructure/state/control/acts.jsonl), for every mod those acts name.
  3. owed.not_held (its word match) against every run record's item id, under every hold set of 2.

Each difference is classed in CLASSED below with the case and why the new verdict stands; an unclassed difference is
a failure. Nothing here reads a live store: the recorded inputs are committed, the control store is a temp file.

    python3 src/RimMandrake/rimflow/selftest_mod_next_equivalence.py            exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_mod_next_equivalence.py --record   refresh recorded_inputs.json from the
                                                                                live tick history and run records
"""
import ast
import collections
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
BASE = "dfb4ce69bc"      # the tree before the one home (acceptance.sh NEXT read RED on it)
FIXTURE = os.path.join(REPO, "design", "specs", "2026-11-22-mod-next", "recorded_inputs.json")
ACTS = os.path.join(REPO, "infrastructure", "state", "control", "acts.jsonl")
AUTO = "NEXT (automatic: the Dispatch tick launches it): blind cycle 2 (maturation.py launch M ...)"
FAILS = []

# (path, old class, new class) -> why the difference is right. Every other difference fails.
CLASSED = {
    ("tick", "yes", "waiting"): "refined: the tick waits (a live run, settling, full slots, his walk, a rested pass); "
                                "the old line said 'automatic' and named the wait only on its dispatch line",
    ("tick", "yes", "paused"): "old wrong: a planned stop (a pipeline pause, the step disabled) or an unclassed row the "
                               "tick's own _klass rule pauses (not_offline, hand_step, ready) printed 'automatic'",
    ("tick", "paused", "ceiling"): "refined: a ceiling is its own result, with its release command",
    ("why", "none", "off"): "old wrong: a stage switch (`pipe off stage:<stage>`) blocks a mod that stands at that stage; "
                            "the old why ignored it. Seen 2026-11-22 when FlowWorks went back to in_game (revs 76 and "
                            "79 hold stage:in_game off): the case reads each mod's live stage record",
    ("owed", "kept", "dropped"): "the identity home's rule (item_identity.item_mod): a held mod named by its initials "
                                 "or a 7+ letter word of its name is that mod; the old word match missed it",
}


def check(ok, what, got=None):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def old_source(rel):
    r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (BASE, rel)], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("git show %s:%s: %s" % (BASE, rel, r.stderr.strip()))
    return r.stdout


def old_function(rel, name, glb):
    src = old_source(rel)
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            exec(compile(ast.get_source_segment(src, node), "%s@%s" % (rel, BASE), "exec"), glb)
            return glb[name]
    raise RuntimeError("%s has no %s at %s" % (rel, name, BASE))


def old_module(rel, name, tmp):
    p = os.path.join(tmp, name + ".py")
    with open(p, "w", encoding="utf-8") as f:
        f.write(old_source(rel))
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---- record ---------------------------------------------------------------------------------------------------------

def record():
    import mod_next as MN
    import detached_helper as DH
    ticks = os.path.join(MN.reading_dir(), "ticks.jsonl")
    combos, n, rows = collections.Counter(), 0, 0
    with open(ticks, encoding="utf-8") as f:
        for line in f:
            try:
                t = json.loads(line)
            except ValueError:
                continue
            n += 1
            for _, v in (t.get("decisions") or {}).items():
                rows += 1
                combos[(v[0], v[2] if len(v) > 2 else None)] += 1
    d = DH.runs_dir()
    items, nrec = collections.Counter(), 0
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json") and not fn.endswith(".out.json"):
            try:
                with open(os.path.join(d, fn), encoding="utf-8") as f:
                    r = json.load(f)
            except (OSError, ValueError):
                continue
            if isinstance(r, dict) and r.get("unit"):
                nrec += 1
                items[(str(r.get("item") or ""), str(r.get("mod") or ""))] += 1
    out = {"recorded": time.strftime("%Y-%m-%d %H:%M %Z"), "ticks": {"source": ticks, "ticks": n, "rows": rows,
           "combos": sorted([[a, b, c] for (a, b), c in combos.items()], key=lambda x: -x[2])},
           "records": {"source": d, "records": nrec, "items": sorted([[i, m, c] for (i, m), c in items.items()])}}
    with open(FIXTURE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("recorded %d ticks (%d rows, %d pairs), %d run records (%d items) -> %s" % (
        n, rows, len(combos), nrec, len(items), FIXTURE))


# ---- 1. the tick overlay ----------------------------------------------------------------------------------------------

def old_overlay_class(nxt):
    for pre, k in (("NEXT (PAUSED", "paused"), ("NEXT (HELD", "held"), ("NEXT (automatic", "yes"),
                   ("NEXT (UNMEASURED", "UNMEASURED"), ("NEXT (a hand step", "hand")):
        if nxt.startswith(pre):
            return k
    return "other"


def t_tick_overlay(fx, diffs):
    import mod_next as MN
    overlay = old_function("src/RimMandrake/rimflow/maturation.py", "dispatch_overlay",
                           {"UNM": "UNMEASURED", "DISPATCH_READING_MAX_AGE_S": 1800})
    now, n, rows = 1795400000.0, 0, 0
    for dec, klass, count in fx["ticks"]["combos"]:
        row = {"decision": dec, "why": "recorded"}
        if klass:
            row["klass"] = klass
        rd = {"at": now - 30, "at_pac": "rec", "mods": {"M": row}}
        old = old_overlay_class(overlay("M", AUTO, rd, "/rec/reading.json", now)["next"])
        holds = {"M": {"mod": "M", "date": "2026-11-16", "said": "recorded hold"}} if dec == "owner_hold" else {}
        src = {"holds": lambda h=holds: dict(h), "pause": lambda t: {},
               "blocked": lambda spec, d=dec: "OFF (all, act ct_rec at x): recorded" if d == "control_off" else None,
               "reading": lambda r=rd: (r, "/rec/reading.json", None),
               "gate": lambda root, mod: {"mod": mod, "stage": "blind_challenge", "next": AUTO}}
        new = MN.next_for("/rec", "M", now=now, src=src)["may_run"]["result"]
        n += 1
        rows += count
        if old != new:
            diffs[("tick", old, new)].append("%s/%s x%d" % (dec, klass, count))
    check(n == len(fx["ticks"]["combos"]) and n > 0, "the tick overlay compared on %d recorded (decision, klass) pairs, "
          "%d tick rows from %d ticks" % (n, rows, fx["ticks"]["ticks"]))
    return rows


# ---- 2. pipe why over the control acts ----------------------------------------------------------------------------------

def fold(acts):
    """-> [(rev, {(scope, layer): switch row})]: the switch table after each act that moved one."""
    sw, out = {}, []
    for a in acts:
        aft = json.loads(a["after"]) if isinstance(a.get("after"), str) else a.get("after")
        bef = json.loads(a["before"]) if isinstance(a.get("before"), str) else a.get("before")
        moved = False
        if a["kind"] in ("off", "hold") and isinstance(aft, dict) and aft.get("layer"):
            sw[(a["scope"], aft["layer"])] = {"scope": a["scope"], "layer": aft["layer"], "why": aft.get("why") or "-",
                                              "said": a.get("owner_said"), "date": str(a.get("at") or "")[:10],
                                              "until": aft.get("until"), "act": a["id"], "at_pacific": a.get("at_pacific"),
                                              "who": a.get("who"), "extra": None}
            moved = True
        elif a["kind"] in ("on", "lift"):
            lay = (bef or {}).get("layer") or ("owner" if a["kind"] == "lift" else "control")
            moved = sw.pop((a["scope"], lay), None) is not None
        if moved:
            out.append((a["rev"], dict(sw)))
    return out


def why_class(line):
    head = line.split(": ", 1)[1] if ": " in line else line
    if head.startswith("BLOCKED HELD BY OWNER"):
        return "held"
    if head.startswith("BLOCKED OFF"):
        return "off"
    if head.startswith("BLOCKED PIPELINE PAUSED"):
        return "paused"
    return "none"


def t_pipe_why(tmp, diffs):
    acts = [json.loads(x) for x in open(ACTS, encoding="utf-8") if x.strip()]
    states = fold(acts)
    mods = sorted({a["scope"][4:] for a in acts if a["scope"].startswith("mod:") and "/" not in a["scope"]})
    ddir = os.path.join(tmp, "dispatch")
    os.makedirs(ddir, exist_ok=True)
    with open(os.path.join(ddir, "reading.json"), "w", encoding="utf-8") as f:     # a neutral tick: it decides nothing
        json.dump({"at": time.time(), "at_pac": "rec", "mods": {m: {"decision": "live", "klass": "wait", "why": "x"}
                                                               for m in mods}}, f)
    hold = os.path.join(tmp, "holds.json")
    with open(hold, "w", encoding="utf-8") as f:
        json.dump({"holds": []}, f)     # his file holds are imported into the store as hold acts: the store alone
    os.environ.update(RM_MATURATION_DISPATCH_DIR=ddir, RM_OWNER_HOLD_FILE=hold,
                      RM_PIPELINE_PAUSE_FILE=os.path.join(tmp, "pause.json"))
    import control as C
    old = old_module("src/RimMandrake/rimflow/control.py", "control_old_%s" % BASE, tmp)
    real = (C.game_lines, C.to_run_text)
    for mod_ in (C, old):       # the drivers and Stage-6 tails are no part of the verdict: one read each, not 2 x 800
        mod_.game_lines, mod_.to_run_text = (lambda short=False: []), (lambda mod, root=None: "")
    n, seen = 0, set()
    for rev, sw in states:
        sig = tuple(sorted(sw))
        if sig in seen:         # the same switch table again (an off then its on): already compared
            continue
        seen.add(sig)
        db = os.path.join(tmp, "control-%d.db" % rev)
        C.init(db)
        c = C.connect(db)
        with c:
            for r in sw.values():
                c.execute("INSERT INTO switches (scope, layer, why, said, date, until, act, at_pacific, who, extra) "
                          "VALUES (?,?,?,?,?,?,?,?,?,?)", tuple(r[k] for k in (
                              "scope", "layer", "why", "said", "date", "until", "act", "at_pacific", "who", "extra")))
        c.close()
        os.environ["RM_CONTROL_DB"] = db
        for m in mods:
            o, w = why_class(old.why(m)), why_class(C.why(m))
            n += 1
            if o != w:
                diffs[("why", o, w)].append("%s at rev %s" % (m, rev))
    C.game_lines, C.to_run_text = real
    check(n > 0, "pipe why compared on %d (switch table, mod) pairs: %d distinct tables over %d revisions of %d acts, "
          "%d mods" % (n, len(seen), len(states), len(acts), len(mods)))
    return states, mods


# ---- 3. owed's hold filter ----------------------------------------------------------------------------------------------

def t_owed_filter(fx, states, diffs):
    import owed
    not_held = old_function("src/RimMandrake/rimflow/owed.py", "not_held", {"re": re})
    items = [{"item": i, "mod": m or None} for i, m, _ in fx["records"]["items"]]
    n, sets = 0, set()
    for rev, sw in states:
        held = tuple(sorted({s[0][4:] for s in sw if s[0].startswith("mod:") and "/" not in s[0]}))
        if held in sets:
            continue
        sets.add(held)
        holds = {m: {"mod": m, "said": "rec", "date": ""} for m in held}
        names = {re.sub(r"[^A-Z0-9]", "", m.upper()) for m in held}
        _, old_kept = not_held([], items, names)
        _, new_kept = owed.held_filter([], items, holds)
        ok_ = {id(r) for r in old_kept}
        nk = {id(r) for r in new_kept}
        for r in items:
            n += 1
            o, w = ("kept" if id(r) in ok_ else "dropped"), ("kept" if id(r) in nk else "dropped")
            if o != w:
                diffs[("owed", o, w)].append("%s under %s" % (r["item"], "+".join(held)))
    check(n > 0, "owed's filter compared on %d (hold set, run item) pairs: %d hold sets, %d run items from %d records" % (
        n, len(sets), len(items), fx["records"]["records"]))


def main(argv):
    if "--record" in argv:
        record()
        return 0
    with open(FIXTURE, encoding="utf-8") as f:
        fx = json.load(f)
    os.environ["RM_UNDER_SELFTEST"] = "1"
    tmp = tempfile.mkdtemp(prefix="mod_next_equiv_")
    diffs = collections.defaultdict(list)
    try:
        t_tick_overlay(fx, diffs)
        states, _ = t_pipe_why(tmp, diffs)
        t_owed_filter(fx, states, diffs)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for k in sorted(diffs):
        v = diffs[k]
        why = CLASSED.get(k)
        print("%s  difference %s -> %s on %s: %d case(s), e.g. %s%s" % (
            "PASS" if why else "FAIL", k[1], k[2], k[0], len(v), "; ".join(v[:3]), " -- " + why if why else ""))
        if not why:
            FAILS.append("unclassed difference %r" % (k,))
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
