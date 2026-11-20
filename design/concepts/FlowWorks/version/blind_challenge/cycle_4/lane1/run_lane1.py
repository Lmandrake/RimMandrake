#!/usr/bin/env python3
"""Run FlowWorks blind lane 1 (cycle 4) against the shipped kernels, or with one kernel swapped.
    python3 run_lane1.py [--kernel <path>]... [--src <FlowWorks/Source dir>] [--out <rows.jsonl>]
A --kernel file replaces the shipped kernel of the same basename. Stages BlindLane1.cs and the kernels under
<agent storage>/scratch/flowworks_blind_c4_lane1 (dotnet.exe cannot build from a WSL path; LANE1_STAGE overrides it),
builds with the per-user Windows dotnet, writes one JSON row per line and prints the verdict counts.
Exit 0 = no FAIL row; 1 = a FAIL row; 2 = build or run failure (no rows written)."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/FlowWorks/Source")
KERNELS = ["RM_SheetMath.cs", "RM_Volume.cs", "RM_StockMath.cs", "RM_FireMath.cs", "Machinery/RM_ConversionMath.cs", "Thirst/RM_ThirstMath.cs",
           "Drilling/RM_DrillSurveyMath.cs", "Sprinklers/RM_SprinklerKernel.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings>
<AssemblyName>BlindLane1</AssemblyName></PropertyGroup></Project>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    stage = os.environ.get("LANE1_STAGE")
    if not stage:
        root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
        stage = os.path.join(root, "rimmandrake", "scratch", "flowworks_blind_c4_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    swap = {os.path.basename(k): k for k in a.kernel}
    for k in KERNELS:
        b = os.path.basename(k)
        shutil.copy(swap.pop(b, os.path.join(a.src, k)), os.path.join(stage, b))
    if swap:
        sys.exit("unknown kernel(s): %s" % ", ".join(swap))
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    sset = open(os.path.join(a.src, "Sprinklers/RM_SprinklerSettings.cs")).read()
    m = re.search(r"RadiusChoices\s*=\s*\{([^}]*)\}", sset)
    choices = m.group(1) if m else ""
    open(os.path.join(stage, "Shadow.cs"), "w").write(
        "public static partial class RM_SprinklerSettings_Shadow { public static readonly float[] RadiusChoices = { %s }; }\n" % choices)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        print("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
        sys.exit(2)
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not rows:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
        sys.exit(2)
    with open(a.out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows:
        c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c, sort_keys=True), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL":
            print("FAIL", row["id"], row["detail"][:400])
    sys.exit(1 if any(row["verdict"] == "FAIL" for row in rows) else 0)


main()
