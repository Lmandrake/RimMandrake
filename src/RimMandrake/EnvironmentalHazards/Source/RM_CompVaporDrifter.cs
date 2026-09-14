using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef ParentName="AnimalThingBase">
    //     <defName>RUT_Fumerider</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_VaporDrifter">
    //         <forageRadiusBeyondColumns>0</forageRadiusBeyondColumns>
    //         <groundHazardImmune>true</groundHazardImmune>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_VaporDrifter : CompProperties
    {
        // F3 spec, "fleet fliers": "the drifter comp with a looser leash
        // (INVENTED: forage radius 12 beyond columns)". 0 (the default) is
        // the column-bound reading for beldons/fumeriders — a destination
        // outside every column is never valid. A concrete fleet-flier kind
        // sets this to 12 via XML.
        public float forageRadiusBeyondColumns = 0f;

        // How far RM_JobGiver_ColumnWander will search from the pawn's own
        // position for a column cell to use as the wander root before
        // falling back to standing still (spec gives no figure for this —
        // INVENTED, generous enough to reach across an ordinary map's vent
        // field without scanning the whole map every wander decision).
        public float columnSearchRadius = 60f;

        // "grants ground-hazard immunity (scald bursts ... do not touch
        // drifters — they live in the steam)" — read by
        // RM_GameCondition_WeatherPulse.DoScaldDamageOnMap. A per-kind
        // escape hatch (default true) rather than an unconditional skip,
        // matching this kit's own "everything is a prop" posture.
        public bool groundHazardImmune = true;

        public CompProperties_VaporDrifter()
        {
            compClass = typeof(RM_CompVaporDrifter);
        }
    }

    // FORGE_MECHANICS_1 F3 build pass. Marker + data comp: RM_JobGiver_
    // ColumnWander and RM_GameCondition_WeatherPulse both just read Props off
    // whatever pawn carries this — the comp itself does no per-tick work
    // (unlike CompActiveGasEmitter, there's nothing to burst or gather here).
    //
    // No float-draw offset: FORGE_MECHANICS_1's own spike pass (forge_kit_
    // spec.md F3, "RESOLVED") already settled this — the Aerofleet float is
    // CONFIRMED class-side, Vanilla Expanded Framework's own CompFloating
    // registering into a shared list consumed by exactly one Harmony postfix
    // on Pawn_DrawTracker.DrawPos. A sky kind that also carries VEF's
    // CompProperties_Floating already floats without this comp (or this
    // build pass) touching draw code at all — the spec's own "if the
    // Aerofleet route turns out to be class-side rather than def-side" ❓ is
    // resolved to class-side, so per the spec's own allowance this pass
    // ships no offset code.
    public class RM_CompVaporDrifter : ThingComp
    {
        public CompProperties_VaporDrifter Props => (CompProperties_VaporDrifter)props;
    }

    // Crib: RM_CompTerritorialAnchor's RM_JobGiver_AnchorWander
    // (MIASMA_MECHANICS_1 M6), generalized from "anchored to a fixed Thing"
    // to "anchored to the nearest RM_MapComponent_VaporColumns cell" — the
    // spec's own F3 resolution names this exact generalization ("a sibling
    // RM_JobGiver_ColumnWander : JobGiver_Wander overriding GetWanderRoot to
    // return the nearest cell RM_MapComponent_VaporColumns.InColumn
    // accepts... No new C# class is needed to prove this seam; it already
    // compiles as RM_CompTerritorialAnchor's own JobGivers.").
    //
    // Two seams do the constraining, not one:
    //   - GetWanderRoot picks the nearest column cell to wander AROUND;
    //   - wanderDestValidator (a real JobGiver_Wander field, Verse/AI/
    //     JobGiver_Wander.cs) rejects any candidate destination that is
    //     neither in a column nor within the carrying pawn's own
    //     forageRadiusBeyondColumns of one — this is what actually keeps a
    //     column-bound species OFF the open ash even when RCellFinder rolls
    //     a candidate cell outside the column proper, not just the root.
    // wanderRadius is left at JobGiver_Wander's own default (protected, not
    // touched in the constructor) so a concrete kind's ThinkTreeDef XML can
    // tune it per the vanilla idiom stock animal wander JobGivers already
    // use (e.g. JobGiver_WanderHive's own XML sets <wanderRadius> directly);
    // RM_JobGiver_AnchorWander hardcodes its own radius in C# instead only
    // because it serves exactly one anchored-creature family — this
    // JobGiver is meant for every future sky kind, so the radius is
    // deliberately XML, not baked.
    public class RM_JobGiver_ColumnWander : JobGiver_Wander
    {
        public RM_JobGiver_ColumnWander()
        {
            wanderDestValidator = DestInColumnOrForageRange;
        }

        protected override IntVec3 GetWanderRoot(Pawn pawn)
        {
            RM_MapComponent_VaporColumns columns = pawn.Map?.GetComponent<RM_MapComponent_VaporColumns>();
            if (columns == null)
            {
                return pawn.Position;
            }

            CompProperties_VaporDrifter props = pawn.TryGetComp<RM_CompVaporDrifter>()?.Props;
            float searchRadius = props != null ? props.columnSearchRadius : 60f;

            IntVec3 nearest = columns.NearestColumnCell(pawn.Position, searchRadius);
            return nearest.IsValid ? nearest : pawn.Position;
        }

        private static bool DestInColumnOrForageRange(Pawn pawn, IntVec3 root, IntVec3 dest)
        {
            RM_MapComponent_VaporColumns columns = pawn.Map?.GetComponent<RM_MapComponent_VaporColumns>();
            if (columns == null)
            {
                return true; // no column data on this map — do not strand the pawn
            }

            if (columns.InColumn(dest))
            {
                return true;
            }

            float forageRadius = pawn.TryGetComp<RM_CompVaporDrifter>()?.Props.forageRadiusBeyondColumns ?? 0f;
            if (forageRadius <= 0f)
            {
                return false;
            }

            return columns.NearestColumnCell(dest, forageRadius).IsValid;
        }
    }
}
