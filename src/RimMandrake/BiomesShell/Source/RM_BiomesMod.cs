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
    // DEFERRED (spec §5 arm 2): each biome's MapComponents/comps early-outing
    //   on RM_BiomesSettings.Enabled(key). That needs a one-line check inside
    //   each biome's own assembly and is wired biome by biome, not here.
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

        public static RM_BiomesSettings Instance;

        public static bool Enabled(string key)
        {
            if (Instance == null || key == null) return true;
            return !Instance.enabled.TryGetValue(key, out bool on) || on;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref enabled, "enabled", LookMode.Value, LookMode.Value);
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
        }

        // MOD_OPTIONS_RETROFIT_1: per-entry toggles live in the Scribed RM_BiomesSettings.enabled dictionary (absent key = on).
        // Scope AUDITED against the read site (2026-10-10): RM_BiomesGate.Apply writes BiomeDef.generatesNaturally, which only
        // WorldGenStep_Terrain.BiomeFrom reads -> NewMapsOnly for an entry that ships BiomeDefs. RM_BiomesSettings.Enabled(key) has
        // NO other reader in the repo, so an entry with no BiomeDefs (every engine/mechanic entry today) gates nothing yet: DEAD.
        private float viewHeight = 1200f;
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

            foreach (var g in new[] { "biome", "engine", "kit" })
            {
                var members = roster.Where(e => e.group == g).ToList();
                if (members.Count == 0) continue;
                string title = g == "biome" ? "Biomes (WORLDGEN-AFFECTING)" : g == "engine" ? "Engines" : "Mechanics";
                string tag = RimMandrake.Shared.SettingsKitCore.ScopeTag(RimMandrake.Shared.SettingScope.NewMapsOnly);
                string note = members.Any(e => e.biomeDefs.Count > 0)
                    ? tag + " changes only affect worlds generated afterwards"
                    : "[no effect yet] these toggles are recorded but nothing reads them; each is wired per mod later";
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
                              + "Biome defs: " + string.Join(", ", e.biomeDefs)
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
}
