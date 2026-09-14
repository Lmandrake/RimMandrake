using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.EnvironmentalHazards
{
    // SCARLANDS_MECHANICS_1 §4 (the Forgotten Sentinels — hard ban §6:
    // defend only, never assault, never pursue past their lines).
    //
    // Two real vanilla lord jobs were checked and rejected before writing
    // this, both RimSage/decompile-verified against the live 1.6 source:
    //
    //   - LordJob_MechanoidsDefend.CreateGraph leaks into
    //     LordToil_AssaultColony on TriggerSignalType.MechClusterDefeated
    //     and (for !isMechCluster) Trigger_AnyThingDamageTaken — i.e.
    //     destroying the defended thing turns the "defenders" into
    //     attackers. Exactly the leak ban §6 forbids.
    //   - LordJob_DefendPoint (Verse.AI.Group, read in full below) is the
    //     pure single-toil shape this kit wants, but its only public ctor
    //     takes (IntVec3, float? wanderRadius, float? defendRadius, bool
    //     isCaravanSendable, bool addFleeToil) — no SpawnedPawnParams ctor,
    //     so CompSpawnerPawn.CreateNewLord (RimSage/decompile-verified:
    //     Activator.CreateInstance(lordJobType, new SpawnedPawnParams
    //     { aggressive, spawnerThing, defendRadius, defSpot })) can never
    //     construct one. Sentinel spawner buildings (repair alcoves,
    //     grave-wards) ride ordinary CompSpawnerPawn, so a SpawnedPawnParams
    //     ctor is required, not optional.
    //
    // This class is that ctor plus the ban made structural: AddFleeToil is
    // permanently false (Sentinels hold their post, they don't rout — the
    // sheet's own framing) and CreateGraph is a single toil, nothing else —
    // no signal handler exists to transition anywhere, so there is nothing
    // for a future edit to accidentally wire into an assault toil the way
    // the vanilla mechanoid job does.
    //
    // Deliberately RM_-tier and content-blind: defendDuty is passed in by
    // whatever spawns the lord (Sentinel content is RUT_-tier per
    // scarlands_kit_spec.md's own naming section) rather than hardcoded
    // here, so this class is reusable by any future "defend without
    // assaulting" pawn kind, not just the Scarlands' own Sentinels. Passing
    // null keeps vanilla's own DutyDefOf.Defend (RM_LordToil_DefendPerimeter
    // below falls back to it), so this class is a strict superset of
    // LordJob_DefendPoint's own behavior, never a behavior change by
    // omission.
    public class RM_LordJob_DefendPerimeter : LordJob
    {
        private IntVec3 point;
        private float defendRadius;
        private float wanderRadius;
        private DutyDef defendDuty;

        // Parameterless ctor required by Scribe (LordJob instances are
        // save/loaded by type, then ExposeData fills the fields back in —
        // same shape LordJob_DefendPoint itself uses).
        public RM_LordJob_DefendPerimeter()
        {
        }

        // The ctor CompSpawnerPawn.CreateNewLord actually calls via
        // Activator.CreateInstance(lordJobType, SpawnedPawnParams). Radii
        // default to the owner-ruled doubled values (scarlands_kit_spec.md
        // owner ruling 6b: acquire 72 / keep 80 / wander 24 / defend 80) —
        // the caller may still override via the explicit-args ctor below.
        public RM_LordJob_DefendPerimeter(SpawnedPawnParams parms)
            : this(parms.defSpot, parms.defendRadius > 0f ? parms.defendRadius : 80f, 24f, null)
        {
        }

        public RM_LordJob_DefendPerimeter(IntVec3 point, float defendRadius = 80f, float wanderRadius = 24f, DutyDef defendDuty = null)
        {
            this.point = point;
            this.defendRadius = defendRadius;
            this.wanderRadius = wanderRadius;
            this.defendDuty = defendDuty;
        }

        // Ban §6, structurally: LordJob_DefendPoint.AddFleeToil defaults
        // true (vanilla lets a losing defender rout); this override is the
        // one-line difference that keeps a Sentinel standing its ground
        // instead, matching "they never raid, never pursue" from the other
        // direction — they don't retreat past their own lines either.
        public override bool AddFleeToil => false;

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();
            graph.AddToil(new RM_LordToil_DefendPerimeter(point, defendRadius, wanderRadius, defendDuty));
            return graph;
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref point, "point");
            Scribe_Values.Look(ref defendRadius, "defendRadius", 80f);
            Scribe_Values.Look(ref wanderRadius, "wanderRadius", 24f);
            Scribe_Defs.Look(ref defendDuty, "defendDuty");
        }
    }

    // Subclassed rather than reused as-is because LordToil_DefendPoint.
    // UpdateAllDuties (RimSage/decompile-verified, Verse.AI.Group.
    // LordToil_DefendPoint) hardcodes DutyDefOf.Defend on every pawn's
    // PawnDuty — the ❓ the kit spec flagged as needing a build-time check.
    // Resolved: it is hardcoded, so the ~10-line subclassed-toil fallback
    // the spec already anticipated is what ships. Everything else
    // (defendPoint/defendRadius/wanderRadius storage, FlagLoc) is inherited
    // unchanged from the base LordToilData_DefendPoint this class reuses.
    public class RM_LordToil_DefendPerimeter : LordToil_DefendPoint
    {
        private readonly DutyDef defendDuty;

        public RM_LordToil_DefendPerimeter(IntVec3 defendPoint, float defendRadius, float wanderRadius, DutyDef defendDuty)
            : base(defendPoint, defendRadius, wanderRadius)
        {
            this.defendDuty = defendDuty;
        }

        public override void UpdateAllDuties()
        {
            DutyDef duty = defendDuty ?? DutyDefOf.Defend;
            for (int i = 0; i < lord.ownedPawns.Count; i++)
            {
                Pawn pawn = lord.ownedPawns[i];
                if (pawn?.mindState == null)
                {
                    continue;
                }
                pawn.mindState.duty = new PawnDuty(duty, Data.defendPoint);
                pawn.mindState.duty.focusSecond = Data.defendPoint;
                pawn.mindState.duty.radius = pawn.kindDef.defendPointRadius >= 0f
                    ? pawn.kindDef.defendPointRadius
                    : Data.defendRadius;
                pawn.mindState.duty.wanderRadius = Data.wanderRadius;
            }
        }
    }
}
