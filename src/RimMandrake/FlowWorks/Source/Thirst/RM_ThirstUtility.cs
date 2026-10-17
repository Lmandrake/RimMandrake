using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>Design §3: where a thirsty pawn drinks, and what a drink does. Every drink route (bottle ingest, terrain edge,
	/// tank, administered, caravan) ends in <see cref="Drink"/>, so the quality effects are the same everywhere and in both
	/// provider modes (they are about the liquid, not the need). Hydration is applied only to OUR need; in Dbh mode DBH reads
	/// its own WaterExt off the bottle.</summary>
	public static class RM_ThirstUtility
	{
		public const float SearchRadius = 60f;

		private static List<ThingDef> drinkableBottles;

		public static RM_WaterQuality? QualityOf(LiquidDef liquid)
		{
			if (liquid == null || !liquid.thirstQuality.HasValue)
			{
				return null;
			}
			return (RM_WaterQuality)(int)liquid.thirstQuality.Value;
		}

		public static RM_WaterQuality Effective(LiquidDef liquid)
		{
			return RM_ThirstMath.Effective(QualityOf(liquid) ?? RM_WaterQuality.Potable, RM_ThirstSettings.waterQualityEffects);
		}

		public static Need_RM_Thirst NeedOf(Pawn p)
		{
			return p?.needs?.TryGetNeed(RM_ThirstDefOf.RM_Thirst) as Need_RM_Thirst;
		}

		public static float Level(Pawn p)
		{
			return NeedOf(p)?.CurLevel ?? 1f;
		}

		public static bool IsThirsty(Pawn p)
		{
			return RM_ThirstProvider.OursLive && NeedOf(p) is Need_RM_Thirst n && n.CurLevel < RM_ThirstMath.ThirstyBelow;
		}

		/// <summary>The liquid a pawn drinks at a terrain: the registry row (RM_LiquidBottleUtility.LiquidAt), or, for a
		/// river or a fresh-water terrain no row adopts (vanilla rivers, a modded lake), plain fresh water. Ocean and every
		/// row without a thirstQuality (boiling, icy, acid, tar, fuel, slime, lava) is not a drink.</summary>
		public static LiquidDef DrinkLiquidAt(TerrainDef terrain)
		{
			if (terrain == null)
			{
				return null;
			}
			LiquidDef row = RM_LiquidBottleUtility.LiquidAt(terrain);
			if (row != null)
			{
				return row.thirstQuality.HasValue ? row : null;
			}
			if (terrain.IsRiver || (terrain.IsWater && !terrain.IsOcean))
			{
				return RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater;
			}
			return null;
		}

		/// <summary>Every drinkable container: a BOTTLE-sized ThingDef with an ingestible block holding a liquid that has a
		/// thirstQuality (buckets and barrels are not drunk, design §3).</summary>
		public static List<ThingDef> DrinkableBottles
		{
			get
			{
				if (drinkableBottles == null)
				{
					drinkableBottles = new List<ThingDef>();
					foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
					{
						RM_BottledLiquidExtension ext = d.GetModExtension<RM_BottledLiquidExtension>();
						if (ext?.liquid != null && ext.size == RM_ContainerSize.Bottle && d.ingestible != null
							&& ext.liquid.thirstQuality.HasValue)
						{
							drinkableBottles.Add(d);
						}
					}
				}
				return drinkableBottles;
			}
		}

		public static LiquidDef LiquidOf(Thing bottle)
		{
			RM_BottledLiquidExtension ext = bottle?.def.GetModExtension<RM_BottledLiquidExtension>();
			return ext != null && ext.size == RM_ContainerSize.Bottle && bottle.def.ingestible != null ? ext.liquid : null;
		}

		public static bool IsDrinkableBottle(Thing t)
		{
			return QualityOf(LiquidOf(t)).HasValue;
		}

		/// <summary>One drink. <paramref name="source"/> is the bottle (null for terrain or a tank).</summary>
		public static void Drink(Pawn pawn, LiquidDef liquid, float litres, Thing source)
		{
			if (pawn == null || pawn.Dead)
			{
				return;
			}
			RM_WaterQuality q = Effective(liquid);
			Need_RM_Thirst need = NeedOf(pawn);
			if (need != null && RM_ThirstProvider.OursLive)
			{
				need.CurLevel += RM_ThirstMath.Hydration(litres, q, RM_ThirstSettings.waterQualityEffects);
			}
			QualityEffects(pawn, q, source);
		}

		public static void QualityEffects(Pawn pawn, RM_WaterQuality q, Thing source)
		{
			if (!RM_ThirstSettings.waterQualityEffects)
			{
				return;
			}
			switch (q)
			{
				case RM_WaterQuality.Distilled:
					pawn.needs?.mood?.thoughts?.memories?.TryGainMemory(RM_ThirstDefOf.RM_Thought_DrankDistilled);
					break;
				case RM_WaterQuality.Fouled:
					// vanilla's rule: only humanlikes get food poisoning
					if (pawn.RaceProps.Humanlike && Rand.Chance(RM_ThirstMath.FouledPoisonChance))
					{
						if (source != null)
						{
							FoodUtility.AddFoodPoisoningHediff(pawn, source, FoodPoisonCause.DangerousFoodType);
						}
						else if (!pawn.health.hediffSet.HasHediff(HediffDefOf.FoodPoisoning))
						{
							pawn.health.AddHediff(HediffMaker.MakeHediff(HediffDefOf.FoodPoisoning, pawn));
						}
					}
					break;
				case RM_WaterQuality.Toxic:
					HealthUtility.AdjustSeverity(pawn, HediffDefOf.ToxicBuildup, RM_ThirstMath.ToxicBuildupPerDrink);
					break;
			}
		}

		// ── where to drink ────────────────────────────────────────────────

		/// <summary>The best drinkable bottle <paramref name="pawn"/> can reach (its inventory first, then its map), by quality
		/// then distance, acceptable for a drinker at <paramref name="level"/> (toxic only when parched).</summary>
		public static Thing BestBottle(Pawn pawn, float level, bool inventory, out RM_WaterQuality quality, out float dist)
		{
			quality = RM_WaterQuality.Toxic;
			dist = float.MaxValue;
			Thing best = null;
			if (inventory && pawn.inventory != null)
			{
				foreach (Thing t in pawn.inventory.innerContainer)
				{
					LiquidDef l = LiquidOf(t);
					if (!QualityOf(l).HasValue)
					{
						continue;
					}
					RM_WaterQuality q = Effective(l);
					if (RM_ThirstMath.Acceptable(q, level) && (best == null || RM_ThirstMath.Better(q, 0f, quality, dist)))
					{
						best = t;
						quality = q;
						dist = 0f;
					}
				}
			}
			Map map = pawn.Map;
			if (map == null)
			{
				return best;
			}
			var cands = new List<(Thing t, RM_WaterQuality q, float d)>();
			foreach (ThingDef def in DrinkableBottles)
			{
				List<Thing> things = map.listerThings.ThingsOfDef(def);
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					RM_WaterQuality q = Effective(LiquidOf(t));
					if (!RM_ThirstMath.Acceptable(q, level))
					{
						continue;
					}
					float d = (t.Position - pawn.Position).LengthHorizontalSquared;
					if (d > SearchRadius * SearchRadius * 4f)
					{
						continue;
					}
					cands.Add((t, q, d));
				}
			}
			cands.Sort((a, b) => a.q != b.q ? ((int)a.q).CompareTo((int)b.q) : a.d.CompareTo(b.d));
			for (int i = 0; i < cands.Count; i++)
			{
				var c = cands[i];
				if (best != null && !RM_ThirstMath.Better(c.q, c.d, quality, dist))
				{
					break;
				}
				if (c.t.IsForbidden(pawn) || !pawn.CanReserveAndReach(c.t, PathEndMode.ClosestTouch, Danger.Some, 1, 1))
				{
					continue;
				}
				return SetOut(c, out quality, out dist);
			}
			return best;
		}

		private static Thing SetOut((Thing t, RM_WaterQuality q, float d) c, out RM_WaterQuality quality, out float dist)
		{
			quality = c.q;
			dist = c.d;
			return c.t;
		}

		/// <summary>The best tank of the pawn's own faction holding a drinkable liquid with a drink's worth in it.</summary>
		public static Building_LiquidTank BestTank(Pawn pawn, float level, out RM_WaterQuality quality, out float dist)
		{
			quality = RM_WaterQuality.Toxic;
			dist = float.MaxValue;
			Building_LiquidTank best = null;
			Map map = pawn.Map;
			if (map == null || pawn.Faction == null)
			{
				return null;
			}
			int units = RM_Volume.Units(RM_ThirstMath.TankDrinkLitres);
			foreach (Building b in map.listerBuildings.allBuildingsColonist)
			{
				if (!(b is Building_LiquidTank tank) || tank.Faction != pawn.Faction || !QualityOf(tank.storedLiquid).HasValue
					|| !tank.CanProvide(units))
				{
					continue;
				}
				RM_WaterQuality q = Effective(tank.storedLiquid);
				float d = (tank.Position - pawn.Position).LengthHorizontalSquared;
				if (!RM_ThirstMath.Acceptable(q, level) || (best != null && !RM_ThirstMath.Better(q, d, quality, dist)))
				{
					continue;
				}
				if (tank.IsForbidden(pawn) || !pawn.CanReach(tank, PathEndMode.Touch, Danger.Some))
				{
					continue;
				}
				best = tank;
				quality = q;
				dist = d;
			}
			return best;
		}

		internal const int NoTerrainMarkTicks = 600;
		private static readonly Dictionary<int, int> noTerrainUntil = new Dictionary<int, int>();

		/// <summary>Nearest reachable drinkable terrain edge, best quality first. GenRadial walks in increasing distance, so
		/// the first reachable cell of a quality is the nearest of it; the walk stops at the first Potable-or-better hit. A
		/// pawn whose search found nothing is not searched again for 600 ticks (a dry desert map must not pay a radial walk
		/// per think for every thirsty wild animal).</summary>
		public static bool TryFindDrinkCell(Pawn pawn, float level, out IntVec3 cell, out LiquidDef liquid,
			out RM_WaterQuality quality)
		{
			cell = IntVec3.Invalid;
			liquid = null;
			quality = RM_WaterQuality.Toxic;
			Map map = pawn?.Map;
			if (map == null)
			{
				return false;
			}
			int now = Find.TickManager.TicksGame;
			if (noTerrainUntil.TryGetValue(pawn.thingIDNumber, out int until))
			{
				// marks are now+600; one further ahead is a stale entry from another game (thing IDs repeat across saves)
				if (now < until && until - now <= NoTerrainMarkTicks) return false;
				noTerrainUntil.Remove(pawn.thingIDNumber);
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			bool found = false;
			int reachFails = 0;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, SearchRadius, true))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				LiquidDef l = DrinkLiquidAt(map.terrainGrid.TerrainAt(c));
				if (l == null)
				{
					continue;
				}
				RM_WaterQuality q = Effective(l);
				if (!RM_ThirstMath.Acceptable(q, level) || (found && (int)q >= (int)quality))
				{
					continue;
				}
				if (ex?.Stock != null && !ex.Stock.CanSupply(map, c, ex))
				{
					continue;   // a spent pond body gives nothing (C2-F2, the bottle fill's rule)
				}
				if (c.IsForbidden(pawn) || !pawn.CanReach(c, PathEndMode.Touch, Danger.Some))
				{
					if (++reachFails > 40)
					{
						break;
					}
					continue;
				}
				cell = c;
				liquid = l;
				quality = q;
				found = true;
				if ((int)q <= (int)RM_WaterQuality.Potable)
				{
					break;
				}
			}
			if (!found)
			{
				noTerrainUntil[pawn.thingIDNumber] = now + NoTerrainMarkTicks;
			}
			return found;
		}

		public static Job TerrainJob(IntVec3 cell)
		{
			return JobMaker.MakeJob(RM_ThirstDefOf.RM_DrinkFromTerrain, cell);
		}

		// ── off the map ───────────────────────────────────────────────────

		/// <summary>The world grid knows rivers, not ponds: a caravan on a river tile can drink from it (its animals always,
		/// its people when no bottle is left).</summary>
		public static bool TileHasFreshWater(PlanetTile tile)
		{
			if (!tile.Valid)
			{
				return false;
			}
			SurfaceTile st = Find.WorldGrid[tile] as SurfaceTile;
			return st?.Rivers != null && st.Rivers.Count > 0;
		}
	}
}
