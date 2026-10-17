using System.Collections.Generic;
using System.Xml;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>Design §5 caravans: every 2500 ticks, a player caravan member below 0.3 drinks the best bottle in the
	/// caravan's inventory (toxic only when parched). Off the map a pawn's need still falls (vanilla keeps caravan members'
	/// needs live), so without this a caravan would die of thirst. A caravan on a river tile drinks from the river: its
	/// animals always (animals never drink bottles, OQ-5), its people when no bottle is left. The forming-screen
	/// days-of-water readout (design build step 6) is NOT built: owed, may be cut to a tooltip.</summary>
	public class RM_WorldComponent_ThirstCaravan : WorldComponent
	{
		public const int Interval = 2500;

		public RM_WorldComponent_ThirstCaravan(World world) : base(world)
		{
		}

		public override void WorldComponentTick()
		{
			if (Find.TickManager.TicksGame % Interval != 0 || !RM_ThirstProvider.OursLive)
			{
				return;
			}
			List<Caravan> caravans = Find.WorldObjects.Caravans;
			for (int i = 0; i < caravans.Count; i++)
			{
				if (caravans[i].IsPlayerControlled)
				{
					Tend(caravans[i]);
				}
			}
		}

		private static void Tend(Caravan caravan)
		{
			bool river = RM_ThirstUtility.TileHasFreshWater(caravan.Tile);
			List<Pawn> pawns = caravan.PawnsListForReading;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (!RM_ThirstUtility.IsThirsty(p))
				{
					continue;
				}
				if (p.RaceProps.Humanlike && TryDrinkBottle(caravan, p))
				{
					continue;
				}
				if (river)
				{
					RM_ThirstUtility.Drink(p, RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater, RM_ThirstMath.TerrainDrinkLitres, null);
				}
			}
		}

		private static bool TryDrinkBottle(Caravan caravan, Pawn p)
		{
			float level = RM_ThirstUtility.Level(p);
			Thing best = null;
			RM_WaterQuality bestQ = RM_WaterQuality.Toxic;
			foreach (Thing t in CaravanInventoryUtility.AllInventoryItems(caravan))
			{
				LiquidDef l = RM_ThirstUtility.LiquidOf(t);
				if (!RM_ThirstUtility.QualityOf(l).HasValue)
				{
					continue;
				}
				RM_WaterQuality q = RM_ThirstUtility.Effective(l);
				if (RM_ThirstMath.Acceptable(q, level) && (best == null || (int)q < (int)bestQ))
				{
					best = t;
					bestQ = q;
				}
			}
			if (best == null)
			{
				return false;
			}
			Thing one = best.SplitOff(1);
			one.Ingested(p, 0f);
			return true;
		}
	}

	/// <summary>The dbhBottleBridge switch for the generated DBH patch (Patches/LiquidTypes/RM_DBH_BottleWaterExt.xml): runs
	/// its inner operations only while the setting is on. Mod Settings are read in the Mod constructor, which runs before
	/// patches apply, so the player's value is known here; a change needs a restart (labelled so).</summary>
	public class RM_PatchOperation_ThirstBridge : PatchOperation
	{
#pragma warning disable CS0649 // set by the XML loader
		private List<PatchOperation> operations;
#pragma warning restore CS0649

		protected override bool ApplyWorker(XmlDocument xml)
		{
			if (!RM_ThirstSettings.dbhBottleBridge || operations == null)
			{
				return true;
			}
			bool ok = true;
			foreach (PatchOperation op in operations)
			{
				if (!op.Apply(xml))
				{
					ok = false;
				}
			}
			return ok;
		}
	}
}
