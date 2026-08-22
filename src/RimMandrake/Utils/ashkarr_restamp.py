#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_restamp.py - make the bundle's own metadata true again.

Two files describe the planet and both had drifted a whole night behind it:

  meta.json     claimed `settlements: 72` against 120 rows, and 14 of its 24 feature
                blocks disagreed with the `region` column (The Anvil 642 vs 349). One
                feature, The Ashteeth, had zero tiles. 37 region names in the CSV were
                unknown to it.
  frozen.json   asserted "20,113 rows with rain_mm = 0"; there were 20,476. It carried
                NO HASH AND NO ROW COUNT - only prose - so nothing could ever have
                detected that it was stale. It was 16 hours behind the file it guards.

🔑 The freeze now carries `sha256` and `rows`. A freeze that cannot detect its own
staleness is not a guard, it is a comment - and this one asserted a number that had been
false for sixteen hours while reading as authoritative.
"""
import csv, hashlib, json, os, sys, collections
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.join(REPO, "world"); STEM = os.path.join(W, "ASHKARR_WORLDMAP")
APPLY = "--apply" in sys.argv
rows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
T = {int(r["tile"]): r for r in rows}
srows = list(csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8")))
lrows = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
links = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))[1:]

meta = json.load(open(STEM + "_meta.json", encoding="utf-8"))
regc = collections.Counter(r["region"] for r in rows if r["region"])
old_s, old_f = meta.get("settlements"), len(meta.get("features", []))
byname = {f["name"]: f for f in meta.get("features", [])}
feats, nid = [], 0
for name, n in regc.most_common():
    f = dict(byname.get(name, {}))
    f["id"] = nid; nid += 1
    f["name"] = name; f["tiles"] = n; f["mass"] = n
    ts = [t for t, r in T.items() if r["region"] == name]
    f["kind"] = "sea" if all(T[t]["water"] == "1" for t in ts) else f.get("kind", "region")
    f["lat"] = round(sum(float(T[t]["lat"]) for t in ts) / n, 4)
    f["lon"] = round(sum(float(T[t]["lon"]) for t in ts) / n, 4)
    feats.append(f)
meta["features"] = feats
meta["regions"] = [f["name"] for f in feats]
meta["settlements"] = len(srows)
meta["landmarks"] = len(lrows)
meta["riverLinks"] = sum(1 for r in links if r[0] == "river")
meta["roadLinks"] = sum(1 for r in links if r[0] == "road")
meta["water_pct"] = round(100.0 * sum(1 for r in rows if r["water"] == "1") / len(rows), 2)
meta["unnamedLandTiles"] = sum(1 for r in rows if not r["region"] and r["water"] == "0")
meta["factions"] = sorted({s["faction_def"] for s in srows})
meta["faction_labels"] = {s["faction_def"]: s["faction"] for s in srows}
st = T[int(meta["startingTile"])]
meta["start"] = {k: (int(st[k]) if k in ("tile", "elev_m") else st[k]) for k in
                 ("tile", "lat", "lon", "arc", "biome", "elev_m", "temp_c", "rain_mm")}
meta["start"]["name"] = "The Setdown"
print("meta.json  settlements %s -> %d | features %d -> %d | regions -> %d | "
      "landmarks -> %d | unnamed land -> %d"
      % (old_s, len(srows), old_f, len(feats), len(regc), len(lrows), meta["unnamedLandTiles"]))

blob = open(STEM + "_tiles.csv", "rb").read()
fz = json.load(open(STEM + "_tiles.csv.frozen.json", encoding="utf-8"))
dry = sum(1 for r in rows if float(r["rain_mm"]) == 0)
fz["sha256"] = hashlib.sha256(blob).hexdigest()
fz["rows"] = len(rows)
fz["bytes"] = len(blob)
fz["frozenOn"] = "2026-08-22"
fz["restampedWhy"] = ("Restamped 2026-08-22 after an independent audit found this file "
                      "16 hours stale and STRUCTURALLY UNABLE to notice: it asserted "
                      "'20,113 rows with rain_mm = 0' (actual at the time: 20,476) and "
                      "carried no hash and no row count, so the claim read as "
                      "authoritative while being false. sha256/rows/bytes are the fix - "
                      "a freeze that cannot detect its own staleness is a comment, not a guard.")
fz["dryRows"] = dry
print("frozen.json  sha256 %s... | rows %d | dry rows %d" % (fz["sha256"][:16], len(rows), dry))
if APPLY:
    json.dump(meta, open(STEM + "_meta.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    json.dump(fz, open(STEM + "_tiles.csv.frozen.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\nwritten: meta.json and the freeze fingerprint")
else:
    print("\nplan only - re-run with --apply")
