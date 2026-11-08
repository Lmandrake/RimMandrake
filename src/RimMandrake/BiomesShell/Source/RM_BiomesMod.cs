using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // ════════════════════════════════════════════════════════════════════
    // BAROQUE_BIOMES_COMPOSE_1 — the settings shell of "RimMandrake: Baroque
    // Biomes" (spec: design/RimMandrake/biome_mod_unification_spec.md §5).
    //
    // The roster is NOT hardcoded here. deploy_custom_mods.py --compose biomes
    // writes Biomes.roster.xml at the unified mod's root from
    // src/RimMandrake/Biomes.compose.json (key, label, blurb, group, and the
    // concrete BiomeDef defNames each entry ships), and this reads it.
    //
    // WHAT A TOGGLE GATES TODAY (Wave 0):
    //   worldgen only — every BiomeDef of a toggled-off entry gets
    //   generatesNaturally = false, which is the one gate
    //   WorldGenStep_Terrain.BiomeFrom reads (decompiled 1.6: `implemented &&
    //   generatesNaturally && Worker.CanPlaceOnLayer`). No Harmony, no def is
    //   unloaded, nothing is saved in the game file; the original value is
    //   restored when the toggle comes back on.
    // MECHANICS (spec §5 arm 2): each biome's own assembly reads
    //   RM_BiomesSettings.Enabled(key) by reflection (it still ships standalone,
    //   where this DLL is absent) and adds its key to mechanicsGated. Wired
    //   biome by biome; today only Pyrelands (PyrelandsMechanicsGate.cs).
    // ════════════════════════════════════════════════════════════════════
    public class RosterEntry
    {
        public string key;
        public string label;
        public string group;
        public string blurb;
        public List<string> biomeDefs = new List<string>();
    }

    public class RM_BiomesSettings : ModSettings
    {
        // Absent key = enabled. Defaults = shipped behaviour = ALL ON.
        public Dictionary<string, bool> enabled = new Dictionary<string, bool>();

        // PACK_ANIMALS_RESTORE_EMPTY_SADDLES (decision taken by question card 2026-10-11, "add them to vanilla
        // factions"): every faction trader group carries our own pack beasts (RM_Tirbak, RM_Vellak, RM_Vaalok), so a
        // caravan can reach the biomes whose pack list names only them. Read by RM_PatchOperationBiomesSettingGate at
        // patch time, so a change takes effect on the NEXT game start.
        public static bool ownedCaravanCarriers = true;

        // CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD (owner 2026-10-18): trees whose def carries RM_CanopyExtension (the Titanic
        // tier) draw their trunk always and their canopy only when zoomed out below canopyThresholdPx screen pixels per
        // cell, fading in over canopyFadePx (RM_Canopy.cs). Off = the vanilla whole-tree picture. Applies at once.
        public static bool canopyEnabled = true;
        public static float canopyThresholdPx = CanopyMath.DefaultThresholdPx;
        public static float canopyFadePx = CanopyMath.DefaultFadePx;

        // WORLDMAP_BORDER_BLEND (2026-10-20): soft gradients between neighbouring land biomes on the planet, and seas that
        // deepen away from the coast (RM_WorldLook.cs). Looks only; the world is untouched. Applies at once.
        public static bool worldBorderBlend = true;
        public static bool worldSeaDepth = true;

        // BIOME SWIRLS (owner by card 2026-10-20, WORLD_FACES_REDRAW_ABYSS_ROT_RUST): a continuous swirl layer drawn over the
        // whole of the Abyss and The Rot on the planet (RM_WorldLook.BuildSwirls). Looks only. Applies at once.
        public static bool worldBiomeSwirls = true;

        // BIOME DECALS (WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE): 2-3 small glyphs per flat land tile from the biome's own atlas
        // (World/Decals/<defName>), fading out as the camera rises past mid zoom (RM_WorldDecals.cs). Looks only. Applies at once.
        public static bool worldBiomeDecals = true;

        // SOFT HILLS (2026-10-20): our own hill decal art on the planet's shared hill materials (RM_WorldLook.ApplyHills).
        // Looks only; hilliness is untouched. Applies at once.
        public static bool worldSoftHills = true;

        // SUN-LIT PEAKS (owner by card 2026-10-20, WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS): hills and mountains drawn as
        // peak clusters turned to face the substellar point (RM_WorldPeaks.cs). Looks only. Applies at once (redraw).
        public static bool worldSunPeaks = true;

        // WORLD_PATHS_READABLE (2026-10-20): road colours/widths and river colour/width/material on the planet
        // (RM_WorldPaths.cs). Looks only; links are untouched. Applies at once.
        public static bool worldReadablePaths = true;

        // RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT (2026-11-02): rivers drawn as rivers (thin at the head, widening, fanning at
        // the mouth, thinning to a dry trace where they die inland, a pale bank and a faint highlight) and roads worn by
        // kind (dirt in worn dashes, stone lighter, the ancient highway broken in pieces). Both ride on readable paths
        // (they need its river material); looks only, links untouched. Applies at once (the planet redraws).
        public static bool worldDrawnRivers = true;
        public static bool worldWornRoads = true;

        // SOFT LANDMARK ICONS (owner by card 2026-10-20, LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE): Odyssey landmark icons
        // draw smaller and fainter on the planet, back to full near the ground (RM_WorldLandmarks.cs). Looks only; which
        // tiles carry landmarks is untouched. Applies at once.
        public static bool worldSoftLandmarks = true;
        public static float worldLandmarkSize = 0.6f;
        public static float worldLandmarkOpacity = 0.55f;
        public static bool worldLandmarksFullClose = true;

        /// <summary>The planet-look block back to its shipped values (the defaults in the field initialisers above).</summary>
        public static void ResetWorldLook()
        {
            worldBorderBlend = true;
            worldSeaDepth = true;
            worldBiomeSwirls = true;
            worldBiomeDecals = true;
            worldSoftHills = true;
            worldSunPeaks = true;
            worldReadablePaths = true;
            worldDrawnRivers = true;
            worldWornRoads = true;
            worldSoftLandmarks = true;
            worldLandmarkSize = 0.6f;
            worldLandmarkOpacity = 0.55f;
            worldLandmarksFullClose = true;
        }

        public static RM_BiomesSettings Instance;

        // Roster keys whose own mod gates its mechanics on Enabled(key), added by that mod at startup by reflection
        // (Pyrelands: PyrelandsMechanicsGate). Drives the tooltip only; nothing here enforces it.
        public static readonly HashSet<string> mechanicsGated = new HashSet<string>();

        public static bool Enabled(string key)
        {
            if (Instance == null || key == null) return true;
            return !Instance.enabled.TryGetValue(key, out bool on) || on;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref enabled, "enabled", LookMode.Value, LookMode.Value);
            Scribe_Values.Look(ref ownedCaravanCarriers, "ownedCaravanCarriers", true);
            Scribe_Values.Look(ref canopyEnabled, "canopyEnabled", true);
            Scribe_Values.Look(ref canopyThresholdPx, "canopyThresholdPx", CanopyMath.DefaultThresholdPx);
            Scribe_Values.Look(ref canopyFadePx, "canopyFadePx", CanopyMath.DefaultFadePx);
            Scribe_Values.Look(ref worldBorderBlend, "worldBorderBlend", true);
            Scribe_Values.Look(ref worldSeaDepth, "worldSeaDepth", true);
            Scribe_Values.Look(ref worldBiomeSwirls, "worldBiomeSwirls", true);
            Scribe_Values.Look(ref worldBiomeDecals, "worldBiomeDecals", true);
            Scribe_Values.Look(ref worldSoftHills, "worldSoftHills", true);
            Scribe_Values.Look(ref worldSunPeaks, "worldSunPeaks", true);
            Scribe_Values.Look(ref worldReadablePaths, "worldReadablePaths", true);
            Scribe_Values.Look(ref worldDrawnRivers, "worldDrawnRivers", true);
            Scribe_Values.Look(ref worldWornRoads, "worldWornRoads", true);
            Scribe_Values.Look(ref worldSoftLandmarks, "worldSoftLandmarks", true);
            Scribe_Values.Look(ref worldLandmarkSize, "worldLandmarkSize", 0.6f);
            Scribe_Values.Look(ref worldLandmarkOpacity, "worldLandmarkOpacity", 0.55f);
            Scribe_Values.Look(ref worldLandmarksFullClose, "worldLandmarksFullClose", true);
            if (enabled == null) enabled = new Dictionary<string, bool>();
        }
    }

    public class RM_BiomesMod : Mod
    {
        public const string LogPrefix = "[Baroque Biomes] ";
        public static RM_BiomesMod Instance;
        public static RM_BiomesSettings settings;
        public static List<RosterEntry> roster = new List<RosterEntry>();

        private Vector2 scroll;

        public RM_BiomesMod(ModContentPack content) : base(content)
        {
            Instance = this;
            settings = GetSettings<RM_BiomesSettings>();
            // What the planet was last drawn with = the loaded settings, so the first change after a load redraws it.
            worldLookShown = RM_BiomesSettings.worldBorderBlend + "/" + RM_BiomesSettings.worldSeaDepth + "/" + RM_BiomesSettings.worldBiomeSwirls;
            peaksShown = RM_BiomesSettings.worldSunPeaks;
            canopyShown = RM_BiomesSettings.canopyEnabled;
            // seeded from the SAVED settings: an all-on seed missed the redraw when a saved-off toggle was turned on
            worldLookShown = WorldLookKey();
            peaksShown = RM_BiomesSettings.worldSunPeaks;
            RM_BiomesSettings.Instance = settings;
            roster = ReadRoster(Path.Combine(content.RootDir, "Biomes.roster.xml"));
        }

        private static List<RosterEntry> ReadRoster(string path)
        {
            var list = new List<RosterEntry>();
            if (!File.Exists(path))
            {
                Log.Error(LogPrefix + "no Biomes.roster.xml at " + path
                          + " — this folder was not built by deploy_custom_mods.py --compose biomes. "
                          + "No biome toggles are available.");
                return list;
            }
            var doc = new XmlDocument();
            doc.Load(path);
            foreach (XmlNode n in doc.DocumentElement.SelectNodes("entry"))
            {
                var e = new RosterEntry
                {
                    key = n.Attributes["key"]?.Value,
                    label = n.Attributes["label"]?.Value,
                    group = n.Attributes["group"]?.Value ?? "biome",
                    blurb = n.SelectSingleNode("blurb")?.InnerText ?? "",
                };
                foreach (XmlNode b in n.SelectNodes("biomeDef"))
                    e.biomeDefs.Add(b.InnerText.Trim());
                list.Add(e);
            }
            return list;
        }

        public override string SettingsCategory() => "RimMandrake: Baroque Biomes";

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_BiomesGate.Apply("settings changed");
            if (canopyShown != RM_BiomesSettings.canopyEnabled)
            {
                canopyShown = RM_BiomesSettings.canopyEnabled;
                RM_Canopy.Reprint();
            }
            if (worldLookShown != WorldLookKey())
            {
                worldLookShown = WorldLookKey();
                if (Current.ProgramState == ProgramState.Playing) Find.World?.renderer?.SetAllLayersDirty();
            }
            if (RM_WorldLook.hillsApplied != RM_BiomesSettings.worldSoftHills) RM_WorldLook.ApplyHills("settings changed");
            if (peaksShown != RM_BiomesSettings.worldSunPeaks)
            {
                peaksShown = RM_BiomesSettings.worldSunPeaks;
                if (Current.ProgramState == ProgramState.Playing) Find.World?.renderer?.SetAllLayersDirty();
            }
            if (RM_WorldPaths.applied != RM_BiomesSettings.worldReadablePaths
                || RM_WorldPaths.drawnRivers != RM_BiomesSettings.worldDrawnRivers
                || RM_WorldPaths.wornRoads != RM_BiomesSettings.worldWornRoads)
            {
                RM_WorldPaths.Apply("settings changed");
                if (Current.ProgramState == ProgramState.Playing) Find.World?.renderer?.SetAllLayersDirty();
            }
        }

        string worldLookShown;
        static string WorldLookKey() => RM_BiomesSettings.worldBorderBlend + "/" + RM_BiomesSettings.worldSeaDepth + "/"
            + RM_BiomesSettings.worldBiomeSwirls + "/" + RM_BiomesSettings.worldBiomeDecals;
        bool peaksShown = true;

        // MOD_OPTIONS_RETROFIT_1: per-entry toggles live in the Scribed RM_BiomesSettings.enabled dictionary (absent key = on).
        // Scope AUDITED against the read site (2026-10-10): RM_BiomesGate.Apply writes BiomeDef.generatesNaturally, which only
        // WorldGenStep_Terrain.BiomeFrom reads -> NewMapsOnly for an entry that ships BiomeDefs. Its other readers are the member mods
        // listed in RM_BiomesSettings.mechanicsGated (live: those mechanics stop on existing maps). An entry with no BiomeDefs and no
        // mechanics reader (every engine/mechanic entry today) gates nothing yet: DEAD.
        private float viewHeight = 1200f;
        private static bool canopyShown = true;
        private string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        private static bool Group(Listing_Standard list, string title, string note, string searchQuery, List<RosterEntry> members)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (var e in members)
                    if (!hit && (RimMandrake.Shared.SettingsKitCore.Matches(e.label ?? "", searchQuery)
                                 || RimMandrake.Shared.SettingsKitCore.Matches(e.key ?? "", searchQuery))) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label(note);
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () =>
            {
                foreach (var e in members) settings.enabled.Remove(e.key);   // absent key = on = the shipped default
            });
            return true;
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            var list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            list.Label("One toggle per roster entry. An entry that ships biomes stops those biomes being placed on new worlds "
                     + "(WORLDGEN-AFFECTING; takes effect on the next new world). Existing maps keep their terrain and creatures; "
                     + "no content is unloaded.");
            list.GapLine();

            if (string.IsNullOrWhiteSpace(searchQuery)
                || RimMandrake.Shared.SettingsKitCore.Matches("caravan pack animals traders", searchQuery))
            {
                list.CheckboxLabeled("Traders bring our pack animals [next game start]", ref RM_BiomesSettings.ownedCaravanCarriers,
                    "Every faction's trade caravans may lead tirbak, vellak and vaalok as pack animals. Without them no land "
                    + "trade caravan can reach the Weeping Stones or the Stillsand, whose only pack animals they are.\n\n"
                    + "Default: on. Takes effect on the next game start (it edits faction defs while the game loads).");
                RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => RM_BiomesSettings.ownedCaravanCarriers = true);
                list.GapLine();
            }


            if (string.IsNullOrWhiteSpace(searchQuery)
                || RimMandrake.Shared.SettingsKitCore.Matches("canopy trees titanic trunk zoom forest crown", searchQuery))
            {
                list.CheckboxLabeled("Titanic trees: trunk close up, canopy zoomed out [now]", ref RM_BiomesSettings.canopyEnabled,
                    "The largest trees (the sweetline tree) draw only their trunk when you are zoomed in, so the colony under "
                    + "them stays visible. Zoom out and their canopy fades in over the trunk, so a forested map reads as a forest. "
                    + "Pawns always draw on top of the canopy.\n\nOff: these trees draw their whole picture at every zoom, as "
                    + "vanilla does.\n\nDefault: on. Takes effect at once on running maps.");
                if (RM_BiomesSettings.canopyEnabled)
                {
                    RM_BiomesSettings.canopyThresholdPx = list.SliderLabeled("    Canopy appears below: "
                        + RM_BiomesSettings.canopyThresholdPx.ToString("0") + " px per cell (default "
                        + CanopyMath.DefaultThresholdPx.ToString("0") + ")",
                        RM_BiomesSettings.canopyThresholdPx, CanopyMath.MinThresholdPx, CanopyMath.MaxThresholdPx, 0.5f,
                        "How far out you must zoom before the canopy shows, as screen pixels per map cell. Higher shows it sooner. "
                        + "Vanilla's furthest zoom is about 9 px per cell on a 1080p screen.");
                    RM_BiomesSettings.canopyFadePx = list.SliderLabeled("    Canopy fade width: "
                        + RM_BiomesSettings.canopyFadePx.ToString("0.0") + " px (default " + CanopyMath.DefaultFadePx.ToString("0") + ")",
                        RM_BiomesSettings.canopyFadePx, 0f, CanopyMath.MaxFadePx, 0.5f,
                        "Over how many px per cell the canopy fades from invisible to solid. 0 is a hard switch.");
                }
                RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () =>
                {
                    RM_BiomesSettings.canopyEnabled = true;
                    RM_BiomesSettings.canopyThresholdPx = CanopyMath.DefaultThresholdPx;
                    RM_BiomesSettings.canopyFadePx = CanopyMath.DefaultFadePx;
                });
                list.GapLine();
            }

            if (string.IsNullOrWhiteSpace(searchQuery)
                || RimMandrake.Shared.SettingsKitCore.Matches("world map planet borders blend sea depth water coast roads rivers highway hills mountains swirls abyss rot decals glyphs marks", searchQuery))
            {
                list.CheckboxLabeled("Planet: soft borders between biomes [now]", ref RM_BiomesSettings.worldBorderBlend,
                    "On the world map, the edge between two land biomes fades over half a tile on each side instead of "
                    + "a hard hex line.\n\nLooks only. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: seas deepen away from the coast [now]", ref RM_BiomesSettings.worldSeaDepth,
                    "On the world map, water is lighter near the shore and darker far from it.\n\nLooks only; tile "
                    + "elevations are not changed. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: swirls over the Abyss and The Rot [now]", ref RM_BiomesSettings.worldBiomeSwirls,
                    "On the world map, a continuous layer of swirls is drawn across the whole of each of these biomes: pale, "
                    + "eerie currents over the near-black Abyss and wild-coloured swirls over The Rot. It fades out across the "
                    + "biome's border.\n\nLooks only. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: biome decals [now]", ref RM_BiomesSettings.worldBiomeDecals,
                    "On the world map, flat land carries two or three small drawn marks per tile (dunes, shrubs, stones... "
                    + "taken from each biome's own look), so a region reads at a glance when you zoom in. They fade out as "
                    + "you zoom out past mid height, so the far view stays clean. A biome without its own marks shows none.\n\n"
                    + "Looks only. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: soft hill shading [now]", ref RM_BiomesSettings.worldSoftHills,
                    "On the world map, hills and mountains draw as soft dark relief that takes the colour of the land "
                    + "under them, instead of the vanilla brown outlined blots.\n\nLooks only; which tiles are hilly is "
                    + "not changed. Default: on. Takes effect at once.");
                list.CheckboxLabeled("Planet: sun-lit mountain peaks [now]", ref RM_BiomesSettings.worldSunPeaks,
                    "On the world map, hills and mountains draw as clusters of peaks with a lit side and a shaded side, "
                    + "every one turned to face the sun (the substellar point), with long shadows near the terminator and snow "
                    + "where the land is cold. Tiles with a road or river show no peak, so routes stay readable. Off restores the "
                    + "previous hill drawing (see soft hill shading).\n\nLooks only; which tiles are hilly is not changed. "
                    + "Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: readable roads and rivers [now]", ref RM_BiomesSettings.worldReadablePaths,
                    "On the world map, roads get a dark casing and a colour per kind (umber dirt, grey-brown stone, "
                    + "old dark asphalt on the ancient highway) and rivers get a bank and a hard edge, a little wider (their colour "
                    + "stays FlowWorks' River Colours where that is on, else blue-grey). Off restores the vanilla road and river "
                    + "look, and turns off the two settings below.\n\nLooks only; which tiles have roads or rivers is "
                    + "not changed. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: drawn rivers [now]", ref RM_BiomesSettings.worldDrawnRivers,
                    "Needs readable roads and rivers. On the world map, a river starts thin at its head and widens "
                    + "downstream, fans out where it meets the sea or a lake, and thins to a pale dry trace where it dies "
                    + "inland. Its bank is a pale line instead of a dark one, with a faint highlight down the middle of the "
                    + "water. Off: rivers keep one width per kind and a dark bank.\n\nLooks only; which tiles have rivers "
                    + "is not changed. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: worn roads [now]", ref RM_BiomesSettings.worldWornRoads,
                    "Needs readable roads and rivers. On the world map, dirt roads show as a worn track (thinner in "
                    + "stretches), stone roads are lighter and solid, and the ancient highway is broken into pieces with "
                    + "gaps, old asphalt from long ago. Off: every road is drawn whole.\n\nLooks only; which tiles have "
                    + "roads, and travel along them, are not changed. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: soft landmark icons [now]", ref RM_BiomesSettings.worldSoftLandmarks,
                    "On the world map, landmark icons (ruins, vents, caves, cliffs...) draw smaller and fainter, so a region "
                    + "full of them no longer reads as speckle over its land, rivers and roads.\n\nLooks only; every "
                    + "landmark stays on its tile and keeps its name and inspect text. Default: on. Takes effect at once.");
                if (RM_BiomesSettings.worldSoftLandmarks)
                {
                    RM_BiomesSettings.worldLandmarkSize = list.SliderLabeled("    Landmark icon size: "
                        + (RM_BiomesSettings.worldLandmarkSize * 100f).ToString("0") + "% (default 60%)",
                        RM_BiomesSettings.worldLandmarkSize, 0.2f, 1f, 0.5f, "Size of a landmark icon against the vanilla size.");
                    RM_BiomesSettings.worldLandmarkOpacity = list.SliderLabeled("    Landmark icon opacity: "
                        + (RM_BiomesSettings.worldLandmarkOpacity * 100f).ToString("0") + "% (default 55%)",
                        RM_BiomesSettings.worldLandmarkOpacity, 0.1f, 1f, 0.5f, "Opacity of a landmark icon; 100% is vanilla.");
                    list.CheckboxLabeled("    Full-size icons when zoomed in close", ref RM_BiomesSettings.worldLandmarksFullClose,
                        "Zooming in towards the ground brings landmark icons back to their vanilla size and opacity, so one "
                        + "is easy to find and read where you look at single tiles.\n\nDefault: on.");
                }
                RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, RM_BiomesSettings.ResetWorldLook);
                list.GapLine();
            }

            foreach (var g in new[] { "biome", "engine", "kit" })
            {
                var members = roster.Where(e => e.group == g).ToList();
                if (members.Count == 0) continue;
                string title = g == "biome" ? "Biomes (WORLDGEN-AFFECTING)" : g == "engine" ? "Engines" : "Mechanics";
                string tag = RimMandrake.Shared.SettingsKitCore.ScopeTag(RimMandrake.Shared.SettingScope.NewMapsOnly);
                // A group mixes entries that ship biomes (worldgen), entries whose own mod reads the toggle at once
                // (mechanicsGated, e.g. the Explosive Growth engine) and entries nothing reads yet; say each that applies.
                var notes = new List<string>();
                if (members.Any(e => e.biomeDefs.Count > 0))
                    notes.Add(tag + " changes only affect worlds generated afterwards");
                if (members.Any(e => e.biomeDefs.Count == 0 && RM_BiomesSettings.mechanicsGated.Contains(e.key)))
                    notes.Add(RimMandrake.Shared.SettingsKitCore.ScopeTag(RimMandrake.Shared.SettingScope.Now)
                              + " " + string.Join(", ", members.Where(e => e.biomeDefs.Count == 0 && RM_BiomesSettings.mechanicsGated.Contains(e.key)).Select(e => e.label))
                              + ": switches that mechanic on or off on running maps at once");
                if (members.Any(e => e.biomeDefs.Count == 0 && !RM_BiomesSettings.mechanicsGated.Contains(e.key)))
                    notes.Add("[no effect yet] " + string.Join(", ", members.Where(e => e.biomeDefs.Count == 0 && !RM_BiomesSettings.mechanicsGated.Contains(e.key)).Select(e => e.label))
                              + ": recorded, but nothing reads these yet; each is wired per mod later");
                string note = string.Join("\n", notes);
                if (!Group(list, title, note, searchQuery, members)) continue;
                foreach (var e in members)
                {
                    if (!string.IsNullOrWhiteSpace(searchQuery)
                        && !RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery)
                        && !RimMandrake.Shared.SettingsKitCore.Matches(e.label ?? "", searchQuery)
                        && !RimMandrake.Shared.SettingsKitCore.Matches(e.key ?? "", searchQuery)) continue;
                    bool on = RM_BiomesSettings.Enabled(e.key);
                    bool was = on;
                    string tip = e.blurb
                        + (e.biomeDefs.Count > 0
                            ? "\n\nAffects world generation — takes effect on the next new world. "
                              + "Existing maps keep their terrain and creatures; this stops new placement.\n"
                              + (RM_BiomesSettings.mechanicsGated.Contains(e.key)
                                  ? "Also switches this biome's mechanics off at once, on maps already running.\n" : "")
                              + "Biome defs: " + string.Join(", ", e.biomeDefs)
                            : RM_BiomesSettings.mechanicsGated.Contains(e.key)
                                ? "\n\nThis entry ships no biome of its own. Its toggle switches this mechanic on or off at once, "
                                  + "on maps already running; its own settings page has a further switch, and both must be on."
                                : "\n\nThis entry ships no biome of its own; its toggle is recorded for "
                                  + "the mechanics gate, which is wired per mod. Nothing reads it yet.");
                    list.CheckboxLabeled(e.label, ref on, tip);
                    if (on != was) settings.enabled[e.key] = on;
                    Text.Font = GameFont.Tiny;
                    GUI.color = Color.gray;
                    list.Label("    " + e.blurb);
                    GUI.color = Color.white;
                    Text.Font = GameFont.Small;
                }
                list.GapLine();
            }
            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_BiomesGate
    {
        // Original generatesNaturally per BiomeDef, captured once before any gating.
        private static readonly Dictionary<BiomeDef, bool> original = new Dictionary<BiomeDef, bool>();

        static RM_BiomesGate()
        {
            int mapped = 0;
            var missing = new List<string>();
            foreach (var e in RM_BiomesMod.roster)
                foreach (var dn in e.biomeDefs)
                {
                    var def = DefDatabase<BiomeDef>.GetNamedSilentFail(dn);
                    if (def == null) { missing.Add(e.key + "/" + dn); continue; }
                    if (!original.ContainsKey(def)) original[def] = def.generatesNaturally;
                    mapped++;
                }
            Log.Message(RM_BiomesMod.LogPrefix + "roster " + RM_BiomesMod.roster.Count + " entries ("
                        + string.Join(", ", RM_BiomesMod.roster.Select(e => e.key + ":" + e.biomeDefs.Count))
                        + "); " + mapped + " BiomeDef(s) mapped"
                        + (missing.Count > 0 ? "; NOT LOADED: " + string.Join(", ", missing) : ""));
            if (missing.Count > 0)
                Log.Warning(RM_BiomesMod.LogPrefix + missing.Count
                            + " roster BiomeDef(s) did not load — their toggle gates nothing: "
                            + string.Join(", ", missing));
            Apply("startup");
        }

        public static void Apply(string why)
        {
            var off = new List<string>();
            foreach (var e in RM_BiomesMod.roster)
            {
                bool on = RM_BiomesSettings.Enabled(e.key);
                foreach (var dn in e.biomeDefs)
                {
                    var def = DefDatabase<BiomeDef>.GetNamedSilentFail(dn);
                    if (def == null || !original.TryGetValue(def, out bool orig)) continue;
                    def.generatesNaturally = on && orig;
                    if (!on) off.Add(dn);
                }
            }
            Log.Message(RM_BiomesMod.LogPrefix + "worldgen gate applied (" + why + "): "
                        + (off.Count == 0 ? "all biomes on" : "OFF -> " + string.Join(", ", off)));
        }
    }

    // A PatchOperation that respects a Baroque Biomes Mod Settings toggle. Same shape and reasoning as
    // src/RimUtinni/UtinniPatches/Source/PatchOperationSettingGate.cs: LoadedModManager constructs RM_BiomesMod
    // (GetSettings, so the statics hold the player's saved choices) BEFORE it applies patches, so a change takes
    // effect on the NEXT game start. Named switch, not reflection: a typo in the XML is loud, never a silent "on".
    public class RM_PatchOperationBiomesSettingGate : PatchOperation
    {
        public string setting;
        public PatchOperation match;
        public PatchOperation nomatch;

        protected override bool ApplyWorker(XmlDocument xml)
        {
            bool on;
            switch (setting)
            {
                case "ownedCaravanCarriers":
                    on = RM_BiomesSettings.ownedCaravanCarriers;
                    break;
                default:
                    Log.Error(RM_BiomesMod.LogPrefix + "RM_PatchOperationBiomesSettingGate: unknown setting '" + setting + "'.");
                    return false;
            }
            PatchOperation branch = on ? match : nomatch;
            return branch == null || branch.Apply(xml);
        }
    }
}
