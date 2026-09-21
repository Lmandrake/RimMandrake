using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // VENOMVINE_FORTRESS_PASSABILITY_1. The shrubland sheet's
    // "small creatures pass through easily; larger ones simply cannot",
    // expressed as three body-size bands on the cell a Thing occupies.
    //
    // XML shape:
    //
    //   <ThingDef ParentName="PlantBaseNonEdible">
    //     <defName>RM_VenomvineThicket</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_CompProperties_BodySizeBarrier">
    //         <passFreelyBodySize>0.8</passFreelyBodySize>
    //         <blockBodySize>1.5</blockBodySize>
    //         <threadMoveCost>300</threadMoveCost>
    //       </li>
    //     </comps>
    //   </ThingDef>
    //
    // Generic on purpose, same posture as CompProperties_ContactVenom beside
    // it: nothing here names a plant, a biome or a campaign, and a later
    // hedge, reef or wreck-tangle reuses it with different numbers.
    //
    // 🔑 The two thresholds are NOT interchangeable, and only one of them is
    // arbitrary:
    //
    //   blockBodySize 1.5 is VANILLA'S OWN "this pawn fills the cell"
    //   constant. PawnUtility.PawnsCanShareCellBecauseOfBodySize returns
    //   false outright once either pawn is >= 1.5f (MEASURED from the
    //   decompiled 1.6 source, 2026-09-21) — a pawn the engine already
    //   refuses to let share a cell with anything is the pawn that cannot
    //   thread a thicket. At 1.5 the blocked set is muffalo (2.4), bison
    //   (2.1), boomalope (2.0), rhinoceros (3.0), elephant/thrumbo (4.0),
    //   dewback (3.0), bantha (4.0), ronto (6.0) and RSW_ShrublandGiant
    //   (6.0) — the shrubland size ladder's HUGE band, exactly the band the
    //   sheet says "simply cannot".
    //
    //   passFreelyBodySize 0.8 is ours, chosen against the roster rather
    //   than against the engine: it puts womprat (0.75), shyrack (0.75),
    //   scurrier (0.2), hare (0.2) and every bird under the free band, and
    //   leaves humanlikes (1.0) and wargs (1.4) in the middle band that
    //   threads slowly. That middle band is the sheet's "sparser stands let
    //   a Jawa slowly thread them".
    //
    // ⚠️ "no larger race can" cannot be read literally against a body-size
    // gate, and this build does not pretend otherwise: "Jawa" is lore text
    // in this campaign, not a race def (CLAUDE.md, shipping names), so a
    // Jawa colonist IS a humanlike at BodySize 1.0 and no threshold can
    // separate one from any other humanlike. Humanlikes therefore thread
    // rather than being blocked, and the fortress reads as "nothing big gets
    // in" rather than "only Jawas get in". Recorded as a build decision, not
    // an oversight.
    public class RM_CompProperties_BodySizeBarrier : CompProperties
    {
        // At or below this, the cell costs what the Thing's own pathCost
        // says and nothing else happens: the runway floor threads the
        // thicket as if it were open ground.
        public float passFreelyBodySize = 0.8f;

        // Above this, the cell is IMPASSABLE to the pathfinder — not
        // expensive, not walkable. See RM_MapComponent_BodySizeBarrier for
        // the engine channel that carries it.
        public float blockBodySize = 1.5f;

        // Per-cell movement cost charged to a pawn in the middle band.
        // Pawn_PathFollower caps a cell at 450 ticks, so 300 is ~33x a
        // normal walk step and still short of the cap — slow enough to read
        // as forcing a way through, not so slow that a colonist ordered to
        // cut a stand from the inside looks frozen.
        public int threadMoveCost = 300;

        // Per-cell movement cost charged to a pawn in the BLOCKED band that
        // is nonetheless standing on a barrier cell — spawned there by map
        // generation, dropped there by a pod, or caught by a stand that grew
        // around it. It must be able to walk out (see the map component's
        // "start cell" carve-out), and it does so at the engine's cap.
        public int trappedMoveCost = 450;

        public RM_CompProperties_BodySizeBarrier()
        {
            compClass = typeof(RM_CompBodySizeBarrier);
        }
    }

    // The Thing-side half, and a deliberate copy of CompContactVenom's
    // shape: it does nothing on tick and must never depend on ticking. All
    // it does is tell the map's RM_MapComponent_BodySizeBarrier which cell
    // it holds and on what terms; the map component owns every grid, every
    // lookup and the whole pathfinder-facing surface.
    public class RM_CompBodySizeBarrier : ThingComp
    {
        public RM_CompProperties_BodySizeBarrier Props => (RM_CompProperties_BodySizeBarrier)props;

        // The cell actually registered, cached rather than re-read from
        // parent.Position at deregistration time: Thing.DeSpawn clears the
        // thing's map/position state around the comp callback, so the only
        // cell we can be sure of removing is the one we put in. Same
        // reasoning, same bug, as CompContactVenom's.
        private IntVec3 registeredCell = IntVec3.Invalid;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            Register(parent.Map);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            Deregister(map);
        }

        private void Register(Map map)
        {
            if (map == null)
            {
                return;
            }

            RM_MapComponent_BodySizeBarrier tracker = map.GetComponent<RM_MapComponent_BodySizeBarrier>();
            if (tracker == null)
            {
                return;
            }

            registeredCell = parent.Position;
            tracker.RegisterCell(registeredCell, this);
        }

        private void Deregister(Map map)
        {
            if (map == null || !registeredCell.IsValid)
            {
                return;
            }

            map.GetComponent<RM_MapComponent_BodySizeBarrier>()?.DeregisterCell(registeredCell, this);
            registeredCell = IntVec3.Invalid;
        }
    }
}
