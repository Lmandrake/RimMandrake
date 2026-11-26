// WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED (owner by card 2026-10-22, "Pick for me: shadow band + navy"): the deep steps past
// 2 m (5 m / 10 m), the navy overlay reproducing the approved mock's pixel rule, and the wiring (setting Scribed, drawn, reset;
// the layer hidden by its setting; no terrain written).
// RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE (owner walk 2026-11-25): ONE water surface over a dug square, the dry
// pit cut by the waterline on each face (twin model/water_surface.py); the wall shadow band is gone.
// NOT proven here: how the looks read in game (the drill's captures, design/concepts/FlowWorks/version/in_game/water_drill_20261125).
using System;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WaterLookChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("WaterLook_deep_steps_start_at_5_and_10_metres", () =>
            {
                Assert(RM_WaterLadder.DeepStepForMetres(2.0) == RM_WaterLadder.DeepStep.None, "2 m: plain deep water");
                Assert(RM_WaterLadder.DeepStepForMetres(4.99) == RM_WaterLadder.DeepStep.None, "just under 5 m");
                Assert(RM_WaterLadder.DeepStepForMetres(5.0) == RM_WaterLadder.DeepStep.FiveMetres, "5 m");
                Assert(RM_WaterLadder.DeepStepForMetres(9.99) == RM_WaterLadder.DeepStep.FiveMetres, "just under 10 m");
                Assert(RM_WaterLadder.DeepStepForMetres(10.0) == RM_WaterLadder.DeepStep.TenMetres, "10 m");
                Assert(RM_WaterLadder.DeepStepForMetres(40.0) == RM_WaterLadder.DeepStep.TenMetres, "40 m");
                long U = RM_LevelSolve.U;
                Assert(RM_WaterLadder.DeepStepForDl(10 * U) == RM_WaterLadder.DeepStep.FiveMetres, "10 notches = 5 m, by decilitres");
                Assert(RM_WaterLadder.DeepStepForDl(10 * U - 1) == RM_WaterLadder.DeepStep.None, "can-fail: one decilitre short");
                Assert(RM_LevelSolve.LookBand(30 * U) == 5, "LookBand unchanged: the steps are a tint, not new terrain bands");
            });

            Case("WaterLook_navy_overlay_reproduces_the_approved_mock", () =>
            {
                // deep_T2_navy (Transient/fw_scenes/water_art/make_water_art.py): out = a*(1-.25i)*(1-f) + navy*f
                double[] navy = { 28, 40, 66 };
                double[] f = { 0, .42, .70 };
                double[][] unders = { new double[] { 72, 86, 101 }, new double[] { 40, 52, 66 }, new double[] { 110, 120, 128 } };
                RM_WaterLookMath.Rgba[] tints = { default, RM_WaterLookMath.TintFive, RM_WaterLookMath.TintTen };
                for (int i = 1; i <= 2; i++)
                {
                    foreach (double[] a in unders)
                    {
                        byte[] t = { tints[i].r, tints[i].g, tints[i].b };
                        for (int ch = 0; ch < 3; ch++)
                        {
                            double mock = a[ch] * (1 - .25 * i) * (1 - f[i]) + navy[ch] * f[i];
                            double ours = RM_WaterLookMath.Over(a[ch], t[ch], tints[i].a);
                            Assert(Math.Abs(mock - ours) <= 1.5, "step " + i + " channel " + ch + ": mock " + mock.ToString("F1") + " ours " + ours.ToString("F1"));
                        }
                    }
                }
                Assert(RM_WaterLookMath.TintAt(0f).a == 0, "strength 0 draws nothing");
                Assert(RM_WaterLookMath.TintAt(1f).a == RM_WaterLookMath.TintFive.a && RM_WaterLookMath.TintAt(2f).a == RM_WaterLookMath.TintTen.a, "1 and 2 are the two tints");
                Assert(RM_WaterLookMath.TintAt(0.5f).a == 72, "half way to the 5 m tint fades its alpha");
                byte prev = 0;
                for (float s = 0f; s <= 2.001f; s += 0.125f)
                {
                    byte a = RM_WaterLookMath.TintAt(s).a;
                    Assert(a >= prev, "alpha never falls as the water deepens (s=" + s + ")");
                    prev = a;
                }
            });

            // WATER_DEPTH_RESKIN_HE_LOOKS_FIRST L3 / plan V7 (flowworks_one_rebuild_plan_2026-10-17.md): "walls: five looks by the
            // step to each neighbour (0.5, 1, 1.5, 2, over 2 m)". A notch is 0.5 m, so drops 1..5 notches must give five
            // pairwise-different faces (north height, side width). Can fail: a NorthByDrop/SideByDrop that saturates at D4
            // draws a 2.5 m step exactly like a 2 m one.
            Case("WallFaces_five_looks_by_drop_to_over_2m", () =>
            {
                for (int a = 1; a <= 5; a++)
                {
                    for (int b = a + 1; b <= 5; b++)
                    {
                        float ha = RM_WallFaceMath.NorthFaceHeight(RM_WallFaceMath.ExposedDrop(a, 0, 0));
                        float hb = RM_WallFaceMath.NorthFaceHeight(RM_WallFaceMath.ExposedDrop(b, 0, 0));
                        float sa = RM_WallFaceMath.SideFaceWidth(RM_WallFaceMath.ExposedDrop(a, 0, 0));
                        float sb = RM_WallFaceMath.SideFaceWidth(RM_WallFaceMath.ExposedDrop(b, 0, 0));
                        Assert(Math.Abs(ha - hb) > 0.01f || Math.Abs(sa - sb) > 0.01f,
                            "a " + (a * 0.5) + " m and a " + (b * 0.5) + " m step draw the same face (north " + ha + "/" + hb
                            + ", side " + sa + "/" + sb + ")");
                    }
                }
                Assert(RM_WallFaceMath.NorthFaceHeight(16) <= RM_WallFaceMath.NorthMax, "an 8 m step never draws taller than NorthMax");
            });

            // L3 / P5 A4 ("floor tint per depth band past 2 m", PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT handed it here). The dry floor
            // terrain past 2 m is one def (RM_Channel_Superdeep, RM_ExcavationDepth.DryTerrainFor), so depth past 2 m can only show
            // through the depth darkness (FootDarkness, which RM_ExcavationWalls.Dark draws). Can fail: a darkness that saturates
            // at 2 m draws a 2 m, a 4 m and an 8 m floor alike. If a separate floor-tint function is built, point this at it with
            // the same three-way distinctness.
            Case("WallFaces_floor_bands_past_2m", () =>
            {
                float d2 = RM_WallFaceMath.FootDarkness(4), d4 = RM_WallFaceMath.FootDarkness(8), d8 = RM_WallFaceMath.FootDarkness(16);
                Assert(d4 > d2 + 0.01f, "a 4 m floor reads darker than a 2 m one (" + d2 + " vs " + d4 + ")");
                Assert(d8 > d4 + 0.01f, "an 8 m floor reads darker than a 4 m one (" + d4 + " vs " + d8 + ")");
                Assert(d8 <= 1f, "darkness stays a fraction");
            });

            Case("WaterLook_settings_and_layers_are_wired", () =>
            {
                string looks = RiverSwitchFlipChecks.Src("RM_WaterLooks.cs");
                string mend = RiverSwitchFlipChecks.Src("RM_WaterBodyMendGame.cs");
                RiverSwitchFlipChecks.Has(looks, @"public static bool deepWaterTintEnabled = true;", "tint ships on");
                RiverSwitchFlipChecks.Has(looks, @"Scribe_Values\.Look\(ref deepWaterTintEnabled, ""waterDeepTintEnabled"", true\);", "tint saved");
                RiverSwitchFlipChecks.Has(looks, @"RM_SettingsReset\.Snapshot\(typeof\(RM_WaterLookSettings\)\)", "shipped values snapshotted");
                RiverSwitchFlipChecks.Has(looks, @"SettingsKitDrawer\.ResetButton\(list, ResetToShipped\)", "Reset button");
                RiverSwitchFlipChecks.Has(looks, @"Visible => DebugViewSettings\.drawTerrain && RM_WaterLookSettings\.deepWaterTintEnabled;", "tint layer hides when off");
                Assert(!looks.Contains("wetWallBand") && !looks.Contains("SectionLayer_RMWetWallBand"), "the wall shadow band layer is gone");
                Assert(!Regex.IsMatch(looks, @"SetTerrain|StageNaturalCell|SetTempTerrain"), "the looks write no terrain");
                RiverSwitchFlipChecks.Has(mend, @"RM_WaterLookSettings\.ExposeData\(\);", "Scribed with the water-body screen");
                RiverSwitchFlipChecks.Has(mend, @"RM_WaterLookSettings\.DoSettingsSection\(list\);", "drawn on the water-body screen");
                // the snapshot must sit below the last setting field, or Reset restores a loaded value instead of the shipped one
                int snap = looks.IndexOf("RM_SettingsReset.Snapshot", StringComparison.Ordinal);
                Assert(snap > looks.IndexOf("public static bool deepWaterTintEnabled", StringComparison.Ordinal), "snapshot below the field");
            });

            // FlowWorks GPT review 2026-10-22 (RM_WaterLooks.cs:116/207): the tint went stale when water crossed 5 m / 10 m without a
            // terrain write. The key changes exactly at a tint step; nothing else.
            Case("WaterLook_key_changes_at_tint_steps_only", () =>
            {
                int Key(double waterMetres) => RM_WaterLookMath.LookKey(
                    (int)RM_WaterLookMath.StepStrength(RM_WaterLadder.DeepStepForMetres(waterMetres)));
                Assert(Key(4.99) != Key(5.0) && Key(9.99) != Key(10.0), "crossing 5 m and 10 m changes the key");
                Assert(Key(5.2) == Key(9.8) && Key(0.3) == Key(4.9), "inside one tint step the key holds (no redraw)");
                var watch = new RM_WaterLookMath.Watch();
                Assert(!watch.Note(3, 10, 0), "dry ground at load needs no redraw");
                Assert(watch.Note(3, 10, 1) && !watch.Note(3, 10, 1) && watch.Note(3, 10, 2), "a key redraws once per change");
            });

            Case("WaterLook_layers_listen_to_their_own_flag_and_the_engine_runs_the_watcher", () =>
            {
                string looks = RiverSwitchFlipChecks.Src("RM_WaterLooks.cs");
                string eng = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                string def = System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(
                    RiverSwitchFlipChecks.SrcPath("RM_WaterLooks.cs")), "..", "Defs", "ManyWaters", "MapMeshFlagDefs", "RM_WaterLooks.xml"));
                Assert(Regex.Matches(looks, @"relevantChangeTypes = RM_WaterLookDraw\.Flags;").Count == 1, "the tint layer listens to Terrain | RM_WaterLooks");
                Assert(!looks.Contains("relevantChangeTypes = MapMeshFlagDefOf.Terrain;"), "no layer is terrain-only any more");
                RiverSwitchFlipChecks.Has(looks, @"GetNamedSilentFail\(""RM_WaterLooks""\)", "the flag is looked up by its defName");
                RiverSwitchFlipChecks.Has(def, @"<defName>RM_WaterLooks</defName>", "the flag def exists");
                RiverSwitchFlipChecks.Has(looks, @"MapMeshDirty\(c, flag, true, false\)", "a changed key dirties only the looks' flag, neighbours included");
                RiverSwitchFlipChecks.Has(eng, @"lookWatcher\.Tick\(map, this, excavatedCells\);", "the engine runs the watcher");
                Assert(!Regex.IsMatch(looks, @"new float\[w \* h\];\s*bool any"), "the tint's strength grid is reused, not allocated per regenerate");
            });

            // RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE (owner walk 2026-11-25: "Station 6 still shows odd pit walls
            // under water ... Look at the corners" and "I suspect you're applying multiple layers over each other instead of calculating
            // a single one"). The census on the parent build counted nine sheet pieces at alpha 0..229 on one square of station 22 and
            // drowned walls drawn as plain rectangles. The rule (twin model/water_surface.py): ONE sheet over the dry pit, cut by the
            // waterline on each face. Swept over the walk map's pit shapes and the stepped ones at every quarter-notch level; an
            // independent oracle inverts the face curves to give each point's true depth. Red on the parent's shape (planted:
            // design/concepts/FlowWorks/version/in_game/water_drill_20261125/red_old_rectangles.patch).
            Case("WaterLook_one_sheet_over_the_dry_pit_cut_by_the_line", () =>
            {
                var pieces = new System.Collections.Generic.List<float[]>();
                int squares = 0;
                foreach (var g in WaterGrids())
                {
                    int dmax = 0;
                    foreach (var kv in g.Value) dmax = Math.Max(dmax, kv.Value);
                    for (int q = 1; q <= dmax * 4; q++)
                    {
                        float lvBody = q * 0.25f;
                        foreach (var kv in g.Value)
                        {
                            int x = kv.Key.Item1, z = kv.Key.Item2, d = kv.Value;
                            int D(int a, int b) => g.Value.TryGetValue((a, b), out int v) ? v : 0;
                            int n = D(x, z + 1), so = D(x, z - 1), w = D(x - 1, z), e = D(x + 1, z), nw = D(x - 1, z + 1), ne = D(x + 1, z + 1);
                            float lv = lvBody - (dmax - d);
                            int count = RM_PitReliefMath.SheetPieces(d, n, so, w, e, nw, ne, lv, 0f, 1f, 0f, 1f, pieces);
                            string at = g.Key + " (" + x + "," + z + ") lv=" + lv;
                            if (!(lv > 0f))
                            {
                                Assert(count == 0, "can-fail: a square holding no liquid draws a sheet: " + at);
                                continue;
                            }
                            squares++;
                            float de = d - lv;
                            for (int i = 0; i < 16; i++)
                            {
                                for (int j = 0; j < 16; j++)
                                {
                                    float px = (i + 0.5f) / 16f, pz = (j + 0.37f) / 16f;
                                    int cover = 0;
                                    foreach (float[] p in pieces) if (Inside(p, px, pz)) cover++;
                                    Assert(cover <= 1, "can-fail: two sheet pieces overlap at (" + px + "," + pz + "): " + at);
                                    float? truth = DepthAt(d, n, so, w, e, nw, ne, px, pz);
                                    if (truth == null || Math.Abs(truth.Value - de) < 0.02f || NearEdge(pieces, px, pz)) continue;
                                    bool wet = truth.Value > de;
                                    Assert(wet == (cover == 1), "can-fail: at (" + px + "," + pz + ") depth " + truth.Value + " vs line " + de
                                        + ": sheet " + (cover == 1) + ", truth " + wet + ": " + at);
                                }
                            }
                        }
                    }
                }
                Assert(squares > 1000, "the sweep reached the wet squares (" + squares + ")");
                // one alpha: the wet-ground darkening composed with the liquid's own overlay is one overlay
                float seen = 0.6f, wa = 0.15f;
                float A = RM_PitReliefMath.SheetAlpha(seen, wa), share = RM_PitReliefMath.SheetBodyShare(seen, wa);
                double under = 0.4, body = 0.2;
                double twoLayers = (under * (1 - wa)) * seen + body * (1 - seen);
                Assert(Math.Abs(under * (1 - A) + body * share * A - twoLayers) < 1e-5, "one overlay equals the two it replaces");
                Assert(RM_PitReliefMath.SheetAlpha(1f, 0f) == 0f, "clear and dry: nothing drawn");
            });

            Case("WaterLook_sluice_parts_the_sheet_and_a_drained_floor_reprints", () =>
            {
                var pieces = new System.Collections.Generic.List<float[]>();
                for (int rot = 0; rot < 4; rot++)
                {
                    foreach (bool lo in new[] { false, true })
                    {
                        foreach (bool hi in new[] { false, true })
                        {
                            RM_PitReliefMath.SluiceHalf(rot, lo, hi, out float x0, out float x1, out float z0, out float z1);
                            bool side = rot == 1 || rot == 3;
                            if (side) RM_PitReliefMath.SheetPieces(1, 0, 0, 1, 1, 0, 0, 1f, x0, x1, z0, z1, pieces);
                            else RM_PitReliefMath.SheetPieces(1, 1, 1, 0, 0, 0, 0, 1f, x0, x1, z0, z1, pieces);
                            bool lowIn = false, highIn = false;
                            foreach (float[] p in pieces)
                            {
                                lowIn |= side ? Inside(p, 0.25f, 0.5f) : Inside(p, 0.5f, 0.25f);
                                highIn |= side ? Inside(p, 0.75f, 0.5f) : Inside(p, 0.5f, 0.75f);
                            }
                            string at = "rot " + rot + " low wet " + lo + " high wet " + hi;
                            Assert(lowIn == (lo || !hi) && highIn == (hi || !lo), "can-fail: the drained half of a shut sluice shows water: " + at);
                        }
                    }
                }
                Assert(RM_PitReliefMath.GateFaceDry(0, true, false) && RM_PitReliefMath.GateFaceDry(2, true, false), "can-fail: drained in front: dry face");
                Assert(!RM_PitReliefMath.GateFaceDry(0, false, true) && !RM_PitReliefMath.GateFaceDry(0, false, false), "water in front covers it");
                Assert(!RM_PitReliefMath.GateFaceDry(1, true, false), "the side view never shows liquid anyway");
                Assert(RM_PitReliefMath.ReprintsFloor(true, false, true), "can-fail: a drained dug square beside water reprints its floor");
                Assert(!RM_PitReliefMath.ReprintsFloor(true, true, true) && !RM_PitReliefMath.ReprintsFloor(false, false, true)
                    && !RM_PitReliefMath.ReprintsFloor(true, false, false), "only a dry dug square beside liquid");
            });

            Case("WaterLook_walls_draw_one_sheet_and_no_second_water_layer", () =>
            {
                string walls = RiverSwitchFlipChecks.Src("Superdeep/RM_ExcavationWalls.cs");
                string looks = RiverSwitchFlipChecks.Src("RM_WaterLooks.cs");
                Assert(Regex.Matches(walls, @"RM_FaceMaterial\.SheetMat").Count == 1, "can-fail: the walls layer draws the liquid's sheet in one place");
                int ws = walls.IndexOf("private void WaterSurface(", StringComparison.Ordinal);
                int sm = walls.IndexOf("RM_FaceMaterial.SheetMat", StringComparison.Ordinal);
                int next = walls.IndexOf("private void AddFace(", StringComparison.Ordinal);
                Assert(ws > 0 && sm > ws && sm < next, "the one sheet is WaterSurface's");
                Assert(!walls.Contains("SideUnder(") && !walls.Contains("SeeThrough(") && !walls.Contains("DrownedBandX"),
                    "can-fail: the drowned-wall rectangles are gone");
                RiverSwitchFlipChecks.Has(walls, @"float lv = sheet \? 0f : lvTrue;", "a wet square under a clear liquid draws the dry pit's faces");
                RiverSwitchFlipChecks.Has(walls, @"ReliefCell\(map, eng, c, d, sp, note == 0 \|\| sheet, sc, y\);", "and its floor shade, lip bands and shadow");
                RiverSwitchFlipChecks.Has(looks, @"!RM_WaterLookDraw\.IsStillWater\(map, c\) \|\| eng\.IsExcavated\(c\)", "can-fail: the deep tint leaves dug squares to the one sheet");
                RiverSwitchFlipChecks.Has(walls, @"RM_PitReliefMath\.ReprintsFloor\(true, false, BesideLiquidTerrain\(map, c\)\)", "a drained square reprints its floor");
            });
        }

        private static System.Collections.Generic.Dictionary<string, System.Collections.Generic.Dictionary<(int, int), int>> WaterGrids()
        {
            var o = new System.Collections.Generic.Dictionary<string, System.Collections.Generic.Dictionary<(int, int), int>>();
            System.Collections.Generic.Dictionary<(int, int), int> Rect(int x0, int z0, int w, int h, int d,
                System.Collections.Generic.Dictionary<(int, int), int> g = null)
            {
                g = g ?? new System.Collections.Generic.Dictionary<(int, int), int>();
                for (int x = x0; x < x0 + w; x++) for (int z = z0; z < z0 + h; z++) g[(x, z)] = d;
                return g;
            }
            foreach (int d in new[] { 1, 2, 4, 10 }) o["3x3 d" + d] = Rect(0, 0, 3, 3, d);
            o["5x1 d1"] = Rect(0, 0, 5, 1, 1);
            o["1x5 d1"] = Rect(0, 0, 1, 5, 1);
            o["hole in a hole"] = Rect(1, 1, 1, 1, 8, Rect(0, 0, 3, 3, 4));
            o["L d4/d2"] = Rect(0, 2, 2, 2, 4, Rect(0, 0, 4, 2, 2));
            o["stepped 4 beside 8"] = Rect(2, 0, 2, 3, 8, Rect(0, 0, 2, 3, 4));
            o["inner block (corner pieces)"] = Rect(2, 2, 1, 1, 2, Rect(0, 0, 5, 5, 6));
            return o;
        }

        private static bool Inside(float[] p, float x, float z)
        {
            bool c = false;
            int n = p.Length / 2;
            for (int i = 0, j = n - 1; i < n; j = i++)
            {
                float xi = p[2 * i], zi = p[2 * i + 1], xj = p[2 * j], zj = p[2 * j + 1];
                if ((zi > z) != (zj > z) && x < xi + (xj - xi) * (z - zi) / (zj - zi)) c = !c;
            }
            return c;
        }

        private static bool NearEdge(System.Collections.Generic.List<float[]> polys, float x, float z)
        {
            foreach (float[] p in polys)
            {
                int n = p.Length / 2;
                for (int i = 0, j = n - 1; i < n; j = i++)
                {
                    float ax = p[2 * j], az = p[2 * j + 1], dx = p[2 * i] - ax, dz = p[2 * i + 1] - az;
                    float l2 = dx * dx + dz * dz;
                    if (l2 <= 0f) continue;
                    float t = Math.Max(0f, Math.Min(1f, ((x - ax) * dx + (z - az) * dz) / l2));
                    float ex = ax + t * dx - x, ez = az + t * dz - z;
                    if (ex * ex + ez * ez < 4e-6f) return true;
                }
            }
            return false;
        }

        private static float Inv(Func<float, float> f, float target)
        {
            float lo = 0f, hi = 40f;
            for (int k = 0; k < 50; k++)
            {
                float mid = (lo + hi) * 0.5f;
                if (f(mid) < target) lo = mid; else hi = mid;
            }
            return (lo + hi) * 0.5f;
        }

        /// <summary>The oracle: the true depth of the DRY pit's surface seen at (x, z), by inverting the face curves; null off every
        /// region or where two regions meet.</summary>
        private static float? DepthAt(int d, int n, int s, int w, int e, int nw, int ne, float x, float z)
        {
            RM_PitReliefMath.StepPlan f = RM_PitReliefMath.PlanStep(d, n, s, w, e, nw, ne, 0f);
            var polys = new System.Collections.Generic.List<float[]>();
            var kinds = new System.Collections.Generic.List<int>();
            RM_PitReliefMath.ReliefFaces(f, polys, kinds);
            int hit = -1, hits = 0;
            for (int i = 0; i < polys.Count; i++) if (Inside(polys[i], x, z)) { hit = i; hits++; }
            if (hits > 1) return null;
            if (hits == 0)
            {
                float[] r = new float[8];
                int nr = RM_PitReliefMath.FloorRects(f.L, f.R, f.T, f.CnwW, f.CnwH, f.CneW, f.CneH, r);
                for (int i = 0; i < nr; i++) if (r[4 * i] < x && x < r[4 * i + 2] && r[4 * i + 1] < z && z < r[4 * i + 3]) return d;
                return null;
            }
            int cw = f.CnwW > 0f ? polys.Count - (f.CneW > 0f ? 2 : 1) : -1;
            int ce = f.CneW > 0f ? polys.Count - 1 : -1;
            if (kinds[hit] == RM_PitReliefMath.CutNorth) return Inv(RM_PitReliefMath.StepH, (1f - z) + RM_PitReliefMath.StepH(n));
            if (hit == cw) return Inv(RM_PitReliefMath.StepW, x + RM_PitReliefMath.StepW(nw));
            if (hit == ce) return Inv(RM_PitReliefMath.StepW, (1f - x) + RM_PitReliefMath.StepW(ne));
            if (kinds[hit] == RM_PitReliefMath.CutWest) return Inv(RM_PitReliefMath.StepW, x + RM_PitReliefMath.StepW(w));
            return Inv(RM_PitReliefMath.StepW, (1f - x) + RM_PitReliefMath.StepW(e));
        }
    }
}
