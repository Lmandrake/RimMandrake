using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // RM_GENSTEP_PLACED_SETPIECES_1. The shared def-list set-piece scatterer
    // both MIASMA_MECHANICS_1's M6 (warden-mother placement) and
    // SUMP_MECHANICS_1's S3 (tar-beast placement) name as a hard prerequisite
    // (miasma_kit_spec.md §M6, sump_kit_spec.md §S3) — both kit specs
    // describe it consistently, which is why it's one class, not two.
    //
    // Base contract confirmed against the live 1.6 decompile
    // (Verse/GenStep_Scatterer.cs, Verse/GenStep_ScatterThings.cs): the
    // scatterer framework already owns "pick N valid sites" —
    // Generate() calls CalculateFinalCount(map), then loops that many times
    // calling the abstract ScatterAt(loc, map, parms, count) at each site
    // TryFindScatterCell/CanScatterAt validated. A subclass's only required
    // job is ScatterAt; everything else (site count, validity predicates) is
    // already exposed as XML-settable fields on the base class:
    //   - site count: inherited `count` / `countPer10kCellsRange` — set
    //     per-GenStepDef-instance in XML (Miasma's ~2-4, Sump's ~1-2).
    //   - validity predicate: inherited `validators` / `fallbackValidators`
    //     (List<ScattererValidator>) — each kit writes its own
    //     ScattererValidator subclass (e.g. a brine-shallow-water validator
    //     reading M1's gradient axis, ordered strictly after
    //     RM_GenStep_GradientAxis; a deep-tar-far-from-edge validator) and
    //     lists it in its own GenStepDef XML. This class never sees either.
    // The only thing genuinely missing from the base class for this item's
    // use case is a content-agnostic "what gets spawned here" hook — vanilla
    // subclasses either hardcode one ThingDef (GenStep_ScatterThings) or pull
    // from randomly-weighted content groups (GenStep_ScatterGroup /
    // GenStep_ScatterGroupPrefabs, both surveyed and rejected: their weighted
    // RandomElementByWeight selection is exactly the "sometimes random"
    // shape both kits' ban text forbids — every site here spawns everything
    // its element list names, not a roll among options).
    //
    // RM_SetPieceElement below is the new hook, deliberately modeled on
    // Verse.ScattererValidator's own pattern (an abstract one-method class,
    // XML `Class=`-instantiated per list entry) rather than invented from
    // nothing: it is the idiomatic vanilla way to let a GenStepDef's XML
    // supply per-instance behavior without the framework class knowing the
    // content type. Miasma's GenStepDef lists a warden-mother pawn element +
    // a juvenile-cluster element + a RUT_CrecheMarker building element; Sump's
    // lists a single dormant-beast element. Neither PawnKindDef nor ThingDef
    // is referenced here — only in each kit's own RM_SetPieceElement
    // subclass, built as part of M6/S3's own remaining scope, not this item.
    //
    // Never random, structurally, not by discipline: this class (and its
    // GenStep_Scatterer base) has no commonality/chance field anywhere in
    // its inheritance chain, assigns no faction, and has exactly one entry
    // point — MapGenerator's GenStep pipeline calling Generate() because a
    // GenStepDef named this class, the same way every other GenStep runs.
    // There is no incident, no ambient roll, nothing else that could invoke
    // ScatterAt.
    public class RM_GenStep_PlacedSetPieces : GenStep_Scatterer
    {
        // Per-XML-instance spawn configuration: everything a chosen site
        // spawns, in order. Empty/omitted is a config error (logged, not a
        // silent no-op) rather than a valid "spawn nothing" state — a
        // GenStepDef with no elements is not doing its job.
        public List<RM_SetPieceElement> elements = new List<RM_SetPieceElement>();

        // Arbitrary but stable, matching the pattern every other GenStep in
        // the decompile uses (a fixed hash seed for its own scatter rolls,
        // independent of other GenSteps' RNG streams).
        public override int SeedPart => 1953847201;

        protected override void ScatterAt(IntVec3 loc, Map map, GenStepParams parms, int count = 1)
        {
            if (elements.NullOrEmpty())
            {
                Log.Error(
                    "[RM EnvironmentalHazards] RM_GenStep_PlacedSetPieces from def "
                    + def?.defName + " has no elements configured — nothing to spawn at " + loc + ".");
                return;
            }

            for (int i = 0; i < elements.Count; i++)
            {
                elements[i]?.SpawnAt(loc, map, parms);
            }
        }
    }

    // The generic "what to spawn" hook. One method, XML `Class=`-instantiable
    // per <li> — mirrors Verse.ScattererValidator exactly. A kit's own
    // subclass owns its content (PawnKindDef, ThingDef, cluster/offset
    // tuning); this class and RM_GenStep_PlacedSetPieces know nothing about
    // any of it.
    public abstract class RM_SetPieceElement
    {
        public abstract void SpawnAt(IntVec3 loc, Map map, GenStepParams parms);
    }
}
