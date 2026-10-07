// Approach B for Inhabited: seeded random ACTION SEQUENCES over the two Verse-free kernels the mod calls,
//   InhabitedCustody    (who holds whom: displaced pool, rosters, the map; nobody is ever held by nothing) and
//   InhabitedFateKernel (fate cause, stock arithmetic, routine).
// The model (people, holders, map goods, event log) is this file's own; every decision comes from the production kernel.
// A failing sequence is shrunk by delta debugging and printed as `family seed N: message | actions`, so it replays exactly.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Inhabited.SelfTest
{
    internal static class InhabitedFuzz
    {
        public static long Cases, Steps;

        internal struct Act
        {
            public int kind, a, b, c, d;
            public string Name;
            public override string ToString() { return Name + "(" + a + "," + b + "," + c + "," + d + ")"; }
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

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

        // ===================================================================== people model (shared by pool and place)

        private const int Ground = 0, InPool = 1, InRosterA = 2, InRosterB = 3, Recruited = 4, Lost = -1, Dead = -2;

        private sealed class Person
        {
            public int id, faction, holder;
            public bool dead, humanlike = true, downed;
        }

        private sealed class Hold
        {
            public int code;
            public List<int> m = new List<int>();
            public int cap = int.MaxValue;
        }

        private sealed class World
        {
            public List<Person> ps = new List<Person>();
            public Hold pool = new Hold { code = InPool }, ra = new Hold { code = InRosterA }, rb = new Hold { code = InRosterB };
            public DisplacementBook book = new DisplacementBook();
            public Dictionary<int, int> seq = new Dictionary<int, int>();
            public Dictionary<int, DisplacedReason> reasonM = new Dictionary<int, DisplacedReason>();
            public Dictionary<int, string> originM = new Dictionary<int, string>();
            public int seqNext;
            public HashSet<int> lost = new HashSet<int>();
            public bool poolRefuse, rosterRefuse;       // per-action fault injection
            public int prepareCalls;

            public Person Spawn(int faction, bool humanlike)
            {
                var p = new Person { id = ps.Count + 100, faction = faction, humanlike = humanlike };
                ps.Add(p);
                return p;
            }
            public Hold HoldOf(int code) { return code == InPool ? pool : code == InRosterA ? ra : rb; }
            public Person Get(int id) { return ps.First(x => x.id == id); }

            // ThingOwner semantics: TryAdd refuses a person already held elsewhere; TryAddOrTransfer would not, but the map
            // holds nobody here, so both reduce to "holder == Ground".
            public bool PoolTryAdd(Person p)
            {
                if (poolRefuse || p.holder != Ground) return false;
                pool.m.Add(p.id); p.holder = InPool; return true;
            }
            public bool PoolRemove(Person p)
            {
                if (p.holder != InPool) return false;
                pool.m.Remove(p.id); p.holder = Ground; return true;
            }
            public bool RosterTryAdd(Hold h, Person p)
            {
                if (rosterRefuse || p.holder != Ground) return false;
                h.m.Add(p.id); p.holder = h.code; return true;
            }
            public bool RosterRemove(Hold h, Person p)
            {
                if (p.holder != h.code) return false;
                h.m.Remove(p.id); p.holder = Ground; return true;
            }
            public void OnLost(Person p) { p.holder = Lost; lost.Add(p.id); }

            public bool Absorb(Person p, DisplacedReason r, string origin)
            {
                bool ok = InhabitedCustody.Absorb(book, p.id, p.dead, () => prepareCalls++, () => PoolTryAdd(p), r, origin);
                if (ok) { seq[p.id] = seqNext++; reasonM[p.id] = r; originM[p.id] = origin; }
                return ok;
            }
            public List<Person> Candidates(Func<Person, bool> f)     // what DisplacedPool.Candidates hands the kernel: pool order, then the kernel's Order
            {
                return InhabitedCustody.Order(book, pool.m.Select(Get).Where(p => !p.dead && f(p)), p => p.id);
            }
            public List<Person> Eligible(Func<Person, bool> f)
            {
                // independent oracle: longest-waiting first by the MODEL's own absorb sequence, never the kernel's ordering
                var elig = pool.m.Select(Get).Where(p => !p.dead && f(p)).OrderBy(p => seq[p.id]).ToList();
                return elig;
            }
        }

        private static readonly string[] Origins = { null, "Scrapyard", "Dune Camp" };

        private static void WorldInvariants(World w, int lostBefore, bool faulted)
        {
            // every person is held by exactly the holder their record names
            foreach (var p in w.ps)
            {
                int inLists = (w.pool.m.Contains(p.id) ? 1 : 0) + (w.ra.m.Contains(p.id) ? 1 : 0) + (w.rb.m.Contains(p.id) ? 1 : 0);
                bool listed = p.holder == InPool || p.holder == InRosterA || p.holder == InRosterB;
                Check(inLists == (listed ? 1 : 0), $"person {p.id} (holder {p.holder}) is in {inLists} holder lists");
                if (listed) Check(w.HoldOf(p.holder).m.Contains(p.id), $"person {p.id} claims holder {p.holder} but is not in its list");
                Check(!(p.holder == InPool && p.dead), $"dead person {p.id} is in the displaced pool");
            }
            Check(w.pool.m.Distinct().Count() == w.pool.m.Count, "duplicate in pool");
            // the metadata book describes exactly the pool's members
            var ids = new HashSet<int>(w.pool.m);
            Check(ids.SetEquals(w.book.reasons.Keys) && ids.SetEquals(w.book.origins.Keys) && ids.SetEquals(w.book.displacedAt.Keys),
                  $"book keys {string.Join(",", w.book.reasons.Keys)} / {string.Join(",", w.book.origins.Keys)} / {string.Join(",", w.book.displacedAt.Keys)} differ from pool members {string.Join(",", ids)}");
            foreach (int id in ids)
            {
                Check(w.book.reasons[id] == w.reasonM[id], $"person {id} reason changed in the pool");
                Check(w.book.origins[id] == w.originM[id], $"person {id} origin changed in the pool");
                Check(w.book.displacedAt[id] == w.seq[id], $"person {id} place in the queue changed ({w.seq[id]} -> {w.book.displacedAt[id]})");
            }
            Check(w.book.nextOrder == w.seqNext, $"nextOrder {w.book.nextOrder} != absorbs so far {w.seqNext} (an order was reused or skipped)");
            Check(w.book.displacedAt.Values.Distinct().Count() == w.book.displacedAt.Count, "two people share a place in the queue");
            // nobody is lost unless a fault was injected into this very action
            Check(w.lost.Count == w.ps.Count(p => p.holder == Lost), "lost set differs from persons marked lost");
            if (!faulted) Check(w.lost.Count == lostBefore, "someone was lost although no refusal was injected");
        }

        // ===================================================================== family: pool

        private static World MakePool(int seed)
        {
            var w = new World();
            var r = new Random(seed * 31 + 7);
            int n = r.Next(0, 5);
            for (int i = 0; i < n; i++) w.Spawn(r.Next(3), r.Next(5) != 0);
            return w;
        }

        private static void PoolStep(World w, Act a)
        {
            int lostBefore = w.lost.Count;
            w.poolRefuse = false; w.rosterRefuse = false;
            bool faulted = false;
            switch (a.kind)
            {
                case 0: w.Spawn(a.a % 3, a.b % 5 != 0); break;
                case 1: // absorb
                {
                    if (w.ps.Count == 0) break;
                    var p = w.ps[a.a % w.ps.Count];
                    w.poolRefuse = a.b % 5 == 0;
                    var reason = (DisplacedReason)(a.c % 6);
                    string origin = Origins[a.d % Origins.Length];
                    bool wantOk = !p.dead && p.holder == Ground && !w.poolRefuse;
                    int calls0 = w.prepareCalls, next0 = w.seqNext;
                    bool ok = w.Absorb(p, reason, origin);
                    Check(ok == wantOk, $"absorb of person {p.id} (dead {p.dead}, holder {p.holder}, poolRefuse {w.poolRefuse}) returned {ok}, expected {wantOk}");
                    Check((w.prepareCalls - calls0 == 1) == !p.dead, "absorb prepared (despawned) a dead person, or skipped a living one");
                    Check(w.seqNext == next0 + (ok ? 1 : 0), "absorb order counter");
                    break;
                }
                case 2: // draw into a roster
                {
                    int f = a.a % 3, count = a.b % 5 - 1;                 // -1..3: includes the no-op counts
                    var dest = a.c % 2 == 0 ? w.ra : w.rb;
                    dest.cap = 1 + (a.d / 8) % 4;
                    int mask = a.d % 8;                                      // refusal bits for the first three attempts
                    int throwAt = (a.d / 32) % 6 == 0 ? (a.d / 64) % 3 : -1;
                    w.poolRefuse = (a.d / 3) % 7 == 0;                       // putBack refused
                    faulted = w.poolRefuse;
                    var elig = w.Eligible(p => p.faction == f);
                    // oracle
                    var expArr = new List<int>(); var expLost = new List<int>(); bool expThrow = false; int attempt = 0, moved = 0;
                    if (count > 0)
                        foreach (var c in elig)
                        {
                            if (moved >= count) break;
                            bool throws = attempt == throwAt;
                            bool accept = !throws && ((mask >> attempt) & 1) == 0 && dest.m.Count + expArr.Count < dest.cap;
                            attempt++;
                            if (throws) { expThrow = true; if (w.poolRefuse) expLost.Add(c.id); break; }
                            if (accept) { expArr.Add(c.id); moved++; } else if (w.poolRefuse) expLost.Add(c.id);
                        }
                    var arrived = new List<Person>(); int at = 0; bool threw = false; int got = 0;
                    try
                    {
                        got = InhabitedCustody.DrawInto(w.book, w.Candidates(p => p.faction == f), count, p => p.id, w.PoolRemove, w.PoolTryAdd,
                            p =>
                            {
                                int k = at++;
                                if (k == throwAt) throw new InvalidOperationException("destination threw");
                                if (((mask >> k) & 1) != 0) return false;
                                var saveRefuse = w.poolRefuse; w.poolRefuse = false;     // the roster's refusal is independent of the pool's
                                bool ok = dest.m.Count < dest.cap && p.holder == Ground;
                                if (ok) { dest.m.Add(p.id); p.holder = dest.code; }
                                w.poolRefuse = saveRefuse;
                                return ok;
                            }, w.OnLost, arrived);
                    }
                    catch (InvalidOperationException) { threw = true; }
                    Check(threw == expThrow, $"destination exception {(threw ? "swallowed?" : "not propagated")}");
                    if (!threw)
                    {
                        Check(got == arrived.Count && got == expArr.Count, $"draw returned {got}, arrived {arrived.Count}, expected {expArr.Count}");
                        Check(arrived.Select(p => p.id).SequenceEqual(expArr), $"draw order {string.Join(",", arrived.Select(p => p.id))} != longest-waiting-first {string.Join(",", expArr)}");
                    }
                    Check(w.lost.Count == lostBefore + expLost.Count && expLost.All(id => w.lost.Contains(id)), $"draw lost {w.lost.Count - lostBefore}, expected exactly {expLost.Count} ({string.Join(",", expLost)})");
                    break;
                }
                case 3: // draw any
                {
                    int mod = 1 + a.a % 4;
                    int throwAt = a.b % 6 == 0 ? a.c % 3 : -1;
                    w.poolRefuse = a.d % 7 == 0; faulted = w.poolRefuse;
                    var elig = w.Eligible(p => p.humanlike);
                    int attempt = 0; int expId = -1; bool expThrow = false; var expLost = new List<int>();
                    foreach (var c in elig)
                    {
                        bool throws = attempt == throwAt;
                        bool accept = !throws && c.id % mod != 0;
                        attempt++;
                        if (throws) { expThrow = true; if (w.poolRefuse) expLost.Add(c.id); break; }
                        if (accept) { expId = c.id; break; }
                        if (w.poolRefuse) expLost.Add(c.id);
                    }
                    int at = 0; bool threw = false; Person got = null;
                    try
                    {
                        got = InhabitedCustody.DrawAny(w.book, w.Candidates(p => p.humanlike), p => p.id, w.PoolRemove, w.PoolTryAdd,
                            p => { int k = at++; if (k == throwAt) throw new InvalidOperationException("x"); bool ok = p.id % mod != 0; if (ok) { p.holder = Recruited; } return ok; }, w.OnLost);
                    }
                    catch (InvalidOperationException) { threw = true; }
                    Check(threw == expThrow, "beggar destination exception propagation");
                    if (!threw) Check((got == null ? -1 : got.id) == expId, $"draw-any gave {(got == null ? -1 : got.id)}, expected {expId}");
                    Check(w.lost.Count == lostBefore + expLost.Count, $"draw-any lost {w.lost.Count - lostBefore}, expected {expLost.Count}");
                    break;
                }
                case 4: // evacuate a roster
                {
                    var h = a.a % 2 == 0 ? w.ra : w.rb;
                    w.poolRefuse = a.b % 4 == 0; w.rosterRefuse = a.c % 4 == 0;
                    faulted = w.poolRefuse && w.rosterRefuse;
                    var snap = h.m.Select(w.Get).ToList();
                    var living = snap.Where(p => !p.dead).ToList();
                    int moved = InhabitedCustody.MoveRosterToPool(snap, p => p.dead, p => w.RosterRemove(h, p),
                        p => w.Absorb(p, DisplacedReason.Fled, Origins[a.d % Origins.Length]),
                        p => w.RosterTryAdd(h, p), w.OnLost);
                    Check(moved == (w.poolRefuse ? 0 : living.Count), $"evacuate moved {moved} of {living.Count} (poolRefuse {w.poolRefuse})");
                    foreach (var p in snap.Where(x => x.dead)) Check(p.holder == h.code, "a dead roster member was moved");
                    int expLost = w.poolRefuse && w.rosterRefuse ? living.Count : 0;
                    Check(w.lost.Count == lostBefore + expLost, $"evacuate lost {w.lost.Count - lostBefore}, expected {expLost}");
                    break;
                }
                case 5: // recall a person from the map onto a roster
                {
                    var ground = w.ps.Where(p => p.holder == Ground && !p.dead).ToList();
                    if (ground.Count == 0) break;
                    var p = ground[a.a % ground.Count];
                    var h = a.b % 2 == 0 ? w.ra : w.rb;
                    w.rosterRefuse = a.c % 3 == 0; w.poolRefuse = a.d % 3 == 0;
                    bool rosterOk = !w.rosterRefuse;
                    var exp = rosterOk ? InhabitedCustody.RecallOutcome.Roster : (!w.poolRefuse ? InhabitedCustody.RecallOutcome.Placeless : InhabitedCustody.RecallOutcome.LeftToWorld);
                    var o = InhabitedCustody.Recall(p, x => w.RosterTryAdd(h, x), x => w.Absorb(x, DisplacedReason.Fled, null));
                    Check(o == exp, $"recall outcome {o}, expected {exp}");
                    Check(o != InhabitedCustody.RecallOutcome.LeftToWorld || p.holder == Ground, "a person left to the world is held by something");
                    break;
                }
                case 6: // save + load the book
                {
                    var b = new DisplacementBook
                    {
                        reasons = new Dictionary<int, DisplacedReason>(w.book.reasons),
                        origins = new Dictionary<int, string>(w.book.origins),
                        displacedAt = new Dictionary<int, int>(w.book.displacedAt),
                        nextOrder = w.book.nextOrder
                    };
                    w.book = b;
                    break;
                }
                case 7: // someone dies
                {
                    var cand = w.ps.Where(p => p.holder == Ground && !p.dead).ToList();
                    if (cand.Count == 0) break;
                    var p = cand[a.a % cand.Count]; p.dead = true; break;
                }
                case 8: // a roster member walks onto the map
                {
                    var h = a.a % 2 == 0 ? w.ra : w.rb;
                    if (h.m.Count == 0) break;
                    var p = w.Get(h.m[a.b % h.m.Count]);
                    Check(w.RosterRemove(h, p), "could not remove a roster member");
                    break;
                }
            }
            WorldInvariants(w, lostBefore, faulted);
        }

        private static List<Act> GenPool(Random r, int len)
        {
            string[] names = { "Spawn", "Absorb", "Draw", "DrawAny", "Evacuate", "Recall", "Reload", "Die", "Walk" };
            int[] weights = { 3, 6, 6, 3, 3, 3, 2, 1, 2 };
            int total = weights.Sum();
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(total), kind = 0;
                while (k >= weights[kind]) { k -= weights[kind]; kind++; }
                l.Add(new Act { kind = kind, Name = names[kind], a = r.Next(60), b = r.Next(60), c = r.Next(60), d = r.Next(100000) });
            }
            return l;
        }

        private static string RunPool(int seed, List<Act> acts)
        {
            try { var w = MakePool(seed); foreach (var a in acts) { PoolStep(w, a); Steps++; } return null; }
            catch (Exception ex) { return ex.Message; }
        }

        public static List<string> Pool(int n, int baseSeed) { return Family("pool", n, baseSeed, GenPool, RunPool); }

        private static List<string> Family(string name, int n, int baseSeed, Func<Random, int, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 3);
                var acts = gen(r, r.Next(5, 160));
                Cases++;
                if (run(seed, acts) == null) continue;
                var min = Shrink(acts, t => run(seed, t) != null);
                fails.Add($"{name} seed {seed}: {run(seed, min)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // ===================================================================== family: place (cast, visit, fate, recall)

        private sealed class Item
        {
            public int id, count;
            public bool alive = true, isItem = true, corpse, player, inArea;
        }

        private sealed class PlaceW
        {
            public World w = new World();
            public InhabitedFate fate;
            public InhabitedState state = InhabitedState.Inhabited;
            public bool threatened, destroyed, instantiated, visiting;
            public string reason;
            public List<Person> grounded = new List<Person>();     // onTheGround
            public List<int> stock = new List<int>();               // held stacks
            public List<Item> goods = new List<Item>();
            public List<int> ledger = new List<int>();
            public int stockSpawned, nextItem = 1000;
            public bool hostile, grav, colonists = true, fire, areaExists = true;
            public float fraction = 0.5f;
            public int stockInit;           // total units ever put in the holder or taken back, for conservation
            public int removedOnMap;        // units the visitors destroyed or took
            public List<int> history = new List<int>();
        }

        private static readonly InhabitedFate[] Fates = { InhabitedFate.Resident, InhabitedFate.Resident, InhabitedFate.FleeIfThreatened, InhabitedFate.FleeIfThreatened, InhabitedFate.FleeOnArrival, InhabitedFate.Transient };

        private static PlaceW MakePlace(int seed)
        {
            var r = new Random(seed * 17 + 5);
            return new PlaceW { fate = Fates[r.Next(Fates.Length)], fraction = new[] { 0.1f, 0.5f, 0.9f }[r.Next(3)], areaExists = r.Next(5) != 0 };
        }

        private static int Held(PlaceW pl) { return pl.stock.Sum(); }
        private static int OnMapOurs(PlaceW pl)
        {
            return pl.goods.Where(g => OursOracle(pl, g)).Sum(g => g.count);
        }
        private static bool OursOracle(PlaceW pl, Item g)
        {
            if (!g.alive || !g.isItem || g.corpse || g.player) return false;
            return pl.ledger.Contains(g.id) || g.inArea;
        }

        private static string CauseNow(PlaceW pl, int[] calls)
        {
            var w = pl.w;
            return InhabitedFateKernel.Cause(pl.fate, () => { calls[0]++; return pl.grav; }, pl.areaExists, () => { calls[1]++; return pl.fire; },
                pl.hostile, pl.colonists, pl.grounded.Count,
                () =>
                {
                    calls[2]++;
                    var c = new CastCount();
                    foreach (var p in pl.grounded)
                    {
                        if (p.dead || p.holder != Ground) continue;
                        if (p.downed) { c.anyDowned = true; return c; }
                        c.standing++;
                    }
                    return c;
                },
                pl.stockSpawned, () => { calls[3]++; return pl.goods.Where(g => OursOracle(pl, g)).Sum(g => g.count); }, pl.fraction);
        }

        private static void PlaceInvariants(PlaceW pl, InhabitedState before, int lostBefore, bool faulted)
        {
            WorldInvariants(pl.w, lostBefore, faulted);
            // the place never walks back to Inhabited, and a Resident place changes state only because nobody was left
            Check(!(before != InhabitedState.Inhabited && pl.state == InhabitedState.Inhabited), "a place that was " + before + " became Inhabited again");
            Check(pl.state != InhabitedState.Squatted, "Squatted is declared, never written");
            Check(pl.stock.All(x => x > 0), "an empty stack is held");
        }

        private static void PlaceStep(PlaceW pl, Act a)
        {
            var w = pl.w;
            var before = pl.state;
            int lostBefore = w.lost.Count;
            w.poolRefuse = false; w.rosterRefuse = false;
            bool faulted = false;
            switch (a.kind)
            {
                case 0: // someone joins the displaced pool
                {
                    var p = w.Spawn(a.a % 3, a.b % 6 != 0);
                    w.Absorb(p, (DisplacedReason)(a.c % 6), Origins[a.d % Origins.Length]);
                    break;
                }
                case 1: // InstantiateCast + FillStock
                {
                    if (pl.instantiated || pl.destroyed) break;
                    pl.instantiated = true;
                    int nr = 1 + a.a % 5;
                    var kinds = new List<string>(); var rolled = new List<int>();
                    var rr = new Random(a.d);
                    for (int i = 0; i < nr; i++)
                    {
                        bool nullKind = rr.Next(6) == 0;
                        kinds.Add(nullKind ? null : "kind" + i);
                        rolled.Add(nullKind ? 0 : rr.Next(0, 4));
                    }
                    int size = a.b % 9;                                 // 0 means "no trim"
                    var wanted = InhabitedCustody.BuildWanted(kinds, rolled, size);
                    var untrimmed = new List<string>();
                    for (int i = 0; i < kinds.Count; i++) if (kinds[i] != null) for (int j = 0; j < rolled[i]; j++) untrimmed.Add(kinds[i]);
                    Check(wanted.SequenceEqual(size > 0 ? untrimmed.Take(size) : untrimmed), "wanted list is not the authored order trimmed from the back");
                    w.ra.cap = 1 + a.c % 6;
                    int fromPool = 0;
                    if (wanted.Count > 0)
                    {
                        int poolBefore = w.pool.m.Count;
                        int sameFaction = w.Eligible(p => p.faction == 0).Count;
                        fromPool = InhabitedCustody.DrawInto(w.book, w.Candidates(p => p.faction == 0), wanted.Count, p => p.id, w.PoolRemove, w.PoolTryAdd,
                            p => { bool ok = w.ra.m.Count < w.ra.cap && p.holder == Ground; if (ok) { w.ra.m.Add(p.id); p.holder = InRosterA; } return ok; }, w.OnLost, null);
                        Check(fromPool <= Math.Min(sameFaction, wanted.Count), "drew more people than the cast wants or the pool held");
                        Check(w.pool.m.Count == poolBefore - fromPool, "pool size after draw");
                        Check(w.ra.m.Select(w.Get).All(p => p.faction == 0), "a person of another faction was drawn into the cast");
                        int gen = InhabitedCustody.GenerateCount(wanted.Count, fromPool);
                        Check(gen + fromPool == wanted.Count, "generated + drawn != wanted");
                        int next = 0; var applied = new List<int>(); var attemptedKinds = new List<string>();
                        int chars = a.d % 5;
                        for (int i = 0; i < gen; i++)
                        {
                            int up = InhabitedCustody.UpcomingCharacter(next, chars);
                            attemptedKinds.Add(wanted[i]);
                            bool fails = (a.d >> i) % 7 == 0;           // generator returned null
                            if (fails) continue;
                            if (up >= 0) { applied.Add(up); next++; }
                            var p = w.Spawn(0, true);
                            if (w.ra.m.Count >= w.ra.cap || !w.RosterTryAdd(w.ra, p)) { p.holder = Dead; p.dead = true; }     // p.Destroy()
                        }
                        Check(attemptedKinds.SequenceEqual(wanted.Take(gen)), "the pool did not fill the TAIL: generated kinds are not the head of the wanted list");
                        Check(applied.SequenceEqual(Enumerable.Range(0, applied.Count)) && applied.Count <= chars, "authored characters were skipped, repeated or over-used");
                        Check(w.ra.m.Count <= wanted.Count, $"cast of {w.ra.m.Count} exceeds the {wanted.Count} wanted");
                        if (size > 0) Check(w.ra.m.Count <= size, $"cast of {w.ra.m.Count} exceeds castSize {size}");
                    }
                    // FillStock: split at the stack limit
                    int entries = a.c % 4;
                    for (int i = 0; i < entries; i++)
                    {
                        int count = (a.d >> (i * 3)) % 400 - 20, limit = new[] { 1, 75, 100, 0, -3 }[(a.d >> i) % 5];
                        var parts = InhabitedFateKernel.SplitStacks(count, limit);
                        Check(parts.Sum() == Math.Max(0, count), $"split of {count} at {limit} sums to {parts.Sum()}");
                        Check(parts.All(x => x >= 1 && x <= Math.Max(1, limit)), $"split of {count} at {limit} has a stack outside 1..{Math.Max(1, limit)}");
                        Check(parts.Count == (count <= 0 ? 0 : (count + Math.Max(1, limit) - 1) / Math.Max(1, limit)), "split used more stacks than needed");
                        pl.stock.AddRange(parts); pl.stockInit += parts.Sum();
                    }
                    break;
                }
                case 2: // the map generates: cast spawns, stock is dropped
                {
                    if (pl.visiting || pl.destroyed || !pl.instantiated) break;
                    pl.visiting = true;
                    if (w.ra.m.Count == 0) { if (pl.state == InhabitedState.Inhabited) pl.state = InhabitedState.Abandoned; }
                    else
                    {
                        pl.grounded.Clear();
                        foreach (int id in w.ra.m.ToList())
                        {
                            var p = w.Get(id);
                            if (p.dead) continue;
                            w.RosterRemove(w.ra, p); pl.grounded.Add(p);
                        }
                    }
                    pl.ledger.Clear(); pl.stockSpawned = 0;
                    var rr = new Random(a.d);
                    int placed = 0;
                    foreach (int n in pl.stock.ToList())
                    {
                        if (rr.Next(8) == 0) continue;                 // TryDrop failed: stays in the holder
                        pl.stock.Remove(n);
                        Item landed;
                        var merge = pl.goods.FirstOrDefault(g => g.alive && !g.corpse && !g.player && rr.Next(4) == 0);
                        if (merge != null) { merge.count += n; landed = merge; } else { landed = new Item { id = pl.nextItem++, count = n, inArea = true }; pl.goods.Add(landed); }
                        placed += n;
                        if (!pl.ledger.Contains(landed.id)) pl.ledger.Add(landed.id);
                    }
                    pl.stockSpawned = placed;
                    break;
                }
                case 3: // visitors do things to the map
                {
                    if (!pl.visiting) break;
                    var rr = new Random(a.d);
                    switch (a.a % 11)
                    {
                        case 0: { var l = pl.grounded.Where(p => !p.dead && p.holder == Ground).ToList(); if (l.Count > 0) { var p = l[rr.Next(l.Count)]; p.dead = true; pl.goods.Add(new Item { id = pl.nextItem++, count = 1, corpse = true, inArea = true }); } break; }
                        case 1: { var l = pl.grounded.Where(p => !p.dead && p.holder == Ground).ToList(); if (l.Count > 0) l[rr.Next(l.Count)].downed = true; break; }
                        case 2: { var l = pl.grounded.Where(p => !p.dead && p.holder == Ground).ToList(); if (l.Count > 0) { var p = l[rr.Next(l.Count)]; p.holder = Recruited; } break; }
                        case 3: { var l = pl.goods.Where(g => g.alive).ToList(); if (l.Count > 0) { var g = l[rr.Next(l.Count)]; int take = Math.Min(g.count, 1 + rr.Next(g.count)); g.count -= take; pl.removedOnMap += take; if (g.count == 0) g.alive = false; } break; }
                        case 4: pl.hostile = !pl.hostile; break;
                        case 5: pl.grav = !pl.grav; break;
                        case 6: pl.fire = !pl.fire; break;
                        case 7: pl.colonists = !pl.colonists; break;
                        case 8: pl.goods.Add(new Item { id = pl.nextItem++, count = 1 + rr.Next(9), player = true, inArea = rr.Next(2) == 0 }); break;         // the colony's own
                        case 9: { var l = pl.goods.Where(g => g.alive && !g.corpse && !g.player && g.count > 1).ToList(); if (l.Count > 0) { var g = l[rr.Next(l.Count)]; int cut = 1 + rr.Next(g.count - 1); g.count -= cut; pl.goods.Add(new Item { id = pl.nextItem++, count = cut, inArea = rr.Next(3) != 0 }); } break; }   // split stack: new id, not in the ledger
                        case 10: { var l = pl.goods.Where(g => g.alive && !g.corpse && !g.player).ToList(); if (l.Count > 0) l[rr.Next(l.Count)].inArea = false; break; }  // hauled out of the stock area
                    }
                    break;
                }
                case 4: // the watch component ticks
                {
                    if (!pl.visiting || pl.threatened) break;
                    var calls = new int[4];
                    string cause = CauseNow(pl, calls);
                    if (cause != null) { pl.threatened = true; pl.reason = cause; }
                    if (pl.fate == InhabitedFate.Resident) Check(cause == null && calls.All(c => c == 0), "a Resident place fired or scanned");
                    if (pl.fate == InhabitedFate.Transient) Check(cause == InhabitedFateKernel.CauseTransient && calls.All(c => c == 0), "a Transient place did not fire at once");
                    break;
                }
                case 5: // the player leaves: recall, collect, state, fate
                {
                    if (!pl.visiting) break;
                    pl.visiting = false;
                    w.rosterRefuse = a.b % 5 == 0; w.poolRefuse = a.c % 5 == 0;
                    faulted = w.poolRefuse && w.rosterRefuse;
                    if (w.rosterRefuse) w.ra.cap = int.MaxValue;
                    var ours = pl.grounded.Where(p => !p.dead && p.holder != Recruited).ToList();
                    int recalled = 0, placeless = 0, world = 0;
                    foreach (var p in ours)
                    {
                        switch (InhabitedCustody.Recall(p, x => w.RosterTryAdd(w.ra, x), x => w.Absorb(x, DisplacedReason.Fled, "x")))
                        {
                            case InhabitedCustody.RecallOutcome.Roster: recalled++; break;
                            case InhabitedCustody.RecallOutcome.Placeless: placeless++; break;
                            default: world++; break;
                        }
                    }
                    if (!w.rosterRefuse && !w.poolRefuse) Check(recalled == ours.Count, "a resident was not recalled to a healthy roster");
                    pl.grounded.Clear();
                    // collect the goods
                    int expect = OnMapOurs(pl), taken = 0;
                    foreach (var g in pl.goods.ToList())
                    {
                        bool ours2 = InhabitedFateKernel.IsPlaceGoods(g.alive, g.isItem, g.corpse, g.player, pl.ledger.Contains(g.id), pl.areaExists && g.inArea);
                        Check(ours2 == (OursOracle(pl, g) && (pl.areaExists || pl.ledger.Contains(g.id))), $"IsPlaceGoods disagrees for item {g.id}");
                        if (!ours2) continue;
                        pl.stock.Add(g.count); taken += g.count; g.alive = false;
                    }
                    if (pl.areaExists) Check(taken == expect, $"collected {taken} units, the map held {expect} of ours");
                    pl.ledger.Clear(); pl.stockSpawned = 0;
                    pl.goods.RemoveAll(g => !g.alive);
                    pl.state = InhabitedFateKernel.StateAfterRecall(pl.state, w.ra.m.Count(i => !w.Get(i).dead));
                    // Apply
                    if (InhabitedFateKernel.ShouldApply(pl.fate, pl.threatened))
                    {
                        Check(pl.fate != InhabitedFate.Resident, "fate applied to a Resident place");
                        if (pl.fate == InhabitedFate.Transient)
                        {
                            var snap = w.ra.m.Select(w.Get).ToList();
                            int moved = InhabitedCustody.MoveRosterToPool(snap, p => p.dead, p => w.RosterRemove(w.ra, p), p => w.Absorb(p, DisplacedReason.Fled, "t"), p => w.RosterTryAdd(w.ra, p), w.OnLost);
                            pl.destroyed = true;
                            Check(w.ra.m.All(i => w.Get(i).dead) || w.poolRefuse, "a destroyed Transient place kept living people although the pool accepts");
                        }
                        else
                        {
                            var snap = w.ra.m.Select(w.Get).ToList();
                            int livingBefore = snap.Count(p => !p.dead);
                            int fled = InhabitedCustody.MoveRosterToPool(snap, p => p.dead, p => w.RosterRemove(w.ra, p), p => w.Absorb(p, DisplacedReason.Fled, "t"), p => w.RosterTryAdd(w.ra, p), w.OnLost);
                            Check(fled == (w.poolRefuse ? 0 : livingBefore), $"fate moved {fled} of {livingBefore}");
                            pl.state = InhabitedFateKernel.StateAfterFate(pl.stock.Count);
                            Check(pl.state == InhabitedState.Looted ? pl.stock.Count == 0 : pl.stock.Count > 0, "Looted/Abandoned disagrees with the larder");
                            if (!w.poolRefuse) Check(w.ra.m.All(i => w.Get(i).dead), "the cast did not leave a place whose fate fired");
                        }
                    }
                    else if (pl.threatened == false) Check(pl.state != InhabitedState.Looted, "a place was Looted without a fate firing");
                    break;
                }
            }
            PlaceInvariants(pl, before, lostBefore, faulted);
        }

        private static List<Act> GenPlace(Random r, int len)
        {
            string[] names = { "JoinPool", "Instantiate", "Visit", "Visitors", "Watch", "Leave" };
            int[] weights = { 3, 2, 3, 8, 4, 3 };
            int total = weights.Sum();
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(total), kind = 0;
                while (k >= weights[kind]) { k -= weights[kind]; kind++; }
                l.Add(new Act { kind = kind, Name = names[kind], a = r.Next(60), b = r.Next(60), c = r.Next(60), d = r.Next(1000000) });
            }
            return l;
        }

        private static string RunPlace(int seed, List<Act> acts)
        {
            try { var pl = MakePlace(seed); foreach (var a in acts) { PlaceStep(pl, a); Steps++; } return null; }
            catch (Exception ex) { return ex.Message; }
        }

        public static List<string> Place(int n, int baseSeed) { return Family("place", n, baseSeed, GenPlace, RunPlace); }

        // ===================================================================== family: cause (random argument vectors, laziness)

        public static List<string> Cause(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 131 + 9);
                Cases++; Steps++;
                var fate = (InhabitedFate)r.Next(4);
                bool grav = r.Next(2) == 0, area = r.Next(3) != 0, fire = r.Next(4) == 0, hostile = r.Next(4) == 0, colonists = r.Next(3) != 0, downed = r.Next(5) == 0;
                int grounded = r.Next(0, 7), standing = r.Next(0, 8), spawned = r.Next(0, 5) == 0 ? 0 : r.Next(1, 300), left = r.Next(0, 320);
                float fr = new[] { 0.1f, 0.25f, 0.5f, 0.9f }[r.Next(4)];
                if (r.Next(3) == 0) left = (int)(spawned * fr);          // the boundary: exactly at the threshold is NOT robbed
                if (r.Next(6) == 0) left = (int)(spawned * fr) - 1;      // and just under it is
                var calls = new int[4];
                string got = InhabitedFateKernel.Cause(fate, () => { calls[0]++; return grav; }, area, () => { calls[1]++; return fire; }, hostile, colonists, grounded,
                    () => { calls[2]++; return new CastCount { standing = standing, anyDowned = downed }; }, spawned, () => { calls[3]++; return left; }, fr);
                string exp = null; var expCalls = new int[4];
                switch (fate)
                {
                    case InhabitedFate.Resident: break;
                    case InhabitedFate.Transient: exp = "InhabitedFateTransient"; break;
                    case InhabitedFate.FleeOnArrival: expCalls[0] = 1; if (grav) exp = "InhabitedFateGravship"; break;
                    case InhabitedFate.FleeIfThreatened:
                        if (area) { expCalls[1] = 1; if (fire) { exp = "InhabitedFateBurned"; break; } }
                        if (hostile) { exp = "InhabitedFateHostile"; break; }
                        if (colonists && grounded > 0) { expCalls[2] = 1; if (downed || standing < grounded) { exp = "InhabitedFateHarmed"; break; } }
                        if (spawned > 0) { expCalls[3] = 1; if (left < spawned * fr) exp = "InhabitedFateRobbed"; }
                        break;
                }
                string err = null;
                if (got != exp) err = $"fate {fate}: cause {got ?? "null"}, expected {exp ?? "null"}";
                else if (!calls.SequenceEqual(expCalls)) err = $"fate {fate}: scans ran {string.Join("", calls)}, expected {string.Join("", expCalls)} (a scan ran that an earlier cause made unnecessary, or was skipped)";
                if (err != null) { fails.Add($"cause seed {seed}: {err}"); if (fails.Count >= 5) break; }
            }
            return fails;
        }

        // ===================================================================== family: units

        public static List<string> Units(int n, int baseSeed)
        {
            var fails = new List<string>();
            void Fail(string m) { fails.Add("units: " + m); }
            Cases++;
            // sleeping hours: 24 hours, wrap, equal means never
            for (int s = 0; s < 24; s++)
                for (int wk = 0; wk < 24; wk++)
                {
                    int sleeping = 0;
                    for (int h = 0; h < 24; h++)
                    {
                        bool x = InhabitedFateKernel.IsSleepingHour(h, s, wk);
                        if (x) sleeping++;
                        bool expect = s == wk ? false : (((h - s + 24) % 24) < ((wk - s + 24) % 24));
                        if (x != expect) Fail($"IsSleepingHour({h},{s},{wk}) = {x}");
                    }
                    int expN = s == wk ? 0 : ((wk - s + 24) % 24);
                    if (sleeping != expN) Fail($"sleep {s}..{wk} covers {sleeping} hours, expected {expN}");
                    Steps++;
                }
            // stance
            if (InhabitedFateKernel.Stance(true, 5000, 4000, true) != RouteStance.Defending) Fail("recent harm does not defend");
            if (InhabitedFateKernel.Stance(true, 5200, 4000, true) != RouteStance.AtRest) Fail("old harm still defends");
            if (InhabitedFateKernel.Stance(false, 5000, 4999, false) != RouteStance.AtWork) Fail("no lord defends");
            // states
            if (InhabitedFateKernel.StateAfterRecall(InhabitedState.Looted, 0) != InhabitedState.Looted) Fail("recall overwrote Looted");
            if (InhabitedFateKernel.StateAfterRecall(InhabitedState.Inhabited, 1) != InhabitedState.Inhabited) Fail("recall abandoned a place with people");
            // legacy save: dictionaries missing
            var b = new DisplacementBook { reasons = null, origins = null, displacedAt = null };
            b.EnsureNotNull();
            if (b.ReasonFor(5) != DisplacedReason.Fled || b.OriginFor(5) != null || b.OrderKey(5) != int.MaxValue) Fail("a person without metadata is not Fled/unknown/last");
            // equal-key ordering stays stable
            var order = InhabitedCustody.Order(b, new[] { 9, 3, 7, 1 }, x => x);
            if (!order.SequenceEqual(new[] { 9, 3, 7, 1 })) Fail("unordered people were reshuffled");
            // wanted
            var kinds = new List<string> { "leader", null, "trader", "guard" };
            var w = InhabitedCustody.BuildWanted(kinds, new List<int> { 1, 5, 1, 4 }, 3);
            if (!w.SequenceEqual(new[] { "leader", "trader", "guard" })) Fail("trim from the back kept " + string.Join(",", w));
            if (InhabitedCustody.GenerateCount(2, 5) != 0) Fail("negative generation count");
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("pool", () => Pool(N(4000), S(1))),
                ("place", () => Place(N(4000), S(1))),
                ("cause", () => Cause(N(20000), S(1))),
                ("units", () => Units(1, 1)),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine($"inhabited fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
