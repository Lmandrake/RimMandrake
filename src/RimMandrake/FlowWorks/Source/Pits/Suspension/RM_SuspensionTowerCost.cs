using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>SUSPENSION_ISLANDS_BUILD_TOWERS_COST_PLENTY: Mod Settings "Tower cost multiplier" applied to the tower def. The
	/// def's own numbers (after every patch) are copied once at startup and every change assigns base × multiplier
	/// (RM_SuspensionMath.ScaledCost), never multiplying the current values again. A blueprint or frame placed earlier keeps
	/// the materials it was planned with until it is replaced: the def is the price of the next tower.</summary>
	[StaticConstructorOnStartup]
	public static class RM_SuspensionTowerCost
	{
		private static List<ThingDefCountClass> baseList;
		private static int baseStuff;
		private static float baseWork;
		private static bool captured;

		static RM_SuspensionTowerCost()
		{
			ThingDef d = RM_SuspensionDefOf.RM_SuspensionTower;
			if (d == null)
			{
				return;
			}
			baseList = new List<ThingDefCountClass>();
			if (d.costList != null)
			{
				foreach (ThingDefCountClass c in d.costList)
				{
					baseList.Add(new ThingDefCountClass(c.thingDef, c.count));
				}
			}
			baseStuff = d.costStuffCount;
			baseWork = d.GetStatValueAbstract(StatDefOf.WorkToBuild);
			captured = true;
			Apply();
		}

		/// <summary>Set the tower def's cost from the base and the current multiplier (no-op before the defs are loaded).</summary>
		public static void Apply()
		{
			ThingDef d = RM_SuspensionDefOf.RM_SuspensionTower;
			if (!captured || d == null)
			{
				return;
			}
			float m = RM_SuspensionSettings.towerCostMultiplier;
			d.costStuffCount = RM_SuspensionMath.ScaledCost(baseStuff, m);
			if (baseList.Count > 0)
			{
				d.costList = new List<ThingDefCountClass>();
				foreach (ThingDefCountClass c in baseList)
				{
					d.costList.Add(new ThingDefCountClass(c.thingDef, RM_SuspensionMath.ScaledCost(c.count, m)));
				}
			}
			StatUtility.SetStatValueInList(ref d.statBases, StatDefOf.WorkToBuild, RM_SuspensionMath.ScaledCost((int)baseWork, m));
		}

		/// <summary>What one tower costs now, for the proof: "stuff=200 Steel=100 work=12000 mult=1.00" (a bridge needs one
		/// tower per lane; no components since SUSPENSION_TOWER_TUNE_NO_CHIPS_IN_STONE).</summary>
		public static string Describe()
		{
			ThingDef d = RM_SuspensionDefOf.RM_SuspensionTower;
			if (d == null)
			{
				return "no tower def";
			}
			string s = "stuff=" + d.costStuffCount;
			if (d.costList != null)
			{
				foreach (ThingDefCountClass c in d.costList)
				{
					s += " " + c.thingDef.defName + "=" + c.count;
				}
			}
			return s + " work=" + d.GetStatValueAbstract(StatDefOf.WorkToBuild) + " mult=" + RM_SuspensionSettings.towerCostMultiplier.ToString("0.00");
		}
	}
}
