// Blind lane 1, Graffiti 0.1.0, cycle 1: the judge's own tests of RM_GraffitiKernel, written from the bars (tree.json, sheet.md,
// plan.md), the shipped settings (RM_GraffitiMod.cs, passed in GR_* variables) and the per-type values (Defs, passed as a TSV in
// GR_DEFS). Written before any builder test, journal or evidence was opened. One JSON row per line on stdout.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using RimMandrake.Graffiti;
using K = RimMandrake.Graffiti.RM_GraffitiKernel;

static class BlindLane1
{
    static int fails;

    static string Esc(string s) { return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " "); }

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\":\"" + id + "\",\"bars\":[" + string.Join(",", bars.Select(b => "\"" + b + "\"")) + "],\"kind\":\"" + kind +
            "\",\"verdict\":\"" + verdict + "\",\"cases\":" + cases + ",\"detail\":\"" + Esc(detail) + "\"}");
    }

    static string[] B(params string[] b) { return b; }
    static string F(float f) { return f.ToString("0.####", CultureInfo.InvariantCulture); }

    static string Env(string k, string d) { string v = Environment.GetEnvironmentVariable(k); return string.IsNullOrEmpty(v) ? d : v; }

    static readonly GraffitiForm[] Forms = (GraffitiForm[])Enum.GetValues(typeof(GraffitiForm));

    // ------------------------------------------------------------------ weathering_bounds_marks

    static void Weathering()
    {
        // fixed+sweep: WeatherDays roofed exceeds unroofed for every form, craft, id
        int n = 0; string bad = null;
        foreach (var f in Forms) for (int q = -1; q <= 7; q++) for (int id = 0; id < 3000; id += 7)
        {
            n++;
            float inD = K.WeatherDays(f, q, false, id), outD = K.WeatherDays(f, q, true, id);
            if (!(inD > outD) && bad == null) bad = "form " + f + " craft " + q + " id " + id + " roofed " + F(inD) + " outdoors " + F(outD);
            if ((!(outD > 0f) || float.IsInfinity(inD) || float.IsNaN(inD) || inD > 365f) && bad == null) bad = "non-finite or non-positive life: form " + f + " craft " + q + " id " + id + " in " + F(inD) + " out " + F(outD);
        }
        Row("weather_roofed_outlasts_outdoors", B("weathering_bounds_marks", "inv_weathering"), "sweep", bad == null ? "PASS" : "FAIL", n,
            bad ?? "every form x craft -1..7 x id 0..2999 step 7: roofed days > outdoor days, both finite, positive and under a year (marks always weather)");

        // fade curve: 0 before 60% of life, 1 at end and after, monotone, linear 0..1 over the last 40%
        var rnd = new Random(1101); n = 0; bad = null;
        for (int i = 0; i < 20000; i++)
        {
            float life = (float)(rnd.NextDouble() * 80 + 0.5); float age = (float)(rnd.NextDouble() * life * 1.5);
            float fa = K.WeatherFade(age, life); n++;
            float frac = age / life;
            float want = frac < 0.6f ? 0f : (frac >= 1f ? 1f : (frac - 0.6f) / 0.4f);
            if (Math.Abs(fa - want) > 1e-3f && bad == null) bad = "seed 1101 case " + i + " life " + F(life) + " age " + F(age) + " fade " + F(fa) + " want " + F(want);
            float fb = K.WeatherFade(age + 0.01f, life);
            if (fb + 1e-6f < fa && bad == null) bad = "not monotone: seed 1101 life " + F(life) + " age " + F(age);
        }
        Row("weather_fade_last_forty_percent", B("weathering_bounds_marks", "inv_weathering"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seed 1101, 20000 (life, age) pairs: alpha 1 (fade 0) before 60% of life, fade linear to 1 at end of life, 1 after, monotone");

        // steps: 0 fresh, 4 gone, monotone
        bad = null; int prev = 0; n = 0;
        for (int i = 0; i <= 1000; i++) { float fd = i / 1000f; int s = K.WeatherStep(fd); n++; if ((s < prev || s < 0 || s > 4) && bad == null) bad = "fade " + F(fd) + " step " + s; prev = s; }
        if (K.WeatherStep(0f) != 0 || K.WeatherStep(1f) != 4) bad = bad ?? ("ends " + K.WeatherStep(0f) + "/" + K.WeatherStep(1f));
        Row("weather_step_bounded", B("weathering_bounds_marks"), "fixed", bad == null ? "PASS" : "FAIL", n, bad ?? "WeatherStep 0 at fade 0, 4 at fade 1, monotone over 1001 fades");

        // a zero-life call never fades: the kernel's guard. Whether "permanent never fades" rides on it is game-side.
        Row("weather_permanent_is_game_side", B("weathering_bounds_marks"), "not_kernel", "UNSETTLED", 1,
            "permanence (Filth_Mark.permanent) is not in the kernel: WeatherFade(age, 0) returns 0 (never fades) but nothing in the kernel says a permanent mark takes that path; owed to the caller read in lane 2 / Stage 6");

        // the oracle's craft clause: a good writer's paint lasts longer (monotone in craft) per id
        bad = null; n = 0;
        foreach (var f in Forms) foreach (bool o in new[] { true, false }) for (int id = 0; id < 500; id++)
        {
            float last = -1f;
            for (int q = 0; q <= 6; q++) { float d = K.WeatherDays(f, q, o, id); n++; if (d + 1e-5f < last && bad == null) bad = "form " + f + " id " + id + " craft " + q + " days " + F(d) + " < " + F(last); last = d; }
        }
        Row("weather_craft_monotone", B("weathering_bounds_marks"), "sweep", bad == null ? "PASS" : "FAIL", n, bad ?? "days never fall as craft rises (Awful..Legendary), every form, both roofings, ids 0..499");
    }

    // ------------------------------------------------------------------ art skill and ugliness

    static void ArtSkill(List<string[]> defs)
    {
        string bad = null; int n = 0;
        float last = float.NegativeInfinity;
        for (int q = 0; q <= 6; q++) { float b = K.CraftBeauty(q); n++; if (!(b > last) && bad == null) bad = "CraftBeauty not rising at " + q; last = b; }
        if (!(K.CraftBeauty(K.Awful) < 0 && K.CraftBeauty(K.Poor) < 0 && K.CraftBeauty(K.Normal) == 0 && K.CraftBeauty(K.Good) > 0)) bad = bad ?? "signs wrong";
        Row("craft_beauty_both_ways", B("art_skill", "inv_beauty_and_craft"), "fixed", bad == null ? "PASS" : "FAIL", n,
            bad ?? "CraftBeauty strictly rises Awful..Legendary; Awful/Poor < 0 (harms a room), Normal 0 (the control: craft forced Normal gives equal beauty for every mark), Good+ > 0");

        bad = null; n = 0;
        for (int q = 0; q <= 6; q++)
        {
            n++; int st = K.CraftStage(q, out bool ugly);
            bool wantUgly = q <= K.Poor;
            if (ugly != wantUgly && bad == null) bad = "q " + q + " ugly " + ugly;
            if (q == K.Normal && st != -1 && bad == null) bad = "Normal gives a craft thought";
            if (q != K.Normal && st < 0 && bad == null) bad = "q " + q + " gives no craft thought";
        }
        if (!(K.CraftStage(K.Awful, out _) > K.CraftStage(K.Poor, out _))) bad = bad ?? "awful not worse stage than poor";
        int prev = -1; for (int q = K.Good; q <= K.Legendary; q++) { int s = K.CraftStage(q, out _); if (s <= prev && bad == null) bad = "fine-art stage not rising at " + q; prev = s; }
        Row("craft_thought_sign", B("art_skill", "inv_viewer_mood"), "fixed", bad == null ? "PASS" : "FAIL", n,
            bad ?? "CraftStage: Awful/Poor give the ugly thought (awful stronger), Normal none, Good..Legendary the fine-art thought rising");

        // a skilled slander angers and pleases at once: the meaning reaction and the craft thought are independent
        var subj = new RM_Viewer { isSubject = true, ownFaction = true };
        var r = K.ReactionOf(RM_Meaning.Mockery, subj);
        int stg = K.CraftStage(K.Excellent, out bool ug);
        bool ok = r == RM_Reaction.Humiliated && stg >= 0 && !ug;
        // and the budget keeps the two signs apart: a full bad budget leaves the good one untouched
        float keepGood = K.FitBudget(0f, 2f, K.GoodMoodBudget);
        ok &= keepGood == 1f;
        Row("skilled_slander_two_thoughts", B("art_skill"), "fixed", ok ? "PASS" : "FAIL", 1,
            "subject of an Excellent mockery: reaction " + r + " (anger) and craft stage " + stg + " ugly " + ug + " (beauty); good budget untouched by bad memories (FitBudget keeps " + F(keepGood) + "); whether the game gives both memories rather than netting them is game-side");

        // ceilings: a scrawl is never better than poor; tally/glyph never above Normal
        bad = null;
        if (K.CraftCeiling(GraffitiForm.Scrawl) > K.Poor) bad = "scrawl ceiling " + K.CraftCeiling(GraffitiForm.Scrawl);
        if (K.CraftCeiling(GraffitiForm.Glyph) > K.Normal) bad = bad ?? "glyph ceiling above normal";
        Row("craft_ceiling_scrawl_poor", B("ugliness_visible", "art_skill"), "fixed", bad == null ? "PASS" : "FAIL", Forms.Length,
            bad ?? "ceilings: " + string.Join(", ", Forms.Select(f => f + " " + K.CraftCeiling(f))));

        // ugliness_visible's control: the def stats are -15 (scrawl) and -3 (tally)
        var vandal = defs.FirstOrDefault(d => d[0] == "RM_Graffiti_Vandal"); var tally = defs.FirstOrDefault(d => d[0] == "RM_Graffiti_TallyMarks");
        ok = vandal != null && tally != null && vandal[4] == "-15" && tally[4] == "-3" && vandal[1] == "Scrawl";
        Row("ugliness_def_stats", B("ugliness_visible"), "fixed", ok ? "PASS" : "FAIL", 1,
            "defs: Vandal form " + (vandal == null ? "?" : vandal[1]) + " Beauty " + (vandal == null ? "?" : vandal[4]) + ", TallyMarks form " + (tally == null ? "?" : tally[1]) + " Beauty " + (tally == null ? "?" : tally[4]));

        // the stat a player inspects: if a mark's net beauty is CraftBeauty alone (the kernel's doc), a best scrawl (-2.5) beats an awful tally (-6)
        float bestScrawl = K.CraftBeauty(K.CraftCeiling(GraffitiForm.Scrawl)), worstTally = K.CraftBeauty(K.Awful);
        Row("ugliness_craft_vs_def_stat", B("ugliness_visible"), "info", "INFO", 1,
            "kernel CraftBeauty says it is 'a mark's net beauty in its cell by craft': best scrawl " + F(bestScrawl) + " vs awful tally " + F(worstTally) +
            "; if the game uses craft beauty alone, the def stat -15 vs -3 is not what a player inspects and an awful tally can be uglier than a scrawl. How Filth_Mark.GetBeauty combines them is for lane 2");

        Row("skill_to_quality_game_side", B("art_skill"), "not_kernel", "UNSETTLED", 1,
            "the kernel has no Artistic level -> craft quality map (CraftCeiling caps it, FormAffinity steers the pick); skill 2 vs 16 reaching beauty is game-side (StatPart / paint job)");
    }

    // ------------------------------------------------------------------ the pool: marks_various, ideo_sigil

    static void Pool(List<string[]> defs)
    {
        // defs rows: defName, form, poolWeight, minArtistic, beauty, memeGated
        var spree = defs.Where(d => Enum.TryParse(d[1], out GraffitiForm f) && K.SpreeForm(f)).ToList();
        var joy = defs.Where(d => Enum.TryParse(d[1], out GraffitiForm f) && K.JoyForm(f)).ToList();
        string bad = null; int n = 0;
        var rnd = new Random(2202);
        int minDistinct = int.MaxValue; string worst = "";
        for (int lvl = 0; lvl <= 20; lvl++) foreach (bool hasIdeo in new[] { false, true })
        {
            var w = new List<float>();
            foreach (var d in spree)
            {
                Enum.TryParse(d[1], out GraffitiForm f);
                bool meme = K.MemeGate(d[5] == "1", hasIdeo, false);
                bool skill = K.SkillGate(int.Parse(d[3]), true, lvl);
                float pw = float.Parse(d[2], CultureInfo.InvariantCulture) * K.FormAffinity(f, lvl);
                w.Add(K.InPool(meme, skill, true, pw) ? pw : 0f);
            }
            var seen = new HashSet<int>();
            float tot = K.Total(w);
            for (int i = 0; i < 400; i++) { int p = K.PickIndex(w, (float)(rnd.NextDouble() * tot)); n++; if (p < 0 || w[p] <= 0f) { if (bad == null) bad = "picked a zero weight at level " + lvl; } else seen.Add(p); }
            if (seen.Count < minDistinct) { minDistinct = seen.Count; worst = "level " + lvl + " ideo " + hasIdeo; }
        }
        if (minDistinct < 3) bad = bad ?? ("only " + minDistinct + " distinct spree defs at " + worst);
        Row("pool_spree_variety", B("marks_various", "inv_mark_art_set", "inv_spree"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seed 2202: spree pool from " + spree.Count + " shipped spree-form defs, levels 0..20, with/without ideo: at least " + minDistinct + " distinct defs in 400 picks at every level (bar asks 3)");

        // control: all but one gated off -> one def
        bad = null; n = 0;
        for (int keep = 0; keep < spree.Count; keep++)
        {
            var w = spree.Select((d, i) => i == keep ? 1f : 0f).ToList();
            for (int i = 0; i < 50; i++) { int p = K.PickIndex(w, (float)(rnd.NextDouble() * K.Total(w))); n++; if (p != keep && bad == null) bad = "kept " + keep + " got " + p; }
        }
        Row("pool_one_def_control", B("marks_various"), "random", bad == null ? "PASS" : "FAIL", n, bad ?? "seed 2202 cont.: with every def but one at weight 0 the pick is always that one");

        // PickIndex distribution follows the weights; empty / zero pools give -1; edges
        bad = null; n = 0; List<float> failW = null; int failSeed = 0;
        for (int seed = 0; seed < 200 && failW == null; seed++)
        {
            var r = new Random(3300 + seed);
            var w = Enumerable.Range(0, 1 + r.Next(8)).Select(_ => r.NextDouble() < 0.25 ? 0f : (float)r.NextDouble() * 5f).ToList();
            if (!CheckPick(w, r, out string why)) { failW = w; failSeed = 3300 + seed; bad = why; }
            n++;
        }
        if (failW != null) { failW = Shrink(failW, ww => !CheckPick(ww, new Random(failSeed), out _)); bad += " shrunk weights [" + string.Join(",", failW.Select(F)) + "] seed " + failSeed; }
        if (K.PickIndex(new List<float>(), 0f) != -1 || K.PickIndex(new List<float> { 0f, -1f }, 0f) != -1) bad = bad ?? "non-empty answer for an empty pool";
        if (K.PickIndex(new List<float> { 0f, 2f, 0f }, 0f) != 1) bad = bad ?? "roll 0 landed on a leading zero";
        if (K.PickIndex(new List<float> { 1f, 2f, 0f }, 3.0001f) != 1) bad = bad ?? "roll past total did not land on the last positive";
        Row("pick_follows_weights", B("marks_various"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seeds 3300..3499: 20000 rolls each, picked share within 0.02 of weight share, zero/negative weights never picked; empty pool -1; roll 0 skips leading zeros; roll past total -> last positive");

        // the joy pool: a piece only from Artistic 4 (its minArtistic), and the planned forms appear
        var piece = joy.FirstOrDefault(d => d[1] == "Piece");
        bool ok = piece != null && !K.SkillGate(int.Parse(piece[3]), true, int.Parse(piece[3]) - 1) && K.SkillGate(int.Parse(piece[3]), true, int.Parse(piece[3])) && !K.SkillGate(1, false, 20);
        Row("skill_gate_piece", B("marks_various", "art_skill"), "fixed", ok ? "PASS" : "FAIL", 3, "Piece minArtistic " + (piece == null ? "?" : piece[3]) + " gates below it, opens at it; a pawn with no skill record fails a real requirement");

        // meme gate: gated glyphs need an ideo holding the meme
        ok = K.MemeGate(false, false, false) && !K.MemeGate(true, false, true) && !K.MemeGate(true, true, false) && K.MemeGate(true, true, true);
        Row("meme_gate", B("ideo_sigil", "inv_ideo_sigils"), "fixed", ok ? "PASS" : "FAIL", 4, "MemeGate truth table: ungated open; gated needs ideo and a held meme");

        // ideo_sigil control: no ideo -> no sigil in the pool. The sigil defs carry no requiresAnyMeme, so MemeGate opens for them.
        var sig = defs.Where(d => d[1] == "Sigil").ToList();
        bool anyGated = sig.Any(d => d[5] == "1");
        Row("sigil_no_ideo_control", B("ideo_sigil"), "not_kernel", "UNSETTLED", sig.Count,
            "the " + sig.Count + " Sigil defs carry requiresAnyMeme " + (anyGated ? "on some" : "on none") + ", so the kernel's MemeGate passes them for a pawn with no ideo; the 'no ideoligion, no sigil' control must live in the caller (GraffitiPool) or the sigil drawer: lane 2");

        // gather prefers bare wall, at most 12
        bad = null; n = 0; var rg = new Random(4404);
        for (int t = 0; t < 3000; t++)
        {
            var cells = Enumerable.Range(0, rg.Next(40)).Select(_ => new RM_MarkCell(rg.NextDouble() < 0.8, rg.NextDouble() < 0.5)).ToList();
            var g = K.Gather(cells); n++;
            bool anyBare = cells.Any(c => c.usable && !c.marked);
            if (g.Count > K.MaxCandidates || g.Any(i => !cells[i].usable) || (anyBare && g.Any(i => cells[i].marked)) || (!anyBare && cells.Any(c => c.usable) && g.Count == 0)) { bad = bad ?? ("seed 4404 case " + t); }
        }
        Row("gather_bare_first", B("mark_appears", "inv_spree"), "random", bad == null ? "PASS" : "FAIL", n, bad ?? "seed 4404, 3000 scans: candidates usable, at most 12, bare cells whenever any exist, never empty when a usable cell exists");
    }

    static bool CheckPick(List<float> w, Random r, out string why)
    {
        why = null; float tot = K.Total(w);
        if (tot <= 0f) { if (K.PickIndex(w, 0f) != -1) { why = "zero pool not -1"; return false; } return true; }
        var c = new int[w.Count]; int N = 20000;
        for (int i = 0; i < N; i++) { int p = K.PickIndex(w, (float)(r.NextDouble() * tot)); if (p < 0 || w[p] <= 0f) { why = "picked index " + p; return false; } c[p]++; }
        for (int i = 0; i < w.Count; i++) { float want = w[i] > 0 ? w[i] / tot : 0f; if (Math.Abs(c[i] / (float)N - want) > 0.02f) { why = "share " + i + " " + F(c[i] / (float)N) + " want " + F(want); return false; } }
        return true;
    }

    static List<float> Shrink(List<float> w, Func<List<float>, bool> fails)
    {
        bool changed = true;
        while (changed)
        {
            changed = false;
            for (int i = 0; i < w.Count; i++) { var t = new List<float>(w); t.RemoveAt(i); if (t.Count > 0 && fails(t)) { w = t; changed = true; break; } }
        }
        return w;
    }

    // ------------------------------------------------------------------ the wall: sits_on_wall

    static void Wall()
    {
        // which cells take paint: only one with a wall north of it (face-on); edge-on and far side never
        string bad = null; int n = 0;
        for (int m = 0; m < 16; m++)
        {
            bool N = (m & 1) != 0, E = (m & 2) != 0, S = (m & 4) != 0, W = (m & 8) != 0;
            int side = K.WallSide(N, E, S, W); n++;
            bool paints = side != K.NoWall && K.SidePaintable(side) && K.PaintsEdgeOn(K.FaceOfSide(side));
            if (paints != N && bad == null) bad = "N" + N + " E" + E + " S" + S + " W" + W + " side " + side + " paints " + paints;
            if (paints && K.FaceOfSide(side) != K.FaceFront && bad == null) bad = "paints a non-front face";
        }
        Row("wall_choice_front_only", B("sits_on_wall", "inv_mark_on_wall"), "sweep", bad == null ? "PASS" : "FAIL", n,
            bad ?? "all 16 neighbour sets: a cell takes paint iff a wall stands north of it (front face); east/west-only is edge-on and takes none; south-only (far side) is not paintable");

        // geometry: every piece lies on its cell's face or top, never below the face foot; full-size marks climb onto the top
        bad = null; n = 0; var rnd = new Random(5505); int climbed = 0, full = 0;
        for (int t = 0; t < 4000; t++)
        {
            int runL = rnd.Next(0, 4), runR = rnd.Next(0, 4);
            Func<int, int> links = k => k < -runL || k > runR ? -1 : ((k > -runL ? K.LinkW : 0) | (k < runR ? K.LinkE : 0));
            float crease = 0.3f + (float)rnd.NextDouble() * 0.2f, sideW = 0.15f + (float)rnd.NextDouble() * 0.1f;
            float width = 0.4f + (float)rnd.NextDouble() * 2.6f; bool isFull = rnd.NextDouble() < 0.5;
            float height = isFull ? K.ClimbHeight : 0.2f + (float)rnd.NextDouble() * 1.0f;
            K.HandOf(rnd.Next(), width, out float slope, out float scale, out float slide, out float lift, out bool flip);
            var pcs = K.MarkPieces(links, K.FaceFront, crease, sideW, width * scale, height, slide, slope, lift, flip); n++;
            if (pcs.Count == 0 && bad == null) bad = "seed 5505 case " + t + ": no pieces";
            bool top = false;
            foreach (var p in pcs)
            {
                if (p.k < -runL || p.k > runR) { bad = bad ?? ("seed 5505 case " + t + ": piece on cell " + p.k + " with no wall"); continue; }
                foreach (var v in p.poly)
                {
                    if (v.x < p.k - 1e-3f || v.x > p.k + 1 + 1e-3f) bad = bad ?? ("seed 5505 case " + t + ": x " + F(v.x) + " off cell " + p.k);
                    if (v.z < K.RimZ - 1e-3f) bad = bad ?? ("seed 5505 case " + t + ": z " + F(v.z) + " below the face foot (floor)");
                    if (v.z > 1f + 1e-3f) bad = bad ?? ("seed 5505 case " + t + ": z " + F(v.z) + " past the wall top");
                    if (p.onTop && v.z < crease - 1e-3f) bad = bad ?? ("seed 5505 case " + t + ": top piece below crease");
                    if (!p.onTop && v.z > crease + 1e-3f) bad = bad ?? ("seed 5505 case " + t + ": face piece above crease");
                }
                top |= p.onTop;
            }
            if (isFull) { full++; if (top) climbed++; }
        }
        if (climbed != full) bad = bad ?? ("only " + climbed + " of " + full + " full-size marks climb onto the top");
        Row("wall_pieces_on_face_and_top", B("sits_on_wall", "inv_mark_on_wall"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seed 5505, 4000 marks on random runs: every piece on a walled cell, inside x [k,k+1], z from the face foot (RimZ) to the top, face pieces under the crease, top pieces over it; " + climbed + "/" + full + " full-size marks climb over the crease");

        // the hidden face and no-wall draw nothing
        bool ok = K.MarkPieces(k => K.LinkE | K.LinkW, K.FaceHidden, 0.4f, 0.22f, 1f, 1.2f, 0f, 0f, 0.5f, false).Count == 0
               && K.MarkPieces(k => -1, K.FaceFront, 0.4f, 0.22f, 1f, 1.2f, 0f, 0f, 0.5f, false).Count == 0;
        Row("wall_hidden_face_empty", B("sits_on_wall"), "fixed", ok ? "PASS" : "FAIL", 2, "MarkPieces draws nothing on the hidden (far) face and nothing where no wall stands");

        Row("wall_far_side_order_game_side", B("sits_on_wall", "player_orders"), "not_kernel", "UNSETTLED", 1,
            "the oracle's 'a cell whose only wall is south gets no mark from a paint order or a pool pick' runs through the designator / work giver re-checking the side at the brush: game-side (and named an open defect in VERSION.json)");
    }

    // ------------------------------------------------------------------ the social tables

    static RM_Viewer RandViewer(Random r)
    {
        return new RM_Viewer
        {
            isMaker = r.NextDouble() < 0.1, isSubject = r.NextDouble() < 0.2, ownFaction = r.NextDouble() < 0.7, hostileMaker = r.NextDouble() < 0.15,
            loverOfSubject = r.NextDouble() < 0.1, loverOfMaker = r.NextDouble() < 0.1, opinionOfMaker = r.Next(-100, 101), opinionOfSubject = r.Next(-100, 101),
            kind = r.NextDouble() < 0.2, hot = r.NextDouble() < 0.3, psychopath = r.NextDouble() < 0.1, hasIdeo = r.NextDouble() < 0.8, makerHasIdeo = r.NextDouble() < 0.8,
            sameIdeoAsMaker = r.NextDouble() < 0.5
        };
    }

    static readonly RM_Reaction[] Calm = { RM_Reaction.None, RM_Reaction.Honored, RM_Reaction.Warmed, RM_Reaction.Amused, RM_Reaction.Moved, RM_Reaction.Uplifted, RM_Reaction.Gleeful, RM_Reaction.FriendTag, RM_Reaction.ShrugsOff, RM_Reaction.Scoffs, RM_Reaction.LostFace, RM_Reaction.Disapproves, RM_Reaction.Jealous, RM_Reaction.Mourning };

    static void Social()
    {
        // mockery: subject hurt, rival of subject amused, maker nothing; a plain tag moves no opinion for a neutral own-faction viewer
        var subj = new RM_Viewer { isSubject = true, ownFaction = true };
        var rival = new RM_Viewer { ownFaction = true, opinionOfSubject = -40 };
        var friend = new RM_Viewer { ownFaction = true, opinionOfSubject = 30 };
        var neutral = new RM_Viewer { ownFaction = true, opinionOfMaker = 0 };
        var maker = new RM_Viewer { isMaker = true, ownFaction = true, isSubject = true };
        bool ok = K.ReactionOf(RM_Meaning.Mockery, subj) == RM_Reaction.Humiliated && K.ReactionOf(RM_Meaning.Mockery, rival) == RM_Reaction.Gleeful
               && K.ReactionOf(RM_Meaning.Mockery, friend) == RM_Reaction.FriendDefends && K.ReactionOf(RM_Meaning.Mockery, maker) == RM_Reaction.None
               && K.ReactionOf(RM_Meaning.None, neutral) == RM_Reaction.None;
        Row("mockery_reactions", B("mockery", "inv_social_layer"), "fixed", ok ? "PASS" : "FAIL", 5,
            "mockery: subject " + K.ReactionOf(RM_Meaning.Mockery, subj) + ", rival of subject " + K.ReactionOf(RM_Meaning.Mockery, rival) + ", friend " + K.ReactionOf(RM_Meaning.Mockery, friend) + ", maker " + K.ReactionOf(RM_Meaning.Mockery, maker) + "; control plain tag, neutral viewer " + K.ReactionOf(RM_Meaning.None, neutral));

        // random: the maker never reacts; a plain tag only gives tag reactions; a hostile maker only Uneasy/Defiant
        string bad = null; int n = 0; var r = new Random(6606);
        var metas = (RM_Meaning[])Enum.GetValues(typeof(RM_Meaning));
        for (int i = 0; i < 50000; i++)
        {
            var v = RandViewer(r); var m = metas[r.Next(metas.Length)]; var re = K.ReactionOf(m, v); n++;
            if (v.isMaker && re != RM_Reaction.None) bad = bad ?? ("seed 6606 case " + i + ": maker reacts " + re);
            if (!v.isMaker && v.hostileMaker && re != RM_Reaction.Uneasy && re != RM_Reaction.Defiant) bad = bad ?? ("hostile maker gives " + re);
            if (!v.isMaker && !v.hostileMaker && m == RM_Meaning.None && re != RM_Reaction.None && re != RM_Reaction.RivalTag && re != RM_Reaction.FriendTag) bad = bad ?? ("plain tag gives " + re);
            if (!v.isMaker && !v.hostileMaker && v.psychopath && (m == RM_Meaning.Memorial || m == RM_Meaning.Beauty || m == RM_Meaning.Jest) && re != RM_Reaction.None) bad = bad ?? ("psychopath moved by " + m);
        }
        Row("reaction_invariants", B("mockery", "temperament", "inv_social_layer"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seed 6606, 50000 (meaning, viewer): the maker never reacts; a hostile maker's mark gives only Uneasy/Defiant; a plain tag gives only RivalTag/FriendTag/None; a psychopath is unmoved by memorial, beauty and jest");

        // who paints what: kind never mocks; no enemy no mockery; no dead no memorial; no beloved no tribute
        bad = null; n = 0;
        for (int i = 0; i < 50000; i++)
        {
            bool sp = r.NextDouble() < 0.5, kind = r.NextDouble() < 0.3, en = r.NextDouble() < 0.5, be = r.NextDouble() < 0.5, mo = r.NextDouble() < 0.5; int op = r.Next(-100, 101);
            var w = K.WantsToPaint(sp, kind, op, en, be, mo, (float)r.NextDouble()); n++;
            if (w == RM_Meaning.Mockery && (kind || !en || op > K.EnemyOpinion)) bad = bad ?? ("mockery without grudge or by a kind hand, case " + i);
            if (w == RM_Meaning.Memorial && !mo) bad = bad ?? ("memorial with no dead, case " + i);
            if (w == RM_Meaning.Tribute && (!be || sp)) bad = bad ?? ("tribute without a beloved or in a spree, case " + i);
        }
        ok = K.RefusesToPaint(RM_Meaning.Mockery, true) && K.RefusesToPaint(RM_Meaning.Insult, true) && !K.RefusesToPaint(RM_Meaning.Tribute, true) && !K.RefusesToPaint(RM_Meaning.Mockery, false);
        if (!ok) bad = bad ?? "RefusesToPaint table";
        Row("who_paints_what", B("mockery", "tribute_memorial", "fights_reasons"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seed 6606 cont., 50000 hands: mockery only from a non-kind hand with an enemy at <= -15; memorial only from a mourner (control: no dead friend, never); tribute only with a beloved, never in a spree; a kind hand refuses mockery and insult");

        // tribute: subject honoured, partner of the painter jealous, the subject's enemy scoffs, friend warmed
        ok = K.ReactionOf(RM_Meaning.Tribute, new RM_Viewer { isSubject = true }) == RM_Reaction.Honored
          && K.ReactionOf(RM_Meaning.Tribute, new RM_Viewer { loverOfMaker = true }) == RM_Reaction.Jealous
          && K.ReactionOf(RM_Meaning.Tribute, new RM_Viewer { opinionOfSubject = -50 }) == RM_Reaction.Scoffs
          && K.ReactionOf(RM_Meaning.Tribute, new RM_Viewer { opinionOfSubject = 30 }) == RM_Reaction.Warmed
          && K.ReactionOf(RM_Meaning.Memorial, new RM_Viewer { opinionOfSubject = 30 }) == RM_Reaction.Mourning;
        Row("tribute_reactions", B("tribute_memorial", "inv_social_layer"), "fixed", ok ? "PASS" : "FAIL", 5, "tribute: subject Honored, painter's lover Jealous, subject's enemy Scoffs, friend Warmed; memorial: a friend of the dead Mourning");

        // a memorial eases and never turns grief into a gain: random sequences
        bad = null; n = 0;
        for (int t = 0; t < 20000; t++)
        {
            float grief = (float)r.NextDouble() * 20f, before = 0f;
            int k = 1 + r.Next(8);
            for (int j = 0; j < k; j++) { float raw = (float)r.NextDouble() * 10f; float got = K.EaseShare(grief, raw, before); if (got < 0f || got > raw + 1e-5f) bad = bad ?? ("seed 6606 grief " + F(grief) + " raw " + F(raw) + " got " + F(got)); before += got; }
            n++;
            if (before > grief * K.GriefEaseShare + 1e-4f) bad = bad ?? ("eases sum " + F(before) + " > half grief " + F(grief));
        }
        Row("memorial_ease_bounded", B("tribute_memorial"), "random", bad == null ? "PASS" : "FAIL", n, bad ?? "seed 6606 cont., 20000 runs of 1..8 eases: each in [0, raw], their sum never past half the grief (conservation: grief eased, never turned into a gain)");
    }

    // ------------------------------------------------------------------ answers and fights

    static void Answers()
    {
        var reacts = (RM_Reaction[])Enum.GetValues(typeof(RM_Reaction));
        var leans = (RM_Lean[])Enum.GetValues(typeof(RM_Lean));
        var reached = new HashSet<RM_Answer>(); string bad = null; int n = 0; bool confrontOverDestroyed = false;
        foreach (var re in reacts) foreach (var lean in leans) for (int m = 0; m < 16; m++) for (int ri = 0; ri <= 100; ri++)
        {
            bool hot = (m & 1) != 0, fight = (m & 2) != 0, here = (m & 4) != 0, good = (m & 8) != 0; float roll = ri / 100f;
            var a = K.AnswerOf(re, hot, fight, here, good, roll, lean); n++;
            reached.Add(a);
            if (a == RM_Answer.Confront && !(fight && here)) bad = bad ?? ("confront without a fighter and the maker present: " + re);
            if (a == RM_Answer.Reply && !(good && here)) bad = bad ?? ("reply without a good hand and the maker: " + re);
            if (Calm.Contains(re) && a != RM_Answer.None) bad = bad ?? ("a calm reaction " + re + " answered " + a);
            if (lean == RM_Lean.Nothing && a != RM_Answer.None) bad = bad ?? "lean Nothing answered";
            if (lean == RM_Lean.Scrub && (a == RM_Answer.Confront || a == RM_Answer.Deface || a == RM_Answer.Reply)) bad = bad ?? ("lean Scrub gave " + a);
            if (re == RM_Reaction.WorkDestroyed && (a == RM_Answer.Scrub || a == RM_Answer.Deface)) bad = bad ?? ("work destroyed answered " + a);
            if (re == RM_Reaction.WorkDestroyed && a == RM_Answer.Confront) confrontOverDestroyed = true;
        }
        foreach (var want in new[] { RM_Answer.Scrub, RM_Answer.Deface, RM_Answer.Reply, RM_Answer.Confront }) if (!reached.Contains(want)) bad = bad ?? ("answer " + want + " unreachable");
        if (!confrontOverDestroyed) bad = bad ?? "no confront over painted-out work";
        Row("answer_table", B("answer_wall", "fights_reasons", "inv_social_layer"), "sweep", bad == null ? "PASS" : "FAIL", n,
            bad ?? "every reaction x lean x 16 flag sets x 101 rolls: all four answers reachable (incl. confront over painted-out work); confront needs a fighter and the painter present, reply a good hand and the painter; no answer from a calm reaction (control); lean Nothing never answers, lean Scrub never confronts/defaces/replies");

        // fight chance: never from nothing, capped, rising in both
        bad = null; n = 0;
        for (int i = 0; i <= 100; i++) for (int j = 0; j <= 100; j++)
        {
            float v = i / 100f, t = j / 25f; float c = K.ConfrontFightChance(v, t); n++;
            if (c < 0f || c > K.ConfrontFightCap + 1e-6f) bad = bad ?? ("chance " + F(c) + " out of [0, cap]");
            if ((v == 0f || t == 0f) && c != 0f) bad = bad ?? ("a fight from nothing: vanilla " + F(v) + " temper " + F(t));
            if (i > 0 && K.ConfrontFightChance((i - 1) / 100f, t) > c + 1e-6f) bad = bad ?? "falls with vanilla";
            if (j > 0 && K.ConfrontFightChance(v, (j - 1) / 25f) > c + 1e-6f) bad = bad ?? "falls with temper";
        }
        Row("fight_chance_bounded", B("fights_reasons", "temperament"), "sweep", bad == null ? "PASS" : "FAIL", n,
            bad ?? "vanilla 0..1 x temper 0..4: chance in [0, 0.85], zero when either is zero (no fight from nothing), never falling as either rises");

        bool ok = K.AnswerWaits(true, false, false, 1f) && K.AnswerWaits(false, true, false, 1f) && K.AnswerWaits(false, false, true, 1f) && K.AnswerWaits(false, false, false, K.AnswerReach + 1f) && !K.AnswerWaits(false, false, false, 5f);
        Row("answer_waits", B("fights_reasons", "answer_wall"), "fixed", ok ? "PASS" : "FAIL", 5, "an answer waits when hungry, tired, enemies near, or the target past 45 cells; else goes");

        Row("restrictions_game_side", B("fights_reasons"), "not_kernel", "UNSETTLED", 1,
            "drafted and area-restricted pawns never leaving to answer is a job-giver check (the kernel has no draft/area input): game-side, Stage 6");
    }

    // ------------------------------------------------------------------ temperament, budgets

    static RM_Temper T(string spec)
    {
        // spec: "bad=1.25,good=1.25,numb=1,neat=2,lean=Scrub,temper=..."
        var t = RM_Temper.Plain; t.bad = t.good = t.fine = t.ugly = t.temper = t.paint = t.offended = 1f;
        foreach (var kv in spec.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries))
        {
            var p = kv.Split('='); float f; float.TryParse(p[1], NumberStyles.Float, CultureInfo.InvariantCulture, out f);
            switch (p[0])
            {
                case "numb": t.numb = p[1] == "true"; break;
                case "bad": t.bad = f; break; case "good": t.good = f; break; case "fine": t.fine = f; break; case "ugly": t.ugly = f; break;
                case "temper": t.temper = f; break; case "paint": t.paint = f; break; case "offended": t.offended = f; break;
                case "neat": t.neat = (int)f; break; case "lean": t.lean = (RM_Lean)Enum.Parse(typeof(RM_Lean), p[1]); break;
            }
        }
        return t;
    }

    static void Temperament(Dictionary<string, string> rows)
    {
        // rows: key (trait[:degree] / gene / hediff / precept) -> spec of the shipped TemperamentDefs row (craft is reported, not mapped)
        Func<string, RM_Temper> row = k => rows.ContainsKey(k) ? T(rows[k]) : RM_Temper.Plain;
        var ordinary = K.Combine(new List<RM_Temper>());
        var psycho = K.Combine(new List<RM_Temper> { row("Psychopath"), row("Nerves:-2"), row("TorturedArtist") });
        var sens = K.Combine(new List<RM_Temper> { row("Nerves:-1") });
        bool ok = ordinary.bad == 1f && ordinary.good == 1f && ordinary.fine == 1f && ordinary.ugly == 1f
               && psycho.numb && psycho.bad == 0f && psycho.good == 0f && psycho.fine == 0f && psycho.ugly == 0f && psycho.offended == 0f && psycho.lean == RM_Lean.Nothing
               && sens.bad > 1f && sens.good > 1f && rows.ContainsKey("Psychopath") && rows.ContainsKey("Nerves:-1");
        Row("temper_psycho_sensitive_ordinary", B("temperament", "inv_temperament"), "fixed", ok ? "PASS" : "FAIL", 3,
            "ordinary (no rows) all 1 (control: offsets equal def values); psychopath (+ volatile + tortured artist) numb, every multiplier 0, lean Nothing; sensitive (Nerves -1 'volatile') bad " + F(sens.bad) + " good " + F(sens.good) + " (both above 1)");

        // clean freak: rows carrying neat
        var neatKeys = rows.Where(kv => kv.Value.Contains("neat=")).Select(kv => kv.Key).ToList();
        var parts = neatKeys.Select(k => { var c = K.Combine(new List<RM_Temper> { T(rows[k]) }); return k + " bad " + F(c.bad) + " ugly " + F(c.ugly) + " fine " + F(c.fine) + " neat " + c.neat; });
        bool anyMore = neatKeys.Any(k => { var c = K.Combine(new List<RM_Temper> { T(rows[k]) }); return c.bad > 1f || c.ugly > 1f; });
        Row("temper_clean_freak_multipliers", B("temperament"), "info", "INFO", neatKeys.Count,
            "clean-freak rows (those with neat): " + string.Join("; ", parts) + ". " + (anyMore ? "some" : "none") + " raise bad/ugly above 1 by the multipliers alone; 'the clean freak's debuff exceeds the ordinary one' must come from how neat is used game-side (lane 2)");
        Row("temper_clean_freak_break_game_side", B("temperament"), "not_kernel", "UNSETTLED", 1,
            "the clean freak's extra debuff by neat and its forced compulsive-clean break are not in the kernel (only BreakCooldownTicks is): game-side, Stage 6");

        // combine stays within its clamps for any mix of shipped rows; numb wins over everything
        string bad = null; int n = 0; var r = new Random(7707); var all = rows.Keys.ToList();
        for (int i = 0; i < 20000; i++)
        {
            var pick = Enumerable.Range(0, 1 + r.Next(5)).Select(_ => all[r.Next(all.Count)]).ToList();
            var c = K.Combine(pick.Select(k => T(rows[k])).ToList()); n++;
            if (c.bad < 0 || c.bad > 1.5f || c.good < 0 || c.good > 1.5f || c.fine < 0 || c.fine > 1.5f || c.ugly < 0 || c.ugly > 1.5f || c.temper < 0 || c.temper > 4f || c.paint < 0 || c.paint > 2f || c.offended < 0 || c.offended > 1.5f)
                bad = bad ?? ("seed 7707 rows " + string.Join("+", pick) + " out of clamps");
            if (pick.Any(k => rows[k].Contains("numb=true")) && (c.bad != 0f || c.good != 0f || c.lean != RM_Lean.Nothing)) bad = bad ?? ("numb lost: " + string.Join("+", pick));
            var rev = K.Combine(pick.AsEnumerable().Reverse().Select(k => T(rows[k])).ToList());
            if (Math.Abs(rev.bad - c.bad) > 1e-5f || Math.Abs(rev.good - c.good) > 1e-5f || rev.neat != c.neat) bad = bad ?? ("order changes multipliers: " + string.Join("+", pick));
        }
        Row("temper_combine_bounded", B("temperament", "stories_not_tax"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seed 7707, 20000 mixes of 1..5 shipped rows: every multiplier inside its clamp, numb always wins, multipliers order-free");

        // budgets: whatever arrives, memories of a sign never add past the budget
        bad = null; n = 0; List<float> failSeq = null;
        for (int t = 0; t < 20000 && failSeq == null; t++)
        {
            float budget = new[] { K.BadMoodBudget, K.VictimMoodBudget, K.GoodMoodBudget, K.AmbientMoodBudget }[r.Next(4)] * (0.5f + (float)r.NextDouble());
            var seq = Enumerable.Range(0, 1 + r.Next(30)).Select(_ => (float)r.NextDouble() * 8f).ToList(); n++;
            if (BudgetOver(seq, budget)) { failSeq = Shrink(seq, s => BudgetOver(s, budget)); bad = "seed 7707 budget " + F(budget) + " shrunk offsets [" + string.Join(",", failSeq.Select(F)) + "]"; }
        }
        float amb = 0f; for (int i = 0; i <= 400; i++) amb = Math.Max(amb, K.AmbientBudget(i / 100f));
        if (amb > K.AmbientMoodBudget + 1e-6f) bad = bad ?? ("ambient budget " + F(amb) + " past +3");
        Row("mood_budget_conserved", B("stories_not_tax", "rereads_daily", "temperament"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seed 7707 cont., 20000 runs of 1..30 memories: FitBudget never lets one sign's memories sum past its budget; ambient budget never past the owner's +3 for good 0..4 (max " + F(amb) + ")");

        // opinion caps exist and are finite; territory unease bounded and gone at zero marks
        bool ok2 = K.TerritoryStage(0) == -1 && Enumerable.Range(0, 200).All(i => K.TerritoryStage(i) <= 2 && K.TerritoryStage(i + 1) >= K.TerritoryStage(i));
        Row("territory_unease_lifts", B("raid_mark_troubles", "inv_raid_marks", "stories_not_tax"), "sweep", ok2 ? "PASS" : "FAIL", 200,
            "TerritoryStage: none at 0 standing enemy marks (troubles end when the wall is retaken), rising with count, capped at stage 2");
    }

    static bool BudgetOver(List<float> seq, float budget)
    {
        float already = 0f;
        foreach (float o in seq) { float k = K.FitBudget(already, o, budget); if (k < 0f || k > 1f) return true; already += o * k; }
        return already > budget + 1e-3f;
    }

    // ------------------------------------------------------------------ rereads, visitors

    static void Rereads()
    {
        bool ok = K.ReadAgainTicks >= 60000 && K.RereadFactor > 0f && K.RereadFactor <= 1f;
        Row("reread_daily_constants", B("rereads_daily"), "fixed", ok ? "PASS" : "FAIL", 1, "ReadAgainTicks " + K.ReadAgainTicks + " (>= one day), RereadFactor " + F(K.RereadFactor) + " (a re-read is no stronger than the first)");
        Row("reread_opinion_once_game_side", B("rereads_daily"), "not_kernel", "UNSETTLED", 1, "'opinion changed once' and the per-pawn read memory are game-side (GraffitiSocial): Stage 6");

        // visitors: within one visit, losses never pass the cap; another faction's insult moves nothing
        string bad = null; int n = 0; var r = new Random(8808);
        for (int t = 0; t < 20000; t++)
        {
            int lost = 0, gained = 0; int k = 1 + r.Next(20);
            for (int j = 0; j < k; j++)
            {
                var m = (RM_Meaning)r.Next(8); int d = K.GoodwillOf(m, r.NextDouble() < 0.5, r.NextDouble() < 0.3, r.NextDouble() < 0.5);
                int c = K.VisitCharge(d, lost, gained);
                if (Math.Sign(c) != Math.Sign(d) && c != 0) bad = bad ?? "charge flips sign";
                if (Math.Abs(c) > Math.Abs(d)) bad = bad ?? "charge exceeds the read";
                if (c < 0) lost -= c; else gained += c;
            }
            n++;
            if (lost > K.VisitLossCap || gained > K.VisitGainCap) bad = bad ?? ("seed 8808 run " + t + " lost " + lost + " gained " + gained);
        }
        bool ok2 = K.GoodwillOf(RM_Meaning.Insult, false, false, false) == 0 && K.GoodwillOf(RM_Meaning.Insult, false, true, false) == 0 && K.GoodwillOf(RM_Meaning.Insult, true, false, false) < 0;
        if (!ok2) bad = bad ?? "an insult to another faction moved goodwill";
        Row("visit_goodwill_capped", B("visitors", "inv_visitors"), "random", bad == null ? "PASS" : "FAIL", n,
            bad ?? "seed 8808, 20000 visits of 1..20 reads: loss never past 12, gain never past 3, a charge never larger or of other sign than the read; control: an insult naming another faction moves this faction's goodwill 0 (taunt flag or not)");
        Row("visit_once_per_mark_game_side", B("visitors", "walk_lived_in"), "not_kernel", "UNSETTLED", 1, "'one goodwill change attributed to the mark per visit' (which reads charge, visit start/end) is game-side bookkeeping: Stage 6");
    }

    // ------------------------------------------------------------------ raid exit, scrub protection, going over, breach lure

    static void Raid()
    {
        string bad = null; int n = 0;
        for (int m = 0; m < 32; m++)
        {
            bool p = (m & 1) != 0, e = (m & 2) != 0, fk = (m & 4) != 0, fp = (m & 8) != 0, h = (m & 16) != 0;
            bool got = K.RaidExitTags(p, e, fk, fp, h), want = p && e && fk && !fp && h; n++;
            if (got != want) bad = bad ?? ("painting " + p + " exit " + e + " known " + fk + " player " + fp + " hostile " + h + " -> " + got);
        }
        if (!(K.TurnsToLeave(false, true) && !K.TurnsToLeave(true, true) && !K.TurnsToLeave(false, false) && !K.TurnsToLeave(true, false))) bad = bad ?? "TurnsToLeave";
        if (!(K.ExteriorFace(false, true, true) && !K.ExteriorFace(true, true, true) && !K.ExteriorFace(false, false, true) && !K.ExteriorFace(false, true, false))) bad = bad ?? "ExteriorFace";
        Row("raid_exit_gate", B("raid_mark_troubles", "inv_raid_marks", "stands_alone_settings"), "sweep", bad == null ? "PASS" : "FAIL", n + 8,
            bad ?? "RaidExitTags all 32: tags only for a known hostile non-player faction with painting and exit-tagging on; TurnsToLeave once per departure (control: a raid that never turns leaves no tag); ExteriorFace only unroofed outdoors with a known room");

        bad = null; n = 0;
        for (int m = 0; m < 128; m++)
        {
            bool f = (m & 1) != 0, s = (m & 2) != 0, im = (m & 4) != 0, he = (m & 8) != 0, fl = (m & 16) != 0, own = (m & 32) != 0, dev = (m & 64) != 0;
            bool got = K.ProtectsFromAutoClean(f, s, im, he, fl, own, dev), want = !f && s && im && he && (fl || own || dev); n++;
            if (got != want) bad = bad ?? ("forced " + f + " setting " + s + " mark " + im + " ext " + he + " flag " + fl + " own " + own + " dev " + dev + " -> " + got);
        }
        Row("scrub_protection_table", B("scrub_protection", "inv_scrub_protection", "stands_alone_settings"), "sweep", bad == null ? "PASS" : "FAIL", n,
            bad ?? "all 128: unforced cleaners skip own/devotional/flagged marks with the setting on; a hostile unflagged vandal mark is cleaned (control); an ordered (forced) clean takes everything; setting off protects nothing");

        bool ok = K.IsRival(true, false) && !K.IsRival(true, true) && !K.IsRival(false, false);
        Row("going_over_rival", B("going_over"), "fixed", ok ? "PASS" : "FAIL", 3, "a different mark on the cell is a rival (destroyed first); the same def thickens; a non-mark is not a rival. One mark per cell after is game-side");

        var rnd = new Random(9909); bad = null; n = 0;
        for (int t = 0; t < 5000; t++)
        {
            int c = rnd.Next(0, 10); var d = Enumerable.Range(0, c).Select(_ => (long)rnd.Next(0, 20)).ToList(); var key = Enumerable.Range(0, c).Select(_ => rnd.Next(0, 1000)).ToList();
            int b = K.ChooseLure(d, key); n++;
            if (c == 0) { if (b != -1) bad = bad ?? "lure from nothing"; continue; }
            for (int i = 0; i < c; i++) if (d[i] < d[b] || (d[i] == d[b] && key[i] < key[b])) bad = bad ?? ("seed 9909 case " + t + " not nearest/lowest key");
        }
        Row("breach_lure_nearest", B("inv_breach_bias"), "random", bad == null ? "PASS" : "FAIL", n, bad ?? "seed 9909, 5000 sets: the lure is the nearest, ties by lowest key; none from an empty set");
    }

    // ------------------------------------------------------------------ settings as shipped, swept

    static void Settings()
    {
        int pace = int.Parse(Env("GR_PACE", "250"));
        string bad = null; int n = 0;
        if (pace < 60 || pace > 1000) bad = "shipped pace " + pace + " outside its slider 60..1000";
        foreach (var f in Forms) if (K.PaintTicks(f, pace) != K.PaintTicksBase(f) && pace == 250) bad = bad ?? ("default pace does not give the base ticks for " + f);
        int[] probe = { int.MinValue, -1000, 0, 1, 59, 60, 61, 250, 999, 1000, 1001, 100000, int.MaxValue };
        foreach (int s in probe.Concat(Enumerable.Range(6, 95).Select(i => i * 10)))
        {
            int iv = K.PaintInterval(s); n++;
            if (iv < 60 || iv > 1000) bad = bad ?? ("interval " + iv + " from setting " + s);
            foreach (var f in Forms) { int tk = K.PaintTicks(f, s); if (tk < 30 || tk > 2800 * 4) bad = bad ?? ("ticks " + tk + " for " + f + " at " + s); if (s > 60 && s <= 1000 && K.PaintTicks(f, s - 10) > tk) bad = bad ?? "ticks fall as pace rises"; }
        }
        Row("settings_pace_sweep", B("stands_alone_settings", "inv_settings"), "sweep", bad == null ? "PASS" : "FAIL", n,
            bad ?? "shipped paintIntervalTicks " + pace + " (slider 60..1000); default gives each form's base ticks; slider swept in 10s and hand-edited values (int min/max, 0, negatives): interval clamped 60..1000 (no divide by zero), ticks 30..11200 and monotone");

        // switches off, as shipped and swept: each gate in the kernel stops its behaviour
        bool painting = Env("GR_PAINTING", "1") == "1", exit = Env("GR_EXIT", "1") == "1", viewer = Env("GR_VIEWER", "1") == "1", protect = Env("GR_PROTECT", "1") == "1";
        bad = null;
        if (!(painting && exit && viewer && protect)) bad = "a shipped switch defaults off: painting " + painting + " exit " + exit + " viewer " + viewer + " protect " + protect;
        if (K.RaidExitTags(false, true, true, false, true) || K.RaidExitTags(true, false, true, false, true)) bad = bad ?? "exit tags with a switch off";
        if (K.ThoughtActive(false, true, true, true)) bad = bad ?? "viewer thought with the switch off";
        if (K.ProtectsFromAutoClean(false, false, true, true, true, true, true)) bad = bad ?? "protection with the switch off";
        if (!K.RaidExitTags(painting, exit, true, false, true) || !K.ThoughtActive(viewer, true, true, true) || !K.ProtectsFromAutoClean(false, protect, true, true, false, true, false)) bad = bad ?? "a switch at its shipped value does not run its behaviour";
        Row("settings_switches_off", B("stands_alone_settings", "inv_settings"), "sweep", bad == null ? "PASS" : "FAIL", 7,
            bad ?? "shipped defaults all on; each kernel-gated switch (painting, raid exit tagging, viewer reaction, auto-clean protection) off stops its own behaviour; back on restores it");

        int count = int.Parse(Env("GR_SETTING_COUNT", "-1"));
        Row("settings_count_vs_bar", B("stands_alone_settings", "raider_pressure"), "info", "INFO", 1,
            "RM_GraffitiMod.cs ships " + count + " settings (" + Env("GR_SETTING_NAMES", "?") + "); the bar says '8 today, 11 with the raider pressure's switch, mode and size' and the floor line wants the pressure's switch and tuning: no raider-pressure setting is shipped");
        Row("settings_social_breach_game_side", B("stands_alone_settings", "inv_breach_bias"), "not_kernel", "UNSETTLED", 1,
            "socialEnabled, socialMessagesEnabled and breachBiasEnabled are not kernel inputs: their off-switches are game-side (Stage 6); save/reload of mark fields likewise");
    }

    static void JoyAndIdle()
    {
        bool ok = Forms.Where(K.SpreeForm).All(K.JoyForm) && K.JoyForm(GraffitiForm.Piece) && !K.SpreeForm(GraffitiForm.Piece)
               && K.SittingContinues(10, true, 1f) && K.SittingContinues(0, false, 0.5f) && !K.SittingContinues(K.MaxMarksPerJoySitting, false, 0.1f) && !K.SittingContinues(0, false, 0.96f);
        Row("joy_sitting", B("own_fun", "inv_joy_and_idle_tag"), "fixed", ok ? "PASS" : "FAIL", 6,
            "joy pool holds every spree form plus the planned ones; a joy sitting stops at 4 marks or joy 0.95, a spree never stops on those");
        ok = K.IdleHandTags(0f) && !K.IdleHandTags(K.IdleTagChance) && K.IdleTagChance > 0f && K.IdleTagChance < 0.1f;
        Row("idle_tag_rare", B("own_fun", "stories_not_tax", "inv_joy_and_idle_tag"), "fixed", ok ? "PASS" : "FAIL", 2, "idle tagging chance " + F(K.IdleTagChance) + " per think: positive and rare");
        Row("maker_buff_game_side", B("own_fun"), "not_kernel", "UNSETTLED", 1, "the maker's thought and the joy job choice are game-side (JoyGiver / thoughts): Stage 6");
    }

    static void NotKernel()
    {
        foreach (var b in new[] {
            new[] { "mark_appears", "a spree's paint job placing marks in a lane is a map run" },
            new[] { "reads_at_play_zoom", "art read by a judge at 64 px" },
            new[] { "punk_register", "art read by a judge" },
            new[] { "no_english", "art read by a judge" },
            new[] { "not_dirt", "art read by a judge beside vanilla dirt" },
            new[] { "player_orders", "designator and work giver on a map" },
            new[] { "raider_pressure", "per-faction record, letter and raid points/timing: no kernel function exists for it, and no setting ships (see settings_count_vs_bar)" },
            new[] { "paint_dies_with_wall", "a wall-loss patch on a map" },
            new[] { "walk_lived_in", "a lived-in save walked twice" },
            new[] { "stories_not_tax", "a three-week soak; the kernel budgets bound it (mood_budget_conserved) but the average is live" },
        })
            Row("not_kernel_" + b[0], B(b[0]), "not_kernel", "UNSETTLED", 0, b[1] + ": game-side, owed to Stage 6");
    }

    static int Main()
    {
        var defs = new List<string[]>();
        string dp = Env("GR_DEFS", "");
        if (dp != "" && File.Exists(dp)) foreach (var l in File.ReadAllLines(dp)) if (l.Trim() != "") defs.Add(l.Split('\t'));
        var temper = new Dictionary<string, string>();
        string tp = Env("GR_TEMPER", "");
        if (tp != "" && File.Exists(tp)) foreach (var l in File.ReadAllLines(tp)) { var p = l.Split('\t'); if (p.Length == 2) temper[p[0]] = p[1]; }
        if (defs.Count == 0 || temper.Count == 0) { Row("inputs_read", B("stands_alone_settings"), "info", "FAIL", 0, "defs " + defs.Count + " temper rows " + temper.Count + ": the harness could not read the shipped values"); return 1; }
        Weathering(); ArtSkill(defs); Pool(defs); Wall(); Social(); Answers(); Temperament(temper); Rereads(); Raid(); Settings(); JoyAndIdle(); NotKernel();
        return fails > 0 ? 1 : 0;
    }
}
