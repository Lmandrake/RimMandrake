#!/usr/bin/env python3
"""selftest_onboard.py: proves Source/onboard.py (stamp, check, land) on a temporary copy of a smelter-like fixture.

The fixture is the factory mod's own smelter ThingDef, verbatim (Source/onboarding_staged/_fixture/donor_smelter.xml), its six ProcessDefs,
and the smelter's row as the shipped table has it. Nothing is read from the installed factory mod and nothing in the real Defs/ is touched.

What it shows, each printing the value it measured and the limit it was held to:
  must stay green   stamp then check passes; every gating row (three_level_defs, wreck_is_carried, two_projects_studied, table_row_whole)
                    and every row of our own (staged_files, row_whole, texts, donor_fidelity, ids) has no fault
  fidelity          the stamped three defs equal the shipped smelter defs field by field (texts, and the Refurbished picture, which the
                    brief points at the donor's own, excepted): the fields compared, the fields that differ
  must be refused   a Kludged process the donor lacks (at stamp, and planted in a stamped levels.xml at check); a row without
                    refurbishCost/RM_WM_AncientComponent (at stamp, and planted in a stamped row at check); a duplicate analysisID
                    (inside the line, and one already held by a landed def); a donor field that leaks into a level; a banned word in a text;
                    a Wrecked def with one comp too many; a wrong analysisID for the line number; a stamp with the donor not found (exit 2)
  land              refused without passing pictures; refused when a file exists; lands the three files on a copy and removes the stage

Last line: selftest_onboard: PASS or selftest_onboard: FAIL.
"""
import contextlib
import copy
import io
import os
import re
import shutil
import sys
import tempfile

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import onboard as ob  # noqa: E402

MOD = os.path.dirname(HERE)
FIX = os.path.join(HERE, "onboarding_staged", "_fixture")
SHIPPED_LEVELS = os.path.join(MOD, "Defs", "ThingDefs_Buildings", "Buildings_WreckedMachines_AutomatedSmelter.xml")
RESULTS = []


def say(ok, name, measured, limit):
    RESULTS.append(ok)
    print("%s  %-62s measured %-40s limit %s" % ("PASS" if ok else "FAIL", name, measured, limit))


def run(args):
    """-> (exit code, output) of onboard.main(args), in this process."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ob.main(args)
    return rc, buf.getvalue()


def make_fixture(tmp):
    """-> (mod dir, vfef dir): a mini mod with the smelter's row staged, and a mini factory mod holding the smelter donor."""
    vfef = os.path.join(tmp, "vfef")
    os.makedirs(os.path.join(vfef, "1.6", "Defs", "ThingDefs_Buildings"))
    os.makedirs(os.path.join(vfef, "1.6", "Defs", "ProcessDefs"))
    shutil.copy(os.path.join(FIX, "donor_smelter.xml"), os.path.join(vfef, "1.6", "Defs", "ThingDefs_Buildings", "Buildings_Factories.xml"))
    shutil.copy(os.path.join(FIX, "processdefs_smelter.xml"), os.path.join(vfef, "1.6", "Defs", "ProcessDefs", "ProcessDefs.xml"))
    mod = os.path.join(tmp, "src", "RimMandrake", "WreckedMachines")
    os.makedirs(os.path.join(mod, "Source", "onboarding_staged", "smelter"))
    os.makedirs(os.path.join(mod, "Defs", "ThingDefs_Buildings"))
    shutil.copy(os.path.join(MOD, "Source", "WreckedMachinesMod.cs"), os.path.join(mod, "Source", "WreckedMachinesMod.cs"))
    shutil.copy(os.path.join(FIX, "row_smelter.xml"), os.path.join(mod, "Source", "onboarding_staged", "smelter", "row.xml"))
    open(os.path.join(mod, "Defs", "ThingDefs_Buildings", "Stub.xml"), "w").write('<?xml version="1.0" encoding="utf-8"?>\n<Defs/>\n')
    return mod, vfef


def staged(mod, f="row.xml", key="smelter"):
    return os.path.join(mod, "Source", "onboarding_staged", key, f)


def edit(path, fn):
    """Parse path, let fn change the root, write it back."""
    tree = etree.parse(path, etree.XMLParser(remove_blank_text=False))
    fn(tree.getroot())
    open(path, "w", encoding="utf-8").write(etree.tostring(tree, encoding="unicode"))


def add_twin(mod, vfef, number):
    """A second staged line (key twin, donor VFEFactory_TwinSmelter: the smelter donor under another name) with the given line number."""
    f = os.path.join(vfef, "1.6", "Defs", "ThingDefs_Buildings", "Buildings_Factories.xml")
    body = open(f).read().replace("VFEFactory_AutomatedSmelter", "VFEFactory_TwinSmelter")
    open(f, "w").write(body)
    row = open(os.path.join(FIX, "row_smelter.xml")).read().replace("<key>smelter</key>", "<key>twin</key>").replace("RM_WM_Line_smelter", "RM_WM_Line_twin") \
        .replace("AutomatedSmelter", "TwinSmelter").replace("line number 1", "line number %d" % number)
    os.makedirs(os.path.join(mod, "Source", "onboarding_staged", "twin"))
    open(staged(mod, "row.xml", "twin"), "w").write(row)


def st(e, value):
    """Set the text of an element; returns the element (for use inside a list comprehension)."""
    e.text = value
    return e


def faults(mod, vfef, key="smelter"):
    """-> ({row: [faults]}, lines read) of check_key on the fixture."""
    module = ob.load_rows_for(MOD)
    return ob.check_key(mod, key, vfef, module, set())


def gating(res):
    return {r: f for r, f in res.items() if f and r in ob.GATING + ob.OWN_ROWS}


def flat(d, skip_text, skip_paths):
    """A def as a list of (path, text) with comments and the listed text fields left out."""
    out = []

    def walk(e, path):
        for c in e:
            if not isinstance(c.tag, str):
                continue
            p = "%s/%s%s" % (path, c.tag, ("[%s]" % c.get("Class")) if c.get("Class") else "")
            out.append((p, (c.text or "").strip() if p.split("/")[-1].split("[")[0] not in skip_text else "*"))
            walk(c, p)
    walk(d, d.tag)
    return [x for x in out if x[0] not in skip_paths]


def main():
    tmp = tempfile.mkdtemp(prefix="selftest_onboard_")
    try:
        # ---- green path
        mod, vfef = make_fixture(tmp)
        rc, out = run(["stamp", "smelter", "--mod", mod, "--vfef", vfef])
        say(rc == 0 and os.path.isfile(staged(mod, "levels.xml")) and os.path.isfile(staged(mod, "projects.xml")), "stamp writes levels.xml and projects.xml",
            "exit %d" % rc, "exit 0 and both files")
        res, n = faults(mod, vfef)
        worst = {r: len(f) for r, f in res.items() if f and r in ob.GATING + ob.OWN_ROWS}
        say(not worst and n == 1, "check of the stamped smelter: no gating or own fault", "%d faulty rows, %d lines read" % (len(worst), n), "0 faulty rows, 1 line read")
        rcc, _ = run(["check", "smelter", "--mod", mod, "--vfef", vfef])
        say(rcc == 0, "check exits 0 on the stamped smelter", "exit %d" % rcc, "exit 0")
        say(bool(res["pictures_of_its_own"]) and bool(res["pictures_judged"]), "the picture rows fail, as they must until the art is made and judged",
            "%d + %d faults" % (len(res["pictures_of_its_own"]), len(res["pictures_judged"])), "both above 0")

        # ---- pictures made and judged: the check, which reads a temporary copy of the mod, finds the judge's record
        import hashlib
        import json
        slots = []
        for d in etree.parse(staged(mod, "levels.xml")).getroot():
            if isinstance(d.tag, str) and d.findtext("defName", "").endswith(("_Wrecked", "_Kludged")):
                for facing in ("north", "south", "east", "west"):
                    f = os.path.join(mod, "Textures", *d.findtext("graphicData/texPath").split("/")) + "_%s.png" % facing
                    os.makedirs(os.path.dirname(f), exist_ok=True)
                    open(f, "wb").write(("picture %s %s" % (d.findtext("defName"), facing)).encode())
                    slots.append({"slot": os.path.relpath(f, tmp), "sha": hashlib.sha256(open(f, "rb").read()).hexdigest()})
        recs = os.path.join(tmp, "design", "concepts", "WreckedMachines", "version", "evidence", "art")
        os.makedirs(recs)
        json.dump({"verdict": "keep", "judge": {"made_it": False}, "slots": slots}, open(os.path.join(recs, "smelter.json"), "w"))
        res2, _ = faults(mod, vfef)
        say(len(slots) == 8 and not res2["pictures_of_its_own"] and not res2["pictures_judged"],
            "with its 8 pictures made and a judge's record for each, the picture rows pass in the check's temporary copy",
            "%d pictures, %d + %d faults%s" % (len(slots), len(res2["pictures_of_its_own"]), len(res2["pictures_judged"]),
                                              (": " + res2["pictures_judged"][0]) if res2["pictures_judged"] else ""), "8 pictures, 0 + 0 faults")
        open(os.path.join(mod, "Textures", *slots[0]["slot"].split(os.sep)[4:]), "wb").write(b"redrawn after the judge looked")
        res3, _ = faults(mod, vfef)
        say(bool(res3["pictures_judged"]), "a picture changed after the judge looked fails pictures_judged", "%d faults" % len(res3["pictures_judged"]), "above 0")
        shutil.rmtree(os.path.join(mod, "Textures"))
        shutil.rmtree(os.path.join(tmp, "design"))

        # ---- fidelity against the shipped smelter
        new = etree.parse(staged(mod, "levels.xml")).getroot()
        old = etree.parse(SHIPPED_LEVELS).getroot()
        text_tags = {"description", "jobString", "inspectString", "completedLetterLabel", "completedLetter"}
        compared = diff = 0
        diffs = []
        olds = {d.findtext("defName"): d for d in old if isinstance(d.tag, str) and d.tag == "ThingDef"}
        for d in new:
            if not isinstance(d.tag, str):
                continue
            nm = d.findtext("defName")
            skip = {"ThingDef/graphicData/texPath"} if nm.endswith("_Refurbished") else set()
            a, b = flat(olds[nm], text_tags, skip), flat(d, text_tags, skip)
            compared += max(len(a), len(b))
            for x, y in zip(a, b):
                if x != y:
                    diff += 1
                    diffs.append("%s %s" % (nm, x[0] if x[0] == y[0] else "%s vs %s" % (x, y)))
            if len(a) != len(b):
                diff += abs(len(a) - len(b))
                diffs.append("%s: %d fields shipped, %d stamped" % (nm, len(a), len(b)))
        say(diff == 0 and compared > 150 and len(olds) == 3, "the stamped smelter equals the shipped smelter field by field",
            "%d of %d fields differ%s" % (diff, compared, (" (" + diffs[0] + ")") if diffs else ""), "0 differ, over 150 fields compared, 3 defs")
        proj_new = etree.parse(staged(mod, "projects.xml")).getroot()
        proj_old = etree.parse(os.path.join(MOD, "Defs", "ResearchProjectDefs", "ResearchProjects_WreckedMachines.xml")).getroot()
        pold = {d.findtext("defName"): d for d in proj_old if isinstance(d.tag, str)}
        pd = []
        for d in proj_new:
            if not isinstance(d.tag, str):
                continue
            o = pold[d.findtext("defName")]
            for t in ("baseCost", "techLevel", "tab", "researchViewX", "prerequisites/li", "requiredAnalyzed/li", "label"):
                if (o.findtext(t) or "").strip() != (d.findtext(t) or "").strip():
                    pd.append("%s %s: %r vs %r" % (d.findtext("defName"), t, o.findtext(t), d.findtext(t)))
        # researchViewY: the shipped smelter sits at y 0 (the stamp puts a line at its line number: 1 here)
        say(not pd, "the stamped smelter projects equal the shipped ones (cost, tier, tab, x, links, label)", "%d differ%s" % (len(pd), (": " + pd[0]) if pd else ""), "0 differ")

        # ---- planted faults, each on a fresh copy
        def fresh():
            m, v = make_fixture(tempfile.mkdtemp(dir=tmp))
            return m, v

        m, v = fresh()
        edit(staged(m), lambda r: r.find(ob.LINE_TAG + "/kludgedProcesses").append(etree.fromstring("<li>VFEFactory_NotInTheDonor</li>")))
        rc, out = run(["stamp", "smelter", "--mod", m, "--vfef", v])
        say(rc == 1 and "NotInTheDonor" in out and not os.path.exists(staged(m, "levels.xml")), "PLANT a Kludged process the donor lacks: stamp refuses",
            "exit %d, levels.xml written: %s" % (rc, os.path.exists(staged(m, "levels.xml"))), "exit 1, nothing written")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "levels.xml"), lambda r: [st(li, "VFEFactory_NotInTheDonor") for li in r.iter("li")
                                                  if (li.text or "") == "VFEFactory_SmeltWeapon" and li.getparent().getparent().find("canOverclock") is not None][:1])
        res, _ = faults(m, v)
        say(bool(res["donor_fidelity"]) and "NotInTheDonor" in " ".join(res["donor_fidelity"]), "PLANT that process in a stamped levels.xml: check faults donor_fidelity",
            "%d faults" % len(res["donor_fidelity"]), "at least 1")
        rc, _ = run(["check", "smelter", "--mod", m, "--vfef", v])
        say(rc == 1, "  and check exits 1", "exit %d" % rc, "exit 1")

        m, v = fresh()
        edit(staged(m), lambda r: r.find(ob.LINE_TAG + "/refurbishCost").remove(r.find(ob.LINE_TAG + "/refurbishCost/RM_WM_AncientComponent")))
        rc, out = run(["stamp", "smelter", "--mod", m, "--vfef", v])
        say(rc == 1 and "AncientComponent" in out, "PLANT a row with no refurbishCost/RM_WM_AncientComponent: stamp refuses", "exit %d" % rc, "exit 1")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m), lambda r: r.find(ob.LINE_TAG + "/refurbishCost").remove(r.find(ob.LINE_TAG + "/refurbishCost/RM_WM_AncientComponent")))
        res, _ = faults(m, v)
        say(bool(res["row_whole"]) and bool(res["table_row_whole"]), "PLANT that in a stamped line's row: check faults row_whole and table_row_whole",
            "%d + %d faults" % (len(res["row_whole"]), len(res["table_row_whole"])), "both above 0")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "levels.xml"), lambda r: [st(e, "77120011") for e in r.iter("analysisID")])
        res, _ = faults(m, v)
        say(bool(res["ids"]) and bool(res["two_projects_studied"]), "PLANT a duplicate analysisID inside the line: check faults ids and two_projects_studied",
            "%d + %d faults" % (len(res["ids"]), len(res["two_projects_studied"])), "both above 0")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        open(os.path.join(m, "Defs", "ThingDefs_Buildings", "Stub.xml"), "w").write(
            '<?xml version="1.0" encoding="utf-8"?>\n<Defs><ThingDef><defName>Stub_Other</defName><comps>'
            '<li Class="CompProperties_CompAnalyzableUnlockResearch"><analysisID>77120012</analysisID></li></comps></ThingDef></Defs>\n')
        res, _ = faults(m, v)
        say(bool(res["two_projects_studied"]), "PLANT an analysisID that a landed def already holds: check faults two_projects_studied", "%d faults" % len(res["two_projects_studied"]), "at least 1")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        add_twin(m, v, 1)
        rc1, _ = run(["stamp", "twin", "--mod", m, "--vfef", v])
        res, _ = faults(m, v, "twin")
        say(rc1 == 0 and bool(res["ids"]), "PLANT a second staged line with the same line number: check faults ids", "stamp exit %d, %d faults" % (rc1, len(res["ids"])), "stamp exit 0, at least 1 fault")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        add_twin(m, v, 2)
        rc1, _ = run(["stamp", "twin", "--mod", m, "--vfef", v])
        res, n = faults(m, v, "twin")
        rca, outa = run(["check", "--all", "--mod", m, "--vfef", v])
        say(rc1 == 0 and not gating(res) and rca == 0, "a second staged line with its own line number stays green (check twin, check --all)",
            "%d faulty rows, --all exit %d" % (len(gating(res)), rca), "0 faulty rows, exit 0")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "levels.xml"), lambda r: [st(e, "77120099") for e in r.iter("analysisID")][:1])
        res, _ = faults(m, v)
        say(bool(res["ids"]), "PLANT an analysisID the line number does not make: check faults ids", "%d faults" % len(res["ids"]), "at least 1")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "levels.xml"), lambda r: [t.addnext(etree.fromstring("<designationCategory>Production</designationCategory>"))
                                                 for t in r.findall("ThingDef")[1].findall("tickerType")])
        res, _ = faults(m, v)
        say(bool(res["donor_fidelity"]) or bool(res["three_level_defs"]), "PLANT a designationCategory on the Kludged level: refused",
            "%d + %d faults" % (len(res["donor_fidelity"]), len(res["three_level_defs"])), "at least 1 in all")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "levels.xml"), lambda r: [st(e, "A refurbished grade of machine.") for e in r.findall("ThingDef")[2].findall("description")])
        res, _ = faults(m, v)
        say(bool(res["texts"]), "PLANT a banned word in a description: check faults texts", "%d faults" % len(res["texts"]), "at least 1")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "levels.xml"), lambda r: r.findall("ThingDef")[0].find("comps").append(etree.fromstring('<li Class="CompProperties_Flickable"/>')))
        res, _ = faults(m, v)
        say(bool(res["donor_fidelity"]), "PLANT a donor comp on the Wrecked level: check faults donor_fidelity", "%d faults" % len(res["donor_fidelity"]), "at least 1")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "levels.xml"), lambda r: r.findall("ThingDef")[0].find("minifiedDef").getparent().remove(r.findall("ThingDef")[0].find("minifiedDef")))
        res, _ = faults(m, v)
        say(bool(res["wreck_is_carried"]) or bool(res["three_level_defs"]), "PLANT a Wrecked def that cannot be carried: refused", "%d faults" % len(res["wreck_is_carried"]), "at least 1")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "projects.xml"), lambda r: r.findall("ResearchProjectDefs")[:0] or r.remove(r.findall("ResearchProjectDef")[1]))
        res, _ = faults(m, v)
        say(bool(res["two_projects_studied"]), "PLANT a line with one project only: check faults two_projects_studied", "%d faults" % len(res["two_projects_studied"]), "at least 1")

        m, v = fresh()
        os.remove(os.path.join(v, "1.6", "Defs", "ThingDefs_Buildings", "Buildings_Factories.xml"))
        rc, out = run(["stamp", "smelter", "--mod", m, "--vfef", v])
        say(rc == 2 and "COULD NOT LOOK" in out, "PLANT a donor that is not there: stamp says COULD NOT LOOK", "exit %d" % rc, "exit 2")

        m, v = fresh()
        edit(staged(m), lambda r: st(r.find(ob.LINE_TAG + "/label"), "smelter"))
        rc, out = run(["stamp", "smelter", "--mod", m, "--vfef", v])
        say(rc == 1 and "own label" in out, "PLANT a row label that is not the donor's: stamp refuses", "exit %d" % rc, "exit 1")

        # ---- a donor process that needs another mod keeps that condition on every level (the failure that happened, 2026-11-27:
        # the Kludged alloy forge named VFEFactory_AlloyBronze bare, the donor has it MayRequire VFE Classical, and the load said
        # "Could not resolve cross-reference to PipeSystem.ProcessDef named VFEFactory_AlloyBronze")
        def conditional_donor(v, attr, value):
            f = os.path.join(v, "1.6", "Defs", "ThingDefs_Buildings", "Buildings_Factories.xml")
            body = open(f).read()
            assert "<li>VFEFactory_SmeltMetalFromSlag</li>" in body
            open(f, "w").write(body.replace("<li>VFEFactory_SmeltMetalFromSlag</li>", '<li %s="%s">VFEFactory_SmeltMetalFromSlag</li>' % (attr, value)))

        def conditions(m_, attr):
            out = {}
            for d in etree.parse(staged(m_, "levels.xml")).getroot():
                if isinstance(d.tag, str) and d.findtext("defName"):
                    for li in d.findall("comps/li/processes/li"):
                        if li.text == "VFEFactory_SmeltMetalFromSlag":
                            out[d.findtext("defName").rsplit("_", 1)[-1]] = li.get(attr)
            return out
        # Both condition attributes the factory mod writes on a process entry: MayRequire, and MayRequireAnyOf (the factory
        # mod's biofuel refinery lists VFEFactory_MakeChemfuelFromRedWood MayRequireAnyOf="sarg.alphaanimals,sarg.alphabiomes").
        for attr, value in (("MayRequire", "Some.OtherMod"), ("MayRequireAnyOf", "Some.OtherMod,Some.ThirdMod")):
            m, v = fresh()
            conditional_donor(v, attr, value)
            rc, out = run(["stamp", "smelter", "--mod", m, "--vfef", v])
            got = conditions(m, attr) if rc == 0 else {}
            say(got == {"Kludged": value, "Refurbished": value}, "a donor process that needs another mod keeps its %s on the Kludged and the Refurbished level" % attr,
                "exit %d, %s" % (rc, got), "%s on both" % value)
            if rc == 0:
                edit(staged(m, "levels.xml"), lambda r: [li.attrib.pop(attr, None) for li in r.iter("li")
                                                          if li.text == "VFEFactory_SmeltMetalFromSlag" and li.getparent().getparent().find("canOverclock") is not None][:1])
            res, _ = faults(m, v)
            say(any(attr in f for f in res["donor_fidelity"]), "PLANT that %s dropped from the Kludged level: check faults donor_fidelity" % attr,
                "%d faults" % len(res["donor_fidelity"]), "at least 1 that names %s" % attr)

        # ---- a donor whose XML lists no processes (the factory mod makes them in code: the fish farm). Each level keeps an empty
        # <processes> element. With none, the game makes no list: the Kludged fish farm threw in the factory framework's config
        # check at startup and the C# found no list to fill (live, 2026-11-27).
        for donor_has_element in (True, False):
            m, v = fresh()
            f = os.path.join(v, "1.6", "Defs", "ThingDefs_Buildings", "Buildings_Factories.xml")

            def empty(r):
                for p in list(r.iter("processes")):
                    if donor_has_element:
                        for li in list(p):
                            p.remove(li)
                    else:
                        p.getparent().remove(p)
            edit(f, empty)

            def count_row(r):
                row = r.find(ob.LINE_TAG)
                row.remove(row.find("kludgedProcesses"))
                (row.find("kludgedProcessCount") if row.find("kludgedProcessCount") is not None
                 else etree.SubElement(row, "kludgedProcessCount")).text = "2"
            edit(staged(m), count_row)
            rc, out = run(["stamp", "smelter", "--mod", m, "--vfef", v])
            got = {}
            if rc == 0:
                for d in etree.parse(staged(m, "levels.xml")).getroot():
                    if isinstance(d.tag, str) and d.findtext("defName") and d.find("comps/li/canOverclock") is not None:
                        got[d.findtext("defName").rsplit("_", 1)[-1]] = len(d.findall("comps/li/processes"))
            say(got == {"Kludged": 1, "Refurbished": 1}, "a donor with %s: the Kludged and the Refurbished level each keep one <processes> element"
                % ("an empty process list" if donor_has_element else "a processor and no <processes> element"), "exit %d, %s" % (rc, got), "1 on both")

        # ---- land
        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        rc, out = run(["land", "smelter", "--mod", m, "--vfef", v])
        say(rc == 1 and "pictures" in out and os.path.isfile(staged(m, "levels.xml")), "land refuses while the pictures have not passed", "exit %d, staged files kept: %s" % (rc, os.path.isfile(staged(m, "levels.xml"))), "exit 1, files kept")
        dest = ob.landing(m, "smelter", "VFEFactory_AutomatedSmelter")
        os.makedirs(os.path.dirname(dest["levels.xml"]), exist_ok=True)
        open(dest["levels.xml"], "w").write("x")
        rc, out = run(["land", "smelter", "--mod", m, "--vfef", v, "--without-pictures"])
        say(rc == 1 and os.path.isfile(staged(m, "row.xml")) and not os.path.exists(dest["row.xml"]), "land refuses when a destination file exists, and moves nothing",
            "exit %d, row moved: %s" % (rc, os.path.exists(dest["row.xml"])), "exit 1, nothing moved")
        os.remove(dest["levels.xml"])
        rc, out = run(["land", "smelter", "--mod", m, "--vfef", v, "--without-pictures"])
        say(rc == 0 and all(os.path.isfile(p) for p in dest.values()) and not os.path.exists(staged(m, "levels.xml")), "land moves the three files into Defs/ on a copy",
            "exit %d, %d of 3 landed" % (rc, sum(os.path.isfile(p) for p in dest.values())), "exit 0, 3 of 3")
        rc, out = run(["land", "smelter", "--mod", m, "--vfef", v, "--without-pictures"])
        say(rc != 0, "land of a line already landed is refused", "exit %d" % rc, "not 0")

        m, v = fresh()
        run(["stamp", "smelter", "--mod", m, "--vfef", v])
        edit(staged(m, "levels.xml"), lambda r: [st(e, "77120099") for e in r.iter("analysisID")][:1])
        rc, out = run(["land", "smelter", "--mod", m, "--vfef", v, "--without-pictures"])
        say(rc == 1 and os.path.isfile(staged(m, "levels.xml")), "land refuses a line whose check fails", "exit %d" % rc, "exit 1, files kept")

        # ---- the real staged lines are not touched by any of this
        real_bad = [p for p in (os.path.join(MOD, "Defs", "MachineLines", "MachineLines_WreckedMachines_smelter.xml"),) if os.path.exists(p)]
        say(not real_bad, "no landing happened in the real Defs/", "%d stray files" % len(real_bad), "0")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = all(RESULTS) and len(RESULTS) >= 20
    print("%d checks, %d failed" % (len(RESULTS), sum(1 for r in RESULTS if not r)))
    print("selftest_onboard: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
