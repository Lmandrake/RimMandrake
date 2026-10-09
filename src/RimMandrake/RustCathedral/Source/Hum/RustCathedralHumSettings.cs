using UnityEngine;
using Verse;

namespace RimMandrake.RustCathedral.Hum
{
	// MOD_OPTIONS_RETROFIT_1 -- Mod Settings for RustCathedralHum.
	//
	// Every mechanic this mod runs is gated here, all-off degrades gracefully:
	// with humMechanicEnabled off, the map component still exists (auto-added
	// to every map, harmless) but skips its check entirely -- no sound, no
	// irritation, no goodwill drain, no commentary. Live-play tuning only
	// (nothing here is worldgen-affecting -- this mechanic never touches map
	// generation).
	public class RustCathedralHumSettings : ModSettings
	{
		public static bool humMechanicEnabled = true;
		public static bool commentaryEnabled = true;
		public static bool goodwillDrainEnabled = true;
		public static float irritationDecayRateMultiplier = 1f;

		// RUST_CATHEDRAL_MECHANICS_1 §3 (the living bolts). Three separable
		// mechanics, same pattern as the three above: default = shipped
		// behavior, each off degrades gracefully rather than erroring, and
		// none of them is worldgen-affecting (the bolts' presence on a map is
		// roster/spawn wiring, which this mod does not own -- turning these
		// off changes what a bolt DOES, never whether one exists).
		public static bool boltDanceEnabled = true;
		public static bool boltShedEnabled = true;
		public static bool boltWatchedPricingEnabled = true;

		// The bolts are the hum's display organ, so every bolt mechanic also
		// rides the master hum toggle: with the hum off there is no band to
		// display and nothing to irritate. These three properties are the
		// only thing the §3 code reads, so that coupling lives in one place.
		public static bool BoltDisplayActive => humMechanicEnabled && boltDanceEnabled;

		public static bool BoltShedActive => humMechanicEnabled && boltShedEnabled;

		public static bool BoltWatchedPricingActive => humMechanicEnabled && boltWatchedPricingEnabled;

		// RUST_CATHEDRAL_MECHANICS_1 §4 (eel-fishing consequences) and §5 (the
		// deep-drill response event). Same discipline as everything above:
		// default = shipped behavior, off degrades rather than errors.
		//
		// ⚠️ NEITHER toggle removes CONTENT. The coolant eel def, the negative
		// fishing outcome, and the biome's own fishTypes/maxFishPopulation are
		// XML that Mod Settings cannot reach -- the canals stay fishable and
		// the eel stays catchable and salable with fishing pricing off. What
		// the toggle owns is whether the Cathedral MINDS, which is the
		// mechanic. (maxFishPopulation is the one worldgen-adjacent field here:
		// it is read when a map's water bodies are built, so changing it
		// affects maps generated afterwards, not maps already made. That is why
		// it is not a setting.)
		public static bool fishingPricingEnabled = true;
		public static bool drillResponseEnabled = true;

		// §4's line-in tell and per-catch price are the hum reacting, so they
		// ride the master hum toggle for the same reason the bolts do.
		public static bool FishingPricingActive => humMechanicEnabled && fishingPricingEnabled;

		// §5 does NOT ride the master toggle. The response is a storyteller
		// incident and a mechanoid force, not a display of the attitude value:
		// with the hum switched off it still makes sense for drilling the deep
		// metal to be answered, and the escalation coupling into §1 simply
		// lands on a component that is asleep. Turning THIS off also releases
		// vanilla's own deep-drill infestation on Cathedral maps, so all-off is
		// plain vanilla behavior rather than a map where nothing can happen.
		public static bool DrillResponseActive => drillResponseEnabled;

		// RUSTCATHEDRAL_BASE_FINISH_BUILD_1 part 1 (the line-cycle) and part 2 (hum reading). Live play only.
		// lineCycleMtbDays 8 is the item's "about once per 8 days"; 60..120 s is its own duration range.
		// humReaderThresholdDays 5 is the item's default; all PROVISIONAL until a live sitting tunes them.
		public static bool lineCycleEnabled = true;
		public static float lineCycleMtbDays = 8f;
		public static float lineCycleMinSeconds = 60f;
		public static float lineCycleMaxSeconds = 120f;
		public static bool humReadingEnabled = true;
		public static float humReaderThresholdDays = 5f;

		// RUSTCATHEDRAL_HULL_BOLTS_BUILD_1: hull bolts. All numbers PROVISIONAL.
		public static bool hullBoltsEnabled = true;
		public static int hullBoltBoardMin = 1;
		public static int hullBoltBoardMax = 3;
		public static float hullBoltNoneChance = 0.15f;
		public static float hullBoltEdgePull = 0.35f;
		public static bool hullBoltWitnessEnabled = true;
		public static float hullBoltWeightScale = 1f;
		public static float hullBoltIrritationCap = 60f;
		public static float hullBoltRealiseDays = 10f;
		public static float hullBoltRevealDays = 5f;
		public static bool hullBoltPetMemoryEnabled = true;

		public static bool HullBoltsActive => hullBoltsEnabled;

		public override void ExposeData()
		{
			RimMandrake.Shared.PatchApplier.BeforeExpose();
			base.ExposeData();
			Scribe_Values.Look(ref humMechanicEnabled, "humMechanicEnabled", true);
			Scribe_Values.Look(ref commentaryEnabled, "commentaryEnabled", true);
			Scribe_Values.Look(ref goodwillDrainEnabled, "goodwillDrainEnabled", true);
			Scribe_Values.Look(ref irritationDecayRateMultiplier, "irritationDecayRateMultiplier", 1f);
			Scribe_Values.Look(ref boltDanceEnabled, "boltDanceEnabled", true);
			Scribe_Values.Look(ref boltShedEnabled, "boltShedEnabled", true);
			Scribe_Values.Look(ref boltWatchedPricingEnabled, "boltWatchedPricingEnabled", true);
			Scribe_Values.Look(ref fishingPricingEnabled, "fishingPricingEnabled", true);
			Scribe_Values.Look(ref drillResponseEnabled, "drillResponseEnabled", true);
			Scribe_Values.Look(ref lineCycleEnabled, "lineCycleEnabled", true);
			Scribe_Values.Look(ref lineCycleMtbDays, "lineCycleMtbDays", 8f);
			Scribe_Values.Look(ref lineCycleMinSeconds, "lineCycleMinSeconds", 60f);
			Scribe_Values.Look(ref lineCycleMaxSeconds, "lineCycleMaxSeconds", 120f);
			Scribe_Values.Look(ref humReadingEnabled, "humReadingEnabled", true);
			Scribe_Values.Look(ref humReaderThresholdDays, "humReaderThresholdDays", 5f);
			Scribe_Values.Look(ref hullBoltsEnabled, "hullBoltsEnabled", true);
			Scribe_Values.Look(ref hullBoltBoardMin, "hullBoltBoardMin", 1);
			Scribe_Values.Look(ref hullBoltBoardMax, "hullBoltBoardMax", 3);
			Scribe_Values.Look(ref hullBoltNoneChance, "hullBoltNoneChance", 0.15f);
			Scribe_Values.Look(ref hullBoltEdgePull, "hullBoltEdgePull", 0.35f);
			Scribe_Values.Look(ref hullBoltWitnessEnabled, "hullBoltWitnessEnabled", true);
			Scribe_Values.Look(ref hullBoltWeightScale, "hullBoltWeightScale", 1f);
			Scribe_Values.Look(ref hullBoltIrritationCap, "hullBoltIrritationCap", 60f);
			Scribe_Values.Look(ref hullBoltRealiseDays, "hullBoltRealiseDays", 10f);
			Scribe_Values.Look(ref hullBoltRevealDays, "hullBoltRevealDays", 5f);
			Scribe_Values.Look(ref hullBoltPetMemoryEnabled, "hullBoltPetMemoryEnabled", true);
			RimMandrake.Shared.PatchApplier.AfterExpose();
		}

		public void DoWindowContents(Rect inRect)
		{
			Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
			list.Begin(inRect);
			RimMandrake.Shared.PatchApplier.DrawNotice(list);

			list.Label("Live play -- applies to every map immediately, nothing here affects worldgen.");
			list.CheckboxLabeled("Hum-mood system", ref humMechanicEnabled,
				"Off: the Rust Cathedral's attitude tracking, layered hum, and goodwill coupling all stop. Nothing plays, nothing drains.");
			list.CheckboxLabeled("Droid commentary", ref commentaryEnabled,
				"Off: no messages fire on band changes, even with a droid on the map. The hum and goodwill coupling still run.");
			list.CheckboxLabeled("Sustained sacrilege lowers the Cathedral's standing", ref goodwillDrainEnabled,
				"Off: the worst band still sounds and displays, but never lowers the Cathedral's standing on its own. Catches and drilling still cost standing.");
			list.Label("Irritation decay speed: " + irritationDecayRateMultiplier.ToString("0.00") + "x (higher = forgets faster)");
			irritationDecayRateMultiplier = list.Slider(irritationDecayRateMultiplier, 0.25f, 4f);

			list.GapLine();
			list.Label("Living bolts");
			list.CheckboxLabeled("Bolts dance and freeze", ref boltDanceEnabled,
				"Off: living bolts wander like ordinary small mechanoids and never form figures or stop dead. Nothing else about them changes.");
			list.CheckboxLabeled("Bolts shed curiosities", ref boltShedEnabled,
				"Off: living bolts stop leaving shed curiosities on the ground. Curiosities already dropped are unaffected.");
			list.CheckboxLabeled("The Cathedral minds what you do to its bolts", ref boltWatchedPricingEnabled,
				"Off: taking a shed curiosity or killing a living bolt stops feeding the Cathedral's mood. The hum still runs on everything else.");

			list.GapLine();
			list.Label("The canals and the deep");
			list.CheckboxLabeled("The Cathedral minds what you take from its canals", ref fishingPricingEnabled,
				"Off: fishing the coolant canals stops feeding the Cathedral's mood. The eels are still there, still catchable and still worth selling, and the occasional nasty catch still happens -- nothing about the water itself changes.");
			list.CheckboxLabeled("Drilling the deep metal is answered", ref drillResponseEnabled,
				"Off: a deep drill on the Rust Cathedral is treated like a deep drill anywhere else, and ordinary deep-drill infestations can occur there again instead.");

			list.GapLine();
			list.Label("Under the plate");
			list.CheckboxLabeled("Something turns over under the plate", ref lineCycleEnabled,
				"Off: the slow roll under the deck plate never comes, and nothing on the plateau stops for it.");
			list.Label("It comes roughly every " + lineCycleMtbDays.ToString("0.0") + " days");
			lineCycleMtbDays = list.Slider(lineCycleMtbDays, 1f, 30f);
			list.Label("It takes " + lineCycleMinSeconds.ToString("0") + " to " + lineCycleMaxSeconds.ToString("0") + " seconds to pass");
			lineCycleMinSeconds = list.Slider(lineCycleMinSeconds, 20f, 300f);
			lineCycleMaxSeconds = Mathf.Max(lineCycleMinSeconds, list.Slider(lineCycleMaxSeconds, 20f, 300f));
			list.CheckboxLabeled("Colonists learn to read the hum", ref humReadingEnabled,
				"Off: nobody learns to read the hum by listening and nothing new is shown. Primers already written still teach.");
			list.Label("Days of listening on calm ground before it comes: " + humReaderThresholdDays.ToString("0.0"));
			humReaderThresholdDays = list.Slider(humReaderThresholdDays, 0.5f, 30f);

			list.GapLine();
			list.Label("Bolts on the hull");
			list.CheckboxLabeled("Some bolts ride the ship away", ref hullBoltsEnabled,
				"Off: no bolt ever clings to a ship leaving the plateau, and bolts already aboard stop drifting to the edge and stop reacting. Nothing else changes.");
			list.Label("Bolts that cling at liftoff: " + hullBoltBoardMin + " to " + hullBoltBoardMax + " (" + (hullBoltNoneChance * 100f).ToString("0") + "% chance of none)");
			hullBoltBoardMin = Mathf.RoundToInt(list.Slider(hullBoltBoardMin, 0f, 5f));
			hullBoltBoardMax = Mathf.Max(hullBoltBoardMin, Mathf.RoundToInt(list.Slider(hullBoltBoardMax, 0f, 5f)));
			hullBoltNoneChance = list.Slider(hullBoltNoneChance, 0f, 1f);
			list.Label("How often a dancing bolt drifts to a landed ship's edge: " + (hullBoltEdgePull * 100f).ToString("0") + "% of figures");
			hullBoltEdgePull = list.Slider(hullBoltEdgePull, 0f, 1f);
			list.CheckboxLabeled("They stop and turn when the plateau's things change hands", ref hullBoltWitnessEnabled,
				"Off: the bolts aboard never react, and nothing waits for you at the next landing on the plateau.");
			list.Label("How much it is minded: " + hullBoltWeightScale.ToString("0.00") + "x, at most " + hullBoltIrritationCap.ToString("0") + " on landing");
			hullBoltWeightScale = list.Slider(hullBoltWeightScale, 0f, 3f);
			hullBoltIrritationCap = list.Slider(hullBoltIrritationCap, 0f, 100f);
			list.Label("Days aboard before the hull goes cold under them: " + hullBoltRealiseDays.ToString("0.0") + "; days more before it is noticed: " + hullBoltRevealDays.ToString("0.0"));
			hullBoltRealiseDays = list.Slider(hullBoltRealiseDays, 0f, 60f);
			hullBoltRevealDays = list.Slider(hullBoltRevealDays, 0f, 60f);
			list.CheckboxLabeled("Colonists like seeing them", ref hullBoltPetMemoryEnabled,
				"Off: no small good memory from watching the bolts on the hull.");

			list.End();
		}
	}

	// RUSTCATHEDRAL_RM_MOD_BUILD_1: the standalone RustCathedralHumSettingsMod
	// wrapper (one Mod-derived class per satellite kit) is RETIRED now that
	// Hum/Walls/Roaches/the biome all ship in one mod, mandrake.rm.rustcathedral.
	// This settings DATA class is unchanged and still read from everywhere it
	// always was; it is now surfaced through the single
	// RimMandrake.RustCathedral.RM_RustCathedralMod settings screen instead of
	// its own category, so GetSettings<RustCathedralHumSettings>() is called
	// from that Mod's constructor.
}
