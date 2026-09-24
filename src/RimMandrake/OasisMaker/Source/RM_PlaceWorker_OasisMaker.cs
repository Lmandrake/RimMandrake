using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.OasisMaker
{
    /// <summary>
    /// OASIS_MAKER_BUILD_1 §3, "the honest hard part": the projected
    /// footprint painted while the ghost is held is a per-cell function of
    /// the GHOST POSITION — recomputed from RM_OasisPlacementScorer every
    /// call to DrawGhost (which the game calls every frame the ghost is
    /// shown, following the current mouse cell) — not a static radius like
    /// most vanilla PlaceWorkers paint. The projected radius itself is the
    /// SAME quality->radiusCap mapping RM_CompOasisMaker locks in at
    /// Attuning->Working, so what the player sees while placing is exactly
    /// the oasis they would get if they placed here and let it finish.
    ///
    /// Pattern: vanilla RimWorld/PlaceWorker_WatermillGenerator.cs (DrawGhost
    /// override, GenDraw.DrawFieldEdges for cell-set painting, red/green from
    /// Designator_Place.Can/CannotPlaceColor) — read from the decompile
    /// 2026-09-24. Our own precedent for a validity-refusing PlaceWorker:
    /// src/RimMandrake/EnvironmentalHazards/Source/RM_PlaceWorker_OnRequiredVentComp.cs.
    /// </summary>
    public class RM_PlaceWorker_OasisMaker : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            if (!RM_OasisMakerSettings.masterEnabled)
            {
                return true; // disabled mechanic never blocks a placement
            }
            RM_OasisPlacementScorer.Score score = RM_OasisPlacementScorer.ScoreAt(map, CenterCellFor(checkingDef, loc, rot));
            if (score.MeetsFloor())
            {
                return true;
            }
            bool needsShade = score.shade < RM_OasisMakerSettings.shadeScoreFloor;
            bool needsRock = score.rock < RM_OasisMakerSettings.rockScoreFloor;
            if (needsShade && needsRock)
            {
                return "RM_OasisMaker_NeedsBoth".Translate();
            }
            return needsShade ? "RM_OasisMaker_NeedsShade".Translate() : "RM_OasisMaker_NeedsRock".Translate();
        }

        public override void DrawGhost(ThingDef def, IntVec3 loc, Rot4 rot, Color ghostCol, Thing thing = null)
        {
            Map map = Find.CurrentMap;
            if (map == null || !RM_OasisMakerSettings.masterEnabled)
            {
                return;
            }
            IntVec3 center = CenterCellFor(def, loc, rot);
            RM_OasisPlacementScorer.Score score = RM_OasisPlacementScorer.ScoreAt(map, center);
            bool meetsFloor = score.MeetsFloor();

            // Cyan/edge tint on the contributing shade and rock cells — "so
            // the player learns WHY a spot is good" (§3).
            GenDraw.DrawFieldEdges(RM_OasisPlacementScorer.ContributingCells(map, center, shade: true).ToList(),
                new Color(0.3f, 0.9f, 1f, 0.6f));
            GenDraw.DrawFieldEdges(RM_OasisPlacementScorer.ContributingCells(map, center, shade: false).ToList(),
                new Color(1f, 0.85f, 0.3f, 0.6f));

            // The projected footprint itself — green sized/paced by the
            // quality THIS cell would earn, red at the hard-floor radius
            // when the spot fails it. This is the live, per-cell-recomputed
            // preview the spec calls out as the actual design.
            int radius;
            Color fieldColor;
            if (meetsFloor)
            {
                float quality = score.Quality01();
                radius = Mathf.RoundToInt(Mathf.Lerp(
                    RM_OasisMakerSettings.minRadiusCap, RM_OasisMakerSettings.maxRadiusCap, quality));
                fieldColor = Designator_Place.CanPlaceColor.ToOpaque();
            }
            else
            {
                radius = RM_OasisMakerSettings.minRadiusCap;
                fieldColor = Designator_Place.CannotPlaceColor.ToOpaque();
            }
            GenDraw.DrawFieldEdges(ProjectedFootprint(map, center, radius), fieldColor);
        }

        private static IntVec3 CenterCellFor(BuildableDef def, IntVec3 loc, Rot4 rot)
        {
            ThingDef td = def as ThingDef;
            if (td == null)
            {
                return loc;
            }
            // Mirrors ThingDef.OccupiedRect logic for a not-yet-spawned ghost:
            // GenAdj gives the footprint rect for a size/rotation at a corner
            // position, and CellRect.CenterCell does the rounding.
            return GenAdj.OccupiedRect(loc, rot, td.Size).CenterCell;
        }

        private static List<IntVec3> ProjectedFootprint(Map map, IntVec3 center, int radius)
        {
            List<IntVec3> cells = new List<IntVec3>();
            for (int dz = -radius; dz <= radius; dz++)
            {
                for (int dx = -radius; dx <= radius; dx++)
                {
                    if (System.Math.Max(System.Math.Abs(dx), System.Math.Abs(dz)) != radius)
                    {
                        continue; // outline only, not a filled field
                    }
                    IntVec3 cell = new IntVec3(center.x + dx, center.y, center.z + dz);
                    if (cell.InBounds(map))
                    {
                        cells.Add(cell);
                    }
                }
            }
            return cells;
        }
    }
}
