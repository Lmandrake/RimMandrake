"""Build page/data.json from the round-two CSVs; build_page.py embeds it into index.html."""
import csv, json, datetime
W = "/mnt/d/ClaudeWork/rimmandrake/mineral_matrix_2026-10-28/"
rows = list(csv.DictReader(open(W + "draft_matrix_v2.csv")))
cols = list(rows[0].keys())
inv = {r["id"]: r for r in csv.DictReader(open(W + "inventory.csv")) if r["kind"] == "mineral"}
reasons = {(r["biome"], r["column"]): r for r in csv.DictReader(open(W + "reasons_v2.csv"))}
homes = {r["mineral"]: r for r in csv.DictReader(open(W + "mineral_homes_v2.csv"))}
reach = list(csv.DictReader(open(W + "reach/reach_summary.csv")))
stats = json.load(open(W + "v2_stats.json"))
D4 = ["RM_Abyss", "RM_FeverWood", "RM_GelatinousSlime", "RM_Greentide", "RM_LeaningScrub", "RM_LongShade", "RM_Miasma",
      "RM_Pyrelands", "RM_TheRot", "RM_Webwork", "RM_TheScald", "RM_TwilightSea", "RM_SeabedFloor_TwilightSea",
      "RM_SeabedFloor_TheChill", "RUT_AridShrubland"]
SEAS = ["RM_GreySea", "RM_TheChill", "RM_TheScald", "RM_TwilightSea"]
def fam(r):
    b = r["biome"]
    if b == "OTHER_vanilla": return "Elsewhere"
    if b in SEAS: return "Sea surfaces"
    if b.startswith("RM_SeabedFloor_"): return "Sea floors (dive maps)"
    if b == "RM_LanternDeeps": return "Underground"
    mx = float(r["mtn_pct_max"] or 0)
    if mx >= 50: return "Mountain country (up to 50-100% mountain)"
    if mx >= 20: return "Hills and uplands (up to 20-40%)"
    return "Flats and lowlands (up to 15%)"
FAM_ORDER = ["Mountain country (up to 50-100% mountain)", "Hills and uplands (up to 20-40%)", "Flats and lowlands (up to 15%)",
             "Sea surfaces", "Sea floors (dive maps)", "Underground", "Elsewhere"]
CLS = {"Metals": ["steel", "gold", "silver", "uranium", "chimney_iron", "magnetite", "uraninite", "zersium", "phrikite", "live_pattern_metal", "dead_smartsteel"],
       "Gems and crystals": ["jade", "diamond", "ruby", "sapphire", "pyrinth", "kyber", "stygium", "mindstone", "cave_crystal", "scaldpearl"],
       "Stone, glass and ice": ["obsidian", "lanternstone", "sand", "fossils", "blue_ice"],
       "Salts and residues": ["crystal_salts", "cooking_salt", "brine_plate", "bezoars"],
       "Fuels": ["deepchem", "helixien"]}
planet = cols[cols.index("steel"):cols.index("DEEP_gold")]
assert sorted(sum(CLS.values(), [])) == sorted(planet), set(planet) ^ set(sum(CLS.values(), []))
def lab(m): return (inv.get(m, {}).get("label") or m).split(" (")[0]
columns = []
for c, ms in CLS.items():
    for m in ms: columns.append(dict(id=m, mineral=m, group=c, label=lab(m), unit="DPM"))
for c in cols:
    if c.startswith("DEEP_"): columns.append(dict(id=c, mineral=c[5:], group="Deep finds (% of deep-scanner finds; iron is the rest)", label=lab(c[5:]), unit="%"))
for c in cols:
    if c.startswith("RIVER_"): columns.append(dict(id=c, mineral=c[6:], group="River placers", label=lab(c[6:]), unit="DPM"))
def num(v):
    try: return float(v)
    except: return 0.0
biomes, values = [], {}
for r in rows:
    if r["biome"].startswith("SRC_"): continue
    biomes.append(dict(id=r["biome"], label=r["label"], family=fam(r), mtn_min=r["mtn_pct_min"].strip(), mtn_max=r["mtn_pct_max"].strip(),
                       hilliness=r["hilliness_allowed"].strip(), has_iron=r["has_iron"], unique=r["signature_minerals_unique_here"],
                       pull=r["non_mineral_pull"], mountain_reason=r["mountain_reason"], d4_empty=r["biome"] in D4))
    for c in columns:
        v = num(r[c["id"]])
        if v: values[r["biome"] + "|" + c["id"]] = v
biomes.sort(key=lambda b: (FAM_ORDER.index(b["family"]), b["label"].lower().replace("the ", "")))
cells = {}
for (b, c), x in reasons.items():
    cells[b + "|" + c] = dict(reason=x["reason"], why_here=x["why_here"], why_not=x["why_not_elsewhere"], role=x["role"],
                             form=x["form"], channels=x["channels"], provenance=x["provenance"], unit=x["unit"])
src = []
for r in rows:
    if not r["biome"].startswith("SRC_"): continue
    vals = {c: num(r[c]) for c in cols[cols.index("steel"):cols.index("mountain_reason")] if num(r[c])}
    src.append(dict(id=r["biome"], label=r["label"], values=vals,
                    reasons={c: reasons.get((r["biome"], c), {}).get("reason", "") for c in vals}))
minerals = []
for c, ms in CLS.items():
    for m in ms:
        h = homes.get(m)
        minerals.append(dict(id=m, label=lab(m), group=c, home=h["home"] if h else "", second=h["second"] if h else "",
                             why_home=h["why_home"] if h else "Steel is the one broadly present metal (D2: about 10 per map in rocky biomes).",
                             why_second=h["why_second_or_none"] if h else "", defs=inv.get(m, {}).get("defNames", "")))
data = dict(generated=datetime.datetime.now().isoformat(timespec="minutes"), round="two (D3: a home plus one minor second biome)",
            ladder=[0, 0.03, 0.1, 0.3, 1, 2, 5, 10, 25, 99], deep_quick=[0, 5, 10, 15, 25, 50, 60],
            families=FAM_ORDER, groups=list(CLS) + ["Deep finds (% of deep-scanner finds; iron is the rest)", "River placers"],
            biomes=biomes, columns=columns, values=values, cells=cells, src=src, minerals=minerals, reach=reach, stats=stats)
json.dump(data, open(W + "page/data.json", "w"), indent=0, ensure_ascii=False)
print(len(biomes), "biomes", len(columns), "columns", len(values), "nonzero", len(cells), "reasons", len(src), "src rows")
