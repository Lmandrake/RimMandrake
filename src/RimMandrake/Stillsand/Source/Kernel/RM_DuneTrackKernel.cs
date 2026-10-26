using System.Collections.Generic;

namespace RimMandrake.Stillsand
{
    // Verse-free half of the Stillsand's footprint eraser (RM_DuneTrackEraser.cs): which SandGrid writers it hooks and the
    // per-cell tally that decides when moved sand has buried a print. The offline fuzz (SelfTest/Fuzz, family units) runs
    // exactly this code.
    public static class RM_DuneTrackKernel
    {
        /// <summary>Sand moved over a printed cell, summed since its print, at which the print is buried.</summary>
        public const float ChangeThreshold = 0.08f;

        /// <summary>
        /// Every 1.6 Verse.SandGrid method that writes a cell's depth, each hooked by the eraser. SetDepth: the MovingDunes
        /// engine, gravship landing, buildings clearing their footprint. AddDepth: weather (SteadyEnvironmentEffects piles
        /// sand under a sandy weather and wears it away by 1/180 a pass otherwise, outdoors and on heated terrain).
        /// DUNETRACK_ERASE_WIDEN_WEATHER_SAND: the eraser used to hook SetDepth only, so weather sand left prints intact.
        /// </summary>
        public static readonly string[] SandWriters = { "SetDepth", "AddDepth" };
    }

    /// <summary>
    /// DUNE_TRACK_ERASE_ACCUMULATE_1: sand moved over a printed cell since its print, per cell index. Steps smaller than the
    /// threshold add up; counting starts at the first move that finds a print on the cell and is dropped when the cell has
    /// none, so sand that moved BEFORE the print never counts against it. Session-only (one per SandGrid, never saved).
    /// </summary>
    public sealed class RM_SandMoveTally
    {
        private readonly Dictionary<int, float> moved = new Dictionary<int, float>();

        /// <summary>Cells holding a part-buried print.</summary>
        public int Count => moved.Count;

        /// <summary>
        /// One sand write on cell <paramref name="idx"/> that changed its depth by <paramref name="delta"/> (absolute).
        /// True = the print there is buried now: clear it.
        /// </summary>
        public bool Note(int idx, bool hasPrint, float delta)
        {
            if (!(delta > 0f)) return false;
            if (!hasPrint)
            {
                moved.Remove(idx);
                return false;
            }
            moved.TryGetValue(idx, out float sum);
            sum += delta;
            if (sum < RM_DuneTrackKernel.ChangeThreshold)
            {
                moved[idx] = sum;
                return false;
            }
            moved.Remove(idx);
            return true;
        }
    }
}
