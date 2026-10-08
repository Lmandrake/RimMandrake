using System.Collections.Generic;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using Verse;

namespace RimMandrake.Warcasket
{
    // WARCASKET_SUIT_CLASS_1 — the terrain-survival half of the ruling:
    // "ocean access [is] TERRAIN survival (sea floors stay ship-only)".
    //
    // GENERAL, not warcasket-specific: this scans every map for every
    // spawned apparel-capable pawn, the same shape RM_GameCondition_
    // WetBulb.RampMap already uses in this repo (EnvironmentalHazards),
    // and applies/heals RM_TerrainImmersionHazard based on the pawn's
    // SUMMED RM_HazardousTerrainProtection apparel stat — ANY apparel
    // that carries the stat helps, not only a warcasket. Reuses
    // HazardTargeting.SumApparelStat/ProtectionDriveFactor (this mod
    // declares mandrake.rm.environmentalhazards as a hard dependency and
    // compiles against its assembly, same pattern RM_FloodedCanyon uses
    // for RimMandrake:FlowWorks) rather than reimplementing that math a
    // third time.
    //
    // HAZARD SCOPE, DELIBERATE: only water/terrain a pawn CANNOT simply
    // walk across (TerrainDef.IsWater && no Walkable affordance — vanilla's
    // own "must swim" deep/moving-deep water, and this repo's matching
    // ToxicWaterDeepBase/ToxicWaterChestDeepBase-derived brine, e.g.
    // RM_WastelandBrineDeep/RM_WastelandBrineMovingChestDeep) counts as
    // hazardous. An ordinary shallow ford, marsh edge or shallow brine
    // margin (ToxicWaterShallowBase-derived, Walkable) is NOT — every
    // biome already has pawns cross those freely, and turning that into a
    // lethal clock would be a severe, unintended balance change far
    // outside this item's scope. This is also exactly the line the
    // ruling draws: a warcasket (or any suit carrying this stat) lets a
    // wearer stand at the edge or wade the margins of a hostile sea; it
    // never lets them survive, let alone reach, the deep floor beneath
    // one — and even surviving the deep grants no sea-floor ACCESS. A
    // sea floor stays reachable only through a gravship's own
    // RM_SeaDiveHatch (DivingInteraction) — this component adds no verb,
    // no MapPortal, no teleport of any kind, only a survivability check
    // against standing/wading through open deep water.
    public class RM_MapComponent_HazardousTerrainImmersion : MapComponent
    {
        private const int CheckIntervalTicks = RM_WarcasketKernel.ImmersionCheckInterval;
        private const float MinDriveFactor = RM_WarcasketKernel.MinDriveFactor;

        private int ticksUntilCheck = CheckIntervalTicks;

        public RM_MapComponent_HazardousTerrainImmersion(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_WarcasketKernel.ImmersionActive(RM_WarcasketSettings.masterEnabled, RM_WarcasketSettings.terrainImmersionEnabled))
            {
                return;
            }

            if (!RM_WarcasketKernel.CheckDue(ref ticksUntilCheck))
            {
                return;
            }

            // Snapshot: HealthUtility.AdjustSeverity can, in principle,
            // trigger death and mutate the live pawn list — same caution
            // this repo's own GameCondition_EnvironmentalWeather/
            // RM_GameCondition_WetBulb already take.
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                ProcessPawn(pawns[i]);
            }
        }

        private void ProcessPawn(Pawn pawn)
        {
            if (!HazardTargeting.Affects(pawn, PawnTargetKind.Flesh, null, null))
            {
                return;
            }

            if (pawn.apparel == null)
            {
                return; // no apparel tracker: nothing here can ever protect or endanger it further than vanilla already does
            }

            bool hazardous = IsHazardousCell(pawn.Position);
            bool hasHediff = pawn.health.hediffSet.HasHediff(RM_WarcasketDefOf.RM_TerrainImmersionHazard);

            float driveFactor = 1f;
            if (hazardous)
            {
                float protection = HazardTargeting.SumApparelStat(pawn, RM_WarcasketDefOf.RM_HazardousTerrainProtection);
                driveFactor = HazardTargeting.ProtectionDriveFactor(protection, MinDriveFactor, 0f);
            }

            // Clear ground heals fast; gear that holds the clock heals slowly (nothing to apply); otherwise the clock gains.
            float delta = RM_WarcasketKernel.ImmersionDelta(hazardous, hasHediff, driveFactor);
            if (delta == 0f || (delta > 0f && pawn.Dead))
            {
                return;
            }

            HealthUtility.AdjustSeverity(pawn, RM_WarcasketDefOf.RM_TerrainImmersionHazard, delta);
        }

        private bool IsHazardousCell(IntVec3 cell)
        {
            if (!cell.InBounds(map))
            {
                return false;
            }

            TerrainDef terrain = map.terrainGrid.TerrainAt(cell);

            // Walkable water (a ford, a shallow brine margin) is ordinary
            // terrain, never the hazard — see file header.
            return RM_WarcasketKernel.HazardousCell(true, terrain != null, terrain != null && terrain.IsWater,
                terrain != null && terrain.affordances != null,
                terrain != null && terrain.affordances != null && terrain.affordances.Contains(TerrainAffordanceDefOf.Walkable));
        }
    }
}
