// Approach B for The Rot: seeded random ACTION SEQUENCES over the Verse-free kernel the mod calls (RM_TheRotKernel.cs):
//   gut     - the hwelgrue's digest clock, map cap and rot boost
//   swallow - a hwelgrue holding someone: digest length, knocks, belly cut, release, strangers
//   vat     - the gut-mother vat's clock: fuel, dormancy, splits, accepting bodies
//   core    - the world's one swallowed drive core: who carries it, the ping clock, integrity
//   log     - the navigator's log cadence and its cut
//   unjoin  - the unjoining draught's sorting
//   units   - tables, boundaries, the biome score
// The model (reference counters, double-precision oracles) is this file's own; every number under test comes from the production kernel.
// A failing sequence is shrunk by delta debugging and printed as `family seed N: message | actions`, so it replays exactly.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;

namespace RimMandrake.TheRot.Fuzz
{
    internal static class TheRotFuzz
    {
        public static long Cases, Steps;
        private static readonly List<string> Info = new List<string>();
        private static readonly Dictionary<string, long> Stats = new Dictionary<string, long>();
        private static void Hit(string k) { Stats[k] = (Stats.TryGetValue(k, out long v) ? v : 0) + 1; }

        internal struct Act
        {
            public int kind, a, b, c;
            public string Name;
            public override string ToString() { return Name + "(" + a + "," + b + "," + c + ")"; }
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static string F(double v) { return v.ToString("R", CultureInfo.InvariantCulture); }
        private const float Eps = 1e-4f;

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<T>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        private static List<string> RunFamily<W>(string name, int n, int baseSeed, int mult, string[] names, int[] kindWeights, int maxLen,
            Func<int, W> make, Action<W, Act> step, int aMax, int bMax, int cMax)
        {
            var fails = new List<string>();
            int total = kindWeights.Sum();
            Func<int, List<Act>, string> run = (seed, acts) =>
            {
                try { var w = make(seed); foreach (var a in acts) { step(w, a); Steps++; } return null; }
                catch (Exception ex) { return ex.Message; }
            };
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * mult + 3);
                int len = r.Next(5, maxLen);
                var acts = new List<Act>(len);
                for (int i = 0; i < len; i++)
                {
                    int pick = r.Next(total), kind = 0;
                    while (pick >= kindWeights[kind]) { pick -= kindWeights[kind]; kind++; }
                    acts.Add(new Act { kind = kind, Name = names[kind], a = r.Next(aMax), b = r.Next(bMax), c = r.Next(cMax) });
                }
                Cases++;
                if (run(seed, acts) == null) continue;
                var min = Shrink(acts, t => run(seed, t) != null);
                fails.Add(name + " seed " + seed + ": " + run(seed, min) + " | " + string.Join(" ", min));
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // ===================================================================== gut: digest clock, cap, rot boost

        private sealed class GutWorld
        {
            public int ticks, gutCount, sweep = 250;
            public float days = 2f;
            public int sinceFill;           // reference: sweeps with a non-empty gut since the last casting or emptying
            public int cap = 1, others;
            public bool enabled = true;
        }

        private static void GutStep(GutWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // a sweep
                {
                    int interval = RM_TheRotKernel.CastingIntervalTicks(w.days);
                    bool was0 = w.gutCount == 0;
                    bool due = RM_TheRotKernel.GutSweep(ref w.ticks, w.gutCount, w.sweep, interval);
                    if (w.gutCount == 0) { Check(w.ticks == 0 && !due, "an empty gut kept a clock or made a casting"); w.sinceFill = 0; break; }
                    w.sinceFill++;
                    Check(w.ticks == w.sinceFill * w.sweep, "clock " + w.ticks + " != " + w.sinceFill + " sweeps x " + w.sweep);
                    Check(due == (w.sinceFill * w.sweep >= interval), "casting due=" + due + " after " + w.sinceFill * w.sweep + "/" + interval + " ticks");
                    if (due) { w.ticks = 0; w.sinceFill = 0; Hit("gut.casting"); }      // PassCasting resets the clock and empties the gut
                    break;
                }
                case 1: w.gutCount++; break;                 // metal swallowed
                case 2: w.gutCount = 0; break;               // passed / spilled
                case 3: w.days = new[] { 0.5f, 1f, 2f, 10f, 0.001f }[a.a % 5]; break;
                case 4: // the map cap
                {
                    w.cap = 1 + a.a % 5; w.others = a.b % 7; w.enabled = a.c % 5 != 0;
                    bool over = RM_TheRotKernel.OverCap(false, w.enabled, w.cap, w.others);
                    Check(over == (w.others >= (w.enabled ? w.cap : 0)), "OverCap=" + over + " for others " + w.others + " cap " + w.cap + " enabled " + w.enabled);
                    Check(!RM_TheRotKernel.OverCap(true, w.enabled, w.cap, w.others), "a factioned hwelgrue was over the cap");
                    if (!w.enabled) Check(over, "with the creature off every wild hwelgrue is over a cap of 0");
                    if (w.others == 0 && w.enabled) Check(!over, "the first hwelgrue was over the cap");
                    if (over) Hit("gut.overCap");
                    break;
                }
                case 5: // rot boost
                {
                    float mult = new[] { 0f, 0.5f, 1f, 1.5f, 3f, 10f }[a.a % 6];
                    float rate = new[] { -1f, 0f, 0.1f, 1f, 2f }[a.b % 5];
                    float boost = RM_TheRotKernel.RotBoost(mult, rate, 250);
                    Check(boost >= 0f, "negative rot boost");
                    if (mult <= 1f || rate <= 0f) Check(boost == 0f, "boost " + boost + " with multiplier " + mult + " at rate " + rate);
                    else Check(Math.Abs(boost - rate * (mult - 1f) * 250f) < 1e-3f, "boost " + boost + " != rate x (mult-1) x 250");
                    break;
                }
            }
        }

        // ===================================================================== swallow

        private sealed class SwallowWorld
        {
            public RM_TheRotKernel.SwallowState s = RM_TheRotKernel.SwallowState.Fresh();
            public bool holding, insideDead, humanlike = true;
            public int now = 1000, swallowAt, lastKnock = -1;
            public float minHours = 3f, perBody = 3f, cut = 150f, loud = 1f;
            public float lastFraction = 1f;
            public Random rng;
            public int heldTicks;
        }

        private static readonly float[] Bodies = { 0.2f, 0.5f, 1f, 1.6f, 3f };

        private static void SwallowFinish(SwallowWorld w)
        {
            Check(w.s.ticksInside >= w.s.ticksToDigest || w.insideDead, "digestion finished at " + w.s.ticksInside + "/" + w.s.ticksToDigest + " with the victim alive");
            if (!w.insideDead) Check(w.s.ticksInside == w.s.ticksToDigest, "digestion overshot: " + w.s.ticksInside + "/" + w.s.ticksToDigest);
            RM_TheRotKernel.Clear(ref w.s);
            Check(w.s.ticksInside == 0 && w.s.ticksToDigest == 0 && w.s.damageSinceSwallow == 0f, "Clear left state behind");
            w.holding = false; w.insideDead = false;
            Hit("swallow.finish");
        }

        private static void SwallowStepFn(SwallowWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // swallow a downed victim
                {
                    if (w.holding) break;
                    float body = Bodies[a.a % Bodies.Length];
                    int digest = RM_TheRotKernel.DigestTicksFor(w.minHours, w.perBody, body);
                    Check(digest >= (int)Math.Round(w.minHours * 2500) - 1, "digest " + digest + " under the creature's own minimum hours");
                    Check(digest == (int)Math.Round(Math.Max(w.minHours, w.perBody * body) * 2500.0), "digest ticks " + digest + " != reference for body " + body);
                    RM_TheRotKernel.Begin(ref w.s, digest, w.now);
                    Check(w.s.nextKnockTick == w.now + 120 && w.s.ticksInside == 0 && w.s.ticksToDigest == digest, "a fresh swallow is not at zero with the first knock 120 ticks out");
                    w.holding = true; w.insideDead = false; w.humanlike = a.b % 3 != 0; w.swallowAt = w.now; w.lastKnock = -1; w.lastFraction = 1f; w.heldTicks = 0;
                    Hit("swallow.begin");
                    break;
                }
                case 1: // ticks
                {
                    int n = 1 + a.a * 5;
                    for (int i = 0; i < n && w.holding; i++)
                    {
                        w.now++; w.heldTicks++;
                        var ev = RM_TheRotKernel.Tick(ref w.s, w.now, w.insideDead);
                        Check(w.s.ticksInside == w.heldTicks, "inside clock " + w.s.ticksInside + " != ticks held " + w.heldTicks);
                        float f = RM_TheRotKernel.TimeLeftFraction(w.s);
                        Check(f >= 0f && f <= 1f && f <= w.lastFraction + Eps, "time-left fraction " + f + " rose or left [0,1] (last " + w.lastFraction + ")");
                        w.lastFraction = f;
                        if (ev == RM_TheRotKernel.SwallowEvent.Finish) { SwallowFinish(w); break; }
                        Check(w.s.ticksInside < w.s.ticksToDigest, "no Finish at the digest length");
                        if (ev == RM_TheRotKernel.SwallowEvent.Knock)
                        {
                            int before = w.now;
                            float kf = RM_TheRotKernel.KnockNext(ref w.s, w.now);
                            int gap = w.s.nextKnockTick - before;
                            Check(Math.Abs(gap - (900.0 - 720.0 * Math.Min(1.0, Math.Max(0.0, kf)))) <= 1.0, "knock gap " + gap + " for fraction " + kf + " (900 at full time, 180 at none)");
                            Check(gap >= 180 && gap <= 900, "knock gap " + gap + " outside 180..900");
                            float vol = RM_TheRotKernel.KnockVolume(kf, w.loud);
                            Check(vol >= 0.25f * w.loud - Eps && vol <= w.loud + Eps, "knock volume " + vol + " outside [0.25, 1] x loudness " + w.loud);
                            var kind = RM_TheRotKernel.KnockKindFor(w.humanlike, kf);
                            if (!w.humanlike) Check(kind == RM_TheRotKernel.KnockKind.Scrabbling, "an animal did not scrabble");
                            else Check(kind == (kf > 0.66f ? RM_TheRotKernel.KnockKind.Knocking : kf > 0.33f ? RM_TheRotKernel.KnockKind.Weak : RM_TheRotKernel.KnockKind.Failing), "knock kind " + kind + " at fraction " + kf);
                            if (w.lastKnock >= 0) Check(before - w.lastKnock >= 180, "two knocks " + (before - w.lastKnock) + " ticks apart");
                            w.lastKnock = before;
                            Hit("swallow.knock");
                        }
                    }
                    break;
                }
                case 2: // the hwelgrue is hurt while holding
                {
                    if (!w.holding) break;
                    float dmg = new[] { 1f, 10f, 49.9f, 75f, 150f, 600f }[a.a % 6];
                    float before = w.s.damageSinceSwallow;
                    bool opens = RM_TheRotKernel.BellyOpens(ref w.s, dmg, w.cut);
                    Check(Math.Abs(w.s.damageSinceSwallow - (before + dmg)) < 1e-3f, "damage not accumulated");
                    Check(opens == (before + dmg >= w.cut), "belly opens=" + opens + " at " + (before + dmg) + "/" + w.cut);
                    if (opens)
                    {
                        float f = RM_TheRotKernel.Clear(ref w.s);
                        float acid = RM_TheRotKernel.EarnedAcid(f);
                        Check(acid >= 5f - Eps && acid <= 60f + Eps, "released victim earned " + acid + " acid damage (5..60)");
                        Check(f >= 0f && f <= 1f, "released at fraction " + f);
                        w.holding = false; w.insideDead = false;
                        Hit("swallow.release");
                    }
                    break;
                }
                case 3: if (w.holding) w.insideDead = true; break;     // it died in there
                case 4: // a stranger already part-digested
                {
                    if (w.holding) break;
                    float body = Bodies[a.a % Bodies.Length];
                    int digest = RM_TheRotKernel.DigestTicksFor(w.minHours, w.perBody, body);
                    int left = (int)Math.Round((2f + (a.b % 100) / 25f) * 2500f);
                    RM_TheRotKernel.BeginStranger(ref w.s, digest, w.now, left);
                    Check(w.s.ticksInside == Math.Max(0, digest - left), "stranger has " + (w.s.ticksToDigest - w.s.ticksInside) + " ticks left, expected " + Math.Min(digest, left));
                    Check(RM_TheRotKernel.TicksLeft(w.s) == Math.Min(digest, left), "TicksLeft disagrees");
                    w.holding = true; w.insideDead = false; w.humanlike = true; w.lastKnock = -1; w.lastFraction = RM_TheRotKernel.TimeLeftFraction(w.s); w.heldTicks = w.s.ticksInside;
                    Hit("swallow.stranger");
                    break;
                }
                case 5:
                    switch (a.a % 4)
                    {
                        case 0: w.minHours = new[] { 3f, 6f }[a.b % 2]; break;
                        case 1: w.perBody = new[] { 3f, 6f }[a.b % 2]; break;
                        case 2: w.cut = new[] { 25f, 150f, 600f }[a.b % 3]; break;
                        default: w.loud = new[] { 0f, 1f, 2f }[a.b % 3]; break;
                    }
                    break;
            }
            if (!w.holding) Check(w.s.ticksInside == 0 || a.kind == 4 || a.kind == 0, "an empty belly kept a clock");
        }

        // ===================================================================== vat: the gut-mother

        private sealed class VatWorld
        {
            public int progress, restUntil = -1, now = 1000;
            public bool holds, enabled = true;
            public float fuel = 2f, capacity = 20f, burnPerDay = 4f, hours = 24f, restHours = 12f, splitFuel = 6f;
            public int activeTicks;
            public int digestAtAccept;
        }

        private static void VatStep(VatWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // a body offered
                {
                    bool usable = a.a % 7 != 0;
                    bool accepts = RM_TheRotKernel.VatAccepts(w.enabled, usable, w.holds);
                    Check(accepts == (w.enabled && usable && !w.holds), "VatAccepts=" + accepts);
                    if (accepts) { w.holds = true; w.progress = 0; w.activeTicks = 0; w.digestAtAccept = RM_TheRotKernel.GutMotherDigestTicks(w.hours); Hit("vat.accepted"); }
                    else if (w.holds) Hit("vat.refusedFull");
                    break;
                }
                case 1: // rare ticks
                {
                    int n = 1 + a.a % 120;
                    for (int i = 0; i < n; i++)
                    {
                        w.now += 250;
                        if (!w.enabled) continue;                                    // the comp does nothing while the vat is off
                        float burn = RM_TheRotKernel.GutMotherFuelBurn(w.burnPerDay);
                        Check(Math.Abs(burn - w.burnPerDay * 250f / 60000f) < 1e-7f, "fuel burn " + burn + " per rare tick");
                        bool fueledBefore = w.fuel > 0f;
                        if (fueledBefore) w.fuel = Math.Max(0f, w.fuel - burn);
                        Check(w.fuel >= 0f, "negative fuel");
                        bool dormant = !(w.fuel > 0f);
                        int digest = RM_TheRotKernel.GutMotherDigestTicks(w.hours);
                        int before = w.progress;
                        bool done = RM_TheRotKernel.GutMotherTick(ref w.progress, w.holds, dormant, digest);
                        if (!w.holds || dormant) Check(w.progress == before && !done, "the clock moved with nothing inside or no fuel");
                        else
                        {
                            Check(w.progress == before + 250, "the clock did not advance by one rare tick");
                            w.activeTicks++;
                            Check(done == (w.progress >= digest), "done=" + done + " at " + w.progress + "/" + digest);
                            if (done)
                            {
                                Check(w.activeTicks * 250 >= digest, "a body finished after only " + w.activeTicks * 250 + " active ticks of " + digest);
                                w.holds = false; w.progress = 0; w.activeTicks = 0; Hit("vat.finished");
                            }
                        }
                        if (dormant && w.holds) Hit("vat.dormant");
                    }
                    break;
                }
                case 2: w.fuel = Math.Min(w.capacity, w.fuel + new[] { 1f, 5f, 20f }[a.a % 3]); break;
                case 3: // a split
                {
                    int rest = RM_TheRotKernel.RestUntil(w.now, w.restHours);
                    Check(rest == w.now + (int)Math.Round(w.restHours * 2500f), "rest until " + rest);
                    w.restUntil = rest; w.fuel = Math.Max(0f, w.fuel - w.splitFuel);
                    Check(RM_TheRotKernel.Resting(w.now, w.restUntil), "not resting right after a split");
                    Check(!RM_TheRotKernel.Resting(w.restUntil, w.restUntil), "still resting at the rest-until tick");
                    Hit("vat.split");
                    break;
                }
                case 4: w.enabled = !w.enabled; break;
                case 5: w.hours = new[] { 1f, 24f, 96f, 0.0001f }[a.a % 4]; break;
            }
            bool resting = RM_TheRotKernel.Resting(w.now, w.restUntil);
            Check(RM_TheRotKernel.VatBusy(w.holds, resting) == (w.holds || resting), "busy disagrees with holds || resting");
            Check(RM_TheRotKernel.GutMotherDigestTicks(w.hours) >= 1, "digest length under 1");
        }

        // ===================================================================== core: the one swallowed drive core

        private sealed class CoreHwelgrue
        {
            public string id; public bool hasFaction, claimChecked, carrier, engineSeen, dead;
            public int nextPing = -1; public float integrity = 100f; public bool overCap; public int mapTile;
        }

        private sealed class CoreWorld
        {
            public string carrierId; public bool spent, haveWorld = true;
            public List<CoreHwelgrue> pack = new List<CoreHwelgrue>();
            public int nextId = 1, now = 1000, campaignTile = -1, interval = 30000, pings;
            public bool engine;
            public HashSet<string> everCarriers = new HashSet<string>();
            public string firstCarrier;
        }

        private static void CoreStep(CoreWorld w, Act a)
        {
            CoreHwelgrue pick = w.pack.Count == 0 ? null : w.pack[a.a % w.pack.Count];
            switch (a.kind)
            {
                case 0: w.pack.Add(new CoreHwelgrue { id = "H" + w.nextId++, overCap = a.b % 4 == 0, mapTile = a.c % 3 == 0 ? 5 : 7, hasFaction = a.c % 11 == 0 }); break;
                case 1: // its first CompTick: claim check
                {
                    if (pick == null || pick.dead || pick.claimChecked) break;
                    pick.claimChecked = true;
                    string carrierBefore = w.carrierId; bool spentBefore = w.spent;
                    var r = RM_TheRotKernel.Claim(w.haveWorld, w.spent, pick.hasFaction, w.carrierId, pick.id, pick.overCap, w.campaignTile, pick.mapTile);
                    switch (r)
                    {
                        case RM_TheRotKernel.ClaimResult.Mine: pick.carrier = true; break;
                        case RM_TheRotKernel.ClaimResult.NotMine: pick.carrier = false; break;
                        case RM_TheRotKernel.ClaimResult.New:
                            Check(carrierBefore == null && !spentBefore && !pick.hasFaction && !pick.overCap, "a core was claimed with a carrier already, spent, by a factioned or over-cap hwelgrue");
                            Check(w.campaignTile < 0 || pick.mapTile == w.campaignTile, "a core was claimed off its campaign tile");
                            w.carrierId = pick.id; pick.carrier = true; pick.integrity = 100f; w.everCarriers.Add(pick.id); if (w.firstCarrier == null) w.firstCarrier = pick.id;
                            Hit("core.claimed");
                            break;
                        default:
                            Check(!(w.haveWorld && !w.spent && !pick.hasFaction && string.IsNullOrEmpty(w.carrierId) && !pick.overCap && (w.campaignTile < 0 || pick.mapTile == w.campaignTile)), "an eligible first claimant was refused");
                            break;
                    }
                    break;
                }
                case 2: // the carrier dies
                {
                    if (pick == null || pick.dead) break;
                    pick.dead = true;
                    if (pick.carrier) { w.spent = true; pick.carrier = false; Hit("core.carrierDied"); }
                    break;
                }
                case 3: if (pick != null) pick.hasFaction = true; break;       // tamed
                case 4: w.engine = !w.engine; break;
                case 5: // 250 tick pings for every living carrier
                {
                    int n = 1 + a.a % 200;
                    for (int i = 0; i < n; i++)
                    {
                        w.now += 250;
                        foreach (CoreHwelgrue h in w.pack)
                        {
                            if (h.dead || !h.carrier) continue;
                            int nextBefore = h.nextPing; bool seenBefore = h.engineSeen;
                            bool due = RM_TheRotKernel.PingDue(ref h.nextPing, ref h.engineSeen, w.now, w.engine, w.interval);
                            Check(h.engineSeen == w.engine, "engine-seen not tracked");
                            if (w.engine && !seenBefore) Check(due, "a grav engine appearing did not ping at once");
                            if (due)
                            {
                                Check(h.nextPing == w.now + w.interval, "next ping " + (h.nextPing - w.now) + " ticks out, interval " + w.interval);
                                bool engineAppeared = w.engine && !seenBefore;
                                Check(engineAppeared || nextBefore < 0 || w.now >= nextBefore, "a ping fired early");
                                if (w.engine) { w.pings++; Hit("core.ping"); }
                                if (engineAppeared) Hit("core.engineAppeared");
                            }
                            else Check(w.now < h.nextPing, "a ping was due (now " + w.now + ", next " + h.nextPing + ") and not given");
                        }
                    }
                    break;
                }
                case 6: // the ship's guns hit the carrier
                {
                    if (pick == null || !pick.carrier) break;
                    float dmg = new[] { 1f, 10f, 40f, 400f }[a.b % 4], factor = new[] { 0f, 0.5f, 1f, 2f }[a.c % 4];
                    float before = pick.integrity;
                    pick.integrity = RM_TheRotKernel.IntegrityAfterHit(pick.integrity, dmg, factor);
                    Check(pick.integrity >= 0f && pick.integrity <= before + Eps, "integrity " + before + " -> " + pick.integrity);
                    Check(Math.Abs(pick.integrity - Math.Max(0f, before - dmg * factor)) < 1e-3f, "integrity arithmetic");
                    break;
                }
                case 7: w.campaignTile = a.a % 2 == 0 ? -1 : 5; break;
                case 9: if (w.carrierId == null) w.spent = true; break;        // the bridge proof (ProofKillThenPing) spends the core with no carrier
                case 8: // what a dead carrier leaves
                {
                    float integrity = new[] { 0f, 24.9f, 25f, 25.1f, 60f, 100f }[a.a % 6], threshold = new[] { 0f, 25f, 90f }[a.b % 3];
                    bool ruined = RM_TheRotKernel.DropsRuined(integrity, threshold);
                    Check(ruined == (integrity < threshold), "ruined=" + ruined + " at " + integrity + "/" + threshold);
                    float rf = RM_TheRotKernel.RangeFactor(true, 0.25f, integrity);
                    Check(Math.Abs(rf - (1f + 0.25f * integrity / 100f)) < 1e-5f && rf >= 1f, "range factor " + rf);
                    Check(RM_TheRotKernel.RangeFactor(false, 0.25f, integrity) == 1f, "range factor with the option off");
                    break;
                }
            }
            // ---- invariants
            Check(w.pack.Count(h => h.carrier && !h.dead) <= 1, "more than one living carrier");
            Check(w.everCarriers.Count <= 1, "the core had " + w.everCarriers.Count + " different carriers (one per world, ever)");
            if (w.carrierId != null) Check(w.carrierId == w.firstCarrier, "the carrier id changed after it was set");
            foreach (CoreHwelgrue h in w.pack) if (h.carrier) Check(h.id == w.carrierId, "a carrier that is not the world's carrier");
            if (w.spent) Check(!w.pack.Any(h => h.carrier), "a spent core still has a carrier");
        }

        // ===================================================================== log: the navigator's log

        private sealed class LogWorld
        {
            public int pings, entriesRead, sitesRevealed, entryCount = 8, perEntry = 4;
            public bool spent, logCut;
            public int[] siteEntries = { 3, 6 };
            public int[] campaignTiles = { 11, 22 };
            public int lettersOnDeath;
            public List<int> readOrder = new List<int>();
            public List<int> tilesUsed = new List<int>();
        }

        private static void LogStep(LogWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // a ping (the caller bumps pings, then Notify_Ping)
                {
                    w.pings++;
                    if (!RM_TheRotKernel.LogReads(true, true, w.spent, w.logCut)) break;
                    int due = RM_TheRotKernel.EntriesDue(w.pings, w.perEntry, w.entryCount);
                    int expectRead = Math.Max(w.entriesRead, due);      // reads only ever catch up: a slower setting later never un-reads
                    while (w.entriesRead < due)
                    {
                        int n = ++w.entriesRead;
                        w.readOrder.Add(n);
                        if (w.siteEntries.Contains(n))
                        {
                            int idx = RM_TheRotKernel.CampaignTileIndex(w.sitesRevealed, w.campaignTiles.Length);
                            Check(idx == (w.sitesRevealed < w.campaignTiles.Length ? w.sitesRevealed : -1), "campaign tile index " + idx + " for site #" + (w.sitesRevealed + 1));
                            if (idx >= 0) { Check(!w.tilesUsed.Contains(w.campaignTiles[idx]), "a campaign tile was used twice"); w.tilesUsed.Add(w.campaignTiles[idx]); }
                            w.sitesRevealed++;
                            Hit("log.site");
                        }
                        Hit("log.entry");
                    }
                    Check(w.entriesRead == expectRead, "after a ping " + w.entriesRead + " entries are read, expected " + expectRead);
                    break;
                }
                case 1: // the carrier dies
                {
                    int readBefore = w.entriesRead; bool cutBefore = w.logCut;
                    w.spent = true;
                    bool letter = RM_TheRotKernel.CutLogOnDeath(ref w.logCut, w.entriesRead, w.entryCount);
                    if (cutBefore || readBefore >= w.entryCount) Check(!letter && w.logCut == cutBefore, "a finished or already cut log was cut again");
                    else Check(w.logCut && letter == (readBefore > 0), "cut=" + w.logCut + " letter=" + letter + " after " + readBefore + " entries");
                    if (letter) { w.lettersOnDeath++; Hit("log.cutLetter"); }
                    break;
                }
                case 2: w.perEntry = new[] { 0, 1, 4, 12 }[a.a % 4]; break;
            }
            Check(w.entriesRead <= w.entryCount, "read " + w.entriesRead + " of " + w.entryCount + " entries");
            Check(w.readOrder.SequenceEqual(Enumerable.Range(1, w.readOrder.Count)), "entries read out of order");
            Check(w.sitesRevealed <= w.siteEntries.Count(e => e <= w.entriesRead), "more sites than site entries read");
            Check(w.lettersOnDeath <= 1, "two cut letters");
        }

        // ===================================================================== unjoin

        private static void UnjoinStep(object _, Act a)
        {
            bool inP = (a.a & 1) != 0, inS = (a.a & 2) != 0, hasM = (a.a & 4) != 0, mS = (a.a & 8) != 0;
            var s = RM_TheRotKernel.Sort(inP, inS, hasM, mS);
            bool symbiont = inS || (hasM && mS), parasite = inP || hasM;
            Check(s.removed == (symbiont || parasite) && s.husk == symbiont, "Sort(" + inP + "," + inS + "," + hasM + "," + mS + ") = removed " + s.removed + " husk " + s.husk);
            if (!inP && !inS && !hasM) Check(!s.removed, "an ordinary hediff was purged");
            if (s.husk) Check(s.removed, "a husk without a removal");
            if (s.removed) Hit("unjoin.removed"); if (s.husk) Hit("unjoin.husk");
        }

        // ===================================================================== units

        public static List<string> Units(int n, int baseSeed)
        {
            var fails = new List<string>();
            Action<string> bad = m => { if (fails.Count < 8) fails.Add("units: " + m); };
            var r = new Random(baseSeed);

            Cases++;
            {
                Steps += 12;
                if (RM_TheRotKernel.CastingIntervalTicks(2f) != 120000 || RM_TheRotKernel.CastingIntervalTicks(0.5f) != 30000 || RM_TheRotKernel.CastingIntervalTicks(0.001f) != 2500) bad("casting interval table");
                if (RM_TheRotKernel.PingIntervalTicks(12f) != 30000 || RM_TheRotKernel.PingIntervalTicks(0.01f) != 2500) bad("ping interval table");
                if (RM_TheRotKernel.PurgeTicks(24f) != 60000 || RM_TheRotKernel.PurgeTicks(0f) != 2500) bad("purge length table");
                if (RM_TheRotKernel.GutMotherDigestTicks(24f) != 60000 || RM_TheRotKernel.GutMotherDigestTicks(0f) != 1) bad("vat digest table");
                if (RM_TheRotKernel.DigestTicksFor(3f, 24f, 1f) != 60000 || RM_TheRotKernel.DigestTicksFor(3f, 24f, 0.05f) != 7500) bad("swallow digest table (3 h minimum, 24 h per body size)");
                if (RM_TheRotKernel.EarnedAcid(1f) != 5f || RM_TheRotKernel.EarnedAcid(0f) != 60f || RM_TheRotKernel.EarnedAcid(2f) != 5f) bad("acid burn ends");
                if (RM_TheRotKernel.EntriesDue(7, 4, 8) != 1 || RM_TheRotKernel.EntriesDue(8, 4, 8) != 2 || RM_TheRotKernel.EntriesDue(1000, 4, 8) != 8 || RM_TheRotKernel.EntriesDue(5, 0, 8) != 5) bad("entries due table");
                if (RM_TheRotKernel.CampaignTileIndex(0, 0) != -1 || RM_TheRotKernel.CampaignTileIndex(1, 2) != 1 || RM_TheRotKernel.CampaignTileIndex(2, 2) != -1) bad("campaign tile index table");
                if (RM_TheRotKernel.ScarSeverity(4f, 3f) != 2f || RM_TheRotKernel.ScarSeverity(4f, 100f) != 4f || RM_TheRotKernel.ScarSeverity(4f, 1f) > 0f) bad("scar severity (never enough to kill the part)");
                if (RM_TheRotKernel.Lerp(60f, 5f, -1f) != 60f || RM_TheRotKernel.Lerp(60f, 5f, 9f) != 5f) bad("lerp clamp");
            }

            // --- the swallow digest rises with body size and never falls under the minimum
            Cases++;
            {
                int prev = 0;
                for (float body = 0f; body < 6f; body += 0.05f) { Steps++; int d = RM_TheRotKernel.DigestTicksFor(3f, 24f, body); if (d < prev || d < 7500) bad("digest not monotone / under the minimum at body size " + body); prev = d; }
            }

            // --- swallow edge cases a random walk rarely sits on (added with the mutation set)
            Cases++;
            {
                Steps += 14;
                var s0 = RM_TheRotKernel.SwallowState.Fresh();
                if (RM_TheRotKernel.TimeLeftFraction(s0) != 0f || RM_TheRotKernel.TicksLeft(s0) != 0) bad("an empty belly must read as no time left");
                var over = new RM_TheRotKernel.SwallowState { ticksToDigest = 100, ticksInside = 150, nextKnockTick = -1 };
                if (RM_TheRotKernel.TimeLeftFraction(over) != 0f) bad("time-left fraction fell below 0 (" + RM_TheRotKernel.TimeLeftFraction(over) + ")");
                if (RM_TheRotKernel.TicksLeft(over) != 0) bad("ticks left went negative");
                var half = new RM_TheRotKernel.SwallowState { ticksToDigest = 100, ticksInside = 50, nextKnockTick = -1 };
                if (RM_TheRotKernel.TimeLeftFraction(half) != 0.5f) bad("half way in must read 0.5");
                if (RM_TheRotKernel.TimeLeftFraction(new RM_TheRotKernel.SwallowState { ticksToDigest = 100, ticksInside = -20 }) != 1f) bad("time-left fraction rose above 1");
                // a new swallow starts clean even if the last one was never cleared
                var dirty = new RM_TheRotKernel.SwallowState { ticksInside = 77, ticksToDigest = 1000, damageSinceSwallow = 40f, nextKnockTick = 5 };
                RM_TheRotKernel.Begin(ref dirty, 500, 1000);
                if (dirty.damageSinceSwallow != 0f || dirty.ticksInside != 0 || dirty.ticksToDigest != 500 || dirty.nextKnockTick != 1120) bad("Begin must reset damage, clock and the first knock (120 ticks out)");
                var stranger = new RM_TheRotKernel.SwallowState { damageSinceSwallow = 40f };
                RM_TheRotKernel.BeginStranger(ref stranger, 500, 1000, 200);
                if (stranger.damageSinceSwallow != 0f || stranger.ticksInside != 300 || stranger.nextKnockTick != 1120) bad("BeginStranger: damage reset, 200 ticks left, first knock 120 out");
                // Tick: a victim already dead / gone finishes AT ONCE, mid-digest; the knock is due exactly at nextKnockTick, not a tick before
                var t1 = new RM_TheRotKernel.SwallowState { ticksToDigest = 1000, ticksInside = 10, nextKnockTick = 5000 };
                if (RM_TheRotKernel.Tick(ref t1, 100, true) != RM_TheRotKernel.SwallowEvent.Finish) bad("a dead victim must finish the swallow immediately");
                var t2 = new RM_TheRotKernel.SwallowState { ticksToDigest = 1000, ticksInside = 10, nextKnockTick = 500 };
                if (RM_TheRotKernel.Tick(ref t2, 499, false) != RM_TheRotKernel.SwallowEvent.None) bad("a knock fired a tick early");
                if (RM_TheRotKernel.Tick(ref t2, 500, false) != RM_TheRotKernel.SwallowEvent.Knock) bad("a knock did not fire when due");
                var t3 = new RM_TheRotKernel.SwallowState { ticksToDigest = 20, ticksInside = 18, nextKnockTick = 5000 };
                if (RM_TheRotKernel.Tick(ref t3, 1, false) != RM_TheRotKernel.SwallowEvent.None || RM_TheRotKernel.Tick(ref t3, 2, false) != RM_TheRotKernel.SwallowEvent.Finish) bad("the digest must finish on the tick that reaches its length");
                if (t3.ticksInside != 20) bad("Tick must advance the clock by exactly one");
                if (Math.Abs(RM_TheRotKernel.KnockVolume(0f, 1f) - 0.25f) > 1e-6f || Math.Abs(RM_TheRotKernel.KnockVolume(1f, 1f) - 1f) > 1e-6f || Math.Abs(RM_TheRotKernel.KnockVolume(0.5f, 2f) - 1.25f) > 1e-6f) bad("knock volume table (quiet at the end, scaled by loudness)");
                // tile 0 is a real campaign tile: a hwelgrue on any other tile must not claim the core
                if (RM_TheRotKernel.Claim(true, false, false, null, "me", false, 0, 1) != RM_TheRotKernel.ClaimResult.No || RM_TheRotKernel.Claim(true, false, false, null, "me", false, 0, 0) != RM_TheRotKernel.ClaimResult.New || RM_TheRotKernel.Claim(true, false, false, null, "me", false, -1, 9) != RM_TheRotKernel.ClaimResult.New) bad("campaign tile gate (0 is a valid tile, -1 means none set)");
                foreach (bool hw in new[] { false, true }) foreach (bool hd in new[] { false, true }) foreach (bool sp in new[] { false, true }) foreach (bool cut in new[] { false, true })
                    if (RM_TheRotKernel.LogReads(hw, hd, sp, cut) != (hw && hd && !sp && !cut)) bad("LogReads(" + hw + "," + hd + "," + sp + "," + cut + ")");
                var edge = new RM_TheRotKernel.BiomeRanges { tempMin = -40f, tempMax = 15f, rainMin = 0f, rainMax = 1600f, elevMin = 0f, elevMax = 1200f, baseScore = 30f, degreeWeight = 1.2f, rainfallDivisor = 0f };
                if (!(RM_TheRotKernel.BiomeScore(false, false, false, 15f, 100f, 100f, edge) >= 30f) || !(RM_TheRotKernel.BiomeScore(false, false, false, -40f, 100f, 100f, edge) >= 30f)) bad("temperature range edges are inclusive");
                if (!(RM_TheRotKernel.BiomeScore(false, false, false, 0f, 100f, 100f, edge) < 1e6f) || float.IsNaN(RM_TheRotKernel.BiomeScore(false, false, false, 0f, 100f, 100f, edge))) bad("a zero rainfall divisor must not blow the score up");
                // the rot boost is exactly 0 at multiplier 1 and strictly positive above it
                if (RM_TheRotKernel.RotBoost(1f, 2f, 250) != 0f || RM_TheRotKernel.RotBoost(0.5f, 2f, 250) != 0f || !(RM_TheRotKernel.RotBoost(1.5f, 2f, 250) > 0f) || RM_TheRotKernel.RotBoost(2f, 0f, 250) != 0f) bad("rot boost edges");
            }

            // --- biome score
            Cases++;
            {
                var rg = new RM_TheRotKernel.BiomeRanges { tempMin = -40f, tempMax = 15f, rainMin = 0f, rainMax = 1600f, elevMin = 0f, elevMax = 1200f, baseScore = 30f, degreeWeight = 1.2f, rainfallDivisor = 220f };
                Steps += 8;
                if (RM_TheRotKernel.BiomeScore(true, false, false, 0f, 100f, 100f, rg) != -100f || RM_TheRotKernel.BiomeScore(false, true, false, 0f, 100f, 100f, rg) != -100f) bad("null / water tile scored");
                if (RM_TheRotKernel.BiomeScore(false, false, true, 0f, 100f, 100f, rg) != 0f) bad("impassable scored");
                if (RM_TheRotKernel.BiomeScore(false, false, false, 16f, 100f, 100f, rg) != 0f || RM_TheRotKernel.BiomeScore(false, false, false, 0f, 1600f, 100f, rg) != 0f || RM_TheRotKernel.BiomeScore(false, false, false, 0f, 100f, 1201f, rg) != 0f) bad("range edges");
                float want = 30f + (15f - 0f) * 1.2f + (1600f - 100f) / 220f;
                if (Math.Abs(RM_TheRotKernel.BiomeScore(false, false, false, 0f, 100f, 100f, rg) - want) > 1e-4f) bad("score arithmetic");
                for (int k = 0; k < Math.Max(1, n / 50); k++)
                {
                    Steps++;
                    float t = (float)(-40 + r.NextDouble() * 55), rain = (float)(r.NextDouble() * 1599), el = (float)(r.NextDouble() * 1200);
                    float s1 = RM_TheRotKernel.BiomeScore(false, false, false, t, rain, el, rg);
                    float s2 = RM_TheRotKernel.BiomeScore(false, false, false, Math.Min(15f, t + 3f), rain, el, rg);
                    float s3 = RM_TheRotKernel.BiomeScore(false, false, false, t, Math.Min(1599f, rain + 50f), el, rg);
                    if (s2 > s1 + 1e-4f) bad("the Rot scores a WARMER tile higher: " + s1 + " -> " + s2);
                    if (s3 > s1 + 1e-4f) bad("the Rot scores a WETTER tile higher: " + s1 + " -> " + s3);
                    if (s1 < 30f) bad("an eligible tile scored " + s1 + " under the base");
                }
            }
            return fails;
        }

        // ===================================================================== driver

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("gut", () => RunFamily("gut", N(3000), S(1), 7919, new[] { "Sweep", "Fill", "Empty", "Days", "Cap", "Rot" }, new[] { 12, 3, 1, 1, 4, 3 }, 120, seed => new GutWorld(), GutStep, 100, 100, 100)),
                ("swallow", () => RunFamily("swallow", N(1500), S(1), 104729, new[] { "Swallow", "Ticks", "Hurt", "Dies", "Stranger", "Setting" }, new[] { 4, 8, 4, 1, 2, 2 }, 40, seed => new SwallowWorld { rng = new Random(seed) }, SwallowStepFn, 2000, 100, 10)),
                ("vat", () => RunFamily("vat", N(3000), S(1), 6007, new[] { "Offer", "Ticks", "Refuel", "Split", "Toggle", "Hours" }, new[] { 4, 10, 3, 2, 1, 2 }, 100, seed => new VatWorld(), VatStep, 200, 10, 10)),
                ("core", () => RunFamily("core", N(3000), S(1), 30011, new[] { "Spawn", "Claim", "Die", "Tame", "Engine", "Pings", "ShipHit", "CampaignTile", "Drop", "SpendNoCarrier" }, new[] { 6, 8, 2, 1, 2, 6, 3, 1, 2, 1 }, 100, seed => new CoreWorld(), CoreStep, 200, 100, 100)),
                ("log", () => RunFamily("log", N(3000), S(1), 15485863, new[] { "Ping", "CarrierDies", "PerEntry" }, new[] { 20, 1, 1 }, 80, seed => new LogWorld(), LogStep, 10, 10, 10)),
                ("unjoin", () => RunFamily("unjoin", N(2000), S(1), 32452843, new[] { "Sort" }, new[] { 1 }, 20, seed => (object)null, UnjoinStep, 16, 10, 10)),
                ("units", () => Units(N(1000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine("fuzz " + f.name + ": " + (Cases - c0) + " cases, " + (Steps - s0) + " steps, " + t.Elapsed.TotalSeconds.ToString("F2") + "s, " + (fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES"));
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                string[] mustSee = { "gut.casting", "gut.overCap", "swallow.begin", "swallow.finish", "swallow.knock", "swallow.release", "swallow.stranger", "vat.accepted", "vat.finished", "vat.dormant", "vat.split",
                    "core.claimed", "core.carrierDied", "core.ping", "core.engineAppeared", "log.entry", "log.site", "log.cutLetter", "unjoin.removed", "unjoin.husk" };
                var missing = mustSee.Where(k => !Stats.ContainsKey(k)).ToList();
                Console.WriteLine("coverage: " + string.Join(" ", mustSee.Select(k => k + "=" + (Stats.TryGetValue(k, out long v) ? v : 0))));
                if (missing.Count > 0) { Console.WriteLine("FAIL the fuzz never reached: " + string.Join(", ", missing)); ok = false; }
            }
            foreach (string i in Info.Distinct()) Console.WriteLine("info " + i);
            Console.WriteLine("therot fuzz: " + Cases + " cases, " + Steps + " steps, " + sw.Elapsed.TotalSeconds.ToString("F2") + "s total -> " + (ok ? "OK" : "FAILED"));
            return ok;
        }
    }
}
