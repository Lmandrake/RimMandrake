using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD water review, owner ruling 2026-09-25 (SCALD_REVIEW live walk):
    // "some rippling animation from bubbles emerging from the surface ...
    // just the disturbances themselves would be welcome to show how
    // agitated the water is. That could be used to distinguish margin vs
    // shallow vs deep: margin is calm, shallow has a bit of agitation, deep
    // has constant agitation." Generic, terrain-tag-gated like every other
    // mechanism in this kit — not Scald-hardcoded, so any future biome's
    // boiling/roiling/agitated water opts in with two tags and zero new C#.
    //
    // Reuses the vanilla engine's own disturbance mote outright rather than
    // inventing one: RimWorld already spawns FleckDefOf.WaterRipple every
    // time a pawn steps through water (Verse.PawnWaterRippleMaker, on every
    // Pawn's own Pawn_DrawTracker) via the public
    // RimWorld.FleckMaker.WaterRipple(Vector3, Map, float) call. This
    // MapComponent just calls the same engine method itself, at intervals,
    // from cells the water has no pawn standing in — no new art, no new
    // FleckDef, no new shader; MEASURED against the decompiled engine
    // (Source/Verse/PawnWaterRippleMaker.cs, Source/RimWorld/FleckMaker.cs)
    // before writing this.
    //
    // Two tags, not a shared one with the wreck-scatter tag
    // (RUT_ScaldShallow) — same "each purpose gets its own tag" convention
    // this kit already follows elsewhere (RUT_ScaldMarginMat vs the generic
    // Water tag): RM_WaterAgitationLight (occasional ripples — the Scald's
    // three shallow variants) and RM_WaterAgitationHeavy (frequent, near-
    // constant ripples — the Scald's three deep/chest-deep variants). The
    // Scald's margin ring (RUT_ScaldMargin) carries neither, staying calm
    // per the owner's own three-way split.
    public class RM_MapComponent_WaterAgitation : MapComponent
    {
        private const int RescanIntervalTicks = 2500; // 1 in-game hour, same cadence as RM_MapComponent_VaporColumns

        // INVENTED — the owner named no figures, only "a bit" vs "constant".
        // Light: a ripple every couple of in-game minutes per qualifying
        // cell-pool, read as occasional. Heavy: roughly 5x as frequent, read
        // as a surface that never quite settles. Both randomized within a
        // range so many maps' pools don't all pulse in lockstep.
        private const int LightRippleMinTicks = 240;
        private const int LightRippleMaxTicks = 480;
        private const int HeavyRippleMinTicks = 40;
        private const int HeavyRippleMaxTicks = 100;

        private const float LightRippleSize = 0.5f;
        private const float HeavyRippleSize = 0.7f;

        private readonly List<IntVec3> lightCells = new List<IntVec3>();
        private readonly List<IntVec3> heavyCells = new List<IntVec3>();

        private int ticksUntilRescan = 1;
        private int ticksUntilLightRipple = 1;
        private int ticksUntilHeavyRipple = 1;

        public RM_MapComponent_WaterAgitation(Map map)
            : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Rebuild();
            ticksUntilRescan = RescanIntervalTicks;
            ticksUntilLightRipple = Rand.RangeInclusive(LightRippleMinTicks, LightRippleMaxTicks);
            ticksUntilHeavyRipple = Rand.RangeInclusive(HeavyRippleMinTicks, HeavyRippleMaxTicks);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (--ticksUntilRescan <= 0)
            {
                ticksUntilRescan = RescanIntervalTicks;
                Rebuild();
            }

            if (!RM_EnvironmentalHazardsSettings.waterAgitationEnabled)
            {
                return; // pools stay built (cheap, terrain-only) but nothing spawns
            }

            if (--ticksUntilLightRipple <= 0)
            {
                ticksUntilLightRipple = Rand.RangeInclusive(LightRippleMinTicks, LightRippleMaxTicks);
                TryRipple(lightCells, LightRippleSize);
            }

            if (--ticksUntilHeavyRipple <= 0)
            {
                ticksUntilHeavyRipple = Rand.RangeInclusive(HeavyRippleMinTicks, HeavyRippleMaxTicks);
                TryRipple(heavyCells, HeavyRippleSize);
            }
        }

        private void TryRipple(List<IntVec3> pool, float size)
        {
            if (pool.Count == 0)
            {
                return; // this map carries neither agitation tag — quiet no-op, matches the kit's own posture elsewhere
            }

            IntVec3 cell = pool[Rand.Range(0, pool.Count)];
            Vector3 loc = cell.ToVector3Shifted().WithY(AltitudeLayer.MoteLow.AltitudeFor());
            FleckMaker.WaterRipple(loc, map, size);
        }

        private void Rebuild()
        {
            lightCells.Clear();
            heavyCells.Clear();

            foreach (IntVec3 cell in map.AllCells)
            {
                TerrainDef terrain = map.terrainGrid.TerrainAt(cell);
                if (terrain?.tags == null)
                {
                    continue;
                }

                if (terrain.tags.Contains("RM_WaterAgitationHeavy"))
                {
                    heavyCells.Add(cell);
                }
                else if (terrain.tags.Contains("RM_WaterAgitationLight"))
                {
                    lightCells.Add(cell);
                }
            }
        }
    }
}
