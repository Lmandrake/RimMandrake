#!/usr/bin/env python3
"""Shade gear lessons (SHADE_LESSONS_BUILD_WATCH_THE_HERD_CROSS), offline.

Design: design/RimMandrake/shadecraft_lessons_design_2026-10-31.md. Code: EnvironmentalHazards
Source/RM_ShadeLessons.cs, RM_FoundTechStudy.cs; CreatureBehaviors Source/RM_ShadeHop.cs. Defs:
EnvironmentalHazards Defs/ResearchProjectDefs/RM_ShadeLessons_Research.xml, Patches/RM_ShadeLessons_Sources.xml.

What is REAL here:
  - the two pure functions RM_ShadeLessonMath.RaiseAmount and CrossingPoints are lifted from the C# source and
    transliterated to Python (a tiny, strict translator: it refuses any statement shape it does not know), then
    driven through the research model the shipped researchMods describe. Vanilla's side of that model is
    transcribed from decompiled 1.6 (ResearchManager.AddProgress clamps to Cost; FinishProject and game load run
    ReapplyAllMods, which calls every FINISHED project's mods' Apply). A planted bad RaiseAmount (adding instead
    of raising) must FAIL the idempotency case, so the case can see.
  - the patch is applied (PatchOperationConditional / PatchOperationAdd, the two ops it uses) over the combined
    Defs of every mod composed into mandrake.rm.biomes (Biomes.compose.json), and every source row of the
    design's own biome table is then read back from the patched tree.
  - the settings, the gate and the crossing watcher are read as source structure (no game here).
NOT covered: anything needing a live map (a colonist studying, a dash landing). That is the item's quicktest
criterion, in infrastructure/state/live_proofs/SHADE_LESSONS_BUILD_WATCH_THE_HERD_CROSS.txt.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RM = os.path.join(REPO, "src", "RimMandrake")
EH = os.path.join(RM, "EnvironmentalHazards")
CB = os.path.join(RM, "CreatureBehaviors")
DESIGN = os.path.join(REPO, "design", "RimMandrake", "shadecraft_lessons_design_2026-10-31.md")
RESEARCH_XML = os.path.join(EH, "Defs", "ResearchProjectDefs", "RM_ShadeLessons_Research.xml")
GEAR_XML = os.path.join(EH, "Defs", "ThingDefs_Buildings", "RM_ShadeGear.xml")
PATCH_XML = os.path.join(EH, "Patches", "RM_ShadeLessons_Sources.xml")
LESSONS_CS = os.path.join(EH, "Source", "RM_ShadeLessons.cs")
FOUNDTECH_CS = os.path.join(EH, "Source", "RM_FoundTechStudy.cs")
SETTINGS_CS = os.path.join(EH, "Source", "RM_EnvironmentalHazardsMod.cs")
CSPROJ = os.path.join(EH, "Source", "RM_EnvironmentalHazards.csproj")
SHADEHOP_CS = os.path.join(CB, "Source", "RM_ShadeHop.cs")
COMPOSE = os.path.join(RM, "Biomes.compose.json")

GATE = "EnvironmentalHazards.ShadeLessons"
GEAR = {"RM_Research_Parasol": "RM_Parasol", "RM_Research_ShadeTent": "RM_ShadeTent"}
IDEAS = ("RM_ShadeIdea_DewOff", "RM_ShadeIdea_PortableShade", "RM_ShadeIdea_DeepCloth")
IDEA_WORDS = {"dew off": "RM_ShadeIdea_DewOff", "deep cloth": "RM_ShadeIdea_DeepCloth"}
FT_CLASS = "RimMandrake.EnvironmentalHazards.CompProperties_FoundTechStudy"
RAISE_CLASS = "RimMandrake.EnvironmentalHazards.RM_ResearchMod_RaiseProject"
EXT_CLASS = "RimMandrake.EnvironmentalHazards.RM_FoundTechProjectExtension"

FAILS: list[str] = []


def check(ok, what, detail=""):
    print(("PASS " if ok else "FAIL ") + what + ("" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(what)
    return ok


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


# ── C# → Python, for two pure functions only ─────────────────────────────

def cs_method_body(src, name):
    m = re.search(r"public static float %s\(([^)]*)\)\s*\{" % re.escape(name), src)
    if not m:
        raise ValueError("method %s not found" % name)
    i, depth = m.end(), 1
    while depth:
        c = src[i]
        depth += c == "{"
        depth -= c == "}"
        i += 1
    params = [p.split()[-1] for p in m.group(1).split(",")]
    return params, src[m.end():i - 1]


def cs_expr(e):
    e = re.sub(r"(\d+(?:\.\d+)?)f\b", r"\1", e)
    e = e.replace("Math.Max", "max").replace("Math.Min", "min").replace("||", " or ").replace("&&", " and ")
    m = re.fullmatch(r"\s*(.+?)\s*\?\s*(.+?)\s*:\s*(.+?)\s*", e)
    if m:
        e = "(%s if %s else %s)" % (m.group(2), m.group(1), m.group(3))
    if re.search(r"[{};?]|\bnew\b|\bfloat\b", e):
        raise ValueError("untranslatable expression: %r" % e)
    return e


def cs_to_py(params, body, name):
    """Translate `if (c) { return x; }`, `float v = x;` and `return x;` statements; refuse anything else."""
    out = ["def %s(%s):" % (name, ", ".join(params))]
    toks = re.findall(r"if\s*\((.*?)\)\s*\{\s*return\s+(.*?);\s*\}|float\s+(\w+)\s*=\s*(.*?);|return\s+(.*?);|(\S)",
                      body, re.S)
    for cond, ret, var, val, plain, junk in toks:
        if junk:
            raise ValueError("untranslatable statement near %r in %s" % (junk, name))
        if cond:
            out.append("    if %s: return %s" % (cs_expr(cond), cs_expr(ret)))
        elif var:
            out.append("    %s = %s" % (var, cs_expr(val)))
        else:
            out.append("    return %s" % cs_expr(plain))
    ns: dict = {}
    exec("\n".join(out), ns)  # noqa: S102 - our own source, translated by the strict rules above
    return ns[name]


# ── the research model (vanilla side transcribed from decompiled 1.6) ────

class Research:
    def __init__(self, defs, raise_amount):
        self.defs = defs            # name -> {"cost": float, "mods": [(project, requires, fraction)]}
        self.progress = {n: 0.0 for n in defs}
        self.raise_amount = raise_amount

    def finished(self, n):
        return self.progress[n] >= self.defs[n]["cost"]

    def pct(self, n):
        return self.progress[n] / self.defs[n]["cost"]

    def add_progress(self, n, amount):           # ResearchManager.AddProgress
        self.progress[n] = min(self.progress[n] + amount, self.defs[n]["cost"])
        if self.finished(n):
            self.reapply_all()

    def finish(self, n):                         # ResearchManager.FinishProject
        self.progress[n] = self.defs[n]["cost"]
        self.reapply_all()

    def reapply_all(self):                       # ReapplyAllMods: every FINISHED project's mods
        for n in list(self.defs):
            if self.finished(n):
                for project, requires, fraction in self.defs[n]["mods"]:
                    self.apply(project, requires, fraction)

    def apply(self, project, requires, fraction):  # RM_ResearchMod_RaiseProject.Apply
        if self.finished(project) or not all(self.finished(r) for r in requires):
            return
        add = self.raise_amount(self.progress[project], self.defs[project]["cost"], fraction)
        if add > 0:
            self.add_progress(project, add)


def research_defs(root, cost_factor=1.0):
    defs = {}
    for d in root.iter("ResearchProjectDef"):
        mods = []
        for li in d.findall("researchMods/li"):
            if li.get("Class") == RAISE_CLASS:
                mods.append((li.findtext("project"), [r.text for r in li.findall("requires/li")],
                             float(li.findtext("fraction") or 0.75)))
        defs[d.findtext("defName")] = {"cost": float(d.findtext("baseCost")) * cost_factor, "mods": mods}
    return defs


# ── patch application over the composed tree ────────────────────────────

def composed_tree():
    comp = json.load(open(COMPOSE, encoding="utf-8"))
    wave = comp["compose_wave"]
    members = [e for e in comp["entries"] if e["wave"] <= wave]
    root = etree.Element("Defs")
    for e in members:
        for f in sorted(glob.glob(os.path.join(RM, e["source"], "Defs", "**", "*.xml"), recursive=True)):
            try:
                r = etree.parse(f, etree.XMLParser(remove_comments=True)).getroot()
            except etree.XMLSyntaxError:
                continue
            if r.tag == "Defs":
                root.extend(list(r))
    return members, etree.ElementTree(root)


def apply_op(tree, op):
    cls = op.get("Class")
    xp = "/" + op.findtext("xpath").strip()
    if cls == "PatchOperationConditional":
        branch = op.find("match") if tree.xpath(xp) else op.find("nomatch")
        if branch is not None:
            apply_op(tree, branch)
    elif cls == "PatchOperationAdd":
        for node in tree.xpath(xp):
            for child in op.find("value"):
                node.append(etree.fromstring(etree.tostring(child)))
    else:
        raise ValueError("op class this applier does not model: %s" % cls)


def design_table():
    rows = []
    for line in read(DESIGN).splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*`(RM_\w+)`\s*\|\s*(dew off|deep cloth)\s*\|", line)
        if m:
            rows.append((m.group(1), m.group(2), IDEA_WORDS[m.group(3)]))
    return rows


def main():
    lessons = read(LESSONS_CS)
    research = etree.parse(RESEARCH_XML).getroot()
    defs = research_defs(research)

    # 1. Both gear projects reachable with no lessons at all.
    for proj, thing in GEAR.items():
        d = [x for x in research.iter("ResearchProjectDef") if x.findtext("defName") == proj]
        check(len(d) == 1, "%s is defined once" % proj)
        if not d:
            continue
        d = d[0]
        check(d.find("prerequisites") is None and d.find("hiddenPrerequisites") is None,
              "%s has no prerequisites (no lesson stands in front of it)" % proj)
        check(d.find("modExtensions") is None, "%s carries no found-tech extension (never hidden)" % proj)
    for idea in IDEAS:
        check(idea in defs, "%s is defined" % idea)
    gear = etree.parse(GEAR_XML).getroot()
    things = {t.findtext("defName"): t for t in gear.iter("ThingDef")}
    check(things["RM_Parasol"].findtext("recipeMaker/researchPrerequisite") == "RM_Research_Parasol",
          "RM_Parasol's recipe needs RM_Research_Parasol (plain research unlocks it)")
    check([li.text for li in things["RM_ShadeTent"].findall("researchPrerequisites/li")] == ["RM_Research_ShadeTent"],
          "RM_ShadeTent needs only RM_Research_ShadeTent")

    # 2. The discount, from the shipped researchMods and the C# RaiseAmount.
    raise_amount = cs_to_py(*cs_method_body(lessons, "RaiseAmount"), "RaiseAmount")
    crossing_points = cs_to_py(*cs_method_body(lessons, "CrossingPoints"), "CrossingPoints")

    def pair_case(fn, factor, label, chk=check):
        ok = True
        for piece, first, second in (("RM_Research_Parasol", "RM_ShadeIdea_DeepCloth", "RM_ShadeIdea_PortableShade"),
                                     ("RM_Research_Parasol", "RM_ShadeIdea_PortableShade", "RM_ShadeIdea_DeepCloth"),
                                     ("RM_Research_ShadeTent", "RM_ShadeIdea_DewOff", "RM_ShadeIdea_PortableShade"),
                                     ("RM_Research_ShadeTent", "RM_ShadeIdea_PortableShade", "RM_ShadeIdea_DewOff")):
            r = Research(research_defs(research, factor), fn)
            r.finish(first)
            one = r.pct(piece)
            r.finish(second)
            two = r.pct(piece)
            r.reapply_all()     # a later FinishProject elsewhere, or a game load
            r.reapply_all()
            again = r.pct(piece)
            ok &= chk(one == 0.0, "%s: %s alone leaves %s at 0%% (%s)" % (label, first, piece, one))
            ok &= chk(abs(two - 0.75) < 1e-6, "%s: %s second raises %s to 75%% (%s)" % (label, second, piece, two))
            ok &= chk(abs(again - 0.75) < 1e-6, "%s: a second Apply leaves %s at 75%% (%s)" % (label, piece, again))
        return ok

    pair_case(raise_amount, 1.0, "shipped")
    pair_case(raise_amount, 2.5, "shipped, tech-level cost factor 2.5")
    r = Research(research_defs(research), raise_amount)
    r.add_progress("RM_Research_Parasol", 350)
    r.finish("RM_ShadeIdea_DeepCloth")
    r.finish("RM_ShadeIdea_PortableShade")
    check(abs(r.pct("RM_Research_Parasol") - 350 / 400) < 1e-6, "progress past 75% is never lowered")
    r = Research(research_defs(research), raise_amount)
    r.finish("RM_ShadeIdea_DewOff")
    r.finish("RM_ShadeIdea_DeepCloth")
    check(r.pct("RM_Research_Parasol") == 0 and r.pct("RM_Research_ShadeTent") == 0,
          "dew off + deep cloth (no shared idea) discounts nothing")

    # planted break: an Apply that ADDS 75% must be caught by the idempotency case
    caught = not pair_case(lambda cur, cost, frac: frac * cost, 1.0, "planted", chk=lambda ok, *_: bool(ok))
    check(caught, "the idempotency case catches a credit that adds instead of raising")

    # Apply's own guard, as written: every `requires` finished, else return; and no gate check (off keeps the discount)
    apply_src = lessons[lessons.index("class RM_ResearchMod_RaiseProject"):lessons.index("class RM_ShadeCrossingWatch")]
    check("!requires[i].IsFinished" in apply_src and "RM_ShadeLessonMath.RaiseAmount(project.ProgressReal, project.Cost, fraction)" in apply_src,
          "RaiseProject.Apply returns unless every required idea is finished, and raises by RaiseAmount on ProgressReal/Cost")
    check("MechanicGates" not in apply_src, "the 75% credit is not gated (design §6: off, the discount still works)")

    # 3. Crossings.
    check(crossing_points(0) == 0, "an unseen crossing adds no point")
    check(crossing_points(1) == 1, "a seen crossing adds one point")
    check(crossing_points(2) == 1, "two watchers still add one point")
    watch = lessons[lessons.index("class RM_ShadeCrossingWatch"):]
    on = watch[watch.index("public static void OnCrossing"):]
    loop_end = on.index("float points = RM_ShadeLessonMath.CrossingPoints(watchers);")
    check(on.count("k.Add(") == 1 and on.index("k.Add(") > loop_end,
          "OnCrossing credits once, after counting watchers (never once per watcher)")
    can = watch[watch.index("public static bool CanWatch"):watch.index("public static void OnCrossing")]
    for need in ("p.Downed", "p.InMentalState", "p.Awake()", "RM_ShadeLessonMath.WatchRadius", "GenSight.LineOfSight("):
        check(need in can, "a watcher must pass %s" % need)
    check(re.search(r"WatchRadius\s*=\s*20f", lessons) is not None, "the watch radius is 20 cells (design §3)")
    check("animal.Faction != null" in on and "RaceProps.Animal" in on, "any wild animal counts, no herdAnimal filter")
    check("race.herdAnimal" not in on and "herdAnimal" not in on, "no herdAnimal filter")
    check("RM_ShadeHop.CrossingLanded += OnCrossing" in watch, "EnvironmentalHazards subscribes to the CreatureBehaviors event")
    hop = read(SHADEHOP_CS)
    check("public static event Action<Pawn, IntVec3> CrossingLanded;" in hop, "RM_ShadeHop raises a CrossingLanded event")
    drv = hop[hop.index("class RM_JobDriver_ShadeDash"):hop.index("class RM_DashRing")]
    check(drv.index("RM_ShadeHop.RaiseCrossingLanded(") > drv.index("yield return sprint;")
          and "pawn.Position == job.targetB.Cell" in drv,
          "the dash raises a crossing only after the sprint, and only on the landing cell")
    check(re.search(r"RimMandrake\.EnvironmentalHazards", hop) is None,
          "CreatureBehaviors never references EnvironmentalHazards (assembly direction)")

    # 4. Portable shade hides with no ThingDef carrying it.
    ps = [x for x in research.iter("ResearchProjectDef") if x.findtext("defName") == "RM_ShadeIdea_PortableShade"][0]
    ext = [li for li in ps.findall("modExtensions/li") if li.get("Class") == EXT_CLASS]
    check(len(ext) == 1 and ext[0].findtext("gateKey") == GATE and float(ext[0].findtext("knowledgeToReveal")) == 12,
          "RM_ShadeIdea_PortableShade registers itself (gate %s, 12 crossings)" % GATE)
    ft = read(FOUNDTECH_CS)
    build = ft[ft.index("private static void Build()"):ft.index("class RM_Patch_FoundTechHidden")]
    check("DefDatabase<ResearchProjectDef>.AllDefsListForReading" in build and "GetModExtension<RM_FoundTechProjectExtension>()" in build
          and "projects.Add(proj, ext.gateKey)" in build,
          "RM_FoundTechRegistry also registers projects that carry RM_FoundTechProjectExtension")
    post = ft[ft.index("public static void Postfix"):]
    check("RM_FoundTechRegistry.TryGetGate(__instance" in post and "__result = !RM_FoundTechKnowledge.IsRevealed(__instance)" in post,
          "IsHidden is true for a registered project until revealed")
    check("<Compile Include=\"RM_ShadeLessons.cs\" />" in read(CSPROJ), "the csproj compiles RM_ShadeLessons.cs")

    # 5. Every design source carries its study comp after patching, composed into mandrake.rm.biomes.
    members, tree = composed_tree()
    keys = {e["source"] for e in members}
    check("EnvironmentalHazards" in keys, "EnvironmentalHazards is composed into mandrake.rm.biomes")
    patch = etree.parse(PATCH_XML, etree.XMLParser(remove_comments=True)).getroot()
    check("PatchOperationFindMod" not in read(PATCH_XML).split("-->", 1)[1], "the sources patch uses no PatchOperationFindMod")
    rel = os.path.relpath(PATCH_XML, EH)
    clash = [e["source"] for e in members if e["source"] != "EnvironmentalHazards" and os.path.exists(os.path.join(RM, e["source"], rel))]
    check(not clash, "the patch's relative path is unique across composed entries", clash)
    for op in patch:
        apply_op(tree, op)
    rows = design_table()
    check(len(rows) >= 15, "the design's biome table parses (%d rows)" % len(rows))

    def comps_of(defname):
        t = tree.xpath('/Defs/ThingDef[defName="%s"]' % defname)
        if len(t) != 1:
            return None
        return [li for li in t[0].findall("comps/li") if li.get("Class") == FT_CLASS]

    for biome, src, idea in rows:
        cs = comps_of(src)
        check(cs is not None and len(cs) == 1 and cs[0].findtext("project") == idea and cs[0].findtext("gateKey") == GATE,
              "%s: %s carries one study comp for %s after patching" % (biome, src, idea),
              cs and [c.findtext("project") for c in cs])
    for li in tree.xpath('/Defs/ThingDef/comps/li[@Class="%s"]' % FT_CLASS):
        if li.findtext("project") == "RM_ShadeIdea_PortableShade":
            check(False, "no ThingDef carries RM_ShadeIdea_PortableShade", li.getparent().getparent().findtext("defName"))
    for li in tree.xpath('/Defs/ThingDef/comps/li[@Class="%s"]' % FT_CLASS):
        if li.findtext("project") in GEAR:
            check(False, "no study comp hides a gear project", li.findtext("project"))
    for twin_src in ("RM_GargantuanLithops", "RM_GlobularPlant", "RM_Shadefern", "RM_MangrovePalm", "RM_Aaklac"):
        cs = comps_of(twin_src)
        check(cs is not None and len(cs) == 1, "RUT_ twin source %s carries one study comp" % twin_src)
    # sanity probe: the applier really sees a def that existed only BEFORE patching without the comp
    _, fresh = composed_tree()
    pre = fresh.xpath('/Defs/ThingDef[defName="RM_Dewfringe"]/comps/li[@Class="%s"]' % FT_CLASS)
    check(not pre, "sanity probe: RM_Dewfringe has no study comp before the patch (so the patch is what added it)")

    # 6. Mod Settings toggle, and what off degrades to.
    st = read(SETTINGS_CS)
    check("public static bool shadeLessonsEnabled = true;" in st, "the setting exists, default on")
    check('Scribe_Values.Look(ref shadeLessonsEnabled, "shadeLessonsEnabled", true);' in st, "the setting is saved")
    check('"shadeLessonsEnabled" }))' in st and 'CheckboxLabeled("Shade gear is learned by study", ref shadeLessonsEnabled' in st,
          "the toggle is on the settings screen, labelled as the design says")
    check("RM_MechanicGates.Register(RM_ShadeLessons.GateKey, () => RM_EnvironmentalHazardsSettings.shadeLessonsEnabled);" in st,
          "the toggle drives the gate")
    check('public const string GateKey = "%s";' % GATE in lessons, "the gate key is %s" % GATE)
    comp_src = ft[ft.index("public class RM_CompFoundTechStudy"):ft.index("public class RM_FoundTechRecord")]
    check("SetStudyEnabled(GateOn &&" in comp_src and "gained > 0f && GateOn" in comp_src,
          "off: sources are not studiable and a study adds nothing")
    check("!RM_MechanicGates.Enabled(gateKey) || __instance.IsFinished" in post,
          "off: idea projects are ordinary visible research")
    check("!RM_MechanicGates.Enabled(RM_ShadeLessons.GateKey)" in on, "off: crossings add nothing")
    for li in patch.iter("li"):
        if li.get("Class") == FT_CLASS:
            if li.findtext("gateKey") != GATE:
                check(False, "every source comp answers to the gate", li.findtext("project"))

    # 7. The live proof's own offline half (probe compiled, judge sees each break).
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(EH, "prove_shade_lessons.py"), "--offline"],
                       capture_output=True, text=True, timeout=120)
    check(r.returncode == 0 and "RESULT PASS" in r.stdout, "prove_shade_lessons.py --offline passes", r.stdout[-300:])

    print("RESULT %s (%d fail)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
