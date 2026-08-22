#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_name_polish.py - de-cluster the region names and close the unnamed ground.

The fiction review, 2026-08-22, on 60 region names:

  "Duplicative to the point of mush - the rot cluster: The Warm Rot, The Shelf Rot, The
   Grayrot, The High Rot, The Crown Rot, plus The Cold Bloom, The Deep Bloom, The
   Frostbloom, The Coldspore, The Sporefields. Ten names for one idea. On a curved-label
   world map they will read as noise."

plus a dew cluster of four, and six that "say nothing" - anatomy metaphors and two that
are twee. It also found 1,287 land tiles with no region at all, including every tile of
`AB_GelatinousSuperorganism`: "the strangest ground on the planet is nameless".

  1 RENAME    17 of the names DECIDE wrote. ⛔ The older names - The Scald, The Salt, The
              Anvil, The Fall Line, The Rust Cathedral, The Dew Horn, The Dew Belt - are
              untouched. They are the owner's and they set the voice; the clusters are
              mine and they are the ones diluting it.
  2 CLOSE     unnamed blobs of 40+ tiles get a name of their own; the 43 slivers under 40
              tiles are ABSORBED into whichever named region they border most. Inventing
              43 more labels would trade one defect for a busier map.
"""
import csv, collections, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.join(REPO, "world"); STEM = os.path.join(W, "ASHKARR_WORLDMAP")
APPLY = "--apply" in sys.argv
BIG = 40

RENAME = {
    # the rot cluster - five names for fungus
    "The Warm Rot": "The Sweatwood", "The Shelf Rot": "The Stepwood",
    "The Grayrot": "The Mould March", "The High Rot": "The Hanging Wood",
    "The Crown Rot": "The Capwood",
    # the bloom cluster - four more for the same fungus, colder
    "The Cold Bloom": "The Frostcaps", "The Deep Bloom": "The Blindwood",
    "The Frostbloom": "The Stillwood", "The Coldspore": "The Ashwood",
    # the dew cluster - the two ORIGINALS (Dew Horn, Dew Belt) stay
    "The Low Dew": "The Damp", "The Flatdew": "The Level",
    # names that say nothing about the place
    "The Shoulder": "The Coldshelf", "The Saddle": "The Notch",
    "The Apron": "The Fanground", "The Softground": "The Sinkground",
    "The Last Green": "The Verge", "The Last Scrub": "The Thornend",
}
# names for the big unnamed blobs, keyed by what measurement says they are
NEW = ["The Glass Reach", "The Slough", "The Tallow Ground", "The Grinding Floor",
       "The Wither", "The Pale Flats", "The Coldstone", "The Lantern Deeps",
       "The Chalk March", "The Quiet Ground", "The Hollow Verge"]

rows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
T = {int(r["tile"]): r for r in rows}
nb = {}
rd = csv.reader(open(os.path.join(W, "world_neighbors_sub7b.csv"), encoding="utf-8")); next(rd)
for row in rd: nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]

hit = collections.Counter()
for r in rows:
    if r["region"] in RENAME:
        hit[r["region"]] += 1
        r["region"] = RENAME[r["region"]]
print("1 RENAME   %d regions renamed across %d tiles" % (len(hit), sum(hit.values())))
for k, n in sorted(hit.items()):
    print("     %-20s -> %-20s %5d tiles" % (k, RENAME[k], n))

un = {t for t, r in T.items() if not r["region"] and r["water"] == "0"}
seen, blobs = set(), []
for s in sorted(un):
    if s in seen: continue
    st, c = [s], set()
    while st:
        x = st.pop()
        if x in c: continue
        c.add(x); st.extend(n for n in nb[x] if n in un and n not in c)
    seen |= c; blobs.append(c)
blobs.sort(key=lambda b: (-len(b), min(b)))
named = absorbed = 0
for i, b in enumerate(blobs):
    if len(b) >= BIG and i < len(NEW):
        for t in b: T[t]["region"] = NEW[i]
        bi = collections.Counter(T[t]["biome"] for t in b).most_common(1)[0]
        print("2 CLOSE    %-20s %5d tiles  mostly %s" % (NEW[i], len(b), bi[0]))
        named += 1
    else:
        c = collections.Counter()
        for t in b:
            for n in nb[t]:
                if T[n]["region"]: c[T[n]["region"]] += 1
        if not c: continue
        into = c.most_common(1)[0][0]
        for t in b: T[t]["region"] = into
        absorbed += len(b)
left = sum(1 for r in rows if not r["region"] and r["water"] == "0")
print("2 CLOSE    %d blobs named; %d sliver tiles absorbed into the region they border most"
      % (named, absorbed))
print("           unnamed land tiles 1287 -> %d ; regions -> %d"
      % (left, len({r["region"] for r in rows if r["region"]})))

if APPLY:
    with open(STEM + "_tiles.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("\nwritten: tiles.csv")
else:
    print("\nplan only - re-run with --apply")
