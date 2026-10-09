#!/usr/bin/env python3
"""Exotic materials census: every resource/material ThingDef our own content (src/) defines,
with who produces it (creature / plant / mineral / comp), which mod and biome(s), its stats,
and who consumes it (recipes, costLists, fuel filters, stuff consumers, C# string refs).

Analysis only; writes a CSV and prints coverage + sanity probes. Re-run:
    python3 src/RimMandrake/Utils/exotic_materials_census.py [--csv OUT.csv]

Rules it applies (see design/RimMandrake/exotic_materials_census_2026-10-09.md):
- A ThingDef is a MATERIAL if it has stuffProps, a material-ish thingCategory, a resource-ish
  ParentName ancestor, or is named by a producer field (leatherDef, butcherProducts, meatDef,
  harvestedThingDef, mineableThing, or a producing CompProperties).
- ParentName is resolved across all of src/ (child overrides, <li> lists append unless
  Inherit="False"); a Core/donor parent that is not in src/ is kept as an unresolved hint.
- <wildAnimals>/<wildPlants> are read as ELEMENT NAMES (BiomeAnimalRecord custom loader), never
  by counting <li>; patch-added rosters are attributed from the PatchOperation's own xpath.
"""
import argparse, collections, copy, csv, os, re, sys
from lxml import etree

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(REPO, "src")

MAT_CATS = {"Leathers", "Textiles", "StoneChunks", "ResourcesRaw", "Manufactured", "AnimalProductRaw",
            "StoneBlocks", "PlantMatter", "Wools", "RawMaterials", "Chunks", "MetallicStuff",
            "ResourcesMedicine", "Drugs", "PlantFoodRaw", "MeatRaw", "EggsUnfertilized",
            "EggsFertilized", "Fish", "Medicine", "Resources", "Items"}
MAT_PARENT_HINTS = re.compile(r"(Resource|Leather|Wool|Fabric|Textile|Chunk|StoneBlock|Meat|Egg|"
                              r"OrganicProduct|PlantFoodRaw|Fish|Drug|Silk|Ore|Ingot|Crystal|Gem|Gland|"
                              r"Resin|Sap|Oil|Chitin|Shell)", re.I)
NOT_MAT_PARENT = re.compile(r"(Mote|Bullet|Projectile|Filth|Gas|Plant(Base|Food)?$|Building|Weapon|"
                            r"Apparel|Pawn|Animal|Research|Terrain|Mineable)", re.I)
# Core/vanilla abstract parents that are not in src/: what they imply (categories, stuffCategories).
CORE_PARENTS = {
    "LeatherBase": (["Leathers"], ["Leathery"]), "WoolBase": (["Wools"], ["Fabric"]),
    "FishBase": (["Fish"], []), "EggUnfertBase": (["EggsUnfertilized"], []),
    "EggFertBase": (["EggsFertilized"], []), "ChunkRockBase": (["StoneChunks"], []),
    "StoneBlocksBase": (["StoneBlocks"], ["Stony"]), "MeatBase": (["MeatRaw"], []),
    "PlantFoodRawBase": (["PlantFoodRaw"], []), "OrganicProductBase": (["AnimalProductRaw"], []),
}
CORE_STUFF = {"Metallic", "Woody", "Stony", "Fabric", "Leathery"}   # consumed by Core apparel/buildings
NOT_MATERIAL_CATS = {"guy762_weaponmod", "guy762_implants", "BodyPartsArtificial", "BodyPartsNatural",
                     "Weapons", "Apparel", "Artifacts", "ItemsMisc", "InertRelics"}
PRODUCER_COMP = re.compile(r"(Milk|Shear|Egg|Spawn|Harvest|Gather|Yield|Produc|Leav|Drop)", re.I)

parser_x = etree.XMLParser(recover=True, remove_comments=True, huge_tree=True)


def mod_of(path):
    rel = os.path.relpath(path, SRC).split(os.sep)
    return "/".join(rel[:2]) if len(rel) > 2 else rel[0]


def txt(e):
    return (e.text or "").strip() if e is not None else ""


# ---------------------------------------------------------------- load
defs = {}            # (DefType, defName) -> element
by_name = {}         # Name attr -> element (abstract or not)
def_path = {}
patch_files = []
xml_files = []
for root, dirs, files in os.walk(SRC):
    dirs[:] = [d for d in dirs if d not in (".git", "obj", "bin", "__pycache__", "node_modules")]
    for f in files:
        if f.endswith(".xml"):
            xml_files.append(os.path.join(root, f))

parse_fail = []
docs = {}
for p in xml_files:
    try:
        t = etree.parse(p, parser_x)
    except Exception as ex:  # noqa
        parse_fail.append(p)
        continue
    r = t.getroot()
    if r is None:
        parse_fail.append(p)
        continue
    docs[p] = r
    if r.tag == "Patch":
        patch_files.append(p)
        continue
    if r.tag != "Defs":
        continue
    for d in r:
        if not isinstance(d.tag, str):
            continue
        nm = d.get("Name")
        if nm:
            by_name[nm] = (d, p)
        dn = txt(d.find("defName"))
        if dn and d.get("Abstract", "").lower() != "true":
            defs[(d.tag, dn)] = d
            def_path[(d.tag, dn)] = p


def merge(parent, child):
    out = copy.deepcopy(parent)
    for k in ("Abstract", "Name"):
        if k in out.attrib:
            del out.attrib[k]
    for k, v in child.attrib.items():
        out.set(k, v)
    if child.get("Inherit", "").lower() == "false":
        return copy.deepcopy(child)
    ckids = [c for c in child if isinstance(c.tag, str)]
    if not ckids:
        out.text = child.text
        for c in list(out):
            out.remove(c)
        return out
    if all(c.tag == "li" for c in ckids):
        for c in ckids:
            out.append(copy.deepcopy(c))
        return out
    for c in ckids:
        ex = out.find(c.tag)
        if ex is not None and c.tag != "li":
            out.replace(ex, merge(ex, c))
        else:
            out.append(copy.deepcopy(c))
    return out


resolved_cache = {}


def resolve(el, depth=0):
    """Return (merged element, list of unresolved parent names in chain, chain)."""
    key = id(el)
    if key in resolved_cache:
        return resolved_cache[key]
    pn = el.get("ParentName")
    if not pn or depth > 20:
        res = (el, [], [])
    elif pn in by_name:
        pel, _ = by_name[pn]
        pm, unres, chain = resolve(pel, depth + 1)
        res = (merge(pm, el), unres, [pn] + chain)
    else:
        res = (el, [pn], [pn])
    resolved_cache[key] = res
    return res


thing = {}
for (tp, dn), el in defs.items():
    if tp == "ThingDef":
        thing[dn] = resolve(el)
ALL_THING = set(thing)

# ---------------------------------------------------------------- producers
prod = collections.defaultdict(list)   # material defName -> [(kind, sourceDefName, how)]
external_prod = collections.Counter()  # products that are not our defs (Core/donor) -> count

def add_prod(mat, kind, src, how):
    if not mat:
        return
    if mat in ALL_THING:
        prod[mat].append((kind, src, how))
    else:
        external_prod[mat] += 1


def kind_of(m):
    cls = txt(m.find("thingClass"))
    if m.find("race") is not None:
        return "creature"
    if m.find("plant") is not None or "Plant" in cls:
        return "plant"
    if m.find("building") is not None or txt(m.find("category")) == "Building":
        return "mineral" if m.find("building/mineableThing") is not None else "building"
    return "item"


for dn, (m, unres, chain) in thing.items():
    k = kind_of(m)
    race = m.find("race")
    if race is not None:
        add_prod(txt(race.find("leatherDef")), "creature", dn, "leather")
        add_prod(txt(race.find("meatDef")), "creature", dn, "meat")
    bp = m.find("butcherProducts")
    if bp is not None:
        for c in bp:
            if isinstance(c.tag, str):
                add_prod(c.tag if c.tag != "li" else txt(c.find("thingDef")), k, dn, "butcher")
    kl = m.find("killedLeavings")
    if kl is not None:
        for c in kl:
            if isinstance(c.tag, str):
                add_prod(c.tag, k, dn, "killedLeavings")
    pl = m.find("plant")
    if pl is not None:
        add_prod(txt(pl.find("harvestedThingDef")), "plant", dn, "harvest")
    b = m.find("building")
    if b is not None:
        add_prod(txt(b.find("mineableThing")), "mineral", dn, "mined")
    comps = m.find("comps")
    if comps is not None:
        for li in comps:
            cls = li.get("Class", "")
            if not PRODUCER_COMP.search(cls):
                continue
            for e in li.iter():
                if e is li or not isinstance(e.tag, str):
                    continue
                v = txt(e)
                if v in ALL_THING and v != dn:
                    add_prod(v, k, dn, cls.split(".")[-1].replace("CompProperties_", "comp:"))
# producing comps on non-ThingDefs (hediffs etc.) and any def-level field named *ThingDef/thingDef
# in recipe-less contexts are not producers; deliberately skipped.

# ---------------------------------------------------------------- biome attribution
biome_of_src = collections.defaultdict(set)  # source defName -> biomes
biome_defs = {dn for (tp, dn) in defs if tp == "BiomeDef"}
for (tp, dn), el in defs.items():
    if tp != "BiomeDef":
        continue
    m, _, _ = resolve(el)
    for sect in ("wildAnimals", "wildPlants", "pollutionWildAnimals", "coastalWildAnimals"):
        s = m.find(sect)
        if s is None:
            continue
        for c in s:
            if not isinstance(c.tag, str):
                continue
            nm = c.tag if c.tag != "li" else (txt(c.find("animal")) or txt(c.find("plant")))
            biome_of_src[nm].add(dn)
    for s in ("fishTypes",):
        node = m.find(s)
        if node is not None:
            for c in node.iter():
                v = txt(c) if isinstance(c.tag, str) and len(c) == 0 else ""
                if v in ALL_THING:
                    biome_of_src[v].add(dn)
                elif isinstance(c.tag, str) and c.tag in ALL_THING:
                    biome_of_src[c.tag].add(dn)
    # any mineable / scatter named anywhere inside the biome def
    for e in m.iter():
        if isinstance(e.tag, str) and len(e) == 0:
            v = txt(e)
            if v in ALL_THING and kind_of(thing[v][0]) == "mineral":
                biome_of_src[v].add(dn)

BIOME_XP = re.compile(r'BiomeDef\[defName\s*=\s*"([^"]+)"\]')
for p in patch_files:
    r = docs[p]
    for op in r.iter():
        if not isinstance(op.tag, str):
            continue
        xp = op.find("xpath")
        val = op.find("value")
        if xp is None or val is None:
            continue
        bs = BIOME_XP.findall(txt(xp))
        if not bs:
            continue
        for e in val.iter():
            if not isinstance(e.tag, str):
                continue
            for cand in (e.tag, txt(e) if len(e) == 0 else ""):
                if cand in ALL_THING:
                    for bname in bs:
                        biome_of_src[cand].add(bname)

# GenStep / scatter defs naming a mineable: attribute to the GenStep (biome unknown)
for (tp, dn), el in defs.items():
    if tp in ("GenStepDef", "MapGeneratorDef"):
        for e in el.iter():
            if isinstance(e.tag, str) and len(e) == 0 and txt(e) in ALL_THING:
                v = txt(e)
                if kind_of(thing[v][0]) == "mineral" and not biome_of_src[v]:
                    biome_of_src[v].add("genstep:" + dn)

# ---------------------------------------------------------------- consumers
uses = collections.defaultdict(list)   # material -> [(kind, consumerDef)]
cat_uses = collections.defaultdict(set)   # thingCategory -> consumers (recipe filters)
stuffcat_consumers = collections.Counter()  # stuffCategory -> number of defs accepting it


def filter_defs(f):
    out, cats = [], []
    if f is None:
        return out, cats
    for li in f.findall("thingDefs/li"):
        out.append(txt(li))
    for li in f.findall("categories/li"):
        cats.append(txt(li))
    return out, cats


for (tp, dn), el in defs.items():
    m, _, _ = resolve(el) if tp == "ThingDef" else (el, [], [])
    if tp == "RecipeDef":
        for ing in m.findall("ingredients/li"):
            ds, cs = filter_defs(ing.find("filter"))
            for d in ds:
                uses[d].append(("recipe", dn))
            for c in cs:
                cat_uses[c].add(dn)
            td = txt(ing.find("thingDef"))
            if td:
                uses[td].append(("recipe", dn))
        ds, cs = filter_defs(m.find("fixedIngredientFilter"))
        for d in ds:
            if ("recipe", dn) not in uses[d]:
                uses[d].append(("recipe-filter", dn))
    for cl in ("costList", "costListForDifficulty/costList"):
        c = m.find(cl)
        if c is not None:
            for e in c:
                if isinstance(e.tag, str):
                    uses[e.tag].append(("costList", dn))
    for sc in m.findall("stuffCategories/li"):
        stuffcat_consumers[txt(sc)] += 1
    comps = m.find("comps")
    if comps is not None:
        for li in comps:
            if "Refuel" in li.get("Class", "") or "Fuel" in li.get("Class", ""):
                ds, cs = filter_defs(li.find("fuelFilter"))
                for d in ds:
                    uses[d].append(("fuel", dn))
            for tag in ("ammoDef", "ammoFilter"):
                pass

# recipes added by patches (costList / ingredients inserted into existing defs)
for p in patch_files:
    r = docs[p]
    for op in r.iter():
        if not isinstance(op.tag, str):
            continue
        xp, val = op.find("xpath"), op.find("value")
        if xp is None or val is None:
            continue
        x = txt(xp)
        m_ = re.search(r'defName\s*=\s*"([^"]+)"', x)
        tgt = m_.group(1) if m_ else os.path.basename(p)
        if "costList" in x:
            for e in val.iter():
                if isinstance(e.tag, str) and e.tag in ALL_THING:
                    uses[e.tag].append(("patch-costList", tgt))
        for e in val.iter():
            if isinstance(e.tag, str) and e.tag == "costList":
                for c in e:
                    if isinstance(c.tag, str):
                        uses[c.tag].append(("patch-costList", tgt))
            if isinstance(e.tag, str) and e.tag in ("ingredients", "fixedIngredientFilter", "thingDefs") \
                    and ("Recipe" in x or "ingredients" in x or "Filter" in x.lower()):
                for li in e.iter("li"):
                    if txt(li) in ALL_THING:
                        uses[txt(li)].append(("patch-recipe", tgt))
                for li in e.iter("thingDef"):
                    if txt(li) in ALL_THING:
                        uses[txt(li)].append(("patch-recipe", tgt))
        if "costList" not in x and ("ingredients" in x or "Recipe" in x):
            for e in val.iter():
                if isinstance(e.tag, str) and len(e) == 0 and txt(e) in ALL_THING:
                    uses[txt(e)].append(("patch-recipe", tgt))

# C# string references (reflection / DefDatabase lookups)
cs_text = []
for root, dirs, files in os.walk(SRC):
    dirs[:] = [d for d in dirs if d not in ("obj", "bin")]
    for f in files:
        if f.endswith(".cs"):
            try:
                cs_text.append(open(os.path.join(root, f), encoding="utf-8", errors="ignore").read())
            except OSError:
                pass
CS_BLOB = "\n".join(cs_text)

# generic mention count across all xml (other than its own def and producers) -- trader stock etc.
XML_TOKENS = collections.Counter()
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
for p in xml_files:
    try:
        XML_TOKENS.update(TOKEN.findall(open(p, encoding="utf-8", errors="ignore").read()))
    except OSError:
        pass
CS_TOKENS = collections.Counter(TOKEN.findall(CS_BLOB))

# ---------------------------------------------------------------- select materials
ROWS = []


def stat(m, name):
    for path in ("statBases/" + name,):
        v = txt(m.find(path))
        if v:
            return v
    return ""


def cats(m):
    return [txt(li) for li in m.findall("thingCategories/li")]


for dn, (m, unres, chain) in thing.items():
    k = kind_of(m)
    if k in ("creature", "plant", "building", "mineral"):
        continue
    if m.get("Abstract", "").lower() == "true":
        continue
    tc = cats(m)
    core_stuff = []
    for pnm in chain:
        if pnm in CORE_PARENTS:
            tc = tc or CORE_PARENTS[pnm][0]
            core_stuff = CORE_PARENTS[pnm][1]
    if set(tc) & NOT_MATERIAL_CATS and dn not in prod:
        continue
    # manufactured parts, liquid containers and prepared foods are not raw materials unless nature
    # produces them or they are a stuff
    if set(tc) & {"Manufactured", "RM_LiquidBottleItems", "Foods", "RM_HazardCasks"} and dn not in prod \
            and m.find("stuffProps") is None:
        continue
    has_stuff = m.find("stuffProps") is not None
    parent_hit = any(MAT_PARENT_HINTS.search(c) and not NOT_MAT_PARENT.search(c) for c in chain)
    produced = dn in prod
    reason = []
    if has_stuff: reason.append("stuffProps")
    if set(tc) & MAT_CATS: reason.append("category")
    if parent_hit: reason.append("parent")
    if produced: reason.append("produced")
    if not reason:
        continue
    # exclude weapons/apparel/buildings/pawn things even if they sit in a broad category
    if m.find("apparel") is not None or m.find("verbs") is not None and m.find("weaponTags") is not None:
        continue
    if txt(m.find("category")) not in ("", "Item"):
        continue
    sp = m.find("stuffProps")
    stuffcats = [txt(li) for li in sp.findall("categories/li")] if sp is not None else []
    stuffcats = stuffcats or core_stuff
    sf = {}
    if sp is not None:
        for e in sp.findall("statFactors/*"):
            sf[e.tag] = txt(e)
    srcs = prod.get(dn, [])
    biomes = set(biome_of_src.get(dn, set()))
    for kd, s, how in srcs:
        biomes |= biome_of_src.get(s, set())
    u = uses.get(dn, [])
    cat_u = sorted({r for c in tc for r in cat_uses.get(c, ())})
    stuff_u = sum(stuffcat_consumers.get(c, 0) for c in stuffcats) + (1000 if set(stuffcats) & CORE_STUFF else 0)
    cs_refs = CS_TOKENS.get(dn, 0)
    own_path = def_path.get(("ThingDef", dn), "")
    # every xml mention minus its own defName line and one per producer link
    other_xml = max(0, XML_TOKENS.get(dn, 0) - 1 - len(srcs))
    ing = m.find("ingestible")
    food = txt(ing.find("foodType")) if ing is not None else ""
    drug = txt(ing.find("drugCategory")) if ing is not None else ""
    ROWS.append({
        "defName": dn,
        "label": txt(m.find("label")),
        "description": re.sub(r"\s+", " ", txt(m.find("description")))[:400],
        "mod": mod_of(own_path),
        "parent_chain": ">".join(chain),
        "reason": "+".join(reason),
        "thingCategories": ";".join(tc),
        "stuffCategories": ";".join(stuffcats),
        "MarketValue": stat(m, "MarketValue"),
        "Mass": stat(m, "Mass"),
        "Armor_Sharp": stat(m, "StuffPower_Armor_Sharp"),
        "Armor_Blunt": stat(m, "StuffPower_Armor_Blunt"),
        "Armor_Heat": stat(m, "StuffPower_Armor_Heat"),
        "Insul_Cold": stat(m, "StuffPower_Insulation_Cold"),
        "Insul_Heat": stat(m, "StuffPower_Insulation_Heat"),
        "SharpDmg": stat(m, "SharpDamageMultiplier"),
        "BluntDmg": stat(m, "BluntDamageMultiplier"),
        "Flammability": stat(m, "Flammability"),
        "stuff_statFactors": ";".join("%s=%s" % kv for kv in sorted(sf.items())),
        "ingestible": (food + ("/drug:" + drug if drug else "")) if ing is not None else "",
        "source_kind": ";".join(sorted({kd for kd, _, _ in srcs})),
        "sources": ";".join(sorted({"%s(%s)" % (s, how) for _, s, how in srcs}))[:500],
        "biomes": ";".join(sorted(biomes)),
        "uses_recipe": ";".join(sorted({c for kd, c in u if "recipe" in kd}))[:400],
        "uses_cost": ";".join(sorted({c for kd, c in u if "cost" in kd.lower()}))[:400],
        "uses_fuel": ";".join(sorted({c for kd, c in u if kd == "fuel"})),
        "uses_category_recipes": len(cat_u),
        "uses_stuff_consumers": stuff_u,
        "cs_refs": cs_refs,
        "other_xml_mentions": other_xml,
    })

CLUSTER_RULES = [
    ("food-only", lambda r, t: r["ingestible"] and "drug" not in r["ingestible"] and not r["stuffCategories"]
        and re.search(r"\b(meat|egg|milk|fish|catch|fruit|berr(y|ies)|tuber|grain|honey|jelly)\b", t)),
    ("drug/medicine base", lambda r, t: "drug" in r["ingestible"] or re.search(r"\b(drug|medicine|medicinal|narcotic|psychoactive|spice|stimulant|herb|anesthetic|healing|bacta)\b", t)),
    ("armour hide/leather/chitin/plate", lambda r, t: "Leathery" in r["stuffCategories"] or "Chitin" in r["stuffCategories"] or "Plate" in r["stuffCategories"]
        or re.search(r"\b(leather|hide|pelt|chitin|carapace|shell|scale|scales|plate)\b", t) and "Fabric" not in r["stuffCategories"]),
    ("textile/silk/wool/fibre", lambda r, t: "Fabric" in r["stuffCategories"] or "Weave" in r["stuffCategories"] or re.search(r"\b(silk|wool|fibre|fiber|fleece|cloth|thread|textile|weave|spun|down|fur)\b", t)),
    ("fuel/oil/wax/hydrocarbon", lambda r, t: re.search(r"\b(fuel|oil|bitumen|tar|propane|gas|tibanna|rhydonium|coaxium|combustible|flammable|naphtha|methane|petro)", t)),
    ("adhesive/resin/lacquer/sealant", lambda r, t: re.search(r"\b(resin|wax|sap|gum|glue|adhesive|sealant|amber|pitch|lacquer|varnish|mucus|slime|ooze)", t)),
    ("gem/crystal/light-stone", lambda r, t: re.search(r"\b(crystal|gem|jewel|kyber|pearl|quartz|geode|stygium|opal)", t)),
    ("metals, alloys & synthetics", lambda r, t: "Metallic" in r["stuffCategories"] or re.search(r"\b(ore|ingot|metal|alloy|steel|iron|copper|slag|scrap)\b", t)),
    ("structural wood/bone/stone/ice/clay", lambda r, t: set(r["stuffCategories"].split(";")) & {"Stony", "Woody"} or r["thingCategories"] in ("StoneChunks", "StoneBlocks")
        or re.search(r"\b(stone|rock|chunk|block|wood|timber|log|bone|ivory|horn|tusk|coral)\b", t)),
    ("chemical reagent/salt/venom/pigment", lambda r, t: re.search(r"\b(gland|venom|toxin|toxic|acid|chemical|reagent|bile|ichor|spore|salt|powder|dust|mineral|ash|sulph|sulf|catalyst|culture|enzyme|pigment|dye|ink|blood|organ)", t)),
]


# Judgment layer (2026-10-09 census): the keyword pass above mis-files these; each line is a reading of
# the def's own description, not a rename. "out of scope" = not a material (livestock-in-a-sack, water,
# ammo, finished salvage/medicine, filth); they stay in the CSV so coverage is visible.
O = "out of scope (not a material)"
CLUSTER_OVERRIDES = {
    # metal-salt / mineral salts and reagents
    **{d: "chemical reagent/salt/venom/pigment" for d in (
        "RM_ContaminantBezoar", "RUT_MetalSaltBezoar", "RM_VitrifiedBezoar", "RM_BrinePlate", "RUT_BrinePlate",
        "RM_RawVenom", "RM_SaltPink", "RM_SaltViolet", "RM_SaltAmber", "RM_SaltWhite", "RM_KettlewickSalt",
        "RM_SeepSalt", "RM_Tholin", "RM_StrongTarSolvent", "RM_WeakTarSolvent", "RM_WarDust", "RM_Attar",
        "RM_RadioactiveSuppressant", "RM_VauliskLureOrgan", "RM_RawSlime", "RM_DeltaSilt")},
    **{d: "food-only" for d in (
        "RM_DrommathSap", "RM_DrommathBurstSap", "RM_ThornbugNectar", "RM_SekkulaathCream", "RM_QeshraRoe",
        "RM_SeveredTentacleFlesh", "RM_OllathrixEgg", "RM_VisslerArm", "RSW_AcklayClaw", "RM_TumbelGourd")},
    **{d: "drug/medicine base" for d in (
        "RM_SlimeAntidote", "RM_StellockLace", "RM_Symbiont_Nightwake", "RM_LiveIngredient_AgelessCap",
        "RM_LiveIngredient_EuphoricCrown", "RM_LiveIngredient_RegenerantVeil", "RM_Symbiont_Mycoid",
        "RM_Symbiont_Quickflesh", "RM_Symbiont_Sheenblood", "RM_Tea_AgeReversal", "RM_Tea_Bioregeneration",
        "RM_Tea_Pleasure", "RM_TavroskLiquor")},
    **{d: "structural wood/bone/stone/ice/clay" for d in (
        "RM_SlimeBlock", "RUT_Greenwood", "RM_PottersClay", "RM_DeadVenomvine", "RM_MushroomLog",
        "RM_SlackwaxTimber", "RM_Bones", "RSW_KilnClay", "RSW_CrackedCeramicShards", "RM_TollhornCore")},
    **{d: "glass/silica/optics" for d in (
        "RM_Biosilica", "RM_BiosilicaGrit", "RM_FineSand", "RM_GlassSand", "RM_SunGlass", "RM_GlassPearl",
        "RM_WaveglassShard", "RM_VeilPane", "RM_FexxilShard", "RM_FE_Fulgurite", "RUT_AuroraGlass",
        "RM_Floatstone", "RM_Filth_CleaverShards")},
    **{d: "fuel/oil/wax/hydrocarbon" for d in (
        "RM_KorvethPitch", "KOTOR_RawRhydonium", "RM_TarspoolStalk", "RM_PitchpearlBeads", "RM_LampBladder",
        "RM_NoothelmBulb", "RM_Seepwax", "RM_ThrummelSeepwax")},
    **{d: "adhesive/resin/lacquer/sealant" for d in (
        "RM_VaulmLacquer", "RM_SapResin", "RM_CloakLacquer")},
    **{d: "metals, alloys & synthetics" for d in ("RM_LivePatternMetal", "KOTOR_Plastoid", "RM_ZennaqFilament")},
    **{d: "armour hide/leather/chitin/plate" for d in ("RM_RoyalRind",)},
    **{d: "soil/fertiliser" for d in ("RM_DeltaLoam", "RUT_FungalSoil", "RM_SeedFistFertilizer")},
    **{d: "trophy/relic/curio" for d in (
        "RM_FossilImpression", "RM_FossilDeepStratum", "RM_FossilSkeleton", "RM_SaltCameo", "RUT_SaltCameo",
        "RM_SweetlineToken", "RM_SeepStone", "RUT_SeepStone", "RM_ElderSealedRelic", "RM_FungalMantisClaw",
        "RSW_FungalMantisClaw", "RM_GreatboleGrubSpines", "RM_CrestPlate", "RM_BoltShedCuriosity",
        "RM_WatcherRemains_Piinnok", "RM_WombpodSac", "RM_TarRuinedGoods", "RM_GreatboleSeed")},
    **{d: O for d in (
        "RM_CapturedTetchik", "RM_Shell_Thump", "RSW_Shell_BrainWormEgg", "RSW_Skewer", "RM_CargoFloat",
        "RM_TetherChain", "RM_SandSieve", "RUT_SealedWaterJar", "RM_BlueIceMeltwaterCan", "RM_BrimlockWater",
        "RM_CondenserWater", "KotOR_water", "RM_DrainedFluids", "RUT_FallWreck_Tank", "RUT_FallWreck_Cargo",
        "RUT_FallWreck_Hull", "RSW_DW_DroidHead", "RSW_MarshFungus", "RSW_BactaPatch", "RSW_BactaSpray",
        "RM_HulduBreedingStock", "RM_IvvolBreedingStock", "RM_KarrekBreedingStock", "RM_LoomuBreedingStock",
        "RM_MurrinBreedingStock", "RM_SkarrinBreedingStock", "RM_VizhikBreedingStock")},
}
FOOD_CATS = ("Fish", "EggsUnfertilized", "EggsFertilized", "MeatRaw", "PlantFoodRaw", "AnimalProductRaw")


def cluster_of(r):
    if r["defName"] in CLUSTER_OVERRIDES:
        return CLUSTER_OVERRIDES[r["defName"]]
    if r["defName"].startswith(("guy762_medpac", "guy762_stim")):
        return O
    if r["thingCategories"] in FOOD_CATS and not r["stuffCategories"]:
        return "food-only"
    t = " ".join((r["defName"], r["label"], r["description"], r["thingCategories"], r["stuffCategories"])).lower()
    t = re.sub(r"([a-z])([A-Z])", r"\1 \2", t)
    for name, f in CLUSTER_RULES:
        try:
            if f(r, t):
                return name
        except Exception:  # noqa
            pass
    return "trophy/relic/curio"


# quest / trader / thing-set mentions: a material handed out or bought by these has a market, not a recipe
TRADE_TOKENS = collections.Counter()
for (tp, dn_), el in defs.items():
    if tp in ("QuestScriptDef", "TraderKindDef", "ThingSetMakerDef", "IncidentDef", "RewardDef"):
        TRADE_TOKENS.update(TOKEN.findall(etree.tostring(el, encoding="unicode")))
for p_ in patch_files:
    blob = etree.tostring(docs[p_], encoding="unicode")
    if "TraderKindDef" in blob or "QuestScriptDef" in blob:
        TRADE_TOKENS.update(TOKEN.findall(blob))

# orphan verdicts
for r in ROWS:
    r["cluster"] = cluster_of(r)
    direct = bool(r["uses_recipe"] or r["uses_cost"] or r["uses_fuel"])
    if direct:
        r["consumed"] = "direct"
    elif r["uses_stuff_consumers"]:
        r["consumed"] = "as-stuff"
    elif r["ingestible"] or r["thingCategories"] in ("Fish", "EggsUnfertilized", "EggsFertilized", "MeatRaw", "PlantFoodRaw"):
        r["consumed"] = "eaten"
    elif r["cs_refs"]:
        r["consumed"] = "code"
    elif TRADE_TOKENS.get(r["defName"]):
        r["consumed"] = "trade/quest"
    elif r["uses_category_recipes"]:
        r["consumed"] = "category-recipe"
    else:
        r["consumed"] = "ORPHAN"


STAT_KEYS = ("MarketValue", "Armor_Sharp", "Armor_Blunt", "Armor_Heat", "Insul_Cold", "Insul_Heat", "stuff_statFactors")


def _num(v):
    try:
        return round(float(v), 3)
    except ValueError:
        return v


for r in ROWS:
    r["stat_twins"] = ""
by_vec = collections.defaultdict(list)
for r in ROWS:
    if r["cluster"] in ("food-only", O):
        continue
    vec = tuple(_num(r[k]) for k in STAT_KEYS)
    if sum(1 for v in vec if v != "") >= 3:      # at least three stats set, else every bare item "matches"
        by_vec[vec].append(r)
for vec, rs in by_vec.items():
    if len(rs) > 1:
        for r in rs:
            r["stat_twins"] = ";".join(x["defName"] for x in rs if x is not r)

# same text, different defName: RM_/RUT_/RSW_ copies the stat test cannot see (items with no stats)
for r in ROWS:
    r["text_twins"] = ""
by_text = collections.defaultdict(list)
for r in ROWS:
    if r["cluster"] in ("food-only", O) or len(r["description"]) < 60:
        continue
    by_text[(r["label"].lower(), r["description"][:120].lower())].append(r)
for rs in by_text.values():
    if len(rs) > 1:
        for r in rs:
            r["text_twins"] = ";".join(x["defName"] for x in rs if x is not r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(REPO, "design/RimMandrake/exotic_materials_census_2026-10-09.csv"))
    a = ap.parse_args()
    print("xml files %d (parse failures %d); patch files %d; ThingDefs %d; BiomeDefs %d" % (
        len(xml_files), len(parse_fail), len(patch_files), len(thing), len(biome_defs)))
    print("materials %d; producer links %d (to our defs) + %d to external defs" % (
        len(ROWS), sum(len(v) for v in prod.values()), sum(external_prod.values())))
    names = {r["defName"]: r for r in ROWS}
    probes = [("RM_ToxinSealant", lambda n: n == "RM_ToxinSealant"),
              ("*Leather*", lambda n: "leather" in n.lower()),
              ("*Seepwax*", lambda n: "seepwax" in n.lower()),
              ("*Bitumen*", lambda n: "bitumen" in n.lower()),
              ("*Silk*", lambda n: "silk" in n.lower()),
              ("*Chitin*", lambda n: "chitin" in n.lower()),
              ("KOTOR_AlloyDurasteel", lambda n: n == "KOTOR_AlloyDurasteel")]
    for lbl, f in probes:
        inall = sum(1 for n in ALL_THING if f(n))
        found = sum(1 for n in names if f(n))
        print("  probe %-22s found %3d of %3d ThingDefs matching" % (lbl, found, inall))
    c = collections.Counter(r["consumed"] for r in ROWS)
    print("consumed:", dict(c))
    print("clusters:", dict(collections.Counter(r["cluster"] for r in ROWS).most_common()))
    print("orphans by cluster:", dict(collections.Counter(r["cluster"] for r in ROWS if r["consumed"] == "ORPHAN").most_common()))
    print("stat-twin groups (identical stat vectors):", sum(1 for v in by_vec.values() if len(v) > 1))
    print("text-twin groups (same label+description):", sum(1 for v in by_text.values() if len(v) > 1))
    print("source kinds:", dict(collections.Counter(r["source_kind"] or "-" for r in ROWS)))
    keys = list(ROWS[0].keys())
    with open(a.csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in sorted(ROWS, key=lambda r: (r["mod"], r["defName"])):
            w.writerow(r)
    print("wrote", os.path.relpath(a.csv, REPO))


if __name__ == "__main__":
    main()
