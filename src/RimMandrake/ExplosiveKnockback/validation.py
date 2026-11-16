"""validation.py -- modcheck suite for RimMandrake: Explosive Knockback (mandrake.rm.explosiveknockback).

First functional script (design/RimMandrake/debug_process.md §2). Walk: design/validation_walks/RimMandrake/ExplosiveKnockback.md.
Design: design/RimMandrake/explosive_knockback_design_2026-10-06.md (§8).

Every behaviour chain drives ONE in-game scene through jawa/static_call on RimMandrake.ExplosiveKnockback.RM_KnockbackProof:
Stage("<scene>,x,z") builds it on a cleared 15x15 patch and sets the blast off, rimworld/step_game_ticks resolves it
without unpausing, Verdict("<scene>") reads the knockback JOURNAL (request / launch / blocked / item_move / skip /
land / descent records) plus map state. A component PASSes only on a PASS verdict; INVALID (e.g. FlowWorks absent for
a pit scene) records UNMEASURED, never PASS. The same scenes run standalone via knockback_runner.py.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
LIVE leaf: `python.exe validation.py --live walk_storeroom_raid --storeroom x,z,w,h --cover x,z --gas x,z` (sc_walk_raid, the
full list; see walk_storeroom_raid below). `--live` with no game, no bridge or an unknown leaf refuses non-zero.
"""
import collections
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PROOF = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
sys.path.insert(0, HERE)
from proof_build_gate import MESSAGE as PROOF_BUILD_MESSAGE, is_release_answer  # noqa: E402
WALK = os.path.join(REPO, "design", "validation_walks", "RimMandrake", "ExplosiveKnockback.md")
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")

# scene -> (chain, component, toggle it exercises or None)
SCENES = [
    ("calibration", "throw", "mortar_beside_human_throws_3_cells", "strength"),
    ("wall_stop", "throw", "wall_stops_throw_with_impact", "impactDamageEnabled"),
    ("door_stop", "throw", "closed_door_stops_throw_and_takes_a_hit", "doorsTakeDamage"),
    ("over_sandbags", "throw", "thrown_over_sandbags", "sandbagsStopThrow"),
    ("heavy_skip", "throw", "creature_over_mass_limit_is_not_thrown", "creatureMassLimit"),
    ("emp_no_throw", "throw", "emp_blast_throws_nothing", "unpatchedHarmfulPercent"),
    ("items", "light_things", "items_thrown_by_mass_heavy_stays", "throwItems"),
    ("shelf", "light_things", "item_on_an_open_shelf_scatters", "openStorageProtectsGoods"),
    ("killed_by_blast", "light_things", "pawn_killed_by_blast_thrown_as_corpse", "throwCorpses"),
    ("pit_colonist", "pits", "colonist_thrown_into_open_pit_falls", "throwIntoPits"),
    ("pit_enemy", "pits", "enemy_thrown_into_open_pit_falls", None),
    ("no_cross", "pits", "throw_stops_inside_a_1_wide_pit", None),
    ("in_pit_skip", "pits", "pawn_already_in_pit_not_thrown", None),
    ("corpse_into_pit", "pits", "corpse_thrown_onto_pit_floor", None),
    ("cover_breaks", "pits", "blast_breaks_cover_and_pawn_on_it_falls", None),
    ("all_fly_no_cap", "caps", "no_cap_every_throw_in_one_tick", None),
    ("settings_off", "settings", "master_off_nothing_moves_but_wave_hit", "enabled"),
    # 2026-10-06 finish pass (KINETIC_BLAST_WEAPONS_1): per-blast config, stun-lock guard, shields
    ("lookup_projectile", "config", "projectile_extension_wins_over_damagedef", "ownCapScale"),
    ("lookup_zero_wins", "config", "explicit_zero_on_projectile_throws_nothing", None),
    ("impact_factor", "config", "impact_factor_zero_no_wall_impact", None),
    ("body_override", "config", "mass_override_throws_a_160_200_kg_animal_global_does_not", None),
    ("immunity_window", "guards", "second_blast_in_recovery_window_is_immune", "recoveryWindowTicks"),
    ("shield_counter", "guards", "shield_belt_absorbs_throw_and_drains", "shieldsAbsorbThrow"),
    # 2026-11-12 RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: thrown goods fly in a carrier (proof build only)
    ("goods_fly_midair", "flying_goods", "stack_inside_carrier_mid_flight", "flyingGoods"),
    ("goods_fly_lands", "flying_goods", "lands_on_the_instant_cell_count_intact", "goodsFlightSpeed"),
    ("goods_fly_wall", "flying_goods", "wall_cut_short_applies_impact", "goodsRebound"),
    ("goods_fly_rebound", "flying_goods", "rebound_off_wall_at_keep_percent", "goodsReboundKeepPercent"),
    ("goods_fly_off", "flying_goods", "off_goods_unthrown", "flyingGoods"),
    # 2026-11-12 RIMMANDRAKE_STAGE_KNOCKBACK_CONTAINER_SURVIVES_BLAST / RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS
    ("fire_half", "throw", "fire_and_incendiary_throw_at_half", None),
    ("harmful_unpatched", "throw", "unpatched_harmful_blast_throws_at_full", "unpatchedHarmfulPercent"),
    # 2026-11-12 round 2 (owner: "No caps please.", the container thrown whole, "build the unbuilt items and bug")
    ("container_thrown", "light_things", "closed_container_thrown_whole_contents_inside_unhurt", "shoveClosedContainers"),
    ("heavy_knock", "flying_goods", "heavy_stack_hits_and_stops_light_passes", "heavyGoodsKnock"),
    ("land_no_bump", "flying_goods", "landing_never_shoves_a_resident", None),
    ("land_no_bump_pit", "pits", "landing_in_a_pit_never_shoves_a_resident_out", None),
    ("gas_clumps", "gas", "burning_gas_bursts_clump_by_clump_no_damage", "gasChain"),
    # 2026-11-13 creature mass limit + blast power (owner cards; sc_mass_and_power, the showcase). NOT YET RUN LIVE.
    ("mass_and_power", "mass_power", "heavier_flies_less_lightest_colonist_under_150_kg_heavy_spared", "creatureMassLimit"),
    ("mass_and_power_x2", "mass_power", "double_damage_throws_each_creature_farther", "blastPowerFromDamage"),
    ("mass_and_power_off", "mass_power", "power_off_damage_50_throws_as_before", "blastPowerFromDamage"),
    ("mass_and_power_off_x2", "mass_power", "power_off_damage_100_throws_as_damage_50", "blastPowerFromDamage"),
    ("mass_and_power_250", "mass_power", "limit_250_throws_the_220_260_kg_animal", "creatureMassLimit"),
    ("mass_and_power_250_x2", "mass_power", "limit_250_double_damage_throws_the_220_260_kg_animal_farther", "blastPowerRefPercent"),
]
NOT_DRIVEN = [
    ("hose_carry_drops_at_takeoff", "needs a laid hose reel and a colonist mid CarryHoseEnd job; DropCarriedHose is wired "
     "(RM_KnockbackCompat) but no scene stages a carry yet"),
    ("save_mid_flight", "save with a flyer in the air, reload, pawn exists once: needs a save/load half"),
    ("raid_lord_resumes_duty", "a real assault raid hit by a mortar: needs a raid site"),
    ("vef_active_same_results", "VEF patches PawnFlyer.MakeFlyer/RecomputePosition; needs a VEF tier (ship gate)"),
    ("barrage_perf_ms_per_tick", "performance has no Boolean check (debug_process §4); counts are in the caps chain"),
    ("save_mid_flight_keeps_the_stack", "a save taken with a goods carrier in the air, then a reload: driven by "
     "proof/goods_flight_saveload.py (needs bridge save/load), not a scene"),
    ("immunity_survives_reload", "the landing/stun stamps are Scribed on the map component; needs a save/load half"),
]

# The validation ladder (rimflow model.LEVELS): L0 offline, L1 resolved-live on the minimal list, L2 behaviour scenes,
# L4 human. `python3 validation.py --criteria` prints these as `ID LEVEL: text` for `rimflow implemented --criteria-file`.
CRITERIA = [
    ("EK.K", "L0", "kernel selftest K-01..K-20 PASS (selftest_explosiveknockback_kernel.py)"),
    ("EK.static", "L0", "validation.py STATIC PASS: config lookup, shield/landing hooks, settings saved+reset, walk coverage"),
    ("EK.mock", "L0", "validation.py --mock stages every scene"),
    ("EK.load", "L1", "explosiveknockback tier loads with no red error from this mod; Harmony patches applied"),
    ("EK.scenes18", "L2", "the 18 v1 scenes still PASS after the 2026-10-06 config/guard/shield change"),
    ("EK.config", "L2", "lookup_projectile, lookup_zero_wins, impact_factor, body_override PASS"),
    ("EK.mass", "L0", "kernel K-18..K-20 PASS: creature mass limit 150 kg, blast power = force x damage / reference"),
    ("EK.massLive", "L2", "the six mass_and_power scenes PASS (sc_mass_and_power and its two control lanes)"),
    ("EK.guards", "L2", "immunity_window and shield_counter PASS"),
    ("EK.reload", "L2", "recovery-window stamps survive a save/reload (no scene yet)"),
    ("EK.feel", "L4", "owner watches a blast and a shield belt: reads right"),
]


def settings_fields():
    src = open(os.path.join(HERE, "Source", "RM_KnockbackMod.cs"), encoding="utf-8").read()
    body = src.split("class RimMandrakeExplosiveKnockbackSettings", 1)[1].split("public static KbSettings Kernel", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    fields = settings_fields()
    if len(fields) < 10:
        bad.append("settings probe found %d fields (sanity probe failed)" % len(fields))
    proof = open(os.path.join(HERE, "Source", "RM_KnockbackProof.cs"), encoding="utf-8").read()
    for scene, _c, _k, toggle in SCENES:
        if '"%s"' % scene not in proof:
            bad.append("scene %s missing from RM_KnockbackProof" % scene)
        if toggle and toggle not in fields:
            bad.append("scene %s names unknown toggle %s" % (scene, toggle))
    csproj = open(os.path.join(HERE, "Source", "RimMandrake_ExplosiveKnockback.csproj"), encoding="utf-8").read()
    for f in os.listdir(os.path.join(HERE, "Source")):
        if f.endswith(".cs") and 'Include="%s"' % f not in csproj:
            bad.append("%s is not in the csproj Compile list (EnableDefaultCompileItems is false)" % f)
    bad += l0_wiring(fields)
    if not os.path.isfile(WALK):
        bad.append("walk missing")
    else:
        walk = open(WALK, encoding="utf-8").read()
        sec = walk.split("## must be true", 1)[1].split("\n## ", 1)[0]
        for line in sec.splitlines():
            if line.startswith("- ") and "→" not in line:
                bad.append("walk line without coverage arrow: " + line[:60])
        for _s, chain, comp, _t in SCENES:
            if "%s.%s" % (chain, comp) not in sec:
                bad.append("walk does not cover %s.%s" % (chain, comp))
    return bad


def l0_wiring(fields):
    """Offline (L0) proof of every 2026-10-06 feature's wiring, read from the shipped source."""
    bad = []
    src = lambda f: open(os.path.join(HERE, "Source", f), encoding="utf-8").read()
    mod, patch, comp, fly, kern = (src("RM_KnockbackMod.cs"), src("RM_Patch_DamageWorker_ExplosionKnockback.cs"),
                                   src("RM_MapComponent_Knockback.cs"), src("RM_PawnFlyerPatches.cs"), src("RM_KnockbackMath.cs"))
    ext = mod.split("class RM_KnockbackExtension", 1)[1].split("\n    }", 1)[0]
    for f in ("force", "maxThrowCells", "impactFactor", "creatureMassLimitOverride", "refDamage"):
        if "public %s %s" % ("int" if f == "maxThrowCells" else "float", f) not in ext:
            bad.append("RM_KnockbackExtension lacks field " + f)
    res = kern.split("public static KbConfig Resolve", 1)[1].split("public static KbSettings Apply", 1)[0]
    order = [res.find('"projectile"'), res.find('"weapon"'), res.find('"damageDef"'), res.find('"unpatched"')]
    if min(order) < 0 or order != sorted(order):
        bad.append("KbLookup.Resolve order is not projectile -> weapon -> damageDef -> unpatched: %r" % order)
    if "ConfigOf(explosion, __instance.def)" not in patch:
        bad.append("ExplosionDamageThing prefix does not resolve ConfigOf(explosion, def)")
    if "explosion?.projectile" not in patch or "explosion?.weapon" not in patch:
        bad.append("ConfigOf does not read the explosion's projectile and weapon ThingDefs")
    if "HarmonyPatch(typeof(CompShield), nameof(CompShield.PostPreApplyDamage))" not in patch:
        bad.append("no CompShield absorb-capture patch")
    if "AbsorbByShield" not in comp or "shieldsAbsorbThrow" not in comp:
        bad.append("map component does not absorb throws by shield behind the setting")
    if "NotifyLanded" not in fly:
        bad.append("landing postfix does not stamp the stun-lock guard")
    for key in ("rmKbLandedAt", "rmKbStunEnd"):
        if '"%s"' % key not in comp:
            bad.append("stun-lock stamp %s is not Scribed" % key)
    if '"immune"' not in comp:
        bad.append("an immune skip is not journalled")
    # every setting: saved, reset to its default, shown in the window
    expose = mod.split("public override void ExposeData", 1)[1].split("\n        }", 1)[0]
    reset = mod.split("public static void Reset()", 1)[1]
    window = mod.split("public void DoWindowContents", 1)[1].split("class RimMandrakeExplosiveKnockbackMod", 1)[0]
    for f in fields:
        if 'ref %s,' % f not in expose:
            bad.append("setting %s is not saved in ExposeData" % f)
        if "RimMandrakeExplosiveKnockbackSettings.%s =" % f not in reset and "ResetFields(" not in reset:
            bad.append("setting %s is not restored by Reset()" % f)
        if not re.search(r"\b%s\b" % f, window):
            bad.append("setting %s has no control in the settings window" % f)
    bad += proof_restore_wiring(src("RM_KnockbackProof.cs"))
    prog = open(os.path.join(HERE, "Source", "SelfTest", "Program.cs"), encoding="utf-8").read()
    for k in ("K-13", "K-14", "K-15", "K-16"):
        if '"%s ' % k not in prog:
            bad.append("kernel selftest has no %s rows" % k)
    return bad


def proof_restore_wiring(proof):
    """A scene that changes a def or a setting must undo it even when Stage fails or Verdict never runs: a leaked
    extension on vanilla Bullet_Revolver would make every revolver shot throw pawns for the rest of the session."""
    bad = []
    stage = proof.split("public static string Stage(", 1)[1].split("public static string Verdict(", 1)[0]
    if stage.count("RunRestore(") < 3:
        bad.append("RM_KnockbackProof.Stage does not run the scene restore on re-stage, INVALID and ERROR (%d calls)"
                   % stage.count("RunRestore("))
    if "s.restore = null" not in proof:
        bad.append("RM_KnockbackProof restore can run twice (RunRestore does not clear it)")
    # every settings poke registers its restore BEFORE the poke, so a throw in between still undoes it
    for m in re.finditer(r"\n( +)RimMandrakeExplosiveKnockbackSettings\.(\w+) = [^;]+;", proof):
        before = proof[:m.start()]
        last = before.rfind("s.restore = ")
        case = before.rfind("case \"")
        if last < case:
            bad.append("RM_KnockbackProof pokes setting %s before registering its restore" % m.group(2))
    return bad


def criteria_lines():
    return ["%s %s: %s" % c for c in CRITERIA]


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite("ExplosiveKnockback")
    suite.toggles = sorted(settings_fields())
    state = {"origins": None, "next": 0}

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _call(t, method, arg):
        r = t.bridge_call("jawa/static_call", type=PROOF, method=method, args=arg)
        if isinstance(r, dict):
            if r.get("success") is False:
                if is_release_answer(r):                 # the release DLL has no proof type: say so, never a bare FAIL
                    raise ExpectationFailed(PROOF_BUILD_MESSAGE)
                raise ExpectationFailed("static_call %s failed: %r" % (method, r))
            return str(r.get("result", r.get("value", "")))
        return str(r)

    def _origin(t):
        if state["origins"] is None:
            state["origins"] = _call(t, "Origins", str(len(SCENES))).split(";")
            # reset rewrites every field to its default: record the player's values first so the chain's finally
            # (modcheck suite.py) puts them back, whatever happens in between
            t.remember_settings("RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings", sorted(settings_fields()))
            _call(t, "Settings", "reset")
        o = state["origins"][state["next"] % len(state["origins"])]
        state["next"] += 1
        return o

    def _scene(t, scene):
        if not _live(t):
            return
        staged = _call(t, "Stage", "%s,%s" % (scene, _origin(t)))
        if staged.startswith("INVALID"):
            t.upstream_reason = "UNMEASURED: " + staged
            t.upstream_failed = True
            return
        if not staged.startswith("STAGED"):
            raise ExpectationFailed(staged)
        t.bridge_call("rimworld/step_game_ticks", ticks=300)
        v = _call(t, "Verdict", scene)
        if v.startswith("INVALID"):
            t.upstream_reason = "UNMEASURED: " + v
            t.upstream_failed = True
        elif not v.startswith("PASS"):
            raise ExpectationFailed(v)

    chains = {}
    for scene, chain, comp, toggle in SCENES:
        chains.setdefault(chain, []).append((scene, comp, toggle))

    for chain, rows in chains.items():
        def make(rows=rows):
            def run(t):
                for scene, comp, toggle in rows:
                    with t.component(comp, toggle=toggle, beyond_toggle=toggle is None):
                        _scene(t, scene)
            return run
        suite.chain(chain)(make())

    @suite.chain("not_driven")
    def not_driven(t):
        for name, why in NOT_DRIVEN:
            with t.component(name, beyond_toggle=True):
                if _live(t):
                    t.upstream_reason = "UNMEASURED: " + why
                    t.upstream_failed = True

    return suite


suite = _build_suite() if Suite is not None else None

class _MockSession:
    """--mock: answers like a game where every scene PASSes, so the chain plumbing is exercised offline."""

    def __init__(self):
        self.calls = []

    def sweep(self):
        return None

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/static_call":
            m, a = kw.get("method"), kw.get("args", "")
            if m == "Origins":
                return {"success": True, "result": ";".join("%d,12" % (12 + 15 * i) for i in range(int(a)))}
            if m == "Stage":
                return {"success": True, "result": "STAGED " + a.split(",")[0]}
            if m == "Verdict":
                return {"success": True, "result": "PASS " + a + " mock"}
            return {"success": True, "result": "OK"}
        return {"success": True}


def mock_run():
    from runner import run_suite  # modcheck package dir is on sys.path via _UTILS/modcheck
    fake = _MockSession()
    res = run_suite(suite, fake, anchor=(50, 50))
    stages = sum(1 for t, kw in fake.calls if t == "jawa/static_call" and kw.get("method") == "Stage")
    ok = stages == len(SCENES)
    print("MOCK: %s (%d/%d scenes staged, all_green=%s)" % ("PASS" if ok else "FAIL", stages, len(SCENES), res.get("all_green")))
    return 0 if ok else 1



# ============================================================================ walk_storeroom_raid (leaf, scene sc_walk_raid)
# design/concepts/ExplosiveKnockback/scenes.json sc_walk_raid; leaf walk_storeroom_raid in tree.json. FULL LIST, python.exe,
# bridge held, the proof build deployed, a throwaway colony whose storeroom, covered pit trap and vent-gas cell are named by
# the flags below (each asserted from the live map; INVALID, so UNMEASURED rows, otherwise).
#   python.exe src\RimMandrake\ExplosiveKnockback\validation.py --live walk_storeroom_raid --storeroom x,z,w,h --cover x,z
#       --gas x,z [--lit x,z] [--save NAME] [--site x,z,w,h] [--raid-points 300] [--out evidence.json]
# Shells are GenExplosion calls at the HE mortar shell's numbers (Bullet_Shell_HighExplosive: Bomb, radius 2.9) and the
# grenade at the frag grenade's (Proj_GrenadeFrag: Bomb, radius 1.9), so the config lookup resolves on the damageDef path;
# the raid itself is real (jawa/fire_raid) so raiders are on the map. Orders: A mortars, mid-air save + reload, grenade,
# gas; B (from the baseline save) gas, mortars, grenade; C the mortars with the mod off. The baseline save is reloaded at
# the end and the player's settings put back. Exit 0 only if every row PASSes; 2 = refused (no game, no bridge); 3 = PROOF
# BUILD REQUIRED. FRAME_BUDGET (RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED): the orders step paused
# ticks, so they hold no real frames; two more arms reload the baseline, run the clock at speed 1 and set the shells off over
# the stocked storeroom while RM_KnockbackProof.Frame reads real frames, once with the mod on and once off. The row is
# relative (owner, by card 2026-11-16, "Compare to mod-off"): PASS when the on arm's p99 unpaused frame is within 10% of
# the off arm's in the same run, FAIL over it; UNMEASURED unless both arms are read, something flew, and the arms ran at
# like frame counts (a p99 over frames falls as the frame rate rises; live run 5 2026-11-16, an uncapped off arm). The
# 50 ms barrage bar is sc_barrage_perf's, not the walk's. CARRIER_TICK_COST is read in the on arm on a running clock.
# What "match the kernel's plan" can read live: every request has an outcome line for the same blast and thing, a launch
# travels at most its planned cells (fewer only with a stop reason), a goods move flies its wild cells with the kernel's
# cells beside them. Recomputing the plan from the kernel is the offline selftest's job (selftest_explosiveknockback_kernel).
TRIPLET_SEAMS = {}           # saveload_triplet's saves_stat / wait_saved (the offline selftest passes fakes)
SLEEP = None                 # the frame act's real-time wait (time.sleep; the offline selftest passes a no-op)
FRAME_OVER_OFF = 0.10        # the walk's frame row: mod-on p99 at most 10% over the same run's mod-off p99 (owner card 2026-11-16)
FRAME_MIN_ROWS = 30          # fewer unpaused rows in the window than this is no reading
FRAME_ROWS_LIKE = 1.25       # arms whose window frame counts differ by more than this ratio are not like for like
WALK_ROWS = ("W_PRECONDITIONS", "A_IMPACTS_IN_ROOM", "A_SAVE_MIDAIR", "A_RELOAD_NO_DUP_LOST", "A_COVER_BROKEN_ONE_DESCENT",
             "A_GAS_CLUMP_BY_CLUMP", "A_GAS_GOODS_MOVED", "A_REQUESTS_MATCH_PLAN", "A_REACHED_ACCOUNTED",
             "B_GAS_CLUMP_BY_CLUMP", "B_GAS_GOODS_MOVED", "B_IMPACTS_IN_ROOM", "B_COVER_BROKEN_ONE_DESCENT",
             "B_REQUESTS_MATCH_PLAN", "B_REACHED_ACCOUNTED", "C_OFF_IMPACTS_NO_THROWS", "CARRIER_TICK_COST", "FRAME_BUDGET")
SHELL = ("Bomb", 2.9)        # Bullet_Shell_HighExplosive (Core Items_Resource_Shell.xml)
GRENADE = ("Bomb", 1.9)      # Proj_GrenadeFrag (Core RangedIndustrialGrenades.xml)
VENTGAS = "RimMandrake.Cauldron.RM_MapComponent_VentGas"
SETTINGS_TYPE = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
MODS_NEEDED = ("mandrake.rm.explosiveknockback", "mandrake.rm.flowworks", "mandrake.rm.biomes")   # the Cauldron is folded into Biomes (visit 2)



class WalkRefused(Exception):
    """No game or no bridge: the walk did not start, which is never a STATIC exit 0."""


def _xz(s):
    return tuple(int(v) for v in str(s).split(","))


def _in_rect(c, r):
    return c is not None and r[0] <= c[0] < r[0] + r[2] and r[1] <= c[1] < r[1] + r[3]


def _pos(t):
    """A thing's cell: jawa/list_things answers top-level x/z (visit 2, measured live); older payloads a position dict."""
    p = t.get("position") if isinstance(t.get("position"), dict) else t
    x, z = p.get("x"), p.get("z")
    return (x, z) if x is not None and z is not None else None


def _num(s):
    return "".join(ch for ch in str(s) if ch.isdigit())


def active_mods(path=None):
    """ModsConfig's activeMods, lowercased, or None when it is unreadable (it describes the NEXT load)."""
    import xml.etree.ElementTree as ET
    if path is None:
        sys.path.insert(0, _UTILS)
        from game_paths import MODS_CONFIG as path
    if not os.path.isfile(path):
        return None
    return [li.text.strip().lower() for li in ET.parse(path).find("activeMods") if li.text]


def pool_arms(readings):
    """One side's frame arms -> one reading: p99 the median of the arms' p99s, rows the smallest arm's, inAir the
    fewest any arm saw. Any unread arm (no p99, too few frames, no reading at all) makes the side unread: both sides
    MEASURED or the row is UNMEASURED (owner card 2026-11-16)."""
    import statistics
    ok = [r for r in readings if isinstance(r.get("p99"), (int, float)) and (r.get("rows") or 0) >= FRAME_MIN_ROWS]
    text = " | ".join(r.get("text") or r.get("why") or "?" for r in readings)[:600]
    if not readings or len(ok) < len(readings):
        return {"p99": None, "rows": 0, "inAir": 0, "text": "%d of %d arm(s) read: %s" % (len(ok), len(readings), text)}
    return {"p99": statistics.median(r["p99"] for r in ok), "rows": min(r["rows"] for r in ok),
            "rows_each": [r["rows"] for r in ok], "p99_each": [r["p99"] for r in ok],
            "inAir": min(r.get("inAir") or 0 for r in ok), "text": "%d arm(s), p99s %s: %s" % (
                len(ok), [r["p99"] for r in ok], text)}


class _Walk:
    def __init__(self, B, a, wait):
        self.B, self.a, self.wait = B, a, wait
        self.rows, self.ev = {}, {"args": vars(a)}
        self.room = _xz(a.storeroom)
        self.cover, self.gas = _xz(a.cover), _xz(a.gas)
        self.lit = _xz(a.lit) if a.lit else (self.gas[0] - 2, self.gas[1])
        if a.site:
            self.site = _xz(a.site)
        else:
            xs = [self.room[0], self.room[0] + self.room[2], self.cover[0] + 1, self.gas[0] + 3, self.gas[0] - 3]
            zs = [self.room[1], self.room[1] + self.room[3], self.cover[1] + 1, self.gas[1] + 3, self.gas[1] - 3]
            self.site = (min(xs) - 4, min(zs) - 4, max(xs) - min(xs) + 8, max(zs) - min(zs) + 8)

    # ---- bridge plumbing
    def c(self, tool, **kw):
        try:
            r = self.B.call(tool, **kw)
        except Exception as e:  # noqa: BLE001 - one failed call is that row's evidence, never a crash
            return {"success": False, "exc": repr(e)[:300]}
        return r if isinstance(r, dict) else {"success": True, "result": r}

    def kp(self, method, arg="x", type_=PROOF):
        r = self.c("jawa/static_call", type=type_, method=method, args=arg)
        return r, str(r.get("result") or "")

    def step(self, n):
        self.c("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=120000)

    def row(self, rid, ok, det):
        self.rows[rid] = (ok if isinstance(ok, str) else ("PASS" if ok else "FAIL"), str(det)[:400])

    def unmeasured(self, rids, why):
        for rid in rids:
            self.rows.setdefault(rid, ("UNMEASURED", why[:400]))

    def journal(self):
        recs = []
        for line in self.kp("Journal", "4000")[1].splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    recs.append(json.loads(line))
                except ValueError:
                    pass
        return recs

    def haulables(self, rect):
        r = self.c("jawa/list_things", rect="%d,%d,%d,%d" % tuple(rect), group="HaulableEver", limit=2000)
        return r.get("things") or []

    def save(self, name):
        r = self.c("rimworld/save_game", saveName=name)
        self.ev.setdefault("saves", []).append(name)
        return r

    def load(self, name):
        self.c("rimworld/load_game", saveName=name)
        ok, why = self.wait(self.B)
        self.c("rimworld/set_time_speed", speed=0)
        return ok, why

    def perf(self):
        r = self.c("jawa/time_perf")
        return r.get("meanTickTime") if r.get("success") is not False else None

    # ---- preconditions (asserted; any miss makes every later row UNMEASURED)
    def preconditions(self):
        miss = []
        tp = self.c("jawa/time_perf")
        if tp.get("success") is False:
            raise WalkRefused("no game loaded, or the bridge refused (jawa/time_perf: %s)" % str(tp.get("exc") or tp.get("error") or tp)[:240])
        r, names = self.kp("Names")
        if is_release_answer(r):
            return "RELEASE"
        if "flowworks=True" not in names:
            miss.append("FlowWorks not live (Names: %s)" % names[-60:])
        mods = active_mods()
        if mods is None:
            miss.append("ModsConfig.xml unreadable")
        else:
            miss += ["%s not in ModsConfig activeMods" % m for m in MODS_NEEDED if m not in mods]
            if len(mods) < self.a.full_min:
                miss.append("%d active mods: not the full list (--full-min %d)" % (len(mods), self.a.full_min))
            self.ev["active_mods"] = len(mods)
        self.kp("Plant", "reset")
        if "gasreg=True" not in self.kp("Plant", "gasreg=on")[1]:
            miss.append("Cauldron vent gas not registered with the gas chain (Plant gasreg)")
        rb = self.c("jawa/list_things", rect="%d,%d,%d,%d" % self.room, group="BuildingArtificial", limit=500).get("things") or []
        defs = sorted(set(t.get("def") for t in rb if t.get("def")))
        shelves = [d for d in defs if d in self.a.shelf_defs.split(",")]
        closed = [d for d in defs if self.kp("IsClosed", d)[1].startswith("CLOSED ")]
        if not shelves:
            miss.append("no open shelf (%s) in the storeroom" % self.a.shelf_defs)
        for d in shelves:
            if not self.kp("IsClosed", d)[1].startswith("OPEN "):
                miss.append("shelf %s is not OPEN by the shipped rule" % d)
        if not closed:
            miss.append("no closed container in the storeroom (defs %s)" % defs[:12])
        goods = self.haulables(self.room)
        if len(goods) < 3:
            miss.append("%d haulable stacks in the storeroom (want >= 3)" % len(goods))
        cov = self.c("jawa/list_things", rect="%d,%d,1,1" % self.cover, limit=20).get("things") or []
        self.cover_def = next((t.get("def") for t in cov if str(t.get("def", "")).startswith("RM_PitCover")), None)
        if not self.cover_def:
            miss.append("no RM_PitCover* on the cover cell %d,%d" % self.cover)
        self.ev["pre"] = {"shelves": shelves, "closed": closed, "goods": len(goods), "cover": self.cover_def}
        return miss

    # ---- the three acts
    def mortars(self, tag, midair=False):
        cx, cz = self.room[0] + self.room[2] // 2, self.room[1] + self.room[3] // 2
        cells = [(cx, cz), (cx - 1, cz + 1), (cx + 1, cz - 1)][:max(1, self.a.shells)]
        recs, ok_all, reached_miss = [], True, []
        for i, (x, z) in enumerate(cells):
            pre = [t for t in self.haulables((x - 3, z - 3, 7, 7))
                   if _pos(t) and math.hypot(_pos(t)[0] - x, _pos(t)[1] - z) <= SHELL[1] - 1]
            self.kp("Clear")
            e = self.c("jawa/explosion_at", at="%d,%d" % (x, z), radius=SHELL[1], damType=SHELL[0])
            ok_all = ok_all and e.get("success") is not False
            if midair and i == 0:
                self.step(2)
                self.midair(tag)
            self.step(self.a.settle)
            w = self.journal()
            recs += w
            seen = set(_num(r.get("thing")) for r in w if r.get("thing"))
            reached_miss += ["%s@%s" % (t.get("def"), _pos(t)) for t in pre if _num(t.get("id")) not in seen]
        return cells, recs, ok_all, reached_miss

    def midair(self, tag):
        fl = [l for l in self.kp("Flights")[1].splitlines() if l and not l.startswith("NONE")]
        self.ev["tick_air"] = self.perf()
        self.ev["midair_flights"] = fl
        if not fl:
            self.row("A_SAVE_MIDAIR", False, "no carrier in the air 2 ticks after the first shell")
            self.unmeasured(["A_RELOAD_NO_DUP_LOST"], "UNMEASURED: nothing in the air to save")
            return

        # A thing born after the save (a leaving of the shell's wave) takes its id from the game's counter, which a load
        # advances (live 2026-11-16: 42837 live, 43837 in both loads; the triplet's reading must hold no per-load ids):
        # an id above every haulable id read just before the save is NOT the save's: its id, cell and even its count come
        # from the RNG, whose state a load changes (live 2026-11-16: a WoodLog leaving at 101,42 live and 102,42 loaded,
        # then 9 vs 10 things in two loads). The judged census holds the things the save holds; born things are counted
        # per arm in the evidence, unjudged. Blind spot: a load-made twin under a NEW id reads as born.
        hi = [0]
        born_seen = self.ev.setdefault("reload_born", [])

        def census(_B=None):
            ids, born = [], collections.Counter()
            for t in self.haulables(self.site):
                n = _num(t.get("id"))
                if n and int(n) <= hi[0]:
                    ids.append(n)
                else:
                    born[t.get("def")] += 1
            born_seen.append(dict(born))
            for l in self.kp("Flights")[1].splitlines():
                m = re.search(r"innerId=(\S+)", l)
                if m:
                    ids.append(_num(m.group(1)))
            return {"ids": sorted(set(ids)), "dup": sorted(i for i in set(ids) if ids.count(i) > 1)}
        hi[0] = max([int(_num(t.get("id"))) for t in self.haulables(self.site) if _num(t.get("id"))] +
                    [int(_num(m)) for m in re.findall(r"innerId=(\S+)", self.kp("Flights")[1]) if _num(m)] + [0])
        # RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES: run 2 read "11 before, 7 after" from a census taken before
        # the save and one after the load, a tick apart (PauseOnLoad runs one DoSingleTick) while the first shell's wave was
        # still spreading: two moments, not one state. The arms are now aligned on the measured clock (saveload_triplet: live,
        # load and reload, each read at save + TRIPLET_MIN_TICKS, carriers still in the air), so only the round trip differs.
        sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
        import validation_core as VC
        name = "EK_WALK_RAID_MIDAIR_" + self.a.stamp
        walk = self

        class _TB:
            def call(self, tool, _answer=False, **kw):
                return walk.B.call(tool, _answer=_answer, **kw)

            def ticks(self, n):
                walk.step(n)
        self.ev.setdefault("saves", []).append(name)
        try:
            tr = VC.saveload_triplet(_TB(), census, ticks=VC.TRIPLET_MIN_TICKS, save_name=name, wait_playing=self.wait,
                                     **TRIPLET_SEAMS)
        except Exception as e:  # noqa: BLE001 - a bridge fault inside the triplet is an unread row, never a verdict
            tr = {"verdict": "UNMEASURED", "why": "saveload_triplet raised %r" % e, "arms": {}}
        self.row("A_SAVE_MIDAIR", tr.get("target") is not None and "rimworld/save_game refused" not in str(tr.get("why")),
                 "%d carrier(s) in the air; save %s; triplet %s" % (len(fl), name, tr.get("verdict")))
        arms = tr.get("arms") or {}
        dups = {k: [v for kk, v in (a.get("state") or {}).items() if kk.startswith("dup[")] for k, a in arms.items()}
        ids = lambda k: [v for kk, v in ((arms.get(k) or {}).get("state") or {}).items() if kk.startswith("ids[")]  # noqa: E731
        lost, new = sorted(set(ids("A")) - set(ids("B"))), sorted(set(ids("B")) - set(ids("A")))
        self.ev["reload_census"] = {"verdict": tr.get("verdict"), "why": tr.get("why"), "target": tr.get("target"),
                                    "loadedAt": {k: a.get("loadedAt") for k, a in arms.items()},
                                    "count": {k: len(ids(k)) for k in arms}, "dup": dups, "lost": lost, "new": new,
                                    "BC": tr.get("BC")}
        det = "at tick %s: live %d, load %d, reload %d things; dup %s; lost %s new %s (load vs live); %s" % (
            tr.get("target"), len(ids("A")), len(ids("B")), len(ids("C")), {k: v[:5] for k, v in dups.items() if v},
            lost[:5], new[:5], tr.get("why"))
        if any(dups.values()):
            self.row("A_RELOAD_NO_DUP_LOST", False, "MOD: a thing counted twice; " + det)
        elif tr.get("verdict") == VC.TRIPLET_IDENTICAL:
            self.row("A_RELOAD_NO_DUP_LOST", True, det)
        elif tr.get("verdict") == VC.TRIPLET_SAVE_DROPS:
            self.row("A_RELOAD_NO_DUP_LOST", False, "MOD: both loads agree and differ from the live game; " + det)
        else:
            # LOAD_NONDETERMINISTIC (two loads of one save disagree: the census is not the save's alone) or unread
            self.row("A_RELOAD_NO_DUP_LOST", "UNMEASURED", "%s: %s" % (tr.get("verdict"), det))

    def pawns_at(self, rect, corpses=False):
        r = self.c("jawa/list_pawns", rect="%d,%d,%d,%d" % tuple(rect), includeCorpses=corpses, limit=200)
        return r.get("pawns") or []

    def grenade(self, tag):
        """RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES: run 2 read "0 descents" with nothing saying who stood on
        the cover. The riders are read before the blast (living, spawned pawns on the cover cell) and their fate after: no
        rider, or every rider killed by the grenade (a corpse never descends, FlowWorks Building_PitCover.DeSpawn), is a SITE
        miss, UNMEASURED; a living rider without exactly one descent is the mod's FAIL.
        RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES, live run 3 (2026-11-16): the same rider fell once on a fresh
        load of the base save, but read 0 descents in the walk: the cover was not read before the grenade, and the journal
        was cleared first, so a cover the order's shells or raid broke earlier (its rider falling then) read as the mod's
        FAIL. The cover is read before the grenade; gone already is a SITE miss, UNMEASURED, naming the earlier descents."""
        before = [r.get("thing") for r in self.journal()
                  if r.get("type") == "descent" and list(r.get("at") or []) == list(self.cover)]
        cov0 = self.c("jawa/list_things", rect="%d,%d,1,1" % self.cover, limit=20).get("things") or []
        lid0 = [t.get("def") for t in cov0 if str(t.get("def", "")).startswith("RM_PitCover")]
        self.kp("Clear")
        riders = [p.get("id") for p in self.pawns_at((self.cover[0], self.cover[1], 1, 1))
                  if p.get("id") and p.get("spawned", True) and not p.get("dead")]
        e = self.c("jawa/explosion_at", at="%d,%d" % self.cover, radius=GRENADE[1], damType=GRENADE[0])
        self.step(self.a.settle)
        recs = self.journal()
        cov = self.c("jawa/list_things", rect="%d,%d,1,1" % self.cover, limit=20).get("things") or []
        still = [t.get("def") for t in cov if str(t.get("def", "")).startswith("RM_PitCover")]
        dead = set(p.get("id") for p in self.pawns_at(self.site, corpses=True) if p.get("dead"))
        desc = [r for r in recs if r.get("type") == "descent"]
        per = collections.Counter(r.get("thing") for r in desc)
        twice = [k for k, n in per.items() if n > 1]
        alive = [i for i in riders if i not in dead]
        self.ev.setdefault("grenade", {})[tag] = {"riders": riders, "killed": sorted(set(riders) & dead),
                                                  "descents": dict(per), "coverBefore": lid0, "earlierDescents": before,
                                                  "riderLines": [r for r in recs if r.get("thing") in riders][:20]}
        det = "grenade %s; cover left %s; riders %s (killed %s); %d descent(s) %s, twice %s" % (
            "ok" if e.get("success") is not False else e, still or "none", riders, sorted(set(riders) & dead), len(desc),
            dict(per), twice)
        if e.get("success") is False:
            return recs, False, det
        if not lid0:
            return recs, "UNMEASURED", "SITE: the cover %d,%d was already gone before the grenade (earlier descents at it: %s); %s" % (
                self.cover + (before or "none", det))
        if not riders:
            return recs, "UNMEASURED", "SITE: nobody living stood on the cover %d,%d when the grenade went off; %s" % (
                self.cover + (det,))
        if not alive and not still and not twice:
            return recs, "UNMEASURED", "SITE: the grenade killed every rider, and a corpse never descends; " + det
        ok = not still and not twice and all(per.get(i) == 1 for i in alive)
        return recs, ok, det

    def gas_act(self):
        self.kp("Clear")
        seeded = self.kp("SeedCloud", "current|%d,%d|2|250" % self.gas, type_=VENTGAS)[1]
        f = self.c("jawa/map_fire", action="start", rect="%d,%d,1,1" % self.lit, fireSize=1.0)
        if not f.get("firesStarted"):
            # visit 2: bare soil takes no fire (firesStarted 0): one log of kindling, then once more
            self.c("rimworld/spawn_thing", defName="WoodLog", x=self.lit[0], z=self.lit[1])
            f = self.c("jawa/map_fire", action="start", rect="%d,%d,1,1" % self.lit, fireSize=1.0)
        self.fire_ok = bool(f.get("firesStarted"))
        quiet, last = 0, 0
        for _ in range(self.a.gas_ticks // 60):
            self.step(60)
            n = sum(1 for r in self.journal() if r.get("type") == "gas_burst")
            quiet = quiet + 1 if n == last else 0
            last = n
            if n and quiet >= 2:
                break
        recs = self.journal()
        self.kp("ClearOf", "current", type_=VENTGAS)
        self.ev.setdefault("gas", []).append({"seeded": seeded, "fire": {k: f.get(k) for k in ("success", "firesStarted")}})
        return recs

    # ---- judging a window of journal records
    def judge_gas(self, tag, recs):
        if not getattr(self, "fire_ok", True):
            self.unmeasured([tag + "_GAS_CLUMP_BY_CLUMP", tag + "_GAS_GOODS_MOVED"],
                            "UNMEASURED: no fire started on the lit cell %s (jawa/map_fire firesStarted 0, kindling too)" % (self.lit,))
            return
        b = [r for r in recs if r.get("type") == "gas_burst"]
        cells = [tuple(r.get("at") or ()) for r in b]
        ticks = sorted(set(r.get("tick") for r in b))
        d = lambda c: math.hypot(c[0] - self.lit[0], c[1] - self.lit[1]) if len(c) == 2 else 0.0  # noqa: E731
        means = [sum(d(tuple(r["at"])) for r in b if r.get("tick") == t) / max(1, sum(1 for r in b if r.get("tick") == t)) for t in ticks]
        ordered = all(means[i + 1] >= means[i] - 1.0 for i in range(len(means) - 1))
        # run 2 read "31 bursts, 23 distinct cells" and kept no burst: the repeated cells and their ticks are the evidence
        # that tells a re-lit cell (gas drifted back onto a cell still on fire) from one cell burst twice in a tick
        again = dict((str(c), sorted(r.get("tick") for r in b if tuple(r.get("at") or ()) == c))
                     for c in set(cells) if cells.count(c) > 1)
        self.ev.setdefault("gas_bursts", {})[tag] = [[r.get("tick"), r.get("at"), r.get("exp"), r.get("queued")] for r in b]
        self.row(tag + "_GAS_CLUMP_BY_CLUMP", len(b) >= 3 and len(ticks) >= 2 and len(set(cells)) == len(cells) and ordered,
                 "%d bursts on %d ticks, %d distinct cells; mean distance from lit %s by tick %s; burst again %s" % (
                     len(b), len(ticks), len(set(cells)), self.lit, [round(m, 1) for m in means][:12],
                     dict(list(sorted(again.items()))[:6])))
        ids = set(r.get("exp") for r in b)
        moves = [r for r in recs if r.get("type") in ("item_move", "launch") and r.get("exp") in ids]
        self.row(tag + "_GAS_GOODS_MOVED", bool(b) and any(r.get("type") == "item_move" for r in moves),
                 "%d throw(s) from %d burst(s)" % (len(moves), len(ids)))

    def judge_plan(self, tag, recs):
        reqs = [r for r in recs if r.get("type") == "request"]
        out = set((r.get("exp"), r.get("thing")) for r in recs if r.get("type") != "request" and r.get("thing"))
        # RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES: a pawn the blast KILLS is requested by its own name and
        # executed as its corpse (RM_MapComponent_Knockback.Resolve), so every outcome line names Corpse_<race><id>. Such a
        # request is answered by an outcome of the same blast for a Corpse_<its def> that had no request of its own, one each.
        asked = set((r.get("exp"), r.get("thing")) for r in reqs)
        corpses = collections.defaultdict(list)
        for r in recs:
            k = (r.get("exp"), r.get("thing"))
            if r.get("type") != "request" and str(r.get("def", "")).startswith("Corpse_") and k not in asked \
                    and r.get("thing") not in corpses[(r.get("exp"), r.get("def"))]:
                corpses[(r.get("exp"), r.get("def"))].append(r.get("thing"))
        bad, killed = [], []
        for r in reqs:
            if (r.get("exp"), r.get("thing")) in out:
                continue
            pool = corpses.get((r.get("exp"), "Corpse_%s" % r.get("def")))
            if pool:
                killed.append("%s as %s" % (r.get("thing"), pool.pop(0)))
            else:
                bad.append("%s exp %s: no outcome" % (r.get("thing"), r.get("exp")))
        if killed:
            self.ev.setdefault("killed_by_blast", {})[tag] = killed
        for r in recs:
            t, pl, ce, stop = r.get("type"), r.get("planned"), r.get("cells"), str(r.get("stop"))
            if t == "launch" and isinstance(pl, (int, float)) and isinstance(ce, (int, float)):
                if ce > pl or (ce < pl and stop in ("None", "")):
                    bad.append("%s launch %s of %s planned, stop %s" % (r.get("thing"), ce, pl, stop))
            if t == "item_move":
                if r.get("wildCells") != pl or "kernelCells" not in r:
                    bad.append("%s item_move planned %s wild %s kernel %s" % (r.get("thing"), pl, r.get("wildCells"), r.get("kernelCells")))
        if not reqs:
            self.row(tag + "_REQUESTS_MATCH_PLAN", "UNMEASURED", "no throw request in the order's journal")
        else:
            self.row(tag + "_REQUESTS_MATCH_PLAN", not bad, "%d requests, %d mismatch(es): %s; answered by a corpse: %s" % (
                len(reqs), len(bad), bad[:4], killed[:4]))

    def judge_impacts(self, tag, cells, recs, ok_all):
        inside = [r for r in recs if r.get("type") == "request" and _in_rect(tuple(r.get("centre") or ()), self.room)]
        thrown = [r for r in recs if r.get("type") in ("launch", "item_move")]
        if not self.ev.get("raid", {}).get("success", True):
            self.row(tag + "_IMPACTS_IN_ROOM", "UNMEASURED", "the raid did not fire: %s" % self.ev["raid"])
            return
        self.row(tag + "_IMPACTS_IN_ROOM", ok_all and inside and thrown,
                 "%d shell(s) at %s; %d request(s) centred in the storeroom, %d throw(s)" % (len(cells), cells, len(inside), len(thrown)))

    # ---- the walk
    def order(self, tag, gas_first):
        # RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES, live 2026-11-16: the first storeroom shell broke the cover
        # (102,36, 4.5 cells off) within 120 ticks and its rider fell then, so a grenade thrown after the shells always met a
        # broken cover. The scripted grenade goes first in each order; the shells and the gas follow.
        gr, ok, det = self.grenade(tag)
        self.row(tag + "_COVER_BROKEN_ONE_DESCENT", ok, det)
        recs = list(gr)
        if gas_first:
            g = self.gas_act()
            self.judge_gas(tag, g)
            recs += g
        cells, m, ok_all, miss = self.mortars(tag, midair=(tag == "A"))
        self.judge_impacts(tag, cells, m, ok_all)
        self.row(tag + "_REACHED_ACCOUNTED", "UNMEASURED" if not cells else not miss,
                 "%d thing(s) inside a shell's radius with no journal line: %s" % (len(miss), miss[:5]))
        recs += m
        if not gas_first:
            g = self.gas_act()
            self.judge_gas(tag, g)
            recs += g
        self.judge_plan(tag, recs)

    def frame_act(self, arm):
        """FRAME_BUDGET arm `on` or `off` (the mod off), each on a fresh baseline reload: the clock runs at speed 1, the
        shells go off over the stocked storeroom, and the probe reads real frames. The order acts step paused ticks and
        hold no real frames; an arm at the end of order A met an emptied room and measured nothing in the air (live,
        visit 3 run 2: p99 59.3 ms, maxInAir 0, a FAIL that was full-list noise). The row is judged in frame_row."""
        import time
        wait = SLEEP or time.sleep
        secs = float(self.a.frame_seconds)
        readings = self.ev.setdefault("frame_arms", {}).setdefault(arm, [])
        b = self.kp("Frame", "begin")[1]
        if not b.startswith("BEGUN"):
            readings.append({"why": "Frame begin answered %r" % b[:200]})
            return
        # CARRIER_TICK_COST is read in the `on` arm, on a running clock: jawa/time_perf's meanTickTime reads 0.0 on a
        # paused one (live, visit 3: every walk on record read "0.0 ms at rest, 0.0 ms with carriers in the air", PASS)
        moving = self.run_clock(wait)
        self.ev.setdefault("frame_clock", {})[arm] = moving
        wait(2.0)
        if arm == "on" and "tick_rest_running" not in self.ev:
            self.ev["tick_rest_running"] = self.perf()
        cx, cz = self.room[0] + self.room[2] // 2, self.room[1] + self.room[3] // 2
        for x, z in [(cx, cz), (cx - 1, cz + 1), (cx + 1, cz - 1)][:max(1, self.a.shells)]:
            self.c("jawa/explosion_at", at="%d,%d" % (x, z), radius=SHELL[1], damType=SHELL[0])
        wait(1.0)
        if arm == "on" and "tick_air_running" not in self.ev:
            self.ev["tick_air_running"] = self.perf()
            self.ev["in_air_at_tick_read"] = len([l for l in self.kp("Flights")[1].splitlines() if l and not l.startswith("NONE")])
        wait(max(0.0, secs - 1.0))
        self.c("rimworld/set_time_speed", speed=0)
        r = self.kp("Frame", "stop,0.5,%g" % (secs + 2.0))[1]
        num = lambda k: re.search(k + r"=([0-9.]+)", r)  # noqa: E731
        p99, rows, air = num("windowP99Ms"), num("windowRows"), num("maxInAir")
        readings.append({"text": r[:400], "p99": float(p99.group(1)) if p99 else None,
                         "rows": int(rows.group(1)) if rows else 0, "inAir": int(air.group(1)) if air else 0})

    def run_clock(self, wait, tries=6):
        """Unpause at speed 1 until the clock is seen moving -> the tries it took, or 0 if it never moved. Live, visit 3
        run 3: set_time_speed 1 right after a baseline reload did not hold (Prefs.PauseOnLoad pauses again on a later
        frame), and both frame arms read every frame paused (paused=621)."""
        for n in range(1, tries + 1):
            self.c("rimworld/set_time_speed", speed=1)
            wait(0.5)
            t0 = self.c("jawa/time_clock").get("ticksGame")
            wait(0.5)
            t1 = self.c("jawa/time_clock").get("ticksGame")
            if isinstance(t0, int) and isinstance(t1, int) and t1 > t0:
                return n
        return 0

    def frame_row(self):
        """FRAME_BUDGET, judged against its own mod-off arm (owner, by card 2026-11-16, "Compare to mod-off": "Pass if
        mod-on is within 10% of the same colony's mod-off run"): PASS when the `on` arm's 99th-percentile unpaused frame is
        at most 10% over the `off` arm's, FAIL over it. UNMEASURED, never PASS, when either arm has no reading (no p99, too
        few frames), the off arm reads 0 ms or less (nothing to compare to), nothing flew in the on arm's window, or the
        arms' frame counts are not like for like. Each side is the median of its interleaved arms (pool_arms). Live,
        visit 3 run 4: the walk colony's mod-off floor alone was p99 80.2 ms, so the 50 ms barrage bar could not decide it."""
        arms = self.ev.get("frame_arms")
        if arms is not None:
            self.ev["frame_on"], self.ev["frame_off"] = pool_arms(arms.get("on") or []), pool_arms(arms.get("off") or [])
        on, off = self.ev.get("frame_on") or {}, self.ev.get("frame_off") or {}
        det = "on p99 %s ms (%s rows, %s in the air), mod off p99 %s ms (%s rows), PASS at most +%d%%; on: %s; off: %s" % (
            on.get("p99"), on.get("rows"), on.get("inAir"), off.get("p99"), off.get("rows"), round(FRAME_OVER_OFF * 100),
            on.get("text") or on.get("why") or "no on arm", off.get("text") or off.get("why") or "no off arm")
        read = lambda a: isinstance(a.get("p99"), (int, float)) and (a.get("rows") or 0) >= FRAME_MIN_ROWS  # noqa: E731
        each = (on.get("rows_each") or [on.get("rows") or 0]) + (off.get("rows_each") or [off.get("rows") or 0])
        if not read(on):
            self.row("FRAME_BUDGET", "UNMEASURED", "no mod-on frame reading: " + det)
        elif not read(off):
            self.row("FRAME_BUDGET", "UNMEASURED", "no mod-off frame reading: " + det)
        elif off["p99"] <= 0:
            self.row("FRAME_BUDGET", "UNMEASURED", "mod-off p99 is not above 0, nothing to compare to: " + det)
        elif not on.get("inAir"):
            self.row("FRAME_BUDGET", "UNMEASURED", "nothing in the air in the window: " + det)
        elif max(each) > FRAME_ROWS_LIKE * min(each):
            # a p99 over frames is diluted by frame count: live, run 5 (2026-11-16), the off arm ran uncapped from 5 s
            # (863 window frames at ~7 ms against the on arm's 498 at 60 fps) and read 37.1 ms against 91.3 though it
            # stalled more often (8 frames over 50 ms, against 5). Rerun; the two arms must run at the same frame cap.
            self.row("FRAME_BUDGET", "UNMEASURED", "arms not like for like (window frames %s on, %s off, over x%g; a p99 "
                     "over frames falls as the frame rate rises): %s" % (on.get("rows_each") or on["rows"],
                                                                         off.get("rows_each") or off["rows"], FRAME_ROWS_LIKE, det))
        else:
            over = on["p99"] / off["p99"] - 1.0
            self.row("FRAME_BUDGET", "PASS" if over <= FRAME_OVER_OFF else "FAIL", "%+.1f%% over mod off; %s" % (over * 100, det))

    def control(self):
        """The mod off (run() turns it off inside its try, whose finally puts every setting back)."""
        before = dict((_num(t.get("id")), _pos(t)) for t in self.haulables(self.room))
        cells, recs, ok_all, _m = self.mortars("C")
        after = dict((_num(t.get("id")), _pos(t)) for t in self.haulables(self.room))
        moved = [i for i, p in after.items() if i in before and before[i] != p]
        thrown = [r for r in recs if r.get("type") in ("launch", "item_move")]
        self.row("C_OFF_IMPACTS_NO_THROWS", ok_all and not thrown and not moved and before,
                 "mod off: %d shell(s) went off (%s), %d throw line(s), %d of %d storeroom stack(s) moved" % (
                     len(cells), "all" if ok_all else "NOT all", len(thrown), len(moved), len(before)))

    def run(self):
        if self.a.save:
            ok, why = self.load(self.a.save)
            if not ok:
                raise WalkRefused("--save %s never reached Playing (%s)" % (self.a.save, why))
        self.c("rimworld/set_time_speed", speed=0)
        miss = self.preconditions()
        if miss == "RELEASE":
            return 3
        self.row("W_PRECONDITIONS", "INVALID" if miss else "PASS", "; ".join(miss) or "full list, FlowWorks, Cauldron gas, shelves, closed container, cover")
        if miss:
            self.unmeasured(WALK_ROWS, "UNMEASURED: preconditions not met")
            return 1
        snap = {}
        for f in sorted(settings_fields()):
            r = self.c("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="get", field=f)
            if r.get("success", True) is not False and "value" in r:
                snap[f] = r["value"]
        base = "EK_WALK_RAID_BASE_" + self.a.stamp
        try:
            self.kp("Settings", "reset")
            self.save(base)
            self.ev["tick_rest"] = self.perf()
            if self.a.raid_points > 0:
                rr = self.c("jawa/fire_raid", points=float(self.a.raid_points), dryRun=False)
                self.ev["raid"] = {k: rr.get(k) for k in ("success", "blockedByDialog", "pawnsArrivedTotal", "exc")}
            self.order("A", gas_first=False)
            # the frame arms run as interleaved pairs (on, off, on, off, ...): one pair's p99 is decided by one random
            # stall (live 2026-11-16, runs 4-6: the off arm alone read 80.2, 37.1 and 38.1 ms); frame_row takes medians
            arms = [("FRAME_ON", lambda: self.frame_act("on")), ("FRAME_OFF", lambda: self.frame_act("off"))]
            for tag, fn in [("B", lambda: self.order("B", gas_first=True)), ("C", self.control)] + arms * max(1, self.a.frame_pairs):
                ok, why = self.load(base)
                if not ok:
                    self.unmeasured([r for r in WALK_ROWS if r.startswith(tag)], "UNMEASURED: baseline reload failed (%s)" % why)
                    if tag.startswith("FRAME"):
                        self.ev.setdefault("frame_arms", {}).setdefault(tag[6:].lower(), []).append(
                            {"why": "baseline reload failed (%s)" % why})
                    continue
                self.kp("Settings", "reset")
                if self.a.raid_points > 0:                  # B and the control C face the same raid
                    self.c("jawa/fire_raid", points=float(self.a.raid_points), dryRun=False)
                if tag in ("C", "FRAME_OFF"):
                    self.kp("Settings", "enabled=False")
                fn()
        finally:
            self.kp("Plant", "reset")
            self.load(base)
            for f, v in snap.items():
                self.c("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=f, value=str(v))
        air, rest = self.ev.get("tick_air_running"), self.ev.get("tick_rest_running")
        seen = isinstance(air, (int, float)) and isinstance(rest, (int, float)) and air > 0 and rest > 0
        self.row("CARRIER_TICK_COST", "PASS" if seen else "UNMEASURED",
                 "meanTickTime %s ms at rest, %s ms 1 s after the shells with %s carrier(s) in the air, clock running "
                 "(recorded, not judged)%s" % (rest, air, self.ev.get("in_air_at_tick_read"),
                                                "" if seen else ": a reading of 0 or none is a blind instrument"))
        self.frame_row()
        return 0


def _walk_args(argv):
    import argparse
    import datetime
    ap = argparse.ArgumentParser(prog="validation.py --live walk_storeroom_raid")
    ap.add_argument("--storeroom", required=True, help="storeroom interior rect x,z,w,h")
    ap.add_argument("--cover", required=True, help="the covered pit trap's cell x,z")
    ap.add_argument("--gas", required=True, help="vent-gas cloud centre x,z (radius 2, 250)")
    ap.add_argument("--lit", default=None, help="the cell the Fire is set on (default 2 west of --gas)")
    ap.add_argument("--save", default=None, help="load this throwaway colony first")
    ap.add_argument("--site", default=None, help="census rect x,z,w,h (default: around the storeroom, cover and gas)")
    ap.add_argument("--shelf-defs", default="Shelf,ShelfSmall")
    ap.add_argument("--shells", type=int, default=3)
    ap.add_argument("--settle", type=int, default=120, help="ticks after each blast")
    ap.add_argument("--frame-seconds", type=float, default=8.0, help="real seconds at speed 1 for FRAME_BUDGET")
    ap.add_argument("--frame-pairs", type=int, default=3, help="interleaved mod-on/mod-off frame arm pairs for FRAME_BUDGET")
    ap.add_argument("--gas-ticks", type=int, default=900)
    ap.add_argument("--raid-points", type=float, default=300.0, help="0 skips the real raid")
    ap.add_argument("--full-min", type=int, default=100, help="active mods below this are not the full list")
    ap.add_argument("--out", default=None)
    ap.add_argument("--stamp", default=datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
    return ap.parse_args(argv)


def walk_storeroom_raid(argv=None, bridge=None, wait=None, out=sys.stdout):
    """The walk leaf. Returns the exit code: 0 every row PASS, 1 otherwise, 2 refused (no bridge / no game), 3 release DLL."""
    a = _walk_args(argv if argv is not None else [])
    close = None
    try:
        if bridge is None:
            sys.path.insert(0, _UTILS)
            from rimbridge_client import RimBridge, resolve_endpoint
            host, port, token = resolve_endpoint()
            rb = RimBridge(host=host, port=port, token=token)
            rb.__enter__()
            close = rb

            class _Adapter:
                def call(self, tool, _answer=False, **kw):
                    return rb.call(tool, kw, check=not _answer)
            bridge = _Adapter()
        if wait is None:
            from validation_core import _wait_playing
            wait = lambda B: _wait_playing(B, leave_s=10)  # noqa: E731
        w = _Walk(bridge, a, wait)
        code = w.run()
    except WalkRefused as e:
        print("REFUSED walk_storeroom_raid: %s" % e, file=out)
        return 2
    except Exception as e:  # noqa: BLE001 - no bridge is a refusal, never STATIC: PASS
        import traceback
        tb = traceback.extract_tb(e.__traceback__)
        where = "%s:%d %s" % (os.path.basename(tb[-1].filename), tb[-1].lineno, tb[-1].name) if tb else "?"
        print("REFUSED walk_storeroom_raid: no game reachable over the bridge (%s: %s, at %s). Run with python.exe, a game "
              "Playing, the bridge held." % (type(e).__name__, str(e)[:200], where), file=out)
        return 2
    finally:
        if close is not None:
            try:
                close.__exit__(None, None, None)
            except Exception:  # noqa: BLE001
                pass
    if code == 3:
        print(PROOF_BUILD_MESSAGE, file=out)
        return 3
    path = a.out or os.path.join(os.environ.get("RM_SCRATCH", r"D:\ClaudeWork\rimmandrake"), "ek_proof",
                                 "walk_storeroom_raid_%s.json" % a.stamp)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"rows": w.rows, "ev": w.ev}, fh, indent=1, default=str)
    except OSError as e:
        path = "NOT WRITTEN (%s)" % e
    print("%-28s %-10s %s" % ("ROW", "STATUS", "DETAIL"), file=out)
    for rid in WALK_ROWS:
        st, det = w.rows.get(rid, ("UNMEASURED", "not reached"))
        print("%-28s %-10s %s" % (rid, st, det), file=out)
    print("evidence: %s   throwaway saves: %s" % (path, w.ev.get("saves")), file=out)
    return 0 if all(w.rows.get(r, ("",))[0] == "PASS" for r in WALK_ROWS) else 1


LIVE_LEAVES = {"walk_storeroom_raid": walk_storeroom_raid}


if __name__ == "__main__":
    if "--live" in sys.argv:
        rest = sys.argv[sys.argv.index("--live") + 1:]
        leaf = rest[0] if rest and not rest[0].startswith("-") else None
        if leaf not in LIVE_LEAVES:
            print("REFUSED --live: name a leaf (%s); the scene chains run through modcheck" % ", ".join(sorted(LIVE_LEAVES)))
            sys.exit(2)
        sys.exit(LIVE_LEAVES[leaf](rest[1:]))
    if "--criteria" in sys.argv:
        print("\n".join(criteria_lines()))
        sys.exit(0)
    if "--mock" in sys.argv:
        sys.path.insert(0, os.path.join(HERE, "..", "Utils", "modcheck"))
        sys.exit(mock_run())
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
