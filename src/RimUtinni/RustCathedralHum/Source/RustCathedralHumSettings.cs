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

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref humMechanicEnabled, "humMechanicEnabled", true);
			Scribe_Values.Look(ref commentaryEnabled, "commentaryEnabled", true);
			Scribe_Values.Look(ref goodwillDrainEnabled, "goodwillDrainEnabled", true);
			Scribe_Values.Look(ref irritationDecayRateMultiplier, "irritationDecayRateMultiplier", 1f);
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
