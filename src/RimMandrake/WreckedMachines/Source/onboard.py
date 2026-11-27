#!/usr/bin/env python3
"""onboard.py: the onboarding tool of Wrecked Machines (DESIGN.md "The onboarding table" and "The level defs"). Dev tooling, not shipped.

A machine line is one hand-written row (the table's RM_MachineLineDef) plus the donor's ThingDef from the factory mod. The tool stamps
the rest of the line from those two: the three level ThingDefs and the two ResearchProjectDefs. Until the machine's Wrecked and Kludged
pictures have passed the art judge, the row and its stamped defs wait in Source/onboarding_staged/<key>/, a folder the game never loads.

    python3 Source/onboard.py stamp <key>        row.xml + the donor  ->  levels.xml, projects.xml beside the row
    python3 Source/onboard.py check <key> | --all a temporary copy of the mod with the staged files placed as if landed; runs the
                                                 acceptance test's rows (selftest_wm_onboarding_complete.rows_for) and our own
    python3 Source/onboard.py land <key>         moves the three staged files into Defs/ (only when check passes)

Options: --vfef <dir> (the factory mod; default the workshop folder or env RM_VFEF_DIR), --mod <dir> (the mod folder; default this one).

row.xml is a <Defs> file holding one RimMandrake.WreckedMachines.RM_MachineLineDef and a comment `<!-- line number N -->`. The line number
makes the study ids: 77120000 + 10 x N + step (1 the Wrecked study, 2 the Kludged study; lines 1 smelter, 2 power cell, 3 emanator are
taken). A MayRequire attribute on the row is copied to every def of the line.

What the stamp does to the donor (every number below is read from the shipped smelter line and the donor smelter it was made from:
VFEFactory_AutomatedSmelter 260 steel, 300 W, heat 14, breakdown 3, MaxHitPoints 450, Beauty -10, WorkToBuild 5000):
  Wrecked      inert: no donor comp, no ground need, no interaction cell, no hopper link; a carried form (minifiedDef MinifiedThing
               and the donor's thingCategories); the donor's Mass and MaxHitPoints; Beauty x3 (-30); Flammability x0.5; WorkToBuild
               16% of the donor's (800), nearest 100; salvage costList = Steel 30/260 of the donor's, nearest 5; the study comp and the
               machine comp; draw-in buildingTags RM_RuinDrawsConduit (donor has a power comp) and RM_RuinDrawsPipes (donor has a
               PipeSystem.CompProperties_Resource).
  Kludged      the donor's def; cost and WorkToBuild from the row; Beauty x2 (-20); MaxHitPoints x2/3 (300), nearest 10; breakdown
               factor x2 of the donor's (default 1: the stat's own default); VEF_BuildingMaxOverclockFactor 1; power x1.2 (360 W),
               heat x1.4 (14 -> 20); canOverclock false and the overclock gizmo fields gone; the processes of the row; the study comp;
               the machine comp; a carried form only if the row's kludgedMovable.
  Refurbished  the donor's def; cost and WorkToBuild from the row; Beauty x1.5; MaxHitPoints x8/9 (400); breakdown x1.5 (4.5);
               power x1.1 (330 W); heat x1.15 (14 -> 16); canOverclock false; every donor process; the machine comp; a carried form only
               if refurbishedMovable; it draws the donor's own picture.
  A donor with no processor comp (the autofarmer) is stamped without process, breakdown or overclock handling. A donor whose XML
  lists no processes (the fish farm: the factory mod fills them in code) keeps no <processes> element; a comment says the C# fills it.

Exit: 0 done / passes; 1 refused (a fault in the row, the stamp or the check); 2 COULD NOT LOOK (the donor or a file cannot be read:
never a guess).
"""
import argparse
import copy
import glob
import importlib.util
import os
import re
import shutil
import sys
import tempfile
from fractions import Fraction

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_DEFAULT = os.path.dirname(HERE)
STEAM = "/mnt/c/Program Files (x86)/Steam/steamapps"
VFEF_DEFAULT = os.environ.get("RM_VFEF_DIR") or STEAM + "/workshop/content/294100/3686924415"
LINE_TAG = "RimMandrake.WreckedMachines.RM_MachineLineDef"
LEVEL_EXT = "RimMandrake.WreckedMachines.WreckedMachineGrade"
MACHINE_COMP = "RimMandrake.WreckedMachines.CompProperties_WreckedMachine"
STUDY_COMP = "CompProperties_CompAnalyzableUnlockResearch"
STUDY_CLASS = "RimMandrake.WreckedMachines.CompMachineStudy"
PROCESSOR = "PipeSystem.CompProperties_AdvancedResourceProcessor"
PIPE_RESOURCE = "PipeSystem.CompProperties_Resource"
POWER = "CompProperties_Power"
HEAT = "CompProperties_HeatPusher"
COMPONENT = "RM_WM_AncientComponent"
DONOR_PREFIX = "VFEFactory_"
ID_BASE = 77120000
GATING = ("three_level_defs", "wreck_is_carried", "two_projects_studied", "table_row_whole")
OWN_ROWS = ("staged_files", "row_whole", "texts", "donor_fidelity", "ids")
PICTURE_ROWS = ("pictures_of_its_own", "pictures_judged")
# Words no text of a line may hold (brief of 2026-11-27): plus the base game's and a galaxy-far-away vocabulary.
BANNED = re.compile(r"\b(grades?|tiers?|repaired|ships?|crash(?:ed|es)?|factions?|clans?|gods?|jedi|sith|vader|yoda|skywalker|"
                    r"tatooine|death star|lightsaber|stormtroopers?|wookiee|millennium falcon|obi-wan|r2-d2)\b|build over", re.I)
TEXT_TAGS = ("label", "description", "jobString", "inspectString", "completedLetterLabel", "completedLetter", "li")


class CouldNotLook(Exception):
    pass


class Refused(Exception):
    pass


# ------------------------------------------------------------------ small helpers

def half_up(x):
    """Round half up (not Python's banker's rounding); x may be a Fraction, int or float."""
    return int((Fraction(x) + Fraction(1, 2)).__floor__())


def round_to(x, step):
    return half_up(Fraction(x) / step) * step


def fmt(x):
    x = Fraction(x).limit_denominator(1000)
    return str(int(x)) if x.denominator == 1 else ("%g" % float(x))


def parse_file(path, soft=False):
    """Parse an XML file; blank text dropped, comments kept. soft: a bad file is a Refused, not a CouldNotLook."""
    try:
        return etree.parse(path, etree.XMLParser(remove_blank_text=True)).getroot()
    except (OSError, etree.XMLSyntaxError) as e:
        raise (Refused if soft else CouldNotLook)("%s: %s" % (path, e))


def text(el, path):
    return (el.findtext(path) or "").strip() if el is not None else ""


def mk(tag, txt=None, **attrs):
    e = etree.Element(tag, **attrs)
    if txt is not None:
        e.text = txt
    return e


def sub(parent, tag, txt=None):
    e = mk(tag, txt)
    parent.append(e)
    return e


def set_child(parent, tag, txt, after=None):
    """Set the text of the first child `tag`, or add it (after the child named `after`, else at the end)."""
    e = parent.find(tag)
    if e is None:
        e = mk(tag)
        a = parent.find(after) if after else None
        if a is not None:
            a.addnext(e)
        else:
            parent.append(e)
    e.text = txt
    return e


def drop(parent, *tags):
    for t in tags:
        for e in parent.findall(t):
            parent.remove(e)


def comp_of(d, cls):
    for li in d.findall("comps/li"):
        if li.get("Class") == cls:
            return li
    return None


def donor_processes(d):
    p = comp_of(d, PROCESSOR)
    return [li.text.strip() for li in p.findall("processes/li") if li.text] if p is not None else []


def article(label):
    return ("an " if label[:1].lower() in "aeiou" else "a ") + label


def donor_name(original):
    return original[len(DONOR_PREFIX):] if original.startswith(DONOR_PREFIX) else original


def cap(s):
    return s[:1].upper() + s[1:]


def join_and(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


# ------------------------------------------------------------------ paths

def staged_dir(mod, key):
    return os.path.join(mod, "Source", "onboarding_staged", key)


def landing(mod, key, original):
    d = donor_name(original)
    return {"row.xml": os.path.join(mod, "Defs", "MachineLines", "MachineLines_WreckedMachines_%s.xml" % key),
            "levels.xml": os.path.join(mod, "Defs", "ThingDefs_Buildings", "Buildings_WreckedMachines_%s.xml" % d),
            "projects.xml": os.path.join(mod, "Defs", "ResearchProjectDefs", "ResearchProjects_WreckedMachines_%s.xml" % d)}


def staged_keys(mod):
    root = os.path.join(mod, "Source", "onboarding_staged")
    if not os.path.isdir(root):
        return []
    return sorted(k for k in os.listdir(root) if not k.startswith(("_", ".")) and os.path.isfile(os.path.join(root, k, "row.xml")))


# ------------------------------------------------------------------ the donor

_donor_cache = {}


def vfef_root(vfef):
    root = os.path.join(vfef, "1.6")
    if not os.path.isdir(os.path.join(root, "Defs")):
        raise CouldNotLook("the factory mod's 1.6/Defs is not at %s (pass --vfef or set RM_VFEF_DIR)" % root)
    return root


def find_donor(vfef, name):
    """-> (ThingDef element, path of its file relative to the factory mod). A donor not found is CouldNotLook, never a guess."""
    root = vfef_root(vfef)
    if (root, name) in _donor_cache:
        return _donor_cache[(root, name)]
    needle = "<defName>%s</defName>" % name
    files = sorted(glob.glob(os.path.join(root, "Defs", "**", "*.xml"), recursive=True)
                   + glob.glob(os.path.join(root, "Mods", "*", "Defs", "**", "*.xml"), recursive=True))
    for f in files:
        try:
            if needle not in open(f, encoding="utf-8-sig").read():
                continue
        except OSError as e:
            raise CouldNotLook("%s: %s" % (f, e))
        for d in parse_file(f):
            if isinstance(d.tag, str) and d.tag == "ThingDef" and text(d, "defName") == name:
                _donor_cache[(root, name)] = (d, os.path.relpath(f, vfef))
                return _donor_cache[(root, name)]
    raise CouldNotLook("the donor ThingDef %s is not in %s (%d files read)" % (name, root, len(files)))


def process_labels(vfef):
    """{ProcessDef defName: label} over the factory mod's ProcessDefs (empty when it has none)."""
    root = vfef_root(vfef)
    out = {}
    for f in glob.glob(os.path.join(root, "Defs", "ProcessDefs", "*.xml")) + glob.glob(os.path.join(root, "Mods", "*", "Defs", "ProcessDefs", "*.xml")):
        for d in parse_file(f):
            if isinstance(d.tag, str) and d.tag.endswith("ProcessDef") and text(d, "defName"):
                out[text(d, "defName")] = text(d, "label")
    return out


# ------------------------------------------------------------------ the row

def read_row(path, soft=True):
    """-> (row element, line number or None). The row file is a <Defs> with one RM_MachineLineDef."""
    root = parse_file(path, soft=soft)
    rows = root.findall(LINE_TAG)
    if root.tag != "Defs" or len(rows) != 1:
        raise Refused("%s: want a <Defs> with exactly one %s (found %d)" % (path, LINE_TAG, len(rows)))
    m = re.search(r"<!--\s*line number\s+(\d+)\s*-->", open(path, encoding="utf-8-sig").read())
    return rows[0], int(m.group(1)) if m else None


def row_faults(row, key, number):
    """Faults of a hand-written row, read against the shape of DESIGN.md. Empty when whole."""
    f = []
    for t in ("defName", "key", "label", "original", "wrecked", "kludged", "refurbished", "firstProject", "secondProject",
              "kludgeWork", "refurbishWork", "kludgedMovable", "refurbishedMovable"):
        if not text(row, t):
            f.append("no <%s>" % t)
    if f:
        return f
    d = donor_name(text(row, "original"))
    want = {"defName": "RM_WM_Line_" + key, "key": key, "wrecked": "RM_WM_%s_Wrecked" % d, "kludged": "RM_WM_%s_Kludged" % d,
            "refurbished": "RM_WM_%s_Refurbished" % d, "firstProject": "RM_WM_%sKludging" % d, "secondProject": "RM_WM_%sRestoration" % d}
    for t, w in want.items():
        if text(row, t) != w:
            f.append("<%s> is %r, the naming rule wants %r" % (t, text(row, t), w))
    if number is None:
        f.append("no `<!-- line number N -->` comment")
    for cost, work in (("kludgeCost", "kludgeWork"), ("refurbishCost", "refurbishWork")):
        c = row.find(cost)
        if c is None or not len(c) or any(isinstance(e.tag, str) and (not (e.text or "").strip().isdigit() or int(e.text) <= 0) for e in c):
            f.append("no whole <%s> (every entry a whole number above 0)" % cost)
        if not text(row, work).isdigit() or int(text(row, work)) <= 0:
            f.append("<%s> is not a whole number above 0" % work)
    if row.find("refurbishCost/" + COMPONENT) is None:
        f.append("<refurbishCost> has no <%s>: the last repair costs an Ancient Component" % COMPONENT)
    for t in ("kludgedMovable", "refurbishedMovable"):
        if text(row, t) not in ("true", "false"):
            f.append("<%s> must be true or false" % t)
    n = text(row, "kludgedProcessCount") or "0"
    if not n.isdigit():
        f.append("<kludgedProcessCount> is not a whole number")
    return f


def study_ids(number):
    return ID_BASE + 10 * number + 1, ID_BASE + 10 * number + 2


# ------------------------------------------------------------------ texts (plain, true, generic; built from the label and the donor)

def texts_for(label, donor, row, procs_kl, donor_procs, labels):
    """The descriptions of one line. procs_kl: the Kludged level's process names (None when the C# fills them)."""
    L = label
    A = article(L)
    has_proc = comp_of(donor, PROCESSOR) is not None
    has_power = comp_of(donor, POWER) is not None
    has_heat = comp_of(donor, HEAT) is not None
    oc = has_proc and text(comp_of(donor, PROCESSOR), "canOverclock") == "true"
    hoppers = any((li.text or "").strip() == "VFEFactory_FactoryHopper" for li in donor.findall("building/relatedBuildCommands/li"))
    floor = text(donor, "terrainAffordanceNeeded") == "FactoryFloor"
    tail = ""
    if hoppers:
        tail += "Factory buildings need factory hoppers for input and output."
    if floor:
        tail += (" " if tail else "") + "Needs factory floor."
    tail = ("\\n\\n" + tail) if tail else ""
    km, rm = text(row, "kludgedMovable") == "true", text(row, "refurbishedMovable") == "true"

    def names(ps):
        return [labels.get(p, p)[:1].lower() + labels.get(p, p)[1:] for p in ps]

    # what the Kludged level can do
    if not has_proc:
        work = "It does the original's work, but poorly."
    elif procs_kl is None or not donor_procs:
        work = "It can only do part of what the original did."
    elif set(procs_kl) == set(donor_procs):
        work = ("It does the original's one job, in a crude way: %s." if len(procs_kl) == 1 else
                "It does everything the original did, in a crude way: %s.") % "; ".join(names(procs_kl))
    else:
        work = "It can only do part of what the original did: %s. The rest of the original's work is beyond it." % "; ".join(names(procs_kl))
    k_feat = (["draws more power"] if has_power else []) + (["runs hotter than it should"] if has_heat else []) \
        + (["breaks down often"] if has_proc else []) + (["cannot be overclocked"] if oc else [])
    r_feat = (["draws a little more power"] if has_power else []) + (["runs a little hotter"] if has_heat else []) \
        + (["breaks down more often"] if has_proc else []) + (["cannot be overclocked"] if oc else [])
    out = {}
    out["wrecked"] = ("What is left of %s. It has no power in it and nothing to give.\\n\\nA researcher can study it where it stands, and what "
                      "they learn opens the research to patch it back into service. It can be carried. The repair itself is ordered on "
                      "the machine, once the research is done." % A)
    out["kludged"] = ("%s dragged back into service by people who did not build it. The worst of the damage is plated over and the wiring "
                      "is spliced by hand.\\n\\n%s%s %s\\n\\nA researcher can study it further, and what they learn opens the research to "
                      "refurbish it properly. The refurbishment is ordered on the machine and needs an ancient component.%s"
                      % (cap(A), work, (" It " + join_and(k_feat) + ".") if k_feat else "",
                         "It can be carried." if km else "The splicing holds it in place, so it cannot be carried.", tail))
    out["refurbished"] = ("%s refurbished from salvage by people who learned it from the wreck. The breaches are sealed, the wiring is mostly "
                          "original again, and an ancient component holds the worst of it together.\\n\\nIt does everything the original "
                          "did.%s %s%s" % (cap(A), (" It " + join_and(r_feat) + ".") if r_feat else "",
                                           "It can be carried." if rm else "It is bolted in place and cannot be carried.", tail))
    out["w_job"], out["k_job"] = "study the wrecked " + L, "study the kludged " + L
    out["w_inspect"] = "A researcher can study how this %s was put together." % L
    out["k_inspect"] = "A researcher can study how to refurbish this %s." % L
    out["w_letter_label"] = "Wrecked %s studied: {RESEARCH} unlocked" % L
    out["k_letter_label"] = "Kludged %s studied: {RESEARCH} unlocked" % L
    out["w_letter"] = ("By studying the wrecked %s, {PAWN_labelShort} has worked out how it can be patched back into service.\\n\\nThe research "
                       "project {RESEARCH} can now be done at a research bench. Once it is done, order the repair on the %s itself." % (L, L))
    out["k_letter"] = ("By studying the kludged %s, {PAWN_labelShort} has found which of its splices can stay and which must be redone to "
                       "bring the machine close to what it was.\\n\\nThe research project {RESEARCH} can now be done at a research bench. "
                       "Once it is done, order the refurbishment on the %s itself. It needs an ancient component." % (L, L))
    out["p1"] = ("Work out how to patch a wrecked %s back into crude service. Needs a wrecked %s that a researcher has studied.\\n\\nOnce "
                 "this is done, order the kludge on the wrecked %s where it stands." % (L, L, L))
    out["p2"] = ("Learn to bring a kludged %s close to what it was. This is not the original engineering, which its makers already solved. "
                 "It is the colony's own hard-won knowledge of how to bring a dead one back. Needs a kludged %s that a researcher has "
                 "studied.\\n\\nOnce this is done, order the refurbishment on the kludged %s where it stands. It needs an ancient "
                 "component." % (L, L, L))
    return out


# ------------------------------------------------------------------ the three level defs

def study_comp(step, number, tx):
    """The base game's analysis comp with this mod's comp class for the toggle (DESIGN.md "The level defs")."""
    aid = study_ids(number)[step - 1]
    k = step == 2
    li = mk("li", Class=STUDY_COMP)
    for t, v in (("compClass", STUDY_CLASS), ("analysisID", str(aid)), ("requiresMechanitor", "false"), ("canStudyInPlace", "true"),
                 ("analysisRequiredRange", "3~3"), ("analysisDurationHours", "4"), ("cooldownTicks", "20000"), ("destroyedOnAnalyzed", "false"),
                 ("activateTexPath", "UI/Icons/Study"), ("jobString", tx["k_job" if k else "w_job"]),
                 ("inspectString", tx["k_inspect" if k else "w_inspect"]),
                 ("completedLetterLabel", tx["k_letter_label" if k else "w_letter_label"]),
                 ("completedLetter", tx["k_letter" if k else "w_letter"]), ("completedLetterDef", "PositiveEvent")):
        sub(li, t, v)
    tp = sub(li, "targetingParameters")
    for t, v in (("canTargetBuildings", "false"), ("canTargetAnimals", "false"), ("canTargetMechs", "false"), ("onlyTargetControlledPawns", "true")):
        sub(tp, t, v)
    return li


def machine_comp():
    return mk("li", Class=MACHINE_COMP)


def add_extension(d, level, key):
    ext = d.find("modExtensions")
    if ext is None:
        ext = sub(d, "modExtensions")
    li = sub(ext, "li")
    li.set("Class", LEVEL_EXT)
    sub(li, "grade", level)
    sub(li, "line", key)


def tex_path(donor, level):
    """WreckedMachines/Factories/<folder>/<Level>/<file>, folder and file from the donor's own texPath (its last two parts)."""
    parts = text(donor, "graphicData/texPath").split("/")
    if len(parts) < 2:
        raise Refused("the donor's texPath %r has no folder and file" % text(donor, "graphicData/texPath"))
    return "WreckedMachines/Factories/%s/%s/%s" % (parts[-2], level, parts[-1])


def stat(d, name):
    v = text(d, "statBases/" + name)
    return Fraction(v) if v else None


def set_stat(d, name, val):
    sb = d.find("statBases")
    if sb is None:
        sb = mk("statBases")
        d.append(sb)
    set_child(sb, name, fmt(val))


def head(donor, row, level, key, desc):
    """The def's opening: attributes, defName, label, description."""
    d = mk("ThingDef", ParentName=donor.get("ParentName") or "BuildingBase")
    if row.get("MayRequire"):
        d.set("MayRequire", row.get("MayRequire"))
    sub(d, "defName", text(row, {"Wrecked": "wrecked", "Kludged": "kludged", "Refurbished": "refurbished"}[level]))
    sub(d, "label", "%s %s" % (level.lower(), text(row, "label")))
    sub(d, "description", desc)
    return d


def build_wrecked(donor, row, key, number, tx):
    d = head(donor, row, "Wrecked", key, tx["wrecked"])
    sub(d, "drawerType", "MapMeshOnly")
    gd = copy.deepcopy(donor.find("graphicData"))
    gd.find("texPath").text = tex_path(donor, "Wrecked")
    d.append(gd)
    cats = donor.find("thingCategories")
    if cats is None or cats.find("li") is None:
        raise Refused("the donor has no thingCategories: a wreck's carried form needs one (rule R_lift)")
    d.append(copy.deepcopy(cats))
    steel = donor.find("costList/Steel")
    if steel is not None and steel.text:
        cl = sub(d, "costList")
        # the smelter's salvage: 30 of the donor's 260 steel, nearest 5, at least 5
        sub(cl, "Steel", str(max(5, round_to(Fraction(int(steel.text)) * 30 / 260, 5))))
    for t in ("altitudeLayer", "rotatable", "neverMultiSelect", "uiIconScale", "fillPercent", "useHitPoints"):
        if donor.find(t) is not None:
            d.append(copy.deepcopy(donor.find(t)))
    sub(d, "leaveResourcesWhenKilled", "false")
    sb = sub(d, "statBases")
    mass = stat(donor, "Mass")
    if mass is None:
        raise Refused("the donor has no Mass: the wreck keeps the donor's Mass")
    sub(sb, "Mass", fmt(mass))
    beauty = stat(donor, "Beauty") or Fraction(-10)
    sub(sb, "Beauty", fmt(beauty * 3 if beauty < 0 else Fraction(-30)))
    sub(sb, "WorkToBuild", str(round_to(Fraction(text(donor, "statBases/WorkToBuild") or "5000") * 16 / 100, 100)))
    sub(sb, "MaxHitPoints", fmt(stat(donor, "MaxHitPoints") or Fraction(300)))
    sub(sb, "Flammability", fmt((stat(donor, "Flammability") if stat(donor, "Flammability") is not None else Fraction(1)) / 2))
    sub(d, "tickerType", "Never")
    for t in ("size", "passability", "pathCost", "disableImpassableShotOverConfigError"):
        if donor.find(t) is not None:
            d.append(copy.deepcopy(donor.find(t)))
    sub(d, "minifiedDef", "MinifiedThing")
    b = sub(d, "building")
    sub(b, "deconstructible", "true")
    sub(b, "isInert", "true")
    tags = sub(b, "buildingTags")
    for li in donor.findall("building/buildingTags/li"):
        sub(tags, "li", li.text)
    if comp_of(donor, POWER) is not None:
        sub(tags, "li", "RM_RuinDrawsConduit").addnext(etree.Comment(" draw only: it joins no net "))
    if comp_of(donor, PIPE_RESOURCE) is not None:
        sub(tags, "li", "RM_RuinDrawsPipes").addnext(etree.Comment(" draw only: it joins no pipe net "))
    comps = sub(d, "comps")
    comps.append(study_comp(1, number, tx))
    comps.append(machine_comp())
    add_extension(d, "Wrecked", key)
    return d


def strip_build_fields(d):
    drop(d, "designationCategory", "researchPrerequisites", "constructionSkillPrerequisite", "replaceTags", "minifiedDef", "thingCategories")
    pw = d.find("placeWorkers")
    if pw is not None:
        for li in list(pw):
            if "BuildOver" in (li.text or ""):
                pw.remove(li)
        if not len(pw):
            d.remove(pw)


def kludge_processes(row, donor_procs, has_proc):
    """-> (list of process names, or None when the C# fills them). Refuses a name the donor's XML list does not have."""
    if not has_proc:
        return []
    named = [li.text.strip() for li in row.findall("kludgedProcesses/li") if li.text]
    count = int(text(row, "kludgedProcessCount") or "0")
    if named:
        miss = [n for n in named if n not in donor_procs]
        if miss:
            raise Refused("kludgedProcesses names %s, which the donor's own process list does not have (%s)" % (", ".join(miss), ", ".join(donor_procs) or "none in its XML"))
        return named
    if count > 0:
        return donor_procs[:count] if donor_procs else None
    raise Refused("the donor has a processor and the row names no kludgedProcesses and no kludgedProcessCount above 0")


def derive(donor, row, level, key, number, tx, procs_kl):
    """The Kludged or the Refurbished def: the donor's own, changed as the smelter's two defs differ from the donor's."""
    kl = level == "Kludged"
    d = copy.deepcopy(donor)
    d.attrib.clear()
    d.set("ParentName", donor.get("ParentName") or "BuildingBase")
    if row.get("MayRequire"):
        d.set("MayRequire", row.get("MayRequire"))
    strip_build_fields(d)
    set_child(d, "defName", text(row, level.lower()))
    set_child(d, "label", "%s %s" % (level.lower(), text(row, "label")), after="defName")
    set_child(d, "description", tx[level.lower()], after="label")
    gd = d.find("graphicData")
    if kl:
        gd.find("texPath").text = tex_path(donor, "Kludged")
    cost = row.find("kludgeCost" if kl else "refurbishCost")
    drop(d, "costList")
    cl = mk("costList")
    for e in cost:
        if isinstance(e.tag, str):
            sub(cl, e.tag, e.text.strip())
    (d.find("graphicData")).addnext(cl)
    if (text(row, "kludgedMovable") if kl else text(row, "refurbishedMovable")) == "true":
        cats = donor.find("thingCategories")
        if cats is not None:
            cl.addprevious(copy.deepcopy(cats))
        d.append(mk("minifiedDef", "MinifiedThing"))
    drop(d, "leaveResourcesWhenKilled")
    uh = d.find("useHitPoints")
    leave = mk("leaveResourcesWhenKilled", "false")
    (uh.addnext(leave) if uh is not None else d.find("statBases").addprevious(leave))
    work = text(row, "kludgeWork" if kl else "refurbishWork")
    set_stat(d, "WorkToBuild", work)
    has_proc = comp_of(donor, PROCESSOR) is not None
    beauty = stat(donor, "Beauty") or Fraction(-10)
    set_stat(d, "Beauty", beauty * (2 if kl else Fraction(3, 2)) if beauty < 0 else (-20 if kl else -15))
    mhp = stat(donor, "MaxHitPoints")
    if mhp is not None:
        set_stat(d, "MaxHitPoints", round_to(mhp * (Fraction(2, 3) if kl else Fraction(8, 9)), 10))
    if has_proc:
        base = stat(donor, "VEF_BuildingBreakdownFactor") or Fraction(1)
        set_stat(d, "VEF_BuildingBreakdownFactor", base * (2 if kl else Fraction(3, 2)))
        set_stat(d, "VEF_BuildingMaxOverclockFactor", 1)
    if kl:
        b = d.find("building")
        if b is None:
            b = sub(d, "building")
        b.insert(0, mk("deconstructible", "true"))
    comps = d.find("comps")
    pw = comp_of(d, POWER)
    if pw is not None and pw.find("basePowerConsumption") is not None:
        w = Fraction(pw.findtext("basePowerConsumption"))
        pw.find("basePowerConsumption").text = str(half_up(w * (Fraction(6, 5) if kl else Fraction(11, 10))))
    ht = comp_of(d, HEAT)
    if ht is not None and ht.find("heatPerSecond") is not None:
        h = Fraction(ht.findtext("heatPerSecond"))
        ht.find("heatPerSecond").text = str(half_up(h * (Fraction(7, 5) if kl else Fraction(23, 20))))
    pr = comp_of(d, PROCESSOR)
    if pr is not None:
        drop(pr, "overclockGizmo", "overclockLabel", "overclockWindowLabel", "overclockDesc")
        set_child(pr, "canOverclock", "false")
        if kl:
            old = pr.find("processes")
            want = procs_kl
            if want is None or (not want and old is None):
                if old is not None:
                    old.addprevious(etree.Comment(" The donor's XML lists no processes; the C# fills the Kludged list at startup (the row's kludgedProcessCount). "))
                    pr.remove(old)
                else:
                    pr.append(etree.Comment(" The donor's XML lists no processes; the C# fills the Kludged list at startup (the row's kludgedProcessCount). "))
            else:
                lst = mk("processes")
                for p in want:
                    sub(lst, "li", p)
                if old is not None:
                    old.addprevious(etree.Comment(" Part of the donor's list: the row's kludgedProcesses. "))
                    pr.replace(old, lst)
                else:
                    pr.append(lst)
        elif pr.find("processes") is None:
            pr.append(etree.Comment(" The donor's XML lists no processes; the C# fills the list at startup from the donor as loaded. "))
    else:
        d.find("statBases").addprevious(etree.Comment(" The donor has no processor comp: the Kludged level's slower work is set by C#. ")) if kl else None
    if kl:
        comps.append(study_comp(2, number, tx))
    comps.append(machine_comp())
    add_extension(d, level, key)
    return d


# ------------------------------------------------------------------ the two projects

def build_projects(donor, row, number, tx):
    steel = donor.find("costList/Steel")
    if steel is None or not steel.text:
        raise Refused("the donor has no Steel in its costList: the project cost is read from it (2000 x steel / 260)")
    second = round_to(Fraction(int(steel.text)) * 2000 / 260, 100)
    first = Fraction(second, 2)
    L = text(row, "label")
    out = []
    for i, (nm, lab, desc, cost, req, pre, x) in enumerate((
            (text(row, "firstProject"), "%s kludging" % L, tx["p1"], first, text(row, "wrecked"), None, 0),
            (text(row, "secondProject"), "%s refurbishment" % L, tx["p2"], second, text(row, "kludged"), text(row, "firstProject"), 1))):
        p = mk("ResearchProjectDef")
        if row.get("MayRequire"):
            p.set("MayRequire", row.get("MayRequire"))
        sub(p, "defName", nm)
        sub(p, "label", lab)
        sub(p, "description", desc)
        sub(p, "baseCost", fmt(cost))
        sub(p, "techLevel", "Industrial")
        sub(p, "tab", "RM_WM_Restoration")
        if pre:
            sub(sub(p, "prerequisites"), "li", pre)
        sub(sub(p, "requiredAnalyzed"), "li", req)
        sub(p, "researchViewX", str(x))
        sub(p, "researchViewY", str(number))
        out.append(p)
    return out


# ------------------------------------------------------------------ stamp

def header(title, donor_note):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!--\n  %s\n  Stamped by Source/onboard.py from the row beside it and the donor def; do not edit by hand: change the row, or the tool, and stamp again.\n'
            '  %s\n-->\n' % (title, donor_note))


def dump(children, title, donor_note, sep_comments=None):
    root = etree.Element("Defs")
    for i, c in enumerate(children):
        if sep_comments and sep_comments[i]:
            root.append(etree.Comment(sep_comments[i]))
        root.append(c)
    etree.indent(root, space="  ")
    s = etree.tostring(root, encoding="unicode")
    return header(title, donor_note) + s + "\n"


def stamp(mod, key, vfef):
    d = staged_dir(mod, key)
    rowp = os.path.join(d, "row.xml")
    if not os.path.isfile(rowp):
        raise Refused("no staged row at %s" % rowp)
    row, number = read_row(rowp)
    faults = row_faults(row, key, number)
    if faults:
        raise Refused("row of %s refused: %s" % (key, "; ".join(faults)))
    original = text(row, "original")
    donor, rel = find_donor(vfef, original)
    if text(donor, "label") != text(row, "label"):
        raise Refused("the row's label %r is not the donor's own label %r" % (text(row, "label"), text(donor, "label")))
    labels = process_labels(vfef)
    dprocs = donor_processes(donor)
    has_proc = comp_of(donor, PROCESSOR) is not None
    procs_kl = kludge_processes(row, dprocs, has_proc)
    tx = texts_for(text(row, "label"), donor, row, procs_kl, dprocs, labels)
    wrecked = build_wrecked(donor, row, key, number, tx)
    kludged = derive(donor, row, "Kludged", key, number, tx, procs_kl)
    refurb = derive(donor, row, "Refurbished", key, number, tx, None)
    projects = build_projects(donor, row, number, tx)
    for el in (wrecked, kludged, refurb):
        bad = banned_in(el)
        if bad:
            raise Refused("a stamped text holds %r: %s" % (bad[0][1], bad[0][0]))
    note = "DONOR: %s, ThingDef %s (line %s of that file), factory mod folder as read at stamp time." % (rel, original, donor.sourceline)
    title = "WreckedMachines - the %s line (key %s, line number %d): three level defs. The Original is the factory mod's own %s." % (text(row, "label"), key, number, original)
    levels = dump([wrecked, kludged, refurb], title, note,
                  ["WRECKED. Dead. Occupies its tiles and nothing else. Can be carried.",
                   "KLUDGED. Runs, badly, on part of the original's work.",
                   "REFURBISHED. All the original's work; no overclock; a little less reliable. Draws the donor's own picture."])
    proj = dump(projects, "WreckedMachines - the %s line: its two research projects on the tab RM_WM_Restoration." % text(row, "label"), note, [None, None])
    open(os.path.join(d, "levels.xml"), "w", encoding="utf-8").write(levels)
    open(os.path.join(d, "projects.xml"), "w", encoding="utf-8").write(proj)
    return number, procs_kl


def banned_in(el):
    """[(text, banned word)] over the texts of one def (label, description, study strings, letters, rules)."""
    out = []
    for e in el.iter():
        if not isinstance(e.tag, str):
            continue
        if e.tag in TEXT_TAGS and e.text and e.text.strip():
            m = BANNED.search(e.text)
            if m and not (e.tag == "li" and e.getparent().tag in ("buildingTags", "processes", "thingCategories", "requiredAnalyzed", "prerequisites")):
                out.append((e.text.strip()[:60], m.group(0)))
    return out


# ------------------------------------------------------------------ check

def load_rows_for(real_mod):
    p = os.path.join(real_mod, "selftest_wm_onboarding_complete.py")
    if not os.path.isfile(p):
        p = os.path.join(MOD_DEFAULT, "selftest_wm_onboarding_complete.py")
    spec = importlib.util.spec_from_file_location("selftest_wm_onboarding_complete", p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["selftest_wm_onboarding_complete"] = m
    spec.loader.exec_module(m)
    return m


def temp_copy(mod, key, tmp_root):
    """A copy of the mod (Defs, Patches, the settings C#, Textures linked) with the staged key placed as if landed. -> (copy, placed paths)."""
    base = os.path.join(tmp_root, "src", "RimMandrake", "WreckedMachines")
    os.makedirs(os.path.join(base, "Source"))
    for sub_ in ("Defs", "Patches"):
        if os.path.isdir(os.path.join(mod, sub_)):
            shutil.copytree(os.path.join(mod, sub_), os.path.join(base, sub_))
    cs = os.path.join(mod, "Source", "WreckedMachinesMod.cs")
    if os.path.isfile(cs):
        shutil.copy(cs, os.path.join(base, "Source", "WreckedMachinesMod.cs"))
    if os.path.isdir(os.path.join(mod, "Textures")):
        os.symlink(os.path.join(mod, "Textures"), os.path.join(base, "Textures"))
    s = staged_dir(mod, key)
    row, _ = read_row(os.path.join(s, "row.xml"))
    dest = landing(base, key, text(row, "original"))
    placed = []
    for f, to in dest.items():
        if not os.path.isfile(os.path.join(s, f)):
            raise Refused("%s is not stamped: no %s" % (key, f))
        os.makedirs(os.path.dirname(to), exist_ok=True)
        if os.path.exists(to):
            raise Refused("%s already holds %s: the line is landed" % (key, os.path.relpath(to, base)))
        shutil.copy(os.path.join(s, f), to)
        placed.append(to)
    return base, placed


def own_checks(mod, key, vfef, other_ids):
    """Our own rows for one staged key: {row: [faults]}."""
    bad = {r: [] for r in OWN_ROWS}
    s = staged_dir(mod, key)
    docs = {}
    for f in ("row.xml", "levels.xml", "projects.xml"):
        p = os.path.join(s, f)
        if not os.path.isfile(p):
            bad["staged_files"].append("%s is missing (stamp %s)" % (f, key))
            continue
        try:
            docs[f] = parse_file(p, soft=True)
        except Refused as e:
            bad["staged_files"].append("does not parse: %s" % e)
    if "row.xml" not in docs:
        return bad
    row, number = read_row(os.path.join(s, "row.xml"))
    bad["row_whole"] += row_faults(row, key, number)
    if "levels.xml" not in docs or "projects.xml" not in docs:
        return bad
    for f in ("levels.xml", "projects.xml"):
        for el in docs[f]:
            if isinstance(el.tag, str):
                for t, w in banned_in(el):
                    bad["texts"].append("%s: %r in %r" % (f, w, t))
                if row.get("MayRequire") != el.get("MayRequire"):
                    bad["staged_files"].append("%s: %s has MayRequire %r, the row has %r" % (f, text(el, "defName"), el.get("MayRequire"), row.get("MayRequire")))
    # the donor, read again: what the levels may and may not hold
    donor, _ = find_donor(vfef, text(row, "original"))
    dprocs = donor_processes(donor)
    lv = {text(e, "defName"): e for e in docs["levels.xml"] if e.tag == "ThingDef"}
    w, k, r = (lv.get(text(row, t)) for t in ("wrecked", "kludged", "refurbished"))
    if None in (w, k, r) or len(lv) != 3:
        bad["donor_fidelity"].append("levels.xml does not hold exactly the row's three defs")
        return bad
    for nm, d in (("Wrecked", w), ("Kludged", k), ("Refurbished", r)):
        for t in ("designationCategory", "researchPrerequisites", "constructionSkillPrerequisite", "replaceTags"):
            if d.find(t) is not None:
                bad["donor_fidelity"].append("%s holds <%s>: nobody builds a level" % (nm, t))
        if text(d, "size") != text(donor, "size"):
            bad["donor_fidelity"].append("%s size %s is not the donor's %s" % (nm, text(d, "size"), text(donor, "size")))
    cls = [c.get("Class") or text(c, "compClass") for c in w.findall("comps/li")]
    if cls != [STUDY_COMP, MACHINE_COMP]:
        bad["donor_fidelity"].append("Wrecked comps are %s: want the study comp and the machine comp only (inert)" % cls)
    has_proc = comp_of(donor, PROCESSOR) is not None
    for nm, d in (("Kludged", k), ("Refurbished", r)):
        if (comp_of(d, PROCESSOR) is not None) != has_proc:
            bad["donor_fidelity"].append("%s and the donor disagree on a processor comp" % nm)
    if has_proc:
        kp = [li.text.strip() for li in k.findall("comps/li/processes/li") if li.text]
        rp = [li.text.strip() for li in r.findall("comps/li/processes/li") if li.text]
        miss = [p for p in kp if p not in dprocs]
        if miss:
            bad["donor_fidelity"].append("Kludged runs %s, which the donor does not have" % ", ".join(miss))
        named = [li.text.strip() for li in row.findall("kludgedProcesses/li") if li.text]
        if named and kp != named:
            bad["donor_fidelity"].append("Kludged processes %s are not the row's %s" % (kp, named))
        if not named and dprocs and kp != dprocs[:int(text(row, "kludgedProcessCount") or "0")]:
            bad["donor_fidelity"].append("Kludged processes %s are not the donor's first %s" % (kp, text(row, "kludgedProcessCount")))
        if rp != dprocs:
            bad["donor_fidelity"].append("Refurbished runs %s, not the donor's %s" % (rp, dprocs))
        for nm, d in (("Kludged", k), ("Refurbished", r)):
            if text(comp_of(d, PROCESSOR), "canOverclock") != "false":
                bad["donor_fidelity"].append("%s can be overclocked" % nm)
    if text(r, "graphicData/texPath") != text(donor, "graphicData/texPath"):
        bad["donor_fidelity"].append("Refurbished draws %s, not the donor's own %s" % (text(r, "graphicData/texPath"), text(donor, "graphicData/texPath")))
    # study ids: the formula, and no other staged line uses one
    if number is not None:
        want = {text(row, "wrecked"): study_ids(number)[0], text(row, "kludged"): study_ids(number)[1]}
        for nm, d in ((text(row, "wrecked"), w), (text(row, "kludged"), k)):
            c = comp_of(d, STUDY_COMP)
            got = text(c, "analysisID") if c is not None else ""
            if got != str(want[nm]):
                bad["ids"].append("%s analysisID is %r, the line number %d makes %d" % (nm, got, number, want[nm]))
            if got in other_ids:
                bad["ids"].append("%s analysisID %s is also used by staged line %s" % (nm, got, other_ids[got]))
    return bad


def staged_ids(mod, skip=None):
    """{analysisID: key} over every staged line's levels.xml except `skip`."""
    out = {}
    for k in staged_keys(mod):
        if k == skip:
            continue
        p = os.path.join(staged_dir(mod, k), "levels.xml")
        if os.path.isfile(p):
            try:
                for c in parse_file(p, soft=True).iter("li"):
                    if c.get("Class") == STUDY_COMP:
                        out[text(c, "analysisID")] = k
            except Refused:
                pass
    return out


def check_key(mod, key, vfef, module, donors):
    """-> ({row: [faults]} over OWN_ROWS + the acceptance rows, number of lines read)."""
    own = own_checks(mod, key, vfef, staged_ids(mod, skip=key))
    res = dict(own)
    for r in module.ROWS:
        res[r] = []
    if own["staged_files"]:
        return res, 0
    tmp = tempfile.mkdtemp(prefix="wm_onboard_")
    try:
        base, _ = temp_copy(mod, key, tmp)
        bad, n = module.rows_for(base, module.REPO if mod == MOD_DEFAULT else os.path.normpath(os.path.join(mod, "..", "..", "..")), donors)
        for r, fs in bad.items():
            res[r] = [f for f in fs if f.startswith(key + ":") or f.startswith(key + " ")]
            if r == "settings_line":
                res[r] += [f for f in fs if not f.startswith(key) and "Mod Settings" in f]
        return res, n
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def gating_faults(res):
    return {r: res[r] for r in GATING + OWN_ROWS if res.get(r)}


def cmd_check(mod, keys, vfef, quiet=False):
    module = load_rows_for(mod)
    donors = module.donor_hashes(vfef) if os.path.isdir(os.path.join(vfef, "Textures")) else set()
    allres = {}
    for key in keys:
        allres[key], n = check_key(mod, key, vfef, module, donors)
    cols = GATING
    if not quiet:
        for key, res in allres.items():
            print("== %s" % key)
            for r in OWN_ROWS + module.ROWS:
                fs = res.get(r, [])
                tag = "ok" if not fs else ("FAIL" if r in GATING + OWN_ROWS else "FAIL (expected until pictures and C# land)")
                print("   %-22s %s%s" % (r, tag, "" if not fs else ": " + fs[0] + (" (+%d more)" % (len(fs) - 1) if len(fs) > 1 else "")))
        print("%-14s %s" % ("key", " ".join("%-21s" % c for c in cols + ("own checks",))))
        for key, res in allres.items():
            print("%-14s %s" % (key, " ".join("%-21s" % ("ok" if not res[c] else "FAULT") for c in cols)
                                + " %s" % ("ok" if not any(res[c] for c in OWN_ROWS) else "FAULT")))
    n_bad = sum(1 for res in allres.values() if gating_faults(res))
    print("onboard check: %d keys read, %d with a fault in %s" % (len(allres), n_bad, ", ".join(GATING + OWN_ROWS)))
    return (1 if n_bad else 0), allres


# ------------------------------------------------------------------ land

def cmd_land(mod, key, vfef, with_pictures=True):
    rc, allres = cmd_check(mod, [key], vfef, quiet=True)
    res = allres[key]
    if rc:
        raise Refused("check %s fails: %s" % (key, "; ".join("%s: %s" % (r, f[0]) for r, f in gating_faults(res).items())))
    if with_pictures:
        pic = [res[r][0] for r in PICTURE_ROWS if res.get(r)]
        if pic:
            raise Refused("the pictures have not passed the art judge, so %s may not enter the table: %s (--without-pictures to test a landing)" % (key, pic[0]))
    row, _ = read_row(os.path.join(staged_dir(mod, key), "row.xml"))
    dest = landing(mod, key, text(row, "original"))
    for f, to in dest.items():
        if os.path.exists(to):
            raise Refused("%s already exists: nothing landed" % to)
    for f, to in dest.items():
        os.makedirs(os.path.dirname(to), exist_ok=True)
        shutil.move(os.path.join(staged_dir(mod, key), f), to)
    try:
        os.rmdir(staged_dir(mod, key))
    except OSError:
        pass
    return dest


# ------------------------------------------------------------------ main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=("stamp", "check", "land"))
    ap.add_argument("key", nargs="?", help="the line's key (omit with --all)")
    ap.add_argument("--all", action="store_true", help="check: every staged line")
    ap.add_argument("--vfef", default=VFEF_DEFAULT)
    ap.add_argument("--mod", default=MOD_DEFAULT)
    ap.add_argument("--without-pictures", action="store_true", help="land: do not require the picture rows (a test landing on a copy)")
    a = ap.parse_args(argv)
    mod = os.path.abspath(a.mod)
    if a.all and a.command != "check":
        ap.error("--all is for check only")
    if not a.all and not a.key:
        ap.error("a key is required (or --all with check)")
    try:
        if a.command == "stamp":
            number, procs = stamp(mod, a.key, a.vfef)
            print("stamped %s (line number %d): levels.xml and projects.xml in %s; Kludged processes: %s"
                  % (a.key, number, staged_dir(mod, a.key), "set by the C#" if procs is None else (", ".join(procs) or "none (no processor)")))
            return 0
        if a.command == "check":
            keys = staged_keys(mod) if a.all else [a.key]
            if not keys:
                raise Refused("no staged line to check")
            rc, _ = cmd_check(mod, keys, a.vfef)
            return rc
        dest = cmd_land(mod, a.key, a.vfef, not a.without_pictures)
        print("landed %s: %s" % (a.key, "; ".join(os.path.relpath(v, mod) for v in dest.values())))
        return 0
    except CouldNotLook as e:
        print("onboard: COULD NOT LOOK: %s" % e)
        return 2
    except Refused as e:
        print("onboard: REFUSED: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
