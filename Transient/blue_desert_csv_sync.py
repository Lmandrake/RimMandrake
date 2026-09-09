"""BLUE_DESERT_WORLD_SWITCH_1 - sync world/ASHKARR_WORLDMAP_tiles.csv's biome
column to the live repaint already committed in-game (Transient/blue_desert_repaint.py,
world_commit succeeded, 1029/1029 written and read back as RUT_BlueDesert).

Targeted: only rows currently biome=="BiomeGRimond" (same filter the repaint
script used) flip to "RUT_BlueDesert". No other column touched, no other row
touched. Run with python3 from the repo root.
"""
import csv
import sys

PATH = "world/ASHKARR_WORLDMAP_tiles.csv"

with open(PATH, encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

changed = 0
for row in rows:
    if row["biome"] == "BiomeGRimond":
        row["biome"] = "RUT_BlueDesert"
        changed += 1

print("rows flipped:", changed)
if changed != 1029:
    print(f"EXPECTED 1029, GOT {changed} - aborting, no write.")
    sys.exit(1)

with open(PATH, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("wrote", PATH)
