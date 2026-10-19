"""validation.py -- modcheck suite for RimStarWars: Trophy Craft (mandrake.rsw.trophycraft).

First north-star script (TROPHY_CRAFT_FIRST_SCRIPT_1). Walk: design/validation_walks/RimStarWars/TrophyCraft.md.
WYYYSCHOKK_FANG_PENDANT_1: a butchered wyyyschokk drops fangs (a patch onto the donor def), a trade good. The fang
pendant, its recipe RSW_Make_FangPendant, its observer thought RSW_TrophyCraft_ObserverBraveFang, the RSW_Neck layer and
RimUtinni's factions patch were removed from the game (owner, picks_icons_sheet_2026-10-19: "drop"). The thought's C#
classes and the two settings fields remain in Source/ (dead until a rebuild removes them); the settings still round-trip.

CHAINS
  defs_resolve       every def under Defs/ resolves live; the donor Wyyyschokk it patches resolves; a control reads notFound.
  settings_roundtrip every `public static` field of RSW_TrophyCraftSettings (2): default / write / restore, numerics numerically.
  fang_drop          the donor Wyyyschokk's butcherProducts carries the fang; an unpatched animal's does not.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
SETTINGS = "RimMandrake.StarWars.TrophyCraft.RSW_TrophyCraftSettings"
CONTROL_ABSENT = "ThingDef/RSW_TrophyCraftNoSuchDef_ZZ"
FANG = "RSW_WyyyschokkFang"
# removed by the owner's 2026-10-19 ruling (picks_icons_sheet_2026-10-19): must not come back
REMOVED = ("RSW_Apparel_FangPendant", "RSW_Make_FangPendant", "RSW_Neck", "RSW_TrophyCraft_ObserverBraveFang")
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


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


SHIPPED = shipped_defs()


def settings_fields():
    src = open(os.path.join(HERE, "Source", "RSW_TrophyCraftSettings.cs"), encoding="utf-8").read()
    body = src.split("class RSW_TrophyCraftSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def _def(file, tag, name):
    root = ET.parse(os.path.join(HERE, "Defs", file)).getroot()
    return next((e for e in root if e.tag == tag and e.findtext("defName") == name), None)


def static_checks():
    bad = []
    if len(SHIPPED) < 1:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if len(fields) < 2:
        return ["settings probe found %d fields (sanity probe failed)" % len(fields)]
    src = open(os.path.join(HERE, "Source", "RSW_TrophyCraftSettings.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RSW_TrophyCraft.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing, no error)" % fn)
    for _tag, name in SHIPPED:
        if name in REMOVED:
            bad.append("%s is back in Defs/ (removed by the owner, picks_icons_sheet_2026-10-19)" % name)
    rut = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "WyyyschokkFangPendantFactions.xml")
    if os.path.isfile(rut):
        bad.append("the RimUtinni factions patch is back but its target thought was removed")
    # "sells anywhere": the fang carries tradeTags Exotic
    fg = _def("ThingDefs/RSW_TrophyCraft_Items.xml", "ThingDef", FANG)
    if fg is None:
        bad.append("ThingDef %s missing" % FANG)
    elif "Exotic" not in [x.text for x in fg.findall("tradeTags/li")]:
        bad.append("fang lost tradeTags Exotic")
    # the fang-drop patch: butcherProducts is dictionary-keyed (an <li> discards the whole donor def)
    pt = open(os.path.join(HERE, "Patches", "RSW_TrophyCraft_WyyyschokkFangDrop.xml"), encoding="utf-8").read()
    pt_code = re.sub(r"<!--.*?-->", "", pt, flags=re.S)
    if "<%s>3</%s>" % (FANG, FANG) not in pt_code:
        bad.append("fang drop patch no longer adds 3 fangs")
    if "<li>" in pt_code.split("<value>", 1)[1].split("</value>", 1)[0]:
        bad.append("fang drop patch uses <li> inside butcherProducts (discards the whole donor def)")
    if "MayRequire" in re.sub(r"<!--.*?-->", "", pt, flags=re.S):
        bad.append("fang drop patch carries MayRequire on an Operation (inert)")
    # textures
    for tex in ("swresource/WyyyschokkFang",):
        if not os.path.isfile(os.path.join(HERE, "Textures", *tex.split("/")) + ".png"):
            bad.append("texture %s missing" % tex)
    if not os.path.isfile(os.path.join(SRC, "..", "design", "validation_walks", "RimStarWars", "TrophyCraft.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "..", "RimMandrake", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _flat(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            for s in _flat(v):
                yield s
    elif isinstance(x, (list, tuple)):
        for v in x:
            for s in _flat(v):
                yield s


def _build_suite():
    suite = Suite("TrophyCraft")
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    def _row(t, defspec, fields, deep=False):
        r = t.bridge_call("jawa/get_defs", defs=defspec, fields=fields, deep=deep, limit=2)
        if not _live(t):
            return None
        if not isinstance(r, dict) or r.get("success") is False or r.get("notFound") or int(r.get("foundCount", 0)) != 1:
            raise ExpectationFailed("get_defs %s unreadable or absent: %r" % (defspec, r))
        rows = r.get("defs") or []
        return (rows[0].get("fields") or {}) if rows else {}

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=10)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    raise ExpectationFailed("%d shipped defs, foundCount=%r notFound=%r" % (len(names), r.get("foundCount"), r.get("notFound")))
        with t.component("donor_wyyyschokk_resolves", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/Wyyyschokk", fields="defName", limit=2)
            if _live(t) and (not isinstance(r, dict) or r.get("notFound") or int(r.get("foundCount", 0)) != 1):
                raise ExpectationFailed("the donor ThingDef Wyyyschokk is absent (mlie.starwarsanimalcollection not loaded?): %r" % r)

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 2:
                raise ExpectationFailed("settings probe found too few fields (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
                elif ty == "int":
                    new = str(int(float(old)) + 1)       # an Int32 field refuses "25.0" (LIVE 2026-10-03)
                else:
                    new = str(float(old) + 1.0)
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("fang_drop")
    def fang_drop(t):
        with t.component("donor_butcher_products_carry_the_fang", beyond_toggle=True):
            if not _live(t):
                return
            f = _row(t, "ThingDef/Wyyyschokk", "butcherProducts", deep=True)
            blob = " ".join(_flat(f))
            if FANG in blob:
                return
            if "ThingDefCountClass" in blob or not blob.strip():
                _unmeasured(t, "get_defs returned butcherProducts as bare type names even with deep=True: %s" % blob[:120])
                return
            raise ExpectationFailed("the donor Wyyyschokk butcherProducts does not name %s (patch landed nothing): %s" % (FANG, blob[:160]))
        with t.component("probe_can_say_absent_on_an_unpatched_animal", beyond_toggle=True):
            if not _live(t):
                return
            f = _row(t, "ThingDef/Wolf_Timber", "butcherProducts", deep=True)
            if FANG in " ".join(_flat(f)):
                raise ExpectationFailed("an unpatched wolf drops the wyyyschokk fang: the drop check cannot say absent")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
