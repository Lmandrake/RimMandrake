"""validation.py -- modcheck suite for RimStarWars: Shokk (mandrake.rsw.shokk).

First north-star script (SHOKK_FIRST_SCRIPT_1). Walk: design/validation_walks/RimStarWars/Shokk.md.
After SHOKK_SKIN_SHRINK_1 this mod is data only: one skin patch (RSW_Shokk_OllathrixSkin.xml) that re-labels the free-tier
RM_Ollathrix as the canon wyyyschokk, and one hidden FactionDef (RSW_Shokk_FeraliskBrood) the Fever Wood's second raid front
looks up by defName. It has NO C# and NO Mod Settings class.

CHAINS
  defs_resolve     the FactionDef resolves live (parsed from the XML); the donor Wyyyschokk PawnKindDef it fields resolves;
                   a control name reads notFound.
  skin_patch       RM_Ollathrix's ThingDef and PawnKindDef carry the wyyyschokk label and plural after the patch; a
                   never-patched control def reads a different label (the reader can say "different").
  feralisk_brood   the faction is hidden, a permanent enemy, animal tech and fields the Wyyyschokk in its Combat group.
  settings         there is no settings class by design: asserted from the folder, not assumed.
  two_front_lure   the Fever Wood second raid front firing this faction: UNMEASURED (needs a Fever Wood raid).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
OLLATHRIX_XML = os.path.join(SRC, "RimMandrake", "Webwork", "Defs", "ThingDefs_Races", "RM_Ollathrix.xml")
PATCH = os.path.join(HERE, "Patches", "RSW_Shokk_OllathrixSkin.xml")
CONTROL_ABSENT = "ThingDef/RSW_ShokkNoSuchDef_ZZ"
SKIN = "wyyyschokk"
FACTION = "RSW_Shokk_FeraliskBrood"


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


def static_checks():
    bad = []
    if not SHIPPED or ("FactionDef", FACTION) not in SHIPPED:
        return ["FactionDef %s not parsed from Defs/ (sanity probe failed)" % FACTION]
    # no settings class: the day one appears this script must grow a settings_roundtrip chain
    if os.path.isdir(os.path.join(HERE, "Source")):
        bad.append("Shokk now has a Source/ folder: add a settings_roundtrip chain and a csproj check to this script")
    # every patch operation's xpath must match the target def it names (a patch that matches nothing logs nothing)
    tgt = ET.parse(OLLATHRIX_XML).getroot()
    defs = {}
    for e in tgt:
        if isinstance(e.tag, str) and e.findtext("defName") == "RM_Ollathrix":
            defs[e.tag] = e
    if set(defs) != {"ThingDef", "PawnKindDef"}:
        bad.append("RM_Ollathrix ThingDef/PawnKindDef pair not found in the Webwork source: %s" % sorted(defs))
        return bad
    ops = ET.parse(PATCH).getroot().findall("Operation")
    if len(ops) < 8:
        bad.append("expected 8 patch operations, found %d (sanity probe)" % len(ops))
    for op in ops:
        xp = op.findtext("xpath") or ""
        m = re.match(r'/Defs/(\w+)\[defName="RM_Ollathrix"\]/(.+)$', xp)
        if not m:
            bad.append("operation xpath is not an RM_Ollathrix path: %s" % xp)
            continue
        d, rest = defs[m.group(1)], m.group(2)
        node = d.find(re.sub(r"/li\[(\d+)\]", r"/li[\1]", rest))
        has_nomatch = op.find("nomatch") is not None
        if node is None and not has_nomatch:
            bad.append("%s matches nothing in the Webwork def and has no nomatch branch (silent no-op): %s" % (m.group(1), rest))
    if not re.search(r"<texPath>swanimals/Wyyyschokk/Wyyyschokk</texPath>", open(PATCH, encoding="utf-8").read()):
        bad.append("patch no longer swaps in the swanimals/Wyyyschokk texture")
    fac = [e for e in ET.parse(os.path.join(HERE, "Defs", "FactionDefs", "RSW_Shokk_FeraliskBrood.xml")).getroot()][0]
    for k, v in (("hidden", "true"), ("permanentEnemy", "true"), ("techLevel", "Animal"), ("categoryTag", "FeverWoodTwoFrontRaiders")):
        if fac.findtext(k) != v:
            bad.append("faction %s is %r, expected %r" % (k, fac.findtext(k), v))
    if fac.find("pawnGroupMakers/li/options/Wyyyschokk") is None:
        bad.append("faction does not field the Wyyyschokk")
    # the lure component looks the faction up by this exact name
    lure = os.path.join(SRC, "RimMandrake", "FeverWood", "Source", "RM_MapComponent_TwoFrontLure.cs")
    if os.path.isfile(lure) and '"%s"' % FACTION not in open(lure, encoding="utf-8").read():
        bad.append("the Fever Wood lure no longer names %s" % FACTION)
    about = open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read()
    for pid in ("mandrake.rm.biomes", "mlie.starwarsanimalcollection"):
        if "<packageId>%s</packageId>" % pid not in about:
            bad.append("About.xml lost dependency %s" % pid)
    if not os.path.isfile(os.path.join(SRC, "..", "design", "validation_walks", "RimStarWars", "Shokk.md")):
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
    suite = Suite("Shokk")
    suite.toggles = []          # no Mod Settings class exists (see static_checks and the walk)

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

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
                    raise ExpectationFailed("shipped defs did not resolve (is mlie.starwarsanimalcollection loaded? the "
                                            "FactionDef is MayRequire it): %r" % r)
        with t.component("donor_wyyyschokk_kind_resolves", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="PawnKindDef/Wyyyschokk;ThingDef/RM_Ollathrix", fields="defName", limit=4)
            if _live(t) and (not isinstance(r, dict) or r.get("notFound") or int(r.get("foundCount", 0)) != 2):
                raise ExpectationFailed("the donor Wyyyschokk kind or the RM_Ollathrix race is absent: %r" % r)

    @suite.chain("skin_patch")
    def skin_patch(t):
        with t.component("race_label_and_plural_are_wyyyschokk", beyond_toggle=True):
            f = _row(t, "ThingDef/RM_Ollathrix", "label,labelPlural")
            if _live(t):
                if str(f.get("label")).lower() != SKIN:
                    raise ExpectationFailed("ThingDef RM_Ollathrix label is %r after the skin patch, not %r" % (f.get("label"), SKIN))
                if str(f.get("labelPlural")).lower() != SKIN:
                    raise ExpectationFailed("ThingDef RM_Ollathrix labelPlural is %r, not %r (the plural operation matches nothing "
                                            "unless it carries a nomatch Add: the def ships no labelPlural)" % (f.get("labelPlural"), SKIN))
        with t.component("kind_label_and_plural_are_wyyyschokk", beyond_toggle=True):
            f = _row(t, "PawnKindDef/RM_Ollathrix", "label,labelPlural")
            if _live(t):
                for k in ("label", "labelPlural"):
                    if str(f.get(k)).lower() != SKIN:
                        raise ExpectationFailed("PawnKindDef RM_Ollathrix %s is %r, not %r" % (k, f.get(k), SKIN))
        with t.component("probe_can_read_a_different_label_control", beyond_toggle=True):
            f = _row(t, "ThingDef/Wolf_Timber", "label")
            if _live(t) and str(f.get("label")).lower() == SKIN:
                raise ExpectationFailed("an unpatched vanilla def reads the wyyyschokk label: the label check cannot say different")
        with t.component("description_names_the_canon_species", beyond_toggle=True):
            f = _row(t, "ThingDef/RM_Ollathrix", "description")
            if _live(t) and "Kashyyyk" not in str(f.get("description")):
                raise ExpectationFailed("RM_Ollathrix description is not the canon overlay: %r" % str(f.get("description"))[:120])
        with t.component("life_stage_art_swapped", beyond_toggle=True):
            if not _live(t):
                return
            f = _row(t, "PawnKindDef/RM_Ollathrix", "lifeStages", deep=True)
            blob = " ".join(_flat(f))
            if "swanimals/Wyyyschokk/Wyyyschokk" in blob:
                return
            if "Things/Pawn/Animal/RM_Ollathrix" in blob:
                raise ExpectationFailed("a life stage still carries the RM_Ollathrix texture after the skin patch")
            _unmeasured(t, "get_defs returns lifeStages as bare type names (no texPath) even with deep=True: %s" % blob[:120])

    @suite.chain("feralisk_brood")
    def feralisk_brood(t):
        with t.component("faction_is_hidden_permanent_enemy_animal", beyond_toggle=True):
            f = _row(t, "FactionDef/" + FACTION, "hidden,permanentEnemy,techLevel,categoryTag,humanlikeFaction")
            if _live(t):
                want = {"hidden": "true", "permanentenemy": "true", "humanlikefaction": "false"}
                for k, v in (("hidden", "true"), ("permanentEnemy", "true"), ("humanlikeFaction", "false")):
                    if str(f.get(k)).lower() != v:
                        raise ExpectationFailed("%s is %r, expected %r" % (k, f.get(k), v))
                if str(f.get("techLevel")) != "Animal":
                    raise ExpectationFailed("techLevel is %r, expected Animal" % f.get("techLevel"))
                if str(f.get("categoryTag")) != "FeverWoodTwoFrontRaiders":
                    raise ExpectationFailed("categoryTag is %r (the lure finds it by name, not tag; still a shipped value)" % f.get("categoryTag"))
        with t.component("combat_group_fields_the_wyyyschokk", beyond_toggle=True):
            if not _live(t):
                return
            f = _row(t, "FactionDef/" + FACTION, "pawnGroupMakers", deep=True)
            blob = " ".join(_flat(f))
            if "Wyyyschokk" in blob:
                return
            _unmeasured(t, "get_defs returns pawnGroupMakers as bare type names even with deep=True: %s" % blob[:120])

    @suite.chain("settings")
    def settings(t):
        with t.component("no_settings_class_by_design", beyond_toggle=True):
            if os.path.isdir(os.path.join(HERE, "Source")):
                raise ExpectationFailed("a Source/ folder now exists: this script has no settings_roundtrip chain")

    @suite.chain("two_front_lure")
    def two_front_lure(t):
        with t.component("fever_wood_second_front_fires_this_faction", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "RM_MapComponent_TwoFrontLure picks this faction as the Fever Wood raid's second wave; needs a "
                               "generated Fever Wood map and a raid (a different item's mechanism, owned by mandrake.rm.feverwood)")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
