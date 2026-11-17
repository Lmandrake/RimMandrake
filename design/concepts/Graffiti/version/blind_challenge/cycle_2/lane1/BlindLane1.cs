// Graffiti 0.1.0, blind challenge cycle 2, lane 1: the cycle-2 judge's own tests, written from the bars (tree.json, sheet.md,
// plan.md, record.json inventory text), the shipped settings (RM_GraffitiMod.cs) and the defs alone, run against the kernel
// RM_GraffitiKernel.cs (plus the two enum files it compiles with). One JSON row per line on stdout. Exit 0 = no FAIL row.
// Arguments: <TemperamentDefs xml path>. Settings as shipped come in by environment (run_lane1.py reads them from RM_GraffitiMod.cs).
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Xml.Linq;
using RimMandrake.Graffiti;
using K = RimMandrake.Graffiti.RM_GraffitiKernel;

static class BlindLane1
{
    static int fails;
    static void Row(string id, string[] bars, string kind, string verdict, long cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine(JsonSerializer.Serialize(new Dictionary<string, object> {
            ["id"] = id, ["bars"] = bars, ["kind"] = kind, ["verdict"] = verdict, ["cases"] = cases, ["detail"] = detail }));
    }
    static void Check(string id, string[] bars, string kind, Func<(long cases, string bad, string ok)> f)
    {
        try
        {
            var (cases, bad, ok) = f();
            Row(id, bars, kind, bad == null ? "PASS" : "FAIL", cases, bad ?? ok);
        }
        catch (Exception e) { Row(id, bars, kind, "FAIL", 0, "threw " + e.GetType().Name + ": " + e.Message); }
    }
    static float Env(string k, float d) { var s = Environment.GetEnvironmentVariable(k); return s != null && float.TryParse(s, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float v) ? v : d; }
    static readonly GraffitiForm[] Forms = (GraffitiForm[])Enum.GetValues(typeof(GraffitiForm));

    static int Main(string[] args)
    {
        float pushDefault = Env("GR_PUSH_DEFAULT", float.NaN), pushMin = Env("GR_PUSH_MIN", float.NaN), pushMax = Env("GR_PUSH_MAX", float.NaN);
        int modeDefault = (int)Env("GR_MODE_DEFAULT", -9), paceDefault = (int)Env("GR_PACE_DEFAULT", -9);
        float paceMin = Env("GR_PACE_MIN", float.NaN), paceMax = Env("GR_PACE_MAX", float.NaN);
        string[] RP = { "raider_pressure", "inv_raider_future_marks" };

        // ---------------------------------------------------------------- raider pressure
        Check("L1_PRESSURE_SWITCH_OFF_IS_IDENTITY", new[] { "raider_pressure", "inv_raider_future_marks", "stands_alone_settings", "inv_settings" }, "sweep", () =>
        {
            long n = 0;
            foreach (var mode in new[] { RM_PressureMode.Larger, RM_PressureMode.Sooner })
                for (int marks = -2; marks <= 40; marks++)
                    for (float push = 0.5f; push <= 4.01f; push += 0.1f)
                    {
                        n++;
                        if (K.PressureFactor(false, marks, push) != 1f) return (n, $"off, marks {marks}, push {push}: factor {K.PressureFactor(false, marks, push)} (want 1)", null);
                        if (K.PressurePoints(1000f, false, mode, marks, push) != 1000f) return (n, $"off, {mode}, marks {marks}, push {push}: points {K.PressurePoints(1000f, false, mode, marks, push)} (want 1000)", null);
                        if (K.PressureReturnTicks(60000, false, mode, marks, push) != -1) return (n, $"off, {mode}, marks {marks}: a return raid owed", null);
                        if (K.PressureChange(false, marks, false) == 1) return (n, $"off, marks {marks}: pressure starts (a letter) with the switch off", null);
                    }
            return (n, null, "switch off: factor 1, points untouched, no return raid, no letter, in both modes, any mark count and push");
        });
        Check("L1_PRESSURE_NO_STANDING_MARK_IS_IDENTITY", RP, "sweep", () =>
        {
            long n = 0;
            foreach (var mode in new[] { RM_PressureMode.Larger, RM_PressureMode.Sooner })
                for (int marks = -3; marks <= 0; marks++)
                    for (float push = 1.1f; push <= 3.01f; push += 0.1f)
                    {
                        n++;
                        if (K.PressurePoints(777f, true, mode, marks, push) != 777f || K.PressureReturnTicks(60000, true, mode, marks, push) != -1)
                            return (n, $"on, {mode}, marks {marks}, push {push}: a faction with no standing mark is still pushed", null);
                    }
            return (n, null, "faction B (no standing mark) raids exactly as unmarked: A's next raid matches B's once A's last mark is gone");
        });
        Check("L1_PRESSURE_LARGER_SWEEP_PUSH_RANGE", RP, "sweep", () =>
        {
            long n = 0;
            for (int i = 0; i <= 200; i++)
            {
                float raw = pushMin + (pushMax - pushMin) * i / 200f;
                float push = (float)Math.Round(raw * 10f) / 10f;                  // the slider rounds to 0.1, as RM_GraffitiMod does
                float one = K.PressurePoints(1000f, true, RM_PressureMode.Larger, 1, push);
                for (int marks = 1; marks <= 30; marks++)
                {
                    n++;
                    float p = K.PressurePoints(1000f, true, RM_PressureMode.Larger, marks, push);
                    if (!(p > 1000f)) return (n, $"push {push}, marks {marks}: points {p}, not above the unmarked 1000", null);
                    if (Math.Abs(p - 1000f * push) > 0.01f) return (n, $"push {push}, marks {marks}: points {p}, want 1000 x push = {1000f * push}", null);
                    if (p != one) return (n, $"push {push}: {marks} marks give {p}, one mark {one}: more marks stack", null);
                    if (p > 1000f * K.PushMax + 0.01f) return (n, $"push {push}: points {p} past the cap", null);
                }
            }
            return (n, null, $"slider {pushMin}..{pushMax} (0.1 steps): A's points = B's x push, > B's, never stacking with more marks");
        });
        Check("L1_PRESSURE_SOONER_SWEEP_PUSH_RANGE", RP, "sweep", () =>
        {
            long n = 0; int prev = int.MaxValue;
            for (int i = 0; i <= 19; i++)
            {
                float push = (float)Math.Round((pushMin + 0.1f * i) * 10f) / 10f;
                if (push > pushMax + 1e-4f) break;
                n++;
                if (K.PressurePoints(1000f, true, RM_PressureMode.Sooner, 1, push) != 1000f) return (n, $"sooner, push {push}: points changed", null);
                int t = K.PressureReturnTicks(60000, true, RM_PressureMode.Sooner, 1, push);
                if (t <= 0 || t >= K.SoonerBaseDays * 60000) return (n, $"sooner, push {push}: return at {t} ticks, not within (0, {K.SoonerBaseDays} days)", null);
                if (t > prev) return (n, $"sooner: a harder push {push} returns later ({t} > {prev})", null);
                prev = t;
                for (int marks = 2; marks <= 20; marks++) { n++; if (K.PressureReturnTicks(60000, true, RM_PressureMode.Sooner, marks, push) != t) return (n, $"sooner push {push}: {marks} marks change the return", null); }
            }
            return (n, null, "sooner mode: points untouched; the return comes within 15/push days, earlier for a harder push, never stacking");
        });
        Check("L1_PRESSURE_LETTER_ONCE_LIFT_ON_LAST_MARK", RP, "random", () =>
        {
            const int seed = 20261117; var rng = new Random(seed); long n = 0;
            for (int run = 0; run < 2000; run++)
            {
                bool was = false, on = true; int marks = 0; var trace = new List<string>();
                for (int step = 0; step < 60; step++)
                {
                    int r = rng.Next(10);
                    if (r < 4) marks++; else if (r < 8) marks = Math.Max(0, marks - 1); else if (r == 8) marks = 0; else on = !on;
                    int ch = K.PressureChange(was, marks, on); n++;
                    bool now = on && marks > 0;
                    trace.Add($"{(on ? "on" : "off")}:{marks}:{ch}");
                    if (ch == 1 && (was || !now)) return (n, $"seed {seed} run {run}: a letter while already pressured or not pressured: {string.Join(" ", trace.Skip(Math.Max(0, trace.Count - 6)))}", null);
                    if (ch == -1 && (!was || now)) return (n, $"seed {seed} run {run}: a lift with no pressure to lift: {string.Join(" ", trace.Skip(Math.Max(0, trace.Count - 6)))}", null);
                    if (ch == 0 && was != now) return (n, $"seed {seed} run {run}: state changed with no transition: {string.Join(" ", trace.Skip(Math.Max(0, trace.Count - 6)))}", null);
                    if (ch == 1) was = true; else if (ch == -1) was = false;
                    if (marks == 0 && K.PressureFactor(on, marks, 2f) != 1f) return (n, $"seed {seed}: last mark gone but factor {K.PressureFactor(on, marks, 2f)}", null);
                }
            }
            return (n, null, "seed 20261117, 2000 runs x 60 steps of marks painted/scrubbed/weathered and the switch flipped: one letter (+1) per pressure start, one lift (-1) when the last mark goes or the switch goes off, never two letters for one pressure");
        });
        Check("L1_PRESSURE_SHIPPED_DEFAULTS", new[] { "raider_pressure", "inv_raider_future_marks", "inv_settings" }, "fixed", () =>
        {
            string bad = null;
            if (!(pushDefault >= pushMin && pushDefault <= pushMax)) bad = $"shipped push {pushDefault} outside the slider {pushMin}..{pushMax}";
            else if (!(pushMin > 1f)) bad = $"slider floor {pushMin} lets the push be no push at all";
            else if (Math.Abs(pushMax - K.PushMax) > 1e-6f) bad = $"slider top {pushMax} differs from the kernel cap {K.PushMax}";
            else if (modeDefault != 0) bad = $"shipped mode {modeDefault}, not 0 (larger)";
            else if (Math.Abs(K.PressurePoints(1000f, true, RM_PressureMode.Larger, 1, pushDefault) - 1000f * pushDefault) > 0.01f) bad = "the shipped push does not reach the points";
            return (5, bad, $"shipped: on, mode {modeDefault} (larger), push {pushDefault} in {pushMin}..{pushMax}; floor above 1, so a marked faction's raid is always visibly larger");
        });
        {
            // A settings file edited by hand (or an old save's file) can hold any float: does the factor stay a number in [1, PushMax]?
            var probes = new[] { float.NaN, float.PositiveInfinity, float.NegativeInfinity, -5f, 0f, 0.5f, 10f, 1e9f };
            var bad = probes.Where(p => { float f = K.PressureFactor(true, 1, p); return float.IsNaN(f) || f < 1f || f > K.PushMax; }).ToList();
            Row("L1_PRESSURE_EDITED_FILE_PUSH", RP, "info", "INFO", probes.Length,
                bad.Count == 0 ? "every out-of-range push (NaN, +-inf, negative, 0, 10, 1e9) gives a factor in [1, 3]"
                               : "push " + string.Join(", ", bad) + " gives factor " + string.Join(", ", bad.Select(p => K.PressureFactor(true, 1, p))) + " (outside [1,3]; only a hand-edited settings file reaches it: the slider cannot; ExposeData does not clamp)");
        }

        // ---------------------------------------------------------------- ugliness and art skill
        Check("L1_UGLINESS_SAME_HAND_EVERY_CRAFT", new[] { "ugliness_visible", "inv_beauty_and_craft" }, "sweep", () =>
        {
            int cs = K.CraftCeiling(GraffitiForm.Scrawl), ct = K.CraftCeiling(GraffitiForm.Glyph);   // RM_Graffiti_Vandal is a Scrawl, RM_Graffiti_TallyMarks a Glyph (ThingDefs_Graffiti.xml)
            var parts = new List<string>(); long n = 0;
            for (int q = K.Awful; q <= K.Legendary; q++)
            {
                n++;
                float s = K.MarkBeauty(GraffitiForm.Scrawl, Math.Min(q, cs)), t = K.MarkBeauty(GraffitiForm.Glyph, Math.Min(q, ct));
                parts.Add($"{q}:{s}/{t}");
                if (!(s < t)) return (n, $"hand roll {q}: scrawl {s} (craft {Math.Min(q, cs)}) is not uglier than the tally {t} (craft {Math.Min(q, ct)}); attainable: any scrawl below the same hand's tally", null);
            }
            return (n, null, "roll:scrawl/tally " + string.Join(" ", parts) + " : at every craft the hand can roll, the scrawl inspects uglier");
        });
        Check("L1_UGLINESS_SCRAWL_BELOW_EVERY_SAME_HAND_FORM", new[] { "ugliness_visible", "inv_beauty_and_craft" }, "sweep", () =>
        {
            long n = 0;
            foreach (var f in Forms)
            {
                if (f == GraffitiForm.Scrawl) continue;
                for (int q = K.Awful; q <= K.Legendary; q++)
                {
                    n++;
                    float s = K.MarkBeauty(GraffitiForm.Scrawl, Math.Min(q, K.CraftCeiling(GraffitiForm.Scrawl))), o = K.MarkBeauty(f, Math.Min(q, K.CraftCeiling(f)));
                    if (!(s < o)) return (n, $"roll {q}: a scrawl {s} is not uglier than the same hand's {f} {o}", null);
                }
            }
            return (n, null, "a scrawl is the ugliest thing any hand puts on a wall, against every other form at every roll");
        });
        Check("L1_ART_SKILL_SIGN_AND_ORDER", new[] { "art_skill", "inv_beauty_and_craft" }, "fixed", () =>
        {
            long n = 0; float prev = float.NegativeInfinity; float prevReach = float.NegativeInfinity;
            for (int q = K.Awful; q <= K.Legendary; q++)
            {
                n++;
                float b = K.CraftBeauty(q), r = K.CraftReach(q);
                if (q <= K.Poor && !(b < 0f)) return (n, $"craft {q} (a poor hand) beauty {b}: does not harm the room", null);
                if (q >= K.Good && !(b > 0f)) return (n, $"craft {q} (a skilled hand) beauty {b}: does not raise the room", null);
                if (!(b > prev)) return (n, $"craft {q} beauty {b} not above craft {q - 1}'s {prev}", null);
                if (!(r >= prevReach)) return (n, $"craft {q} reach {r} below the lower craft's", null);
                int st = K.CraftStage(q, out bool ugly);
                if (q <= K.Poor && !(ugly && st >= 0)) return (n, $"craft {q}: viewers take no ugly-mark thought", null);
                if (q >= K.Good && !( !ugly && st >= 0)) return (n, $"craft {q}: viewers take no fine-art thought", null);
                prev = b; prevReach = r;
            }
            // control: the same mark with craft forced Normal gives equal beauty whoever painted it (the kernel's beauty takes no hand but its craft)
            foreach (var f in Forms) { n++; float a1 = K.MarkBeauty(f, K.Normal), a2 = K.MarkBeauty(f, K.Normal); if (a1 != a2) return (n, $"{f} at forced Normal differs", null); }
            return (n, null, "awful/poor: beauty < 0 and an ugly-mark thought; good..legendary: beauty > 0 and a fine-art thought; strictly rising; forced Normal equal");
        });
        {
            var low = Forms.Where(f => K.CraftCeiling(f) < K.Good).ToList();
            Row("L1_ART_SKILL_FORM_CEILING", new[] { "art_skill" }, "info", "INFO", Forms.Length,
                "forms whose craft is capped below Good, so a skill-16 hand painting them cannot raise a room: " + string.Join(", ", low.Select(f => f + "<=" + K.CraftCeiling(f)))
                + $"; FormAffinity at level 16: piece {K.FormAffinity(GraffitiForm.Piece, 16)}, throw-up {K.FormAffinity(GraffitiForm.ThrowUp, 16)}, glyph {K.FormAffinity(GraffitiForm.Glyph, 16)}, tag {K.FormAffinity(GraffitiForm.Tag, 16)} (the live scene must give the skill-16 hand a form that can rise)");
        }

        // ---------------------------------------------------------------- weathering
        string[] WB = { "weathering_bounds_marks", "inv_weathering" };
        Check("L1_WEATHER_ROOFED_OUTLASTS_UNROOFED", WB, "sweep", () =>
        {
            long n = 0;
            foreach (var f in Forms)
                for (int craft = -1; craft <= 7; craft++)
                    for (int id = 0; id < 4000; id += 7)
                    {
                        n++;
                        float roofed = K.WeatherDays(f, craft, false, id), outside = K.WeatherDays(f, craft, true, id);
                        if (!(roofed > outside)) return (n, $"{f} craft {craft} id {id}: roofed {roofed} days, unroofed {outside}", null);
                        if (!(outside > 0f) || float.IsNaN(roofed) || float.IsInfinity(roofed)) return (n, $"{f} craft {craft} id {id}: life {outside}/{roofed} not a positive number", null);
                    }
            return (n, null, "every form x craft -1..7 x 572 ids: roofed life > unroofed, both positive and finite");
        });
        Check("L1_WEATHER_FADE_CURVE", WB, "random", () =>
        {
            const int seed = 4040; var rng = new Random(seed); long n = 0;
            for (int i = 0; i < 200000; i++)
            {
                float life = (float)(rng.NextDouble() * 100 + 0.01), age = (float)(rng.NextDouble() * life * 1.5);
                float fade = K.WeatherFade(age, life); n++;
                float alpha = 1f - fade;
                if (age < 0.6f * life * 0.9999f && alpha != 1f) return (n, $"seed {seed}: life {life}, age {age} ({age / life:P1} of life): alpha {alpha}, want 1 before 60%", null);
                if (age >= life && alpha != 0f) return (n, $"seed {seed}: life {life}, age {age} past its life: alpha {alpha}, want 0", null);
                if (age > 0.6f * life * 1.0001f && age < life * 0.9999f && !(alpha < 1f && alpha > 0f)) return (n, $"seed {seed}: life {life}, age {age}: alpha {alpha} not fading in the last 40%", null);
                float later = K.WeatherFade(age + 0.01f * life, life);
                if (later < fade) return (n, $"seed {seed}: fade goes back at age {age}", null);
            }
            return (n, null, "seed 4040, 200000 (life, age) draws: alpha 1 before 60% of life, falling steadily over the last 40%, 0 at the end, never recovering");
        });
        Check("L1_WEATHER_STEPS", WB, "sweep", () =>
        {
            long n = 0; int prev = 0;
            for (int i = 0; i <= 1000; i++) { float f = i / 1000f; int s = K.WeatherStep(f); n++; if (s < prev || (f > 0 && s == 0) || s > 4) return (n, $"fade {f}: step {s}", null); prev = s; }
            return (n, K.WeatherStep(1f) == 4 && K.WeatherStep(0f) == 0 ? null : "ends wrong", "fade 0..1: step 0 only when fresh, rising to 4, never back");
        });

        // ---------------------------------------------------------------- visitors
        Check("L1_VISIT_INSULT_ONCE_PER_VISIT", new[] { "visitors", "inv_visitors" }, "random", () =>
        {
            const int seed = 77; var rng = new Random(seed); long n = 0;
            int first = K.GoodwillOf(RM_Meaning.Insult, true, false, false);
            if (!(first < 0)) return (1, $"an insult to the visitor's own faction moves goodwill {first}", null);
            int lost = 0, gained = 0; var hits = new List<int>();
            for (int pass = 0; pass < 20; pass++) { int c = K.VisitCharge(first, lost, gained); hits.Add(c); if (c < 0) lost -= c; else gained += c; n++; }
            if (hits.Count(h => h != 0) != 1) return (n, $"the same insult read 20 times in one visit moves goodwill {hits.Count(h => h != 0)} times: {string.Join(",", hits)}", null);
            for (int run = 0; run < 5000; run++)
            {
                lost = 0; gained = 0;
                for (int k = 0; k < 30; k++)
                {
                    var m = (RM_Meaning)rng.Next(8); bool names = rng.Next(2) == 0, taunt = rng.Next(3) == 0, same = rng.Next(2) == 0;
                    int c = K.VisitCharge(K.GoodwillOf(m, names, taunt, same), lost, gained); n++;
                    if (c < 0) lost -= c; else gained += c;
                    if (lost > K.VisitLossCap || gained > K.VisitGainCap) return (n, $"seed {seed} run {run}: one visit moved -{lost}/+{gained}, past the caps", null);
                }
            }
            foreach (bool taunt in new[] { false, true }) foreach (bool same in new[] { false, true })
                { n++; if (K.GoodwillOf(RM_Meaning.Insult, false, taunt, same) != 0) return (n, $"an insult to ANOTHER faction (taunt {taunt}) moves this faction's goodwill {K.GoodwillOf(RM_Meaning.Insult, false, taunt, same)}", null); }
            return (n, null, $"one insult: {first} once, then 0 on 19 more passes; seed 77, 5000 visits x 30 reads: never past -{K.VisitLossCap}/+{K.VisitGainCap}; another faction's insult: 0");
        });

        // ---------------------------------------------------------------- rereads
        Row("L1_REREAD_ONCE_A_DAY", new[] { "rereads_daily", "inv_viewer_mood" }, "fixed",
            K.ReadAgainTicks >= 60000 && K.RereadFactor > 0f && K.RereadFactor <= 1f ? "PASS" : "FAIL", 2,
            $"a standing mark is read again after {K.ReadAgainTicks} ticks (one day = 60000), at {K.RereadFactor} of the first reading; that opinion moves only on the first read is caller logic (GraffitiSocial), not here");
        {
            var once = Enum.GetValues(typeof(RM_Reaction)).Cast<RM_Reaction>().Where(K.LogsOncePerDay).ToList();
            Row("L1_REREAD_LOG_TABLE", new[] { "rereads_daily", "stories_not_tax" }, "info", "INFO", once.Count,
                "reactions logged once per day per reader and painter: " + string.Join(", ", once) + "; the rest (mockery, tribute, insult) log every time per the kernel's own note");
        }

        // ---------------------------------------------------------------- mockery, tribute, memorial
        RM_Viewer V(Action<RM_Viewer[]> set) { var a = new RM_Viewer[1]; set(a); return a[0]; }
        Check("L1_MOCKERY_REACTIONS", new[] { "mockery", "inv_social_layer" }, "fixed", () =>
        {
            var subj = V(a => { a[0].isSubject = true; a[0].ownFaction = true; });
            var rival = V(a => { a[0].ownFaction = true; a[0].opinionOfSubject = -20; });      // vanilla's rival line
            var friend = V(a => { a[0].ownFaction = true; a[0].opinionOfSubject = 25; });
            var maker = V(a => { a[0].isMaker = true; a[0].ownFaction = true; });
            var rs = K.ReactionOf(RM_Meaning.Mockery, subj); var rr = K.ReactionOf(RM_Meaning.Mockery, rival); var rf = K.ReactionOf(RM_Meaning.Mockery, friend);
            string bad = rs != RM_Reaction.Humiliated ? $"subject gets {rs}" : rr != RM_Reaction.Gleeful ? $"rival of the subject gets {rr}" : rf != RM_Reaction.FriendDefends ? $"friend gets {rf}" :
                         K.ReactionOf(RM_Meaning.Mockery, maker) != RM_Reaction.None ? "the painter reacts to their own mockery" : null;
            return (4, bad, $"subject {rs} (hurt), rival {rr} (amused), friend {rf}, painter none: not everyone gets the same thought");
        });
        Check("L1_MOCKERY_WHO_PAINTS", new[] { "mockery", "fights_reasons", "inv_social_layer" }, "sweep", () =>
        {
            long n = 0;
            foreach (bool spree in new[] { false, true }) foreach (bool kind in new[] { false, true }) foreach (bool enemy in new[] { false, true })
            foreach (bool bel in new[] { false, true }) foreach (bool mourn in new[] { false, true })
            for (int op = -100; op <= 100; op += 5) for (int r = 0; r <= 100; r++)
            {
                n++; var m = K.WantsToPaint(spree, kind, op, enemy, bel, mourn, r / 100f);
                if (m == RM_Meaning.Mockery && (kind || !enemy || op > K.EnemyOpinion)) return (n, $"spree {spree} kind {kind} enemy {enemy} worst opinion {op} roll {r / 100f}: a mockery with no grudge (or by a kind hand)", null);
                if (m == RM_Meaning.Memorial && !mourn) return (n, $"no dead to mourn, roll {r / 100f}: paints a memorial", null);
                if (m == RM_Meaning.Tribute && !bel) return (n, $"no beloved, roll {r / 100f}: paints a tribute", null);
            }
            return (n, null, "a mockery only from a non-kind hand with an enemy at or below -15; a memorial only from a mourner; a tribute only for a beloved");
        });
        Check("L1_TRIBUTE_MEMORIAL_REACTIONS", new[] { "tribute_memorial", "inv_social_layer" }, "fixed", () =>
        {
            var subj = V(a => { a[0].isSubject = true; a[0].ownFaction = true; });
            var lover = V(a => { a[0].loverOfMaker = true; a[0].ownFaction = true; });
            var enemy = V(a => { a[0].opinionOfSubject = -40; a[0].ownFaction = true; });
            var mourner = V(a => { a[0].opinionOfSubject = 30; a[0].ownFaction = true; });
            var stranger = V(a => { a[0].opinionOfSubject = 0; a[0].ownFaction = true; });
            string bad = K.ReactionOf(RM_Meaning.Tribute, subj) != RM_Reaction.Honored ? "tribute's subject not honoured" :
                         K.ReactionOf(RM_Meaning.Tribute, lover) != RM_Reaction.Jealous ? "painter's lover not jealous" :
                         K.ReactionOf(RM_Meaning.Tribute, enemy) != RM_Reaction.Scoffs ? "an enemy of the subject not annoyed" :
                         K.ReactionOf(RM_Meaning.Memorial, mourner) != RM_Reaction.Mourning ? "a friend of the dead takes nothing from the memorial" :
                         K.ReactionOf(RM_Meaning.Memorial, stranger) != RM_Reaction.None ? "someone who never knew the dead mourns" : null;
            return (5, bad, "tribute: subject Honored, painter's lover Jealous, subject's enemy (<=-30) Scoffs; memorial: the dead's friend Mourning, a stranger nothing");
        });
        {
            var bands = new List<string>();
            for (int op = -29; op <= -15; op++) { var r = K.ReactionOf(RM_Meaning.Tribute, V(a => { a[0].opinionOfSubject = op; a[0].ownFaction = true; })); if (r == RM_Reaction.None) bands.Add(op.ToString()); }
            Row("L1_TRIBUTE_RIVAL_BAND", new[] { "tribute_memorial" }, "info", "UNSETTLED", 15,
                "a viewer whose opinion of the tribute's subject is " + (bands.Count > 0 ? bands.First() + ".." + bands.Last() : "none") + " (a vanilla rival, at or below -20, and the mod's own mockery enemy line -15) takes NO reaction from the tribute; "
                + "only <= -30 (Scoffs) or the painter's lover (Jealous) do. The bar's 'the rival a jealous or annoyed one' does not say whose rival (the painter's or the subject's) nor where rivalry starts. "
                + "Settles it: the live tribute_memorial scene's rival (sc for tribute_memorial in scenes.json) read with its opinion of the subject and of the painter, and whether it holds a jealous or annoyed thought");
        }
        Check("L1_MEMORIAL_EASES_NEVER_GAINS", new[] { "tribute_memorial", "stories_not_tax" }, "random", () =>
        {
            const int seed = 9; var rng = new Random(seed); long n = 0;
            for (int run = 0; run < 20000; run++)
            {
                float grief = (float)(rng.NextDouble() * 30), before = 0f;
                for (int k = 0; k < 6; k++)
                {
                    float raw = (float)(rng.NextDouble() * 20 - 2); float kept = K.EaseShare(grief, raw, before); n++;
                    if (kept < 0f) return (n, $"seed {seed}: ease {kept} negative", null);
                    before += kept;
                    if (before > grief * K.GriefEaseShare + 1e-4f || before > grief + 1e-4f) return (n, $"seed {seed} run {run}: eases {before} past half of grief {grief}", null);
                }
            }
            return (n, null, "seed 9, 20000 griefs x 6 eases: the memorials' total ease stays within half the grief, never negative, never a net gain");
        });

        // ---------------------------------------------------------------- answering the wall, fights
        Check("L1_ANSWER_ALL_FOUR_REACHABLE", new[] { "answer_wall", "inv_social_layer" }, "sweep", () =>
        {
            var seen = new HashSet<RM_Answer>(); long n = 0;
            foreach (var re in new[] { RM_Reaction.Humiliated, RM_Reaction.FriendDefends, RM_Reaction.WorkDestroyed, RM_Reaction.RivalTag, RM_Reaction.Defiant })
                foreach (bool hot in new[] { false, true })
                    for (int r = 0; r < 100; r++) { n++; seen.Add(K.AnswerOf(re, hot, true, true, true, r / 100f)); }
            bool workConfront = Enumerable.Range(0, 100).Any(r => K.AnswerOf(RM_Reaction.WorkDestroyed, true, true, true, false, r / 100f) == RM_Answer.Confront);
            var want = new[] { RM_Answer.Scrub, RM_Answer.Deface, RM_Answer.Reply, RM_Answer.Confront };
            var miss = want.Where(w => !seen.Contains(w)).ToList();
            return (n, miss.Count > 0 ? "never answered with " + string.Join(",", miss) : !workConfront ? "no confront over painted-out work" : null,
                    "scrub, cross-out, reply and confront all reachable; a hot head confronts over painted-out work");
        });
        Check("L1_ANSWER_NONE_WITHOUT_OFFENCE", new[] { "answer_wall" }, "sweep", () =>
        {
            long n = 0;
            foreach (var re in new[] { RM_Reaction.None, RM_Reaction.Honored, RM_Reaction.Warmed, RM_Reaction.Amused, RM_Reaction.Moved, RM_Reaction.Uplifted, RM_Reaction.ShrugsOff, RM_Reaction.Gleeful, RM_Reaction.Mourning, RM_Reaction.FriendTag })
                foreach (bool hot in new[] { false, true }) foreach (bool fight in new[] { false, true }) foreach (bool here in new[] { false, true }) foreach (bool good in new[] { false, true })
                    foreach (RM_Lean lean in Enum.GetValues(typeof(RM_Lean)))
                        for (int r = 0; r <= 100; r++) { n++; var a = K.AnswerOf(re, hot, fight, here, good, r / 100f, lean); if (a != RM_Answer.None) return (n, $"{re} (no offence) answered with {a}", null); }
            return (n, null, "a mark nobody is offended by (pleased, amused, honoured, untouched) gets no answer, any temper, roll or lean");
        });
        Check("L1_FIGHT_HAS_PEOPLE_AND_REASON", new[] { "fights_reasons", "answer_wall" }, "sweep", () =>
        {
            long n = 0;
            foreach (RM_Reaction re in Enum.GetValues(typeof(RM_Reaction)))
                foreach (bool hot in new[] { false, true }) foreach (bool fight in new[] { false, true }) foreach (bool here in new[] { false, true }) foreach (bool good in new[] { false, true })
                    foreach (RM_Lean lean in Enum.GetValues(typeof(RM_Lean)))
                        for (int r = 0; r <= 100; r++)
                        {
                            n++; var a = K.AnswerOf(re, hot, fight, here, good, r / 100f, lean);
                            if (a == RM_Answer.Confront && (!fight || !here)) return (n, $"{re}: a confrontation with the painter absent or unable (canFight {fight}, here {here})", null);
                            if (a == RM_Answer.Reply && (!good || !here)) return (n, $"{re}: a reply without a good hand or the painter here", null);
                        }
            for (float v = -1f; v <= 2f; v += 0.05f) for (float t = -1f; t <= 6f; t += 0.25f)
            {
                n++; float c = K.ConfrontFightChance(v, t);
                if (c < 0f || c > K.ConfrontFightCap || float.IsNaN(c)) return (n, $"fight chance {c} at vanilla {v} temper {t}", null);
                if ((v <= 0f || t <= 0f) && c != 0f) return (n, $"a fight ({c}) from nothing: vanilla {v} temper {t}", null);
            }
            return (n, null, "a confrontation only with the painter here and able; the blows chance 0 with no vanilla reason or no temper, never past 0.85");
        });

        // ---------------------------------------------------------------- temperament (rows from TemperamentDefs_Graffiti.xml)
        var rows = new Dictionary<string, RM_Temper>();
        try
        {
            foreach (var li in XDocument.Load(args[0]).Descendants("li"))
            {
                string key = (string)li.Element("trait") ?? (string)li.Element("gene") ?? (string)li.Element("hediff") ?? (string)li.Element("precept");
                if (key == null) continue;
                if (li.Element("degree") != null) key += ":" + (string)li.Element("degree");
                float G(string n, float d) => li.Element(n) != null ? float.Parse((string)li.Element(n), System.Globalization.CultureInfo.InvariantCulture) : d;
                float craft = G("craft", 1f);
                var t = new RM_Temper { numb = li.Element("numb") != null && (string)li.Element("numb") == "true", bad = G("bad", 1f), good = G("good", 1f),
                    fine = G("fine", craft), ugly = G("ugly", craft), temper = G("temper", 1f), paint = G("paint", 1f), offended = G("offended", 1f), neat = (int)G("neat", 0f),
                    lean = li.Element("lean") != null ? (RM_Lean)Enum.Parse(typeof(RM_Lean), (string)li.Element("lean")) : RM_Lean.None };
                rows[key] = t;
            }
        }
        catch (Exception e) { Row("L1_TEMPER_DEFS_READ", new[] { "temperament" }, "fixed", "FAIL", 0, "could not read the temperament rows: " + e.Message); }
        string[] TB = { "temperament", "inv_temperament" };
        Check("L1_TEMPER_PSYCHOPATH_NUMB", TB, "random", () =>
        {
            const int seed = 31; var rng = new Random(seed); var keys = rows.Keys.ToList(); long n = 0;
            for (int i = 0; i < 20000; i++)
            {
                var pick = new List<RM_Temper> { rows["Psychopath"] }; var names = new List<string> { "Psychopath" };
                int extra = rng.Next(5); for (int k = 0; k < extra; k++) { var key = keys[rng.Next(keys.Count)]; pick.Add(rows[key]); names.Add(key); }
                var sh = pick.OrderBy(_ => rng.Next()).ToList();
                var c = K.Combine(sh); n++;
                if (c.bad != 0f || c.good != 0f || c.fine != 0f || c.ugly != 0f || c.offended != 0f || c.lean != RM_Lean.Nothing)
                    return (n, $"seed {seed}: psychopath with {string.Join("+", names)} keeps bad {c.bad} good {c.good} fine {c.fine} ugly {c.ugly} lean {c.lean}", null);
                for (int r = 0; r <= 20; r++) if (K.AnswerOf(RM_Reaction.Humiliated, true, true, true, true, r / 20f, c.lean) != RM_Answer.None) return (n, "a psychopath answers a mockery", null);
            }
            return (n, null, "seed 31, 20000 trait mixes with Psychopath in any order: every mood multiplier 0, no answer: feels nothing from any mark");
        });
        Check("L1_TEMPER_SENSITIVE_BOTH_WAYS", TB, "fixed", () =>
        {
            var plain = K.Combine(new List<RM_Temper>()); long n = 1;
            if (plain.bad != 1f || plain.good != 1f) return (n, $"an ordinary viewer's offsets are scaled ({plain.bad}, {plain.good}): not the def values", null);
            foreach (var key in new[] { "Nerves:-1", "Nerves:-2", "VTE_Anxious" })
            {
                if (!rows.ContainsKey(key)) continue; n++;
                var c = K.Combine(new List<RM_Temper> { rows[key] });
                if (!(c.bad > plain.bad && c.good > plain.good)) return (n, $"{key}: bad {c.bad}, good {c.good}: not more in both directions", null);
            }
            return (n, null, "ordinary viewer x1 (the def values); nervous, volatile and anxious feel more both ways (bad and good > 1)");
        });
        Check("L1_TEMPER_CLEAN_FREAK", TB, "fixed", () =>
        {
            long n = 0; var notes = new List<string>();
            foreach (var key in new[] { "Neurotic:2", "Hygienic:2", "VTE_Neat", "RT_Tidy" })
            {
                if (!rows.ContainsKey(key)) continue; n++;
                var c = K.Combine(new List<RM_Temper> { rows[key] });
                if (c.neat < 2) return (n, $"{key}: neat {c.neat}, cannot break into compulsive cleaning", null);
                notes.Add($"{key} neat {c.neat} bad {c.bad} lean {c.lean}");
            }
            return (n, null, "clean freaks can break (neat 2): " + string.Join("; ", notes) + ". Their EXTRA debuff is bad > 1 only for Neurotic:2; for the others it must come from neat in the caller (GraffitiTemperament), not this table");
        });

        // ---------------------------------------------------------------- scrub protection, raids, going over
        Check("L1_SCRUB_PROTECTION_TABLE", new[] { "scrub_protection", "inv_scrub_protection", "stands_alone_settings" }, "sweep", () =>
        {
            bool P(bool forced, bool on, bool own, bool dev) => K.ProtectsFromAutoClean(forced, on, true, true, false, own, dev);
            string bad = !P(false, true, true, false) ? "own vandal mark auto-cleaned" : !P(false, true, false, true) ? "enemy devotional sigil auto-cleaned" :
                         P(false, true, false, false) ? "hostile vandal mark protected from the cleaner" : P(true, true, true, true) ? "an ordered clean still skips it" :
                         P(false, false, true, true) ? "protection runs with its switch off" : K.ProtectsFromAutoClean(false, true, false, false, true, true, true) ? "a non-mark is protected" : null;
            return (64, bad, "unordered: own and devotional kept, hostile vandal cleaned; ordered: everything cleaned; switch off: nothing protected");
        });
        Check("L1_RAID_EXIT_TAGS", new[] { "raid_mark_troubles", "inv_raid_marks", "stands_alone_settings" }, "sweep", () =>
        {
            long n = 0;
            for (int m = 0; m < 32; m++)
            {
                bool p = (m & 1) != 0, e = (m & 2) != 0, k = (m & 4) != 0, pl = (m & 8) != 0, h = (m & 16) != 0; n++;
                bool want = p && e && k && !pl && h;
                if (K.RaidExitTags(p, e, k, pl, h) != want) return (n, $"painting {p} exitTag {e} known {k} player {pl} hostile {h}: tags {!want}", null);
            }
            bool everTag = false; bool was = false;
            foreach (bool now in new[] { false, false, false }) { if (K.TurnsToLeave(was, now)) everTag = true; was = now; n++; }
            if (everTag) return (n, "a raid that never turns to leave tags", null);
            int departures = 0; was = false;
            foreach (bool now in new[] { false, true, true, true, false, true }) { if (K.TurnsToLeave(was, now)) departures++; was = now; n++; }
            if (departures != 2) return (n, $"two turns to leave counted {departures}", null);
            if (K.ExteriorFace(true, true, true) || K.ExteriorFace(false, true, false) || K.ExteriorFace(false, false, true) || !K.ExteriorFace(false, true, true)) return (n, "an interior face tagged or the exterior refused", null);
            if (K.TerritoryStage(0) != -1 || K.TerritoryStage(1) < 0) return (n, $"territory stage with 0 marks {K.TerritoryStage(0)}, 1 mark {K.TerritoryStage(1)}", null);
            int prev = -1; for (int s = 1; s < 50; s++) { if (K.TerritoryStage(s) < prev) return (n, "more enemy marks trouble less", null); prev = K.TerritoryStage(s); }
            return (n, null, "tags only from a hostile non-player faction with both switches on, only on the turn to leave, only on an exterior face; the trouble is none at 0 enemy marks and grows with them");
        });
        Check("L1_GOING_OVER", new[] { "going_over", "inv_raid_marks" }, "fixed", () =>
        {
            string bad = !K.IsRival(true, false) ? "a different mark on the cell is not gone over" : K.IsRival(false, false) ? "a non-mark is treated as paint to go over" : null;
            return (3, bad, "a different def on the cell is destroyed first; the same def thickens (an enemy's same-def mark over ours keeps ours: bar silent on it)");
        });

        // ---------------------------------------------------------------- variety, the pool
        Check("L1_POOL_PICK_PROPORTIONAL", new[] { "marks_various", "inv_mark_art_set" }, "random", () =>
        {
            const int seed = 123; var rng = new Random(seed); long n = 0;
            for (int run = 0; run < 300; run++)
            {
                int cnt = 1 + rng.Next(12); var w = new List<float>();
                for (int i = 0; i < cnt; i++) w.Add(rng.Next(4) == 0 ? 0f : (float)rng.NextDouble() * 5f);
                float total = K.Total(w); var hits = new int[cnt]; const int draws = 20000;
                for (int d = 0; d < draws; d++) { int ix = K.PickIndex(w, (float)rng.NextDouble() * total); n++; if (total <= 0f) { if (ix != -1) return (n, "an empty pool picks", null); continue; } if (ix < 0 || w[ix] <= 0f) return (n, $"seed {seed} run {run}: picked index {ix} of weight {(ix >= 0 ? w[ix] : -1)}: [{string.Join(",", w)}]", null); hits[ix]++; }
                if (total > 0f) for (int i = 0; i < cnt; i++) { double want = w[i] / total * draws; if (Math.Abs(hits[i] - want) > 6 * Math.Sqrt(want + 1) + 5) return (n, $"seed {seed} run {run}: index {i} weight {w[i]} picked {hits[i]} of {draws}, want ~{want:0}", null); }
            }
            var one = new List<float> { 0f, 0f, 2f, 0f };
            for (int r = 0; r <= 100; r++) { n++; if (K.PickIndex(one, r / 100f * 2f) != 2) return (n, "the pool with all but one def gated off yields another def", null); }
            return (n, null, "seed 123, 300 pools x 20000 draws: picks follow the weights within 6 sigma, a gated-off (zero) def is never picked; all but one gated off -> that one");
        });
        Check("L1_POOL_GATES", new[] { "marks_various", "ideo_sigil", "inv_ideo_sigils" }, "sweep", () =>
        {
            long n = 0;
            for (int m = 0; m < 8; m++) foreach (float w in new[] { -1f, 0f, 0.5f })
            { bool a = (m & 1) != 0, b = (m & 2) != 0, c = (m & 4) != 0; n++; if (K.InPool(a, b, c, w) != (a && b && c && w > 0f)) return (n, $"InPool({a},{b},{c},{w})", null); }
            if (K.MemeGate(true, false, false) || K.MemeGate(true, false, true)) return (n, "a colonist with no ideoligion gets a meme-gated mark (the sigil control)", null);
            if (!K.MemeGate(false, false, false)) return (n, "an ungated mark is closed to a colonist with no ideoligion (standing alone)", null);
            if (K.SkillGate(5, false, 20) || K.SkillGate(5, true, 4) || !K.SkillGate(5, true, 5) || !K.SkillGate(0, false, 0)) return (n, "the skill gate is off", null);
            if (!K.HostilityGate(false, true, true, false, false, false) || K.HostilityGate(true, true, true, true, true, true) || K.HostilityGate(true, true, true, false, false, true)) return (n, "the hostility gate is off", null);
            return (n, null, "a mark joins the pool only through every gate with positive weight; no ideoligion -> no meme-gated sigil, ungated marks still open");
        });

        // ---------------------------------------------------------------- the wall
        string[] SW = { "sits_on_wall", "inv_mark_on_wall" };
        Check("L1_WALL_ONLY_FRONT_FACE_TAKES_PAINT", SW, "sweep", () =>
        {
            long n = 0;
            for (int m = 0; m < 16; m++)
            {
                bool N = (m & 1) != 0, E = (m & 2) != 0, S = (m & 4) != 0, W = (m & 8) != 0; n++;
                int side = K.WallSide(N, E, S, W);
                bool paints = side != K.NoWall && K.SidePaintable(side) && K.PaintsEdgeOn(K.FaceOfSide(side));
                if (paints != N) return (n, $"walls N{N} E{E} S{S} W{W}: side {side}, face {K.FaceOfSide(side)}, paints {paints} (want {N}: only a wall north of the cell)", null);
                if (paints && K.FaceOfSide(side) != K.FaceFront) return (n, "paint on a face that is not the front", null);
            }
            for (int side = -1; side <= 4; side++) { n++; if (K.SidePaintable(side) && K.PaintsEdgeOn(K.FaceOfSide(side)) && side != 0) return (n, $"side {side} takes paint", null); }
            return (n, null, "every neighbour combination: paint only on the wall north of the cell, its front face; edge-on (east/west) and the far side (south) take none");
        });
        Check("L1_WALL_MARK_ON_FACE_AND_OVER_THE_CREASE", SW, "random", () =>
        {
            const int seed = 555; var rng = new Random(seed); long n = 0; const float eps = 1e-4f;
            for (int run = 0; run < 20000; run++)
            {
                int id = rng.Next(), runLen = 1 + rng.Next(5), at = rng.Next(runLen);    // a wall run of runLen cells, anchor at index `at`
                float width = new[] { 0.6f, 1f, 1f, 2f, 3f }[rng.Next(5)];
                float crease = 0.3f + (float)rng.NextDouble() * 0.2f, sideW = 0.15f + (float)rng.NextDouble() * 0.12f;
                K.HandOf(id, width, out float slope, out float scale, out float slide, out float lift, out bool flip);
                Func<int, int> links = k => { int i = at + k; if (i < 0 || i >= runLen) return -1; return (i > 0 ? K.LinkW : 0) | (i < runLen - 1 ? K.LinkE : 0); };
                var pieces = K.MarkPieces(links, K.FaceFront, crease, sideW, width * scale, K.ClimbHeight * scale, slide, slope, lift, flip);
                n++;
                if (pieces.Count == 0) return (n, $"seed {seed} run {run}: no paint at all (run {runLen}, anchor {at}, width {width})", null);
                bool face = false, top = false;
                foreach (var p in pieces)
                {
                    if (links(p.k) < 0) return (n, $"seed {seed} run {run}: a piece at k {p.k} where there is no wall", null);
                    foreach (var v in p.poly)
                    {
                        float lx = v.x - p.k;
                        if (v.z < -eps) return (n, $"seed {seed} run {run}: vertex z {v.z} below the wall: on the floor cell (id {id}, width {width}, crease {crease})", null);
                        if (lx < -eps || lx > 1f + eps || v.z > 1f + eps) return (n, $"seed {seed} run {run}: vertex ({v.x},{v.z}) outside its wall cell k {p.k}", null);
                        if (!p.onTop && v.z > crease + eps) return (n, $"seed {seed} run {run}: a face piece above the crease", null);
                        if (p.onTop && v.z < crease - eps) return (n, $"seed {seed} run {run}: a top piece below the crease", null);
                    }
                    if (p.onTop) top = true; else face = true;
                }
                if (!face || !top) return (n, $"seed {seed} run {run}: face {face} top {top}: a full-size mark does not climb over the crease (id {id}, scale {scale}, lift {lift})", null);
            }
            // a wall whose own south neighbour is wall has no front face: nothing drawn there
            n++; if (K.MarkPieces(k => k == 0 ? K.LinkS : -1, K.FaceFront, 0.4f, 0.22f, 1f, 1.2f, 0f, 0f, 0.5f, false).Count != 0) return (n, "paint on a front face that does not exist", null);
            return (n, null, "seed 555, 20000 hands on runs of 1-5 wall cells: every vertex on its wall cell (never the floor), face pieces below the crease and top pieces above it, every full-size mark on both, nothing past the wall's end");
        });

        // ---------------------------------------------------------------- settings, cadence, budgets
        Check("L1_SETTINGS_PACE_SWEEP", new[] { "stands_alone_settings", "inv_settings", "mark_appears" }, "sweep", () =>
        {
            long n = 0;
            for (int s = -2000; s <= 6000; s++)
            {
                n++; int iv = K.PaintInterval(s);
                if (iv < 1 || iv < K.MinPaintInterval || iv > K.MaxPaintInterval) return (n, $"setting {s}: interval {iv}", null);
                if (s >= paceMin && s <= paceMax && iv != s) return (n, $"slider value {s} is not honoured ({iv})", null);
                foreach (var f in Forms) if (K.PaintTicks(f, s) <= 0) return (n, $"{f} at setting {s}: {K.PaintTicks(f, s)} work ticks", null);
            }
            return (n, paceDefault >= paceMin && paceDefault <= paceMax ? null : $"shipped pace {paceDefault} outside {paceMin}..{paceMax}",
                    $"pace -2000..6000: interval in [{K.MinPaintInterval},{K.MaxPaintInterval}], never 0, slider {paceMin}..{paceMax} honoured exactly, shipped {paceDefault}; every form takes positive work");
        });
        Check("L1_SETTINGS_EACH_SWITCH_STOPS_ITS_OWN", new[] { "stands_alone_settings", "inv_settings" }, "sweep", () =>
        {
            long n = 0;
            for (int m = 0; m < 32; m++)
            {
                bool painting = (m & 1) != 0, exitTag = (m & 2) != 0, viewer = (m & 4) != 0, protect = (m & 8) != 0, pressure = (m & 16) != 0; n++;
                bool tags = K.RaidExitTags(painting, exitTag, true, false, true), feels = K.ThoughtActive(viewer, true, true, true);
                bool kept = K.ProtectsFromAutoClean(false, protect, true, true, false, true, false); bool pushed = K.PressureFactor(pressure, 1, 1.5f) > 1f;
                if (tags != (painting && exitTag) || feels != viewer || kept != protect || pushed != pressure)
                    return (n, $"painting {painting} exitTag {exitTag} viewer {viewer} protect {protect} pressure {pressure}: tags {tags} feels {feels} kept {kept} pushed {pushed}", null);
            }
            return (n, null, "32 switch combinations: exit tags need painting and exit tagging, viewer thoughts their switch, protection its switch, the push its switch, each independent of the others; back on restores it");
        });
        Check("L1_BUDGET_NEVER_PAST", new[] { "stories_not_tax", "inv_viewer_mood" }, "random", () =>
        {
            const int seed = 2718; var rng = new Random(seed); long n = 0;
            for (int run = 0; run < 20000; run++)
            {
                float good = (float)(rng.NextDouble() * 1.5), budget = new[] { K.BadMoodBudget, K.VictimMoodBudget, K.GoodMoodBudget, K.AmbientBudget(good) }[rng.Next(4)], total = 0f;
                for (int k = 0; k < 40; k++)
                {
                    float off = (float)(rng.NextDouble() * 6); float f = K.FitBudget(total, off, budget); n++;
                    if (f < 0f || f > 1f) return (n, $"seed {seed}: kept factor {f}", null);
                    total += off * f;
                    if (total > budget + 1e-3f) return (n, $"seed {seed} run {run}: memories sum {total} past budget {budget}", null);
                }
            }
            for (float g = 0f; g <= 3f; g += 0.01f) { n++; if (K.AmbientBudget(g) > K.AmbientMoodBudget + 1e-6f) return (n, $"ambient budget {K.AmbientBudget(g)} past +3 at good {g}", null); }
            return (n, null, $"seed 2718, 20000 pawns x 40 memories: never past their budget (bad {K.BadMoodBudget}, victim {K.VictimMoodBudget}, good {K.GoodMoodBudget}); ordinary wall art never past +{K.AmbientMoodBudget} for any temperament");
        });
        Check("L1_OWN_FUN_SITTING", new[] { "own_fun", "inv_joy_and_idle_tag" }, "sweep", () =>
        {
            long n = 0;
            foreach (var f in Forms) { n++; if (K.SpreeForm(f) && !K.JoyForm(f)) return (n, $"{f} in the spree pool but not the joy pool", null); }
            if (!Forms.Any(K.JoyForm)) return (n, "no form is recreation", null);
            for (int made = 0; made <= 10; made++) for (int j = 0; j <= 100; j++)
            { n++; bool go = K.SittingContinues(made, false, j / 100f); if (go && (made >= K.MaxMarksPerJoySitting || j / 100f >= K.JoySittingFull)) return (n, $"a joy sitting goes on after {made} marks at joy {j / 100f}", null); }
            return (n, null, $"painting is recreation (joy pool {Forms.Count(K.JoyForm)} forms); a sitting ends at {K.MaxMarksPerJoySitting} marks or joy {K.JoySittingFull}; a spree keeps going");
        });
        Check("L1_SPREE_NEVER_AN_EMPTY_PICK", new[] { "mark_appears", "inv_spree" }, "random", () =>
        {
            const int seed = 8; var rng = new Random(seed); long n = 0;
            for (int run = 0; run < 50000; run++)
            {
                int c = rng.Next(40); var cells = new List<RM_MarkCell>(); for (int i = 0; i < c; i++) cells.Add(new RM_MarkCell(rng.Next(3) > 0, rng.Next(2) == 0));
                var g = K.Gather(cells); n++;
                bool anyUsable = cells.Any(x => x.usable), anyBare = cells.Any(x => x.usable && !x.marked);
                if (anyUsable && g.Count == 0) return (n, $"seed {seed} run {run}: usable cells but nothing to paint", null);
                if (g.Any(i => !cells[i].usable)) return (n, "an unusable cell offered", null);
                if (anyBare && g.Any(i => cells[i].marked)) return (n, "a marked cell offered while a bare one stands", null);
                if (g.Count > K.MaxCandidates) return (n, "too many candidates", null);
            }
            return (n, null, "seed 8, 50000 scans: a usable wall cell always yields a pick, bare wall first, never an unusable cell");
        });
        Check("L1_BREACH_LURE_NEAREST", new[] { "inv_breach_bias" }, "random", () =>
        {
            const int seed = 66; var rng = new Random(seed); long n = 0;
            for (int run = 0; run < 20000; run++)
            {
                int c = rng.Next(8); var d = new List<long>(); var key = new List<int>();
                for (int i = 0; i < c; i++) { d.Add(rng.Next(5)); key.Add(rng.Next(100)); }
                int b = K.ChooseLure(d, key); n++;
                if (c == 0) { if (b != -1) return (n, "a lure from nothing", null); continue; }
                if (d.Any(x => x < d[b]) || Enumerable.Range(0, c).Any(i => d[i] == d[b] && key[i] < key[b])) return (n, $"seed {seed} run {run}: not the nearest, lowest key", null);
            }
            return (n, null, "seed 66: the raid heads for the nearest lure, ties by key; none with no lure");
        });

        // ---------------------------------------------------------------- game-side bars: no kernel covers them
        void NK(string id, string[] bars, string why) => Row(id, bars, "not_kernel", "UNSETTLED", 0, why);
        NK("L1_NK_ART_READING", new[] { "reads_at_play_zoom", "punk_register", "no_english", "not_dirt", "inv_mark_art_set" }, "textures judged at 64 px by a judge that did not make them; no kernel decides it. Settles it: the gallery and dirt pages at play zoom read by a naive judge, with the planted controls (stage 6)");
        NK("L1_NK_IDEO_SIGIL_ICON", new[] { "ideo_sigil", "inv_ideo_sigils" }, "the sigil's icon and tint are read off a live Ideo (WallPlane.PaintedIcon); the kernel holds only the meme gate (L1_POOL_GATES). Settles it: graffiti_v1_live_proof A3 on a quicktest map");
        NK("L1_NK_SPREE_LIVE_MARKS", new[] { "mark_appears", "marks_various", "inv_spree" }, "marks appearing after a live spree and their def/variant spread over six lanes is runtime state; the kernel parts pass (L1_SPREE_NEVER_AN_EMPTY_PICK, L1_POOL_PICK_PROPORTIONAL). Settles it: the six-lane spree scene, 3000 ticks");
        NK("L1_NK_PLAYER_ORDERS", new[] { "player_orders", "inv_player_orders" }, "a designator, a map component and two work givers; no kernel. Settles it: graffiti_v1_live_proof A7");
        NK("L1_NK_PAINT_DIES_WITH_WALL", new[] { "paint_dies_with_wall", "inv_wall_loss" }, "a Harmony patch on the wall's despawn (WallLossPatch.cs); no kernel. Settles it: deconstruct and destroy a painted wall live");
        NK("L1_NK_WEATHER_PERMANENT", new[] { "weathering_bounds_marks", "inv_weathering" }, "the permanent flag and the roofed reading live in Filth_Mark (the kernel takes `outdoors` as given): the caller is read in lane 2");
        NK("L1_NK_VISIT_ONCE_PER_MARK", new[] { "visitors", "inv_visitors" }, "the kernel caps a visit's total (L1_VISIT_INSULT_ONCE_PER_VISIT); that each mark is charged once per visit, and that a visit is one party, is GraffitiSocial's bookkeeping. Settles it: the trader scene, repeated passes");
        NK("L1_NK_REREAD_OPINION_ONCE", new[] { "rereads_daily", "mockery", "inv_viewer_mood" }, "opinion moving once on the first read, and the 60000-tick reread gate's use, are in GraffitiSocial; read in lane 2, proven live by the two-day walk past one mockery");
        NK("L1_NK_FIGHTS_RESTRICTIONS", new[] { "fights_reasons" }, "drafted and area-restricted pawns never leaving to fight, and the social switch stopping confrontations, are job-giver checks; no kernel. Settles it: the feud scene with the subject drafted and restricted");
        NK("L1_NK_TEMPER_LIVE", new[] { "temperament", "inv_temperament" }, "the thought a psychopath holds (none, not a zero one) and the clean freak's break running the graffiti cleaning job are game-side (GraffitiTemperament, GraffitiCompulsiveClean). Settles it: the four-viewer scene");
        NK("L1_NK_RAID_LIVE", new[] { "raid_mark_troubles", "going_over", "raider_pressure", "inv_raid_marks", "inv_raider_future_marks" }, "the exit tagger on Lord toils, the territory thought, the pressure letter and its look-target, and the raid points or return incident actually reaching the storyteller are game-side (RaidExitTagger, RaiderPressure.cs); read in lane 2, proven live by the two-faction raid scene");
        NK("L1_NK_STANDALONE_RELOAD", new[] { "stands_alone_settings", "inv_standalone", "inv_settings" }, "no ideoligion, save and reload keeping every mark field, and the social / messages / breach switches are game-side; settles it: the settings sweep scene and a save round trip");
        NK("L1_NK_SOAK_AND_WALK", new[] { "stories_not_tax", "walk_lived_in" }, "three in-game weeks and a lived-in walk on the full list; the kernel budgets pass (L1_BUDGET_NEVER_PAST). Settles it: the soak and the walk (stage 6+)");
        NK("L1_NK_SOCIAL_LIVE", new[] { "mockery", "tribute_memorial", "answer_wall", "inv_social_layer", "own_fun", "inv_joy_and_idle_tag", "art_skill" }, "who is the subject, the opinion moves, the grief thought, each answer job running to completion, the joy job and maker thought, and the room beauty a skill-2 and a skill-16 hand actually leave are runtime state; the kernel tables pass above");
        return fails > 0 ? 1 : 0;
    }
}
