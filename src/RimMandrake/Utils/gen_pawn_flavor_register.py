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
for n, t in (("COMMON: Factory-Fresh", "Assembly: boring on purpose - the baseline roll. The default."),
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

# ---------------------------------------------------------------------------
# ROUND 6 — the volume mandate (owner, 2026-08-29): >=5 childhoods (1 COMMON),
# >=10 adulthoods (1 COMMON), >=15-trait pool per faction. Slates drafted from
# the INHABITED cast files (design/Jawa/bridge/INHABITED_CAST_*.md) by four
# subagents, reworked here. "<- name" = the cast character that inspired it.
# THIS GENERATOR IS THE ROSTER OF RECORD; the design doc keeps mechanics prose.
# ---------------------------------------------------------------------------

# shipped backstories the slates designated as their faction's COMMON one
COMMON_SHIPPED = {"Jawa_SandcrawlerBorn", "Jawa_FarmFostered", "Jawa_SunSwornChild",
                  "Jawa_ScrapSifter", "Jawa_SpringSworn", "Jawa_VatDecanted",
                  "Jawa_HatchedToTheLine"}

R6 = [  # (faction, layer, name, does[, contested])
 # Jawa Trade Moot
 ("Jawa Trade Moot", "childhood", "Still House-Bound", "Marked for the House at birth like every girl born there. <- Ubbi Sur"),
 ("Jawa Trade Moot", "adulthood", "COMMON: Fuel-Mixer", "Mixes to the ratio taught once, never varies, content. The boring default. <- Wupp"),
 ("Jawa Trade Moot", "adulthood", "Hem-Cutter", "Measures and logs every robe let down aboard; keeps the strips. <- Nurr"),
 ("Jawa Trade Moot", "adulthood", "Outrider Scout", "Forward runs into wrecks first; sleeps outside the hull. <- Ossik"),
 ("Jawa Trade Moot", "adulthood", "Ration-Keeper", "Weighs the crawler's water to the grain, takes the last share. <- Kutt"),
 # Deepwater Compact
 ("Deepwater Compact", "childhood", "COMMON: Jetty-Taught", "The four rules before the jetty: the measure, both hands, no violence, no asking. The default.", True),
 ("Deepwater Compact", "childhood", "Sea-Watcher's Child", "Grew up walking the stakes to a retreating waterline. <- Sethro Vekk"),
 ("Deepwater Compact", "adulthood", "COMMON: Jetty Hand", "Hauls, fills tankers, logs nothing memorable; most wardens are this.", True),
 ("Deepwater Compact", "adulthood", "Ledger Clerk", "Better at the books than the chair he wants, and everyone knows it. <- Perrik Osso-Vane"),
 ("Deepwater Compact", "adulthood", "The Sharing-Keeper", "Gives water away for a living; audited once, found perfect. <- Ilma Sook"),
 ("Deepwater Compact", "adulthood", "Salt-Pan Worker", "Exiled to the dying shore for a fight inside the walls; works it clean. <- Bosso Tharn"),
 ("Deepwater Compact", "adulthood", "Dirge-Singer", "Keeps the dead of the posting, one song per warden, in order. <- Ashaa Ottouk"),
 # the Junkers
 ("the Junkers", "childhood", "Shadow-Claimed", "The claim-code young: a wreck belongs to whoever's shadow touches it first. <- Fenzik Trawl"),
 ("the Junkers", "childhood", "Tally-Taught", "Carved a first tally at six; keeps count of everything since. <- Ossa Grell"),
 ("the Junkers", "childhood", "Sealed-Compartment Survivor", "Years alone in a wreck before being cut out; silence as survival. <- Weft"),
 ("the Junkers", "adulthood", "COMMON: Cut-Line Welder", "Same cut-line for decades, one opinion, no ambition; outlasts every foreman. <- Perra Tolm"),
 ("the Junkers", "adulthood", "Last-Fault Man", "Licensed to break one part into everything sold; paid twice for it. <- Vesh'kaa"),
 ("the Junkers", "adulthood", "Torch-Tuner", "Sets the cut-line, tunes torches to a chord, stops shifts over pitch. <- Modd Ryel"),
 ("the Junkers", "adulthood", "Shore-Tester", "Stands under the unshored bay first so others don't have to. <- Ketris Vahn"),
 ("the Junkers", "adulthood", "Death-Processor", "Processes the dead, nothing wasted; kindness and this, no contradiction. <- Prah Sook"),
 ("the Junkers", "adulthood", "Market Weigher", "Holds the scales on every legal bribe; incorruptible by fear of being found out. <- Rute Baan"),
 ("the Junkers", "trait", "Junk-Reckoner", "Mood/work speed scales with salvage mass held. Invented to fill the designed-trait floor.", True),
 # Galactic Empire
 ("Galactic Empire", "childhood", "COMMON: Farm Levy", "Conscripted farm youth, cheerful, nothing else recorded; joined for rations. The default. <- Bo Ander"),
 ("Galactic Empire", "childhood", "Conscript, No Next of Kin", "Anonymous intake, no family on file; feeds the helmet cult. <- Sixteen"),
 ("Galactic Empire", "adulthood", "COMMON: Garrison Clerk", "Loves the forms, no ambition; six years of requisition intake. <- Dova Nissik"),
 ("Galactic Empire", "adulthood", "Garrison Commander", "Writes every duty rota; will not move a man off shift, ever. <- Ovel Trask"),
 ("Galactic Empire", "adulthood", "Compliance Officer", "Memorizes the exemption schedule; enforces species policy downward with relish. <- Ivrek Sasso"),
 ("Galactic Empire", "adulthood", "Drill Instructor", "Bred-soldier melee elite; runs bayonet drill in brutal heat for nobody. <- Hesk Varo"),
 ("Galactic Empire", "adulthood", "Water-Plant Engineer", "Keeps condensers alive by forging her own requisitions. <- Weyla Torr"),
 # Blackstar Company
 ("Blackstar Company", "childhood", "COMMON: Dockside Ganger", "Docks, gangs, undentable cheerfulness; fast, lean, stupid. The default. <- Vidd Anselm"),
 ("Blackstar Company", "childhood", "Clan Herald's Child", "Nine years playing herald; learns the recital nobody else will do. <- Nel Sunta Rukh"),
 ("Blackstar Company", "childhood", "Cold-World Hunter's Cub", "First kill young; eats only what is taken, honor as diet. <- Ma'kesh Bruul"),
 ("Blackstar Company", "adulthood", "COMMON: Contract Registrar", "Genuinely boring; closes the register at the hour and does not reopen it. <- Ivve Odo"),
 ("Blackstar Company", "adulthood", "Boarding Bosun", "Sets frame, blows the wall, serves notice - alone, in that order. <- Vurgo Nakk"),
 ("Blackstar Company", "adulthood", "Sniper of the Writ", "One round per contract; will not fire outside the writ. <- Ruune Adlai"),
 ("Blackstar Company", "adulthood", "Boarding Medic", "Stabilizes the named mark first; the crew are not the deliverable. <- Yenevva Poll"),
 ("Blackstar Company", "adulthood", "Claims Adjuster", "Prices your death down to the escort discount; never wrong by much. <- Vessine Roal"),
 ("Blackstar Company", "adulthood", "Ship's Slicer", "Best door-and-lock hand in the Company; tempted to amend the archive. <- Nekk Arda"),
 ("Blackstar Company", "adulthood", "The Recoverer", "When a contract voids, takes the fee back off the client. <- Adann Ferro"),
 # Hutt Cartel
 ("Hutt Cartel", "childhood", "COMMON: Traded Young", "Handed to a household at seven, like all of them; no say in it. The default. <- Poul Adden-Adden"),
 ("Hutt Cartel", "childhood", "Kolto-Rig Ward", "Raised on rigs her people no longer own; approaching the unwilling forbidden. <- Sen Ilva"),
 ("Hutt Cartel", "adulthood", "COMMON: Dock Sorter", "Day-gang sorter; keeps her head down for years. The default. <- Tikka Vosh"),
 ("Hutt Cartel", "adulthood", "Refinery Foreman", "Eighty years on the same tower; recites every mistake you've made, in order. <- Bruk Oleen"),
 ("Hutt Cartel", "adulthood", "Dock Loadmaster", "The only one allowed to tell a Hutt factor he's wrong. <- Adda Wesh"),
 ("Hutt Cartel", "adulthood", "Ledger Factor", "Holds the paper on most of the list; pay and you are family. <- Ummu Sekk"),
 ("Hutt Cartel", "adulthood", "Customs Scanner", "Takes a small, unraised bribe to look away, for years, unbothered. <- Orrin Kwaad"),
 # Homestead Defense League
 ("Homestead Defense League", "childhood", "Trough-Taught", "Recites the free-well rule before working a valve; cannot break it even at cost. <- Ord Halloway"),
 ("Homestead Defense League", "childhood", "Ledger-Child", "Watched unpaid hauling become debt; sharp with favors and grudges. <- Bessa Trull"),
 ("Homestead Defense League", "adulthood", "COMMON: Vaporator Tender", "Keeps a modest string of condensers running; unremarkable. The default."),
 ("Homestead Defense League", "adulthood", "Unarmed Militia Captain", "Commands a company that has never deployed; contingency plans never run. <- Duro Vensk"),
 ("Homestead Defense League", "adulthood", "Arbiter of the Trough", "Settles disputes with no power to enforce them. <- Wenna Dask"),
 ("Homestead Defense League", "adulthood", "Stillmarket Factor", "Trades and hauls water for pay where water itself is free. <- Bessa Trull"),
 ("Homestead Defense League", "adulthood", "Quiet Tributary", "Secretly provisions a hostile neighbor; ashamed to admit it. <- Emm Dorrow"),
 ("Homestead Defense League", "adulthood", "Death-Bed Sitter", "Volunteers to comfort the dying, unmoved by it themselves. Dark register. <- Ren Ashek", True),
 # Deep Desert Tribes
 ("Deep Desert Tribes", "childhood", "Cutter's Apprentice", "Held the bowl for the debt-cutter from childhood; marked young. <- Ish'aal"),
 ("Deep Desert Tribes", "childhood", "Waterless-Crossed", "Survived the Waterless as a child; not all kin returned. <- Ghossa Tal-Vaar"),
 ("Deep Desert Tribes", "adulthood", "COMMON: Herd-Walker", "Ordinary herding labor earning walking-interest; most Tribe adults. The default."),
 ("Deep Desert Tribes", "adulthood", "Debt-Cutter", "Marks arrears into skin; trusted with a blade near a throat. <- Ish'aal"),
 ("Deep Desert Tribes", "adulthood", "Machine-Breaker", "Destroys offworld tech - delighted, not dutiful. <- Kuvv Raan"),
 ("Deep Desert Tribes", "adulthood", "Measure of the Raid", "Calls the litre-count and the halt, unmoved by anything around them. <- Ann'shu"),
 ("Deep Desert Tribes", "adulthood", "Unarmed Herald", "Rides ahead alone to recite the farm's own draw-figures. <- Uli Sheek"),
 ("Deep Desert Tribes", "adulthood", "Compulsive Claimant", "Cannot kill a person standing still; claims them as kin instead. <- Ess'kan"),
 # Wildsteam Clan
 ("Wildsteam Clan", "childhood", "Root-Gallery Raised", "Grew up in tunnels below the rows; open ground came near-adulthood. <- Tikk"),
 ("Wildsteam Clan", "childhood", "Water-Bought Ward", "Bought in from a dry homestead; converted late, overcompensates. <- Ossa Krail"),
 ("Wildsteam Clan", "adulthood", "COMMON: Row-Tender", "Ordinary terrace and crop-row labor; most Wildsteam adults. The default."),
 ("Wildsteam Clan", "adulthood", "Debt-Tallied Warden", "Kills only in defense; plants two trees per life taken, tallied publicly. <- Zesh Vool"),
 ("Wildsteam Clan", "adulthood", "Sole Grievance-Walker", "Travels days alone to deliver one wronged sentence; never complains otherwise. <- Nnu Pell"),
 ("Wildsteam Clan", "adulthood", "Toll-Keeper of the Stair", "Sets and enforces prices without exception. <- Ohrra"),
 ("Wildsteam Clan", "adulthood", "Oath-Breaker's Cook", "Secretly feeds outsiders against clan ruling; can't keep the secret. <- Pell Yoon"),
 # Geonosian Foundry Hive
 ("Geonosian Foundry Hive", "childhood", "Ledger-Given", "Drone given accounts young for weak mandibles; intellect floor, melee-weak. <- Ovv'gan"),
 ("Geonosian Foundry Hive", "childhood", "Arena-Blooded", "Volunteered for the arena - the one route up; restless off small posts. <- Rrekk"),
 ("Geonosian Foundry Hive", "childhood", "Chamber-Selected", "Groomed for the queen's chamber since four, never outdoors; social elite. <- Qu'raa"),
 ("Geonosian Foundry Hive", "adulthood", "COMMON: Seam Drone", "One assigned station, shift after shift, nothing more expected. The default. <- Ttun"),
 ("Geonosian Foundry Hive", "adulthood", "Records Clerk", "Files what the caste requires regardless of whether anyone reads it. <- Ovv'gan"),
 ("Geonosian Foundry Hive", "adulthood", "Void Communicant", "Plateau-cult intellectual; psychic-sensitivity synergy. <- Zzir"),
 ("Geonosian Foundry Hive", "adulthood", "Body-Forged Machinist", "Crafting elite; self-replaces lost limbs with alloy. <- Gizzek Vor"),
 ("Geonosian Foundry Hive", "adulthood", "Verifier-Enforcer", "Melee and interrogation; tests claims personally. <- Grask"),
 ("Geonosian Foundry Hive", "adulthood", "Quartermaster", "Trade and logistics; skims a cut and can justify it. <- Traxx"),
 # Ascendant Helix
 ("Ascendant Helix", "childhood", "Terrace-Groomed", "Bred as the scheduled correction of a prior line, told so constantly. <- Ossa-Four"),
 ("Ascendant Helix", "childhood", "Annex-Raised", "Born among the struck-off; learns the doctrine that discarded them. <- Grandmother 2-C"),
 ("Ascendant Helix", "adulthood", "COMMON: Line Labourer", "The Made: menial obedient work; follows any voice carrying authority. The default. <- Ladder 9-D"),
 ("Ascendant Helix", "adulthood", "Vat Attendant", "Pulls decants from the tank; numbed medical routine. <- Ollo Wen"),
 ("Ascendant Helix", "adulthood", "Discontinuation Officer", "Social elite; delivers the news a line is cut. <- Prith Vane"),
 ("Ascendant Helix", "adulthood", "Record-Keeper", "Reads the discontinued list daily; great-memory doctrine role. <- Ollun Bex"),
 ("Ascendant Helix", "adulthood", "Body Auditor", "Itemizes the cost of every curator's gene-work. <- Kesh Mubb"),
 ("Ascendant Helix", "adulthood", "Annex Warden", "Self-built strength after improvement was denied. <- Sella Kro"),
]

R6_DROIDS = [  # parked with DROID_SYSTEM_EMBRACE_1, like the rest of the droid set
 ("adulthood", "COMMON: Post & Ledger", "Logs, carries, counts; no distinguishing skill, no story attached. The default. <- Gate Log Four"),
 ("adulthood", "Pilgrim's Herald", "Self-appointed oratory elite. <- The Magnificent Oro"),
 ("adulthood", "Mercy Wipe", "Performs memory wipes on request; Continuity-Protocol-adjacent. <- Mercy Nine"),
 ("adulthood", "Line Command", "Shooting elite, self-promoted, unquestioned. <- Captain Fourteen"),
 ("trait", "Continuity-Bound", "Mood/dignity tied to self-ownership doctrine. NEW, no doc source yet.", True),
 ("trait", "Chassis-Proud", "Mood from own parts/upgrade quality vs rivals. NEW, no doc source yet.", True),
 ("trait", "Wipe-Averse / Wipe-Ready", "Degree pair: dread vs peace with memory wipe. NEW, no doc source yet.", True),
]

# 15-trait pools: EXISTING-mod picks per faction ("label(defName) - why").
# Faction-designed traits already have their own rows and complete each pool.
POOLS = {
 "Jawa Trade Moot": [
  ("greedy (Greedy)", "extracting every credit is the trade philosophy"),
  ("ascetic (Ascetic)", "Still House and hard-crawler austerity"),
  ("hard worker (Industriousness)", "the crawler never stops needing hands"),
  ("great memory (GreatMemory)", "ledgers of prices and units"),
  ("abrasive (Abrasive)", "chiefs, appraisers, water-wardens all bark"),
  ("too smart (TooSmart)", "brokers, appraisers, scheme-navigators"),
  ("nimble (Nimble)", "outriders and speeder-bike culture"),
  ("jealous (Jealous)", "marriage-broker doctrine applied to people"),
  ("kleptomaniac (VTE_Kleptomaniac)", "thieving as a virtue per the faith"),
  ("gourmand (Gourmand)", "the water-warden's forbidden hunger"),
  ("night owl (NightOwl)", "swap-meet cries run nine hours"),
  ("wanderlust (VTE_Wanderlust)", "the offworlder-shadow itch"),
 ],
 "Deepwater Compact": [
  ("ascetic (Ascetic)", "the faith's default; used deliberately, not universally"),
  ("abrasive (Abrasive)", "custodians and wardens"),
  ("kind (Kind)", "the sharing-keepers"),
  ("great memory (GreatMemory)", "ledgers, manifests, the Accord recitation"),
  ("too smart (TooSmart)", "clerks and arbiters"),
  ("fast learner (FastLearner)", "jetty apprenticeships"),
  ("delicate (Delicate)", "amphibian frames out of water"),
  ("gourmand (Gourmand)", "the one licensed excess a year"),
  ("jealous (Jealous)", "private ledgers, silent grudges"),
  ("brawler (Brawler)", "the cast is not pacifist by temperament"),
  ("pessimist (NaturalMood)", "dying-shore fatalism"),
 ],
 "the Junkers": [
  ("cannibal (Cannibal)", "nothing wasted - not the meat either"),
  ("masochist (Masochist)", "appetite for the near-miss"),
  ("psychopath (Psychopath)", "no cruelty in it anywhere"),
  ("tough (Tough)", "casket culture, wreck-field survival"),
  ("hard worker (Industriousness)", "the yard runs on it"),
  ("great memory (GreatMemory)", "ledgers and tallies"),
  ("abrasive (Abrasive)", "half the Strip"),
  ("greedy (Greedy)", "claim-code culture"),
  ("body modder (Transhumanist)", "the casket embrace"),
  ("ascetic (Ascetic)", "the Weight's austerity"),
  ("undergrounder (Undergrounder)", "wreck-field and sealed-compartment dwellers"),
  ("occultist (Occultist)", "the Bolt That Missed; relic veneration"),
 ],
 "Galactic Empire": [
  ("ascetic (Ascetic)", "the Order's ration discipline"),
  ("abrasive (Abrasive)", "compliance culture"),
  ("too smart (TooSmart)", "staff officers"),
  ("great memory (GreatMemory)", "rota-writers and clerks"),
  ("hard worker (Industriousness)", "bureaucratic workhorse baseline"),
  ("mood spectrum (NaturalMood)", "the cast's dominant axis"),
  ("kind (Kind)", "the rare decent garrison hand"),
  ("delicate (Delicate)", "desk officers"),
  ("tough (Tough)", "garrison soldier stock"),
  ("shooting spectrum (ShootingAccuracy)", "marksmen and levies both"),
  ("nerves spectrum (Nerves)", "anonymity-cult discipline under fire"),
  ("psychopath (Psychopath)", "the Inquisitorial caste"),
 ],
 "Blackstar Company": [
  ("ascetic (Ascetic)", "the Code's discipline"),
  ("abrasive (Abrasive)", "registrars and recoverers"),
  ("great memory (GreatMemory)", "heralds and adjusters"),
  ("too smart (TooSmart)", "slicers and claims desks"),
  ("brawler (Brawler)", "boarding parties"),
  ("cannibal (Cannibal)", "the Trandoshan hunter shape"),
  ("masochist (Masochist)", "'the Penalty'"),
  ("jealous (Jealous)", "crew rivalries"),
  ("gourmand (Gourmand)", "hunters who eat what is taken"),
  ("shooting spectrum (ShootingAccuracy)", "writ discipline vs dock-gang spray"),
  ("delicate (Delicate)", "the desk half of the Company"),
  ("beautiful (Beauty)", "the bought face"),
  ("body modder (Transhumanist)", "bought pieces"),
 ],
 "Hutt Cartel": [
  ("abrasive (Abrasive)", "foremen and loadmasters"),
  ("great memory (GreatMemory)", "eighty years of your mistakes, in order"),
  ("ascetic (Ascetic)", "the working floor's austerity"),
  ("chemical interest (DrugDesire)", "the dock's small comforts"),
  ("gourmand (Gourmand)", "appetite as culture"),
  ("mood spectrum (NaturalMood)", "the sorter's resignation"),
  ("kind (Kind)", "kindness inside the machine"),
  ("too smart (TooSmart)", "ledger factors"),
  ("jealous (Jealous)", "household rank-watching"),
  ("brawler (Brawler)", "the margrave shape"),
  ("beautiful (Beauty)", "the margrave shape, again"),
  ("psychopath (Psychopath)", "the unbothered bribe-taker"),
  ("tycoon (VTE_Tycoon)", "the Cartel shape itself"),
 ],
 "Homestead Defense League": [
  ("ascetic (Ascetic)", "water-disciplined default; 10 of 25 cast"),
  ("kind (Kind)", "matrons and arbiters"),
  ("abrasive (Abrasive)", "trough disputes"),
  ("great memory (GreatMemory)", "grudge-keepers"),
  ("too smart (TooSmart)", "the militia planner"),
  ("jealous (Jealous)", "well-rights envy"),
  ("nerves spectrum (Nerves)", "militia discipline"),
  ("mood spectrum (NaturalMood)", "spread across the cast"),
  ("careful shooter (ShootingAccuracy)", "the captain's range habit"),
  ("brawler (Brawler)", "bar-tesh muscle"),
  ("delicate (Delicate)", "the frail and the dying-sitters"),
  ("hard worker (Industriousness)", "subsistence farm ethic"),
  ("brave (VTE_Brave)", "militia volunteers"),
  ("technophobe (VTE_Technophobe)", "provincial homestead distrust"),
 ],
 "Deep Desert Tribes": [
  ("ascetic (Ascetic)", "near-universal across the cast"),
  ("masochist (Masochist)", "the Waterless survivors"),
  ("abrasive (Abrasive)", "raid-callers"),
  ("great memory (GreatMemory)", "debt recited by heart"),
  ("cannibal (Cannibal)", "law-sanctioned"),
  ("psychopath (Psychopath)", "the Measure's stillness"),
  ("too smart (TooSmart)", "heralds and cutters"),
  ("jealous (Jealous)", "kin-claim culture"),
  ("body modder (Transhumanist)", "the machine-breaker's irony"),
  ("delicate (Delicate)", "the marked and the frail"),
  ("careful shooter (ShootingAccuracy)", "cliff-line marksmen"),
  ("brawler (Brawler)", "close-raid shapes"),
 ],
 "Wildsteam Clan": [
  ("kind (Kind)", "the feeding, healing half of the clan"),
  ("abrasive (Abrasive)", "wardens and toll-keepers"),
  ("great memory (GreatMemory)", "near-universal"),
  ("ascetic (Ascetic)", "vow-keepers"),
  ("masochist (Masochist)", "penitent shapes"),
  ("jealous (Jealous)", "stair-toll rivalries"),
  ("gourmand (Gourmand)", "harvest-feast culture"),
  ("too smart (TooSmart)", "the bought-in minds"),
  ("delicate (Delicate)", "the grief-walkers"),
  ("chemical fascination (DrugDesire)", "the ferment-tender"),
  ("mood spectrum (NaturalMood)", "spread across the cast"),
 ],
 "Geonosian Foundry Hive": [
  ("hard worker (Industriousness)", "caste-mandated output"),
  ("undergrounder (Undergrounder)", "hatched in the seams"),
  ("abrasive (Abrasive)", "foreman bluntness"),
  ("great memory (GreatMemory)", "recurs across the cast"),
  ("too smart (TooSmart)", "outcaste intellects"),
  ("ascetic (Ascetic)", "drone self-denial"),
  ("psychopath (Psychopath)", "cold caste enforcement"),
  ("masochist (Masochist)", "arena and plateau culture"),
  ("body modder (Transhumanist)", "alloy self-replacement"),
  ("jealous (Jealous)", "caste rivalry"),
  ("mood spectrum (NaturalMood)", "wide variance in cast"),
  ("psychic sensitivity ladder (PsychicSensitivity)", "Rakatan-ruin exposure"),
  ("tough (Tough)", "chitin"),
 ],
 "Ascendant Helix": [
  ("too smart (TooSmart)", "near-universal among curators"),
  ("abrasive (Abrasive)", "auditors"),
  ("ascetic (Ascetic)", "doctrine trait"),
  ("great memory (GreatMemory)", "recorder caste"),
  ("jealous (Jealous)", "caste envy"),
  ("body modder (Transhumanist)", "the core doctrine"),
  ("beauty spectrum (Beauty)", "curated aesthetics"),
  ("psychopath (Psychopath)", "clinical detachment"),
  ("mood spectrum (NaturalMood)", "wide range across cast"),
  ("delicate (Delicate)", "fragile Made lines"),
  ("kind (Kind)", "rare genuine warmth"),
  ("cannibal (Cannibal)", "doctrine-justified disposal of failed decants"),
 ],
 "Droids (PARKED: DROID_SYSTEM_EMBRACE_1)": [
  ("great memory (GreatMemory)", "perfect recall of service-years"),
  ("too smart (TooSmart)", "the calculating chassis"),
  ("ascetic (Ascetic)", "low-maintenance chassis culture"),
  ("abrasive (Abrasive)", "quartermasters"),
  ("jealous (Jealous)", "parts and gyro envy"),
  ("body modder (Transhumanist)", "more natural on a droid than an organic"),
  ("nerves spectrum (Nerves)", "control-loop stability under fire"),
  ("shooting spectrum (ShootingAccuracy)", "war chassis vs salvage frames"),
  ("brawler (Brawler)", "the thing in trench four"),
  ("industriousness spectrum (Industriousness)", "duty-cycle flavor"),
  ("tough (Tough)", "armored war chassis"),
  ("nimble (Nimble)", "the fastest thing on the plateau"),
 ],
}

for fac, layer, name, does, *c in R6:
    d(fac, layer, name, does, status="designed-xml", contested=bool(c and c[0]))
for layer, name, does, *c in R6_DROIDS:
    d(DP, layer, name, does, status="parked", contested=bool(c and c[0]))
for fac, picks in POOLS.items():
    for label, why in picks:
        D.append({"faction": fac, "layer": "trait", "name": label,
                  "does": "POOL PICK: " + why + ".", "status": "pool-pick",
                  "contested": False})

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
            dn = bs.findtext("defName")
            rows.append({
                "id": dn,
                "faction": FACTION_OF_CAT[cat],
                "layer": "childhood" if slot == "Childhood" else "adulthood",
                "name": ("COMMON: " if dn in COMMON_SHIPPED else "") + bs.findtext("title"),
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
