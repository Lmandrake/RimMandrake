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
	// NREs). There is no other mechanic in this mod yet to gate: the
	// front-creep margin extension is deferred to WEBWORK_WEB_STRUCTURES_1,
	// which will add its own dial here rather than opening a new settings
	// class.
	// ════════════════════════════════════════════════════════════════════
	public class RM_WebworkSettings : ModSettings
	{
		public static bool generateOnWorldgen = true;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref generateOnWorldgen, "generateOnWorldgen", true);
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
