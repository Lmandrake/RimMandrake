// Approach B for the Miasma: seeded random ACTION SEQUENCES over the Verse-free kernel the mod calls (RM_MiasmaKernel.cs):
//   creche  - the warden mother's young ledger: registration, the clean record, betrayal, returns, the one-shot succession
//   tame    - the self-taming timer of a stranded young
//   price   - the buyer schedule for held stranded young
//   decay   - decay-cell fuel digestion and the output curve
//   rot     - the rotting bed's clock, bones and stacks
//   flotsam - the yard's seed / restock cadence, request sizing and table pick
//   pick    - the three nearest-thing pickers against a brute-force reference
//   units   - tables, boundaries, the biome score, the attar balm
// The model (reference sets, double-precision oracles) is this file's own; every number under test comes from the production kernel.
// A failing sequence is shrunk by delta debugging and printed as `family seed N: message | actions`, so it replays exactly.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;

namespace RimMandrake.Miasma.Fuzz
{
    internal static class MiasmaFuzz
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

        // ===================================================================== creche: the young ledger

        private sealed class Young { public int id; public bool dead, destroyed, player; public override string ToString() { return "y" + id; } }

        private sealed class CrecheWorld
        {
            public RM_MiasmaKernel.CrecheLedger<Young> ledger = new RM_MiasmaKernel.CrecheLedger<Young>();
            public List<Young> all = new List<Young>();
            public List<Young> registered = new List<Young>();     // reference: registration order
            public bool motherDead, setting = true;
            public int promotions, nextId = 1, returned, nulls;
            public bool wasDone, wasBetrayed, wasDirty;
        }

        private static bool Eligible(Young y) { return !y.dead && !y.destroyed && y.player; }
        private static bool Owed(Young y) { return !y.dead && !y.destroyed && !y.player; }

        private static void CrecheStep(CrecheWorld w, Act a)
        {
            Young pick = w.all.Count == 0 ? null : w.all[a.a % w.all.Count];
            var L = w.ledger;
            bool doneBefore = L.successionDone, cleanBefore = L.recordClean, betrayedBefore = L.betrayed;
            var heirBefore = L.heir;
            switch (a.kind)
            {
                case 0: // a stranded young appears (registered once; a second registration is ignored)
                {
                    var y = new Young { id = w.nextId++ };
                    w.all.Add(y);
                    L.Register(y); w.registered.Add(y);
                    L.Register(y);
                    L.Register(null);
                    Check(L.young.Count(x => x == y) == 1, "a young was registered twice");
                    Check(L.young.Count(x => x == null) <= w.nulls, "Register(null) added a null");
                    break;
                }
                case 1: if (pick != null) pick.player = true; break;                         // it self-tames
                case 2: if (pick != null) pick.dead = true; break;
                case 3: if (pick != null) pick.destroyed = true; break;
                case 4: L.BreakRecord(); break;
                case 5: L.Betray(); Hit("creche.betray"); break;
                case 6: // carried back to its mother (the caller refuses when the mother is betrayed)
                {
                    if (pick == null || RM_MiasmaKernel.ReturnRefused(L.betrayed)) break;
                    int before = L.returnedCount;
                    pick.player = false;
                    L.NoteReturned(pick);
                    w.registered.Remove(pick);
                    Check(L.returnedCount == before + 1 && !L.young.Contains(pick), "a returned young stayed owed");
                    Hit("creche.returned");
                    break;
                }
                case 7: w.motherDead = true; break;
                case 8: // the comp's poll
                {
                    if (!L.PollDue(w.setting) || !w.motherDead) break;
                    Young want = w.registered.FirstOrDefault(Eligible);
                    Young got = L.TryPromote(Eligible);
                    Check(got == want, "promoted " + got + ", the first eligible young in registration order is " + want);
                    Check(L.successionDone, "an attempt did not spend the creche's one succession");
                    if (got != null) { w.promotions++; Check(L.heir == got, "heir not recorded"); Hit("creche.heir"); } else Hit("creche.noheir");
                    break;
                }
                case 9: w.setting = !w.setting; break;
                case 10: // save + load: Scribe copies the list by reference and the fields by value
                {
                    var n = new RM_MiasmaKernel.CrecheLedger<Young>();
                    n.young = new List<Young>(L.young);
                    // Scribe_Collections (reference mode) hands back a null for a young that was destroyed while off the map
                    for (int i = 0; i < n.young.Count; i++)
                        if (n.young[i] != null && n.young[i].destroyed && (a.b & 1) == 0) { w.registered.Remove(n.young[i]); n.young[i] = null; w.nulls++; Hit("creche.nulled"); }
                    n.recordClean = L.recordClean; n.heir = L.heir; n.successionDone = L.successionDone; n.betrayed = L.betrayed; n.returnedCount = L.returnedCount;
                    w.ledger = n;
                    break;
                }
            }
            L = w.ledger;
            // ---- invariants
            Check(L.young.Where(y => y != null).Distinct().Count() == L.young.Count(y => y != null) && L.young.Count(y => y == null) <= w.nulls, "the young list holds a duplicate or an unexplained null");
            Check(L.young.Where(y => y != null).SequenceEqual(w.registered), "the young list drifted from the registration order");
            if (doneBefore) Check(L.successionDone, "a spent succession came back");
            if (!cleanBefore) Check(!L.recordClean, "a broken record healed");
            if (betrayedBefore) Check(L.betrayed && !L.recordClean && L.successionDone && L.heir == null, "a betrayal was undone or left an heir");
            if (L.betrayed) Check(!L.recordClean && L.successionDone && L.heir == null, "a betrayed creche is not void");
            if (L.heir != null) { Check(L.successionDone && !L.betrayed, "an heir without a spent succession, or in a betrayed creche"); Check(L.young.Contains(L.heir) || w.ledger.heir == heirBefore, "the heir is not one of the young"); }
            Check(L.YoungOwed(Owed) == w.registered.Count(Owed), "owed " + L.YoungOwed(Owed) + " != reference " + w.registered.Count(Owed));
            Check(w.promotions <= 1, "the creche promoted " + w.promotions + " heirs (one attempt, ever)");
            Check(L.PollDue(w.setting) == (!L.successionDone && w.setting), "PollDue disagrees with its definition");
            if (L.successionDone) Check(!L.PollDue(true), "a spent creche is still polled");
        }

        // ===================================================================== tame: the self-taming timer

        private sealed class TameWorld
        {
            public int next = -1, now = 1000;
            public bool setting = true, hasLedger = true, clean = true, tamed;
            public Random rng;
            public int intervalDraws, chanceDraws, schedules;
            public float p = 0.12f;
        }

        private static void TameStep(TameWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0:
                {
                    w.now += new[] { 1, 7, 100, 700, 2000, 3200, 9000 }[a.a % 7];
                    int nextBefore = w.next;
                    w.intervalDraws = w.chanceDraws = 0;
                    bool did = RM_MiasmaKernel.SelfTameStep(ref w.next, w.now, () => { w.intervalDraws++; return 2000 + w.rng.Next(1201); }, w.setting, w.hasLedger, w.clean, () => { w.chanceDraws++; return w.rng.NextDouble() < w.p; });
                    if (nextBefore < 0)
                    {
                        Check(!did && w.intervalDraws == 1 && w.chanceDraws == 0, "the first look must only schedule");
                        Check(w.next >= w.now + 2000 && w.next <= w.now + 3200, "first check scheduled " + (w.next - w.now) + " ticks out (2000..3200)");
                        break;
                    }
                    if (w.now < nextBefore) { Check(!did && w.next == nextBefore && w.intervalDraws == 0 && w.chanceDraws == 0, "an early step changed the timer or rolled"); break; }
                    Check(w.intervalDraws == 1 && w.next >= w.now + 2000 && w.next <= w.now + 3200, "a due step must reschedule exactly once, 2000..3200 out");
                    bool allowed = w.setting && !(w.hasLedger && !w.clean);
                    Check(w.chanceDraws == (allowed ? 1 : 0), "the chance was rolled " + w.chanceDraws + " times where " + (allowed ? 1 : 0) + " expected (option " + w.setting + ", ledger " + w.hasLedger + ", clean " + w.clean + ")");
                    if (did) { Check(allowed, "a young tamed while barred"); Hit("tame.tamed"); }
                    if (!allowed) Hit("tame.barred");
                    break;
                }
                case 1: w.setting = !w.setting; break;
                case 2: w.clean = false; break;
                case 3: w.hasLedger = !w.hasLedger; break;
                case 4: w.p = new[] { 0f, 0.12f, 0.5f, 1f }[a.a % 4]; break;
            }
        }

        // ===================================================================== price: the buyer schedule

        private sealed class PriceWorld
        {
            public List<int> offered = new List<int>();
            public Dictionary<int, int> at = new Dictionary<int, int>();
            public HashSet<int> held = new HashSet<int>();
            public Dictionary<int, int> firstSeen = new Dictionary<int, int>();
            public Dictionary<int, int> sentTimes = new Dictionary<int, int>();
            public int now = 2500;
            public Random rng;
            public double successRate = 0.5;
            public List<int> everOffered = new List<int>();
        }

        private static void PriceStep(PriceWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: w.held.Add(a.a % 6); break;                 // a young comes into the player's hands
                case 1: w.held.Remove(a.a % 6); break;               // it leaves (returned, sold, dead)
                case 2: // a poll (every 2500 ticks), with a gap
                {
                    w.now += 2500 * (1 + a.a % 40);
                    var atBefore = new Dictionary<int, int>(w.at);
                    var offeredBefore = new List<int>(w.offered);
                    var sends = new List<int>();
                    var heldNow = w.held.OrderBy(x => x).ToList();
                    RM_MiasmaKernel.BuyerPoll(w.offered, w.at, heldNow, w.now, (lo, hi) => lo + w.rng.Next(hi - lo), id => { sends.Add(id); return w.rng.NextDouble() < w.successRate; });
                    foreach (int id in heldNow)
                    {
                        if (offeredBefore.Contains(id)) { Check(!sends.Contains(id), "an already-offered young got a second buyer"); continue; }
                        if (!atBefore.ContainsKey(id))
                        {
                            Check(w.at.ContainsKey(id) && w.at[id] >= w.now + 60000 && w.at[id] < w.now + 120000, "first sighting booked a buyer " + (w.at.ContainsKey(id) ? (w.at[id] - w.now).ToString() : "never") + " ticks out (60000..120000)");
                            Check(!sends.Contains(id), "a buyer was sent on the first sighting");
                            Hit("price.booked");
                        }
                        else if (w.now < atBefore[id]) Check(!sends.Contains(id) && w.at[id] == atBefore[id], "a buyer was sent or rebooked before its day");
                        else
                        {
                            Check(sends.Count(x => x == id) == 1, "a due young was tried " + sends.Count(x => x == id) + " times");
                            Hit("price.tried");
                            if (w.offered.Contains(id)) { Check(!w.at.ContainsKey(id), "an offered young kept its booking"); Hit("price.offered"); }
                            else { Check(w.at[id] == w.now + 60000, "a failed send rebooked " + (w.at[id] - w.now) + " ticks out (60000)"); Hit("price.retry"); }
                        }
                    }
                    foreach (int id in sends) Check(heldNow.Contains(id), "a buyer was sent for a young not held");
                    Check(w.offered.Distinct().Count() == w.offered.Count, "a young was offered twice");
                    foreach (int id in w.offered) if (!w.everOffered.Contains(id)) w.everOffered.Add(id);
                    Check(offeredBefore.All(w.offered.Contains), "an offer was forgotten");
                    if (w.at.Keys.Any(k => !w.held.Contains(k) && !w.offered.Contains(k))) Hit("price.staleBooking");      // a booking for a young that left is never cleared
                    break;
                }
                case 3: w.successRate = new[] { 0.0, 0.5, 1.0 }[a.a % 3]; break;
            }
        }

        // ===================================================================== decay: digestion

        private sealed class DecayWorld
        {
            public float fuel = 5f, capacity = 10f, lifetime = 600f, minFraction = 0.3f;
            public float lastFuel = -1f, digested;
            public double trueBurn, undercountBound;
            public bool spent, hasSpentDef = true, spawned = true;
            public int observations;
            public bool firstWindowDone;
            public Random rng;
        }

        private static void DecayStep(DecayWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // a 250 tick window: burn, maybe a refill (before or after), then the observation
                {
                    float burn = new[] { 0f, 0.1f, 0.5f, 2f, 7f }[a.a % 5];
                    float refill = new[] { 0f, 0f, 0f, 1f, 4f, 10f }[a.b % 6];
                    bool refillFirst = a.c % 2 == 0;
                    float start = w.fuel;
                    if (refillFirst) w.fuel = Math.Min(w.capacity, w.fuel + refill);
                    float burned = Math.Min(burn, w.fuel);
                    w.fuel -= burned;
                    if (!refillFirst) w.fuel = Math.Min(w.capacity, w.fuel + refill);
                    bool seenBefore = w.lastFuel >= 0f;
                    float digestedBefore = w.digested;
                    bool becomes = RM_MiasmaKernel.DecayObserve(ref w.lastFuel, ref w.digested, w.fuel, w.lifetime, w.hasSpentDef, w.spawned);
                    Check(w.digested >= digestedBefore, "digestion went backwards");
                    Check(w.lastFuel == w.fuel, "the last look was not recorded");
                    if (seenBefore)
                    {
                        w.trueBurn += burned;
                        // exact when no refill fell inside the window; otherwise it may only UNDER-count, by at most min(burn, refill)
                        if (refill == 0f || w.fuel >= start) { }
                        double added = w.digested - digestedBefore;
                        double net = start - w.fuel;
                        Check(Math.Abs(added - Math.Max(0.0, net)) < 1e-4, "digested " + F(added) + " in a window where fuel went " + F(start) + " -> " + F(w.fuel));
                        if (refill == 0f) Check(Math.Abs(added - burned) < 1e-4, "a refill-free window digested " + F(added) + " but burned " + burned);
                        else w.undercountBound += Math.Min(burned, refill);
                        Check(added <= burned + 1e-4, "digested more than burned");
                    }
                    else { w.firstWindowDone = true; Check(w.digested == 0f, "digestion counted before the first look"); }
                    Check(w.digested <= w.trueBurn + 1e-3, "digested " + w.digested + " over the true burn " + F(w.trueBurn));
                    Check(w.trueBurn - w.digested <= w.undercountBound + 1e-3, "digestion under-counts the true burn by " + F(w.trueBurn - w.digested) + " (bound " + F(w.undercountBound) + ")");
                    Check(becomes == (w.digested >= w.lifetime && w.hasSpentDef && w.spawned), "spent=" + becomes + " at digested " + w.digested + "/" + w.lifetime);
                    if (becomes) { w.spent = true; Hit("decay.spent"); w.digested = 0f; w.lastFuel = -1f; w.trueBurn = 0; w.undercountBound = 0; w.fuel = 5f; }
                    break;
                }
                case 1: w.hasSpentDef = !w.hasSpentDef; break;
                case 2: w.spawned = !w.spawned; break;
                case 3: // the output curve at a random fullness
                {
                    float f1 = (a.a % 101) / 100f, f2 = Math.Min(1f, f1 + (a.b % 40) / 100f);
                    float o1 = RM_MiasmaKernel.OutputFraction(f1, w.minFraction), o2 = RM_MiasmaKernel.OutputFraction(f2, w.minFraction);
                    Check(o1 >= 0f && o1 <= 1f && o2 <= 1f, "output fraction outside [0,1]");
                    Check(f1 > 0f ? o1 >= w.minFraction - 1e-6f : o1 == 0f, "output " + o1 + " at fullness " + f1 + " (min " + w.minFraction + ")");
                    Check(o2 >= o1 - 1e-6f, "more fuel gave less power");
                    Check(RM_MiasmaKernel.OutputFraction(1f, w.minFraction) == 1f && RM_MiasmaKernel.OutputFraction(5f, w.minFraction) == 1f, "a full cell is not at full power");
                    Check(RM_MiasmaKernel.OutputFraction(-1f, w.minFraction) == 0f && RM_MiasmaKernel.OutputFraction(0f, w.minFraction) == 0f, "an empty cell makes power");
                    break;
                }
            }
        }

        // ===================================================================== rot: the rotting bed

        private sealed class RotWorld
        {
            public List<int> stored = new List<int>();     // corpse ids in the bed, in slot order
            public int target = -1, rotTicks, rotting = -1;   // rotting = corpse id; target is the kernel's "is something being rotted" flag
            public float days = 3f;
            public int nextId = 1;
            public int rotDone;
            public Dictionary<int, int> presentTicks = new Dictionary<int, int>();   // reference: consecutive rare ticks as the rotting corpse
            public int refRotting = -1, refTicks;
        }

        private static void RotTick(RotWorld w)
        {
            int rotDown = RM_MiasmaKernel.RotDownTicks(w.days, 60000);
            bool valid = w.rotting >= 0 && w.stored.Contains(w.rotting);
            int candidate = valid ? -1 : (w.stored.Count > 0 ? w.stored[0] : -1);
            int targetFlag = w.rotting >= 0 ? 0 : -1;
            int ticksBefore = w.rotTicks;
            RM_MiasmaKernel.RotStep(ref targetFlag, ref w.rotTicks, valid, candidate, rotDown, out bool done);
            if (!valid) w.rotting = candidate;
            // reference clock
            if (!valid) { w.refRotting = candidate; w.refTicks = 0; }
            if (w.refRotting >= 0)
            {
                w.refTicks += 250;
                bool fin = w.refTicks >= rotDown;
                Check(done == fin, "rot done=" + done + " at " + w.refTicks + "/" + rotDown + " ticks");
                if (fin) { w.stored.Remove(w.refRotting); w.refRotting = -1; w.refTicks = 0; w.rotting = -1; w.rotDone++; Hit("rot.done"); }
                else Check(w.rotTicks == w.refTicks, "rot clock " + w.rotTicks + " != reference " + w.refTicks);
            }
            else Check(!done && w.rotTicks == 0, "a rot tick with nothing stored advanced the clock");
            if (done) Check(w.rotTicks == 0, "a finished rot left its clock running");
            Check(w.rotTicks <= rotDown, "rot clock " + w.rotTicks + " ran past the rot-down length " + rotDown);
        }

        private static void RotStepFn(RotWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: w.stored.Add(w.nextId++); break;
                case 1: if (w.stored.Count > 0) w.stored.RemoveAt(a.a % w.stored.Count); break;           // stolen, hauled out, or decayed
                case 2: for (int i = 0, n = 1 + a.a % 30; i < n; i++) RotTick(w); break;
                case 3: w.days = new[] { 0.5f, 1f, 3f, 10f, 0.001f }[a.a % 5]; break;
            }
        }

        // ===================================================================== flotsam

        private static readonly float[] FlotsamWeights = { 4f, 4f, 3f, 1f };

        private sealed class FlotsamWorld
        {
            public bool seeded; public int last = -1, recede = -1, placed;
            public int seeds, restocks;
            public float amount = 1f;
        }

        private static void FlotsamStepFn(FlotsamWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // the yard's 250 tick look
                {
                    bool seededBefore = w.seeded; int lastBefore = w.last;
                    int stacks = RM_MiasmaKernel.FlotsamStep(ref w.seeded, ref w.last, w.recede);
                    if (!seededBefore) { Check(stacks == 24 && w.seeded && w.last == w.recede, "first look must seed 24 and record the recede tick"); w.seeds++; Hit("flotsam.seed"); }
                    else if (w.recede > lastBefore) { Check(stacks == 14 && w.last == w.recede, "a recede must restock 14"); w.restocks++; Hit("flotsam.restock"); }
                    else Check(stacks == 0 && w.last == lastBefore, "no new recede and still " + stacks + " stacks");
                    Check(w.seeds <= 1, "the yard seeded twice");
                    if (stacks > 0)
                    {
                        int want = RM_MiasmaKernel.FlotsamWant(stacks, w.amount, w.placed);
                        int cap = (int)Math.Round(70 * w.amount), req = (int)Math.Round(stacks * w.amount);
                        Check(want == Math.Min(req, cap - w.placed), "want " + want + " != min(request " + req + ", room " + (cap - w.placed) + ")");
                        if (want > 0) { Check(w.placed + want <= cap, "the yard would pass its cap"); w.placed += want; }
                    }
                    break;
                }
                case 1: w.recede = Math.Max(w.recede, 1000 * (1 + a.a % 50)) + (a.b % 3 == 0 ? 0 : 500); break;       // a recede completes (tick moves forward)
                case 2: w.recede = -1; break;                                                                         // no gradient axis component
                case 3: w.amount = new[] { 0.25f, 0.5f, 1f, 2f, 3f }[a.a % 5]; break;
                case 4: w.placed = Math.Max(0, w.placed - (a.a % 30)); break;                                         // goods get hauled away
            }
        }

        // ===================================================================== pick: the nearest-thing pickers

        private static void PickStep(object _, Act a)
        {
            var r = new Random(a.a * 1000 + a.b);
            int n = r.Next(0, 9);
            var d = new List<float>();
            for (int i = 0; i < n; i++) d.Add(r.Next(0, 6) * 4f + (r.Next(5) == 0 ? 1f : 0f));    // many exact ties
            float max = new[] { 0f, 4f, 9f, 16f, 20f, 100f }[a.c % 6];
            // reference: indices within bound, then first/last of the minimum
            Func<bool, int> firstMin = inclusive =>
            {
                var cand = Enumerable.Range(0, n).Where(i => inclusive ? d[i] <= max : d[i] < max).ToList();
                if (cand.Count == 0) return -1;
                float m = cand.Min(i => d[i]);
                return cand.First(i => d[i] == m);
            };
            var inc = Enumerable.Range(0, n).Where(i => d[i] <= max).ToList();
            int lastMin = inc.Count == 0 ? -1 : inc.Last(i => d[i] == inc.Min(j => d[j]));
            Check(RM_MiasmaKernel.NearestFirstInclusive(d, max) == firstMin(true), "NearestFirstInclusive " + RM_MiasmaKernel.NearestFirstInclusive(d, max) + " vs " + firstMin(true) + " for [" + string.Join(",", d) + "] max " + max);
            Check(RM_MiasmaKernel.NearestFirstStrict(d, max) == firstMin(false), "NearestFirstStrict " + RM_MiasmaKernel.NearestFirstStrict(d, max) + " vs " + firstMin(false) + " for [" + string.Join(",", d) + "] max " + max);
            Check(RM_MiasmaKernel.NearestLastInclusive(d, max) == lastMin, "NearestLastInclusive " + RM_MiasmaKernel.NearestLastInclusive(d, max) + " vs " + lastMin + " for [" + string.Join(",", d) + "] max " + max);
            if (n > 1 && d.Distinct().Count() < n) Hit("pick.ties");
            if (d.Any(x => x == max)) Hit("pick.atBound");
        }

        // ===================================================================== units

        public static List<string> Units(int n, int baseSeed)
        {
            var fails = new List<string>();
            Action<string> bad = m => { if (fails.Count < 8) fails.Add("units: " + m); };
            var r = new Random(baseSeed);

            // --- bones and rot length
            Cases++;
            {
                if (RM_MiasmaKernel.RotDownTicks(3f, 60000) != 180000 || RM_MiasmaKernel.RotDownTicks(0.5f, 60000) != 30000 || RM_MiasmaKernel.RotDownTicks(0.001f, 60000) != 2500 || RM_MiasmaKernel.RotDownTicks(0f, 60000) != 2500) bad("rot-down length table");
                if (RM_MiasmaKernel.BonesFor(0f, 8f) != 1 || RM_MiasmaKernel.BonesFor(1f, 8f) != 8 || RM_MiasmaKernel.BonesFor(0.01f, 8f) != 1 || RM_MiasmaKernel.BonesFor(6f, 8f) != 48) bad("bones table");
                float prev = 0;
                for (float s = 0; s < 12; s += 0.05f) { Steps++; int b = RM_MiasmaKernel.BonesFor(s, 8f); if (b < prev || b < 1) bad("bones fell or went under 1 at body size " + s); prev = b; }
                for (int k = 0; k < Math.Max(1, n / 5); k++)
                {
                    Steps++;
                    int total = r.Next(0, 5000), limit = r.Next(1, 200);
                    var st = RM_MiasmaKernel.StackSplit(total, limit);
                    if (st.Sum() != total) bad("stacks " + string.Join("+", st.Take(4)) + "... sum " + st.Sum() + " != " + total);
                    if (st.Any(x => x < 1 || x > limit)) bad("a stack outside 1.." + limit);
                    if (st.Count > 0 && st.Take(st.Count - 1).Any(x => x != limit)) bad("a non-final stack is not full");
                    if (st.Count != (total + limit - 1) / limit) bad("stack count " + st.Count + " for " + total + "/" + limit);
                }
            }

            // --- flotsam pick: proportional, edges
            Cases++;
            {
                var counts = new int[4]; int N = 200000;
                for (int i = 0; i < N; i++) { Steps++; counts[RM_MiasmaKernel.FlotsamPick(FlotsamWeights, (float)r.NextDouble())]++; }
                double[] share = { 4 / 12.0, 4 / 12.0, 3 / 12.0, 1 / 12.0 };
                for (int i = 0; i < 4; i++) if (Math.Abs(counts[i] / (double)N - share[i]) > 0.01) bad("flotsam row " + i + " share " + counts[i] / (double)N + ", want " + share[i]);
                if (RM_MiasmaKernel.FlotsamPick(FlotsamWeights, 0f) != 0) bad("roll 0 should pick the first row");
                if (RM_MiasmaKernel.FlotsamPick(FlotsamWeights, MathF.BitDecrement(1f)) != 3) bad("the top of the range should pick the last row");
                if (RM_MiasmaKernel.FlotsamPick(new float[0], 0.5f) != 0) bad("an empty table must fall back to row 0");
            }

            // --- reach / protocol tables
            Cases++;
            {
                Steps += 8;
                if (RM_MiasmaKernel.ReachOrDefault(null) != 16f || RM_MiasmaKernel.ReachOrDefault(0f) != 16f || RM_MiasmaKernel.ReachOrDefault(-3f) != 16f || RM_MiasmaKernel.ReachOrDefault(22f) != 22f) bad("reach defaults");
                if (!RM_MiasmaKernel.ReturnInReach(true, 16f, 16f) || RM_MiasmaKernel.ReturnInReach(true, 16.01f, 16f) || RM_MiasmaKernel.ReturnInReach(false, 1f, 16f)) bad("return reach boundary");
                if (RM_MiasmaKernel.SaleCounts(false, true) || RM_MiasmaKernel.SaleCounts(true, false) || !RM_MiasmaKernel.SaleCounts(true, true)) bad("sale gate");
                if (!RM_MiasmaKernel.ReturnRefused(true) || RM_MiasmaKernel.ReturnRefused(false)) bad("betrayed mother must refuse");
            }

            // --- attar balm: a scar of severity s needs ceil((s - 0.01) / 3) applications
            Cases++;
            for (float s = 0.05f; s < 30f; s += 0.37f)
            {
                Steps++;
                float cur = s; int applications = 0; bool removed = false;
                while (!removed && applications < 50) { cur = RM_MiasmaKernel.BalmScar(cur, out removed); applications++; if (cur < 0f) bad("balm took a scar negative"); }
                int want = (int)Math.Ceiling((s - 0.01f) / 3f - 1e-6f); if (want < 1) want = 1;
                if (applications != want) bad("a scar of " + s + " took " + applications + " balms, expected " + want);
            }

            // --- biome score
            Cases++;
            {
                var rg = new RM_MiasmaKernel.BiomeRanges { tempMin = 20f, tempMax = 55f, rainMin = 1000f, rainMax = 4000f, elevMin = 0f, elevMax = 200f, baseScore = 30f, degreeWeight = 0.4f, rainfallDivisor = 300f, riverOrCoastBonus = 12f, spawnChance = 0.04f };
                Func<float, bool> always = g => true, never = g => false;
                Steps += 12;
                if (RM_MiasmaKernel.BiomeScore(true, false, false, true, 1f, 30f, 2000f, 50f, rg, always) != -100f) bad("a null tile scored");
                if (RM_MiasmaKernel.BiomeScore(false, true, false, true, 1f, 30f, 2000f, 50f, rg, always) != -100f) bad("water scored");
                if (RM_MiasmaKernel.BiomeScore(false, false, false, true, 0f, 30f, 2000f, 50f, rg, always) != -100f) bad("rarity 0 scored");
                if (RM_MiasmaKernel.BiomeScore(false, false, true, true, 1f, 30f, 2000f, 50f, rg, always) != 0f) bad("mountains scored");
                if (RM_MiasmaKernel.BiomeScore(false, false, false, false, 1f, 30f, 2000f, 50f, rg, always) != 0f) bad("a tile with no river scored");
                if (RM_MiasmaKernel.BiomeScore(false, false, false, true, 1f, 30f, 2000f, 50f, rg, never) != 0f) bad("a failed gate scored");
                if (RM_MiasmaKernel.BiomeScore(false, false, false, true, 1f, 19.9f, 2000f, 50f, rg, always) != 0f || RM_MiasmaKernel.BiomeScore(false, false, false, true, 1f, 30f, 4000f, 50f, rg, always) != 0f) bad("range edges");
                float want = 30f + (30f - 20f) * 0.4f + (2000f - 1000f) / 300f + 12f;
                if (Math.Abs(RM_MiasmaKernel.BiomeScore(false, false, false, true, 1f, 30f, 2000f, 50f, rg, always) - want) > 1e-4f) bad("score arithmetic");
                bool seen = false;
                RM_MiasmaKernel.BiomeScore(false, false, false, true, 30f, 30f, 2000f, 50f, rg, g => { seen = true; return true; });
                if (seen) bad("a gate of 1.2 must not roll");
                for (int k = 0; k < Math.Max(1, n / 50); k++)
                {
                    Steps++;
                    float t = (float)(20 + r.NextDouble() * 35), rain = (float)(1000 + r.NextDouble() * 2999), el = (float)(r.NextDouble() * 200);
                    float s1 = RM_MiasmaKernel.BiomeScore(false, false, false, true, 1f, t, rain, el, rg, always);
                    float s2 = RM_MiasmaKernel.BiomeScore(false, false, false, true, 1f, Math.Min(55f, t + 2f), rain, el, rg, always);
                    if (s2 < s1 - 1e-4f) bad("the Miasma scores a COLDER tile higher (warmer is better): " + s1 + " -> " + s2);
                    if (s1 < 42f) bad("an eligible tile scored " + s1 + " under base + river bonus");
                }
            }

            // --- tightening found by the mutation proof (each line pins a defect the first fuzz let through)
            Cases++;
            try
            {
                Steps += 40;
                if (RM_MiasmaKernel.Lerp(2f, 6f, -1f) != 2f || RM_MiasmaKernel.Lerp(2f, 6f, 2f) != 6f || RM_MiasmaKernel.Lerp(2f, 6f, 0.5f) != 4f) bad("Lerp must clamp t to 0..1");
                for (float m = 0f; m <= 1f; m += 0.125f)
                    for (float f = 0.0625f; f <= 1.25f; f += 0.1875f)
                    {
                        float want = m + (1f - m) * Math.Min(1f, f);
                        if (Math.Abs(RM_MiasmaKernel.OutputFraction(f, m) - want) > 1e-5f) bad("output fraction at fullness " + f + " min " + m + " is " + RM_MiasmaKernel.OutputFraction(f, m) + ", want " + want);
                    }
                if (RM_MiasmaKernel.RotDownTicks(0.50001f, 60000) != 30001 || RM_MiasmaKernel.RotDownTicks(0.49999f, 60000) != 29999 || RM_MiasmaKernel.RotDownTicks(1f, 2500) != 2500) bad("rot-down length must round to nearest");
                // the buyer books 60000..120000 ticks out and is tried on the day, not a tick before
                {
                    var offered = new List<int>(); var at = new Dictionary<int, int>(); int sends = 0;
                    var held = new[] { 7 };
                    RM_MiasmaKernel.BuyerPoll(offered, at, held, 1000, (lo, hi) => 60000, id => { sends++; return true; });
                    if (sends != 0 || at[7] != 61000) bad("first sighting must book now+roll and send nothing");
                    RM_MiasmaKernel.BuyerPoll(offered, at, held, 60999, (lo, hi) => 60000, id => { sends++; return true; });
                    if (sends != 0) bad("a buyer was sent one tick before its day");
                    RM_MiasmaKernel.BuyerPoll(offered, at, held, 61000, (lo, hi) => 60000, id => { sends++; return false; });
                    if (sends != 1 || at[7] != 121000 || offered.Count != 0) bad("a failed send must rebook 60000 ticks out");
                }
                // a finished rot clears its target (the next bed tick must pick a new corpse, not keep rotting the old one)
                {
                    int target = 0, rot = 2500 - 250; bool done;
                    RM_MiasmaKernel.RotStep(ref target, ref rot, true, -1, 2500, out done);
                    if (!done || target != -1 || rot != 0) bad("a finished rot left target " + target + " / clock " + rot);
                }
                // a roll that lands exactly on a cumulative weight belongs to the row it closes
                {
                    var w = new float[] { 1f, 1f, 2f };
                    if (RM_MiasmaKernel.FlotsamPick(w, 0.25f) != 0 || RM_MiasmaKernel.FlotsamPick(w, 0.5f) != 1 || RM_MiasmaKernel.FlotsamPick(w, 0.75f) != 2 || RM_MiasmaKernel.FlotsamPick(w, 0.4999f) != 1) bad("flotsam pick boundary rolls");
                }
                // a zero rainfall divisor must not divide by zero
                {
                    var rg = new RM_MiasmaKernel.BiomeRanges { tempMin = 20f, tempMax = 55f, rainMin = 1000f, rainMax = 4000f, elevMin = 0f, elevMax = 200f, baseScore = 30f, degreeWeight = 0.4f, rainfallDivisor = 0f, riverOrCoastBonus = 12f, spawnChance = 1f };
                    float sc = RM_MiasmaKernel.BiomeScore(false, false, false, true, 1f, 30f, 2000f, 50f, rg, g => true);
                    if (float.IsInfinity(sc) || float.IsNaN(sc) || Math.Abs(sc - (30f + 4f + 1000f + 12f)) > 1e-3f) bad("a zero rainfall divisor gave " + sc);
                }
            }
            catch (Exception ex) { bad("tightening block threw " + ex.GetType().Name + ": " + ex.Message); }
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
                ("creche", () => RunFamily("creche", N(4000), S(1), 7919, new[] { "Young", "Tame", "Die", "Destroy", "Harm", "Sell", "Return", "MotherDies", "Poll", "Setting", "Reload" }, new[] { 10, 3, 2, 1, 2, 1, 3, 2, 6, 1, 2 }, 100, seed => new CrecheWorld(), CrecheStep, 20, 10, 10)),
                ("tame", () => RunFamily("tame", N(3000), S(1), 104729, new[] { "Step", "Setting", "Harm", "Ledger", "Chance" }, new[] { 20, 1, 1, 1, 1 }, 150, seed => new TameWorld { rng = new Random(seed * 3 + 1) }, TameStep, 10, 10, 10)),
                ("price", () => RunFamily("price", N(3000), S(1), 6007, new[] { "Hold", "Release", "Poll", "SendRate" }, new[] { 4, 2, 10, 1 }, 100, seed => new PriceWorld { rng = new Random(seed * 5 + 1) }, PriceStep, 60, 10, 10)),
                ("decay", () => RunFamily("decay", N(3000), S(1), 30011, new[] { "Window", "SpentDef", "Spawned", "Curve" }, new[] { 20, 1, 1, 2 }, 150, seed => new DecayWorld { rng = new Random(seed), minFraction = new[] { 0f, 0.3f, 0.8f }[seed % 3], lifetime = new[] { 20f, 100f, 600f }[seed % 3] }, DecayStep, 100, 100, 100)),
                ("rot", () => RunFamily("rot", N(3000), S(1), 15485863, new[] { "Add", "Remove", "Ticks", "Days" }, new[] { 4, 3, 10, 1 }, 100, seed => new RotWorld(), RotStepFn, 100, 10, 10)),
                ("flotsam", () => RunFamily("flotsam", N(3000), S(1), 32452843, new[] { "Look", "Recede", "NoAxis", "Amount", "Haul" }, new[] { 12, 3, 1, 1, 2 }, 100, seed => new FlotsamWorld(), FlotsamStepFn, 100, 10, 10)),
                ("pick", () => RunFamily("pick", N(20000), S(1), 49979687, new[] { "Pick" }, new[] { 1 }, 20, seed => (object)null, PickStep, 5000, 1000, 1000)),
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
                string[] mustSee = { "creche.nulled", "creche.betray", "creche.returned", "creche.heir", "creche.noheir", "tame.tamed", "tame.barred", "price.booked", "price.tried", "price.offered", "price.retry",
                    "decay.spent", "rot.done", "flotsam.seed", "flotsam.restock", "pick.ties", "pick.atBound" };
                var missing = mustSee.Where(k => !Stats.ContainsKey(k)).ToList();
                if (Stats.TryGetValue("price.staleBooking", out long stale)) Info.Add("buyer bookings outlive the young that left the player's hands (never cleared): seen in " + stale + " polls");
                Console.WriteLine("coverage: " + string.Join(" ", mustSee.Select(k => k + "=" + (Stats.TryGetValue(k, out long v) ? v : 0))));
                if (missing.Count > 0) { Console.WriteLine("FAIL the fuzz never reached: " + string.Join(", ", missing)); ok = false; }
            }
            foreach (string i in Info.Distinct()) Console.WriteLine("info " + i);
            Console.WriteLine("miasma fuzz: " + Cases + " cases, " + Steps + " steps, " + sw.Elapsed.TotalSeconds.ToString("F2") + "s total -> " + (ok ? "OK" : "FAILED"));
            return ok;
        }
    }
}
