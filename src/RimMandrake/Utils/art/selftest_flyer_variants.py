#!/usr/bin/env python3
"""selftest_flyer_variants.py — the owner's variant picks are alternate graphics (FLYER_VARIANTS_INSTALL_MORE_FACES_PLEASE).

Fleet Flier ("Use B, C, D as variants. They're beautiful!") and Murrelith ("B, C, D, E , F, G, H are all beautiful and
wonderful."). The letters are the columns of the snapshots he ruled on, since rebuilt with other letters; the shas below
are copied from those: fleetflier_alien snapshot at 2c3a7f10e3, flyer_north_redraw snapshot at 9a08e9fe3f.

For each creature, from parsed XML, the PNGs on disk and the art ledger:
  * the base graphic draws the main pick, one alternate per other letter, and nothing else;
  * alternateGraphicChance gives every picture the same share;
  * every facing is byte-equal to the column he ruled on;
  * every alternate's facing has a ledger install tied to a ruling carrying his words.
"""
from __future__ import annotations

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EVENTS = REPO / "infrastructure/state/art/events"
ANIMAL = "Things/Pawn/Animal"

CASES = [
    {"kind": "RM_FleetFlier", "mod": "src/RimMandrake/TheForge", "defs": "Defs/ThingDefs_Races/RM_FleetFlier.xml",
     "base": f"{ANIMAL}/RM_FleetFlier/RM_FleetFlier", "said": "Use B, C, D as variants",
     "main": {"south": "a51f796ab1a6", "east": "ca55948c3b70", "north": "ccd8b08dc4f5"},
     "alts": {"B": {"south": "45ce9cdb339e", "east": "88fdf28220e1", "north": "b70b4ee7347c"},
              "C": {"south": "1749a36dd973", "east": "ea1762ebba0c", "north": "978d2dafdaac"}}},
    {"kind": "RM_Murrelith", "mod": "src/RimMandrake/FeverWood", "defs": "Defs/ThingDefs_Races/RM_FeverWoodBirds.xml",
     "base": f"{ANIMAL}/RM_FeverWoodBirds/RM_Murrelith", "said": "are all beautiful and wonderful",
     "main": {"south": "0c867cabba1d", "east": "d27f262073e7", "north": "dc4f8d33a1d4"},
     "alts": {"C": {"south": "a229dad60388", "east": "641a15c1be9d", "north": "21cb2c25114c"},
              "D": {"south": "4cf8b40151e4", "east": "d72a08a2064b", "north": "384c97f7c94e"},
              "E": {"south": "f529f88240d4", "east": "12c76db6b423", "north": "62e4cf875a47"},
              "F": {"south": "5cf46eea6825", "east": "9cb5b19c17b1", "north": "21fdabcf883e"},
              "G": {"south": "5e3371935d6a", "east": "db1a170d870a", "north": "db899189ce25"},
              "H": {"south": "0bf1f96e97ca", "east": "4cf5bdffe576", "north": "8140e74b3c63"}}},
]


def ledger() -> tuple[dict, dict]:
    """({mod/rel: latest live event}, {ruling id: event}) from every seat's art events."""
    live, rulings = {}, {}
    for f in sorted(EVENTS.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("type") == "live":
                live[f"{e.get('mod')}/{e.get('rel')}"] = e
            if e.get("id"):
                rulings[e["id"]] = e
    return live, rulings


def check_case(c: dict, live: dict, rulings: dict) -> list[str]:
    bad = []
    kinds = [k for k in ET.parse(REPO / c["mod"] / c["defs"]).getroot().findall("PawnKindDef")
             if k.findtext("defName") == c["kind"]]
    if len(kinds) != 1:
        return [f"{c['kind']}: {len(kinds)} PawnKindDefs, want 1"]
    k = kinds[0]
    base_paths = {(g.findtext("texPath") or "").strip() for g in k.findall("lifeStages/li/bodyGraphicData")}
    if base_paths != {c["base"]}:
        bad.append(f"{c['kind']}: body texPaths {sorted(base_paths)}")
    want = {f"{c['base']}V_{letter}" for letter in c["alts"]}
    got = [(li.findtext("texPath") or "").strip() for li in k.findall("alternateGraphics/li")]
    if sorted(got) != sorted(want):
        bad.append(f"{c['kind']}: alternates {got}, want {sorted(want)}")
    n = len(c["alts"])
    chance = float(k.findtext("alternateGraphicChance") or -1)
    if abs(chance - n / (n + 1)) > 0.001:
        bad.append(f"{c['kind']}: chance {chance}, want {n}/{n + 1}")
    tex = REPO / c["mod"] / "Textures"
    for name, stem, shas in [("main", c["base"], c["main"])] + [(x, f"{c['base']}V_{x}", s) for x, s in c["alts"].items()]:
        for facing, want_sha in shas.items():
            rel = f"{stem}_{facing}.png"
            p = tex / rel
            if not p.is_file():
                bad.append(f"{c['kind']} {name}: missing {rel}")
                continue
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            if not sha.startswith(want_sha):
                bad.append(f"{c['kind']} {name} {facing}: {sha[:12]} is not the column he ruled on ({want_sha})")
            if name == "main":
                continue
            e = live.get(f"{c['mod']}/{rel}")
            if not e or e.get("sha") != sha:
                bad.append(f"{c['kind']} {name} {facing}: no ledger install of this sha")
            elif c["said"] not in json.dumps(rulings.get(e.get("ruling_id"), {})):
                bad.append(f"{c['kind']} {name} {facing}: ruling {e.get('ruling_id')} does not carry his words")
    return bad


def main() -> int:
    live, rulings = ledger()
    if not live or not rulings:
        print("FAIL: art ledger read empty, instrument blind")
        return 1
    bad = [b for c in CASES for b in check_case(c, live, rulings)]
    for b in bad:
        print("FAIL:", b)
    if bad:
        return 1
    print(f"selftest_flyer_variants: PASS ({sum(len(c['alts']) + 1 for c in CASES)} pictures, 2 creatures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
