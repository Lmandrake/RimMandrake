using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>
    /// GPT #5 (confirmed in decompiled 1.6): PawnFlyer.TickInterval calls private CheckDestination() every 15 ticks
    /// and, when JumpUtility.ValidJumpTarget fails, moves destCell to ANY valid cell within 3.9 — across a wall,
    /// onto the far lip of a pit, out of a pit. Skipped for our def only; vanilla jumps and other mods' flyers
    /// are untouched.
    /// </summary>
    [HarmonyPatch(typeof(PawnFlyer), "CheckDestination")]
    public static class RM_Patch_PawnFlyer_KnockbackNoRedirect
    {
        public static bool Prefix(PawnFlyer __instance)
        {
            return __instance.def != RM_KnockbackDefOf.RM_PawnFlyer_Knockback;
        }
    }

    /// <summary>A pawn our knockback throws lands without vanilla's job search. PawnFlyer.RespawnPawn ends with
    /// pawn.jobs.CheckForJobOverride(), a full think-tree search, and our RespawnPawn postfix then starts the job suspended
    /// at takeoff (or the remembered haul) anyway: the search was spent and thrown away. A pawn with nothing to resume finds
    /// its job on its next tick (curJob == null -> TryFindAndStartJob), as any idle pawn does. Measured live 2026-11-16
    /// (SteveDesktop, the Explosive Knockback tier, the walk storeroom): 19-25 ms of each landing frame was RespawnPawn, and
    /// the walk's frame row read +17.4% over mod off with five colonists in the room, +1.2% without them
    /// (RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES). Only the pawn our landing holds is skipped.</summary>
    [HarmonyPatch(typeof(Pawn_JobTracker), nameof(Pawn_JobTracker.CheckForJobOverride))]
    public static class RM_Patch_JobTracker_KnockbackLandingNoSearch
    {
        public static bool Prefix(Pawn ___pawn)
        {
            return ___pawn != RM_Patch_PawnFlyer_KnockbackLanding.LandingPawn;
        }
    }

    /// <summary>Our own landing check (GPT #7/#11): if the destination became unusable mid-flight (a wall built, a
    /// door closed, another pawn landed there), walk back along the travelled line toward the takeoff; if nothing
    /// is valid, land at the takeoff. Never across a wall.</summary>
    [HarmonyPatch(typeof(PawnFlyer), "RespawnPawn")]
    public static class RM_Patch_PawnFlyer_KnockbackLanding
    {
        private static readonly AccessTools.FieldRef<PawnFlyer, IntVec3> DestCell = AccessTools.FieldRefAccess<PawnFlyer, IntVec3>("destCell");
        private static readonly AccessTools.FieldRef<PawnFlyer, Vector3> StartVec = AccessTools.FieldRefAccess<PawnFlyer, Vector3>("startVec");
        private static readonly AccessTools.FieldRef<PawnFlyer, JobQueue> JobQueueOf = AccessTools.FieldRefAccess<PawnFlyer, JobQueue>("jobQueue");

        /// <summary>The pawn our RespawnPawn is landing, while it runs (RM_Patch_JobTracker_KnockbackLandingNoSearch); null
        /// otherwise. Cleared by the Finalizer, which runs even when RespawnPawn throws.</summary>
        internal static Pawn LandingPawn;

        public sealed class Landing
        {
            public Pawn pawn;
            public Job resume;   // the job MakeFlyer suspended into the captured queue at takeoff
            public long t0;      // proof build: when the landing began (RM_FrameProbe.LandMs)
        }

        public static void Prefix(PawnFlyer __instance, out Landing __state)
        {
            __state = null;
            if (__instance.def != RM_KnockbackDefOf.RM_PawnFlyer_Knockback)
            {
                return;
            }
            Pawn p = __instance.FlyingPawn;
            Map map = __instance.Map;
            JobQueue q = JobQueueOf(__instance);
            __state = new Landing { pawn = p, resume = q != null && q.Count > 0 ? q[0].job : null };
            LandingPawn = p;
#if RM_PROOFS
            __state.t0 = System.Diagnostics.Stopwatch.GetTimestamp();
#endif
            if (p == null || map == null)
            {
                return;
            }
            IntVec3 dest = DestCell(__instance);
            IntVec3 start = StartVec(__instance).ToIntVec3();
            if (LandOk(map, p, dest))
            {
                return;
            }
            IntVec3 chosen = start;
            int n = Mathf.Max(Mathf.Abs(dest.x - start.x), Mathf.Abs(dest.z - start.z));
            for (int i = n - 1; i >= 1; i--)
            {
                var c = new IntVec3(start.x + Mathf.RoundToInt((dest.x - start.x) * i / (float)n), 0,
                    start.z + Mathf.RoundToInt((dest.z - start.z) * i / (float)n));
                if (LandOk(map, p, c))
                {
                    chosen = c;
                    break;
                }
            }
            if (!chosen.InBounds(map) || !chosen.Standable(map))
            {
                chosen = CellFinder.StandableCellNear(start, map, 3f);
                if (!chosen.IsValid)
                {
                    chosen = start.ClampInsideMap(map); // nothing standable near: never hand RespawnPawn an Invalid cell
                }
            }
            RM_KnockbackJournal.Add("redirect", 0, p, "from", dest, "to", chosen);
            DestCell(__instance) = chosen;
        }

        public static void Postfix(Landing __state)
        {
#if RM_PROOFS
            long resumeT0 = System.Diagnostics.Stopwatch.GetTimestamp();
#endif
            if (__state?.pawn != null)
            {
                Resume(__state.pawn, __state.resume);
            }
            Landed(__state?.pawn);
#if RM_PROOFS
            if (__state != null && __state.t0 != 0)
            {
                RM_FrameProbe.ResumeMs += RM_FrameProbe.MsSince(resumeT0);
                RM_FrameProbe.LandMs += RM_FrameProbe.MsSince(__state.t0);
                RM_FrameProbe.Lands++;
            }
#endif
        }

        public static void Finalizer()
        {
            LandingPawn = null;
        }

        /// <summary>Back to what it was doing (bar pawn_flight_arc). RespawnPawn restores the captured queue, but its
        /// CheckForJobOverride lets the think tree's work givers win: live 2026-11-15 a colonist thrown mid-haul, still holding
        /// the stack, went cleaning. So the job suspended at takeoff is taken out of the queue and started again; the landing
        /// stun still holds the pawn before it moves.</summary>
        private static void Resume(Pawn p, Job job)
        {
            if (job == null)
            {
                ResumeHaul(p);
                return;
            }
            if (p.CurJob == job)
            {
                return;
            }
            string why = !p.Spawned || p.Dead || p.Downed || p.jobs == null ? "not_standing"
                : !p.jobs.jobQueue.Contains(job) ? "not_queued" : !job.CanBeginNow(p) ? "cannot_begin" : null;
            if (why != null)
            {
                RM_KnockbackJournal.Add("resume_skip", 0, p, "job", job.def?.defName ?? "none", "reason", why);
                return;
            }
            p.jobs.jobQueue.Extract(job);
            p.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: false, cancelBusyStances: false);
            RM_KnockbackJournal.Add("resume", 0, p, "job", job.def.defName, "started", p.CurJob == job);
        }

        private static readonly System.Collections.Generic.Dictionary<Pawn, Job> Hauling = new System.Collections.Generic.Dictionary<Pawn, Job>();

        /// <summary>Called just before MakeFlyer: which explosion threw this pawn (negative = a gas burst). Kept by the map
        /// component and saved with it (RM_MapComponent_Knockback.RememberThrow), so a flight saved in mid-air still breaks the
        /// cover it comes down on after a reload; it was a static dictionary, forgotten by a load, and a reloaded colonist stood
        /// on the cover.</summary>
        public static void RememberThrow(Pawn p, int explosionId)
        {
            p.Map?.GetComponent<RM_MapComponent_Knockback>()?.RememberThrow(p, explosionId);
        }

        /// <summary>RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP (scene sc_pit_fall: "on the covered cell the colonist
        /// and the stack fall through, one descent each, and the cover is broken"): a pawn a blast threw onto a covered pit cell
        /// breaks the cover and falls, as a thrown stack does (RM_ThingFlyer_Knockback.Land). FlowWorks' own trap springs on a
        /// deck mass that spares the own faction, so without this a thrown colonist stood on the cover. A gas shove (negative id)
        /// never breaks one (LandingBreaksCover). The id rides in the map component's save, so a flight saved in mid-air
        /// breaks its cover after a reload too.</summary>
        internal static void BreakCoverUnderLanding(Pawn p)
        {
            if (p == null || !p.Spawned)
            {
                return;
            }
            Map map = p.Map;
            RM_MapComponent_Knockback comp = map.GetComponent<RM_MapComponent_Knockback>();
            if (comp == null || !comp.TakeThrow(p, out int id) || p.Dead)
            {
                return;
            }
            IntVec3 at = p.Position;
            if (!RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, RM_KnockbackCompat.CoverAt(map, at) != null, false, id))
            {
                return;
            }
            bool broke = RM_KnockbackCompat.BreakCoverUnder(map, at, out int fallers);
            RM_KnockbackJournal.Add("cover_break", id, p, "at", at, "broken", broke, "fallers", fallers, "kind", "pawn");
        }

        /// <summary>Called just before MakeFlyer: the haul a pawn is on. HaulToCell is not suspendable, so MakeFlyer's
        /// captured queue is empty and the job is gone at landing (live 2026-11-15).</summary>
        public static void RememberHaul(Pawn p)
        {
            Job j = p.CurJob;
            if (j != null && (j.def == JobDefOf.HaulToCell || j.def == JobDefOf.HaulToContainer) && j.targetA.Thing != null && !(j.targetA.Thing is Pawn))
            {
                Hauling[p] = j;
            }
            else
            {
                Hauling.Remove(p);
            }
        }

        /// <summary>A pawn thrown mid-haul is given the same haul again (same stack, destination and count), whether it
        /// still holds the stack (HaulToCell jumps to its carry toil) or the stack lies where it was dropped; failing that,
        /// vanilla's haul-to-storage job for what it holds. The landing stun still holds the pawn before it moves.</summary>
        private static void ResumeHaul(Pawn p)
        {
            Job orig = Hauling.TryGetValue(p, out Job r) ? r : null;
            Hauling.Remove(p);
            Thing held = p.carryTracker?.CarriedThing;
            if (held is Pawn || !p.Spawned || p.Dead || p.Downed || p.Drafted || p.Faction != Faction.OfPlayer)
            {
                return;
            }
            Thing stack = orig?.targetA.Thing;
            Job haul = null;
            if (stack != null && !stack.Destroyed && (held == stack || stack.Spawned && stack.Map == p.Map))
            {
                haul = JobMaker.MakeJob(orig.def, orig.targetA, orig.targetB, orig.targetC);
                haul.count = orig.count;
                haul.haulMode = orig.haulMode;
            }
            else if (held != null)
            {
                haul = HaulAIUtility.HaulToStorageJob(p, held, false);
            }
            if (haul == null)
            {
                if (held != null || stack != null)
                {
                    RM_KnockbackJournal.Add("resume_skip", 0, p, "job", "haul", "reason", held != null ? "no_storage" : "stack_gone");
                }
                return;
            }
            Thing target = haul.targetA.Thing;
            if (p.CurJob != null && p.CurJob.targetA.Thing == target)
            {
                return;
            }
            // another pawn may have taken the dropped stack while this one was in the air (live 2026-11-15): StartJob on an
            // unreservable job fails and returns the job to the pool, so reservations are asked first
            bool stackFree = held == target || p.CanReserve(target), cellFree = !haul.targetB.IsValid || p.CanReserve(haul.targetB);
            if (!stackFree || !cellFree)
            {
                Pawn by = !stackFree ? p.Map.reservationManager.FirstRespectedReserver(target, p)
                    : p.Map.reservationManager.FirstRespectedReserver(haul.targetB, p);
                RM_KnockbackJournal.Add("resume_skip", 0, p, "job", haul.def.defName, "reason", stackFree ? "cell_reserved" : "stack_reserved",
                    "by", by?.ThingID ?? "none", "byJob", by?.CurJobDef?.defName ?? "none", "held", held != null);
                return;
            }
            string jobDef = haul.def.defName;
            IntVec3 at = target.Spawned ? target.Position : IntVec3.Invalid;
            p.jobs.StartJob(haul, JobCondition.InterruptForced, null, resumeCurJobAfterwards: false, cancelBusyStances: false);
            RM_KnockbackJournal.Add("resume", 0, p, "job", jobDef, "started", p.CurJob == haul, "held", held != null, "stackAt", at);
        }

        private static void Landed(Pawn __state)
        {
            if (__state != null)
            {
                RM_MapComponent_Knockback.NotifyLanded(__state); // stun-lock guard: stamps landing + stun end
                if (__state.Spawned)
                {
                    // bar collision_bruise_by_size: a pawn that walked onto the landing cell mid-flight is landed on; both are
                    // bruised by size (RM_KnockbackMath.CollisionBruise), by the throwing blast's impact factor. A landing on an
                    // empty cell bruises nobody.
                    RM_MapComponent_Knockback comp = __state.Map.GetComponent<RM_MapComponent_Knockback>();
                    KbSettings ks = RimMandrakeExplosiveKnockbackSettings.Kernel();
                    ks.impactFactor = comp != null ? comp.TakeImpactFactor(__state) : 1f;
                    var landedOn = new System.Collections.Generic.List<Pawn>();
                    foreach (Thing t in __state.Position.GetThingList(__state.Map))
                    {
                        if (t is Pawn o && o != __state && !RM_KnockbackCompat.IsBeneathCover(o))
                        {
                            landedOn.Add(o);
                        }
                    }
                    foreach (Pawn o in landedOn)
                    {
                        float own = RM_MapComponent_Knockback.PawnMass(__state), other = RM_MapComponent_Knockback.PawnMass(o);
                        float amount = RM_KnockbackMath.CollisionBruise(own, other, ks), otherAmount = RM_KnockbackMath.CollisionBruise(other, own, ks);
                        if (otherAmount > 0f && !o.Dead)
                        {
                            o.TakeDamage(new DamageInfo(DamageDefOf.Blunt, otherAmount));
                        }
                        if (amount > 0f && !__state.Dead)
                        {
                            __state.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount));
                        }
                        RM_KnockbackJournal.Add("land_on_pawn", 0, __state, "at", __state.Position, "pawn", o.ThingID, "pawnId", o.thingIDNumber,
                            "mass", own, "otherMass", other, "amount", amount, "otherAmount", otherAmount);
                    }
                }
                RM_KnockbackJournal.Add("land", 0, __state, "at", __state.Spawned ? __state.Position : IntVec3.Invalid,
                    "spawned", __state.Spawned, "dead", __state.Dead, "downed", __state.Downed,
                    "inPit", __state.Spawned && RM_KnockbackCompat.IsSuperdeep(__state.Map, __state.Position));
            }
        }

        private static bool LandOk(Map map, Pawn p, IntVec3 c)
        {
            if (!c.InBounds(map) || !c.Standable(map))
            {
                return false;
            }
            if (c.GetEdifice(map) is Building_Door door && !door.Open)
            {
                return false;
            }
            // a pawn standing on the cell does not re-target the landing (bar pawn_flight_arc: "lands on the cell chosen at the
            // blast"; Stage 3 reconcile 2026-11-14): pawns share cells, and the Postfix journals the pawn landed on
            return true;
        }
    }

    /// <summary>The cover under a thrown pawn breaks after every other landing hook (Priority.Last). FlowWorks' landing hook
    /// (RM_Patch_PawnFlyer_LandInPit) drops a pawn that lands on an open pit cell; breaking the cover before it ran opened the
    /// cell, so the same landing fell twice and was hurt twice (sc_pit_fall solo lane, visit 4: descents=2, 3 of 3). With the
    /// cover still whole it sees a covered cell and does nothing; the break then drops the pawn, once.</summary>
    [HarmonyPatch(typeof(PawnFlyer), "RespawnPawn")]
    public static class RM_Patch_PawnFlyer_KnockbackCoverBreak
    {
        public static void Prefix(PawnFlyer __instance, out Pawn __state)
        {
            __state = __instance.def == RM_KnockbackDefOf.RM_PawnFlyer_Knockback ? __instance.FlyingPawn : null;
        }

        [HarmonyPriority(Priority.Last)]
        public static void Postfix(Pawn __state)
        {
            RM_Patch_PawnFlyer_KnockbackLanding.BreakCoverUnderLanding(__state);
        }
    }
}
