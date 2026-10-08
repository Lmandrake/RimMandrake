// Approach B for RimProperty: seeded fuzz over the Verse-free kernel the mod calls (../../Kernel/RM_PropertyKernel.cs):
//   ledger     a world of pawns, things, factions and silver: events fired through the production spine / authorization / claim
//              ordering / decay, menus built and clicked (money conservation, pay-at-click), loot, gifts, possession, the foreign-claim
//              wipe, against an independent brute-force spec of "who owns this, how strongly"
//   suspicion  a faction's witness record: entries registered, time passing, bribes, prune invariance, bounds
//   tables     fees, prices, recognizability, silver-stack removal conservation, the pocket pick, animal-theft gates
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Property.Fuzz
{
    internal static class PropertyFuzz
    {
        public static long Cases, Steps, Buys, Claims, Bribes, Refused, Thefts, StolenRecords, Flips, Wipes, Witnessed, Ghosts, Ties;
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

        private struct Act
        {
            public int kind, a, b, c; public bool f;
            public override string ToString() { return "k" + kind + "(" + a + "," + b + "," + c + (f ? ",T" : "") + ")"; }
        }

        private static List<string> RunFamily(string name, int n, int seed0, Func<Random, int, Act[]> gen, Func<IList<Act>, int, bool, string> run, int minLen, int spread)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = gen(r, minLen + r.Next(spread)); Cases++;
                if (run(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => run(t, seed, false) != null);
                fails.Add($"{name} seed {seed}: {run(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        private static Act[] Gen(Random r, int len, int[] weights)
        {
            var a = new Act[len]; int total = weights.Sum();
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(total), kind = 0;
                while (k >= weights[kind]) { k -= weights[kind]; kind++; }
                a[i] = new Act { kind = kind, a = r.Next(1 << 12), b = r.Next(1 << 12), c = r.Next(1 << 12), f = r.Next(2) == 0 };
            }
            return a;
        }

        // ════════════════════════ the world ════════════════════════
        private const int Pawns = 6, Things = 5, Factions = 3, TicksPerDay = 60000;

        private struct C
        {
            public byte kind; public int id;
            public bool Same(C o) { return kind == o.kind && (kind == RM_PropertyKernel.KindNone || id == o.id); }
            public override string ToString() { return kind == 1 ? "P" + id : kind == 2 ? "F" + id : "-"; }
        }
        private static C PawnC(int p) { return new C { kind = RM_PropertyKernel.KindPawn, id = p }; }
        private static C CommonsC(int f) { return new C { kind = RM_PropertyKernel.KindCommons, id = f }; }

        private sealed class Rec { public C who; public float initial; public int basis; public int ts; }
        private sealed class Cand { public C who; public float strength; public int spec; public int ts; public bool recorded; public int basis; }
        private sealed class Th { public int stackLimit, stack, quality; public float mv; public bool named, mech; public int possessor = -1, ownerFaction = -1; public List<Rec> recs = new List<Rec>(); }
        private sealed class Entry { public int suspect; public float conf; public int ts; }
        private sealed class Menu { public int kind, actor, target, fee; }

        private sealed class World
        {
            public int now = 100000;
            public int[] pawnFaction = new int[Pawns];
            public bool[] ghost = new bool[Pawns];
            public List<int>[] silver = new List<int>[Pawns];
            public Th[] things = new Th[Things];
            public List<Entry>[] entries = new List<Entry>[Factions];
            public long sink, minted, initial;
            public bool perception = true; public float lifetimeMult = 1f, halfLife = 45f, feeMult = 1f, markup = 1.15f, dampen = 0.35f, witnessConf = 0.75f;
            public float bribeFee = 15f;
            public Menu menu;
            public int writes;   // ledger writes, for the failure-leaves-nothing check
            public List<string> log = new List<string>();

            public World(Random r)
            {
                for (int p = 0; p < Pawns; p++)
                {
                    pawnFaction[p] = r.Next(4) - 1;      // -1 none
                    silver[p] = new List<int>();
                    for (int s = r.Next(3); s > 0; s--) { int amt = 1 + r.Next(300); silver[p].Add(amt); initial += amt; }
                }
                for (int t = 0; t < Things; t++)
                    things[t] = new Th { stackLimit = new[] { 1, 75, 1, 500 }[r.Next(4)], stack = 1 + r.Next(5), quality = r.Next(8) - 1, mv = new[] { 0f, 3f, 40f, 400f, 2500f }[r.Next(5)], named = r.Next(5) == 0, mech = r.Next(8) == 0,
                        ownerFaction = r.Next(4) - 1, possessor = r.Next(3) == 0 ? r.Next(Pawns) : -1 };
                for (int f = 0; f < Factions; f++) entries[f] = new List<Entry>();
            }

            public long Carried(int p) { return silver[p].Sum(); }
            public float Recog(Th t) { return RM_PropertyKernel.Recognizability(true, t.quality >= 0, Math.Max(0, t.quality), t.mv, t.named, t.mech, true, t.stackLimit); }
            public float Lifetime(Th t) { return RM_PropertyKernel.LifetimeTicks(Recog(t), 3f, 3650f, lifetimeMult, TicksPerDay); }
            public float Eff(Th t, Rec r)
            {
                int age = now - r.ts;
                if (age <= 0) return r.initial;
                return RM_PropertyKernel.EffectiveStrength(r.initial, age, Lifetime(t));
            }

            public bool Ghost(C c) { return RM_PropertyKernel.IsGhost(c.kind, c.kind == 1 && ghost[c.id], false); }

            public List<Cand> Candidates(Th t)
            {
                var cs = new List<Cand>();
                foreach (Rec r in t.recs)
                {
                    if (Ghost(r.who)) continue;
                    float s = Eff(t, r);
                    if (s <= 0f) continue;
                    cs.Add(new Cand { who = r.who, strength = s, spec = RM_PropertyKernel.Specificity(r.who.kind), ts = r.ts, recorded = true, basis = r.basis });
                }
                int vb = RM_PropertyKernel.VirtualBasis(t.possessor >= 0, t.ownerFaction >= 0);
                if (vb == RM_PropertyKernel.VirtualSituational) cs.Add(new Cand { who = PawnC(t.possessor), strength = 0.9f, spec = 2, ts = now, basis = 1 });
                else if (vb == RM_PropertyKernel.VirtualTerritorial) cs.Add(new Cand { who = CommonsC(t.ownerFaction), strength = 0.5f, spec = 1, ts = now, basis = 0 });
                return cs;
            }

            public Cand Resolve(Th t)
            {
                var cs = Candidates(t);
                if (cs.Count == 0) return null;
                cs.Sort((a, b) => RM_PropertyKernel.Order(a.strength, a.spec, a.ts, b.strength, b.spec, b.ts));
                return cs[0];
            }

            public bool MayUse(C claimant, C actor)
            {
                bool sameFaction = actor.kind == 1 && pawnFaction[actor.id] == (claimant.kind == 2 ? claimant.id : -2);
                return RM_PropertyKernel.ClaimantMayUse(claimant.Same(actor), claimant.kind, actor.kind, sameFaction);
            }

            public bool Authorized(C actor, Cand prior)
            {
                if (prior == null) return RM_PropertyKernel.IsAuthorized(false, false);
                return RM_PropertyKernel.IsAuthorized(true, MayUse(prior.who, actor));
            }

            public void Record(Th t, C who, int basis, float strength)
            {
                t.recs.Add(new Rec { who = who, initial = strength, basis = basis, ts = now }); writes++;
            }

            public void Prune(int faction)
            {
                var es = entries[faction];
                for (int i = es.Count - 1; i >= 0; i--)
                    if (RM_PropertyKernel.FullyDecayed(RM_PropertyKernel.DaysElapsed(now, es[i].ts, TicksPerDay), halfLife)) es.RemoveAt(i);
            }

            public void Register(int faction, C suspect, float conf)
            {
                if (suspect.kind != RM_PropertyKernel.KindPawn) return;
                Prune(faction);
                entries[faction].Add(new Entry { suspect = suspect.id, conf = conf, ts = now });
            }

            public float Suspicion(int faction, int suspect, bool prune = true)
            {
                if (prune) Prune(faction);
                float total = 0f;
                foreach (Entry e in entries[faction])
                {
                    if (e.suspect != suspect) continue;
                    float days = RM_PropertyKernel.DaysElapsed(now, e.ts, TicksPerDay);
                    total += RM_PropertyKernel.Contribution(e.conf, days, 1f / 3f, halfLife);
                }
                return RM_PropertyKernel.Clamp01(total);
            }

            public void Dampen(int faction, int suspect, float fraction)
            {
                Prune(faction);
                foreach (Entry e in entries[faction])
                    if (e.suspect == suspect) e.conf = RM_PropertyKernel.Dampened(e.conf, fraction);
            }

            // PropertyEngine.Fire, shaped like the mod: resolve, authorize, write, perceive
            public Cand Fire(int thing, C actor, int act, int witnessMask)
            {
                Th t = things[thing];
                Cand prior = Resolve(t);
                bool authorized = Authorized(actor, prior);
                switch (RM_PropertyKernel.SpineWrite(act, authorized, prior != null))
                {
                    case RM_PropertyKernel.WritePurchased: Record(t, actor, 3, 1f); break;
                    case RM_PropertyKernel.WriteClaimFeePaid: Record(t, actor, 4, 1f); break;
                    case RM_PropertyKernel.WriteStolenFromPrior: Record(t, prior.who, 2, 1f); StolenRecords++; break;
                }
                bool after = RM_PropertyKernel.AuthorizedAfter(act, authorized);
                if (RM_PropertyKernel.RollsPerception(after, perception))
                {
                    for (int w = 0; w < Pawns; w++)
                    {
                        if ((witnessMask >> w & 1) == 0 || (actor.kind == 1 && actor.id == w)) continue;
                        Witnessed++;
                        if (pawnFaction[w] >= 0) Register(pawnFaction[w], actor, witnessConf);
                    }
                }
                return prior;
            }

            // RemoveSilverFromInventory: stack by stack, destroying what is taken
            public void RemoveSilver(int p, int amount)
            {
                if (amount <= 0) return;
                int remaining = amount;
                for (int i = 0; i < silver[p].Count && remaining > 0;)
                {
                    int take = RM_PropertyKernel.TakeFromStack(remaining, silver[p][i]);
                    silver[p][i] -= take; remaining -= take; sink += take;
                    if (silver[p][i] == 0) silver[p].RemoveAt(i); else i++;
                }
            }
        }

        private enum LA { Advance, OpenMenu, Click, Drop, Gain, Take, Use, Loot, Gift, Possess, Owner, Wipe, Settings, Ghost, Query }

        private static string RunLedger(IList<Act> acts, int seed, bool count)
        {
            var r = new Random(seed ^ 0x3c6ef372);
            var w = new World(r); int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    int p = a.a % Pawns, ti = a.b % Things, other = a.c % Pawns; Th t = w.things[ti]; C actor = PawnC(p);
                    long totalBefore = w.sink + w.silver.Sum(s => s.Sum());
                    // a pawn whose reference went null after a load (dead, discarded) acts no more
                    LA kindNow = (LA)a.kind;
                    if (w.ghost[p] && (kindNow == LA.OpenMenu || kindNow == LA.Take || kindNow == LA.Use || kindNow == LA.Loot || kindNow == LA.Gift || kindNow == LA.Gain || kindNow == LA.Drop || kindNow == LA.Possess)) continue;
                    if (kindNow == LA.Click && w.menu != null && w.ghost[w.menu.actor]) { w.menu = null; continue; }
                    switch ((LA)a.kind)
                    {
                        case LA.Advance: w.now += 1 + a.a * 40 + (a.f ? a.b * 600 : 0); break;
                        case LA.Gain: { int amt = 1 + a.b % 200; w.silver[p].Add(amt); w.minted += amt; break; }
                        case LA.Drop:
                            if (w.silver[p].Count > 0) { int i = a.b % w.silver[p].Count; w.minted -= w.silver[p][i]; w.silver[p].RemoveAt(i); }
                            break;
                        case LA.Possess: t.possessor = a.f ? p : -1; break;
                        case LA.Owner: t.ownerFaction = a.c % 4 - 1; break;
                        case LA.Settings:
                            w.perception = (a.a & 1) == 0; w.lifetimeMult = new[] { 0.25f, 1f, 4f }[a.b % 3]; w.halfLife = new[] { 5f, 45f, 180f }[a.c % 3];
                            w.feeMult = new[] { 0.25f, 1f, 3f }[(a.a >> 1) % 3]; w.markup = new[] { 0.5f, 1.15f, 3f }[(a.b >> 1) % 3]; w.dampen = new[] { 0f, 0.35f, 1f }[(a.c >> 1) % 3];
                            w.bribeFee = new[] { 0f, 15f, 100f }[(a.a >> 3) % 3];
                            break;
                        case LA.Ghost: w.ghost[p] = true; Ghosts++; break;
                        case LA.Use:
                            {
                                int wb = w.writes;
                                w.Fire(ti, actor, a.f ? RM_PropertyKernel.ActUse : RM_PropertyKernel.ActSabotage, a.c);
                                Check(w.writes == wb, "using or sabotaging someone's property wrote a claim");
                                break;
                            }
                        case LA.Take:
                            {
                                int act = a.f ? RM_PropertyKernel.ActTake : RM_PropertyKernel.ActStrip;
                                Cand prior = w.Resolve(t);
                                int recsBefore = t.recs.Count;
                                w.Fire(ti, actor, act, a.c);
                                bool authorized = prior == null || w.MayUse(prior.who, actor);
                                Thefts++;
                                if (authorized) Check(t.recs.Count == recsBefore, "an authorized take wrote a claim");
                                else
                                {
                                    Check(t.recs.Count == recsBefore + 1, "an unauthorized take with a prior owner wrote " + (t.recs.Count - recsBefore) + " claims");
                                    Rec stolen = t.recs[t.recs.Count - 1];
                                    Check(stolen.basis == 2 && stolen.who.Same(prior.who) && stolen.initial == 1f && stolen.ts == w.now, "the stolen record is not the prior owner's at full strength");
                                    Check(!t.recs.Skip(recsBefore).Any(x => x.who.Same(actor) && !prior.who.Same(actor)), "the thief gained a record by stealing");
                                    // the victim's claim is stronger than anything the thief virtually holds at that instant
                                    Cand now = w.Resolve(t);
                                    Check(now != null && now.strength >= 0.9f - 1e-6f, "the stolen claim does not at least match a possessor's");
                                }
                                break;
                            }
                        case LA.Loot:
                            {
                                C looter = actor; C original = a.f ? PawnC(other) : (a.c % 3 == 0 ? new C { kind = 0 } : CommonsC(a.c % Factions));
                                int before = t.recs.Count;
                                if (RM_PropertyKernel.LootKeepsOrigin(original.kind == 0)) w.Record(t, original, 8, 1f);
                                w.Record(t, looter, 7, 1f);
                                Check(t.recs.Count == before + (original.kind == 0 ? 1 : 2), "loot wrote the wrong number of records");
                                break;
                            }
                        case LA.Gift: w.Record(t, a.f ? actor : CommonsC(a.c % Factions), a.f ? 5 : 6, 1f); break;
                        case LA.OpenMenu:
                            {
                                int kind = a.c % 3;       // 0 buy, 1 salvage claim, 2 bribe
                                Cand prior = w.Resolve(t);
                                int fee = 0;
                                if (kind == 0)
                                {
                                    if (prior == null || w.MayUse(prior.who, actor) || t.mv <= 0f) break;
                                    fee = RM_PropertyKernel.Price(t.mv, t.stack, w.markup);
                                }
                                else if (kind == 1)
                                {
                                    if ((prior != null && w.MayUse(prior.who, actor)) || t.mv <= 0f) break;
                                    fee = RM_PropertyKernel.SalvageFee(w.Recog(t), prior != null, prior != null ? prior.strength : 0f, w.feeMult, 5, 350, 0.2f);
                                }
                                else
                                {
                                    if (other == p || w.pawnFaction[other] < 0 || w.pawnFaction[other] == w.pawnFaction[p]) break;
                                    fee = RM_PropertyKernel.ConfiguredFee(w.bribeFee);
                                }
                                Check(fee >= 1, "a fee below one silver");
                                if (!RM_PropertyKernel.CanPay((int)w.Carried(p), fee)) break;   // "not enough silver" option, nothing to click
                                w.menu = new Menu { kind = kind, actor = p, target = kind == 2 ? other : ti, fee = fee };
                                break;
                            }
                        case LA.Click:
                            {
                                Menu m = w.menu; w.menu = null;
                                if (m == null) break;
                                C who = PawnC(m.actor); long carried = w.Carried(m.actor);
                                int writesBefore = w.writes; long sinkBefore = w.sink;
                                if (!RM_PropertyKernel.CanPay((int)carried, m.fee))
                                {
                                    // the pawn dropped silver after the menu was built: nothing is taken and nothing is granted
                                    Refused++;
                                    Check(w.writes == writesBefore && w.sink == sinkBefore && w.Carried(m.actor) == carried, "a refused payment changed the world");
                                    break;
                                }
                                w.RemoveSilver(m.actor, m.fee);
                                Check(w.Carried(m.actor) == carried - m.fee, $"paid {carried - w.Carried(m.actor)} for a fee of {m.fee}");
                                Check(w.sink - sinkBefore == m.fee, "the silver taken is not the fee");
                                if (m.kind == 0)
                                {
                                    Buys++;
                                    w.Fire(m.target, who, RM_PropertyKernel.ActBuy, 0);
                                    Check(w.writes == writesBefore + 1 && w.things[m.target].recs[w.things[m.target].recs.Count - 1].basis == 3, "a purchase did not record exactly a Purchased claim");
                                    Cand win = w.Resolve(w.things[m.target]);
                                    Check(win != null && win.strength >= 1f - 1e-6f, "after buying the winning claim is not at full strength");
                                    if (!win.who.Same(who))
                                    {   // only a claim as strong, as specific and as recent as the purchase can share the top: another Pawn claim written this very tick
                                        Ties++;
                                        Check(win.strength >= 1f - 1e-6f && win.spec >= 2 && win.ts == w.now, "a purchase lost to a claim that is weaker, less specific or older");
                                    }
                                }
                                else if (m.kind == 1)
                                {
                                    Claims++;
                                    w.Fire(m.target, who, RM_PropertyKernel.ActClaim, 0);
                                    Check(w.writes == writesBefore + 1 && w.things[m.target].recs[w.things[m.target].recs.Count - 1].basis == 4, "a paid claim did not record exactly a ClaimFeePaid claim");
                                }
                                else
                                {
                                    Bribes++;
                                    int f = w.pawnFaction[m.target];
                                    float before = w.Suspicion(f, m.actor);
                                    w.Dampen(f, m.actor, w.dampen);
                                    float afterS = w.Suspicion(f, m.actor);
                                    Check(afterS <= before + 1e-6f, "a bought round increased suspicion");
                                    Check(w.writes == writesBefore, "a bribe wrote a claim");
                                }
                                break;
                            }
                        case LA.Wipe:
                            {
                                C keep = a.f ? CommonsC(a.c % Factions) : PawnC(other);
                                Wipes++;
                                foreach (Th th in w.things)
                                {
                                    var before = th.recs.ToList();
                                    // the spec, stated apart from the kernel: the exact claimant stays, and so does any known pawn of the kept faction's Commons
                                    var expect = before.Where(rec => rec.who.Same(keep) || (keep.kind == 2 && rec.who.kind == 1 && !w.ghost[rec.who.id] && w.pawnFaction[rec.who.id] == keep.id)).ToList();
                                    for (int i = th.recs.Count - 1; i >= 0; i--) if (!WipeKept(w, th.recs[i].who, keep)) th.recs.RemoveAt(i);
                                    Check(th.recs.SequenceEqual(expect), "the wipe changed the order or the kept set");
                                    Check(th.recs.All(rec => rec.who.Same(keep) || (keep.kind == 2 && rec.who.kind == 1 && w.pawnFaction[rec.who.id] == keep.id)), "a foreign claim survived the wipe");
                                }
                                break;
                            }
                        case LA.Query: break;
                    }
                    // standing properties
                    long totalAfter = w.sink + w.silver.Sum(s => s.Sum());
                    Check(w.silver.All(s => s.All(x => x > 0)), "an empty or negative silver stack");
                    Check(w.silver.Sum(s => s.Sum()) + w.sink == w.initial + w.minted, $"silver not conserved: {w.silver.Sum(s => s.Sum())} + sink {w.sink} vs {w.initial + w.minted}");
                    foreach (Th th in w.things)
                    {
                        Check(th.recs.All(x => x.basis >= 2 && x.basis <= 8), "a virtual basis was stored in the ledger");
                        Check(th.recs.All(x => x.initial == 1f), "a stored claim not at full initial strength");
                        SpecCompare(w, th);
                    }
                    for (int f = 0; f < Factions; f++)
                        for (int s = 0; s < Pawns; s++)
                        {
                            float sus = w.Suspicion(f, s);
                            Check(sus >= 0f && sus <= 1f, "suspicion outside 0..1: " + sus);
                        }
                }
                return null;
            }
            catch (Exception e) { return "step " + stepNo + ": " + e.Message; }
        }

        private static bool WipeKept(World w, C claimant, C keep)
        {
            bool keepCommons = keep.kind == 2;
            bool known = claimant.kind == 1 && !w.ghost[claimant.id];
            bool sameFaction = known && keepCommons && w.pawnFaction[claimant.id] == keep.id;
            return RM_PropertyKernel.IsKept(claimant.Same(keep), keepCommons, claimant.kind, known, sameFaction);
        }

        // brute force: the strongest live claim, ties by claimant kind then recency; the production sort must land on one of the winners
        private static void SpecCompare(World w, Th t)
        {
            var cs = new List<(C who, double s, int spec, int ts)>();
            double life = (3.0 + (3650.0 - 3.0) * Math.Min(1.0, Math.Max(0.0, w.Recog(t)))) * w.lifetimeMult * TicksPerDay;
            foreach (Rec r in t.recs)
            {
                if (r.who.kind == 1 && w.ghost[r.who.id]) continue;
                int age = w.now - r.ts;
                double s = age <= 0 ? r.initial : age >= life ? 0 : r.initial * (1 - age / life);
                if (s > 1e-5) cs.Add((r.who, s, r.who.kind == 1 ? 2 : r.who.kind == 2 ? 1 : 0, r.ts));
            }
            if (t.possessor >= 0) cs.Add((PawnC(t.possessor), 0.9, 2, w.now));
            else if (t.ownerFaction >= 0) cs.Add((CommonsC(t.ownerFaction), 0.5, 1, w.now));
            Cand got = w.Resolve(t);
            if (cs.Count == 0) { Check(got == null || got.strength <= 2e-5f, "a claim resolved with nothing standing"); return; }
            Check(got != null, "no claim resolved though " + cs.Count + " stand");
            double max = cs.Max(c => c.s);
            double gs = cs.Where(c => c.who.Same(got.who) && c.ts == got.ts).Select(c => c.s).DefaultIfEmpty(-1).Max();
            Check(gs >= max - 1e-4, $"winner holds {gs:F5} but {max:F5} stands");
            Check(got.strength > 0f && got.strength <= 1f, "winner strength outside (0,1]: " + got.strength);
            // the sort is exact on the strengths the kernel computed (floats: a long-lived claim's decay is finer than a float step near 1,
            // so claims a few ticks apart can be equal): nothing stronger exists, and among exactly equal strengths the winner is the
            // more specific claimant, then the more recent
            var live = w.Candidates(t);
            Check(live.All(c => c.strength <= got.strength), "a stronger claim lost");
            var equal = live.Where(c => c.strength == got.strength).ToList();
            Check(equal.All(c => c.spec <= got.spec), "a tie was not broken to the more specific claimant");
            Check(equal.Where(c => c.spec == got.spec).All(c => c.ts <= got.ts), "a tie was not broken to the more recent claim");
        }

        // ════════════════════════ suspicion ════════════════════════
        private enum SA { Witness, Advance, Query, Bribe, Prune, Settings }

        private static string RunSuspicion(IList<Act> acts, int seed, bool count)
        {
            var r = new Random(seed ^ 0x7f4a7c15);
            var w = new World(r); w.now = 5000; int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    int f = a.a % Factions, s = a.b % Pawns;
                    switch ((SA)a.kind)
                    {
                        case SA.Witness:
                            {
                                int before = w.entries[f].Count;
                                C suspect = a.f ? PawnC(s) : CommonsC(a.c % Factions);
                                w.Register(f, suspect, new[] { 0.75f, 1f, 0.1f, 0f }[a.c % 4]);
                                if (suspect.kind != 1) Check(w.entries[f].Count <= before, "a Commons suspect was recorded");
                                break;
                            }
                        case SA.Advance: w.now += 1 + a.a * 200 + (a.f ? a.b * 2000 : 0); break;
                        case SA.Settings: w.halfLife = new[] { 5f, 45f, 180f }[a.a % 3]; break;
                        case SA.Prune:
                            {
                                int expired = w.entries[f].Count(e => (w.now - e.ts) / (double)TicksPerDay > w.halfLife + 1e-6);
                                int boundary = w.entries[f].Count(e => Math.Abs((w.now - e.ts) / (double)TicksPerDay - w.halfLife) <= 1e-6);
                                int before = w.entries[f].Count;
                                w.Prune(f);
                                if (boundary == 0) Check(w.entries[f].Count == before - expired, $"prune removed {before - w.entries[f].Count} entries, spec {expired}");
                                Check(w.entries[f].All(e => (w.now - e.ts) / (double)TicksPerDay < w.halfLife + 1e-6), "an expired entry survived the prune");
                                break;
                            }
                        case SA.Query:
                            {
                                // prune invariance: totalling ALL the entries, expired ones included and nothing pruned, gives the same answer
                                // (an expired entry weighs zero), so the total can be read before or after a prune
                                var all = w.entries[f].Select(e => new Entry { suspect = e.suspect, conf = e.conf, ts = e.ts }).ToList();
                                var copy = new World(new Random(1)) { now = w.now, halfLife = w.halfLife };
                                copy.entries[f] = all;
                                float unpruned = copy.Suspicion(f, s, false);
                                float pruned = w.Suspicion(f, s, true);
                                var snapshot = w.entries[f].Select(e => new Entry { suspect = e.suspect, conf = e.conf, ts = e.ts }).ToList();
                                Check(Math.Abs(pruned - unpruned) < 1e-6f, $"pruning changed the suspicion: {pruned} vs {unpruned}");
                                Check(pruned >= 0f && pruned <= 1f, "suspicion outside 0..1");
                                // the spec: sum of conf x min(1, days/3) x max(0, 1 - days/halfLife), clamped
                                double spec = 0;
                                foreach (Entry e in snapshot.Where(e => e.suspect == s))
                                {
                                    double days = (w.now - e.ts) / (double)TicksPerDay;
                                    spec += e.conf * Math.Min(1.0, Math.Max(0.0, days / 3.0)) * Math.Min(1.0, Math.Max(0.0, 1.0 - days / w.halfLife));
                                }
                                Check(Math.Abs(pruned - Math.Min(1.0, spec)) < 1e-3, $"suspicion {pruned} spec {Math.Min(1.0, spec):F5}");
                                // knows-enough implies a total of at least the threshold
                                bool knows = snapshot.Any(e => RM_PropertyKernel.KnowsEnough(RM_PropertyKernel.Contribution(e.conf, RM_PropertyKernel.DaysElapsed(w.now, e.ts, TicksPerDay), 1f / 3f, w.halfLife), 0.05f));
                                if (knows) Check(Enumerable.Range(0, Pawns).Any(sp => w.Suspicion(f, sp) >= 0.05f - 1e-6f), "an entry knows enough but no suspect reaches the threshold");
                                break;
                            }
                        case SA.Bribe:
                            {
                                float fraction = new[] { 0f, 0.35f, 1f, 2f, -1f }[a.c % 5];
                                float before = w.Suspicion(f, s);
                                var confBefore = w.entries[f].Select(e => e.conf).ToList();
                                w.Dampen(f, s, fraction);
                                float after = w.Suspicion(f, s);
                                Check(after <= before + 1e-6f, "dampening increased suspicion");
                                if (fraction >= 1f) Check(after == 0f, "a full bribe left suspicion " + after);
                                if (fraction <= 0f) Check(Math.Abs(after - before) < 1e-6f, "a non-positive bribe changed suspicion");
                                foreach (Entry e in w.entries[f]) Check(e.conf >= 0f, "negative confidence");
                                break;
                            }
                    }
                    for (int ff = 0; ff < Factions; ff++) foreach (Entry e in w.entries[ff]) Check(e.suspect >= 0 && e.suspect < Pawns, "entry for a non-pawn");
                }
                return null;
            }
            catch (Exception e) { return "step " + stepNo + ": " + e.Message; }
        }

        // ════════════════════════ tables ════════════════════════
        private static List<string> Tables(int n, int seed0)
        {
            var fails = new List<string>();
            Action<string, Action> run = (name, act) => { Cases++; try { act(); } catch (Exception e) { fails.Add("tables " + name + ": " + e.Message); } };

            run("decay", () =>
            {
                var r = new Random(seed0 + 1);
                for (int i = 0; i < n * 60; i++)
                {
                    Steps++;
                    float rec = (float)(r.NextDouble() * 1.4 - 0.2), mult = new[] { 0.25f, 1f, 4f, 0f }[r.Next(4)];
                    float life = RM_PropertyKernel.LifetimeTicks(rec, 3f, 3650f, mult, TicksPerDay);
                    double spec = (3.0 + 3647.0 * Math.Min(1.0, Math.Max(0.0, rec))) * mult * TicksPerDay;
                    Check(Math.Abs(life - spec) <= spec * 1e-5 + 1, $"lifetime {life} spec {spec}");
                    Check(RM_PropertyKernel.LifetimeTicks(Math.Min(1f, rec + 0.1f), 3f, 3650f, mult, TicksPerDay) >= life, "lifetime not monotone in recognizability");
                    float init = (float)r.NextDouble();
                    int age1 = r.Next(-5, (int)Math.Min(int.MaxValue / 2, life * 1.2) + 2), age2 = age1 + r.Next(0, 5000);
                    float s1 = RM_PropertyKernel.EffectiveStrength(init, age1, life), s2 = RM_PropertyKernel.EffectiveStrength(init, age2, life);
                    Check(s1 >= 0f && s1 <= init + 1e-6f, "strength outside 0..initial");
                    Check(age1 <= 0 ? s1 == init : true, "a claim not yet born decayed");
                    if (age1 > 0) Check(s2 <= s1 + 1e-6f, "strength grew with age");
                    if (age1 > 0 && age1 >= life) Check(s1 == 0f, "alive at or past its lifetime");
                    if (age1 > 0 && age1 < life) Check(Math.Abs(s1 - init * (1 - age1 / (double)life)) < 1e-4, "not linear");
                    if (age1 > 0 && mult > 0f) Check(RM_PropertyKernel.EffectiveStrength(init, age1, life * 2) >= s1 - 1e-6f, "a longer life weakened a claim");
                }
                Check(RM_PropertyKernel.EffectiveStrength(1f, 1, 0f) == 0f, "zero lifetime keeps a claim alive after birth");
            });

            run("order", () =>
            {
                var r = new Random(seed0 + 2);
                for (int i = 0; i < n * 80; i++)
                {
                    Steps++;
                    float s1 = (float)Math.Round(r.NextDouble(), 1), s2 = (float)Math.Round(r.NextDouble(), 1);
                    int p1 = r.Next(3), p2 = r.Next(3), t1 = r.Next(4), t2 = r.Next(4);
                    int o = RM_PropertyKernel.Order(s1, p1, t1, s2, p2, t2);
                    int spec = s1 != s2 ? (s1 > s2 ? -1 : 1) : p1 != p2 ? (p1 > p2 ? -1 : 1) : t1 != t2 ? (t1 > t2 ? -1 : 1) : 0;
                    Check(Math.Sign(o) == spec, $"Order({s1},{p1},{t1} vs {s2},{p2},{t2}) = {o}, spec {spec}");
                    Check(Math.Sign(RM_PropertyKernel.Order(s2, p2, t2, s1, p1, t1)) == -spec, "Order not antisymmetric");
                }
                Check(RM_PropertyKernel.Specificity(1) == 2 && RM_PropertyKernel.Specificity(2) == 1 && RM_PropertyKernel.Specificity(0) == 0, "specificity ranks");
            });

            run("spine", () =>
            {
                for (int act = 0; act <= 5; act++) foreach (bool auth in new[] { false, true }) foreach (bool prior in new[] { false, true })
                        {
                            Steps++;
                            int w = RM_PropertyKernel.SpineWrite(act, auth, prior);
                            int spec = act == 4 ? 1 : act == 5 ? 2 : ((act == 0 || act == 2) && !auth && prior) ? 3 : 0;
                            Check(w == spec, $"SpineWrite({act},{auth},{prior}) = {w}, spec {spec}");
                            bool after = RM_PropertyKernel.AuthorizedAfter(act, auth);
                            Check(after == (act == 4 || act == 5 || auth), "AuthorizedAfter");
                            Check(RM_PropertyKernel.RollsPerception(after, true) == !after && !RM_PropertyKernel.RollsPerception(after, false), "RollsPerception");
                            Check(RM_PropertyKernel.IsAuthorized(prior, auth) == (!prior || auth), "IsAuthorized");
                        }
                // an act nobody authorized, with no one wronged, writes nothing; use and sabotage never write
                Check(RM_PropertyKernel.SpineWrite(1, false, true) == 0 && RM_PropertyKernel.SpineWrite(3, false, true) == 0, "use / sabotage wrote");
                for (byte ck = 0; ck < 3; ck++) for (byte ak = 0; ak < 3; ak++) foreach (bool eq in new[] { false, true }) foreach (bool sf in new[] { false, true })
                                Check(RM_PropertyKernel.ClaimantMayUse(eq, ck, ak, sf) == (eq || (ck == 2 && ak == 1 && sf)), "ClaimantMayUse");
                for (byte k = 0; k < 3; k++) foreach (bool pm in new[] { false, true }) foreach (bool fm in new[] { false, true })
                            Check(RM_PropertyKernel.IsGhost(k, pm, fm) == ((k == 1 && pm) || (k == 2 && fm)), "IsGhost");
                Check(RM_PropertyKernel.VirtualBasis(true, true) == 1 && RM_PropertyKernel.VirtualBasis(false, true) == 2 && RM_PropertyKernel.VirtualBasis(false, false) == 0 && RM_PropertyKernel.VirtualBasis(true, false) == 1, "VirtualBasis");
                Check(RM_PropertyKernel.LootKeepsOrigin(false) && !RM_PropertyKernel.LootKeepsOrigin(true), "LootKeepsOrigin");
                Check(RM_PropertyKernel.OwnerWitnessed(true, true) && !RM_PropertyKernel.OwnerWitnessed(true, false) && !RM_PropertyKernel.OwnerWitnessed(false, true), "OwnerWitnessed");
                // the constants restate the enums
                Check(RM_PropertyKernel.KindNone == 0 && RM_PropertyKernel.KindPawn == 1 && RM_PropertyKernel.KindCommons == 2 && RM_PropertyKernel.ActTake == 0 && RM_PropertyKernel.ActBuy == 4 && RM_PropertyKernel.ActClaim == 5, "enum constants");
            });

            run("money", () =>
            {
                var r = new Random(seed0 + 3);
                for (int i = 0; i < n * 120; i++)
                {
                    Steps++;
                    // silver removal: conservation across any stacking
                    int stacks = r.Next(0, 6); var st = new List<int>(); for (int k = 0; k < stacks; k++) st.Add(1 + r.Next(500));
                    int amount = r.Next(-5, 2600), total = st.Sum(), remaining = Math.Max(0, amount), taken = 0;
                    var left = new List<int>(st);
                    for (int k = 0; k < left.Count && remaining > 0; k++)
                    {
                        int take = RM_PropertyKernel.TakeFromStack(remaining, left[k]);
                        Check(take >= 0 && take <= left[k] && take <= remaining, "a take outside the stack or the remaining amount");
                        left[k] -= take; remaining -= take; taken += take;
                    }
                    Check(taken == Math.Min(Math.Max(0, amount), total), $"took {taken} of {amount} from {total}");
                    Check(left.Sum() == total - taken && left.All(x => x >= 0), "silver not conserved by removal");
                    Check(!RM_PropertyKernel.CanPay(total, total + 1) && RM_PropertyKernel.CanPay(total, total) && RM_PropertyKernel.CanPay(total, 0), "CanPay edge");

                    // fees and prices
                    float mv = new[] { 0f, 1f, 3f, 40f, 400f, 2500f, -5f }[r.Next(7)], markup = new[] { 0.5f, 1.15f, 3f }[r.Next(3)]; int stack = r.Next(-1, 80);
                    int price = RM_PropertyKernel.Price(mv, stack, markup);
                    Check(price >= 1, "price below one");
                    Check(Math.Abs(price - Math.Max(1.0, Math.Round(Math.Max(0, mv) * Math.Max(1, stack) * markup))) <= 1, "price formula");
                    Check(RM_PropertyKernel.Price(mv + 10f, stack, markup) >= price && RM_PropertyKernel.Price(mv, stack + 1, markup) >= price, "price not monotone");
                    float rec = (float)r.NextDouble(), str = (float)r.NextDouble(), mult = new[] { 0.25f, 1f, 3f, 0f }[r.Next(4)];
                    int fee = RM_PropertyKernel.SalvageFee(rec, true, str, mult, 5, 350, 0.2f);
                    double feeSpec = (5.0 + 345.0 * rec * (0.2 + 0.8 * str)) * mult;
                    Check(Math.Abs(fee - Math.Max(1.0, feeSpec)) <= 1.0, $"salvage fee {fee} spec {Math.Max(1.0, feeSpec):F2} (recognizability {rec}, claim {str}, x{mult})");
                    Check(fee >= 1, "a salvage fee below one silver");
                    if (rec > 0.5f && mult > 0f) Check(RM_PropertyKernel.SalvageFee(rec, true, 1f, mult, 5, 350, 0.2f) > RM_PropertyKernel.SalvageFee(rec, true, 0f, mult, 5, 350, 0.2f) || mult * rec < 0.01f, "a stronger claim did not cost more");
                    Check(fee <= Math.Max(1, (int)Math.Round(350 * mult)) + 1, $"fee {fee} out of range at mult {mult}");
                    Check(RM_PropertyKernel.SalvageFee(Math.Min(1f, rec + 0.1f), true, str, mult, 5, 350, 0.2f) >= fee, "fee not monotone in recognizability");
                    Check(RM_PropertyKernel.SalvageFee(rec, true, Math.Min(1f, str + 0.1f), mult, 5, 350, 0.2f) >= fee, "fee not monotone in claim strength");
                    Check(RM_PropertyKernel.SalvageFee(rec, false, 0.9f, mult, 5, 350, 0.2f) == RM_PropertyKernel.SalvageFee(rec, true, 0f, mult, 5, 350, 0.2f), "an unclaimed thing priced by a phantom claim");
                    int top = RM_PropertyKernel.SalvageFee(1f, true, 1f, mult, 5, 350, 0.2f);
                    Check(top == Math.Max(1, (int)Math.Round(350 * mult)), "the dearest fee is not the maximum");
                    Check(RM_PropertyKernel.ConfiguredFee(r.Next(-3, 120) * 0.5f) >= 1, "configured fee below one");
                }
                Check(RM_PropertyKernel.ConfiguredFee(0f) == 1 && RM_PropertyKernel.ConfiguredFee(14.5f) == 14 && RM_PropertyKernel.ConfiguredFee(15.5f) == 16, "ConfiguredFee rounding (to even)");
            });

            run("pocket", () =>
            {
                var r = new Random(seed0 + 4);
                for (int i = 0; i < n * 80; i++)
                {
                    Steps++;
                    float min = new[] { 0f, 1f, 4f, 30f, 50f }[r.Next(5)]; int cnt = r.Next(0, 6);
                    var vals = new List<float>();
                    for (int k = 0; k < cnt; k++)
                    {
                        float mvk = new[] { 0f, 1f, 4f, 30f, 400f, -3f }[r.Next(6)]; int sk = r.Next(-1, 5);
                        float v = RM_PropertyKernel.ItemValue(mvk, sk);
                        Check(Math.Abs(v - Math.Max(0f, mvk) * Math.Max(1, sk)) < 1e-6, $"ItemValue({mvk},{sk}) = {v}");
                        vals.Add(v);
                    }
                    int best = -1; float bestV = 0f;
                    for (int k = 0; k < vals.Count; k++)
                    {
                        if (!RM_PropertyKernel.WorthStealing(vals[k], min)) continue;
                        if (RM_PropertyKernel.BeatsBest(vals[k], bestV)) { bestV = vals[k]; best = k; }
                    }
                    var eligible = vals.Select((v, k) => (v, k)).Where(x => x.v >= min && x.v > 0f).ToList();
                    if (eligible.Count == 0) Check(best == -1, "picked a pocket nothing in it is worth");
                    else
                    {
                        Check(best >= 0 && Math.Abs(vals[best] - eligible.Max(x => x.v)) < 1e-6, "did not pick the most valuable item");
                        Check(best == eligible.First(x => Math.Abs(x.v - eligible.Max(y => y.v)) < 1e-6).k, "a tie was not broken to the first");
                        Check(vals[best] >= min, "picked below the threshold");
                    }
                }
                // an item worth exactly zero is never stolen even when the threshold slider is at zero
                Check(!RM_PropertyKernel.BeatsBest(RM_PropertyKernel.ItemValue(0f, 3), 0f), "a zero-value item beats nothing");
                Check(RM_PropertyKernel.TheftRollPasses(1f, 0.9999f) && RM_PropertyKernel.TheftRollPasses(2f, 1f) && !RM_PropertyKernel.TheftRollPasses(0f, 0f) && RM_PropertyKernel.TheftRollPasses(0.5f, 0.49f) && !RM_PropertyKernel.TheftRollPasses(0.5f, 0.5f), "animal-theft roll");
                Check(RM_PropertyKernel.LightEnough(2.5f, 2.5f) && !RM_PropertyKernel.LightEnough(2.51f, 2.5f), "carry limit edge is inclusive");
            });

            run("recognizability", () =>
            {
                var r = new Random(seed0 + 5);
                Check(RM_PropertyKernel.Recognizability(false, true, 6, 9999f, true, true, true, 1) == 0f, "a missing thing has a score");
                for (int i = 0; i < n * 80; i++)
                {
                    Steps++;
                    bool hq = r.Next(2) == 0, named = r.Next(2) == 0, mech = r.Next(2) == 0; int q = r.Next(0, 7), sl = new[] { 1, 75, 500 }[r.Next(3)]; float mv = (float)(r.NextDouble() * 4000 - 100);
                    float s = RM_PropertyKernel.Recognizability(true, hq, q, mv, named, mech, true, sl);
                    double spec = 0.05 + (hq ? 0.30 * q / 6.0 : 0) + (mv > 0 ? 0.25 * Math.Min(1, mv / 2000.0) : 0) + (named ? 0.30 : 0) + (mech ? 0.25 : 0) + (sl <= 1 ? 0.05 : 0);
                    Check(Math.Abs(s - Math.Min(1.0, spec)) < 1e-5, $"recognizability {s} spec {Math.Min(1.0, spec)}");
                    Check(s >= 0.05f && s <= 1f, "score outside 0.05..1");
                    if (hq && q < 6) Check(RM_PropertyKernel.Recognizability(true, hq, q + 1, mv, named, mech, true, sl) >= s, "better quality scored lower");
                    Check(RM_PropertyKernel.Recognizability(true, hq, q, mv + 100f, named, mech, true, sl) >= s, "a dearer thing scored lower");
                    Check(RM_PropertyKernel.Recognizability(true, hq, q, mv, true, mech, true, sl) >= s, "a named thing scored lower");
                }
            });
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
                ("ledger", () => RunFamily("ledger", N(5000), S(1), (r, len) => Gen(r, len, new[] { 10, 12, 14, 8, 8, 8, 2, 5, 4, 4, 2, 3, 3, 2, 2 }), RunLedger, 30, 170)),
                ("suspicion", () => RunFamily("suspicion", N(4000), S(1), (r, len) => Gen(r, len, new[] { 25, 25, 25, 12, 8, 5 }), RunSuspicion, 20, 120)),
                ("tables", () => Tables(Math.Max(1, N(40)), S(1))),
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
            Console.WriteLine($"reached: purchases {Buys}, paid claims {Claims}, bribes {Bribes}, payments refused at click {Refused}, takes {Thefts} ({StolenRecords} unauthorized with an owner), witnesses {Witnessed}, wipes {Wipes}, ghosts {Ghosts}, purchases not winning on a tie {Ties}");
            if (only == null && !oneSeed.HasValue && scale >= 1 && (Buys == 0 || Claims == 0 || Bribes == 0 || Refused == 0 || StolenRecords == 0 || Witnessed == 0 || Wipes == 0))
            { Console.WriteLine("FAIL property fuzz never reached a path (blind)"); ok = false; }
            Console.WriteLine($"property fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
