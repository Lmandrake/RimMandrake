using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.Webwork
{
	/// <summary>
	/// WEBWORK_BASE_PORT_BUILD_1. Startup-time application of the Webwork's two settings-gated mechanisms.
	/// Runs once after defs load (so a change needs a restart, and the settings say so).
	/// 1. The thrixweave sole-source strip, moved down from the campaign tier (SHOKKWEAVE_SOLE_SOURCE_1):
	///    tradeability All -> Sellable (TraderCanSell() is false for Sellable, which closes every stock route
	///    in StockGeneratorUtility; the colonist can still sell it), RewardStandardCore removed from the
	///    quest-reward pool, the ExoticMisc trade tag removed as a second lock, stuff commonality 0.1 -> 0.05.
	/// 2. The creeping front: off removes RM_FrontCreepExtension from RM_Webwork; otherwise the advance
	///    interval is scaled. The extension class lives in CreatureBehaviors, so it is reached by type name
	///    and field reflection (no assembly reference).
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
			ApplyFront(DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Webwork"));
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

		private static void ApplyFront(BiomeDef biome)
		{
			if (biome?.modExtensions == null)
			{
				return;
			}
			for (int i = biome.modExtensions.Count - 1; i >= 0; i--)
			{
				DefModExtension ext = biome.modExtensions[i];
				if (ext.GetType().Name != "RM_FrontCreepExtension")
				{
					continue;
				}
				if (!RM_WebworkSettings.frontCreepEnabled)
				{
					biome.modExtensions.RemoveAt(i);
					continue;
				}
				FieldInfo f = ext.GetType().GetField("advanceIntervalTicks");
				if (f != null)
				{
					f.SetValue(ext, (int)(((int)f.GetValue(ext)) * RM_WebworkSettings.frontCreepIntervalMultiplier));
				}
			}
		}
	}
}
