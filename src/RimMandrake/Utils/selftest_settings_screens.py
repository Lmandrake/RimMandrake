#!/usr/bin/env python3
"""MOD_OPTIONS_RETROFIT_1 offline check for the SettingsKit settings screens retrofitted onto a mod's own Mod file.

For each mod listed in MODS below: every setting the settings class Scribes sits inside exactly one named Group(...) block whose
names array lists it (so it collapses, searches and resets with its group); every control drawn in a block is listed by it;
groups are brace-balanced and do not swallow the next group; the group scope tags equal the AUDITED scopes recorded here (the
audit is per setting, against its read site: a worldgen step is NewMapsOnly, a Gale-onset or storyteller-roll read is
NextPulse, a tick/job/patch read is Now); the SettingsKit files are in the csproj; the shippedDefaults snapshot exists.
Then plants one defect at a time per mod and requires the check to fail on each.

Master switches (SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST): a mod that declares a SettingDependencies (`.Declare(master,
dependents...)`) has opted in, and then EVERY grouped setting must be a master, a declared dependent or marked
`.Independent(...)` (a dependent without a declared master is flagged); every declared name must be a Scribed setting;
every drawn dependent must sit inside a `using (Dependent(list, ...))` scope that lists it (else it would not grey);
there must be a Reset-all button; the csproj must link SettingsKitMasters.cs and SettingsKitMastersDrawer.cs.

Add a mod by adding one entry to MODS.     python3 src/RimMandrake/Utils/selftest_settings_screens.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# folder: (mod .cs, csproj, expected groups, extra setting names the screen resets that are not Scribe_Values fields)
MODS = {
    "AtmosphericBase": ("RM_AtmosphericBaseSettings.cs", "RM_AtmosphericBase.csproj", {   # every read is per evaluation / per frame / per button query
        "Light channel": "Now",
        "Hand-over buttons": "Now",
        "Moods": "Now",
        "Pattern (off the Utinni)": "Now",   # ATMOSPHERIC_BASE_BUILD_PROGRAM_1 (b): read by DefaultMood and the per-fixture loop each evaluation
        "Territory (two moods at once)": "Now",
        "Tremor (third and later moods)": "Now",
    }, ()),
    "BlueDesert": ("RM_BlueDesertMod.cs", "RM_BlueDesert.csproj", {
        "Mod switch": "Now",
        "Natives, flora detonations and cues": "Now",
        "Flora roster": "NextGameStart",
        "Vhaulk": "Now",
        "Vhaulk stay length": "NextPulse",
        "Blue Desert weathers": "NextPulse",
        "Haze and blue-ice thaw": "Now",
        "Murrek burial": "NextPulse",
        "Blue-ice cold rack": "Now",
        "The ablation line": "NextPulse",
    }, ()),
    "CrackedLands": ("RM_CrackedLandsMod.cs", "RM_CrackedLands.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Flood cycle": "Now",
        "Warning: chimes and signs": "Now",
        "Flood timing": "NextPulse",
        "Soaked ground": "Now",
        "Fossil seams (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Muttavaq": "Now",
        "After the water recedes": "NextPulse",
        "Native plants": "NextGameStart",
        "Refuge ledges and carvings": "Now",
        "Cliff ledges (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Map controls (placed in development mode)": "Now",   # FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: read per tick/press
    }, ()),
    "HugeThings": ("RM_HugeThingsSettings.cs", "RM_HugeThings.csproj", {
        "Giant plants": "Now",
        "Giant animals": "Now",   # keyed header since HUGETHINGS_KEYS_FIX_ORPHAN_HEADERS (601e7482f3): RM_HugeThings_GiantAnimals
        "Large Pawns footprint and custom size tiers": "NextGameStart",
        "Wake and plant smashing": "Now",
        "Big creatures: walls, slots and roofs": "Now",   # BIG_CREATURES_DESIGN_WALLS_AND_SLOTS: read at each path start, strike and tick
        "Yield curve": "Now",
        "Titanic corpse sites": "Now",
        "Titan events": "NextPulse",   # TITAN_CAMPS_SCAVENGERS_EVENTS_1 (70cc1a28a): read when the storyteller offers RM_TitanPassage
    }, ()),
    "GimmeSomeSlack#Cables": ("GimmeSomeSlackMod.cs", "RimMandrake_GimmeSomeSlack.csproj", {
        "Messy cords and default style": "Now",
        "Slack, loops and tangles": "Now",
        "Breaks and sparks": "Now",
        "Wind sway": "Now",
        "Which conduits become cords": "Now",
        "Far zoom and debug": "Now",
    }, ("excludedConduits",)),
    "GimmeSomeSlack#Aerial": ("Aerial/AerialSettings.cs", "RimMandrake_GimmeSomeSlack.csproj", {
        "Overhead power lines": "Now",
        "Wire sway": "Now",
        "Damage, shock and alerts": "Now",
        "Power-tap clamps": "Now",
    }, ()),
    # the flexible hoses moved to FlowWorks at the hose port (2026-10-11): a static section drawn in FlowWorks' one window
    "FlowWorks#Hose": ("Hose/RM_HoseSettings.cs", "RimMandrake_FlowWorks.csproj", {
        "Flexible hoses": "Now",
        "Hose length and shape": "Now",
        "Colonists carrying hoses": "Now",
        "Look": "Now",
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
        "The ripple and the calling-pyre": "Now",
        "Ruins and living camps": "NewMapsOnly",
        "Venomvine islands": "NewMapsOnly",
        "Venomvine creep": "Now",
    }, ()),
    "LanternDeeps": ("LanternDeepsMod.cs", "RM_LanternDeeps.csproj", {
        "Entrances: cave mouth and ruined mineshaft": "NewMapsOnly",
        "Darkness inside a Deep": "Now",
        "Newly generated Deeps: crystal, dead and galuush": "NewMapsOnly",
        "Flora and deposits": "Now",
        "Shard-minds and Orun-Ghal": "Now",
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
        "Canopy swarm (the krannock)": "NextGameStart",   # RM_GreentideSpeciesStartup, 2026-10-15
        "Stellock lace": "Now",
        "The shoal (the illisk)": "Now",
        "The false bank (the vurrak)": "Now",
        "The canopy-breaker (the thurrock)": "Now",
        "The Roil (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Greatbole fruitfall and harvest ladder": "Now",
        "Greatbole seeds and servants": "NextGameStart",
        "Giant ant raids": "Now",   # RM_GreentideAntRaidApplier on window close, 2026-10-22
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
        "Contagion-touched": "Now",
        "Contagion mulch": "Now",
        "The zhool's red haze": "Now",
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
        "Vent gas": "Now",
        "Corroded ruins (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Rhossak groves": "Now",          # RM_CompRhossakGrove reads all three on its 250-tick check
    }, ()),
    "Pyrelands": ("RM_PyrelandsMod.cs", "FireEcologyHook.csproj", {
        "Mod enabled": "Now",
        "Loose ash and scorch-fruit": "Now",
        "Ash accumulation (Ash Fall / Cinderfall weather)": "Now",
        "Plant art and wild flora": "Now",
        "Scorched ruins (new maps)": "NewMapsOnly",
        "Biome placement (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Absorbed mechanics (mandrake.rut.pyrelandsmechanics)": "Now",
        "Giants and herds (restart)": "NextGameStart",
        "Burrowers": "Now",
        "Sand shovelling": "Now",
        "Cross-biome ash accumulation": "Now",
        "Ash field": "Now",
    }, ()),
    "GelatinousSlime": ("SlimeMod.cs", "RM_GelatinousSlime.csproj", {
        "The gene archive": "Now",
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Slimification and fields": "Now",
        "Ruined farms (WORLDGEN-AFFECTING)": "NewMapsOnly",
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
        "Ship: the portable warm mat": "Now",
        "Technology: the gut-mother and the unjoining draught": "Now",
        "Cross-biome opt-in": "Now",
    }, ()),
    "TheForge": ("RM_TheForgeMod.cs", "RM_TheForge.csproj", {
        "The Forge enabled": "Now",
        "Weather pulse and grand cycle": "Now",
        "Spunstone study": "Now",
        "Spunstone door and hull (restart)": "NextGameStart",
        "Voices and the dhuvvox": "Now",
        "White plume fronts": "Now",
        "Vapour columns and sky creatures": "Now",
        "The dhokkur": "Now",
        "Not wired yet (these change nothing)": "Now",
        "The dhoggur": "Now",
        "The ummisk": "Now",
    }, ()),
    "ShipVermin": ("RM_ShipVerminMod.cs", "RM_ShipVermin.csproj", {
        "Alert and fuel mites": "Now",
        "Wreck-anchored vermin nests": "Now",
        "Species a wreck nest may produce": "Now",
    }, ()),
    "Wastes": ("RM_WastesMod.cs", "RM_Wastes.csproj", {
        "Wasteland master switch": "Now",
        "Storms": "Now",
        "Ambient dose and radiothermal heat": "Now",
        "Processor animals": "Now",
        "Grippers": "Now",
        "The Middenshell": "Now",
        "Waste casks and the sealed cask bay": "Now",
        "Rite of Tipping": "Now",
    }, ()),
    "SolarMirrors": ("RM_SolarMirrorsMod.cs", "RM_SolarMirrors.csproj", {
        "Mirror light": "Now",
        "Appearance": "Now",
        "Uses": "Now",
        "Ancient mirror fields (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Upkeep": "Now",
        "Solar panels": "Now",
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
        "Thrixweave (restart)": "NextGameStart",
        "Urraveth remains: new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "The dead giant (urraveth remains)": "Now",
        "Web network on new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Webfall weather (restart)": "NextGameStart",
        "The siege (affects maps next to the Webwork)": "Now",
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
    }, ("genStepEnabled", "yardangShapingEnabled", "torEnabled", "torChance", "wallRingEnabled", "rowEnabled", "rowWeight", "preservationEnabled", "bloomOnPour", "ledgerEnabled", "ledgerIncidentWeighting", "thumperEnabled", "thumperRadius", "sandFishingWakeEnabled", "sandFishingWakeChance", "driftSwimEnabled", "driftSwimDepth", "listeningHissEnabled", "listeningSingingEnabled", "listeningWarningEnabled", "singingWarningCells", "listeningRumbleEnabled", "duneErasesTracks")),
    "Stillsand#Skeletons": ("RM_SkeletonSettings.cs", "RM_Stillsand.csproj", {
        "Giant skeletons on new maps (fixed at map generation)": "NewMapsOnly",
        "Giant corpses become skeletons": "Now",
        "Bone harps": "Now",
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
    "GizkaStowaway": ("RSW_GizkaSettings.cs", "RimMandrakeGizkaStowaway.csproj", {
        "Gizka stowaway events": "Now",
        "Discovery": "Now",
        "The turn: breeding and cap": "Now",
        "The turn: chewing and guilt": "Now",
        "The creature itself (every gizka)": "Now",
    }, ()),
    "SithLine": ("RSW_SithLineSettings.cs", "RSW_SithLine.csproj", {
        "Sith reskin and closed routes": "NextGameStart",
        "Never one of yours": "Now",
        "Inquisitors in the Galactic Empire": "Now",
        "The Abyss lair": "Now",
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
        "Oil boil weather": "NextPulse",
        "Oil boil: yield and flash": "Now",
        "Brood ransom": "Now",
        "Brood ransom: casks, goodwill and gifts": "NextPulse",
    }, ("broodGiftWeightMultipliers",)),
    "ExplosiveGrowth": ("ExplosiveGrowthMod.cs", "RM_ExplosiveGrowth.csproj", {
        "Mod switch": "Now",
        "Growth rates": "Now",
        "Vanilla crops and plants in our biomes": "Now",
        "Our plants outside our biomes": "Now",
        "The cycle at maturity": "Now",
        "Ageing, light and growers": "Now",
        "Water sources": "Now",
        "After the rain": "NextPulse",
        "The charge": "Now",
        "The tops (a disabled top falls back to fruiting)": "Now",
        "Player verbs": "Now",
        "Trees (our plants drawn 3.0 or larger, fungi excepted)": "Now",
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
        "Helixien gas": "Now",
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
    "StarWarsRaces": ("RSW_StarWarsRacesMod.cs", "RSW_StarWarsRaces.csproj", {
        "Facial Animation": "Now",
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
        "Fuel blasts draw the Empire": "Now",   # read when the FlowWorks blast event arrives (CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL)
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
    }, ()),
    "SleepingIce": ("RM_SleepingIceMod.cs", "RM_SleepingIce.csproj", {
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
        # CANON_MATERIALS_BUILD_1 added a 13th group: the beskar-smelt and mine-shaft-gate toggles share it.
        "Beskar smelting and mine shafts": "Now",
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
        "Perpetual aurora (biomes that never lose it)": "Now",
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
    "Rites": ("RM_NinefoldMod.cs", "RimMandrake.Utinni.Rites.csproj", {   # Ninefold, folded into Salvation Rites 2026-10-22
        "Ninefold engine": "Now",
        "First-contact letters": "Now",
        "Event impact and mood": "Now",
        "Favour tilts the odds": "NextPulse",
        "Offerings (Nine Faults, the Left Behind)": "Now",
    }, ()),
    "Antiquities": ("AntiquitiesMod.cs", "RimMandrake.Utinni.Antiquities.csproj", {
        "Reading the antiquities": "Now",
        "Key text bonus": "Now",
    }, ()),
    "CathedralPass": ("CathedralPassMod.cs", "RimMandrake.Utinni.CathedralPass.csproj", {
        "Cathedral mechanoid pass": "Now",
    }, ()),
    "DroidRepairJobs": ("DroidRepairJobsMod.cs", "RimMandrake.Utinni.DroidRepairJobs.csproj", {
        "Repair-job payment": "NextPulse",
    }, ()),
    "EggReckoning": ("EggReckoningSettings.cs", "RimMandrake.Utinni.EggReckoning.csproj", {
        "The Reckoning quest": "NextPulse",
    }, ()),
    "FungalSoilTrade": ("FungalSoilTradeOptions.cs", "RimMandrake.Utinni.FungalSoilTrade.csproj", {
        "Fungal ground on the Rot (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Fungal distress (mining the Rot's soil)": "Now",
    }, ()),
    "KyberTradePlot": ("KyberTradePlotSettings.cs", "RimMandrake.Utinni.KyberTradePlot.csproj", {
        "Kyber trade plot content": "NextPulse",
    }, ()),
    "LongHunger": ("LongHungerMod.cs", "LongHunger.csproj", {
        "Whether it surfaces": "NextPulse",
        "Eruption, tremors and salvage": "Now",
    }, ()),
    "ScavengerEvents": ("ScavengerEventsSettings.cs", "RimMandrake.Utinni.ScavengerEvents.csproj", {
        "Wildlife migration": "NextPulse",
        "Survival pod gift": "NextPulse",
        "Tribal pod crash (rescue)": "NextPulse",
        "Insect swarm": "NextPulse",
        "Colonist stroke": "NextPulse",
        "Ship break (cargo rain)": "NextPulse",
        "Emergency food relief (Thanksgiving)": "NextPulse",
    }, ()),
    "PropaneLakeMechanics": ("PropaneLakeMechanicsSettings.cs", "RimMandrake.Utinni.PropaneLakeMechanics.csproj", {
        "Gas vents and pipe networks": "Now",
        "V-wake agitation": "Now",
        "Saturation heist raid": "NextPulse",
        "Saturation deflagration": "Now",
    }, ()),
    "ShipMemory": ("ShipMemorySettings.cs", "RimMandrake.Utinni.ShipMemory.csproj", {
        "Memory-Core reveal": "Now",
        "Bioferrite stockpile trigger": "Now",
    }, ()),
    "TrophyCraft": ("RSW_TrophyCraftSettings.cs", "RSW_TrophyCraft.csproj", {
        "Fang pendant social consequence": "Now",
        "Opinion magnitude": "Now",
    }, ()),
    "DesertVehicleReskin": ("Fuel/RSW_DesertVehicleReskinSettings.cs", "Fuel/DesertVehicleReskin.csproj", {
        "Vegetable fuel for draught carts": "Now",
    }, ()),
    "WildsteamEggBounty": ("WildsteamEggBountySettings.cs", "RimMandrake.Utinni.WildsteamEggBounty.csproj", {
        "Wildsteam egg bounty quest": "NextPulse",
    }, ()),
    "JawaIonWeapons": ("RSW_JawaIonWeaponsSettings.cs", "JawaIonWeapons.csproj", {
        "People and droids: wearing a target down": "Now",
        "Body-size resistance": "Now",
        "Machines and mechanoids: instant overload": "Now",
        "Shields": "Now",
        "Vehicles (needs Vehicle Framework installed)": "Now",
    }, ()),
    "UtinniStatues": ("UtinniStatuesMod.cs", "RimMandrake.Utinni.UtinniStatues.csproj", {
        "Statue carving": "NextGameStart",
        "Sh'kaar's burning idol": "NextPulse",
        "Sumpgas fuels the idol": "NextGameStart",
    }, ()),
    "BrainWorms": ("RSW_BrainWormsSettings.cs", "RimMandrake.StarWars.BrainWorms.csproj", {
        "Salvaged cargo pod incident": "NextPulse",
        "Egg mortar shells": "Now",
        "Infection progression speed": "Now",
        "Cold-kill rate": "Now",
    }, ()),
    "WeepingStones": ("RM_WeepingStonesSettings.cs", "RM_WeepingStones.csproj", {
        "Stocked pools": "Now",
        "Netting breeders": "Now",   # net job reads netThrowRange/netMaxThrows at throw time
        "Vhorrin and vizhik odds": "NextPulse",
        "Walking condenser": "Now",
        "Condenser season length": "NextPulse",
        "Condenser quests": "NextPulse",
        "Dewsilk cocoons": "NextGameStart",
        "Native oasis flora (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),
    "SWBestiary#Livestock": ("Livestock/RSW_LivestockSettings.cs", "Livestock/RimMandrakeLivestockRSW.csproj", {
        "Kiln-belly feed cycle (Onnik)": "Now",
        "Kiln batch cooldown": "NextPulse",
        "Moornak grief hazard": "Now",
        "Moornak release timer": "NextPulse",
    }, ()),
    "SWBestiary#Ikee": ("JawaIkee/RSW_JawaIkeeSettings.cs", "JawaIkee/JawaIkee.csproj", {
        "Ikee mood effect": "Now",
    }, ()),
    "SWBestiary#BeastMechanics": ("BeastMechanics/RSW_BeastMechanicsSettings.cs", "BeastMechanics/RimMandrakeBeastMechanicsRSW.csproj", {
        "Innate creature abilities": "NextPulse",
        "Scrap-hoarding birds": "Now",
        "Scrap-bird raids": "NextPulse",
        "Toxin-dependent creatures": "Now",
        "Taozin brine tank": "Now",
        "Taozin nests": "NewMapsOnly",
        "Albino dragonsnake": "NextGameStart",
    }, ()),
}

# (field, key) pairs where the Scribe key was renamed on purpose when the field's meaning changed (old saved values must not load)
DELIBERATE_KEY_RENAMES = {("scorchFruitChance", "scorchFruitChancePerCell")}
# a settings SECTION Scribed inside another class's ExposeData prefixes its keys (FlowWorks' hose section, hose port)
DELIBERATE_KEY_PREFIXES = ("hose_",)
# Scribed migration flags with no control and no reset (resetting one would re-run its one-time migration)
INTERNAL_FLAGS = {"hoseSettingsImported"}


GROUP_RE = re.compile(r'if \(Group\(list, ("([^"]+)"|"(\w+)"\.Translate\(\)), [\w.]*SettingScope\.(\w+), new\[\] \{ ([^}]*) \}(?:, "(\[[a-z ]+\])")?\)')


def english_keyed(mod_dir):
    """{key: English text} from the mod's Languages/English/Keyed/*.xml (a Group title may be `"KEY".Translate()`)."""
    import glob
    import xml.etree.ElementTree as ET
    out = {}
    for f in glob.glob(os.path.join(mod_dir, "Languages", "English", "Keyed", "*.xml")):
        try:
            for el in ET.parse(f).getroot():
                if isinstance(el.tag, str) and el.text is not None:
                    out[el.tag] = el.text.strip()
        except ET.ParseError as ex:
            out.setdefault("__parse_errors__", []).append("%s: %s" % (os.path.basename(f), ex))
    return out


def check(cs, csproj, expected, extra=(), keyed=None):
    """errs, groups; each group is (title, scope, names, block text, the title argument as written in the source). A title
    written `"KEY".Translate()` is the KEY's English Keyed text (HUGETHINGS_KEYS_FIX_ORPHAN_HEADERS), and an unresolved key
    is an error."""
    errs = []
    keyed = keyed or {}
    scribed = set(re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', cs))
    for field, key in scribed:
        if field != key and (field, key) not in DELIBERATE_KEY_RENAMES and not any(key == p + field for p in DELIBERATE_KEY_PREFIXES):
            errs.append(f"scribe key {key!r} != field {field!r}")
    scribed = ({f for f, _ in scribed} - INTERNAL_FLAGS) | set(extra)
    a = re.search(r"public (?:static )?void (?:DoWindowContents|DoSettingsSection)\(", cs).start()
    m_end = cs.index("\n        }\n", a)          # the method's own closing brace (8-space indent)
    le = cs.find("list.End();", a)
    body = cs[a:le if 0 <= le < m_end else m_end]  # a static section drawn into the parent's list has no list.End()
    groups = []   # (title, scope, names, text, raw title argument)
    for m in GROUP_RE.finditer(body):
        if m.group(2) is not None:
            gtitle = m.group(2)
        else:
            gtitle = keyed.get(m.group(3))
            if gtitle is None:
                errs.append(f"group title key {m.group(3)!r} has no English Keyed text")
                gtitle = m.group(3)
        names = re.findall(r'"(\w+)"', m.group(5))
        i = body.index("{", m.end())          # the block's opening brace (the line after the if(...))
        depth, j = 0, i
        while j < len(body):
            depth += body[j] == "{"
            depth -= body[j] == "}"
            j += 1
            if depth == 0:
                break
        else:
            errs.append(f"group {gtitle!r}: unbalanced braces")
        if "if (Group(" in body[i:j]:
            errs.append(f"group {gtitle!r}: swallows the next group (a closing brace is missing)")
        scope = {"[next game start]": "NextGameStart"}.get(m.group(6), m.group(4))   # a tag override is the audited label
        groups.append((gtitle, scope, names, body[i:j], m.group(1)))
    got = {t: s for t, s, _, _, _ in groups}
    if len(groups) != len(expected):
        errs.append(f"{len(groups)} groups found, expected {len(expected)}")
    for t, s in expected.items():
        if t not in got:
            errs.append(f"group {t!r} missing")
        elif got[t] != s:
            errs.append(f"group {t!r} scope tag {got[t]} but the audited scope is {s}")
    seen = {}
    for title, _, names, text, _ in groups:
        for n in names:
            if n in seen:
                errs.append(f"{n} listed in two groups: {seen[n]!r} and {title!r}")
            seen[n] = title
            if n not in scribed:
                errs.append(f"group {title!r} names {n}, which is not a Scribed setting")
        drawn = set(re.findall(r'ref (\w+)\b', text)) | set(re.findall(r'(\w+) = (?:\(int\)|Mathf\.\w+\()?list\.Slider', text))
        drawn -= set(re.findall(r'\b(?:bool|int|float|string|var)\s+(\w+)\s*=', text))   # a block-local (per-def checkbox), not a setting
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
    errs += masters_check(cs, csproj, body, scribed, seen)
    return errs, groups


def balanced_end(text, i):
    """Index just past the brace block opening at text[i] == '{' (len(text) if unbalanced)."""
    depth = 0
    for j in range(i, len(text)):
        depth += text[j] == "{"
        depth -= text[j] == "}"
        if depth == 0:
            return j + 1
    return len(text)


def masters_check(cs, csproj, body, scribed, grouped):
    """SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST: only for a mod that declared master switches (opt-in)."""
    decls = re.findall(r'\.Declare\(([^)]*)\)', cs)
    if not decls:
        return []
    errs = []
    masters, masters_of = set(), {}
    for d in decls:
        names = re.findall(r'"(\w+)"', d)
        if not names:
            continue
        masters.add(names[0])
        for x in names[1:]:
            masters_of.setdefault(x, set()).add(names[0])
    indep = {n for d in re.findall(r'\.Independent\(([^)]*)\)', cs) for n in re.findall(r'"(\w+)"', d)}
    classified = masters | set(masters_of) | indep
    for f in sorted(grouped):
        if f not in classified:
            errs.append(f"setting {f} has no declared master and is not marked Independent")
    for n in sorted(classified - scribed):
        errs.append(f"masters declaration names {n}, which is not a Scribed setting")
    scopes = []
    for m in re.finditer(r'using \(Dependent\(list, ([^)]*)\)\)', body):
        keys = set(re.findall(r'"(\w+)"', m.group(1)))
        i = body.find("{", m.end())
        scopes.append((m.start(), balanced_end(body, i) if i >= 0 else m.end(), keys))
        for k in sorted(keys - set(masters_of)):
            errs.append(f"Dependent scope lists {k}, which has no declared master")
        # the scope greys only when NO key is live, so its root keys (those not under another key of the same scope)
        # must share one master set, or one could be dead while a sibling keeps the block drawable
        roots = [k for k in keys if k in masters_of and not (masters_of[k] & keys)]
        if len({frozenset(masters_of[k]) for k in roots}) > 1:
            errs.append("Dependent scope mixes keys with different masters: " + ", ".join(sorted(roots)))
    drawn = [(m.start(), m.group(1)) for m in re.finditer(r'ref (\w+)\b', body)]
    drawn += [(m.start(), m.group(1)) for m in re.finditer(r'(\w+) = (?:\(int\)|Mathf\.\w+\()?list\.Slider', body)]
    for pos, name in drawn:
        if name in masters_of and not any(a <= pos < b and name in keys for a, b, keys in scopes):
            errs.append(f"draws dependent {name} outside a Dependent scope that lists it (it would not grey)")
    if "SettingsKitMastersDrawer.ResetAllButton" not in cs:
        errs.append("no Reset-all button")
    for kit in ("SettingsKitMasters.cs", "SettingsKitMastersDrawer.cs"):
        if kit not in csproj:
            errs.append(f"csproj lacks the {kit} Compile Include")
    return errs


def run_mod(name, cs_name, pj_name, expected, extra):
    base = name.split("#")[0]
    for tier in (ROOT, os.path.join(os.path.dirname(ROOT), "RimStarWars"), os.path.join(os.path.dirname(ROOT), "RimUtinni")):
        if os.path.isdir(os.path.join(tier, base)):
            break
    src = os.path.join(tier, base, "Source")
    cs = open(os.path.join(src, cs_name), encoding="utf-8").read()
    pj = open(os.path.join(src, pj_name), encoding="utf-8").read()
    keyed = english_keyed(os.path.join(tier, base))
    bad = total = 0
    e, groups = check(cs, pj, expected, extra, keyed)
    total += 1
    print(("ok   " if not e else "FAIL ") + f"{name}: real screen, every setting grouped, resettable, scopes as audited" + ("" if not e else " | " + "; ".join(e[:4])))
    bad += bool(e)
    g0, g1 = groups[0], (groups[1] if len(groups) > 1 else groups[0])
    last0 = g0[2][-1]
    g1lit = {'NextGameStart': 'Now'}.get(g1[1], g1[1])   # a [next game start] override is written as SettingScope.Now
    raw_of = {g[0]: g[4] for g in groups}                 # title -> its argument as written ("title" or "KEY".Translate())
    scope_swap = next(((t, s) for t, s in expected.items() if s not in ("Now", "NextGameStart")), None)
    plants = [
        ("a name dropped from its group array", lambda c, p: (c.replace(f', "{last0}" }}', ' }', 1) if f', "{last0}" }}' in c else c.replace(f'"{last0}" }}', ' }', 1), p), "no group"),
        ("a setting in two groups", lambda c, p: (c.replace(f'{g1[4]}, RimMandrake.Shared.SettingScope.{g1lit}, new[] {{ ', f'{g1[4]}, RimMandrake.Shared.SettingScope.{g1lit}, new[] {{ "{g0[2][0]}", ', 1), p), "two groups"),
        ("group names a non-setting", lambda c, p: (c.replace(f'"{last0}" }}', '"notASettingAtAll" }', 1), p), "not a Scribed setting"),
        ("a Group's closing brace lost", lambda c, p: (c.replace('                list.GapLine();\n            }\n', '                list.GapLine();\n', 1), p), "swallows|unbalanced braces"),
        ("kit dropped from the csproj", lambda c, p: (c, p.replace("SettingsKitDrawer.cs", "SettingsKitDrawr.cs")), "SettingsKitDrawer.cs"),
        ("snapshot removed", lambda c, p: (c.replace("shippedDefaults = SnapshotDefaults()", "shippedDefaultz = SnapshotDefaults()"), p), "shippedDefaults"),
    ]
    if scope_swap:
        t, s = scope_swap
        plants.append(("a scope tag flipped to a dishonest one", lambda c, p: (c.replace(f'{raw_of.get(t, chr(34) + t + chr(34))}, RimMandrake.Shared.SettingScope.{s}', f'{raw_of.get(t, chr(34) + t + chr(34))}, RimMandrake.Shared.SettingScope.Now', 1), p), "audited scope"))
    tk = next((g[4] for g in groups if g[4].endswith(".Translate()")), None)
    if tk:
        plants.append(("a keyed group title with no English text", lambda c, p: (c.replace(tk, tk.replace('".Translate()', 'Zz".Translate()'), 1), p), "no English Keyed text"))
    if "NextGameStart" in expected.values():
        plants.append(("a next-game-start tag overridden to [now]", lambda c, p: (c.replace('"[next game start]"))', '"[now]"))', 1), p), "audited scope"))
    decl = re.search(r'\.Declare\(([^)]*)\)', cs)
    if decl:
        # a pure dependent of the first Declare (not itself a master, not declared again elsewhere)
        first = re.findall(r'"(\w+)"', decl.group(1))
        masters = {re.findall(r'"(\w+)"', d)[0] for d in re.findall(r'\.Declare\(([^)]*)\)', cs)}
        # (declared as a dependent of ONLY this Declare: a second master keeps it classified, so the plant would be a no-op)
        ndecl = lambda n: sum(1 for d in re.findall(r'\.Declare\(([^)]*)\)', cs) if n in re.findall(r'"(\w+)"', d)[1:])
        pure = next(n for n in reversed(first[1:]) if n not in masters and ndecl(n) == 1 and cs.count(f'"{n}"') >= 2)
        # a scope whose first key is drawn by a checkbox (a radio-button setting is invisible to the drawn-control scan)
        dm = next(m for m in re.finditer(r'using \(Dependent\(list, "(\w+)"', cs) if re.search(r'CheckboxLabeled\([^;]*ref ' + m.group(1) + r'\b', cs))
        dmasters = {}
        for d in re.findall(r'\.Declare\(([^)]*)\)', cs):
            n = re.findall(r'"(\w+)"', d)
            for x in n[1:]:
                dmasters.setdefault(x, set()).add(n[0])
        scope_keys = set(re.findall(r'"(\w+)"', re.match(r'using \(Dependent\(list, ([^)]*)\)', cs[dm.start():]).group(1)))
        # a dependent whose masters differ from the scope's root and touch none of its keys: planted, it is a second root
        mixed = next(k for k in sorted(dmasters) if k not in scope_keys and not (dmasters[k] & scope_keys)
                     and dmasters[k] != dmasters.get(dm.group(1)))
        plants += [
            ("a dependent dropped from its master declaration (no master, not independent)",
             lambda c, p: (c.replace(decl.group(0), re.sub(r',\s*"' + pure + '"', '', decl.group(0), count=1), 1), p), "no declared master"),
            ("a dependent drawn outside its Dependent scope",
             lambda c, p: (c.replace(dm.group(0), dm.group(0).replace(f'"{dm.group(1)}"', '"zzUnlisted"'), 1), p), "outside a Dependent scope"),
            ("a scope mixing keys with different masters",
             lambda c, p: (c.replace(dm.group(0), dm.group(0).replace("(list, ", f'(list, "{mixed}", '), 1), p), "mixes keys with different masters"),
            ("Reset-all button removed",
             lambda c, p: (c.replace("SettingsKitMastersDrawer.ResetAllButton", "SettingsKitMastersDrawer.ResetAllButtn"), p), "Reset-all"),
            ("masters kit dropped from the csproj",
             lambda c, p: (c, p.replace("SettingsKitMastersDrawer.cs", "SettingsKitMastersDrawr.cs")), "SettingsKitMastersDrawer.cs"),
        ]
    for label, f, want in plants:
        c2, p2 = f(cs, pj)
        total += 1
        if (c2, p2) == (cs, pj):
            print(f"FAIL {name}: {label}: pattern not found")
            bad += 1
            continue
        try:
            e, _ = check(c2, p2, expected, extra, keyed)
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


# FlowWorks' MAIN screen (RimMandrakeFlowWorksMod.cs) draws `if (Section(list, "title", new[] { names }))` blocks, not Group(...):
# no scope tags, but the same promises. Titles are the audited section list; names the screen resets that are not Scribe_Values.
FLOWWORKS_MAIN_SECTIONS = 19   # 12 -> 19: FLOWWORKS_SETTINGS_UNTANGLE_THE_JUNK_DRAWER (2026-10-22) split pits seven ways, Digging / Water engine
FLOWWORKS_MAIN_EXTRA = {"disabledFluids"}


def check_flowworks_main(cs, csproj):
    errs = []
    scribed = {f for f, _ in re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', cs)}
    for f, k in re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', cs):
        if f != k:
            errs.append(f"scribe key {k!r} != field {f!r}")
    a = cs.index("public void DoWindowContents(")
    end = cs.index("lastListHeight = list.CurHeight", a)
    body = cs[a:end]
    secs = list(re.finditer(r'if \(Section\(list, "([^"]+)", new\[\] \{ ([^}]*) \}\)\)', body))
    if len(secs) != len(re.findall(r'\bSection\(list,', body)):
        errs.append("a Section(...) call is not in the audited `if (Section(list, title, new[] {...}))` shape")
    if len(secs) != FLOWWORKS_MAIN_SECTIONS:
        errs.append(f"{len(secs)} sections found, expected {FLOWWORKS_MAIN_SECTIONS}")
    seen = {}
    for idx, m in enumerate(secs):
        title = m.group(1)
        names = re.findall(r'"(\w+)"', m.group(2))
        for n in names:
            if n in seen:
                errs.append(f"{n} listed in two sections: {seen[n]!r} and {title!r}")
            seen[n] = title
            if n not in scribed and n not in FLOWWORKS_MAIN_EXTRA:
                errs.append(f"section {title!r} names {n}, which is not a Scribed setting")
        i = body.index("{", m.end())
        j = balanced_end(body, i)
        if "if (Section(" in body[i:j]:
            errs.append(f"section {title!r} swallows the next section (a closing brace is missing)")
        drawn = set(re.findall(r'ref (\w+)\b', body[i:j])) | set(re.findall(r'(\w+) = (?:\(int\)|Mathf\.\w+\()?list\.Slider', body[i:j]))
        drawn -= set(re.findall(r'\b(?:bool|int|float|string|var)\s+(\w+)\s*=', body[i:j]))
        for d in drawn - set(names):
            if d in scribed:
                errs.append(f"section {title!r} draws {d} but does not list it (it would not reset)")
    for f in sorted(scribed - set(seen)):
        errs.append(f"setting {f} is in no section (no reset, not searchable)")
    for kit in ("SettingsKitCore.cs", "SettingsKitDrawer.cs", "SettingsKitMasters.cs", "SettingsKitMastersDrawer.cs"):
        if kit not in csproj:
            errs.append(f"csproj lacks the {kit} Compile Include")
    if "SettingsKitDrawer.SearchBox" not in cs:
        errs.append("no search box")
    if "SettingsKitMastersDrawer.ResetAllButton" not in cs:
        errs.append("no Reset-all button")
    if "shippedDefaults = CaptureDefaults()" not in cs:
        errs.append("no shippedDefaults snapshot for per-section reset")
    # FLOWWORKS_SETTINGS_MEND_EMPTY_BELOW_RESET: a throw in the long draw must be caught and shown, not left as a blank screen.
    # In the method: list.Begin(...) BEFORE the try (so the catch never leaves the group open), a catch of System.Exception
    # (not a narrower type) that records drawFailure, and list.End() / Widgets.EndScrollView() AFTER the catch. (Until
    # 2026-10-19 this read `"catch" not in <text before the try> and "drawFailure" not in cs`: only the variable's name was
    # really checked, so a narrowed or deleted catch passed.)
    meth = cs[a:cs.index("\n        }\n", a)]
    tr, cat = meth.find("try\n"), meth.find("catch (System.Exception ")
    guard = []
    if tr < 0 or cat < tr:
        guard.append("no try ... catch (System.Exception ...) around the draw")
    else:
        if not re.match(r'catch \(System\.Exception (\w+)\)\s*\{[^}]*drawFailure = \1;', meth[cat:]):
            guard.append("the catch does not record drawFailure")
        if not 0 <= meth.find("list.Begin(") < tr:
            guard.append("list.Begin is not before the try")
        if not (meth.rfind("list.End();") > cat and meth.rfind("Widgets.EndScrollView();") > cat):
            guard.append("list.End / EndScrollView are not after the catch")
    if guard:
        errs.append("the screen's draw is not guarded (a throw would leave it blank below Reset all): " + "; ".join(guard))
    return errs


def run_flowworks_main():
    src = os.path.join(ROOT, "FlowWorks", "Source")
    cs = open(os.path.join(src, "RimMandrakeFlowWorksMod.cs"), encoding="utf-8").read()
    pj = open(os.path.join(src, "RimMandrake_FlowWorks.csproj"), encoding="utf-8").read()
    bad = total = 0
    e = check_flowworks_main(cs, pj)
    total += 1
    print(("ok   " if not e else "FAIL ") + "FlowWorks#Main: real screen, every setting in exactly one resettable section" + ("" if not e else " | " + "; ".join(e[:4])))
    bad += bool(e)
    first = re.search(r'if \(Section\(list, "([^"]+)", new\[\] \{ ([^}]*) \}\)\)', cs)
    names = re.findall(r'"(\w+)"', first.group(2))
    second = list(re.finditer(r'if \(Section\(list, "([^"]+)", new\[\] \{ ', cs))[1]
    plants = [
        ("a name dropped from its section array", lambda c, p: (c.replace(f', "{names[-1]}" }})', ' })', 1), p), "no section"),
        ("a setting in two sections", lambda c, p: (c.replace(second.group(0), second.group(0) + f'"{names[0]}", ', 1), p), "two sections"),
        ("a section names a non-setting", lambda c, p: (c.replace(f', "{names[-1]}" }})', ', "notASettingAtAll" })', 1), p), "not a Scribed setting"),
        ("a Section's closing brace lost", lambda c, p: (c.replace("            }\n\n            if (Section(", "\n            if (Section(", 1), p), "swallows|unbalanced"),
        ("Reset-all removed", lambda c, p: (c.replace("SettingsKitMastersDrawer.ResetAllButton", "SettingsKitMastersDrawer.ResetAllButtn"), p), "Reset-all"),
        ("kit dropped from the csproj", lambda c, p: (c, p.replace("SettingsKitMastersDrawer.cs", "SettingsKitMastersDrawr.cs")), "SettingsKitMastersDrawer.cs"),
        ("the draw guard removed", lambda c, p: (c.replace("drawFailure", "drawFailur3"), p), "not guarded"),
        ("the draw guard narrowed to one exception type",
         lambda c, p: (c.replace("catch (System.Exception ex)", "catch (System.ArgumentException ex)", 1), p), "not guarded"),
        ("list.End moved inside the try",
         lambda c, p: (c.replace("            list.End();\n            Widgets.EndScrollView();", "            Widgets.EndScrollView();", 1)
                       .replace("RM_WaterMendSettings.DoSettingsSection);\n            }\n            catch",
                                "RM_WaterMendSettings.DoSettingsSection);\n            list.End();\n            }\n            catch", 1), p),
         "not guarded"),
    ]
    for label, f, want in plants:
        c2, p2 = f(cs, pj)
        total += 1
        if (c2, p2) == (cs, pj):
            print(f"FAIL FlowWorks#Main: {label}: pattern not found")
            bad += 1
            continue
        try:
            e = check_flowworks_main(c2, p2)
        except Exception as ex:
            e = [f"exception {ex}"]
        hit = any(w in x for x in e for w in want.split("|"))
        print(("ok   " if hit else "FAIL ") + f"FlowWorks#Main: {label}" + ("" if hit else f" | wanted {want!r}, got {e[:2]}"))
        bad += not hit
    return bad, total


# FLOWWORKS_SETTINGS_MEND_EMPTY_BELOW_RESET (real cause, 2026-10-19): a Listing_Standard inside a scroll view whose view
# height is fed back from list.CurHeight MUST set maxOneColumn. Vanilla Listing.NewColumnIfNeeded wraps any row that would
# pass listingRect.height into a new column at x = ColumnWidth + 17 (outside the scroll view, so invisible), and CurHeight is
# curY of the LAST column only. Fed back as next frame's view height, it shrinks every frame: FlowWorks' screen collapsed to
# search box + "Reset all" and nothing else. listing_model() replays that arithmetic; scan_scroll_listings() finds the shape.
def listing_model(rows, first_height, max_one_column, frames=12):
    """Rows (heights) drawn per frame into a view of the last measured height; returns (heights per frame, rows in column 0
    on the last frame). Mirrors Verse.Listing.GetRect / NewColumnIfNeeded / CurHeight (decompiled 1.6)."""
    h, seen = first_height, []
    for _ in range(frames):
        cur, col, col0 = 0.0, 0, 0
        for r in rows:
            if not max_one_column and cur + r > h:
                col, cur = col + 1, 0.0
            if col == 0:
                col0 += 1
            cur += r
        h = cur + 40.0
        seen.append(h)
    return seen, col0


def scan_scroll_listings(files):
    """[(path, why)] for every `new Listing_Standard ...;` statement in a file that scrolls (BeginScrollView) lacking
    maxOneColumn = true. Per statement, not per file (a second unflagged listing in a flagged file must fail), and whether or
    not the height is fed back from CurHeight: a fixed-height view wraps the same way once content outgrows it."""
    bad = []
    for path, text in files:
        if "BeginScrollView" not in text:
            continue
        for m in re.finditer(r"new Listing_Standard\b[^;]*;", text):
            if "maxOneColumn = true" not in m.group(0):
                bad.append((path, "scrolling Listing_Standard without maxOneColumn = true: " + m.group(0)[:60]))
    return bad


def check_scroll_listings():
    bad = total = 0
    rows = [30.0, 24.0, 32.0] + [24.0] * 600          # notice, search, Reset all, then the sections
    wrap, col0 = listing_model(rows, 11600.0, False)
    one, col0_one = listing_model(rows, 11600.0, True)
    for label, ok in (("model: without maxOneColumn the measured height collapses below the content", wrap[-1] < 600 * 24 and col0 < len(rows)),
                      ("model: with maxOneColumn every row stays in column one and the height holds", col0_one == len(rows) and one[-1] >= sum(rows))):
        total += 1
        print(("ok   " if ok else "FAIL ") + "ScrollListing: " + label)
        bad += not ok
    files = []
    for dp, _, fns in os.walk(os.path.dirname(ROOT)):   # src/: all three tiers (RimMandrake, RimStarWars, RimUtinni)
        for fn in fns:
            if fn.endswith(".cs"):
                fp = os.path.join(dp, fn)
                try:
                    files.append((fp, open(fp, encoding="utf-8", errors="replace").read()))
                except OSError:
                    pass
    found = scan_scroll_listings(files)
    total += 1
    print(("ok   " if not found else "FAIL ") + f"ScrollListing: {len(files)} .cs files, every scrolling listing is one column"
          + ("" if not found else " | " + "; ".join(os.path.relpath(p, ROOT) for p, _ in found[:6])))
    bad += bool(found)
    planted = [(p, t.replace("maxOneColumn = true", "maxOneColumn = false")) for p, t in files
               if p.endswith("RimMandrakeFlowWorksMod.cs")]
    total += 1
    hit = bool(planted) and bool(scan_scroll_listings(planted))
    print(("ok   " if hit else "FAIL ") + "ScrollListing: plant (FlowWorks maxOneColumn removed) is caught")
    bad += not hit
    # a flagged file that also holds one unflagged scrolling listing (the per-file test this replaced passed it)
    twin = [(p, t + "\n Listing_Standard other = new Listing_Standard { ColumnWidth = 9f };\n") for p, t in files
            if p.endswith("RM_CreatureBehaviorsMod.cs")]
    total += 1
    hit = bool(twin) and bool(scan_scroll_listings(twin))
    print(("ok   " if hit else "FAIL ") + "ScrollListing: plant (a second, unflagged listing in a flagged file) is caught")
    bad += not hit
    # the tiers outside RimMandrake are walked (RimUtinni and RimStarWars settings screens scroll too)
    total += 1
    tiers = {os.path.relpath(p, os.path.dirname(ROOT)).split(os.sep)[0] for p, t in files if "BeginScrollView" in t}
    hit = {"RimMandrake", "RimStarWars", "RimUtinni"} <= tiers
    print(("ok   " if hit else "FAIL ") + f"ScrollListing: scroll screens found in tiers {sorted(tiers)}")
    bad += not hit
    return bad, total


def main():
    bad = total = 0
    for name, (cs_name, pj_name, expected, extra) in MODS.items():
        b, t = run_mod(name, cs_name, pj_name, expected, extra)
        bad += b
        total += t
    b, t = run_flowworks_main()
    bad += b
    total += t
    b, t = check_biomes_shell()
    bad += b
    total += t
    b, t = check_scroll_listings()
    bad += b
    total += t
    print(f"settings screens selftest: {total - bad}/{total} ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
