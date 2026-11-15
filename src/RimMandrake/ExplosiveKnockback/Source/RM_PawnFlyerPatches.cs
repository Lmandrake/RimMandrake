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

    /// <summary>Our own landing check (GPT #7/#11): if the destination became unusable mid-flight (a wall built, a
    /// door closed, another pawn landed there), walk back along the travelled line toward the takeoff; if nothing
    /// is valid, land at the takeoff. Never across a wall.</summary>
    [HarmonyPatch(typeof(PawnFlyer), "RespawnPawn")]
    public static class RM_Patch_PawnFlyer_KnockbackLanding
    {
        private static readonly AccessTools.FieldRef<PawnFlyer, IntVec3> DestCell = AccessTools.FieldRefAccess<PawnFlyer, IntVec3>("destCell");
        private static readonly AccessTools.FieldRef<PawnFlyer, Vector3> StartVec = AccessTools.FieldRefAccess<PawnFlyer, Vector3>("startVec");
        private static readonly AccessTools.FieldRef<PawnFlyer, JobQueue> JobQueueOf = AccessTools.FieldRefAccess<PawnFlyer, JobQueue>("jobQueue");

        public sealed class Landing
        {
            public Pawn pawn;
            public Job resume;   // the job MakeFlyer suspended into the captured queue at takeoff
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
            if (__state?.pawn != null)
            {
                Resume(__state.pawn, __state.resume);
            }
            Landed(__state?.pawn);
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
                    foreach (Thing t in __state.Position.GetThingList(__state.Map))
                    {
                        if (t is Pawn o && o != __state)
                        {
                            RM_KnockbackJournal.Add("land_on_pawn", 0, __state, "at", __state.Position, "pawn", o.ThingID, "pawnId", o.thingIDNumber);
                        }
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
}
