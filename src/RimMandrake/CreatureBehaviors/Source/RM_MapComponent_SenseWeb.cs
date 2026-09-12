using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_KIT_BUILD_1, mechanic 1 (webwork_kit_spec.md §1) — "a network of
    // registered Things senses intruders and marks them for a species." Any
    // Thing carrying RM_CompSenseWebNode registers its occupied cells (and
    // itself, for RM_JobGiver_ChewAnchors's benefit) here on spawn/despawn.
    // On a scan interval, any pawn standing in a registered cell, or carrying
    // the (content-defined) egg item, gets the biome's felt-mark hediff if it
    // doesn't have one already.
    //
    // Deliberately name-blind: this component never hardcodes a species, a
    // hediff, or an item — it looks up RUT_Webwork_FeltMark / RUT_Webwork_Egg
    // by defName (soft, DefDatabase.GetNamedSilentFail) so it no-ops cleanly
    // on any map/mod-set where that content isn't loaded, and so a future
    // biome's own kit could reuse the same mechanism under a different name
    // without editing this file (spec's own "mechanism is generic" framing).
    //
    // Convergence/targeting off a felt-mark (spec's RM_JobGiver_SenseWebConverge)
    // is NOT built by this item — it needs the owner race's ThinkTree, which is
    // still unbuilt (WYYYSCHOKK_FERALISK_MERGE_1). This component tracks and
    // marks; a later item wires a JobGiver consumer.
    public class RM_MapComponent_SenseWeb : MapComponent
    {
        // Cell -> count of registered nodes there (supports overlapping webs
        // without one node's despawn blinding a cell another node still
        // covers).
        private Dictionary<IntVec3, int> registeredCells = new Dictionary<IntVec3, int>();
        private HashSet<Thing> nodes = new HashSet<Thing>();

        // ❓INVENTED scan interval (webwork_kit_spec.md §1: "~250 ticks").
        private const int ScanIntervalTicks = 250;
        private int ticksUntilScan = ScanIntervalTicks;

        public RM_MapComponent_SenseWeb(Map map) : base(map)
        {
        }

        public bool AnyRegisteredCells => registeredCells.Count > 0;

        // Live nodes carrying RM_ChewableExtension — RM_JobGiver_ChewAnchors's
        // search set, so anchor-beetles never need a map-wide thing scan.
        public IEnumerable<Thing> ChewableNodes => nodes.Where(n => n.Spawned && n.def.GetModExtension<RM_ChewableExtension>() != null);

        public void RegisterNode(Thing node)
        {
            if (node == null)
            {
                return;
            }
            nodes.Add(node);
            foreach (IntVec3 cell in node.OccupiedRect())
            {
                registeredCells.TryGetValue(cell, out int count);
                registeredCells[cell] = count + 1;
            }
        }

        public void DeregisterNode(Thing node)
        {
            if (node == null)
            {
                return;
            }
            nodes.Remove(node);
            foreach (IntVec3 cell in node.OccupiedRect())
            {
                if (!registeredCells.TryGetValue(cell, out int count))
                {
                    continue;
                }
                if (count <= 1)
                {
                    registeredCells.Remove(cell);
                }
                else
                {
                    registeredCells[cell] = count - 1;
                }
            }
        }

        public bool IsRegistered(IntVec3 cell)
        {
            return registeredCells.ContainsKey(cell);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!RM_CreatureBehaviorsSettings.senseWebEnabled)
            {
                return;
            }
            if (registeredCells.Count == 0)
            {
                return;
            }

            ticksUntilScan--;
            if (ticksUntilScan > 0)
            {
                return;
            }
            ticksUntilScan = ScanIntervalTicks;

            ScanAndMark();
        }

        private void ScanAndMark()
        {
            HediffDef feltMarkDef = DefDatabase<HediffDef>.GetNamedSilentFail("RUT_Webwork_FeltMark");
            if (feltMarkDef == null)
            {
                return; // biome content not loaded on this mod set; no-op
            }

            ThingDef eggDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_Webwork_Egg");

            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn == null || pawn.Dead || pawn.health?.hediffSet == null)
                {
                    continue;
                }

                bool inWeb = IsRegistered(pawn.Position);
                bool carriesEgg = eggDef != null && pawn.inventory?.innerContainer != null
                    && pawn.inventory.innerContainer.Contains(eggDef);

                if (!inWeb && !carriesEgg)
                {
                    continue;
                }
                if (pawn.health.hediffSet.HasHediff(feltMarkDef))
                {
                    continue;
                }

                pawn.health.AddHediff(feltMarkDef);
            }
        }
    }
}
