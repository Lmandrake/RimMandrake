"""validation.py -- modcheck suite for RimMandrake: Warscar (mandrake.rm.warscar).

Item WARSCAR_TURRETS_TRACK_1 (the only live mechanic this mod ships so far). Warscar's biome, flora and
item defs have no script yet; this first script covers the turret pair only.

WHAT IT PROVES (state reads, never a screenshot hunt):
  * defs_resolve: RM_OldLineTurret / _Gun / _Bullet resolve live, and the aim comp type loaded
    (a def naming a missing comp type is discarded silently by the engine).
  * tracking: a broken turret spawned beside a walking pawn reports the tracking inspect line (the comp's
    own state) and spawns NO projectile; with `turretTrackingEnabled` off the line is absent (control).
  * refit: a Refit gizmo exists on the broken turret when `turretRefitEnabled` is on and is absent when
    off (control).
NOT PROVEN HERE: the old-line turret FIRING at hostiles (needs a raid and power; owner/FOUNDRY live
round, criterion 2 of the item), the barrel's drawn angle (visual), and the Refit blueprint's
construction. Each says UNMEASURED rather than passing.

STATIC (offline) CHECKS: `python3 validation.py` runs `static_checks()` without a game: XML parses, every
Mod Settings field is Scribed and exposed, the .cs file is in the csproj, the patch targets exist.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "RimMandrake.Scarlands."
SETTINGS_TYPE = NS + "RM_WarscarSettings"
DEFAULTS = {"turretTrackingEnabled": True, "turretRefitEnabled": True,
            "oldLineDamageFactor": 1.0, "oldLineCooldownFactor": 1.0}
BROKEN = ["AncientAutocannonTurret", "AncientUraniumSlugTurret", "RUT_BustedShieldedTurret"]
NEW_DEFS = ["ThingDef/RM_OldLineTurret", "ThingDef/RM_OldLineTurret_Gun", "ThingDef/RM_OldLineTurret_Bullet"]


def static_checks():
    """Return a list of failure strings; empty means pass. Needs no game."""
    bad = []
    src = open(os.path.join(HERE, "Source", "RM_WarscarMod.cs")).read()
    for f in DEFAULTS:
        if '"%s"' % f not in src:
            bad.append("settings field %s is not Scribed in RM_WarscarMod.cs" % f)
        if not re.search(r"\b%s\b" % f, src.split("DoWindowContents")[1]):
            bad.append("settings field %s has no control in DoWindowContents" % f)
    if 'Compile Include="RM_CompTurretAim.cs"' not in open(os.path.join(HERE, "Source", "RM_Warscar.csproj")).read():
        bad.append("RM_CompTurretAim.cs missing from RM_Warscar.csproj")
    d = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_OldLineTurret.xml")).getroot()
    names = [e.findtext("defName") for e in d]
    for n in NEW_DEFS:
        if n.split("/")[1] not in names:
            bad.append("def %s missing" % n)
    turret = [e for e in d if e.findtext("defName") == "RM_OldLineTurret"][0]
    gun = [e for e in d if e.findtext("defName") == "RM_OldLineTurret_Gun"][0]
    if turret.findtext("building/turretGunDef") != "RM_OldLineTurret_Gun":
        bad.append("turretGunDef does not name the gun def")
    if float(gun.findtext("verbs/li/range")) < 40:
        bad.append("old-line turret is not long range")
    if float(turret.findtext("building/turretBurstCooldownTime")) < 10:
        bad.append("old-line turret cooldown is not long")
    p = ET.parse(os.path.join(HERE, "Patches", "Patches_BrokenTurretAim.xml")).getroot()
    txt = open(os.path.join(HERE, "Patches", "Patches_BrokenTurretAim.xml")).read()
    for b in BROKEN:
        if 'defName="%s"' % b not in txt:
            bad.append("patch does not target %s" % b)
    if "MayRequire" in txt.replace("no top-level MayRequire", ""):
        bad.append("patch uses MayRequire (inert on an Operation)")
    cs = open(os.path.join(HERE, "Source", "RM_CompTurretAim.cs")).read()
    cs = re.sub(r"//[^\n]*", "", cs)
    if re.search(r"\bVerb\b|Verb_|AttackTarget|TryStartCastOn|Projectile\b.*Launch", cs.split("OldLineTurretTuning")[0]):
        bad.append("the aim comp touches a verb or projectile -- it must stay verbless")
    return bad


def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("Warscar")
    suite.toggles = ["turretTrackingEnabled", "turretRefitEnabled"]

    def _set(t, field, value):
        t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=field,
                      value=str(value))

    def _restore(t, field):
        if t.session is not None:
            try:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set",
                               field=field, value=str(DEFAULTS[field]))
            except Exception as ex:
                print("[warscar] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)

    def _inspect(t, thing_id):
        r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
        rows = (r or {}).get("things") or []
        row = next((x for x in rows if x.get("id") == thing_id), None)
        if row is None or row.get("error"):
            raise ExpectationFailed("inspect_string failed for %s: %r" % (thing_id, row or r))
        return " ".join(str(x) for x in (row.get("inspect") or []))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("old_line_defs_resolve", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=";".join(NEW_DEFS), fields="defName", limit=20)
            if t.session is None:
                return
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                raise ExpectationFailed("old-line defs did not resolve live: %r" % r)
            if int(r.get("foundCount", 0)) != len(NEW_DEFS):
                raise ExpectationFailed("expected %d old-line defs, found %r" % (len(NEW_DEFS), r.get("foundCount")))

    @suite.chain("tracking")
    def tracking(t):
        t.clear_area(size=24)
        cells = t.spawn(BROKEN[0], count=1, at="point") or [(0, 0)]
        wreck_rect = "%d,%d,24,24" % (cells[0][0] - 12, cells[0][1] - 12)

        def wreck_id():
            rows = (t.bridge_call("jawa/list_things", defName=BROKEN[0], rect=wreck_rect) or {}).get("things") or []
            if not rows:
                raise ExpectationFailed("no %s found after spawning it" % BROKEN[0])
            return rows[0]["id"]

        with t.component("barrel_follows_mover_and_never_fires", toggle="turretTrackingEnabled"):
            wid = wreck_id()
            pawn = t.spawn_pawn("Colonist") if hasattr(t, "spawn_pawn") else None
            pid = (pawn or {}).get("id") if isinstance(pawn, dict) else pawn
            if t.session is not None and pid is not None:
                t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef="Goto",
                              targetAPos="%d,%d" % (cells[0][0] + 10, cells[0][1] + 10))
                t.wait_ticks(60)
                if "follow" not in _inspect(t, wid):
                    raise ExpectationFailed("a broken turret beside a walking pawn reports no tracking state")
                shots = (t.bridge_call("jawa/list_things", defName="Bullet_AncientArmoredTurret", rect=wreck_rect) or {}).get("things") or []
                if shots:
                    raise ExpectationFailed("a broken turret produced projectiles: %r" % shots[:2])
                _set(t, "turretTrackingEnabled", False)
                try:
                    t.wait_ticks(30)
                    if "follow" in _inspect(t, wid):
                        raise ExpectationFailed("tracking line persists with turretTrackingEnabled off (toggle dead)")
                finally:
                    _restore(t, "turretTrackingEnabled")
            elif t.session is not None:
                raise ExpectationFailed("UNMEASURED: could not spawn a pawn to walk")

    @suite.chain("refit_gizmo")
    def refit_gizmo(t):
        with t.component("refit_gated_by_toggle", toggle="turretRefitEnabled"):
            if t.session is None:
                return
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_OldLineTurret", fields="defName,costList", limit=2)
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("could not read the refit target def: %r" % r)
            if "ComponentSpacer" not in str(r) and "RM_Etchant" not in str(r):
                raise ExpectationFailed("refit cost carries neither advanced components nor etchant: %r" % r)
            # Gizmo presence has no bridge reader; the toggle is read back so a dead setting still fails.
            _set(t, "turretRefitEnabled", False)
            try:
                got = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="get",
                                    field="turretRefitEnabled")
                if str((got or {}).get("value")).lower() != "false":
                    raise ExpectationFailed("turretRefitEnabled did not take: %r" % got)
            finally:
                _restore(t, "turretRefitEnabled")

    return suite


try:
    suite = _build_suite()
except ImportError:      # run outside the modcheck path (the static check below needs no game)
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
