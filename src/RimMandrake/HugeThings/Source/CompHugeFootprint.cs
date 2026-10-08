using System.Collections.Generic;
using RimWorld;
using UnityEngine;
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
    /// Keeps a huge plant's ground-contact blockers and its selection rect in step with the plant as drawn.
    /// Attached at startup to every plant def carrying RM_HugePlantExtension (HugeThingsStartup), never in XML.
    ///
    /// Holds no saved state: the blockers are ordinary saved Things that remember their owner, and the first
    /// refresh after spawn or load re-links them by scanning the largest possible quad. All spawning happens
    /// from MapComponent_HugeFootprints (after mapgen / load, then on a slow cadence for growth), never inside
    /// SpawnSetup, so mapgen's own plant pass is never re-entered.
    /// </summary>
    public class CompHugeFootprint : ThingComp
    {
        private readonly List<Building_TrunkBlocker> blockers = new List<Building_TrunkBlocker>();
        private bool linked;

        // Plant.Print's random draws, fixed by the plant's cell (see FootprintMath's class note). Replayed on each
        // use, not cached: the variant index depends on the CURRENT graphic's sub-graphic count.
        private float jitterX, jitterZ;
        private bool flip;
        private int variantIndex;

        // Selection cache, keyed on what can change it.
        private float cachedGrowth = -1f;
        private int cachedStamp = -1;
        private Graphic cachedGraphic;
        private CellRect cachedSelect;

        public RM_HugePlantExtension Ext => parent.def.GetModExtension<RM_HugePlantExtension>();

        public Plant Plant => parent as Plant;

        public int BlockerCount => blockers.Count;

        public bool Flipped
        {
            get
            {
                Roll();
                return flip;
            }
        }

        /// <summary>Replays Plant.Print's Rand sequence for this cell: jitter, flipUv, Graphic_Random index.</summary>
        private void Roll()
        {
            Plant p = Plant;
            if (p == null || !p.Spawned) return;
            Rand.PushState();
            Rand.Seed = p.Position.GetHashCode();
            Vector3 j = Gen.RandomHorizontalVector(0.05f);
            bool f = Rand.Bool;
            int n = p.Graphic is Graphic_Random gr ? gr.SubGraphicsCount : 0;
            int idx = n > 0 ? Rand.Range(0, n) : 0;
            Rand.PopState();
            jitterX = j.x;
            jitterZ = j.z;
            flip = f;
            variantIndex = idx;
        }

        /// <summary>The quad the engine draws right now.</summary>
        public HugeQuad Quad()
        {
            Plant p = Plant;
            Roll();
            float visual = p.def.plant.visualSizeRange.LerpThroughRange(p.Growth);
            return FootprintMath.Quad(p.Position, p.def.graphicData?.drawSize.x ?? 1f, visual, jitterX, jitterZ);
        }

        /// <summary>The measured variant of the picture actually drawn, or the union stand-in when the drawn
        /// texture was never measured (an immature or leafless graphic, an art override).</summary>
        public HugePlantVariant DrawnVariant(out bool measured)
        {
            RM_HugePlantExtension ext = Ext;
            Roll();
            Graphic g = Plant.Graphic;
            if (g is Graphic_Random gr && gr.SubGraphicsCount > 0) g = gr.SubGraphicAtIndex(variantIndex);
            string path = g?.path;
            string name = path == null ? null : path.Substring(path.LastIndexOf('/') + 1);
            HugePlantVariant v = ext.Find(name);
            measured = v != null;
            return v ?? ext.Union;
        }

        /// <summary>Ground-contact cells wanted now (empty when blocking is off or the plant is too young).</summary>
        public List<IntVec3> DesiredBlocked()
        {
            Plant p = Plant;
            RM_HugePlantExtension ext = Ext;
            if (p == null || ext == null || !p.Spawned || !RM_HugeThingsSettings.plantTrunkEnabled
                || p.Growth < ext.minGrowthToBlock)
            {
                return new List<IntVec3>();
            }
            HugePlantVariant v = DrawnVariant(out bool measured);
            return FootprintMath.ContactCells(p.Position, Quad(), RM_HugeThingsSettings.plantTrunkScale, Flipped,
                                              ext.MaskFor(v, measured));
        }

        /// <summary>The whole drawn picture plus every blocked cell; null when selection is off.</summary>
        public CellRect? SelectRect()
        {
            Plant p = Plant;
            RM_HugePlantExtension ext = Ext;
            if (p == null || ext == null || !p.Spawned || !RM_HugeThingsSettings.plantSelectionEnabled) return null;
            Graphic g = p.Graphic;
            if (cachedStamp == RM_HugeThingsSettings.Stamp() && cachedGrowth == p.Growth && cachedGraphic == g) return cachedSelect;

            HugePlantVariant v = DrawnVariant(out bool measured);
            cachedSelect = FootprintMath.SelectRect(p.Position, Quad(), ext.MaskFor(v, measured), Flipped, DesiredBlocked());
            cachedStamp = RM_HugeThingsSettings.Stamp();
            cachedGrowth = p.Growth;
            cachedGraphic = g;
            return cachedSelect;
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            linked = false;
            cachedStamp = -1;
            parent.Map?.GetComponent<MapComponent_HugeFootprints>()?.Register(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map?.GetComponent<MapComponent_HugeFootprints>()?.Deregister(this);
            RemoveAll(map);
        }

        /// <summary>The largest area any growth or setting could block, for re-linking after load.</summary>
        private CellRect MaxRect()
        {
            Plant p = Plant;
            float side = (p.def.graphicData?.drawSize.x ?? 1f) * p.def.plant.visualSizeRange.max
                       * RM_HugeThingsSettings.MaxTrunkScale;
            int r = Mathf.CeilToInt(side / 2f) + 1;
            return CellRect.FromLimits(p.Position.x - r, p.Position.z - 1, p.Position.x + r, p.Position.z + Mathf.CeilToInt(side) + 1);
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

        /// <summary>Bring the blockers in line with the current growth, drawn picture and settings.</summary>
        public void Refresh()
        {
            Plant p = Plant;
            if (p == null || !p.Spawned || Ext == null) return;
            Map map = p.Map;
            if (!linked) Relink(map);

            HashSet<IntVec3> want = new HashSet<IntVec3>(DesiredBlocked());
            for (int i = blockers.Count - 1; i >= 0; i--)
            {
                Building_TrunkBlocker b = blockers[i];
                if (b == null || b.Destroyed || !b.Spawned)
                {
                    blockers.RemoveAt(i);
                }
                else if (!want.Contains(b.Position))
                {
                    b.Destroy(DestroyMode.Vanish);
                    blockers.RemoveAt(i);
                }
            }
            if (want.Count == 0) return;

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
