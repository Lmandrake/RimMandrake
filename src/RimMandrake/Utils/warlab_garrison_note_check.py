#!/usr/bin/env python3
"""Proof for WARLAB_GARRISON_DESIGN_EARLY_BLAST: the design note says what the item owes, and every existing
system it cites resolves in src/. Names the note introduces are listed, and must NOT exist yet or be built."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
NOTE = ROOT / "design/Jawa/worldbuilding/warlab_garrison_early_blast_2026-11-01.md"
VERDICT = ROOT / "infrastructure/state/delegated/2026-11-01/warlab_garrison_early_blast.json"
SECTIONS = ["## 2. The heat rise", "## 4. The garrison", "## 5. The codes", "## 6. Where it meets other rulings",
            "## 7. Mod Settings", "## Judgment"]
PHRASES = ["**Who.**", "**Where.**", "**Persistence.**", "RaiseFloor", "AdjustVisibility", "CodesUsable",
           "labFate", "Route6Live", "WARLAB_ROUTE6_ASK_DOES_LAKE_LIGHT_FUSE"]
ROUTES = ROOT / "design/Jawa/worldbuilding/biomes/the_chill_warlab_routes_spec_2026-09-27.md"
BLIND_ROUTE = "Round 2 is the blind check"
# Judge round 1 removed the blast-lit Route 6: a ruled route is not edited on an agent's reading.
GONE = {NOTE: ["Route 6 clock", "Days until the Empire"], ROUTES: ["warlab_garrison_early_blast", "ordnance clock"]}
EXISTING = ["WarLabCraterMutation", "GameComponent_WarLabCrater", "CompIgniteCraterOnDestroy", "EmpireSearch",
            "GameComponent_ColonyVisibility", "GameComponent_EmpireSearch", "MapComponent_EmpireSearch",
            "FuelBlastInvestigation", "EmpireLadderMath", "RFPSettings", "CompRedeemRakatanCommandCodes",
            "AshfallCommandCodesFlag", "RUT_RakatanCommandCodes", "RUT_WarLabSite", "RUT_GenStep_WarLabSite",
            "RM_GenStep_DetentionPost", "RM_ChillCrater", "RM_ChillHeatedSuit", "RM_HeatedSuitCharger",
            "RUT_Jawa_Empire_Grunt", "RUT_Jawa_Empire_Heavy", "RUT_Jawa_Empire_Specialist", "RUT_Jawa_Empire_Leader",
            "launchResetMultiplier", "ANCIENT_WAR_LAB_1", "ASSAILANT_WARLAB_BUILD_MERGE"]


def ruling_defects(text: str) -> list[str]:
    """The record is honest about the ruling. A KEEP on file is one way. The other leaves it to the blind check, whose
    own verdict rules (contract step 2): this script cannot rule, so it passes only with round 1 and that route on file."""
    bad = []
    if BLIND_ROUTE not in text.split("## Judgment", 1)[-1]:
        bad.append(f"note's ## Judgment does not say: {BLIND_ROUTE}")
    try:
        rec = json.loads(VERDICT.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return bad + [f"no readable verdict file: {e}"]
    if rec.get("verdict") not in ("KEEP", "ROUND2_AT_BLIND_CHECK"):
        bad.append(f"verdict neither KEEP nor sent to the blind check: {str(rec.get('verdict'))[:60]}")
    if rec.get("verdict") == "KEEP" and not rec.get("judge"):
        bad.append("verdict names no judge")
    if not any(r.get("round") == 1 and r.get("verdict") == "REDO" for r in rec.get("judge_rounds", [])):
        bad.append("round 1 REDO is not on file")
    return bad


def main() -> int:
    text = NOTE.read_text(encoding="utf-8")
    bad = [f"missing section/phrase: {s}" for s in SECTIONS + PHRASES if s not in text]
    for sym in EXISTING:
        if sym not in text:
            bad.append(f"note no longer cites {sym}")
            continue
        hit = subprocess.run(["git", "-C", str(ROOT), "grep", "-q", "-F", sym, "--", "src", "infrastructure/state/items"])
        if hit.returncode != 0:
            bad.append(f"cited symbol resolves nowhere: {sym}")
    for path, phrases in GONE.items():
        bad += [f"{path.name} still says: {p}" for p in phrases if p in path.read_text(encoding="utf-8")]
    bad += ruling_defects(text)
    print("\n".join(bad) if bad else f"OK {len(EXISTING)} symbols, {len(SECTIONS + PHRASES)} sections; the ruling is contract step 2")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
