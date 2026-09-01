import json, csv

DUMP = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/captures/2026-08-31T08-41-34Z"
OUT = "/mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/data/seas_waterline_manifest.csv"

d = json.load(open(DUMP + "/animals.json"))
ba = d["biomeAnimals"]

# defName -> source: sw (Star Wars Animal Collection, first-spawn/repatriate cast)
#                     borrowed (neighbor mods, Lane-1 license-cleared)
TARGETS = {
    "KwazelMaw": "sw", "Mott": "sw", "Dianoga": "sw", "Dragonsnake": "sw",
    "Fambaa": "sw", "Fanback": "sw", "Blixus": "sw",
    "BMT_MucklurkerCatfish": "borrowed", "BMT_TaintedTurtle": "borrowed",
    "BMT_MutatingTumorfishSpawn": "borrowed", "BMT_MutatingTumorfishFry": "borrowed",
    "BMT_MutatingTumorfishAdult": "borrowed",
    "Megasquid": "borrowed", "DA_LeviathanCrab": "borrowed",
}

by_animal = {}
for r in ba:
    race = r.get("race")
    if race in TARGETS:
        by_animal.setdefault(race, {})[r["biome"]] = r["commonalityDeclared"]

rows = []
for name, source in TARGETS.items():
    biomes = by_animal.get(name, {})
    base = max(biomes.values()) if biomes else 0.3
    new_lake = round(base * 0.75, 2)
    new_ocean = round(base * 0.4, 2)
    misplaced_biome = ""
    misplaced_old = ""
    if name == "KwazelMaw":
        misplaced_biome, misplaced_old = "ExtremeDesert", biomes.get("ExtremeDesert", "")
    elif name == "Mott":
        misplaced_biome, misplaced_old = "LavaField", biomes.get("LavaField", "")
    rows.append({
        "defName": name, "source": source,
        "existing_max_commonality": base,
        "Lake_present": "Lake" in biomes, "Lake_old": biomes.get("Lake", ""), "Lake_new": new_lake,
        "Ocean_present": "Ocean" in biomes, "Ocean_old": biomes.get("Ocean", ""), "Ocean_new": new_ocean,
        "misplaced_biome": misplaced_biome, "misplaced_old": misplaced_old,
    })

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)

print(f"{len(rows)} rows -> {OUT}")
for r in rows:
    print(r["defName"], "Lake", r["Lake_old"] or 0, "->", r["Lake_new"],
          "Ocean", r["Ocean_old"] or 0, "->", r["Ocean_new"],
          f"[{r['misplaced_biome']}={r['misplaced_old']}->0]" if r["misplaced_biome"] else "")
