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
        // and not general Haul." This comp cannot grey the two excluded
        // TrainableDefs out of the training UI itself without a Harmony
        // patch on an engine method this pass could not verify offline
        // (RimSage is unreachable from this machine, CLAUDE.md) — the
        // backstop below (interrupt any job the moment she's found off
        // water) is what ships now; hard-excluding Rescue/Haul from the
        // training tab is filed as WARDEN_MOTHER_TRAINABLE_GATE_1.
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

            int tick = Find.TickManager.TicksGame;
            if (nextCheckTick < 0)
            {
                nextCheckTick = tick + Props.checkIntervalTicksRange.RandomInRange;
                return;
            }

            if (tick < nextCheckTick)
            {
                return;
            }

            nextCheckTick = tick + Props.checkIntervalTicksRange.RandomInRange;

            if (!RM_MiasmaSettings.wardenSuccessionEnabled)
            {
                return;
            }

            RM_CompCrecheYoungLedger ledger = crecheMarker?.TryGetComp<RM_CompCrecheYoungLedger>();
            if (ledger != null && !ledger.RecordClean)
            {
                return; // barred: the player has harmed one of this creche's young
            }

            if (Rand.Chance(RM_MiasmaSettings.selfTameChancePerCheck))
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
            Thing nearest = null;
            float nearestDistSq = Props.crecheSearchRadius * Props.crecheSearchRadius;
            float bestDistSq = float.MaxValue;
            for (int i = 0; i < markers.Count; i++)
            {
                float distSq = (markers[i].Position - pawn.Position).LengthHorizontalSquared;
                if (distSq <= nearestDistSq && distSq < bestDistSq)
                {
                    nearest = markers[i];
                    bestDistSq = distSq;
                }
            }

            return nearest;
        }

        // "harmed" per the roster's own deferred-work note
        // (WARDEN_MOTHER_BEFRIENDING_1): the player harming ANY of this
        // creche's young bars self-taming for the rest of it, not just the
        // one hurt. HediffComp.Notify_PawnPostApplyDamage(DamageInfo,float)
        // is the real signature — MEASURED via reflection against the
        // installed game's Assembly-CSharp.dll this pass (an earlier attempt
        // at this file guessed HediffComp.Notify_PawnDied(DamageInfo?) and
        // it does not exist with that signature; the actual method takes a
        // second Hediff culprit parameter and only fires on a death that
        // hediff caused, so PostApplyDamage — firing on ANY damage, lethal
        // or not — is the correct, more literal match for "harmed" anyway).
        // "Player-caused" is read off the DamageInfo's own Instigator, the
        // same test RM_JobGiver_AnchorDefense already applies elsewhere in
        // this build. NOT caught here, disclosed rather than guessed past:
        // butchering a corpse that died of natural causes, which runs as a
        // Bill well after this pawn stopped taking damage — that would need
        // a Harmony patch this pass does not add.
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
        private List<Pawn> registeredYoung = new List<Pawn>();
        private bool recordClean = true;
        private Pawn motherPawn;
        private Pawn heirPawn;
        private bool successionDone;

        public CompProperties_CrecheYoungLedger Props => (CompProperties_CrecheYoungLedger)props;

        public bool RecordClean => recordClean;

        public void RegisterYoung(Pawn p)
        {
            if (p != null && !registeredYoung.Contains(p))
            {
                registeredYoung.Add(p);
            }
        }

        public void BreakRecord()
        {
            recordClean = false;
        }

        public override void CompTick()
        {
            base.CompTick();

            if (successionDone || !RM_MiasmaSettings.wardenSuccessionEnabled)
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
            Pawn chosen = null;
            for (int i = 0; i < registeredYoung.Count; i++)
            {
                Pawn p = registeredYoung[i];
                if (p == null || p.Dead || p.Destroyed || p.Faction != Faction.OfPlayer)
                {
                    continue;
                }

                chosen = p;
                break;
            }

            successionDone = true; // one succession attempt per creche, ever

            if (chosen == null)
            {
                return; // no clean self-tamed young survives her — "the crèche is just a place" per the roster's own "not guaranteed"
            }

            heirPawn = chosen;
            Messages.Message(
                "RUT_WardenSuccessionMessage".Translate(chosen.LabelShort),
                chosen,
                MessageTypeDefOf.PositiveEvent);
        }

        public override string CompInspectStringExtra()
        {
            if (heirPawn != null && !heirPawn.Destroyed)
            {
                return "RUT_CrecheMarkerHeir".Translate(heirPawn.LabelShort);
            }

            return null;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref registeredYoung, "registeredYoung", LookMode.Reference);
            Scribe_Values.Look(ref recordClean, "recordClean", true);
            Scribe_References.Look(ref motherPawn, "motherPawn");
            Scribe_References.Look(ref heirPawn, "heirPawn");
            Scribe_Values.Look(ref successionDone, "successionDone", false);

            if (Scribe.mode == LoadSaveMode.PostLoadInit && registeredYoung == null)
            {
                registeredYoung = new List<Pawn>();
            }
        }
    }
}
