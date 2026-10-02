"""modcheck.selftest_suite_corrections -- offline proof of MODCHECK_SUITE_CORRECTIONS_1's suite fixes.

Each case runs the REAL corrected chain from the mod's own validation.py against a scripted bridge that
replays the reply SHAPES measured in the 2026-10-01 live pass (Transient/modcheck/*_situational_summary.json),
and checks both directions: the corrected suite PASSES a mod that behaves as measured, and still FAILS a mod
that genuinely does not (a correction that can no longer fail is a weakened test, not a fixed one).

No socket, no game.   python3 src/RimMandrake/Utils/modcheck/selftest_suite_corrections.py
Picked up automatically by run_selftests.py.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_HERE, _UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner  # noqa: E402
from suite import TestContext, PASS, FAIL  # noqa: E402
from rimdrive.session import Session  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s  %s" % (name, detail))
        FAILURES.append(name)


def _session(handler):
    s = Session.__new__(Session)
    s.strict = True
    s.quiet = True
    s.calls = 0
    s.mutations = 0
    s.no_ops = []
    s.unverified = []
    s.litter = []
    s.call = handler
    return s


class FakeWatch(object):
    """Just enough of watch.Watch for a chain that declares expectations."""

    class _Exps(object):
        def __init__(self):
            self.phase = None

        def set_phase(self, name):
            self.phase = name

    def __init__(self):
        self.declared = []
        self.exps = FakeWatch._Exps()

    def expect(self, kind, matcher, until_tick=None, phase=None):
        self.declared.append((kind, matcher, phase))

    def expect_fixture(self, pid, name=None):
        pass

    def charge_verb(self, label):
        pass

    def wait(self, ctx, n):
        return {"success": True, "advanced": n, "requested": n}


def run_chain(mod, chain, handler, watch=None, waits=None):
    suite = runner.load_validation(runner.find_mod_dir(mod))
    fn = dict(suite.chains)[chain]
    def wrapped(tool, **p):
        if tool == "rimworld/get_cell_info":          # TestContext.spawn checks the cell after a batch
            return {"success": True, "cell": {"things": []}}
        return handler(tool, **p)
    t = TestContext(_session(wrapped), anchor=(100, 100), watch=watch)
    t.screenshot = lambda *a, **k: None       # the real verb falls back to an OS screenshot with no game
    if waits is not None:
        t.wait_ticks = lambda n, **k: waits.append(n)
    fn(t)
    return dict((c.name, c.verdict) for c in t.components), dict((c.name, c.detail) for c in t.components)


def _pawn_spawn(ids):
    it = iter(ids)

    def spawn(**p):
        return {"success": True, "pawns": [{"id": next(it), "name": "N"}]}
    return spawn


# ------------------------------------------------------------------ JawaIonWeapons
def _ion_handler(shield_works=True, exponent=2.0):
    """Pawns: Pirate (bodySize 1.0) and Rat (0.2). Severity = 0.03*dmg/bodySize^exponent, clamped to 1.0.
    jawa/damage reports hitPoints -1 for every pawn (MEASURED); a worn shield absorbs ONE Bullet then pops
    when an ion hit lands (if shield_works)."""
    st = {"sev": {}, "belt": True, "hed": {}}
    bodies = {"Pirate1": 1.0, "Rat1": 0.2}

    def h(tool, **p):
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": "Rat1" if p["kindDef"] == "Rat" else "Pirate1"}]}
        if tool == "jawa/damage":
            tid, dd, amt = p["thingId"], p["damageDef"], p["amount"]
            row = {"id": tid, "isPawn": True, "hitPointsBefore": -1, "hitPointsAfter": -1, "dead": False,
                   "totalDamageDealt": 0.0, "hediffsBefore": st["hed"].get(tid, 0),
                   "hediffsAfter": st["hed"].get(tid, 0), "stunTicksLeft": 0}
            if dd == "RSW_JawaIon_Damage":
                bs = bodies[tid]
                st["sev"][tid] = min(1.0, st["sev"].get(tid, 0.0) + 0.03 * amt / (bs ** exponent))
                if shield_works:
                    st["belt"] = False
                st["hed"][tid] = st["hed"].get(tid, 0) + (0 if st["hed"].get(tid) else 1)
                row["hediffsAfter"] = st["hed"][tid]
            elif dd == "Bullet":
                if st["belt"]:
                    pass                                          # absorbed
                else:
                    row["totalDamageDealt"] = 5.625
                    st["hed"][tid] = st["hed"].get(tid, 0) + 1
                    row["hediffsAfter"] = st["hed"][tid]
            return {"success": True, "targets": [row], "results": [row]}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [
                {"id": k, "bodySize": bodies[k],
                 "health": {"hediffs": ([{"def": "RSW_JawaIon_Stun", "severity": v}] if v else [])}}
                for k, v in st["sev"].items()]}
        if tool == "jawa/thing_stats":
            return {"success": True, "things": [{"stats": [
                {"defName": "RSW_Jawa_InverseBodySize", "value": 1.0 / bodies["Pirate1"]}]}]}
        return {"success": True}
    return h


def t_jawaion():
    v, d = run_chain("JawaIonWeapons", "shield_break", _ion_handler(shield_works=True))
    check("JawaIon shield: absorbed control + landed proof (MEASURED reply shape) -> PASS",
          v.get("ion_pops_shield_then_bullet_lands") == PASS, (v, d))
    v, d = run_chain("JawaIonWeapons", "shield_break", _ion_handler(shield_works=False))
    check("JawaIon shield: a belt the ion hit does NOT pop still FAILS",
          v.get("ion_pops_shield_then_bullet_lands") == FAIL, (v, d))

    v, d = run_chain("JawaIonWeapons", "buildup_math", _ion_handler(exponent=2.0))
    check("JawaIon bodySize^2: rat clamped by an 8-point hit no longer hides a squared curve -> PASS",
          v.get("bodysize_squared_resistance") == PASS, (v, d))
    check("JawaIon bodySize^2: the downstream stat component is measured again",
          v.get("thirdparty_stat_matches_formula") == PASS, (v, d))
    v, d = run_chain("JawaIonWeapons", "buildup_math", _ion_handler(exponent=1.0))
    check("JawaIon bodySize^2: a LINEAR resistance curve still FAILS",
          v.get("bodysize_squared_resistance") == FAIL, (v, d))


# ------------------------------------------------------------------ ShipMemory
def _ship_handler(zone_counts):
    st = {"zones": [], "letter": False}

    def h(tool, **p):
        if tool == "jawa/map_zones":
            if p.get("action") == "createZone":
                st["zones"].append({"label": "Stockpile 1", "type": "Zone_Stockpile", "cells": 1})
            elif p.get("action") == "deleteZone":
                st["zones"] = []
            return {"success": True, "zones": list(st["zones"])}
        if tool == "jawa/letter_list":
            made = bool(st["zones"]) if zone_counts else False
            return {"success": True, "letters": ([{"label": "She remembers the chains"}] if made else [])}
        return {"success": True}
    return h, st


def t_shipmemory():
    h, st = _ship_handler(zone_counts=True)
    v, d = run_chain("ShipMemory", "bioferrite_stockpile_reveal", h)
    check("ShipMemory: a stockpile zone is created before the Bioferrite lands -> reveal measured",
          v.get("reveals_on_stockpile") == PASS, (v, d))
    check("ShipMemory: the zone is removed afterwards", st["zones"] == [], st)
    h, st = _ship_handler(zone_counts=False)
    v, d = run_chain("ShipMemory", "bioferrite_stockpile_reveal", h)
    check("ShipMemory: no letter even with the stockpile still FAILS (and cleans up)",
          v.get("reveals_on_stockpile") == FAIL and st["zones"] == [], (v, st))


# ------------------------------------------------------------------ Droidworks
def _bolt_handler(removes_at_zero=True):
    st = {"hed": {}}

    def h(tool, **p):
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": "Col%d" % (len(st) + 1), "name": "C"}]}
        if tool == "jawa/pawn_health":
            if p["action"] == "add":
                sev = p.get("severity", 0.5)
                if not (removes_at_zero and sev <= 0):
                    st["hed"][p["hediff"]] = sev
            return {"success": True}
        if tool == "wait":
            return {"success": True}
        if tool == "jawa/pawn_get":
            return {"success": True, "pawns": [{"hediffs": [{"def": k, "severity": v}
                                                           for k, v in st["hed"].items()]}]}
        if tool == "rimworld/step_game_ticks":
            if "RSW_DW_BoltResentment" in st["hed"]:
                st["hed"]["RSW_DW_BoltResentment"] += 0.001
            return {"success": True}
        return {"success": True}
    return h


def t_droidworks_bolt():
    v, d = run_chain("Droidworks", "bolt_core", _bolt_handler())
    check("Droidworks resentment: seeded above zero it survives and rises -> PASS",
          v.get("resentment_accrues") == PASS, (v, d))
    # the engine removes a hediff at severity <= 0; if the suite seeded 0 again the row would be gone
    h = _bolt_handler()
    base = h

    def zero_seed(tool, **p):
        if tool == "jawa/pawn_health" and p.get("hediff") == "RSW_DW_BoltResentment":
            p = dict(p, severity=0.0)
        return base(tool, **p)
    v, d = run_chain("Droidworks", "bolt_core", zero_seed)
    check("Droidworks resentment: a zero-seeded (engine-removed) hediff reads as no accrual -> FAIL",
          v.get("resentment_accrues") == FAIL, (v, d))


def t_droidworks_quirk_and_prices():
    hed = {}

    def quirk(tool, **p):
        if tool == "jawa/pawn_health":
            hed[p["hediff"]] = p.get("severity", 0.5)
        if tool == "jawa/pawn_get":
            return {"success": True, "pawns": [{"hediffs": [{"def": k, "severity": v} for k, v in hed.items()]}]}
        if tool == "jawa/get_defs":
            return {"success": True, "defs": [{"defName": "x", "fields": {"modExtensions": [{}]}}]}
        return {"success": True}
    v, d = run_chain("Droidworks", "wipe_and_drift_structural", quirk)
    check("Droidworks quirk marker: the measured [{}] is accepted", v.get("quirk_pool_marked") == PASS, (v, d))

    def nomarker(tool, **p):
        if tool == "jawa/get_defs":
            return {"success": True, "defs": [{"defName": "x", "fields": {"modExtensions": []}}]}
        return quirk(tool, **p)
    v, d = run_chain("Droidworks", "wipe_and_drift_structural", nomarker)
    check("Droidworks quirk marker: a quirk with NO extension still FAILS", v.get("quirk_pool_marked") == FAIL, (v, d))

    def prices(shift):
        st = {"n": 0}

        def h(tool, **p):
            if tool == "jawa/fire_incident":
                return {"success": True, "fired": True}
            if tool == "jawa/spawn_pawn":
                return {"success": True, "pawns": [{"id": "P%d" % (st["n"] + 1)}]}
            if tool == "jawa/trade_price_probe":
                st["n"] += 1
                steel = 3.0 - (0.4 if (shift and st["n"] > 1) else 0.0)
                return {"success": True, "prices": [
                    {"defName": "Silver", "buy": 1.0, "sell": 1.0},
                    {"defName": "Steel", "buy": steel, "sell": 1.2}]}
            return {"success": True}
        return h
    v, d = run_chain("Droidworks", "protocol_trade_advantage", prices(True))
    check("Droidworks trade: silver is ignored, a shifted steel price passes",
          v.get("protocol_droid_shifts_prices") == PASS, (v, d))
    v, d = run_chain("Droidworks", "protocol_trade_advantage", prices(False))
    check("Droidworks trade: NO shift on any non-currency row still FAILS",
          v.get("protocol_droid_shifts_prices") == FAIL, (v, d))


def t_droidworks_nimbus():
    def h(tool, **p):
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"id": "Nimbus9", "def": "RSW_DW_ChargeNimbus"}]}
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": "Droid1"}]}
        if tool == "jawa/pawn_get":
            return {"success": True, "pawns": [{"needs": [{"need": "RSW_DW_Power", "level": 0.4}]}]}
        return {"success": True}
    v, d = run_chain("Droidworks", "passive_charging", h)
    check("Droidworks nimbus: found through list_things rows {id, def} -> PASS",
          v.get("nimbus_charges_in_range") == PASS, (v, d))


# ------------------------------------------------------------------ Aftermath
def t_aftermath():
    calls = []

    def h(tool, **p):
        calls.append(tool)
        if tool == "jawa/fire_incident":
            return {"success": True, "fired": True, "canFireNow": False}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": "Raider1", "hostile": True}]}
        if tool == "jawa/drain_log":
            return {"success": True, "messages": [{"text": "[RimMandrake.Aftermath] battle opened -> Repelled"}]}
        return {"success": True}
    w = FakeWatch()
    v, d = run_chain("Aftermath", "battle_lifecycle_repelled", h, watch=w)
    check("Aftermath: the raid goes through jawa/fire_incident (TryExecute), never the CanFireNow gate",
          "jawa/fire_incident" in calls and "jawa/storyteller_fire" not in calls, calls)
    check("Aftermath: raid and raiders are declared to the envelope",
          [k for k, _m, _p in w.declared] == ["raid", "hostile"] and w.declared[1][2] == "raid", w.declared)
    check("Aftermath: the raiders' phase closes before they are killed", w.exps.phase == "after", w.exps.phase)
    check("Aftermath: both components measured", v.get("devmode_and_raid_fire") == PASS
          and v.get("kill_all_raiders_closes_repelled") == PASS, (v, d))
    w = FakeWatch()
    v, d = run_chain("Aftermath", "battle_lifecycle_repelled",
                     lambda tool, **p: {"success": True, "fired": False} if tool == "jawa/fire_incident"
                     else h(tool, **p), watch=w)
    check("Aftermath: an incident that does not fire still FAILS", v.get("devmode_and_raid_fire") == FAIL, (v, d))


# ------------------------------------------------------------------ Inhabited
def t_inhabited():
    calls = []

    def h(tool, **p):
        calls.append((tool, p))
        if tool == "jawa/world_objects_get":
            return {"success": True, "objects": [{"id": 77, "def": "Inhabited_Place"}]}
        if tool == "jawa/drain_log":
            return {"success": True, "messages": [{"text": "[RimMandrake.Inhabited] created x dumped 9 goods"}]}
        return {"success": True}
    v, d = run_chain("Inhabited", "fate_and_stock", h)
    order = [c[0] for c in calls]
    check("Inhabited: the previous chain's place is removed BEFORE the create action",
          "jawa/world_objects_remove" in order and order.index("jawa/world_objects_remove")
          < order.index("rimworld/execute_debug_action"), order)
    rm = [c for c in calls if c[0] == "jawa/world_objects_remove"]
    check("Inhabited: it removes exactly the existing place id", rm and rm[0][1].get("ids") == "77", rm)
    check("Inhabited: the chain still measures stock_dumped", v.get("stock_dumped") == PASS, (v, d))


# ------------------------------------------------------------------ PawnFlavor
def t_pawnflavor():
    table = {"RUT_Jawa_AcademyCadet": ("Childhood", "JawaBSC_Empire"),
             "RUT_Jawa_Majordomo": ("Adulthood", "JawaBSC_Hutt"),
             "RUT_Jawa_PurificationEngineer": ("Adulthood", "JawaBSC_Deepwater"),
             "RUT_Jawa_ColdForged": ("Childhood", "JawaBSC_FDENightside"),
             "RUT_Jawa_AshSpeaker": ("Adulthood", "JawaBSC_Tribes"),
             "RUT_Jawa_MootSpeaker": ("Adulthood", "JawaBSC_Moot"),
             "RUT_Jawa_RetrievalAgent": ("Adulthood", "JawaBSC_Helix")}

    def h(tool, **p):
        if tool != "jawa/get_defs":
            return {"success": True}
        out = []
        for spec in p["defs"].split(";"):
            kind, name = spec.split("/")
            f = {}
            if name == "RUT_Jawa_Numbered":
                f = {"commonality": 0.0}
            elif name == "RUT_Jawa_WaterDiscipline":
                f = {"commonality": 0.5, "degreeDatas": []}
            elif name in table:
                f = {"slot": table[name][0], "spawnCategories": [table[name][1]]}
            elif name == "RUT_Jawa_RakataSiegeChild":
                f = {"spawnCategories": ["VQE_AncientPatient"]}
            elif name == "RUT_Jawa_RakataTakenChild":
                f = {"spawnCategories": ["VQE_Experiment"]}
            elif name == "Empire":
                f = {"backstoryFilters": [{"categories": ["ImperialCommon"]}, {"categories": ["JawaBSC_Empire"]}]
                     if p.get("deep") else ["BackstoryCategoryFilter", "BackstoryCategoryFilter"]}
            elif name == "Pirate":
                f = {"backstoryFilters": [{"categories": ["JawaBSC_Blackstar"]}]
                     if p.get("deep") else ["BackstoryCategoryFilter"]}
            out.append({"defName": name, "fields": f})
        return {"success": True, "defs": out}
    v, d = run_chain("PawnFlavor", "trait_defs_readback", h)
    check("PawnFlavor: a float 0.0 commonality is accepted as 0", v.get("forced_only_trait_resolves") == PASS, (v, d))
    v, d = run_chain("PawnFlavor", "backstory_defs_readback", h)
    check("PawnFlavor: ColdForged is a Childhood FDENightside backstory", v.get("backstory_RUT_Jawa_ColdForged") == PASS, (v, d))
    v, d = run_chain("PawnFlavor", "vqe_rakata_categories_readback", h)
    check("PawnFlavor: the VQE_Experiment backstory is RakataTakenChild", v.get("experiment_pool_marked") == PASS, (v, d))
    v, d = run_chain("PawnFlavor", "faction_patch_wired_vanilla", h)
    check("PawnFlavor: the faction filters are read with deep=True",
          v.get("empire_filter_wired") == PASS and v.get("pirate_filter_wired") == PASS, (v, d))
    def wrong(tool, **p):
        r = h(tool, **p)
        for row in r.get("defs", []):
            if row["defName"] == "RUT_Jawa_RakataTakenChild":
                row["fields"] = {"spawnCategories": ["VQE_AncientPatient"]}
        return r
    v, d = run_chain("PawnFlavor", "vqe_rakata_categories_readback", wrong)
    check("PawnFlavor: a backstory missing its category still FAILS", v.get("experiment_pool_marked") == FAIL, (v, d))


# ------------------------------------------------------------------ StarWarsRaces
def t_starwarsraces():
    import re
    with open(os.path.join(runner.find_mod_dir("StarWarsRaces"), "Defs", "XenotypeDefs",
                           "MandrakeJawaXenotype.xml"), encoding="utf-8") as f:
        declared = re.findall(r"<li>\s*([A-Za-z0-9_]+)\s*</li>",
                              re.search(r"<genes>(.*?)</genes>", f.read(), re.S).group(1))
    donor = [g for g in declared if g.split("_")[0] in ("AG", "SEX", "Outland", "VRE", "BS", "AptitudeStrong",
                                                       "AptitudeTerrible")]

    def handler(genes_in_def, drop_own=False):
        def h(tool, **p):
            if tool == "jawa/spawn_pawn":
                return {"success": True, "pawns": [{"id": "C1"}]}
            if tool == "jawa/set_pawn_xenotype":
                return {"success": True, "pawns": [{"now": "RSW_MandrakeJawa", "genesInDef": genes_in_def}]}
            if tool == "jawa/get_defs":
                return {"success": True, "notFound": ["GeneDef/%s" % g for g in donor]}
            if tool == "jawa/pawn_genes":
                have = [g for g in declared if g not in donor and not (drop_own and g == "RSW_Jawa_Skittish")]
                return {"success": True, "endogenes": have}
            return {"success": True}
        return h
    n_present = len(declared) - len(donor)
    v, d = run_chain("StarWarsRaces", "jawa_xenotype_mechanism", handler(n_present))
    check("StarWarsRaces: every declared gene this load CAN supply is present (%d of %d) -> PASS"
          % (n_present, len(declared)), v.get("xenotype_applies_fragile_genes") == PASS, (v, d))
    v, d = run_chain("StarWarsRaces", "jawa_xenotype_mechanism", handler(n_present - 1))
    check("StarWarsRaces: one resolvable gene silently dropped still FAILS",
          v.get("xenotype_applies_fragile_genes") == FAIL, (v, d))
    v, d = run_chain("StarWarsRaces", "jawa_xenotype_mechanism", handler(n_present, drop_own=True))
    check("StarWarsRaces: a resolvable expected gene missing from the pawn still FAILS",
          v.get("xenotype_applies_fragile_genes") == FAIL, (v, d))


# ------------------------------------------------------------------ Ninefold
def t_ninefold():
    calls = []

    def h(tool, **p):
        calls.append((tool, p))
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": "Col1", "name": "Chaz"}]}
        if tool == "jawa/pawn_get":
            return {"success": True, "pawns": [{"nameShort": "Chaz"}]}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"id": "Wall7", "def": "Wall"}]}
        if tool == "jawa/drain_log":
            return {"success": True, "messages": [{"text": "[Ninefold] Zizzik satiation +15.0 (x)"}]}
        return {"success": True}
    w = FakeWatch()
    v, d = run_chain("Ninefold", "mental_break_started", h, watch=w)
    kinds = [k for k, _m, _p in w.declared]
    check("Ninefold: the induced break is declared as a mental expectation", kinds == ["mental"], w.declared)
    m = w.declared[0][1]
    check("Ninefold: matcher accepts the colonist's pawn row and rejects another pawn",
          m({"id": "Col1"}) is True and m({"id": "Other"}) is False)
    check("Ninefold: matcher accepts the letter 'Sad wander: Chaz'", m({"label": "Sad wander: Chaz"}) is True)
    check("Ninefold: matcher rejects another pawn's letter", m({"label": "Sad wander: Vas"}) is False)
    check("Ninefold: component still measured", v.get("mental_break_ledger") == PASS, (v, d))

    calls[:] = []
    v, d = run_chain("Ninefold", "building_repaired_and_deconstructed", h)
    dmg = [c for c in calls if c[0] == "jawa/damage"]
    check("Ninefold: the wall is hit with a NON-destructive blunt hit", dmg and dmg[0][1].get("damageDef") == "Blunt", dmg)
    fac = [c for c in calls if c[0] == "jawa/set_thing_props"]
    check("Ninefold: the wall is given the player faction the repair hook requires",
          fac and fac[0][1].get("faction") == "PlayerColony", fac)

    waits = []
    run_chain("Ninefold", "birth_outcome", h, waits=waits)
    check("Ninefold: the birth wait covers labor (<=25000) + pushing (<=5000) ticks", sum(waits) >= 30000, waits)


def main():
    for fn in (t_jawaion, t_shipmemory, t_droidworks_bolt, t_droidworks_quirk_and_prices, t_droidworks_nimbus,
               t_aftermath, t_inhabited, t_pawnflavor, t_starwarsraces, t_ninefold):
        print(fn.__name__)
        try:
            fn()
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            check("%s ran without raising" % fn.__name__, False, "%s: %s" % (type(e).__name__, e))
    if FAILURES:
        print("\nFAILED %d: %s" % (len(FAILURES), "; ".join(FAILURES)))
        sys.exit(1)
    print("\nSELFTEST OK")


if __name__ == "__main__":
    main()
