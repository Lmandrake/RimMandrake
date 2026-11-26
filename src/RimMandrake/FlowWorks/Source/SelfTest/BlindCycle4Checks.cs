// FlowWorks 0.1.0 blind challenge, cycle 4 (design/concepts/FlowWorks/version/blind_challenge/cycle_4/): cases the blind
// judge added where a planted fault stayed green under its bar's decider (lane2/planted_results.jsonl). Each case is named
// inside its bar's recorded --only glob (Sheet*, Converter*, DrillWhyNot*) so the decider runs it.
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using static RimMandrake.FlowWorks.RM_SheetMath;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class BlindCycle4Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(string rel) => RiverSwitchFlipChecks.Src(rel);

        private static string Body(string src, string head)
        {
            int i = src.IndexOf(head, StringComparison.Ordinal);
            if (i < 0) return "";
            int open = src.IndexOf('{', i), depth = 0;
            for (int k = open; k >= 0 && k < src.Length; k++)
            {
                if (src[k] == '{') depth++;
                else if (src[k] == '}' && --depth == 0) return src.Substring(open, k - open + 1);
            }
            return "";
        }

        public static void Run(Action<string, Action> Case)
        {
            // RIMMANDRAKE_PIN_FLOWWORKS_FILM_NEVER_DROWNS_CROPS: planted SHEET_FILM_DROWNS_CROPS (the crop timer counting a film)
            // stayed green under T_SHEET: its film soaked away long before the delay. A film is held moisture that only
            // irrigates; only standing overflow (sheet tier and up) drowns a crop, however long the film stands.
            Case("Sheet_film_standing_past_the_delay_never_drowns_a_crop", () =>
            {
                var p = new Params();
                var w = new World(5, 3);
                for (int c = 0; c < 15; c++) w.Kinds[c] = Kind.Blocked;
                int film = 1 * 5 + 1, sheet = 1 * 5 + 3;
                w.Kinds[film] = Kind.Open; w.Kinds[sheet] = Kind.Open;   // two walled single squares, no soak, no drying
                var s = new State(5, 3, 4u);
                ResolveSpills(s, w, p, new[] { new SpillOffer { LipNearestFirst = new[] { film }, AmountDl = p.SheetUpDl - 1, Fluid = 1, From = Source.Rain } });
                ResolveSpills(s, w, p, new[] { new SpillOffer { LipNearestFirst = new[] { sheet }, AmountDl = p.SheetUpDl, Fluid = 1, From = Source.Rain } });
                var rep = new PulseReport();
                long sheetFirst = -1;
                for (int i = 0; i < p.CropKillPulses * 2; i++)
                {
                    Pulse(s, w, p, rep);
                    foreach (var (c, _) in rep.CropDrowning)
                    {
                        Assert(c != film, "can-fail: a film (" + s.Dl[film] + " dL, tier " + s.Tiers[film] + ") drowned its crop at pulse " + s.Pulse);
                        if (c == sheet && sheetFirst < 0) sheetFirst = s.Pulse;
                    }
                }
                Assert(s.Tiers[film] == Tier.Film && s.Dl[film] == p.SheetUpDl - 1, "the film stood the whole run (" + s.Dl[film] + " dL, " + s.Tiers[film] + ")");
                Assert(sheetFirst == p.CropKillPulses, "the sheet beside it drowns its crop at the delay (" + sheetFirst + ", not " + p.CropKillPulses + ")");
            });

            // RIMMANDRAKE_PIN_FLOWWORKS_SHEET_SETTINGS_KEEP_THEIR_UNITS: planted CALLER_SHEET_DOOR_PERCENT_AS_PERMILLE (the door
            // slider's percent handed to the kernel as permille, a tenth of the leak) stayed green: the cycle-3 law checks only
            // that each setting is read. Verse-bound, so a source law on the conversion itself: percent x 10 = permille,
            // centimetres x DlPerCm = decilitres.
            Case("Sheet_settings_reach_the_kernel_in_its_units", () =>
            {
                string sync = Body(Src(System.IO.Path.Combine("Sheet", "RM_MapComponent_Sheet.cs")), "private void SyncParams()");
                Assert(sync.Length > 0, "SyncParams found");
                Assert(Regex.IsMatch(sync, @"prm\.DoorLeakPermille = Mathf\.Clamp\(RM_SheetSettings\.doorLeakPercent, 0, 100\) \* 10;"),
                    "can-fail: the door slider's percent reaches the kernel as permille (x 10)");
                Assert(Regex.IsMatch(sync, @"prm\.SheetCapDl = [^;]*RM_SheetSettings\.sheetCapCm \* DlPerCm\b[^;]*;"),
                    "can-fail: the sheet cap's centimetres reach the kernel as decilitres (x DlPerCm)");
                Assert(Regex.IsMatch(sync, @"prm\.RetentionDl = [^;]*RM_SheetSettings\.retentionCm \* DlPerCm\b[^;]*;"),
                    "can-fail: retention's centimetres reach the kernel as decilitres (x DlPerCm)");
                Assert(DlPerCm == 200, "1 cm over a square is 200 dL (" + DlPerCm + ")");
            });

            // RIMMANDRAKE_CLASS_SEVEN_THIRST_FAILS_SITE_FULL_OF_PATIENTS (CROPS_IRRIGATE_THEN_DROWN, live 2026-11-25/26): SyncParams
            // ran only when a map's kernel was built (load, first spill) and when a new liquid first spilled, so a slider moved
            // in a running game (crop-drown delay, sheet cap, wet-square limit, retention, sweeps, door leak) never reached the
            // kernel until a reload. Every pulse re-reads the Mod Settings before the kernel steps.
            Case("Sheet_settings_reach_the_kernel_mid_game", () =>
            {
                string pulse = Body(Src(System.IO.Path.Combine("Sheet", "RM_MapComponent_Sheet.cs")), "public void EnginePulse()");
                Assert(pulse.Length > 0, "EnginePulse found");
                int sync = pulse.IndexOf("SyncParams();", StringComparison.Ordinal);
                int step = pulse.IndexOf("RM_SheetMath.Pulse(state, world, prm, rep);", StringComparison.Ordinal);
                Assert(step > 0, "the kernel step found in EnginePulse");
                Assert(sync > 0 && sync < step, "can-fail: each pulse re-reads the Mod Settings (SyncParams) before the kernel steps");
            });

            // RIMMANDRAKE_PIN_FLOWWORKS_CONVERTER_CALLER_RATE_AND_SUN: planted CALLER_CONV_RATE_SETTING_IGNORED (the throughput
            // slider dropped from the budget) and CALLER_CONV_SUN_FACTOR_SKIPPED (a solar still running at night) stayed green
            // under T_CONVERT: the kernel's rate and sun maths are tested, the caller's use of them was not. Source laws.
            Case("Converter_caller_budget_scales_by_the_throughput_setting", () =>
            {
                string tick = Body(Src("Machinery/CompLiquidConverter.cs"), "public override void CompTickRare()");
                Assert(tick.Length > 0, "CompTickRare found");
                Assert(Regex.IsMatch(tick, @"float perTick = RM_ConversionMath\.BudgetPerRareTick\([^;]*RM_MachinerySettings\.converterRateMultiplier, env\);"),
                    "can-fail: the budget is scaled by the Mod Setting's converter throughput and the environment");
                Assert(Regex.IsMatch(tick, @"accrued \+= perTick;"), "the budget accrues every rare tick");
                float a = RimMandrake.FlowWorks.Machinery.RM_ConversionMath.BudgetPerRareTick(240f, 1f, 1f, 1f);
                float b = RimMandrake.FlowWorks.Machinery.RM_ConversionMath.BudgetPerRareTick(240f, 1f, 2.5f, 1f);
                Assert(Math.Abs(b - 2.5f * a) < 1e-4f, "the kernel's budget is linear in the throughput setting");
            });

            Case("Converter_caller_solar_still_reads_the_sky", () =>
            {
                string src = Src("Machinery/CompLiquidConverter.cs");
                string env = Body(src, "private float EnvironmentFactor(out string why)");
                Assert(env.Length > 0, "EnvironmentFactor found");
                Assert(Regex.IsMatch(env, @"if \(Props\.needsSun\)\s*\{\s*float f = RM_ConversionMath\.SunFactor\(parent\.Map\.skyManager\.CurSkyGlow, parent\.Position\.Roofed\(parent\.Map\)\);[\s\S]*?return f;"),
                    "can-fail: a solar still's factor is the kernel's SunFactor of the live sky glow and roof");
                string tick = Body(src, "public override void CompTickRare()");
                Assert(Regex.IsMatch(tick, @"float env = EnvironmentFactor\(out string why\);\s*if \(env <= 0f\)\s*\{[^}]*return;"),
                    "can-fail: a machine whose environment factor is 0 (night, off, no power, no fuel) does nothing that tick");
                Assert(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.SunFactor(0.2f, false) == 0f, "the kernel gives a solar still nothing at night");
            });

            // RIMMANDRAKE_PIN_FLOWWORKS_DRILL_CALLER_READS_SETTING: planted CALLER_DRILL_IGNORES_SETTING (the drill's Mod Setting
            // switch never reaching WhyNot, so a drill pours with drilling switched off) stayed green under T_DRILL. Source law.
            Case("DrillWhyNot_caller_reads_the_drilling_setting", () =>
            {
                string src = Src("Drilling/Building_LiquidDrill.cs");
                string cur = Body(src, "public RM_DrillSurveyMath.Block CurrentBlock()");
                Assert(cur.Length > 0, "CurrentBlock found");
                Assert(Regex.IsMatch(cur, @"st\.settingOn = RimMandrakeFlowWorksSettings\.liquidDrillingEnabled;"),
                    "can-fail: the drilling Mod Setting reaches WhyNot as settingOn");
                string tick = Body(src, "public override void TickRare()");
                Assert(Regex.IsMatch(tick, @"lastBlock = CurrentBlock\(\);\s*if \(lastBlock != RM_DrillSurveyMath\.Block\.None && lastBlock != RM_DrillSurveyMath\.Block\.OutletBrimming\)\s*\{\s*return;"),
                    "can-fail: the tick pours only when CurrentBlock says None (or brimming, which backs up)");
                var st = new RimMandrake.FlowWorks.Drilling.RM_DrillSurveyMath.State
                {
                    settingOn = false, switchedOn = true, powered = true, surveyed = true, hasYield = true, reserve = 10f,
                    hasCanalForm = true, fluidAllowed = true, outletDug = true,
                };
                Assert(RimMandrake.FlowWorks.Drilling.RM_DrillSurveyMath.WhyNot(st) == RimMandrake.FlowWorks.Drilling.RM_DrillSurveyMath.Block.DisabledInSettings,
                    "the kernel blocks a drill whose setting is off");
            });
        }
    }
}
