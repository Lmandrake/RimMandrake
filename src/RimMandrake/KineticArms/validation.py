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
]
NOT_DRIVEN = [
    ("walk_on_spring", "a pawn pathing onto an armed plate (spring chance); scenes call Kick() directly"),
    ("ai_use", "pirate raiders firing them sensibly needs a live raid; looted_pirates proves only who carries them"),
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
    if "--mock" in sys.argv:
        sys.path.insert(0, os.path.join(HERE, "..", "Utils", "modcheck"))
        sys.exit(mock_run())
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
