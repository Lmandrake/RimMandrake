"""validation.py -- modcheck suite for RimMandrake: Huge Things (mandrake.rm.hugethings).

First script (HUGE_THINGS_FOOTPRINT_1). Walk: design/validation_walks/RimMandrake/HugeThings.md.
Design: design/RimMandrake/giant_footprint_design_2026-10-07.md.

THE MOD is an ENGINE: a plant carrying RM_HugePlantExtension gets a solid trunk (invisible impassable
RM_HugeTrunkBlocker edifices on trunkWidth x trunkDepth cells north of its own cell, grown into with the plant)
and a trunk-wide click area (Thing.CustomRectForSelector postfix); a race carrying RM_HugePawnExtension gets a
click area the size of its drawn body. The Rot opts in nine giants (TheRot/Patches/RotGiants_HugeFootprint.xml);
TitanicCreatures opts in every tiered race.

CHAINS
  defs_resolve       RM_HugeTrunkBlocker resolves; a control name reads notFound.
  settings_roundtrip every `public static` bool/float of RM_HugeThingsSettings (5), numerically compared.
  harmony            Thing.get_CustomRectForSelector carries a postfix owned by mandrake.rm.hugethings.
  trunk              a full-grown brommok timber (RM_Nogtyl, 3x3 trunk) gets exactly 8 blockers (the rect minus its
                     own cell) and none south of it; a young one (growth 0.1) gets none; `plantTrunkEnabled` off
                     clears them on the next refresh; cutting the plant removes them at once.
  not_driven         click selection (no tool reads CustomRectForSelector or simulates a map click), pawn hitbox,
                     save/load re-link, mapgen: UNMEASURED, each with its reason.

LIST: needs mandrake.rm.biomes (TheRot folded in) beside this mod for RM_Nogtyl. STATIC: `python3 validation.py`
-> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.HugeThings.RM_HugeThingsSettings"
HARMONY_ID = "mandrake.rm.hugethings"
CONTROL_ABSENT = "ThingDef/RM_HugeNoSuchDef_ZZ"
BLOCKER = "RM_HugeTrunkBlocker"
GIANT = "RM_Nogtyl"          # brommok timber: TheRot's own def (no donor mod needed), 3x3 trunk in the Rot patch
GIANT_BLOCKERS = 8           # 3x3 minus the plant's own cell
REFRESH_TICKS = 2000         # MapComponent_HugeFootprints.RefreshInterval
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
DEFAULTS = {"plantTrunkEnabled": True, "plantSelectionEnabled": True, "plantTrunkScale": 1.0,
            "pawnHitboxEnabled": True, "pawnHitboxScale": 1.0}


def settings_fields():
    src = open(os.path.join(HERE, "Source", "RM_HugeThingsSettings.cs"), encoding="utf-8").read()
    body = src.split("class RM_HugeThingsSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def shipped_defs():
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text:
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


def giant_trunk():
    """(w, d) the Rot patch gives GIANT, read from the patch (never a hand number)."""
    p = os.path.join(HERE, "..", "TheRot", "Patches", "RotGiants_HugeFootprint.xml")
    for op in ET.parse(p).getroot():
        if 'defName="%s"' % GIANT in (op.findtext("xpath") or ""):
            li = op.find("match/value/li")
            return int(li.findtext("trunkWidth")), int(li.findtext("trunkDepth"))
    return None


def static_checks():
    bad = []
    defs = shipped_defs()
    if ("ThingDef", BLOCKER) not in defs:
        bad.append("blocker def %s not shipped (sanity probe read %r)" % (BLOCKER, defs))
    fields = settings_fields()
    if sorted(fields) != sorted(DEFAULTS):
        bad.append("settings fields changed: %s (update DEFAULTS and the walk)" % sorted(set(fields) ^ set(DEFAULTS)))
    src = open(os.path.join(HERE, "Source", "RM_HugeThingsSettings.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    core = open(os.path.join(HERE, "Source", "HugeThingsCore.cs"), encoding="utf-8").read()
    if 'HarmonyId = "%s"' % HARMONY_ID not in core:
        bad.append("Harmony id is no longer %s" % HARMONY_ID)
    if "nameof(Thing.CustomRectForSelector), MethodType.Getter" not in core:
        bad.append("the selection postfix no longer targets Thing.CustomRectForSelector's getter")
    mc = open(os.path.join(HERE, "Source", "MapComponent_HugeFootprints.cs"), encoding="utf-8").read()
    if "RefreshInterval = %d" % REFRESH_TICKS not in mc:
        bad.append("refresh interval moved; update REFRESH_TICKS (the toggle-off wait depends on it)")
    if giant_trunk() is None or giant_trunk()[0] * giant_trunk()[1] - 1 != GIANT_BLOCKERS:
        bad.append("the Rot patch no longer gives %s a trunk of %d+1 cells: %r" % (GIANT, GIANT_BLOCKERS, giant_trunk()))
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "HugeThings.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite("HugeThings")
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        kw = dict(typeName=SETTINGS, action=action, field=field)
        if value is not None:
            kw["value"] = str(value)
        r = t.session.call("jawa/mod_settings_field", **kw)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    def _count(t, defName, rect):
        r = t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=200)
        if not _live(t):
            return 0
        if not isinstance(r, dict) or r.get("success") is False or "countMatched" not in r:
            raise ExpectationFailed("list_things(%s) unreadable: %r" % (defName, r))
        return int(r.get("countMatched"))

    def _stage(t, x, z, growth):
        r = t.bridge_call("jawa/artboard_stage", phase="subjects", pause=False, killHostiles=True,
                          ops="id=g|kind=plant|x=%d|z=%d|def=%s|growth=%s" % (x, z, GIANT, growth))
        if not _live(t):
            return True
        ops = (r or {}).get("ops") or [] if isinstance(r, dict) else []
        if not ops or not ops[0].get("ok"):
            _unmeasured(t, "could not stage %s at %d,%d (growth %s): %s" % (GIANT, x, z, growth, str(r)[:200]))
            return False
        return True

    def _rects(x, z):
        trunk = "%d,%d,3,3" % (x - 1, z)          # NorthRect(root, 3, 3)
        around = "%d,%d,7,8" % (x - 3, z - 2)     # trunk plus margin, incl. two rows south
        south = "%d,%d,7,2" % (x - 3, z - 2)
        return trunk, around, south

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t) and (not isinstance(r, dict) or r.get("success") is False or int(r.get("foundCount", 0)) != 0):
                raise ExpectationFailed("control def reads as present or the call failed: %r" % r)
        with t.component("blocker_def_resolves", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s;ThingDef/%s" % (BLOCKER, GIANT), fields="defName", limit=4)
            if _live(t) and (not isinstance(r, dict) or r.get("success") is False or int(r.get("foundCount", 0)) != 2):
                raise ExpectationFailed("blocker or %s did not resolve (is mandrake.rm.biomes loaded?): %r" % (GIANT, r))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else str(round(float(old) - 0.25, 2))
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)

    @suite.chain("harmony")
    def harmony(t):
        with t.component("Thing_get_CustomRectForSelector_postfix_attached", beyond_toggle=True):
            r = t.bridge_call("jawa/harmony_patches", typeName="Thing", methodName="get_CustomRectForSelector")
            if not _live(t):
                return
            methods = (r or {}).get("methods") or [] if isinstance(r, dict) else []
            if not isinstance(r, dict) or r.get("success") is not True or not methods:
                _unmeasured(t, "harmony_patches could not resolve the property getter: %s" % str(r)[:160])
                return
            owners = [p.get("owner") for m in methods for p in (m.get("postfixes") or [])]
            if HARMONY_ID not in owners:
                raise ExpectationFailed("no postfix owned by %s (owners %r)" % (HARMONY_ID, owners[:8]))

    @suite.chain("trunk")
    def trunk(t):
        if _live(t):
            t.clear_area(size=30)
        x, z = t.anchor if t.anchor else (0, 0)
        trunk_r, around_r, south_r = _rects(x, z)
        with t.component("full_grown_giant_gets_a_solid_trunk", toggle="plantTrunkEnabled"):
            if _live(t) and _stage(t, x, z, 1):
                t.wait_ticks(120)
                n, out, south = _count(t, BLOCKER, trunk_r), _count(t, BLOCKER, around_r), _count(t, BLOCKER, south_r)
                if n != GIANT_BLOCKERS or out != GIANT_BLOCKERS:
                    raise ExpectationFailed("%s at growth 1 has %d blockers in its 3x3 trunk, %d nearby (want %d and %d)"
                                            % (GIANT, n, out, GIANT_BLOCKERS, GIANT_BLOCKERS))
                if south:
                    raise ExpectationFailed("%d blockers south of the plant: its own cell would be unreachable" % south)
        with t.component("toggle_off_clears_the_trunk", toggle="plantTrunkEnabled"):
            if _live(t):
                _raw(t, "set", "plantTrunkEnabled", "False")
                try:
                    t.wait_ticks(REFRESH_TICKS + 60)
                    n = _count(t, BLOCKER, around_r)
                    if n:
                        raise ExpectationFailed("plantTrunkEnabled off, yet %d blockers remain after a refresh" % n)
                finally:
                    _raw(t, "set", "plantTrunkEnabled", "True")
                t.wait_ticks(REFRESH_TICKS + 60)
        with t.component("cutting_the_plant_removes_the_trunk", toggle="plantTrunkEnabled"):
            if _live(t):
                if _count(t, BLOCKER, around_r) != GIANT_BLOCKERS:
                    _unmeasured(t, "the trunk did not come back after re-enabling: no baseline to cut")
                else:
                    t.bridge_call("jawa/destroy_batch", rects="%d,%d,1,1" % (x, z), categories="Plant")
                    n = _count(t, BLOCKER, around_r)
                    if n:
                        raise ExpectationFailed("plant destroyed, %d blockers left behind" % n)
        with t.component("young_giant_blocks_nothing", toggle="plantTrunkEnabled"):
            if _live(t) and _stage(t, x, z, 0.1):
                t.wait_ticks(120)
                n = _count(t, BLOCKER, around_r)
                if n:
                    raise ExpectationFailed("%s at growth 0.1 already has %d blockers" % (GIANT, n))

    @suite.chain("not_driven")
    def not_driven(t):
        for name, why in (
                ("click_anywhere_on_trunk_selects_plant", "no bridge tool reads Thing.CustomRectForSelector or simulates a map click"),
                ("huge_pawn_hitbox_covers_drawn_body", "no RM_HugePawnExtension race in a mod-only list, and no selection-rect read tool"),
                ("trunk_relinks_after_save_load", "needs a save/load round on a map with a giant"),
                ("mapgen_giants_get_trunks", "needs a fresh Rot map generation")):
            with t.component(name, beyond_toggle=True):
                if _live(t):
                    _unmeasured(t, why)

    return suite


suite = _build_suite() if Suite is not None else None


if __name__ == "__main__":
    findings = static_checks()
    for f in findings:
        print("FINDING:", f)
    print("STATIC: %s (%d findings)" % ("PASS" if not findings else "FAIL", len(findings)))
    sys.exit(1 if findings else 0)
