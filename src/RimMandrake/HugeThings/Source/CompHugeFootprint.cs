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
            RM_HugePlantExtension ext = Ext;
            int w = FootprintMath.Scaled(ext.trunkWidth, RM_HugeThingsSettings.MaxTrunkScale);
            int d = FootprintMath.Scaled(ext.Depth, RM_HugeThingsSettings.MaxTrunkScale);
            return FootprintMath.NorthRect(parent.Position, w, d).ExpandedBy(1);
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
            for (int i = blockers.Count - 1; i >= 0; i--)
            {
                Building_TrunkBlocker b = blockers[i];
                if (b == null || b.Destroyed || !b.Spawned)
                {
                    blockers.RemoveAt(i);
                }
                else if (want.IsEmpty || !want.Contains(b.Position))
                {
                    b.Destroy(DestroyMode.Vanish);
                    blockers.RemoveAt(i);
                }
            }
            if (want.IsEmpty) return;

            ThingDef blockerDef = HugeThingsDefOf.RM_HugeTrunkBlocker;
            foreach (IntVec3 c in want)
            {
                if (c == p.Position || !c.InBounds(map) || HasOwnBlocker(c)) continue;
                if (!CellTakesTrunk(c, map)) continue;
                Building_TrunkBlocker b = (Building_TrunkBlocker)ThingMaker.MakeThing(blockerDef);
                b.owner = p;
                GenSpawn.Spawn(b, c, map, WipeMode.VanishOrMoveAside);
                blockers.Add(b);
            }
        }

        private bool HasOwnBlocker(IntVec3 c)
        {
            for (int i = 0; i < blockers.Count; i++)
            {
                if (blockers[i].Position == c) return true;
            }
            return false;
        }

        /// <summary>
        /// A trunk grows only into cells it can take without destroying anything that matters: never over
        /// a building (any kind, including another trunk), a blueprint or frame, a pawn, a tree, another
        /// huge plant, or impassable ground. Small plants and filth are wiped; items are moved aside.
        /// The skipped cell simply stays open, and the next refresh tries again.
        /// </summary>
        public static bool CellTakesTrunk(IntVec3 c, Map map)
        {
            if (!c.Walkable(map)) return false;
            List<Thing> list = c.GetThingList(map);
            for (int i = 0; i < list.Count; i++)
            {
                Thing t = list[i];
                if (t is Pawn) return false;
                if (t.def.category == ThingCategory.Building) return false;
                if (t.def.IsBlueprint || t.def.IsFrame) return false;
                if (!t.def.destroyable) return false;
                if (t is Plant pl && (pl.def.plant.IsTree || pl.def.HasModExtension<RM_HugePlantExtension>())) return false;
            }
            return true;
        }
    }
}
