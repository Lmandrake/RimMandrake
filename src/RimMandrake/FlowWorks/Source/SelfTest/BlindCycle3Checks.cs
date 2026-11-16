// FlowWorks 0.1.0 blind challenge, cycle 3 (design/concepts/FlowWorks/version/blind_challenge/cycle_3/): cases the blind
// judge added where a planted fault stayed green under its bar's decider (lane2/planted_results.jsonl). Each case is named
// inside its bar's recorded --only glob (Sheet*, Converter*) so the decider runs it.
using System;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class BlindCycle3Checks
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
            // RIMMANDRAKE_PIN_FLOWWORKS_SHEET_SETTINGS_REACH_THE_KERNEL: planted CALLER_SHEET_DOOR_SETTING_IGNORED (the door slider
            // wired to a constant) and SETTINGS_RAIN_READS_PUMP_SWITCH (the rain switch answering for pumps) stayed green under
            // T_SHEET. Verse-bound, so source laws: every tuning slider feeds the kernel's Params in SyncParams, and each inflow's
            // switch answers for that inflow only.
            Case("Sheet_every_setting_reaches_the_kernel_and_its_own_inflow", () =>
            {
                string sync = Body(Src(System.IO.Path.Combine("Sheet", "RM_MapComponent_Sheet.cs")), "private void SyncParams()");
                Assert(sync.Length > 0, "SyncParams found");
                foreach (var (field, setting) in new[] {
                    ("CropKillPulses", "cropDrownPulses"), ("SheetCapDl", "sheetCapCm"), ("MaxWetCells", "maxWetSquares"),
                    ("RetentionDl", "retentionCm"), ("SweepsPerPulse", "sweepsPerPulse"), ("DoorLeakPermille", "doorLeakPercent") })
                    Assert(Regex.IsMatch(sync, @"prm\." + field + @" = [^;]*RM_SheetSettings\." + setting + @"\b[^;]*;"),
                        "can-fail: prm." + field + " is set from RM_SheetSettings." + setting + " every sync");
                string spills = Body(Src(System.IO.Path.Combine("Sheet", "RM_SheetSettings.cs")), "public static bool SpillsFrom(");
                foreach (var (src, flag) in new[] { ("Pump", "spillFromPumps"), ("Rain", "spillFromRain"), ("Flood", "spillFromFloods"),
                    ("FillIn", "spillFromFillIn"), ("Gravity", "spillFromGravity") })
                    Assert(spills.Contains("case RM_SheetMath.Source." + src + ": return " + flag + ";"),
                        "can-fail: the " + src + " inflow answers to its own switch " + flag);
                Assert(spills.Contains("if (!sheetOverflowEnabled)"), "the master switch gates every inflow");
            });

            // RIMMANDRAKE_PIN_FLOWWORKS_CROP_DELAY_TEXT_FOLLOWS_PULSE: planted SETTINGS_CROP_DAYS_LABEL_UNCONVERTED (the slider
            // label converting at the current flow pulse again) and CALLER_SHEET_MESSAGE_DAYS_AT_BASE (the drowning message
            // converting the kernel's pulses at the 250-tick base) stayed green. The stored delay is pulses of the 250-tick base;
            // the kernel's CropKillPulses are pulses of the current flow pulse. Each text must convert with its own pulse.
            Case("Sheet_crop_delay_text_converts_with_its_own_pulse", () =>
            {
                string set = Src(System.IO.Path.Combine("Sheet", "RM_SheetSettings.cs"));
                Assert(!set.Contains("RimMandrakeFlowWorksSettings.PulseIntervalTicks"),
                    "can-fail: the settings page stores and shows the delay at the 250-tick base, never the live flow pulse");
                Assert(Regex.Matches(set, @"RM_SheetMath\.CropDelayBasePulseTicks").Count >= 3,
                    "the label, the slider's days and the stored pulses all use CropDelayBasePulseTicks");
                string sheet = Src(System.IO.Path.Combine("Sheet", "RM_MapComponent_Sheet.cs"));
                Assert(Regex.IsMatch(sheet, @"""Standing water drowned ""[\s\S]{0,400}?prm\.CropKillPulses \* \(float\)RimMandrakeFlowWorksSettings\.PulseIntervalTicks"),
                    "can-fail: the drowning message turns the kernel's pulses into days at the live flow pulse");
            });

            // RIMMANDRAKE_PIN_FLOWWORKS_SHEET_DELAY_UP_AND_DRYING_CAP: planted SHEET_PULSES_ROUND_DOWN and SHEET_HEAT_DRIES_UNCAPPED
            // stayed green under T_SHEET (blind lane 1 caught both). The delay is never shorter than the days set, at any flow
            // pulse; drying speeds up with heat to 3x and no further (the settings text: "Hotter dries faster (up to 3x)").
            Case("Sheet_crop_delay_never_short_and_drying_capped_at_three_times", () =>
            {
                Assert(RM_SheetMath.PulsesFor(1, 250) == 1 && RM_SheetMath.PulsesFor(251, 250) == 2 && RM_SheetMath.PulsesFor(250, 250) == 1,
                    "can-fail: PulsesFor rounds a part pulse up");
                for (int pulse = 60; pulse <= 2500; pulse += 10)
                    for (int halfDays = 1; halfDays <= 60; halfDays++)
                    {
                        int ticks = halfDays * 30000;
                        int stored = Math.Max(1, RM_SheetMath.PulsesFor(ticks, RM_SheetMath.CropDelayBasePulseTicks));
                        long got = (long)RM_SheetMath.CropKillPulsesFor(stored, pulse) * pulse;
                        Assert(got >= ticks && got < ticks + pulse + RM_SheetMath.CropDelayBasePulseTicks,
                            "can-fail: a " + (halfDays / 2f) + "-day delay at a " + pulse + "-tick pulse lasts " + got + " ticks");
                    }
                float maxF = RimMandrake.FlowWorks.Sheet.RM_MapComponent_Sheet_Consts.EvapMaxFactor;
                int at20 = RM_SheetTemp.EvapMilliDl(20 * RM_SheetTemp.PerDegree, 0.5f, maxF, 1f, RM_SheetMath.DlPerCm, 240f);
                int at60 = RM_SheetTemp.EvapMilliDl(60 * RM_SheetTemp.PerDegree, 0.5f, maxF, 1f, RM_SheetMath.DlPerCm, 240f);
                int at120 = RM_SheetTemp.EvapMilliDl(120 * RM_SheetTemp.PerDegree, 0.5f, maxF, 1f, RM_SheetMath.DlPerCm, 240f);
                Assert(at20 > 0 && at60 > 2 * at20, "heat speeds drying (" + at20 + " at 20 C, " + at60 + " at 60 C)");
                Assert(at120 == at60 && Math.Abs(at60 - 3 * at20) <= 1, "can-fail: drying stops speeding up at 3x (" + at60 + " at 60 C, " + at120 + " at 120 C, 3x is " + 3 * at20 + ")");
            });

            // RIMMANDRAKE_PIN_FLOWWORKS_CONVERTER_KEEPS_DRINKERS_RESERVE: planted CALLER_CONVERTER_DRINKS_RESERVE (the converter
            // counting every unit of its input liquid as available) stayed green under T_CONVERT and both thirst tests. Q10
            // (owner 2026-10-17): a machine draws a potable liquid only above the drinkers' reserve. Verse-bound: a source law.
            Case("Converter_caller_keeps_drinkers_reserve", () =>
            {
                string c = Src("Machinery/CompLiquidConverter.cs");
                Assert(Regex.IsMatch(c, @"int n = RM_ConversionMath\.Batches\(capped, step\.InputUnits, step\.OutputUnits, Thirst\.RM_DrinkReserve\.Spendable\(parent, liquid\), room\);"),
                    "can-fail: the batches a converter runs are bounded by what the drinkers' reserve leaves spendable");
                Assert(RM_ThirstMathProbe.SpendableKeepsReserve(), "the kernel keeps a potable reserve back");
            });
        }
    }

    internal static class RM_ThirstMathProbe
    {
        public static bool SpendableKeepsReserve() =>
            RimMandrake.FlowWorks.Thirst.RM_ThirstMath.Spendable(500, 200, true) == 300
            && RimMandrake.FlowWorks.Thirst.RM_ThirstMath.Spendable(150, 200, true) == 0
            && RimMandrake.FlowWorks.Thirst.RM_ThirstMath.Spendable(150, 200, false) == 150;
    }
}

namespace RimMandrake.FlowWorks.Sheet
{
    // EvapMaxFactor lives in the Verse-bound RM_MapComponent_Sheet; the SelfTest cannot compile that file, so the
    // case reads the constant from its source and refuses if it is gone (a stale copy would hide a change)
    internal static class RM_MapComponent_Sheet_Consts
    {
        public static float EvapMaxFactor
        {
            get
            {
                string s = RimMandrake.FlowWorks.SelfTest.RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Sheet", "RM_MapComponent_Sheet.cs"));
                var m = System.Text.RegularExpressions.Regex.Match(s, @"public const float EvapMaxFactor = ([\d.]+)f;");
                if (!m.Success) throw new Exception("EvapMaxFactor not found in RM_MapComponent_Sheet.cs");
                return float.Parse(m.Groups[1].Value, System.Globalization.CultureInfo.InvariantCulture);
            }
        }
    }
}
