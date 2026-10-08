using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.HugeThings
{
    public class CompProperties_HugeFootprint : CompProperties
    {
        public CompProperties_HugeFootprint()
        {
            compClass = typeof(CompHugeFootprint);
        }
    }

    /// <summary>
    /// Keeps a huge plant's trunk blockers in step with the plant. Attached at startup to every plant def
    /// carrying RM_HugePlantExtension (HugeThingsStartup), never declared in XML.
    ///
    /// Holds no saved state: the blockers are ordinary saved Things that remember their owner, and the
    /// first refresh after spawn or load re-links them by scanning the largest possible trunk rect. All
    /// spawning happens from MapComponent_HugeFootprints (after mapgen / load, then on a slow cadence for
    /// growth), never inside SpawnSetup, so mapgen's own plant pass is never re-entered.
    /// </summary>
    public class CompHugeFootprint : ThingComp
    {
        private readonly List<Building_TrunkBlocker> blockers = new List<Building_TrunkBlocker>();
        private bool linked;

        public RM_HugePlantExtension Ext => parent.def.GetModExtension<RM_HugePlantExtension>();

        public Plant Plant => parent as Plant;

        public int BlockerCount => blockers.Count;

        public float GrowthScale
        {
            get
            {
                Plant p = Plant;
                if (p?.def.plant == null) return 1f;
                FloatRange v = p.def.plant.visualSizeRange;
                return FootprintMath.GrowthScale(v.min, v.max, p.Growth);
            }
        }

        public CellRect DesiredTrunk()
        {
            Plant p = Plant;
            RM_HugePlantExtension ext = Ext;
            if (p == null || ext == null || !p.Spawned || !RM_HugeThingsSettings.plantTrunkEnabled) return CellRect.Empty;
            return FootprintMath.TrunkRect(p.Position, ext, GrowthScale, p.Growth, RM_HugeThingsSettings.plantTrunkScale);
        }

        public CellRect? SelectRect()
        {
            Plant p = Plant;
            RM_HugePlantExtension ext = Ext;
            if (p == null || ext == null || !p.Spawned || !RM_HugeThingsSettings.plantSelectionEnabled) return null;
            return FootprintMath.SelectRect(p.Position, ext, GrowthScale, RM_HugeThingsSettings.plantTrunkScale);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            linked = false;
            parent.Map?.GetComponent<MapComponent_HugeFootprints>()?.Register(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map?.GetComponent<MapComponent_HugeFootprints>()?.Deregister(this);
            RemoveAll(map);
        }

        /// <summary>The largest rect any setting could ask for, for re-linking after load.</summary>
        private CellRect MaxRect()
        {
            return FootprintMath.MaxRect(parent.Position, Ext);
        }

        private void Relink(Map map)
        {
            blockers.Clear();
            foreach (IntVec3 c in MaxRect())
            {
                if (!c.InBounds(map)) continue;
                List<Thing> list = c.GetThingList(map);
                for (int i = 0; i < list.Count; i++)
                {
                    if (list[i] is Building_TrunkBlocker b && b.owner == parent && !blockers.Contains(b)) blockers.Add(b);
                }
            }
            linked = true;
        }

        private void RemoveAll(Map map)
        {
            if (!linked && map != null) Relink(map);
            for (int i = blockers.Count - 1; i >= 0; i--)
            {
                Building_TrunkBlocker b = blockers[i];
                if (b != null && !b.Destroyed) b.Destroy(DestroyMode.Vanish);
            }
            blockers.Clear();
        }

        /// <summary>Bring the blockers in line with the current growth and settings.</summary>
        public void Refresh()
        {
            Plant p = Plant;
            if (p == null || !p.Spawned || Ext == null) return;
            Map map = p.Map;
            if (!linked) Relink(map);

            CellRect want = DesiredTrunk();
            // drop blockers that are gone first, so the plan sees only live ones
            for (int i = blockers.Count - 1; i >= 0; i--)
            {
                Building_TrunkBlocker b = blockers[i];
                if (b == null || b.Destroyed || !b.Spawned) blockers.RemoveAt(i);
            }
            var cells = new List<long>(blockers.Count);
            for (int i = 0; i < blockers.Count; i++) cells.Add(RM_FootprintKernel.Pack(blockers[i].Position.x, blockers[i].Position.z));
            RM_TrunkPlan plan = RM_FootprintKernel.Plan(new RM_KRect(want.minX, want.minZ, want.Width, want.Height), p.Position.x, p.Position.z, cells,
                (x, z) => new IntVec3(x, 0, z).InBounds(map), (x, z) => CellTakesTrunk(new IntVec3(x, 0, z), map));
            for (int i = plan.destroyIndexes.Count - 1; i >= 0; i--)
            {
                Building_TrunkBlocker b = blockers[plan.destroyIndexes[i]];
                b.Destroy(DestroyMode.Vanish);
                blockers.RemoveAt(plan.destroyIndexes[i]);
            }
            if (plan.spawnCells.Count == 0) return;

            ThingDef blockerDef = HugeThingsDefOf.RM_HugeTrunkBlocker;
            foreach (long k in plan.spawnCells)
            {
                var c = new IntVec3(RM_FootprintKernel.PackedX(k), 0, RM_FootprintKernel.PackedZ(k));
                Building_TrunkBlocker b = (Building_TrunkBlocker)ThingMaker.MakeThing(blockerDef);
                b.owner = p;
                GenSpawn.Spawn(b, c, map, WipeMode.VanishOrMoveAside);
                blockers.Add(b);
            }
        }

        /// <summary>
        /// A trunk grows only into cells it can take without destroying anything that matters: never over
        /// a building (any kind, including another trunk), a blueprint or frame, a pawn, a tree, another
        /// huge plant, or impassable ground. Small plants and filth are wiped; items are moved aside.
        /// The skipped cell simply stays open, and the next refresh tries again.
        /// </summary>
        public static bool CellTakesTrunk(IntVec3 c, Map map)
        {
            bool walkable = c.Walkable(map), pawn = false, building = false, planned = false, indestructible = false, tree = false;
            List<Thing> list = c.GetThingList(map);
            for (int i = 0; i < list.Count; i++)
            {
                Thing t = list[i];
                if (t is Pawn) pawn = true;
                if (t.def.category == ThingCategory.Building) building = true;
                if (t.def.IsBlueprint || t.def.IsFrame) planned = true;
                if (!t.def.destroyable) indestructible = true;
                if (t is Plant pl && (pl.def.plant.IsTree || pl.def.HasModExtension<RM_HugePlantExtension>())) tree = true;
            }
            return RM_FootprintKernel.CellTakesTrunk(walkable, pawn, building, planned, indestructible, tree);
        }
    }
}
