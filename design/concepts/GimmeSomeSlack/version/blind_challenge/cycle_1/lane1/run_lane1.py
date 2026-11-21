#!/usr/bin/env python3
"""Run blind lane 1 (GimmeSomeSlack 0.1.1, cycle 1).
    python3 run_lane1.py [--kernel <AerialMath.cs>] [--mod-root <mod dir>] [--out <rows.jsonl>]
Part 1: blind_no_hose.py over the mod root (the offline bars no_hose, no_hose_in_gss).
Part 2: BlindLane1.cs + the kernel staged under <agent storage>/scratch/gimmesomeslack_blind_c1_lane1 (dotnet.exe cannot
build from a WSL path; $GSS_LANE1_STAGE overrides), built and run with the per-user Windows dotnet.
Part 3: one not_kernel row per bar whose logic is game-side (not_kernel.json beside this file).
Writes one JSON row per line, prints the verdict counts. Exit 0 = no FAIL row, 1 = a FAIL row, 2 = could not run."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
KERNEL = os.path.join(MOD, "Source/Aerial/AerialMath.cs")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=KERNEL); ap.add_argument("--mod-root", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    rows = []
    r = subprocess.run([sys.executable, os.path.join(HERE, "blind_no_hose.py"), "--mod-root", a.mod_root], capture_output=True, text=True, timeout=300)
    part1 = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not part1:
        print("RUN FAILED: blind_no_hose.py rc %s %s" % (r.returncode, r.stderr[-1500:])); sys.exit(2)
    rows += part1
    r = subprocess.run([sys.executable, os.path.join(HERE, "blind_settings.py"), "--mod-root", a.mod_root], capture_output=True, text=True, timeout=120)
    part1b = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not part1b:
        print("RUN FAILED: blind_settings.py rc %s %s" % (r.returncode, r.stderr[-1500:])); sys.exit(2)
    rows += part1b
    stage = os.environ.get("GSS_LANE1_STAGE")
    if not stage:
        root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
        stage = os.path.join(root, "scratch", "gimmesomeslack_blind_c1_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")): os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage); shutil.copy(a.kernel, os.path.join(stage, "AerialMath.cs"))
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    # AerialMath reads two constants of Core.WallMount (which pulls Shared.Slack): stub them with the shipped values
    wm = open(os.path.join(a.mod_root, "Source/Core/WallMount.cs")).read()
    consts = {n: re.search(r"public const double %s = ([\d.]+);" % n, wm).group(1) for n in ("SouthBand", "SideBevel")}
    open(os.path.join(stage, "WallMountStub.cs"), "w").write("namespace RimMandrake.GimmeSomeSlack.Core { public static class WallMount { "
        + " ".join("public const double %s = %s;" % kv for kv in consts.items()) + " } }\n")
    dns = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))
    if not dns: print("RUN FAILED: no per-user dotnet.exe"); sys.exit(2)
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dns[0], "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        # a kernel that does not compile is a red for every kernel row (a planted fault may do this)
        rows.append(dict(id="kernel_compiles", bars=["overhead_spans"], kind="fixed", verdict="FAIL", cases=1, detail="BUILD FAILED " + (b.stdout[-600:] + b.stderr[-300:]).replace("\n", " ")))
    else:
        k = subprocess.run([dns[0], win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
        part2 = [json.loads(l) for l in k.stdout.splitlines() if l.startswith("{")]
        if k.returncode not in (0, 1) or not part2:
            rows.append(dict(id="kernel_run", bars=["overhead_spans"], kind="fixed", verdict="FAIL", cases=1, detail="RUN FAILED rc %s %s" % (k.returncode, k.stderr[-600:])))
        rows += part2
    nk = os.path.join(HERE, "not_kernel.json")
    if os.path.exists(nk):
        for bar, why in json.load(open(nk)).items():
            rows.append(dict(id="not_kernel_" + bar, bars=[bar], kind="not_kernel", verdict="UNSETTLED", cases=0, detail=why))
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows: c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL": print("FAIL", row["id"], row["detail"][:400])
    sys.exit(1 if c.get("FAIL") else 0)


main()
