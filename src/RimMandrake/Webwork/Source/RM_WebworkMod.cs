using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Webwork
{
	// ════════════════════════════════════════════════════════════════════
	// MOD_OPTIONS_RETROFIT_1 — Mod Settings for Webwork.
	//
	// Precedent: src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static
	// fields read from everywhere, Scribe_Values in ExposeData, a
	// DoWindowContents helper called from the Mod subclass).
	//
	// Phase A ships one real toggle — whether RM_Webwork's BiomeWorker
	// competes at all during world generation (WORLDGEN-AFFECTING, labeled as
	// such; default ON, matching shipped behavior; off degrades gracefully —
	// the worker just always returns 0, so the biome never wins a tile, no
	// NREs).
	//
	// SHOKK_SKIN_SHRINK_1 (S6 ruling 1) adds the emergent-spawn dial, moved
	// here verbatim from mandrake.rsw.shokk's RSW_ShokkSettings (SHOKK_RSW_MOD_1)
	// along with the comp it gates (RM_CompEmergentSpawnOnDestroy.cs) — the
	// mechanism is mechanism-not-IP and now lives in this free-tier mod.
	// ════════════════════════════════════════════════════════════════════
	public class RM_WebworkSettings : ModSettings
	{
		public static bool generateOnWorldgen = true;
		public static bool emergentSpawnEnabled = true;
		public static float emergentSpawnChanceMultiplier = 1f;

		// WEBWORK_NEST_EGG_ECONOMY_1 (S6 rulings 3/4): the guaranteed nest
		// cluster RM_GenStep_WebworkNest places on every map, and the tuning
		// dial on how fast a living nest re-lays (RM_CompEggClutchRelay).
		public static bool nestEnabled = true;
		public static float eggRelayIntervalMultiplier = 1f;

		// WEBWORK_BASE_PORT_BUILD_1: the creeping front (both apply at startup, so a restart) and the
		// thrixweave sole-source strip (trader stock, quest rewards, trade tag, stuff commonality).
		// The rename of Hyperweave to thrixweave always applies.
		public static bool frontCreepEnabled = true;
		public static float frontCreepIntervalMultiplier = 1f;
		public static bool thrixweaveTraderStripEnabled = true;

		// SHOKKWEAVE_SOLE_SOURCE_1: colonists may cut creep-web nodes (vanilla Deconstruct) for thrixweave.
		public static bool webHarvestEnabled = true;

		// WEBWORK_DEAD_GIANT_BUILD_1: the urraveth remains (RM_UrravethRemains.cs). Numbers PROVISIONAL.
		public static bool urravethEnabled = true;
		public static float urravethSiteChance = 0.25f;
		public static int urravethThrixweavePerPiece = 8;
		public static float urravethWarningHours = 6f;
		public static float urravethCollapseDamageMultiplier = 1f;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref generateOnWorldgen, "generateOnWorldgen", true);
			Scribe_Values.Look(ref emergentSpawnEnabled, "emergentSpawnEnabled", true);
			Scribe_Values.Look(ref emergentSpawnChanceMultiplier, "emergentSpawnChanceMultiplier", 1f);
			Scribe_Values.Look(ref nestEnabled, "nestEnabled", true);
			Scribe_Values.Look(ref eggRelayIntervalMultiplier, "eggRelayIntervalMultiplier", 1f);
			Scribe_Values.Look(ref frontCreepEnabled, "frontCreepEnabled", true);
			Scribe_Values.Look(ref frontCreepIntervalMultiplier, "frontCreepIntervalMultiplier", 1f);
			Scribe_Values.Look(ref thrixweaveTraderStripEnabled, "thrixweaveTraderStripEnabled", true);
			Scribe_Values.Look(ref webHarvestEnabled, "webHarvestEnabled", true);
			Scribe_Values.Look(ref urravethEnabled, "urravethEnabled", true);
			Scribe_Values.Look(ref urravethSiteChance, "urravethSiteChance", 0.25f);
			Scribe_Values.Look(ref urravethThrixweavePerPiece, "urravethThrixweavePerPiece", 8);
			Scribe_Values.Look(ref urravethWarningHours, "urravethWarningHours", 6f);
			Scribe_Values.Look(ref urravethCollapseDamageMultiplier, "urravethCollapseDamageMultiplier", 1f);
		}

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_WebworkSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_WebworkSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): biome score = worldgen; nest GenStep and urraveth
        /// site roll = map generation; startup gate (static constructor) = next game start; comps, jobs and collapse = now.</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
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
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "World generation (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "generateOnWorldgen" }))
            {
                list.CheckboxLabeled("Let the Webwork generate on new worlds", ref generateOnWorldgen,
                    "WORLDGEN-AFFECTING. On: RM_Webwork competes for tiles like any other biome when "
                  + "a new planet is generated. Off: RM_Webwork never wins a tile — a currently "
                  + "generated world is never retroactively changed either way.");
                list.GapLine();
            }

            if (Group(list, "Emergent spawn", RimMandrake.Shared.SettingScope.Now, new[] { "emergentSpawnEnabled", "emergentSpawnChanceMultiplier" }))
            {
                list.CheckboxLabeled("Emergent ollathrix spawn enabled", ref emergentSpawnEnabled,
                    "Destroying a harvest-type Thing this is attached to (a creep-web node, a "
                  + "gutter, …) has a chance to spawn a hostile, manhunter-forced ollathrix on the "
                  + "spot. Off: destroying those things never spawns anything.");
                list.Label("Spawn chance: " + emergentSpawnChanceMultiplier.ToString("0.00")
                    + "x (each def's own base chance, e.g. the shipped default of 3%)");
                emergentSpawnChanceMultiplier = list.Slider(emergentSpawnChanceMultiplier, 0f, 3f);
                list.GapLine();
            }

            if (Group(list, "Guaranteed nest (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "nestEnabled" }))
            {
                list.CheckboxLabeled("Guaranteed nest on new maps", ref nestEnabled,
                    "MAP-GENERATION-AFFECTING. On: every new RM_Webwork map gets one nest cluster "
                  + "(a guardian ollathrix and a harvestable egg clutch), per S6 ruling 3. Off: no "
                  + "nest ever generates; a currently generated map is never retroactively changed "
                  + "either way.");
                list.GapLine();
            }

            if (Group(list, "Egg economy", RimMandrake.Shared.SettingScope.Now, new[] { "eggRelayIntervalMultiplier" }))
            {
                list.Label("Egg re-lay speed: " + eggRelayIntervalMultiplier.ToString("0.00")
                    + "x (lower = faster; shipped default re-lays every 20-30 days)");
                eggRelayIntervalMultiplier = list.Slider(eggRelayIntervalMultiplier, 0.1f, 3f);
                list.GapLine();
            }

            if (Group(list, "Creeping front and thrixweave (restart)", RimMandrake.Shared.SettingScope.Now, new[] { "frontCreepEnabled", "frontCreepIntervalMultiplier", "thrixweaveTraderStripEnabled", "webHarvestEnabled" }, "[next game start]"))
            {
                list.CheckboxLabeled("The web creeps out over the border", ref frontCreepEnabled,
                    "On: a map bordering a Webwork slowly grows anchor lines, sheet webs and gutters inward from "
                  + "that edge. Off: the Webwork stays in its own tiles. Applies at startup.");
                list.Label("Creep advance interval: " + frontCreepIntervalMultiplier.ToString("0.00")
                    + "x (higher = slower; shipped default one band step per day)");
                frontCreepIntervalMultiplier = list.Slider(frontCreepIntervalMultiplier, 0.25f, 4f);
                list.CheckboxLabeled("Thrixweave is sold by no trader", ref thrixweaveTraderStripEnabled,
                    "On: no trader stocks thrixweave (Hyperweave, renamed), it leaves the standard quest-reward "
                  + "pool, and tailored gear is half as likely to be made of it - the Webwork is its only source. "
                  + "Off: it trades like vanilla Hyperweave. The rename always applies. Applies at startup.");
                list.CheckboxLabeled("Colonists can cut web for thrixweave", ref webHarvestEnabled,
                    "On: anchor lines and sheet webs (in the Webwork and on maps its front creeps onto) can be marked with "
                  + "the Deconstruct tool; a colonist cuts them for thrixweave (3 per anchor line, 2 per sheet web), and "
                  + "any cut can wake the emergent ollathrix spawn above. Off: those two can only be broken by force (which "
                  + "still drops their silk). Gutters stay cuttable either way. Applies at startup.");
                list.GapLine();
            }

            if (Group(list, "Urraveth remains: new maps (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "urravethSiteChance" }))
            {
                list.Label("Site chance per new Webwork map: " + urravethSiteChance.ToStringPercent()
                    + " (also needs the toggle below on)");
                urravethSiteChance = list.Slider(urravethSiteChance, 0f, 1f);
                list.GapLine();
            }

            if (Group(list, "The dead giant (urraveth remains)", RimMandrake.Shared.SettingScope.Now, new[] { "urravethEnabled", "urravethThrixweavePerPiece", "urravethWarningHours", "urravethCollapseDamageMultiplier" }))
            {
                list.CheckboxLabeled("Urraveth remains enabled", ref urravethEnabled,
                    "On: a new RM_Webwork map may hold the wrapped skeleton of an urraveth, read "
                  + "bone by bone; loaded bones creak and can collapse. Off: no new site generates, and existing remains "
                  + "cannot be examined and never creak (that part applies at once). The planet is never changed either way.");
                list.Label("Thrixweave per piece read: " + urravethThrixweavePerPiece);
                urravethThrixweavePerPiece = Mathf.RoundToInt(list.Slider(urravethThrixweavePerPiece, 0f, 40f));
                list.Label("Creak warning before a collapse: " + urravethWarningHours.ToString("0.#") + " in-game hours");
                urravethWarningHours = list.Slider(urravethWarningHours, 1f, 24f);
                list.Label("Collapse damage: " + urravethCollapseDamageMultiplier.ToString("0.00") + "x (vanilla thin-roof collapse)");
                urravethCollapseDamageMultiplier = list.Slider(urravethCollapseDamageMultiplier, 0f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

	public class RM_WebworkMod : Mod
	{
		public static RM_WebworkSettings settings;

		public RM_WebworkMod(ModContentPack content) : base(content)
		{
			settings = GetSettings<RM_WebworkSettings>();
		}

		public override string SettingsCategory()
		{
			return "Webwork";
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			settings.DoWindowContents(inRect);
		}
	}
}
