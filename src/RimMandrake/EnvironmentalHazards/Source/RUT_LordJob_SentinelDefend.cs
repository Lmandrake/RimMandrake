using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.EnvironmentalHazards
{
    // SCARLANDS_MECHANICS_2 build pass, §4 (Forgotten Sentinels). The
    // SpawnedPawnParams ctor CompSpawnerPawn.CreateNewLord actually calls
    // (Activator.CreateInstance(lordJobType, SpawnedPawnParams), decompile-
    // confirmed) is the ONLY seam a <lordJob> XML field can reach — and
    // RM_LordJob_DefendPerimeter's own version of that ctor always passes
    // defendDuty=null (it has nowhere else to source content from, being
    // deliberately RM_-tier and content-blind). A spawner building's XML
    // still needs a way to hand in the real, tightened-radius duty
    // (RUT_SentinelDefend — DutyDefOf.Defend's own targetAcquireRadius 65/
    // targetKeepRadius 72 tightened to the owner-ruled 72/80, scarlands_kit_
    // spec.md owner ruling 6b). This one-method subclass is that seam:
    // <lordJob>RimMandrake.EnvironmentalHazards.RUT_LordJob_SentinelDefend</lordJob>
    // on the grave-ward/repair-alcove ThingDef's CompProperties_SpawnerPawn.
    //
    // DefDatabase lookup rather than a cached DefOf: this ctor runs at
    // lord-creation time during play, well after defs are loaded, so no
    // load-order hazard — and GetNamedSilentFail degrades to null (RM_
    // LordToil_DefendPerimeter's own defendDuty ?? DutyDefOf.Defend fallback)
    // rather than throwing if RUT_SentinelDefend is ever missing.
    public class RUT_LordJob_SentinelDefend : RM_LordJob_DefendPerimeter
    {
        // Parameterless ctor required by Scribe (see RM_LordJob_DefendPerimeter's
        // own note — LordJob instances are save/loaded by type, ExposeData
        // fills the fields back in from the base class).
        public RUT_LordJob_SentinelDefend()
        {
        }

        public RUT_LordJob_SentinelDefend(SpawnedPawnParams parms)
            : base(
                parms.defSpot,
                parms.defendRadius > 0f ? parms.defendRadius : 80f,
                24f,
                DefDatabase<DutyDef>.GetNamedSilentFail("RUT_SentinelDefend"))
        {
        }
    }
}
