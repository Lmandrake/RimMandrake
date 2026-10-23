using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CrackedLands
{
    // ════════════════════════════════════════════════════════════════════
    // CRACKEDLANDS_GPT_ENRICHMENT_1 §5 + §6 — WHAT THE RECEDE LEAVES BEHIND.
    //
    // Called once per flood by RM_MapComponent_CanyonFlood.RecedeFlood with
    // the wetted footprint (both halves: walled cells and FlowWorks-raised
    // cells). Owns two short-lived things, each with its own clock and its
    // own Mod Settings toggle. (A third, THE MIGRANT SKY -- this biome's own fliers
    // flying in to feed on the carpet and out at the dry -- was CUT 2026-10-23 by the fluff review,
    // design/RimMandrake/fluff_cuts_2026-10-23.md.)
    //
    //   THE IRQIT CARPET (§5)  a bounded cohort of RM_Irqit on the wetted
    //     cells, each carrying RM_IrqitFloodBorn (the readable sign: the
    //     health tab says what it is and that it dies at the dry). At the dry
    //     — the same soakDecayDays the ground stays soaked — every survivor
    //     dies where it stands; the corpses ARE the windrows. Nothing
    //     vanishes. The "breeds once" half needs no simulation: the next
    //     flood's cohort is that generation, hatched from the clay.
    //
    //   FLOODLINE SALVAGE (§6, the scatter half only)  a disciplined handful
    //     of half-buried industrial components and slag on the wetted cells,
    //     spawned forbidden. Whatever is still lying unclaimed where it was
    //     exposed when the clock runs out is taken back by the mud, with a
    //     message saying so. Claim stakes and the rival crew are a follow-up
    //     (CRACKEDLANDS_SALVAGE_CLAIM_CREW_1).
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_RecedeAftermath : MapComponent
    {
        private List<Pawn> cohort = new List<Pawn>();
        private int cohortDieTick = -1;

        private List<Thing> salvage = new List<Thing>();
        private List<IntVec3> salvageCells = new List<IntVec3>();
        private int salvageExpireTick = -1;

        public RM_MapComponent_RecedeAftermath(Map map) : base(map)
        {
        }

        // TUNED: one irqit per 8 wetted cells, capped by the setting — enough
        // to read as a carpet on a default flood (40–400 cells) without a
        // pawn-count spike. The "millions" are the art's job, not the tick's.

        // TUNED: 1–3 components + 1–3 slag chunks per flood — "loot tables need
        // discipline or the flood becomes a slot machine" (review §H).
        private static readonly IntRange ComponentCount = new IntRange(1, 3);
        private static readonly IntRange SlagCount = new IntRange(1, 3);

        public void OnRecede(List<IntVec3> wetted)
        {
            if (wetted == null || wetted.Count == 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            int dryTicks = RM_CanyonRulesKernel.DryTicks(RM_CrackedLandsSettings.soakDecayDays);

            if (RM_CrackedLandsSettings.recedeFeastEnabled)
            {
                SpawnCohort(wetted, now + dryTicks);
            }
            if (RM_CrackedLandsSettings.floodlineSalvageEnabled)
            {
                SpawnSalvage(wetted, now + RM_CanyonRulesKernel.SalvageTicks(RM_CrackedLandsSettings.salvageDecayDays));
            }
        }

        private static bool GoodGround(IntVec3 c, Map map)
        {
            return c.InBounds(map) && c.Standable(map) && !c.Fogged(map)
                && map.terrainGrid.TerrainAt(c) is TerrainDef t && !t.IsWater;
        }

        private void SpawnCohort(List<IntVec3> wetted, int dieTick)
        {
            PawnKindDef kind = RM_CrackedLandsDefOf.RM_Irqit;
            int want = RM_CanyonRulesKernel.CohortWant(RM_CrackedLandsSettings.irqitCohortMax, wetted.Count);
            if (kind == null || want <= 0)
            {
                return;
            }
            List<IntVec3> pool = wetted.FindAll(c => GoodGround(c, map));
            int spawned = 0;
            for (int i = 0; i < want && pool.Count > 0; i++)
            {
                IntVec3 c = pool.RandomElement();
                Pawn p = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(p, c, map);
                p.health.AddHediff(RM_CrackedLandsDefOf.RM_IrqitFloodBorn);
                cohort.Add(p);
                spawned++;
            }
            if (spawned > 0)
            {
                cohortDieTick = dieTick;
                Messages.Message(
                    "The flood-touched mud is moving: an irqit carpet has hatched in the wet clay. It will be gone by the time the ground dries.",
                    new LookTargets(cohort[cohort.Count - 1]), MessageTypeDefOf.NeutralEvent);
            }
        }

        private void SpawnSalvage(List<IntVec3> wetted, int expireTick)
        {
            List<IntVec3> pool = wetted.FindAll(c => GoodGround(c, map) && c.GetFirstItem(map) == null);
            if (pool.Count == 0)
            {
                return;
            }
            int nComp = ComponentCount.RandomInRange;
            int nSlag = SlagCount.RandomInRange;
            for (int i = 0; i < nComp + nSlag && pool.Count > 0; i++)
            {
                IntVec3 c = pool.RandomElement();
                pool.Remove(c);
                Thing t = ThingMaker.MakeThing(i < nComp ? ThingDefOf.ComponentIndustrial : ThingDefOf.ChunkSlagSteel);
                GenSpawn.Spawn(t, c, map);
                t.SetForbidden(true, false);
                salvage.Add(t);
                salvageCells.Add(c);
            }
            salvageExpireTick = expireTick;
            if (salvage.Count > 0)
            {
                Messages.Message(
                    "The receding water has scoured wreckage out of the mud along the flood line. Unclaimed, the mud will take it back.",
                    new LookTargets(salvage[0]), MessageTypeDefOf.PositiveEvent);
            }
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % 250 != 0)
            {
                return;
            }

            if (RM_CanyonRulesKernel.Due(cohortDieTick, now))
            {
                int died = 0;
                for (int i = 0; i < cohort.Count; i++)
                {
                    Pawn p = cohort[i];
                    if (p != null && p.Spawned && !p.Dead && p.Map == map)
                    {
                        p.Kill(null);
                        died++;
                    }
                }
                cohort.Clear();
                cohortDieTick = -1;
                if (died > 0)
                {
                    Messages.Message("The mud has stiffened. The irqit carpet has died where it stood, in windrows along the flood line.",
                        MessageTypeDefOf.NeutralEvent);
                }
            }

            if (RM_CanyonRulesKernel.Due(salvageExpireTick, now))
            {
                int taken = 0;
                int n = System.Math.Min(salvage.Count, salvageCells.Count);
                for (int i = 0; i < n; i++)
                {
                    Thing t = salvage[i];
                    // Only what still lies forbidden exactly where the mud
                    // exposed it — anything a pawn touched, claimed or moved
                    // is the player's now.
                    if (t != null && RM_CanyonRulesKernel.SalvageTaken(t.Spawned, t.Map == map, t.Position == salvageCells[i], t.IsForbidden(Faction.OfPlayer)))
                    {
                        t.Destroy(DestroyMode.Vanish);
                        taken++;
                    }
                }
                salvage.Clear();
                salvageCells.Clear();
                salvageExpireTick = -1;
                if (taken > 0)
                {
                    Messages.Message("The mud has taken back the floodline salvage nobody claimed.", MessageTypeDefOf.NeutralEvent);
                }
            }
        }

        public string DebugStateReport()
        {
            return string.Format("cohort={0} cohortDieTick={1} salvage={2} salvageExpireTick={3} now={4}",
                cohort.Count, cohortDieTick, salvage.Count, salvageExpireTick, Find.TickManager.TicksGame);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref cohort, "cohort", LookMode.Reference);
            Scribe_Values.Look(ref cohortDieTick, "cohortDieTick", -1);
            Scribe_Collections.Look(ref salvage, "salvage", LookMode.Reference);
            Scribe_Collections.Look(ref salvageCells, "salvageCells", LookMode.Value);
            Scribe_Values.Look(ref salvageExpireTick, "salvageExpireTick", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (cohort == null) cohort = new List<Pawn>();
                if (salvage == null) salvage = new List<Thing>();
                if (salvageCells == null) salvageCells = new List<IntVec3>();
                cohort.RemoveAll(p => p == null);
                // Keep the two salvage lists aligned if a reference failed to
                // resolve (the thing was destroyed): drop the pair.
                for (int i = System.Math.Min(salvage.Count, salvageCells.Count) - 1; i >= 0; i--)
                {
                    if (salvage[i] == null)
                    {
                        salvage.RemoveAt(i);
                        salvageCells.RemoveAt(i);
                    }
                }
            }
        }
    }
}
