// Approach B for Watchers: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_WatcherKernel.cs):
//   step    the watch job simulated tick by tick against random worlds (creatures drifting in and out of the flinch circle, geophone pings,
//           hunt orders, hunger, losing the medium): sign iff hidden, a hunt order never survives a peek, a hungry hidden watcher emerges and
//           ends the same step, a quiet watcher always finishes, hiding lasts at least its roll; plus every StepIn combination against a
//           truth table written as nested predicates
//   scan    nearest-creature scan against brute force (ties, the watch edge, the flinch edge, radius metamorphics)
//   gates   every think-tree gate (watch giver, seek-medium backstop, flush hunt mark) exhaustively against an independent restatement,
//           plus the cross-gate property that the giver never starts a watch that the first step would end for hunger
//   config  RM_WatcherExtension.ConfigErrors against a restatement, the shipped piinnok values accepted, each single break reported
// A failing case prints `family seed N: message`; --fuzz-seed N replays it. PROVISIONAL numbers (watch 14, flinch 6, hide 2500~7500, boltTicks
// 1200, wander 0.1) are design-draft tuning; the properties hold for any valid values.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.Watchers;

namespace RimMandrake.Watchers.SelfTest
{
    internal static class WatcherFuzz
    {
        public static long Cases, Steps, Hides, Emerges, HungryEmerges, Succeeded, Interrupted, HuntSinks, SignRestores;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float F(Random r, float lo, float hi) { return lo + (float)r.NextDouble() * (hi - lo); }

        // ---------------------------------------------------------------- step
        private static StepFlags SpecStep(StepIn s)
        {
            // nested-predicate restatement of the ruled behaviour
            if (!(s.watchersEnabled && s.onMedium)) return StepFlags.EndInterrupted;
            bool flinched = s.hideAndFlinch && (s.inFlinch || s.geophone || s.hunted);
            if (!s.hidden)
            {
                if (flinched) return StepFlags.Hide | (s.hunted ? StepFlags.DropHunt : 0);
                StepFlags f = 0;
                if (s.turnToFace && s.hasNearest) f |= StepFlags.Face;
                if (s.now - s.watchStart >= s.maxWatchTicks) f |= StepFlags.EndSucceeded;
                return f;
            }
            StepFlags g = s.signMissing ? StepFlags.RestoreSign : 0;
            bool calm = s.now >= s.hiddenUntil && !s.inFlinch && !s.geophone;
            if (s.hungry || !s.hideAndFlinch || calm)
            {
                g |= StepFlags.Emerge | StepFlags.ResetWatchClock;
                if (s.hungry) g |= StepFlags.EndSucceeded;
            }
            return g;
        }

        private static List<string> Step(int cases, int seed0)
        {
            var fails = new List<string>();
            // exhaustive truth table first (all booleans x the time relations)
            try
            {
                for (int m = 0; m < (1 << 11); m++)
                    for (int tc = 0; tc < 4; tc++)
                    {
                        var s = new StepIn
                        {
                            watchersEnabled = (m & 1) != 0, onMedium = (m & 2) != 0, hidden = (m & 4) != 0, hideAndFlinch = (m & 8) != 0,
                            turnToFace = (m & 16) != 0, hasNearest = (m & 32) != 0, inFlinch = (m & 64) != 0, geophone = (m & 128) != 0,
                            hunted = (m & 256) != 0, signMissing = (m & 512) != 0, hungry = (m & 1024) != 0,
                            now = 10000, hiddenUntil = tc == 0 ? 9999 : tc == 1 ? 10000 : 10001, watchStart = tc == 3 ? 10000 - 2500 : 10000 - 2499, maxWatchTicks = 2500,
                        };
                        Cases++; Steps++;
                        StepFlags got = RM_WatcherKernel.DecideStep(s), want = SpecStep(s);
                        Check(got == want, $"DecideStep({Describe(s)}) = {got}, spec {want}");
                    }
            }
            catch (Exception e) { fails.Add("step table: " + e.Message); }

            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    bool enabled = r.Next(12) != 0, hideAndFlinch = r.Next(8) != 0, turn = r.Next(4) != 0;
                    int maxWatch = 600 + r.Next(3000); float scale = F(r, 0.25f, 3f);
                    int hideMin = 300 + r.Next(2500), hideMax = hideMin + r.Next(5000);
                    int now = 100000 + r.Next(50000);
                    bool hidden = false, signThere = false, hunted = false; int hiddenUntil = -1, watchStart = now;
                    int hiddenSince = -1, rolled = 0; bool ended = false;
                    double hunger = F(r, 0f, 1f); float below = F(r, 0.1f, 0.5f);
                    // the world: a creature that wanders in and out of the flinch circle
                    double nearDist = F(r, 0f, 30f); bool geoPending = false; int quietFor = 0;
                    for (int t = 0; t < 400 && !ended; t++)
                    {
                        Steps++; now += RM_WatcherKernel.StepInterval;
                        nearDist = Math.Max(0, nearDist + F(r, -3f, 3f));
                        bool hasNearest = nearDist <= 14.0; bool inFlinch = nearDist <= 6.0;
                        geoPending = r.Next(40) == 0;
                        if (!hidden && r.Next(60) == 0) { hunted = true; }
                        hunger = Math.Max(0, Math.Min(1, hunger + F(r, -0.02f, 0.012f)));
                        bool hungry = hunger < below;
                        bool onMedium = r.Next(300) != 0 || t == 0;
                        bool signMissing = hidden && (!signThere);
                        if (hidden && r.Next(50) == 0) signThere = false;   // a building placed over the sign
                        signMissing = hidden && !signThere;
                        var s = new StepIn
                        {
                            watchersEnabled = enabled, onMedium = onMedium, hidden = hidden, hideAndFlinch = hideAndFlinch, turnToFace = turn,
                            hasNearest = hasNearest, inFlinch = inFlinch, geophone = geoPending, hunted = hunted && !hidden, signMissing = signMissing, hungry = hungry,
                            now = now, hiddenUntil = hiddenUntil, watchStart = watchStart, maxWatchTicks = maxWatch,
                        };
                        StepFlags f = RM_WatcherKernel.DecideStep(s);
                        Check(!((f & StepFlags.Hide) != 0 && hidden), "Hide while already hidden");
                        Check(!((f & StepFlags.Emerge) != 0 && !hidden), "Emerge while not hidden");
                        Check(!((f & StepFlags.Face) != 0 && (hidden || !turn || !hasNearest)), "Face while hidden / setting off / nothing to face");
                        Check(!((f & StepFlags.Hide) != 0 && (f & (StepFlags.EndInterrupted | StepFlags.EndSucceeded)) != 0), "Hide and End in one step");
                        Check(!((f & StepFlags.EndInterrupted) != 0 && f != StepFlags.EndInterrupted), "EndInterrupted combined with other flags");
                        if ((f & StepFlags.EndInterrupted) != 0)
                        {
                            Check(!enabled || !onMedium, "interrupted although enabled and on its medium");
                            Interrupted++; ended = true; break;     // the finish action emerges it (RM_WatcherUtility.Emerge)
                        }
                        if ((f & StepFlags.Hide) != 0)
                        {
                            Check(hideAndFlinch && (inFlinch || geoPending || (hunted && !hidden)), "hid without a reason");
                            hidden = true; signThere = true; hiddenSince = now; rolled = hideMin + r.Next(hideMax - hideMin + 1);
                            hiddenUntil = RM_WatcherKernel.HiddenUntil(now, rolled, scale); Hides++;
                            if ((f & StepFlags.DropHunt) != 0) { hunted = false; HuntSinks++; }
                            else Check(!hunted, "peeked while hunted but the hunt order was not dropped");
                            continue;
                        }
                        Check(!(hunted && !hidden && hideAndFlinch), "a visible watcher is hunted although the peek rule should have hidden it");
                        if ((f & StepFlags.RestoreSign) != 0) { signThere = true; SignRestores++; }
                        if ((f & StepFlags.Emerge) != 0)
                        {
                            Check(hidden, "emerge from nothing");
                            bool early = now < hiddenUntil;
                            if (early) Check(hungry || !hideAndFlinch, $"emerged {hiddenUntil - now} ticks early without hunger or the setting off");
                            Check(!(inFlinch && hideAndFlinch && !hungry), "emerged while a creature stood in the flinch circle");
                            Check(!(geoPending && hideAndFlinch && !hungry), "emerged while the geophone was pinging");
                            hidden = false; signThere = false; watchStart = now; Emerges++;
                            if (hungry) { Check((f & StepFlags.EndSucceeded) != 0, "hungry emerge did not end the job (hide/emerge loop)"); HungryEmerges++; }
                        }
                        else if (hidden)
                        {
                            Check(signThere || (f & StepFlags.RestoreSign) != 0, "hidden watcher left with no sign");
                        }
                        Check(!hidden || signThere, "sign missing while hidden after the step");
                        if (!hidden) Check(!signThere, "sign left standing on a visible watcher");
                        if ((f & StepFlags.EndSucceeded) != 0) { Succeeded++; ended = true; }
                        quietFor++;
                    }
                    // liveness: a world with no creature and no geophone ends the job within maxWatch + one step (setting on or off)
                    {
                        bool done = false; int tt = 0; int ws = 5000; int n2 = 5000; bool en = true;
                        for (; tt < 200 && !done; tt++)
                        {
                            n2 += RM_WatcherKernel.StepInterval;
                            StepFlags f = RM_WatcherKernel.DecideStep(new StepIn { watchersEnabled = en, onMedium = true, hidden = false, hideAndFlinch = hideAndFlinch, turnToFace = turn, now = n2, watchStart = ws, maxWatchTicks = maxWatch });
                            if ((f & StepFlags.EndSucceeded) != 0) done = true;
                        }
                        Check(done, $"a quiet watcher never finished (maxWatch {maxWatch})");
                        Check(n2 - ws <= maxWatch + RM_WatcherKernel.StepInterval, "a quiet watcher overran its watch time");
                    }
                    // a hidden watcher in a calm world comes up no earlier than its roll and no later than one step after
                    {
                        int h0 = 20000; int until = RM_WatcherKernel.HiddenUntil(h0, hideMin, scale); int n3 = h0; bool up = false;
                        for (int tt = 0; tt < 4000 && !up; tt++)
                        {
                            n3 += RM_WatcherKernel.StepInterval;
                            StepFlags f = RM_WatcherKernel.DecideStep(new StepIn { watchersEnabled = true, onMedium = true, hidden = true, hideAndFlinch = true, turnToFace = true, now = n3, hiddenUntil = until, watchStart = h0, maxWatchTicks = maxWatch });
                            if ((f & StepFlags.Emerge) != 0) { up = true; Check(n3 >= until, "emerged before its hide time"); Check(n3 - until < RM_WatcherKernel.StepInterval + 1, "emerged long after its hide time"); }
                        }
                        Check(up, "a calm hidden watcher never came back up");
                    }
                }
                catch (Exception e) { fails.Add($"step seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static string Describe(StepIn s)
        {
            return $"en={s.watchersEnabled} med={s.onMedium} hid={s.hidden} hf={s.hideAndFlinch} face={s.turnToFace} near={s.hasNearest} flinch={s.inFlinch} geo={s.geophone} hunted={s.hunted} nosign={s.signMissing} hungry={s.hungry} until={s.hiddenUntil} start={s.watchStart}";
        }

        // ---------------------------------------------------------------- scan
        private static List<string> Scan(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    float watch = F(r, 2f, 30f), flinch = F(r, 0.5f, watch * 2f);   // the flinch slider can push the flinch circle past the watch circle
                    int n = r.Next(0, 12);
                    var d = new List<float>();
                    for (int i = 0; i < n; i++)
                    {
                        int k = r.Next(8);
                        float v = k == 0 ? watch * watch : k == 1 ? flinch * flinch : k == 2 && d.Count > 0 ? d[r.Next(d.Count)] : k == 3 ? 0f : F(r, 0f, watch * watch * 2f);
                        d.Add(v);
                    }
                    Steps++;
                    bool inF; int got = RM_WatcherKernel.Nearest(d, watch, flinch, out inF);
                    // brute force
                    float ws = watch * watch, fs = flinch * flinch; int want = -1; float best = float.MaxValue; bool wantF = false;
                    for (int i = 0; i < d.Count; i++) { if (d[i] > ws) continue; if (d[i] <= fs) wantF = true; if (d[i] < best) { best = d[i]; want = i; } }
                    Check(got == want, $"Nearest index {got}, brute force {want} ({string.Join(",", d)} watch {watch})");
                    Check(inF == wantF, $"inFlinch {inF}, brute force {wantF}");
                    if (got >= 0) { Check(d[got] <= ws, "nearest outside the watch radius"); for (int i = 0; i < got; i++) Check(!(d[i] <= ws) || d[i] > d[got], "an earlier equal/nearer creature was skipped (first of equals wins)"); }
                    else Check(!inF, "inFlinch with nobody in range");
                    // metamorphic: a larger flinch circle never un-flinches; a larger watch circle never loses the nearest's presence
                    bool inF2; RM_WatcherKernel.Nearest(d, watch, flinch * 1.5f, out inF2);
                    Check(!inF || inF2, "growing the flinch circle un-flinched");
                    bool inF3; int g3 = RM_WatcherKernel.Nearest(d, watch * 1.5f, flinch, out inF3);
                    Check(!(got >= 0) || g3 >= 0, "growing the watch radius lost the nearest");
                    Check(!inF || inF3, "growing the watch radius un-flinched");
                    // a creature dropped exactly inside the flinch circle always flinches
                    var d2 = new List<float>(d) { Math.Min(fs, ws) * 0.5f }; bool inF4; RM_WatcherKernel.Nearest(d2, watch, flinch, out inF4);
                    Check(inF4, "a creature inside the flinch circle did not flinch");
                    Check(Math.Abs(RM_WatcherKernel.FlinchRadius(6f, 2f) - 12f) < 1e-6f && RM_WatcherKernel.FlinchRadius(6f, 0.5f) == 3f, "FlinchRadius is not radius x scale");
                }
                catch (Exception e) { fails.Add($"scan seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        // ---------------------------------------------------------------- gates
        private static List<string> Gates()
        {
            var fails = new List<string>();
            try
            {
                // watch giver: exhaustive over 11 booleans x food relation x active relation
                for (int m = 0; m < (1 << 11); m++)
                    foreach (int foodRel in new[] { 0, 1, 2 })       // below, equal, above the emerge threshold
                        foreach (int actRel in new[] { 0, 1, 2 })    // below, equal, above the cap
                        {
                            bool hasExt = (m & 1) != 0, en = (m & 2) != 0, spawned = (m & 4) != 0, downed = (m & 8) != 0, mental = (m & 16) != 0,
                                 hasMap = (m & 32) != 0, hasComp = (m & 64) != 0, bolting = (m & 128) != 0, onMed = (m & 256) != 0, hf = (m & 512) != 0, turn = (m & 1024) != 0;
                            foreach (bool hasFood in new[] { false, true })
                                foreach (bool roll in new[] { false, true })
                                {
                                    float thr = 0.25f, food = foodRel == 0 ? 0.1f : foodRel == 1 ? 0.25f : 0.9f;
                                    int cap = 40, act = actRel == 0 ? 10 : actRel == 1 ? 40 : 90;
                                    Cases++; Steps++;
                                    bool got = RM_WatcherKernel.WatchGiverAllows(hasExt, en, spawned, downed, mental, hasMap, hasComp, bolting, onMed, hf, turn, hasFood, food, thr, roll, act, cap);
                                    bool want = hasExt && en && spawned && !downed && !mental && hasMap && hasComp && !bolting && onMed && (hf || turn)
                                        && !(hasFood && food < thr) && !roll && act < cap;
                                    Check(got == want, $"WatchGiverAllows mismatch (mask {m}, food {foodRel}, active {actRel}, hasFood {hasFood}, roll {roll}): got {got}, spec {want}");
                                    // cross-gate: the giver never starts a watch whose first hidden step would end for hunger
                                    if (got && hasFood) Check(!(food < thr), "giver started a watch for a pawn below the emerge threshold");
                                    Check(RM_WatcherKernel.WatchGiverPre(hasExt, en, spawned, downed, mental, hasMap, hasComp, bolting, onMed, hf, turn, hasFood, food, thr)
                                        == (hasExt && en && spawned && !downed && !mental && hasMap && hasComp && !bolting && onMed && (hf || turn) && !(hasFood && food < thr)), "Pre disagrees with the spec");
                                    Check(got == (RM_WatcherKernel.WatchGiverPre(hasExt, en, spawned, downed, mental, hasMap, hasComp, bolting, onMed, hf, turn, hasFood, food, thr)
                                        && RM_WatcherKernel.WatchGiverCapOk(roll, act, cap)), "Allows is not Pre && CapOk");
                                }
                        }
                // seek-medium backstop
                for (int m = 0; m < (1 << 10); m++)
                {
                    bool en = (m & 1) != 0, stay = (m & 2) != 0, hasMed = (m & 4) != 0, downed = (m & 8) != 0, mental = (m & 16) != 0, bolting = (m & 32) != 0,
                         noMed = (m & 64) != 0, onMed = (m & 128) != 0, hasJob = (m & 256) != 0, idle = (m & 512) != 0;
                    Cases++; Steps++;
                    bool got = RM_WatcherKernel.ShouldSeekMedium(en, stay, hasMed, downed, mental, bolting, noMed, onMed, hasJob, idle);
                    bool want = en && stay && hasMed && !downed && !mental && !bolting && !noMed && !onMed && (!hasJob || idle);
                    Check(got == want, $"ShouldSeekMedium mask {m}: got {got}, spec {want}");
                    if (bolting) Check(!got, "a bolting watcher was sent back to its medium mid-flight");
                    if (hasJob && !idle) Check(!got, "the backstop interrupted a non-idle job");
                }
                // flush hunt mark
                for (int m = 0; m < 32; m++)
                {
                    bool set = (m & 1) != 0, player = (m & 2) != 0, hasFac = (m & 4) != 0, human = (m & 8) != 0, marked = (m & 16) != 0;
                    Cases++; Steps++;
                    bool got = RM_WatcherKernel.FlushMarksHunt(set, player, hasFac, human, marked);
                    Check(got == (set && player && (!hasFac || !human) && !marked), $"FlushMarksHunt mask {m}");
                    if (hasFac && human) Check(!got, "a humanlike-faction animal was marked for hunting");
                    if (marked) Check(!got, "marked twice");
                }
                // hide duration
                for (int i = 0; i < 2000; i++)
                {
                    var r = new Random(i); int now = r.Next(1000000), rolled = 1 + r.Next(10000); float sc = F(r, 0.25f, 3f);
                    int u = RM_WatcherKernel.HiddenUntil(now, rolled, sc);
                    Cases++; Steps++;
                    Check(u > now, "hidden until a moment already past");
                    Check(u == now + (int)(rolled * sc), "HiddenUntil is not now + roll x scale");
                    Check(RM_WatcherKernel.HiddenUntil(now, rolled, sc * 1.5f) >= u, "a longer emerge-delay slider shortened the hide");
                }
            }
            catch (Exception e) { fails.Add("gates: " + e.Message); }
            return fails;
        }

        // ---------------------------------------------------------------- config
        private static List<string> Config(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++; Steps++;
                try
                {
                    // the shipped piinnok must be sound
                    Check(RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 2500, 7500, 2500, 1200, 0.1f, 0.25f, 2.5f).Count == 0, "the shipped piinnok values are rejected");
                    bool hh = r.Next(8) != 0, sd = r.Next(8) != 0, sc = r.Next(8) != 0;
                    float fl = F(r, -2f, 20f), wr = F(r, -2f, 30f), wc = F(r, -0.5f, 1.5f), em = F(r, -0.5f, 1.5f), geo = F(r, -1f, 5f);
                    int hmin = r.Next(-100, 8000), hmax = hmin + r.Next(-500, 8000), mw = r.Next(-100, 5000), bt = r.Next(-100, 3000);
                    var got = RM_WatcherKernel.ConfigErrors(hh, sd, sc, fl, wr, hmin, hmax, mw, bt, wc, em, geo);
                    int want = 0;
                    if (!hh) want++;
                    if (!sd) want++; else if (!sc) want++;
                    if (fl <= 0f || wr < fl) want++;
                    if (hmin <= 0 || hmax < hmin) want++;
                    if (mw <= 0 || bt <= 0) want++;
                    if (wc < 0f || wc > 1f) want++;
                    if (em < 0f || em > 1f) want++;
                    if (geo < 0f) want++;
                    Check(got.Count == want, $"ConfigErrors reported {got.Count} for a def that has {want} faults: {string.Join(" | ", got)}");
                    // each single break of the good def is reported exactly once
                    var good = new object[] { true, true, true, 6f, 14f, 2500, 7500, 2500, 1200, 0.1f, 0.25f, 2.5f };
                    var breaks = new (string name, Func<List<string>> run)[]
                    {
                        ("no hediff", () => RM_WatcherKernel.ConfigErrors(false, true, true, 6f, 14f, 2500, 7500, 2500, 1200, 0.1f, 0.25f, 2.5f)),
                        ("no sign", () => RM_WatcherKernel.ConfigErrors(true, false, false, 6f, 14f, 2500, 7500, 2500, 1200, 0.1f, 0.25f, 2.5f)),
                        ("wrong sign class", () => RM_WatcherKernel.ConfigErrors(true, true, false, 6f, 14f, 2500, 7500, 2500, 1200, 0.1f, 0.25f, 2.5f)),
                        ("flinch beyond watch", () => RM_WatcherKernel.ConfigErrors(true, true, true, 15f, 14f, 2500, 7500, 2500, 1200, 0.1f, 0.25f, 2.5f)),
                        ("flinch zero", () => RM_WatcherKernel.ConfigErrors(true, true, true, 0f, 14f, 2500, 7500, 2500, 1200, 0.1f, 0.25f, 2.5f)),
                        ("hide range reversed", () => RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 7500, 2500, 2500, 1200, 0.1f, 0.25f, 2.5f)),
                        ("hide min zero", () => RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 0, 7500, 2500, 1200, 0.1f, 0.25f, 2.5f)),
                        ("no watch time", () => RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 2500, 7500, 0, 1200, 0.1f, 0.25f, 2.5f)),
                        ("no bolt time", () => RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 2500, 7500, 2500, 0, 0.1f, 0.25f, 2.5f)),
                        ("wander above 1", () => RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 2500, 7500, 2500, 1200, 1.2f, 0.25f, 2.5f)),
                        ("wander negative", () => RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 2500, 7500, 2500, 1200, -0.1f, 0.25f, 2.5f)),
                        ("emerge threshold above 1", () => RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 2500, 7500, 2500, 1200, 0.1f, 1.5f, 2.5f)),
                        ("geophone negative", () => RM_WatcherKernel.ConfigErrors(true, true, true, 6f, 14f, 2500, 7500, 2500, 1200, 0.1f, 0.25f, -1f)),
                    };
                    foreach (var b in breaks) Check(b.run().Count == 1, $"single break '{b.name}' reported {b.run().Count} errors");
                    // edges that must stay valid
                    Check(RM_WatcherKernel.ConfigErrors(true, true, true, 14f, 14f, 1, 1, 1, 1, 0f, 0f, 0f).Count == 0, "boundary values rejected");
                    Check(RM_WatcherKernel.ConfigErrors(true, true, true, 14f, 14f, 1, 1, 1, 1, 1f, 1f, 0f).Count == 0, "boundary values (1.0) rejected");
                }
                catch (Exception e) { fails.Add($"config seed {seed}: {e.Message}"); }
            }
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
                ("step", () => Step(N(3000), S(1))),
                ("scan", () => Scan(N(4000), S(1))),
                ("gates", () => Gates()),
                ("config", () => Config(N(3000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails.Take(8)) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"step reached: hides {Hides}, emerges {Emerges} (hungry {HungryEmerges}), finished {Succeeded}, interrupted {Interrupted}, hunt orders dropped {HuntSinks}, signs restored {SignRestores}");
                if (Hides == 0 || Emerges == 0 || HungryEmerges == 0 || Succeeded == 0 || Interrupted == 0 || HuntSinks == 0 || SignRestores == 0) { Console.WriteLine("FAIL watcher fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"watchers fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
