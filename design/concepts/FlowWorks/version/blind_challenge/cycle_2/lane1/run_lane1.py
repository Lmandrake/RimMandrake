#!/usr/bin/env python3
"""Run FlowWorks blind lane 1 (cycle 2) against the shipped kernels, or with any one kernel file swapped.
    python3 run_lane1.py [--kernel <path>]... [--out <rows.jsonl>]
--kernel replaces the shipped file of the same basename (RM_SheetMath.cs, RM_ConversionMath.cs, RM_DrillSurveyMath.cs,
RM_SprinklerKernel.cs, RM_ThirstMath.cs, RM_Volume.cs). Stages under <agent storage>/rimmandrake/scratch/flowworks_blind_c2_lane1 (or
$LANE1_STAGE), because dotnet.exe cannot build from a WSL path; builds with the per-user Windows dotnet; one JSON row a line.
Exit 0 = every decided row PASS; 1 = a FAIL row; 2 = build or run failure."""
import argparse, glob, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/FlowWorks/Source")
KERNELS = ["RM_SheetMath.cs", "RM_Volume.cs", "Machinery/RM_ConversionMath.cs", "Drilling/RM_DrillSurveyMath.cs",
           "Sprinklers/RM_SprinklerKernel.cs", "Thirst/RM_ThirstMath.cs", "RM_FireMath.cs", "RM_StockMath.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl")); a = ap.parse_args()
    stage = os.environ.get("LANE1_STAGE")
    if not stage:
        root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
        stage = os.path.join(root, "rimmandrake", "scratch", "flowworks_blind_c2_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")): os.remove(f)
    swap = {os.path.basename(k): k for k in a.kernel}
    for k in KERNELS:
        b = os.path.basename(k); shutil.copy(swap.pop(b, os.path.join(SRC, k)), os.path.join(stage, b))
    if swap: sys.exit("unknown kernel(s): %s" % list(swap))
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        print("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:]); sys.exit(2)
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows: c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL": print("FAIL", row["id"], row["detail"][:400])
    if r.returncode not in (0, 1) or not rows:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:])); sys.exit(2)
    sys.exit(r.returncode)
main()
