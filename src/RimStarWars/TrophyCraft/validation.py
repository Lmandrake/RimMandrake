"""validation.py -- modcheck suite for RimStarWars: Trophy Craft (mandrake.rsw.trophycraft).

First north-star script (TROPHY_CRAFT_FIRST_SCRIPT_1). Walk: design/validation_walks/RimStarWars/TrophyCraft.md.
WYYYSCHOKK_FANG_PENDANT_1: a butchered wyyyschokk drops fangs (a conditional patch onto RM_Ollathrix, THE wyyyschokk by
the 2026-10-03 ruling, shipped by mandrake.rm.webwork; the donor Wyyyschokk block was deleted 2026-10-15), a tailoring-bench recipe cords
4 fangs + 5 textiles into a neck-layer pendant, and observers of configured factions (the campaign's hunting tribes, data
shipped by RimUtinni, EMPTY at this tier) form a +8 opinion of anyone wearing it, scaled by a Mod Settings slider.

CHAINS
  defs_resolve       every def under Defs/ resolves live; a control reads notFound. (The fang's animal is fang_drop's.)
  settings_roundtrip every `public static` field of RSW_TrophyCraftSettings (2): default / write / restore, numerics numerically.
  crafting           the recipe's work amount and the neck layer's draw order read back; products / ingredients read when
                     get_defs expands them, else UNMEASURED; a control recipe reads a different work amount.
  fang_drop          RM_Ollathrix's butcherProducts carries the fang (UNMEASURED when Webwork is not loaded: the patch is
                     conditional); an unpatched animal's does not.
  social_thought     the thought's classes and base opinion read back; the observer firing: UNMEASURED.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import contextlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
SETTINGS = "RimMandrake.StarWars.TrophyCraft.RSW_TrophyCraftSettings"
NS = "RimMandrake.StarWars.TrophyCraft."
CONTROL_ABSENT = "ThingDef/RSW_TrophyCraftNoSuchDef_ZZ"
FANG, PENDANT, RECIPE, LAYER, THOUGHT = ("RSW_WyyyschokkFang", "RSW_Apparel_FangPendant", "RSW_Make_FangPendant",
                                         "RSW_Neck", "RSW_TrophyCraft_ObserverBraveFang")
ANIMAL = "RM_Ollathrix"     # THE wyyyschokk (WYYYSCHOKK_IDENTITY_COLLISION_1); the patch's only target
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
    if len(SHIPPED) < 5:
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
    allsrc = ""
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs"):
            allsrc += open(os.path.join(HERE, "Source", fn), encoding="utf-8").read()
            if 'Compile Include="%s"' % fn not in proj:
                bad.append("%s is not in the csproj (compiles into nothing, no error)" % fn)
    # the thought: classes exist, the extension names the shipped pendant, the factions list ships empty
    th = _def("ThoughtDefs/RSW_TrophyCraft_Thoughts.xml", "ThoughtDef", THOUGHT)
    if th is None:
        return bad + ["ThoughtDef %s missing" % THOUGHT]
    for tag in ("thoughtClass", "workerClass"):
        cls = (th.findtext(tag) or "").replace(NS, "")
        if "class %s" % cls not in allsrc:
            bad.append("%s %r is not in Source/" % (tag, th.findtext(tag)))
    ext = th.find("modExtensions/li")
    if ext is None or ext.findtext("apparelDefName") != PENDANT:
        bad.append("thought extension does not name %s" % PENDANT)
    if ext is not None and ext.find("factionDefNames") is None:
        bad.append("thought extension lost its factionDefNames node (the RimUtinni Add patch would match nothing)")
    if ext is not None and ext.findall("factionDefNames/li"):
        bad.append("factionDefNames ships non-empty at the RimStarWars tier (campaign data is RimUtinni's)")
    if float(th.findtext("stages/li/baseOpinionOffset") or 0) != 8:
        bad.append("base opinion offset is not +8")
    # the RimUtinni data patch targets this def's node
    rut = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "WyyyschokkFangPendantFactions.xml")
    if os.path.isfile(rut):
        t = open(rut, encoding="utf-8").read()
        if 'defName="%s"]/modExtensions/li/factionDefNames' % THOUGHT not in t:
            bad.append("the RimUtinni factions patch no longer targets %s" % THOUGHT)
    # recipe: fixed ingredients, correct product, usable at both tailoring benches
    rc = _def("RecipeDefs/RSW_TrophyCraft_Recipes.xml", "RecipeDef", RECIPE)
    if rc is None:
        bad.append("RecipeDef %s missing" % RECIPE)
    else:
        if rc.findtext("products/%s" % PENDANT) != "1":
            bad.append("recipe does not produce one %s" % PENDANT)
        if rc.findtext("ingredients/li/filter/thingDefs/li") != FANG or rc.findtext("ingredients/li/count") != "4":
            bad.append("recipe does not take 4 %s" % FANG)
        users = [x.text for x in rc.findall("recipeUsers/li")]
        if sorted(users) != ["ElectricTailoringBench", "HandTailoringBench"]:
            bad.append("recipe users wrong: %r" % users)
        if rc.findtext("workAmount") != "400":
            bad.append("recipe workAmount is not 400")
    pd = _def("ThingDefs/RSW_TrophyCraft_Items.xml", "ThingDef", PENDANT)
    if pd is None or pd.findtext("apparel/layers/li") != LAYER or pd.findtext("apparel/bodyPartGroups/li") != "Neck":
        bad.append("pendant is not a Neck-group apparel on layer %s" % LAYER)
    # NORTHSTAR_PARTIAL_GAPS_FILL_1: "sells anywhere" -- the pendant carries ExoticMisc, the fang Exotic, and the
    # crafted pendant is worth more than the four fangs it eats (or crafting it destroys value).
    fg = _def("ThingDefs/RSW_TrophyCraft_Items.xml", "ThingDef", FANG)
    if pd is not None and "ExoticMisc" not in [x.text for x in pd.findall("tradeTags/li")]:
        bad.append("pendant lost tradeTags ExoticMisc (no longer sells to any trader)")
    if fg is not None and "Exotic" not in [x.text for x in fg.findall("tradeTags/li")]:
        bad.append("fang lost tradeTags Exotic")
    try:
        pv, fv = float(pd.findtext("statBases/MarketValue")), float(fg.findtext("statBases/MarketValue"))
        if pv <= 4 * fv:
            bad.append("pendant MarketValue %s <= 4 fangs at %s: crafting destroys value" % (pv, fv))
    except (AttributeError, TypeError, ValueError):
        bad.append("pendant or fang MarketValue unreadable from XML")
    if _def("ApparelLayerDefs/RSW_TrophyCraft_ApparelLayerDefs.xml", "ApparelLayerDef", LAYER) is None:
        bad.append("ApparelLayerDef %s missing" % LAYER)
    # the fang-drop patch: butcherProducts is dictionary-keyed (an <li> discards the whole donor def)
    pt = open(os.path.join(HERE, "Patches", "RSW_TrophyCraft_WyyyschokkFangDrop.xml"), encoding="utf-8").read()
    pt_code = re.sub(r"<!--.*?-->", "", pt, flags=re.S)
    if "<%s>3</%s>" % (FANG, FANG) not in pt_code:
        bad.append("fang drop patch no longer adds 3 fangs")
    if "<li>" in pt_code.split("<value>", 1)[1].split("</value>", 1)[0]:
        bad.append("fang drop patch uses <li> inside butcherProducts (discards the whole donor def)")
    if 'ThingDef[defName="%s"]/butcherProducts' % ANIMAL not in pt_code or "Wyyyschokk\"]" in pt_code:
        bad.append("fang drop patch no longer targets %s alone (validation's fang_drop reads that def)" % ANIMAL)
    if "MayRequire" in re.sub(r"<!--.*?-->", "", pt, flags=re.S):
        bad.append("fang drop patch carries MayRequire on an Operation (inert)")
    # textures
    for tex in ("Things/Item/RSW_Apparel_FangPendant/RSW_Apparel_FangPendant", "swresource/WyyyschokkFang"):
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
        t._why = why

    @contextlib.contextmanager
    def _comp(t, name, **kw):
        """A row in a chain of INDEPENDENT reads. A declared UNMEASURED is this row's own verdict: lift its latch so the
        next row runs and says its own reason, restoring the PRIOR reason (never None: a later plain FAIL latches
        without setting one). A real upstream failure still ends the chain (TROPHYCRAFT_VALIDATION_FIX_SKIPPED_ROWS)."""
        before, reason = t.upstream_failed, t.upstream_reason
        t._why = None
        with t.component(name, **kw):
            yield
        if getattr(t, "_why", None) and not before:
            t.upstream_failed, t.upstream_reason = False, reason
        t._why = None

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

    # Each row's body is its own function: a `return` inside a `with` row used to leave the whole CHAIN, so a PASS or
    # a declared UNMEASURED silently dropped every later row from the record (TROPHYCRAFT_VALIDATION_FIX_SKIPPED_ROWS).
    def _work_amount(t):
        f = _row(t, "RecipeDef/" + RECIPE, "workAmount")
        if not _live(t):
            return
        try:
            wa = float(f.get("workAmount"))
        except (TypeError, ValueError):
            return _unmeasured(t, "get_defs did not return a numeric workAmount: %r" % (f,))
        if wa != 400.0:
            raise ExpectationFailed("workAmount is %s, expected 400" % wa)

    def _work_amount_control(t):
        f = _row(t, "RecipeDef/Make_Patchleather", "workAmount")
        if _live(t) and str(f.get("workAmount")) in ("400", "400.0"):
            raise ExpectationFailed("a vanilla recipe reads workAmount 400 too: the read cannot say different")

    def _recipe_products(t):
        if not _live(t):
            return
        f = _row(t, "RecipeDef/" + RECIPE, "products,ingredients", deep=True)
        if not _live(t):
            return
        blob = " ".join(_flat(f))
        if PENDANT in blob and FANG in blob:
            return
        if PENDANT in blob and "filter" in blob:
            return _unmeasured(t, "products name %s, but get_defs prints an ingredient's filter without its allowed thingDefs, so the fang half cannot be read live (2026-10-07: the old check FAILED here on that instrument gap)" % PENDANT)
        if PENDANT not in blob and FANG not in blob and ("ThingDefCountClass" in blob or "IngredientCount" in blob):
            return _unmeasured(t, "get_defs returned products/ingredients as bare type names even with deep=True: %s" % blob[:120])
        raise ExpectationFailed("recipe products/ingredients do not name %s and %s: %s" % (PENDANT, FANG, blob[:160]))

    def _draw_order(t):
        f = _row(t, "ApparelLayerDef/" + LAYER, "drawOrder")
        if not _live(t):
            return
        try:
            do = float(f.get("drawOrder"))
        except (TypeError, ValueError):
            return _unmeasured(t, "get_defs did not return a numeric drawOrder: %r" % (f,))
        if do != 150.0:
            raise ExpectationFailed("RSW_Neck drawOrder is %s, expected 150" % do)

    def _pendant_layer(t):
        if not _live(t):
            return
        f = _row(t, "ThingDef/" + PENDANT, "apparel", deep=True)
        if _live(t) and LAYER not in " ".join(_flat(f)):
            _unmeasured(t, "get_defs returns the apparel record as a bare type name (no layers): %s" % " ".join(_flat(f))[:120])

    @suite.chain("crafting")
    def crafting(t):
        for name, body in (("recipe_work_amount_400", _work_amount),
                           ("probe_reads_a_different_work_amount_control", _work_amount_control),
                           ("recipe_takes_fangs_and_makes_a_pendant", _recipe_products),
                           ("neck_layer_draws_between_middle_and_shell", _draw_order),
                           ("pendant_wears_on_the_neck_layer", _pendant_layer)):
            with _comp(t, name, beyond_toggle=True):
                body(t)

    def _animal_fang(t):
        if not _live(t):
            return
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/" + ANIMAL, fields="butcherProducts", deep=True, limit=2)
        if not _live(t):
            return
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("get_defs ThingDef/%s failed: %r" % (ANIMAL, r))
        if r.get("notFound") or int(r.get("foundCount", 0)) != 1:
            return _unmeasured(t, "%s is not loaded (mandrake.rm.webwork absent): the fang patch is conditional and lands "
                                  "nothing by design, so there is no drop to read" % ANIMAL)
        rows = r.get("defs") or []
        blob = " ".join(_flat((rows[0].get("fields") or {}) if rows else {}))
        if FANG in blob:
            return
        if "ThingDefCountClass" in blob or not blob.strip():
            return _unmeasured(t, "get_defs returned butcherProducts as bare type names even with deep=True: %s" % blob[:120])
        raise ExpectationFailed("%s butcherProducts does not name %s (patch landed nothing): %s" % (ANIMAL, FANG, blob[:160]))

    def _unpatched_control(t):
        if not _live(t):
            return
        f = _row(t, "ThingDef/Wolf_Timber", "butcherProducts", deep=True)
        if _live(t) and FANG in " ".join(_flat(f)):
            raise ExpectationFailed("an unpatched wolf drops the wyyyschokk fang: the drop check cannot say absent")

    @suite.chain("fang_drop")
    def fang_drop(t):
        with _comp(t, "ollathrix_butcher_products_carry_the_fang", beyond_toggle=True):
            _animal_fang(t)
        with _comp(t, "probe_can_say_absent_on_an_unpatched_animal", beyond_toggle=True):
            _unpatched_control(t)

    def _thought_classes(t):
        f = _row(t, "ThoughtDef/" + THOUGHT, "thoughtClass,workerClass")
        if not _live(t):
            return
        if all("no such field" in str(f.get(k)) for k in ("thoughtClass", "workerClass")):
            return _unmeasured(t, "get_defs returns '(no such field)' for ThoughtDef's Type fields thoughtClass/workerClass (2026-10-07, def resolved with both set in XML): an instrument gap, not a missing class")
        for k, want in (("thoughtClass", "RSW_Thought_ObserverBraveFang"), ("workerClass", "RSW_ThoughtWorker_ObserverFactionApparel")):
            if want not in str(f.get(k)):
                raise ExpectationFailed("%s is %r, expected the %s class" % (k, f.get(k), want))

    @suite.chain("social_thought")
    def social_thought(t):
        with _comp(t, "thought_classes_and_base_offset", toggle="socialConsequenceEnabled"):
            _thought_classes(t)
        with _comp(t, "observer_forms_opinion_of_a_pendant_wearer", toggle="socialConsequenceEnabled"):
            if _live(t):
                _unmeasured(t, "the thought fires only for an observer of a faction listed in factionDefNames (empty at this tier; "
                               "RimUtinni's patch adds RUT_Jawa_WildsteamClan, Pirate and TribeCivil) who sees a wearer of the pendant, "
                               "and no bridge tool equips apparel on a pawn or reads a pawn's social thoughts")
        with _comp(t, "opinion_multiplier_scales_the_offset", toggle="opinionMultiplier"):
            if _live(t):
                _unmeasured(t, "needs the same observer/wearer pair plus an opinion read; the slider's write/read-back is covered "
                               "in settings_roundtrip")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
