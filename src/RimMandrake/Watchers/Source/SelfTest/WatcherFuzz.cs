// Approach B for Watchers: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_WatcherKernel.cs):
//   step    the watch job simulated tick by tick against random worlds (creatures drifting in and out of the flinch circle, geophone pings,
//           hunt orders, neighbour alarms, hunger, losing the medium): sign iff hidden, a hunt order never sends it under and never survives
//           a step that leaves it hidden, a hungry hidden watcher emerges and ends the same step, a quiet watcher always finishes, hiding lasts
//           at least its roll, only a body or the geophone raises an alarm; plus every StepIn combination against a nested-predicate table
//   scan    nearest-creature scan against brute force (ties, the watch edge, the flinch edge, radius metamorphics)
//   gates   every think-tree gate (watch giver, seek-medium backstop) exhaustively against an independent restatement,
//           plus the cross-gate property that the giver never starts a watch that the first step would end for hunger
//   config  RM_WatcherExtension.ConfigErrors against a restatement, the shipped piinnok values accepted, each single break reported
//   death   the fragility rule (150 x baseHealthScale against maxLethalDamage) and the sign validity rule (orphan / duplicate repair)
//   alarm   the bounded ripple simulated on random fields of watchers: never more than maxCount reached, never past maxHops or the origin
//           distance or the hop radius, never after maxAge, never the same watcher twice, always terminates, and reaches someone when it can
// A failing case prints `family seed N: message`; --fuzz-seed N replays it. PROVISIONAL numbers (watch 14, flinch 6, hide 2500~7500,
// wander 0.1, the alarm limits) are design-draft tuning; the properties hold for any valid values.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.Watchers;

namespace RimMandrake.Watchers.SelfTest
{
    internal static class WatcherFuzz
    {
        public static long CueHides, CueFires;
        public static long Cases, Steps, Hides, Emerges, HungryEmerges, Succeeded, Interrupted, HuntSinks, SignRestores, AlarmHides, AlarmRaises;
        public static long RipplesRun, RippleReaches, RipplesCapped, SignVerdicts;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float F(Random r, float lo, float hi) { return lo + (float)r.NextDouble() * (hi - lo); }

        // ---------------------------------------------------------------- step
        private static StepFlags SpecStep(StepIn s)
        {
            // nested-predicate restatement of the ruled behaviour
            if (!(s.watchersEnabled && s.onMedium)) return StepFlags.EndInterrupted;
            bool flinched = s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue || s.alarmed);
            if (!s.hidden)
            {
                if (flinched) return StepFlags.Hide | (s.huntMarked ? StepFlags.DropHunt : 0) | (s.inFlinch || s.geophone ? StepFlags.RaiseAlarm : 0);
                StepFlags f = 0;
                if (s.turnToFace && s.hasNearest) f |= StepFlags.Face;
                if (s.now - s.watchStart >= s.maxWatchTicks) f |= StepFlags.EndSucceeded;
                return f;
            }
            StepFlags g = s.signMissing ? StepFlags.RestoreSign : 0;
            bool calm = s.now >= s.hiddenUntil && !s.inFlinch && !s.geophone && !s.cue && !s.alarmed;
            bool up = s.hungry || !s.hideAndFlinch || calm;
            if (up)
            {
                g |= StepFlags.Emerge | StepFlags.ResetWatchClock;
                if (s.hungry) g |= StepFlags.EndSucceeded;
            }
            if (!up && s.huntMarked) g |= StepFlags.DropHunt;   // stays under: nothing may keep aiming at it
            return g;
        }

        private static List<string> Step(int cases, int seed0)
        {
            var fails = new List<string>();
            // exhaustive truth table first (all booleans x the time relations)
            try
            {
                for (int m = 0; m < (1 << 13); m++)
                    for (int tc = 0; tc < 4; tc++)
                    {
                        var s = new StepIn
                        {
                            watchersEnabled = (m & 1) != 0, onMedium = (m & 2) != 0, hidden = (m & 4) != 0, hideAndFlinch = (m & 8) != 0,
                            turnToFace = (m & 16) != 0, hasNearest = (m & 32) != 0, inFlinch = (m & 64) != 0, geophone = (m & 128) != 0,
                            huntMarked = (m & 256) != 0, signMissing = (m & 512) != 0, hungry = (m & 1024) != 0, cue = (m & 2048) != 0,
                            alarmed = (m & 4096) != 0,
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
                    double nearDist = F(r, 0f, 30f); bool geoPending = false; int quietFor = 0; int cueRun = 0; int alarmRun = 0;
                    for (int t = 0; t < 400 && !ended; t++)
                    {
                        Steps++; now += RM_WatcherKernel.StepInterval;
                        nearDist = Math.Max(0, nearDist + F(r, -3f, 3f));
                        bool hasNearest = nearDist <= 14.0; bool inFlinch = nearDist <= 6.0;
                        geoPending = r.Next(40) == 0;
                        bool cuePending = cueRun > 0 ? (--cueRun > 0) : (r.Next(120) == 0 && (cueRun = 1 + r.Next(40)) > 0);   // a cue that holds for a while (sun, a fire)
                        bool alarmPending = alarmRun > 0 ? (--alarmRun > 0) : (r.Next(90) == 0 && (alarmRun = 1 + r.Next(10)) > 0);   // a neighbour's alarm hold
                        if (r.Next(hidden ? 400 : 60) == 0) { hunted = true; }   // the player marks a visible one; rarely a mark lands on a hidden one (another mod)
                        hunger = Math.Max(0, Math.Min(1, hunger + F(r, -0.02f, 0.012f)));
                        bool hungry = hunger < below;
                        bool onMedium = r.Next(300) != 0 || t == 0;
                        bool signMissing = hidden && (!signThere);
                        if (hidden && r.Next(50) == 0) signThere = false;   // a building placed over the sign
                        signMissing = hidden && !signThere;
                        var s = new StepIn
                        {
                            watchersEnabled = enabled, onMedium = onMedium, hidden = hidden, hideAndFlinch = hideAndFlinch, turnToFace = turn,
                            hasNearest = hasNearest, inFlinch = inFlinch, geophone = geoPending, cue = cuePending, alarmed = alarmPending, huntMarked = hunted, signMissing = signMissing, hungry = hungry,
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
                        Check(!((f & StepFlags.RaiseAlarm) != 0 && (f & StepFlags.Hide) == 0), "RaiseAlarm without a hide");
                        Check(!((f & StepFlags.DropHunt) != 0 && !hunted), "dropped a hunt order that was not there");
                        if ((f & StepFlags.Hide) != 0)
                        {
                            Check(hideAndFlinch && (inFlinch || geoPending || cuePending || alarmPending), "hid without a reason (a hunt order is not one)");
                            Check(((f & StepFlags.RaiseAlarm) != 0) == (inFlinch || geoPending), "an alarm raised by a cue/alarm, or a body/geophone hide that raised none");
                            if ((f & StepFlags.RaiseAlarm) != 0) AlarmRaises++;
                            if (cuePending && !inFlinch && !geoPending && !alarmPending) CueHides++;
                            if (alarmPending && !inFlinch && !geoPending && !cuePending) AlarmHides++;
                            hidden = true; signThere = true; hiddenSince = now; rolled = hideMin + r.Next(hideMax - hideMin + 1);
                            hiddenUntil = RM_WatcherKernel.HiddenUntil(now, rolled, scale); Hides++;
                            if ((f & StepFlags.DropHunt) != 0) { hunted = false; HuntSinks++; }
                            Check(!hunted, "went under with a hunt order still on it (a hidden watcher must not be targetable)");
                            continue;
                        }
                        if ((f & StepFlags.DropHunt) != 0) { hunted = false; HuntSinks++; }
                        if ((f & StepFlags.RestoreSign) != 0) { signThere = true; SignRestores++; }
                        if ((f & StepFlags.Emerge) != 0)
                        {
                            Check(hidden, "emerge from nothing");
                            bool early = now < hiddenUntil;
                            if (early) Check(hungry || !hideAndFlinch, $"emerged {hiddenUntil - now} ticks early without hunger or the setting off");
                            Check(!(inFlinch && hideAndFlinch && !hungry), "emerged while a creature stood in the flinch circle");
                            Check(!(geoPending && hideAndFlinch && !hungry), "emerged while the geophone was pinging");
                            Check(!(cuePending && hideAndFlinch && !hungry), "emerged while a cue still held");
                            Check(!(alarmPending && hideAndFlinch && !hungry), "emerged while a neighbour's alarm still held");
                            hidden = false; signThere = false; watchStart = now; Emerges++;
                            if (hungry) { Check((f & StepFlags.EndSucceeded) != 0, "hungry emerge did not end the job (hide/emerge loop)"); HungryEmerges++; }
                        }
                        else if (hidden)
                        {
                            Check(signThere || (f & StepFlags.RestoreSign) != 0, "hidden watcher left with no sign");
                        }
                        Check(!hidden || signThere, "sign missing while hidden after the step");
                        Check(!(hidden && hunted), "a hunt order survived a step that left it hidden");
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
            return $"en={s.watchersEnabled} med={s.onMedium} hid={s.hidden} hf={s.hideAndFlinch} face={s.turnToFace} near={s.hasNearest} flinch={s.inFlinch} geo={s.geophone} cue={s.cue} alarm={s.alarmed} hunt={s.huntMarked} nosign={s.signMissing} hungry={s.hungry} until={s.hiddenUntil} start={s.watchStart}";
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
                // watch giver: exhaustive over 10 booleans x food relation x active relation
                for (int m = 0; m < (1 << 10); m++)
                    foreach (int foodRel in new[] { 0, 1, 2 })       // below, equal, above the emerge threshold
                        foreach (int actRel in new[] { 0, 1, 2 })    // below, equal, above the cap
                        {
                            bool hasExt = (m & 1) != 0, en = (m & 2) != 0, spawned = (m & 4) != 0, downed = (m & 8) != 0, mental = (m & 16) != 0,
                                 hasMap = (m & 32) != 0, hasComp = (m & 64) != 0, onMed = (m & 128) != 0, hf = (m & 256) != 0, turn = (m & 512) != 0;
                            foreach (bool hasFood in new[] { false, true })
                                foreach (bool roll in new[] { false, true })
                                {
                                    float thr = 0.25f, food = foodRel == 0 ? 0.1f : foodRel == 1 ? 0.25f : 0.9f;
                                    int cap = 40, act = actRel == 0 ? 10 : actRel == 1 ? 40 : 90;
                                    Cases++; Steps++;
                                    bool got = RM_WatcherKernel.WatchGiverAllows(hasExt, en, spawned, downed, mental, hasMap, hasComp, onMed, hf, turn, hasFood, food, thr, roll, act, cap);
                                    bool want = hasExt && en && spawned && !downed && !mental && hasMap && hasComp && onMed && (hf || turn)
                                        && !(hasFood && food < thr) && !roll && act < cap;
                                    Check(got == want, $"WatchGiverAllows mismatch (mask {m}, food {foodRel}, active {actRel}, hasFood {hasFood}, roll {roll}): got {got}, spec {want}");
                                    // cross-gate: the giver never starts a watch whose first hidden step would end for hunger
                                    if (got && hasFood) Check(!(food < thr), "giver started a watch for a pawn below the emerge threshold");
                                    Check(RM_WatcherKernel.WatchGiverPre(hasExt, en, spawned, downed, mental, hasMap, hasComp, onMed, hf, turn, hasFood, food, thr)
                                        == (hasExt && en && spawned && !downed && !mental && hasMap && hasComp && onMed && (hf || turn) && !(hasFood && food < thr)), "Pre disagrees with the spec");
                                    Check(got == (RM_WatcherKernel.WatchGiverPre(hasExt, en, spawned, downed, mental, hasMap, hasComp, onMed, hf, turn, hasFood, food, thr)
                                        && RM_WatcherKernel.WatchGiverCapOk(roll, act, cap)), "Allows is not Pre && CapOk");
                                }
                        }
                // seek-medium backstop
                for (int m = 0; m < (1 << 9); m++)
                {
                    bool en = (m & 1) != 0, stay = (m & 2) != 0, hasMed = (m & 4) != 0, downed = (m & 8) != 0, mental = (m & 16) != 0,
                         noMed = (m & 32) != 0, onMed = (m & 64) != 0, hasJob = (m & 128) != 0, idle = (m & 256) != 0;
                    Cases++; Steps++;
                    bool got = RM_WatcherKernel.ShouldSeekMedium(en, stay, hasMed, downed, mental, noMed, onMed, hasJob, idle);
                    bool want = en && stay && hasMed && !downed && !mental && !noMed && !onMed && (!hasJob || idle);
                    Check(got == want, $"ShouldSeekMedium mask {m}: got {got}, spec {want}");
                    if (hasJob && !idle) Check(!got, "the backstop interrupted a non-idle job");
                }
                // reaction speed: a colonist sprinting at ~6 cells/s (0.1 cell/tick) gets at most half the default 6-cell flinch radius in
                // before the next step sees it, so the watcher is gone well before it can be reached ("fast retraction")
                Cases++; Steps++;
                Check(RM_WatcherKernel.StepInterval * 0.1f <= 6f / 2f, $"step interval {RM_WatcherKernel.StepInterval} lets an intruder cover over half the flinch radius unseen");
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
        private static List<string> CE(bool hh, bool sd, bool sc, float fl, float wr, int hmin, int hmax, int mw, float wc, float em, float geo, float ml)
            => RM_WatcherKernel.ConfigErrors(hh, sd, sc, fl, wr, hmin, hmax, mw, wc, em, geo, ml);

        private static List<string> Config(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++; Steps++;
                try
                {
                    // the shipped piinnok must be sound
                    Check(CE(true, true, true, 6f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, 2.5f, 5f).Count == 0, "the shipped piinnok values are rejected");
                    bool hh = r.Next(8) != 0, sd = r.Next(8) != 0, sc = r.Next(8) != 0;
                    float fl = F(r, -2f, 20f), wr = F(r, -2f, 30f), wc = F(r, -0.5f, 1.5f), em = F(r, -0.5f, 1.5f), geo = F(r, -1f, 5f), ml = F(r, -2f, 10f);
                    int hmin = r.Next(-100, 8000), hmax = hmin + r.Next(-500, 8000), mw = r.Next(-100, 5000);
                    var got = CE(hh, sd, sc, fl, wr, hmin, hmax, mw, wc, em, geo, ml);
                    int want = 0;
                    if (!hh) want++;
                    if (!sd) want++; else if (!sc) want++;
                    if (fl <= 0f || wr < fl) want++;
                    if (hmin <= 0 || hmax < hmin) want++;
                    if (mw <= 0) want++;
                    if (wc < 0f || wc > 1f) want++;
                    if (em < 0f || em > 1f) want++;
                    if (geo < 0f) want++;
                    if (!(ml > 0f)) want++;
                    Check(got.Count == want, $"ConfigErrors reported {got.Count} for a def that has {want} faults: {string.Join(" | ", got)}");
                    // each single break of the good def is reported exactly once
                    var breaks = new (string name, Func<List<string>> run)[]
                    {
                        ("no hediff", () => CE(false, true, true, 6f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, 2.5f, 5f)),
                        ("no sign", () => CE(true, false, false, 6f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, 2.5f, 5f)),
                        ("wrong sign class", () => CE(true, true, false, 6f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, 2.5f, 5f)),
                        ("flinch beyond watch", () => CE(true, true, true, 15f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, 2.5f, 5f)),
                        ("flinch zero", () => CE(true, true, true, 0f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, 2.5f, 5f)),
                        ("hide range reversed", () => CE(true, true, true, 6f, 14f, 7500, 2500, 2500, 0.1f, 0.25f, 2.5f, 5f)),
                        ("hide min zero", () => CE(true, true, true, 6f, 14f, 0, 7500, 2500, 0.1f, 0.25f, 2.5f, 5f)),
                        ("no watch time", () => CE(true, true, true, 6f, 14f, 2500, 7500, 0, 0.1f, 0.25f, 2.5f, 5f)),
                        ("wander above 1", () => CE(true, true, true, 6f, 14f, 2500, 7500, 2500, 1.2f, 0.25f, 2.5f, 5f)),
                        ("wander negative", () => CE(true, true, true, 6f, 14f, 2500, 7500, 2500, -0.1f, 0.25f, 2.5f, 5f)),
                        ("emerge threshold above 1", () => CE(true, true, true, 6f, 14f, 2500, 7500, 2500, 0.1f, 1.5f, 2.5f, 5f)),
                        ("geophone negative", () => CE(true, true, true, 6f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, -1f, 5f)),
                        ("fragility ceiling zero", () => CE(true, true, true, 6f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, 2.5f, 0f)),
                        ("fragility ceiling NaN", () => CE(true, true, true, 6f, 14f, 2500, 7500, 2500, 0.1f, 0.25f, 2.5f, float.NaN)),
                    };
                    foreach (var b in breaks) Check(b.run().Count == 1, $"single break '{b.name}' reported {b.run().Count} errors");
                    // edges that must stay valid
                    Check(CE(true, true, true, 14f, 14f, 1, 1, 1, 0f, 0f, 0f, 0.001f).Count == 0, "boundary values rejected");
                    Check(CE(true, true, true, 14f, 14f, 1, 1, 1, 1f, 1f, 0f, 1000f).Count == 0, "boundary values (1.0) rejected");
                }
                catch (Exception e) { fails.Add($"config seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        // ---------------------------------------------------------------- death (fragility + sign validity)
        private static List<string> Death(int cases, int seed0)
        {
            var fails = new List<string>();
            try
            {
                // the shipped piinnok: baseHealthScale 0.02 dies at 3, under its ceiling 5
                Check(Math.Abs(RM_WatcherKernel.LethalDamage(0.02f, 1f) - 3f) < 1e-4f, "piinnok lethal damage is not 150 x 0.02");
                Check(RM_WatcherKernel.FragilityErrors(0.02f, 5f).Count == 0, "the shipped piinnok fails the fragility audit");
                Check(RM_WatcherKernel.FragilityErrors(0.02f, RM_WatcherKernel.LethalDamage(0.02f, 1f)).Count == 0, "dying exactly at the ceiling fails the audit (the edge is inclusive)");
                Check(RM_WatcherKernel.FragilityErrors(0.3f, 5f).Count == 1, "the old piinnok (0.3, dies at 45) passes the fragility audit");
                Check(RM_WatcherKernel.FragilityErrors(1f, 5f).Count == 1, "an ordinary-health animal passes the fragility audit");
                for (int c = 0; c < cases; c++)
                {
                    var r = new Random(seed0 + c); Cases++; Steps++;
                    float bhs = F(r, 0f, 2f), ml = F(r, 0.01f, 200f), stage = F(r, 0.05f, 1f);
                    bool bad = RM_WatcherKernel.FragilityErrors(bhs, ml).Count > 0;
                    Check(bad == !(150f * bhs <= ml), $"fragility verdict for bhs {bhs} ceiling {ml}");
                    // a younger stage (factor <= 1) is never sturdier than the audited adult
                    Check(RM_WatcherKernel.LethalDamage(bhs, stage) <= RM_WatcherKernel.LethalDamage(bhs, 1f) + 1e-4f, "a young stage is sturdier than the adult");
                    // monotone: a sturdier race never passes where a frailer one failed
                    if (bad) Check(RM_WatcherKernel.FragilityErrors(bhs * 1.5f + 0.001f, ml).Count > 0, "raising health cured a fragility failure");
                }
                // sign validity: exhaustive
                for (int m = 0; m < 32; m++)
                {
                    bool own = (m & 1) != 0, sp = (m & 2) != 0, dead = (m & 4) != 0, job = (m & 8) != 0, mine = (m & 16) != 0;
                    Cases++; Steps++; SignVerdicts++;
                    bool got = RM_WatcherKernel.SignValid(own, sp, dead, job, mine);
                    Check(got == (own && sp && !dead && job && mine), $"SignValid mask {m}");
                    if (dead) Check(!got, "a sign outlived its dead owner");
                    if (!mine) Check(!got, "a duplicate sign (not the job's own) stood");
                    if (!job) Check(!got, "an orphan sign (owner out of the watch job) stood");
                }
            }
            catch (Exception e) { fails.Add("death: " + e.Message); }
            return fails;
        }

        // ---------------------------------------------------------------- alarm
        // A field of watchers on a grid; the ripple is driven exactly as RM_WatcherAlarm drives it (a queue of passes ordered by deliver
        // tick), with independent checks on what it reached.
        private static List<string> Alarm(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    var L = RM_WatcherKernel.DefaultAlarmLimits();
                    if (r.Next(3) == 0)
                    {
                        L.maxCount = r.Next(0, 9); L.maxHops = r.Next(0, 5); L.maxAgeTicks = r.Next(1, 1200); L.minDelayTicks = r.Next(0, 80);
                        L.maxDelayTicks = L.minDelayTicks + r.Next(0, 120); L.hopRadius = F(r, 0.5f, 15f); L.maxDistFromOrigin = F(r, 0.5f, 25f);
                    }
                    int n = r.Next(0, 40); int span = 4 + r.Next(30);
                    var xs = new int[n]; var zs = new int[n]; var elig = new bool[n];
                    for (int i = 0; i < n; i++) { xs[i] = r.Next(span); zs[i] = r.Next(span); elig[i] = r.Next(5) != 0; }
                    int ox = r.Next(span), oz = r.Next(span); int start = 1000 + r.Next(100000);
                    var reachedAt = new int[n]; var hopOf = new int[n]; for (int i = 0; i < n; i++) { reachedAt[i] = -1; hopOf[i] = -1; }
                    var queue = new List<(int who, int tick, int hop, int px, int pz, int passerTick)>();
                    int reachedCount = 0; int passes = 0;
                    void DoPass(int px, int pz, int hop, int passerTick, int now)
                    {
                        passes++;
                        var dp = new List<float>(); var dO = new List<float>(); var el = new List<bool>(); var rc = new List<bool>();
                        for (int i = 0; i < n; i++)
                        {
                            dp.Add((xs[i] - px) * (xs[i] - px) + (zs[i] - pz) * (zs[i] - pz)); dO.Add((xs[i] - ox) * (xs[i] - ox) + (zs[i] - oz) * (zs[i] - oz));
                            el.Add(elig[i]); rc.Add(reachedAt[i] >= 0);
                        }
                        var pick = RM_WatcherKernel.AlarmPick(dp, dO, el, rc, hop, reachedCount, now, start, L);
                        Check(pick.Distinct().Count() == pick.Count, "picked the same watcher twice in one pass");
                        for (int k = 0; k < pick.Count; k++)
                        {
                            int i = pick[k];
                            Check(elig[i], "reached an ineligible watcher (hidden, dead or busy)");
                            Check(reachedAt[i] < 0, "reached a watcher the event had already reached");
                            Check(dp[i] <= L.hopRadius * L.hopRadius, "reached beyond the hop radius");
                            Check(dO[i] <= L.maxDistFromOrigin * L.maxDistFromOrigin, "reached beyond the distance from the origin");
                            if (k > 0) Check(dp[pick[k - 1]] <= dp[i], "a pass did not take the nearest first");
                            int dt = RM_WatcherKernel.AlarmDeliverTick(passerTick, (float)r.NextDouble(), L);
                            Check(dt >= passerTick + L.minDelayTicks && dt <= passerTick + L.maxDelayTicks, "a delay outside [minDelay, maxDelay]");
                            reachedAt[i] = dt; hopOf[i] = hop + 1; reachedCount++;
                            queue.Add((i, dt, hop + 1, xs[i], zs[i], dt));
                        }
                        // liveness: when the pass picked nobody but could have, that is a bug
                        if (pick.Count == 0 && RM_WatcherKernel.AlarmLive(now, start, L) && hop < L.maxHops && reachedCount < L.maxCount)
                            for (int i = 0; i < n; i++)
                                Check(!(elig[i] && reachedAt[i] < 0 && dp[i] <= L.hopRadius * L.hopRadius && dO[i] <= L.maxDistFromOrigin * L.maxDistFromOrigin),
                                    "a live pass with room skipped a reachable watcher");
                    }
                    DoPass(ox, oz, 0, start, start);
                    int guard = 0;
                    while (queue.Count > 0)
                    {
                        Check(++guard < 10000, "the ripple did not terminate");
                        int bi = 0; for (int i = 1; i < queue.Count; i++) if (queue[i].tick < queue[bi].tick) bi = i;
                        var q = queue[bi]; queue.RemoveAt(bi); Steps++;
                        if (!RM_WatcherKernel.AlarmLive(q.tick, start, L)) continue;   // the event expired before this pass landed: it is dropped
                        RippleReaches++;
                        DoPass(q.px, q.pz, q.hop, q.passerTick, q.tick);
                    }
                    RipplesRun++;
                    Check(reachedCount <= Math.Max(0, L.maxCount), $"reached {reachedCount} > maxCount {L.maxCount}");
                    if (reachedCount == L.maxCount && L.maxCount > 0) RipplesCapped++;
                    for (int i = 0; i < n; i++) if (hopOf[i] >= 0) Check(hopOf[i] <= L.maxHops, "reached past maxHops");
                    Check(passes <= 1 + reachedCount, "more passes than reached watchers + the origin");
                    // nothing lands after the event's age (passes landing late are dropped above, never delivered)
                    Check(!RM_WatcherKernel.AlarmLive(start + L.maxAgeTicks, start, L) && RM_WatcherKernel.AlarmLive(start + L.maxAgeTicks - 1, start, L) == (L.maxAgeTicks > 0),
                        "AlarmLive edge is not [start, start + maxAge)");
                    // a dead event picks nobody
                    var none = RM_WatcherKernel.AlarmPick(new List<float> { 0f }, new List<float> { 0f }, new List<bool> { true }, new List<bool> { false }, 0, 0, start + L.maxAgeTicks, start, L);
                    Check(none.Count == 0, "an expired event still reached a watcher");
                }
                catch (Exception e) { fails.Add($"alarm seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        // ---------------------------------------------------------------- cues
        private static CueKind SpecCues(CueIn c)
        {
            CueKind k = 0;
            if (c.gasOn) { if (!(c.gasPercent < c.gasMin)) k |= CueKind.Gas; }
            if (c.heatOn) { if (!(c.tempC < c.heatAboveC)) k |= CueKind.Heat; }
            if (c.fireOn) { if (c.fireDistSq != float.MaxValue && !(c.fireDistSq > c.fireRadius * c.fireRadius)) k |= CueKind.Fire; }
            if (c.steamOn) { if (c.steamDistSq != float.MaxValue && !(c.steamDistSq > c.steamRadius * c.steamRadius)) k |= CueKind.Steam; }
            if (c.shadeOn) { if (c.shade < c.shadeMin) k |= CueKind.Shade; }
            if (c.buriedOn) { if (c.buriedDistSq != float.MaxValue && !(c.buriedDistSq > c.buriedRadius * c.buriedRadius)) k |= CueKind.Buried; }
            if (c.lightOn) { if (!(c.glow < c.lightAbove)) k |= CueKind.Light; }
            return k;
        }

        private static float Dist(Random r, float radius)
        {
            int k = r.Next(6);
            if (k == 0) return float.MaxValue;                      // none on the map
            if (k == 1) return radius * radius;                     // exactly on the edge: counts
            float d = k == 2 ? (float)Math.Floor(radius) : F(r, 0f, radius * 2f);
            return d * d;
        }

        private static List<string> Cues(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++; Steps++;
                try
                {
                    float fr = F(r, 0.5f, 20f), sr = F(r, 0.5f, 20f), br = F(r, 0.5f, 20f);
                    var ci = new CueIn
                    {
                        gasOn = r.Next(2) == 0, heatOn = r.Next(2) == 0, fireOn = r.Next(2) == 0, steamOn = r.Next(2) == 0,
                        shadeOn = r.Next(2) == 0, buriedOn = r.Next(2) == 0, lightOn = r.Next(2) == 0,
                        gasMin = F(r, 0.01f, 1f), heatAboveC = F(r, -150f, 80f), fireRadius = fr, steamRadius = sr, shadeMin = F(r, 0.01f, 1f),
                        buriedRadius = br, lightAbove = F(r, 0.01f, 1f), fireDistSq = Dist(r, fr), steamDistSq = Dist(r, sr), buriedDistSq = Dist(r, br),
                    };
                    ci.gasPercent = r.Next(4) == 0 ? ci.gasMin : F(r, 0f, 1f);
                    ci.tempC = r.Next(4) == 0 ? ci.heatAboveC : F(r, -200f, 120f);
                    ci.shade = r.Next(4) == 0 ? ci.shadeMin : F(r, 0f, 1f);
                    ci.glow = r.Next(4) == 0 ? ci.lightAbove : F(r, 0f, 1f);
                    CueKind got = RM_WatcherKernel.Cues(ci), want = SpecCues(ci);
                    Check(got == want, $"Cues {got}, spec {want}");
                    if (got != 0) CueFires++;
                    // a cue that is off never fires, whatever its reading
                    var off = ci; off.gasOn = off.heatOn = off.fireOn = off.steamOn = off.shadeOn = off.buriedOn = off.lightOn = false;
                    Check(RM_WatcherKernel.Cues(off) == CueKind.None, "a cue fired with every cue off");
                    // metamorphic: closer/hotter/darker never un-fires
                    var m2 = ci; m2.fireDistSq = Math.Min(ci.fireDistSq, 0f); m2.tempC = ci.tempC + 10f; m2.gasPercent = Math.Min(1f, ci.gasPercent + 0.1f);
                    m2.shade = Math.Max(0f, ci.shade - 0.1f); m2.glow = Math.Min(1f, ci.glow + 0.1f);
                    Check((RM_WatcherKernel.Cues(m2) & got) == got, "a stronger stimulus un-fired a cue");
                    // shade reading: roof = full shade; night = full shade; grid never makes it brighter than the sky alone
                    float g = F(r, -0.5f, 1.5f), sky = F(r, -0.5f, 1.5f);
                    float sAct = RM_WatcherKernel.ShadeReading(false, true, g, sky), sOff = RM_WatcherKernel.ShadeReading(false, false, g, sky);
                    Check(RM_WatcherKernel.ShadeReading(true, r.Next(2) == 0, g, sky) == 1f, "a roofed cell is not full shade");
                    Check(RM_WatcherKernel.ShadeReading(false, r.Next(2) == 0, g, 0f) == 1f, "night is not full shade");
                    Check(sAct >= sOff && sAct >= 0f && sAct <= 1f && sOff >= 0f && sOff <= 1f, $"shade reading out of order/range: active {sAct}, off {sOff}");
                    Check(RM_WatcherKernel.ShadeReading(false, false, 1f, 1f) == 0f, "full sun, no grid, no roof is not 0 shade");
                }
                catch (Exception e) { fails.Add($"cues seed {seed}: {e.Message}"); }
            }
            try
            {
                // config: the sound example in RM_WatcherCues' header, then each single break exactly once
                int E(bool a, int b, float c2, bool d, float e2, bool f, float g, bool h, int i, float j, bool k, float l, bool m, int n, float o, bool p, float q)
                    => RM_WatcherKernel.CueConfigErrors(a, b, c2, d, e2, f, g, h, i, j, k, l, m, n, o, p, q).Count;
                Check(E(true, 1, 0.1f, true, -120f, true, 8f, true, 1, 10f, true, 0.5f, true, 1, 10f, true, 0.5f) == 0, "the documented example is rejected");
                Check(E(false, 0, 0f, false, 0f, false, 0f, false, 0, 0f, false, 0f, false, 0, 0f, false, 0f) == 0, "no cues at all is rejected");
                Check(E(true, 1, 1f, true, -272f, true, 0.01f, true, 1, 0.01f, true, 1f, true, 1, 0.01f, true, 1f) == 0, "boundary values rejected");
                var breaks = new (string, int)[]
                {
                    ("gas no types", E(true, 0, 0.1f, false, 0f, false, 0f, false, 0, 0f, false, 0f, false, 0, 0f, false, 0f)),
                    ("gas min 0", E(true, 1, 0f, false, 0f, false, 0f, false, 0, 0f, false, 0f, false, 0, 0f, false, 0f)),
                    ("gas min above 1", E(true, 1, 1.5f, false, 0f, false, 0f, false, 0, 0f, false, 0f, false, 0, 0f, false, 0f)),
                    ("heat below absolute zero", E(false, 0, 0f, true, -300f, false, 0f, false, 0, 0f, false, 0f, false, 0, 0f, false, 0f)),
                    ("heat NaN", E(false, 0, 0f, true, float.NaN, false, 0f, false, 0, 0f, false, 0f, false, 0, 0f, false, 0f)),
                    ("fire radius 0", E(false, 0, 0f, false, 0f, true, 0f, false, 0, 0f, false, 0f, false, 0, 0f, false, 0f)),
                    ("steam no things", E(false, 0, 0f, false, 0f, false, 0f, true, 0, 5f, false, 0f, false, 0, 0f, false, 0f)),
                    ("steam radius 0", E(false, 0, 0f, false, 0f, false, 0f, true, 1, 0f, false, 0f, false, 0, 0f, false, 0f)),
                    ("shade min 0", E(false, 0, 0f, false, 0f, false, 0f, false, 0, 0f, true, 0f, false, 0, 0f, false, 0f)),
                    ("buried no hediffs", E(false, 0, 0f, false, 0f, false, 0f, false, 0, 0f, false, 0f, true, 0, 5f, false, 0f)),
                    ("buried radius negative", E(false, 0, 0f, false, 0f, false, 0f, false, 0, 0f, false, 0f, true, 1, -1f, false, 0f)),
                    ("light min 0", E(false, 0, 0f, false, 0f, false, 0f, false, 0, 0f, false, 0f, false, 0, 0f, true, 0f)),
                };
                foreach (var (name, n) in breaks) { Cases++; Check(n == 1, $"single cue break '{name}' reported {n} errors"); }
                // the water audit, exhaustively
                for (int m = 0; m < 32; m++)
                {
                    bool imp = (m & 1) != 0, avoid = (m & 2) != 0, water = (m & 4) != 0, seeker = (m & 8) != 0, swim = (m & 16) != 0;
                    var errs = new List<string>(); var warns = new List<string>(); Cases++; Steps++;
                    RM_WatcherKernel.MediumAudit(imp, avoid, water, seeker, swim, errs, warns);
                    Check(errs.Count == (imp ? 1 : 0), $"medium audit errors {errs.Count} for mask {m}");
                    Check(warns.Count == (avoid && !seeker ? 1 : 0) + (water && swim ? 1 : 0), $"medium audit warnings {warns.Count} for mask {m}");
                }
                // the shipped piinnok (deep sand: avoidWander, IsWater, waterSeeker, no swim sprite) audits clean
                var e0 = new List<string>(); var w0 = new List<string>();
                RM_WatcherKernel.MediumAudit(false, true, true, true, false, e0, w0);
                Check(e0.Count == 0 && w0.Count == 0, "the shipped piinnok fails the water audit");
            }
            catch (Exception e) { fails.Add("cues config/audit: " + e.Message); }
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
                ("cues", () => Cues(N(6000), S(1))),
                ("death", () => Death(N(3000), S(1))),
                ("alarm", () => Alarm(N(4000), S(1))),
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
                Console.WriteLine($"cues reached: cue-only hides {CueHides}, cue fires {CueFires}");
                Console.WriteLine($"alarm reached: alarm-only hides {AlarmHides}, alarms raised {AlarmRaises}, ripples {RipplesRun}, passes landed {RippleReaches}, ripples at the cap {RipplesCapped}, sign verdicts {SignVerdicts}");
                if (AlarmHides == 0 || AlarmRaises == 0 || RippleReaches == 0 || RipplesCapped == 0 || SignVerdicts == 0) { Console.WriteLine("FAIL alarm/death paths never reached (blind)"); ok = false; }
                if (CueHides == 0 || CueFires == 0) { Console.WriteLine("FAIL cue paths never reached (blind)"); ok = false; }
                if (Hides == 0 || Emerges == 0 || HungryEmerges == 0 || Succeeded == 0 || Interrupted == 0 || HuntSinks == 0 || SignRestores == 0) { Console.WriteLine("FAIL watcher fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"watchers fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
