"""WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1 - patch the frozen tiles CSV to match
the live fix already committed and verified via jawa/world_lint (count 181->0).
Same surgical-patch pattern as every prior restamp entry in
world/ASHKARR_WORLDMAP_tiles.csv.frozen.json: only biome/elev_m/water move on
exactly the 181 rows named in Transient/wble_fix_plan.json, nothing else.

Writes to a TEMP path first and diffs before touching the real CSV in place -
"patch a curated artifact, never re-allocate" (CLAUDE.md / a prior lesson).
"""
import csv, json, os, shutil

TILES_CSV = os.path.join("world", "ASHKARR_WORLDMAP_tiles.csv")
TMP_CSV = os.path.join("Transient", "wble_tiles_patched_TEMP.csv")

plan = json.load(open(os.path.join("Transient", "wble_fix_plan.json")))
twilight = set(plan["twilight"])
grey = set(plan["grey"])
damp2m = {957, 4924, 9784, 13026, 13027, 4161, 12269, 12271, 16042}
damp21m = {1446}

with open(TILES_CSV, encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

changed = []
for r in rows:
    t = int(r["tile"])
    old = dict(r)
    if t in twilight:
        r["biome"] = "RUT_TwilightSea"
    elif t in grey:
        r["biome"] = "RUT_GreySea"
    elif t in damp2m:
        r["elev_m"] = "2"
        r["water"] = "0"
    elif t in damp21m:
        r["elev_m"] = "21"
        r["water"] = "0"
    else:
        continue
    if r != old:
        changed.append((t, old, dict(r)))

print(f"rows that would change: {len(changed)} (expect 181)")
expected = twilight | grey | damp2m | damp21m
actual_changed_tiles = {c[0] for c in changed}
print("matches expected tile set exactly:", actual_changed_tiles == expected)
missing = expected - actual_changed_tiles
extra = actual_changed_tiles - expected
print("missing (expected but not changed):", missing)
print("extra (changed but not expected):", extra)

with open(TMP_CSV, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

# Full diff vs the ORIGINAL file: confirm ONLY these rows' bytes differ, by
# re-reading both and comparing every row, not just the ones we intended.
with open(TILES_CSV, encoding="utf-8", newline="") as f:
    orig_rows = list(csv.DictReader(f))
with open(TMP_CSV, encoding="utf-8", newline="") as f:
    new_rows = list(csv.DictReader(f))

assert len(orig_rows) == len(new_rows) == 21872, "row count changed!"
real_diff_tiles = set()
for o, n in zip(orig_rows, new_rows):
    if o != n:
        real_diff_tiles.add(int(o["tile"]))
print("REAL full-file diff tile count:", len(real_diff_tiles))
print("REAL diff matches expected set exactly:", real_diff_tiles == expected)

if real_diff_tiles == expected and len(orig_rows) == len(new_rows):
    shutil.copy(TMP_CSV, TILES_CSV)
    print("APPLIED: copied patched CSV over", TILES_CSV)
else:
    print("REFUSED to apply - diff did not match expectation. Inspect", TMP_CSV)
