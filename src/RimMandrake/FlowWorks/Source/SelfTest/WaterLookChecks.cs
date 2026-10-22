// WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED (owner by card 2026-10-22, "Pick for me: shadow band + navy"): the deep steps past
// 2 m (5 m / 10 m), the navy overlay reproducing the approved mock's pixel rule, the wall shadow band's thickness and gap, and the
// wiring (settings Scribed, drawn, reset; each layer hidden by its setting; no terrain written).
// NOT proven here: how either look reads in game (L1/L4 looks, owed on the item).
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

            Case("WaterLook_wall_band_follows_the_gap_to_the_lip", () =>
            {
                Assert(Math.Abs(RM_WaterLookMath.GapMetres(4, 0, 0.5) - 1.5) < 1e-9, "a 2 m hole with 0.5 m of water: 1.5 m of wall");
                Assert(RM_WaterLookMath.GapMetres(4, 0, 2.0) == 0.0, "full to the brim: no band");
                Assert(RM_WaterLookMath.GapMetres(4, 0, 3.0) == 0.0, "never negative");
                Assert(RM_WaterLookMath.GapMetres(4, 4, 0.5) == 0.0, "a neighbour as deep: no wall on that side");
                Assert(RM_WaterLookMath.GapMetres(4, 6, 0.5) == 0.0, "a deeper neighbour: no wall on that side");
                Assert(Math.Abs(RM_WaterLookMath.GapMetres(8, 6, 0.2) - 0.8) < 1e-9, "a step of 1 m inside a cut, 0.2 m of water");
                Assert(RM_WaterLookMath.BandThickness(0.0) == 0f, "no gap, no band");
                Assert(Math.Abs(RM_WaterLookMath.BandThickness(1.5) - 0.255f) < 1e-6, "0.34 of a square per 2 m");
                Assert(RM_WaterLookMath.BandThickness(0.05) == RM_WaterLookMath.BandMin, "a sliver still shows");
                Assert(RM_WaterLookMath.BandThickness(20.0) == RM_WaterLookMath.BandMax, "at most half a square");
                Assert(RM_WaterLookMath.BandThickness(0.5) < RM_WaterLookMath.BandThickness(1.0), "can-fail: deeper gap, wider band");
                Assert(Math.Abs(RM_WaterLookMath.BandAlpha(false) - 0.75f) < 1e-6 && Math.Abs(RM_WaterLookMath.BandAlpha(true) - 0.6f) < 1e-6,
                    "north 0.75 at the lip, west 0.8 of it");
            });

            Case("WaterLook_settings_and_layers_are_wired", () =>
            {
                string looks = RiverSwitchFlipChecks.Src("RM_WaterLooks.cs");
                string mend = RiverSwitchFlipChecks.Src("RM_WaterBodyMendGame.cs");
                RiverSwitchFlipChecks.Has(looks, @"public static bool deepWaterTintEnabled = true;", "tint ships on");
                RiverSwitchFlipChecks.Has(looks, @"public static bool wetWallBandEnabled = true;", "band ships on");
                RiverSwitchFlipChecks.Has(looks, @"Scribe_Values\.Look\(ref deepWaterTintEnabled, ""waterDeepTintEnabled"", true\);", "tint saved");
                RiverSwitchFlipChecks.Has(looks, @"Scribe_Values\.Look\(ref wetWallBandEnabled, ""waterWallBandEnabled"", true\);", "band saved");
                RiverSwitchFlipChecks.Has(looks, @"RM_SettingsReset\.Snapshot\(typeof\(RM_WaterLookSettings\)\)", "shipped values snapshotted");
                RiverSwitchFlipChecks.Has(looks, @"SettingsKitDrawer\.ResetButton\(list, ResetToShipped\)", "Reset button");
                RiverSwitchFlipChecks.Has(looks, @"Visible => DebugViewSettings\.drawTerrain && RM_WaterLookSettings\.deepWaterTintEnabled;", "tint layer hides when off");
                RiverSwitchFlipChecks.Has(looks, @"Visible => DebugViewSettings\.drawTerrain && RM_WaterLookSettings\.wetWallBandEnabled\s*&& RimMandrakeFlowWorksSettings\.excavationWallFacesEnabled;", "band layer hides when off, and with the wall faces");
                Assert(!Regex.IsMatch(looks, @"SetTerrain|StageNaturalCell|SetTempTerrain"), "the looks write no terrain");
                RiverSwitchFlipChecks.Has(mend, @"RM_WaterLookSettings\.ExposeData\(\);", "Scribed with the water-body screen");
                RiverSwitchFlipChecks.Has(mend, @"RM_WaterLookSettings\.DoSettingsSection\(list\);", "drawn on the water-body screen");
                // the snapshot must sit below the last setting field, or Reset restores a loaded value instead of the shipped one
                int snap = looks.IndexOf("RM_SettingsReset.Snapshot", StringComparison.Ordinal);
                Assert(snap > looks.IndexOf("public static bool wetWallBandEnabled", StringComparison.Ordinal)
                    && snap > looks.IndexOf("public static bool deepWaterTintEnabled", StringComparison.Ordinal), "snapshot below both fields");
            });

            // FlowWorks GPT review 2026-10-22 (RM_WaterLooks.cs:116/207): the looks went stale when water crossed 5 m / 10 m, or a
            // band's gap changed, without a terrain write. The key changes exactly at a tint step or a band rung; nothing else.
            Case("WaterLook_key_changes_at_tint_steps_and_band_rungs_only", () =>
            {
                int Key(double waterMetres, double gapMetres) => RM_WaterLookMath.LookKey(
                    (int)RM_WaterLookMath.StepStrength(RM_WaterLadder.DeepStepForMetres(waterMetres)),
                    RM_WaterLookMath.BandThickness(gapMetres), 0f);
                Assert(Key(4.99, 0) != Key(5.0, 0) && Key(9.99, 0) != Key(10.0, 0), "crossing 5 m and 10 m changes the key");
                Assert(Key(5.2, 0) == Key(9.8, 0) && Key(0.3, 0) == Key(4.9, 0), "inside one tint step the key holds (no redraw)");
                Assert(Key(1, 0) != Key(1, 0.05), "a band appearing changes the key");
                float rung = 1f / RM_WaterLookMath.BandRungsPerSquare;
                double gapPerRung = rung / RM_WaterLookMath.BandPerTwoMetres * 2.0;   // ~0.18 m of gap per band rung
                double centre = 6 * gapPerRung;   // a gap whose band sits exactly on rung 6
                Assert(Key(1, centre) == Key(1, centre + gapPerRung * 0.3) && Key(1, centre) == Key(1, centre - gapPerRung * 0.3),
                    "a band edge moving under a third of a rung holds the key");
                Assert(Key(1, centre) != Key(1, centre + gapPerRung * 1.2), "a band edge moving more than a rung changes it");
                Assert(RM_WaterLookMath.BandRung(RM_WaterLookMath.BandMin) >= 1 && RM_WaterLookMath.BandRung(0f) == 0, "a sliver is a rung");
                Assert(RM_WaterLookMath.LookKey(2, RM_WaterLookMath.BandMax, RM_WaterLookMath.BandMax) != RM_WaterLookMath.LookKey(2, RM_WaterLookMath.BandMax, 0f),
                    "north and west bands do not alias (max rung fits its field)");
                var watch = new RM_WaterLookMath.Watch();
                Assert(!watch.Note(3, 10, 0), "dry ground at load needs no redraw");
                Assert(watch.Note(3, 10, 5) && !watch.Note(3, 10, 5) && watch.Note(3, 10, 6), "a key redraws once per change");
            });

            Case("WaterLook_layers_listen_to_their_own_flag_and_the_engine_runs_the_watcher", () =>
            {
                string looks = RiverSwitchFlipChecks.Src("RM_WaterLooks.cs");
                string eng = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                string def = System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(
                    RiverSwitchFlipChecks.SrcPath("RM_WaterLooks.cs")), "..", "Defs", "ManyWaters", "MapMeshFlagDefs", "RM_WaterLooks.xml"));
                Assert(Regex.Matches(looks, @"relevantChangeTypes = RM_WaterLookDraw\.Flags;").Count == 2, "both layers listen to Terrain | RM_WaterLooks");
                Assert(!looks.Contains("relevantChangeTypes = MapMeshFlagDefOf.Terrain;"), "no layer is terrain-only any more");
                RiverSwitchFlipChecks.Has(looks, @"GetNamedSilentFail\(""RM_WaterLooks""\)", "the flag is looked up by its defName");
                RiverSwitchFlipChecks.Has(def, @"<defName>RM_WaterLooks</defName>", "the flag def exists");
                RiverSwitchFlipChecks.Has(looks, @"MapMeshDirty\(c, flag, true, false\)", "a changed key dirties only the looks' flag, neighbours included");
                RiverSwitchFlipChecks.Has(eng, @"lookWatcher\.Tick\(map, this, excavatedCells\);", "the engine runs the watcher");
                Assert(!Regex.IsMatch(looks, @"new float\[w \* h\];\s*bool any"), "the tint's strength grid is reused, not allocated per regenerate");
            });
        }
    }
}
