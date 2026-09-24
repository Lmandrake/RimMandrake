using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // WATER_TRUCE_RETRIBUTION_1 (caused_by WEEPING_STONES_DESIGN_SITTING_1).
    // "First GUILTY hit in truce radius turns wildlife on the aggressor
    // faction; engine attribution MEASURED (DamageInfo.InstigatorGuilty) —
    // no dont-fight-back needed." §6 ambush ban intact: this fires on
    // VIOLENCE landing at the water, never on ordinary predation — nothing
    // here touches hunting AI or spawns anything.
    //
    // Ships the RETRIBUTION half only. The SUPPRESSION half (a stocked-pool
    // predator never hunts near truce water — weeping_stones_fauna_roster_
    // 2026-09-24.md row §2f, "truce v1... side effect included") is a
    // separate owed build (candidate shape already noted there: invert
    // RM_MapComponent_DreadField + RM_JobGiver_DreadAvoidWander). This
    // component's field is deliberately public via IsTruceWater so that
    // future work can read the identical radius rather than re-deriving it.
    //
    // Only active on a map whose BiomeDef carries RM_WaterTruceExtension —
    // every other map's Notify_GuiltyHitInTruce call is a single null check
    // and nothing else runs. Terrain is scanned ONCE, at FinalizeInit: pools
    // are hand-placed landmark terrain that does not move over a map's
    // lifetime in the shipped campaign (OASIS_LANDMARK_PLACEMENT_1, CLOSED),
    // so a live rescan on every dig/flood is not owed for v1 — Rebuild() is
    // exposed publicly for whoever eventually wires a terrain-change hook.
    public class RM_MapComponent_WaterTruce : MapComponent
    {
        // INVENTED — no owner-ruled number. Minimum real-world gap between
        // two retributions triggered by the SAME aggressor faction on this
        // map, so a raid landing a dozen guilty hits in the truce radius
        // rings the alarm once, not a dozen times. Re-arms automatically
        // once the cooldown elapses; not Scribe-saved (same posture as
        // RM_MapComponent_DreadField's own field — cheap to rebuild, not
        // worth a save-format entry, and re-arming one cooldown early after
        // a reload is a harmless v1 corner, never a silent loss of state
        // that matters).
        private const int RetributionCooldownTicks = 2500;

        private readonly RM_WaterTruceExtension extension;

        private bool[] field;

        private readonly Dictionary<Faction, int> lastRetributionTick = new Dictionary<Faction, int>();

        public RM_MapComponent_WaterTruce(Map map)
            : base(map)
        {
            extension = map.Biome?.GetModExtension<RM_WaterTruceExtension>();
        }

        public bool Active => extension != null;

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Rebuild();
        }

        public bool IsTruceWater(IntVec3 cell)
        {
            if (field == null || !cell.InBounds(map))
            {
                return false;
            }

            return field[map.cellIndices.CellToIndex(cell)];
        }

        public void Rebuild()
        {
            if (extension == null)
            {
                field = null;
                return;
            }

            int n = map.cellIndices.NumGridCells;
            bool[] painted = new bool[n];

            foreach (IntVec3 waterCell in map.AllCells)
            {
                TerrainDef terrain = map.terrainGrid.TerrainAt(waterCell);
                if (terrain == null || !terrain.IsWater)
                {
                    continue;
                }

                foreach (IntVec3 cell in GenRadial.RadialCellsAround(waterCell, extension.radius, useCenter: true))
                {
                    if (cell.InBounds(map))
                    {
                        painted[map.cellIndices.CellToIndex(cell)] = true;
                    }
                }
            }

            field = painted;
        }

        // Called from a Harmony postfix on Thing.PostApplyDamage for every
        // hit landing anywhere in the game — bails in three field reads on
        // every map that never opts in, which is the overwhelming majority.
        public void Notify_GuiltyHitInTruce(DamageInfo dinfo, Thing victim, float totalDamageDealt)
        {
            if (!Active || !RM_EnvironmentalHazardsSettings.waterTruceRetributionEnabled)
            {
                return;
            }

            if (totalDamageDealt <= 0f || !dinfo.InstigatorGuilty)
            {
                return;
            }

            Thing instigator = dinfo.Instigator;
            Faction aggressor = instigator?.Faction;
            if (instigator == null || aggressor == null || victim == null)
            {
                return; // no faction to hold accountable — nothing for the water to answer against
            }

            if (!victim.Spawned || victim.Map != map || !IsTruceWater(victim.Position))
            {
                return; // the hit did not land at the water
            }

            if (lastRetributionTick.TryGetValue(aggressor, out int lastTick)
                && Find.TickManager.TicksGame - lastTick < RetributionCooldownTicks)
            {
                return; // already answered this aggressor recently — first hit, not every hit
            }

            lastRetributionTick[aggressor] = Find.TickManager.TicksGame;
            Retaliate(instigator, aggressor);
        }

        private void Retaliate(Thing instigator, Faction aggressor)
        {
            MentalStateDef stateDef = RM_MentalStateDefOf.RM_WaterTruceRetribution;
            if (stateDef == null)
            {
                return;
            }

            int roused = 0;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn.Faction != null || pawn.Dead || pawn.Downed || !pawn.RaceProps.Animal)
                {
                    continue; // wildlife only — a player-tamed or another faction's animal never flips here
                }

                if (!IsTruceWater(pawn.Position))
                {
                    continue; // same radius as the hit itself — the biome, not the whole map, answers
                }

                if (pawn.InMentalState)
                {
                    continue; // already manhunting, fleeing, etc. — leave whatever it is doing alone
                }

                if (pawn.mindState.mentalStateHandler.TryStartMentalState(stateDef, null, forced: true, forceWake: true,
                        causedByMood: false, otherPawn: instigator as Pawn, transitionSilently: true, causedByDamage: true))
                {
                    if (pawn.MentalState is RM_MentalState_WaterTruceRetribution retribution)
                    {
                        retribution.targetFaction = aggressor;
                    }

                    roused++;
                }
            }

            if (roused <= 0)
            {
                return;
            }

            Find.LetterStack.ReceiveLetter(
                "RM_WaterTruceRetributionLetterLabel".Translate(),
                "RM_WaterTruceRetributionLetterText".Translate(aggressor.Name, roused),
                LetterDefOf.NeutralEvent,
                new LookTargets(instigator));
        }
    }

    [DefOf]
    public static class RM_MentalStateDefOf
    {
        public static MentalStateDef RM_WaterTruceRetribution;

        static RM_MentalStateDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_MentalStateDefOf));
        }
    }
}
