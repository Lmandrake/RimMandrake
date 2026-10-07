"""validation.py -- modcheck suite for RimMandrake: Kinetic Arms (mandrake.rm.kineticarms).

First functional script (design/RimMandrake/debug_process.md §2). Walk: design/validation_walks/RimMandrake/KineticArms.md.
Design: design/RimMandrake/kinetic_blast_weapons_design_2026-10-06.md (§3, §10).

Every behaviour chain drives ONE in-game scene through jawa/static_call on RimMandrake.KineticArms.RM_KineticArmsProof:
Stage("<scene>,x,z") builds it on a cleared 15x15 patch and fires the weapon's REAL projectile (or the kicker mine's
Kick), rimworld/step_game_ticks resolves it, Verdict("<scene>") reads Explosive Knockback's journal plus map state.
A component PASSes only on a PASS verdict; INVALID records UNMEASURED, never PASS.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PROOF = "RimMandrake.KineticArms.RM_KineticArmsProof"
WALK = os.path.join(REPO, "design", "validation_walks", "RimMandrake", "KineticArms.md")
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")

# scene -> (chain, component, toggle it exercises or None)
SCENES = [
    ("thump_cannon", "thump", "thump_bomb_beside_human_throws_farther_than_mortar", "thumpCannonForce"),
    ("thump_off", "thump", "thump_off_throws_nothing", "thumpCannonThrows"),
    ("thudder_crowd", "grenades", "thudder_clears_a_cluster_without_killing", "enableThudder"),
    ("slam_charge", "grenades", "slam_charge_throws", "enableSlamLauncher"),
    ("thump_shell", "grenades", "thump_shell_throws", "enableThumpShell"),
    ("palm_shove", "bolts", "palm_shove_along_shot_no_wound", "enablePalmThumper"),
    ("repulsor_along_shot", "bolts", "repulsor_pushes_along_shot", "enableRepulsorRifle"),
    ("repulsor_westward", "bolts", "repulsor_westward_wraps", None),
    ("grav_ram", "bolts", "grav_ram_throws_hardest", "enableGravRam"),
    ("kicker_north", "kicker", "kicks_north", "enableKickerMine"),
    ("kicker_east", "kicker", "kicks_east", None),
    ("kicker_south", "kicker", "kicks_south", None),
    ("kicker_west", "kicker", "kicks_west", None),
    ("kicker_dud_rearm", "kicker", "dud_when_empty_rearms_with_fuel", "kickerRearms"),
    ("pulse_push", "pulse", "pulse_wave_pushes_away_from_turret", "enablePulseCannon"),
    ("pulse_charge_gate", "pulse", "no_charge_no_target", "pulseCapacity"),
    ("strength_zero", "settings", "strength_zero_throws_nothing", "kineticStrength"),
    ("looted_pirates", "factions", "pirates_only_rarely_carry_looted", "lootedChancePercent"),
    # 2026-10-06 finish pass (KINETIC_BLAST_WEAPONS_1)
    ("palm_arrest_wall", "bolts", "palm_shove_into_wall_hurts_nobody", None),
    ("gravram_big_body", "bolts", "grav_ram_moves_a_3_body_repulsor_cannot", None),
    ("ruins_loot", "ruins", "ancient_temple_loot_holds_kinetic_weapons", "foundInRuins"),
    ("kicker_hidden", "kicker", "hidden_from_raiders_unless_setting_off", "kickerHidden"),
    ("cords_marker", "settings", "kinetic_blasts_marked_to_spare_cords", "kineticCutsCords"),
    ("ring_fleck", "fx", "kinetic_ring_fleck_texture_resolves", None),
]
NOT_DRIVEN = [
    ("walk_on_spring", "a pawn pathing onto an armed plate (spring chance); scenes call Kick() directly"),
    ("ai_use", "pirate raiders firing them sensibly needs a live raid; looted_pirates proves only who carries them"),
    ("cords_sway_live", "a kinetic blast under a Gimme Some Slack span leaving it whole needs a strung span (GSS tier)"),
    ("temple_generates_live", "a generated ancient-danger temple holding the loot needs a map with a shrine"),
]

# The validation ladder (rimflow model.LEVELS). `python3 validation.py --criteria` prints `ID LEVEL: text` lines.
CRITERIA = [
    ("KA.K", "L0", "kernel selftest KA-01..KA-16 PASS (selftest_kineticarms_kernel.py)"),
    ("KA.static", "L0", "validation.py STATIC PASS: defs/art/patch/settings/GSS-marker wiring, walk coverage"),
    ("KA.mock", "L0", "validation.py --mock stages every scene"),
    ("KA.load", "L1", "explosiveknockback tier + kineticarms loads, no red error; fleck and ruins maker resolve"),
    ("KA.scenes18", "L2", "the 18 v1 scenes still PASS on the rebuilt DLLs"),
    ("KA.new6", "L2", "palm_arrest_wall, gravram_big_body, ruins_loot, kicker_hidden, cords_marker, ring_fleck PASS"),
    ("KA.cords", "L2", "with Gimme Some Slack: repulsor blast under a span leaves it whole; a frag grenade cuts it"),
    ("KA.temple", "L2", "a debug-generated ancient temple (chance 100) holds one kinetic weapon or minified mine/cannon"),
    ("KA.shield", "L2", "a repulsor hit on a shield-belted raider: not thrown, belt drained (EK shield_counter via KA)"),
    ("KA.feel", "L4", "owner: a repulsor line reads as a moving wall; a kicker mine at a pit lip as an ejection gate"),
]


def settings_fields():
    src = open(os.path.join(HERE, "Source", "RM_KineticArmsMod.cs"), encoding="utf-8").read()
    body = src.split("class RimMandrakeKineticArmsSettings", 1)[1].split("public override void ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    fields = settings_fields()
    if len(fields) < 12:
        bad.append("settings probe found %d fields (sanity probe failed)" % len(fields))
    proof = open(os.path.join(HERE, "Source", "RM_KineticArmsProof.cs"), encoding="utf-8").read()
    for scene, _c, _k, toggle in SCENES:
        if '"%s"' % scene not in proof:
            bad.append("scene %s missing from RM_KineticArmsProof" % scene)
        if toggle and toggle not in fields:
            bad.append("scene %s names unknown toggle %s" % (scene, toggle))
    csproj = open(os.path.join(HERE, "Source", "RimMandrake_KineticArms.csproj"), encoding="utf-8").read()
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
    """Offline (L0) proof of the shipped wiring: per-weapon knockback values, ruins loot, art, settings, GSS marker."""
    import xml.etree.ElementTree as ET
    bad = []
    defs = {}
    for root, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for f in files:
            if f.endswith(".xml"):
                for el in ET.parse(os.path.join(root, f)).getroot():
                    key = el.findtext("defName") or el.get("Name")
                    if key:
                        defs[(el.tag, key)] = el

    def ext(dd):
        el = defs.get(("DamageDef", dd))
        for li in (el.find("modExtensions") if el is not None and el.find("modExtensions") is not None else []):
            if li.get("Class", "").endswith("RM_KnockbackExtension"):
                return li
        return None
    palm, ram = ext("RM_Repulse_Palm"), ext("RM_Repulse_GravRam")
    if palm is None or palm.findtext("impactFactor") != "0":
        bad.append("RM_Repulse_Palm lacks impactFactor 0 (palm thumper is the arrest tool)")
    if ram is None or ram.findtext("immuneBodySizeOverride") != "3.6":
        bad.append("RM_Repulse_GravRam lacks immuneBodySizeOverride 3.6")
    for base in ("RM_ConcussiveBase", "RM_RepulseBase"):
        el = defs.get(("DamageDef", base))
        mx = el.find("modExtensions") if el is not None else None
        if mx is None or not any(li.get("Class", "").endswith(".RM_KineticBlastExtension") for li in mx):
            bad.append("%s does not carry the RM_KineticBlastExtension cord marker" % base)
    # every texPath a Kinetic Arms def names resolves to a PNG in this mod
    for (tag, key), el in defs.items():
        for tp in el.iter("texPath"):
            png = os.path.join(HERE, "Textures", tp.text.strip() + ".png")
            if not os.path.isfile(png):
                bad.append("%s %s texPath %s has no PNG" % (tag, key, tp.text.strip()))
    fl = defs.get(("FleckDef", "RM_Fleck_KineticRing"))
    if fl is None:
        bad.append("FleckDef RM_Fleck_KineticRing missing")
    src = open(os.path.join(HERE, "Source", "RM_KineticRuinsAndCompat.cs"), encoding="utf-8").read()
    patches = "".join(open(os.path.join(HERE, "Patches", f), encoding="utf-8").read() for f in os.listdir(os.path.join(HERE, "Patches")))
    if 'ThingSetMakerDef[defName="MapGen_AncientTempleContents"]/root/options' not in patches \
            or "RimMandrake.KineticArms.RM_ThingSetMaker_KineticRuins" not in patches or "class RM_ThingSetMaker_KineticRuins" not in src:
        bad.append("ruins loot is not wired onto MapGen_AncientTempleContents")
    for tbl in ("MapGen_AncientComplexRoomLoot_Default", "MapGen_AncientComplexRoomLoot_Better", "MapGen_AncientComplex_SecurityCrate"):
        if 'ThingSetMakerDef[defName="%s"]/root/options' % tbl not in patches:
            bad.append("ancient-complex loot is not wired onto %s" % tbl)
    if "RimMandrake.KineticArms.RM_ThingSetMaker_KineticComplex" not in patches or "class RM_ThingSetMaker_KineticComplex" not in src:
        bad.append("RM_ThingSetMaker_KineticComplex missing from the patch or the source")
    if "RuinsWeights" not in open(os.path.join(HERE, "Source", "RM_KineticRuinsAndCompat.cs"), encoding="utf-8").read():
        bad.append("ruins pick ignores the rarity tiers (RM_KineticMath.RuinsWeights)")
    if "class RM_KineticBlastExtension" not in src:
        bad.append("cord marker class missing")
    gss = os.path.join(HERE, "..", "GimmeSomeSlack", "Source", "Aerial", "RM_MapComponent_Aerial.cs")
    if os.path.isfile(gss) and '"RM_KineticBlastExtension"' not in open(gss, encoding="utf-8").read():
        bad.append("Gimme Some Slack's explosion hook does not skip the RM_KineticBlastExtension marker (owner Q3)")
    mod = open(os.path.join(HERE, "Source", "RM_KineticArmsMod.cs"), encoding="utf-8").read()
    weapons = re.findall(r'\("(\w+)", "[^"]+", "(\w+)"\)', mod.split("Weapons =", 1)[1].split("};", 1)[0])
    if len(weapons) != 8:
        bad.append("Weapons table probe found %d rows, want 8" % len(weapons))
    for field, d in weapons:
        if field not in fields:
            bad.append("weapon toggle %s is not a setting" % field)
        if not any(k == d for (_t, k) in defs):
            bad.append("weapon def %s not in Defs" % d)
    expose = mod.split("public override void ExposeData", 1)[1].split("\n        }", 1)[0]
    reset = mod.split("public static void Reset()", 1)[1]
    window = mod.split("DoSettingsWindowContents", 1)[1].split("public static void Reset()", 1)[0]
    toggled = set(f for f, _d in weapons)
    for f in fields:
        if 'ref %s,' % f not in expose:
            bad.append("setting %s is not saved in ExposeData" % f)
        if "RimMandrakeKineticArmsSettings.%s =" % f not in reset:
            bad.append("setting %s is not restored by Reset()" % f)
        if f not in toggled and "RimMandrakeKineticArmsSettings.%s" % f not in window:
            bad.append("setting %s has no control in the settings window" % f)
    bad += load_error_checks(defs, patches)
    prog = open(os.path.join(HERE, "Source", "SelfTest", "Program.cs"), encoding="utf-8").read()
    if '"KA-16 ' not in prog:
        bad.append("kernel selftest has no KA-16 (ruins pick) rows")
    return bad


# Projectile thingClasses that derive from Projectile_Explosive (VerbProperties.CausesExplosion is true for them).
_EXPLOSIVE_CLASSES = ("Projectile_Explosive", "RimMandrake.KineticArms.RM_Projectile_KineticExplosive",
                      "RimMandrake.KineticArms.RM_Projectile_KineticBolt")
# The vanilla pirate gangs that loot (owner 2026-10-06). Each is patched BY NAME: a mod setting Inherit="False" on a
# child's modExtensions (ReGrowth 2 does it to PirateWaster) silently drops anything patched on the Pirate parent.
LOOTER_FACTIONS = ("Pirate", "CannibalPirate", "PirateYttakin", "PirateWaster")


def load_error_checks(defs, patches):
    """L0 repro of the 2026-10-07 full-list load errors and the looted_pirates miss."""
    bad = []
    for (tag, key), el in defs.items():
        if tag != "ThingDef":
            continue
        for v in el.iter("li"):
            proj = v.findtext("defaultProjectile")
            if not proj or v.findtext("verbClass") not in ("Verb_Shoot", "Verb_LaunchProjectile"):
                continue
            p = defs.get(("ThingDef", proj))
            explosive = p is not None and (p.findtext("thingClass") or "") in _EXPLOSIVE_CLASSES
            fmr = float(v.findtext("forcedMissRadius") or 0)
            # VerbProperties.ConfigErrors: (forcedMissRadius > 0) != CausesExplosion is a red config error
            if (fmr > 0) != explosive:
                bad.append("%s verb fires %s (explosive=%s) with forcedMissRadius %s: forcedMiss config error"
                           % (key, proj, explosive, fmr))
        # ThingDef.ConfigErrors: smeltable with no smeltProducts and no costList yields nothing (BaseWeapon is smeltable)
        if el.get("ParentName") in ("BaseWeapon", "BaseGunWithQuality") and el.findtext("smeltable") != "false" \
                and el.find("smeltProducts") is None and el.find("costList") is None:
            bad.append("%s is smeltable but gives nothing for smelting" % key)
    for f in LOOTER_FACTIONS:
        if 'FactionDef[defName="%s"]' % f not in patches:
            bad.append("looter faction %s is not patched by name (inheritance from Pirate is not safe)" % f)
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
    suite = Suite("KineticArms")
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
