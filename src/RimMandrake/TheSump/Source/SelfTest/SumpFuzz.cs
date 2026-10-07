// Approach B for TheSump: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/RM_SumpKernel.cs):
//   kethrel  the scrap-shell animal: pickup / stage / molt / handler choice through a fake world, probe order checked, against a spec
//   vault    the tar vault's seal ledger: arrivals, departures, destruction, extraction with and without solvent, rot flags in step
//   mere     the Deep Black mere's randomized flood fill on random grids: connectivity, size, exhaustion, rim, reservoir uniformity
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.TheSump.SelfTest
{
    internal static class SumpFuzz
    {
        public static long Cases, Steps, Picks, Molts, Seeks, Cleans, Ruins, Seals, Unseals, Blobs, Exhausted;
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

        // ════════════════════════ kethrel ════════════════════════
        private enum KA { Spawn, Tick, Coax, Despawn, Settings }
        private struct KAct
        {
            public KA kind; public int a, b; public bool f;
            public override string ToString() { return kind + "(" + a + "," + b + (f ? ",T" : "") + ")"; }
        }

        private sealed class Item { public int id; public float kg; public int stack; public float value; public bool weapon, listed, forbidden, home, item = true; }

        private sealed class KWorld
        {
            public List<float> thresholds = new List<float> { 3f, 10f, 22f };
            public List<Item> ground = new List<Item>(), carried = new List<Item>();
            public int stage; public float hediff; public float moltKg = 30f, ceiling = 200f; public bool takeColony, enabled = true;
            public int nextId = 1, molts, picks, seeks;
            public float Load { get { float k = 0f; foreach (Item i in carried) k += i.kg * i.stack; return k; } }
            public bool WantedItem(Item i)
            {
                return RM_KethrelKernel.Wanted(true, i.item, i.forbidden, i.weapon || i.listed, i.value * i.stack, ceiling, takeColony, i.home);
            }
            public Item Find(bool far, bool nearOnly)
            {
                Item best = null;
                foreach (Item i in ground) if (WantedItem(i) && (far || !i.home || true) && (nearOnly ? i.id % 3 != 0 : true)) { best = i; break; }
                return best;
            }
            public void Refresh()
            {
                int s = RM_KethrelKernel.StageForLoad(thresholds, Load);
                if (RM_KethrelKernel.StageChanged(stage, s)) { stage = s; hediff = s <= 0 ? 0f : RM_KethrelKernel.HediffSeverity(s); }
            }
        }

        private static KAct[] GenK(Random r, int len)
        {
            var a = new KAct[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                KA kind = k < 30 ? KA.Spawn : k < 80 ? KA.Tick : k < 88 ? KA.Coax : k < 93 ? KA.Despawn : KA.Settings;
                a[i] = new KAct { kind = kind, a = r.Next(1 << 12), b = r.Next(1 << 12), f = r.Next(2) == 0 };
            }
            return a;
        }

        private static string RunKethrel(IList<KAct> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x3c6ef372);
            var w = new KWorld();
            if (rr.Next(3) == 0) w.thresholds = new List<float> { 1f + rr.Next(4), 5f + rr.Next(8), 15f + rr.Next(12), 30f + rr.Next(10) }.OrderBy(x => x).ToList();
            w.moltKg = 12f + rr.Next(40);
            float totalKg = 0f; int made = 0, droppedBack = 0;
            int stepNo = 0;
            try
            {
                foreach (KAct a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case KA.Spawn:
                            {
                                var it = new Item { id = w.nextId++, kg = (a.a % 9) * 0.75f, stack = 1 + a.b % 3, value = (a.a % 7) * 40f, weapon = (a.a & 8) != 0, listed = (a.a & 16) != 0, forbidden = (a.b & 8) == 0 && (a.b & 16) != 0, home = (a.b & 32) != 0, item = (a.a & 64) == 0 };
                                w.ground.Add(it); made++;
                                break;
                            }
                        case KA.Settings:
                            w.takeColony = a.f; w.ceiling = 50f + (a.a % 6) * 60f; w.enabled = (a.b & 3) != 0;
                            break;
                        case KA.Despawn:
                            // death / leaving the map: nothing vanishes with the animal
                            droppedBack += w.carried.Count; w.ground.AddRange(w.carried); w.carried.Clear(); w.stage = 0; w.hediff = 0f;
                            break;
                        case KA.Coax:
                            {
                                int n = a.a % 5;
                                var skills = new List<int>(); var able = new List<bool>();
                                for (int i = 0; i < n; i++) { skills.Add((a.b >> i * 2) & 7); able.Add(((a.b >> 11) + i) % 3 != 0); }
                                int pick = RM_KethrelKernel.BestHandler(skills, able);
                                int want = -1, bs = -1; for (int i = 0; i < n; i++) if (able[i] && skills[i] > bs) { bs = skills[i]; want = i; }
                                Check(pick == want, $"BestHandler {pick} vs spec {want}");
                                if (pick >= 0) Check(able[pick] && skills.Where((s, i) => able[i]).All(s => s <= skills[pick]), "handler is not the best able colonist");
                                // a coaxed molt drops everything
                                if (w.carried.Count > 0 && pick >= 0) { droppedBack += w.carried.Count; w.ground.AddRange(w.carried); w.carried.Clear(); w.stage = 0; w.hediff = 0f; w.molts++; if (count) Molts++; }
                                break;
                            }
                        case KA.Tick:
                            {
                                bool dead = (a.a & 1) != 0 && (a.b & 3) == 0, spawned = (a.a & 2) == 0 || (a.b & 3) != 0, downed = (a.a & 4) != 0 && (a.b & 7) == 0;
                                bool tar = (a.a & 8) != 0 || (a.b & 12) != 0, idle = (a.a & 16) != 0, reach = (a.a & 32) != 0 || a.f;
                                var probes = new List<string>();
                                Item near = null, far = null;
                                KethrelAction act = RM_KethrelKernel.Decide(w.enabled, dead, spawned, downed, () => { probes.Add("load"); return w.Load; }, w.moltKg,
                                    () => { probes.Add("tar"); return tar; },
                                    () => { probes.Add("near"); near = w.Find(false, true); return near != null; },
                                    () => { probes.Add("idle"); return idle; },
                                    () => { probes.Add("far"); far = w.Find(true, false); return far != null && reach; });
                                // spec
                                KethrelAction want; var wantProbes = new List<string>();
                                if (!w.enabled || dead || !spawned || downed) want = KethrelAction.None;
                                else
                                {
                                    wantProbes.Add("load");
                                    if (w.Load >= w.moltKg) want = KethrelAction.Molt;
                                    else
                                    {
                                        wantProbes.Add("tar");
                                        if (!tar) want = KethrelAction.None;
                                        else
                                        {
                                            wantProbes.Add("near");
                                            if (w.Find(false, true) != null) want = KethrelAction.PickUp;
                                            else
                                            {
                                                wantProbes.Add("idle");
                                                if (!idle) want = KethrelAction.None;
                                                else { wantProbes.Add("far"); want = (w.Find(true, false) != null && reach) ? KethrelAction.Seek : KethrelAction.None; }
                                            }
                                        }
                                    }
                                }
                                Check(act == want, $"Decide {act} vs spec {want}");
                                Check(probes.SequenceEqual(wantProbes), $"probes [{string.Join(",", probes)}] vs spec [{string.Join(",", wantProbes)}] (laziness / order)");
                                switch (act)
                                {
                                    case KethrelAction.PickUp: w.ground.Remove(near); w.carried.Add(near); w.Refresh(); w.picks++; if (count) Picks++; break;
                                    case KethrelAction.Molt: droppedBack += w.carried.Count; w.ground.AddRange(w.carried); w.carried.Clear(); w.stage = 0; w.hediff = 0f; w.molts++; if (count) Molts++; break;
                                    case KethrelAction.Seek: w.seeks++; if (count) Seeks++; break;
                                }
                                break;
                            }
                    }
                    // invariants
                    Check(w.ground.Count + w.carried.Count == made, $"things lost: {w.ground.Count} + {w.carried.Count} != {made} made");
                    Check(w.carried.Distinct().Count() == w.carried.Count, "a thing is carried twice");
                    Check(w.carried.All(c => !w.ground.Contains(c)), "a thing is both carried and on the ground");
                    int expectStage = RM_KethrelKernel.StageForLoad(w.thresholds, w.Load);
                    if (w.carried.Count == 0) Check(w.stage == 0 && w.hediff == 0f, "bare animal still wears a stage");
                    else Check(w.stage == expectStage, $"stage {w.stage} but load {w.Load} kg gives {expectStage}");
                    Check(w.stage == 0 || w.hediff == w.stage + 0.01f, $"hediff severity {w.hediff} vs stage {w.stage}");
                }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        private static List<string> Kethrel(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = GenK(r, 30 + r.Next(170)); Cases++;
                if (RunKethrel(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => RunKethrel(t, seed, false) != null);
                fails.Add($"kethrel seed {seed}: {RunKethrel(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            try { KethrelTables(); Cases++; } catch (Exception e) { fails.Add("kethrel tables: " + e.Message); }
            return fails;
        }

        private static void KethrelTables()
        {
            // Wanted: exhaustive over its eight inputs (the value ceiling as below / equal / above)
            for (int m = 0; m < 256; m++)
            {
                bool ok = (m & 1) != 0, item = (m & 2) != 0, forb = (m & 4) != 0, wl = (m & 8) != 0, take = (m & 16) != 0, home = (m & 32) != 0;
                float value = (m >> 6 & 3) == 0 ? 199f : (m >> 6 & 3) == 1 ? 200f : (m >> 6 & 3) == 2 ? 200.01f : 0f;
                bool got = RM_KethrelKernel.Wanted(ok, item, forb, wl, value, 200f, take, home);
                bool want = ok && item && !forb && wl && !(value > 200f) && (take || !home);
                Check(got == want, $"Wanted({m}) = {got}");
                if (home && !take) Check(!got, "took colony property with the setting off");
                if (forb) Check(!got, "took a forbidden item");
                Steps++;
            }
            Check(RM_KethrelKernel.IsTarName("RM_TarShallow") && RM_KethrelKernel.IsTarName("RM_Filth_TarCoating") && !RM_KethrelKernel.IsTarName("RM_Sand") && !RM_KethrelKernel.IsTarName(null) && !RM_KethrelKernel.IsTarName("tar"), "IsTarName (case-sensitive 'Tar')");
            // FailChance: bounded, rises with difficulty, falls with skill
            for (int s = 0; s <= 20; s++)
                for (float d = 0f; d <= 3.01f; d += 0.25f)
                {
                    float f = RM_KethrelKernel.FailChance(s, d);
                    Check(f >= 0.02f && f <= 0.9f, $"FailChance({s},{d}) = {f}");
                    Check(RM_KethrelKernel.FailChance(s + 1, d) <= f && RM_KethrelKernel.FailChance(s, d + 0.25f) >= f, "FailChance not monotone");
                    Steps++;
                }
            Check(Math.Abs(RM_KethrelKernel.FailChance(0, 1f) - 0.45f) < 1e-6f && Math.Abs(RM_KethrelKernel.FailChance(10, 1f) - 0.15f) < 1e-6f && RM_KethrelKernel.FailChance(20, 0.5f) == 0.02f && RM_KethrelKernel.FailChance(0, 3f) == 0.9f, "FailChance anchors");
            // stages: monotone in load, exact at each threshold, labels
            var th = new List<float> { 3f, 10f, 22f };
            Check(RM_KethrelKernel.StageForLoad(th, 2.99f) == 0 && RM_KethrelKernel.StageForLoad(th, 3f) == 1 && RM_KethrelKernel.StageForLoad(th, 10f) == 2 && RM_KethrelKernel.StageForLoad(th, 22f) == 3 && RM_KethrelKernel.StageForLoad(th, 999f) == 3 && RM_KethrelKernel.StageForLoad(new List<float>(), 50f) == 0, "stage thresholds");
            int prev = 0; for (float kg = 0f; kg < 40f; kg += 0.25f) { int s = RM_KethrelKernel.StageForLoad(th, kg); Check(s >= prev, "stage fell as load rose"); prev = s; }
            Check(RM_KethrelKernel.StageLabel(0) == "bare" && RM_KethrelKernel.StageLabel(1) == "light shell" && RM_KethrelKernel.StageLabel(2) == "heavy shell" && RM_KethrelKernel.StageLabel(3) == "full carapace" && RM_KethrelKernel.StageLabel(7) == "bare", "stage labels");
            Check(th.Last() < 30f, "the last stage must be reachable below the shipped molt load of 30 kg");
        }

        // ════════════════════════ vault ════════════════════════
        private enum VA { Arrive, Remove, Destroy, Scan, Extract, Solvent, Settings }
        private struct VAct
        {
            public VA kind; public int a, b;
            public override string ToString() { return kind + "(" + a + "," + b + ")"; }
        }

        private sealed class VItem { public int id; public int stack; public bool destroyed, rotOff, forbidden, present; }

        private static VAct[] GenV(Random r, int len)
        {
            var a = new VAct[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                VA kind = k < 25 ? VA.Arrive : k < 33 ? VA.Remove : k < 38 ? VA.Destroy : k < 62 ? VA.Scan : k < 82 ? VA.Extract : k < 92 ? VA.Solvent : VA.Settings;
                a[i] = new VAct { kind = kind, a = r.Next(1 << 12), b = r.Next(1 << 12) };
            }
            return a;
        }

        private static string RunVault(IList<VAct> acts, int seed, bool count)
        {
            var ledger = new RM_VaultLedger<VItem>();
            var items = new List<VItem>(); int nextId = 1, solvent = 0, ruinedMade = 0; var ruinedStacks = new List<int>();
            var specSealed = new HashSet<VItem>();           // independent: what the vault should have sealed as of the last scan
            int stepNo = 0, arrivedTotal = 0;
            try
            {
                foreach (VAct a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case VA.Arrive: { var it = new VItem { id = nextId++, stack = 1 + a.a % 40, present = true }; items.Add(it); arrivedTotal++; break; }
                        case VA.Remove: { var pool = items.Where(i => i.present && !i.destroyed).ToList(); if (pool.Count > 0) pool[a.a % pool.Count].present = false; break; }
                        case VA.Destroy: { var pool = items.Where(i => !i.destroyed).ToList(); if (pool.Count > 0) { var v = pool[a.a % pool.Count]; v.destroyed = true; v.present = false; } break; }
                        case VA.Solvent: solvent += 1 + a.a % 3; break;
                        case VA.Settings: break;
                        case VA.Scan:
                            {
                                var present = items.Where(i => i.present && !i.destroyed).ToList();
                                int sealCalls = 0, unsealCalls = 0;
                                ledger.Scan(present, t => t.destroyed, t => { t.rotOff = true; t.forbidden = true; sealCalls++; }, t => { t.rotOff = false; t.forbidden = false; unsealCalls++; });
                                if (count) { Seals += sealCalls; Unseals += unsealCalls; }
                                // spec: sealed = present and alive; whatever left and still exists was unsealed
                                var wantSealed = new HashSet<VItem>(present);
                                int wantSeal = present.Count(i => !specSealed.Contains(i));
                                int wantUnseal = specSealed.Count(i => !wantSealed.Contains(i) && !i.destroyed);
                                Check(sealCalls == wantSeal, $"sealed {sealCalls} fresh arrivals, spec says {wantSeal}");
                                Check(unsealCalls == wantUnseal, $"unsealed {unsealCalls} departures, spec says {wantUnseal}");
                                specSealed = wantSealed;
                                Check(ledger.sealedThings.Count == specSealed.Count && ledger.sealedThings.All(specSealed.Contains), "ledger differs from the spec after a scan");
                                Check(ledger.sealedThings.Distinct().Count() == ledger.sealedThings.Count, "a thing is tracked twice");
                                // a second scan right away changes nothing
                                int c2 = 0; ledger.Scan(present, t => t.destroyed, t => c2++, t => c2++);
                                Check(c2 == 0, "a scan with nothing new did work");
                                foreach (VItem it in items.Where(i => !i.destroyed))
                                    Check(it.rotOff == specSealed.Contains(it) && it.forbidden == it.rotOff, $"item {it.id}: rot-freeze {it.rotOff} but sealed={specSealed.Contains(it)}");
                                break;
                            }
                        case VA.Extract:
                            {
                                var pool = items.Where(i => !i.destroyed).ToList();
                                if (pool.Count == 0) break;
                                VItem t = pool[a.a % pool.Count];
                                bool wasSealed = ledger.IsSealed(t);
                                int solventBefore = solvent;
                                if (ledger.Plan(t, t.destroyed, false) == ExtractPlan.Ignore)
                                {
                                    Check(!wasSealed, "a sealed, live item was ignored");
                                    break;
                                }
                                Check(wasSealed, "extraction went ahead on an item the vault never sealed");
                                ExtractPlan plan = ledger.Plan(t, false, solvent > 0);
                                ledger.Forget(t);
                                if (plan == ExtractPlan.Clean)
                                {
                                    solvent--; t.rotOff = false; t.forbidden = false;
                                    if (count) Cleans++;
                                    Check(solvent == solventBefore - 1, "a clean extraction did not spend exactly one solvent");
                                    Check(solventBefore > 0, "a clean extraction without solvent");
                                }
                                else
                                {
                                    Check(plan == ExtractPlan.Ruined && solventBefore == 0, $"plan {plan} with {solventBefore} solvent");
                                    int stack = t.stack; t.rotOff = false; t.forbidden = false; t.destroyed = true; t.present = false;
                                    ruinedStacks.Add(RM_VaultLedger<VItem>.RuinedStack(stack)); ruinedMade++;
                                    if (count) Ruins++;
                                    Check(ruinedStacks.Last() == Math.Max(1, stack) && ruinedStacks.Last() >= 1, "ruined stack lost goods");
                                }
                                specSealed.Remove(t);
                                Check(!ledger.IsSealed(t), "the target is still sealed after extraction");
                                break;
                            }
                    }
                }
                Check(ruinedStacks.Count == ruinedMade, "ruined count");
                Check(items.Count == arrivedTotal, "items vanished from the bookkeeping");
                Check(RM_VaultLedger<VItem>.RuinedStack(0) == 1 && RM_VaultLedger<VItem>.RuinedStack(-5) == 1 && RM_VaultLedger<VItem>.RuinedStack(40) == 40, "RuinedStack floor");
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        private static List<string> Vault(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = GenV(r, 30 + r.Next(170)); Cases++;
                if (RunVault(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => RunVault(t, seed, false) != null);
                fails.Add($"vault seed {seed}: {RunVault(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            try
            {
                for (int m = 0; m < 4; m++) foreach (int iv in new[] { -1, 0, 1, 60 }) foreach (int t in new[] { 0, 59, 60, 120, 121 })
                {
                    bool got = RM_VaultLedger<object>.ScanDue(m != 0, iv, t);
                    bool want = m != 0 && iv > 0 && t % iv == 0;
                    Check(got == want, $"ScanDue({m != 0},{iv},{t}) = {got}");
                }
                Check(new RM_VaultLedger<object>().Plan(null, false, true) == ExtractPlan.Ignore, "a null target must be ignored");
                Cases++;
            }
            catch (Exception e) { fails.Add("vault tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ mere ════════════════════════
        private sealed class Grid : IMereGrid
        {
            public int W, H; public bool[,] blocked;
            public int Width { get { return W; } }
            public int Height { get { return H; } }
            public bool CanCarry(int x, int z)
            {
                if (x < 0 || z < 0 || x >= W || z >= H) return false;
                if (x == 0 || z == 0 || x == W - 1 || z == H - 1) return false;     // OnEdge
                return !blocked[x, z];
            }
        }

        private sealed class SysRng : IMereRng
        {
            public Random r; public long calls;
            public int Range(int a, int b) { calls++; return r.Next(a, b); }
        }

        private static List<string> Mere(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++; Steps++;
                try
                {
                    int w = r.Next(30, 130), h = r.Next(30, 130);
                    var g = new Grid { W = w, H = h, blocked = new bool[w, h] };
                    double density = r.Next(3) == 0 ? 0.0 : r.NextDouble() * 0.45;
                    for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) g.blocked[x, z] = r.NextDouble() < density;
                    if (r.Next(4) == 0) { int bx = r.Next(w); for (int z = 0; z < h; z++) g.blocked[bx, z] = true; }   // a river
                    // a seed
                    int sx = -1, sz = -1;
                    for (int t = 0; t < 300 && sx < 0; t++) { int x = r.Next(w), z = r.Next(h); if (RM_MereKernel.IsSeedCandidate(g, x, z)) { sx = x; sz = z; } }
                    if (sx < 0) continue;
                    Check(RM_MereKernel.EdgeDistance(sx, sz, w, h) >= 12 && g.CanCarry(sx, sz), "seed candidate on the edge band or blocked");
                    int target = r.Next(3) == 0 ? r.Next(1, 40) : r.Next(RM_MereKernel.MinMereCells, RM_MereKernel.MaxMereCells + 1);
                    var rng = new SysRng { r = new Random(seed * 31 + 7) };
                    HashSet<int> blob = RM_MereKernel.GrowBlob(g, sx, sz, rng, target, RM_MereKernel.MaxGrowAttempts);
                    int seedKey = RM_MereKernel.Key(sx, sz, w);
                    Check(blob.Contains(seedKey), "the blob lost its seed");
                    Check(blob.Count <= target || target < 1, $"blob {blob.Count} exceeds target {target}");
                    foreach (int k in blob) { Check(g.CanCarry(k % w, k / w), $"blob cell ({k % w},{k / w}) is not carriable"); }
                    // 4-connected from the seed
                    var seen = new HashSet<int> { seedKey }; var stack = new Stack<int>(); stack.Push(seedKey);
                    while (stack.Count > 0)
                    {
                        int k = stack.Pop(); int x = k % w, z = k / w;
                        foreach (var d in new[] { (0, 1), (1, 0), (0, -1), (-1, 0) })
                        {
                            int nk = RM_MereKernel.Key(x + d.Item1, z + d.Item2, w);
                            if (x + d.Item1 >= 0 && z + d.Item2 >= 0 && x + d.Item1 < w && z + d.Item2 < h && blob.Contains(nk) && seen.Add(nk)) stack.Push(nk);
                        }
                    }
                    Check(seen.Count == blob.Count, $"blob is not connected: {seen.Count} of {blob.Count} reachable from the seed");
                    // exhaustion: short of the target means no carriable cell touches the blob any more (or attempts ran out, which cannot happen below 2*target)
                    bool grewMore = false;
                    foreach (int k in blob)
                    {
                        int x = k % w, z = k / w;
                        foreach (var d in new[] { (0, 1), (1, 0), (0, -1), (-1, 0) })
                            if (g.CanCarry(x + d.Item1, z + d.Item2) && !blob.Contains(RM_MereKernel.Key(x + d.Item1, z + d.Item2, w))) grewMore = true;
                    }
                    if (blob.Count < target) { Check(!grewMore, $"stopped at {blob.Count} of {target} with room left to grow"); Exhausted++; }
                    else Check(blob.Count == target, $"overshot target {target} with {blob.Count}");
                    Check(rng.calls <= 3L * (blob.Count + 1) + 1000, $"used {rng.calls} random draws for {blob.Count} cells (the attempt cap is a safety net, not a working limit)");
                    Check(blob.Count <= RM_MereKernel.MaxGrowAttempts, "more cells than attempts");
                    // replay determinism
                    var again = RM_MereKernel.GrowBlob(g, sx, sz, new SysRng { r = new Random(seed * 31 + 7) }, target, RM_MereKernel.MaxGrowAttempts);
                    Check(again.SetEquals(blob), "same seed, different blob");
                    // rim
                    HashSet<int> rim = RM_MereKernel.RimOf(g, blob);
                    Check(!rim.Overlaps(blob), "rim overlaps the blob");
                    var wantRim = new HashSet<int>();
                    foreach (int k in blob) { int x = k % w, z = k / w; foreach (var d in new[] { (0, 1), (1, 0), (0, -1), (-1, 0) }) { int nx = x + d.Item1, nz = z + d.Item2; if (nx >= 0 && nz >= 0 && nx < w && nz < h && !blob.Contains(RM_MereKernel.Key(nx, nz, w))) wantRim.Add(RM_MereKernel.Key(nx, nz, w)); } }
                    Check(rim.SetEquals(wantRim), $"rim {rim.Count} cells vs brute force {wantRim.Count}");
                    if (RM_MereKernel.Acceptable(blob.Count)) Blobs++;
                    Check(RM_MereKernel.Acceptable(RM_MereKernel.MinMereCells) && !RM_MereKernel.Acceptable(RM_MereKernel.MinMereCells - 1), "acceptance threshold");
                }
                catch (Exception e) { fails.Add($"mere seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            // reservoir uniformity: on an open field the first growth step picks each of the four directions about equally
            try
            {
                var g = new Grid { W = 60, H = 60, blocked = new bool[60, 60] };
                var cnt = new int[4]; var rnd = new Random(99); int N = 40000;
                for (int k = 0; k < N; k++)
                {
                    HashSet<int> b = RM_MereKernel.GrowBlob(g, 30, 30, new SysRng { r = rnd }, 2, 100);
                    int other = b.First(x => x != RM_MereKernel.Key(30, 30, 60));
                    int dx = other % 60 - 30, dz = other / 60 - 30;
                    cnt[dz == 1 ? 0 : dx == 1 ? 1 : dz == -1 ? 2 : 3]++;
                    Steps++;
                }
                for (int d = 0; d < 4; d++) Check(Math.Abs(cnt[d] / (double)N - 0.25) < 0.02, $"direction {d} chosen {cnt[d] / (double)N:F3} of the time, not 0.25");
                // with exactly one eligible neighbour it is always chosen
                for (int x = 25; x <= 35; x++) for (int z = 25; z <= 35; z++) if (!(x == 30 && z == 30) && !(x == 30 && z == 31)) g.blocked[x, z] = true;
                HashSet<int> one = RM_MereKernel.GrowBlob(g, 30, 30, new SysRng { r = new Random(5) }, 2, 100);
                Check(one.Contains(RM_MereKernel.Key(30, 31, 60)) && one.Count == 2, "the single open neighbour was not taken");
                // no eligible neighbour at all: only the seed
                g.blocked[30, 31] = true;
                Check(RM_MereKernel.GrowBlob(g, 30, 30, new SysRng { r = new Random(5) }, 50, 100).Count == 1, "grew into a blocked cell");
                var open = new Grid { W = 100, H = 100, blocked = new bool[100, 100] };
                Check(RM_MereKernel.IsSeedCandidate(open, 12, 50) && !RM_MereKernel.IsSeedCandidate(open, 11, 50) && RM_MereKernel.IsSeedCandidate(open, 87, 50) && !RM_MereKernel.IsSeedCandidate(open, 88, 50) && RM_MereKernel.IsSeedCandidate(open, 50, 12) && !RM_MereKernel.IsSeedCandidate(open, 50, 88), "seed band edge (distance 12 is allowed, 11 is not)");
                open.blocked[50, 50] = true;
                Check(!RM_MereKernel.IsSeedCandidate(open, 50, 50), "a blocked cell was a seed candidate");
                Check(RM_MereKernel.EdgeDistance(5, 40, 100, 100) == 5 && RM_MereKernel.EdgeDistance(98, 50, 100, 100) == 1 && RM_MereKernel.EdgeDistance(50, 0, 100, 100) == 0 && RM_MereKernel.EdgeDistance(50, 99, 100, 100) == 0, "EdgeDistance");
                Cases++;
            }
            catch (Exception e) { fails.Add("mere uniformity: " + e.Message); }
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
                ("kethrel", () => Kethrel(N(5000), S(1))),
                ("vault", () => Vault(N(5000), S(1))),
                ("mere", () => Mere(N(600), S(1))),
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
            if (only == null || only == "kethrel") Console.WriteLine($"kethrel reached: pickups {Picks}, molts {Molts}, seeks {Seeks}");
            if (only == null || only == "vault") Console.WriteLine($"vault reached: seals {Seals}, unseals {Unseals}, clean extractions {Cleans}, ruined {Ruins}");
            if (only == null || only == "mere") Console.WriteLine($"mere reached: acceptable meres {Blobs}, exhausted before target {Exhausted}");
            if (!oneSeed.HasValue && scale >= 1)
            {
                if ((only == null || only == "kethrel") && (Picks == 0 || Molts == 0 || Seeks == 0)) { Console.WriteLine("FAIL kethrel fuzz never reached pickup / molt / seek (blind)"); ok = false; }
                if ((only == null || only == "vault") && (Seals == 0 || Unseals == 0 || Cleans == 0 || Ruins == 0)) { Console.WriteLine("FAIL vault fuzz never reached a seal / unseal / clean / ruined path (blind)"); ok = false; }
                if ((only == null || only == "mere") && (Blobs == 0 || Exhausted == 0)) { Console.WriteLine("FAIL mere fuzz never made a mere or never ran out of room (blind)"); ok = false; }
            }
            Console.WriteLine($"sump fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
