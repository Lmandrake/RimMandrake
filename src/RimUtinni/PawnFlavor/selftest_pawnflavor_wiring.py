#!/usr/bin/env python3
"""selftest_pawnflavor_wiring.py -- PAWNFLAVOR_COVERAGE_GAPS_1: the static wiring/defs bars of validation.py are green on the
shipped mod and go red on each break they exist to catch (planted on the parsed data in memory, never the shipped files).
Run bare: python3 src/RimUtinni/PawnFlavor/selftest_pawnflavor_wiring.py"""
import copy
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)
import validation as V                                         # noqa: E402
import runner                                                  # noqa: E402
from modcheck import Suite                                     # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def base():
    stories, traits = V.load_pack_defs()
    return dict(wiring=copy.deepcopy(V.load_wiring()), stories=copy.deepcopy(stories), traits=traits, patch=set(V.patch_faction_names()),
                van_f=set(V.dump_names("FactionDef") or ()) or None, van_t=set(V.dump_names("TraitDef") or ()) or None,
                about=V.about_counts(), comments=dict(V.trait_comments()))


def findings(b):
    return V.wiring_findings(b["wiring"], b["stories"], b["traits"], b["patch"], b["van_f"], b["van_t"], b["about"], b["comments"])


def lis(b, tgt, kind):
    return next(l for t, k, l in b["wiring"] if t == tgt and k == kind)


def main():
    b = base()
    check("shipped mod: no finding", findings(b) == [], findings(b))
    check("sanity: 12 wired targets, 77 backstories, 13 traits, 13 JawaBSC categories drawn",
          len(set(t for t, _k, _l in b["wiring"])) == 12 and len(b["stories"]) == 77 and len(b["traits"]) == 13
          and len(set(c for v in b["stories"].values() for c in v["cats"] if c.startswith("JawaBSC_"))) == 13)
    check("sanity: the 3 deferred traits really are label-only today", all(
        not any(d.find(tag) is not None for d in b["traits"][n].findall("degreeDatas/li") for tag in V.EFFECT_TAGS) for n in V.DEFERRED_LABEL_ONLY))

    def brk(tag, fn, must):
        x = base()
        fn(x)
        got = findings(x)
        check("break %-40s reddens (%s)" % (tag, must), any(must in g for g in got), got)

    brk("Junkers declares the Blackstar filter", lambda x: lis(x, "RUT_Jawa_Junkers", "declare").append(["JawaBSC_Blackstar"]), "leak")
    brk("Pirate stops adding Blackstar", lambda x: lis(x, "Pirate", "raw").__setitem__(0, ["JawaBSC_Empire"]), "leak")
    brk("Junkers drops Pirate", lambda x: lis(x, "RUT_Jawa_Junkers", "declare").__setitem__(0, ["Tribal"]), "Junkers")
    brk("Hutt drops Offworld", lambda x: lis(x, "RUT_Jawa_HuttCartel", "declare").remove(["Offworld"]), "drop the parent")
    brk("TribeCivil gets two flavour categories", lambda x: lis(x, "TribeCivil", "declare").append(["JawaBSC_Moot"]), "JawaBSC_ categor")
    brk("Empire filter names two categories", lambda x: lis(x, "Empire", "raw")[0].append("JawaBSC_Hutt"), "exactly one")
    brk("Junkers operation missing", lambda x: x.__setitem__("wiring", [w for w in x["wiring"] if w[0] != "RUT_Jawa_Junkers"]), "Junkers")

    def blackstar_adult_only(x):
        for v in x["stories"].values():
            if "JawaBSC_Blackstar" in v["cats"]:
                v["slot"] = "Adulthood"
    brk("Blackstar has no childhood", blackstar_adult_only, "slots")
    brk("a backstory in an unwired category", lambda x: x["stories"].__setitem__("RUT_Jawa_Orphan", dict(slot="Adulthood", cats=["JawaBSC_Orphan"], traits=[])), "no faction wires")
    brk("Hutt faction missing from the Patches mod", lambda x: (x["patch"].discard("RUT_Jawa_HuttCartel"), x["van_f"] and x["van_f"].discard("RUT_Jawa_HuttCartel")), "wiring targets FactionDef")
    if b["van_f"]:
        brk("Empire missing from the vanilla dump", lambda x: x["van_f"].discard("Empire"), "wiring targets FactionDef")
    else:
        print("skip  vanilla-dump breaks: no readable dump here")

    def new_cosmetic_trait(x):
        el = ET.fromstring("<TraitDef><defName>RUT_Jawa_Cosmetic</defName><degreeDatas><li><label>x</label><description>y</description></li></degreeDatas></TraitDef>")
        x["traits"]["RUT_Jawa_Cosmetic"] = el
    brk("a new label-only trait", new_cosmetic_trait, "no mechanical effect")

    def deferred_gains_effect(x):
        li = x["traits"]["RUT_Jawa_StillTemper"].find("degreeDatas/li")
        ET.SubElement(ET.SubElement(li, "statOffsets"), "MentalBreakThreshold").text = "-0.02"
    brk("a deferred trait gains an effect", deferred_gains_effect, "remove it from DEFERRED_LABEL_ONLY")
    brk("a deferred trait loses its C# comment", lambda x: x["comments"].__setitem__("RUT_Jawa_ReapsTheFlames", "nothing to see"), "no longer says")

    def trait_without_label(x):
        x["traits"]["RUT_Jawa_SandStoic"].find("degreeDatas/li/label").text = ""
    brk("a trait with an empty label", trait_without_label, "no label or description")
    brk("a backstory forces a missing trait", lambda x: x["stories"]["RUT_Jawa_AcademyCadet"]["traits"].append("RUT_Jawa_Ghost"), "names trait")
    brk("About says fifty backstories", lambda x: x.__setitem__("about", x["about"].replace("Seventy-seven", "Fifty")), "About.xml")
    brk("About says seven inherit", lambda x: x.__setitem__("about", x["about"].replace("other eight", "other seven")), "About.xml")
    brk("About childhood split wrong", lambda x: x.__setitem__("about", x["about"].replace("30 childhoods", "31 childhoods")), "About.xml")

    # the chain: clean + each class of finding reddens its own bar; the deferred stub and the live stub stay UNMEASURED
    def chain(extra=None):
        saved = V._all_findings
        if extra:
            def fake(vanilla=True):
                f, vf, vt = saved(vanilla)
                return f + [extra], vf, vt
            V._all_findings = fake
        try:
            suite = Suite("PawnFlavorWiring")
            suite.chain("faction_wiring_static")(V.faction_wiring_static)
            s = FastSession(transport=MockTransport(MockGame()), strict=False)
            with s:
                res = runner.run_suite(suite, s, anchor=None, mod=None)
        finally:
            V._all_findings = saved
        return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
    got = chain()
    hard = [k for k in got if k not in ("label_only_traits_are_the_declared_deferred_ones", "live_draw_per_faction_and_trait_effect_state_read")]
    check("clean chain: every static bar PASSes or is UNMEASURED only for a missing dump", all(got[k] in ("PASS", "UNMEASURED") for k in hard) and got["inherited_filters_restate_the_parent_and_add_one_flavour_category"] == "PASS", got)
    check("clean chain: the declared-deferred traits and the live draw are UNMEASURED, never PASS",
          got["label_only_traits_are_the_declared_deferred_ones"] == "UNMEASURED" and got["live_draw_per_faction_and_trait_effect_state_read"] == "UNMEASURED", got)
    for finding, comp in (("pirate leak containment: x", "blackstar_does_not_leak_into_the_junkers"),
                          ("About.xml says nothing", "about_counts_match_the_shipped_defs"),
                          ("category JawaBSC_Q is wired to a faction but has backstories for slots [] only", "every_wired_category_is_drawable_in_both_slots_and_none_is_orphaned"),
                          ("something brand new nobody claims", "no_finding_escapes_the_bars_above")):
        check("chain: %r reddens %s" % (finding[:30], comp), chain(finding).get(comp) == "FAIL", chain(finding))

    if FAILS:
        print("\n%d PawnFlavor wiring selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall PawnFlavor wiring selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
