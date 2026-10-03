using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LanternDeeps
{
    // ════════════════════════════════════════════════════════════════════
    // LANTERNDEEPS_ORUN_GHAL_BUILD_1 (slate row 7 of
    // design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md §5, revised by the
    // owner, typed): "I like the mining suit that's alive despite the skeleton within it. But it might
    // not just mine as when animated it is controlled by the sentient crystals. Instead it becomes an
    // inhabitant on the map to study and befriend. I don't think the crystals are too keen mining."
    //
    //  - RM_OrunGhal: a huge dead mining exoframe, its miner's skeleton inside, worn and moved by the
    //    Shard-minds. A wild pawn on an ordinary footprint, drawn huge. It never mines, cuts no tunnel,
    //    never hunts, never turns on anyone (manhunter chance 0): never a boss, never a worker.
    //  - RM_JobGiver_OrunGhalRounds: it walks its rounds between the Shard-minds and any lit Lantern,
    //    and, as it comes to know the colony, toward the colonists themselves.
    //  - Study + befriend: a colonist (Research work) visits it and studies it; it stands still for
    //    the visit. Each session can reveal what the crystals are and what they want (lore letters,
    //    data on the comp props); each visit on a NEW day raises its standing one step. Standing
    //    changes how it walks its rounds and what its inspect pane says. One study visit per day.
    // Free tier, invented name, no franchise. One per Deep, placed by RM_GenStep_OrunGhal.
    // ════════════════════════════════════════════════════════════════════

    public class RM_OrunGhalLore
    {
        public int session = 1;
        public string label;
        public string text;
    }

    public class CompProperties_RM_OrunGhal : CompProperties
    {
        public int studyTicks = 2000;
        public float intellectualXpPerTick = 0.12f;
        // standing at which each tier begins: Wary 0, Curious, Familiar, Friend
        public int curiousAt = 2;
        public int familiarAt = 5;
        public int friendAt = 9;
        public List<RM_OrunGhalLore> lore = new List<RM_OrunGhalLore>();

        public CompProperties_RM_OrunGhal()
        {
            compClass = typeof(CompRM_OrunGhal);
        }
    }

    public class CompRM_OrunGhal : ThingComp
    {
        public int sessions;
        public int standing;
        public int lastVisitDay = -1;
        public int lastStudyTick = -999999;

        public CompProperties_RM_OrunGhal Props => (CompProperties_RM_OrunGhal)props;

        public int Tier => standing >= Props.friendAt ? 3 : standing >= Props.familiarAt ? 2 : standing >= Props.curiousAt ? 1 : 0;

        public static string TierLabel(int tier) => ("RM_OrunGhalTier" + tier).Translate();

        public bool CanStudyNow => LanternDeepsSettings.orunGhalStudyEnabled
            && Find.TickManager.TicksGame - lastStudyTick >= GenDate.TicksPerDay;

        public void CompleteSession(Pawn studier)
        {
            Pawn orun = (Pawn)parent;
            sessions++;
            lastStudyTick = Find.TickManager.TicksGame;
            int day = GenDate.DaysPassed;
            int oldTier = Tier;
            if (day != lastVisitDay)
            {
                lastVisitDay = day;
                standing++;
            }
            foreach (RM_OrunGhalLore l in Props.lore)
            {
                if (l.session == sessions)
                {
                    Find.LetterStack.ReceiveLetter(l.label, l.text.Formatted(studier.Named("STUDIER")),
                        LetterDefOf.PositiveEvent, orun);
                }
            }
            if (Tier != oldTier)
            {
                MoteMaker.ThrowText(orun.DrawPos, orun.Map, TierLabel(Tier), 4f);
                if (Tier == 3)
                {
                    Find.LetterStack.ReceiveLetter("RM_OrunGhalFriendLabel".Translate(),
                        "RM_OrunGhalFriendText".Translate(studier.Named("STUDIER")), LetterDefOf.PositiveEvent, orun);
                }
                else
                {
                    Messages.Message("RM_OrunGhalTierMsg".Translate(TierLabel(Tier)), orun, MessageTypeDefOf.PositiveEvent);
                }
            }
        }

        public override string CompInspectStringExtra()
        {
            string s = "RM_OrunGhalInspect".Translate(TierLabel(Tier), sessions);
            if (!CanStudyNow && LanternDeepsSettings.orunGhalStudyEnabled)
            {
                s += "\n" + "RM_OrunGhalRested".Translate();
            }
            return s;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref sessions, "sessions", 0);
            Scribe_Values.Look(ref standing, "standing", 0);
            Scribe_Values.Look(ref lastVisitDay, "lastVisitDay", -1);
            Scribe_Values.Look(ref lastStudyTick, "lastStudyTick", -999999);
        }
    }

    // ── Its rounds ──────────────────────────────────────────────────────
    public class RM_JobGiver_OrunGhalRounds : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            CompRM_OrunGhal comp = pawn.TryGetComp<CompRM_OrunGhal>();
            if (comp == null || pawn.Map == null || pawn.Faction != null || !LanternDeepsSettings.orunGhalEnabled)
            {
                return null;
            }
            if (!Rand.Chance(0.35f))
            {
                return null; // the rest of the time it stands and wanders as an animal does
            }
            Thing dest = PickDestination(pawn, comp);
            if (dest == null)
            {
                return null;
            }
            float radius = dest is Pawn ? 4f : 6f;
            if (!CellFinder.TryFindRandomReachableNearbyCell(dest.Position, pawn.Map, radius, TraverseParms.For(pawn),
                    c => c.Standable(pawn.Map) && !c.GetTerrain(pawn.Map).IsWater, null, out IntVec3 cell))
            {
                return null;
            }
            Job job = JobMaker.MakeJob(JobDefOf.GotoWander, cell);
            job.locomotionUrgency = LocomotionUrgency.Walk;
            return job;
        }

        private static Thing PickDestination(Pawn pawn, CompRM_OrunGhal comp)
        {
            Map map = pawn.Map;
            // Coming to know the colony: Familiar sometimes, Friend often, it walks to a colonist.
            float toColonist = comp.Tier == 3 ? 0.4f : comp.Tier == 2 ? 0.2f : 0f;
            if (toColonist > 0f && Rand.Chance(toColonist))
            {
                Pawn c = map.mapPawns.FreeColonistsSpawned.Where(p => pawn.CanReach(p, PathEndMode.Touch, Danger.Some)).RandomElementWithFallback();
                if (c != null)
                {
                    return c;
                }
            }
            // "Keeps near the Lantern": a lit Lantern first, else the Shard-minds that wear it.
            List<Thing> lanterns = map.listerThings.AllThings
                .Where(t => t.def.defName == "RM_Lantern" && (t.TryGetComp<CompGlower>()?.Glows ?? false)).ToList();
            if (lanterns.Count > 0 && Rand.Chance(0.6f))
            {
                return lanterns.RandomElement();
            }
            ThingDef mind = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ShardMind");
            if (mind != null)
            {
                Thing m = map.listerThings.ThingsOfDef(mind).RandomElementWithFallback();
                if (m != null)
                {
                    return m;
                }
            }
            return lanterns.RandomElementWithFallback();
        }
    }

    // ── Study ───────────────────────────────────────────────────────────
    public class RM_WorkGiver_StudyOrunGhal : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            return pawn.Map.mapPawns.AllPawnsSpawned.Where(p => p.TryGetComp<CompRM_OrunGhal>() != null).Cast<Thing>();
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !LanternDeepsSettings.orunGhalStudyEnabled || !pawn.Map.mapPawns.AllPawnsSpawned.Any(p => p.TryGetComp<CompRM_OrunGhal>() != null);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            CompRM_OrunGhal comp = t.TryGetComp<CompRM_OrunGhal>();
            if (comp == null || !(t is Pawn orun) || orun.Dead || !comp.CanStudyNow)
            {
                return false;
            }
            return pawn.CanReserve(t, 1, -1, null, forced) && pawn.CanReach(t, PathEndMode.Touch, Danger.Some);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            JobDef def = DefDatabase<JobDef>.GetNamedSilentFail("RM_StudyOrunGhal");
            return def == null ? null : JobMaker.MakeJob(def, t);
        }
    }

    public class RM_JobDriver_StudyOrunGhal : JobDriver
    {
        private Pawn Orun => (Pawn)job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => Orun.Dead || !(Orun.TryGetComp<CompRM_OrunGhal>()?.CanStudyNow ?? false));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            CompProperties_RM_OrunGhal props = Orun.TryGetComp<CompRM_OrunGhal>().Props;
            Toil study = ToilMaker.MakeToil("StudyOrunGhal");
            study.initAction = delegate
            {
                // It stands still for the visit.
                if (!Orun.Downed)
                {
                    Job wait = JobMaker.MakeJob(JobDefOf.Wait_MaintainPosture);
                    wait.expiryInterval = props.studyTicks + 120;
                    Orun.jobs.StartJob(wait, JobCondition.InterruptForced);
                    Orun.rotationTracker.FaceTarget(pawn);
                }
            };
            study.tickIntervalAction = delegate(int delta)
            {
                pawn.skills?.Learn(SkillDefOf.Intellectual, props.intellectualXpPerTick * delta);
                pawn.rotationTracker.FaceTarget(Orun);
            };
            study.defaultCompleteMode = ToilCompleteMode.Delay;
            study.defaultDuration = props.studyTicks;
            study.WithProgressBarToilDelay(TargetIndex.A);
            study.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            study.activeSkill = () => SkillDefOf.Intellectual;
            yield return study;
            yield return Toils_General.Do(delegate
            {
                Orun.TryGetComp<CompRM_OrunGhal>()?.CompleteSession(pawn);
            });
        }
    }

    // ── Placement: one per Deep ─────────────────────────────────────────
    public class RM_GenStep_OrunGhal : GenStep
    {
        public PawnKindDef kind;

        public override int SeedPart => 771940213;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (LanternDeepsSettings.orunGhalEnabled)
            {
                Place(map, kind);
            }
        }

        public static string Place(Map map, PawnKindDef kind)
        {
            if (kind == null)
            {
                return "no kind";
            }
            ThingDef mind = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ShardMind");
            Thing anchor = mind == null ? null : map.listerThings.ThingsOfDef(mind).RandomElementWithFallback();
            IntVec3 cell;
            bool found = anchor != null
                ? CellFinder.TryFindRandomCellNear(anchor.Position, map, 8, c => c.Standable(map), out cell)
                : CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.DistanceToEdge(map) > 8, out cell);
            if (!found)
            {
                return "no cell";
            }
            Pawn orun = PawnGenerator.GeneratePawn(kind);
            GenSpawn.Spawn(orun, cell, map);
            return "placed " + orun.LabelShort + " at " + cell + (anchor != null ? " near a shard-mind" : "");
        }
    }

    // ── Proof hooks for jawa/static_call (validation.py, orun_ghal) ────────
    public static class RM_OrunGhalProof
    {
        public static string ProofPlace(string unused)
        {
            Map map = Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_OrunGhal");
            return map == null ? "no map" : RM_GenStep_OrunGhal.Place(map, kind);
        }

        // Completes `n` study sessions on the first Orun-Ghal on the map, each on its own day as far as
        // standing is concerned; returns "sessions=.. standing=.. tier=..".
        public static string ProofStudy(string n)
        {
            Map map = Find.CurrentMap;
            Pawn orun = map?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.TryGetComp<CompRM_OrunGhal>() != null);
            Pawn studier = map?.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (orun == null || studier == null)
            {
                return "need an Orun-Ghal and a colonist on the current map";
            }
            CompRM_OrunGhal comp = orun.TryGetComp<CompRM_OrunGhal>();
            int count = int.TryParse(n, out int parsed) ? parsed : 1;
            for (int i = 0; i < count; i++)
            {
                comp.lastVisitDay = -1;
                comp.CompleteSession(studier);
            }
            return "sessions=" + comp.sessions + " standing=" + comp.standing + " tier=" + comp.Tier
                + " mining=" + (orun.CurJobDef == JobDefOf.Mine);
        }
    }
}
