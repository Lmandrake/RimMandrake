#!/usr/bin/env python3
"""selftest_stage3_owed.py -- the six offline checks FlowWorks 0.1.0's Maturation Stage 3 owed (2026-11-14).

One section per test id of design/concepts/FlowWorks/version/test_table.json; run one with --only <section>, or all:

    python3 src/RimMandrake/FlowWorks/selftest_stage3_owed.py [--only prison_care|wetting|wetness_probe|toss_flame|fetch_fallen|coating]

The production code these bars need is Verse-bound (Harmony patches on Room, WorkGivers, JobDrivers), which the C#
SelfTest cannot run, so each section is a SOURCE LAW over the shipping .cs and XML (comments masked), the way
selftest_natives_drink_own_water.py's half A is: it names what must be true of the code for the bar to hold, and each
law's undo mutant must turn it RED, or the check is blind. A section whose behaviour does not exist yet is RED by
design (built failing first, his ruling 2026-11-13: "we build the test at the same time as the item"). The live half
of each is a scene in northstar/concept_scenes.py, run at Stage 6.

  prison_care     T_PRISON_CARE_OFFLINE    a held pawn in a drained, enclosed pit is a prisoner without a bed; fed and
                                           tended from the lip; a bed elsewhere does not move him   (code present)
  wetting         T_WETTING_OFFLINE        cells within two squares of a filled canal read wetted, the third does not;
                                           a wetted cell holds no liquid and costs no wading         (code absent)
  wetness_probe   T_WETNESS_PROBE_OFFLINE  a static_call probe reads a cell's wetting for the live scene (code absent)
  toss_flame      T_TOSS_FLAME_OFFLINE     an order: a colonist walks to the rim and tosses a flame onto the picked
                                           square                                                    (code absent)
  fetch_fallen    T_FETCH_FALLEN_OFFLINE   raiders climb into a pit to bring out a comrade held there (ladder jobs
                                           exist for trenches; the fetch itself is absent)
  coating         T_LIQUID_COATING_OFFLINE a pawn out of a staining liquid carries a named condition that plain water
                                           washes off                                               (code absent)
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
DEFS = HERE / "Defs"


def mask(text):
    """Strip // and /* */ comments, keep string literals (a law must hold in code, not in a comment)."""
    text = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), text, flags=re.S)
    return re.sub(r'("(?:\\.|[^"\\])*")|//[^\n]*', lambda m: m.group(1) or "", text)


def cs_all():
    return {p: mask(p.read_text(encoding="utf-8", errors="replace")) for p in SRC.rglob("*.cs") if "SelfTest" not in p.parts}


def xml_all():
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in DEFS.rglob("*.xml"))


# ------------------------------------------------------------------------------------------------ the laws
def prison_care(cs, xml):
    t = cs.get(SRC / "Superdeep" / "RM_PitPrisonCare.cs", "")
    return [
        ("a pit room is a prison cell: IsPrisonCell postfix sets true for PrisonRoom",
         "nameof(Room.IsPrisonCell)" in t and re.search(r"if \(!__result && RM_PitPrisonCare\.PrisonRoom\(__instance\)\) __result = true;", t)),
        ("only an enclosed pit counts: PrisonRoom needs ProperRoom and IsPitRoom",
         re.search(r"PrisonRoom\(Room room\) =>[^;]*room\.ProperRoom[^;]*RM_PitRooms\.IsPitRoom\(room\)", t)),
        ("kept = a secure prisoner of the colony, held in that pit",
         re.search(r"Kept\(Pawn p\) =>[^;]*IsPrisonerOfColony[^;]*PrisonerIsSecure[^;]*PrisonRoom\(p\.GetRoom\(\)\)[^;]*RM_SuperdeepTrap\.IsHeld\(p\)", t)),
        ("a bed elsewhere does not move him: TakeToBed returns no job for a kept pawn",
         "WorkGiver_Warden_TakeToBed" in t and re.search(r"if \(!RM_PitPrisonCare\.Kept\(t as Pawn\)\) return true;\s*__result = null;\s*return false;", t)),
        ("fed without a bed: ShouldBeFed postfix for lip care",
         "WardenFeedUtility.ShouldBeFed" in t and re.search(r"RM_PitPrisonCare\.LipCare\(p\) && p\.guest\.CanBeBroughtFood", t)),
        ("tended without a bed: GoodLayingStatusForTend postfix for lip care",
         "GoodLayingStatusForTend" in t and re.search(r"RM_PitPrisonCare\.LipCare\(patient\) && patient\.Downed\) __result = true;", t)),
        ("food lands in the hole, not outside it",
         re.search(r"RM_PitPrisonCare\.LipCare\(t as Pawn\)\) __result\.targetC = t\.Position;", t)),
    ]


def _any(cs, pat):
    return [str(p.relative_to(HERE)) for p, t in cs.items() if re.search(pat, t)]


def wetting(cs, xml):
    return [
        ("a wetting law exists: a class named for wetting", _any(cs, r"\bclass \w*Wett\w*")),
        ("its reach is two squares (owner 2026-11-04: \"Two squares away from the canal\")",
         _any(cs, r"\bclass \w*Wett\w*[\s\S]*?\b\w*Reach\w*\s*=\s*2\b")),
        ("a wetted cell is never standing water: the wetting class writes no liquid",
         (lambda hits: hits and not any(re.search(r"\b(AddWater|SetWater\w*|SpawnFlood|Pour\w*)\(", cs[HERE / h]) for h in hits))(
             _any(cs, r"\bclass \w*Wett\w*"))),
    ]


def wetness_probe(cs, xml):
    return [("a static_call probe reads one cell's wetting (\"x,z\" -> \"WETTING ... wetted=b\")",
             _any(cs, r"public static string \w*Wetness\w*\(string \w+\)[\s\S]{0,1500}?wetted="))]


def toss_flame(cs, xml):
    return [
        ("a JobDef for the toss-flame order", re.search(r"<defName>RM_\w*Toss\w*Flame\w*</defName>", xml)),
        ("its JobDriver walks to the rim and lights the picked square", _any(cs, r"class JobDriver_\w*Toss\w*[\s\S]*?(FireUtility\.TryStartFireIn|TryIgnite)")),
        ("the player can give it: a float-menu or gizmo offers it", _any(cs, r"(FloatMenuOption|Command_Target)[\s\S]{0,400}?Toss")),
    ]


def fetch_fallen(cs, xml):
    return [
        ("the ladder half exists: raiders already set a ladder (trench raids)", re.search(r"<defName>RM_RaiderSetLadder</defName>", xml)),
        ("a raider job to fetch a comrade held in a pit", re.search(r"<defName>RM_Raider\w*(Fetch|Rescue|Carry)\w*(Fallen|Comrade|Ally)\w*</defName>", xml)),
        ("its target is a pawn of the raider's own faction held in a pit",
         _any(cs, r"(Fallen|Comrade)[\s\S]{0,600}?RM_SuperdeepTrap\.IsHeld\([\s\S]{0,300}?Faction")),
    ]


def coating(cs, xml):
    return [
        ("a named condition for a staining coat", re.search(r"<HediffDef[\s\S]{0,300}?<defName>RM_\w*Coat\w*</defName>", xml)),
        ("leaving oil, tar, blood or another staining liquid applies it", _any(cs, r"Coat\w*[\s\S]{0,800}?(Oil|Tar|Blood|stain)")),
        ("normal water washes it off", _any(cs, r"(Wash|Rinse)\w*[\s\S]{0,600}?(RM_Liquid_FreshWater|Fresh|Water)[\s\S]{0,300}?Coat")),
        # RIMMANDRAKE_BUILD_FLOWWORKS_COATING_WASH_PASSED_ON_NOTHING: the three laws above match loose text; these pin the
        # behaviour in RM_LiquidCoating.cs (each has an undo mutant in COAT_MUTANTS)
        ("the map ticks the coating", _any(cs, r"RM_LiquidCoating\.Tick\(map, this\);")),
        ("stepping out of a coating liquid adds the coat",
         _any(cs, r"if \(f != null && f\.coats\)[\s\S]{0,200}?wading\.Remove\(id\);\s*Coat\(p, left\);")
         and _any(cs, r"public static void Coat\([\s\S]{0,700}?p\.health\.AddHediff\(h\);")),
        ("wading a washing liquid removes the coat",
         _any(cs, r"if \(f != null && f\.washesCoat\)\s*\{\s*Wash\(p, f\);")
         and _any(cs, r"public static bool Wash\([\s\S]{0,400}?p\.health\.RemoveHediff\(h\);")),
        ("oil, tar and blood coat; water washes",
         all(re.search(r"<defName>%s</defName>[\s\S]{0,200}?<%s>true</%s>" % (d, f, f), xml)
             for d, f in (("RM_Fluid_Oil", "coats"), ("RM_Fluid_Tar", "coats"), ("RM_Fluid_Blood", "coats"),
                          ("RM_Fluid_Water", "washesCoat")))),
        ("the coat is named for its liquid", _any(cs, r"class Hediff_LiquidCoat[\s\S]{0,300}?LabelBase => \"coated in \" \+")),
    ]


COAT_FILE = SRC / "RM_LiquidCoating.cs"
COAT_MUTANTS = {
    "never ticked": (SRC / "RM_MapComponent_Excavation.cs", "RM_LiquidCoating.Tick(map, this);", ""),
    "leaving forgets the coat": (COAT_FILE, "Coat(p, left);", ""),
    "coat never added": (COAT_FILE, "p.health.AddHediff(h);", ""),
    "water never washes": (COAT_FILE, "Wash(p, f);", ""),
    "wash keeps the coat": (COAT_FILE, "p.health.RemoveHediff(h);", ""),
    "nameless coat": (COAT_FILE, 'LabelBase => "coated in " +', 'LabelBase => "x" +'),
}


SECTIONS = {"prison_care": prison_care, "wetting": wetting, "wetness_probe": wetness_probe, "toss_flame": toss_flame,
            "fetch_fallen": fetch_fallen, "coating": coating}

# undo mutants for the one section with code today: each must turn a law RED, or the law is blind
PRISON_MUTANTS = {
    "room patch gone": ("if (!__result && RM_PitPrisonCare.PrisonRoom(__instance)) __result = true;", ""),
    "stay lets the bed win": ("__result = null;\n            return false;", "return true;"),
    "kept forgets the hold": ("&& RM_SuperdeepTrap.IsHeld(p)", ""),
    "feed patch gone": ("RM_PitPrisonCare.LipCare(p) && p.guest.CanBeBroughtFood", "false"),
    "food drops outside": ("__result.targetC = t.Position;", ""),
}


def run(name, cs, xml):
    laws = SECTIONS[name](cs, xml)
    bad = [w for w, ok in laws if not ok]
    for w, ok in laws:
        print("  %s  %s" % ("ok  " if ok else "RED ", w))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=sorted(SECTIONS))
    a = ap.parse_args()
    cs, xml = cs_all(), xml_all()
    faults = []
    for name in ([a.only] if a.only else list(SECTIONS)):
        print(name)
        faults += ["%s: %s" % (name, w) for w in run(name, cs, xml)]
        if name == "prison_care":
            p = SRC / "Superdeep" / "RM_PitPrisonCare.cs"
            raw = mask(p.read_text(encoding="utf-8"))
            for m, (old, new) in PRISON_MUTANTS.items():
                if old not in raw:
                    faults.append("prison_care mutant %r: its text is not in the source (the law moved)" % m)
                    continue
                if not [w for w, ok in prison_care({**cs, p: raw.replace(old, new)}, xml) if not ok]:
                    faults.append("prison_care mutant %r stayed green (blind law)" % m)
            print("  %d undo mutants checked" % len(PRISON_MUTANTS))
        if name == "coating" and not [f for f in faults if f.startswith("coating:")]:
            for m, (p, old, new) in COAT_MUTANTS.items():
                if old not in cs[p]:
                    faults.append("coating mutant %r: its text is not in the source (the law moved)" % m)
                    continue
                if not [w for w, ok in coating({**cs, p: cs[p].replace(old, new)}, xml) if not ok]:
                    faults.append("coating mutant %r stayed green (blind law)" % m)
            for d, f in (("RM_Fluid_Water", "washesCoat"), ("RM_Fluid_Oil", "coats")):
                bad = re.sub(r"(<defName>%s</defName>[\s\S]{0,200}?)<%s>true</%s>" % (d, f, f), r"\1", xml, count=1)
                if bad == xml or not [w for w, ok in coating(cs, bad) if not ok]:
                    faults.append("coating mutant %s loses %s stayed green (blind law)" % (d, f))
            print("  %d undo mutants checked" % (len(COAT_MUTANTS) + 2))
    print(("RED %d: " % len(faults) + "; ".join(faults)) if faults else "PASS")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main())
