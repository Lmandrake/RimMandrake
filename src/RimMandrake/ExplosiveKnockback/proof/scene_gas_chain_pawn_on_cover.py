"""scene_gas_chain_pawn_on_cover.py - Explosive Knockback 0.2.0, sc_gas_chain_pawn_on_cover: a burning gas burst shoves a
colonist who stands on an intact pit cover one cell, unhurt, as it shoves one on plain ground (scene library 0.3.0).

Bar (design/concepts/ExplosiveKnockback/record.json): gas_shoves_pawn_on_pit_cover. The kernel's rule is decided offline
(RM_KnockbackPlan.PawnSkipReason: a superdeep cell skips its pawn as in_pit unless the source is gas and the cell is under
an intact cover; RM_MapComponent_Knockback sets onCover only for a pawn on the deck, not beneath it). This scene reads what
only the game can show: the Cauldron's real burning vent gas, through the gas chain, shoves a colonist off a real FlowWorks
cover; the shove is one cell, with no impact; the cover still stands.

Kind A. A fresh quicktest map on ArchSmall; one clean station; two lanes, 14 cells apart, each set off alone. Along +x:
  cover    fire (3, z) | vent gas seeded at (5, z), radius 2 (cells 3..7) | colonist on RM_PitCover_ReinforcedFrame over a
           superdeep pit (8, z) | plain soil (9, z)
  control  the same, with no pit and no cover: the colonist on plain soil at (8, z)
The pit is jawa/flowworks_excavation_drive (4 Deepen calls: RM_KnockbackCompat.DigToSuperdeep's own count). The cover is
FlowWorks' RM_PitCover_ReinforcedFrame (RM_PitCovers.xml, 160 HP, no stuff), placed by s.act.place after the dig. The
colonist is staged 3 cells east, drafted (jawa/set_draft) and walked onto the deck (jawa/ordered_job Goto): a pawn staged
on the cell before the dig would stand beneath the cover, not on it. The control colonist walks the same 3 cells. The gas is RM_MapComponent_VentGas.SeedCloud
(radius 2, 250 a cell, as RM_KnockbackProof's gas_into_pit stages it), lit by one Fire at its far end (jawa/spawn_batch):
the Cauldron's BurnScan lights the cells beside a fire, and the burning front walks east to (7, z). Of the seeded cells only
(7, z) reaches the colonist (1 cell, inside gasBurstRadius 1.9; (6, z) is 2, (7, z+-1) is not seeded), and none reaches
(9, z) (2 or more cells), so one shove is the most it can take; gas that drifts nearer is the open point below. No
raid, no hostile pawn. gasChain stays at the player's value (read and printed; the bar is read at its default, true).

The checks (each prints PASS or FAIL with what it read):
  V_SMALL_LIST       design/concepts/ExplosiveKnockback/version/small_list.json "also" holds mandrake.rm.flowworks and
                     mandrake.rm.biomes (the Cauldron), the two mods this scene needs beside ours
  V_ON_DECK cover    the colonist stood on the cover cell when the gas was lit, and CoverAt there read a cover
  V_SHOVE <lane>     exactly one `launch` record names the colonist: gas true, planned <= 1, impact 0; the colonist ends
                     spawned, exactly 1 cell (chessboard) from where it stood, and its `land` record reads the launch's `to`
  V_ON_COVER cover   that launch reads onCover true (the kernel saw a pawn on an intact cover, not one in a pit)
  V_UNHURT <lane>    no hediff other than Burn was added (the shove harms nobody; a Burn is the fire's, printed)
  V_COVER_INTACT     RimMandrake.FlowWorks.Pits.RM_PitCoverUtility.CoverAt still reads a cover on the pit cell after the
                     settle; its hitPointsInt before and after is printed
  V_BURST <lane>     at least one `gas_burst` record was written in the lane (else the lane is UNLAID: the gas never burned)
  SHOTS              <lane>_lit when the first burst is seen, <lane>_after after the settle

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_gas_chain_pawn_on_cover.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_gas_chain_pawn_on_cover.py --plant gas_chain_off

UNRUN until Stage 6: written 2026-11-24 by RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT and never run live.
The plant `gas_chain_off` sets gasChain False (restored in a finally): V_SHOVE, V_ON_COVER and V_BURST must then FAIL on
both lanes (the gas still burns, nobody is shoved), which shows that the checks can see a shove.
Open points for the first run:
  - the dig, the gas, the fire, the draft, the walk and the cover reads are s.raw (jawa/flowworks_excavation_drive,
    jawa/static_call, jawa/spawn_batch, jawa/set_draft, jawa/ordered_job, jawa/mod_settings_field): the run is EXPLORED
    and counts for no bar until verbs for them are built (`order` is NOT_BUILT).
  - whether s.act.place (jawa/build_batch) puts the cover on a pit cell (its place worker may want a designator); if
    it refuses, place it with jawa/spawn_batch "RM_PitCover_ReinforcedFrame:x,z" and read CoverAt as here.
  - drift: vent gas that drifts to (7, z+-1) or (8, z) before it burns can burst at the colonist's cell too; a second
    launch then fails V_SHOVE, and the row prints every launch.
  - whether a drafted colonist paths onto the deck (V_ON_DECK prints where it stood); whether vent gas enters the
    cover's cell (it need not: the burst at (7, z) reaches it either way).
  - a fire spreading to the colonist sets it alight; V_UNHURT ignores Burn, and a burning colonist that runs off its
    cell before the burst spoils V_SHOVE (the row prints whether a Fire is on its cell).
"""
import json
import os

import scene
from scene import cond as c

GAME = "ArchSmall"
# a stage save (stage_map.py make ArchSmall --kind settlement --save RM_Stage_ExplosiveKnockback): every roof and
# destroyable thing cleared. A fixed station on a fresh quicktest map can lie under mountain roof: on 2026-11-24 the
# colonist was gone by tick 3 under collapsed rocks and the stack buried (APPARATUS FAULT of the first run).
STAGE = "RM_Stage_ExplosiveKnockback"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
JOURNAL = "RimMandrake.ExplosiveKnockback.RM_KnockbackJournal"
VENT = "RimMandrake.Cauldron.RM_MapComponent_VentGas"
COVERS = "RimMandrake.FlowWorks.Pits.RM_PitCoverUtility"
COVER = "RM_PitCover_ReinforcedFrame"
SMALL_LIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "design", "concepts",
                          "ExplosiveKnockback", "version", "small_list.json")
STATION = (20, 20, 20, 30)
LANES = {"cover": 6, "control": 20}
ORDER = ["cover", "control"]
X0 = 8              # the colonist's cell (the cover's, in the cover lane)
GAS_AT, GAS_R, GAS_AMOUNT = 5, 2, 250
FIRE_AT = 3
WALK = 600          # ticks for the walk of 3 cells onto the deck
BURN = 900          # ticks for the front to walk from the fire to (7, z): BurnScan every 30 ticks
SETTLE = 240

on_cover = scene.contract(
    claim="a burning gas burst shoves a colonist on an intact pit cover one cell, unhurt, and the cover stands",
    kind="A",
    exposure=c.state("cover", "positionInt") == "ok",          # the cover really stood under the colonist
    success=[c.played(SETTLE)],                              # the judged run is the last: the control lane's settle
    forbidden=[],
    end=SETTLE, limit=len(ORDER) * (WALK + BURN + SETTLE) + 900)


def at(x, z):
    return STATION[0] + x, STATION[1] + z



# The journal is a static list: it outlives a load. Every run of a scene loads the same stage save, so its thing ids and
# ticks repeat, and a filter on tick or id cannot tell this run's records from the last run's. mark_journal keeps the
# last line already there when the session opens; since_mark keeps only the lines after it (the list trims its oldest
# 1000 lines at 4000, so the mark is a line's text, not a position; a mark trimmed away means every line is this run's).
_MARK = []


def mark_journal(s):
    v = s.read("static:" + JOURNAL, "lines")
    lines = list(v.v) if v.state == "ok" and isinstance(v.v, (list, tuple)) else []
    _MARK[:] = [lines[-1] if lines else None, len(lines)]
    print("INFO journal mark: %d line(s) before this run" % len(lines))


def since_mark(raw):
    raw = list(raw)
    if not _MARK or _MARK[0] is None:
        return raw
    for i in range(len(raw) - 1, -1, -1):
        if raw[i] == _MARK[0]:
            return raw[i + 1:]
    return raw


def journal(s, since):
    v = s.read("static:" + JOURNAL, "lines")
    if v.state != "ok":
        return []
    raw = since_mark(v.v if isinstance(v.v, (list, tuple)) else str(v.v).splitlines())
    recs = []
    for line in raw:
        line = str(line).strip()
        if line.startswith("{"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r.get("tick"), (int, float)) and r["tick"] >= since:
                recs.append(r)
    return recs


def thing_id(s, alias):
    d, n = s.read(alias, "def.defName"), s.read(alias, "thingIDNumber")
    return "%s%d" % (d.v, int(float(n.v))) if d.state == "ok" and n.state == "ok" else None   # an id reads back as a float


def num(v):
    try:
        return float(v.v) if v.state == "ok" else None
    except (TypeError, ValueError):
        return None


def pos(s, alias):
    return (num(s.read(alias, "positionInt.x")), num(s.read(alias, "positionInt.z")))


def hediffs(s, alias):
    """-> sorted [defName] of the pawn's hediffs, or None when they cannot be read."""
    n = s.read(alias, "health.hediffSet.hediffs._size")
    if n.state != "ok":
        return None
    vals = s.read_many(reads=[(alias, "health.hediffSet.hediffs[%d].def.defName" % i) for i in range(int(n.v))]) if int(n.v) else []
    return sorted(str(v.v) for v in vals if v.state == "ok")


def cover_at(s, x, z):
    r = s.raw("jawa/static_call", type=COVERS, method="CoverAt", args="current|%d,0,%d" % (x, z)) or {}
    out = str(r.get("result"))
    return out if r.get("success") and out not in ("", "None", "null") else None


def gas(s, method, args):
    return str((s.raw("jawa/static_call", type=VENT, method=method, args=args) or {}).get("result"))


def lane(s, name, rows):
    z = LANES[name]
    col = "colonist_" + name
    cid = thing_id(s, col)
    row = dict(cid=cid, err=None)
    rows[name] = row
    cx, cz = at(X0, z)
    s.raw("jawa/set_draft", pawnId=cid, drafted=True)
    if name == "cover":
        row["dig"] = {k: (s.raw("jawa/flowworks_excavation_drive", x=cx, z=cz, deepenLevels=4, setBodyWaterM=-1) or {}).get(k)
                      for k in ("success", "depth")}
        s.act.place(COVER, at=(cx, cz), bind="cover")
        row["hp_before"] = num(s.read("cover", "hitPointsInt"))
    s.raw("jawa/ordered_job", pawnId=cid, jobDef="Goto", targetAX=cx, targetAZ=cz, waitTicks=0)    # both lanes walk the same 3 cells
    s.run(until=c.value(col, "positionInt.x") == cx, limit=WALK)
    if name == "cover":
        row["deck"] = cover_at(s, cx, cz)
    row["stood"] = pos(s, col)
    row["before"] = hediffs(s, col)
    t0 = s.read(col, "positionInt").tick or 0
    gx, gz = at(GAS_AT, z)
    row["seeded"] = gas(s, "SeedCloud", "current|%d,0,%d|%d|%d" % (gx, gz, GAS_R, GAS_AMOUNT))
    fx, fz = at(FIRE_AT, z)
    row["fire"] = (s.raw("jawa/spawn_batch", ops="Fire:%d,%d" % (fx, fz)) or {}).get("thingsPlaced")
    rect = (STATION[0], STATION[1] + z - 4, 14, 9)
    lit = False
    for _ in range(BURN // 30):
        s.run(until=30, limit=40)
        if not lit and any(r.get("type") == "gas_burst" for r in journal(s, t0)):
            lit = True
            s.shot(rect, name=name + "_lit")
        if any(r.get("type") == "launch" and r.get("thing") == cid for r in journal(s, t0)):
            break
    if not lit:
        s.shot(rect, name=name + "_lit")
    s.run(until=SETTLE, limit=SETTLE + 60)
    s.shot(rect, name=name + "_after")
    recs = journal(s, t0)
    row["bursts"] = [r for r in recs if r.get("type") == "gas_burst"]
    row["moves"] = [r for r in recs if r.get("thing") == cid and r.get("type") in ("launch", "blocked", "skip")]
    row["lands"] = [r for r in recs if r.get("thing") == cid and r.get("type") == "land"]
    row["after"] = hediffs(s, col)
    row["end"] = pos(s, col)
    row["spawned"] = s.read(col, "Spawned").v
    ex, ez = row["end"]
    row["burning"] = (None if None in (ex, ez) else      # a Fire on the colonist's cell: its own (attached) or the ground's
                      any(v.state == "ok" and str(v.v) == "Fire" for v in s.read_many(rect=(int(ex), int(ez), 1, 1), path="def.defName")))
    if name == "cover":
        row["intact"] = cover_at(s, cx, cz)
        row["hp_after"] = num(s.read("cover", "hitPointsInt"))


def small_list():
    try:
        with open(SMALL_LIST) as f:
            also = json.load(f).get("also") or {}
    except (OSError, ValueError) as e:
        return None, str(e)
    return sorted(also), None


planted = scene.plant() == "gas_chain_off"
cast = {"colonist_" + n: dict(kind="Colonist", at=(X0 + 3, z), faction="player") for n, z in LANES.items()}
listed, list_err = small_list()

with scene.open(GAME, contract=on_cover, needs={"mods": ["ExplosiveKnockback", "FlowWorks", "Cauldron"], "map": STAGE,
                                               "calm": "standard"}) as s:
    mark_journal(s)
    s.stage(station=STATION, cast=cast)
    prior = {f: (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f) or {}).get("value") for f in ["gasChain"]}
    rows = {}
    try:
        if planted:
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="gasChain", value="False")
        for name in ORDER:
            gas(s, "ClearOf", "current")
            lane(s, name, rows)
    finally:
        gas(s, "ClearOf", "current")                       # harness housekeeping: no vent gas outlives the scene
        s.raw("jawa/map_fire", action="extinguish", rect="%d,%d,%d,%d" % STATION)
        for f, v in prior.items():   # back to what it read before, on every exit path
            if v is not None:
                s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v))
    folder = s.run_dir

fails = 0


def row(ok, ident, text):
    global fails
    fails += not ok
    print("%s %s: %s" % ("PASS" if ok else "FAIL", ident, text))


def as_bool(v):
    return v is True or str(v).lower() == "true"


def cell(v):
    return tuple(int(a) for a in v) if isinstance(v, (list, tuple)) and len(v) == 2 else None


print("INFO gasChain = %s (the bar is read at its default, True)" % prior.get("gasChain"))
row(listed is not None and "mandrake.rm.flowworks" in listed and "mandrake.rm.biomes" in listed, "V_SMALL_LIST",
    "small_list.json also = %s%s" % (listed, ", " + list_err if list_err else ""))
for name in ORDER:
    r = rows[name]
    cx, cz = at(X0, LANES[name])
    if name == "cover":
        row(r.get("stood") == (cx, cz) and r.get("deck") is not None, "V_ON_DECK cover",
            "stood at %s (deck %s), CoverAt %s; dig %s" % (r.get("stood"), (cx, cz), r.get("deck"), r.get("dig")))
    row(len(r["bursts"]) >= 1, "V_BURST " + name, "%d gas_burst record(s); seeded %s; fire placed %s%s" % (
        len(r["bursts"]), r["seeded"], r["fire"], "" if r["bursts"] else ": UNLAID"))
    launches = [m for m in r["moves"] if m.get("type") == "launch"]
    m = launches[0] if len(launches) == 1 else None
    st, en = r["stood"], r["end"]
    moved = (max(abs(en[0] - st[0]), abs(en[1] - st[1])) if None not in st + en else None)
    land_ok = m is not None and len(r["lands"]) >= 1 and cell(r["lands"][0].get("at")) == cell(m.get("to"))
    try:
        planned, impact = float(m.get("planned")), float(m.get("impact"))
    except (TypeError, ValueError, AttributeError):
        planned, impact = None, None
    row(m is not None and as_bool(m.get("gas")) and planned is not None and planned <= 1 and impact == 0
        and as_bool(r["spawned"]) and moved == 1 and land_ok, "V_SHOVE " + name,
        "%d launch(es) %s; moved %s cell(s) %s -> %s; land %s; fire on its cell after %s" % (
            len(launches), [{k: x.get(k) for k in ("gas", "planned", "cells", "impact", "stop", "from", "to")} for x in launches],
            moved, st, en, [x.get("at") for x in r["lands"]], r["burning"]))
    if name == "cover":
        row(m is not None and as_bool(m.get("onCover")), "V_ON_COVER cover",
            "launch onCover %s; other records %s" % (m.get("onCover") if m else None,
                                                      [{k: x.get(k) for k in ("type", "reason")} for x in r["moves"] if x is not m]))
        row(r.get("intact") is not None, "V_COVER_INTACT",
            "CoverAt %s after the settle; hitPointsInt %s -> %s" % (r.get("intact"), r.get("hp_before"), r.get("hp_after")))
    b, a = r["before"], r["after"]
    added = None
    if b is not None and a is not None:
        added = list(a)
        for d in b:
            if d in added:
                added.remove(d)
    row(added is not None and all(d == "Burn" for d in added), "V_UNHURT " + name, "hediffs added: %s (Burn is the fire's)" % added)
print("%s sc_gas_chain_pawn_on_cover: %d failing row(s); pictures in %s" % ("PASS" if fails == 0 else "FAIL", fails, folder))
print(scene.judge(folder))
