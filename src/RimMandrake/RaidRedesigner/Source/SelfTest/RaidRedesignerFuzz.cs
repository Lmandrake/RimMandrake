// Approach B for RaidRedesigner: seeded fuzz over RM_RosterKernel (the roster flow GameComponent_OldFriends runs) against an independent
// restatement of the 1.4 rules (a plain list of records, written from the design text, sharing no code with the kernel).
//   roster  random Record / Die / Sweep / cap-change sequences; after EVERY step the kernel-driven roster must equal the model and the
//           structural invariants hold (one living entry per pawn, clamps, cap, dead entries immortal and frozen, victims are the lowest)
//   tables  ScaledDelta / Clamp / Sweep / DeadSummary exhaustively or on dense grids
// A failing sequence is shrunk and printed as `roster seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.RaidRedesigner.SelfTest
{
    internal static class RaidRedesignerFuzz
    {
        public static long Cases, Steps, NewEntries, SelfEvictions, Prunes, Upgrades, Deaths, Lost, ZeroMult;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private sealed class FEntry : IRosterEntry
        {
            public int Pawn; public RoleTag role; public int grudge, notability, lastSeen; public bool dead; public int encounters; public string lastSummary;
            public RoleTag Role { get { return role; } set { role = value; } }
            public int Grudge { get { return grudge; } set { grudge = value; } }
            public int Notability { get { return notability; } set { notability = value; } }
            public int LastSeenTick { get { return lastSeen; } set { lastSeen = value; } }
            public bool Dead { get { return dead; } }
            public bool PinnedByUs { get; set; }
            public void NoteEncounter(int tick, RoleTag r, string summary) { encounters++; lastSeen = tick; lastSummary = summary; }
        }

        private enum A { Record, Die, Sweep, Cap }
        private struct Act
        {
            public A kind; public int pawn; public RoleTag role; public int tick, gd, nd, cap; public float mult;
            public override string ToString() { return kind + "(p" + pawn + "," + role + ",t" + tick + ",g" + gd + ",n" + nd + ",x" + mult.ToString(System.Globalization.CultureInfo.InvariantCulture) + ",cap" + cap + ")"; }
        }

        // ── independent model ──
        private sealed class Rec { public int pawn; public RoleTag role; public int g, n, seen, enc; public bool dead; }

        private static int Trunc(int d, float m) { double v = (double)d * (double)m; return v < 0 ? -(int)Math.Floor(-v) : (int)Math.Floor(v); }
        private static int Cl(int v, int lo, int hi) { return Math.Max(lo, Math.Min(hi, v)); }

        private sealed class Model
        {
            public List<Rec> recs = new List<Rec>();
            public bool lastEvictedSelf; public bool lastNew; public List<int> lastVictims = new List<int>();
            public void Record(Act a, int cap)
            {
                Rec r = recs.FirstOrDefault(x => !x.dead && x.pawn == a.pawn);
                lastNew = r == null; lastEvictedSelf = false; lastVictims = new List<int>();
                if (r == null) { r = new Rec { pawn = a.pawn, role = a.role, seen = a.tick }; recs.Add(r); }
                else if (a.role == RoleTag.Captain) r.role = RoleTag.Captain;
                r.enc++; r.seen = a.tick;
                r.g = Cl(r.g + Trunc(a.gd, a.mult), -100, 100);
                r.n = Cl(r.n + Trunc(a.nd, a.mult), 0, 100);
                if (lastNew)
                {
                    var living = recs.Where(x => !x.dead).ToList();
                    int over = living.Count - cap;
                    if (over > 0)
                    {
                        // lowest notability, then stalest; the same key twice is a true tie (identical rows), so any order is equal
                        var victims = living.OrderBy(x => x.n).ThenBy(x => x.seen).Take(over).ToList();
                        foreach (var v in victims) { recs.Remove(v); lastVictims.Add(v.pawn); if (ReferenceEquals(v, r)) lastEvictedSelf = true; }
                    }
                }
            }
        }

        private static string Describe(IEnumerable<FEntry> es) { return string.Join(";", es.Select(e => e.Pawn + ":" + e.role + "," + e.grudge + "," + e.notability + "," + e.lastSeen + "," + e.encounters + (e.dead ? ",D" : ""))); }
        private static string Describe(IEnumerable<Rec> rs) { return string.Join(";", rs.Select(e => e.pawn + ":" + e.role + "," + e.g + "," + e.n + "," + e.seen + "," + e.enc + (e.dead ? ",D" : ""))); }

        private static readonly float[] Mults = { 0f, 0.25f, 0.5f, 1f, 1f, 1f, 1.5f, 2f, 3f, 0.1f, 0.3f };
        private static readonly int[] Deltas = { 0, 5, 10, 15, 20, 25, -5, -20, 100, -100, 200, -200, 1, -1 };

        private static List<Act> Gen(Random rng, int len, int pawns)
        {
            var acts = new List<Act>();
            int cap = 24, tick = 0;
            for (int i = 0; i < len; i++)
            {
                var a = new Act { pawn = rng.Next(pawns) };
                int k = rng.Next(100);
                a.kind = k < 80 ? A.Record : k < 88 ? A.Die : k < 95 ? A.Sweep : A.Cap;
                tick += rng.Next(0, 4) == 0 ? 0 : rng.Next(1, 900);   // ties on lastSeen are deliberately common
                if (rng.Next(25) == 0) tick -= rng.Next(0, 500);      // and the odd out-of-order tick
                a.tick = Math.Max(0, tick);
                a.role = (RoleTag)rng.Next(8);
                if (rng.Next(6) == 0) a.role = RoleTag.Captain;
                a.gd = Deltas[rng.Next(Deltas.Length)]; a.nd = Deltas[rng.Next(Deltas.Length)];
                a.mult = Mults[rng.Next(Mults.Length)];
                if (a.kind == A.Cap) { cap = rng.Next(6) == 0 ? rng.Next(0, 3) : rng.Next(2, 49); }
                a.cap = cap;
                acts.Add(a);
            }
            return acts;
        }

        // Runs a sequence; returns null if every invariant held, else a message.
        private static string Run(List<Act> acts, bool count)
        {
            var roster = new List<FEntry>();
            var model = new Model();
            var deadSnapshots = new Dictionary<FEntry, string>();
            var lostPawns = new HashSet<int>();
            int step = 0;
            try
            {
                foreach (Act a in acts)
                {
                    step++;
                    if (count) Steps++;
                    int cap = a.cap;
                    switch (a.kind)
                    {
                        case A.Record:
                        {
                            int before = roster.Count(e => !e.Dead);
                            var encBefore = roster.Where(e => !e.Dead && e.Pawn == a.pawn).Select(e => e.encounters).DefaultIfEmpty(-1).First();
                            var deadBefore = roster.Where(e => e.Dead).ToList();
                            RecordOutcome<FEntry> o = RM_RosterKernel.Record(roster, e => e.Pawn == a.pawn,
                                () => new FEntry { Pawn = a.pawn, role = a.role, lastSeen = a.tick }, a.role, a.tick, "s" + step, a.gd, a.nd, a.mult, cap);
                            model.Record(a, cap);
                            Check(o.Entry != null, "Record returned no entry");
                            Check(o.IsNew == model.lastNew, "IsNew " + o.IsNew + " vs model " + model.lastNew);
                            Check(o.EvictedSelf == model.lastEvictedSelf, "EvictedSelf " + o.EvictedSelf + " vs model " + model.lastEvictedSelf);
                            Check(o.EvictedSelf == !roster.Contains(o.Entry), "EvictedSelf disagrees with the entry being in the roster");
                            Check(o.Victims.Select(v => v.Pawn).OrderBy(x => x).SequenceEqual(model.lastVictims.OrderBy(x => x)), "victims differ: " + string.Join(",", o.Victims.Select(v => v.Pawn)) + " vs " + string.Join(",", model.lastVictims));
                            Check(o.Victims.All(v => !v.Dead), "a dead entry was chosen as a prune victim");
                            Check(o.IsNew || o.Victims.Count == 0, "an existing pawn's encounter pruned someone");
                            Check(o.IsNew || o.Entry.encounters == encBefore + 1, "encounter count of an existing entry did not go up by one");
                            Check(deadBefore.All(d => roster.Contains(d)), "Record removed a dead entry");
                            Check(o.IsNew || o.Entry.lastSummary == "s" + step, "summary not recorded");
                            if (count)
                            {
                                if (o.IsNew) NewEntries++;
                                if (o.EvictedSelf) SelfEvictions++;
                                Prunes += o.Victims.Count;
                                if (!o.IsNew && a.role == RoleTag.Captain) Upgrades++;
                                if (a.mult == 0f) ZeroMult++;
                            }
                            if (o.IsNew) Check(roster.Count(e => !e.Dead) <= Math.Max(cap, 0), "living " + roster.Count(e => !e.Dead) + " exceeds cap " + cap + " after a new entry");
                            break;
                        }
                        case A.Die:
                        {
                            // the hourly sweep found the pawn dead: the production verdict decides
                            foreach (FEntry e in roster.ToList())
                            {
                                if (e.Pawn != a.pawn) continue;
                                var v = RM_RosterKernel.Sweep(e.Dead, lostPawns.Contains(e.Pawn), true);
                                if (v == RM_RosterKernel.SweepVerdict.Died) { e.dead = true; deadSnapshots[e] = e.role + "|" + e.grudge + "|" + e.notability; if (count) Deaths++; }
                            }
                            foreach (Rec r in model.recs) if (!r.dead && r.pawn == a.pawn) r.dead = true;
                            break;
                        }
                        case A.Sweep:
                        {
                            // a discarded pawn: its reference resolved to null on load
                            foreach (FEntry e in roster)
                            {
                                bool gone = e.Pawn % 7 == a.pawn % 7 && !e.Dead;
                                var v = RM_RosterKernel.Sweep(e.Dead, gone, false);
                                Check(v == (gone ? RM_RosterKernel.SweepVerdict.Lost : RM_RosterKernel.SweepVerdict.Alive), "sweep verdict for a lost pawn");
                                if (v == RM_RosterKernel.SweepVerdict.Lost) { e.dead = true; deadSnapshots[e] = e.role + "|" + e.grudge + "|" + e.notability; if (count) Lost++; }
                            }
                            foreach (Rec r in model.recs) if (!r.dead && r.pawn % 7 == a.pawn % 7) r.dead = true;
                            break;
                        }
                        case A.Cap: break;   // the cap only matters at the next new entry (the kernel never prunes by itself)
                    }
                    // model equality and structural invariants after every step
                    Check(Describe(roster) == Describe(model.recs), "state differs\n   kernel: " + Describe(roster) + "\n   model:  " + Describe(model.recs));
                    foreach (FEntry e in roster)
                    {
                        Check(e.grudge >= -100 && e.grudge <= 100, "grudge " + e.grudge + " out of range");
                        Check(e.notability >= 0 && e.notability <= 100, "notability " + e.notability + " out of range");
                        if (e.dead) Check(deadSnapshots.ContainsKey(e) && deadSnapshots[e] == e.role + "|" + e.grudge + "|" + e.notability, "a dead entry changed after death");
                    }
                    Check(roster.Where(e => !e.dead).GroupBy(e => e.Pawn).All(g => g.Count() == 1), "two living entries for one pawn");
                }
            }
            catch (Exception ex) { return "step " + step + ": " + ex.Message; }
            return null;
        }

        private static List<Act> Shrink(List<Act> acts)
        {
            var cur = new List<Act>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<Act>(cur); trial.RemoveRange(i, chunk);
                        if (Run(trial, false) != null) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        private static List<string> Roster(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s;
                var rng = new Random(seed);
                // a small pawn pool crowds the roster so the cap bites; a large one exercises many distinct entries
                var acts = Gen(rng, rng.Next(5, 200), rng.Next(3) == 0 ? 6 : rng.Next(3) == 0 ? 80 : 30);
                Cases++;
                string msg = Run(acts, true);
                if (msg != null)
                {
                    var small = Shrink(acts);
                    fails.Add("roster seed " + seed + ": " + (Run(small, false) ?? msg) + " | " + string.Join(" ", small));
                }
            }
            return fails;
        }

        private static List<string> Tables()
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                foreach (int d in new[] { -300, -100, -25, -5, -1, 0, 1, 5, 10, 25, 100, 300 })
                    foreach (float m in new[] { 0f, 0.1f, 0.25f, 0.3f, 0.5f, 0.7f, 1f, 1.1f, 1.5f, 2f, 3f })
                    {
                        Steps++;
                        int got = RM_RosterKernel.ScaledDelta(d, m);
                        Check(Math.Abs(got) <= Math.Abs((double)d * m) + 1e-4, "ScaledDelta(" + d + "," + m + ") = " + got + " grew past |delta*mult|");
                        Check(Math.Abs((double)d * m - got) < 1.0 + 1e-4, "ScaledDelta(" + d + "," + m + ") = " + got + " is more than one off");
                        Check(got == 0 || Math.Sign(got) == Math.Sign(d), "ScaledDelta flipped the sign");
                        Check(m != 1f || got == d, "multiplier 1 must pass the delta through");
                        Check(m != 0f || got == 0, "multiplier 0 must freeze the score");
                        Check(RM_RosterKernel.ScaledDelta(-d, m) == -got, "ScaledDelta is not odd (" + d + "," + m + ")");
                    }
                foreach (int v in new[] { -1000, -101, -100, -1, 0, 1, 99, 100, 101, 1000 })
                {
                    Steps++;
                    Check(RM_RosterKernel.Clamp(v, 0, 100) == Math.Max(0, Math.Min(100, v)), "Clamp 0..100 of " + v);
                    Check(RM_RosterKernel.NextGrudge(v, 0, 1f) >= -100 && RM_RosterKernel.NextGrudge(v, 0, 1f) <= 100, "NextGrudge range");
                    Check(RM_RosterKernel.NextNotability(v, 0, 1f) >= 0 && RM_RosterKernel.NextNotability(v, 0, 1f) <= 100, "NextNotability range");
                }
                // sweep verdict table, exhaustive
                foreach (bool dead in new[] { false, true }) foreach (bool isNull in new[] { false, true }) foreach (bool pd in new[] { false, true })
                {
                    Steps++;
                    var want = dead ? RM_RosterKernel.SweepVerdict.Alive : isNull ? RM_RosterKernel.SweepVerdict.Lost : pd ? RM_RosterKernel.SweepVerdict.Died : RM_RosterKernel.SweepVerdict.Alive;
                    Check(RM_RosterKernel.Sweep(dead, isNull, pd) == want, "Sweep(" + dead + "," + isNull + "," + pd + ")");
                }
                // dead summary carries everything the design promises
                foreach (RoleTag r in Enum.GetValues(typeof(RoleTag)))
                {
                    Steps++;
                    string s = RM_RosterKernel.DeadSummary("Korro", r, -7, 42, "died");
                    Check(s.Contains("Korro") && s.Contains(r.ToString()) && s.Contains("-7") && s.Contains("42") && s.EndsWith("died") && s.IndexOf('\n') < 0, "DeadSummary text: " + s);
                }
                // pin ownership truth tables, exhaustive: a pin is released only if it was ours and the pawn leads no faction
                foreach (bool ours in new[] { false, true }) foreach (bool before in new[] { false, true }) foreach (bool after in new[] { false, true })
                {
                    Steps++;
                    if (before && !after) continue;   // a pin is never removed by a pin attempt
                    bool want = ours || (!before && after);
                    Check(RM_RosterKernel.PinnedByUsAfter(ours, before, after) == want, "PinnedByUsAfter(" + ours + "," + before + "," + after + ")");
                    Check(!RM_RosterKernel.PinnedByUsAfter(false, true, after), "a pin somebody else placed was claimed as ours");
                }
                foreach (bool ours in new[] { false, true }) foreach (bool leader in new[] { false, true })
                {
                    Steps++;
                    Check(RM_RosterKernel.ShouldUnpin(ours, leader) == (ours && !leader), "ShouldUnpin(" + ours + "," + leader + ")");
                }
                // the role enum is append-only and scribed by name; eight tags today
                Check(Enum.GetValues(typeof(RoleTag)).Length == 8, "RoleTag count changed - the hook table and the fuzz generator need a look");
                Check(RM_RosterKernel.GrudgeMin == -100 && RM_RosterKernel.GrudgeMax == 100 && RM_RosterKernel.NotabilityMin == 0 && RM_RosterKernel.NotabilityMax == 100, "score bounds are the design's -100..100 / 0..100");
            }
            catch (Exception ex) { fails.Add("tables: " + ex.Message); }
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
                ("roster", () => Roster(N(6000), S(1))),
                ("tables", () => Tables()),
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
            if (only == null || only == "roster")
            {
                Console.WriteLine($"roster reached: new entries {NewEntries}, self-evictions {SelfEvictions}, prunes {Prunes}, captain upgrades {Upgrades}, deaths {Deaths}, lost {Lost}, zero-multiplier records {ZeroMult}");
                if (!oneSeed.HasValue && scale >= 1 && (NewEntries == 0 || SelfEvictions == 0 || Prunes == 0 || Upgrades == 0 || Deaths == 0 || Lost == 0 || ZeroMult == 0)) { Console.WriteLine("FAIL roster fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"raidredesigner fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
