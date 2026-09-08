"""Re-derive every biome sheet's MEASURED block against the CANONICAL world.

Identifies each sheet's SUBJECT def self-calibratingly: the sheet states a tile
count in its opening measurement block; exactly one biome def in the DEPRECATED
CSV (the one it was measured against) has that count. That def is the subject.
Then reports what the same def looks like on the canonical planet. Read-only.
"""
import csv, collections, glob, os, re

REPO = "/mnt/d/Luke/dev/Rimworld"
canon = list(csv.DictReader(open(os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv"))))
depr = list(csv.DictReader(open(os.path.join(REPO, "world", "DEPRECATED_painted_lineage", "PAINTED_tiles.csv"))))
SHEETS = os.path.join(REPO, "design", "Jawa", "worldbuilding", "biomes")

CB, DB = collections.defaultdict(list), collections.defaultdict(list)
for r in canon:
    CB[r["biome"]].append(r)
for r in depr:
    DB[r["biome"]].append(r)
by_count = collections.defaultdict(list)
for d, rows in DB.items():
    by_count[len(rows)].append(d)


def stats(rows):
    if not rows:
        return None
    arc = sorted(float(r["arc"]) for r in rows)
    tmp = sorted(float(r["temp_c"]) for r in rows)
    return dict(n=len(rows), arc=(arc[0], arc[-1]), tmed=tmp[len(tmp) // 2],
                regions=collections.Counter(r["region"] for r in rows).most_common(3))


rows_out = []
for p in sorted(glob.glob(os.path.join(SHEETS, "*.md"))):
    name = os.path.basename(p)
    if name.startswith("_") or name.startswith("README"):
        continue
    head = "\n".join(open(p, encoding="utf-8").read().splitlines()[:60])
    claims = [int(m.replace(",", "")) for m in re.findall(r"\*?\*?([\d,]{3,7})\*?\*?\s+tiles", head)]
    subj, claimed = None, None
    for c in claims:                      # first claim that names exactly one deprecated def
        if len(by_count.get(c, [])) == 1:
            subj, claimed = by_count[c][0], c
            break
    rows_out.append((name, subj, claimed, claims[:3]))

print("=" * 96)
print("BIOME SHEETS vs THE CANONICAL WORLD  (subject def identified by the sheet's own tile count)")
print("=" * 96)

dead, moved, same, unid = [], [], [], []
for name, subj, claimed, claims in rows_out:
    if subj is None:
        unid.append((name, claims))
        continue
    c = len(CB.get(subj, []))
    (dead if c == 0 else (same if c == claimed else moved)).append((name, subj, claimed, c))

print("\n🔴 THE BIOME DOES NOT EXIST ON THE CANONICAL WORLD (%d sheets)" % len(dead))
print("   Every measurement, arc range, temperature and roster in these was reasoned")
print("   about tiles that were never on the planet the owner approved.\n")
for name, subj, cl, c in sorted(dead, key=lambda x: -x[2]):
    print("   %-24s %-22s sheet says %5d tiles   CANON HAS 0" % (name, subj, cl))

print("\n⚠️  THE BIOME EXISTS BUT THE POPULATION MOVED (%d sheets)\n" % len(moved))
for name, subj, cl, c in sorted(moved, key=lambda x: -abs(x[3] - x[2])):
    s = stats(CB[subj])
    print("   %-24s %-22s sheet %5d -> canon %5d  (%+d)" % (name, subj, cl, c, c - cl))
    print("        canon: arc %.0f-%.0f  temp med %.1f  regions %s"
          % (s["arc"][0], s["arc"][1], s["tmed"], ", ".join("%s %d" % kv for kv in s["regions"])))

print("\n✅ UNCHANGED — the sheet's own count still holds (%d)" % len(same))
for name, subj, cl, c in sorted(same, key=lambda x: -x[3]):
    print("   %-24s %-22s %d tiles" % (name, subj, c))

print("\n·  subject not identifiable from a tile count (%d): %s"
      % (len(unid), ", ".join(n for n, _ in unid)))
