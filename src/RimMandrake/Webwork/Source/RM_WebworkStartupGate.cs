using RimWorld;
using Verse;

namespace RimMandrake.Webwork
{
	/// <summary>
	/// WEBWORK_BASE_PORT_BUILD_1. Startup-time application of the Webwork's settings-gated mechanisms.
	/// 1. The thrixweave sole-source strip, moved down from the campaign tier (SHOKKWEAVE_SOLE_SOURCE_1):
	///    tradeability All -> Sellable (TraderCanSell() is false for Sellable, which closes every stock route
	///    in StockGeneratorUtility; the colonist can still sell it), RewardStandardCore removed from the
	///    quest-reward pool, the ExoticMisc trade tag removed as a second lock, stuff commonality 0.1 -> 0.05.
	/// 2. The web harvest (webHarvestEnabled): ApplyWebHarvest (anchor line, sheet web and, since
	/// WEBWORK_TERRAIN_WEATHER_PASS_1, the web cable).
	/// 3. Webfall (webfallEnabled / webfallCommonality): ApplyWebfall, RM_Webwork's weather row.
	/// Runs once after defs load (so a change needs a restart, and the settings say so).
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_WebworkStartupGate
	{
		static RM_WebworkStartupGate()
		{
			if (RM_WebworkSettings.thrixweaveTraderStripEnabled)
			{
				ApplyThrixweaveStrip(DefDatabase<ThingDef>.GetNamedSilentFail("Hyperweave"));
			}
			ApplyWebHarvest();
			ApplyWebfall(DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Webwork"), DefDatabase<WeatherDef>.GetNamedSilentFail(WebfallDefName));
		}

		public const string WebfallDefName = "RM_Webfall";

		/// <summary>WEBWORK_TERRAIN_WEATHER_PASS_1: webfall's row in RM_Webwork's weather table. Off (or a commonality of 0)
		/// removes the row; on sets it to webfallCommonality, adding it if the XML row is missing. Returns the commonality now
		/// in the table (0 when absent).</summary>
		public static float ApplyWebfall(BiomeDef biome, WeatherDef webfall)
		{
			if (biome?.baseWeatherCommonalities == null || webfall == null)
			{
				return 0f;
			}
			biome.baseWeatherCommonalities.RemoveAll(r => r.weather == webfall);
			if (!RM_WebworkSettings.webfallEnabled || RM_WebworkSettings.webfallCommonality <= 0f)
			{
				return 0f;
			}
			biome.baseWeatherCommonalities.Add(new WeatherCommonalityRecord { weather = webfall, commonality = RM_WebworkSettings.webfallCommonality });
			return RM_WebworkSettings.webfallCommonality;
		}

		/// <summary>SHOKKWEAVE_SOLE_SOURCE_1: webHarvestEnabled off withdraws the Deconstruct route from the two silk
		/// nodes (the gutter keeps it: cutting one out is the traction-lance specimen route, not this setting's).</summary>
		public static readonly string[] HarvestNodeDefNames = { "RM_Webwork_Anchor", "RM_Webwork_Web", "RM_Webwork_Cable" };

		public static void ApplyWebHarvest()
		{
			foreach (string n in HarvestNodeDefNames)
			{
				ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(n);
				if (d?.building != null)
				{
					d.building.alwaysDeconstructible = RM_WebworkSettings.webHarvestEnabled;
				}
			}
		}

		public static void ApplyThrixweaveStrip(ThingDef weave)
		{
			if (weave == null)
			{
				return;
			}
			weave.tradeability = Tradeability.Sellable;
			weave.thingSetMakerTags?.RemoveAll(t => t == "RewardStandardCore");
			weave.tradeTags?.RemoveAll(t => t == "ExoticMisc");
			if (weave.stuffProps != null)
			{
				weave.stuffProps.commonality = 0.05f;
			}
		}
	}
}
