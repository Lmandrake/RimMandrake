// HOSE_INVALIDATION_REWIRE_EVENT_DRIVEN part (b): RM_HoseLinkCache (PRODUCTION, ../Machinery/RM_HoseLinkCache.cs) against a
// brute-force oracle. A Verse-free model of RM_HoseLinks: reels with a body port and a free-end port, each read through its
// own 60-tick phased cache (CompHoseReel.Port / FreeEndOf) that bumps the reel's serial when a re-read differs and re-reads
// at once when the cached thing despawned. The ORACLE is the old walk: every Refresh evaluates every reel. The DRIVER mirrors
// RM_HoseLinks.RefreshCore (Begin, Due with key / gone / audit, key taken after the read, Store, End, signature fold). Both
// see the same world; every Refresh must yield the same (ok, inlet id, far id) per reel and the same rebuild decision.
// Fault probes: the same run with the gone check, the serial or the down flag dropped must go red (the oracle can see).
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseLinkCacheChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "hoselinkcache: " + msg);
        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(System.IO.Path.Combine(rel));

        private sealed class Thing { public int Id; public bool Spawned = true; public bool Foreign; }

        private sealed class Reel
        {
            public int Id;
            public bool Laid = true;
            public int FarX, FarZ, Role;          // key inputs (read directly, as Ends reads carry / far / role)
            public Thing TrueBody, TrueEnd;       // what a re-read finds now
        }

        /// <summary>One reader's caches and reel serials (the oracle and the driver each own one, since reading a cache changes
        /// it; a forced re-read, which in the game updates the one shared cache, is applied to both).</summary>
        private sealed class Caches
        {
            public readonly Dictionary<Reel, (int at, Thing v)> body = new(), end = new();
            public readonly Dictionary<Reel, int> serial = new();
            public int Serial(Reel r) => serial.TryGetValue(r, out int n) ? n : 0;

            public Thing Read(Dictionary<Reel, (int at, Thing v)> d, Reel r, Thing truth, int now, bool force)
            {
                if (!force && d.TryGetValue(r, out var c) && HoseLive.PhasedFresh(now, c.at, 60, r.Id) && (c.v == null || c.v.Spawned)) return c.v;
                bool had = d.TryGetValue(r, out var old);
                d[r] = (now, truth);
                if (!had || old.v != truth) serial[r] = Serial(r) + 1;   // CompHoseReel.linkInputSerial++
                return truth;
            }
        }

        private sealed class World
        {
            public readonly List<Reel> reels = new();
            public readonly List<Thing> things = new();
            public bool theft, roles = true;
            public int revision;
        }

        private static bool RoleOk(World w, Thing t) => t != null && t.Spawned && (w.theft || !t.Foreign);

        /// <summary>Ends(): (ok, inlet id, far id) plus the raw things read.</summary>
        private static bool Ends(World w, Caches c, Reel r, int now, out long a, out long b, out Thing wa, out Thing wb)
        {
            a = b = 0; wa = wb = null;
            if (!r.Laid) return false;
            wa = c.Read(c.body, r, r.TrueBody, now, false);
            if (RoleOk(w, wa)) a = wa.Id;
            wb = c.Read(c.end, r, r.TrueEnd, now, false);
            if (RoleOk(w, wb)) b = wb.Id;
            else if (wb == null && w.roles && r.Role != 0) b = -((long)r.FarX * 1000 + r.FarZ) * 8 - r.Role;   // a free-end port
            return a != 0 && b != 0;
        }

        private static ulong Key(Reel r, int serial) =>
            RM_HoseLinkCache.Mix(RM_HoseLinkCache.Mix(RM_HoseLinkCache.Mix(RM_HoseLinkCache.Mix(RM_HoseLinkCache.Mix(17, r.Id), r.Laid ? 1 : 0), r.FarX * 4096L + r.FarZ), r.Role), serial);

        private sealed class Driver
        {
            public readonly RM_HoseLinkCache cache = new();
            public readonly Caches caches = new();
            public ulong sig; public bool built; public int rebuilds; int revSeen = int.MinValue; long foreign;
            public bool noGone, noSerial, noDown;

            public void Refresh(World w, int now, long[] okA, long[] okB)
            {
                if (w.revision != revSeen) { revSeen = w.revision; foreign++; }
                ulong g = RM_HoseLinkCache.Mix(RM_HoseLinkCache.Mix(RM_HoseLinkCache.Mix(1, w.theft ? 1 : 0), w.roles ? 1 : 0), foreign);
                bool every = cache.Begin(w.reels.Count, g);
                bool changed = false;
                for (int i = 0; i < w.reels.Count; i++)
                {
                    Reel r = w.reels[i];
                    bool gone = !noGone && ((cache.WatchA(i) is Thing x && !x.Spawned) || (cache.WatchB(i) is Thing y && !y.Spawned));
                    if (!cache.Due(every, i, Key(r, noSerial ? 0 : caches.Serial(r)), gone, now, r.Id)) continue;
                    bool ok = Ends(w, caches, r, now, out long a, out long b, out Thing wa, out Thing wb);
                    ulong key = Key(r, noSerial ? 0 : caches.Serial(r));   // taken after the read, as RefreshCore does
                    bool down = !noDown && ((wa != null && !wa.Spawned) || (wb != null && !wb.Spawned));
                    changed |= cache.Store(i, key, now, r.Id, ok, null, a, null, b, wa, wb, down);
                }
                if (cache.End(changed) || !built)
                {
                    ulong h = 1469598103934665603UL;
                    for (int i = 0; i < w.reels.Count; i++) if (cache.Ok(i)) h = RM_LiquidNetKernel.SigStep(h, w.reels[i].Id, cache.InletId(i), cache.FarId(i));
                    if (!built || h != sig) { sig = h; built = true; rebuilds++; revSeen = ++w.revision; }
                }
                for (int i = 0; i < w.reels.Count; i++) { okA[i] = cache.Ok(i) ? cache.InletId(i) : 0; okB[i] = cache.Ok(i) ? cache.FarId(i) : 0; }
            }
        }

        private sealed class Oracle
        {
            public readonly Caches caches = new();
            public ulong sig; public bool built; public int rebuilds;

            public void Refresh(World w, int now, long[] okA, long[] okB)
            {
                ulong h = 1469598103934665603UL;
                for (int i = 0; i < w.reels.Count; i++)
                {
                    bool ok = Ends(w, caches, w.reels[i], now, out long a, out long b, out _, out _);
                    okA[i] = ok ? a : 0; okB[i] = ok ? b : 0;
                    if (ok) h = RM_LiquidNetKernel.SigStep(h, w.reels[i].Id, a, b);
                }
                if (!built || h != sig) { sig = h; built = true; rebuilds++; }
            }
        }

        /// <summary>One randomized run; returns the number of Refreshes where driver and oracle disagree.</summary>
        private static int Run(int seed, Action<Driver> fault, out long evals, out long skips, out int refreshes)
        {
            var rng = new Random(seed);
            var w = new World();
            for (int i = 0; i < 40; i++) w.things.Add(new Thing { Id = 1000 + i, Foreign = rng.Next(4) == 0 });
            Thing Pick() => rng.Next(3) == 0 ? null : w.things[rng.Next(w.things.Count)];
            int nextId = 1;
            Reel NewReel() => new Reel { Id = nextId++ * 7 + 3, FarX = rng.Next(20), FarZ = rng.Next(20), Role = rng.Next(3), TrueBody = Pick(), TrueEnd = Pick() };
            for (int i = 0; i < 12; i++) w.reels.Add(NewReel());
            var d = new Driver(); fault?.Invoke(d);
            var o = new Oracle();
            int bad = 0; refreshes = 0;
            var a1 = new long[64]; var b1 = new long[64]; var a2 = new long[64]; var b2 = new long[64];
            for (int now = 1; now < 3000; now++)
            {
                int ev = rng.Next(100);
                Reel r = w.reels.Count > 0 ? w.reels[rng.Next(w.reels.Count)] : null;
                if (ev < 8 && r != null) r.TrueBody = Pick();                      // a pipe / tank built or removed beside the reel: silent
                else if (ev < 16 && r != null) r.TrueEnd = Pick();                 // same at the free end: silent
                else if (ev < 19) { Thing t = w.things[rng.Next(w.things.Count)]; t.Spawned = !t.Spawned; }   // despawn / respawn
                else if (ev < 21 && r != null) { r.FarX = rng.Next(20); r.FarZ = rng.Next(20); }
                else if (ev < 23 && r != null) r.Laid = !r.Laid;
                else if (ev < 24 && r != null) r.Role = rng.Next(3);
                else if (ev < 25) { w.things[rng.Next(w.things.Count)].Foreign ^= true; w.revision++; }   // faction change: a topology bump
                else if (ev < 26) w.theft = !w.theft;
                else if (ev < 27) w.roles = !w.roles;
                else if (ev < 28 && w.reels.Count < 60) w.reels.Insert(rng.Next(w.reels.Count + 1), NewReel());
                else if (ev < 29 && w.reels.Count > 1) w.reels.RemoveAt(rng.Next(w.reels.Count));
                else if (ev < 33 && r != null)                                     // someone forces a port re-read (the one shared cache)
                {
                    d.caches.Read(d.caches.body, r, r.TrueBody, now, true);
                    o.caches.Read(o.caches.body, r, r.TrueBody, now, true);
                }
                if (rng.Next(4) == 0) continue;                                     // Refresh runs only on a liquid query tick
                refreshes++;
                d.Refresh(w, now, a1, b1);
                // the oracle reads through its own caches every Refresh, so a silent change is seen when its cache re-reads: at the
                // first Refresh of the reel's next window, or at once after a despawn or a forced re-read
                o.Refresh(w, now, a2, b2);
                bool same = true;
                for (int i = 0; i < w.reels.Count; i++) if (a1[i] != a2[i] || b1[i] != b2[i]) same = false;
                if (!same) bad++;
            }
            evals = d.cache.Evals; skips = d.cache.Skips;
            return bad;
        }

        public static void Run()
        {
            long ev = 0, sk = 0; int bad = 0, refreshes = 0;
            for (int seed = 1; seed <= 40; seed++)
            {
                bad += Run(seed, null, out long e, out long s, out int n);
                ev += e; sk += s; refreshes += n;
            }
            Console.WriteLine($"  hose link cache: {refreshes} refreshes over 40 seeds, {bad} disagree with the full walk; {ev} reel reads, {sk} skipped ({(ev + sk == 0 ? 0 : 100.0 * sk / (ev + sk)):0.0}% saved)");
            Check(bad == 0, "the memoised links equal the full walk on every Refresh (" + bad + " disagree)");
            Check(sk > ev, "the cache skips most reel reads on a model map (" + sk + " skipped vs " + ev + " read)");
            // fault probes: the oracle can see each input class the cache must not miss
            foreach (var (name, fault) in new (string, Action<Driver>)[] { ("no gone check", x => x.noGone = true), ("no serial in the key", x => x.noSerial = true), ("no down flag (respawn of a thing read despawned)", x => x.noDown = true) })
            {
                int fb = 0;
                for (int seed = 1; seed <= 40; seed++) fb += Run(seed, fault, out _, out _, out _);
                Check(fb > 0, "fault '" + name + "' is caught (" + fb + " disagreeing refreshes)");
            }
            // the audit window is HoseLive.PhasedFresh over 60 ticks with the reel's id as phase: the reels' own cache window
            Check(RM_HoseLinkCache.AuditTicks == 60 && RM_HoseLinkCache.Fresh(119, 61, 0) && !RM_HoseLinkCache.Fresh(120, 119, 0) && !RM_HoseLinkCache.Fresh(5, 6, 0),
                "the audit window is the 60-tick phased cache window (never fresh across a boundary or from the future)");
            // source pins: production RefreshCore uses the cache the way the driver above does
            string src = Src("Machinery", "RM_LiquidNet.cs");
            Check(src.Contains("if (!cache.Due(every, i, KeyOf(r), Gone(i), now, id))") && src.Contains("changed |= cache.Store(i, KeyOf(r), now, id, ok, inlet, ok ? IdOf(inlet) : 0, far, ok ? IdOf(far) : 0, bodyPort, endPort, Down(bodyPort) || Down(endPort));")
                && src.Contains("return RM_HoseLinkCache.Mix(k, r.linkInputSerial);") && src.Contains("revSeen = RM_LiquidNet.RevisionOf(map); // our own bump is no foreign change")
                && src.Contains("g = RM_HoseLinkCache.Mix(g, Pits.RM_Drawbridges.RaisedLeafCount(map));"),
                "RM_HoseLinks.RefreshCore reads through the slot cache (due by key / gone / audit; key after the read; own bump excluded)");
            string hoses = Src("Hose", "RM_MapComponent_Hoses.cs"), reel = Src("Hose", "CompHoseReel.cs");
            Check(hoses.Contains("old.Value.Port != e.Port || old.Value.Relay != e.Relay") && reel.Contains("if (port != was) linkInputSerial++;"),
                "a changed free-end or body-port re-read bumps the reel's link serial");
        }
    }
}
