#!/usr/bin/env python3
"""Blind challenge cycle 2, lane 1: build BlindLane1.cs against the shipped kernel with the per-user Windows dotnet and
write lane1_rows.jsonl. Staged on D: because dotnet.exe cannot build from a WSL path. Prints RESULT: GREEN|RED."""
import json, os, pathlib, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[6]
KERNEL = REPO / "src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackMath.cs"
STAGE = pathlib.Path(os.environ.get("EK_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/ek_blind_c2_lane1"))
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><Nullable>disable</Nullable>
  <EnableDefaultCompileItems>false</EnableDefaultCompileItems><NoWarn>CS0168;CS0219;CS8981</NoWarn></PropertyGroup>
  <ItemGroup><Compile Include="RM_KnockbackMath.cs" /><Compile Include="BlindLane1.cs" /></ItemGroup>
</Project>
"""

def dotnet():
    for p in sorted(pathlib.Path("/mnt/c/Users").glob("*/.dotnet/dotnet.exe")):
        return str(p)
    sys.exit("no per-user dotnet.exe under /mnt/c/Users/*/.dotnet")

def winpath(p):
    return subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True, check=True).stdout.strip()

def main():
    kernel = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else KERNEL
    STAGE.mkdir(parents=True, exist_ok=True)
    shutil.copy(kernel, STAGE / "RM_KnockbackMath.cs")
    shutil.copy(HERE / "BlindLane1.cs", STAGE / "BlindLane1.cs")
    (STAGE / "BlindLane1.csproj").write_text(CSPROJ)
    proj = winpath(STAGE / "BlindLane1.csproj")
    b = subprocess.run([dotnet(), "build", proj, "-c", "Release", "-nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode != 0:
        print(b.stdout[-3000:], b.stderr[-2000:])
        print("RESULT: RED (build)")
        return 2
    r = subprocess.run([dotnet(), winpath(STAGE / "bin/Release/net8.0/BlindLane1.dll")], capture_output=True, text=True, timeout=300)
    rows = [json.loads(l) for l in r.stdout.replace("\r", "").splitlines() if l.strip().startswith("{")]
    out = pathlib.Path(os.environ.get("EK_LANE1_OUT", HERE / "lane1_rows.jsonl"))
    out.write_text("".join(json.dumps(x) + "\n" for x in rows))
    tally = {}
    for x in rows:
        tally[x["verdict"]] = tally.get(x["verdict"], 0) + 1
    for x in rows:
        if x["verdict"] == "FAIL":
            print("FAIL", x["id"], x["detail"][:300])
    print("rows", len(rows), tally, "->", out)
    print("RESULT:", "RED" if tally.get("FAIL") or r.returncode else "GREEN")
    return 1 if tally.get("FAIL") or r.returncode else 0

if __name__ == "__main__":
    sys.exit(main())
