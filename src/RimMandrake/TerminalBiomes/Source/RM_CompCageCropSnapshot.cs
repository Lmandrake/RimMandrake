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

    // CAGE_CROP_SNAPSHOT_FIDELITY_1: the snapshot used to destroy the plants and grow fresh ones from (def, growth),
    // losing health and age, at world-space offsets that land wrong when the cage is reinstalled rotated; and it was
    // a struct under LookMode.Deep. Now the PLANTS THEMSELVES are despawned into a ThingOwner the cage carries (so
    // everything about them survives, including through a save made while minified) with each one's cell stored
    // cage-local (rotation-normalised), and are spawned back at the same cage-local cell under the new rotation.
    public class RM_CageCropRecord : IExposable
    {
        public int thingId;     // the held plant's thingIDNumber
        public IntVec3 local;   // its cell relative to the cage, rotated back to Rot4.North

        public void ExposeData()
        {
            Scribe_Values.Look(ref thingId, "thingId");
            Scribe_Values.Look(ref local, "local");
        }
    }

    public class RM_Comp_CageCropSnapshot : ThingComp, IThingHolder
    {
        // Saves from before CAGE_CROP_SNAPSHOT_FIDELITY_1: (def, offset, growth), respawned fresh as before.
        private class LegacySnapshot : IExposable
        {
            public ThingDef def;
            public IntVec3 offset;
            public float growth;

            public void ExposeData()
            {
                Scribe_Defs.Look(ref def, "def");
                Scribe_Values.Look(ref offset, "offset");
                Scribe_Values.Look(ref growth, "growth");
            }
        }

        private ThingOwner<Thing> held;
        private List<RM_CageCropRecord> records = new List<RM_CageCropRecord>();
        private List<LegacySnapshot> legacy = new List<LegacySnapshot>();

        public ThingOwner GetDirectlyHeldThings()
        {
            return held ?? (held = new ThingOwner<Thing>(this));
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Deep.Look(ref held, "cageCropsHeld", this);
            Scribe_Collections.Look(ref records, "cageCropRecords", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                if (legacy.Count > 0) Scribe_Collections.Look(ref legacy, "cageCropSnapshot", LookMode.Deep);
            }
            else
            {
                Scribe_Collections.Look(ref legacy, "cageCropSnapshot", LookMode.Deep);
            }
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (held == null) held = new ThingOwner<Thing>(this);
                if (records == null) records = new List<RM_CageCropRecord>();
                if (legacy == null) legacy = new List<LegacySnapshot>();
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            // respawningAfterLoad is FALSE both for a brand-new build and for a post-minify reinstall — the two
            // are told apart by whether anything was actually captured on the way out.
            if (!respawningAfterLoad)
            {
                RespawnHeld();
                RespawnLegacy();
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            // MinifyUtility.MakeMinified (the uninstall/pack-up path this comp exists for) despawns with
            // DestroyMode.Vanish. An actual deconstruct/kill/destroy passes its own mode — capturing then would
            // carry crops away inside a building that is gone for good.
            if (mode == DestroyMode.Vanish)
            {
                Capture(map);
            }
            base.PostDeSpawn(map, mode);
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            held?.ClearAndDestroyContents(); // the cage itself is gone (destroyed while minified): so are its crops
        }

        private static IntVec3 ToLocal(IntVec3 offset, Rot4 rot)
        {
            return offset.RotatedBy(new Rot4((4 - rot.AsInt) % 4));
        }

        private void Capture(Map map)
        {
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
                plant.DeSpawn(DestroyMode.Vanish);
                if (!GetDirectlyHeldThings().TryAdd(plant, canMergeWithExistingStacks: false))
                {
                    GenSpawn.Spawn(plant, cell, map); // could not hold it: leave it growing where it was
                    continue;
                }
                records.Add(new RM_CageCropRecord { thingId = plant.thingIDNumber, local = ToLocal(cell - parent.Position, parent.Rotation) });
            }
        }

        private void RespawnHeld()
        {
            Map map = parent.Map;
            if (map == null || held == null || held.Count == 0)
            {
                records.Clear();
                return;
            }
            foreach (Thing t in new List<Thing>(held))
            {
                RM_CageCropRecord rec = records.Find(r => r.thingId == t.thingIDNumber);
                IntVec3 cell = rec != null ? parent.Position + rec.local.RotatedBy(parent.Rotation) : IntVec3.Invalid;
                held.Remove(t);
                if (!cell.IsValid || !cell.InBounds(map) || cell.GetPlant(map) != null)
                {
                    t.Destroy(DestroyMode.Vanish); // never overwrite something that grew there while the cage was away
                    continue;
                }
                GenSpawn.Spawn(t, cell, map);
            }
            records.Clear();
        }

        private void RespawnLegacy()
        {
            Map map = parent.Map;
            if (map == null || legacy.Count == 0)
            {
                legacy.Clear();
                return;
            }
            foreach (LegacySnapshot s in legacy)
            {
                IntVec3 cell = parent.Position + s.offset;
                if (!cell.InBounds(map) || s.def == null || cell.GetPlant(map) != null)
                {
                    continue;
                }
                Plant plant = (Plant)ThingMaker.MakeThing(s.def);
                plant.Growth = s.growth;
                GenSpawn.Spawn(plant, cell, map);
            }
            legacy.Clear();
        }
    }
}
