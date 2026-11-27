#!/usr/bin/env python3
# selftest-tier: deployed
"""T_ONBOARDING_COMPLETE (tree check C_onboarding_complete): each ancient machine has a Wrecked, a Kludged and a Refurbished def;
a carried form for its wreck; two restoration projects, each with its studied-thing requirement; pictures of its own for Wrecked
and Kludged in each facing (8 for a large machine); one row in the onboarding table; one line in Mod Settings.

    python3 src/RimMandrake/WreckedMachines/selftest_wm_onboarding_complete.py [--vfef <the factory mod's folder>]

It reads the mod's shipped files: the onboarding table (Defs/MachineLines/*.xml, one RM_MachineLineDef for each machine), the
ThingDefs and ResearchProjectDefs of Defs and Patches, the pictures under Textures, the art judge's records under
design/concepts/WreckedMachines/version/evidence/art, and Source/WreckedMachinesMod.cs. It reads the factory mod's own pictures
(--vfef, the installed workshop folder) only to see that no level borrows one.

ROWS, each read for every line of the table (a table with no line FAILS every row: it read nothing)
  three_level_defs      the row's wrecked, kludged and refurbished ThingDefs exist, each with the level extension naming its
                        level and the row's key; no level def is in the build menu (no designationCategory)
  wreck_is_carried      the Wrecked def has a carried form (minifiedDef, a thingCategory) and names no ground need (rule R_ground)
  two_projects_studied  the row's two projects exist; the first is locked by the study of the Wrecked def and the second by the
                        study of the Kludged def (requiredAnalyzed), the second follows the first; each studied def carries the
                        base game's analysis comp with an id no other def uses, studied where it stands
  pictures_of_its_own   the Wrecked and the Kludged def each draw a picture of the mod's own in each facing (4 files for a machine
                        that turns, 1 for one that does not); no file of one level is the file of the other or of the donor
  pictures_judged       an art judge that did not make them kept each of those pictures: a record in evidence/art names each
                        file with the hash it has now (plan.md: a machine enters the set only when its pictures pass the judge)
  table_row_whole       the row has a label, a cost and work for each repair, and the last repair costs an Ancient Component
  settings_line         Mod Settings draws one switch for each row of the table (the machineLines field, saved, drawn from the
                        table), and every row has a label for it

Exit 0 all PASS; 1 a FAIL; 2 COULD NOT LOOK (a file does not parse, or the factory mod is not installed where this looks), never
a verdict on the mod. The planted faults at the end show each row able to fail on a whole made table.
"""
import argparse
import copy
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
LINE_TAG = "RimMandrake.WreckedMachines.RM_MachineLineDef"
LEVEL_EXT = "RimMandrake.WreckedMachines.WreckedMachineGrade"
STUDY_COMP = "CompProperties_CompAnalyzableUnlockResearch"
COMPONENT = "RM_WM_AncientComponent"
LEVELS = (("wrecked", "Wrecked"), ("kludged", "Kludged"), ("refurbished", "Refurbished"))
FACINGS = ("_north", "_south", "_east", "_west")
ART_RECORDS = os.path.join("design", "concepts", "WreckedMachines", "version", "evidence", "art")
STEAM = "/mnt/c/Program Files (x86)/Steam/steamapps"
VFEF_DEFAULT = os.environ.get("RM_VFEF_DIR") or STEAM + "/workshop/content/294100/3686924415"
ROWS = ("three_level_defs", "wreck_is_carried", "two_projects_studied", "pictures_of_its_own", "pictures_judged",
        "table_row_whole", "settings_line")


class CouldNotLook(Exception):
    pass


def _parse(path):
    try:
        return ET.parse(path).getroot()
    except (OSError, ET.ParseError) as e:
        raise CouldNotLook("%s: %s" % (path, e))


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load(mod):
    """The mod's table, defs and projects: ({key: row element}, {defName: ThingDef}, {defName: ResearchProjectDef})."""
    lines, things, projects = {}, {}, {}
    order = []
    for sub in ("Defs", "Patches"):
        for f in sorted(glob.glob(os.path.join(mod, sub, "**", "*.xml"), recursive=True)):
            root = _parse(f)
            for d in root.iter(LINE_TAG):
                key = (d.findtext("key") or "").strip() or "(no key, %s)" % os.path.basename(f)
                lines[key] = d
                order.append(key)
            for d in root.iter("ThingDef"):
                if d.findtext("defName"):
                    things[d.findtext("defName").strip()] = d
            for d in root.iter("ResearchProjectDef"):
                if d.findtext("defName"):
                    projects[d.findtext("defName").strip()] = d
    return lines, things, projects


def _texture_files(mod, d):
    """The files a def's graphicData draws from the mod's Textures: ([paths that exist], [paths wanted and missing])."""
    tex = (d.findtext("graphicData/texPath") or "").strip()
    cls = (d.findtext("graphicData/graphicClass") or "Graphic_Single").strip()
    if not tex:
        return [], ["no graphicData/texPath"]
    base = os.path.join(mod, "Textures", *tex.split("/"))
    want = [base + f + ".png" for f in FACINGS] if cls == "Graphic_Multi" else [base + ".png"]
    return [p for p in want if os.path.isfile(p) and os.path.getsize(p) > 0], [p for p in want if not (os.path.isfile(p) and os.path.getsize(p) > 0)]


def judged(repo):
    """{repo path of a picture: its hash as judged} over every record of the art judge that kept its picture and did not make it."""
    out = {}
    for f in sorted(glob.glob(os.path.join(repo, ART_RECORDS, "*.json"))):
        try:
            rec = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise CouldNotLook("%s: %s" % (f, e))
        for r in rec if isinstance(rec, list) else [rec]:
            if not isinstance(r, dict) or r.get("verdict") != "keep" or (r.get("judge") or {}).get("made_it") is not False:
                continue
            for s in r.get("slots") or [{"slot": r.get("slot"), "sha": r.get("sha")}]:
                if s.get("slot") and s.get("sha"):
                    out[os.path.normpath(s["slot"])] = s["sha"]
    return out


def donor_hashes(vfef):
    root = os.path.join(vfef, "Textures")
    if not os.path.isdir(root):
        raise CouldNotLook("the factory mod's Textures are not at %s; pass --vfef or set RM_VFEF_DIR" % root)
    out = set()
    for f in glob.glob(os.path.join(root, "**", "*.png"), recursive=True):
        out.add(_sha(f))
    if len(out) < 20:
        raise CouldNotLook("only %d pictures read under %s (sanity probe)" % (len(out), root))
    return out


def rows_for(mod, repo, donors):
    """{row: [faults]} and the count of lines read."""
    lines, things, projects = load(mod)
    bad = {r: [] for r in ROWS}
    art = judged(repo)
    ids = {}
    for dn, d in things.items():
        for li in d.findall("comps/li"):
            if li.get("Class") == STUDY_COMP:
                ids.setdefault((li.findtext("analysisID") or "").strip(), []).append(dn)
    for key, row in sorted(lines.items()):
        defs = {}
        for field, level in LEVELS:
            name = (row.findtext(field) or "").strip()
            d = things.get(name)
            defs[field] = d
            if d is None:
                bad["three_level_defs"].append("%s: no ThingDef %r for its %s level" % (key, name, level))
                continue
            ext = [li for li in d.findall("modExtensions/li") if li.get("Class") == LEVEL_EXT]
            if len(ext) != 1 or (ext[0].findtext("grade") or "").strip() != level or (ext[0].findtext("line") or "").strip() != key:
                bad["three_level_defs"].append("%s: %s does not carry one level extension with grade %s and line %s" % (key, name, level, key))
            if d.find("designationCategory") is not None:
                bad["three_level_defs"].append("%s: %s is in the build menu (%s)" % (key, name, d.findtext("designationCategory")))
        w, k = defs["wrecked"], defs["kludged"]
        if w is not None:
            if (w.findtext("minifiedDef") or "").strip() != "MinifiedThing" or w.find("thingCategories/li") is None:
                bad["wreck_is_carried"].append("%s: the Wrecked def has no carried form (minifiedDef MinifiedThing and a thingCategory)" % key)
            if w.find("terrainAffordanceNeeded") is not None:
                bad["wreck_is_carried"].append("%s: the Wrecked def names a ground need (%s)" % (key, w.findtext("terrainAffordanceNeeded")))
        else:
            bad["wreck_is_carried"].append("%s: no Wrecked def" % key)
        # the two projects and their studies
        p1n, p2n = (row.findtext("firstProject") or "").strip(), (row.findtext("secondProject") or "").strip()
        for pn, field, d in ((p1n, "wrecked", w), (p2n, "kludged", k)):
            p = projects.get(pn)
            dn = (row.findtext(field) or "").strip()
            if p is None:
                bad["two_projects_studied"].append("%s: no ResearchProjectDef %r" % (key, pn))
                continue
            if [li.text.strip() for li in p.findall("requiredAnalyzed/li") if li.text] != [dn]:
                bad["two_projects_studied"].append("%s: %s is not locked by the study of %s alone" % (key, pn, dn))
            comps = [li for li in (d.findall("comps/li") if d is not None else []) if li.get("Class") == STUDY_COMP]
            if len(comps) != 1:
                bad["two_projects_studied"].append("%s: %s carries %d analysis comps, want 1" % (key, dn, len(comps)))
                continue
            c = comps[0]
            aid = (c.findtext("analysisID") or "").strip()
            if not aid.isdigit() or len(ids.get(aid, [])) != 1:
                bad["two_projects_studied"].append("%s: %s has analysisID %r, used by %s" % (key, dn, aid, ids.get(aid)))
            if (c.findtext("canStudyInPlace") or "").strip().lower() != "true" or c.find("targetingParameters") is None \
                    or not (c.findtext("activateTexPath") or "").strip() or (c.findtext("requiresMechanitor") or "false").strip().lower() == "true":
                bad["two_projects_studied"].append("%s: the analysis comp of %s is not studied where it stands by any colonist "
                                                   "(canStudyInPlace, targetingParameters, activateTexPath, no mechanitor)" % (key, dn))
        if p1n and p2n and p2n in projects and p1n not in [li.text.strip() for li in projects[p2n].findall("prerequisites/li") if li.text]:
            bad["two_projects_studied"].append("%s: %s does not follow %s" % (key, p2n, p1n))
        # pictures
        hashes = {}
        for field, level in LEVELS[:2]:
            d = defs[field]
            if d is None:
                bad["pictures_of_its_own"].append("%s: no %s def to draw" % (key, level))
                bad["pictures_judged"].append("%s: no %s def to draw" % (key, level))
                continue
            have, missing = _texture_files(mod, d)
            if missing:
                bad["pictures_of_its_own"].append("%s %s: %d of %d pictures missing (%s)" % (key, level, len(missing), len(have) + len(missing),
                                                                                           os.path.relpath(missing[0], mod) if os.sep in missing[0] else missing[0]))
            if d.find("graphicData/color") is not None:
                bad["pictures_of_its_own"].append("%s %s: a tint on its picture (a shade of a picture is not a picture of its own)" % (key, level))
            hashes[level] = {_sha(p) for p in have}
            if hashes[level] & donors:
                bad["pictures_of_its_own"].append("%s %s: a picture is the factory mod's own file" % (key, level))
            unjudged = [os.path.relpath(p, mod) for p in have if art.get(os.path.normpath(os.path.relpath(p, repo))) != _sha(p)]
            if unjudged or missing:
                bad["pictures_judged"].append("%s %s: %d of %d pictures have no judge's record for the file as it is now%s"
                                              % (key, level, len(unjudged) + len(missing), len(have) + len(missing),
                                                 " (first %s)" % unjudged[0] if unjudged else ""))
        if hashes.get("Wrecked") and hashes.get("Kludged") and hashes["Wrecked"] & hashes["Kludged"]:
            bad["pictures_of_its_own"].append("%s: the Wrecked and the Kludged level share a picture file" % key)
        # the row itself
        faults = []
        if not (row.findtext("label") or "").strip():
            faults.append("no label")
        for cost, work in (("kludgeCost", "kludgeWork"), ("refurbishCost", "refurbishWork")):
            c = row.find(cost)
            if c is None or not len(c) or any(not (e.text or "").strip().isdigit() or int(e.text) <= 0 for e in c):
                faults.append("no %s" % cost)
            try:
                if float(row.findtext(work) or 0) <= 0:
                    faults.append("no %s" % work)
            except ValueError:
                faults.append("%s is not a number" % work)
        if row.find("refurbishCost/" + COMPONENT) is None:
            faults.append("the last repair costs no Ancient Component")
        if not (row.findtext("original") or "").strip():
            faults.append("no original")
        if faults:
            bad["table_row_whole"].append("%s: %s" % (key, ", ".join(faults)))
            if "no label" in faults:
                bad["settings_line"].append("%s: no label for its Mod Settings line" % key)
    # Mod Settings: one switch for each row, drawn from the table
    try:
        src = open(os.path.join(mod, "Source", "WreckedMachinesMod.cs"), encoding="utf-8").read()
    except OSError as e:
        raise CouldNotLook(str(e))
    src = re.sub(r"//[^\n]*", "", src)
    field = re.search(r"public\s+static\s+Dictionary<string,\s*bool>\s+machineLines\b", src)
    scribed = re.search(r"Scribe_Collections\.Look\(\s*ref\s+machineLines\s*,\s*\"machineLines\"", src)
    ui = src.split("void DoWindowContents", 1)[-1]
    drawn = re.search(r"RM_MachineLineDef", ui) and re.search(r"machineLines", ui)
    if not (field and scribed and drawn):
        bad["settings_line"].append("Mod Settings does not hold, save and draw machineLines from the table (field %s, saved %s, drawn %s)"
                                    % (bool(field), bool(scribed), bool(drawn)))
    if not lines:
        for r in ROWS:
            bad[r].append("the onboarding table holds no line")
    return bad, len(lines)


# ---------------------------------------------------------------- planted faults, on a whole made mod

def _made_mod(d):
    """A tiny whole mod with one line that passes every row; -> (mod folder, repo folder)."""
    mod = os.path.join(d, "src", "RimMandrake", "WreckedMachines")
    for sub in ("Defs/MachineLines", "Defs/Things", "Defs/Research", "Source", "Textures/WM/W", "Textures/WM/K"):
        os.makedirs(os.path.join(mod, sub))
    os.makedirs(os.path.join(d, ART_RECORDS))

    def thing(name, level, tex, extra=""):
        study = ('<comps><li Class="%s"><analysisID>%d</analysisID><canStudyInPlace>true</canStudyInPlace><activateTexPath>UI/Icons/Study'
                 '</activateTexPath><targetingParameters /></li></comps>' % (STUDY_COMP, 7700 + len(name))) if level != "Refurbished" else ""
        return ('<ThingDef><defName>%s</defName><graphicData><texPath>%s</texPath><graphicClass>Graphic_Multi</graphicClass></graphicData>%s%s'
                '<modExtensions><li Class="%s"><grade>%s</grade><line>made</line></li></modExtensions></ThingDef>' % (name, tex, extra, study, LEVEL_EXT, level))
    open(os.path.join(mod, "Defs/Things/T.xml"), "w").write(
        "<Defs>" + thing("RM_WM_Made_Wrecked", "Wrecked", "WM/W/Made", "<minifiedDef>MinifiedThing</minifiedDef><thingCategories><li>X</li></thingCategories>")
        + thing("RM_WM_Made_Kludged1", "Kludged", "WM/K/Made") + thing("RM_WM_Made_Refurbished12", "Refurbished", "Things/Donor") + "</Defs>")
    open(os.path.join(mod, "Defs/Research/R.xml"), "w").write(
        "<Defs><ResearchProjectDef><defName>P1</defName><requiredAnalyzed><li>RM_WM_Made_Wrecked</li></requiredAnalyzed></ResearchProjectDef>"
        "<ResearchProjectDef><defName>P2</defName><prerequisites><li>P1</li></prerequisites><requiredAnalyzed><li>RM_WM_Made_Kludged1</li>"
        "</requiredAnalyzed></ResearchProjectDef></Defs>")
    open(os.path.join(mod, "Defs/MachineLines/L.xml"), "w").write(
        "<Defs><%s><defName>RM_WM_Line_made</defName><key>made</key><label>made machine</label><original>Donor</original>"
        "<wrecked>RM_WM_Made_Wrecked</wrecked><kludged>RM_WM_Made_Kludged1</kludged><refurbished>RM_WM_Made_Refurbished12</refurbished>"
        "<firstProject>P1</firstProject><secondProject>P2</secondProject><kludgeCost><Steel>10</Steel></kludgeCost><kludgeWork>100</kludgeWork>"
        "<refurbishCost><Steel>20</Steel><%s>1</%s></refurbishCost><refurbishWork>200</refurbishWork></%s></Defs>" % (LINE_TAG, COMPONENT, COMPONENT, LINE_TAG))
    open(os.path.join(mod, "Source/WreckedMachinesMod.cs"), "w").write(
        'class S { public static Dictionary<string, bool> machineLines = new Dictionary<string, bool>();\n'
        'void ExposeData() { Scribe_Collections.Look(ref machineLines, "machineLines", LookMode.Value, LookMode.Value); }\n'
        'void DoWindowContents() { foreach (RM_MachineLineDef l in All) Draw(machineLines, l); } }\n')
    slots = []
    for lvl in ("W", "K"):
        for f in FACINGS:
            p = os.path.join(mod, "Textures", "WM", lvl, "Made" + f + ".png")
            open(p, "wb").write(b"\x89PNG" + (lvl + f).encode())
            slots.append({"slot": os.path.relpath(p, d), "sha": _sha(p)})
    json.dump({"subject": "made", "verdict": "keep", "judge": {"made_it": False}, "slots": slots},
              open(os.path.join(d, ART_RECORDS, "made_judge_verdict.json"), "w"))
    return mod, d


def _edit(path, a, b):
    s = open(path).read()
    if a not in s:
        raise AssertionError("plant: %r not in %s" % (a, path))
    open(path, "w").write(s.replace(a, b))


def _plants():
    """(name, row that must go red, function(mod, repo))."""
    T, R, L, S = "Defs/Things/T.xml", "Defs/Research/R.xml", "Defs/MachineLines/L.xml", "Source/WreckedMachinesMod.cs"
    j = lambda m, f: os.path.join(m, f)
    return (
        ("kludged def missing", "three_level_defs", lambda m, r: _edit(j(m, L), "<kludged>RM_WM_Made_Kludged1</kludged>", "<kludged>RM_WM_None</kludged>")),
        ("level in the build menu", "three_level_defs", lambda m, r: _edit(j(m, T), "<defName>RM_WM_Made_Kludged1</defName>", "<defName>RM_WM_Made_Kludged1</defName><designationCategory>Production</designationCategory>")),
        ("extension names another level", "three_level_defs", lambda m, r: _edit(j(m, T), "<grade>Kludged</grade>", "<grade>Wrecked</grade>")),
        ("wreck has no carried form", "wreck_is_carried", lambda m, r: _edit(j(m, T), "<minifiedDef>MinifiedThing</minifiedDef>", "")),
        ("wreck needs heavy ground", "wreck_is_carried", lambda m, r: _edit(j(m, T), "<minifiedDef>MinifiedThing</minifiedDef>", "<minifiedDef>MinifiedThing</minifiedDef><terrainAffordanceNeeded>Heavy</terrainAffordanceNeeded>")),
        ("first project needs no study", "two_projects_studied", lambda m, r: _edit(j(m, R), "<requiredAnalyzed><li>RM_WM_Made_Wrecked</li></requiredAnalyzed>", "")),
        ("second project studies the wreck", "two_projects_studied", lambda m, r: _edit(j(m, R), "<li>RM_WM_Made_Kludged1</li>", "<li>RM_WM_Made_Wrecked</li>")),
        ("study carried to a bench", "two_projects_studied", lambda m, r: _edit(j(m, T), "<canStudyInPlace>true</canStudyInPlace>", "")),
        ("two defs share an analysis id", "two_projects_studied", lambda m, r: _edit(j(m, T), "<analysisID>7719</analysisID>", "<analysisID>7718</analysisID>")),
        ("a facing has no picture", "pictures_of_its_own", lambda m, r: os.remove(j(m, "Textures/WM/K/Made_east.png"))),
        ("kludged draws the wreck's files", "pictures_of_its_own", lambda m, r: [shutil.copyfile(j(m, "Textures/WM/W/Made" + f + ".png"), j(m, "Textures/WM/K/Made" + f + ".png")) for f in FACINGS]),
        ("kludged is a tint", "pictures_of_its_own", lambda m, r: _edit(j(m, T), "<texPath>WM/K/Made</texPath>", "<texPath>WM/K/Made</texPath><color>(120,110,100)</color>")),
        ("a picture changed after the judge", "pictures_judged", lambda m, r: open(j(m, "Textures/WM/W/Made_north.png"), "ab").write(b"x")),
        ("no judge's record", "pictures_judged", lambda m, r: os.remove(os.path.join(r, ART_RECORDS, "made_judge_verdict.json"))),
        ("the maker judged it", "pictures_judged", lambda m, r: _edit(os.path.join(r, ART_RECORDS, "made_judge_verdict.json"), '"made_it": false', '"made_it": true')),
        ("last repair needs no component", "table_row_whole", lambda m, r: _edit(j(m, L), "<%s>1</%s>" % (COMPONENT, COMPONENT), "")),
        ("a repair with no work", "table_row_whole", lambda m, r: _edit(j(m, L), "<kludgeWork>100</kludgeWork>", "")),
        ("settings not drawn from the table", "settings_line", lambda m, r: _edit(j(m, S), "foreach (RM_MachineLineDef l in All) Draw(machineLines, l);", "")),
        ("row has no label", "settings_line", lambda m, r: _edit(j(m, L), "<label>made machine</label>", "")),
    )


def planted():
    """-> (count of plants, [plants that were not caught or a made mod that does not pass])."""
    blind = []
    plants = _plants()
    for name, want, fn in (("nothing planted", None, None),) + plants:
        d = tempfile.mkdtemp(prefix="wm_onb_")
        try:
            mod, repo = _made_mod(d)
            if fn:
                fn(mod, repo)
            bad, n = rows_for(mod, repo, {"0" * 64})
            red = sorted(r for r in ROWS if bad[r])
            if want is None and red:
                blind.append("the whole made mod does not pass: %s %s" % (red, bad[red[0]][:1]))
            if want is not None and want not in red:
                blind.append("%s did not turn %s red" % (name, want))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return len(plants), blind


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vfef", default=VFEF_DEFAULT)
    a = ap.parse_args()
    try:
        donors = donor_hashes(a.vfef)
        bad, n = rows_for(HERE, REPO, donors)
        nplants, blind = planted()
    except CouldNotLook as e:
        print("T_ONBOARDING_COMPLETE: COULD NOT LOOK: %s" % e)
        return 2
    for r in ROWS:
        print("%-22s %-4s worst %d faults, limit 0, %d lines read%s" % (r, "PASS" if not bad[r] else "FAIL", len(bad[r]), n,
                                                                       "".join("\n    " + b for b in bad[r][:6])
                                                                       + ("\n    ... %d more" % (len(bad[r]) - 6) if len(bad[r]) > 6 else "")))
    print("planted faults: %d of %d caught%s" % (nplants - len([b for b in blind if "did not turn" in b]), nplants,
                                                "; " + "; ".join(blind) if blind else ""))
    red = [r for r in ROWS if bad[r]]
    fail = bool(red or blind)
    print("T_ONBOARDING_COMPLETE: %s (%d rows, %d not PASS, %d lines)" % ("FAIL" if fail else "PASS", len(ROWS), len(red), n))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
