using RimWorld;
using Verse;

namespace RimMandrake.Webwork
{
	/// <summary>
	/// WEBWORK_NEST_EGG_ECONOMY_1. Design doc §3d / S6 ruling 3 (owner,
	/// question card, 2026-09-24): "a nest on EVERY Webwork map ... no
	/// Webwork colony is without the egg economy." This is a plain GenStep
	/// that unconditionally places exactly one nest cluster, rather than a
	/// probabilistic scatter density that could come up empty — the shape
	/// the old campaign-tier placeholder used (RUT_WebworkNestScatter,
	/// ShokkweaveEconomy's own ShokkweaveHarvestScatter.xml, "a map either
	/// has one nest or none"). That campaign GenStepDef is untouched by this
	/// item; its own retarget to RM_Ollathrix/this mod's defs is
	/// WEBWORK_RM_MOD_BUILD_1 §5 table scope.
	///
	/// Places one RM_Webwork_NestWall (the mother's guardian spawner) plus
	/// 2-3 RM_Webwork_EggClutch (the harvestable resource) in the immediate
	/// ring around it — §3a's table, minus the flavour-only hide-mass/
	/// flower-ring/mite-trail rows (owed to WEBWORK_WEB_STRUCTURES_1/
	/// WEBWORK_MECHANICS_1, not required for the mechanic).
	///
	/// Placement is a plain rejection-sampling search, same idiom as
	/// RM_GenStep_AntHiveDungeon.TryFindAnchor (FeverWood) rather than
	/// ScattererValidator machinery: prefers the map's richest fertility
	/// ground first (§3a: "the richest ground on the map — the mother
	/// irrigates it"), then falls back to any standable non-edge cell so the
	/// nest is never simply absent because no rich soil rolled on a given
	/// map — ruling 3's own "no Webwork colony is without the egg economy"
	/// would otherwise be violated by a failed roll, not honoured by one.
	/// </summary>
	public class RM_GenStep_WebworkNest : GenStep
	{
		public const string WebworkBiomeDefName = "RM_Webwork";
		public const string NestWallDefName = "RM_Webwork_NestWall";
		public const string EggClutchDefName = "RM_Webwork_EggClutch";

		private const int EdgeMargin = 8;
		private const int PlacementAttempts = 80;
		private const float RichFertilityThreshold = 0.6f;
		private const float ClutchRingRadius = 3f;

		public override int SeedPart => 194074231;

		public override void Generate(Map map, GenStepParams parms)
		{
			if (map.Biome == null || map.Biome.defName != WebworkBiomeDefName)
			{
				return;
			}

			if (!RM_WebworkSettings.nestEnabled)
			{
				return; // MOD_OPTIONS_RETROFIT_1: map-gen-affecting master toggle
			}

			ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail(NestWallDefName);
			ThingDef clutchDef = DefDatabase<ThingDef>.GetNamedSilentFail(EggClutchDefName);
			if (wallDef == null || clutchDef == null)
			{
				Log.Warning("[RM Webwork] RM_GenStep_WebworkNest: " + NestWallDefName + "/"
					+ EggClutchDefName + " not found — nest skipped on " + map.Biome.defName + ".");
				return;
			}

			if (!TryFindCenter(map, out IntVec3 center))
			{
				Log.Warning("[RM Webwork] RM_GenStep_WebworkNest: no valid site found on "
					+ map.Biome.defName + " — nest skipped this map (S6 ruling 3 expects one on every map).");
				return;
			}

			GenSpawn.Spawn(ThingMaker.MakeThing(wallDef), center, map);

			int clutchCount = Rand.RangeInclusive(2, 3);
			int placed = 0;
			foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, ClutchRingRadius, false))
			{
				if (placed >= clutchCount)
				{
					break;
				}
				if (cell == center || !cell.InBounds(map) || !cell.Standable(map))
				{
					continue;
				}
				GenSpawn.Spawn(ThingMaker.MakeThing(clutchDef), cell, map);
				placed++;
			}

			if (placed == 0 && CellFinder.TryFindRandomCellNear(center, map, 4,
				(IntVec3 c) => c != center && c.Standable(map), out IntVec3 fallback))
			{
				// Degrade gracefully rather than leaving the mother with no
				// clutch at all if the ring's own Standable filter rejected
				// every candidate (e.g. dense terrain right around center).
				GenSpawn.Spawn(ThingMaker.MakeThing(clutchDef), fallback, map);
				placed = 1;
			}

			Log.Message("[RM Webwork] RM_GenStep_WebworkNest: placed a nest (1 wall, " + placed
				+ " clutch/es) on " + map.Biome.defName + " at " + center + ".");
		}

		private bool TryFindCenter(Map map, out IntVec3 result)
		{
			for (int attempt = 0; attempt < PlacementAttempts; attempt++)
			{
				IntVec3 candidate = CellFinder.RandomCell(map);
				if (!InBoundsWithMargin(map, candidate) || !candidate.Standable(map))
				{
					continue;
				}
				if (candidate.GetTerrain(map).fertility >= RichFertilityThreshold)
				{
					result = candidate;
					return true;
				}
			}

			for (int attempt = 0; attempt < PlacementAttempts; attempt++)
			{
				IntVec3 candidate = CellFinder.RandomCell(map);
				if (InBoundsWithMargin(map, candidate) && candidate.Standable(map))
				{
					result = candidate;
					return true;
				}
			}

			result = IntVec3.Invalid;
			return false;
		}

		private bool InBoundsWithMargin(Map map, IntVec3 cell)
		{
			return cell.x >= EdgeMargin && cell.z >= EdgeMargin
				&& cell.x < map.Size.x - EdgeMargin && cell.z < map.Size.z - EdgeMargin;
		}
	}
}
