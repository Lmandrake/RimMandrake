#!/usr/bin/env python3
"""Live proof of the BRIDGE v2.0 slice (jawa/scene_slice): a condition run stepped in the game's OWN loop, a trace on disk, an
exact stop. Page: design/specs/2026-11-23-bridge-v2/boundary.md. Item RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED.

    python.exe prove_scene_tick_wiring.py [--out DIR]      on a TEST-profile game, a small mod list, a scratch map (it hurts one
                                                           colonist of its own quicktest map; no save is read or written)
    python3 prove_scene_tick_wiring.py --selfcheck         the judges on hand-made traces, good and planted; no game

Five rows:
  1 exact stop at Normal and at Ultrafast  2 a private field path reads what jawa/pawn_get reads  3 the damage act's effect is
  in the trace before the end  4 the close counts no dropped row  5 the steady state allocates nothing (the counter that
  jawa/alloc_probe calibrated).
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED."""
import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))

ROWS = []
S = [None]


def row(name, v, detail):
    """v is True PASS, False FAIL, None UNMEASURED."""
    w = "PASS" if v is True else ("FAIL" if v is False else "UNMEASURED")
    ROWS.append((name, w))
    print("%-44s %-10s %s" % (name, w, str(detail)[:500]), flush=True)
    return v


# ------------------------------------------------------------------------------------------------ the judges (pure)
def recs(trace, rec, **kw):
    return [r for r in trace if r.get("rec") == rec and all(r.get(k) == v for k, v in kw.items())]


def whole(trace):
    """None when the trace meets the evidence contract, else the point it breaks."""
    if len(recs(trace, "open")) != 1 or len(recs(trace, "close")) != 1 or len(recs(trace, "end")) != 1:
        return "open/end/close records: %s" % [len(recs(trace, x)) for x in ("open", "end", "close")]
    c = recs(trace, "close")[0]
    if trace[-1]["rec"] != "close":
        return "the close is not the last record"
    if [r["n"] for r in trace] != list(range(1, len(trace) + 1)):
        return "a gap in n"
    if any(a["seq"] >= b["seq"] for a, b in zip(trace, trace[1:])):
        return "seq does not rise"
    if c.get("rows") != len(trace) - 1:
        return "close counts %s rows, the file holds %d" % (c.get("rows"), len(trace) - 1)
    if not c.get("drained") or c.get("dropped"):
        return "drained %s, dropped %s" % (c.get("drained"), c.get("dropped"))
    if recs(trace, "fault"):
        return "fault records: %s" % [(f.get("what"), f.get("detail")) for f in recs(trace, "fault")]
    for t in recs(trace, "open")[0].get("tracks") or []:
        for ph in ("first", "last"):
            if len(recs(trace, "track", name=t, phase=ph)) != 1:
                return "track %s has no %s sample" % (t, ph)
    return None


def judge_stop(trace, want, t_after, t_later, paused):
    """The game stands ON tick T0+want. t_after: the tick read when the run closed; t_later: read again a second later."""
    why = whole(trace)
    if why:
        return None, "trace not whole: " + why
    t0, e, c = recs(trace, "open")[0]["tick"], recs(trace, "end")[0], recs(trace, "close")[0]
    ok = (e["state"] == "hit" and e["hitTick"] == t0 + want and e["executed"] == want and c["tickAfter"] == t0 + want
          and t_after == t0 + want and t_later == t0 + want and paused is True and c["paused"] is True)
    return ok, "T0 %s want +%d: state %s hitTick +%s executed %s tickAfter +%s, read after +%s, a second later +%s, paused %s" % (
        t0, want, e["state"], (e["hitTick"] or 0) - t0, e["executed"], c["tickAfter"] - t0, (t_after or 0) - t0, (t_later or 0) - t0, paused)


def judge_field(trace, x):
    last = recs(trace, "track", name="field", phase="last")
    if not last or x is None:
        return None, "last sample %s, pawn_get x %s" % (last, x)
    return last[0]["st"] == "ok" and last[0]["v"] == x, "positionInt.x in the last sample %s (%s), jawa/pawn_get x %s" % (last[0]["v"], last[0]["st"], x)


def judge_act(trace):
    why = whole(trace)
    if why:
        return None, "trace not whole: " + why
    act, e = recs(trace, "act"), recs(trace, "end")[0]
    if len(act) != 1 or not act[0]["ok"]:
        return None, "the act was not delivered: %s" % act
    first = recs(trace, "track", name="hediffs", phase="first")[0]
    after = [r for r in recs(trace, "track", name="hediffs") if r["seq"] > act[0]["seq"] and r["phase"] == "end_of_tick"]
    ok = bool(after) and after[0]["v"] > first["v"] and after[0]["seq"] < e["seq"] and after[0]["tick"] == act[0]["tick"] + 1 and e["state"] == "hit" and e["tick"] > act[0]["tick"]
    return ok, "act %s at tick %s; hediffs %s -> %s at tick %s; end %s at tick %s" % (
        act[0]["detail"], act[0]["tick"], first["v"], after[0]["v"] if after else None, after[0]["tick"] if after else None, e["state"], e["tick"])


def judge_drop(traces):
    if not traces or any(not recs(t, "close") for t in traces):
        return None, "a trace has no close"
    d = [recs(t, "close")[0] for t in traces]
    return all(c["dropped"] == 0 and c["drained"] is True for c in d), "dropped %s, drained %s, rows %s" % (
        [c["dropped"] for c in d], [c["drained"] for c in d], [c["rows"] for c in d])


def judge_alloc(trace, trusted):
    c = recs(trace, "close")
    a = c[0].get("alloc") if c else None
    if not trusted or not a or a["steadyTicks"] < 500:
        return None, "counter %s, alloc %s" % (trusted, a)
    return a["bytes"] == 0, "counter %s: %s bytes over %s steady ticks (%s of them allocated, %s more had a GC)" % (
        trusted, a["bytes"], a["steadyTicks"], a["ticksThatAllocated"], a["ticksWithGc"])


# ------------------------------------------------------------------------------------------------- the offline self-check
def made(**o):
    t, seq = [], [100]

    def add(tick, phase, rec, **kw):
        seq[0] += 3
        t.append(dict({"seq": seq[0], "n": len(t) + 1, "tick": tick, "phase": phase, "rec": rec}, **kw))
    add(1000, "first", "open", tracks=["field", "hediffs"])
    add(1000, "first", "track", name="field", st="ok", v=5)
    add(1000, "first", "track", name="hediffs", st="ok", v=1)
    if not o.get("no_act"):
        if o.get("sample_late"):
            add(1041, "end_of_tick", "track", name="hediffs", st="ok", v=2)
        add(1040, "end_of_tick", "act", name="damage", ok=True, detail="x")
        if not o.get("sample_late") and not o.get("no_effect"):
            add(1041, "end_of_tick", "track", name="hediffs", st="ok", v=2)
    e = 1000 + o.get("stop", 137)
    add(e, "end_of_tick", "end", state="hit", hitTick=e, executed=e - 1000)
    add(o.get("after", e), "last", "track", name="field", st="ok", v=5)
    add(o.get("after", e), "last", "track", name="hediffs", st="ok", v=2)
    add(e, "last", "close", rows=len(t) - o.get("lost", 0), dropped=o.get("dropped", 0), drained=o.get("drained", True), paused=True,
        tickAfter=o.get("after", e), alloc={"steadyTicks": 600, "bytes": o.get("bytes", 0), "ticksThatAllocated": 0, "ticksWithGc": 0})
    return t


def selfcheck():
    cases = [
        ("stop good", judge_stop(made(), 137, 1137, 1137, True)[0], True),
        ("stop one tick late", judge_stop(made(stop=138), 137, 1138, 1138, True)[0], False),
        ("stop ran past the end", judge_stop(made(after=1139), 137, 1139, 1139, True)[0], False),
        ("stop then the game went on", judge_stop(made(), 137, 1137, 1160, True)[0], False),
        ("stop not paused", judge_stop(made(), 137, 1137, 1137, False)[0], False),
        ("stop on a lost row", judge_stop(made(lost=1), 137, 1137, 1137, True)[0], None),
        ("stop on no trace", judge_stop([], 137, 1137, 1137, True)[0], None),
        ("field good", judge_field(made(), 5)[0], True),
        ("field wrong", judge_field(made(), 6)[0], False),
        ("field unread", judge_field(made(), None)[0], None),
        ("act good", judge_act(made())[0], True),
        ("act with no effect", judge_act(made(no_effect=True))[0], False),
        ("act with the sample before it", judge_act(made(sample_late=True))[0], False),
        ("act missing", judge_act(made(no_act=True))[0], None),
        ("drop good", judge_drop([made(), made()])[0], True),
        ("drop one", judge_drop([made(), made(dropped=1)])[0], False),
        ("drop not drained", judge_drop([made(drained=False)])[0], False),
        ("drop no close", judge_drop([made()[:-1]])[0], None),
        ("alloc good", judge_alloc(made(), "gcTotalMemory")[0], True),
        ("alloc some", judge_alloc(made(bytes=24), "gcTotalMemory")[0], False),
        ("alloc no counter", judge_alloc(made(), None)[0], None),
    ]
    bad = [n for n, got, want in cases if got is not want]
    for n, got, want in cases:
        print("%s %s -> %s" % ("ok  " if got is want else "FAIL", n, got))
    print("prove_scene_tick_wiring judges: %d of %d" % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------- the game
def connect():
    import rimbridge_client as rb
    host, port, token = rb.resolve_endpoint()
    if not token:
        raise SystemExit("UNMEASURED: no bridge token")
    S[0] = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
    S[0].connect()


def call(tool, **p):
    try:
        r = S[0].call(tool, p, check=False) or {}
    except Exception as e:  # noqa: BLE001 - a refusal may arrive as a transport error; it is the reading
        return {"success": False, "_error": "%s: %s" % (type(e).__name__, e)}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except (ValueError, KeyError, IndexError, TypeError):
            pass
    return r if isinstance(r, dict) else {"_raw": r}


def read_trace(st, limit_s=10):
    """The run's lines, in seq order, once its close is on disk."""
    end = time.time() + limit_s
    while True:
        out = []
        for p in sorted(glob.glob(os.path.join(st.get("recordDir") or "", "tps_*_%s_*.jsonl" % st.get("session")))):
            with open(p, encoding="utf-8") as f:
                for ln in f:
                    if '"kind":"scene"' not in ln:
                        continue
                    try:
                        r = json.loads(ln)
                    except ValueError:
                        continue
                    if r.get("run") == st.get("run"):
                        out.append(r)
        out.sort(key=lambda r: r["seq"])
        if any(r.get("rec") == "close" for r in out) or time.time() > end:
            return out
        time.sleep(0.5)


def run(limit_s=240, **p):
    """-> (status at close, trace) or (the refusal, [])."""
    r = call("jawa/scene_slice", action="start", **p)
    if not r.get("success"):
        return r, []
    end = time.time() + limit_s
    while r.get("stage") != "closed" and time.time() < end:
        time.sleep(0.3)
        r = call("jawa/scene_slice", action="status")
    if r.get("stage") != "closed":
        call("jawa/scene_slice", action="cancel")
        return r, []
    return r, read_trace(r)


def save(out, name, st, trace):
    with open(os.path.join(out, name + ".json"), "w", encoding="utf-8") as f:
        json.dump({"status": st, "trace": trace}, f, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    os.makedirs(a.out, exist_ok=True)
    connect()
    call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    from await_lifecycle import await_lifecycle
    if not await_lifecycle(call, "map_ready", deadline_s=240):
        row("map", None, "no quicktest map reached Playing")
        return 2
    time.sleep(3)
    pl = [p for p in call("jawa/pawn_get", limit=200).get("pawns") or [] if p.get("faction") == "PlayerColony" and p.get("kindDef") == "Colonist"]
    if not pl:
        row("pawn", None, "no colonist on the quicktest map: %s" % call("jawa/pawn_get", limit=20))
        return 2
    pid = pl[0]["thingId"]
    tick = {"p": "game.tick"}
    traces = []

    # a condition whose names do not resolve is refused before a tick runs
    r = call("jawa/scene_slice", action="start", pawn=pid, until=json.dumps({"cmp": [{"p": "pawn.state", "pawn": "NoSuchPawn", "f": "dead"}, "==", True]}))
    row("0 an unknown name is refused", None if r.get("_error") else r.get("success") is False and r.get("refused") == "bind", {k: r.get(k) for k in ("refused", "detail", "message", "_error")})

    for sp, n in (("Normal", 137), ("Ultrafast", 1370)):
        t0 = call("jawa/map_info").get("ticksGame")
        st, tr = run(pawn=pid, speed=sp, maxTicks=n + 200, until=json.dumps({"cmp": [tick, ">=", t0 + n]}))
        save(a.out, "stop_" + sp, st, tr)
        t1 = call("jawa/map_info").get("ticksGame")
        time.sleep(1.5)
        s2 = call("jawa/scene_slice", action="status")
        if not tr:
            row("1 exact stop at " + sp, None, {k: st.get(k) for k in ("message", "error", "stage", "state", "lastFault", "_error")})
            continue
        traces.append(tr)
        v, d = judge_stop(tr, n, t1, s2.get("ticksGame"), s2.get("paused"))
        many = st.get("maxFrameTicks")
        if sp == "Ultrafast" and v is True and not (many or 0) > 1:
            v, d = None, d + "; no frame of the run played more than %s tick: the mid-frame stop was not exercised" % many
        row("1 exact stop at " + sp, v, "%s; most ticks in one frame %s, in the ending frame %s" % (d, many, st.get("endFrameTicks")))
        if sp == "Normal":
            pg = (call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
            x = pg.get("x", (pg.get("position") or {}).get("x") if isinstance(pg.get("position"), dict) else None)
            row("2 a private field path against pawn_get", *judge_field(tr, x))

    st, tr = run(pawn=pid, speed="Normal", maxTicks=400, actAt=60, damage=6.0,
                 until=json.dumps({"changed": {"p": "thing.field", "thing": pid, "path": "health.hediffSet.hediffs._size"}}))
    save(a.out, "act", st, tr)
    traces.append(tr)
    row("3 the act's effect is in the trace", *(judge_act(tr) if tr else (None, {k: st.get(k) for k in ("message", "refused", "detail", "stage", "state", "lastFault")})))
    row("4 no dropped row", *judge_drop(traces))

    cal = call("jawa/alloc_probe", action="calibrate", trials=9)
    trusted = (cal.get("probe") or cal).get("trusted")
    st, tr = run(pawn=pid, speed="Fast", maxTicks=1500, until=json.dumps({"cmp": [{"p": "pawn.state", "pawn": pid, "f": "dead"}, "==", True]}))
    save(a.out, "alloc", st, tr)
    row("5 the steady state allocates nothing", *(judge_alloc(tr, trusted) if tr else (None, {k: st.get(k) for k in ("message", "stage", "state", "lastFault")})))
    n = dict((v, sum(1 for _r, x in ROWS if x == v)) for v in ("PASS", "FAIL", "UNMEASURED"))
    print("scene tick wiring live: %d PASS, %d FAIL, %d UNMEASURED" % (n["PASS"], n["FAIL"], n["UNMEASURED"]))
    return 1 if n["FAIL"] else (2 if n["UNMEASURED"] or not ROWS else 0)


if __name__ == "__main__":
    sys.exit(main())
