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
    /// A huge plant's DESIRED footprint (ground-contact cells) and its selection rect, both from the picture the engine
    /// draws right now. Attached at startup to every plant def carrying RM_HugePlantExtension (HugeThingsStartup).
    ///
    /// It never spawns anything itself: it hands its desired cells to MapComponent_HugeFootprints, which owns the map-wide
    /// claim ledger, plans which cells may safely close, and keeps exactly one blocker per claimed cell. Holds no saved
    /// state; the map component rebuilds everything from the plants and the blockers on load.
    /// </summary>
    public class CompHugeFootprint : ThingComp
    {
        // Plant.Print's random draws for this cell (see RM_HugeFootprintKernel's header). Replayed on each use: the variant
        // index depends on the CURRENT graphic's sub-graphic count.
        private float jitterX, jitterZ;
        private bool flip;
        private int variantIndex;

        private readonly SignatureCache<CellRect> selectCache = new SignatureCache<CellRect>();
        private FootprintSignature lastTaken;
        private bool takenOnce;

        public RM_HugePlantExtension Ext => parent.def.GetModExtension<RM_HugePlantExtension>();

        public Plant Plant => parent as Plant;

        public int OwnerId => parent.thingIDNumber;

        /// <summary>Replays Plant.Print's Rand sequence for this cell: jitter, flipUv, Graphic_Random index. The global Rand
        /// state is always restored, even if a graphic getter throws (GPT review #16).</summary>
        private void Roll()
        {
            Plant p = Plant;
            if (p == null || !p.Spawned) return;
            Graphic g = p.Graphic;
            int n = g is Graphic_Random gr ? gr.SubGraphicsCount : 0;
            Rand.PushState();
            try
            {
                Rand.Seed = p.Position.GetHashCode();
                Vector3 j = Gen.RandomHorizontalVector(0.05f);
                bool f = Rand.Bool;
                int idx = n > 0 ? Rand.Range(0, n) : 0;
                jitterX = j.x;
                jitterZ = j.z;
                flip = f;
                variantIndex = idx;
            }
            finally
            {
                Rand.PopState();
            }
        }

        /// <summary>The measured variant of the picture actually drawn, or the union stand-in when the drawn texture was
        /// never measured (an immature or leafless graphic, an art override).</summary>
        private HugePlantVariant DrawnVariant(RM_HugePlantExtension ext, out bool measured, out int maskId)
        {
            Graphic g = Plant.Graphic;
            if (g is Graphic_Random gr && gr.SubGraphicsCount > 0) g = gr.SubGraphicAtIndex(variantIndex);
            string path = g?.path;
            string name = path == null ? null : path.Substring(path.LastIndexOf('/') + 1);
            HugePlantVariant v = ext.Find(name);
            measured = v != null;
            maskId = measured ? ext.variants.IndexOf(v) + 1 : 0;
            return v ?? ext.Union;
        }

        /// <summary>Everything the footprint and the selection rect depend on right now.</summary>
        public FootprintSignature Signature(out HugeMask mask)
        {
            Plant p = Plant;
            RM_HugePlantExtension ext = Ext;
            Roll();
            HugePlantVariant v = DrawnVariant(ext, out bool measured, out int maskId);
            mask = ext.MaskFor(v, measured);
            return new FootprintSignature
            {
                RootX = p.Position.x,
                RootZ = p.Position.z,
                MaskId = maskId,
                DrawX = p.def.graphicData?.drawSize.x ?? 1f,
                Visual = p.def.plant.visualSizeRange.LerpThroughRange(p.Growth),
                JitterX = jitterX,
                JitterZ = jitterZ,
                BlockScale = RM_HugeThingsSettings.plantTrunkScale,
                Flip = flip,
                Measured = measured,
                Blocking = RM_HugeThingsSettings.PlantTrunkActive && ext.blockingSupported,
                Selecting = RM_HugeThingsSettings.PlantSelectionActive,
                OldEnough = p.Growth >= ext.minGrowthToBlock,
            };
        }

        private static HugeQuad QuadOf(FootprintSignature s)
            => RM_HugeFootprintKernel.Quad(s.RootX, s.RootZ, s.DrawX, s.Visual, s.JitterX, s.JitterZ);

        /// <summary>Ground-contact cells wanted now, as cell keys (empty when blocking is off or the plant is too young).</summary>
        public List<long> DesiredKeys()
        {
            Plant p = Plant;
            if (p == null || !p.Spawned || Ext == null) return new List<long>();
            FootprintSignature s = Signature(out HugeMask m);
            return DesiredKeys(s, m);
        }

        private static List<long> DesiredKeys(FootprintSignature s, HugeMask m)
        {
            if (!s.Blocking || !s.OldEnough) return new List<long>();
            return RM_HugeFootprintKernel.ContactCells(s.RootX, s.RootZ, QuadOf(s), s.BlockScale, s.Flip, m);
        }

        /// <summary>The cells this plant could EVER claim at full growth and the largest setting: the fixed planning window
        /// (Planner.Window) and the re-link scan, derived from the real transform (GPT review #7).</summary>
        public List<long> MaxKeys()
        {
            Plant p = Plant;
            RM_HugePlantExtension ext = Ext;
            FootprintSignature s = Signature(out HugeMask m);
            s.Visual = p.def.plant.visualSizeRange.max;
            s.BlockScale = RM_HugeThingsSettings.MaxTrunkScale;
            s.Blocking = true;
            s.OldEnough = true;
            HugeQuad q = QuadOf(s);
            List<long> keys = new List<long>();
            CellBox b = RM_HugeFootprintKernel.PictureBox(q, new HugeMask(), false);
            float bs = q.Size * s.BlockScale;
            int x0 = Mathf.FloorToInt(q.CentreX - bs / 2f), x1 = Mathf.CeilToInt(q.CentreX + bs / 2f);
            int z0 = Mathf.FloorToInt(q.MinZ), z1 = Mathf.CeilToInt(q.MinZ + bs);
            keys.Add(RM_HugeFootprintKernel.Key(System.Math.Min(b.MinX, x0), System.Math.Min(b.MinZ, z0)));
            keys.Add(RM_HugeFootprintKernel.Key(System.Math.Max(b.MaxX, x1), System.Math.Max(b.MaxZ, z1)));
            return keys;
        }

        /// <summary>The whole drawn picture plus every desired blocked cell; null when selection is off.</summary>
        public CellRect? SelectRect()
        {
            Plant p = Plant;
            if (p == null || Ext == null || !p.Spawned || !RM_HugeThingsSettings.PlantSelectionActive) return null;
            FootprintSignature sig = Signature(out HugeMask m);
            return selectCache.Get(sig, s =>
            {
                HugeQuad q = QuadOf(s);
                List<long> blocked = DesiredKeys(s, m);
                CellBox b = RM_HugeFootprintKernel.SelectBox(s.RootX, s.RootZ, RM_HugeFootprintKernel.PictureBox(q, m, s.Flip), blocked);
                return CellRect.FromLimits(b.MinX, b.MinZ, b.MaxX, b.MaxZ);
            });
        }

        /// <summary>True when the footprint may have changed since the map component last took it (growth, harvest,
        /// graphic, settings, position): GPT review #14.</summary>
        public bool Changed()
        {
            if (Plant == null || !Plant.Spawned || Ext == null) return false;
            FootprintSignature s = Signature(out _);
            return !takenOnce || !s.Equals(lastTaken);
        }

        public void MarkTaken()
        {
            lastTaken = Signature(out _);
            takenOnce = true;
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            takenOnce = false;
            selectCache.Clear();
            parent.Map?.GetComponent<MapComponent_HugeFootprints>()?.Register(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map?.GetComponent<MapComponent_HugeFootprints>()?.Deregister(this);
            selectCache.Clear();
        }

        /// <summary>Plants only TickLong (Plant never overrides Tick); growth changes there, so that is where a change is
        /// noticed. Harvest is caught by a PlantCollected postfix (HugeThingsCore).</summary>
        public override void CompTickLong()
        {
            base.CompTickLong();
            if (Changed()) parent.Map?.GetComponent<MapComponent_HugeFootprints>()?.MarkDirty(this);
        }
    }
}
