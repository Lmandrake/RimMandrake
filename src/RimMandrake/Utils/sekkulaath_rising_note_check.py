#!/usr/bin/env python3
"""Proof for SEKKULAATH_RISING_DESIGN_CRATER_EVENT: the note names the sites and specifies the event, every named
site resolves against the paint-input planet record, every cited symbol resolves in src/, and a judge other than
the maker returned KEEP. A cited name src/ cannot hold is listed here: NEW (the note introduces it) or ENGINE (vanilla)."""
import collections
import csv
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
NOTE = ROOT / "design/Jawa/worldbuilding/sekkulaath_rising_crater_event_2026-11-01.md"
VERDICT = ROOT / "infrastructure/state/delegated/2026-11-01/sekkulaath_rising.json"
WORLD = ROOT / "world/paint_inputs_2026-10-20"
SECTIONS = ["## 2. The event", "## 3. The Wildsteam sites", "## 4. The closed sites", "## 5. Elsewhere only threat rises",
            "## 6. The rising, seen live", "## 7. The cut-scene and the words", "## 9. Mod Settings", "## Judgment"]
PHRASES = ["RUT_SekkulaathRising", "<baseChance>0</baseChance>", "<targetTags><li>World</li></targetTags>"]
HARMED = {"Sporefall": 11927, "Steamreach": 12624}
CLOSED = {"Vhelloth": 12631, "Fevrakesh": 18373, "Octopus Silted Creek": 12630,
          "Elephant Sealshoulder Standing Channel": 3468, "Minonlanen Town": 11922}
REGION = "Fever Wood"
EXISTING = ["WarLabCraterMutation", "GameComponent_WarLabCrater", "RM_ChillCrater", "RM_WorldComponent_DeepYoung",
            "Notify_DisplayTankFreed", "DisplayTankFreed", "RM_GenStep_DisplayTank", "BoldnessMultiplier",
            "RestlessnessLine", "RM_TenantEmergenceSpawner", "RM_MapComponent_TentacleWatch",
            "RM_MapComponent_TheTenant", "RM_FeverWoodMirrorPool", "RM_FeverWoodSettings", "EmpireLadder",
            "RuthlessPursuingMechanoids", "RM_FeverWood", "warLabCraterEnabled"]
NEW = {"RUT_SekkulaathRising", "IncidentWorker_SekkulaathRising", "SekkulaathRisingExtension", "RM_SunkenGround",
       "GameComponent_SekkulaathRising", "RUT_Trader_WildsteamRuined",
       "RaidThreatPointsNow"}                               # F12's owed method, colony_visibility_stat.md 4.3
ENGINE = {"IncidentTargetTagDefOf", "TryDestroyStock"}      # read public in the 1.6 decompile, 2026-11-01


def rows(name: str) -> list[dict]:
    with (WORLD / f"ASHKARR_WORLDMAP_{name}.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cited_symbols(text: str) -> set[str]:
    """Prefixed names and camelCase identifiers, in inline code and in the fenced XML's element text."""
    fenced = re.findall(r"```.*?```", text, re.S)
    inline = re.findall(r"`([^`\n]+)`", re.sub(r"```.*?```", "", text, flags=re.S))
    found = {w for span in inline for w in re.findall(r"[A-Za-z_]\w*", span)
             if w.startswith(("RM_", "RUT_", "RSW_")) or re.search(r"[a-z][A-Z]", w)}
    values = [v for block in fenced for v in re.findall(r'>([^<>]+)<|Class="([^"]+)"', block)]
    values = [a or b for a, b in values]
    return found | {w for v in values for w in re.findall(r"[A-Za-z_]\w*", v)
                    if w.startswith(("RM_", "RUT_", "RSW_")) or re.search(r"[a-z][A-Z]", w)}


def event_list_defects(text: str) -> list[str]:
    """The event's two XML site lists hold exactly the sites this checker resolved."""
    bad = []
    for tag, want in (("harmedSettlements", HARMED), ("closedLandmarks", CLOSED)):
        got = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.S)
        items = re.findall(r"<li>([^<]+)</li>", got[1]) if got else []
        if set(items) != set(want) or got[1].count("<li") != len(want):
            bad.append(f"event list {tag} differs from the checked sites")
    return bad


def in_src(sym: str) -> bool:
    """A whole-word match, or a prefix for a `NAME_*` family. The checker cites every name, so it never counts."""
    me = f":!{pathlib.Path(__file__).resolve().relative_to(ROOT)}"
    how = ["-E", rf"\b{sym}"] if sym.endswith("_") else ["-F", "-w", sym]
    return subprocess.run(["git", "-C", str(ROOT), "grep", "-q", *how, "--", "src", me]).returncode == 0


def world_defects() -> list[str]:
    bad = []
    tiles = {int(r["tile"]): r for r in rows("tiles")}
    settlements = rows("settlements")
    by_name = {r["name"]: r for r in settlements}
    occupied = {int(r["tile"]) for r in settlements}
    landmarks = {r["name"]: int(r["tile"]) for r in rows("landmarks")}
    for name, tile in HARMED.items():
        row = by_name.get(name)
        if row is None or int(row["tile"]) != tile:
            bad.append(f"harmed settlement {name} is not on tile {tile}")
        elif row["faction_def"] != "RUT_Jawa_WildsteamClan":
            bad.append(f"{name} is not a Wildsteam settlement")
    for name, tile in CLOSED.items():
        if landmarks.get(name) != tile:
            bad.append(f"closed site {name} is not a landmark on tile {tile}")
        elif tiles[tile]["region"] != REGION:
            bad.append(f"closed site {name} is outside the region")
        elif tile in occupied:
            bad.append(f"closed site {name} holds a settlement")
    roads = collections.defaultdict(set)
    for r in rows("links"):
        if r["kind"] == "road":
            a, b = int(r["a"]), int(r["b"])
            roads[a].add(b)
            roads[b].add(a)
    closed = set(CLOSED.values())

    def reach(ban: set[int]) -> set[int]:
        seen, todo = {HARMED["Sporefall"]}, [HARMED["Sporefall"]]
        while todo:
            for v in roads[todo.pop()]:
                if v not in seen and v not in ban:
                    seen.add(v)
                    todo.append(v)
        return seen

    full = reach(set())
    if len(full) < 2:
        bad.append("sanity: Sporefall reaches no road tile, the instrument is blind")
    lost = full - reach(closed) - closed
    if lost:
        bad.append(f"closing the sites cuts {len(lost)} other road tiles off from Sporefall")
    return bad


def ruling_defects(text: str) -> list[str]:
    bad = []
    if "not yet ruled" in text.split("## Judgment", 1)[-1]:
        bad.append("note's ## Judgment still says not yet ruled")
    try:
        rec = json.loads(VERDICT.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return bad + [f"no readable verdict file: {e}"]
    if not isinstance(rec, dict):
        return bad + ["verdict file is not an object"]
    if rec.get("verdict") != "KEEP":
        bad.append(f"verdict is not KEEP: {str(rec.get('verdict'))[:60]}")
    if not rec.get("judge"):
        bad.append("verdict names no judge")
    elif rec["judge"] == rec.get("maker") or not rec.get("maker"):
        bad.append("verdict must name a maker and a judge who differ")
    return bad


def main() -> int:
    text = NOTE.read_text(encoding="utf-8")
    bad = [f"missing section/phrase: {s}" for s in SECTIONS + PHRASES if s not in text]
    bad += [f"note does not name site: {s}" for s in [*HARMED, *CLOSED] if s not in text]
    bad += [f"note no longer cites {sym}" for sym in EXISTING if sym not in text]
    cited = cited_symbols(text)
    if not set(EXISTING) & cited:
        bad.append("sanity: the symbol scan sees none of the known names, the instrument is blind")
    bad += [f"cited symbol resolves nowhere: {sym}" for sym in sorted((cited | set(EXISTING)) - NEW - ENGINE) if not in_src(sym)]
    bad += event_list_defects(text)
    bad += world_defects()
    bad += ruling_defects(text)
    print("\n".join(bad) if bad else f"OK {len(cited)} symbols, {len(HARMED) + len(CLOSED)} sites, ruled KEEP")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
