using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef ParentName="Squirrel">
    //     <defName>RUT_Placeholder_SumpMouseRace</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_DreadAvoidWanderExtension" />
    //     </modExtensions>
    //   </ThingDef>
    //
    // Presence-only marker — no fields. A race opts in to dread-avoidance
    // wander by carrying this; RM_JobGiver_DreadAvoidWander.TryGiveJob
    // checks for it on its very first line before doing anything else.
    public class RM_DreadAvoidWanderExtension : DefModExtension
    {
    }

    // SUMP_MECHANICS_1 S4 (sump_kit_spec.md S4, "mouse-line telegraphy" —
    // "mice never path into dread cells").
    //
    // ❓ resolved (spec's own named seam question): "cheapest seam: ThinkTree
    // wander-node validator vs pathfinder cost injection — read the wander
    // JobGiver family at build and crib the smaller." Read
    // Verse.AI/JobGiver_Wander.cs and Verse.AI/RCellFinder.cs in full this
    // pass (live 1.6 decompile): JobGiver_Wander.GetExactWanderDest already
    // threads a `Func<Pawn, IntVec3, IntVec3, bool> wanderDestValidator`
    // through RCellFinder.RandomWanderDestFor for every candidate cell it
    // rolls — the exact "wander-node validator" arm of the spec's own
    // question, and the smaller one: no pathfinder-cost-grid code is needed
    // at all. This mod already has a real, reviewed, compiling instance of
    // this seam — RM_JobGiver_ColumnWander (FORGE_MECHANICS_1 F3,
    // RM_CompVaporDrifter.cs) — so this class cribs it verbatim rather than
    // re-deriving the pattern: a JobGiver_Wander subclass setting
    // wanderDestValidator in its own constructor. GetWanderRoot is left at
    // the pawn's own position (no anchor/column concept here, unlike the
    // Forge/Miasma variants — mice roam freely, they are just forbidden
    // from stepping INTO a dread cell).
    //
    // Insertion seam: NOT a per-race ThinkTreeDef override (that would mean
    // authoring a full replacement for vanilla's "Animal" main tree, a much
    // bigger and riskier surface than this mechanic needs). Instead this
    // class is inserted via insertTag="Animal_PreMain"
    // (RUT_ThinkTree_SumpMouseWander.xml) — the SAME global, safe-by-
    // construction extension point SHIP_VERMIN_MOD_1's own
    // RM_ThinkTree_VerminBehaviors.xml already established in this repo
    // (its own header: "every ThinkTreeDef sharing an insertTag is tried,
    // in insertPriority order, for EVERY animal in the game whose think
    // tree includes that tag — the vanilla Animal tree does,
    // unconditionally... safe to insert globally" provided every inserted
    // JobGiver returns no job instantly for a pawn whose race lacks its own
    // marker extension). RM_DreadAvoidWanderExtension (above) is this
    // mechanic's own marker, checked on TryGiveJob's very first line —
    // every animal in the game that is NOT the Sump mouse placeholder falls
    // through untouched to its own ordinary wander node, same tick.
    public class RM_JobGiver_DreadAvoidWander : JobGiver_Wander
    {
        public RM_JobGiver_DreadAvoidWander()
        {
            wanderDestValidator = DestNotDreaded;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (pawn.def.GetModExtension<RM_DreadAvoidWanderExtension>() == null)
            {
                return null; // not an opted-in race — no-op, matches every other animal's ordinary wander
            }

            return base.TryGiveJob(pawn);
        }

        protected override IntVec3 GetWanderRoot(Pawn pawn)
        {
            return pawn.Position;
        }

        private static bool DestNotDreaded(Pawn pawn, IntVec3 root, IntVec3 dest)
        {
            RM_MapComponent_DreadField field = pawn.Map?.GetComponent<RM_MapComponent_DreadField>();
            if (field == null)
            {
                return true; // no dread field on this map — do not strand the pawn
            }

            return !field.IsDreaded(dest);
        }
    }
}
