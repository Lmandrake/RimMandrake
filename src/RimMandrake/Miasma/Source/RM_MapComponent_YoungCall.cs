using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Miasma
{
    // MIASMA_YOUNG_CALL_1: the cry itself is the shared RM_HediffComp_LocatableCall on RUT_StrandedDeformation
    // (any spawned stranded young calls, penned or not). This adds the rest of fauna roster section 6 steps 3-4:
    //  - a one-time letter per map, pointing at the first crying young, so the cry is locatable;
    //  - the nearest living warden mother is sent to the water cell nearest the young. She never goes onto dry land:
    //    the target is always a water cell, and RM_CompWaterLocked stops her if anything pulls her out.
    // "Its mother" is the nearest warden mother on the map (the crèche ledger's mother field is private).
    public class RM_MapComponent_YoungCall : MapComponent
    {
        private const string StrandedHediff = "RUT_StrandedDeformation";
        private const int PollTicks = 250;
        private const float MaxMotherDist = 60f;
        private const int SearchRadius = 30;
        private bool letterSent;

        public RM_MapComponent_YoungCall(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % PollTicks != 0) return;
            if (!RM_MiasmaSettings.youngCallEnabled || map.Biome == null || map.Biome.defName != "RM_Miasma") return;

            HediffDef hd = DefDatabase<HediffDef>.GetNamedSilentFail(StrandedHediff);
            if (hd == null) return;

            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            Pawn young = null;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.health?.hediffSet == null || !p.health.hediffSet.HasHediff(hd)) continue;
                young = p;
                if (!letterSent && p.Faction != Faction.OfPlayer)
                {
                    letterSent = true;
                    Find.LetterStack.ReceiveLetter("RM_YoungCallLetterLabel".Translate(),
                        "RM_YoungCallLetterText".Translate(p.LabelShort), LetterDefOf.NeutralEvent, p);
                }
                SummonMother(p);
            }
        }

        private void SummonMother(Pawn young)
        {
            Pawn mother = null;
            float best = MaxMotherDist * MaxMotherDist;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.kindDef == null || p.kindDef.defName != "RM_WardenMother" || p.Dead || p.Downed) continue;
                if (p.Faction == Faction.OfPlayer) continue;
                float d = (p.Position - young.Position).LengthHorizontalSquared;
                if (d < best) { best = d; mother = p; }
            }
            if (mother == null) return;

            IntVec3 target = NearestWaterCell(young.Position, mother);
            if (!target.IsValid || mother.Position == target) return;
            Job cur = mother.CurJob;
            if (cur != null && cur.def == JobDefOf.Goto && cur.targetA.Cell == target) return;
            Job job = JobMaker.MakeJob(JobDefOf.Goto, target);
            job.expiryInterval = 600;
            job.checkOverrideOnExpire = true;
            mother.jobs.StartJob(job, JobCondition.InterruptForced);
        }

        public static IntVec3 NearestWaterCell(IntVec3 from, Pawn mother)
        {
            Map map = mother.Map;
            IntVec3 best = IntVec3.Invalid;
            float bestD = float.MaxValue;
            int n = GenRadial.NumCellsInRadius(SearchRadius);
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = from + GenRadial.RadialPattern[i];
                if (!c.InBounds(map)) continue;
                if (map.terrainGrid.TerrainAt(c) == null || !map.terrainGrid.TerrainAt(c).IsWater) continue;
                float d = (c - from).LengthHorizontalSquared;
                if (d >= bestD) continue;
                if (!mother.CanReach(c, PathEndMode.OnCell, Danger.Deadly)) continue;
                bestD = d;
                best = c;
                break; // RadialPattern is ordered by distance
            }
            return best;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref letterSent, "letterSent", false);
        }
    }
}
