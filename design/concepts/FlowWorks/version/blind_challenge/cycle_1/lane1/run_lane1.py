#!/usr/bin/env python3
"""Run blind lane 1 (FlowWorks 0.1.0, cycle 1) against the shipped kernels, or against a substitute kernel file.
    python3 run_lane1.py [--kernel <path> ...] [--src <FlowWorks/Source>] [--out <rows.jsonl>]
--kernel replaces the shipped kernel of the same file name (repeatable). The shipped settings (defaults, read from the
settings files with a regex, never hand-copied) go to the test in FW_* variables (WSLENV carries them to dotnet.exe).
Stages BlindLane1.cs + the kernels under <agent storage>/scratch/fw_blind_lane1 (dotnet.exe cannot build from a WSL path),
builds and runs with the per-user Windows dotnet, writes one JSON row per line, prints the verdict counts.
Exit 0 = every decided row PASS; 1 = a row FAILed; 2 = build or run failure."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/FlowWorks/Source")
KERNELS = ["RM_SheetMath.cs", "RM_Volume.cs", "RM_FireMath.cs", "RM_FloodReleaseMath.cs", "Machinery/RM_ConversionMath.cs",
           "Thirst/RM_ThirstMath.cs", "LiquidTypes/RM_ContainerStyleMath.cs", "RM_StockMath.cs", "Drilling/RM_DrillSurveyMath.cs",
           "Sprinklers/RM_SprinklerKernel.cs", "Sprinklers/RM_PipeSeatMath.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0162;CS0168;CS0219</NoWarn></PropertyGroup></Project>"""
# (env var, file under Source, regex with one group) -- the shipped default of each setting the rows read
SETTINGS = [
    ("FW_SHEET_ON", "Sheet/RM_SheetSettings.cs", r"public static bool sheetOverflowEnabled = (true|false);"),
    ("FW_SHEET_CAP_CM", "Sheet/RM_SheetSettings.cs", r"public static int sheetCapCm = (\d+);"),
    ("FW_MAX_WET", "Sheet/RM_SheetSettings.cs", r"public static int maxWetSquares = (\d+);"),
    ("FW_RETENTION_CM", "Sheet/RM_SheetSettings.cs", r"public static float retentionCm = ([\d.]+)f;"),
    ("FW_SWEEPS", "Sheet/RM_SheetSettings.cs", r"public static int sweepsPerPulse = (\d+);"),
    ("FW_DOOR_LEAK", "Sheet/RM_SheetSettings.cs", r"public static int doorLeakPercent = (\d+);"),
    ("FW_CROP_PULSES", "Sheet/RM_SheetSettings.cs", r"public static int cropDrownPulses = (\d+);"),
    ("FW_PULSE_TICKS", "RimMandrakeFlowWorksMod.cs", r"public static float pulseIntervalTicks = ([\d.]+)f;"),
    ("FW_CONV_MULT", "Machinery/RM_MachinerySettings.cs", r"public static float converterRateMultiplier = ([\d.]+)f;"),
    ("FW_THIRST_RATE", "Thirst/RM_ThirstSettings.cs", r"public static float thirstRateMultiplier = ([\d.]+)f;"),
    ("FW_RESERVE_L", "Thirst/RM_ThirstSettings.cs", r"public static float drinkingReserveLitres = ([\d.]+)f;"),
    ("FW_BOTTLES_PER", "Thirst/RM_ThirstSettings.cs", r"public static int filledBottlesPerColonist = (\d+);"),
    ("FW_SPRINKLER_L", "Sprinklers/RM_SprinklerSettings.cs", r"public static float sprinklerLitresPerCellHour = RM_SprinklerKernel\.RuledLitresPerCellHour;"),
    ("FW_SPRINKLER_R", "Sprinklers/RM_SprinklerSettings.cs", r"public static float sprinklerNativeRadius = RM_SprinklerKernel\.NativeRadius;"),
    ("FW_DRILL_ON", "RimMandrakeFlowWorksMod.cs", r'Scribe_Values\.Look\(ref liquidDrillingEnabled, "liquidDrillingEnabled", (true|false)\);'),
    ("FW_DRILL_YIELD", "RimMandrakeFlowWorksMod.cs", r'Scribe_Values\.Look\(ref drillYieldChanceMultiplier, "drillYieldChanceMultiplier", ([\d.]+)f\);'),
    ("FW_DRILL_UNITS", "RimMandrakeFlowWorksMod.cs", r'Scribe_Values\.Look\(ref drillUnitsPerCycle, "drillUnitsPerCycle", ([\d.]+)f\);'),
]
KERNEL_CONST = {"FW_SPRINKLER_L": (r"RuledLitresPerCellHour = ([\d.]+)f;", "Sprinklers/RM_SprinklerKernel.cs"),
                "FW_SPRINKLER_R": (r"NativeRadius = ([\d.]+)f;", "Sprinklers/RM_SprinklerKernel.cs")}


def settings_env(src):
    env = {}
    for var, rel, rx in SETTINGS:
        try:
            m = re.search(rx, open(os.path.join(src, rel), encoding="utf-8").read())
        except OSError:
            m = None
        if not m:
            continue  # unread: the row reports it
        if var in KERNEL_CONST and not m.groups():
            krx, krel = KERNEL_CONST[var]
            k = re.search(krx, open(os.path.join(src, krel), encoding="utf-8").read())
            if k:
                env[var] = k.group(1)
            continue
        v = m.group(1)
        env[var] = {"true": "1", "false": "0"}.get(v, v)
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
    stage = os.path.join(root, "scratch", os.environ.get("FW_LANE1_STAGE", "fw_blind_lane1"))
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    subs = {os.path.basename(k): k for k in a.kernel}
    for rel in KERNELS:
        b = os.path.basename(rel)
        shutil.copy(subs.pop(b, os.path.join(a.src, rel)), os.path.join(stage, b))
    if subs:
        sys.exit("no shipped kernel named " + ", ".join(subs))
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400)
    if b.returncode:
        print("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
        sys.exit(2)
    senv = settings_env(a.src)
    env = dict(os.environ, **senv)
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", "")] + list(senv)))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    with open(a.out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows:
        c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL":
            print("FAIL", row["id"], row["detail"][:400])
    if r.returncode not in (0, 1) or not rows:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
        sys.exit(2)
    sys.exit(r.returncode)


main()
