#!/usr/bin/env python3
"""Proof for WEEPINGSTONES_SETTLED_FOLLOWUPS_1: the Vellak text, the huldu fur icon and the dead catches landed."""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "src/RimMandrake/WeepingStones"
ITEM = "WEEPINGSTONES_SETTLED_FOLLOWUPS_1"
# First 12 hex of the 2026-10-07 gapall renders these replace.
OLD = {"Huldu": "16c98b90489f", "Loomu": "e65730d0ee05", "Skarrin": "ff9591892cb8",
       "Vizhik": "ad6eb677ad19", "Karrek": "1e3b20c69bb2", "Ivvol": "98c2472bf02a"}
MURRIN_KEPT = "94ddb6a01d13"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def thing(xml: Path, name: str) -> ET.Element:
    for d in ET.parse(xml).getroot().iter("ThingDef"):
        if d.findtext("defName") == name:
            return d
    raise SystemExit(f"FAIL no ThingDef {name} in {xml}")


def installs() -> dict[str, str]:
    """sha -> the install event's text, across every seat's art shard."""
    out: dict[str, str] = {}
    for shard in (ROOT / "infrastructure/state/art/events").glob("*.jsonl"):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if ITEM in line:
                ev = json.loads(line)
                if ev.get("sha"):
                    out[ev["sha"]] = line
    return out


def main() -> int:
    bad: list[str] = []
    d = thing(MOD / "Defs/ThingDefs_Races/RM_WeepingStonesNatives.xml", "RM_Vellak")
    text = d.findtext("description") or ""
    for want in ("furred snake", "pack animals"):
        if want not in text:
            bad.append(f"RM_Vellak description lacks {want!r}")
    if "Camel" in text or "RM_ tier" in text:
        bad.append("RM_Vellak description keeps the pre-art text")

    fur = thing(MOD / "Defs/ThingDefs_Items/RM_HulduFur.xml", "RM_Leather_Huldu").find("graphicData")
    tex = fur.findtext("texPath") if fur is not None else None
    if tex != "Things/Item/Resource/RM_LeatherHuldu":
        bad.append(f"RM_Leather_Huldu texPath is {tex!r}")
    elif not (MOD / "Textures" / f"{tex}.png").is_file():
        bad.append("RM_Leather_Huldu icon PNG missing")
    # LeatherBase is Graphic_StackCount, which would read texPath as a folder.
    if fur is None or fur.findtext("graphicClass") != "Graphic_Single":
        bad.append("RM_Leather_Huldu must override graphicClass to Graphic_Single")

    ledger = installs()
    for n, old in OLD.items():
        png = MOD / f"Textures/Things/Item/Fish/RM_{n}Catch.png"
        cur = sha(png)
        if cur.startswith(old):
            bad.append(f"RM_{n}Catch is still the old gapall picture")
        if cur not in ledger:
            bad.append(f"RM_{n}Catch {cur[:12]} has no ledger event naming {ITEM}")
    if (MOD / "Textures/Things/Item/Fish/RM_IvvolCatch_east.png").exists():
        bad.append("stray RM_IvvolCatch_east.png: the catch is Graphic_Single, the game never reads it")
    if not sha(MOD / "Textures/Things/Item/RM_MurrinCatch.png").startswith(MURRIN_KEPT):
        bad.append("RM_MurrinCatch is no longer his kept picture")

    for b in bad:
        print("FAIL", b)
    print("ok" if not bad else f"{len(bad)} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
