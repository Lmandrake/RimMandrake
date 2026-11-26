#!/usr/bin/env python3
"""Run blind lane 1 (cycle 6): python3 run_lane1.py [--kernel <file> ...] [--out rows.jsonl]. --kernel replaces the shipped file of the same
name (RM_BurnKernel.cs, RM_FireEcoKernel.cs, RM_FoamPathKernel.cs). Exit 0 = no FAIL row."""
import argparse, glob, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
KD = os.path.join(REPO, "src/RimMandrake/Pyrelands/Source/Kernel")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""
ap = argparse.ArgumentParser(); ap.add_argument("--kernel", nargs="*", default=[]); ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
a = ap.parse_args()
st = os.environ.get("PYRE_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c6_lane1"); os.makedirs(st, exist_ok=True)
for f in glob.glob(st + "/*.cs"): os.remove(f)
ks = {os.path.basename(p): p for p in (KD + "/RM_BurnKernel.cs", KD + "/RM_FireEcoKernel.cs", KD + "/RM_FoamPathKernel.cs")}
ks.update({os.path.basename(p): p for p in a.kernel})
for p in ks.values(): shutil.copy(p, st)
shutil.copy(HERE + "/BlindLane1.cs", st); open(st + "/BlindLane1.csproj", "w").write(CSPROJ)
dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
win = subprocess.run(["wslpath", "-w", st], capture_output=True, text=True, check=True).stdout.strip()
b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True)
if b.returncode: sys.exit("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-1000:])
r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True)
rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
if r.returncode not in (0, 1) or not rows: sys.exit("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
import lane1_files
rows += lane1_files.rows(REPO)
NK = [("populations_are_the_biomes_own", "the census is the live map's"), ("three_skies", "a look"), ("walk_season_on_the_pyre", "a live season"),
      ("furnacebeast_warms", "the beast's live room; the def row sparesRoofs is another mod's code")]
for bar, why in NK: rows.append(dict(id="nk_" + bar, bars=[bar], kind="not_kernel", verdict="UNSETTLED", cases=0, detail="changed inputs touch it but its logic is game-side: " + why + "; settled by its Stage 6 scene"))
open(a.out, "w").write("".join(json.dumps(x) + "\n" for x in rows))
c = {}
for x in rows: c[x["verdict"]] = c.get(x["verdict"], 0) + 1
print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
for x in rows:
    if x["verdict"] == "FAIL": print("FAIL", x["id"], x["detail"][:600])
sys.exit(1 if c.get("FAIL") else 0)
