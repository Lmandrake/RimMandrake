using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef ParentName="Squirrel">
    //     <defName>RUT_Placeholder_SumpMouseRace</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_FilthTrail">
    //         <filthDef>RUT_Filth_MouseTrack</filthDef>
    //         <validTerrains>
    //           <li>RM_TarShallow</li>
    //         </validTerrains>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_FilthTrail : CompProperties
    {
        public ThingDef filthDef;

        // Which terrain grades count as "tar cells crossed" (spec's own
        // wording). Empty = every terrain — deliberately NOT the default,
        // since an ungated trail would paint the whole map, not just the
        // black; a concrete kind's XML must name at least one grade.
        public List<TerrainDef> validTerrains = new List<TerrainDef>();

        // ~1 per 40 cells walked, INVENTED per the spec's own text
        // ("mice deposit ... on tar cells they cross (INVENTED: 1 per ~40
        // cells walked)"). A per-cell-moved-into Bernoulli trial with this
        // probability has an expected value of exactly 1 deposit per 40
        // cells, over a long walk — the simplest mechanism matching the
        // spec's own framing without tracking a running cell counter.
        public float chancePerCellMoved = 0.025f;

        public CompProperties_FilthTrail()
        {
            compClass = typeof(RM_CompFilthTrail);
        }
    }

    // SUMP_MECHANICS_1 S4 (sump_kit_spec.md S4, "mouse-line telegraphy" —
    // "mice deposit RUT_Filth_MouseTrack ... on tar cells they cross").
    // ~20-line comp per the spec's own estimate ("Filth deposit is a
    // ~20-line comp/JobDriver hook") — a comp, not a JobDriver hook: no new
    // Job/JobDriver is needed since the deposit rides the pawn's EXISTING
    // wander job (RM_JobGiver_DreadAvoidWander's own Job.GotoWander),
    // simply watching for the pawn's cell to change on ordinary CompTick —
    // smaller than intercepting or wrapping the wander JobDriver itself,
    // and works for the placeholder's other jobs too (a mouse fleeing or
    // foraging across tar still tracks, matching "mice run the black
    // everywhere," not "only while explicitly wandering").
    //
    // 🔴 Filth-cap finding, this pass's own named ❓ ("verify filth-per-cell
    // caps don't erase the pattern at low mouse counts"), resolved against
    // the live 1.6/Odyssey decompile (RimWorld/Filth.cs, RimWorld/
    // FilthMaker.cs, both read in full):
    //   - Filth.CanBeThickened caps at a HARDCODED 5 (Filth.cs's own
    //     `private const int MaxThickness = 5`, distinct from and stricter
    //     than FilthProperties.maxThickness, which defaults to 100 and is
    //     only consulted inside ThickenFilth()'s own increment guard — the
    //     visible cap any caller actually hits is the hardcoded 5).
    //   - Once a cell's filth reaches that cap, FilthMaker.TryMakeFilth
    //     does NOT drop the deposit: `shouldPropagate` walks the 8
    //     neighbouring cells looking for room instead (FilthMaker.cs:98-124,
    //     `TryMakeFilth`'s own `outFilth != null && !outFilth.CanBeThickened`
    //     branch). So the pattern does not erase at low mouse counts or
    //     heavy single-cell traffic — it SPREADS outward, which if anything
    //     reinforces "a faint tracery," not a single overloaded pixel.
    //   - The real engine block this pass found is upstream of thickness
    //     entirely: `WaterBase.filthAcceptanceMask` is explicitly `None`
    //     (Data/Core/Defs/TerrainDefs/Terrain_Water.xml), inherited
    //     unmodified by RM_TarShallow/RM_TarDeep (LIQUID_TYPES_MOD_1,
    //     checked directly — neither overrides it) — FilthMaker.
    //     TerrainAcceptsFilth returns false outright on a filthAcceptanceMask
    //     of None, so every deposit onto natural tar would silently fail
    //     with zero log output ("a patch that matches nothing logs
    //     nothing," the same silent-failure shape this repo's own CLAUDE.md
    //     already warns about for patches, here hitting a plain API call
    //     instead). Fixed this pass by
    //     RUT_TarShallow_FilthAcceptance.xml (a patch, not an edit to
    //     LIQUID_TYPES_MOD_1's own generated RM_Tar.xml) adding
    //     `filthAcceptanceMask: [Terrain]` directly onto RM_TarShallow —
    //     RM_TarDeep was left untouched (WaterDeepBase-derived, Impassable,
    //     never a cell a wandering pawn's own path can cross, so patching
    //     it would have no observable effect).
    //   - `ignoreFilthMultiplierStat true` on RUT_Filth_MouseTrack (not an
    //     engine block — StatDefOf.FilthMultiplier defaults to 1/100% and
    //     no terrain in this chain overrides it, confirmed against Stats_
    //     Basics_Special.xml — but set anyway so the spec's own single
    //     density knob, chancePerCellMoved, is the ONLY randomness in the
    //     deposit path rather than being further dilated by an unrelated
    //     per-terrain stat a future terrain edit could silently change).
    public class RM_CompFilthTrail : ThingComp
    {
        private IntVec3 lastPosition = IntVec3.Invalid;

        public CompProperties_FilthTrail Props => (CompProperties_FilthTrail)props;

        public override void CompTick()
        {
            base.CompTick();

            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned)
            {
                return;
            }

            IntVec3 pos = pawn.Position;
            if (pos == lastPosition)
            {
                return; // hasn't moved to a new cell since the last tick — nothing to deposit
            }
            lastPosition = pos;

            CompProperties_FilthTrail props = Props;
            if (props?.filthDef == null || props.validTerrains.NullOrEmpty())
            {
                return;
            }

            if (!props.validTerrains.Contains(pos.GetTerrain(pawn.Map)))
            {
                return; // not a tracked "tar" cell — no track laid
            }

            if (!Rand.Chance(props.chancePerCellMoved))
            {
                return;
            }

            FilthMaker.TryMakeFilth(pos, pawn.Map, props.filthDef);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastPosition, "filthTrailLastPosition", IntVec3.Invalid);
        }
    }
}
