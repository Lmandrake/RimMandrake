using System;
using System.Collections.Generic;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>What the layer needs to know about one living caster at refresh time. alive false means the
    /// caster despawned or left the map and must be dropped. hasProps false (or height not above 0) means it
    /// is registered but throws no shade.</summary>
    public struct RM_MovingCasterInfo
    {
        public bool alive;
        public int x, z;
        public bool hasProps;
        public float height;
        public int radius;
        public float depth;
    }

    public interface IRM_MovingCasterSource<TKey>
    {
        bool TryGetCaster(TKey key, out RM_MovingCasterInfo info);
    }

    /// <summary>
    /// LONGSHADE_GPT_ENRICHMENT_1 §2, the bookkeeping half: the moving-shade grid and the per-caster dirty
    /// rectangles, extracted from RM_MapComponent_ShadeGrid so the offline fuzz
    /// (Source/SelfTestFuzz, Utils/selftest_creaturebehaviors_fuzz.py) compiles this exact file. System only.
    /// The component owns one instance and supplies the live facts through IRM_MovingCasterSource; every
    /// statement below is the one that used to sit in RefreshMovingShade / Register / Unregister.
    /// </summary>
    public sealed class RM_MovingShadeLayer<TKey>
    {
        private sealed class CasterState
        {
            public int lastX = int.MinValue, lastZ = int.MinValue;
            public bool hasRect;
            public int minX, minZ, maxX, maxZ;
        }

        private float[] grid;
        private readonly Dictionary<TKey, CasterState> casters = new Dictionary<TKey, CasterState>();
        private bool dirty;

        /// <summary>The shade array, row-major (index = z * width + x), or null before the first refresh.</summary>
        public float[] Grid => grid;

        public int Count => casters.Count;

        public void Register(TKey key)
        {
            if (key != null && !casters.ContainsKey(key))
            {
                casters.Add(key, new CasterState());
                dirty = true;
            }
        }

        public void Unregister(TKey key, int width, int height)
        {
            if (key != null && casters.TryGetValue(key, out CasterState st))
            {
                if (st.hasRect && grid != null)
                {
                    RM_MovingShadeMath.ClearRect(grid, width, height, st.minX, st.minZ, st.maxX, st.maxZ);
                }
                casters.Remove(key);
                dirty = true;
            }
        }

        public float At(int index)
        {
            return grid == null ? 0f : grid[index];
        }

        /// <summary>Clears the old rectangle of every caster that moved and recasts every caster whose
        /// rectangle touched a cleared one. force: the sun vector or the arrays changed, so redo all of them.
        /// `on` false clears the layer and leaves it empty.</summary>
        public void Refresh(IRM_MovingCasterSource<TKey> src, int w, int h, bool force, bool on,
            bool directional, float dirX, float dirZ, float sunLengthPerHeight, float maxCastCells, float tipShade)
        {
            if (casters.Count == 0 && !force)
            {
                return;
            }
            int n = w * h;
            if (grid == null || grid.Length != n)
            {
                grid = new float[n];
                force = true;
            }
            if (force)
            {
                Array.Clear(grid, 0, n);
                foreach (CasterState st in casters.Values)
                {
                    st.hasRect = false;
                    st.lastX = int.MinValue;
                    st.lastZ = int.MinValue;
                }
            }
            List<TKey> gone = null;
            bool any = force || dirty;
            foreach (KeyValuePair<TKey, CasterState> kv in casters)
            {
                if (!src.TryGetCaster(kv.Key, out RM_MovingCasterInfo info) || !info.alive)
                {
                    (gone ??= new List<TKey>()).Add(kv.Key);
                    any = true;
                    continue;
                }
                if (info.x != kv.Value.lastX || info.z != kv.Value.lastZ)
                {
                    any = true;
                }
            }
            if (gone != null)
            {
                foreach (TKey t in gone)
                {
                    Unregister(t, w, h);
                }
            }
            dirty = false;
            if (!any)
            {
                return;
            }
            // Clear every old rectangle first, then cast every caster at its new place: overlapping shadows
            // of two casters stay whole.
            foreach (CasterState st in casters.Values)
            {
                if (st.hasRect)
                {
                    RM_MovingShadeMath.ClearRect(grid, w, h, st.minX, st.minZ, st.maxX, st.maxZ);
                    st.hasRect = false;
                }
            }
            if (!on)
            {
                return;
            }
            foreach (KeyValuePair<TKey, CasterState> kv in casters)
            {
                CasterState st = kv.Value;
                src.TryGetCaster(kv.Key, out RM_MovingCasterInfo info);
                st.lastX = info.x;
                st.lastZ = info.z;
                if (!info.hasProps || info.height <= 0f)
                {
                    continue;
                }
                float len = directional ? RM_SunHeatMath.ShadowLength(info.height, sunLengthPerHeight, maxCastCells) : 0f;
                if (!RM_MovingShadeMath.ShadowBounds(w, h, info.x, info.z, info.radius,
                    directional, dirX, dirZ, len, out st.minX, out st.minZ, out st.maxX, out st.maxZ))
                {
                    continue;
                }
                st.hasRect = true;
                RM_MovingShadeMath.CastBody(grid, w, h, info.x, info.z, info.radius,
                    directional, dirX, dirZ, len, tipShade, info.depth);
            }
        }
    }
}
