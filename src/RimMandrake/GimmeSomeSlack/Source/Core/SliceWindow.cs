// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// GSS round 9 scopes (live round 8, 2026-10-26): the probe's rebuildPhasesMs was the LAST rebuild's split, so the 86 ms
// window maximum came back with a 6-9 ms phase split beside it and could not be attributed. This keeps, per slice window
// ("slicereset"), the whole record of the slowest slice and of the slowest one no gen-0 collection was counted in: its
// phases, the part no phase timed (gap: a pause, not GSS work), the collector and heap deltas across it, whether a worker
// was running, and its ordinal and age in the window. Pure, so the SelfTest proves the phases shown belong to the max.
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>One frame rebuild's timings and context.</summary>
    internal sealed class SliceRecord
    {
        /// <summary>Phase name to ms, in Rebuild order (snapBase, snapClone, snapPower, tapIds, styles, build, tail).</summary>
        public readonly List<KeyValuePair<string, double>> Phases = new List<KeyValuePair<string, double>>();
        /// <summary>Sub-splits of a phase (the Build's bInputs, bReduce...): shown, not summed into the gap.</summary>
        public readonly List<KeyValuePair<string, double>> Detail = new List<KeyValuePair<string, double>>();
        public double TotalMs;
        /// <summary>Gen 0/1/2 collections counted across the slice; heap bytes after minus before (GC.GetTotalMemory(false)
        /// on the game, which an incremental collector can shrink mid-slice, so it may be negative).</summary>
        public int Gc0, Gc1, Gc2;
        public long HeapDelta;
        /// <summary>The lay worker / graph worker was running when the slice started.</summary>
        public bool LayBusy, GraphBusy;
        public int Landed, Pending;
        /// <summary>1-based ordinal in the window and ms from the window's reset to the slice's start.</summary>
        public int Ordinal;
        public double SinceResetMs;

        public double PhaseSumMs { get { double s = 0; foreach (var kv in Phases) s += kv.Value; return s; } }
        /// <summary>Total minus the timed phases: time no GSS phase owns (a stop-the-world pause lands here).</summary>
        public double GapMs => TotalMs - PhaseSumMs;

        public void Add(string phase, double ms) => Phases.Add(new KeyValuePair<string, double>(phase, ms));

        public string Json()
        {
            var sb = new StringBuilder("{");
            sb.Append("\"totalMs\":").Append(D(TotalMs)).Append(",\"gapMs\":").Append(D(GapMs)).Append(",\"phases\":{");
            for (int i = 0; i < Phases.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('"').Append(Phases[i].Key).Append("\":").Append(D(Phases[i].Value));
            }
            sb.Append("},\"detail\":{");
            for (int i = 0; i < Detail.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('"').Append(Detail[i].Key).Append("\":").Append(D(Detail[i].Value));
            }
            sb.Append("},\"gc0\":").Append(Gc0).Append(",\"gc1\":").Append(Gc1).Append(",\"gc2\":").Append(Gc2)
              .Append(",\"heapDelta\":").Append(HeapDelta)
              .Append(",\"layBusy\":").Append(LayBusy ? "true" : "false").Append(",\"graphBusy\":").Append(GraphBusy ? "true" : "false")
              .Append(",\"landed\":").Append(Landed).Append(",\"pending\":").Append(Pending)
              .Append(",\"ordinal\":").Append(Ordinal).Append(",\"sinceResetMs\":").Append(D(SinceResetMs)).Append('}');
            return sb.ToString();
        }

        private static string D(double v) => v.ToString("0.###", CultureInfo.InvariantCulture);
    }

    /// <summary>The slices since the last Reset: count, collector-tagged count, and the max and max-without-gen-0 records.</summary>
    internal sealed class SliceWindow
    {
        public int Slices, GcHits;
        public SliceRecord Max, MaxNoGc;
        /// <summary>The first slice after the reset (the spawn's own rebuild when the probe resets just before a spawn).</summary>
        public SliceRecord First;
        private long resetTs;
        private bool hasReset;

        public void Reset(long nowTs) { Slices = GcHits = 0; Max = MaxNoGc = First = null; resetTs = nowTs; hasReset = true; }

        /// <summary>Records a finished slice that started at <paramref name="startTs"/> (Stopwatch ticks at <paramref name="freq"/>).</summary>
        public void Record(SliceRecord r, long startTs, long freq)
        {
            Slices++;
            r.Ordinal = Slices;
            r.SinceResetMs = hasReset ? (startTs - resetTs) * 1000.0 / freq : -1;
            if (First == null) First = r;
            if (Max == null || r.TotalMs > Max.TotalMs) Max = r;
            if (r.Gc0 > 0) GcHits++;
            else if (MaxNoGc == null || r.TotalMs > MaxNoGc.TotalMs) MaxNoGc = r;
        }

        public string Json() =>
            "{\"slices\":" + Slices + ",\"gcHits\":" + GcHits + ",\"max\":" + (Max?.Json() ?? "null") +
            ",\"maxNoGc\":" + (MaxNoGc?.Json() ?? "null") + ",\"first\":" + (First?.Json() ?? "null") + "}";
    }
}
