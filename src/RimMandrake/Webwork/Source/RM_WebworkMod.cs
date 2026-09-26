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

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref generateOnWorldgen, "generateOnWorldgen", true);
			Scribe_Values.Look(ref emergentSpawnEnabled, "emergentSpawnEnabled", true);
			Scribe_Values.Look(ref emergentSpawnChanceMultiplier, "emergentSpawnChanceMultiplier", 1f);
		}

		public void DoWindowContents(Rect inRect)
		{
			Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
			list.Begin(inRect);

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

			list.End();
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
