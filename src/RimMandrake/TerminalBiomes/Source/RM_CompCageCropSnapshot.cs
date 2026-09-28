using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_LIGHT_ECONOMY_1 §2.1. "Vanilla minification would kill a
    // grower's plants, so the cage carries a small comp that snapshots its
    // plants (def, growth) on uninstall and respawns them on reinstall —
    // the one C# this verb needs (tiny)."
    //
    // Verified sequence (RimWorld/MinifyUtility.cs, read this pass):
    // MakeMinified() calls thing.DeSpawnOrDeselect(...) BEFORE wrapping the
    // still-alive ThingWithComps as MinifiedThing.InnerThing — so
    // PostDeSpawn fires on this comp while parent.Map is still valid, the
    // parent object (and this comp's own saved fields) survive intact
    // inside the minified wrapper, and re-installing spawns that same
    // parent again via GenSpawn.Spawn, firing PostSpawnSetup(false) — the
    // same "just naturally spawned, not loaded from a save" signal used
    // elsewhere in this codebase (e.g. RM_Comp_WarblingGlow's phase reroll).
    public class RM_CompProperties_CageCropSnapshot : CompProperties
    {
        public RM_CompProperties_CageCropSnapshot()
        {
            compClass = typeof(RM_Comp_CageCropSnapshot);
        }
    }

    public class RM_Comp_CageCropSnapshot : ThingComp
    {
        private struct PlantSnapshot : IExposable
        {
            public ThingDef def;
            public IntVec3 offset; // relative to the cage's own position
            public float growth;

            public void ExposeData()
            {
                Scribe_Defs.Look(ref def, "def");
                Scribe_Values.Look(ref offset, "offset");
                Scribe_Values.Look(ref growth, "growth");
            }
        }

        private List<PlantSnapshot> snapshot = new List<PlantSnapshot>();

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref snapshot, "cageCropSnapshot", LookMode.Deep);
            if (snapshot == null)
            {
                snapshot = new List<PlantSnapshot>();
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            // respawningAfterLoad is FALSE both for a brand-new build and
            // for a post-minify reinstall — the two are told apart by
            // whether a snapshot was actually captured on the way out.
            if (!respawningAfterLoad && snapshot.Count > 0)
            {
                RespawnSnapshot();
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            // MinifyUtility.MakeMinified (the uninstall/pack-up path this
            // comp exists for) despawns with DestroyMode.Vanish. An actual
            // deconstruct/kill/destroy passes its own mode (Deconstruct,
            // Kill, KillFinalize, ...) — capturing then would destroy the
            // crops with nothing left alive to ever respawn them from the
            // snapshot, since the building itself is gone for good.
            if (mode == DestroyMode.Vanish)
            {
                CaptureSnapshot(map);
            }
            base.PostDeSpawn(map, mode);
        }

        private void CaptureSnapshot(Map map)
        {
            snapshot.Clear();
            if (map == null)
            {
                return;
            }
            foreach (IntVec3 cell in GenAdj.CellsOccupiedBy(parent))
            {
                Plant plant = cell.GetPlant(map);
                if (plant == null)
                {
                    continue;
                }
                snapshot.Add(new PlantSnapshot
                {
                    def = plant.def,
                    offset = cell - parent.Position,
                    growth = plant.Growth,
                });
                plant.Destroy(DestroyMode.Vanish);
            }
        }

        private void RespawnSnapshot()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            foreach (PlantSnapshot s in snapshot)
            {
                IntVec3 cell = parent.Position + s.offset;
                if (!cell.InBounds(map) || s.def == null)
                {
                    continue;
                }
                Plant existing = cell.GetPlant(map);
                if (existing != null)
                {
                    continue; // never overwrite something that grew there while the cage was away
                }
                Plant plant = (Plant)ThingMaker.MakeThing(s.def);
                plant.Growth = s.growth;
                GenSpawn.Spawn(plant, cell, map);
            }
            snapshot.Clear();
        }
    }
}
