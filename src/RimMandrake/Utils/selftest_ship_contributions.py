#!/usr/bin/env python3
"""selftest_ship_contributions.py -- ship_contributions.py passes the real list and FAILS each kind of false claim.

A checker that only ever says PASS proves nothing (grader-validation). Each mutation below rewrites ONE row of the
real running list into a copy and must flip the verdict to exit 1 with the expected reason; the unmutated copy must
exit 0. Real defs are used as the bad examples, so the checker's view of the repo is exercised, not a fixture.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "src/RimMandrake/Utils/ship_contributions.py"
ITEM = ROOT / "infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md"


def run(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
    try:
        p = subprocess.run([sys.executable, str(TOOL), "--item", f.name], capture_output=True, text=True, timeout=300)
    finally:
        Path(f.name).unlink()
    return p.returncode, p.stdout + p.stderr


def set_defs(text, biome, defs):
    pat = re.compile(r"^(\| %s \|[^|]*\|)[^|]*(\|.*)$" % re.escape(biome), re.M)
    out, n = pat.subn(lambda m: m.group(1) + " " + " ".join("`%s`" % d for d in defs) + " " + m.group(2), text)
    assert n == 1, "row %s not found" % biome
    return out


def unit_checks():
    """The source heuristic on real data: a costList-only mention is not a source, About.xml prose is not one,
    a mineable/butcher/trader mention is; an install-only def nothing hands out fails."""
    sys.path.insert(0, str(TOOL.parent))
    import ship_contributions as sc
    errs = []
    if sc.material_sources("RM_NoSuchMaterial"):
        errs.append("a nonexistent material has sources")
    if sc.material_sources("RM_ToxinSealant"):  # costLists + About.xml prose only; it is CRAFTED (recipeMaker)
        errs.append("RM_ToxinSealant: costList/About mentions counted as sources: %s"
                    % sc.material_sources("RM_ToxinSealant"))
    ix = sc.build_index(sc.find_data(None))
    if sc.obtainable(ix, "RM_ToxinSealant"):
        errs.append("RM_ToxinSealant: its machining-table recipe was not accepted: %s" % sc.obtainable(ix, "RM_ToxinSealant"))
    if not sc.obtainable(ix, "RM_NoSuchMaterial"):
        errs.append("a nonexistent material read as obtainable")
    if not any("RM_PyrelandsFauna" in h for h in sc.material_sources("RM_FurnaceHide")):
        errs.append("RM_FurnaceHide: the leatherDef source was not seen")
    # consumption-only and path-only mentions are not sources (code review 2026-11-11): RM_DeltaSilt's RM_MakeAttar
    # ingredient filter, RM_Vexxith's `<costList Inherit="False">` lines, an item's own texPath
    for item, notfrom in (("RM_DeltaSilt", "RM_MakeAttar"), ("RM_Vexxith", "RM_VentGasTap"),
                          ("RM_Vexxith", "RM_FilterWorks"), ("RM_FossilSkeleton", "RM_Fossils.xml")):
        if any(notfrom in h for h in sc.material_sources(item)):
            errs.append("%s: %s counted as a source" % (item, notfrom))
    if not any("RM_HelixCurators" in h for h in sc.material_sources("RM_CloudRepulsorShip")):
        errs.append("RM_CloudRepulsorShip: the Helix trader stock line was not seen")
    return errs


def main():
    errs = unit_checks()
    if errs:
        print("FAIL\n" + "\n".join(errs))
        return 1
    real = ITEM.read_text(encoding="utf-8")
    code, out = run(real)
    assert code == 0, "the real list should pass:\n" + out[-2000:]
    cases = [
        ("bridge affordance", set_defs(real, "Fever Wood", ["RM_StiltPlatform"]), "needs affordance Bridgeable"),
        ("vent-bound placeWorker", set_defs(real, "The Cauldron", ["RM_VentGasTap"]), "needs a Cauldron vent"),
        ("geyser-bound", set_defs(real, "Pyrelands", ["RM_MagmaThermalGenerator"]), "steam geyser"),
        ("a plant", set_defs(real, "The Abyss", ["RM_Wickwood"]), "a plant"),
        ("no such def", set_defs(real, "Webwork", ["RM_NoSuchShipThing"]), "is not a ThingDef/TerrainDef"),
        ("not the biome's own", set_defs(real, "Webwork", ["RM_FoldLamp"]), "own: no named"),
        ("grow-soil floor", set_defs(real, "The Contagion", ["RM_MulchedSoil"]), "needs affordance GrowSoil"),
        ("missing row", re.sub(r"^\| Webwork \|.*\n", "", real, flags=re.M), "coverage: no row"),
        ("exempt without ruling", set_defs(real, "Webwork", []).replace(
            "| Webwork | **the traction lance**", "| Webwork | EXEMPT for now", 1), "cites no owner ruling"),
        ("exempt with a bare quote mark", set_defs(real, "Webwork", []).replace(
            "| Webwork | **the traction lance**", '| Webwork | EXEMPT: no "ship" part yet', 1), "cites no owner ruling"),
        ("joined rows", real.replace("|\n| The Forge", "|| The Forge", 1), "malformed table line"),
    ]
    bad = []
    for name, text, want in cases:
        code, out = run(text)
        if code != 1 or want not in out:
            bad.append("%s: exit %s, wanted '%s'\n%s" % (name, code, want, out[-800:]))
    if bad:
        print("FAIL\n" + "\n".join(bad))
        return 1
    print("PASS: real list passes; %d false claims each fail with their reason" % len(cases))
    return 0


if __name__ == "__main__":
    sys.exit(main())
