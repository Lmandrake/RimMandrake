// HOSE_PERF_BUILD_OFFLINE_REPLAY_HARNESS: the v1 corpus, generated deterministically (own xorshift, never System.Random, whose
// sequence is not promised across runtimes; the Mono lane must read the same traces). Until the live recorder exists (follow-up),
// these are the traces every commit replays. Each scenario is one stress the advisory names (section 5.3):
//   dry          10k quiet ticks: a tree grows or is felled now and then, a draw reads the world, a few pump orders
//   setup        a base going up: a wall run every 100 ticks, hoses wound in and laid again
//   rain         a rain burst: 400 puddle cells flip per tick for 600 ticks, read every tick
//   cold         a cold load: version bump and a settings flip at tick 0 (every hose lays at once)
//   dirty16383 / dirty16384 / dirty16385   exactly N cells change at tick 300, then a read: the 16,384-cell dirty capacity
//                cliff (HoseWorldDirty): only the 16,385th cell overflows into a whole rebuild
//   settings     a settings flip touching every hose at tick 1000
//   aligned      reel ids all congruent mod 250, so all 200 rechecks land on one tick; half their far ends walled in (no
//                route: the unbounded CheckReplan search, then a retract), half a tree on their corridor (replan, re-lay)
//   splitjoin    every 10 ticks a relay hose is wound in between two pump orders and laid again 5 ticks later
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.Replay
{
    internal sealed class XorShift
    {
        private ulong s;
        public XorShift(ulong seed) { s = seed == 0 ? 0x9E3779B97F4A7C15UL : seed; }
        public ulong Next()
        {
            s ^= s >> 12;
            s ^= s << 25;
            s ^= s >> 27;
            return s * 2685821657736338717UL;
        }
        public int Int(int lo, int hiExclusive) => lo + (int)(Next() % (ulong)(hiExclusive - lo));
    }

    internal static class TraceGen
    {
        public const int Size = 325, ReelCount = 200, TankCount = 100, RelayCount = 20;

        public static readonly string[] Scenarios =
            { "dry", "setup", "rain", "cold", "dirty16383", "dirty16384", "dirty16385", "settings", "aligned", "splitjoin" };

        public static Trace Make(string scenario)
        {
            var rng = new XorShift(0xC0FFEE1234UL);
            bool aligned = scenario == "aligned";
            Trace t = Base(rng, aligned);
            t.Name = scenario;
            var ev = new EventSink(t);
            switch (scenario)
            {
                case "dry":
                    t.Ticks = 10000;
                    for (int tick = 0; tick < t.Ticks; tick++)
                    {
                        if (tick % 37 == 5) TreeFlip(t, ev, rng, tick);
                        if (tick % 100 == 50) ev.Add(tick, 0, "read");
                        if (tick % 500 == 120) RandomMove(ev, rng, tick, 1);
                    }
                    break;
                case "setup":
                    t.Ticks = 5000;
                    for (int tick = 100; tick < t.Ticks; tick += 100)
                    {
                        int x = rng.Int(10, Size - 20), z = rng.Int(10, Size - 20);
                        if (rng.Int(0, 2) == 0) ev.Add(tick, 0, "rect", '#', x, z, x + 7, z);
                        else ev.Add(tick, 0, "rect", '#', x, z, x, z + 7);
                        ev.Add(tick, 0, "read");
                        if (tick % 400 == 0)
                        {
                            int reel = t.Reels[rng.Int(0, ReelCount)].Id;
                            ev.Add(tick, 1, "cut", '\0', reel);
                            ev.Add(tick + 200, 0, "lay", '\0', reel);
                        }
                    }
                    break;
                case "rain":
                    t.Ticks = 3000;
                    for (int tick = 2000; tick < 2600; tick++)
                    {
                        ev.Add(tick, 0, "rain", '\0', 400, tick * 131);
                        ev.Add(tick, 0, "read");
                    }
                    break;
                case "cold":
                    t.Ticks = 1000;
                    ev.Add(0, 0, "version");
                    ev.Add(0, 0, "settings");
                    break;
                case "dirty16383":
                case "dirty16384":
                case "dirty16385":
                    t.Ticks = 600;
                    ev.Add(300, 0, "rain", '\0', int.Parse(scenario.Substring(5)), 17);
                    ev.Add(300, 0, "read");
                    break;
                case "settings":
                    t.Ticks = 2000;
                    ev.Add(1000, 0, "settings");
                    break;
                case "aligned":
                    t.Ticks = 1000;
                    for (int k = 0; k < t.Reels.Count; k++)
                    {
                        TraceReel r = t.Reels[k];
                        if (k % 2 == 0) ev.Add(200, 0, "rect", '#', r.FarX - 1, r.FarZ - 1, r.FarX + 1, r.FarZ + 1);
                        else ev.Add(200, 0, "cell", 't', (r.X0 + r.FarX) / 2, (r.Z0 + r.FarZ) / 2);
                    }
                    break;
                case "splitjoin":
                    t.Ticks = 3000;
                    for (int tick = 10; tick < t.Ticks; tick += 10)
                    {
                        int i = 4 * ((tick / 10) % 50);                       // a relay reel (TankB < 0 for i % 4 == 0)
                        int src = t.Reels[i].TankA, dst = t.Reels[(i + 80) % ReelCount].TankA;   // the same relay
                        ev.Add(tick, 0, "move", '\0', src, dst, 5);           // warms the topology cache before the cut
                        ev.Add(tick, 0, "cut", '\0', t.Reels[i].Id);
                        ev.Add(tick, 1, "move", '\0', src, dst, 5);           // must not cross the cut
                        ev.Add(tick + 5, 0, "lay", '\0', t.Reels[i].Id);
                        TreeFlip(t, ev, rng, tick);
                        ev.Add(tick, 0, "read");
                    }
                    break;
                default:
                    throw new ArgumentException("unknown scenario '" + scenario + "' (known: " + string.Join(", ", Scenarios) + ")");
            }
            t.SortEvents();
            return t;
        }

        private sealed class EventSink
        {
            private readonly Trace t;
            private int seq;
            public EventSink(Trace t) { this.t = t; }
            public void Add(int tick, int phase, string kind, char c = '\0', params int[] args) =>
                t.Events.Add(new TraceEvent { Tick = tick, Phase = phase, Seq = seq++, Kind = kind, A = args, C = c });
        }

        private static void TreeFlip(Trace t, EventSink ev, XorShift rng, int tick)
        {
            for (int tries = 0; tries < 50; tries++)
            {
                int x = rng.Int(0, Size), z = rng.Int(0, Size);
                char c = t.At(x, z);
                if (c != '.' && c != 't') continue;
                ev.Add(tick, 0, "cell", c == '.' ? 't' : '.', x, z);   // the trace map is the tick-0 map: a flip back is a later event
                return;
            }
        }

        private static void RandomMove(EventSink ev, XorShift rng, int tick, int phase)
        {
            int a = rng.Int(0, TankCount), b = rng.Int(0, TankCount);
            if (a != b) ev.Add(tick, phase, "move", '\0', a, b, 20);
        }

        /// <summary>The shared map, reels and tanks: 325x325, ~15% rock in blobs, 25 walled rooms with a door each, a water band,
        /// 3% trees; 200 2x2 reels each with a reachable-looking far end 20-50 cells away; 100 tanks, 20 relays.</summary>
        private static Trace Base(XorShift rng, bool aligned)
        {
            var t = new Trace { Width = Size, Height = Size, Cells = new char[Size * Size] };
            for (int i = 0; i < t.Cells.Length; i++) t.Cells[i] = '.';
            int rock = 0;
            while (rock < t.Cells.Length * 15 / 100)
            {
                int cx = rng.Int(0, Size), cz = rng.Int(0, Size), rad = rng.Int(4, 13);
                for (int z = cz - rad; z <= cz + rad; z++)
                    for (int x = cx - rad; x <= cx + rad; x++)
                    {
                        if (x < 0 || z < 0 || x >= Size || z >= Size) continue;
                        if ((x - cx) * (x - cx) + (z - cz) * (z - cz) > rad * rad) continue;
                        if (t.Cells[z * Size + x] != 'r') { t.Cells[z * Size + x] = 'r'; rock++; }
                    }
            }
            for (int z = 0; z < Size; z++)
                for (int x = 200; x < 206; x++) t.Cells[z * Size + x] = '~';
            for (int room = 0; room < 25; room++)
            {
                int x0 = rng.Int(5, Size - 25), z0 = rng.Int(5, Size - 25), w = rng.Int(8, 17), h = rng.Int(8, 17);
                for (int z = z0; z <= z0 + h; z++)
                    for (int x = x0; x <= x0 + w; x++)
                    {
                        bool edge = z == z0 || z == z0 + h || x == x0 || x == x0 + w;
                        t.Cells[z * Size + x] = edge ? '#' : '.';
                    }
                t.Cells[z0 * Size + x0 + w / 2] = 'd';
            }
            for (int i = 0; i < t.Cells.Length; i++) if (t.Cells[i] == '.' && rng.Int(0, 100) < 3) t.Cells[i] = 't';

            for (int k = 0; k < TankCount; k++)
            {
                RM_TankMode mode = k % 3 == 0 ? RM_TankMode.Fill : k % 3 == 1 ? RM_TankMode.Empty : RM_TankMode.Store;
                int units = mode == RM_TankMode.Fill ? 100 : mode == RM_TankMode.Empty ? 900 : 500;
                t.Tanks.Add(new TraceTank { Id = k, Units = units, Cap = 1000, Liquid = k % 10 == 9 ? 1 : 0, Mode = mode });
            }
            var taken = new HashSet<int>();
            for (int i = 0; i < ReelCount; i++)
            {
                int x0, z0;
                do { x0 = rng.Int(3, Size - 5); z0 = rng.Int(3, Size - 5); }
                while (!Clear(t, x0, z0, taken));
                for (int dz = -1; dz <= 2; dz++) for (int dx = -1; dx <= 2; dx++) taken.Add((z0 + dz) * Size + x0 + dx);
                int fx, fz, tries = 0;
                do
                {
                    double ang = rng.Int(0, 3600) / 3600.0 * 2 * Math.PI, dist = rng.Int(20, 51);
                    fx = x0 + (int)Math.Round(Math.Cos(ang) * dist);
                    fz = z0 + (int)Math.Round(Math.Sin(ang) * dist);
                    tries++;
                }
                while (tries < 200 && (fx < 1 || fz < 1 || fx >= Size - 1 || fz >= Size - 1 || t.At(fx, fz) != '.'));
                double straight = Math.Sqrt((fx - x0) * (double)(fx - x0) + (fz - z0) * (double)(fz - z0));
                int tankA = i % TankCount;
                int tankB = i % 4 == 0 ? -((i / 4) % RelayCount + 1) : (i * 7 + 3) % TankCount;
                if (tankB == tankA) tankB = (tankB + 1) % TankCount;
                t.Reels.Add(new TraceReel
                {
                    Id = aligned ? 1000 + i * 250 : 1000 + i * 37,
                    X0 = x0, Z0 = z0, FarX = fx, FarZ = fz,
                    MaxLength = Math.Round(straight * 1.6 + 10),
                    TankA = tankA, TankB = tankB,
                });
            }
            return t;
        }

        private static bool Clear(Trace t, int x0, int z0, HashSet<int> taken)
        {
            for (int dz = 0; dz < 2; dz++)
                for (int dx = 0; dx < 2; dx++)
                {
                    int i = (z0 + dz) * Size + x0 + dx;
                    if (t.Cells[i] != '.' || taken.Contains(i)) return false;
                }
            return true;
        }
    }
}
