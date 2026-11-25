#!/usr/bin/env python3
"""Live proof of jawa/session, jawa/run_until and jawa/read_paths. Page: design/specs/2026-11-23-bridge-v2-hands/boundary.md. Item
RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH.

    python.exe prove_run_until.py [--out DIR]      on a TEST-profile game, a scratch quicktest map; row 4 needs FlowWorks loaded.
                                                   It spawns and kills one animal. No save is read or written.
    python3 prove_run_until.py --selfcheck         the judges on hand-made traces, good and planted; no game

Rows: 1 a run with no session is refused  2 exact stop at Normal and Ultrafast (the tick is read a second time by TicksGame after the
pause and equals the trace's)  3 a private field read twice, by the hand and by jawa/pawn_get  4 a private field of a FlowWorks comp on
every tick of 200  5 an unreadable value ends as unknown  6 a frozen group keeps its dead member  7 a repeat of a request plays
no tick  8 another driver is refused  9 1,000 reads change nothing  10 a private static, and a wrong name with its fields  11 the lease
pauses and does not close  12 the count of trace rows equals the closing record's count, and n has no gap.
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED."""
import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, HERE)
import prove_scene_tick_wiring as W  # noqa: E402  the connection, call() and row()

DRIVER = "prove:%d" % os.getpid()
SERIAL = [0]


# ------------------------------------------------------------------------------------------------ the judges (pure)
def recs(trace, rec, **kw):
    return [r for r in trace if r.get("rec") == rec and all(r.get(k) == v for k, v in kw.items())]


def whole(trace):
    """None when one session's trace is whole, else the point it breaks."""
    if not trace or trace[0]["rec"] != "session_open" or trace[-1]["rec"] != "session_close":
        return "the trace does not start with session_open and end with session_close"
    if [r["n"] for r in trace] != list(range(1, len(trace) + 1)):
        return "a gap in n"
    if any(a["seq"] >= b["seq"] for a, b in zip(trace, trace[1:])):
        return "seq does not rise"
    c = trace[-1]
    if c.get("rows") != len(trace) - 1:
        return "session_close counts %s rows, the file holds %d" % (c.get("rows"), len(trace) - 1)
    if c.get("dropped") or not c.get("drained"):
        return "dropped %s, drained %s" % (c.get("dropped"), c.get("drained"))
    for o in recs(trace, "open"):
        own = [r for r in trace if r.get("run") == o["run"]]
        if not recs(own, "close") or recs(own, "close")[0]["rows"] != len(own) - 1:
            return "run %s: its close does not count its rows" % o["run"]
    return None


def judge_stop(rows, reply, want, t_after, t_later, paused):
    """The game stands ON tick T0+want: the trace, the reply and two later reads of TicksGame say the same tick."""
    if len(recs(rows, "end")) != 1 or len(recs(rows, "close")) != 1:
        return None, "the run's trace is not whole: %s" % [r.get("rec") for r in rows][-5:]
    t0, e, c = recs(rows, "open")[0]["tick"], recs(rows, "end")[0], recs(rows, "close")[0]
    seen = dict(trace=e["hitTick"], tickAfter=c["tickAfter"], reply=reply.get("tick"), after=t_after, later=t_later)
    ok = all(v == t0 + want for v in seen.values()) and paused is True and reply.get("why") == "hit" and not recs(rows, "fault")
    return ok, "T0 %s want +%d: %s, why %s, paused %s" % (t0, want, {k: None if v is None else v - t0 for k, v in seen.items()}, reply.get("why"), paused)


def judge_every_tick(reply, name, ticks):
    v = (reply.get("values") or {}).get(name)
    if not v or reply.get("why") != "limit":
        return None, "why %s, value %s" % (reply.get("why"), v)
    blind = [b for b in reply.get("couldNotLook") or [] if b.get("value") == name]
    return v["state"] == "ok" and v["reads"] == ticks + 2 and not blind, "%s = %s (%s), %s reads for %d ticks, the first and the last; not readable: %s" % (
        name, v["v"], v["state"], v["reads"], ticks, blind)


def selfcheck():
    def made(**o):
        t, seq = [], [10]

        def add(rec, tick, run="S1_r1", **kw):
            seq[0] += 2
            t.append(dict({"seq": seq[0], "n": len(t) + 1, "rec": rec, "tick": tick, "run": run, "sess": "S1"}, **kw))
        add("session_open", 1000, None)
        add("open", 1000)
        add("track", 1000, name="x", v=1)
        e = 1000 + o.get("stop", 137)
        add("end", e, hitTick=e)
        add("close", e, rows=3 - o.get("lost_run", 0), tickAfter=o.get("after", e))
        add("session_close", e, None, rows=len(t) - o.get("lost", 0), dropped=o.get("dropped", 0), drained=o.get("drained", True))
        if o.get("gap"):
            t[2]["n"] = 9
        return t

    def run(t):
        return [r for r in t if r["run"] == "S1_r1"]
    rep = {"why": "hit", "tick": 1137}
    v = {"why": "limit", "values": {"p": {"state": "ok", "v": 4, "reads": 202}}, "couldNotLook": []}
    cases = [
        ("whole", whole(made()) is None, True), ("a gap in n", whole(made(gap=1)) is None, False), ("a lost row", whole(made(lost=1)) is None, False),
        ("a lost row of the run", whole(made(lost_run=1)) is None, False), ("a dropped row", whole(made(dropped=1)) is None, False),
        ("not drained", whole(made(drained=False)) is None, False), ("no closing record", whole(made()[:-1]) is None, False), ("no trace", whole([]) is None, False),
        ("stop good", judge_stop(run(made()), rep, 137, 1137, 1137, True)[0], True),
        ("stop one tick late", judge_stop(run(made(stop=138)), dict(rep, tick=1138), 137, 1138, 1138, True)[0], False),
        ("stop then the game went on", judge_stop(run(made()), rep, 137, 1137, 1140, True)[0], False),
        ("stop not paused", judge_stop(run(made()), rep, 137, 1137, 1137, False)[0], False),
        ("stop with no trace", judge_stop([], rep, 137, 1137, 1137, True)[0], None),
        ("every tick good", judge_every_tick(v, "p", 200)[0], True),
        ("every tick, one missed", judge_every_tick(dict(v, values={"p": dict(v["values"]["p"], reads=201)}), "p", 200)[0], False),
        ("every tick, unreadable on some", judge_every_tick(dict(v, couldNotLook=[{"value": "p"}]), "p", 200)[0], False),
        ("every tick, not recorded", judge_every_tick(v, "q", 200)[0], None),
    ]
    bad = [n for n, got, want in cases if got is not want]
    for n, got, want in cases:
        print("%s %s -> %s" % ("ok  " if got is want else "FAIL", n, got))
    print("prove_run_until judges: %d of %d" % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------- the game
def req(name):
    SERIAL[0] += 1
    return "%s_%d" % (name, SERIAL[0])


def read_session(st, sess, limit_s=15):
    """The session's lines in seq order, once session_close is on disk."""
    end = time.time() + limit_s
    while True:
        out = []
        for p in sorted(glob.glob(os.path.join(st.get("recordDir") or "", "tps_*_%s_*.jsonl" % st.get("writerSession")))):
            with open(p, encoding="utf-8") as f:
                for ln in f:
                    if '"kind":"scene"' in ln and sess in ln:
                        try:
                            r = json.loads(ln)
                        except ValueError:
                            continue
                        if r.get("sess") == sess:
                            out.append(r)
        out.sort(key=lambda r: r["seq"])
        if any(r.get("rec") == "session_close" for r in out) or time.time() > end:
            return out
        time.sleep(0.5)


def open_session(lease=60):
    """A short lease: a proof that dies leaves a game that the next one can take. A session that another process left is
    aborted once its lease has ended."""
    end = time.time() + 90
    while True:
        r = W.call("jawa/session", action="open", driver=DRIVER, leaseS=lease)
        if r.get("success"):
            return r
        if r.get("refused") != "SESSION_OPEN" or time.time() > end:
            print("UNMEASURED: no session: %s" % brief(r), flush=True)
            sys.exit(2)
        W.call("jawa/session", action="abort", driver=DRIVER)
        time.sleep(2)


def end_session(action="close", limit_s=80):
    r = W.call("jawa/session", action=action, driver=DRIVER)
    if r.get("refused") == "NO_SESSION":
        return r
    end = time.time() + limit_s
    while r.get("success") and r.get("stage") == "closing" and time.time() < end:
        time.sleep(0.2)
        r = W.call("jawa/session", action="state")
    return r


def run(until, limit, limit_s=240, request=None, **kw):
    """Start and wait. -> the closed reply, or the refusal."""
    rid = request or req("run")
    for k in ("record", "acts"):
        if k in kw:
            kw[k] = json.dumps(kw[k])
    r = W.call("jawa/run_until", action="start", driver=DRIVER, request=rid, until=json.dumps(until), limit=limit, **kw)
    end = time.time() + limit_s
    while r.get("success") and r.get("stage") != "closed" and time.time() < end:
        time.sleep(0.15)
        r = W.call("jawa/run_until", action="status", driver=DRIVER, request=rid)
    return r


def read(*pairs):
    """The values. The host drops a null from a reply, so an absent `v` is null: it is put back here, and the state says what it means."""
    r = W.call("jawa/read_paths", reads=json.dumps([{"of": o, "path": p} for o, p in pairs]))
    return [dict({"v": None}, **v) for v in r.get("values") or []]


def at_tick(t):
    return {"cmp": [{"p": "game.tick"}, ">=", t]}


def value(of, path, op, lit):
    return {"cmp": [{"p": "value", "of": of, "path": path}, op, lit]}


def tick():
    return W.call("jawa/map_info").get("ticksGame")


def brief(r):
    return {k: r.get(k) for k in ("refused", "message", "why", "stage", "state", "detail", "unknownValue", "faults", "lastFault", "_error") if r.get(k)}


def start_map():
    from await_lifecycle import await_lifecycle
    lc = await_lifecycle(W.call, "map_ready", deadline_s=400, start=True)
    if not lc:
        W.row("map", None, "no quicktest map: %s; started %s %s" % (lc.reason, lc.started, (lc.last or {}).get("startError") or ""))
        return False
    time.sleep(3)
    return True


def animal(x, z, kind="Muffalo"):
    r = W.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="none")
    return ((r.get("pawns") or [{}])[0]).get("id"), r


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
    if not start_map():
        return 2
    open_session()                                              # a session that an earlier run left is out of the way first
    end_session("abort")
    r = W.call("jawa/run_until", action="start", driver=DRIVER, request=req("none"), until=json.dumps(at_tick(1)), limit=10)
    row("1 no session, no run", r.get("refused") == "NO_SESSION" if r.get("success") is False and not r.get("_error") else None, brief(r))

    s = open_session()
    sess, keep = s["session"], []
    replies = {}
    for sp, n in (("Normal", 137), ("Ultrafast", 1370)):
        t0 = tick()
        rep = run(at_tick(t0 + n), n + 200, speed=sp)
        t1 = tick()
        time.sleep(1.2)
        st = W.call("jawa/session", action="state")
        keep.append((sp, n, rep, t1, st.get("ticksGame"), st.get("paused")))
        replies["stop_" + sp] = rep

    pl = [p for p in W.call("jawa/pawn_get", limit=200).get("pawns") or [] if p.get("faction") == "PlayerColony"]
    pid = pl[0]["thingId"] if pl else None
    W.call("jawa/session", action="bind", driver=DRIVER, bindings=json.dumps({"col": pid}))
    got = read(("col", "positionInt.x"), ("col", "Position"), ("col", "jobs.curJob.loadID"))
    x, z = pl[0].get("x"), pl[0].get("z")
    if x is None and isinstance(pl[0].get("position"), dict):
        x, z = pl[0]["position"].get("x"), pl[0]["position"].get("z")
    row("3 a private field against jawa/pawn_get", None if x is None or not got else got[0]["v"] == x and got[1]["v"] == "%s,%s" % (x, z), "read_paths %s, pawn_get %s,%s" % (got, x, z))

    comp = "comp<RM_MapComponent_Excavation>.pulseCount"
    have = read(("map", comp))
    if have and have[0]["state"] == "ok":
        rep = run(at_tick(tick() + 5000), 200, record=[{"of": "map", "path": comp}, {"of": "game", "path": "tickManager.ticksGameInt"}], speed="Fast")
        replies["flowworks"] = rep
        v, d = judge_every_tick(rep, "map." + comp, 200)
        v2, d2 = judge_every_tick(rep, "game.tickManager.ticksGameInt", 200)
        after = read(("map", comp))[0]["v"]
        row("4 a FlowWorks private field, 200 ticks", None if v is None or v2 is None else v and v2 and after == rep["values"]["map." + comp]["v"], "%s; %s; read again after: %s" % (d, d2, after))
    else:
        row("4 a FlowWorks private field, 200 ticks", None, "FlowWorks is not readable on this map: %s" % have)

    cells = [(x + 6, z + 2), (x + 8, z + 2)]
    ids = [animal(*c) for c in cells]
    if all(i[0] for i in ids):
        W.call("jawa/session", action="bind", driver=DRIVER, bindings=json.dumps({"herd": [i[0] for i in ids]}))
        kill = {"id": req("kill"), "tool": "jawa/damage", "args": {"damageDef": "Cut", "amount": 5000, "thingId": ids[0][0], "armorPenetration": 9, "bodyPart": "Body"}, "at": 40}
        rep = run(value("herd[0]", "Position.x", "<", -1), 400, record=[{"of": "herd", "path": "Position"}], acts=[kill])
        replies["unknown"] = rep
        u = rep.get("unknownValue") or {}
        # the scene is staged only when the tool itself says that the victim died (a cut rolls dice)
        dead = [x_ for x_ in rep.get("acts") or [] if x_.get("state") == "done" and any(t_.get("dead") for t_ in (x_.get("reply") or {}).get("targets") or [])]
        row("5 an unreadable value ends as unknown", None if not dead else rep.get("why") == "unknown" and rep.get("tick") == rep.get("tickFrom") + 41 and u.get("status") == "gone" and "herd[0]" in str(u.get("value")), "the victim did not die: %s" % (rep.get("acts") or brief(rep)) if not dead else "%s at +%s: %s" % (rep.get("why"), rep.get("tick") - rep.get("tickFrom"), u))
        vals = rep.get("values") or {}
        row("6 a group keeps its dead member", None if not dead else sorted(k for k in vals if k.endswith(".Position")) == ["herd[0].Position", "herd[1].Position"] and vals["herd[0].Position"]["state"] == "gone" and vals["herd[0].Position"].get("v") is None and vals["herd[1].Position"]["state"] == "ok", vals)
    else:
        row("5 an unreadable value ends as unknown", None, "no animal: %s" % [i[1] for i in ids])
        row("6 a group keeps its dead member", None, "no animal")

    rid, t0 = req("again"), tick()
    one = run(at_tick(t0 + 30), 100, request=rid)
    t1 = tick()
    two = run(at_tick(t0 + 30), 100, request=rid)
    three = run(at_tick(t0 + 31), 100, request=rid)
    row("7 a repeat plays no tick", None if one.get("why") != "hit" else two.get("success") is True and two.get("replayed") in (True, False) and two.get("run") == one.get("run") and tick() == t1 and three.get("refused") == "REQUEST_CONFLICT",
        "run %s then %s, tick %s then %s; other arguments: %s" % (one.get("run"), two.get("run"), t1, tick(), three.get("refused")))
    other = W.call("jawa/run_until", action="start", driver="somebody", request=req("x"), until=json.dumps(at_tick(1)), limit=10)
    row("8 another driver is refused", None if other.get("_error") else other.get("refused") == "NOT_THE_DRIVER" and tick() == t1, brief(other))

    probe = [("col", "health.hediffSet.hediffs._size"), ("col", "positionInt.x"), ("col", "needs.food.curLevelInt"), ("col", "jobs.curJob.loadID"), ("game", "tickManager.ticksGameInt"), ("static:Verse.Rand", "seed"), ("static:Verse.Rand", "iterations")]
    b = read(*probe)
    many = W.call("jawa/read_paths", reads=json.dumps([{"of": o, "path": p} for o, p in (probe + [("col", "Position"), ("col", "CurJobDef"), ("col", "nothing")]) * 100]))
    c = read(*probe)
    row("9 1,000 reads change nothing", None if len(many.get("values") or []) != 1000 or any(v["state"] != "ok" for v in b[:3]) else [v["v"] for v in b] == [v["v"] for v in c], "%d reads; before %s after %s" % (len(many.get("values") or []), [v["v"] for v in b], [v["v"] for v in c]))

    st = read(("static:JawaBench.BridgeTools.JawaBenchTpsWriter", "_seq"), ("col", "hitPoints"), ("thing:NoSuchThing", "Position"), ("def:ThingDef/Wall", "passability"))
    no = W.call("jawa/read_paths", reads=json.dumps([{"of": "col", "path": "LabelShort"}]))
    row("10 statics, a wrong name, a property", None if len(st) != 4 else st[0]["state"] == "ok" and st[1]["state"] == "error" and "hitPointsInt" in st[1].get("detail", "") and st[2]["state"] == "unbound" and st[2]["v"] is None and st[3]["v"] == "Impassable" and no.get("refused") == "PATH_CALLS_METHOD",
        "%s | %s" % ([(v["state"], v["v"], str(v.get("detail"))[:60]) for v in st], brief(no)))

    done = end_session()
    tr = read_session(done, sess)
    with open(os.path.join(a.out, "run_until.json"), "w", encoding="utf-8") as f:
        json.dump({"state": done, "replies": replies, "trace": tr}, f, indent=1)
    for sp, n, rep, t1, t2, paused in keep:
        rows = [r_ for r_ in tr if r_.get("run") == rep.get("run")]
        v, d = judge_stop(rows, rep, n, t1, t2, paused) if rows else (None, brief(rep))
        row("2 exact stop at " + sp, v, d)
    why = whole(tr)
    row("12 the trace is whole", None if not tr else why is None, "%d rows; %s; runs %d" % (len(tr), why or "n has no gap, the close counts each row", len(recs(tr, "open"))))

    s = open_session(4)
    rid = req("lease")
    W.call("jawa/run_until", action="start", driver=DRIVER, request=rid, until=json.dumps(at_tick(tick() + 50000)), limit=50000, speed="Normal")
    time.sleep(1.5)
    playing = W.call("jawa/session", action="state")
    time.sleep(6)
    st = W.call("jawa/session", action="state")
    t1 = st.get("ticksGame")
    time.sleep(1)
    row("11 the lease pauses and does not close", None if playing.get("paused") is not False else st.get("stage") == "open" and st.get("leaseEnded") is True and st.get("paused") is True and tick() == t1 and (st.get("lastRun") or {}).get("why") == "cancelled",
        "playing first: %s; then stage %s leaseEnded %s paused %s, run %s" % (not playing.get("paused"), st.get("stage"), st.get("leaseEnded"), st.get("paused"), (st.get("lastRun") or {}).get("why")))
    end_session("abort")
    n = dict((v, sum(1 for _r, x_ in W.ROWS if x_ == v)) for v in ("PASS", "FAIL", "UNMEASURED"))
    print("run until live: %d PASS, %d FAIL, %d UNMEASURED" % (n["PASS"], n["FAIL"], n["UNMEASURED"]))
    return 1 if n["FAIL"] else (2 if n["UNMEASURED"] or not W.ROWS else 0)


def closing(body):
    """The proof, and whatever happens in it the session is not left open."""
    try:
        return body()
    finally:
        if W.S[0] is not None:
            end_session("abort")


if __name__ == "__main__":
    sys.exit(closing(main))
