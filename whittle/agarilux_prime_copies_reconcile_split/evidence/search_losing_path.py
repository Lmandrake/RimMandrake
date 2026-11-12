#!/usr/bin/env python3
"""Repo-wide search for the retired copies, after the change: every hit, classified.

Patterns: the old donor slot texPath, the two retired files' repo paths, and the gptredo_03 subject keys.
Scope: src/, infrastructure/ (art ledger, art-eval state, items, artpipe), design/, skills/. Ledger event shards and
whittle/ (this item's own record) are excluded. Each hit is classified by its path:
  LIVE-READER  -> a def, patch, code or live config that a tool or the game reads: must be zero
  APPEND-ONLY  -> art ledger events / run records / regen counters that are history by design (never edited)
  DATED-RECORD -> a dated sheet snapshot, ruling, design doc or closed item describing the state of its date
  THIS-CHANGE  -> the comment/script/item text written by this change, naming what was retired
  OTHER-DEF    -> names the slot or key but serves something else (the donor def AB_AgariluxPrime in Alpha Biomes'
                  own workshop folder; a docstring's example key format); each with its reason, checked by hand
Exit 1 if any LIVE-READER hit remains.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PATTERNS = [
    "Things/Plants/AB_AgariluxPrime",
    "TheRot/Textures/Things/Plants/AB_AgariluxPrime",
    "UtinniPatches/Textures/Things/Plants/AB_AgariluxPrime",
    "AgariluxPrime__UtinniPatches",
    "AgariluxPrime__TheRot",
]
SCOPE = ["src", "infrastructure", "design", "skills"]
THIS_CHANGE = {
    "src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml",   # the comment naming what was retired
    "src/RimMandrake/Utils/art/agarilux_prime_retire_copies.py",
    "infrastructure/state/items/AGARILUX_PRIME_COPIES_RECONCILE_SPLIT.md",
    "infrastructure/state/items/RIMMANDRAKE_RETIRE_ROT_DONOR_SLOT_COPIES_ELEVEN_SHADOWED.md",
    "infrastructure/state/items/RIMMANDRAKE_FIX_SLOT_SCAN_BLIND_TO_TEXPATH_PATCHES.md",
}
OTHER_DEF = {
    "design/Jawa/mods/plant_pool.csv": "row of the DONOR def AB_AgariluxPrime (Alpha Biomes), its own workshop texPath",
    "design/Jawa/mods/plant_sprites/manifest.json": "texture-resolver fixture: AB_AgariluxPrime's donor PNG in workshop 1841354677",
    "design/Jawa/worldbuilding/review/plant_register_rows.json": "plant register row defName AB_AgariluxPrime (donor def)",
    "src/RimMandrake/Utils/art_eval/shadow.py": "docstring example of the <def>__<tag> card-key format, not a path",
    "design/RimMandrake/texregen_unproven_roster_snapshot.json": "derived census snapshot (git_head e87f41b812); --check "
        "re-resolves each row NOW and passes after the retire (evidence/unproven_adjudicate_check.txt)",
}
APPEND_ONLY = [r"^infrastructure/state/ledger/events/", r"^infrastructure/state/art/events/", r"^infrastructure/state/art_eval/runs/",
               r"^infrastructure/state/art_eval/regen_rounds\.json$", r"^infrastructure/state/delegated/\d{4}-\d\d-\d\d/",
               r"^infrastructure/state/art/snapshots/"]
DATED = [r"_20\d\d-\d\d-\d\d", r"/20\d\d-\d\d-\d\d_", r"^infrastructure/state/items/closed/", r"\.snapshot\.json$",
         r"^infrastructure/state/art_rulings/"]


def classify(path: str, line: str) -> str:
    if path in THIS_CHANGE:
        return "THIS-CHANGE"
    if path in OTHER_DEF:
        return "OTHER-DEF"
    if any(re.search(p, path) for p in APPEND_ONLY):
        return "APPEND-ONLY"
    if any(re.search(p, path) for p in DATED):
        return "DATED-RECORD"
    return "LIVE-READER"


def main() -> int:
    args = ["git", "-C", str(REPO), "grep", "-n", "-I", "-F"]
    for p in PATTERNS:
        args += ["-e", p]
    args += ["--"] + SCOPE
    out = subprocess.run(args, capture_output=True, text=True, timeout=300).stdout.splitlines()
    rows = []
    for ln in out:
        path, _, rest = ln.partition(":")
        num, _, text = rest.partition(":")
        rows.append((classify(path, text), path, num, text.strip()[:160]))
    by = {}
    for c, p, n, t in rows:
        by.setdefault(c, {}).setdefault(p, []).append((n, t))
    print(f"patterns: {PATTERNS}\nscope: {SCOPE} (git grep over tracked files at HEAD worktree)\n")
    for c in ("LIVE-READER", "THIS-CHANGE", "OTHER-DEF", "DATED-RECORD", "APPEND-ONLY"):
        files = by.get(c, {})
        print(f"== {c}: {sum(len(v) for v in files.values())} hit(s) in {len(files)} file(s)")
        for p, hits in sorted(files.items()):
            print(f"   {p}  ({len(hits)})" + (f"  -- {OTHER_DEF[p]}" if c == "OTHER-DEF" else ""))
            if c in ("LIVE-READER", "THIS-CHANGE", "OTHER-DEF"):
                for n, t in hits:
                    print(f"      {n}: {t}")
    # sanity probe: the same instrument must find the survivor's path
    probe = subprocess.run(["git", "-C", str(REPO), "grep", "-c", "-F", "RotSpecies/AgariluxPrime", "--", "src"],
                           capture_output=True, text=True, timeout=120).stdout.strip()
    print(f"\nsanity probe: git grep 'RotSpecies/AgariluxPrime' in src/ -> {probe or 'NOTHING (instrument blind)'}")
    files_on_disk = sorted(str(p.relative_to(REPO)) for p in (REPO / "src").glob("*/*/Textures/**/*AgariluxPrime*.png"))
    print(f"PNG files named *AgariluxPrime* under src/*/*/Textures: {files_on_disk}")
    live = by.get("LIVE-READER", {})
    print(f"\nVERDICT: {'no live reader names a retired copy' if not live else 'LIVE READERS REMAIN'}")
    return 1 if live else 0


if __name__ == "__main__":
    sys.exit(main())
