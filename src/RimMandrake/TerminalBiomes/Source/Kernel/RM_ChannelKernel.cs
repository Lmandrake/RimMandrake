// Verse-free kernel of the Twilight Sea's channel current (RM_MapComponent_ChannelCurrent): the per-cell flow / lane / bank-band
// grids, what counts as current (surge widens it onto the banks), how fast something drifts, where one step goes (stop, sink,
// move) and the grab onto the widened band. The mod supplies standability, sinks and the actual move. Directions are the
// RM_FlowDir byte values (0 none, 1 N, 2 NE, 3 E, 4 SE, 5 S, 6 SW, 7 W, 8 NW). SelfTest/TerminalBiomesFuzz.cs compiles this
// file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.TerminalBiomes
{
    public enum ChannelStep { Stop, Sink, Moved }

    public sealed class ChannelField
    {
        public readonly int W, H;
        public byte[] Flow, Lane, Band;
        public bool Surge;

        public ChannelField(int w, int h) { W = w; H = h; Flow = new byte[w * h]; Lane = new byte[w * h]; Band = new byte[w * h]; }

        public bool InBounds(int x, int z) { return x >= 0 && z >= 0 && x < W && z < H; }
        private int Idx(int x, int z) { return z * W + x; }

        // Adopt saved grids; a grid of the wrong size is replaced by an empty one.
        public void Adopt(byte[] flow, byte[] lane, byte[] band)
        {
            int n = W * H;
            Flow = flow != null && flow.Length == n ? flow : new byte[n];
            Lane = lane != null && lane.Length == n ? lane : new byte[n];
            Band = band != null && band.Length == n ? band : new byte[n];
        }

        public void SetFlow(int x, int z, int dir, int lane)
        {
            if (!InBounds(x, z)) return;
            Flow[Idx(x, z)] = (byte)dir;
            Lane[Idx(x, z)] = (byte)lane;
        }

        // A bank cell points toward the channel unless it is itself a channel cell; band clamps to 0..2.
        public void SetBankBand(int x, int z, int towardChannel, int band)
        {
            if (!InBounds(x, z)) return;
            int i = Idx(x, z);
            if (Lane[i] == 0) Flow[i] = (byte)towardChannel;
            Band[i] = (byte)(band < 0 ? 0 : (band > 2 ? 2 : band));
        }

        public bool HasCurrent(int x, int z)
        {
            if (!InBounds(x, z)) return false;
            int i = Idx(x, z);
            if (Lane[i] != 0) return true;
            return Surge && Band[i] > 0 && Flow[i] != 0;
        }

        // 0 none, 1 margin, 2 centre. A surge turns a widened bank cell into margin.
        public int LaneAt(int x, int z)
        {
            if (!InBounds(x, z)) return 0;
            int i = Idx(x, z);
            if (Lane[i] != 0) return Lane[i];
            if (Surge && Band[i] > 0) return 1;
            return 0;
        }

        public int FlowAt(int x, int z) { return InBounds(x, z) ? Flow[Idx(x, z)] : 0; }
        public int BankBandAt(int x, int z) { return InBounds(x, z) ? Band[Idx(x, z)] : 0; }
    }

    public static class RM_ChannelKernel
    {
        public const int CentreCadenceTicks = 45;
        public const int MarginCadenceTicks = 90;

        public static bool Offset(int dir, out int dx, out int dz)
        {
            dx = 0; dz = 0;
            switch (dir)
            {
                case 1: dz = 1; return true;
                case 2: dx = 1; dz = 1; return true;
                case 3: dx = 1; return true;
                case 4: dx = 1; dz = -1; return true;
                case 5: dz = -1; return true;
                case 6: dx = -1; dz = -1; return true;
                case 7: dx = -1; return true;
                case 8: dx = -1; dz = 1; return true;
                default: return false;
            }
        }

        // Ticks between steps: centre 45, margin 90 (a surge turns margin into centre and doubles the centre rate; a float
        // harness caps a wearer at the margin pace); items drift at half the pawn rate; the strength setting divides it.
        public static int CadenceFor(int lane, bool surge, bool harnessCapped, bool isPawn, float strength)
        {
            bool centre = lane == 2 && !harnessCapped;
            if (surge && lane == 1 && !harnessCapped) centre = true;
            int cadence = centre ? CentreCadenceTicks : MarginCadenceTicks;
            if (surge && centre) cadence = Math.Max(1, cadence / 2);
            if (!isPawn) cadence *= 2;
            float s = Math.Max(0.05f, strength);
            return Math.Max(1, (int)Math.Round(cadence / s, MidpointRounding.AwayFromZero));
        }

        // One drift step from (x,z): Stop when there is no current, no direction, or the next cell is out of the map or not
        // standable; Sink when the next cell is a sink; otherwise Moved to (nx,nz).
        public static ChannelStep Step(ChannelField f, int x, int z, Func<int, int, bool> standable, Func<int, int, bool> isSink, out int nx, out int nz)
        {
            nx = x; nz = z;
            if (!f.HasCurrent(x, z)) return ChannelStep.Stop;
            if (!Offset(f.FlowAt(x, z), out int dx, out int dz)) return ChannelStep.Stop;
            nx = x + dx; nz = z + dz;
            if (!f.InBounds(nx, nz) || !standable(nx, nz)) return ChannelStep.Stop;
            return isSink(nx, nz) ? ChannelStep.Sink : ChannelStep.Moved;
        }

        // The surge grabs someone standing on the widened band two cells toward the bed (one if two is blocked).
        public static bool GrabTarget(ChannelField f, int x, int z, Func<int, int, bool> standable, out int tx, out int tz)
        {
            tx = x; tz = z;
            if (f.BankBandAt(x, z) <= 0) return false;
            if (!Offset(f.FlowAt(x, z), out int dx, out int dz)) return false;
            tx = x + 2 * dx; tz = z + 2 * dz;
            if (!f.InBounds(tx, tz) || !standable(tx, tz)) { tx = x + dx; tz = z + dz; }
            return f.InBounds(tx, tz) && standable(tx, tz);
        }
    }

    // Who is drifting and when each is next due.
    public sealed class ChannelBook<T> where T : class
    {
        private readonly Dictionary<T, int> next = new Dictionary<T, int>();
        public int Count { get { return next.Count; } }
        public bool Contains(T t) { return next.ContainsKey(t); }
        public void Register(T t, int now, int cadence) { next[t] = now + cadence; }
        public void Remove(T t) { next.Remove(t); }
        public bool TryGetDue(T t, out int due) { return next.TryGetValue(t, out due); }
        public List<T> Keys() { return new List<T>(next.Keys); }

        // Drop everyone the scan did not see this pass.
        public void Prune(ICollection<T> stillPresent)
        {
            List<T> stale = null;
            foreach (KeyValuePair<T, int> kv in next)
                if (!stillPresent.Contains(kv.Key)) (stale ?? (stale = new List<T>())).Add(kv.Key);
            if (stale != null) foreach (T t in stale) next.Remove(t);
        }
    }
}
