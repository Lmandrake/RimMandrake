"""Build <out>/page/data.json and items.json from the CSVs gen_matrix.py wrote into <out>; build_page.py embeds them.

    python3 build_data.py <out>      (gen_matrix.py runs it for you)
"""
import csv, json, datetime, os, sys
W = os.path.abspath(sys.argv[1]) + "/"
os.makedirs(W + "page", exist_ok=True)
rows = list(csv.DictReader(open(W + "draft_matrix.csv")))
cols = list(rows[0].keys())
breg = {r["biome"]: r for r in csv.DictReader(open(W + "biomes.csv"))}
inv = {r["id"]: r for r in csv.DictReader(open(W + "inventory.csv")) if r["kind"] == "mineral"}
reasons = {(r["biome"], r["column"]): r for r in csv.DictReader(open(W + "reasons.csv"))}
homes = {r["mineral"]: r for r in csv.DictReader(open(W + "mineral_homes.csv"))}
reach = list(csv.DictReader(open(W + "reach_summary.csv")))
changes = list(csv.DictReader(open(W + "column_changes.csv")))
stats = json.load(open(W + "stats.json"))
# family = the biome's highest allowed mountain share (mtn_pct_max): 50 or more, 20-49, under 20
FAM_ORDER = ["Mountain country (mountain share can reach 50-100%)", "Hills and uplands (mountain share can reach 20-40%)",
             "Flats and lowlands (mountain share 15% at most)",
             "Seas (each row includes its sea floor)", "Not on the painted map (kept, marked)"]
def fam(r):
    g = breg[r["biome"]]
    if g["kind"] in ("aftermath", "cave"): return FAM_ORDER[4]
    if g["kind"] == "sea": return FAM_ORDER[3]
    mx = float(r["mtn_pct_max"] or 0)
    return FAM_ORDER[0] if mx >= 50 else FAM_ORDER[1] if mx >= 20 else FAM_ORDER[2]
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
    except (TypeError, ValueError): return 0.0
biomes, values = [], {}
for r in rows:
    if r["biome"].startswith("SRC_"): continue
    g = breg[r["biome"]]
    biomes.append(dict(id=r["biome"], label=g["label"], family=fam(r), kind=g["kind"], mark=g["mark"], label_note=g["label_note"],
                       src_def=g["src_def"], mtn_min=r["mtn_pct_min"].strip(), mtn_max=r["mtn_pct_max"].strip(),
                       hilliness=r["hilliness_allowed"].strip(), has_iron=r["has_iron"], unique=r["signature_minerals_unique_here"],
                       pull=r["non_mineral_pull"], mountain_reason=r["mountain_reason"], d4_empty=g["d4_empty"] == "yes"))
    for c in columns:
        v = num(r[c["id"]])
        if v: values[r["biome"] + "|" + c["id"]] = v
assert len(biomes) == 29, len(biomes)
biomes.sort(key=lambda b: (FAM_ORDER.index(b["family"]), b["label"].lower().replace("the ", "")))
cells = {}
for (b, c), x in reasons.items():
    cells[b + "|" + c] = dict(reason=x["reason"], why_here=x["why_here"], why_not=x["why_not_elsewhere"], role=x["role"], form=x["form"],
                             channels=x["channels"], provenance=x["provenance"], unit=x["unit"], draft=x["draft"])
src = []
for r in rows:
    if not r["biome"].startswith("SRC_"): continue
    vals = {c: num(r[c]) for c in cols[cols.index("steel"):cols.index("mountain_reason")] if num(r[c])}
    src.append(dict(id=r["biome"], label=r["label"], values=vals, reasons={c: reasons.get((r["biome"], c), {}).get("reason", "") for c in vals}))
minerals = []
for c, ms in CLS.items():
    for m in ms:
        h = homes.get(m)
        minerals.append(dict(id=m, label=lab(m), group=c, home=h["home"] if h else "", second=h["second"] if h else "",
                             why_home=h["why_home"] if h else "Steel is the one broadly present metal (D2: about 10 per map in rocky biomes).",
                             why_second=h["why_second_or_none"] if h else "", defs=inv.get(m, {}).get("defNames", "")))
# one ITEMS entry per biome row, for the prereview record (prereview.py reads <script id="ITEMS">)
items = []
for b in biomes:
    nz = ["%s %g" % (c["id"], values[b["id"] + "|" + c["id"]]) for c in columns if b["id"] + "|" + c["id"] in values]
    items.append(dict(id=b["id"], label=b["label"], desc="; ".join(x for x in [b["kind"], b["family"], b["mark"], "D4 empty" if b["d4_empty"] else "",
                                                                          "cells: " + (", ".join(nz) or "none")] if x)))
data = dict(generated=datetime.datetime.now().isoformat(timespec="minutes"), round="rebuild on the painted map (2026-10-30)",
            ladder=[0, 0.03, 0.1, 0.3, 1, 2, 5, 10, 25, 99], deep_quick=[0, 5, 10, 15, 25, 50, 60],
            families=FAM_ORDER, groups=list(CLS) + ["Deep finds (% of deep-scanner finds; iron is the rest)", "River placers"],
            biomes=biomes, columns=columns, values=values, cells=cells, src=src, minerals=minerals, reach=reach, stats=stats, changes=changes)
json.dump(data, open(W + "page/data.json", "w"), indent=0, ensure_ascii=False)
json.dump(items, open(W + "page/items.json", "w"), indent=0, ensure_ascii=False)
print(len(biomes), "biomes", len(columns), "columns", len(values), "nonzero", len(cells), "reasons", len(src), "src rows", len(items), "items")
