#!/usr/bin/env python3
"""selftest_alpha_plants_renders.py — ALPHA_BIOMES_INSTALL_UNINSTALLED_RENDERS stays done.

The 14 Alpha Biomes plants (design/RimMandrake/alpha_biomes_retirement_2026-10-16.md) became RM_ defs; tinkle grass
was then dropped by the owner (picks_plants_and_gaps_sheet_2026-10-19, AB_TinkleGrass row: "drop"). This proves, on
the committed tree:
  * each of the 13 surviving RM_ plant defs resolves, after our own texPath/graphicClass patches, to a texture of
    OURS on disk in its own mod: no `StandIn/` path, and no file byte-identical to any PNG in the donor's workshop
    folder (sarg.alphabiomes, 1841354677);
  * RM_TinkleGrass / AB_TinkleGrass is defined nowhere and named in no RM_ biome roster;
  * every `rotvar_ab_*` render the picks sheet showed (and every one the art ledger records) is installed (its sha is a Textures PNG under src/) or has a
    recorded disposition below.
Exit 0 pass, 1 fail, 2 UNMEASURED (donor folder unreadable, or the ledger shows no rotvar_ab renders at all).
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DONOR = Path(os.environ.get(
    "ALPHA_BIOMES_DONOR_DIR",
    "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/1841354677"))

DEF_FILES = {
    "TheRot": ROOT / "src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml",
    "TheForge": ROOT / "src/RimMandrake/TheForge/Defs/RM_TheForge_DonorPorts.xml",
}
SHEET = ROOT / "infrastructure/state/art/sheets/picks_plants_and_gaps_sheet_2026-10-19.snapshot.json"
PATCHES = [ROOT / "src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml"]
PLANTS = ["Bryolux", "Glowstool", "GiantAgarilux", "GlowingAgarilux", "LilacBeacon", "WitchesOyster",
          "RecurvedStropharia", "ArbuscularMycorrhiza", "SlimyPholiota", "AgaricusDomeCap", "DribblingCap",
          "AgariluxPrime", "FirevineTree"]

# Renders that are deliberately NOT installed, and why (sheet: Transient/biome_ffar/
# picks_plants_and_gaps_sheet_2026-10-19.decisions.json, owner's rulings 2026-10-19).
DISPOSITIONS = {
    "rotvar_ab_bryolux_b_v1": "not picked: AB_Bryolux row decision A (rotvar_ab_bryolux_a_v1, now RM_Rimetangle)",
    "rotvar_ab_giantagarilux_b_v1": "superseded by rotvar_ab_giantagarilux_b_v2 (grader-flagged v1; v2 installed)",
}

FAILS: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def sha(p: str | Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def patched_graphic() -> dict[str, dict[str, str]]:
    """defName -> {texPath|graphicClass: value} from PatchOperationReplace on graphicData children."""
    out: dict[str, dict[str, str]] = {}
    pat = re.compile(r'ThingDef\[defName="(RM_\w+)"\]/graphicData/(texPath|graphicClass)$')
    for pf in PATCHES:
        for op in ET.parse(pf).getroot().iter():
            if op.get("Class") != "PatchOperationReplace":
                continue
            m = pat.search((op.findtext("xpath") or "").strip())
            val = op.find("value")
            if m and val is not None and len(val):
                out.setdefault(m.group(1), {})[m.group(2)] = (val[0].text or "").strip()
    return out


def main() -> int:
    if not DONOR.is_dir():
        print(f"UNMEASURED donor folder unreadable: {DONOR}")
        return 2
    donor_shas = {sha(p) for p in DONOR.rglob("*.png")}
    check(len(donor_shas) > 50, f"sanity: donor folder holds {len(donor_shas)} distinct PNGs (>50)")

    defs = {}
    for mod, f in DEF_FILES.items():
        for d in ET.parse(f).getroot():
            dn = d.findtext("defName")
            if dn:
                defs[dn] = (mod, d)
    patches = patched_graphic()

    for name in PLANTS:
        dn = "RM_" + name
        if dn not in defs:
            check(False, f"{dn} defined")
            continue
        mod, d = defs[dn]
        tex = (d.findtext("graphicData/texPath") or "").strip()
        gcls = (d.findtext("graphicData/graphicClass") or "").strip()
        tex = patches.get(dn, {}).get("texPath", tex)
        gcls = patches.get(dn, {}).get("graphicClass", gcls)
        base = ROOT / "src/RimMandrake" / mod / "Textures" / tex
        files = sorted(base.glob("*.png")) if gcls == "Graphic_Random" else (
            [base.with_suffix(".png")] if base.with_suffix(".png").is_file() else [])
        check(bool(files), f"{dn} ({gcls}) {mod}/Textures/{tex} resolves to {len(files)} PNG(s) of its own mod")
        check("StandIn" not in tex, f"{dn} texPath is not a StandIn path ({tex})")
        donorish = [f.name for f in files if sha(f) in donor_shas]
        check(not donorish, f"{dn} no texture byte-identical to a donor PNG {donorish or ''}")
        for leaf in ("plant/leaflessGraphicPath", "plant/immatureGraphicPath"):
            lp = (d.findtext(leaf) or "").strip()
            if lp:
                check("StandIn" not in lp, f"{dn} {leaf} is not a StandIn path ({lp})")

    tinkle_defs, tinkle_roster = [], []
    for x in glob.glob(str(ROOT / "src/**/*.xml"), recursive=True):
        t = Path(x).read_text(encoding="utf-8", errors="replace")
        if re.search(r"<defName>(RM|AB)_TinkleGrass</defName>", t):
            tinkle_defs.append(x)
        if "/RimMandrake/" in x and "BiomeDefs" in x and re.search(r"<(RM|AB)_TinkleGrass>", t):
            tinkle_roster.append(x)
    check(not tinkle_defs, f"tinkle grass defined nowhere {tinkle_defs or ''}")
    check(not tinkle_roster, f"tinkle grass on no RM_ biome roster {tinkle_roster or ''}")

    bound: dict[str, set[str]] = {}
    for ev in glob.glob(str(ROOT / "infrastructure/state/art/events/*.jsonl")):
        for line in open(ev, encoding="utf-8"):
            if "rotvar_ab_" not in line:
                continue
            e = json.loads(line)
            job = e.get("job") or ""
            if job.startswith("rotvar_ab_") and e.get("type") in ("binding", "variant") and e.get("sha"):
                bound.setdefault(job, set()).add(e["sha"])
    if not bound:
        print("UNMEASURED the art ledger shows no rotvar_ab_* renders")
        return 2
    sheet = json.loads(SHEET.read_text(encoding="utf-8"))
    shown = set(re.findall(r"rotvar_ab_[a-z]+_[ab]_v\d+", json.dumps(sheet["rows"])))
    check(len(shown) >= 17, f"sanity: the picks sheet showed {len(shown)} rotvar_ab renders (>=17)")
    check(not shown - set(bound), f"every rotvar_ab render the sheet showed has a sha in the art ledger "
                                  f"{sorted(shown - set(bound)) or ''}")
    src_shas = {sha(p) for p in (ROOT / "src").rglob("Textures/**/*.png")}
    for job in sorted(bound):
        installed = bool(bound[job] & src_shas)
        why = DISPOSITIONS.get(job)
        check(installed or bool(why), f"{job}: " + ("installed" if installed else f"disposition: {why}"))
    stale = [j for j in DISPOSITIONS if j in bound and bound[j] & src_shas]
    check(not stale, f"no disposition names a render that is in fact installed {stale or ''}")

    print(f"\n{'FAIL' if FAILS else 'PASS'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
