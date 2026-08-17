#!/usr/bin/env python3
"""Rename every faction on Ash'karr.

The generated names ("Thiussia Compact", "Hive of Ko'coclak", "Koulbobel Kinship")
are what the world map draws in Faction Territories mode and under every settlement
marker, so they are the most-read text on the planet - and they are worldgen noise.

Our 14 ratified factions get their real names. The rest still EXIST - they are
never deleted, because deleting a faction tears the save's reference graph - and
they still generate raids, traders and events, so they get names that belong on
this planet instead of fantasy-generator output.

    python3 src/RimMandrake/Utils/name_ashkarr_factions.py [--dry]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SAVE = os.path.join(REPO, "world", "WORLDMAP_gen.rws")
GAME = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/Saves/WORLDMAP_gen.rws")

# our 14, from the ratified keep list
OURS = {
    # the ratified 14 - FACTION_SPEC.md "The 14 factions". Labels are the spec's.
    "Empire":                          "The Galactic Empire",
    "OutlanderCivil":                  "Homestead Defense League",
    "TribeCivil":                      "Deep Desert Tribes",
    "Pirate":                          "Blackstar Company",
    "Jawa_HuttCartel":                 "Hutt Cartel",
    "Jawa_FreeDroidEnclaves":          "Free Droid Enclaves",
    "Jawa_WildsteamClan":              "Wildsteam Clan",
    "Jawa_DeepwaterCompact":           "Deepwater Compact",
    "Jawa_GeonosianFoundryHive":       "Geonosian Foundry Hive",
    "Jawa_AscendantHelix":             "Ascendant Helix",
    "Jawa_IndigenousTribes":           "Jawa Trade Moot",
    "Jawa_Junkers":                    "the Junkers",
    "Mechanoid":                       "the Forgotten Arsenal",
    "Insect":                          "the Unbound Hive",
}

# everything else, named so nothing on screen breaks the setting
OTHERS = {
    "SplinterColony": "Wreck Camp", "CASacrilegHunters": "The Tomb Robbers",
    "Horrors": "The Sharp Swarm", "GR_RoamingMonstrosities": "Dune Horrors",
    "ABYautjaClan": "The Trophy Takers", "ABYautjaModderClan": "The Scarred",
    "ABYautjaBerserkClan": "The Blood Hunt", "ABYautjaBadBloodClan": "The Outcast Hunt",
    "OutlanderCivil": "Wellstead", "AG_OutlanderCivilUnion": "The Waterline Union",
    "OutlanderRoughPig": "Sty Nine", "DV_OutlanderRoughBuzzer": "The Drone Hive",
    "KAR_OrcClan": "The Bonepickers",
    "VRESaurids_OutlanderRoughSaurid": "The Scaled Concord",
    "BS_LittlePeople": "The Small Folk", "BS_Niflheim": "Coldhold",
    "BS_Dvergr_Medieval_Union": "The Deepsmiths", "BS_Muspelheim": "Emberhold",
    "TribeCivil": "The Grey Fox Moot", "VFEP_Junkers": "The Scrap Crews",
    "VFEP_Mercenaries": "The Contract Guns", "OuterRim_RebelAlliance": "The Rebellion",
    "BS_OgreFaction": "The Great Ones", "TribeRoughNeanderthal": "The Old Blood",
    "TribeSavageImpid": "The Cinder Tribe", "PirateYttakin": "The Fur Corsairs",
    "PirateWaster": "The Rot Fleet", "DV_PirateKeshig": "The Black Riders",
    "AG_XenohumanPirates": "The Night Market", "Mechanoid": "The Iron Choir",
    "Insect": "The Deep Hive", "Entities": "The Dark", "BS_ZombieFaction": "The Lost",
    "DA_Troll": "The Stone Eaters", "AA_BlackHive": "The Black Hive",
    "BMT_PustuleHornets": "Pustule Hornets", "Ancients": "The Forsaken",
    "AncientsHostile": "The Forsaken Guard", "HoraxCult": "The Servants of Horax",
    "AM_EnemyPirate": "The Strife Band", "TribalHostile": "Raiding Tribe",
    "DP_GenericHostile": "Raiders", "VRE_Archons": "The Archons",
    "TradersGuild": "The Voidborn Cartel", "Salvagers": "The Grey Reapers",
}


def main():
    dry = "--dry" in sys.argv
    text = open(SAVE, encoding="utf-8").read()
    i = text.find("<allFactions>")
    j = text.find("</allFactions>", i)
    seg = text[i:j]

    changed, missed = 0, []

    def one(mo):
        nonlocal changed
        defname, mid, old = mo.group(1), mo.group(2), mo.group(3)
        new = OURS.get(defname) or OTHERS.get(defname)
        if not new:
            missed.append((defname, old))
            return mo.group(0)
        if new != old:
            changed += 1
        tag = " ⭐" if defname in OURS else ""
        print("  %-34s %-28s -> %s%s" % (defname, old[:28], new, tag))
        return "<def>%s</def>%s<name>%s</name>" % (defname, mid, new)

    seg = re.sub(r"<def>([\w.]+)</def>(\s*)<name>([^<]*)</name>", one, seg)
    text = text[:i] + seg + text[j:]

    print("\nrenamed %d factions" % changed)
    if missed:
        print("NOT in either table, left alone:")
        for dn, old in missed:
            print("   %-34s %s" % (dn, old))

    if dry:
        print("\n--dry: nothing written")
        return
    open(SAVE, "w", encoding="utf-8").write(text)
    with open(SAVE, "rb") as a, open(GAME, "wb") as b:
        b.write(a.read())
    print("wrote and deployed")


if __name__ == "__main__":
    main()
