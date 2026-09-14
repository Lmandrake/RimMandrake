using System;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S4 (sump_kit_spec.md S4, "mouse-line telegraphy").
    // Generic per-map avoid-cell set built from REGISTERED dread sources —
    // deliberately NOT a hardcoded RUT_BeastBulge scan (the spec's own
    // text: "generic — any Patient-family map presence can register").
    // CompProperties_DreadSource/RM_CompDreadSource below is the whole
    // registration interface: any future dread source (a different
    // Patient-family set-piece, per the spec's own cross-reference to
    // sarlacc_spec.md / the Fever Wood) attaches the comp via its own def
    // or a patch and needs no defName-specific code here. RUT_BeastBulge
    // (S3, already shipped) is wired onto this MapComponent this pass via
    // RUT_BeastBulge_DreadRegistration.xml — a PATCH, not an edit to
    // RUT_BeastBulge.xml itself, per this pass's own "do not touch S3"
    // scope.
    //
    // Field shape cribbed from RM_MapComponent_VaporColumns
    // (FORGE_MECHANICS_1 F3, this same mod) — a flat bool[] over map cells,
    // painted via GenRadial — but event-driven (Register/Deregister) rather
    // than VaporColumns' own periodic full-map rescan. That distinction is
    // deliberate, not an oversight: VaporColumns scans for anonymous
    // emitters whose positions it does not otherwise know about, while a
    // dread source here always KNOWS the moment it spawns or despawns (its
    // own comp lifecycle), so a push registration is both cheaper and more
    // exact than a periodic pull scan would be, and needs no rescan
    // interval to tune.
    //
    // Not Scribe-saved, same reasoning VaporColumns' own header already
    // gives: the field is entirely derived from currently-spawned dread
    // sources, and every RM_CompDreadSource re-registers itself from
    // PostSpawnSetup on load (respawningAfterLoad included) — so a fresh
    // load reconstructs the identical field with no save-format owed.
    public class RM_MapComponent_DreadField : MapComponent
    {
        private readonly Dictionary<Thing, float> sources = new Dictionary<Thing, float>();

        private bool[] field;

        public RM_MapComponent_DreadField(Map map)
            : base(map)
        {
        }

        public void Register(Thing source, float radius)
        {
            if (source == null)
            {
                return;
            }

            sources[source] = radius;
            Rebuild();
        }

        public void Deregister(Thing source)
        {
            if (source == null)
            {
                return;
            }

            if (sources.Remove(source))
            {
                Rebuild();
            }
        }

        public bool IsDreaded(IntVec3 cell)
        {
            if (field == null || !cell.InBounds(map))
            {
                return false;
            }

            return field[map.cellIndices.CellToIndex(cell)];
        }

        private void Rebuild()
        {
            int n = map.cellIndices.NumGridCells;
            if (field == null || field.Length != n)
            {
                field = new bool[n];
            }
            else
            {
                Array.Clear(field, 0, n);
            }

            foreach (KeyValuePair<Thing, float> kv in sources)
            {
                if (!kv.Key.Spawned)
                {
                    continue; // stale entry (despawned without going through Deregister) — skip, do not paint
                }

                foreach (IntVec3 cell in GenRadial.RadialCellsAround(kv.Key.Position, kv.Value, useCenter: true))
                {
                    if (cell.InBounds(map))
                    {
                        field[map.cellIndices.CellToIndex(cell)] = true;
                    }
                }
            }
        }
    }

    //   <ThingDef ParentName="BuildingNaturalBase">
    //     <defName>RUT_BeastBulge</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_CompDreadSource">
    //         <radius>8</radius>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_DreadSource : CompProperties
    {
        // INVENTED, spec's own S4 text verbatim: "radius INVENTED: 8 cells."
        public float radius = 8f;

        public CompProperties_DreadSource()
        {
            compClass = typeof(RM_CompDreadSource);
        }
    }

    // The registration half of the interface: attach this to any Thing that
    // should make nearby cells "dreaded" for the lifetime it is spawned.
    // PostSpawnSetup/PostDeSpawn are the correct seams — both fire exactly
    // once per spawn/despawn cycle (respawningAfterLoad included on the
    // spawn side), matching RM_CompVaporDrifter's own posture in this mod:
    // a marker/registration comp that does no per-tick work of its own.
    public class RM_CompDreadSource : ThingComp
    {
        public CompProperties_DreadSource Props => (CompProperties_DreadSource)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            parent.Map?.GetComponent<RM_MapComponent_DreadField>()?.Register(parent, Props?.radius ?? 8f);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map?.GetComponent<RM_MapComponent_DreadField>()?.Deregister(parent);
        }
    }
}
