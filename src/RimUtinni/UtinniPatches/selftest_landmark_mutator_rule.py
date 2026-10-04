#!/usr/bin/env python3
"""selftest_landmark_mutator_rule.py — LandmarkDef.ConfigErrors (RimWorld/LandmarkDef.cs:175)
demands a mutatorChances entry with chance >= 1 (MutatorChance: empty node text = 1).
LOAD13_CONFIGERRORS_TRIAGE_1: RUT_ComplexStructures + RUT_Slough_GelatinousBreach failed it.

Red on: any concrete src LandmarkDef with no chance>=1 entry; the inert
RUT_LandmarkIconOnly becoming addable (canSpawnOnLandmark not false, or a
chanceOnNonLandmarkTile > 0). Entries carrying MayRequire are counted but
printed, since they vanish on a list without that mod. Mutants must go red.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INERT = ROOT / "src/RimUtinni/UtinniPatches/Defs/TileMutatorDefs/RUT_LandmarkIconOnly.xml"


def landmark_findings(root, fname="?"):
    out, notes = [], []
    for ld in root.iter("LandmarkDef"):
        if ld.get("Abstract", "").lower() == "true":
            continue
        name = ld.findtext("defName")
        mc = ld.find("mutatorChances")
        best = []
        for e in (list(mc) if mc is not None else []):
            if not isinstance(e.tag, str):
                continue
            txt = (e.text or "").strip()
            ch = float(txt) if txt else 1.0
            if ch >= 1.0:
                best.append(e)
        if not best:
            out.append(f"{fname}:{name} has no mutatorChances entry with chance >= 1")
        elif all(e.get("MayRequire") for e in best):
            notes.append(f"{fname}:{name} chance>=1 only via MayRequire ({best[0].tag})")
    return out, notes


def inert_findings(root):
    out = []
    d = next((t for t in root.iter("TileMutatorDef") if t.findtext("defName") == "RUT_LandmarkIconOnly"), None)
    if d is None:
        return ["RUT_LandmarkIconOnly missing"]
    if (d.findtext("canSpawnOnLandmark") or "").strip().lower() != "false":
        out.append("RUT_LandmarkIconOnly canSpawnOnLandmark is not false: it would land on landmark tiles")
    if float((d.findtext("chanceOnNonLandmarkTile") or "0").strip()) > 0:
        out.append("RUT_LandmarkIconOnly rolls on non-landmark tiles")
    for bad in ("workerClass", "extraGenSteps", "categories"):
        if d.find(bad) is not None:
            out.append(f"RUT_LandmarkIconOnly carries {bad}: no longer inert")
    return out


def main():
    fails, notes, n = [], [], 0
    for p in (ROOT / "src").rglob("*.xml"):
        t = p.read_text(errors="ignore")
        if "<LandmarkDef" not in t:
            continue
        try:
            r = ET.fromstring(t.encode())
        except ET.ParseError as e:
            fails.append(f"{p.name}: parse error {e}")
            continue
        n += sum(1 for _ in r.iter("LandmarkDef"))
        f, nt = landmark_findings(r, p.name)
        fails += f
        notes += nt
    if n < 3:
        print(f"UNMEASURED: only {n} LandmarkDefs seen (expected >= 3)")
        return 2
    inert = ET.fromstring(INERT.read_bytes())
    fails += inert_findings(inert)
    print(f"{n} LandmarkDefs scanned;", *notes, sep="\n  ")
    m = [
        ("landmark without mutators", landmark_findings(ET.fromstring(
            "<Defs><LandmarkDef><defName>X</defName></LandmarkDef></Defs>"))[0]),
        ("landmark with chance 0.5 only", landmark_findings(ET.fromstring(
            "<Defs><LandmarkDef><defName>X</defName><mutatorChances><A>0.5</A></mutatorChances></LandmarkDef></Defs>"))[0]),
        ("inert can spawn on landmark", inert_findings(ET.fromstring(INERT.read_text().split("?>", 1)[1]
            .replace("<canSpawnOnLandmark>false</canSpawnOnLandmark>", "")))),
    ]
    for name, res in m:
        print(f"mutant {name}: {'red' if res else 'STAYED GREEN'}")
        if not res:
            fails.append(f"mutant stayed green: {name}")
    print("FAIL" if fails else "PASS", *fails, sep="\n  ")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
