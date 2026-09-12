using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.RustCathedralHum
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

		public override void ExposeData()
		{
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
		}

		public void DoWindowContents(Rect inRect)
		{
			Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
			list.Begin(inRect);

			list.Label("Live play -- applies to every map immediately, nothing here affects worldgen.");
			list.CheckboxLabeled("Hum-mood system", ref humMechanicEnabled,
				"Off: the Rust Cathedral's attitude tracking, layered hum, and goodwill coupling all stop. Nothing plays, nothing drains.");
			list.CheckboxLabeled("Droid commentary", ref commentaryEnabled,
				"Off: no messages fire on band changes, even with a droid on the map. The hum and goodwill coupling still run.");
			list.CheckboxLabeled("Sustained sacrilege drains faction goodwill", ref goodwillDrainEnabled,
				"Off: the worst band still sounds and displays, but never ticks faction-13 goodwill on its own -- only direct sacrilege (destroying/claiming a sacred wall) still costs goodwill.");
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

			list.End();
		}
	}

	public class RustCathedralHumSettingsMod : Mod
	{
		public static RustCathedralHumSettings settings;

		public RustCathedralHumSettingsMod(ModContentPack content) : base(content)
		{
			settings = GetSettings<RustCathedralHumSettings>();
		}

		public override string SettingsCategory()
		{
			return "Rust Cathedral Hum";
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			settings.DoWindowContents(inRect);
		}
	}
}
