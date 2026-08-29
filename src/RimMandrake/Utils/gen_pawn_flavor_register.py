#!/usr/bin/env python3
"""Generate the pawn-flavor review sheet (PAWN_FLAVOR_STARWARS_1).

Emits design/Jawa/worldbuilding/review/pawn_flavor_register.html and, when no
owner-touched decisions file exists, the prefill JSON beside it.

The sheet's row data merges two sources:
  * SHIPPED content read live from src/RimMandrake/Jawa_PawnFlavor/Defs/*.xml
    (backstories + traits) and the ISEKAI reflavor patch - regenerating the
    sheet tracks the mod.
  * DESIGNED content transcribed from design/Jawa/pawn_flavor_design.md
    (rounds 1-5). That doc is the source; edit it, then re-transcribe here.

🔴 The decisions file is the OWNER'S once it carries `savedAt` (stamped only by
the page). This generator refuses to overwrite it without
--i-know-this-overwrites-the-owners-decisions.
"""
import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_DIR = os.path.join(ROOT, "design", "Jawa", "worldbuilding", "review")
HTML_OUT = os.path.join(OUT_DIR, "pawn_flavor_register.html")
DEC_OUT = os.path.join(OUT_DIR, "pawn_flavor_register.decisions.json")
DEC_NATIVE = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\pawn_flavor_register.decisions.json"
HTML_NATIVE = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\pawn_flavor_register.html"

FACTION_OF_CAT = {
    "JawaBSC_Homestead": "Homestead Defense League",
    "JawaBSC_Wildsteam": "Wildsteam Clan",
    "JawaBSC_Junkers": "the Junkers",
    "JawaBSC_Empire": "Galactic Empire",
    "JawaBSC_Hutt": "Hutt Cartel",
    "JawaBSC_Tribes": "Deep Desert Tribes",
    "JawaBSC_Geonosian": "Geonosian Foundry Hive",
    "JawaBSC_Helix": "Ascendant Helix",
    "JawaBSC_Blackstar": "Blackstar Company",
    "JawaBSC_Moot": "Jawa Trade Moot",
    "JawaBSC_Deepwater": "Deepwater Compact",
}

SHIPPED_TRAIT_FACTION = {
    "Jawa_WaterDiscipline": ("Cross-faction seed families", "D-family: low water/food needs; colony-waste mood hit."),
    "Jawa_SandStoic": ("Deep Desert Tribes", "Heat and sandstorm tolerance; the desert does not frighten them."),
    "Jawa_Numbered": ("Galactic Empire", "Bonds slowly, insult-immune - a designation, not a name."),
    "Jawa_Laconic": ("Blackstar Company", "Says little; social chill, unshakable under fire."),
    "Jawa_PodracerReflexes": ("Cross-faction seed families", "A-family: speed and dodge up, ranged aim down, reckless."),
}

# DESIGNED rows: (faction, layer, name, does, status, contested, note)
# status: designed-xml | designed-csharp | parked
D = []
def d(faction, layer, name, does, status="designed-csharp", contested=False):
    D.append({"faction": faction, "layer": layer, "name": name, "does": does,
              "status": status, "contested": contested})

# Cross-cutting slave arc
d("Cross-cutting: slave arc", "mechanic", "Ransomable",
  "Origin faction pays for this pawn; income vs workforce decision.")
d("Cross-cutting: slave arc", "mechanic", "Rescue-Worthy",
  "Origin faction raids to retrieve this pawn specifically.")
d("Cross-cutting: slave arc", "trait", "Unbending / Broken (APPROVED)",
  "Trait degrees flipped by a Harmony hook on vanilla slave-rebellion; the degree IS the state, no new UI.")
d("Cross-cutting: slave arc", "mechanic", "Collared Expertise",
  "Some skills usable only when trusted/freed; freeing becomes a gameplay verb (buy low, free high).",
  contested=True)

# Cross-faction seed families (unshipped concepts only)
F = "Cross-faction seed families"
d(F, "trait", "Scavenger's Eye", "A: salvage yield bonus / hoarder mood debuff.")
d(F, "trait", "Jury-Rigger", "A: faster, cheaper crafts / output breaks down more.")
d(F, "trait", "Void-Touched", "A: high psychic sensitivity, cuts both ways.", status="designed-xml")
d(F, "backstory", "Debt to the Hutts", "B: periodic tithe demand - pay or be raided.")
d(F, "backstory", "Carries a Secret", "B: hidden second backstory revealed on trigger.")
d(F, "backstory", "Last of the Crew", "B: grief thought converts to a buff after N new bonds.")
d(F, "childhood", "Clan-Born", "C: kin-link web across pawns sharing the tag.")
d(F, "mechanic", "Master-and-Apprentice", "C: paired pawns, double learning, separation penalty.")
d(F, "mechanic", "Sworn Rival", "C: hostile link to a category, payoff on reconciliation.")
d(F, "childhood", "Dune-Raised", "D: heat/sand mastery, roof-sick indoors.", status="designed-xml")
d(F, "childhood", "Vault-Born", "D: the inverse - underground comfort, sky-fear.", status="designed-xml")
d(F, "trait", "Droid-Whisperer", "E: droid affinity; can soothe berserk droids.")
d(F, "adulthood", "Stormtrooper Washout", "F: aim penalty specifically vs moving targets - on-lore, needs C#.",
  contested=True)
d(F, "trait", "War-Echoed", "F: flashback mental break, decays with calm battles.")
d(F, "trait", "Shield-Line Veteran", "F: formation bonus when adjacent to allies.")
d(F, "trait", "Force ladder: Latent / Awakened / Trained", "G: psychic sensitivity ladder feeding meditation and rare abilities.")
d(F, "trait", "Force-Null", "G: psychic immunity, no psycasts, unsettling aura.")
d(F, "childhood", "Sold Young", "H: modifies any adulthood - freed-slave interactions.")

# Per-faction designed extras (unshipped)
d("Homestead Defense League", "childhood", "Vaporator Apprentice", "Plants/crafting floors; the family trade.", status="designed-xml")
d("Homestead Defense League", "adulthood", "Militia Sergeant", "Passive shooting trainer for nearby colonists.")
d("Homestead Defense League", "trait", "vanilla pool: patient/stubborn/quietly brave + NEW 'provincial'",
  "Weighting pass on vanilla traits; 'provincial' (uneasy off-world) would be new.", status="designed-xml", contested=True)
d("Wildsteam Clan", "childhood", "Canopy-Cradled", "Animals passion, starts with a bonded animal.", status="designed-xml")
d("Wildsteam Clan", "adulthood", "Beast-Sung", "Handling savant, calm-manhunter ability; severe grief on bonded death.")
d("Wildsteam Clan", "adulthood", "The Small Elder (HOMAGE)", "Frail, awful on paper, hidden top-degree Force trait + teaching aura.", contested=True)
d("Wildsteam Clan", "trait", "Web-Minded", "Mood scales with count of distinct living species on map - signature.")
d("Wildsteam Clan", "trait", "Green-Grief", "Mass plant destruction mood hit.")
d("Wildsteam Clan", "trait", "Rooted", "Home-map bonus, hates travel.")
d("Wildsteam Clan", "trait", "Life-Debt", "Strong bond to whoever heals them.")
d("the Junkers", "adulthood", "Casket-Bound", "Lives in a warcasket (VFEP hediffs carry mechanics): irreversible, social debuffs, combat monster.")
d("the Junkers", "trait", "Casket-Dreamer", "Mood buff near warcaskets; wants in.")
d("the Junkers", "trait", "Casket-Haunted", "Fear: debuff near caskets, refuses surgery.")
d("Galactic Empire", "childhood", "Core-Worlds Evacuee", "Fast learner; displaced debuff fading with an owned bedroom.", status="designed-xml")
d("Galactic Empire", "adulthood", "Propaganda Auditor", "Conversion elite; others' opinion of them decays.")
d("Galactic Empire", "adulthood", "Inquisitorial Washout", "Rare failed Force-adept: haunted breaks, hidden ladder potential.", contested=True)
d("Galactic Empire", "trait", "Order-Bound", "Mood tied to a kept schedule.")
d("Galactic Empire", "trait", "Rank-Minded", "Opinion bonus toward higher-skilled pawns.")
d("Hutt Cartel", "childhood", "Toll-Gate Child", "Trade savant; gift-giving mood penalty.", status="designed-xml")
d("Hutt Cartel", "adulthood", "Cistern Auditor", "Colony spoilage reduced.", status="designed-xml")
d("Hutt Cartel", "adulthood", "Freed Proxy", "Social elite; Cartel opinion floor permanently low.", status="designed-xml")
d("Hutt Cartel", "trait", "Transactional", "Favor/slight opinion swings doubled.")
d("Hutt Cartel", "trait", "Appetite / Cold-Blooded", "Vanilla-adjacent pool pair for Cartel spawns.", status="designed-xml")
d("Deep Desert Tribes", "childhood", "Water-Priest's Ward", "Mood HIT while colony runs vaporators - sacrilege; conversion clears it.", contested=True)
d("Deep Desert Tribes", "adulthood", "Adopted Outsider", "Any species; fast learner, low recruit resistance.", status="designed-xml")
d("Deep Desert Tribes", "trait", "Water-Pious", "Mood tied to water-source purity; feeds the conversion arc.")
d("Deep Desert Tribes", "trait", "Vengeful / Stoic pool", "Vanilla weighting pass.", status="designed-xml")
d("Geonosian Foundry Hive", "adulthood", "Queen's Attendant", "Rare: counts as several hive-kin for others - makes drone-keeping viable.")
d("Geonosian Foundry Hive", "trait", "Hive-Tuned", "Mood averages toward nearby Geonosians.")
d("Geonosian Foundry Hive", "trait", "Tireless / Chitin-Proud", "Low rest need; armor pride pool.", status="designed-xml")
d("Ascendant Helix", "childhood", "Catalogue Orphan", "Discarded line: random genes, flagged 'recall item'.", status="designed-xml")
d("Ascendant Helix", "adulthood", "Bioweapon Warden", "Toxin/disease immune, unsettling.", status="designed-xml")
d("Ascendant Helix", "trait", "Perfected", "Global bonus + sterile.", status="designed-xml")
d("Ascendant Helix", "trait", "Catalogued", "Suppression-friendly; the Made are made to be managed.", status="designed-xml")
d("Ascendant Helix", "trait", "Draft-Hater", "Opinion penalty toward baseliners.", status="designed-xml")
d("Blackstar Company", "mechanic", "Named Hunter raid-spike + truce event",
  "Holding a Named Hunter SPIKES Blackstar raids; freeing them fires a one-time truce - the only lever on a permanent enemy.", contested=True)
d("Blackstar Company", "trait", "The Code", "Professional-pride mood after clean victories.")
d("Blackstar Company", "trait", "Gear-Proud", "Mood from equipped weapon quality - feeds the Jawa economy loop.")
d("Jawa Trade Moot", "childhood", "Offworlder's Shadow", "Creche translator for spacer crews: social/intellect, wanderlust thought.", status="designed-xml")
d("Jawa Trade Moot", "childhood", "Salvage-Sifter", "E-family cruder: mining/hauling floors, hoarder mood.", status="designed-xml")
d("Jawa Trade Moot", "adulthood", "Utinni Prospector", "Mining/ruins savant, greed-spike break weight.", status="designed-xml")
d("Jawa Trade Moot", "adulthood", "Crawler Mechanic", "Construction/craft elite, breakdown affinity.", status="designed-xml")
d("Jawa Trade Moot", "adulthood", "Droidwright of the Moot", "Droid affinity - the droid-system bridge.", contested=True)
d("Jawa Trade Moot", "trait", "Utinni!", "Mood buff on acquiring new things - the signature.")
d("Jawa Trade Moot", "trait", "Kin-Web", "Opinion bonus across Moot/Jawa pawns.")
d("Jawa Trade Moot", "trait", "Chatter-Trade", "Trade-price statOffsets - plain XML, shippable now.", status="designed-xml")
d("Deepwater Compact", "childhood", "Drought-Witness", "Saw a reservoir fail: water discipline, hoards water, resists heat breaks.", status="designed-xml")
d("Deepwater Compact", "adulthood", "Balance Arbiter", "Secular judge: social elite, conversion-resistant both ways.", status="designed-xml")
d("Deepwater Compact", "adulthood", "Reservoir Cartographer", "Caravan speed, scout.", status="designed-xml")
d("Deepwater Compact", "trait", "Amphibian-Blooded", "Mood/health scales with water access - a slave you must plumb for.", contested=True)
d("Deepwater Compact", "trait", "Neutral to the Bone", "Damped opinion swings, conversion resistance.")
d("Deepwater Compact", "trait", "Monopolist", "Sell-price bonus; gift-giving mood hit.", status="designed-xml")
d("Deepwater Compact", "trait", "Still-Water Patience", "Lower break weights, slower work.", status="designed-xml")

# Droids - parked with DROID_SYSTEM_EMBRACE_1
DP = "Droids (PARKED: DROID_SYSTEM_EMBRACE_1)"
for n, t in (("Factory-Fresh", "Assembly: boring on purpose - the baseline roll."),
             ("Battlefield Salvage", "Assembly: combat stats, one missing capacity."),
             ("Artisan Hand-Build", "Assembly: one savant skill, one crippled."),
             ("Frankenframe", "Assembly: stats re-roll on each down-and-repair."),
             ("Cursed Line", "Assembly: cheap, one guaranteed severe quirk.")):
    d(DP, "childhood", n, t, status="parked")
for n, t in (("Three Centuries of Protocol", "Service: social/trade monster, absolute pacifist."),
             ("Memory-Wiped xN", "Service: degrees - lower skills, faster learning, skill-return event."),
             ("War-Surplus", "Service: shooting elite, anti-droid targeting bonus."),
             ("Restraining-Bolt Decades", "Service: tireless; berserk-on-liberation risk."),
             ("Companion-Imprinted", "Service: huge buffs near ONE colonist, useless after their death."),
             ("Corrupted Core", "Service: savant + periodic scrambled wander/babble.")):
    d(DP, "adulthood", n, t, status="parked")

ISEKAI_DOES = {
    "Isekai_Protagonist": "x10 XP, +2 stat points/level. Now 'chosen one'.",
    "Isekai_Antagonist": "x8 XP, +25% melee, -25 opinion from all. Now 'dark side ascendant'.",
    "Isekai_Reincarnated": "New Game+: level reset, x5 XP, constellation kept. Now 'force echo'.",
    "Isekai_Regressor": "x4 XP, free respec always. Now 'foresight-touched'.",
    "Isekai_SummonedHero": "x3 XP, break-resistant, -8 mood displaced. Now 'outlander'.",
}


def shipped_rows():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "src/RimMandrake/Jawa_PawnFlavor/Defs/Backstories_*.xml"))):
        for bs in ET.parse(f).getroot():
            cat = [c.text for c in bs.find("spawnCategories")][0]
            skills = ", ".join("%s+%s" % (s.tag[:5], s.text) for s in bs.find("skillGains"))
            slot = bs.findtext("slot")
            rows.append({
                "id": bs.findtext("defName"),
                "faction": FACTION_OF_CAT[cat],
                "layer": "childhood" if slot == "Childhood" else "adulthood",
                "name": bs.findtext("title"),
                "does": (skills or "no skill gains") + ".",
                "status": "shipped-xml", "contested": False,
                "desc": (bs.findtext("description") or "")})
    tf = os.path.join(ROOT, "src/RimMandrake/Jawa_PawnFlavor/Defs/Traits_JawaPawnFlavor.xml")
    for td in ET.parse(tf).getroot():
        dn = td.findtext("defName")
        fac, does = SHIPPED_TRAIT_FACTION[dn]
        lab = next(dd.findtext("label") for dd in td.iter("li") if dd.findtext("label"))
        rows.append({"id": dn, "faction": fac, "layer": "trait", "name": lab,
                     "does": does, "status": "shipped-xml", "contested": False, "desc": ""})
    return rows


def isekai_rows():
    rows = []
    for dn, does in ISEKAI_DOES.items():
        rows.append({"id": dn, "faction": "ISEKAI leveling (reflavored live)", "layer": "trait",
                     "name": dn.replace("Isekai_", ""), "does": does,
                     "status": "reflavored-live", "contested": False, "desc": ""})
    for r in ("F", "E", "D", "C", "B", "A", "S", "SS", "SSS", "Nation"):
        nm = "sector-class threat" if r == "Nation" else ("guild rating " + r)
        rows.append({"id": "Isekai_Rank_" + r, "faction": "ISEKAI leveling (reflavored live)",
                     "layer": "trait", "name": nm,
                     "does": "Leveling-granted rank tier; label/desc now Guild threat rating.",
                     "status": "reflavored-live", "contested": False, "desc": ""})
    return rows


def build_rows():
    rows = shipped_rows()
    seen = set(r["id"] for r in rows)
    for x in D:
        rid = "design_" + "".join(ch if ch.isalnum() else "_" for ch in (x["faction"] + "_" + x["name"]))[:70]
        assert rid not in seen, rid
        seen.add(rid)
        rows.append({"id": rid, "desc": "", **x})
    rows += isekai_rows()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true")
    args = ap.parse_args()

    rows = build_rows()
    prefill = {r["id"]: {"d": "parked" if r["status"] == "parked" else "keep", "n": ""}
               for r in rows}

    # decisions file: refuse once the owner has touched it
    if os.path.exists(DEC_OUT):
        try:
            existing = json.load(open(DEC_OUT, encoding="utf-8"))
        except ValueError:
            existing = {}
        if existing.get("savedAt") and not getattr(
                args, "i_know_this_overwrites_the_owners_decisions"):
            print("REFUSED: %s carries savedAt=%s - it holds the owner's decisions.\n"
                  "Re-run with --i-know-this-overwrites-the-owners-decisions to discard them."
                  % (DEC_OUT, existing.get("savedAt")))
        else:
            write_prefill(prefill)
    else:
        write_prefill(prefill)

    html = render_html(rows, prefill)
    os.makedirs(OUT_DIR, exist_ok=True)
    open(HTML_OUT, "w", encoding="utf-8").write(html)
    print("wrote %s (%d rows)" % (HTML_OUT, len(rows)))


def write_prefill(prefill):
    payload = {
        "sheet": "pawn_flavor_register",
        "posture": "design-review; default KEEP - a row left undecided ships as designed",
        "prefill": True,   # the page's own save replaces this with savedAt/decidedBy
        "rows": prefill,
    }
    json.dump(payload, open(DEC_OUT, "w", encoding="utf-8"), indent=1)
    print("wrote prefill %s (%d rows)" % (DEC_OUT, len(prefill)))


def render_html(rows, prefill):
    data_json = json.dumps(rows)
    prefill_json = json.dumps(prefill)
    tpl = open(os.path.join(os.path.dirname(__file__),
                            "pawn_flavor_register_template.html"), encoding="utf-8").read()
    return (tpl.replace("/*__DATA__*/[]", data_json)
               .replace("/*__PREFILL__*/{}", prefill_json)
               .replace("__DEC_NATIVE__", DEC_NATIVE.replace("\\", "\\\\"))
               .replace("__HTML_NATIVE__", HTML_NATIVE.replace("\\", "\\\\")))


if __name__ == "__main__":
    sys.exit(main())
