#!/usr/bin/env python3
"""GSS_ART_MANIFEST_FIX_OVERLAY_SIZES: gss_art_manifest.py must size four pieces the way the C# DRAWS them.

The mast heads (power and lamp) are an overlay quad texture-width/128 x 1 cell (RM_MapComponent_Aerial.cs), never the
mast's (2,4); the hose Binding is WrapLength x WrapWidth(vis)/BindBand, never a square; the hose Mouth is drawn EDGE-ON
(HoseMath.OpenEndLip), never a face-on square. Each expected number is re-read from the C# source here (not from the
manifest's own constants), and so are the six fittings' FittingSize, so a retune in the mod fails this test instead of silently mis-sizing every review sheet.
Also: the generator runs clean on today's textures, and the committed gss_art_manifest.json rows equal a regeneration.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AERIAL = REPO / "src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_MapComponent_Aerial.cs"
HOSEMATH = REPO / "src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs"
HOSES = REPO / "src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs"
GSS_TEX = REPO / "src/RimMandrake/GimmeSomeSlack/Textures"
FAILS: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def const(src: str, name: str) -> float:
    """A C# `const`/`static readonly` double or float declaration of `name` (alone or in a `a = x, name = 1.2f` list); a
    comment or local that merely mentions `name = ...` never matches. Exactly one declaration, or the test stops."""
    hits = re.findall(rf"(?:\bconst|\bstatic\s+readonly)\s+(?:double|float)\s+(?:\w+\s*=\s*[^,;]+,\s*)*{name}\s*=\s*([0-9.]+)f?\s*[,;]", src)
    if len(hits) != 1:
        raise SystemExit(f"FAIL constant {name}: {len(hits)} const declarations found (want 1; renamed? update this test from the source)")
    return float(hits[0])


def close(a, b, tol=1e-3) -> bool:
    return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))


def png_width(p: Path) -> int:
    return int.from_bytes(p.read_bytes()[16:20], "big")


def main() -> int:
    aer, hm, hc = AERIAL.read_text(encoding="utf-8"), HOSEMATH.read_text(encoding="utf-8"), HOSES.read_text(encoding="utf-8")

    # 1. the drawing code still has the shapes this test models (else the expectations below are about dead code)
    check(re.search(r"AerialMaterials\.Top\(AerialMaterials\.TopPathFor\(a\)\)", aer) is not None
          and re.search(r"mainTexture\.width\s*/\s*128f\s*:\s*1f,\s*1f,\s*1f\)", aer) is not None,
          "Aerial mast head drawn as plane10 scaled (texture width / 128, 1, 1)")
    check(re.search(r"PieceXZ\(hm\.Binding,[^;]*\(float\)len,\s*\(float\)HoseMath\.WrapWidth\(vis\)\s*/\s*BindBand", hc) is not None,
          "hose Binding drawn len x WrapWidth(vis) / BindBand")
    check(re.search(r"PieceXZ\(hm\.Mouth,[^;]*\(float\)lipAlong,\s*\(float\)lipAcross", hc) is not None,
          "hose Mouth drawn edge-on: lipAlong x lipAcross")
    lip = re.search(r"OpenEndLip\([^)]*\)\s*\{\s*across\s*=\s*([0-9.]+)\s*\*\s*visible;\s*along\s*=\s*([0-9.]+)\s*\*\s*visible;", hm)
    check(lip is not None, "HoseMath.OpenEndLip reads across = k x visible; along = k x visible")
    wrap_w = re.search(r"WrapWidth\(double visible\)\s*=>\s*WrapK\s*\*\s*visible", hm)
    check(wrap_w is not None, "HoseMath.WrapWidth = WrapK x visible")
    if FAILS:
        return 1

    vis = const(hm, "FlatVisible")
    wrap_k, wrap_len, bind_band = const(hm, "WrapK"), const(hm, "WrapLength"), const(hc, "BindBand")
    lip_across, lip_along = float(lip.group(1)), float(lip.group(2))
    exp_binding = [wrap_len, wrap_k * vis / bind_band]
    exp_mouth = [lip_along * vis, lip_across * vis]

    # 2. regenerate the manifest into a temp file (never the committed one)
    spec = importlib.util.spec_from_file_location("gss_art_manifest", HERE / "gss_art_manifest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory() as td:
        mod.OUT = Path(td) / "m.json"
        rc = mod.main()
        check(rc == 0, f"gss_art_manifest.py main() exits 0 (got {rc}; an unclassified texture is exit 2)")
        if rc != 0:
            return 1
        rows = json.loads(mod.OUT.read_text())["rows"]

    by_part: dict[str, list[dict]] = {}
    for r in rows:
        by_part.setdefault(r["part"], []).append(r)
    # sanity probe: the instrument can see each of the four pieces (a zero here is a classifier miss, not a pass)
    for part in ("AerialMastTop", "AerialLampMastTop", "Binding", "Mouth"):
        check(len(by_part.get(part, [])) >= 1, f"{part}: manifest has {len(by_part.get(part, []))} row(s) (>= 1)")

    for part in ("AerialMastTop", "AerialLampMastTop"):
        for r in by_part.get(part, []):
            w = {png_width(GSS_TEX / f"{res}.png") for res in r["resources"]}
            exp = [next(iter(w)) / 128, 1.0]
            check(len(w) == 1 and close(r["size"]["drawSize"], exp),
                  f"{part} {r['look']}: drawSize {r['size']['drawSize']} == texture {sorted(w)} px / 128 x 1 = {exp}")
        styled = [r for r in by_part.get(part, []) if r["look"] != "base"]
        check(bool(styled) and all(close(r["size"]["drawSize"], [2.0, 1.0]) for r in styled),
              f"{part}: every look's head (256 px art) is 2 x 1, never the mast's 2 x 4")
    for r in by_part.get("Binding", []):
        check(close(r["size"]["drawSize"], exp_binding),
              f"Binding {r['look']}: drawSize {r['size']['drawSize']} == WrapLength x WrapK*vis/BindBand {[round(x, 4) for x in exp_binding]}")
    for r in by_part.get("Mouth", []):
        check(close(r["size"]["drawSize"], exp_mouth, 1e-4),
              f"Mouth {r['look']}: drawSize {r['size']['drawSize']} == edge-on lip {[round(x, 4) for x in exp_mouth]}")
        check("EDGE-ON" in r["label"], f"Mouth {r['look']}: row is labelled EDGE-ON")

    # the fittings: HoseMath.FittingSize(vis, PieceBand, maxBand) = min(vis / band, 0.95 x WrapWidth(vis) / maxBand)
    check(re.search(r"FittingSize\(double visible, double hoseBand, double maxBand\)\s*=>\s*Math\.Min\(visible / hoseBand,\s*0\.95 \* WrapWidth\(visible\) / maxBand\)", hm) is not None,
          "HoseMath.FittingSize = min(visible / hoseBand, 0.95 x WrapWidth(visible) / maxBand)")
    band = const(hm, "PieceBand")
    fit_max = {"Coupling": const(hm, "CouplingMax"), "Nozzle": const(hc, "NozzleMax"), "EndCap": const(hc, "EndCapMax")}
    for part in ("Coupling_Brass", "Coupling_Bare", "Nozzle", "Nozzle_Bare", "EndCap", "EndCap_Bare"):
        size = min(vis / band, 0.95 * wrap_k * vis / fit_max[part.split("_")[0]])
        for r in by_part.get(part, []):
            check(close(r["size"]["drawSize"], [size, size]),
                  f"{part} {r['look']}: drawSize {r['size']['drawSize']} == FittingSize {round(size, 3)}")

    # 3. the committed manifest is what the generator makes today (sheets are built from the committed json)
    committed = json.loads((HERE / "gss_art_manifest.json").read_text())["rows"]
    check(committed == rows, f"committed gss_art_manifest.json rows ({len(committed)}) equal a regeneration ({len(rows)})")

    print(f"{'FAIL' if FAILS else 'PASS'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
