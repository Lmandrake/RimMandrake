#!/usr/bin/env python3
"""selftest_starwarspatches_semantics.py -- STARWARSPATCHES_COVERAGE_GAPS_1 (second half): the patch_semantics_static bars are green on
the shipped patches + current dump and go red on each break they exist to catch (planted on parsed copies, never the shipped
files). Run bare: python3 src/RimStarWars/StarWarsPatches/selftest_starwarspatches_semantics.py"""
import copy
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)
import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from modcheck import Suite                                     # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def main():
    roots, pack, dump = V.load_patch_roots(), V.pack_def_names(), V.dump_names()
    if dump is None:
        # a synthetic dump keeps the defName-literal rules exercised on a machine with no def dump
        dump = dict(XenotypeDef={"RSW_X"}, GeneDef=set(), WeatherDef={"Clear", "Sandstorm"}, ThingDef=set(), PawnKindDef={"Grenadier"}, FactionDef=set(), BiomeDef={"Desert"})
        print("note  no readable dump: using a synthetic one for the break tests")
        dump_is_real = False
    else:
        dump_is_real = True
    base = V.patch_findings(roots, pack, dump)
    check("shipped patches: no finding", base == [] or not dump_is_real, base)
    nested = sum(1 for _f, r in roots for e in r.iter() if e.tag in ("match", "nomatch") and e.get("Class", "").startswith("PatchOperation"))
    check("sanity: nested <match>/<nomatch> operations exist and are walked (the weather attaches live there)", nested > 20, nested)
    check("sanity: >= 100 operations parsed, 4 pack weathers", sum(1 for _f, r in roots for e in r.iter() if e.get("Class", "").startswith("PatchOperation")) >= 100 and len(pack.get("WeatherDef", ())) == 4)

    def brk(tag, fn, must, roots_in=None, pack_in=None):
        r = copy.deepcopy(roots_in if roots_in is not None else roots)
        pk = copy.deepcopy(pack_in if pack_in is not None else pack)
        fn(r, pk)
        got = V.patch_findings(r, pk, dump)
        check("break %-42s reddens (%s)" % (tag, must), any(must in g for g in got), got[:4])

    def file(r, name):
        return next(root for fn, root in r if fn == name)

    def first_weather_value(r):
        for el in file(r, "SWDesertWeather_Attach.xml").iter("value"):
            if len(el) and el[0].tag.startswith("RSW_SW_"):
                return el
    brk("<li> into baseWeatherCommonalities", lambda r, p: ET.SubElement(first_weather_value(r), "li").__setattr__("text", "RSW_SW_Sandstorm"), "dictionary-keyed")
    brk("attach names a nonexistent weather", lambda r, p: ET.SubElement(first_weather_value(r), "RSW_SW_NoSuch").__setattr__("text", "5"), "attaches weather")
    brk("attach at commonality 0", lambda r, p: first_weather_value(r)[0].__setattr__("text", "0"), "never rolls")

    def unattach_redfog(r, p):
        for el in file(r, "SWDesertWeather_Attach.xml").iter("value"):
            for c in list(el):
                if c.tag == "RSW_SW_RedFog":
                    el.remove(c)
    brk("a pack weather is never attached", unattach_redfog, "dead content")

    def mayrequire_op(r, p):
        for el in file(r, "SWDesertWeather_Attach.xml").iter("Operation"):
            el.set("MayRequire", "some.mod")
            return
    brk("MayRequire on a whole operation", mayrequire_op, "MayRequire")

    def add_op(r, p, xpath, guarded=False, value=True):
        root = file(r, "BodySizeIsReal.xml")
        op = ET.fromstring('<Operation Class="PatchOperationAdd"><xpath>%s</xpath>%s</Operation>' % (xpath, "<value><li>x</li></value>" if value else ""))
        if guarded:
            wrap = ET.fromstring('<Operation Class="PatchOperationFindMod"><mods><li>Some Mod</li></mods><match/></Operation>')
            wrap.find("match").append(op)
            op = wrap
        root.append(op)
    brk("unguarded xpath at a def that does not exist", lambda r, p: add_op(r, p, '/Defs/PawnKindDef[defName="RSW_NoSuchKind"]/x'), "xpath targets")
    brk("an Add with no value", lambda r, p: add_op(r, p, "/Defs/BiomeDef[defName=\"Desert\"]/x", value=False), "has no value")

    r = copy.deepcopy(roots)
    add_op(r, pack, '/Defs/PawnKindDef[defName="RSW_NoSuchKind"]/x', guarded=True)
    got = V.patch_findings(r, pack, dump)
    check("control: the same xpath under a FindMod guard is NOT a finding", not any("RSW_NoSuchKind" in g for g in got), got[:3])

    def bad_value(r, p):
        root = file(r, "VanillaFaction_Xenotypes.xml")
        root.append(ET.fromstring('<Operation Class="PatchOperationAdd"><xpath>/Defs/FactionDef[defName="Pirate"]/x</xpath><value><li>RSW_NoSuchXeno</li></value></Operation>'))
    brk("a value names an undefined RSW_ def", bad_value, "value names")

    def wrong_root(r, p):
        r[0] = (r[0][0], ET.fromstring("<Defs/>"))
    brk("a patch file with a <Defs> root", wrong_root, "not <Patch>")

    # the weapon-tag index
    things = [dict(defName="W", fields=dict(weaponTags=["A", "B"]))]
    kinds = [dict(defName="RSW_Disarmed", modName="X", fields=dict(weaponTags=["Z"], weaponMoney=dict(min=1, max=10))),
             dict(defName="Armed", modName="Core", fields=dict(weaponTags=["A"], weaponMoney=dict(min=1, max=10))),
             dict(defName="NoBudget", modName="Core", fields=dict(weaponTags=["Z"], weaponMoney=dict(min=0, max=0))),
             dict(defName="Third", modName="Big and Small", fields=dict(weaponTags=["Q"], weaponMoney=dict(min=1, max=10))),
             dict(defName="CoreDisarmed", modName="Core", fields=dict(weaponTags=["Y"], weaponMoney=dict(min=1, max=10)))]
    dis = V.disarmed_kinds(things, kinds)
    check("disarmed_kinds finds exactly the 3 with tags no weapon carries and a weapon budget", sorted(d[0] for d in dis) == ["CoreDisarmed", "RSW_Disarmed", "Third"], dis)
    check("ours_or_official: RSW_ prefix and Core count, a third-party kind does not", [V.ours_or_official(d) for d in sorted(dis)] == [True, True, False], dis)
    check("real dump: no Core/DLC/campaign kind is disarmed (3rd-party ones are noted, not failed)",
          not dump_is_real or not [d for d in V.disarmed_kinds(V.dump_defs("ThingDef"), V.dump_defs("PawnKindDef")) if V.ours_or_official(d)])

    # the chain
    def chain(extra=None, dis_extra=None):
        saved, saved_dis = V.patch_findings, V.disarmed_kinds
        if extra:
            V.patch_findings = lambda *a: saved(*a) + [extra]
        if dis_extra:
            V.disarmed_kinds = lambda *a: saved_dis(*a) + [dis_extra]
        try:
            suite = Suite("SWPatchSemantics")
            suite.chain("patch_semantics_static")(V.patch_semantics_static)
            s = FastSession(transport=MockTransport(MockGame()), strict=False)
            with s:
                res = runner.run_suite(suite, s, anchor=None, mod=None)
        finally:
            V.patch_findings, V.disarmed_kinds = saved, saved_dis
        return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
    got = chain()
    stub = "blast_door_opens_and_closes_state_read"
    check("clean chain: static bars PASS (or UNMEASURED only for a missing dump), the door stub is UNMEASURED",
          all(v in ("PASS", "UNMEASURED") for k, v in got.items() if k != stub) and got[stub] == "UNMEASURED"
          and (not dump_is_real or all(v == "PASS" for k, v in got.items() if k != stub)), got)
    for finding, comp in (("X: adds <li> to dictionary-keyed baseWeatherCommonalities", "dictionary_keyed_fields_never_get_li"),
                          ("X: carries MayRequire on a whole operation", "patch_files_wellformed_and_no_inert_mayrequire"),
                          ("weather def W is defined but never attached (dead content)", "weather_defs_are_all_attached_with_real_names_and_positive_commonality"),
                          ("X: value names RSW_Q, which nobody defines", "patch_xpath_literals_and_values_name_loaded_defs_or_are_guarded")):
        check("chain: %r reddens %s" % (finding[:28], comp), chain(finding).get(comp) == "FAIL", chain(finding))
    if dump_is_real:
        got = chain(dis_extra=("RSW_Ghost", "Whatever", ["Z"]))
        check("chain: a disarmed campaign kind reddens the weapon-tag bar", got["weapon_tag_index_leaves_no_core_or_campaign_kind_disarmed"] == "FAIL", got)

    if FAILS:
        print("\n%d StarWarsPatches semantic selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall StarWarsPatches semantic selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
