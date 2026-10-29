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
	/// 4. The soundscape rows (hushEnabled / webThrumEnabled): ApplySoundscape.
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
			ApplyResalePrice(DefDatabase<TraderKindDef>.GetNamedSilentFail(ResaleTraderDefName));
			ApplyWebHarvest();
			ApplyWebfall(DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Webwork"), DefDatabase<WeatherDef>.GetNamedSilentFail(WebfallDefName));
			ApplySoundscape(DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Webwork"), DefDatabase<SoundDef>.GetNamedSilentFail(HushDefName),
				DefDatabase<SoundDef>.GetNamedSilentFail(ThrumDefName));
		}

		public const string HushDefName = "RM_Webwork_Hush";
		public const string ThrumDefName = "RM_Webwork_Thrum";

		/// <summary>WEBWORK_TERRAIN_WEATHER_PASS_1, soundscape rows. hushEnabled off removes the hush from RM_Webwork's
		/// soundsAmbient (AmbientSoundManager reads that list when a map is shown; weather beds are untouched). webThrumEnabled
		/// off empties the thrum's subSounds: RM_MapComponent_SenseWeb (CreatureBehaviors, a separate assembly that cannot
		/// read these settings) still looks it up by name and plays it, and PlayOneShot only loops subSounds, so an empty
		/// list is silence with no error. Returns "hush=&lt;in table&gt; thrum=&lt;audible&gt;" for a proof read.</summary>
		public static string ApplySoundscape(BiomeDef biome, SoundDef hush, SoundDef thrum)
		{
			bool hushIn = false;
			if (biome != null && hush != null)
			{
				if (biome.soundsAmbient == null) biome.soundsAmbient = new System.Collections.Generic.List<SoundDef>();
				if (!RM_WebworkSettings.hushEnabled) biome.soundsAmbient.RemoveAll(s => s == hush);
				else if (!biome.soundsAmbient.Contains(hush)) biome.soundsAmbient.Add(hush);
				hushIn = biome.soundsAmbient.Contains(hush);
			}
			if (thrum?.subSounds != null && !RM_WebworkSettings.webThrumEnabled)
			{
				thrum.subSounds.Clear();
			}
			bool thrumOn = thrum?.subSounds != null && thrum.subSounds.Count > 0;
			return "hush=" + hushIn + " thrum=" + thrumOn;
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

		public const string ResaleTraderDefName = "Orbital_Exotic";

		/// <summary>WEBWORK_RESELL: the resale line's price tier from thrixweaveResaleSteepPrice (the generator is added by
		/// Patches/RM_Thrixweave_Resale.xml). Returns how many resale lines were set.</summary>
		public static int ApplyResalePrice(TraderKindDef kind)
		{
			int n = 0;
			if (kind?.stockGenerators == null) return 0;
			foreach (StockGenerator g in kind.stockGenerators)
			{
				if (g is StockGenerator_ThrixweaveResale)
				{
					g.price = RM_WebworkSettings.thrixweaveResaleSteepPrice ? PriceType.Expensive : PriceType.Normal;
					n++;
				}
			}
			return n;
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
