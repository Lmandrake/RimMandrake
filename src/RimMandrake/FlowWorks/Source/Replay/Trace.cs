// HOSE_PERF_BUILD_OFFLINE_REPLAY_HARNESS: the replay's input. A trace is what the Verse-free hose and liquid cores READ,
// recorded at their boundary (design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md section 5.1): a map snapshot,
// the reels and tanks, and an ordered event stream (tick, phase, seq, event). Never an answer of our own algorithms: no lay,
// no route, no component and no settle result is ever an input.
//
// Text format "RMREPLAY 1" (versioned; runtime-neutral so a net472 build for the Mono lane reads it too):
//   RMREPLAY 1
//   name <scenario>        ticks <n>           map <w> <h>
//   row <z> <w chars>      . walkable  # wall  r rock  ~ water  d door  t tree (walkable, cost)  p puddle (walkable, cost)
//   reel <id> <x0> <z0> <farX> <farZ> <maxLen> <tankA> <tankB|-1>
//   tank <id> <units> <cap> <liquid> <mode Store|Fill|Empty|Dump>
//   ev <tick> <phase> <seq> <kind> <args...>
// Event kinds (phase 0 = before the hose tick, 1 = after it, before the settle, 2 = after the settle):
//   cell x z c           one cell becomes char c (a building, tree or terrain change: the map event marks it dirty)
//   rect x0 z0 x1 z1 c    every cell of the rectangle becomes c (a building footprint)
//   rain n salt           n distinct cells flip puddle <-> walkable, chosen by a hash of (salt, k): a rain burst
//   cut reel             the hose is wound in (retract/despawn): its link is dead from this instant
//   lay reel             the hose is (re)laid: link live again, its lay re-made at the next recheck
//   settings             a settings change touching every hose: version bump, every lay key dropped
//   version              anything else that bumps the map version (a cold load): the next read rebuilds whole
//   read                 something reads the hose world now (a lay, a draw): World() is called
//   move a b units       a transfer request from tank a to tank b across the network (a pump or player order)
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.Replay
{
    internal sealed class TraceReel
    {
        public int Id, X0, Z0, FarX, FarZ, TankA, TankB;
        public double MaxLength;
    }

    internal sealed class TraceTank
    {
        public int Id, Units, Cap, Liquid;
        public RM_TankMode Mode;
    }

    internal sealed class TraceEvent
    {
        public int Tick, Phase, Seq;
        public string Kind;
        public int[] A = new int[0];
        public char C;
    }

    internal sealed class Trace
    {
        public const string Magic = "RMREPLAY 1";
        public string Name = "unnamed";
        public int Ticks, Width, Height;
        public char[] Cells;   // z * Width + x
        public readonly List<TraceReel> Reels = new List<TraceReel>();
        public readonly List<TraceTank> Tanks = new List<TraceTank>();
        public readonly List<TraceEvent> Events = new List<TraceEvent>();

        public char At(int x, int z) => Cells[z * Width + x];

        /// <summary>Events in replay order: tick, phase, seq. A recorder's seq is its own arrival order; the sort is stable.</summary>
        public void SortEvents()
        {
            var keyed = new List<KeyValuePair<long, TraceEvent>>(Events.Count);
            for (int i = 0; i < Events.Count; i++)
            {
                TraceEvent e = Events[i];
                keyed.Add(new KeyValuePair<long, TraceEvent>(((long)e.Tick << 40) | ((long)e.Phase << 32) | (uint)e.Seq, e));
            }
            keyed.Sort((a, b) => a.Key.CompareTo(b.Key));
            Events.Clear();
            foreach (var kv in keyed) Events.Add(kv.Value);
        }

        public void Save(string path)
        {
            var sb = new StringBuilder();
            sb.Append(Magic).Append('\n');
            sb.Append("name ").Append(Name).Append('\n');
            sb.Append("ticks ").Append(Ticks).Append('\n');
            sb.Append("map ").Append(Width).Append(' ').Append(Height).Append('\n');
            for (int z = 0; z < Height; z++) sb.Append("row ").Append(z).Append(' ').Append(Cells, z * Width, Width).Append('\n');
            foreach (TraceReel r in Reels)
                sb.Append("reel ").Append(r.Id).Append(' ').Append(r.X0).Append(' ').Append(r.Z0).Append(' ').Append(r.FarX).Append(' ').Append(r.FarZ)
                  .Append(' ').Append(r.MaxLength.ToString("R", CultureInfo.InvariantCulture)).Append(' ').Append(r.TankA).Append(' ').Append(r.TankB).Append('\n');
            foreach (TraceTank t in Tanks)
                sb.Append("tank ").Append(t.Id).Append(' ').Append(t.Units).Append(' ').Append(t.Cap).Append(' ').Append(t.Liquid).Append(' ').Append(t.Mode).Append('\n');
            foreach (TraceEvent e in Events)
            {
                sb.Append("ev ").Append(e.Tick).Append(' ').Append(e.Phase).Append(' ').Append(e.Seq).Append(' ').Append(e.Kind);
                foreach (int a in e.A) sb.Append(' ').Append(a);
                if (e.C != '\0') sb.Append(' ').Append(e.C);
                sb.Append('\n');
            }
            File.WriteAllText(path, sb.ToString());
        }

        public static Trace Load(string path)
        {
            var t = new Trace();
            int lineNo = 0;
            foreach (string raw in File.ReadLines(path))
            {
                lineNo++;
                string line = raw.TrimEnd('\r');
                if (lineNo == 1)
                {
                    if (line != Magic) throw new InvalidDataException(path + ": not a " + Magic + " trace (first line '" + line + "')");
                    continue;
                }
                if (line.Length == 0 || line[0] == '#') continue;
                string[] f = line.Split(' ');
                switch (f[0])
                {
                    case "name": t.Name = f[1]; break;
                    case "ticks": t.Ticks = I(f[1]); break;
                    case "map":
                        t.Width = I(f[1]); t.Height = I(f[2]);
                        t.Cells = new char[t.Width * t.Height];
                        break;
                    case "row":
                    {
                        int z = I(f[1]);
                        if (f[2].Length != t.Width) throw new InvalidDataException(path + ":" + lineNo + ": row width " + f[2].Length);
                        f[2].CopyTo(0, t.Cells, z * t.Width, t.Width);
                        break;
                    }
                    case "reel":
                        t.Reels.Add(new TraceReel { Id = I(f[1]), X0 = I(f[2]), Z0 = I(f[3]), FarX = I(f[4]), FarZ = I(f[5]),
                            MaxLength = double.Parse(f[6], CultureInfo.InvariantCulture), TankA = I(f[7]), TankB = I(f[8]) });
                        break;
                    case "tank":
                        t.Tanks.Add(new TraceTank { Id = I(f[1]), Units = I(f[2]), Cap = I(f[3]), Liquid = I(f[4]),
                            Mode = (RM_TankMode)Enum.Parse(typeof(RM_TankMode), f[5]) });
                        break;
                    case "ev":
                    {
                        var e = new TraceEvent { Tick = I(f[1]), Phase = I(f[2]), Seq = I(f[3]), Kind = f[4] };
                        var args = new List<int>();
                        for (int k = 5; k < f.Length; k++)
                        {
                            if (f[k].Length == 1 && !char.IsDigit(f[k][0]) && f[k][0] != '-') e.C = f[k][0];
                            else args.Add(I(f[k]));
                        }
                        e.A = args.ToArray();
                        t.Events.Add(e);
                        break;
                    }
                    default: throw new InvalidDataException(path + ":" + lineNo + ": unknown record '" + f[0] + "'");
                }
            }
            if (t.Cells == null) throw new InvalidDataException(path + ": no map record");
            t.SortEvents();
            return t;
        }

        private static int I(string s) => int.Parse(s, CultureInfo.InvariantCulture);
    }
}
