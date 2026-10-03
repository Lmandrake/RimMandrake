"""validation.py -- first script for Jawa Fall Line Arrivals (mandrake.rut.falllinearrivals).

FALL_LINE_ARRIVAL_MECHANISM_1, first pass (Band A wreck falls + Band C the lab rat). Walk:
design/validation_walks/RimUtinni/FallLineArrivals.md. Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run FallLineArrivals

Environment: minimal + every DLC + mandrake.rm.biomes (Ship Vermin's kit host) +
mandrake.rm.shipvermin + mandrake.rsw.swbestiary (the nest species) + this mod.

A quicktest map is NOT on the Fall Line, so the gate chain proves the gate (onlyOnFallLine ON ->
canFireNow false) and every other chain runs with onlyOnFallLine OFF. Whether the in-game
WorldFeature on the start tile is literally named "Fall Line"/"The Breaks" is UNMEASURED here
(first poke on the campaign save: fire_incident dryRun RUT_FallArrival with the setting ON).
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("FallLineArrivals")
suite.toggles = ["onlyOnFallLine", "wreckFallsEnabled", "wreckHull", "wreckCargo", "wreckTank",
                 "labRatEnabled", "survivorsEnabled", "allowDestroyer", "feralAttackInstead"]

SETTINGS_TYPE = "RimMandrake.Utinni.FallLineArrivals.FallLineArrivalsSettings"
WRECKS = ("RUT_FallWreck_Hull", "RUT_FallWreck_Cargo", "RUT_FallWreck_Tank")
VERMIN = ("RSW_Mynock", "RSW_Scavrat", "RSW_WompRat", "RSW_Zhakka")
NEEDLES = ("mandrake.rut.falllinearrivals", "RUT_FallWreck", "RUT_LabRat", "RUT_FallLine",
           "IncidentWorker_FallArrival", "IncidentWorker_LabRatFalls", "RM_CompVerminNest",
           "RUT_FallSurvivor", "RUT_Hediff_Feral", "FeralSurvivors", "JobGiver_Feral", "RUT_CompFeralLurker")
FERAL_POOL = ("RSW_DW_OuterRim_MSEDroid", "RSW_DW_OuterRim_SalvageAssistDroid", "RSW_DW_OuterRim_DUMDroid",
              "RSW_DW_OuterRim_GNKDroid", "RSW_DW_OuterRim_RSeriesDroid", "RSW_DW_OuterRim_FX7Droid",
              "RSW_DW_OuterRim_MuckrakerDroid", "RSW_DW_OuterRim_DestroyerDroid")


def _dry(t, incident):
    r = t.bridge_call("jawa/fire_incident", incidentDef=incident, dryRun=True)
    if t._guard() and not (r or {}).get("success"):
        raise ExpectationFailed("fire_incident dryRun %s failed: %r" % (incident, r))
    return (r or {}).get("canFireNow")


def _count(t, defName):
    r = t.bridge_call("jawa/list_things", defName=defName, limit=50)
    if not t._guard():
        return 0
    if not (r or {}).get("success") or "countMatched" not in r:
        raise ExpectationFailed("list_things(%s) unreadable: %r" % (defName, r))
    return r["countMatched"]


@suite.chain("load_clean")
def load_clean(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


@suite.chain("defs")
def defs(t):
    with t.component("all_defs_resolve", beyond_toggle=True):
        want = ["IncidentDef/RUT_FallArrival", "IncidentDef/RUT_LabRatFalls", "PawnKindDef/RUT_LabRat",
                "IncidentDef/RUT_FallSurvivor", "HediffDef/RUT_Hediff_Feral", "ThinkTreeDef/RUT_FeralDroidInsert",
                "TileMutatorDef/RUT_FallLine"] + ["ThingDef/%s" % w for w in WRECKS] + \
               ["ThingDef/%s" % w.replace("FallWreck_", "FallWreckIncoming_") for w in WRECKS]
        r = t.bridge_call("jawa/get_defs", defs=";".join(want), fields="defName")
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed("get_defs failed: %r" % r)
            if r.get("notFound"):
                raise ExpectationFailed("defs missing: %r" % r.get("notFound"))


@suite.chain("gate")
def gate(t):
    with t.component("off_fall_line_refused", toggle="onlyOnFallLine"):
        t.set_setting(SETTINGS_TYPE, {"onlyOnFallLine": True})
        if _dry(t, "RUT_FallArrival") is not False:
            raise ExpectationFailed("onlyOnFallLine ON on a quicktest (non-Fall-Line) map, but RUT_FallArrival "
                                    "can fire")
        if _dry(t, "RUT_LabRatFalls") is not False:
            raise ExpectationFailed("onlyOnFallLine ON on a quicktest map, but RUT_LabRatFalls can fire")
    with t.component("anywhere_allows", toggle="onlyOnFallLine"):
        t.set_setting(SETTINGS_TYPE, {"onlyOnFallLine": False})
        if _dry(t, "RUT_FallArrival") is not True:
            raise ExpectationFailed("onlyOnFallLine OFF but RUT_FallArrival cannot fire (no skyfaller cell?)")
    with t.component("wrecks_toggle_off_refuses", toggle="wreckFallsEnabled"):
        t.set_setting(SETTINGS_TYPE, {"wreckFallsEnabled": False})
        off = _dry(t, "RUT_FallArrival")
        t.set_setting(SETTINGS_TYPE, {"wreckFallsEnabled": True})
        if off is not False:
            raise ExpectationFailed("wreckFallsEnabled OFF but RUT_FallArrival can fire")


@suite.chain("wreck_falls_and_nests")
def wreck_falls_and_nests(t):
    t.set_setting(SETTINGS_TYPE, {"onlyOnFallLine": False})
    with t.component("wreck_lands", toggle="wreckFallsEnabled"):
        before = sum(_count(t, w) for w in WRECKS)
        r = t.bridge_call("jawa/fire_incident", incidentDef="RUT_FallArrival", dryRun=False)
        if t._guard() and not (r or {}).get("fired"):
            raise ExpectationFailed("RUT_FallArrival did not fire: %r" % r)
        t.wait_ticks(600)                                  # skyfaller ticksToImpact 240~360
        after = sum(_count(t, w) for w in WRECKS)
        if t._guard() and after <= before:
            raise ExpectationFailed("no wreck on the map after the fall (%d -> %d)" % (before, after))
    with t.component("vermin_burst_from_wreck", toggle="wreckFallsEnabled"):
        before = sum(_count(t, v) for v in VERMIN)
        t.wait_ticks(2600)                                 # initialBurstDelayTicks 600~2400
        after = sum(_count(t, v) for v in VERMIN)
        if t._guard() and after <= before:
            raise ExpectationFailed("no ship-vermin came out of the wreck within 2600 ticks (%d -> %d)"
                                    % (before, after))


@suite.chain("specimen")
def specimen(t):
    t.set_setting(SETTINGS_TYPE, {"onlyOnFallLine": False})
    with t.component("lab_rat_toggle_off_refuses", toggle="labRatEnabled"):
        t.set_setting(SETTINGS_TYPE, {"labRatEnabled": False})
        off = _dry(t, "RUT_LabRatFalls")
        t.set_setting(SETTINGS_TYPE, {"labRatEnabled": True})
        if off is not False:
            raise ExpectationFailed("labRatEnabled OFF but RUT_LabRatFalls can fire")
    with t.component("lab_rat_arrives_in_pod", toggle="labRatEnabled"):
        r = t.bridge_call("jawa/fire_incident", incidentDef="RUT_LabRatFalls", dryRun=False)
        if t._guard() and not (r or {}).get("fired"):
            raise ExpectationFailed("RUT_LabRatFalls did not fire: %r" % r)
        t.wait_ticks(600)                                  # pod open delay 180
        p = t.bridge_call("jawa/list_pawns", limit=500)
        if t._guard():
            rats = [x for x in ((p or {}).get("pawns") or []) if x.get("kindDef") == "RUT_LabRat"]
            if not rats:
                raise ExpectationFailed("no RUT_LabRat pawn on the map after the pod opened")


# FALL_LINE_FERAL_SURVIVORS_BUILD_1 (Band B). Environment adds mandrake.rsw.droidworks (the pool).
# Not yet proven here (first pokes, in order): a colonist walking at a survivor -> a Flee job toward a
# wreck (>= 5 droids, one pawn is RNG); boxed in -> AttackMelee; night -> Wait beside a wreck; an armed
# wreck (DEV gizmo) bolting one at 25 cells; recruitment by RSW_DW_DataSpike_Wild clearing the hediff.
@suite.chain("survivors")
def survivors(t):
    t.set_setting(SETTINGS_TYPE, {"onlyOnFallLine": False})
    with t.component("survivor_toggle_off_refuses", toggle="survivorsEnabled"):
        t.set_setting(SETTINGS_TYPE, {"survivorsEnabled": False})
        off = _dry(t, "RUT_FallSurvivor")
        t.set_setting(SETTINGS_TYPE, {"survivorsEnabled": True})
        if off is not False:
            raise ExpectationFailed("survivorsEnabled OFF but RUT_FallSurvivor can fire")
    with t.component("survivor_drifts_in_feral", toggle="survivorsEnabled"):
        r = t.bridge_call("jawa/fire_incident", incidentDef="RUT_FallSurvivor", dryRun=False)
        if t._guard() and not (r or {}).get("fired"):
            raise ExpectationFailed("RUT_FallSurvivor did not fire (Droidworks loaded? pool empty?): %r" % r)
        t.wait_ticks(120)
        p = t.bridge_call("jawa/list_pawns", limit=500, includeHealth=True)
        if t._guard():
            rows = [x for x in ((p or {}).get("pawns") or []) if x.get("kindDef") in FERAL_POOL]
            feral = [x for x in rows if not x.get("faction") and any(
                h.get("def") == "RUT_Hediff_Feral" for h in ((x.get("health") or {}).get("hediffs") or []))]
            if not feral:
                raise ExpectationFailed("no factionless pool droid carrying RUT_Hediff_Feral after the drift-in: %r"
                                        % [(x.get("kindDef"), x.get("faction")) for x in rows][:5])
