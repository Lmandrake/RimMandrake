using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
	// GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1, spec §3c (greatbole_harvest_spec.md): a greatbole
	// planted from RM_GreatboleSeed needs open water beside it to grow at all, and when it has
	// water it grows far faster than anything else on the map.
	//
	// Mechanism (MEASURED, decompiled 1.6, RimSage 2026-10-06): Plant.GrowthRate is a public
	// virtual property, and GrowthPerTick = 1 / (60000 * growDays) * GrowthRate. CompPlantable.DoPlant
	// sets plant.sown = true, which is how a seeded greatbole is told apart from a wild one.
	//
	// ONLY sown greatboles are touched. A wild RM_Greatbole (sown == false) grows exactly as the
	// roster shipped it — the water rule is the seed's rule (spec §3c), not a new rule for the
	// species' wild population.
	//
	// Readable sign: the inspect pane says when a planted greatbole has no water and so is not
	// growing, and when it is growing fast because it has. CompPlantable.CanPlantAt is not virtual,
	// so a dry cell cannot be refused at targeting time without Harmony; the sapling simply
	// sits at zero growth and says why.
	public class RM_GreatboleSeedlingExtension : DefModExtension
	{
		// "Adjacent water is REQUIRED" (spec §3c). 1.5 = the eight neighbouring cells.
		public float waterRadius = 1.5f;
		// INVENTED: 220 growDays / 20 = 11 days to maturity — "stupendously fast and visibly so".
		public float sownGrowthMultiplier = 20f;
	}

	public class RM_Plant_Greatbole : Plant
	{
		private const int WaterRecheckTicks = 2500;

		private int lastWaterCheckTick = -999999;
		private bool cachedHasWater;

		private RM_GreatboleSeedlingExtension Ext => def.GetModExtension<RM_GreatboleSeedlingExtension>();

		private bool SeedRulesApply => sown && RM_GreentideSettings.greatboleSeedPlantingEnabled && Ext != null;

		public bool HasOpenWaterNearby
		{
			get
			{
				if (!Spawned)
				{
					return false;
				}
				int now = Find.TickManager.TicksGame;
				if (now - lastWaterCheckTick >= WaterRecheckTicks || now < lastWaterCheckTick)
				{
					lastWaterCheckTick = now;
					cachedHasWater = ComputeHasWater();
				}
				return cachedHasWater;
			}
		}

		private bool ComputeHasWater()
		{
			Map map = Map;
			float radius = Ext?.waterRadius ?? 1.5f;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, radius, useCenter: true))
			{
				if (c.InBounds(map) && c.GetTerrain(map).IsWater)
				{
					return true;
				}
			}
			return false;
		}

		public override float GrowthRate
		{
			get
			{
				float baseRate = base.GrowthRate;
				if (!SeedRulesApply)
				{
					return baseRate;
				}
				if (!HasOpenWaterNearby)
				{
					return 0f;
				}
				return baseRate * Ext.sownGrowthMultiplier;
			}
		}

		public override string GrowthRateCalcDesc
		{
			get
			{
				string baseDesc = base.GrowthRateCalcDesc;
				if (!SeedRulesApply)
				{
					return baseDesc;
				}
				var sb = new StringBuilder(baseDesc ?? string.Empty);
				if (!HasOpenWaterNearby)
				{
					sb.AppendInNewLine("RM_GreatboleSeedling_NoWaterFactor".Translate());
				}
				else
				{
					sb.AppendInNewLine("RM_GreatboleSeedling_WaterFactor".Translate(Ext.sownGrowthMultiplier.ToStringPercent()));
				}
				return sb.ToString();
			}
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			if (!SeedRulesApply || !Spawned || LifeStage != PlantLifeStage.Growing)
			{
				return s;
			}
			string line = HasOpenWaterNearby
				? "RM_GreatboleSeedling_InspectWater".Translate().ToString()
				: "RM_GreatboleSeedling_InspectNoWater".Translate().ToString();
			return s.NullOrEmpty() ? line : s + "\n" + line;
		}
	}
}
