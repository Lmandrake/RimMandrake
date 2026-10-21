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

        // GIANT_MUSHROOM_DRAW_FIX_SOUTH_GOES_FRONT (owner 2026-10-16): on maps in our biomes, of two overlapping plants the
        // more southern one draws in front (RM_PlantDrawOrder.cs). Draw order only; applies at once on running maps.
        public static bool plantDrawOrderSouthInFront = true;

        // WORLDMAP_BORDER_BLEND (2026-10-20): soft gradients between neighbouring land biomes on the planet, and seas that
        // deepen away from the coast (RM_WorldLook.cs). Looks only; the world is untouched. Applies at once.
        public static bool worldBorderBlend = true;
        public static bool worldSeaDepth = true;

        // WORLD_PATHS_READABLE (2026-10-20): road colours/widths and river colour/width/material on the planet
        // (RM_WorldPaths.cs). Looks only; links are untouched. Applies at once.
        public static bool worldReadablePaths = true;

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
            Scribe_Values.Look(ref plantDrawOrderSouthInFront, "plantDrawOrderSouthInFront", true);
            Scribe_Values.Look(ref worldBorderBlend, "worldBorderBlend", true);
            Scribe_Values.Look(ref worldSeaDepth, "worldSeaDepth", true);
            Scribe_Values.Look(ref worldReadablePaths, "worldReadablePaths", true);
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
            plantDrawOrderShown = RM_BiomesSettings.plantDrawOrderSouthInFront;
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
            if (plantDrawOrderShown != RM_BiomesSettings.plantDrawOrderSouthInFront)
            {
                plantDrawOrderShown = RM_BiomesSettings.plantDrawOrderSouthInFront;
                RM_PlantDrawOrder.Reprint();
            }
            if (worldLookShown != RM_BiomesSettings.worldBorderBlend + "/" + RM_BiomesSettings.worldSeaDepth)
            {
                worldLookShown = RM_BiomesSettings.worldBorderBlend + "/" + RM_BiomesSettings.worldSeaDepth;
                if (Current.ProgramState == ProgramState.Playing) Find.World?.renderer?.SetAllLayersDirty();
            }
            if (RM_WorldPaths.applied != RM_BiomesSettings.worldReadablePaths)
            {
                RM_WorldPaths.Apply("settings changed");
                if (Current.ProgramState == ProgramState.Playing) Find.World?.renderer?.SetAllLayersDirty();
            }
        }

        string worldLookShown = "True/True";

        // MOD_OPTIONS_RETROFIT_1: per-entry toggles live in the Scribed RM_BiomesSettings.enabled dictionary (absent key = on).
        // Scope AUDITED against the read site (2026-10-10): RM_BiomesGate.Apply writes BiomeDef.generatesNaturally, which only
        // WorldGenStep_Terrain.BiomeFrom reads -> NewMapsOnly for an entry that ships BiomeDefs. Its other readers are the member mods
        // listed in RM_BiomesSettings.mechanicsGated (live: those mechanics stop on existing maps). An entry with no BiomeDefs and no
        // mechanics reader (every engine/mechanic entry today) gates nothing yet: DEAD.
        private float viewHeight = 1200f;
        private static bool plantDrawOrderShown = true;
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
                list.GapLine();
            }

            if (string.IsNullOrWhiteSpace(searchQuery)
                || RimMandrake.Shared.SettingsKitCore.Matches("plants draw order south front mushrooms overlap", searchQuery))
            {
                list.CheckboxLabeled("Southern plants draw in front [now]", ref RM_BiomesSettings.plantDrawOrderSouthInFront,
                    "On maps in our biomes, where two plants overlap, the one standing further south is drawn in front, "
                    + "whatever their sizes. Without it a giant mushroom on a higher draw layer covers a southern neighbour.\n\n"
                    + "Draw order only. Ground cover stays under every plant; pawns and items stay on top. "
                    + "Other mods' biomes are not touched.\n\nDefault: on. Takes effect at once on running maps.");
                list.GapLine();
            }

            if (string.IsNullOrWhiteSpace(searchQuery)
                || RimMandrake.Shared.SettingsKitCore.Matches("world map planet borders blend sea depth water coast roads rivers highway", searchQuery))
            {
                list.CheckboxLabeled("Planet: soft borders between biomes [now]", ref RM_BiomesSettings.worldBorderBlend,
                    "On the world map, the edge between two land biomes fades over half a tile on each side instead of "
                    + "a hard hex line.\n\nLooks only. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: seas deepen away from the coast [now]", ref RM_BiomesSettings.worldSeaDepth,
                    "On the world map, water is lighter near the shore and darker far from it.\n\nLooks only; tile "
                    + "elevations are not changed. Default: on. Takes effect at once (the planet redraws).");
                list.CheckboxLabeled("Planet: readable roads and rivers [now]", ref RM_BiomesSettings.worldReadablePaths,
                    "On the world map, roads get a dark casing and a colour per kind (umber dirt, slate stone, gold "
                    + "ancient highway) and rivers get a dark bank and a hard edge, a little wider (their colour stays FlowWorks' River Colours where that is on, else bright blue). "
                    + "Off restores the vanilla road and river look.\n\nLooks only; which tiles have roads or rivers is "
                    + "not changed. Default: on. Takes effect at once (the planet redraws).");
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
