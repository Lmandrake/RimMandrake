#!/usr/bin/env python3
"""mod_next: the one home of what a mod does next and whether the pipeline may run it now.

Item RIMMANDRAKE_MERGE_NEXT_STEP_AND_MAY_RUN_THREE_ANSWERS_ONE_MOD. Promises and contract:
design/specs/2026-11-22-mod-next/boundary.md. Tests: selftest_mod_next.py (promises), selftest_mod_next_equivalence.py
(the old paths replayed on recorded tick readings, holds and switches).

    next_for(root, mod, now=None, gate=True, src=None) -> {may_run: {result, why}, by, next_act, next, tick, ...}

The readers it joins, each the only reader of its fact: the stage record's exit tests (maturation.gate_step), the owner
holds and `pipe off <Mod>` rows (mod_owner_hold.load), the control store's other switches (control.blocked), the
pipeline pause (pipeline_pause.state) and the Dispatch tick's last reading (tick_reading, here).

    python3 src/RimMandrake/rimflow/mod_next.py <Mod> [--gate] [--json]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

UNM = "UNMEASURED"
RESULTS = ("yes", "held", "off", "paused", "ceiling", "waiting", "hand", UNM)
# A dead-tick guard: the tick runs every 60 s, so a reading this old means about 30 ticks did not run, and its rows no
# longer say what the tick decides now (RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS: six hours of
# "automatic" on a paused mod). Past it an automatic claim reads UNMEASURED.
# budget: danger=a dead tick's rows read as current (six hours of automatic on a paused mod); ends no work: the claim reads
# budget: UNMEASURED
READING_MAX_AGE_S = 1800


def key(name):
    return os.path.basename(os.path.normpath(str(name or "")))


# ---- the tick's reading -----------------------------------------------------------------------------------------------

def reading_dir():
    d = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    if d:
        return d
    import doorbell
    return os.path.join(doorbell.state_dir(), "maturation")


def tick_reading():
    """-> (the Dispatch tick's last reading or None, its path, why it is None or None). Creates nothing."""
    try:
        p = os.path.join(reading_dir(), "reading.json")
    except Exception as e:      # noqa: BLE001  no state dir is no reading, said
        return None, "reading.json", "the state dir cannot be found (%s: %s)" % (type(e).__name__, e)
    try:
        with open(p, encoding="utf-8") as f:
            rd = json.load(f)
    except FileNotFoundError:
        return None, p, "no reading.json yet"
    except (OSError, ValueError) as e:
        return None, p, "%s: %s" % (type(e).__name__, e)
    if not isinstance(rd, dict):
        return None, p, "the reading is not an object"
    return rd, p, None


def tick_rows(rd):
    """-> {mod: the tick's last row} from a reading (its `mods` is a dict by mod; an older one a list of rows)."""
    ms = (rd or {}).get("mods") or (rd or {}).get("rows") or {}
    if isinstance(ms, dict):
        return {key(m): r for m, r in ms.items() if isinstance(r, dict)}
    return {key(r.get("mod")): r for r in ms if isinstance(r, dict) and r.get("mod")}


def tick_class(row):
    """-> the tick's class of a row: its own `klass`, or (a row written before the tick classed rows) the class
    maturation_autonomy._klass gives its decision."""
    k = row.get("klass")
    if k:
        return k
    import maturation_autonomy as AUT
    dec = row.get("decision")
    if dec in AUT.LAUNCH:
        return "launch"
    if dec in AUT.PLANNED:
        return "planned"
    if dec in AUT.WAIT:
        return "wait"
    return {"owner": "owner", "control_off": "held", "owner_hold": "held", "rested": "rested"}.get(dec, "paused")


def tick_of(mod, rd, path, why, now):
    """-> {"line", "decision", "klass", "at_pac", "why", "for_min", "age_s", "stale"}: what the reading says of MOD.
    decision None and klass None: the reading says nothing of it (no reading, stale, or not listed; `why` says which)."""
    if rd is None:
        return {"line": "dispatch tick: no readable reading at %s (%s)" % (path, why), "decision": None, "klass": None,
                "why": "no readable Dispatch tick reading at %s (%s)" % (path, why), "stale": True}
    try:
        age = now - float(rd.get("at"))
    except (TypeError, ValueError):
        age = None
    at = rd.get("at_pac", UNM)
    row = tick_rows(rd).get(key(mod))
    if age is None or age > READING_MAX_AGE_S:
        w = ("the Dispatch tick's reading is %d min old (the step is not ticking)" % (age / 60) if age is not None
             else "the Dispatch tick's reading has no time")
        said = (" (at %s it said: %s %s)" % (at, row.get("decision"), row.get("why") or row.get("status") or "")
                if isinstance(row, dict) else "")
        return {"line": "dispatch tick: %s%s" % (w, said), "decision": None, "klass": None, "why": w, "stale": True,
                "age_s": age}
    if row is None:
        w = ("%s is not on the Dispatch tick's list at %s (maturation_dispatch.json advancing): nothing launches it"
             % (key(mod), at))
        return {"line": "dispatch tick: %s" % w, "decision": None, "klass": None, "why": w, "stale": False,
                "at_pac": at, "age_s": age, "unlisted": True}
    dec, k = row.get("decision", UNM), tick_class(row)
    w = str(row.get("why") or row.get("status") or "")
    since = (" for %s min" % row["for_min"]) if isinstance(row.get("for_min"), int) else ""
    waits = " | waits on: %s" % row["waits_on"] if row.get("waits_on") else ""
    return {"line": "dispatch tick (%s): %s (%s)%s: %s%s" % (at, dec, k, since, w, waits), "decision": dec, "klass": k,
            "why": w, "for_min": row.get("for_min"), "at_pac": at, "age_s": age, "stale": False,
            "status": row.get("status")}


# ---- the readers, live or fixtures ------------------------------------------------------------------------------------

def readers(cache=True):
    """-> the live readers, as a src mapping. cache: each store is read once per mapping (a page over every mod)."""
    memo = {}

    def once(name, fn):
        def f(*a):
            k = (name,) + tuple(json.dumps(x, sort_keys=True, default=str) for x in a)
            if not cache:
                return fn(*a)
            if k not in memo:
                try:
                    memo[k] = (True, fn(*a))
                except Exception as e:      # noqa: BLE001  re-raised to every caller, never cached as a value
                    memo[k] = (False, e)
            ok, v = memo[k]
            if not ok:
                raise v
            return v
        return f

    def holds():
        import mod_owner_hold as OH
        return OH.load()

    def blocked(spec):
        import control as C
        return C.blocked(spec)

    def pause(now):
        import pipeline_pause as PP
        return PP.state(now)

    def gate(root, mod):
        import maturation as M
        return M.gate_step(root, mod)

    def stage(root, mod):
        import maturation as M
        rec = M.load(root, mod)
        return rec.get("stage") if isinstance(rec, dict) else UNM

    return {"holds": once("holds", holds), "blocked": once("blocked", blocked), "pause": once("pause", pause),
            "reading": once("reading", tick_reading), "gate": gate, "stage": once("stage", stage)}


# ---- the answer ---------------------------------------------------------------------------------------------------------

def split_next(nxt):
    """'NEXT (by): act' -> (by, act). A line of another shape is all act, by UNMEASURED."""
    if isinstance(nxt, str) and nxt.startswith("NEXT (") and "): " in nxt:
        by, act = nxt[len("NEXT ("):].split("): ", 1)
        return by, act
    return UNM, str(nxt)


def gate_class(by):
    """-> the may-run result a gate tag decides alone, or None when it is the tick's ("automatic")."""
    if by.startswith("automatic"):
        return None
    if by.startswith("PAUSED"):
        return "paused"
    if by.startswith("read again") or by == UNM:
        return UNM
    return "waiting"       # OWNER, a wait on a live run, a hand step: someone else acts


def _block(mod, stage, src, now):
    """-> (result, why, by) of the first store that blocks MOD, or None. An unreadable store is UNMEASURED."""
    import mod_owner_hold as OH
    try:
        h = OH.held(mod, src["holds"]())
    except Exception as e:      # noqa: BLE001  could not look is never "not held"
        return UNM, "the owner holds cannot be read (%s: %s): nothing launches on it until they can" % (
            type(e).__name__, e), "UNMEASURED whether it may run"
    if h:
        if h.get("unreadable"):
            return UNM, OH.status(h), "UNMEASURED whether it may run"
        return ("off", OH.status(h), "OFF") if h.get("control") else ("held", OH.status(h), "HELD BY OWNER")
    spec = {"family": "detached", "unit": "-", "mod": key(mod)}
    if stage and stage != UNM:
        spec["stage"] = stage
    try:
        b = src["blocked"](spec)
    except Exception as e:      # noqa: BLE001
        return UNM, "the control store cannot be read (%s: %s)" % (type(e).__name__, e), "UNMEASURED whether it may run"
    if b:
        return ("held", b, "HELD BY OWNER") if b.startswith("HELD BY OWNER") else ("off", b, "OFF")
    try:
        pz = src["pause"](now)
    except Exception as e:      # noqa: BLE001
        pz = {"error": "%s: %s" % (type(e).__name__, e)}
    if pz.get("error"):
        return UNM, "the pause state cannot be read (%s)" % pz["error"], "UNMEASURED whether it may run"
    import pipeline_pause as PP
    w = PP.reason(pz, key(mod))
    if w:
        return "paused", w, "PAUSED"
    return None


def _from_tick(t, live_clean):
    """-> (result, by) of a tick row for an automatic step."""
    if t.get("decision") is None:
        return ("hand", "a hand step") if t.get("unlisted") else (UNM, "UNMEASURED whether the Dispatch tick launches it")
    dec, k = t["decision"], t["klass"]
    when = " (tick %s%s)" % (t.get("at_pac", UNM), " for %s min" % t["for_min"] if isinstance(t.get("for_min"), int) else "")
    if dec == "ceiling":
        return "ceiling", "CEILING by the Dispatch tick%s" % when
    if k == "launch":
        return "yes", "automatic: the Dispatch tick%s" % when
    if k in ("wait", "owner", "rested"):
        return "waiting", "waiting, says the Dispatch tick%s" % when
    if k == "held":
        if live_clean:      # the live stores hold nothing now: a lift binds before the next tick reads it
            return "waiting", "waiting: the tick read a hold that the stores no longer hold%s" % when
        return ("off" if dec == "control_off" else "held"), "HELD by the Dispatch tick%s" % when
    return "paused", "PAUSED by the Dispatch tick%s" % when


def next_for(root, mod, now=None, gate=True, src=None):
    """-> the one answer for MOD (design/specs/2026-11-22-mod-next/boundary.md)."""
    now = time.time() if now is None else now
    live = readers()
    src = dict(live, **(src or {}))
    m = key(mod)
    if gate:
        out = dict(src["gate"](root, m))
        out["gate_next"] = out.get("next")      # the stage record's own line, before a hold, switch, pause or tick
        g_by, g_act = split_next(out.get("next"))
        stage = out.get("stage", UNM)
    else:
        try:
            stage = src["stage"](root, m)
        except Exception as e:      # noqa: BLE001
            stage = UNM
        out = {"mod": m, "stage": stage}
        g_by, g_act = None, None
    rd, path, rwhy = src["reading"]()
    t = tick_of(m, rd, path, rwhy, now)
    out["tick"] = t
    blk = _block(m, stage, src, now)
    then = (lambda act: "%s; the record's step, once it may run: %s" % (act, g_act)) if gate else (lambda act: act)
    if blk:
        result, why, by = blk
        act = why if result != UNM else "%s; %s" % (why, g_act if gate else "maturation.py next %s" % m)
        out.update(may_run={"result": result, "why": why}, by=by, next_act=then(act) if result != UNM else act)
    elif gate and gate_class(g_by):
        result = gate_class(g_by)
        out.update(may_run={"result": result, "why": "the stage record's step: %s" % g_by}, by=g_by, next_act=g_act)
    else:
        result, by = _from_tick(t, live_clean=True)
        why = t["why"]
        if gate:
            if result == "yes":     # the tick launches it: the gate's own words stand
                by, act = g_by, g_act
            else:
                act = "%s; the record's step, once it launches: %s" % (why or t["line"], g_act)
        else:
            act = "%s; the stage record's step: maturation.py next %s" % (why or t["line"], m)
        out.update(may_run={"result": result, "why": why}, by=by, next_act=act)
    out["next"] = "NEXT (%s): %s" % (out["by"], out["next_act"])
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mod")
    ap.add_argument("--gate", action="store_true", help="run the stage record's exit tests too (slow at the walk)")
    ap.add_argument("--json", action="store_true")
    o = ap.parse_args(argv)
    import maturation as M
    r = next_for(M.REPO, o.mod, gate=o.gate)
    if o.json:
        print(json.dumps(r, indent=2, ensure_ascii=False, default=str))
    else:
        print("%s: may run: %s (%s)" % (key(o.mod), r["may_run"]["result"], r["may_run"]["why"]))
        print("  " + r["tick"]["line"])
        print(r["next"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
