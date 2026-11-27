#!/usr/bin/env python3
"""Run blind lane 1 (FlowWorks 0.1.0, cycle 5) against the shipped kernels, or substitute kernel files.

    python3 run_lane1.py [--kernel <path to a kernel .cs>]... [--src <FlowWorks dir>] [--out <rows.jsonl>]

BlindLane1.cs compiles against the six offline kernels (RM_SheetMath, RM_ConversionMath, RM_DrillSurveyMath,
RM_SprinklerKernel, RM_ContainerStyleMath, RM_ThirstMath) and the three files they use (RM_Volume, RM_FireMath,
RM_StockMath). A --kernel file replaces the staged file of the same name (planted faults reuse this). The shipped settings
defaults go to the test as FW_* variables read from the settings files by regex (never hand-copied; WSLENV carries them to
dotnet.exe). The Python rows check each settings file's field initializers against its Scribe defaults, and write one
not_kernel row per bar whose logic is game-side.
Stage: /mnt/d/ClaudeWork/rimmandrake/scratch/flowworks_blind_c5_lane1/ (dotnet.exe cannot build from a WSL path); override
with FW_LANE1_STAGE (plant_faults.py uses its own).
Exit 0 = no FAIL row; 1 = a FAIL row; 2 = build or run failure (no rows written)."""
import argparse, glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/FlowWorks")
CONCEPT = os.path.join(REPO, "design/concepts/FlowWorks")
STAGE = os.environ.get("FW_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/flowworks_blind_c5_lane1")
KERNELS = ["RM_SheetMath.cs", "Machinery/RM_ConversionMath.cs", "Drilling/RM_DrillSurveyMath.cs", "Sprinklers/RM_SprinklerKernel.cs",
           "LiquidTypes/RM_ContainerStyleMath.cs", "Thirst/RM_ThirstMath.cs", "RM_Volume.cs", "RM_FireMath.cs", "RM_StockMath.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0162;CS0168;CS0219</NoWarn></PropertyGroup></Project>"""
SETTINGS = {  # file -> class marker (fields read inside it)
    "Source/Sheet/RM_SheetSettings.cs": "class RM_SheetSettings",
    "Source/Thirst/RM_ThirstSettings.cs": "class RM_ThirstSettings",
    "Source/Sprinklers/RM_SprinklerSettings.cs": "class RM_SprinklerSettings",
    "Source/Machinery/RM_MachinerySettings.cs": "class RM_MachinerySettings",
}
WANT_ENV = ["pulseIntervalTicks", "cropDrownPulses", "sheetOverflowEnabled", "converterRateMultiplier", "thirstRateMultiplier",
            "drinkingReserveLitres", "filledBottlesPerColonist", "sprinklerLitresPerCellHour"]
DECL_RX = re.compile(r"public static (bool|float|int) ([^;]+);")


class _Fields:
    """public static T a = x, b = y; -> (T, a, x), (T, b, y)"""
    @staticmethod
    def findall(body):
        out = []
        for t, rest in DECL_RX.findall(body):
            for part in rest.split(","):
                if "=" in part and "(" not in part:
                    n, v = part.split("=", 1)
                    out.append((t, n.strip(), v.strip()))
        return out


FIELD_RX = _Fields
CONSTS = {"RM_SprinklerKernel.RuledLitresPerCellHour": "0.5", "RM_SprinklerKernel.NativeRadius": "2.9"}


def norm(v):
    v = CONSTS.get(v.strip(), v.strip())
    if v in ("true", "false"):
        return v
    try:
        return float(v.rstrip("f"))
    except ValueError:
        return v


def all_fields(src):
    out = {}
    for rel, marker in list(SETTINGS.items()) + [("Source/RimMandrakeFlowWorksMod.cs", "class RimMandrakeFlowWorksSettings")]:
        text = open(os.path.join(src, rel), encoding="utf-8").read()
        i = text.find(marker)
        body = text[i:] if i >= 0 else text
        for t, n, v in FIELD_RX.findall(body):
            out.setdefault(n, (t, v.strip(), rel))
    return out


def row(rows, id_, bars, kind, verdict, cases, detail):
    rows.append({"id": id_, "bars": bars, "kind": kind, "verdict": verdict, "cases": cases, "detail": detail})


def settings_rows(src, rows):
    bad, n = [], 0
    for rel, marker in SETTINGS.items():
        text = open(os.path.join(src, rel), encoding="utf-8").read()
        body = text[text.find(marker):]
        fields = {nm: (t, v) for t, nm, v in FIELD_RX.findall(body)}
        scribe = {m.group(1): m.group(3) for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "(\w+)", ([^)]+)\);', body)}
        for nm, (t, v) in fields.items():
            if nm not in scribe:
                continue  # derived or unsaved (read by its own reader)
            n += 1
            if norm(scribe[nm]) != norm(v):
                bad.append("%s %s: initializer %s, Scribe default %s" % (os.path.basename(rel), nm, v, scribe[nm]))
    bars = ["inv_overflow_sheet", "inv_bottles_thirst", "inv_sprinklers", "inv_converters"]
    row(rows, "L1_FIXED_SETTINGS_INITIALIZER_EQUALS_SCRIBE_DEFAULT", bars, "fixed", "FAIL" if bad else "PASS", n,
        "; ".join(bad[:10]) if bad else "%d saved settings in the sheet, thirst, sprinkler and machinery files: each field's initializer equals its Scribe default (a fresh install and a loaded save start alike)" % n)


def not_kernel_rows(rows):
    text = open(os.path.join(CONCEPT, "version/bars.md"), encoding="utf-8").read()
    ids = re.findall(r"^- `(\w+)`", text, re.M)
    offline = {"inv_overflow_sheet", "inv_converters", "inv_bottles_thirst", "inv_drilling", "inv_sprinklers"}
    covered = {}
    for r in rows:
        for b in r["bars"]:
            covered.setdefault(b, []).append(r["id"])
    for b in ids:
        if b in offline:
            continue
        k = covered.get(b, [])
        row(rows, "L1_NOT_KERNEL_" + b.upper(), [b], "not_kernel", "UNSETTLED", 0,
            "game-side: what the player sees is decided by this bar's in-game scene (Stage 6 or the walk), not by an offline kernel. "
            + ("Its kernel half is tested in " + ", ".join(k) + "." if k else "No offline kernel of this lane carries its logic.")
            + " Settled by: that scene's run on a game, on this build.")
    return len(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--src", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    os.makedirs(STAGE, exist_ok=True)
    for f in glob.glob(os.path.join(STAGE, "*.cs")):
        os.remove(f)
    subs = {os.path.basename(k): k for k in a.kernel}
    for k in KERNELS:
        b = os.path.basename(k)
        shutil.copy(subs.get(b, os.path.join(a.src, "Source", k)), os.path.join(STAGE, b))
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), STAGE)
    open(os.path.join(STAGE, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=400)  # a hang guard: a build measured about 10 s
    if b.returncode:
        print("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
        sys.exit(2)
    fields = all_fields(a.src)
    senv = {}
    for n in WANT_ENV:
        if n in fields:
            t, v, _ = fields[n]
            nv = norm(v)
            senv["FW_" + n] = ("1" if nv == "true" else "0") if t == "bool" else str(nv)
    env = dict(os.environ, **senv)
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", "")] + list(senv)))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=500)  # a hang guard: a run measured under a minute
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not rows:
        print("RUN FAILED rc %s\n%s\n%s" % (r.returncode, r.stdout[-1500:], r.stderr[-2000:]))
        sys.exit(2)
    settings_rows(a.src, rows)
    nbars = not_kernel_rows(rows)
    with open(a.out, "w") as f:
        for row_ in rows:
            f.write(json.dumps(row_) + "\n")
    c = {}
    for row_ in rows:
        c[row_["verdict"]] = c.get(row_["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "bars", nbars, "->", a.out)
    for row_ in rows:
        if row_["verdict"] == "FAIL":
            print("FAIL", row_["id"], row_["detail"][:600])
    sys.exit(1 if c.get("FAIL") else 0)


main()
