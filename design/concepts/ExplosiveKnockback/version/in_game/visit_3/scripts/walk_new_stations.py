#!/usr/bin/env python3
"""The four 0.2.0 throws as walk stations (RIMMANDRAKE_STAGE_KNOCKBACK_WALK_STATIONS_NEW_PARTS_SAME_SIXTEEN): walk_save.py
imports this. Each station is staged as its 0.2.0 scene stages it, by the same bridge calls, on one column of the walk map:

    sc_pawn_arc_carried_thing       a colonist hauling 20 Steel; the blast throws it and the stack flies on its own arc
    sc_pawn_arc_bruise_sizes        a colonist thrown into a standing squirrel (lane 1) and a standing elephant (lane 2)
    sc_pawn_arc_sandbag_no_contact  a colonist thrown at a standing colonist behind a sandbag (lane 1); lane 2, no sandbag
    sc_gas_chain_pawn_on_cover      a drafted colonist on an intact pit cover; the Cauldron's vent gas burns beside it

The blast is jawa/explosion_at (Bomb, radius 2.9, damage 1) with "Bigger blasts throw harder" off, as in the scenes (a
real shell would down the thrown colonist and hide the bar). The AFTER site is set off and stepped to rest; the START site
is staged with nothing armed. An AFTER returns the record lines the sign quotes (from the knockback journal) or NOT STAGED.

Order (walk_save.after_new / start_new): every AFTER first, while nothing else stands on the map, then the 16 old AFTER
sites, then every START with no tick, except the carried START: its colonist needs a few ticks to pick the stack up, so
it is staged last of all, stepped only until it holds the stack, and turned to face its path (face_east).
"""
import json

SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
VENT = "RimMandrake.Cauldron.RM_MapComponent_VentGas"
COVERS = "RimMandrake.FlowWorks.Pits.RM_PitCoverUtility"
COVER = "RM_PitCover_ReinforcedFrame"
RADIUS = 2.9

# (key = the 0.2.0 scene, what stood there and what the blast did, what to decide)
NEW = [
    ("sc_pawn_arc_carried_thing", "NEW IN 0.2.0: a colonist hauling 20 steel is thrown; the stack leaves its hands and flies on its "
     "own arc to its own cell", "does the stack fly on its own and land where it should?"),
    ("sc_pawn_arc_bruise_sizes", "NEW IN 0.2.0: a thrown colonist hits a standing squirrel (lower lane) and a standing elephant "
     "(upper lane, 5 cells north); each is bruised by the other's size", "does the bruise feel right for the sizes?"),
    ("sc_pawn_arc_sandbag_no_contact", "NEW IN 0.2.0: a colonist is thrown at a standing colonist behind a sandbag; the sandbag "
     "stops the throw and nobody is touched (lower lane). Upper lane, 5 cells north: no sandbag, so both are bruised",
     "does the sandbag stop read as no contact?"),
    ("sc_gas_chain_pawn_on_cover", "NEW IN 0.2.0: a colonist stands on an intact pit cover; the Cauldron's vent gas burns "
     "beside it and shoves it one cell, unhurt; the cover stands", "does the shove off the cover read right?"),
]


class NotStaged(Exception):
    pass


def tick(b, n):
    b.call("rimworld/step_game_ticks", {"ticks": int(n), "pauseFirst": True, "timeoutMs": 120000})


def read(b, of, path):
    """-> the value of one jawa/read_paths read, or None when it does not read ok."""
    r = b.call("jawa/read_paths", {"reads": json.dumps([{"of": of, "path": path}])})
    v = (r.get("values") or [{}])[0]
    return v.get("v") if v.get("state") == "ok" else None


def spawn(b, kind, x, z, drafted=None):
    r = b.call("jawa/spawn_pawn", {"kindDef": kind, "x": x, "z": z, "faction": "player", "count": 1})
    p = (r.get("pawns") or [{}])[0]
    pid = p.get("id") or p.get("thingId")
    if not pid:
        raise NotStaged("spawn_pawn %s at %d,%d returned %s" % (kind, x, z, str(r)[:200]))
    if drafted is not None:
        b.call("jawa/set_draft", {"pawnId": pid, "drafted": drafted})
    return str(pid)


def of(pid):
    return pid if str(pid).startswith("thing:") else "thing:%s" % pid


def clear(b, x, z, w=15, h=15):
    """The station's patch: nothing built, grown or lying there (the old stations' Stage does the same in C#)."""
    b.call("jawa/destroy_batch", {"rects": "%d,%d,%d,%d" % (x - w // 2, z - h // 2, w, h), "categories": "Building,Plant,Item,Filth"})


def setting(b, field, value):
    r = b.call("jawa/mod_settings_field", {"typeName": SETTINGS, "action": "set", "field": field, "value": str(value)})
    if not (isinstance(r, dict) and r.get("success") and str(r.get("valueAfter")) == str(value)):
        raise NotStaged("setting %s=%s was not written: %s" % (field, value, str(r)[:200]))


def explode(b, x, z):
    b.call("jawa/explosion_at", {"at": "%d,%d" % (x, z), "radius": RADIUS, "damType": "Bomb", "damAmount": 1})


def journal(call):
    """-> the knockback journal's records (dicts), oldest first; call = knockback_runner.call bound to the bridge."""
    out = []
    for ln in str(call("Journal", "all")).splitlines():
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def steel_at(b, x, z):
    things = b.call("jawa/list_things", {"rect": "%d,%d,1,1" % (x, z), "defName": "Steel", "limit": 5}).get("things") or []
    return things[0] if things else None


def thing_ref(t):
    return str(t.get("id") or t.get("thingId") or ("%s%s" % (t.get("defName"), t.get("thingIDNumber"))))


def haul(b, x, z, wait=600):
    """A colonist at (x, z) on 20 Steel, ordered to haul it 6 cells east; stepped until it holds the stack. -> (pawn, ticks).
    East, not north: a pawn that faces north draws its load behind its body, so the START capture showed no steel."""
    pid = spawn(b, "Colonist", x, z, drafted=False)
    b.call("jawa/spawn_batch", {"ops": "Steel:%d,%d,20" % (x, z)})
    st = steel_at(b, x, z)
    if not st:
        raise NotStaged("no Steel on %d,%d after spawning it" % (x, z))
    b.call("jawa/ordered_job", {"pawnId": pid, "jobDef": "HaulToCell", "targetAId": thing_ref(st), "targetBX": x + 6,
                                "targetBZ": z, "count": 20, "waitTicks": 0})
    for n in range(1, wait + 1):
        tick(b, 1)
        if (read(b, of(pid), "carryTracker.innerContainer.innerList._size") or 0) > 0:
            return pid, n
    raise NotStaged("the colonist at %d,%d never picked the stack up in %d ticks" % (x, z, wait))


def corpse_in(b, kind, x, z):
    """A corpse of the kind within 7 cells of (x, z): a dead pawn no longer reads through its id (visit 3 of 0.2.0)."""
    things = b.call("jawa/list_things", {"rect": "%d,%d,15,11" % (x - 7, z - 5), "limit": 400}).get("things") or []
    return any(str(t.get("def") or t.get("defName")) == "Corpse_" + kind for t in things)


def rec_of(recs, kind, **match):
    return [r for r in recs if r.get("type") == kind and all(str(r.get(k)) == str(v) for k, v in match.items())]


# ---- the AFTER sites (set off, stepped to rest) ------------------------------------------------------------------------

def after_carried(b, call, x, z):
    clear(b, x, z)
    call("Clear", "x")
    pid, picked = haul(b, x, z)
    explode(b, x - 1, z)
    for _ in range(60):                         # the colonist lands about 20 ticks later; then it is drafted, or it would
        tick(b, 5)                              # walk back and haul the stack again (0.1.0 visit 1)
        recs = journal(call)
        if rec_of(recs, "item_land") and [r for r in recs if r.get("type") == "land"]:
            break
    b.call("jawa/set_draft", {"pawnId": pid, "drafted": True})
    tick(b, 120)
    recs = journal(call)
    ct = rec_of(recs, "carried_throw")
    il = rec_of(recs, "item_land")
    la = [r for r in recs if r.get("type") == "land"]
    if not ct or ct[0].get("act") != "thrown" or not il or not la:
        raise NotStaged("carried: carried_throw %s item_land %s land %s" % (ct[:1], il[:1], la[:1]))
    return ("the stack flew to %s, the colonist landed at %s (picked the stack up after %d ticks)"
            % (tuple(il[0].get("to") or ()), tuple(la[0].get("at") or ()), picked))


def bruise_lanes(b, x, z):
    lanes = []
    for animal, lz in (("Squirrel", z), ("Elephant", z + 5)):
        col = spawn(b, "Colonist", x, lz, drafted=True)
        ani = spawn(b, animal, x + 1, lz)
        lanes.append((animal, lz, col, ani))
    return lanes


def after_bruise(b, call, x, z):
    clear(b, x, z)
    call("Clear", "x")
    lanes = bruise_lanes(b, x, z)
    for _a, lz, _c, _p in lanes:
        explode(b, x - 2, lz)
    tick(b, 30)                                 # the bruise lands at once (the thrower stops on the standing pawn)
    b.call("jawa/pen_pin", {"rects": "%d,%d,15,15" % (x - 7, z - 7)})       # the animals stay where the bruise left them;
    tick(b, 90)                                 # pinned at 120 ticks, the squirrel and the elephant had stepped 1-3 cells
    recs = journal(call)
    out = []
    for animal, lz, col, ani in lanes:
        br = [r for r in recs if r.get("type") == "bruise" and animal in str(r.get("other"))]
        if not br:
            raise NotStaged("bruise: no bruise record names the %s (lane z %d)" % (animal, lz))
        dead = corpse_in(b, animal, x, lz)
        out.append("%s lane: the colonist took %s, the %s %s%s" % (animal.lower(), br[0].get("amount"), animal.lower(),
                                                                  br[0].get("otherAmount"), " and died of it" if dead else ""))
    return "; ".join(out)


def sandbag_lanes(b, x, z):
    out = []
    for lz, sand in ((z, True), (z + 5, False)):
        thrower = spawn(b, "Colonist", x, lz, drafted=True)
        if sand:
            r = b.call("jawa/build_batch", {"ops": "Sandbags:%d,%d" % (x + 1, lz), "stuff": "Cloth", "faction": "player",
                                            "wipeExisting": False})
            if not (r.get("survived") or r.get("placed")):
                raise NotStaged("sandbag at %d,%d not built: %s" % (x + 1, lz, str(r)[:200]))
        other = spawn(b, "Colonist", x + 2, lz, drafted=True)
        out.append((lz, sand, thrower, other))
    return out


def after_sandbag(b, call, x, z):
    clear(b, x, z)
    call("Clear", "x")
    lanes = sandbag_lanes(b, x, z)
    for lz, _s, _t, _o in lanes:
        explode(b, x - 1, lz)
    tick(b, 120)
    recs = journal(call)
    out = []
    for lz, sand, thrower, other in lanes:
        tid = thrower.replace("thing:", "")
        moves = [r for r in recs if r.get("type") in ("launch", "blocked") and str(r.get("thing")) == tid]
        br = [r for r in recs if r.get("type") == "bruise" and str(r.get("thing")) == tid]
        stop = moves[0].get("stop") if moves else None
        if sand and (stop != "PawnBeyondCover" or br):
            raise NotStaged("sandbag lane: stop %s, bruises %s" % (stop, br[:1]))
        if not sand and (stop != "Pawn" or not br):
            raise NotStaged("open lane: stop %s, bruises %s" % (stop, br[:1]))
        out.append("sandbag lane: stopped by the sandbag, no bruise on anyone" if sand else
                   "open lane: the colonist hit the standing one; bruises %s and %s" % (br[0].get("amount"), br[0].get("otherAmount")))
    return "; ".join(out)


def cover_lane(b, x, z):
    """A pit dug to superdeep at (x, z), FlowWorks' reinforced cover on it, a drafted colonist walked onto the deck from 3
    cells east (one staged on the cell before the dig would stand beneath the cover). -> the colonist."""
    clear(b, x, z)
    pid = spawn(b, "Colonist", x + 3, z, drafted=True)
    dig = b.call("jawa/flowworks_excavation_drive", {"x": x, "z": z, "deepenLevels": 4, "setBodyWaterM": -1})
    if not dig.get("success"):
        raise NotStaged("cover: the dig at %d,%d failed: %s" % (x, z, str(dig)[:200]))
    r = b.call("jawa/build_batch", {"ops": "%s:%d,%d" % (COVER, x, z), "faction": "player", "wipeExisting": False})
    if not (r.get("survived") or r.get("placed")):
        raise NotStaged("cover not built at %d,%d: %s" % (x, z, str(r)[:200]))
    b.call("jawa/ordered_job", {"pawnId": pid, "jobDef": "Goto", "targetAX": x, "targetAZ": z, "waitTicks": 0})
    for _ in range(60):
        tick(b, 10)
        if read(b, of(pid), "positionInt.x") == x and read(b, of(pid), "positionInt.z") == z:
            break
    else:
        raise NotStaged("cover: the colonist never stood on the deck at %d,%d" % (x, z))
    if not cover_at(b, x, z):
        raise NotStaged("cover: no intact cover at %d,%d under the colonist" % (x, z))
    return pid


def cover_at(b, x, z):
    r = b.call("jawa/static_call", {"type": COVERS, "method": "CoverAt", "args": "current|%d,0,%d" % (x, z)})
    out = str(r.get("result"))
    return out if r.get("success") and out not in ("", "None", "null") else None


def seed(b, x, z):
    return str(b.call("jawa/static_call", {"type": VENT, "method": "SeedCloud", "args": "current|%d,0,%d|2|250" % (x - 3, z)}).get("result"))


def after_cover(b, call, x, z):
    call("Clear", "x")
    pid = cover_lane(b, x, z)
    seed(b, x, z)
    b.call("jawa/spawn_batch", {"ops": "Fire:%d,%d" % (x - 5, z)})
    tid = pid.replace("thing:", "")
    launch = []
    for _ in range(30):                         # BurnScan every 30 ticks: the front walks from the fire to the colonist
        tick(b, 30)
        launch = [r for r in journal(call) if r.get("type") == "launch" and str(r.get("thing")) == tid]
        if launch:
            break
    tick(b, 240)
    b.call("jawa/map_fire", {"action": "extinguish", "rect": "%d,%d,15,15" % (x - 7, z - 7)})
    if not launch or not launch[0].get("gas") or not launch[0].get("onCover"):
        raise NotStaged("cover: launch %s" % launch[:1])
    if not cover_at(b, x, z):
        raise NotStaged("cover: the cover at %d,%d is gone after the burn" % (x, z))
    return "the burning gas shoved the colonist from %s to %s (%s cell, impact %s); the cover still stands" % (
        tuple(launch[0].get("from") or ()), tuple(launch[0].get("to") or ()), launch[0].get("cells"), launch[0].get("impact"))


AFTER = {"sc_pawn_arc_carried_thing": after_carried, "sc_pawn_arc_bruise_sizes": after_bruise,
         "sc_pawn_arc_sandbag_no_contact": after_sandbag, "sc_gas_chain_pawn_on_cover": after_cover}
AFTER_ORDER = ["sc_gas_chain_pawn_on_cover", "sc_pawn_arc_sandbag_no_contact", "sc_pawn_arc_carried_thing",
               "sc_pawn_arc_bruise_sizes"]      # the longest first; the animals last, so they stand pinned the least time


# ---- the START sites (nothing armed, no tick) --------------------------------------------------------------------------

def start_bruise(b, x, z):
    clear(b, x, z)
    bruise_lanes(b, x, z)
    b.call("jawa/pen_pin", {"rects": "%d,%d,15,15" % (x - 7, z - 7)})
    return "a colonist beside a squirrel (lower lane) and beside an elephant (upper lane); the blast stood 2 cells west of each colonist"


def start_sandbag(b, x, z):
    clear(b, x, z)
    sandbag_lanes(b, x, z)
    return "a colonist, a sandbag, a standing colonist (lower lane); the same with no sandbag (upper lane); the blast stood 1 cell west"


def start_cover_walk(b, x, z):
    """Ticks: the walk onto the deck. Done with the AFTER sites, before any START site is staged; drafted, it stays."""
    cover_lane(b, x, z)


def start_cover_gas(b, x, z):
    return "the colonist on the pit cover; the vent gas cloud beside it, unlit (%s)" % seed(b, x, z)[:60]


def face_east(b, pid):
    """Turn the hauler to face its path. One tick after the pickup it still faces north, and a pawn that faces north draws
    its load behind its body (the first capture of this START showed no steel). Locked to turn, unlocked at once: the lock
    is saved with the pawn (jawa/set_pawn_rotation), the facing holds while the game stays paused."""
    for d in ("east", "unlock"):
        r = b.call("jawa/set_pawn_rotation", {"pawnId": str(pid).replace("thing:", ""), "dir": d})
        if not r.get("success"):
            raise NotStaged("set_pawn_rotation %s: %s" % (d, str(r)[:200]))


def start_carried(b, x, z):
    clear(b, x, z)
    pid, picked = haul(b, x, z)
    face_east(b, pid)
    return "the colonist holds the 20 steel it was ordered to haul east (it picked the stack up %d tick(s) ago)" % picked
