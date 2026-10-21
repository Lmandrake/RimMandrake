#!/usr/bin/env python3
# selftest-timeout: 120
"""selftest_plant_glow_halfset.py — no plant in src/ sets growMinGlow 0 and leaves growOptimalGlow above 0.

Why: vanilla's light factor is GenMath.InverseLerp(growMinGlow, growOptimalGlow, glow). With min 0 and the default
optimal 1.0 it is 0 at glow 0, so a plant meant to live in the dark never grows and (dieIfNoSunlight defaults true)
dies after 7.5 days, and WildPlantSpawner re-seeds it: a churn of stunted plants. Under the tidal lock the night side
has glow 0 forever. Vanilla cave plants (Glowstool) set BOTH fields to 0. Item DARK_FLORA_FIX_WILTS_WITHOUT_A_SUN,
audit design/RimMandrake/glow_consumers_2026-10-20.md §A.

Part 1, synthetic: resolve() follows ParentName through abstract Name= defs; the lint flags the half-set pattern
(own fields, inherited fields, a patch that adds growMinGlow 0 alone) and passes 0/0 and light-needing plants.
Part 2, the REAL src/: every plant ThingDef resolves to a factor > 0 at glow 0 whenever its growMinGlow is 0.
SANITY PROBE: the scan must see a few hundred plant defs and resolve RM_Brindeth (Sump) to 0/0, or it is not looking.

ALLOW lists a plant that deliberately sets min 0 with optimal > 0 (it then grows only under some light and dies in
the dark). Each entry carries its reason. Empty on purpose.
"""
from __future__ import annotations

import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEFAULT_MIN, DEFAULT_OPT = 0.51, 1.0     # Verse.PlantProperties defaults (1.6)
ALLOW: dict[str, str] = {}
FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:600]}]"))
    if not cond:
        FAILS.append(msg)


def scan(root: Path):
    """(concrete plant defs {defName: elem}, abstract {Name: elem}, half-set patch ops [(file, xpath)])."""
    concrete, abstract, patch_hits = {}, {}, []
    for p in sorted(root.rglob("*.xml")):
        try:
            top = ET.parse(p).getroot()
        except (ET.ParseError, OSError):
            continue
        if top.tag == "Defs":
            for d in top:
                if d.tag != "ThingDef":
                    continue
                if d.get("Name"):
                    abstract[d.get("Name")] = d
                dn = d.findtext("defName")
                if dn and d.get("Abstract", "").lower() != "true":
                    concrete[dn] = d
        elif top.tag == "Patch":
            for op in top.iter("Operation"):
                v = op.find("value")
                if v is None:
                    continue
                for pl in [v] + list(v.iter("plant")):
                    mg, og = pl.findtext("growMinGlow"), pl.findtext("growOptimalGlow")
                    if mg is not None and float(mg) == 0 and (og is None or float(og) > 0):
                        patch_hits.append((p.relative_to(root).as_posix(), op.findtext("xpath") or "?"))
    return concrete, abstract, patch_hits


def resolve(d, abstract, path, depth=0):
    if d is None or depth > 16:
        return None
    v = d.find(path)
    if v is not None:
        return v.text
    par = d.get("ParentName")
    return resolve(abstract.get(par), abstract, path, depth + 1) if par else None


def is_plant(d, abstract) -> bool:
    cur, depth = d, 0
    while cur is not None and depth < 16:
        if cur.find("plant") is not None or (cur.get("ParentName") or "") in ("PlantBase", "PlantBaseNonEdible",
                                                                              "TreeBase", "BushBase"):
            return True
        cur, depth = abstract.get(cur.get("ParentName")), depth + 1
    return False


def lint(root: Path):
    """(violations [(defName, min, opt)], plant count, resolved {defName: (min, opt)}, patch hits)."""
    concrete, abstract, patch_hits = scan(root)
    bad, seen = [], {}
    for dn, d in concrete.items():
        if not is_plant(d, abstract):
            continue
        mg = resolve(d, abstract, "plant/growMinGlow")
        og = resolve(d, abstract, "plant/growOptimalGlow")
        mn = float(mg) if mg is not None else DEFAULT_MIN
        op = float(og) if og is not None else DEFAULT_OPT
        seen[dn] = (mn, op)
        if mn == 0 and op > 0 and dn not in ALLOW:
            bad.append((dn, mn, op))
    return sorted(bad), len(seen), seen, patch_hits


def synthetic() -> None:
    d = Path(tempfile.mkdtemp(prefix="glowlint_"))
    (d / "Defs").mkdir()
    (d / "Patches").mkdir()
    (d / "Defs" / "a.xml").write_text("""<Defs>
  <ThingDef Name="DarkBase" ParentName="PlantBase" Abstract="True"><plant><growMinGlow>0</growMinGlow></plant></ThingDef>
  <ThingDef Name="GoodBase" ParentName="PlantBase" Abstract="True"><plant><growMinGlow>0</growMinGlow><growOptimalGlow>0</growOptimalGlow></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>OwnHalf</defName><plant><growMinGlow>0</growMinGlow></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>OwnHalfExplicit</defName><plant><growMinGlow>0</growMinGlow><growOptimalGlow>1</growOptimalGlow></plant></ThingDef>
  <ThingDef ParentName="DarkBase"><defName>InheritedHalf</defName><plant><growDays>3</growDays></plant></ThingDef>
  <ThingDef ParentName="GoodBase"><defName>InheritedGood</defName><plant><growDays>3</growDays></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>OwnGood</defName><plant><growMinGlow>0</growMinGlow><growOptimalGlow>0</growOptimalGlow></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>SunPlant</defName><plant><growDays>3</growDays></plant></ThingDef>
  <ThingDef ParentName="DarkBase"><defName>ChildFixes</defName><plant><growOptimalGlow>0</growOptimalGlow></plant></ThingDef>
  <ThingDef ParentName="BuildingBase"><defName>NotAPlant</defName></ThingDef>
</Defs>""")
    (d / "Patches" / "p.xml").write_text("""<Patch><Operation Class="PatchOperationAdd">
  <xpath>Defs/ThingDef[defName="X"]/plant</xpath><value><growMinGlow>0</growMinGlow></value></Operation></Patch>""")
    bad, n, seen, ph = lint(d)
    names = [b[0] for b in bad]
    check(names == ["InheritedHalf", "OwnHalf", "OwnHalfExplicit"], "synthetic: flags own, explicit-1 and inherited half-sets",
          names)
    check(n == 7, "synthetic: counts plants only (BuildingBase child is not a plant)", n)
    check(seen.get("ChildFixes") == (0.0, 0.0), "synthetic: a child setting optimal 0 over a half-set base is fixed",
          seen.get("ChildFixes"))
    check(seen.get("SunPlant") == (DEFAULT_MIN, DEFAULT_OPT), "synthetic: unset fields read the vanilla defaults",
          seen.get("SunPlant"))
    check(len(ph) == 1, "synthetic: a patch adding growMinGlow 0 alone is flagged", ph)


def real() -> None:
    bad, n, seen, ph = lint(REPO / "src")
    check(n >= 300, f"sanity: the scan sees the src plant defs ({n})", n)
    check(seen.get("RM_Brindeth") == (0.0, 0.0), "sanity: RM_Brindeth (Sump chemotroph) resolves to 0/0",
          seen.get("RM_Brindeth"))
    check(seen.get("RM_Bryolux") == (0.0, 0.0), "sanity: RM_Bryolux resolves 0/0 through RM_TheRotPortedCavePlantBase",
          seen.get("RM_Bryolux"))
    check(not bad, f"src: no plant with growMinGlow 0 and growOptimalGlow > 0 ({len(bad)})",
          "; ".join(f"{a} min={b} opt={c}" for a, b, c in bad))
    check(not ph, "src: no patch adds growMinGlow 0 without growOptimalGlow 0", ph)
    stale = [k for k in ALLOW if k not in seen]
    check(not stale, "ALLOW names only plants that exist", stale)


def main() -> int:
    synthetic()
    real()
    print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
