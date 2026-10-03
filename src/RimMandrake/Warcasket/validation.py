"""validation.py -- modcheck suite for RimMandrake: Warcasket (mandrake.rm.warcasket).
Walk: design/validation_walks/RimMandrake/Warcasket.md (`## must be true`, every line arrowed to a
component below). Plan: northstar_plan.py. Tier: `warcasket` (modset_builder.py --list).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Warcasket \\
        --plan src/RimMandrake/Warcasket/northstar_plan.py

Grounded in the mod's source, read in full: `RM_CompWarcasketIntegrity.cs` (compound failure,
CompTickRare = every 250 ticks, 2+ of {vacuum, temp <= -60 or >= 70, polluted ground or
ToxicFallout}), `RM_MapComponent_HazardousTerrainImmersion.cs` (non-walkable water, 250-tick
checks, +0.12 x driveFactor, driveFactor = max(0.05, 1 - protection)), `RM_Sarcophagus.cs`,
`RM_CaskBay.cs` (shielding + core dose, both expose their state through CompInspectStringExtra),
`RM_WarcasketSettings.cs` (SIX toggles), and Defs/*.xml.

THE ONE STATISTICAL CHECK. The compound failure is a dice roll (0.015 per rare tick with two
hazards). A single wearer proves nothing, so `compound_failure` runs TWENTY wearers per arm for
4000-6000 ticks: ~7 expected failures in the 6000-tick ON arm (P(zero by chance) ~ 0.1%), ~4.8 in
each 4000-tick OFF arm (~0.8%). A CONTROL room carries ONE hazard (heat, no pollution): the mod
promises that never fails, and the same sample size would expose a mod that counted a single
hazard. Vacuum, the third hazard, has no bridge tool to create it, so the two-hazard path is
heat + polluted ground (`UNCOVERED: vacuum` is named in the walk).

TWO MOD DEFECTS FOUND AND FIXED OFFLINE while writing this (never seen red live): (1) RM_Warcasket had
no `tickerType`, so apparel (default Never) never ran `CompTickRare` and the compound failure could not
fire -- guard: `compound_failure_fires`; (2) `ToxicEnvironmentResistance` sat in `statBases` where vanilla
masks use `equippedStatOffsets` (the pawn stat reads the offset) -- guards: `toxin_cover`,
`warcasket_wearer_resists_core_dose`.

Behaviour that is UNMEASURED until the first live run: `jawa/make_empty_room` leaves one random
DOOR (room_heat is re-set every 500 ticks for that reason); `jawa/ordered_job` accepting a Corpse
as targetA; Soil being pollutable (the site component checks `cellsEverPollutable`).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.join(HERE, "..", "Utils")
if os.path.isdir(_UTILS) and _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)

from modcheck import Suite, ExpectationFailed

suite = Suite("Warcasket")
suite.toggles = ["masterEnabled", "compoundFailureEnabled", "terrainImmersionEnabled",
                 "sarcophagiEnabled", "caskBayShieldingEnabled", "coreDoseEnabled"]

SETTINGS = "RimMandrake.Warcasket.RM_WarcasketSettings"
SUIT, JUNKER, BAY, CORE = "RM_Warcasket", "RM_WarcasketJunker", "RM_CaskBay", "RM_HalfExtractedCore"
BREACH, IMMERSION = "RM_WarcasketBreach", "RM_TerrainImmersionHazard"
HEAT_C = 80.0                 # >= the suit's extremeHeatThresholdC (70)
N_PER_ROOM = 20
ROOM = 13                     # 13x13 outer, 11x11 interior


# ------------------------------------------------------------------------------- helpers

def _live(t):
    """True only for a real run on a real Session and an unfailed chain; False for the offline
    declaration probe, so assertions never trip on its no-op (None) results."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed or unreadable: %s" % (what, str(r)[:200]))
    return r


def _note(t, label, data):
    """Evidence record, echoed to stderr (the results JSON keeps only a ~300-char excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("[warcasket-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]),
              file=sys.stderr, flush=True)


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


def _prep_site(t, size=90):
    """Everything true before the first assertion: clear, Soil floor, unfogged, clear locked weather."""
    t.clear_area(size=size)
    x, z = t.anchor
    h = size // 2
    t.bridge_call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % (x - h, z - h, size, size))
    t.bridge_call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (x - h, z - h, size, size))
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
    t.bridge_call("jawa/log_autoopen_suppress")


def _spawn(t, x, z, kind="Colonist"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="player", count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("jawa/spawn_pawn gave no pawn at (%d,%d): %s" % (x, z, str(r)[:160]))
    return pid


def _wear(t, pid, def_name):
    r = t.bridge_call("jawa/pawn_gear", pawn=pid, action="wear", **{"def": def_name, "quality": "Normal"})
    if _live(t):
        _ok(r, "pawn_gear wear %s on %s" % (def_name, pid))
    return r


def _settle(t, pid, draft=True):
    """Fed, rested, and (default) drafted so it stands exactly where it was put."""
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
    t.bridge_call("jawa/set_draft", pawnId=pid, drafted=bool(draft))


def _stats(t, pid, names):
    """{stat: value} read off the PAWN instance. A refused stat is UNMEASURED, never 0."""
    r = t.bridge_call("jawa/pawn_stats", pawn=pid, stats=",".join(names))
    if not _live(t):
        return {}
    _ok(r, "pawn_stats")
    if r.get("refused"):
        _fail("UNMEASURED: pawn_stats refused %s (DLC inactive? wrong stat name?)" % r.get("refused"))
    got = dict((s.get("defName"), s.get("value")) for s in (r.get("stats") or []))
    missing = [n for n in names if got.get(n) is None]
    if missing:
        _fail("UNMEASURED: pawn_stats returned no value for %s" % missing)
    return got


def _pawn_rows(t, rect):
    """list_pawns rows (with health) in rect. Hediffs live at row['health']['hediffs']."""
    r = t.bridge_call("jawa/list_pawns", rect=rect, includeHealth=True, limit=200)
    if not _live(t):
        return []
    _ok(r, "list_pawns")
    return (r or {}).get("pawns") or []


def _hediff(row, def_name):
    """Severity of `def_name` on a list_pawns row, or 0.0 when absent."""
    sev = 0.0
    for h in ((row.get("health") or {}).get("hediffs") or []):
        if h.get("def") == def_name:
            sev = max(sev, float(h.get("severity") or 0.0))
    return sev


def _count_things(t, rect, defs):
    """{def: count} for ground things in rect. A truncated/failed read is not 'zero'."""
    r = t.bridge_call("jawa/list_things", defName=defs, rect=rect, limit=500)
    if not _live(t):
        return {}
    _ok(r, "list_things")
    if r.get("isCompleteList") is False:
        _fail("list_things truncated: %s" % str(r)[:160])
    out = {}
    for th in r.get("things") or []:
        d = th.get("def") or th.get("defName")
        out[d] = out.get(d, 0) + int(th.get("stackCount") or 1)
    return out


def _inspect(t, defname, rect):
    r = t.bridge_call("jawa/inspect_string", defName=defname, rect=rect, limit=10)
    if not _live(t):
        return []
    _ok(r, "inspect_string(%s)" % defname)
    rows = r.get("things") or []
    if r.get("threw"):
        _fail("inspect_string threw for %s: %s" % (defname, [x.get("error") for x in rows if x.get("error")]))
    return [" | ".join(x.get("inspect") or []) for x in rows]


def _restore(t):
    """Always put every toggle back, even when the chain has failed (direct session call: a failed
    chain's `_guard()` would swallow t.set_setting and leave a toggle OFF for the next chain)."""
    if t.session is None:
        return
    for field in suite.toggles:
        try:
            t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value="True")
        except Exception as ex:   # noqa: BLE001 -- surfaced, never swallowed silently
            print("[warcasket] restore %s failed: %s" % (field, ex), file=sys.stderr, flush=True)


# ------------------------------------------------------------------------------- chain 1: defs

@suite.chain("defs_and_load")
def defs_and_load(t):
    """Static intent, read back from the RUNNING game: every shipped def resolved, the comps and
    extensions the XML names actually bound, and the log clean."""
    shipped = ["ThingDef/%s" % d for d in (SUIT, JUNKER, BAY, CORE)] + [
        "StatDef/RM_HazardousTerrainProtection", "HediffDef/%s" % BREACH, "HediffDef/%s" % IMMERSION,
        "JobDef/RM_CrackSarcophagus", "ThingCategoryDef/RM_HazardCasks"]

    with t.component("defs_resolve"):
        r = t.bridge_call("jawa/get_defs", defs=";".join(shipped), fields="defName,label")
        if _live(t):
            _ok(r, "get_defs")
            if r.get("notFound") or r.get("foundCount") != len(shipped):
                _fail("shipped defs did not all resolve: foundCount=%r of %d, notFound=%r"
                      % (r.get("foundCount"), len(shipped), r.get("notFound")))

    with t.component("absent_def_is_refused"):
        # CONTROL: proves defs_resolve can fail -- a def that is not there must come back notFound.
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_WarcasketDoesNotExist", fields="defName")
        if _live(t):
            _ok(r, "get_defs(control)")
            if r.get("foundCount") or "RM_WarcasketDoesNotExist" not in str(r.get("notFound")):
                _fail("get_defs answered for a def that does not exist: %s" % str(r)[:200])

    with t.component("comps_wired"):
        r = t.bridge_call(
            "jawa/get_defs", defs="ThingDef/%s;ThingDef/%s;ThingDef/%s;ThingDef/%s" % (SUIT, JUNKER, BAY, CORE),
            fields="comps,modExtensions")
        if _live(t):
            _ok(r, "get_defs(comps)")
            if r.get("notFound"):
                _fail("defs missing: %r" % r.get("notFound"))
            rows = dict((d.get("defName"), json.dumps(d.get("fields") or {}, default=str)) for d in (r.get("defs") or []))
            want = {SUIT: "WarcasketIntegrity", JUNKER: "SarcophagusSeal", BAY: "CaskShielding", CORE: "CoreDose"}
            bad = [d for d, frag in want.items() if frag not in rows.get(d, "")]
            if bad:
                _fail("comp not bound on %s (a mistyped Class discards the comp): %s" % (bad, rows))
            if "JunkerSarcophagusExtension" not in rows.get(JUNKER, ""):
                _fail("RM_WarcasketJunker lost its RM_JunkerSarcophagusExtension: %s" % rows.get(JUNKER))
            # CONTROL: the base suit must NOT carry the sarcophagus seal (Junker-only).
            if "SarcophagusSeal" in rows.get(SUIT, ""):
                _fail("base RM_Warcasket carries the sarcophagus seal: %s" % rows.get(SUIT))

    with t.component("no_warcasket_log_errors"):
        r = t.bridge_call("jawa/drain_log", contains="Warcasket", errorsOnly=True, limit=50)
        if _live(t):
            _ok(r, "drain_log")
            if (r.get("totalInBuffer") or 0) >= 1000:
                _fail("UNMEASURED: log buffer is full (%s lines) -- load-time lines have rolled out; read "
                      "Player.log's first exception instead" % r.get("totalInBuffer"))
            if r.get("messages"):
                _fail("Warcasket log errors/warnings: %s" % [m.get("text", "")[:160] for m in r["messages"][:3]])


# ------------------------------------------------------------------------------- chain 2: suit stats

@suite.chain("suit_stats")
def suit_stats(t):
    """Intended function of the base suit and the Junker variant, read off a wearer BEFORE and
    AFTER putting it on (the naked reading is the control: a suit that applied nothing would read
    a zero delta)."""
    names = ["ComfyTemperatureMin", "ComfyTemperatureMax", "VacuumResistance",
             "ToxicEnvironmentResistance", "MoveSpeed", "WorkSpeedGlobal"]
    x, z = t.anchor
    S = {}
    with t.component("site_ready_suit"):
        _prep_site(t, 40)
        S["a"] = _spawn(t, x, z)
        S["j"] = _spawn(t, x + 4, z)
        if _live(t):
            for k in ("a", "j"):
                _settle(t, S[k])
            S["a0"] = _stats(t, S["a"], names)
            S["j0"] = _stats(t, S["j"], names)
            _wear(t, S["a"], SUIT)
            _wear(t, S["j"], JUNKER)
            S["a1"] = _stats(t, S["a"], names)
            S["j1"] = _stats(t, S["j"], names)
            _note(t, "suit stats before/after", {"suit": [S["a0"], S["a1"]], "junker": [S["j0"], S["j1"]]})

    def delta(k, stat):
        return float(S[k + "1"][stat]) - float(S[k + "0"][stat])

    with t.component("thermal_cover"):
        if _live(t):
            hot, cold = delta("a", "ComfyTemperatureMax"), delta("a", "ComfyTemperatureMin")
            # Insulation_Heat 100 / Insulation_Cold 140 on the def; 80%/ >=110 allows quality+condition scaling
            if hot < 80 or cold > -110:
                _fail("suit moved comfy max by %+.1f (want >= +80) and comfy min by %+.1f (want <= -110)" % (hot, cold))

    with t.component("vacuum_cover"):
        if _live(t) and S["a1"]["VacuumResistance"] < 0.8:
            _fail("VacuumResistance on the wearer is %.2f (suit declares +0.85, was %.2f naked)"
                  % (S["a1"]["VacuumResistance"], S["a0"]["VacuumResistance"]))

    with t.component("toxin_cover"):
        # SUSPECTED MOD DEFECT: ToxicEnvironmentResistance is in the suit's statBases, vanilla puts it
        # in equippedStatOffsets. A red here is a MOD finding, not a harness one.
        if _live(t) and S["a1"]["ToxicEnvironmentResistance"] < 0.85:
            _fail("ToxicEnvironmentResistance on the wearer is %.2f (naked %.2f); the suit declares 0.9 in "
                  "statBases, which the pawn stat does not read -- vanilla gas masks use equippedStatOffsets"
                  % (S["a1"]["ToxicEnvironmentResistance"], S["a0"]["ToxicEnvironmentResistance"]))

    with t.component("slow_and_bulky"):
        if _live(t):
            mv, wk = delta("a", "MoveSpeed"), delta("a", "WorkSpeedGlobal")
            if mv > -1.0 or wk > -0.2:
                _fail("MoveSpeed moved %+.2f (declared -1.8, want <= -1.0), WorkSpeedGlobal %+.2f (declared -0.25, "
                      "want <= -0.2)" % (mv, wk))

    with t.component("terrain_protection_stat"):
        r = t.bridge_call("jawa/thing_stats", pawn=S.get("a"), slot="apparel", defFilter=SUIT,
                          stats="RM_HazardousTerrainProtection")
        if _live(t):
            _ok(r, "thing_stats")
            val = None
            for th in r.get("things") or []:
                for s in th.get("stats") or []:
                    if s.get("defName") == "RM_HazardousTerrainProtection":
                        val = s.get("value")
            if r.get("refused") or val is None or abs(float(val) - 0.9) > 0.05:
                _fail("worn suit reads RM_HazardousTerrainProtection %r (declared 0.9 at Normal quality); refused=%s"
                      % (val, r.get("refused")))

    with t.component("junker_variant_is_still_a_suit"):
        if _live(t):
            hot, cold = delta("j", "ComfyTemperatureMax"), delta("j", "ComfyTemperatureMin")
            vac = S["j1"]["VacuumResistance"]
            if hot < 80 or cold > -110 or vac < 0.8:
                _fail("RM_WarcasketJunker did not inherit the suit's cover: heat %+.1f cold %+.1f vacuum %.2f"
                      % (hot, cold, vac))


# ------------------------------------------------------------------------------- chain 3: compound failure

def _build_room(t, rect, pollute):
    """A sealed 13x13 steel room on Soil; heated to HEAT_C; interior polluted when `pollute`."""
    r = t.bridge_call("jawa/make_empty_room", rect=_rs(rect), stuffDef="Steel", floorDef="Soil")
    if _live(t):
        _ok(r, "make_empty_room")
    ix, iz = rect[0] + 1, rect[1] + 1
    if pollute:
        p = t.bridge_call("jawa/set_pollution", rect=_rs((ix, iz, ROOM - 2, ROOM - 2)), polluted=True)
        if _live(t):
            _ok(p, "set_pollution")
            if not p.get("cellsEverPollutable"):
                _fail("UNMEASURED: no cell of the room is pollutable (Soil rejected?): %s" % str(p)[:200])
    t.bridge_call("jawa/room_heat", x=ix + 5, z=iz + 5, mode="set", value=HEAT_C)
    return ix, iz


def _fill_room(t, ix, iz):
    """20 drafted colonists in the suit, on a 5x4 lattice of the 11x11 interior."""
    ids = []
    for i in range(N_PER_ROOM):
        pid = _spawn(t, ix + 1 + (i % 5) * 2, iz + 1 + (i // 5) * 2)
        if _live(t):
            _settle(t, pid)
            _wear(t, pid, SUIT)
            ids.append(pid)
    return ids


def _expose(t, rooms, ticks, step=500):
    """Hold each room at HEAT_C (it is re-set every `step`: the door and wall conduction drag it down)."""
    done = 0
    while done < ticks:
        for ix, iz in rooms:
            t.bridge_call("jawa/room_heat", x=ix + 5, z=iz + 5, mode="set", value=HEAT_C)
        t.wait_ticks(step)
        done += step


def _arm(t, rect_a, ids_a):
    """(alive, failed-count, breach severities) over room A's pawns."""
    rows = [r for r in _pawn_rows(t, _rs(rect_a)) if r.get("id") in set(ids_a)]
    alive = [r for r in rows if not r.get("dead")]
    sev = [_hediff(r, BREACH) for r in alive]
    return rows, alive, [s for s in sev if s > 0.0]


@suite.chain("compound_failure")
def compound_failure(t):
    x, z = t.anchor
    A = (x - 34, z - 7, ROOM, ROOM)         # heat + polluted ground  = TWO hazards
    B = (x + 12, z - 7, ROOM, ROOM)         # heat only               = ONE hazard (control)
    S = {"ids_a": [], "ids_b": []}
    try:
        with t.component("site_ready_compound"):
            _prep_site(t, 100)
            ax, az = _build_room(t, A, pollute=True)
            bx, bz = _build_room(t, B, pollute=False)
            S["ia"], S["ib"] = (ax, az), (bx, bz)
            S["ids_a"] = _fill_room(t, ax, az)
            S["ids_b"] = _fill_room(t, bx, bz)
            if _live(t):
                for nm, (cx, cz) in (("A", (ax + 5, az + 5)), ("B", (bx + 5, bz + 5))):
                    tmp = _ok(t.bridge_call("jawa/cell_temperature", cell="%d,%d" % (cx, cz)), "cell_temperature")
                    if float(tmp.get("temperature")) < 70.0:
                        _fail("room %s is at %.1f C, the suit's extreme-heat threshold is 70: the heat hazard is "
                              "not active" % (nm, float(tmp.get("temperature"))))
                for nm, ids in (("A", S["ids_a"]), ("B", S["ids_b"])):
                    if len(ids) != N_PER_ROOM:
                        _fail("room %s holds %d wearers, want %d" % (nm, len(ids), N_PER_ROOM))

        with t.component("exposure_on"):
            _expose(t, [S.get("ia", (0, 0)), S.get("ib", (0, 0))], 6000)
            if _live(t):
                rows_a, alive_a, fail_a = _arm(t, A, S["ids_a"])
                rows_b, alive_b, fail_b = _arm(t, B, S["ids_b"])
                S["on"] = {"alive_a": len(alive_a), "failed_a": len(fail_a), "alive_b": len(alive_b),
                           "failed_b": len(fail_b), "sev_a": [round(s, 3) for s in fail_a]}
                _note(t, "compound exposure, shipped settings, 6000 ticks", S["on"])
                if len(alive_a) < 15 or len(alive_b) < 15:
                    _fail("UNMEASURED: too many wearers died/left (A %d, B %d of %d) for the failure count to mean "
                          "anything" % (len(alive_a), len(alive_b), N_PER_ROOM))

        with t.component("compound_failure_fires"):
            if _live(t) and not S["on"]["failed_a"]:
                _fail("0 of %d wearers suffered a breach in 6000 ticks under TWO hazards (heat %.0f C + polluted "
                      "ground); expected ~7. The compound-failure roll never fired." % (S["on"]["alive_a"], HEAT_C))

        with t.component("single_hazard_never_fails"):
            if _live(t) and S["on"]["failed_b"]:
                _fail("%d of %d wearers breached under ONE hazard (heat only); the suit must shrug a single "
                      "threat off" % (S["on"]["failed_b"], S["on"]["alive_b"]))

        for comp_name, field, ticks in (("compound_failure_off", "compoundFailureEnabled", 4000),
                                        ("master_off", "masterEnabled", 4000)):
            with t.component(comp_name, toggle=field):
                if _live(t):
                    # clear the ON arm's breaches so only NEW ones count, then switch the setting off
                    for r in _pawn_rows(t, _rs(A)):
                        if _hediff(r, BREACH) > 0.0 and r.get("id") in set(S["ids_a"]):
                            t.bridge_call("jawa/pawn_health", pawn=r["id"], action="remove", hediff=BREACH)
                    left = [r for r in _pawn_rows(t, _rs(A)) if _hediff(r, BREACH) > 0.0]
                    if left:
                        _fail("could not clear the baseline breaches (%d left)" % len(left))
                    t.set_setting(SETTINGS, {field: False})
                _expose(t, [S.get("ia", (0, 0))], ticks)
                if _live(t):
                    _, alive_a, fail_a = _arm(t, A, S["ids_a"])
                    _note(t, "%s=False, %d ticks" % (field, ticks), {"alive": len(alive_a), "failed": len(fail_a)})
                    if len(alive_a) < 15:
                        _fail("UNMEASURED: only %d of %d wearers still alive" % (len(alive_a), N_PER_ROOM))
                    if fail_a:
                        _fail("%d breach(es) with %s OFF under two hazards; the suit must never fail when the "
                              "setting is off" % (len(fail_a), field))
                    t.set_setting(SETTINGS, {field: True})
    finally:
        _restore(t)


# ------------------------------------------------------------------------------- chain 4: terrain immersion

@suite.chain("terrain_immersion")
def terrain_immersion(t):
    """Four pawns on their own 3x3 pads: naked on DEEP water (non-walkable), warcasket on DEEP water,
    naked on a shallow FORD (walkable), and -- after each toggle is switched off -- a fresh naked pawn on
    deep water. The hazard accrues at +0.12 x max(0.05, 1 - protection) per 250 ticks."""
    x, z = t.anchor
    P = {"naked": (x - 12, z), "suit": (x - 4, z), "ford": (x + 4, z), "tog": (x + 12, z), "mst": (x + 20, z)}
    S = {}

    def pad(name, terrain):
        cx, cz = P[name]
        t.bridge_call("jawa/set_terrain_batch", ops="%s:%d,%d,3,3" % (terrain, cx - 1, cz - 1))

    def read_sev(pid, rect):
        for r in _pawn_rows(t, rect):
            if r.get("id") == pid:
                return _hediff(r, IMMERSION), bool(r.get("dead"))
        _fail("pawn %s not found in %s" % (pid, rect))

    full = "%d,%d,50,16" % (x - 16, z - 8)
    try:
        with t.component("site_ready_immersion"):
            _prep_site(t, 70)
            for nm in P:
                S[nm] = _spawn(t, *P[nm])
            if _live(t):
                for nm in P:
                    _settle(t, S[nm])
                _wear(t, S["suit"], SUIT)
            for nm, ter in (("naked", "WaterDeep"), ("suit", "WaterDeep"), ("ford", "WaterShallow"),
                            ("tog", "WaterDeep"), ("mst", "WaterDeep")):
                pad(nm, ter)
            if _live(t):
                g = _ok(t.bridge_call("jawa/get_terrain_batch", rects="%d,%d,3,3" % (P["naked"][0] - 1, P["naked"][1] - 1)),
                        "get_terrain_batch")
                if "WaterDeep" not in str(g.get("ops")) or g.get("cellsRead") != g.get("cellsRequested"):
                    _fail("deep-water pad did not take: %s" % str(g)[:200])

        # `tog` / `mst` also stand on deep water from the start; their arms below use the DELTA across the toggle
        with t.component("unprotected_on_deep_water_accrues"):
            t.wait_ticks(1000)
            if _live(t):
                sev, dead = read_sev(S["naked"], full)
                S["naked_sev"] = sev
                if dead:
                    _fail("UNMEASURED: the naked pawn died")
                if sev < 0.3:
                    _fail("naked pawn on deep water has %s severity %.3f after 1000 ticks (expected ~0.48 = 4 checks "
                          "x 0.12)" % (IMMERSION, sev))

        with t.component("protected_wearer_barely_accrues"):
            if _live(t):
                sev, dead = read_sev(S["suit"], full)
                naked = S.get("naked_sev", 0.0)
                _note(t, "immersion severities", {"naked": naked, "suit": sev})
                if dead:
                    _fail("UNMEASURED: the suited pawn died")
                if sev > 0.35 * naked:
                    _fail("suited pawn severity %.3f is not well below the naked pawn's %.3f (protection 0.9 should "
                          "cut the clock to ~10%%)" % (sev, naked))

        with t.component("ford_is_safe"):
            if _live(t):
                sev, _ = read_sev(S["ford"], full)
                if sev > 0.0:
                    _fail("a pawn on WALKABLE shallow water (a ford) carries %s severity %.3f; only water nothing can "
                          "walk across is the hazard" % (IMMERSION, sev))

        # the toggle arms: tog/mst were on deep water the whole time but their arm has not "run" yet --
        # so first read their severity (it accrued under the ON setting) and use the DELTA from here on.
        for comp_name, field, pid_key in (("terrain_immersion_off", "terrainImmersionEnabled", "tog"),
                                          ("master_off_terrain", "masterEnabled", "mst")):
            with t.component(comp_name, toggle=field):
                if _live(t):
                    before, _ = read_sev(S[pid_key], full)
                    t.set_setting(SETTINGS, {field: False})
                t.wait_ticks(1000)
                if _live(t):
                    after, _ = read_sev(S[pid_key], full)
                    _note(t, "%s=False delta" % field, {"before": before, "after": after})
                    if after > before + 0.01:
                        _fail("severity rose %.3f -> %.3f while %s was OFF" % (before, after, field))
                    t.set_setting(SETTINGS, {field: True})
    finally:
        _restore(t)


# ------------------------------------------------------------------------------- chain 5: sarcophagus

@suite.chain("sarcophagus")
def sarcophagus(t):
    """Junker wearer dies; a second colonist cracks the corpse open (the same RM_CrackSarcophagus job the
    float-menu option orders): suit + welded tooling + RM_HalfExtractedCore appear. Control: an ordinary
    RM_Warcasket corpse yields nothing."""
    x, z = t.anchor
    J, C1 = (x - 10, z), (x - 10, z + 3)         # sealed Junker corpse + its cracker
    N, C2 = (x + 10, z), (x + 10, z + 3)         # control: ordinary suit corpse + its cracker
    rj, rn = "%d,%d,12,12" % (x - 16, z - 6), "%d,%d,12,12" % (x + 4, z - 6)
    S = {}
    try:
        with t.component("site_ready_sarcophagus"):
            _prep_site(t, 60)
            S["jw"], S["c1"] = _spawn(t, *J), _spawn(t, *C1)
            S["nw"], S["c2"] = _spawn(t, *N), _spawn(t, *C2)
            if _live(t):
                for k in ("jw", "c1", "nw", "c2"):
                    _settle(t, S[k], draft=False)
                _wear(t, S["jw"], JUNKER)
                _wear(t, S["nw"], SUIT)
                for k in ("jw", "nw"):
                    d = _ok(t.bridge_call("jawa/pawn_force_incapacitate", pawn=S[k], action="kill"), "kill")
                    if not d.get("deadAfter"):
                        _fail("pawn %s did not die: %s" % (S[k], str(d)[:160]))
                for k, rect in (("jc", rj), ("nc", rn)):
                    r = _ok(t.bridge_call("jawa/list_things", group="Corpse", rect=rect, limit=20), "list corpses")
                    if len(r.get("things") or []) != 1:
                        _fail("expected exactly one corpse in %s, found %s" % (rect, len(r.get("things") or [])))
                    S[k] = r["things"][0]["id"]

        with t.component("crack_open_yields_salvage", toggle="sarcophagiEnabled"):
            if _live(t):
                before = _count_things(t, rj, "%s,%s,%s,Steel,ComponentIndustrial" % (JUNKER, CORE, SUIT))
                if before.get(CORE) or before.get(JUNKER):
                    _fail("salvage already present before the crack: %s" % before)
                r = t.bridge_call("jawa/ordered_job", pawnId=S["c1"], jobDef="RM_CrackSarcophagus",
                                  targetAId=S["jc"], waitTicks=0, timeoutSeconds=60)
                if not (r or {}).get("accepted"):
                    _fail("jawa/ordered_job RM_CrackSarcophagus not accepted: %s" % str(r)[:200])
            t.wait_ticks(2200)         # walk + crackOpenTicks 1200
            if _live(t):
                after = _count_things(t, rj, "%s,%s,%s,Steel,ComponentIndustrial" % (JUNKER, CORE, SUIT))
                _note(t, "salvage after crack", after)
                if after.get(CORE, 0) < 1 or after.get(JUNKER, 0) < 1:
                    _fail("cracking the sealed Junker corpse left suit=%s core=%s on the ground (want both >= 1): %s"
                          % (after.get(JUNKER), after.get(CORE), after))
                if after.get("Steel", 0) < 25 or after.get("ComponentIndustrial", 0) < 2:
                    _fail("welded tooling missing: Steel %s (want 25) / ComponentIndustrial %s (want 2)"
                          % (after.get("Steel"), after.get("ComponentIndustrial")))

        with t.component("plain_suit_corpse_yields_nothing"):
            # CONTROL for the component above: the same job aimed at an ordinary warcasket corpse must do nothing.
            if _live(t):
                t.bridge_call("jawa/ordered_job", pawnId=S["c2"], jobDef="RM_CrackSarcophagus",
                              targetAId=S["nc"], waitTicks=0, timeoutSeconds=60)
            t.wait_ticks(1600)
            if _live(t):
                got = _count_things(t, rn, "%s,%s,%s,ComponentIndustrial" % (JUNKER, CORE, SUIT))
                if got.get(CORE) or got.get(JUNKER):
                    _fail("an ordinary RM_Warcasket corpse was cracked open like a Junker sarcophagus: %s" % got)

        with t.component("sarcophagi_setting_flips"):
            # Write + read-back only. The seal state of a corpse's suit has no bridge reader (UNCOVERED in the walk).
            t.set_setting(SETTINGS, {"sarcophagiEnabled": False})
            t.set_setting(SETTINGS, {"sarcophagiEnabled": True})
    finally:
        _restore(t)


# ------------------------------------------------------------------------------- chain 6: cask bay + core dose

@suite.chain("core_and_cask_bay")
def core_and_cask_bay(t):
    """A loose half-extracted core doses what stands within 4 cells; a core ON a cask-bay cell does not;
    a warcasket wearer is dosed far less. Both comps print their state in the inspect pane, which is the
    cheap deterministic read for the two toggles."""
    x, z = t.anchor
    LOOSE, SHIELD = (x - 12, z), (x + 8, z)        # core cells; the bay is 2x2 starting at SHIELD
    S = {}
    full = "%d,%d,40,14" % (x - 18, z - 7)
    try:
        with t.component("site_ready_core"):
            _prep_site(t, 60)
            t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d;%s:%d,%d;%s:%d,%d" % (
                CORE, LOOSE[0], LOOSE[1], BAY, SHIELD[0], SHIELD[1], CORE, SHIELD[0], SHIELD[1]))
            S["n"] = _spawn(t, LOOSE[0] + 2, LOOSE[1])             # naked, 2 cells from the loose core
            S["w"] = _spawn(t, LOOSE[0], LOOSE[1] + 2)             # suited, 2 cells from the loose core
            S["far"] = _spawn(t, LOOSE[0] - 12, LOOSE[1])          # naked, far outside the 4-cell radius
            S["sh"] = _spawn(t, SHIELD[0] + 3, SHIELD[1])          # naked, beside the SHIELDED core
            if _live(t):
                for k in ("n", "w", "far", "sh"):
                    _settle(t, S[k])
                _wear(t, S["w"], SUIT)
                got = _count_things(t, full, "%s,%s" % (CORE, BAY))
                if got.get(CORE) != 2 or got.get(BAY) != 1:
                    _fail("fixture did not place 2 cores + 1 bay: %s" % got)

        with t.component("inspect_reports_shielding"):
            if _live(t):
                core_lines = " || ".join(_inspect(t, CORE, full))
                bay_lines = " || ".join(_inspect(t, BAY, full))
                if "Unshielded" not in core_lines or "Shielded in a cask bay" not in core_lines:
                    _fail("core inspect strings should show one Unshielded and one Shielded core: %s" % core_lines)
                if "Lead-lined" not in bay_lines:
                    _fail("cask bay inspect string missing its shielding line: %s" % bay_lines)

        with t.component("cask_bay_storage_filter"):
            r = t.bridge_call("jawa/list_things", defName=BAY, rect=full, limit=5)
            if _live(t):
                bid = ((_ok(r, "list bay").get("things") or [{}])[0]).get("id")
                s = _ok(t.bridge_call("jawa/storage_settings", target=bid), "storage_settings(read)")
                sample = set((a.get("defName") if isinstance(a, dict) else a) for a in (s.get("allowedSample") or []))
                n = s.get("allowedCountAfter", s.get("allowedCountBefore"))
                if not {"Wastepack", CORE} <= sample or "Steel" in sample or (n is not None and int(n) > 12):
                    _fail("cask bay filter should admit Wastepack + the core only (cask cargo): count=%s sample=%s"
                          % (n, sorted(sample)[:20]))

        with t.component("loose_core_doses_nearby"):
            t.wait_ticks(2500)          # a dose every 4 rare ticks = 1000 ticks
            if _live(t):
                rows = dict((r.get("id"), r) for r in _pawn_rows(t, full))
                sev = dict((k, _hediff(rows[S[k]], "ToxicBuildup")) for k in ("n", "w", "far", "sh"))
                S["sev"] = sev
                _note(t, "ToxicBuildup after 2500 ticks", sev)
                if sev["n"] <= 0.0:
                    _fail("naked pawn 2 cells from a loose core has no ToxicBuildup after 2500 ticks: %s" % sev)
                if sev["far"] > 0.0:
                    _fail("a pawn 12+ cells from any core has ToxicBuildup %.3f (control must be clean)" % sev["far"])

        with t.component("cask_bay_silences_core"):
            if _live(t) and S["sev"]["sh"] > 0.0:
                _fail("pawn beside the SHIELDED core has ToxicBuildup %.3f; a core on a cask-bay cell must not dose"
                      % S["sev"]["sh"])

        with t.component("warcasket_wearer_resists_core_dose"):
            # Depends on `toxin_cover` (suspected defect: statBases vs equippedStatOffsets).
            if _live(t) and S["sev"]["w"] > 0.35 * S["sev"]["n"]:
                _fail("suited pawn took ToxicBuildup %.3f vs naked %.3f; the suit's toxin rating (0.9) should cut it "
                      "to ~10%%" % (S["sev"]["w"], S["sev"]["n"]))

        with t.component("core_dose_off", toggle="coreDoseEnabled"):
            if _live(t):
                t.set_setting(SETTINGS, {"coreDoseEnabled": False})
                S["n2"] = _spawn(t, LOOSE[0] + 2, LOOSE[1] + 1)
                _settle(t, S["n2"])
            t.wait_ticks(2500)
            if _live(t):
                rows = dict((r.get("id"), r) for r in _pawn_rows(t, full))
                sev = _hediff(rows[S["n2"]], "ToxicBuildup")
                if sev > 0.0:
                    _fail("fresh naked pawn beside the loose core took ToxicBuildup %.3f with coreDoseEnabled OFF" % sev)
                t.set_setting(SETTINGS, {"coreDoseEnabled": True})

        with t.component("cask_bay_shielding_off", toggle="caskBayShieldingEnabled"):
            if _live(t):
                t.set_setting(SETTINGS, {"caskBayShieldingEnabled": False})
                core_lines = " || ".join(_inspect(t, CORE, full))
                bay_lines = " || ".join(_inspect(t, BAY, full))
                if "Shielded in a cask bay" in core_lines:
                    _fail("a core still reads as shielded with caskBayShieldingEnabled OFF: %s" % core_lines)
                if "Shielding disabled" not in bay_lines:
                    _fail("cask bay did not report 'Shielding disabled in Mod Settings' with the setting OFF: %s" % bay_lines)
                t.set_setting(SETTINGS, {"caskBayShieldingEnabled": True})

        with t.component("master_off_core", toggle="masterEnabled"):
            if _live(t):
                t.set_setting(SETTINGS, {"masterEnabled": False})
                S["n3"] = _spawn(t, LOOSE[0] + 1, LOOSE[1] - 2)
                _settle(t, S["n3"])
            t.wait_ticks(2500)
            if _live(t):
                rows = dict((r.get("id"), r) for r in _pawn_rows(t, full))
                sev = _hediff(rows[S["n3"]], "ToxicBuildup")
                if sev > 0.0:
                    _fail("fresh naked pawn took ToxicBuildup %.3f with masterEnabled OFF" % sev)
                t.set_setting(SETTINGS, {"masterEnabled": True})
    finally:
        _restore(t)


# ------------------------------------------------------------------------------- chain 7: settings round trip

_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def settings_fields():
    """{name: type} for every scalar `public static` field of RM_WarcasketSettings, read from the C#."""
    src = open(os.path.join(HERE, "Source", "RM_WarcasketSettings.cs"), encoding="utf-8").read()
    body = src.split("class RM_WarcasketSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def _sraw(t, action, field, value=None):
    kw = dict(typeName=SETTINGS, action=action, field=field)
    if value is not None:
        kw["value"] = str(value)
    r = t.session.call("jawa/mod_settings_field", **kw)
    return r if isinstance(r, dict) else {}


def _same(ty, a, b):
    if ty == "bool":
        return str(a).lower() == str(b).lower()
    return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))


@suite.chain("settings_roundtrip")
def settings_roundtrip(t):
    """Every `public static` field of the settings class (found by regex, sanity probe >= 1): write the
    opposite, read it back independently, restore, read the restore back."""
    with t.component("settings_probe_finds_fields", beyond_toggle=True):
        if len(settings_fields()) < 1:
            _fail("settings probe found no field (blind regex)")
        if sorted(settings_fields()) != sorted(suite.toggles):
            _fail("suite.toggles %s differs from the C# fields %s" % (sorted(suite.toggles), sorted(settings_fields())))
    for field, ty in sorted(settings_fields().items()):
        with t.component("%s_round_trips" % field, toggle=field):
            if not _live(t):
                continue
            old = _sraw(t, "get", field).get("value")
            if old is None:
                _fail("%s: get returned no value" % field)
            new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else str(float(old) + 1.0)
            try:
                if not _sraw(t, "set", field, new).get("success"):
                    _fail("%s: set failed" % field)
                back = _sraw(t, "get", field).get("value")
                if not _same(ty, back, new):
                    _fail("%s: wrote %s, read %r" % (field, new, back))
            finally:
                _sraw(t, "set", field, old)
            if not _same(ty, _sraw(t, "get", field).get("value"), old):
                _fail("%s did not restore to %r" % (field, old))


# ------------------------------------------------------------------------------- static (no game)

def static_checks():
    """Offline: Source files are in the csproj, every settings field is Scribed and has a control, the def
    XML parses and names every shipped def the live chains expect, and the walk exists."""
    import xml.etree.ElementTree as ET
    bad = []
    srcdir = os.path.join(HERE, "Source")
    fields = settings_fields()
    if len(fields) < 1:
        return ["settings probe found no scalar field (sanity probe failed)"]
    if sorted(fields) != sorted(suite.toggles):
        bad.append("suite.toggles differs from the C# settings fields")
    sset = open(os.path.join(srcdir, "RM_WarcasketSettings.cs"), encoding="utf-8").read()
    scribed = sset.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1] if "DoWindowContents" in scribed else ""
    scribed = scribed.split("DoWindowContents", 1)[0]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if ui and not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(srcdir, "RM_Warcasket.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(srcdir)):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj and "EnableDefaultCompileItems" in proj \
                and 'Compile Include="*.cs"' not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    names = set()
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in files:
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    if isinstance(el.tag, str) and el.findtext("defName"):
                        names.add(el.findtext("defName").strip())
    if len(names) < 5:
        bad.append("only %d defs parsed from Defs/ (sanity probe failed)" % len(names))
    for d in (SUIT, JUNKER, BAY, CORE, BREACH, IMMERSION, "RM_HazardousTerrainProtection", "RM_CrackSarcophagus", "RM_HazardCasks"):
        if d not in names:
            bad.append("def %s named by defs_and_load is not in Defs/" % d)
    suit_xml = ""
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs", "ThingDefs_Apparel")):
        for fn in files:
            txt = open(os.path.join(dp, fn), encoding="utf-8").read()
            if "<defName>%s</defName>" % SUIT in txt:
                suit_xml = txt
    if not suit_xml:
        bad.append("could not find the %s def file (tickerType guard blind)" % SUIT)
    if suit_xml and "<tickerType>Rare</tickerType>" not in suit_xml:
        bad.append("RM_Warcasket lost its <tickerType>Rare</tickerType>: compound failure can never fire (guard of compound_failure_fires)")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "Warcasket.md")):
        bad.append("walk missing")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
