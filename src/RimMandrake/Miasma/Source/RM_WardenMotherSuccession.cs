using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Miasma
{
    //   <li Class="RimMandrake.Miasma.RM_HediffCompProperties_SelfTameOnRecord">
    //     <checkIntervalTicksRange>2000~3200</checkIntervalTicksRange>
    //   </li>
    //
    // WARDEN_MOTHER_SUCCESSION_1 pieces 1+2 (design:
    // design/Jawa/worldbuilding/biomes/miasma_fauna_roster_2026-09-23.md §6a,
    // owner: "the babies should be trainable... they should frequently
    // self-tame if there are no hostilities against them"). Same consent
    // pattern as the mother's own tolerance (WARDEN_MOTHER_BEFRIENDING_1) —
    // never a taming grind, never commanded into it.
    //
    // Scoped to carriers of RUT_StrandedDeformation only. The roster's own
    // alternate population ("or on the plain nursery juvenile species once
    // rescued") is NOT built here: there is no engine signal that reliably
    // means "rescued" for a plain wild juvenile without inventing one the
    // roster never specified, so that half is left for a follow-on rather
    // than guessed at.
    //
    // Deliberately holds NO reference to mandrake.rm.environmentalhazards —
    // see RM_CompCrecheYoungLedger's own header (below, same file) for why.
    // The water-scope check re-implements RM_CompWaterLocked's own one-line
    // terrain test rather than calling that shared class, which keeps this
    // whole file dependency-free of an assembly several other seats are
    // concurrently editing this session (CreatureBehaviors/FeverWood/
    // EnvironmentalHazards/Greentide).
    public class RM_HediffCompProperties_SelfTameOnRecord : HediffCompProperties
    {
        public IntRange checkIntervalTicksRange = new IntRange(2000, 3200);

        public float crecheSearchRadius = 24f;

        // Water-scoped enforcement cadence once self-tamed. §6a: "Guard...
        // Release/Attack in water, and Haul-from-water-only... not Rescue
        // and not general Haul." Rescue/Haul are hidden from the training
        // tab by RM_Patch_WardenYoungTrainableGate.cs; the backstop below
        // (interrupt any job the moment she's found off water) still guards
        // every other trained job.
        public int waterCheckIntervalTicks = 60;

        public RM_HediffCompProperties_SelfTameOnRecord()
        {
            compClass = typeof(RM_HediffComp_SelfTameOnRecord);
        }
    }

    public class RM_HediffComp_SelfTameOnRecord : HediffComp
    {
        private int nextCheckTick = -1;
        private bool selfTamed;
        private Thing crecheMarker;

        public RM_HediffCompProperties_SelfTameOnRecord Props =>
            (RM_HediffCompProperties_SelfTameOnRecord)props;

        /// <summary>MIASMA_MOTHERS_PRICE_1: the crèche this young registered with (null until it found one).</summary>
        public Thing CrecheMarker => crecheMarker;

        public override void CompPostTick(ref float severityAdjustment)
        {
            base.CompPostTick(ref severityAdjustment);

            Pawn pawn = parent.pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Map == null)
            {
                return;
            }

            if (selfTamed || pawn.Faction == Faction.OfPlayer)
            {
                selfTamed = true;
                EnforceWaterScope(pawn);
                return;
            }

            if (crecheMarker == null || crecheMarker.Destroyed)
            {
                crecheMarker = FindNearestCrecheMarker(pawn);
                if (crecheMarker != null)
                {
                    crecheMarker.TryGetComp<RM_CompCrecheYoungLedger>()?.RegisterYoung(pawn);
                }
            }

            // the timer (schedule, option, broken record bars it, the chance) is RM_MiasmaKernel.SelfTameStep, offline-fuzzed
            RM_CompCrecheYoungLedger crecheLedger = crecheMarker?.TryGetComp<RM_CompCrecheYoungLedger>();
            if (RM_MiasmaKernel.SelfTameStep(ref nextCheckTick, Find.TickManager.TicksGame, () => Props.checkIntervalTicksRange.RandomInRange,
                    RM_MiasmaSettings.wardenSuccessionEnabled, crecheLedger != null, crecheLedger != null && crecheLedger.RecordClean,
                    () => Rand.Chance(RM_MiasmaSettings.selfTameChancePerCheck)))
            {
                SelfTame(pawn);
            }
        }

        private void SelfTame(Pawn pawn)
        {
            selfTamed = true;
            pawn.SetFaction(Faction.OfPlayer);
            pawn.training?.Train(TrainableDefOf.Tameness, null, complete: true);
            Messages.Message(
                "RUT_WardenYoungSelfTamed".Translate(pawn.LabelShort),
                pawn,
                MessageTypeDefOf.PositiveEvent);
        }

        // WARDEN_MOTHER_SUCCESSION_1 piece 2's backstop — same reasoning as
        // RM_CompWaterLocked.cs's own header (EnvironmentalHazards), applied
        // here as a plain terrain check rather than a shared reference: stop
        // any in-progress job dead the moment she's found off water, rather
        // than let her keep executing a trained behaviour (Guard/Attack/
        // Haul) she cannot finish on land.
        private void EnforceWaterScope(Pawn pawn)
        {
            if (!pawn.IsHashIntervalTick(Props.waterCheckIntervalTicks))
            {
                return;
            }

            if (IsWaterCell(pawn.Position, pawn.Map))
            {
                return;
            }

            pawn.pather?.StopDead();
            if (pawn.jobs?.curJob != null)
            {
                pawn.jobs.EndCurrentJob(JobCondition.InterruptForced, startNewJob: false);
            }
        }

        private static bool IsWaterCell(IntVec3 cell, Map map)
        {
            if (map == null || !cell.InBounds(map))
            {
                return false;
            }

            TerrainDef terrain = map.terrainGrid.TerrainAt(cell);
            return terrain != null && terrain.IsWater;
        }

        private Thing FindNearestCrecheMarker(Pawn pawn)
        {
            ThingDef markerDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_CrecheMarker");
            if (markerDef == null)
            {
                return null;
            }

            List<Thing> markers = pawn.Map.listerThings.ThingsOfDef(markerDef);
            var distSq = new List<float>(markers.Count);
            for (int i = 0; i < markers.Count; i++) distSq.Add((markers[i].Position - pawn.Position).LengthHorizontalSquared);
            int nearest = RM_MiasmaKernel.NearestFirstInclusive(distSq, Props.crecheSearchRadius * Props.crecheSearchRadius);
            return nearest >= 0 ? markers[nearest] : null;
        }

        public override void Notify_PawnPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.Notify_PawnPostApplyDamage(dinfo, totalDamageDealt);

            if (crecheMarker == null)
            {
                return;
            }

            if (!(dinfo.Instigator is Pawn instigator) || instigator.Faction != Faction.OfPlayer)
            {
                return;
            }

            crecheMarker.TryGetComp<RM_CompCrecheYoungLedger>()?.BreakRecord();
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref nextCheckTick, "nextCheckTick", -1);
            Scribe_Values.Look(ref selfTamed, "selfTamed", false);
            Scribe_References.Look(ref crecheMarker, "crecheMarker");
        }
    }

    //   <li Class="RimMandrake.Miasma.CompProperties_CrecheYoungLedger">
    //     <pollIntervalTicks>600</pollIntervalTicks>
    //   </li>
    //
    // WARDEN_MOTHER_SUCCESSION_1 piece 3: succession on the warden mother's
    // death. Lives on RUT_CrecheMarker (the permanent site identity)
    // alongside the existing despoiled-memory comp (RM_CompCrecheMarker,
    // RimMandrake.EnvironmentalHazards) — a sibling, not a replacement; that
    // comp is untouched by this item.
    //
    // Detects the mother's death by POLLING Pawn.Dead on a cached reference,
    // rather than via RM_CompTerritorialAnchor's own IRM_AnchorDeathListener
    // push (RimMandrake.EnvironmentalHazards, used today only by
    // RM_CompCrecheMarker's despoiled-memory mechanic). Deliberately, for
    // two reasons:
    //   1. This item's own "Watch out" flags that whether an old-age death
    //      actually routes through Pawn.Kill() (and therefore fires
    //      ThingComp.Notify_Killed at all) is UNCONFIRMED from this machine
    //      — RimSage/the decompile are Windows-Desktop-only (CLAUDE.md) and
    //      this session runs off it. Pawn.Dead is the terminal state flag
    //      regardless of which internal path set it, so polling it is
    //      correct succession-detection even if that routing question
    //      answers "no" for natural old age specifically — filed as
    //      WARDEN_MOTHER_OLDAGE_KILL_ROUTE_VERIFY_1 (mirroring the parent's
    //      own WARDEN_MOTHER_PATHFINDER_VERIFY_1) rather than guessed at
    //      here. A ~600-tick poll latency is immaterial to a succession
    //      beat.
    //   2. It keeps this file's own new mechanism dependency-free of
    //      mandrake.rm.environmentalhazards's assembly — several other
    //      seats are concurrently editing that exact project this session.
    //
    // Also carries the "clean record" ledger piece 1 reads — one shared
    // per-creche bookkeeping comp rather than two, since both need "which
    // young belong to this creche."
    public class CompProperties_CrecheYoungLedger : CompProperties
    {
        public int pollIntervalTicks = 600;

        public float motherSearchRadius = 20f;

        public CompProperties_CrecheYoungLedger()
        {
            compClass = typeof(RM_CompCrecheYoungLedger);
        }
    }

    public class RM_CompCrecheYoungLedger : ThingComp
    {
        // The bookkeeping (young list, clean record, betrayal, one succession attempt, the heir) is RM_MiasmaKernel.CrecheLedger,
        // offline-fuzzed; this comp keeps the mother reference, the sold label and the engine reads. Scribed field for field below.
        private readonly RM_MiasmaKernel.CrecheLedger<Pawn> ledger = new RM_MiasmaKernel.CrecheLedger<Pawn>();
        private Pawn motherPawn;
        private string soldLabel;

        public CompProperties_CrecheYoungLedger Props => (CompProperties_CrecheYoungLedger)props;

        public bool RecordClean => ledger.recordClean;

        /// <summary>MIASMA_MOTHERS_PRICE_1: one of this crèche's young was sold.</summary>
        public bool Betrayed => ledger.betrayed;

        public int ReturnedCount => ledger.returnedCount;

        public bool SuccessionVoid => ledger.betrayed;

        /// <summary>A sale: self-taming barred for good, succession void, the mother's tolerance revoked (the caller
        /// does that through RM_MothersPrice, which reaches the shared assembly's anchor comp).</summary>
        public void Betray(Pawn sold)
        {
            ledger.Betray();
            soldLabel = sold?.LabelShort ?? soldLabel;
        }

        public void NoteReturned(Pawn young)
        {
            ledger.NoteReturned(young);
        }

        public int YoungOwed =>
            ledger.YoungOwed(p => !p.Dead && !p.Destroyed && p.Faction != Faction.OfPlayer);

        public Pawn MotherNow()
        {
            if (motherPawn == null || motherPawn.Destroyed)
            {
                motherPawn = FindNearestWardenMother();
            }
            return motherPawn;
        }

        public void RegisterYoung(Pawn p)
        {
            ledger.Register(p);
        }

        public void BreakRecord()
        {
            ledger.BreakRecord();
        }

        public override void CompTick()
        {
            base.CompTick();

            if (!ledger.PollDue(RM_MiasmaSettings.wardenSuccessionEnabled))
            {
                return;
            }

            if (!parent.IsHashIntervalTick(System.Math.Max(1, Props.pollIntervalTicks)))
            {
                return;
            }

            if (motherPawn == null || motherPawn.Destroyed)
            {
                motherPawn = FindNearestWardenMother();
            }

            if (motherPawn != null && motherPawn.Dead)
            {
                TryPromoteSuccessor();
            }
        }

        private Pawn FindNearestWardenMother()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return null;
            }

            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            float radiusSq = Props.motherSearchRadius * Props.motherSearchRadius;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.kindDef == null || p.kindDef.defName != "RM_WardenMother")
                {
                    continue;
                }

                float distSq = (p.Position - parent.Position).LengthHorizontalSquared;
                if (distSq <= radiusSq)
                {
                    return p; // one warden mother per creche site by construction (RUT_GenStep_CrecheScatterer)
                }
            }

            return null;
        }

        private void TryPromoteSuccessor()
        {
            Pawn chosen = ledger.TryPromote(p => !p.Dead && !p.Destroyed && p.Faction == Faction.OfPlayer);   // one attempt per creche, ever

            if (chosen == null)
            {
                return; // no clean self-tamed young survives her — "the crèche is just a place" per the roster's own "not guaranteed"
            }

            Messages.Message(
                "RUT_WardenSuccessionMessage".Translate(chosen.LabelShort),
                chosen,
                MessageTypeDefOf.PositiveEvent);
        }

        public override string CompInspectStringExtra()
        {
            // MIASMA_MOTHERS_PRICE_1: her ledger, readable.
            var lines = new List<string>();
            if (ledger.heir != null && !ledger.heir.Destroyed)
            {
                lines.Add("RUT_CrecheMarkerHeir".Translate(ledger.heir.LabelShort));
            }
            lines.Add("Young she is owed: " + YoungOwed + (ledger.returnedCount > 0 ? "; brought back to her: " + ledger.returnedCount : ""));
            if (ledger.betrayed)
            {
                lines.Add("Sold" + (soldLabel.NullOrEmpty() ? "" : ": " + soldLabel) + ". The crèche remembers: she will never tolerate you, and none of her young will be yours.");
            }
            return string.Join("\n", lines);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref ledger.young, "registeredYoung", LookMode.Reference);
            Scribe_Values.Look(ref ledger.recordClean, "recordClean", true);
            Scribe_References.Look(ref motherPawn, "motherPawn");
            Scribe_References.Look(ref ledger.heir, "heirPawn");
            Scribe_Values.Look(ref ledger.successionDone, "successionDone", false);
            Scribe_Values.Look(ref ledger.betrayed, "betrayed", false);
            Scribe_Values.Look(ref ledger.returnedCount, "returnedCount", 0);
            Scribe_Values.Look(ref soldLabel, "soldLabel");

            if (Scribe.mode == LoadSaveMode.PostLoadInit && ledger.young == null)
            {
                ledger.young = new List<Pawn>();
            }
        }
    }
}
