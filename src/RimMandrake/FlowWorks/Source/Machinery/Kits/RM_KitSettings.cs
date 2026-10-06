using Verse;

namespace RimMandrake.FlowWorks.Machinery.Kits
{
	/// <summary>
	/// Settings for the liquid-side kit mechanisms biome kits consume (flowworks_remaining row 18, 2026-10-05):
	/// liquid bath recipes (GELATINOUSSLIME_PIT_SOLVENT_1), two-liquid reactions (SUMP_GASLIGHT_1), hot releases
	/// (FORGE_CYCLE_MECHANICS_1's boiling-rain flood) and drained-liquid residue (SUMP_TAR_NASTINESS_1).
	/// Own class and file, called from RimMandrakeFlowWorksSettings like the machinery section.
	/// Defaults = shipped behaviour. Every number is PROVISIONAL (owner ruling 2026-10-03: ship first guesses).
	/// </summary>
	public static class RM_KitSettings
	{
		/// <summary>Bills carrying RM_RecipeLiquidExtension need their liquid (a tank on the bench's net, or the
		/// liquid's own ground beside the bench). Off: those bills run without it and draw nothing.</summary>
		public static bool liquidBathRecipesEnabled = true;

		/// <summary>Reaction vats run their two-liquid reactions.</summary>
		public static bool liquidReactionsEnabled = true;

		/// <summary>Scales every reaction vat's batches per day.</summary>
		public static float reactionRateMultiplier = 1f;

		/// <summary>A hot release (boiling water flood) scalds pawns standing in it until it cools.</summary>
		public static bool hotLiquidEnabled = true;

		/// <summary>Scales the scald damage of a hot release.</summary>
		public static float hotLiquidBurnMultiplier = 1f;

		/// <summary>A drained flood of a residue-leaving liquid (tar) leaves its filth on the ground.</summary>
		public static bool fluidResidueEnabled = true;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref liquidBathRecipesEnabled, "liquidBathRecipesEnabled", true);
			Scribe_Values.Look(ref liquidReactionsEnabled, "liquidReactionsEnabled", true);
			Scribe_Values.Look(ref reactionRateMultiplier, "reactionRateMultiplier", 1f);
			Scribe_Values.Look(ref hotLiquidEnabled, "hotLiquidEnabled", true);
			Scribe_Values.Look(ref hotLiquidBurnMultiplier, "hotLiquidBurnMultiplier", 1f);
			Scribe_Values.Look(ref fluidResidueEnabled, "fluidResidueEnabled", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Liquid kits (what biome kits borrow: baths, reactions, hot floods, residue)");
			list.CheckboxLabeled("Liquid bath bills need their liquid", ref liquidBathRecipesEnabled,
				"On: a bill such as the slime pit's solvent rendering only runs with its liquid to hand — a tank of it on the bench's hose net, or a cell of it beside the bench — and draws its units from the tank. Off: such bills run dry and take nothing.");
			list.CheckboxLabeled("Reaction vats run (two liquids in, product or gas out)", ref liquidReactionsEnabled,
				"Tar and acid water react in a vat: the gas comes off as a product where a kit names one (the Sump's tar gas), else it vents as a toxic cloud.");
			list.Label("Reaction pace: " + reactionRateMultiplier.ToString("0.00") + "x  (first-guess number)");
			reactionRateMultiplier = list.Slider(reactionRateMultiplier, 0.1f, 5f);
			list.CheckboxLabeled("Hot releases scald (boiling floods)", ref hotLiquidEnabled,
				"On: a flood released hot — the Forge's boiling rain — burns pawns standing in it and steams until it cools over a few hours. Off: the same flood is plain water.");
			list.Label("Scald strength: " + hotLiquidBurnMultiplier.ToString("0.00") + "x  (first-guess number)");
			hotLiquidBurnMultiplier = list.Slider(hotLiquidBurnMultiplier, 0f, 3f);
			list.CheckboxLabeled("Drained floods leave residue (tar stains the ground)", ref fluidResidueEnabled,
				"On: when a tar flood drains, part of the ground it covered keeps a tar stain until cleaned. Off: it drains clean.");
		}
	}
}
