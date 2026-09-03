#!/usr/bin/env python3
"""Thematic regroup of the research trees — BENCH design pass 2026-09-03.

Fixes the manifest's tier-band tab defaulting: reassigns every surviving project
to its THEMATIC tab (weapon->Armory, droid->Machine, ship->Ship, gene/archotech->
Reach, industry->Trade & Craft, early utility->Scavenger) with tier kept orthogonal.
Applies the owner's cuts (Anomaly, Big & Small) + BENCH's parallel cut (Dungeon Pack).

Reads Transient/research_restructure/model.json (already carries owner cuts);
writes restructured.json + prints the new distribution.
"""
import json
import re
from collections import Counter, defaultdict

M = json.load(open("Transient/research_restructure/model.json"))

# extra BENCH cut: Dungeon Pack — map/dungeon locations, 0 unlocks, repurposed (owner's Anomaly principle)
for m in M:
    if m["fate"] not in ("cut", "merge") and "Dungeon Pack" in m["mod"]:
        m["fate"] = "cut"
        m["reason"] = "Dungeon Pack: map/dungeon locations, 0 unlocks — repurposed content, not player research (BENCH, owner's Anomaly principle)"

def hay(m):
    # a research's tab follows its OWN identity (label + defName), never its noisy
    # unlock list — a chem research that unlocks one shelled item is not a weapon.
    return (m["defName"] + " " + m["label"]).lower()

def classify(m):
    mod = m["mod"].lower()
    h = hay(m)
    # 1. THE SHIP — gravship/gravtech
    if re.search(r"grav\b|gravship|gravtech|reactor|astrofuel|\bwarp|ship design|memory core|hull plat", h) \
       or "gravship" in mod or "gravtech" in mod:
        return "THE SHIP"
    # 2. The Machine — droids / mechs / synthetic intelligence
    if re.search(r"droid|\bmech\b|mechtech|automaton|servitor|synstruct|artificial intel|\brimai\b|robotic", h) \
       or any(k in mod for k in ("droid", "alpha mechs", "synstruct", "rimai", "asimov", "mechanoid")):
        return "The Machine"
    # 3. industry mods claimed BEFORE weapon-keyword matching (their chem/material
    #    rows kept leaking into the Armory on a unlock word)
    if any(k in mod for k in ("rimefeller", "custom gas", "dubs bad hygiene", "cooking",
                              "furniture", "kotor resources", "fortifications",
                              "gas types", "miningco", "tinkering")):
        return "Trade & Craft"
    # 4. The Reach — the archotech / gene / bio endgame ladder
    if re.search(r"\bgene|archite|archotech|archogenet|biosculpt|bioregen|xenogerm|xenogenet|"
                 r"glandular|nano|ultratech|high mechtech|ultra mechtech|psy(chic|link|cast)|"
                 r"fertilit|toxin|wastepack|deathrest|sanguophage|ghoul", h) \
       or (any(k in mod for k in ("genetics", "biotech", "highmate")) and m["tier"] in ("T2", "T3", "T4")):
        return "The Reach"
    # 5. The Armory — weapon word in the research's OWN name (or the Armoury mod)
    if re.search(r"weapon|turret|blaster|rifle|pistol|\bgun|cannon|munition|ordnance|\bammo|"
                 r"shield|\barmor|\barmour|warcasket|grenade|explos|missile|artillery|slug|railgun|"
                 r"tesla|\bion |sonic|saber|vibro|\bied|mortar|rocket|\bbomb|flak|long blade|smokepop", h) \
       or "armoury" in mod:
        if not (m["tier"] == "T0" and re.search(r"\bbow\b|\bclub\b", h)):
            return "The Armory"
    # 6. Trade & Craft — industrial economy by keyword
    if re.search(r"fabricat|refin|\bgas\b|\bpower\b|production|furnitur|textile|smelt|material|"
                 r"drill|hydroponic|electric|machin|chemfuel|biofuel|reservoir|pipe|forge|"
                 r"cook|brew|butcher|smith|tailor|loom|component|neutroamine|synth(read|ylene)|"
                 r"drug|medicine|penoxy|electronics|packaged|nutrient", h):
        return "Trade & Craft"
    # 7. fall through by tier
    return {"T0": "Scavenger", "T1": "Scavenger", "T2": "Trade & Craft",
            "T3": "The Reach", "T4": "The Reach"}.get(m["tier"], "Scavenger")

for m in M:
    m["newtab"] = None if m["fate"] in ("cut", "merge") else classify(m)

surv = [m for m in M if m["newtab"]]
json.dump(M, open("Transient/research_restructure/restructured.json", "w"), indent=1)

TABS = ["Scavenger", "Trade & Craft", "The Armory", "The Machine", "THE SHIP", "The Reach"]
print("=== NEW thematic distribution (survivors) ===")
for tab in TABS:
    rows = [m for m in surv if m["newtab"] == tab]
    tiers = Counter(m["tier"] for m in rows)
    print(f"  {tab:15} {sum(tiers.values()):4}   {dict(sorted(tiers.items()))}")
print(f"  {'(survivors)':15} {len(surv):4}")
print()
print("=== CUT total by reason ===")
cuts = [m for m in M if m["fate"] == "cut"]
b = Counter()
for m in cuts:
    r = m["reason"]
    k = ("Anomaly" if "Anomaly" in r else "Big & Small" if "Big & Small" in r
         else "Dungeon Pack" if "Dungeon" in r else "Royalty" if "oyalty" in r
         else "measured-dead" if "dead" in r.lower() else "other-ruled")
    b[k] += 1
for k, n in b.most_common():
    print(f"  {n:4}  {k}")
print(f"  {len(cuts)} cut · {len([m for m in M if m['fate']=='merge'])} merge · {len(surv)} in trees")
