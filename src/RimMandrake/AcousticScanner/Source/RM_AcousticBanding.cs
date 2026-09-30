using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.AcousticScanner
{
    public enum RM_AcousticTier : byte { Faint = 0, Moderate = 1, Strong = 2 }

    /// <summary>One square probability band: a whole block of the pulse's coarse grid.</summary>
    public struct RM_AcousticBand
    {
        public int targetIndex;
        public RM_AcousticTier tier;
        public CellRect rect;
    }

    // GRAVSHIP_ACOUSTIC_SCANNER_1 criterion: "The reading is always banded, never exact."
    //
    // Enforced here, not by XML: a hit is reported only as the coarse-grid BLOCK it
    // falls in (block side >= RM_AcousticScannerSettings.MinBandSize = 7, clamped in
    // code whatever the settings file says), the grid origin is re-rolled on every
    // pulse so two pulses cannot be intersected down to a cell, and every heard block
    // bleeds a faint halo into its 8 neighbours so a lone hit never reads as one tight
    // square. No cell coordinate of a hit ever leaves this class.
    public static class RM_AcousticBanding
    {
        public static List<RM_AcousticBand> Build(Map map, List<List<IntVec3>> hitsPerTarget,
            List<float> weightPerTarget, int bandSize, int seed)
        {
            var result = new List<RM_AcousticBand>();
            int b = Mathf.Max(bandSize, RM_AcousticScannerSettings.MinBandSize);

            Rand.PushState(seed);
            int ox = Rand.Range(0, b);
            int oz = Rand.Range(0, b);
            Rand.PopState();

            for (int t = 0; t < hitsPerTarget.Count; t++)
            {
                List<IntVec3> hits = hitsPerTarget[t];
                if (hits == null || hits.Count == 0) continue;
                float w = t < weightPerTarget.Count ? weightPerTarget[t] : 1f;

                var blocks = new Dictionary<IntVec2, float>();
                for (int i = 0; i < hits.Count; i++)
                {
                    var key = new IntVec2(FloorDiv(hits[i].x + ox, b), FloorDiv(hits[i].z + oz, b));
                    blocks.TryGetValue(key, out float cur);
                    blocks[key] = cur + w;
                }

                float max = 0f;
                foreach (float v in blocks.Values) if (v > max) max = v;
                if (max <= 0f) continue;

                var tiers = new Dictionary<IntVec2, RM_AcousticTier>();
                foreach (KeyValuePair<IntVec2, float> kv in blocks)
                {
                    float frac = kv.Value / max;
                    RM_AcousticTier tier = frac >= 0.6f ? RM_AcousticTier.Strong
                        : frac >= 0.25f ? RM_AcousticTier.Moderate : RM_AcousticTier.Faint;
                    // A single-block reading with only one hit is never better than moderate.
                    if (blocks.Count == 1 && hits.Count == 1) tier = RM_AcousticTier.Moderate;
                    tiers[kv.Key] = tier;
                }
                // Halo: neighbours of any heard block read at least faint.
                foreach (IntVec2 k in new List<IntVec2>(blocks.Keys))
                {
                    for (int dx = -1; dx <= 1; dx++)
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        var nk = new IntVec2(k.x + dx, k.z + dz);
                        if (!tiers.ContainsKey(nk)) tiers[nk] = RM_AcousticTier.Faint;
                    }
                }

                foreach (KeyValuePair<IntVec2, RM_AcousticTier> kv in tiers)
                {
                    int minX = kv.Key.x * b - ox;
                    int minZ = kv.Key.z * b - oz;
                    CellRect rect = new CellRect(minX, minZ, b, b).ClipInsideMap(map);
                    if (rect.Area <= 0) continue;
                    result.Add(new RM_AcousticBand { targetIndex = t, tier = kv.Value, rect = rect });
                }
            }
            return result;
        }

        private static int FloorDiv(int a, int b) => a >= 0 ? a / b : -((-a + b - 1) / b);
    }
}
