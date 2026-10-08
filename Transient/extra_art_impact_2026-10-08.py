"""Extra-art impact scoring (gender + juvenile) over our animal-style races. 2026-10-08, BENCH design helper.

Reads src/**/{Defs,Patches}/*.xml. ParentName resolved inside our XML only (vanilla/donor parents unseen; vanilla
defaults assumed: wildGroupSize 1, herdAnimal false, hasGenders true). Rosters: BiomeDef <wildAnimals> read as
ELEMENTS (node name = animal, text = commonality) plus patch-added rosters resolved from each PatchOperation's own
xpath. Output: extra_art_impact_2026-10-08.csv beside this file. Run: python3 <this>.
"""
import csv, glob, math, re, sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/mandrake/rm/bench")
SRC = REPO / "src"
CANON = REPO / "design/RimStarWars/canon_references"
OUT = REPO / "Transient/extra_art_impact_2026-10-08.csv"
SKIP = {"Utils", "bridgetools", "mapsynth", "rimflow", "RimDefDump"}

files = [p for p in glob.glob(str(SRC) + "/**/*.xml", recursive=True)
         if ("/Defs/" in p or "/Patches/" in p) and not (SKIP & set(p.split("/")))]
named, things, kinds, bad = {}, {}, [], 0
roster = defaultdict(dict)          # animal -> {biome: commonality}
XP = re.compile(r'BiomeDef\[(?:@Name|defName)\s*=\s*"([^"]+)"\]')


def num(s, d=None):
    try:
        return float(s)
    except Exception:
        return d


for p in files:
    try:
        r = ET.parse(p).getroot()
    except Exception:
        bad += 1
        continue
    if r.tag == "Defs":
        for e in r:
            if not isinstance(e.tag, str):
                continue
            if e.get("Name"):
                named[(e.tag, e.get("Name"))] = e
            dn = (e.findtext("defName") or "").strip()
            if e.tag == "ThingDef" and dn and e.get("Abstract") != "True":
                things[dn] = (p, e)
            elif e.tag == "PawnKindDef" and dn and e.get("Abstract") != "True":
                kinds.append((p, e))
            elif e.tag == "BiomeDef" and dn:
                wa = e.find("wildAnimals")
                if wa is not None:
                    for c in wa:
                        if c.tag == "li":
                            a, v = (c.findtext("animal") or "").strip(), num(c.findtext("commonality"), 0.0)
                        else:
                            a, v = c.tag, num(c.text, 0.0)
                        if a:
                            roster[a][dn] = max(roster[a].get(dn, 0.0), v or 0.0)
    elif r.tag == "Patch":
        for op in r.iter():
            xp = op.find("xpath")
            val = op.find("value")
            if xp is None or not xp.text or val is None or "wildAnimals" not in xp.text:
                continue
            for biome in XP.findall(xp.text):
                kids = list(val)
                if len(kids) == 1 and kids[0].tag == "wildAnimals":
                    kids = list(kids[0])
                for c in kids:
                    if c.tag == "li":
                        a, v = (c.findtext("animal") or "").strip(), num(c.findtext("commonality"), 0.0)
                    else:
                        a, v = c.tag, num(c.text, 0.0)
                    if a:
                        roster[a][biome] = max(roster[a].get(biome, 0.0), v or 0.0)


def find(e, tag, path):
    seen = 0
    while e is not None and seen < 12:
        x = e.find(path)
        if x is not None:
            return x
        pn = e.get("ParentName")
        e = named.get((tag, pn)) if pn else None
        seen += 1
    return None


def ft(e, tag, path, d=""):
    x = find(e, tag, path)
    return (x.text or "").strip() if x is not None and x.text else d


def rng(x):
    if x is None:
        return (1, 1)
    if x.text and x.text.strip():
        a = x.text.strip().split("~")
        return (int(float(a[0])), int(float(a[-1])))
    return (int(num(x.findtext("min"), 1)), int(num(x.findtext("max"), 1)))


canon = {}
for d in CANON.iterdir():
    if d.is_dir() and not d.name.startswith(("_", ".")):
        canon[d.name] = " ".join(open(f, errors="ignore").read() for f in d.glob("*.md"))
norm = lambda s: re.sub(r"[^a-z]", "", s.lower())
TRAIT = r"(larger|smaller|bigger|heavier|horns?|crests?|manes?|tusks?|colou?r\w*|bright\w*|plum\w*|antlers?|frills?|sails?|lack\w*|dull\w*|drab|wattles?|spurs?|display)"
DIMORPH = re.compile(r"(sexual(?:ly)? dimorph\w*|\bdimorph\w*|\b(?:fe)?males?\b[^.]{0,80}\b" + TRAIT + r"\b|\b"
                     + TRAIT + r"\b[^.]{0,40}\b(?:than|in) (?:the )?(?:fe)?males?\b|\b(?:bulls?|cows?|stags?|hens?|roosters?|drakes?)\b[^.]{0,40}\b"
                     + TRAIT + r"\b|\bonly (?:the )?(?:fe)?males?\b)", re.I)
YN = r"(calf|calves|cubs?|pups?|foals?|chicks?|hatchlings?|young|babies|baby|juveniles?|younglings?|whelps?|kits?|fledglings?|nymphs?)"
YT = r"(lack\w*|without|differ\w*|unlike|until|pale\w*|pink|spotted|striped|stripes|mottled|colou?r\w*|downy|down\b|fluff\w*|hornless|no horns|translucent|soft-shelled|bright\w*|carried|ride|riding|cling\w*|pouch)"
YOUNG = re.compile(r"\b" + YN + r"\b[^.]{0,80}\b" + YT + r"\b|\b" + YT + r"\b[^.]{0,40}\b(?:the |its )?" + YN + r"\b", re.I)
def snip(rx, text, w=60):
    m = rx.search(text or "")
    return "" if not m else re.sub(r"\s+", " ", text[max(0, m.start() - w):m.end() + w])


# every dimorphism hit read by hand 2026-10-08; these two are not dimorphism
DIMORPH_REJECT = {"RSW_Varactyl": "both sexes carry crests", "RSW_Urusai": "canon: dimorphism not stated"}
# every young-differs hit read by hand 2026-10-08; these say the young look the SAME (or are not about looks)
YOUNG_REJECT = {"RSW_Falumpaset": "calf is a smaller version of the same shape", "RSW_TeeMuss": "calf hide, not looks",
                "RSW_Urusai": "chicks duel: behaviour", "RSW_Grank": "identical colouring stated",
                "RSW_Diggerpede": "bears young alive", "RM_Gristle": "bears young alive",
                "RSW_Zakkeg": "about a render, not the young", "RSW_Borcatu": "size only",
                "RSW_Blarth": "same colouring stated", "RSW_OpeeSeaKiller": "mouth-brooding, not looks"}
rows, races_seen = [], set()
for p, k in kinds:
    ls = find(k, "PawnKindDef", "lifeStages")
    lis = ls.findall("li") if ls is not None else []
    if not any(li.find("bodyGraphicData") is not None for li in lis):
        continue
    race = ft(k, "PawnKindDef", "race")
    if race in races_seen or race not in things:
        continue                                  # one row per race, local races only
    races_seen.add(race)
    rp, re_ = things[race]
    rc = find(re_, "ThingDef", "race")
    if rc is None or (rc.findtext("intelligence") or "") == "Humanlike":
        continue
    dn = ft(k, "PawnKindDef", "defName")
    label = ft(re_, "ThingDef", "label") or race
    desc = ft(re_, "ThingDef", "description")
    slug = next((s for s in (norm(re.sub(r"^(RM|RSW|RUT)_", "", race)), norm(label)) if s in canon), "")
    ctext = canon.get(slug, "")
    tags = [li.text.strip() for li in (find(re_, "ThingDef", "tradeTags") if find(re_, "ThingDef", "tradeTags") is not None else []) if li.text]
    comps = find(re_, "ThingDef", "comps")
    cls = [c.get("Class") or "" for c in (comps if comps is not None else [])]
    sb = find(re_, "ThingDef", "statBases")
    wild = num(sb.findtext("Wildness") if sb is not None else None, num(ft(re_, "ThingDef", "race/wildness"), None))
    mft = num(sb.findtext("MaxFlightTime") if sb is not None else None, 0) or 0
    herd = ft(re_, "ThingDef", "race/herdAnimal").lower() == "true"
    pack = ft(re_, "ThingDef", "race/packAnimal").lower() == "true"
    gen = ft(re_, "ThingDef", "race/hasGenders", "true").lower() != "false"
    train = ft(re_, "ThingDef", "race/trainability", "")
    roam = num(ft(re_, "ThingDef", "race/roamMtbDays"), None)
    size = num(ft(re_, "ThingDef", "race/baseBodySize"), 1.0)
    life = num(ft(re_, "ThingDef", "race/lifeExpectancy"), None)
    gest = num(ft(re_, "ThingDef", "race/gestationPeriodDays"), None)
    water = find(re_, "ThingDef", "race/waterCellCost") is not None
    lsa = find(re_, "ThingDef", "race/lifeStageAges")
    stages = [((li.findtext("def") or "").strip(), num(li.findtext("minAge"), 0)) for li in (lsa if lsa is not None else [])]
    adult_age = next((a for d, a in stages if "Adult" in d), None)
    young_days = round(adult_age * 60, 1) if adult_age is not None else None
    gmin, gmax = rng(find(k, "PawnKindDef", "wildGroupSize"))
    bodytex = [(li.findtext("bodyGraphicData/texPath") or "").strip() for li in lis]
    distinct_young = len({t for t in bodytex if t}) > 1
    has_f = any(li.find("femaleGraphicData") is not None for li in lis)
    has_swim = any(li.find("swimmingGraphicData") is not None for li in lis)
    flyprefix = ft(k, "PawnKindDef", "flyingAnimationFramePathPrefix")
    domestic = ("AnimalFarm" in tags) or (roam is not None) or (wild is not None and wild <= 0.3)
    petlike = "AnimalPet" in tags or num(ft(re_, "ThingDef", "race/nuzzleMtbHours"), None) is not None
    tameable = wild is None or wild < 0.98
    egg = any("EggLayer" in c for c in cls)
    milk = any("Milkable" in c for c in cls)
    shear = any("Shearable" in c for c in cls)
    rost = roster.get(race, {})
    rost_n, rost_c = len(rost), round(sum(rost.values()), 2)
    dim_s = snip(DIMORPH, ctext) or snip(DIMORPH, desc)
    if race in DIMORPH_REJECT:
        dim_s = ""
    young_s = snip(YOUNG, ctext) or snip(YOUNG, desc)
    if race in YOUNG_REJECT:
        young_s = ""
    young_strong = bool(young_s)
    separate_young_race = bool(re.search(r"(Larva|Larvae|Spawn|Hatchling|Grub)$", race))

    # ---- gender impact: how often does the player see several of these side by side?
    seen_together = math.log2(1 + gmax) * 2 + (1.5 if herd else 0)
    presence = min(rost_c, 3) + min(rost_n, 4) * 0.25
    kept = (3 if domestic else 0) + (1.5 if pack else 0) + (1 if milk or shear or egg else 0)
    # a sex difference is invisible on a tiny sprite or a swarm: scale the whole score by visible size
    sizef = min(1.0, max(size, 0.05) / 0.6)
    g = (seen_together + presence + kept + (4 if dim_s else 0) + min(size, 3) * 0.5) * sizef
    g_cost = 3 + (3 if pack else 0) + (3 if has_swim else 0) + (12 if mft > 0 else 0)   # pack path follows female body!
    # ---- juvenile impact: how long and how often is a young one on screen, and does a scaled adult look wrong?
    bred = (3 if domestic else 0) + (1.5 if pack else 0) + (1 if tameable else 0) + (1 if petlike else 0)
    yd = young_days or 0
    duration = min(math.log2(1 + yd), 6) * 0.6
    j = bred + duration + (4 if young_strong else 0) + min(rost_c, 3) * 0.5 \
        + (0.5 if herd else 0) + min(size, 3) * 0.5
    j *= min(1.0, max(size, 0.05) / 0.4)          # a young swarmling is a dot either way
    j_cost = 3 + (3 if has_swim else 0)
    rows.append(dict(race=race, kind=dn, label=label, mod=str(Path(rp).relative_to(SRC)).split("/")[1],
                     has_genders=gen, has_female_art=has_f, has_distinct_young=distinct_young,
                     group=f"{gmin}~{gmax}", herd=herd, roster_biomes=rost_n, roster_commonality=rost_c,
                     domestic=domestic, pack=pack, petlike=petlike, tameable=tameable, wildness=wild, trainability=train,
                     milk=milk, shear=shear, egg=egg, body_size=size, young_days=young_days, life_years=life,
                     gestation_days=gest, flyer=mft > 0, swim_art=has_swim, water=water,
                     bodydef=ft(re_, "ThingDef", "race/body"), canon=slug, dimorph_snip=dim_s[:160], young_snip=young_s[:160], young_strong=young_strong, separate_young_race=separate_young_race,
                     g_score=round(g, 2), g_cost_jobs=g_cost, j_score=round(j, 2), j_cost_jobs=j_cost))

print(f"xml {len(files)} parse-fail {bad} | races scored {len(rows)} | roster creatures {len(roster)} | canon {len(canon)}")
print("SANITY PROBE (race: roster biomes / group / domestic):")
for pr in ["RM_Fessk", "RSW_Gizka", "RM_Sytheclaw", "RSW_Bantha", "RSW_Dewback", "RSW_Eopie"]:
    r = next((x for x in rows if x["race"] == pr), None)
    print("  ", pr, "MISSING" if r is None else (r["roster_biomes"], r["group"], r["domestic"], r["has_female_art"]))
print("roster probe RSW_Gizka biomes:", sorted(roster.get("RSW_Gizka", {})))
rows.sort(key=lambda r: -r["g_score"])
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("wrote", OUT)
