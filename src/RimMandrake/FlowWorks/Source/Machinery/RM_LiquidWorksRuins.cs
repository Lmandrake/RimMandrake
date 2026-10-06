using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>LIQUID_INDUSTRY_SETPIECES_1: a kludged or repaired works may only be raised over its own ruin
	/// (or an earlier tier of itself) — industrial scale is FOUND, never built from nothing. Mod Setting
	/// industrialWorksBuildAnywhere lifts it (the public wave's switch).</summary>
	public class RM_RestoreOverExtension : DefModExtension
	{
		public List<ThingDef> over = new List<ThingDef>();
	}

	public class PlaceWorker_RM_OverRuin : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map,
			Thing thingToIgnore = null, Thing thing = null)
		{
			if (RM_MachinerySettings.industrialWorksBuildAnywhere)
			{
				return true;
			}
			RM_RestoreOverExtension ext = (checkingDef as ThingDef)?.GetModExtension<RM_RestoreOverExtension>();
			if (ext == null || ext.over.NullOrEmpty())
			{
				return true;
			}
			foreach (Thing t in loc.GetThingList(map))
			{
				if (ext.over.Contains(t.def) && t.Position == loc)
				{
					return true;
				}
			}
			return new AcceptanceReport("RMFlow_MustRestoreOverRuin".Translate(ext.over[0].label));
		}
	}

	/// <summary>Dressing for a found ruin (design §4: "set-pieces stock stealable pumps and tanks feeding the
	/// tanker pillar"): on first spawn it sets a damaged pump and a part-filled tank beside itself, holding
	/// the liquid that lies nearest. Runs once per ruin (scribed), never on load.</summary>
	public class CompProperties_LiquidWorksRuin : CompProperties
	{
		public ThingDef pumpDef;
		public ThingDef tankDef;
		public List<LiquidDef> stockLiquids = new List<LiquidDef>();
		public FloatRange stockFraction = new FloatRange(0.15f, 0.5f);
		public FloatRange hitPointFraction = new FloatRange(0.25f, 0.6f);

		public CompProperties_LiquidWorksRuin()
		{
			compClass = typeof(CompLiquidWorksRuin);
		}
	}

	public class CompLiquidWorksRuin : ThingComp
	{
		private bool dressed;

		public CompProperties_LiquidWorksRuin Props => (CompProperties_LiquidWorksRuin)props;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref dressed, "RM_ruinDressed", false);
		}

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			if (respawningAfterLoad || dressed)
			{
				return;
			}
			dressed = true;
			if (!RM_MachinerySettings.liquidWorksRuinStockEnabled || parent.Faction == Faction.OfPlayer)
			{
				return;
			}
			Map map = parent.Map;
			LiquidDef liquid = NearestLiquid(map);
			if (Props.tankDef != null)
			{
				Thing tank = SpawnBeside(Props.tankDef, map);
				if (tank is Building_LiquidTank t && liquid != null)
				{
					t.TryAddLiquid(liquid, System.Math.Max(5, (int)(t.Capacity * Props.stockFraction.RandomInRange)));
				}
			}
			if (Props.pumpDef != null)
			{
				SpawnBeside(Props.pumpDef, map);
			}
		}

		private LiquidDef NearestLiquid(Map map)
		{
			foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, 14f, true))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				TerrainDef terr = c.GetTerrain(map);
				foreach (LiquidDef l in Props.stockLiquids)
				{
					LiquidTerrainSuite s = l?.terrainSuite;
					if (s != null && (s.shallow == terr || s.deep == terr || s.chestDeep == terr))
					{
						return l;
					}
				}
			}
			return Props.stockLiquids.NullOrEmpty() ? null : Props.stockLiquids[0];
		}

		private Thing SpawnBeside(ThingDef def, Map map)
		{
			ThingDef stuff = def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null;
			foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(parent).InRandomOrder())
			{
				CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, def.size);
				bool ok = true;
				foreach (IntVec3 r in rect)
				{
					if (!r.InBounds(map) || !r.Standable(map) || r.GetEdifice(map) != null || r.GetTerrain(map).IsWater
						|| parent.OccupiedRect().Contains(r))
					{
						ok = false;
						break;
					}
				}
				if (!ok)
				{
					continue;
				}
				Thing t = ThingMaker.MakeThing(def, stuff);
				t.HitPoints = System.Math.Max(1, (int)(t.MaxHitPoints * Props.hitPointFraction.RandomInRange));
				return GenSpawn.Spawn(t, c, map);
			}
			return null;
		}
	}

	/// <summary>Site validator for the shared set-piece scatterer (RM_GenStep_PlacedSetPieces, Environmental
	/// Hazards kit): a dry, buildable footprint of <see cref="size"/> with one of <see cref="liquids"/>' terrain
	/// within <see cref="radius"/>. Mod Setting liquidWorksRuinsEnabled off: no site is ever valid.</summary>
	public class RM_ScattererValidator_NearLiquid : ScattererValidator
	{
		public List<LiquidDef> liquids = new List<LiquidDef>();
		public bool anyLiquid;
		public float radius = 10f;
		public IntVec2 size = new IntVec2(3, 3);

		public override bool Allows(IntVec3 c, Map map)
		{
			if (!RM_MachinerySettings.liquidWorksRuinsEnabled)
			{
				return false;
			}
			CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, size).ExpandedBy(1);
			foreach (IntVec3 r in rect)
			{
				if (!r.InBounds(map) || !r.Standable(map) || r.GetEdifice(map) != null || r.GetTerrain(map).IsWater
					|| r.Roofed(map))
				{
					return false;
				}
			}
			foreach (IntVec3 n in GenRadial.RadialCellsAround(c, radius, true))
			{
				if (n.InBounds(map) && Matches(n.GetTerrain(map)))
				{
					return true;
				}
			}
			return false;
		}

		private bool Matches(TerrainDef terr)
		{
			if (terr == null)
			{
				return false;
			}
			foreach (LiquidDef l in anyLiquid ? DefDatabase<LiquidDef>.AllDefsListForReading : liquids)
			{
				LiquidTerrainSuite s = l?.terrainSuite;
				if (s != null && (s.shallow == terr || s.deep == terr || s.chestDeep == terr))
				{
					return true;
				}
			}
			return false;
		}
	}
}
