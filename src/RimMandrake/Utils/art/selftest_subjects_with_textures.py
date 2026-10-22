#!/usr/bin/env python3
"""art_sheet --subjects + --textures: one look-over census holds the def rows AND the texture manifest's rows (C#-drawn
art with no def), the manifest rows keep their runtimeSize, and a key in both stays the def row (2026-10-21, all bridge art)."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402

fails = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


man = {"rows": [
    {"key": "T_Leaf", "label": "leaf", "part": "Leaf", "look": "Timber", "section": "T", "resources": ["Mod/T/Leaf"],
     "size": {"drawSize": [1.0, 2.0], "footprint": [1, 2], "source": "Leaf.cs:1"}},
    {"key": "RM_SuspensionDeck_Steel", "label": "dup", "part": "Deck", "look": "Steel", "section": "T",
     "resources": ["Mod/T/Dup"], "size": {"drawSize": [1, 1], "source": "Dup.cs:1"}}]}
with tempfile.TemporaryDirectory() as td:
    mp = Path(td) / "m.json"
    mp.write_text(json.dumps(man))
    old_out = A.BIOME_OUT
    A.BIOME_OUT = Path(td)
    try:
        cpath, key = A.subjects_with_textures("selftest_mix", mp, ["RM_SuspensionDeck_Steel"], label="Mix")
    finally:
        A.BIOME_OUT = old_out
    b = json.loads(Path(cpath).read_text())["biomes"][key]
    rows = {r["key"]: r for r in b["rows"]}
    check(set(rows) == {"RM_SuspensionDeck_Steel", "T_Leaf"}, "def row and manifest row both in one census")
    check(rows["RM_SuspensionDeck_Steel"]["defNames"] == ["RM_SuspensionDeck_Steel"], "a key in both stays the def row")
    check(rows["T_Leaf"]["runtimeSize"]["source"] == "Leaf.cs:1", "manifest row keeps its runtime size")
    check(b.get("textures_manifest", "").endswith("m.json"), "census records the manifest")
    check(key == "SUBJECTS_selftest_mix" and b["subjects"] is True, "one subjects census key")
sys.exit(1 if fails else 0)
