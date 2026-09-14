using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M1 build (miasma_kit_spec.md M1). Runs after
    // GenStep_Terrain (vanilla order 210) so it repaints what map-gen
    // already placed, exactly as the spec's own text specifies ("ordered
    // after GenStep_Terrain").
    //
    // Direction: a correction to the item's own spike write-up (Spike 1
    // finding 5), found reading the SAME live 1.6/Odyssey decompile this
    // pass — RimWorld.Planet/SurfaceTile.cs's RiverLink struct carries only
    // `neighbor` (a PlanetTile) and `river` (a RiverDef); there is no
    // stored per-link angle field to read (the spike's claim was wrong on
    // this specific point). Rather than derive a bearing from neighbor-tile
    // world positions (real complexity a river can run either way relative
    // to the coast, buying little certainty for it), this GenStep uses
    // World.CoastDirectionAt(tile)/LakeDirectionAt(tile) alone — both
    // confirmed real (RimWorld.Planet/World.cs:316), both return a Rot4
    // that already points FROM this tile TOWARD the adjacent sea/lake
    // tile — which is exactly the signal M1 needs (brine is toward the
    // water; fresh is the opposite direction) for a biome that the sheet's
    // own SS0 already measures as coastal (93 tiles strung along the Salt
    // Gate, 6 sea tiles, 32 river tiles). If neither resolves (defensive:
    // should not happen for this biome, but never crash map-gen over it) a
    // fixed default direction is used and logged once.
    public class RM_GenStep_GradientAxis : GenStep
    {
        // Arbitrary but stable, matching every other GenStep's own fixed
        // seed pattern in this mod (RM_GenStep_PlacedSetPieces.SeedPart).
        public override int SeedPart => 1994030146;

        public override void Generate(Map map, GenStepParams parms)
        {
            RM_MapComponent_GradientAxis axis = map.GetComponent<RM_MapComponent_GradientAxis>();
            if (axis == null)
            {
                // Should be unreachable — MapComponent subclasses are
                // auto-instantiated by Map.FillComponents() — but map-gen
                // must never hard-fail over a missing optional mechanic.
                Log.Error("[RM EnvironmentalHazards] RM_GenStep_GradientAxis: map has no RM_MapComponent_GradientAxis — skipping.");
                return;
            }

            RM_GradientAxisExtension ext = map.Biome != null ? map.Biome.GetModExtension<RM_GradientAxisExtension>() : null;

            Vector2 brineDir = BrineDirection(map);
            float halfExtent = Mathf.Max(map.Size.x, map.Size.z) * 0.5f;
            Vector2 origin = new Vector2(map.Size.x * 0.5f, map.Size.z * 0.5f);

            // Phase offset so different maps of the same biome don't share
            // one identical wandering pattern. Generate() runs inside the
            // map generator's own Rand-seeded scope (keyed off this GenStep
            // via SeedPart), so this stays deterministic per map/seed.
            float noiseOffsetX = Rand.Range(0f, 1000f);
            float noiseOffsetZ = Rand.Range(0f, 1000f);

            float noiseAmplitude = ext != null ? ext.noiseAmplitude : 0.12f;
            float noiseCellScale = ext != null ? ext.noiseCellScale : 0.045f;

            foreach (IntVec3 c in map.AllCells)
            {
                Vector2 rel = new Vector2(c.x, c.z) - origin;
                float projection = Vector2.Dot(rel, brineDir);
                float t = Mathf.InverseLerp(-halfExtent, halfExtent, projection);

                if (noiseAmplitude > 0f)
                {
                    float n = Mathf.PerlinNoise(noiseOffsetX + c.x * noiseCellScale, noiseOffsetZ + c.z * noiseCellScale);
                    t += (n * 2f - 1f) * noiseAmplitude;
                }

                t = Mathf.Clamp01(t);
                axis.SetSalinityAt(c, t);

                if (ext == null)
                {
                    continue; // axis recorded; no band table to paint from
                }

                RepaintCell(map, c, t, ext);
            }
        }

        private static void RepaintCell(Map map, IntVec3 c, float t, RM_GradientAxisExtension ext)
        {
            TerrainDef current = map.terrainGrid.TerrainAt(c);
            if (current == null)
            {
                return;
            }

            if (current.IsWater)
            {
                RM_GradientAxisWaterBand band = PickWaterBand(ext, t);
                if (band == null)
                {
                    return;
                }

                bool shallow = IsShallowWater(current);
                TerrainDef repaint = shallow ? band.terrainShallow : band.terrainDeep;
                if (repaint != null && repaint != current)
                {
                    map.terrainGrid.SetTerrain(c, repaint);
                }

                return;
            }

            if (ext.landTerrain != null && t >= ext.landRepaintMinSalinity
                && !ext.landRepaintSource.NullOrEmpty() && ext.landRepaintSource.Contains(current))
            {
                map.terrainGrid.SetTerrain(c, ext.landTerrain);
            }
        }

        private static RM_GradientAxisWaterBand PickWaterBand(RM_GradientAxisExtension ext, float t)
        {
            for (int i = 0; i < ext.waterBands.Count; i++)
            {
                if (t <= ext.waterBands[i].max)
                {
                    return ext.waterBands[i];
                }
            }

            return null;
        }

        // Heuristic, not a stored engine flag: WaterShallowBase-derived
        // terrain (vanilla and this mod's own LiquidTypes grades alike)
        // carries the ShallowWater affordance; WaterDeepBase-derived does
        // not. Good enough to pick the matching shallow/deep grade without
        // ever needing a hand-authored terrain-to-terrain lookup table.
        private static bool IsShallowWater(TerrainDef terrain)
        {
            if (terrain.affordances == null)
            {
                return false;
            }

            for (int i = 0; i < terrain.affordances.Count; i++)
            {
                if (terrain.affordances[i].defName == "ShallowWater")
                {
                    return true;
                }
            }

            return false;
        }

        private static Vector2 BrineDirection(Map map)
        {
            PlanetTile tile = map.Tile;
            Rot4 dir = Find.World.CoastDirectionAt(tile);
            if (!dir.IsValid)
            {
                dir = Find.World.LakeDirectionAt(tile);
            }

            if (!dir.IsValid)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] RM_GenStep_GradientAxis: tile " + tile
                    + " resolved neither a coast nor a lake direction — defaulting the brine axis to South. "
                    + "Owed: verify this against the live authored Miasma tiles.",
                    tile.GetHashCode() ^ 0x6117A215);
                dir = Rot4.South;
            }

            return dir.AsVector2;
        }
    }
}
