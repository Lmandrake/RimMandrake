using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M12 build. The registration half of
    // RM_MapComponent_LivingRegrowth's interface — same push-registration
    // idiom as RM_CompDreadSource/RM_MapComponent_DreadField elsewhere in
    // this assembly. Attach to any marker building ("RUT_GreatboleCore" is
    // this kit's own instance) to make it the anchor of one living-dungeon
    // bole: on first spawn it flood-fills outward from its own position
    // over every contiguous cell whose edifice is regrowthThing, registers
    // that as its footprint, and hands the whole thing to the map
    // component. Nothing here names Greentide or the Greatbole.
    //
    //   <ThingDef>
    //     <defName>RUT_GreatboleCore</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_LivingBoleMarker">
    //         <regrowthThing>RUT_GreatboleHeartwood</regrowthThing>
    //         <sealantTerrain>RUT_ToxinSealant</sealantTerrain>
    //         <regrowDaysRange>3~6</regrowDaysRange>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_LivingBoleMarker : CompProperties
    {
        // What a mined-out chamber cell regrows back into, and what floor
        // marks a cell as permanently exempt. Required — see ConfigErrors.
        public ThingDef regrowthThing;
        public TerrainDef sealantTerrain;

        // Days (INVENTED, kit spec's own "3-6 per cell") before an empty,
        // enclosed, unsealed cell regrows.
        public IntRange regrowDaysRange = new IntRange(3, 6);

        // Creak-warning lead time before crushing starts, and the pulse
        // interval/damage once it does. Defaults match the kit spec's own
        // INVENTED numbers ("~1 in-game hour ahead" for the creak).
        public int creakWarningTicks = GenDate.TicksPerHour;
        public int crushIntervalTicks = 600;
        public float crushDamagePerHit = 12f;

        // Safety cap on the first-spawn flood fill, in case a malformed
        // heartwood blob (e.g. hand-placed by a future world-editing tool)
        // is accidentally unbounded.
        public int maxFootprintCells = 400;

        public CompProperties_LivingBoleMarker()
        {
            compClass = typeof(RM_CompLivingBoleMarker);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (regrowthThing == null)
            {
                yield return "CompProperties_LivingBoleMarker on " + parentDef?.defName + " has no regrowthThing.";
            }
        }
    }

    public class RM_CompLivingBoleMarker : ThingComp
    {
        private static readonly IntVec3[] EightDirs =
        {
            new IntVec3(1, 0, 0), new IntVec3(1, 0, 1), new IntVec3(0, 0, 1), new IntVec3(-1, 0, 1),
            new IntVec3(-1, 0, 0), new IntVec3(-1, 0, -1), new IntVec3(0, 0, -1), new IntVec3(1, 0, -1),
        };

        // -1 means "not yet registered". Scribed so a save/load never
        // re-runs the flood fill (which would silently shrink the
        // footprint once any chamber cell has been mined out — see
        // RM_MapComponent_LivingRegrowth's own class header).
        private int boleId = -1;

        public CompProperties_LivingBoleMarker Props => (CompProperties_LivingBoleMarker)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);

            if (boleId >= 0)
            {
                return; // already registered (a load restored the id) — do not re-flood-fill
            }

            RM_MapComponent_LivingRegrowth mc = parent.Map?.GetComponent<RM_MapComponent_LivingRegrowth>();
            if (mc == null || Props?.regrowthThing == null)
            {
                return;
            }

            List<IntVec3> footprint = FloodFillFootprint();
            boleId = mc.RegisterBole(
                parent.Position,
                footprint,
                Props.regrowthThing,
                Props.sealantTerrain,
                Props.regrowDaysRange,
                Props.creakWarningTicks,
                Props.crushIntervalTicks,
                Props.crushDamagePerHit);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            if (boleId >= 0)
            {
                map?.GetComponent<RM_MapComponent_LivingRegrowth>()?.DeregisterBole(boleId);
                boleId = -1;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref boleId, "boleId", -1);
        }

        // BFS outward from the marker's own cell over every contiguous
        // cell whose edifice is Props.regrowthThing, plus the marker's own
        // cell (which holds the marker itself, not the regrowth thing).
        // Correct exactly once — at first-ever spawn, while the blob is
        // still fully solid — which is the only time this runs; see
        // PostSpawnSetup above.
        private List<IntVec3> FloodFillFootprint()
        {
            Map map = parent.Map;
            IntVec3 start = parent.Position;
            List<IntVec3> result = new List<IntVec3> { start };
            HashSet<IntVec3> seen = new HashSet<IntVec3> { start };
            Queue<IntVec3> frontier = new Queue<IntVec3>();
            frontier.Enqueue(start);
            int cap = Mathf.Max(1, Props.maxFootprintCells);

            while (frontier.Count > 0 && result.Count < cap)
            {
                IntVec3 cur = frontier.Dequeue();
                for (int i = 0; i < EightDirs.Length; i++)
                {
                    IntVec3 next = cur + EightDirs[i];
                    if (!next.InBounds(map) || seen.Contains(next))
                    {
                        continue;
                    }
                    seen.Add(next);

                    Building edifice = next.GetEdifice(map);
                    if (edifice != null && edifice.def == Props.regrowthThing)
                    {
                        result.Add(next);
                        frontier.Enqueue(next);
                    }
                }
            }

            if (result.Count >= cap)
            {
                Log.Warning("[RM EnvironmentalHazards] RM_CompLivingBoleMarker on " + parent?.def?.defName
                    + " at " + start + " hit its maxFootprintCells cap (" + cap + ") flood-filling — footprint may be truncated.");
            }

            return result;
        }
    }
}
