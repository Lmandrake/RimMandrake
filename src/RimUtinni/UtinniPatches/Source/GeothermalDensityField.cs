using System;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
	// GEOTHERMAL_DENSITY_FIELD_1 (owner ruling R12): vanilla's SteamGeysers
	// GenStepDef (GenStep_ScatterGeysers, Core/Defs/MapGeneration) gates its
	// count on countPer10kCellsRange * map.Biome.geyserCountFactor *
	// TileMutatorDef.geyserCountFactor — none of which vary with WORLD
	// POSITION, so every map on the frozen Ash'karr planet gets ~0.7-1
	// geysers per 10k cells regardless of whether it sits on the dayside
	// mountain spine or deep in the nightside cold. This gives every map a
	// SECOND multiplier, keyed on where the tile actually sits.
	//
	// The arc-from-substellar-point formula is NOT reinvented here — it is
	// the exact great-circle test RimMandrake.StarWars.WeatherSuite's
	// WeatherGeometryUtility.ArcFromSubstellar already ships and that mod's
	// own header cites as verified against world/ASHKARR_WORLDMAP_tiles.csv
	// row 0 (WeatherSuiteHook.cs). Reusing it means this field agrees with
	// the terminator storm wall and the dark-side aurora about where the
	// terminator actually is, by construction, instead of by coincidence.
	//
	// "Distance from the nearest dayside mountain range" is a DIFFERENT
	// query (angular distance between two arbitrary tiles, not a tile and
	// the fixed substellar point), so it needs its own formula. It is the
	// same spherical-law-of-cosines shape as ArcFromSubstellar (and as
	// world_relief.py's `ang()` / ashkarr_rebase_from_save.py's `arc_of()` —
	// see that file's docstring), generalised to two arbitrary points
	// instead of one fixed at (0,0). Do not read this as a second,
	// competing arc definition — it collapses to ArcFromSubstellar exactly
	// when one of the two points is the substellar point.
	public static class GeothermalDensityUtility
	{
		// Degrees of great-circle distance over which the mountain-range
		// falloff decays by 1/e. 20 degrees is a soft-touch first cut: on
		// Ash'karr's ~2000-tile surface a "close to a dayside range" tile
		// is a few tiles away, not a quarter of a hemisphere. Not owner-
		// ruled; a tuning knob the falloff report exists to let him judge —
		// now exposed as UtinniPatchesSettings.geothermalMountainFalloffDeg
		// (MOD_OPTIONS_RETROFIT_1), default unchanged at 20f.

		// "Full density on dayside mountainous/hilly tiles" per the item's
		// own scope note: a tile's own terrain already buys most of the way
		// there without needing to be near any OTHER range.
		private static float OwnHillinessFactor(Hilliness h)
		{
			switch (h)
			{
				case Hilliness.Mountainous:
				case Hilliness.Impassable:
					return 1f;
				case Hilliness.LargeHills:
					return 0.75f;
				case Hilliness.SmallHills:
					return 0.45f;
				case Hilliness.Flat:
					return 0.15f;
				default:
					return 0f;
			}
		}

		private static bool IsMountainous(Hilliness h)
		{
			return h == Hilliness.Mountainous || h == Hilliness.Impassable;
		}

		// General two-point great-circle angular distance, degrees. Same
		// formula as WeatherGeometryUtility.ArcFromSubstellar with the fixed
		// substellar point replaced by an arbitrary second tile's lat/lon.
		private static float AngularDistanceDeg(Vector2 longLatA, Vector2 longLatB)
		{
			float latA = longLatA.y * Mathf.Deg2Rad;
			float lonA = longLatA.x * Mathf.Deg2Rad;
			float latB = longLatB.y * Mathf.Deg2Rad;
			float lonB = longLatB.x * Mathf.Deg2Rad;

			float cosD = Mathf.Sin(latA) * Mathf.Sin(latB)
			             + Mathf.Cos(latA) * Mathf.Cos(latB) * Mathf.Cos(lonA - lonB);
			cosD = Mathf.Clamp(cosD, -1f, 1f);
			return Mathf.Acos(cosD) * Mathf.Rad2Deg;
		}

		// Degrees to the nearest DAYSIDE (arc < 90) mountainous/impassable
		// tile, or -1f if none exists on the loaded world. O(TilesCount) —
		// runs once per map generation, not per cell; Ash'karr's surface is
		// a few thousand tiles, cheap at that cadence.
		private static float DistanceToNearestDaysideMountainDeg(PlanetTile from)
		{
			WorldGrid grid = Find.WorldGrid;
			if (grid == null || !from.Valid)
			{
				return -1f;
			}
			Vector2 fromLongLat = grid.LongLatOf(from);
			float best = -1f;
			int count = grid.TilesCount;
			for (int i = 0; i < count; i++)
			{
				PlanetTile candidate = new PlanetTile(i);
				Tile t = grid[candidate];
				if (t == null || !IsMountainous(t.hilliness))
				{
					continue;
				}
				float candidateArc = RimMandrake.StarWars.WeatherSuite.WeatherGeometryUtility.ArcFromSubstellar(candidate);
				if (candidateArc < 0f || candidateArc >= 90f)
				{
					continue; // nightside/terminator mountain ranges don't count
				}
				float d = AngularDistanceDeg(fromLongLat, grid.LongLatOf(candidate));
				if (best < 0f || d < best)
				{
					best = d;
				}
			}
			return best;
		}

		private static float MountainFalloffDeg => UtinniPatchesSettings.geothermalMountainFalloffDeg;

		// 0..1 per-tile geothermal density. Zero past the terminator
		// (arc >= 90, the item's own hard cutoff); on the dayside, the max
		// of "how mountainous is THIS tile" and "how close is the nearest
		// dayside mountain range."
		//
		// Fails OPEN (returns 1f, i.e. vanilla behaviour) rather than zeroing
		// every geyser on the planet if no PlanetGeometryDef is loaded —
		// mirrors WeatherGeometryUtility's own fail-closed-per-band-but-
		// fail-safe-for-the-caller shape, and means this code does nothing
		// destructive on a non-Ashkarr world that happens to load this mod.
		public static float ComputeDensity(PlanetTile tile)
		{
			if (Find.WorldGrid == null || !tile.Valid)
			{
				return 1f;
			}
			float arc = RimMandrake.StarWars.WeatherSuite.WeatherGeometryUtility.ArcFromSubstellar(tile);
			if (arc < 0f)
			{
				return 1f; // no PlanetGeometryDef loaded — don't gate a world this mod wasn't authored for
			}
			if (arc >= 90f)
			{
				return 0f; // past the terminator: nightside, hard zero per spec
			}

			Hilliness hilliness = tile.Tile.hilliness;
			float ownFactor = OwnHillinessFactor(hilliness);

			float nearestDist = DistanceToNearestDaysideMountainDeg(tile);
			float distFactor = (nearestDist < 0f) ? 0f : Mathf.Exp(-nearestDist / MountainFalloffDeg);

			return Mathf.Clamp01(Mathf.Max(ownFactor, distFactor));
		}
	}

	// Swapped in for vanilla's GenStep_ScatterGeysers via
	// Patches/GeothermalDensityField.xml (PatchOperationAttributeSet on
	// SteamGeysers' genStep Class attribute) rather than a Harmony patch —
	// same no-Harmony, plain-subclass shape as LanternDeeps'
	// GenStep_ScatterCavePortal. Multiplies vanilla's own count (already
	// gated by biome/mutator geyserCountFactor, minSpacing, terrain
	// validation etc. — all preserved) by the world-position density field.
	public class GenStep_ScatterGeysersDensityField : GenStep_ScatterGeysers
	{
		protected override int CalculateFinalCount(Map map)
		{
			int baseCount = base.CalculateFinalCount(map);
			if (baseCount <= 0)
			{
				return baseCount;
			}
			if (!UtinniPatchesSettings.geothermalDensityFieldEnabled)
			{
				return baseCount;
			}
			try
			{
				float density = GeothermalDensityUtility.ComputeDensity(map.Tile);
				return Mathf.RoundToInt(baseCount * density);
			}
			catch (Exception e)
			{
				Log.WarningOnce("[RimMandrake.Utinni.UtinniPatches] GeothermalDensityField failed, "
				                 + "falling back to vanilla geyser count: " + e.Message, 0x67A02);
				return baseCount;
			}
		}
	}
}
