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
			Scribe_Values.Look(ref urravethEnabled, "urravethEnabled", true);
			Scribe_Values.Look(ref urravethSiteChance, "urravethSiteChance", 0.25f);
			Scribe_Values.Look(ref urravethThrixweavePerPiece, "urravethThrixweavePerPiece", 8);
			Scribe_Values.Look(ref urravethWarningHours, "urravethWarningHours", 6f);
			Scribe_Values.Look(ref urravethCollapseDamageMultiplier, "urravethCollapseDamageMultiplier", 1f);
		}

		public void DoWindowContents(Rect inRect)
		{
			// Scrolls: ~25 rows against a ~570px settings window clipped the lower
			// sections. View height = last measured content height.
			Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(lastContentHeight, inRect.height));
			Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);
			Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
			list.Begin(viewRect);

			list.Label("World generation");
			list.CheckboxLabeled("Let the Webwork generate on new worlds", ref generateOnWorldgen,
				"WORLDGEN-AFFECTING. On: RM_Webwork competes for tiles like any other biome when "
			  + "a new planet is generated. Off: RM_Webwork never wins a tile — a currently "
			  + "generated world is never retroactively changed either way.");

			list.Gap();
			list.Label("Emergent spawn");
			list.CheckboxLabeled("Emergent ollathrix spawn enabled", ref emergentSpawnEnabled,
				"Destroying a harvest-type Thing this is attached to (a creep-web node, a "
			  + "gutter, …) has a chance to spawn a hostile, manhunter-forced ollathrix on the "
			  + "spot. Off: destroying those things never spawns anything.");
			if (emergentSpawnEnabled)
			{
				list.Label("  Spawn chance: " + emergentSpawnChanceMultiplier.ToString("0.00")
					+ "x (each def's own base chance, e.g. the shipped default of 3%)");
				emergentSpawnChanceMultiplier = list.Slider(emergentSpawnChanceMultiplier, 0f, 3f);
			}

			list.Gap();
			list.Label("Nest + egg economy");
			list.CheckboxLabeled("Guaranteed nest on new maps", ref nestEnabled,
				"MAP-GENERATION-AFFECTING. On: every new RM_Webwork map gets one nest cluster "
			  + "(a guardian ollathrix and a harvestable egg clutch), per S6 ruling 3. Off: no "
			  + "nest ever generates; a currently generated map is never retroactively changed "
			  + "either way.");
			if (nestEnabled)
			{
				list.Label("  Egg re-lay speed: " + eggRelayIntervalMultiplier.ToString("0.00")
					+ "x (lower = faster; shipped default re-lays every 20-30 days)");
				eggRelayIntervalMultiplier = list.Slider(eggRelayIntervalMultiplier, 0.1f, 3f);
			}

			list.Gap();
			list.Label("Creeping front and thrixweave (restart to apply)");
			list.CheckboxLabeled("The web creeps out over the border", ref frontCreepEnabled,
				"On: a map bordering a Webwork slowly grows anchor lines, sheet webs and gutters inward from "
			  + "that edge. Off: the Webwork stays in its own tiles. Applies at startup.");
			if (frontCreepEnabled)
			{
				list.Label("  Creep advance interval: " + frontCreepIntervalMultiplier.ToString("0.00")
					+ "x (higher = slower; shipped default one band step per day)");
				frontCreepIntervalMultiplier = list.Slider(frontCreepIntervalMultiplier, 0.25f, 4f);
			}
			list.CheckboxLabeled("Thrixweave is sold by no trader", ref thrixweaveTraderStripEnabled,
				"On: no trader stocks thrixweave (Hyperweave, renamed), it leaves the standard quest-reward "
			  + "pool, and tailored gear is half as likely to be made of it - the Webwork is its only source. "
			  + "Off: it trades like vanilla Hyperweave. The rename always applies. Applies at startup.");

			list.Gap();
			list.Label("The dead giant (urraveth remains)");
			list.CheckboxLabeled("Urraveth remains enabled", ref urravethEnabled,
				"MAP-GENERATION-AFFECTING. On: a new RM_Webwork map may hold the wrapped skeleton of an urraveth, read "
			  + "bone by bone; loaded bones creak and can collapse. Off: no new site generates, and existing remains "
			  + "cannot be examined and never creak. The planet is never changed either way.");
			if (urravethEnabled)
			{
				list.Label("  Site chance per new Webwork map: " + urravethSiteChance.ToStringPercent());
				urravethSiteChance = list.Slider(urravethSiteChance, 0f, 1f);
				list.Label("  Thrixweave per piece read: " + urravethThrixweavePerPiece);
				urravethThrixweavePerPiece = Mathf.RoundToInt(list.Slider(urravethThrixweavePerPiece, 0f, 40f));
				list.Label("  Creak warning before a collapse: " + urravethWarningHours.ToString("0.#") + " in-game hours");
				urravethWarningHours = list.Slider(urravethWarningHours, 1f, 24f);
				list.Label("  Collapse damage: " + urravethCollapseDamageMultiplier.ToString("0.00") + "x (vanilla thin-roof collapse)");
				urravethCollapseDamageMultiplier = list.Slider(urravethCollapseDamageMultiplier, 0f, 3f);
			}

			lastContentHeight = list.CurHeight + 12f;
			list.End();
			Widgets.EndScrollView();
		}

		private Vector2 scrollPosition;
		private float lastContentHeight;
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
