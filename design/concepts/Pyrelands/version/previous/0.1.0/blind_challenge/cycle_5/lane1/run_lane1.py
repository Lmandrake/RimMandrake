#!/usr/bin/env python3
"""Pyrelands blind cycle 5, lane 1: one command.
    python3 run_lane1.py [--src <Pyrelands mod dir>] [--out <rows.jsonl>] [--only cs|py]
Stages BlindLane1.cs with the six game-free kernels AS SHIPPED (copied from --src, default the repo's mod) under
$PYR_LANE1_STAGE or D:\\ClaudeWork\\rimmandrake\\scratch\\pyrelands_blind_c5_lane1 (dotnet.exe cannot build from a WSL
path), builds and runs it with the per-user Windows dotnet, then runs lane1_defs.py (the defs/text/settings half) on the
same --src. Writes one JSON row per line and prints the verdict counts. Exit 0 = no FAIL row; 1 = a FAIL row; 2 = could
not run (build or run failure: no rows are written, so nothing can pass for an answer)."""
import argparse, glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
KERNELS = ["Kernel/RM_BurnKernel.cs", "Kernel/RM_FireEcoKernel.cs", "Kernel/RM_FireHawkKernel.cs",
           "Kernel/RM_FireHawkRewardsKernel.cs", "Kernel/RM_FurnaceKernel.cs", "FurnaceWarmthMath.cs"]
TUNING = ["FurnaceAuraRadius", "FurnaceWarmthMaxC", "FurnaceSleepIgnitionGraceTicks", "StandingBurnQuietTicks",
          "StandingBurnRetryTicks", "BurnWatchIntervalTicks", "WetRootsCoolingC"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""


def run_cs(src):
    stage = os.environ.get("PYR_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c5_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    for k in KERNELS:
        shutil.copy(os.path.join(src, "Source", k), os.path.join(stage, os.path.basename(k)))
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        return None, "BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-1500:]
    tuning = open(os.path.join(src, "Source", "PyrelandsTuning.cs")).read()
    env = dict(os.environ)
    names = []
    for t in TUNING:
        m = re.search(r"public const (?:float|int|double) " + t + r"\s*=\s*([-\d.]+)f?;", tuning)
        if m:
            env["PYR_" + t] = m.group(1)
            names.append("PYR_" + t)
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", "")] + names))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, env=env, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not rows:
        return None, "RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:])
    return rows, None


def run_py(src):
    r = subprocess.run([sys.executable, os.path.join(HERE, "lane1_defs.py"), "--src", src], capture_output=True, text=True, timeout=300)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not rows:
        return None, "PY RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:])
    return rows, None


def bar_ids():
    """The 44 bars of 0.1.0 from the locked files: record.json inventory rows + tree.json leaves, less the coverage leaf."""
    concept = os.path.join(REPO, "design/concepts/Pyrelands")
    rec = json.load(open(os.path.join(concept, "record.json")))
    tree = json.load(open(os.path.join(concept, "tree.json")))
    inv = [r["id"] for r in rec["inventory"] if str(r.get("id", "")).startswith("inv_")]
    leaves = [l["id"] for l in tree["leaves"] if l["id"] != "firehawk_hunt_rewards"]
    return inv + leaves


def not_kernel(rows):
    covered = {b for r in rows for b in r["bars"]}
    rest = [b for b in bar_ids() if b not in covered]
    return {"id": "game_side_bars", "bars": rest, "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
            "detail": "%d of %d bars have no game-free kernel that decides them (their logic is in game-side callers, defs read "
                      "by the engine, or captures): each settles by its Stage 6 scene in the live game" % (len(rest), len(bar_ids()))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(REPO, "src/RimMandrake/Pyrelands"))
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    ap.add_argument("--only", choices=["cs", "py"])
    a = ap.parse_args()
    rows = []
    for name, fn in (("cs", run_cs), ("py", run_py)):
        if a.only and a.only != name:
            continue
        got, err = fn(a.src)
        if err:
            print(err)
            sys.exit(2)
        rows += got
    if not a.only:
        rows.append(not_kernel(rows))
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
    sys.exit(1 if c.get("FAIL") else 0)


main()
