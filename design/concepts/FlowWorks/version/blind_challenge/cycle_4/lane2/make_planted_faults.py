import json, os
REPO = os.getcwd()
FW = "src/RimMandrake/FlowWorks/Source/"
SH = "Depth*,FloodRelease*,Outflow*,Overflow*,Sheet*"; SHPY = ["python3 src/RimMandrake/FlowWorks/selftest_flowworks_sheet_drown_message.py"]
CV = "Converter*,Fuzz*,Gpt1016*,GptA*,P2*,Transfer*"
TH = "BottleLoop*,ContainerStyle*,Thirst*"; THPY = ["python3 src/RimMandrake/FlowWorks/Tools/selftest_water_not_food.py", "python3 src/RimMandrake/FlowWorks/selftest_natives_drink_own_water.py"]
DR = "CoverFloor*,DrillSurvey*,DrillWhyNot*"; SP = "Sprinkler*"
F = []
def add(i, f, old, new, bars, stock=None, py=None, kind="kernel"):
    F.append({"id": i, "file": f, "old": old, "new": new, "bars": bars, "stock": stock, "py": py or [], "where": kind})
S = FW + "RM_SheetMath.cs"
add("SHEET_CROP_WEEK_PLUS_ONE", S, "if (s.Stand[c] >= p.CropKillPulses) rep?.CropDrowning.Add", "if (s.Stand[c] > p.CropKillPulses) rep?.CropDrowning.Add", ["inv_overflow_sheet"], SH, SHPY)
add("SHEET_FILM_DROWNS_CROPS", S, "if (t >= p.CropStandMinTier)", "if (t >= Tier.Film)", ["inv_overflow_sheet"], SH, SHPY)
add("SHEET_SOAK_UNCOUNTED", S, "if (take > 0) { s.Dl[c] -= take; s.Soaked += take; rep?.Soaked", "if (take > 0) { s.Dl[c] -= take; rep?.Soaked", ["inv_overflow_sheet"], SH, SHPY)
add("SHEET_CROP_DELAY_IGNORES_PULSE", S, "(long)Math.Max(1, pulsesAtBase) * CropDelayBasePulseTicks), pulseIntervalTicks));", "(long)Math.Max(1, pulsesAtBase) * CropDelayBasePulseTicks), CropDelayBasePulseTicks));", ["inv_overflow_sheet"], SH, SHPY)
add("SHEET_DOOR_ZERO_LEAKS", S, "if (p.DoorLeakPermille <= 0) continue;   // GPT deep review 2026-10-22 #10: the 0% setting seals a door", "// seal removed", ["inv_overflow_sheet"], SH, SHPY)
add("SHEET_LIQUIDS_MIX", S, "private static bool Compatible(byte a, byte b) => a == 0 || b == 0 || a == b;", "private static bool Compatible(byte a, byte b) => true;", ["inv_overflow_sheet"], SH, SHPY)
add("SHEET_SAVE_DROPS_CALM", S, "bw.Write(s.Stand[c]); bw.Write(s.Calm[c]);", "bw.Write(s.Stand[c]); bw.Write((byte)0);", ["inv_overflow_sheet"], SH, SHPY)
add("SHEET_FREEZES_AT_ZERO", S, "if (fr.NeverFreezes || w.TempDeciC[c] >= fr.FreezeDeciC) continue;", "if (fr.NeverFreezes || w.TempDeciC[c] > fr.FreezeDeciC) continue;", ["inv_overflow_sheet"], SH, SHPY)
C = FW + "Machinery/RM_ConversionMath.cs"
add("CONV_CAP_DROPS_EXTRA_BATCH", C, "perTick > inputUnits ? perTick + inputUnits : inputUnits", "perTick > inputUnits ? perTick : inputUnits", ["inv_converters"], CV)
add("CONV_CLIPPED_INCOME_LOST", C, "return Math.Max(0f, Math.Min(accrued - capped, perTick));", "return 0f;", ["inv_converters"], CV)
add("CONV_BLOCKED_TAKES_FIRST_CAP", C, "if (capped[i] > best) best = capped[i];", "if (false) best = capped[i];", ["inv_converters"], CV)
add("CONV_IGNORES_OUTPUT_ROOM", C, "n = Math.Min(n, outputRoom / outputUnits);", "n = Math.Min(n, int.MaxValue);", ["inv_converters"], CV)
add("CONV_ROTATION_STUCK_FIRST", C, "int i = ((last < 0 ? -1 : last) + k) % n;", "int i = (k - 1) % n;", ["inv_converters"], CV)
add("CONV_SUN_AT_DUSK", C, "return !roofed && skyGlow >= 0.5f ? 1f : 0f;", "return !roofed && skyGlow >= 0.3f ? 1f : 0f;", ["inv_converters"], CV)
add("CONV_SUN_AT_NIGHT", C, "return !roofed && skyGlow >= 0.5f ? 1f : 0f;", "return !roofed ? 1f : 0f;", ["inv_converters"], CV)
add("CALLER_CONV_SUN_FACTOR_SKIPPED", FW + "Machinery/CompLiquidConverter.cs", "float f = RM_ConversionMath.SunFactor(parent.Map.skyManager.CurSkyGlow, parent.Position.Roofed(parent.Map));", "float f = 1f;", ["inv_converters"], CV, kind="caller")
T = FW + "Thirst/RM_ThirstMath.cs"
add("THIRST_FALL_SLOWER", T, "public const float BaseFallPerDay = 0.8f;", "public const float BaseFallPerDay = 0.6f;", ["inv_bottles_thirst"], TH, THPY)
add("THIRST_HEAT_UNCAPPED", T, "return f > HeatCap ? HeatCap : f;", "return f;", ["inv_bottles_thirst"], TH, THPY)
add("THIRST_LAST_RESORT_SWITCH_IGNORED", T, "return lastResortAllowed && Desperate(level);", "return Desperate(level);", ["inv_bottles_thirst"], TH, THPY)
add("THIRST_RESERVE_HALVED", T, "return available > reserveUnits ? available - reserveUnits : 0;", "return available > reserveUnits ? available - reserveUnits / 2 : 0;", ["inv_bottles_thirst"], TH, THPY)
add("THIRST_BOTTLE_HYDRATES_DOUBLE", T, "return litres / LitresPerFullNeed * HydrateFactor(quality, qualityEffects);", "return litres / 1.5f * HydrateFactor(quality, qualityEffects);", ["inv_bottles_thirst"], TH, THPY)
add("THIRST_ANIMALS_DRINK_ANYTHING", T, "\t\t\t\treturn native;\n", "\t\t\t\treturn true;\n", ["inv_bottles_thirst"], TH, THPY)
D = FW + "Drilling/RM_DrillSurveyMath.cs"
add("DRILL_SPENT_RESERVE_ALLOWED", D, "return reserve <= 0f ? Verdict.Spent : Verdict.Allowed;", "return Verdict.Allowed;", ["inv_drilling"], DR)
add("DRILL_UNPOWERED_POURS", D, "if (s.needsPower && !s.powered) return Block.Unpowered;", "// power check removed", ["inv_drilling"], DR)
add("DRILL_CHARGES_WHOLE_LEVELS", D, "return (float)((afterDl - beforeDl) / (double)dlPerLevel) * unitPerLevel;", "return (float)System.Math.Ceiling((afterDl - beforeDl) / (double)dlPerLevel) * unitPerLevel;", ["inv_drilling"], DR)
P = FW + "Sprinklers/RM_SprinklerKernel.cs"
add("SPRK_PART_PAID_SPRAYS", P, "if (available < need) return RM_SprinklerState.Dry;", "if (available <= 0) return RM_SprinklerState.Dry;", ["inv_sprinklers"], SP)
add("SPRK_NO_PUMP_SPRAYS", P, "if (!pressure) return RM_SprinklerState.NoPressure;", "// pressure check removed", ["inv_sprinklers"], SP)
add("SPRK_COST_ROUNDS_DOWN", P, "return (int)Math.Ceiling(Math.Round(cells * (double)litresPerCellHour * unitsPerLitre, 3));", "return (int)Math.Floor(Math.Round(cells * (double)litresPerCellHour * unitsPerLitre, 3));", ["inv_sprinklers"], SP)
add("SPRK_VALVE_IGNORES_RESERVE", P, "if (reserveUnits > 0) cap = Math.Min(", "if (reserveUnits > 1000000) cap = Math.Min(", ["inv_sprinklers"], SP)
add("SPRK_NO_GRACE", P, "public static int WetUntil(int now) => now + PulseTicks + GraceTicks;", "public static int WetUntil(int now) => now + PulseTicks;", ["inv_sprinklers"], SP)
# game-side callers and patches
CC = FW + "Machinery/CompLiquidConverter.cs"
add("CALLER_CONV_CLIPPED_NOT_ADDED_BACK", CC, "accrued += clipped;   // CAP_EATS_CHANGE", "accrued += 0f;   // CAP_EATS_CHANGE", ["inv_converters"], CV, kind="caller")
add("CALLER_CONV_BATCHES_FREE", CC, "accrued -= n * step.InputUnits;", "accrued -= 0;", ["inv_converters"], CV, kind="caller")
add("CALLER_CONV_RATE_SETTING_IGNORED", CC, "RM_MachinerySettings.converterRateMultiplier, env);", "1f, env);", ["inv_converters"], CV, kind="caller")
RS = FW + "Sprinklers/RM_Sprinkle.cs"
add("CALLER_SPRK_NO_PUMP_NEEDED", RS, "bool pressure = enabled && switchOn && HasPressure(head);", "bool pressure = enabled && switchOn;", ["inv_sprinklers"], SP, kind="caller")
add("CALLER_SPRK_DRINKS_RESERVE", RS, "held = Thirst.RM_DrinkReserve.Spendable(head, l);   // Q10: drinkers first", "held = parts.Sum(p => p.Key == pick ? p.Value : 0);", ["inv_sprinklers", "inv_bottles_thirst"], SP + "," + TH, THPY, kind="caller")
BD = FW + "Drilling/Building_LiquidDrill.cs"
add("CALLER_DRILL_SPENDS_ASKED", BD, "pendingUnits -= RM_DrillSurveyMath.SpentUnits(beforeDl, excavation.WaterDlAt(outlet), RM_LevelSolve.U, unitPerLevel);", "pendingUnits = 0f;", ["inv_drilling"], DR, kind="caller")
add("CALLER_DRILL_IGNORES_SETTING", BD, "st.settingOn = RimMandrakeFlowWorksSettings.liquidDrillingEnabled;", "st.settingOn = true;", ["inv_drilling"], DR, kind="caller")
MS = FW + "Sheet/RM_MapComponent_Sheet.cs"
add("CALLER_SHEET_CROP_DELAY_AT_BASE", MS, "prm.CropKillPulses = RM_SheetMath.CropKillPulsesFor(RM_SheetSettings.cropDrownPulses, RimMandrakeFlowWorksSettings.PulseIntervalTicks);", "prm.CropKillPulses = RM_SheetMath.CropKillPulsesFor(RM_SheetSettings.cropDrownPulses, RM_SheetMath.CropDelayBasePulseTicks);", ["inv_overflow_sheet"], SH, SHPY, kind="caller (changed file BlindCycle3Checks.cs law)")
add("CALLER_SHEET_DOOR_PERCENT_AS_PERMILLE", MS, "prm.DoorLeakPermille = Mathf.Clamp(RM_SheetSettings.doorLeakPercent, 0, 100) * 10;", "prm.DoorLeakPermille = Mathf.Clamp(RM_SheetSettings.doorLeakPercent, 0, 100);", ["inv_overflow_sheet"], SH, SHPY, kind="caller (changed file BlindCycle3Checks.cs law)")
add("CALLER_SHEET_CROPS_DROWN_SWITCH_IGNORED", MS, "if (RM_SheetSettings.cropsDrownEnabled && rep.CropDrowning.Count > 0)", "if (rep.CropDrowning.Count > 0)", ["inv_overflow_sheet"], SH, SHPY, kind="caller")
TR = FW + "Thirst/RM_DrinkReserve.cs"
add("CALLER_RESERVE_NEVER_POTABLE", TR, "liquid != null && liquid.AutoGathered);", "false);", ["inv_bottles_thirst", "inv_converters", "inv_sprinklers"], CV + "," + TH + "," + SP, THPY, kind="caller")
# changed files: FlowKernelFuzz.cs (its kernel), glow_tank_live.py, pit draw census
K = FW + "RM_FlowKernel.cs"
add("CHANGED_FUZZ_SINK_UNREPORTED", K, "sinkDrained += total / (float)RM_LevelSolve.U;", "sinkDrained += 0f * total;", ["inv_flow_level"], "Kernel*", kind="changed: FlowKernelFuzz.cs")
add("CHANGED_FUZZ_SINK_DRAIN_UNREPORTED", K, "sinkDrained += drained / (float)U;", "sinkDrained += 0f * drained;", ["inv_flow_level"], "Kernel*", kind="changed: FlowKernelFuzz.cs")
G = "src/RimMandrake/FlowWorks/northstar/glow_tank_live.py"
GPY = ["python3 src/RimMandrake/FlowWorks/northstar/selftest_glow_tank_live.py"]
add("CHANGED_GLOW_GROWN_TENTHS", G, "out.append(float(m.group(1)) / 100.0)", "out.append(float(m.group(1)) / 10.0)", ["inv_looks"], None, GPY, kind="changed: glow_tank_live.py")
add("CHANGED_GLOW_ROOM_SHORT", G, "return (ox, z - 2, 10, 6)", "return (ox, z - 2, 10, 5)", ["inv_looks"], None, GPY, kind="changed: glow_tank_live.py")
PCPY = ["python3 src/RimMandrake/FlowWorks/selftest_flowworks_pit_draw_census.py"]
add("CHANGED_CENSUS_GATE_ROUTE_GONE", FW + "Superdeep/RM_SubmergeDraw.cs", "return RM_SubmergeDraw.BeginRealtime(__instance, phase)", "return RM_SubmergeDraw.BeginRealtime(__instance, DrawPhase.Draw)", ["inv_pits"], None, PCPY, kind="changed: selftest_flowworks_pit_draw_census.py")
add("CHANGED_CENSUS_PREDRAW_GATE_FLIPPED", FW + "Superdeep/RM_SubmergeDraw.cs", "phase != DrawPhase.Draw", "phase == DrawPhase.Draw", ["inv_pits"], None, PCPY, kind="changed: selftest_flowworks_pit_draw_census.py")
out = []
for f in F:
    p = os.path.join(REPO, f["file"]); n = open(p, encoding="utf-8").read().count(f["old"])
    if n != 1: print("NOT UNIQUE", n, f["id"])
json.dump({"cycle": 4, "run": "judge-1795134433", "faults": F}, open("design/concepts/FlowWorks/version/blind_challenge/cycle_4/lane2/planted_faults.json", "w"), indent=1)
print(len(F), "faults")
