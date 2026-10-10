#!/usr/bin/env python3
"""MOD_OPTIONS_RETROFIT_1 offline check for the SettingsKit settings screens retrofitted onto a mod's own Mod file.

For each mod listed in MODS below: every setting the settings class Scribes sits inside exactly one named Group(...) block whose
names array lists it (so it collapses, searches and resets with its group); every control drawn in a block is listed by it;
groups are brace-balanced and do not swallow the next group; the group scope tags equal the AUDITED scopes recorded here (the
audit is per setting, against its read site: a worldgen step is NewMapsOnly, a Gale-onset or storyteller-roll read is
NextPulse, a tick/job/patch read is Now); the SettingsKit files are in the csproj; the shippedDefaults snapshot exists.
Then plants one defect at a time per mod and requires the check to fail on each.

Add a mod by adding one entry to MODS.     python3 src/RimMandrake/Utils/selftest_settings_screens.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# folder, mod .cs, csproj, expected groups: title -> scope (the audited scopes)
# folder: (mod .cs, csproj, expected groups, extra setting names the screen resets that are not Scribe_Values fields)
MODS = {
    "BlueDesert": ("RM_BlueDesertMod.cs", "RM_BlueDesert.csproj", {
        "Mod switch": "Now",
        "Natives, flora detonations and cues": "Now",
        "Flora roster": "NextGameStart",
        "Vhaulk": "Now",
        "Vhaulk road and stay lengths": "NextPulse",
        "Blue Desert weathers": "NextPulse",
        "Haze and blue-ice thaw": "Now",
        "Murrek burial": "NextPulse",
        "Blue-ice cold rack": "Now",
        "The ablation line": "NextPulse",
        "Ossivel and virr song": "Now",
    }, ()),
    "FloodedCanyon": ("RM_FloodedCanyonMod.cs", "RM_FloodedCanyon.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Flood cycle": "Now",
        "Warning: chimes and signs": "Now",
        "Flood timing": "NextPulse",
        "Soaked ground": "Now",
        "Fossil seams (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Muttavaq": "Now",
        "After the water recedes": "NextPulse",
        "Native plants": "NextGameStart",
        "Zennaq and lightning": "Now",
        "Refuge ledges and carvings": "Now",
        "Cliff ledges (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),
    "HugeThings": ("RM_HugeThingsSettings.cs", "RM_HugeThings.csproj", {
        "Giant plants": "Now",
        "Giant animals: hitbox and roofs": "Now",
        "Large Pawns footprint and custom size tiers": "NextGameStart",
        "Wake and plant smashing": "Now",
        "Yield curve": "Now",
        "Titanic corpse sites": "Now",
    }, ()),
    "GimmeSomeSlack#Cables": ("GimmeSomeSlackMod.cs", "RimMandrake_GimmeSomeSlack.csproj", {
        "Messy cords and default style": "Now",
        "Slack, loops and tangles": "Now",
        "Breaks and sparks": "Now",
        "Wind sway": "Now",
        "Far zoom and debug": "Now",
    }, ()),
    "GimmeSomeSlack#Aerial": ("Aerial/AerialSettings.cs", "RimMandrake_GimmeSomeSlack.csproj", {
        "Overhead power lines": "Now",
        "Wire sway": "Now",
        "Damage, shock and alerts": "Now",
        "Power-tap clamps": "Now",
    }, ()),
    "GimmeSomeSlack#Hose": ("Hose/HoseSettings.cs", "RimMandrake_GimmeSomeSlack.csproj", {
        "Flexible hoses": "Now",
        "Hose length and shape": "Now",
        "Colonists carrying hoses": "Now",
        "Look and FlowWorks": "Now",
    }, ()),
    "Graffiti": ("RM_GraffitiMod.cs", "Graffiti.csproj", {
        "Painting": "Now",
        "Viewer reactions": "Now",
        "Raiders": "Now",
        "Cleaning": "Now",
    }, ()),
    "LeaningScrub": ("RM_LeaningScrubMod.cs", "RM_LeaningScrub.csproj", {
        "Mod and venomvine passability": "Now",
        "The Stall and the Gale": "Now",
        "Gale raid weighting": "NextPulse",
        "Twitcher venomvine": "Now",
        "Smother-craft": "Now",
        "The Lean (wind heading)": "Now",
        "Venomvine rooms and the runway bloom": "Now",
        "Sweetline trees": "Now",
        "Sweetline trees on new maps": "NewMapsOnly",
        "Vissler arms and fire-stamping giants": "Now",
        "Venomvine forms": "Now",
        "Forms that act when the Gale starts": "NextPulse",
    }, ()),
    "LanternDeeps": ("LanternDeepsMod.cs", "RM_LanternDeeps.csproj", {
        "Entrances: cave mouth and ruined mineshaft": "NewMapsOnly",
        "Darkness inside a Deep": "Now",
        "Newly generated Deeps: crystal, dead and galuush": "NewMapsOnly",
        "Flora and deposits": "Now",
        "Shard-minds, Orun-Ghal and the Answering": "Now",
        "Methane, the Creep and Cleavers": "Now",
        "Aurora, roofs and cave fauna": "Now",
        "Entrance biomes (world generation)": "NewMapsOnly",
    }, ("entranceBiomes",)),
    "Greentide": ("RM_GreentideMod.cs", "RM_Greentide.csproj", {
        "Churnmud and the mire": "Now",
        "Jungle density": "NewMapsOnly",
        "World-map movement": "Now",
        "Cross-biome opt-in (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "The Frenzy": "Now",
        "Jungle grenades": "Now",
        "Canopy swarm (the krannock)": "Now",
        "Stellock lace": "Now",
        "The shoal (the illisk)": "Now",
        "The false bank (the vurrak)": "Now",
        "The canopy-breaker (the thurrock)": "Now",
        "The Roil (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Greatbole fruitfall and harvest ladder": "Now",
        "Greatbole seeds and servants": "NextGameStart",
    }, ()),
    "Miasma": ("RM_MiasmaMod.cs", "RM_Miasma.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Warden mother young": "Now",
        "Predators and pollination": "Now",
        "Flotsam in the root-lines": "Now",
        "Attar: still, glaze and balm": "Now",
        "Decay cells and the rotting bed": "Now",
        "The mother's price": "Now",
    }, ()),
    "Abyss": ("RM_AbyssMod.cs", "RM_Abyss.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Gharreks, sorters and krizzaks": "Now",
        "Sorter dens on new maps": "NewMapsOnly",
        "Summs and ombrathias": "Now",
        "Ishvariths and light": "Now",
        "The Dark": "Now",
        "Etchfall": "Now",
        "The hidden ship": "Now",
        "Wickwood lamp crops": "NextGameStart",
        "Fold-lamps": "Now",
        "Heat-folding discovery": "NextGameStart",
        "Sound": "Now",
        "Cryptid signs": "Now",
        "Brood lair switch": "Now",
        "Brood lair details (fixed at map generation)": "NewMapsOnly",
        "Stolen egg and bonded summ": "Now",
    }, ()),
    "Contagion": ("RM_ContagionMod.cs", "RM_Contagion.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Genome growing and the Unfinished": "Now",
        "The Burn": "Now",
        "Burn frequency": "NextPulse",
        "The Coalescence": "Now",
        "Draftprints": "Now",
        "Helix contract pay": "NextPulse",
        "Helix devices": "Now",
    }, ()),
    "Cauldron": ("RM_CauldronMod.cs", "RM_Cauldron.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Metal in the trees": "Now",
        "Vent bloom exposure": "Now",
        "Vexxiss behaviour": "Now",
        "Nettle shorelines": "Now",
        "Ground vents (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Vents and what hangs on them": "Now",
        "Vent silence length": "NextPulse",
        "Dewfall": "Now",
        "Flora expansion and fexxil venom": "NextGameStart",
        "Vexxith acid-proofing": "Now",
        "Acid-proof vexxith door": "NextGameStart",
    }, ()),
    "Pyrelands": ("RM_PyrelandsMod.cs", "FireEcologyHook.csproj", {
        "Mod enabled": "Now",
        "Fulgurite, loose ash and scorch-fruit": "Now",
        "Ash accumulation (Ash Fall / Cinderfall weather)": "Now",
        "Plant art and wild flora": "Now",
        "Scorched ruins (new maps)": "NewMapsOnly",
        "Biome placement (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Absorbed mechanics (mandrake.rut.pyrelandsmechanics)": "Now",
        "Furnace-beast herds at world start (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Giants and recipe costs (restart)": "NextGameStart",
        "Burrowers": "Now",
        "Lightning breakers and sand shovelling": "Now",
        "Cross-biome ash accumulation": "Now",
    }, ()),
    "GelatinousSlime": ("SlimeMod.cs", "RM_GelatinousSlime.csproj", {
        "The gene archive": "Now",
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Flavour": "Now",
        "Slimification and fields": "Now",
        "Ruined farms (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Joining Water ring": "Now",
        "Visitors": "Now",
        "Creatures and the slime pit": "Now",
        "Titanoslime chunks and the archive vat": "Now",
        "The titanoslime": "Now",
        "Titanoslime rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),
    "TheRot": ("RM_TheRotMod.cs", "RM_TheRot.csproj", {
        "The Rot enabled": "Now",
        "Sheen, rot, heat and spores": "Now",
        "Wild spawns and kin bonds (restart)": "NextGameStart",
        "Giant: the hwelgrue": "Now",
        "Ship: the swallowed navigator": "Now",
        "Technology: the gut-mother and the unjoining draught": "Now",
        "Cross-biome opt-in": "Now",
    }, ()),
    "TheForge": ("RM_TheForgeMod.cs", "RM_TheForge.csproj", {
        "The Forge enabled": "Now",
        "Weather pulse and grand cycle": "Now",
        "Keelwork and spunstone study": "Now",
        "Spunstone door and hull (restart)": "NextGameStart",
        "Voices and the dhuvvox": "Now",
        "White plume fronts": "Now",
        "Vapour columns and sky creatures": "Now",
        "The dhokkur": "Now",
        "Not wired yet (these change nothing)": "Now",
    }, ()),
    "ShipVermin": ("RM_ShipVerminMod.cs", "RM_ShipVermin.csproj", {
        "Alert and fuel mites": "Now",
        "Wreck-anchored vermin nests": "Now",
        "Species a wreck nest may produce": "Now",
    }, ()),
    "Wasteland": ("RM_WastelandMod.cs", "RM_Wasteland.csproj", {
        "Wasteland master switch": "Now",
        "Storms": "Now",
        "Ambient dose and radiothermal heat": "Now",
        "Processor animals": "Now",
        "Grippers": "Now",
        "The Middenshell": "Now",
        "Waste casks and the sealed cask bay": "Now",
        "Rite of Tipping": "Now",
        "Not wired yet (these change nothing)": "Now",
    }, ()),
    "SolarMirrors": ("RM_SolarMirrorsMod.cs", "RM_SolarMirrors.csproj", {
        "Mirror light": "Now",
        "Appearance": "Now",
        "Uses": "Now",
        "Ancient mirror fields (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Upkeep": "Now",
        "Work and timing": "Now",
    }, ()),
    "WreckedMachines": ("WreckedMachinesMod.cs", "RM_WreckedMachines.csproj", {
        "Research and material costs": "Now",
        "The grade ladder": "Now",
        "The alloy forge": "Now",
        "Architect menu (restart)": "NextGameStart",
    }, ()),
    "Webwork": ("RM_WebworkMod.cs", "RM_Webwork.csproj", {
        "World generation (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Emergent spawn": "Now",
        "Guaranteed nest (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Egg economy": "Now",
        "Creeping front and thrixweave (restart)": "NextGameStart",
        "Urraveth remains: new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "The dead giant (urraveth remains)": "Now",
    }, ()),
    "Warcasket": ("RM_WarcasketSettings.cs", "RM_Warcasket.csproj", {
        "Warcasket master switch": "Now",
        "Suit failure and hazardous water": "Now",
        "Sarcophagi": "Now",
        "Cask bay and core dose": "Now",
        "Sealed corpses on new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),

    "RustCathedral": ("RustCathedral/RM_RustCathedralMod.cs", "RustCathedral/RM_RustCathedral.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly", "Cathedral roaches": "Now",
        "The borehulk on new maps (WORLDGEN-AFFECTING)": "NewMapsOnly", "Borehulk grinding": "Now",
        "Canal eels and dried-out dead on new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Not wired yet (these change nothing)": "Now"}, ()),
    "RustCathedral#Hum": ("Hum/RustCathedralHumSettings.cs", "Hum/RimMandrake.RustCathedral.Hum.csproj", {
        "The hum and the Cathedral's standing": "Now", "Living bolts": "Now", "The canals": "Now",
        "Drilling the deep metal": "NextPulse", "Under the plate": "Now", "How long the roll lasts": "NextPulse",
        "Bolts on the hull": "Now"}, ()),
    "RustCathedral#Walls": ("Walls/RustCathedralWallsSettings.cs", "Walls/RimMandrake.RustCathedral.Walls.csproj", {
        "Wall tiers and sacred walls (WORLDGEN-AFFECTING)": "NewMapsOnly", "Live Pattern Metal": "Now"}, ()),
    "Scarlands": ("RM_WarscarMod.cs", "RM_Warscar.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Broken turrets": "Now",
        "Old-line turret tuning": "NextGameStart",
        "Totchak (wall colossus)": "Now",
        "Inscribed panels: placement (old tongue)": "NewMapsOnly",
        "Inscribed panels: reading": "Now",
        "Hospice (kneeling chassis and cradle)": "Now",
        "Hospice: chassis placement": "NewMapsOnly",
        "Rainbow pools": "Now",
        "Rainbow pools: placement": "NewMapsOnly",
        "Chotrix (invisible hunter)": "Now",
        "Chotrix: placement": "NewMapsOnly",
        "Lacquered cloaks": "Now",
        "The Settling (calm-triggered war fallout)": "Now",
        "War dust and buried shells": "Now",
        "Buried shells: placement": "NewMapsOnly",
        "Geiger choir (Warscar soundscape)": "Now",
        "The Warscar mark": "Now",
        "The Warscar mark: trade": "NextGameStart",
        "The chatrak's snap": "Now",
        "The chatrak's snap: turning speed": "NextGameStart",
        "Loosened wall panels": "Now",
        "Loosened wall panels: placement": "NewMapsOnly",
        "Aerosol screens": "Now",
        "Projector rings": "Now",
        "Projector rings: placement": "NewMapsOnly",
        "Species (restart required)": "NextGameStart",
        "Bileworm gas": "Now",
        "Wreck-lichen": "Now",
        "Cross-biome opt-in": "Now",
    }, ()),
    "TerminalBiomes": ("RM_TerminalBiomesMod.cs", "RM_TerminalBiomes.csproj", {
        "Mod and biome switches": "Now",
        "The Scald's kit": "Now",
        "The Scald's map-generation scatter (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "The Chill's growers and wax procession": "Now",
        "The suulk (TWILIGHT_DANGER_LIGHTWEB_1)": "NextPulse",
        "The vaulisk lure (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Vaulisk reveal": "Now",
        "Pane strikes (TWILIGHT_PANE_STRIKE_1)": "NextPulse",
        "Deck accumulation (TWILIGHT_PANE_STRIKE_1)": "Now",
        "The Twilight Sea's light economy": "Now",
        "Floor flora placement (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Floor flora light behaviour": "Now",
        "Channel current (TWILIGHT_CHANNEL_CURRENT_1)": "Now",
        "The Grey Sea files your ship (GREYSEA_HULL_CRUST_BUILD_1)": "Now",
        "The Grey Sea answers your light (GREYSEA_LAMP_RESPONSE_BUILD_1)": "Now",
        "Not wired yet (these change nothing)": "Now",
    }, ()),
    "Stillsand#Main": ("RM_StillsandMod.cs", "RM_Stillsand.csproj", {
        "Zuurrik (blood on the sand)": "Now",
        "Precious cave: carving and set pieces (fixed at map generation)": "NewMapsOnly",
        "Precious cave: what it holds (fixed at map generation)": "NewMapsOnly",
        "Nothing rots in the cave": "Now",
        "Water on the sand": "Now",
        "Water debt weights the sand's events": "NextPulse",
        "Under the sand: thumper, fishing and swimmers": "Now",
        "The Listening": "Now",
        "Footprints in moving sand": "Now",
    }, ("genStepEnabled", "yardangShapingEnabled", "torEnabled", "torChance", "dripEnabled", "wallRingEnabled", "tribalMarkEnabled", "rowEnabled", "rowWeight", "preservationEnabled", "bloomOnPour", "ledgerEnabled", "ledgerIncidentWeighting", "thumperEnabled", "thumperRadius", "sandFishingWakeEnabled", "sandFishingWakeChance", "driftSwimEnabled", "driftSwimDepth", "listeningHissEnabled", "listeningSingingEnabled", "listeningWarningEnabled", "singingWarningCells", "listeningRumbleEnabled", "duneErasesTracks")),
    "Stillsand#Skeletons": ("RM_SkeletonSettings.cs", "RM_Stillsand.csproj", {
        "Giant skeletons on new maps (fixed at map generation)": "NewMapsOnly",
        "Giant corpses become skeletons": "Now",
        "Bone harps and dune burial": "Now",
        "Dust on the horizon": "NextPulse",
        "Dust-settled letter": "Now",
    }, ()),
    "Stillsand#GlassChain": ("RM_GlassChainMod.cs", "RM_Stillsand.csproj", {
        "Sun-fed work tables": "Now",
        "Sand sieve": "Now",
        "Solar and wringing stills": "Now",
        "Sun lance": "Now",
        "Geophone": "Now",
        "Recipes": "Now",
    }, ()),
    "Stillsand#Events": ("RM_StillsandEventsMod.cs", "RM_Stillsand.csproj", {
        "Leviathan incidents": "NextPulse",
        "Muurrok mirror beam": "Now",
        "Krayt horn": "Now",
        "Krayt den quest": "NextPulse",
    }, ("leviathanDisabled", "leviathanOdds")),
    "Stillsand#DuneGale": ("RM_DuneGaleSettings.cs", "RM_Stillsand.csproj", {
        "The dune gale": "NextPulse",
        "Gale effects": "Now",
        "What the wind uncovers at gale end": "Now",
        "Dust devils": "NextPulse",
    }, ("emergenceOff",)),
    "Droidworks": ("Droidworks/RSW_DroidworksSettings.cs", "Droidworks/Droidworks.csproj", {
        "Restraining bolts: breaks and resentment": "Now",
        "Restraining bolts: fights and mood": "Now",
        "Droids run on stored power (reload)": "NextGameStart",
        "Power drain and charging": "Now",
        "Ion hits shut a droid down": "Now",
        "Droids blow up when destroyed": "Now",
        "After a memory wipe": "Now",
        "Wild droids": "Now",
        "Salvage from a dead droid": "Now",
        "Droids become people": "Now",
        "Protocol droids and trade": "Now",
        "Hutt captives (next stock)": "NextPulse",
    }, ()),
    "Droidworks": ("Droidworks/RSW_DroidworksSettings.cs", "Droidworks/Droidworks.csproj", {
        "Restraining bolts: breaks and resentment": "Now",
        "Restraining bolts: fights and mood": "Now",
        "Droids run on stored power (reload)": "NextGameStart",
        "Power drain and charging": "Now",
        "Ion hits shut a droid down": "Now",
        "Droids blow up when destroyed": "Now",
        "After a memory wipe": "Now",
        "Wild droids": "Now",
        "Salvage from a dead droid": "Now",
        "Droids become people": "Now",
        "Protocol droids and trade": "Now",
        "Hutt captives (next stock)": "NextPulse",
    }, ()),
    "GizkaStowaway": ("RSW_GizkaSettings.cs", "RimMandrakeGizkaStowaway.csproj", {
        "Gizka stowaway events": "Now",
        "Discovery": "Now",
        "The turn: breeding and cap": "Now",
        "The turn: chewing and guilt": "Now",
        "The creature itself (every gizka)": "Now",
    }, ()),
    "Sarlacc": ("RSW_SarlaccSettings.cs", "Sarlacc.csproj", {
        "Stage I to II: rooting in play": "Now",
        "Stage II: the anchored sarlacc's tithe": "Now",
        "The swimmer's road (Long Shade)": "Now",
        "The swimmer comes to root (Stillsand)": "Now",
        "Changed on return": "Now",
        "Stage III: breaching a cistern": "Now",
    }, ()),
    "Droidworks": ("Droidworks/RSW_DroidworksSettings.cs", "Droidworks/Droidworks.csproj", {
        "Restraining bolts: breaks and resentment": "Now",
        "Restraining bolts: fights and mood": "Now",
        "Droids run on stored power (reload)": "NextGameStart",
        "Power drain and charging": "Now",
        "Ion hits shut a droid down": "Now",
        "Droids blow up when destroyed": "Now",
        "After a memory wipe": "Now",
        "Wild droids": "Now",
        "Salvage from a dead droid": "Now",
        "Droids become people": "Now",
        "Protocol droids and trade": "Now",
        "Hutt captives (next stock)": "NextPulse",
    }, ()),
    "GizkaStowaway": ("RSW_GizkaSettings.cs", "RimMandrakeGizkaStowaway.csproj", {
        "Gizka stowaway events": "Now",
        "Discovery": "Now",
        "The turn: breeding and cap": "Now",
        "The turn: chewing and guilt": "Now",
        "The creature itself (every gizka)": "Now",
    }, ()),
    "Sarlacc": ("RSW_SarlaccSettings.cs", "Sarlacc.csproj", {
        "Stage I to II: rooting in play": "Now",
        "Stage II: the anchored sarlacc's tithe": "Now",
        "The swimmer's road (Long Shade)": "Now",
        "The swimmer comes to root (Stillsand)": "Now",
        "Changed on return": "Now",
        "Stage III: breaching a cistern": "Now",
    }, ()),
    "UtinniPatches": ("UtinniPatchesSettings.cs", "RimMandrake.Utinni.UtinniPatches.csproj", {
        "Shrine guardians (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Geothermal density (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Ores in new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "World-map icon and flame statue (restart)": "NextGameStart",
    }, ()),
    "Droidworks": ("Droidworks/RSW_DroidworksSettings.cs", "Droidworks/Droidworks.csproj", {
        "Restraining bolts: breaks and resentment": "Now",
        "Restraining bolts: fights and mood": "Now",
        "Droids run on stored power (reload)": "NextGameStart",
        "Power drain and charging": "Now",
        "Ion hits shut a droid down": "Now",
        "Droids blow up when destroyed": "Now",
        "After a memory wipe": "Now",
        "Wild droids": "Now",
        "Salvage from a dead droid": "Now",
        "Droids become people": "Now",
        "Protocol droids and trade": "Now",
        "Hutt captives (next stock)": "NextPulse",
    }, ()),
    "GizkaStowaway": ("RSW_GizkaSettings.cs", "RimMandrakeGizkaStowaway.csproj", {
        "Gizka stowaway events": "Now",
        "Discovery": "Now",
        "The turn: breeding and cap": "Now",
        "The turn: chewing and guilt": "Now",
        "The creature itself (every gizka)": "Now",
    }, ()),
    "Sarlacc": ("RSW_SarlaccSettings.cs", "Sarlacc.csproj", {
        "Stage I to II: rooting in play": "Now",
        "Stage II: the anchored sarlacc's tithe": "Now",
        "The swimmer's road (Long Shade)": "Now",
        "The swimmer comes to root (Stillsand)": "Now",
        "Changed on return": "Now",
        "Stage III: breaching a cistern": "Now",
    }, ()),
    "UtinniPatches": ("UtinniPatchesSettings.cs", "RimMandrake.Utinni.UtinniPatches.csproj", {
        "Shrine guardians (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Geothermal density (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Ores in new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "World-map icon and flame statue (restart)": "NextGameStart",
    }, ()),
    "UnfinishedLine": ("UnfinishedLineMod.cs", "RimMandrake.Utinni.UnfinishedLine.csproj", {
        "The chain and its offer gate": "NextPulse",
        "Pacing and failure": "NextPulse",
        "The Hive truce": "Now",
        "The Pattern Cores (beat 3)": "NextPulse",
        "First Light (beat 5)": "NextPulse",
        "The Tithe and the Hands (beat 4)": "NextPulse",
        "The line in the world: regrowth and stock (affects the world)": "Now",
        "Foundry-grade stock and volunteers (affects the world)": "NextPulse",
        "Imperial Foundry strikes (affects the world)": "Now",
        "Where the line stands (end of beat 2)": "NextPulse",
    }, ()),
    "Droidworks": ("Droidworks/RSW_DroidworksSettings.cs", "Droidworks/Droidworks.csproj", {
        "Restraining bolts: breaks and resentment": "Now",
        "Restraining bolts: fights and mood": "Now",
        "Droids run on stored power (reload)": "NextGameStart",
        "Power drain and charging": "Now",
        "Ion hits shut a droid down": "Now",
        "Droids blow up when destroyed": "Now",
        "After a memory wipe": "Now",
        "Wild droids": "Now",
        "Salvage from a dead droid": "Now",
        "Droids become people": "Now",
        "Protocol droids and trade": "Now",
        "Hutt captives (next stock)": "NextPulse",
    }, ()),
    "GizkaStowaway": ("RSW_GizkaSettings.cs", "RimMandrakeGizkaStowaway.csproj", {
        "Gizka stowaway events": "Now",
        "Discovery": "Now",
        "The turn: breeding and cap": "Now",
        "The turn: chewing and guilt": "Now",
        "The creature itself (every gizka)": "Now",
    }, ()),
    "Sarlacc": ("RSW_SarlaccSettings.cs", "Sarlacc.csproj", {
        "Stage I to II: rooting in play": "Now",
        "Stage II: the anchored sarlacc's tithe": "Now",
        "The swimmer's road (Long Shade)": "Now",
        "The swimmer comes to root (Stillsand)": "Now",
        "Changed on return": "Now",
        "Stage III: breaching a cistern": "Now",
    }, ()),
    "UtinniPatches": ("UtinniPatchesSettings.cs", "RimMandrake.Utinni.UtinniPatches.csproj", {
        "Shrine guardians (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Geothermal density (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Ores in new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "World-map icon and flame statue (restart)": "NextGameStart",
    }, ()),
    "UnfinishedLine": ("UnfinishedLineMod.cs", "RimMandrake.Utinni.UnfinishedLine.csproj", {
        "The chain and its offer gate": "NextPulse",
        "Pacing and failure": "NextPulse",
        "The Hive truce": "Now",
        "The Pattern Cores (beat 3)": "NextPulse",
        "First Light (beat 5)": "NextPulse",
        "The Tithe and the Hands (beat 4)": "NextPulse",
        "The line in the world: regrowth and stock (affects the world)": "Now",
        "Foundry-grade stock and volunteers (affects the world)": "NextPulse",
        "Imperial Foundry strikes (affects the world)": "Now",
        "Where the line stands (end of beat 2)": "NextPulse",
    }, ()),
    "FallLineArrivals": ("FallLineArrivalsMod.cs", "RimMandrake.Utinni.FallLineArrivals.csproj", {
        "Where events fire": "NextPulse",
        "Wrecks fall (ship-vermin nests)": "NextPulse",
        "Fall survivors (feral droids)": "NextPulse",
        "The specimen (a lab rat in an escape pod)": "NextPulse",
    }, ()),
    "PyrelandsMechanics": ("PyrelandsMechanicsMod.cs", "RimMandrake.Utinni.PyrelandsMechanics.csproj", {
        "The Tribes answer the burn": "NextPulse",
        "The Deep Tribes' fire rite": "NextPulse",
        "What the rite carries off": "Now",
    }, ()),
    "Droidworks": ("Droidworks/RSW_DroidworksSettings.cs", "Droidworks/Droidworks.csproj", {
        "Restraining bolts: breaks and resentment": "Now",
        "Restraining bolts: fights and mood": "Now",
        "Droids run on stored power (reload)": "NextGameStart",
        "Power drain and charging": "Now",
        "Ion hits shut a droid down": "Now",
        "Droids blow up when destroyed": "Now",
        "After a memory wipe": "Now",
        "Wild droids": "Now",
        "Salvage from a dead droid": "Now",
        "Droids become people": "Now",
        "Protocol droids and trade": "Now",
        "Hutt captives (next stock)": "NextPulse",
    }, ()),
    "GizkaStowaway": ("RSW_GizkaSettings.cs", "RimMandrakeGizkaStowaway.csproj", {
        "Gizka stowaway events": "Now",
        "Discovery": "Now",
        "The turn: breeding and cap": "Now",
        "The turn: chewing and guilt": "Now",
        "The creature itself (every gizka)": "Now",
    }, ()),
    "Sarlacc": ("RSW_SarlaccSettings.cs", "Sarlacc.csproj", {
        "Stage I to II: rooting in play": "Now",
        "Stage II: the anchored sarlacc's tithe": "Now",
        "The swimmer's road (Long Shade)": "Now",
        "The swimmer comes to root (Stillsand)": "Now",
        "Changed on return": "Now",
        "Stage III: breaching a cistern": "Now",
    }, ()),
    "UtinniPatches": ("UtinniPatchesSettings.cs", "RimMandrake.Utinni.UtinniPatches.csproj", {
        "Shrine guardians (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Geothermal density (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Ores in new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "World-map icon and flame statue (restart)": "NextGameStart",
    }, ()),
    "UnfinishedLine": ("UnfinishedLineMod.cs", "RimMandrake.Utinni.UnfinishedLine.csproj", {
        "The chain and its offer gate": "NextPulse",
        "Pacing and failure": "NextPulse",
        "The Hive truce": "Now",
        "The Pattern Cores (beat 3)": "NextPulse",
        "First Light (beat 5)": "NextPulse",
        "The Tithe and the Hands (beat 4)": "NextPulse",
        "The line in the world: regrowth and stock (affects the world)": "Now",
        "Foundry-grade stock and volunteers (affects the world)": "NextPulse",
        "Imperial Foundry strikes (affects the world)": "Now",
        "Where the line stands (end of beat 2)": "NextPulse",
    }, ()),
    "FallLineArrivals": ("FallLineArrivalsMod.cs", "RimMandrake.Utinni.FallLineArrivals.csproj", {
        "Where events fire": "NextPulse",
        "Wrecks fall (ship-vermin nests)": "NextPulse",
        "Fall survivors (feral droids)": "NextPulse",
        "The specimen (a lab rat in an escape pod)": "NextPulse",
    }, ()),
    "PyrelandsMechanics": ("PyrelandsMechanicsMod.cs", "RimMandrake.Utinni.PyrelandsMechanics.csproj", {
        "The Tribes answer the burn": "NextPulse",
        "The Deep Tribes' fire rite": "NextPulse",
        "What the rite carries off": "Now",
    }, ()),
    "ScarlandsLadder": ("PilgrimCamps.cs", "RimMandrake.Utinni.ScarlandsLadder.csproj", {
        "Pilgrim camps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Reading the journals": "Now",
    }, ()),
    "Droidworks": ("Droidworks/RSW_DroidworksSettings.cs", "Droidworks/Droidworks.csproj", {
        "Restraining bolts: breaks and resentment": "Now",
        "Restraining bolts: fights and mood": "Now",
        "Droids run on stored power (reload)": "NextGameStart",
        "Power drain and charging": "Now",
        "Ion hits shut a droid down": "Now",
        "Droids blow up when destroyed": "Now",
        "After a memory wipe": "Now",
        "Wild droids": "Now",
        "Salvage from a dead droid": "Now",
        "Droids become people": "Now",
        "Protocol droids and trade": "Now",
        "Hutt captives (next stock)": "NextPulse",
    }, ()),
    "GizkaStowaway": ("RSW_GizkaSettings.cs", "RimMandrakeGizkaStowaway.csproj", {
        "Gizka stowaway events": "Now",
        "Discovery": "Now",
        "The turn: breeding and cap": "Now",
        "The turn: chewing and guilt": "Now",
        "The creature itself (every gizka)": "Now",
    }, ()),
    "Sarlacc": ("RSW_SarlaccSettings.cs", "Sarlacc.csproj", {
        "Stage I to II: rooting in play": "Now",
        "Stage II: the anchored sarlacc's tithe": "Now",
        "The swimmer's road (Long Shade)": "Now",
        "The swimmer comes to root (Stillsand)": "Now",
        "Changed on return": "Now",
        "Stage III: breaching a cistern": "Now",
    }, ()),
    "UtinniPatches": ("UtinniPatchesSettings.cs", "RimMandrake.Utinni.UtinniPatches.csproj", {
        "Shrine guardians (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Geothermal density (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Ores in new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "World-map icon and flame statue (restart)": "NextGameStart",
    }, ()),
    "UnfinishedLine": ("UnfinishedLineMod.cs", "RimMandrake.Utinni.UnfinishedLine.csproj", {
        "The chain and its offer gate": "NextPulse",
        "Pacing and failure": "NextPulse",
        "The Hive truce": "Now",
        "The Pattern Cores (beat 3)": "NextPulse",
        "First Light (beat 5)": "NextPulse",
        "The Tithe and the Hands (beat 4)": "NextPulse",
        "The line in the world: regrowth and stock (affects the world)": "Now",
        "Foundry-grade stock and volunteers (affects the world)": "NextPulse",
        "Imperial Foundry strikes (affects the world)": "Now",
        "Where the line stands (end of beat 2)": "NextPulse",
    }, ()),
    "FallLineArrivals": ("FallLineArrivalsMod.cs", "RimMandrake.Utinni.FallLineArrivals.csproj", {
        "Where events fire": "NextPulse",
        "Wrecks fall (ship-vermin nests)": "NextPulse",
        "Fall survivors (feral droids)": "NextPulse",
        "The specimen (a lab rat in an escape pod)": "NextPulse",
    }, ()),
    "PyrelandsMechanics": ("PyrelandsMechanicsMod.cs", "RimMandrake.Utinni.PyrelandsMechanics.csproj", {
        "The Tribes answer the burn": "NextPulse",
        "The Deep Tribes' fire rite": "NextPulse",
        "What the rite carries off": "Now",
    }, ()),
    "ScarlandsLadder": ("ScarlandsLadderSettings.cs", "RimMandrake.Utinni.ScarlandsLadder.csproj", {
        "Pilgrim camps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Reading the journals": "Now",
    }, ()),
    "DivingInteraction": ("RM_DivingSettings.cs", "RM_DivingInteraction.csproj", {
        "Master switch and access": "Now",
        "Sea-floor generation (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "The Scald: floor generation (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "The Chill: floor generation (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Grey Sea: floor generation (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Sea-floor life (restart)": "NextGameStart",
        "Patch-gated features (restart)": "NextGameStart",
        "The Scald: hot floor": "Now",
        "Grey Sea: brine and Elders": "Now",
        "The Chill: survival": "Now",
        "The Chill: garden and footprints": "Now",
        "The Chill: aurora surges": "Now",
    }, ()),
    "KeelHoist": ("KeelHoistMod.cs", "RM_KeelHoist.csproj", {
        "Hoist switches and safety": "Now",
        "Cycle time and cable reach": "Now",
        "Restraint cradle (applies to the next beast lowered)": "NextPulse",
        "Buyer pits": "Now",
        "Buyer pit sites (offered by quests)": "NextPulse",
        "Chance chute": "Now",
        "Chance chute odds (applied at the next roll)": "NextPulse",
    }, ()),
    "KineticArms": ("RM_KineticArmsMod.cs", "RimMandrake_KineticArms.csproj", {
        "Weapons": "Now",
        "Throw strength, thump cannons and cords": "Now",
        "Kicker mines": "Now",
        "Pulse cannon": "Now",
        "Raiders carrying looted weapons": "NextPulse",
        "Ruins and complexes loot (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),
    "FeverWood": ("RM_FeverWoodMod.cs", "RM_FeverWood.csproj", {
        "Tentacle bestiary and sinking": "Now",
        "The Great Emergence (rare set-piece)": "NextPulse",
        "Uranium suppression": "Now",
        "Sekkulaath prison tank": "Now",
        "Ant hive dungeons (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Ant hive alarm sealing": "NextPulse",
        "Two-front lure: stake and rolls": "Now",
        "Two-front lure: the waves": "NextPulse",
        "Sap-suckers, silloch and brathek": "Now",
        "Kurreth theft letters": "Now",
        "Kurreth raids and raid-back": "NextPulse",
        "Oil boil weather": "NextPulse",
        "Oil boil: yield and flash": "Now",
        "Brood ransom": "Now",
        "Brood ransom: casks, goodwill and gifts": "NextPulse",
    }, ("broodGiftWeightMultipliers",)),
    "ExplosiveGrowth": ("ExplosiveGrowthMod.cs", "RM_ExplosiveGrowth.csproj", {
        "Mod switch": "Now",
        "The soak": "Now",
        "Soak length": "NextPulse",
        "Which plants soak": "Now",
        "The charge": "Now",
        "The tops (a disabled top falls back to the Churn)": "Now",
        "Player verbs": "Now",
    }, ()),
    "ExplosiveKnockback": ("RM_KnockbackMod.cs", "RimMandrake_ExplosiveKnockback.csproj", {
        "Mod switch": "Now",
        "Throw strength and range": "Now",
        "What gets thrown": "Now",
        "Impact and landing": "Now",
        "Shield belts": "Now",
        "Performance caps and debug": "Now",
    }, ()),
    "AcousticScanner": ("RM_AcousticScannerMod.cs", "RM_AcousticScanner.csproj", {
        "Sounder availability": "Now",
        "Pulse reading": "NextPulse",
    }, ()),
    "Aftermath": ("RM_AftermathMod.cs", "RM_Aftermath.csproj", {
        "Battle aftermath switch": "NextPulse",
        "Follow-up limits and windows": "NextPulse",
    }, ()),
    "FlameStatues": ("FlameStatuesMod.cs", "RimMandrake.FlameStatues.csproj", {
        "Flames and light": "Now",
        "Fuel on or off": "Now",
        "Fuel use rate (restart)": "NextGameStart",
    }, ()),
    "Inhabited": ("RM_InhabitedMod.cs", "Inhabited.csproj", {
        "Visited places can break": "Now",
        "Robbed threshold": "NextPulse",
        "Beggars from displaced people": "NextPulse",
    }, ()),
    "GravshipLanding": ("GravshipLandingMod.cs", "RM_GravshipLanding.csproj", {
        "Landing reveal (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),
    "LoreStages": ("RM_LoreStagesMod.cs", "RM_LoreStages.csproj", {
        "Staged lore text": "Now",
    }, ()),
    "Watchers": ("RM_WatchersMod.cs", "RM_Watchers.csproj", {
        "Mod switch": "Now",
        "Watcher behaviour": "Now",
        "Other things they hide from": "Now",
        "Flinch, hiding and crowd size": "Now",
        "The Watcher (Rust Cathedral)": "Now",
    }, ()),
    "Bacta": ("BactaMod.cs", "RimMandrake.StarWars.Bacta.csproj", {
        "The fluid's work": "Now",
        "Scars and permanent injuries": "Now",
        "Infections": "Now",
        "Fluid cost": "Now",
        "The occupant": "Now",
        "Revival": "Now",
        "Medical droid (BACTA_SIDE_ITEMS_1)": "Now",
        "Field kit (BACTA_SIDE_ITEMS_1)": "Now",
    }, ()),
    "RimProperty": ("PropertySettings.cs", "RM_Property.csproj", {
        "Getting caught": "Now",
        "Claim memory": "Now",
        "Animal theft": "Now",
        "Theft Hauler": "Now",
        "Salvage claim fees": "Now",
        "Walkable commerce": "Now",
        "Pickpocket": "Now",
        "Hire the placeless": "Now",
        "Bribes and bought rounds": "Now",
    }, ()),
    "ShipShields": ("ShipShieldsSettings.cs", "RimMandrake.Utinni.ShipShields.csproj", {
        "Bubble shields": "Now",
        "Field modes": "Now",
        "Unshielded hazard exposure": "Now",
        "On landing": "NextPulse",
    }, ()),
    "WasteRun": ("WasteRunSettings.cs", "RimMandrake.Utinni.WasteRun.csproj", {
        "Waste run and destinations": "Now",
        "Quest offers": "NextPulse",
        "Throat cask": "Now",
    }, ()),
    "EmpirePursuit": ("Settings.cs", "EmpirePursuit.csproj", {
        "Debug": "Now",
        "Escalation ladder": "Now",
        "Which rungs fire": "NextPulse",
        "Rung memory": "NextPulse",
        "Ion cordon timing": "Now",
    }, ()),
    "Atlas": ("AtlasSettings.cs", "RimMandrake.Utinni.Atlas.csproj", {
        "Discovery": "Now",
        "Spoilers": "Now",
        "Presentation": "Now",
        "On a new discovery: message and small rewards": "NextPulse",
        "Regions of the ship": "Now",
    }, ("disabledCategories",)),
    "LuminousPigment": ("LuminousPigmentMod.cs", "RM_LuminousPigment.csproj", {
        "Wild crowncarpet on new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Mat sighting and shelf life": "Now",
        "The press": "Now",
        "Deepfire jars and night visibility": "Now",
        "The GlowTank": "Now",
        "Painting: coats and light": "Now",
        "Painting: deepfire cost per target": "Now",
        "What can take deepfire": "Now",
        "Glowing in the dark: combat penalties": "Now",
        "First-coat and floor beauty": "Now",
        "Cuisine": "Now",
        "Cuisine: dish odds and families": "Now",
        "Gods (Ninefold)": "Now",
        "Status (the purple engine)": "Now",
    }, ("coatRadius", "coatIntensity", "familyEnabled")),
    "LongShade": ("RM_LongShadeMod.cs", "RM_LongShade.csproj", {
        "Mod switch and the dewfringe rim": "Now",
        "Map generation (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Shipfall Commons (the ship as a refuge)": "Now",
        "Lee-side middens": "Now",
        "Shade extras": "Now",
        "Incidents: stampede, haze fronts and the clan's return": "NextPulse",
        "After the haze: ash pulse and sand-lock": "NextPulse",
    }, ()),
    "NightsideIce": ("RM_NightsideIceMod.cs", "RM_NightsideIce.csproj", {
        "Nightside Ice enabled": "Now",
        "The heat dial": "Now",
        "The shivven": "Now",
        "Breach cracks": "Now",
        "Breach cracks: the first crack's countdown": "NextPulse",
    }, ()),
    "Armoury": ("RSW_ArmourySettings.cs", "JawaArmoury.csproj", {
        "Extra weapon sounds": "Now",
        "Lightsaber crystal formations (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Emergency healing gear": "Now",
        "Jumppack charges": "Now",
        "Kolto tank": "Now",
        "Mental break suppression": "Now",
        "Defusing mines": "Now",
        "Bonus finds while mining": "Now",
        "Ship alloys, doonium and slag re-melt": "NextGameStart",
        "Gear that buffs its wearer": "Now",
        "Thrown weapons that come back": "Now",
        "Ion and stun damage": "Now",
    }, ()),
    "RustChrome": ("RustChromeMod.cs", "RustChrome.csproj", {
        "Rust & Chrome UI theme": "Now",
    }, ()),
    "SacredGraffiti": ("RM_SacredGraffitiMod.cs", "SacredGraffiti.csproj", {
        "Sacred marks from rituals": "Now",
    }, ()),
    "StructureInjections": ("RM_StructureInjectionsMod.cs", "StructureInjections.csproj", {
        "Structure injection templates (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),
    "SeaShores": ("RM_SeaShoresSettings.cs", "RM_SeaShores.csproj", {
        "Modded seas count as coastline": "Now",
        "Shores beside a modded sea (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Fishing": "Now",
        "Repair existing worlds": "NextGameStart",
    }, ()),
    "ProximityHatch": ("RM_ProximityHatchMod.cs", "RimMandrake_ProximityHatch.csproj", {
        "Proximity hatching": "Now",
        "Scan cadence": "NextPulse",
    }, ()),
    "WeatherSuite": ("WeatherSuiteSettings.cs", "WeatherSuiteHook.csproj", {
        "Terminator Front permanent storm (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Nightside Aurora incident": "NextPulse",
        "Maximized aurora colours": "Now",
    }, ()),
    "Wreckage": ("RM_WreckageMod.cs", "RM_Wreckage.csproj", {
        "Salvage loot": "Now",
        "Wreck fields (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Fresh wreck falls": "NextPulse",
        "Wreck hazards": "Now",
    }, ()),
    "Visibility": ("RM_VisibilityMod.cs", "Visibility.csproj", {
        "Colony Visibility raid scaling": "NextPulse",
        "Launch reset (next gravship launch)": "NextPulse",
    }, ()),
    "Oracle": ("OracleSettings.cs", "Oracle.csproj", {
        "Oracle kill switch": "Now",
        "Claude CLI and timeout": "Now",
        "Gods budget": "Now",
    }, ()),
    "OasisMaker": ("RM_OasisMakerSettings.cs", "RM_OasisMaker.csproj", {
        "Oasis-maker enabled": "Now",
        "Placement scoring": "Now",
        "Growth timing": "Now",
        "Radius caps (locked when an oasis-maker's quality locks)": "NextPulse",
    }, ()),
    "MovingDunes": ("MovingDunesSettings.cs", "RimMandrake_MovingDunes.csproj", {
        "Dune drift": "Now",
        "Burial, plants and announcements": "Now",
        "Shovelled drift": "Now",
    }, ()),
    "TheBazaar": ("RM_BazaarSettings.cs", "RimMandrake_Bazaar.csproj", {
        "Price economy (not wired yet: changes nothing in play)": "Now",
        "Locality of untagged settlements (not wired yet)": "NextPulse",
        "Trade intel by Social skill (not wired yet)": "Now",
        "Protocol-droid intel modules (not wired yet)": "Now",
    }, ()),
    "RaidRedesigner": ("RaidRedesignerSettings.cs", "RM_RaidRedesigner.csproj", {
        "Old friends and enemies": "NextPulse",
        "Roster size and grudge strength": "NextPulse",
        "Remember them permanently": "NextPulse",
    }, ()),
    "Ninefold": ("RM_NinefoldMod.cs", "Ninefold.csproj", {
        "Ninefold engine": "Now",
        "First-contact letters": "Now",
        "Event impact and mood": "Now",
        "Favour tilts the odds": "NextPulse",
        "Offerings (Nine Faults, the Left Behind)": "Now",
    }, ()),
}

# (field, key) pairs where the Scribe key was renamed on purpose when the field's meaning changed (old saved values must not load)
DELIBERATE_KEY_RENAMES = {("scorchFruitChance", "scorchFruitChancePerCell")}


def check(cs, csproj, expected, extra=()):
    errs = []
    scribed = set(re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', cs))
    for field, key in scribed:
        if field != key and (field, key) not in DELIBERATE_KEY_RENAMES:
            errs.append(f"scribe key {key!r} != field {field!r}")
    scribed = {f for f, _ in scribed} | set(extra)
    a = cs.index("public void DoWindowContents")
    body = cs[a:cs.index("list.End();", a)]
    groups = []   # (title, scope, names, text)
    for m in re.finditer(r'if \(Group\(list, "([^"]+)", [\w.]*SettingScope\.(\w+), new\[\] \{ ([^}]*) \}(?:, "(\[[a-z ]+\])")?\)', body):
        names = re.findall(r'"(\w+)"', m.group(3))
        i = body.index("{", m.end())          # the block's opening brace (the line after the if(...))
        depth, j = 0, i
        while j < len(body):
            depth += body[j] == "{"
            depth -= body[j] == "}"
            j += 1
            if depth == 0:
                break
        else:
            errs.append(f"group {m.group(1)!r}: unbalanced braces")
        if "if (Group(" in body[i:j]:
            errs.append(f"group {m.group(1)!r}: swallows the next group (a closing brace is missing)")
        scope = {"[next game start]": "NextGameStart"}.get(m.group(4), m.group(2))   # a tag override is the audited label
        groups.append((m.group(1), scope, names, body[i:j]))
    got = {t: s for t, s, _, _ in groups}
    if len(groups) != len(expected):
        errs.append(f"{len(groups)} groups found, expected {len(expected)}")
    for t, s in expected.items():
        if t not in got:
            errs.append(f"group {t!r} missing")
        elif got[t] != s:
            errs.append(f"group {t!r} scope tag {got[t]} but the audited scope is {s}")
    seen = {}
    for title, _, names, text in groups:
        for n in names:
            if n in seen:
                errs.append(f"{n} listed in two groups: {seen[n]!r} and {title!r}")
            seen[n] = title
            if n not in scribed:
                errs.append(f"group {title!r} names {n}, which is not a Scribed setting")
        drawn = set(re.findall(r'ref (\w+)\b', text)) | set(re.findall(r'(\w+) = (?:\(int\)|Mathf\.\w+\()?list\.Slider', text))
        for d in drawn - set(names):
            errs.append(f"group {title!r} draws {d} but does not list it (it would not reset)")
    for f in scribed:
        if f not in seen:
            errs.append(f"setting {f} is in no group (no reset, not searchable)")
    for kit in ("SettingsKitCore.cs", "SettingsKitDrawer.cs"):
        if kit not in csproj:
            errs.append(f"csproj lacks the {kit} Compile Include")
    if "private static readonly Dictionary<string, object> shippedDefaults" not in cs:
        errs.append("no shippedDefaults snapshot for per-group reset")
    if "SettingsKitDrawer.SearchBox" not in cs:
        errs.append("no search box")
    return errs, groups


def run_mod(name, cs_name, pj_name, expected, extra):
    base = name.split("#")[0]
    for tier in (ROOT, os.path.join(os.path.dirname(ROOT), "RimStarWars"), os.path.join(os.path.dirname(ROOT), "RimUtinni")):
        if os.path.isdir(os.path.join(tier, base)):
            break
    src = os.path.join(tier, base, "Source")
    cs = open(os.path.join(src, cs_name), encoding="utf-8").read()
    pj = open(os.path.join(src, pj_name), encoding="utf-8").read()
    bad = total = 0
    e, groups = check(cs, pj, expected, extra)
    total += 1
    print(("ok   " if not e else "FAIL ") + f"{name}: real screen, every setting grouped, resettable, scopes as audited" + ("" if not e else " | " + "; ".join(e[:4])))
    bad += bool(e)
    g0, g1 = groups[0], (groups[1] if len(groups) > 1 else groups[0])
    last0 = g0[2][-1]
    scope_swap = next(((t, s) for t, s in expected.items() if s not in ("Now", "NextGameStart")), None)
    plants = [
        ("a name dropped from its group array", lambda c, p: (c.replace(f', "{last0}" }}', ' }', 1) if f', "{last0}" }}' in c else c.replace(f'"{last0}" }}', ' }', 1), p), "no group"),
        ("a setting in two groups", lambda c, p: (c.replace(f'"{g1[0]}", RimMandrake.Shared.SettingScope.{g1[1]}, new[] {{ ', f'"{g1[0]}", RimMandrake.Shared.SettingScope.{g1[1]}, new[] {{ "{g0[2][0]}", ', 1), p), "two groups"),
        ("group names a non-setting", lambda c, p: (c.replace(f'"{last0}" }}', '"notASettingAtAll" }', 1), p), "not a Scribed setting"),
        ("a Group's closing brace lost", lambda c, p: (c.replace('                list.GapLine();\n            }\n', '                list.GapLine();\n', 1), p), "swallows|unbalanced braces"),
        ("kit dropped from the csproj", lambda c, p: (c, p.replace("SettingsKitDrawer.cs", "SettingsKitDrawr.cs")), "SettingsKitDrawer.cs"),
        ("snapshot removed", lambda c, p: (c.replace("shippedDefaults = SnapshotDefaults()", "shippedDefaultz = SnapshotDefaults()"), p), "shippedDefaults"),
    ]
    if scope_swap:
        t, s = scope_swap
        plants.append(("a scope tag flipped to a dishonest one", lambda c, p: (c.replace(f'"{t}", RimMandrake.Shared.SettingScope.{s}', f'"{t}", RimMandrake.Shared.SettingScope.Now', 1), p), "audited scope"))
    if "NextGameStart" in expected.values():
        plants.append(("a next-game-start tag overridden to [now]", lambda c, p: (c.replace('"[next game start]"))', '"[now]"))', 1), p), "audited scope"))
    for label, f, want in plants:
        c2, p2 = f(cs, pj)
        total += 1
        if (c2, p2) == (cs, pj):
            print(f"FAIL {name}: {label}: pattern not found")
            bad += 1
            continue
        try:
            e, _ = check(c2, p2, expected, extra)
        except Exception as ex:   # a broken file must still be a failure, not a crash
            e = [f"exception {ex}"]
        hit = any(w in x for x in e for w in want.split('|'))
        print(("ok   " if hit else "FAIL ") + f"{name}: {label}" + ("" if hit else f" | wanted {want!r}, got {e[:2]}"))
        bad += not hit
    return bad, total


def check_biomes_shell():
    """BiomesShell keeps a Scribed per-entry toggle DICTIONARY (no Scribe_Values), so it has its own check:
    kit in csproj, search box, collapsible groups with a per-group reset, worldgen label, dictionary still Scribed,
    then plants one defect at a time."""
    base = os.path.join(ROOT, "BiomesShell", "Source")
    cs = open(os.path.join(base, "RM_BiomesMod.cs"), encoding="utf-8").read()
    pj = open(os.path.join(base, "RM_Biomes.csproj"), encoding="utf-8").read()

    def errs(c, p):
        e = []
        for kit in ("SettingsKitCore.cs", "SettingsKitDrawer.cs"):
            if kit not in p:
                e.append(f"csproj lacks the {kit} Compile Include")
        if "SettingsKitDrawer.SearchBox" not in c:
            e.append("no search box")
        if "SettingsKitDrawer.ResetButton" not in c:
            e.append("no per-group reset")
        if "(WORLDGEN-AFFECTING)" not in c:
            e.append("biome group not labelled worldgen")
        if 'Scribe_Collections.Look(ref enabled, "enabled"' not in c:
            e.append("toggle dictionary not Scribed")
        if "maxOneColumn = true" not in c:
            e.append("no maxOneColumn")
        return e
    bad = total = 1
    e = errs(cs, pj)
    print(("ok   " if not e else "FAIL ") + "BiomesShell: kit screen (search, grouped reset, worldgen label)" + ("" if not e else " | " + "; ".join(e)))
    bad = 1 if e else 0
    for label, c2, p2, want in (
        ("kit dropped from csproj", cs, pj.replace("SettingsKitDrawer.cs", "SettingsKitDrawr.cs"), "SettingsKitDrawer.cs"),
        ("search box removed", cs.replace("SettingsKitDrawer.SearchBox", "SettingsKitDrawer.SearchBx"), pj, "search box"),
        ("reset removed", cs.replace("SettingsKitDrawer.ResetButton", "SettingsKitDrawer.ResetButtn"), pj, "per-group reset"),
        ("worldgen label dropped", cs.replace("(WORLDGEN-AFFECTING)", "(x)"), pj, "worldgen"),
    ):
        total += 1
        hit = any(want in x for x in errs(c2, p2)) and (c2, p2) != (cs, pj)
        print(("ok   " if hit else "FAIL ") + f"BiomesShell: {label}")
        bad += not hit
    return bad, total


def main():
    bad = total = 0
    for name, (cs_name, pj_name, expected, extra) in MODS.items():
        b, t = run_mod(name, cs_name, pj_name, expected, extra)
        bad += b
        total += t
    b, t = check_biomes_shell()
    bad += b
    total += t
    print(f"settings screens selftest: {total - bad}/{total} ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
