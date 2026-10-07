"""validation.py -- modcheck suite for RimMandrake: Explosive Knockback (mandrake.rm.explosiveknockback).

First functional script (design/RimMandrake/debug_process.md §2). Walk: design/validation_walks/RimMandrake/ExplosiveKnockback.md.
Design: design/RimMandrake/explosive_knockback_design_2026-10-06.md (§8).

Every behaviour chain drives ONE in-game scene through jawa/static_call on RimMandrake.ExplosiveKnockback.RM_KnockbackProof:
Stage("<scene>,x,z") builds it on a cleared 15x15 patch and sets the blast off, rimworld/step_game_ticks resolves it
without unpausing, Verdict("<scene>") reads the knockback JOURNAL (request / launch / blocked / item_move / skip /
land / descent records) plus map state. A component PASSes only on a PASS verdict; INVALID (e.g. FlowWorks absent for
a pit scene) records UNMEASURED, never PASS. The same scenes run standalone via knockback_runner.py.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PROOF = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
WALK = os.path.join(REPO, "design", "validation_walks", "RimMandrake", "ExplosiveKnockback.md")
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")

# scene -> (chain, component, toggle it exercises or None)
SCENES = [
    ("calibration", "throw", "mortar_beside_human_throws_3_cells", "strength"),
    ("wall_stop", "throw", "wall_stops_throw_with_impact", "impactDamageEnabled"),
    ("door_stop", "throw", "closed_door_stops_throw_and_takes_a_hit", "doorsTakeDamage"),
    ("over_sandbags", "throw", "thrown_over_sandbags", "sandbagsStopThrow"),
    ("heavy_skip", "throw", "body_size_2_5_is_not_thrown", "immuneBodySize"),
    ("emp_no_throw", "throw", "emp_blast_throws_nothing", "unpatchedHarmfulPercent"),
    ("items", "light_things", "items_thrown_by_mass_heavy_stays", "throwItems"),
    ("shelf", "light_things", "item_on_a_shelf_stays", None),
    ("killed_by_blast", "light_things", "pawn_killed_by_blast_thrown_as_corpse", "throwCorpses"),
    ("pit_colonist", "pits", "colonist_thrown_into_open_pit_falls", "throwIntoPits"),
    ("pit_enemy", "pits", "enemy_thrown_into_open_pit_falls", None),
    ("no_cross", "pits", "throw_stops_inside_a_1_wide_pit", None),
    ("in_pit_skip", "pits", "pawn_already_in_pit_not_thrown", None),
    ("corpse_into_pit", "pits", "corpse_thrown_onto_pit_floor", None),
    ("cover_breaks", "pits", "blast_breaks_cover_and_pawn_on_it_falls", None),
    ("caps", "caps", "per_explosion_cap_holds_pawns_first", "maxThrowsPerExplosion"),
    ("tick_cap", "caps", "per_tick_item_cap_drops_overflow", "maxItemThrowsPerMapTick"),
    ("settings_off", "settings", "master_off_nothing_moves_but_wave_hit", "enabled"),
    # 2026-10-06 finish pass (KINETIC_BLAST_WEAPONS_1): per-blast config, stun-lock guard, shields
    ("lookup_projectile", "config", "projectile_extension_wins_over_damagedef", "ownCapScale"),
    ("lookup_zero_wins", "config", "explicit_zero_on_projectile_throws_nothing", None),
    ("impact_factor", "config", "impact_factor_zero_no_wall_impact", None),
    ("body_override", "config", "body_override_throws_a_3_body_global_does_not", None),
    ("immunity_window", "guards", "second_blast_in_recovery_window_is_immune", "recoveryWindowTicks"),
    ("shield_counter", "guards", "shield_belt_absorbs_throw_and_drains", "shieldsAbsorbThrow"),
]
NOT_DRIVEN = [
    ("hose_carry_drops_at_takeoff", "needs a laid hose reel and a colonist mid CarryHoseEnd job; DropCarriedHose is wired "
     "(RM_KnockbackCompat) but no scene stages a carry yet"),
    ("save_mid_flight", "save with a flyer in the air, reload, pawn exists once: needs a save/load half"),
    ("raid_lord_resumes_duty", "a real assault raid hit by a mortar: needs a raid site"),
    ("vef_active_same_results", "VEF patches PawnFlyer.MakeFlyer/RecomputePosition; needs a VEF tier (ship gate)"),
    ("barrage_perf_ms_per_tick", "performance has no Boolean check (debug_process §4); counts are in the caps chain"),
    ("immunity_survives_reload", "the landing/stun stamps are Scribed on the map component; needs a save/load half"),
]

# The validation ladder (rimflow model.LEVELS): L0 offline, L1 resolved-live on the minimal list, L2 behaviour scenes,
# L4 human. `python3 validation.py --criteria` prints these as `ID LEVEL: text` for `rimflow implemented --criteria-file`.
CRITERIA = [
    ("EK.K", "L0", "kernel selftest K-01..K-16 PASS (selftest_explosiveknockback_kernel.py)"),
    ("EK.static", "L0", "validation.py STATIC PASS: config lookup, shield/landing hooks, settings saved+reset, walk coverage"),
    ("EK.mock", "L0", "validation.py --mock stages every scene"),
    ("EK.load", "L1", "explosiveknockback tier loads with no red error from this mod; Harmony patches applied"),
    ("EK.scenes18", "L2", "the 18 v1 scenes still PASS after the 2026-10-06 config/guard/shield change"),
    ("EK.config", "L2", "lookup_projectile, lookup_zero_wins, impact_factor, body_override PASS"),
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
    for f in ("force", "maxThrowCells", "impactFactor", "immuneBodySizeOverride"):
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
    window = mod.split("DoSettingsWindowContents", 1)[1].split("public static void Reset()", 1)[0]
    for f in fields:
        if 'ref %s,' % f not in expose:
            bad.append("setting %s is not saved in ExposeData" % f)
        if "RimMandrakeExplosiveKnockbackSettings.%s =" % f not in reset:
            bad.append("setting %s is not restored by Reset()" % f)
        if "RimMandrakeExplosiveKnockbackSettings.%s" % f not in window:
            bad.append("setting %s has no control in the settings window" % f)
    prog = open(os.path.join(HERE, "Source", "SelfTest", "Program.cs"), encoding="utf-8").read()
    for k in ("K-13", "K-14", "K-15", "K-16"):
        if '"%s ' % k not in prog:
            bad.append("kernel selftest has no %s rows" % k)
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
                raise ExpectationFailed("static_call %s failed: %r" % (method, r))
            return str(r.get("result", r.get("value", "")))
        return str(r)

    def _origin(t):
        if state["origins"] is None:
            state["origins"] = _call(t, "Origins", str(len(SCENES))).split(";")
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


if __name__ == "__main__":
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
