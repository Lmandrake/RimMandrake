#!/usr/bin/env python3
"""prove_scene_repeats.py - the live proof of stamp again (scene_repeats.Series) on the ordered rescue
(RIMMANDRAKE_PROVE_STAMP_AGAIN_TWENTY_COPIES_ON_THE_RESCUE). Page: design/specs/2026-11-23-bridge-v2/boundary.md §STAMP AGAIN;
its reading goes under §LIVE READINGS. Evidence: design/specs/2026-11-23-bridge-v2/live/stamp_again/.

    python.exe src\\RimMandrake\\bridgetools\\prove_scene_repeats.py --game ArchSmall [--rows R1,R2,R3] [--log PATH] < /dev/null
    python3 src/RimMandrake/bridgetools/prove_scene_repeats.py --selfcheck          (the judges on hand-made rows; no game)

The scene library takes the driver lock (scene.open). The stage save RM_Stage_<game>_settlement is made first by
stage_map.py make (through wsl.exe), unless --no-make. One copy of the ordered rescue on a 7x5 station: a rescuer at (1,2),
a victim at (3,2) downed by jawa/pawn_force_incapacitate, a sleeping spot at (5,3) (a bed with no quality and no stuff, so
two honest copies read back alike). The rescue is the ordered-rescue scene's (prove_ordered_rescue.py R0): `jawa/ordered_job
Rescue` with the victim and the spot. DoctorRescue is not directOrderable (Core WorkGivers.xml), so jawa/order through that
giver is refused: measured on ArchBig 2026-11-25. The rescuer is drafted first: an idle undrafted colonist wandered 7 cells off
its station and onto the next copy's margin (ArchBig 2026-11-25), and a drafted one stands where its job ends. A run of 1500
ticks at Normal; SUCCESS when the victim then lies in its own spot.
  R1 20 stamped copies of the rescue (one cluster, one run) finish in less wall time than 3 single runs (each its own
     session, one copy, one run); both times printed; every copy whose order was given reads SUCCESS, and no BREACH;
  R2 a planted cross-talk: copy 1's rescuer ordered onto copy 2's victim is a BREACH, and both ledger lines read UNRESOLVED;
  R3 a mod state left dirty on purpose changes the reset digest and stops the repeat RESET_DIGEST_DIFFERS. It needs a loaded
     mod of ours with a digest hook ([RMDigest], jawa/mod_hooks list) and a reset hook ([RMReset]), and that mod's dirtying act
     (--dirty-tool, --dirty-args); without them the row reads UNRUN and names what is missing. The hook is proven and reset first,
     then stamped, dirtied and stamped again: a digest not proven reads None, so a first stamp before the proof compares nothing.
Exit 0 every row PASS, 1 a row FAIL, 2 no verdict (no game, no stage, no jawa/order, a row that could not look), 3 no row failed
and a row is UNRUN."""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
sys.path.insert(0, UTILS)
sys.path.insert(0, HERE)

RESCUE = "Rescue"             # the JobDef of the ordered-rescue scene (jawa/ordered_job, targetA the victim, targetB the bed)
SPOT = "SleepingSpot"         # RimSage: Building_Bed, no CompQuality, no stuff, useHitPoints False
STATION = (7, 5)
DISTANCE = 12                 # cells kept between two copies (the allocator's margin is half of it on each side)
TICKS = 1500                  # a rescue over 3 cells and back took well under this on the ordered-rescue stage
COPIES, SINGLES = 20, 3
LINES = []


def log(s):
    LINES.append(s)
    print(s, flush=True)


def _h(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]


PLAN = {"station": STATION, "rescuer": (1, 2), "victim": (3, 2), "spot": (5, 3, 0), "job": RESCUE, "drafted": True, "ticks": TICKS, "speed": "Normal"}
CLAIM = "an ordered rescue on a stage station: the rescuer carries the downed victim to the station's own sleeping spot"


# ------------------------------------------------------------------------------------------------ pure parts (selfcheck)
def cell_of(v):
    """-> (x, z) from a Position as the trace writes it ("(12, 0, 7)", "12,7", [12, 0, 7], {"x":..,"z":..}), or None."""
    if isinstance(v, dict) and "x" in v and "z" in v:
        return int(v["x"]), int(v["z"])
    if isinstance(v, (list, tuple)):
        n = [int(float(a)) for a in v]
    elif isinstance(v, str):
        n = [int(float(a)) for a in re.findall(r"-?\d+(?:\.\d+)?", v)]
    else:
        return None
    if len(n) == 3:
        return n[0], n[2]
    if len(n) == 2:
        return n[0], n[1]
    return None


def cells_from_trace(rows, names):
    """-> {alias: [cells]} from the track rows of a run trace. `names`: {track name: alias}. Only rows read `ok` count."""
    out = {a: [] for a in names.values()}
    for r in rows:
        if r.get("rec") != "track" or r.get("st") != "ok":
            continue
        a = names.get(r.get("name"))
        c = cell_of(r.get("v")) if a else None
        if c is not None and (not out[a] or out[a][-1] != c):
            out[a].append(c)
    return out


def rescue_outcome(order, job, target):
    """-> (outcome, why). order: the jawa/order reply; job, target: the victim's job and its target def after the run."""
    if not isinstance(order, dict) or order.get("success") is not True:
        return "APPARATUS FAULT", "the rescue order was not taken: %s" % short(order)
    if job == "LayDown" and target == SPOT:
        return "SUCCESS", "the victim lies in a %s" % SPOT
    return "UNRESOLVED", "after the run the victim's job is %s on %s" % (job, target)


def judge_r1(singles, copies_wall, launches, breaches, stopped):
    """None when 20 copies beat 3 singles and every copy whose order was given is SUCCESS with no breach, else why not."""
    if stopped:
        return "the repeat stopped: %s" % stopped
    if len(launches) < COPIES:
        return "%d of %d copies ran" % (len(launches), COPIES)
    if breaches:
        return "%d breach(es) between honest copies: %s" % (len(breaches), breaches[:2])
    blind = [l["launch"] for l in launches if not l.get("seen", True)]
    if blind:
        return "COULD NOT LOOK: no cell of the rescuer of launch(es) %s was read, so the cross-talk check saw nothing" % blind[:5]
    given = [l for l in launches if l.get("outcome") != "APPARATUS FAULT"]
    bad = [(l["launch"], l["outcome"], l.get("why")) for l in given if l["outcome"] != "SUCCESS"]
    if bad:
        return "%d given copies did not succeed: %s" % (len(bad), bad[:3])
    if len(given) < COPIES // 2:
        return "only %d of %d orders were given: the stage is wrong" % (len(given), COPIES)
    if len(singles) < SINGLES:
        return "%d of %d single runs ran" % (len(singles), SINGLES)
    if not copies_wall < sum(singles):
        return "%d copies took %.1f s, %d single runs %.1f s" % (COPIES, copies_wall, SINGLES, sum(singles))
    return None


def judge_r2(breaches, lines, plant=None):
    """None when the planted order was taken, it put launch 1's rescuer on launch 2's station (a BREACH), and both ledger lines
    read UNRESOLVED. A breach from anything but the plant (a wander) does not count: the plant is what the row tests."""
    if plant is not None and plant.get("success") is not True:
        return "the planted order was not taken: %s" % short(plant)
    breaches = [b for b in breaches if re.match(r"BREACH: rescuer_\S+ of launch 1 was at .* on launch 2's station", b)]
    if not breaches:
        return "no BREACH for a rescuer ordered onto the other copy's station"
    if len(lines) != 2 or any(l.get("outcome") != "UNRESOLVED" for l in lines):
        return "the ledger lines read %s, not UNRESOLVED twice" % [l.get("outcome") for l in lines]
    return None


def short(r, n=260):
    return json.dumps(r, default=str)[:n] if r is not None else "None"


class FakeHooks(object):
    """A session whose jawa/mod_hooks keeps one hooked mod as JawaBenchModHooksCore.cs does: step=clean reads the clean digest and
    sets the proof false, step=dirty proves the digest when it differs, digest gives `proven` as it stands, reset clears the state.
    `dirties`: False plants a dirtying act that changes nothing; `resets`: False plants a reset hook that clears nothing."""

    def __init__(self, dirties=True, resets=True):
        self.state, self.proven, self.clean, self.dirties, self.resets = 0, False, None, dirties, resets

    def raw(self, tool, **a):
        d = "d%d" % self.state
        if tool == "dirty":
            self.state += 1 if self.dirties else 0
            return {"success": True}
        if a.get("action") == "digest":
            return {"success": True, "digests": [{"mod": "M", "digest": d, "proven": self.proven, "why": None},
                                                 {"mod": "N", "digest": None, "why": SR_NO_HOOK}]}
        if a.get("step") == "clean":
            self.clean, self.proven = d, False
        elif a.get("step") == "dirty":
            self.proven = d != self.clean
        elif a.get("action") == "reset":
            self.state = 0 if self.resets else self.state
            d = "d%d" % self.state
            return {"success": True, "reset": "verified" if self.proven and d == self.clean else "differs" if self.proven else "unproven"}
        return {"success": True, "digestProven": self.proven}


SR_NO_HOOK = "no digest hook"


def selfcheck():
    import scene_repeats as SR
    ok = []
    ok.append(cell_of("(12, 0, 7)") == (12, 7) and cell_of("12,7") == (12, 7) and cell_of({"x": 3, "z": 4}) == (3, 4) and cell_of(None) is None)
    rows = [{"rec": "track", "name": "a.Position", "st": "ok", "v": "(1, 0, 2)", "tick": 1},
            {"rec": "track", "name": "a.Position", "st": "gone", "v": None, "tick": 2},
            {"rec": "track", "name": "a.Position", "st": "ok", "v": "(2, 0, 2)", "tick": 3}]
    ok.append(cells_from_trace(rows, {"a.Position": "a"}) == {"a": [(1, 2), (2, 2)]})
    ok.append(rescue_outcome({"success": True}, "LayDown", SPOT)[0] == "SUCCESS")
    ok.append(rescue_outcome({"success": False, "message": "no path"}, None, None)[0] == "APPARATUS FAULT")
    ok.append(rescue_outcome({"success": True}, "Wait_Downed", None)[0] == "UNRESOLVED")
    good = [{"launch": i, "outcome": "SUCCESS"} for i in range(1, 21)]
    ok.append(judge_r1([30.0, 30.0, 30.0], 60.0, good, [], None) is None)
    ok.append(judge_r1([30.0, 30.0, 30.0], 95.0, good, [], None) is not None)               # slower than three singles
    ok.append(judge_r1([30.0] * 3, 60.0, good[:-1] + [{"launch": 20, "outcome": "UNRESOLVED"}], [], None) is not None)
    ok.append(judge_r1([30.0] * 3, 60.0, good, ["BREACH: x"], None) is not None)
    ok.append(str(judge_r1([30.0] * 3, 60.0, good[:-1] + [{"launch": 20, "outcome": "SUCCESS", "seen": 0}], [], None)).startswith("COULD NOT LOOK"))
    # R2 on the real Series: a rescuer of launch 1 seen on launch 2's station is a breach, both lines UNRESOLVED
    s = SR.Series("sc", claim="c", build="b", plan="p", distance=DISTANCE)
    c = s.cluster()
    l1 = s.stamp(("d", None), {}, rect=(10, 10, 7, 5), cluster=c)
    l2 = s.stamp(("d", None), {}, rect=(29, 10, 7, 5), cluster=c)
    s.ended(l1, "SUCCESS", True, cells={"rescuer_1": [(11, 12), (25, 12), (31, 12)]})
    s.ended(l2, "SUCCESS", True, cells={"rescuer_2": [(30, 12)]})
    ok.append(judge_r2(s.crosstalk(c), s.ledger_lines({}), {"success": True}) is None)
    ok.append(judge_r2(["BREACH: rescuer_1 of launch 1 was at (31, 12), on launch 2's station (29, 10, 7, 5) (margin 6)"],
                       [{"outcome": "UNRESOLVED"}] * 2, {"success": False}) is not None)    # the plant not taken: no verdict for the row
    s = SR.Series("sc", claim="c", build="b", plan="p", distance=DISTANCE)
    c = s.cluster()
    l1 = s.stamp(("d", None), {}, rect=(10, 10, 7, 5), cluster=c)
    l2 = s.stamp(("d", None), {}, rect=(29, 10, 7, 5), cluster=c)
    s.ended(l1, "SUCCESS", True, cells={"rescuer_1": [(11, 12), (16, 12)]})                 # stays home: no breach (must stay green)
    s.ended(l2, "SUCCESS", True, cells={"rescuer_2": [(30, 12)]})
    ok.append(judge_r2(s.crosstalk(c), s.ledger_lines({})) is not None)
    # R3 on a fake mod_hooks that keeps the proof as the companion does: a real dirtying act stops the repeat on the mod (must
    # pass); a dirtying act that changes nothing, or a reset that clears nothing, is never a PASS
    def r3(**kw):
        try:
            return r3_reading(FakeHooks(**kw), "M", "dirty", "{}", lambda i, series: {"rect": (10 * i, 10, 7, 5), "digest": ("st", None)})
        except Exception as e:  # noqa: BLE001  a judge that throws is a red selfcheck case
            return "threw %s: %s" % (type(e).__name__, e), ""
    got = r3()
    print("  R3 on a real dirtying act: %s" % (got[0],))
    ok.append(got[0] is None)
    ok.append(str(r3(dirties=False)[0]).startswith("COULD NOT LOOK"))
    ok.append(str(r3(resets=False)[0]).startswith("COULD NOT LOOK"))
    print("prove_scene_repeats selfcheck: %d of %d" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


# ------------------------------------------------------------------------------------------------ the game
def reply(r):
    return dict(r) if isinstance(r, dict) else {"raw": str(r)[:300]}


class Blocks(object):
    """Collects the readBack blocks of the staging calls of one copy: s.stage's (clean, build, spawn) and the downing's and the
    work priority's. The station digest is made from them (scene_repeats.station_digest)."""

    def __init__(self, s):
        self.s, self.blocks, self._orig = s, [], s._call

        def call(tool, **args):
            r = self._orig(tool, **args)
            if isinstance(r, dict):
                b = r.get("stageReadBack") if isinstance(r.get("stageReadBack"), dict) else r.get("readBack")
                if isinstance(b, dict) and "made" in b:
                    self.blocks.append(dict(b, tool=tool))
            return r
        s._call = call

    def take(self):
        out, self.blocks = self.blocks, []
        return out


def stage_copy(s, i, series, blk):
    """Stage copy i on a station of the stage. -> dict(rect, launch fields, aliases) or raises scene.Fault/Refused."""
    import scene_repeats as SR
    r, v, b = "rescuer_%d" % i, "victim_%d" % i, "spot_%d" % i
    cast = s.stage(cast={r: dict(kind="Colonist", at=PLAN["rescuer"]), v: dict(kind="Colonist", at=PLAN["victim"])},
                   things={b: dict(thing=SPOT, at=PLAN["spot"][:2], rot=PLAN["spot"][2])},
                   station=series.station_request(STATION) if series else dict(size=STATION, margin=DISTANCE // 2))
    m = next((re.search(r"took station (\S+) \((\d+), (\d+), (\d+), (\d+)\)", d) for d in cast.receipt.did if d.startswith("took station")), None)
    if not m:
        raise RuntimeError("the stage receipt names no station: %s" % cast.receipt.did)
    rect = tuple(int(m.group(k)) for k in (2, 3, 4, 5))
    rid, vid = getattr(cast, r).id, getattr(cast, v).id
    sid = getattr(cast, b).id
    down = reply(s.raw("jawa/pawn_force_incapacitate", pawn=vid, action="downed", allowBleedingWounds=False))
    work = reply(s.raw("jawa/set_draft", pawnId=rid, drafted=True))
    breach = [d for d in cast.receipt.did if d.startswith("BREACH")]
    blocks = blk.take()
    return {"i": i, "rect": rect, "station": m.group(1), "rescuer": r, "victim": v, "rid": rid, "vid": vid, "sid": sid, "blocks": blocks,
            "downed": bool(down.get("downedAfter") or down.get("downed")), "down": down, "work": work.get("success"), "stage_breach": breach,
            "digest": SR.station_digest(blocks, rect) if blocks else (None, "no readBack block was seen")}


def order(s, rescuer, victim):
    """The ordered rescue of prove_ordered_rescue.py R0: `rescuer` carries `victim` (a staged copy) to that copy's spot."""
    return reply(s.raw("jawa/ordered_job", pawnId=rescuer["rid"], jobDef=RESCUE, targetAId=victim["vid"], targetBId=victim["sid"],
                       count=1, waitTicks=0))


def run_and_read(s, copies):
    """One run of TICKS with every alias's Position recorded. -> (run result, {alias: cells}, {victim: (job, target def)})."""
    import scene
    c = scene.cond
    tracks, names = [], {}
    for k in copies:
        for a in (k["rescuer"], k["victim"]):
            t = c.track(a, "Position")
            tracks.append(t)
            names[t.name] = a
    res = s.run(TICKS, limit=TICKS + 10, speed="Normal", record=tracks)
    with open(res.trace, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    cells = cells_from_trace(rows, names)
    reads = []
    for k in copies:
        reads += [(k["victim"], "jobs.curJob.def.defName"), (k["victim"], "jobs.curJob.targetA.thingInt.def.defName")]
    vals = s.read_many(reads=reads)
    out = {}
    for n, k in enumerate(copies):
        j, t = vals[2 * n], vals[2 * n + 1]
        out[k["victim"]] = (j.v if j.state == "ok" else "<%s>" % j.state, t.v if t.state == "ok" else "<%s>" % t.state)
    return res, cells, out


def open_stage(game, save):
    import prove_stage_map as PSM
    return PSM.open_session(game, save, calm="standard")


def build_key(s):
    return _h(getattr(s, "build", None) or {})


def single_run(game, save, i):
    """One copy in its own session, as a scene runs today. -> (wall s, outcome, why)."""
    t0 = time.time()
    with open_stage(game, save) as s:
        blk = Blocks(s)
        k = stage_copy(s, i, None, blk)
        o = order(s, k, k)
        _res, _cells, got = run_and_read(s, [k])
    out, why = rescue_outcome(o, *got[k["victim"]])
    return time.time() - t0, out, why


def row1(game, save, rows):
    import scene_repeats as SR
    singles = []
    for i in range(1, SINGLES + 1):
        w, out, why = single_run(game, save, 100 + i)
        singles.append(w)
        log("  single run %d: %.1f s wall, %s (%s)" % (i, w, out, why))
    t0 = time.time()
    launches, stopped, breaches, digests = [], None, [], set()
    with open_stage(game, save) as s:
        series = SR.Series("ordered_rescue_copies", claim=_h(CLAIM), build=build_key(s), plan=_h(PLAN), distance=DISTANCE)
        cl = series.cluster()
        blk = Blocks(s)
        copies = []
        for i in range(1, COPIES + 1):
            k = stage_copy(s, i, series, blk)
            digests.add(k["digest"][0])
            try:
                k["launch"] = series.stamp(k["digest"], SR.read_mod_digests(s), rect=k["rect"], cluster=cl)
            except SR.Stop as e:
                stopped = "%s at copy %d: %s" % (e.name, i, e.why)
                first = SR.station_lines(copies[0]["blocks"], copies[0]["rect"])[0] if copies else None
                now = SR.station_lines(k["blocks"], k["rect"])[0]
                if first is not None and now is not None:
                    log("  the station lines that differ: only in copy 1 %s; only in copy %d %s" % (
                        sorted(set(first) - set(now))[:6], i, sorted(set(now) - set(first))[:6]))
                break
            copies.append(k)
        mods = series.launches[0]["start"]["mods"] if series.launches else {}
        for k in copies:
            k["order"] = order(s, k, k)
        _res, cells, got = run_and_read(s, copies) if copies and not stopped else (None, {}, {})
        for k in copies:
            out, why = rescue_outcome(k["order"], *got.get(k["victim"], (None, None)))
            series.ended(k["launch"], out, opportunity=out != "APPARATUS FAULT", exposures=1,
                         cells={k["rescuer"]: cells.get(k["rescuer"], []), k["victim"]: cells.get(k["victim"], [])})
            launches.append({"launch": k["launch"]["launch"], "outcome": out, "why": why, "rect": k["rect"],
                             "seen": len(cells.get(k["rescuer"], []))})
        breaches = series.crosstalk(cl) if copies else []
        lines = series.ledger_lines({})
        counts = series.counts()
    wall = time.time() - t0
    for l in launches:
        log("  copy %d at %s: %s (%s); %d rescuer cell(s) read" % (l["launch"], l["rect"], l["outcome"], l["why"], l.get("seen", 0)))
    log("  series %s: counts %s; station digests %s; mods %s; %d ledger lines, clusters %s" % (
        series.id, counts, sorted(d for d in digests if d) or digests, mods, len(lines), sorted({l.get("cluster") for l in lines})))
    bad = judge_r1(singles, wall, launches, breaches, stopped)
    rows.append(("R1 20 stamped copies of the rescue finish in less wall time than 3 single runs", bad,
                 "%d copies in one session and one run: %.1f s wall; %d single runs: %s = %.1f s; %d of %d SUCCESS, %d order(s) not given, "
                 "%d breach(es)" % (COPIES, wall, SINGLES, ", ".join("%.1f" % w for w in singles), sum(singles),
                                    sum(l["outcome"] == "SUCCESS" for l in launches), len(launches),
                                    sum(l["outcome"] == "APPARATUS FAULT" for l in launches), len(breaches))))


def row2(game, save, rows):
    import scene_repeats as SR
    with open_stage(game, save) as s:
        series = SR.Series("ordered_rescue_crosstalk", claim=_h(CLAIM), build=build_key(s), plan=_h(PLAN), distance=DISTANCE)
        cl = series.cluster()
        blk = Blocks(s)
        ks = []
        for i in (201, 202):
            k = stage_copy(s, i, series, blk)
            k["launch"] = series.stamp(k["digest"], SR.read_mod_digests(s), rect=k["rect"], cluster=cl)
            ks.append(k)
        a, b = ks
        o = order(s, a, b)                              # the plant: copy 1's rescuer onto copy 2's victim, on copy 2's station
        _res, cells, got = run_and_read(s, ks)
        raw_out = {}
        for k in ks:
            out, why = rescue_outcome(o, *got.get(k["victim"], (None, None)))
            raw_out[k["victim"]] = out
            series.ended(k["launch"], out, opportunity=True, exposures=1,
                         cells={k["rescuer"]: cells.get(k["rescuer"], []), k["victim"]: cells.get(k["victim"], [])})
        breaches = series.crosstalk(cl)
        lines = series.ledger_lines({})
    rows.append(("R2 a planted cross-talk between two copies is a BREACH and both copies read UNRESOLVED", judge_r2(breaches, lines, o),
                 "plant %s; stations %s and %s; %s; ledger outcomes %s, spoiled_by %s" % (
                     {k: o.get(k) for k in ("success", "job", "curJob", "message")}, a["rect"], b["rect"], breaches[:2] or "no breach",
                     [l.get("outcome") for l in lines], sorted({str(l.get("spoiled_by")) for l in lines})) +
                 "; the planted rescuer's cells %s; before the breach the victims read %s" % (cells.get(a["rescuer"], [])[:8], raw_out)))


def row3(game, save, rows, tool, args):
    name = "R3 a mod state left dirty on purpose changes the reset digest and stops the repeat RESET_DIGEST_DIFFERS"
    with open_stage(game, save) as s:
        lst = reply(s.raw("jawa/mod_hooks", action="list"))
        mods = [m for m in lst.get("mods") or [] if isinstance(m, dict)]
        hooked = [m for m in mods if m.get("digest") not in (None, "", False, "no digest hook")]
        if not hooked or not tool:
            cmd = "python.exe src\\RimMandrake\\bridgetools\\prove_scene_repeats.py --game %s --rows R3 --dirty-tool <tool> --dirty-args '<json>'" % game
            rows.append((name, "UNRUN", "%d mod(s) of ours loaded, %d with a digest hook (%s); dirtying act %s. Needs a mod with an "
                         "[RMDigest] hook, an [RMReset] hook and its dirtying act. Command: %s" % (
                             len(mods), len(hooked), [m.get("mod") for m in hooked] or "none",
                             tool or "not given", cmd)))
            return
        mod = hooked[0]["mod"]
        blk = Blocks(s)
        bad, info = r3_reading(s, mod, tool, args, lambda i, series: stage_copy(s, i, series, blk))
    rows.append((name, bad, info))


def r3_reading(s, mod, tool, args, stage):
    """R3 on an open session: `mod` has a digest hook, `tool`/`args` dirty its state, stage(i, series) stages copy i (-> its
    rect and digest). -> (bad, info): bad None when the dirty state stops the repeat RESET_DIGEST_DIFFERS on that mod.
    The digest is proven first (step=clean, the dirtying act, step=dirty) and the mod's reset hook clears the state: a digest that
    is not proven reads None (scene_repeats.mod_digests), and step=clean sets the proof false (JawaBenchModHooksCore.Prove), so a
    first stamp taken before the proof would stop RESET_UNVERIFIED and compare nothing."""
    import scene_repeats as SR
    act = json.loads(args or "{}")
    clean = reply(s.raw("jawa/mod_hooks", action="prove", mod=mod, step="clean"))
    dirty = reply(s.raw(tool, **act))
    proof = reply(s.raw("jawa/mod_hooks", action="prove", mod=mod, step="dirty"))
    info = "mod %s; prove clean %s, dirty act %s, prove dirty %s" % (mod, short(clean, 120), short(dirty, 120), short(proof, 160))
    if proof.get("digestProven") is not True:
        return "COULD NOT LOOK: the digest hook of %s was not proven by its dirtying act" % mod, info
    reset = reply(s.raw("jawa/mod_hooks", action="reset", mod=mod))
    info += "; reset %s" % short(reset, 160)
    if reset.get("reset") != "verified":
        return "COULD NOT LOOK: the reset hook of %s did not bring the digest back to its clean read" % mod, info
    series = SR.Series("ordered_rescue_dirty", claim=_h(CLAIM), build=build_key(s), plan=_h(PLAN), distance=DISTANCE)
    k1 = stage(301, series)
    try:
        series.stamp(k1["digest"], SR.read_mod_digests(s), rect=k1["rect"])
    except SR.Stop as e:
        return "COULD NOT LOOK: the first stamp could not be a reference: %s %s" % (e.name, e.why), info
    again = reply(s.raw(tool, **act))
    k2 = stage(302, series)
    try:
        series.stamp(k2["digest"], SR.read_mod_digests(s), rect=k2["rect"])
        stop = None
    except SR.Stop as e:
        stop = e
    bad = None
    if stop is None:
        bad = "the dirty mod state did not stop the repeat"
    elif stop.name != "RESET_DIGEST_DIFFERS" or not any(p == "mod " + mod for p, _a, _b in stop.diffs):
        bad = "stopped %s on %s, not RESET_DIGEST_DIFFERS on mod %s" % (stop.name, [p for p, _a, _b in stop.diffs], mod)
    return bad, info + "; dirty act again %s; stop %s" % (short(again, 120), stop and "%s %s" % (stop.name, stop.diffs))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--game", default="ArchSmall")
    ap.add_argument("--rows", default="R1,R2,R3")
    ap.add_argument("--log")
    ap.add_argument("--no-make", action="store_true", help="the stage save RM_Stage_<game>_settlement is already on the game")
    ap.add_argument("--dirty-tool", help="R3: the bridge tool that dirties the hooked mod's state")
    ap.add_argument("--dirty-args", help="R3: its arguments as JSON")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        return selfcheck()
    want = set(a.rows.split(","))
    save = "RM_Stage_%s_settlement" % a.game
    log("prove_scene_repeats %s on %s, rows %s, stage %s" % (datetime.datetime.now().isoformat(timespec="seconds"), a.game, a.rows, save))
    if not a.no_make:
        import prove_stage_map as PSM
        rc, text, wall = PSM.wsl_make(a.game, "make", "--kind", "settlement", "--save", save)
        log("make settlement: exit %s, %.1f s wall\n  %s" % (rc, wall, "\n  ".join(text.strip().splitlines()[-12:])))
        if rc != 0:
            log("NO VERDICT: the stage was not made")
            return finish(a, 2)
    rows = []
    for r, fn in (("R1", lambda: row1(a.game, save, rows)), ("R2", lambda: row2(a.game, save, rows)),
                  ("R3", lambda: row3(a.game, save, rows, a.dirty_tool, a.dirty_args))):
        if r in want:
            try:
                fn()
            except SystemExit as e:
                log(str(e))
                return finish(a, 2)
            except Exception as e:  # noqa: BLE001  a row that threw is named and the next row runs
                rows.append(("%s (threw)" % r, "COULD NOT LOOK: %s: %s" % (type(e).__name__, str(e)[:600]), ""))
    fails = unrun = blind = 0
    for name, bad, info in rows:
        word = "PASS" if bad is None else ("UNRUN" if bad == "UNRUN" else ("COULD NOT LOOK" if str(bad).startswith("COULD NOT LOOK") else "FAIL"))
        unrun += word == "UNRUN"
        blind += word == "COULD NOT LOOK"
        fails += word == "FAIL"
        log("%s %s: %s" % (word, name, info if bad in (None, "UNRUN") else "%s | %s" % (bad, info)))
    log("prove_scene_repeats: %d of %d rows held, %d failed, %d could not look, %d unrun" % (
        len(rows) - fails - unrun - blind, len(rows), fails, blind, unrun))
    return finish(a, 1 if fails else (2 if blind else (3 if unrun else 0)))


def finish(a, rc):
    if a.log:
        with open(a.log, "w", encoding="utf-8") as f:
            f.write("\n".join(LINES) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
