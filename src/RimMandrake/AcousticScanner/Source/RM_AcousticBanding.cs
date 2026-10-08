using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.AcousticScanner
{
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
    // falls in (block side >= RM_AcousticKernel.MinBandSize = 7, clamped in
    // code whatever the settings file says), the grid origin is re-rolled on every
    // pulse so two pulses cannot be intersected down to a cell, and every heard block
    // bleeds a faint halo into its 8 neighbours so a lone hit never reads as one tight
    // square. No cell coordinate of a hit ever leaves this class. The arithmetic is
    // Kernel/RM_AcousticKernel.cs (Verse-free, fuzzed offline); this class only rolls the
    // grid origin and converts cells.
    public static class RM_AcousticBanding
    {
        public static List<RM_AcousticBand> Build(Map map, List<List<IntVec3>> hitsPerTarget,
            List<float> weightPerTarget, int bandSize, int seed)
        {
            int b = RM_AcousticKernel.EffectiveBand(bandSize);

            Rand.PushState(seed);
            int ox = Rand.Range(0, b);
            int oz = Rand.Range(0, b);
            Rand.PopState();

            var cells = new List<List<RM_KCell>>(hitsPerTarget.Count);
            for (int t = 0; t < hitsPerTarget.Count; t++)
            {
                var list = new List<RM_KCell>();
                List<IntVec3> hits = hitsPerTarget[t];
                if (hits != null)
                    for (int i = 0; i < hits.Count; i++) list.Add(new RM_KCell(hits[i].x, hits[i].z));
                cells.Add(list);
            }

            var result = new List<RM_AcousticBand>();
            foreach (RM_KBand kb in RM_AcousticKernel.Build(map.Size.x, map.Size.z, cells, weightPerTarget, bandSize, ox, oz))
                result.Add(new RM_AcousticBand { targetIndex = kb.targetIndex, tier = kb.tier, rect = new CellRect(kb.x, kb.z, kb.w, kb.h) });
            return result;
        }
    }
}
