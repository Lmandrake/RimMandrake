#!/usr/bin/env python3
"""Run Pyrelands blind lane 1 (cycle 4): the C# kernel tests (BlindLane1.cs) and the def/settings tests (BlindLane1.py),
plus one not_kernel row per bar whose logic is game-side.
    python3 run_lane1.py [--kernel <file.cs> ...] [--mod <mod dir>] [--out <rows.jsonl>]
--kernel replaces the shipped kernel of the same file name (a planted copy). The C# side is staged under
/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c4_lane1/ (dotnet.exe cannot build from a WSL path; override with
LANE1_STAGE) and built with the per-user Windows dotnet. Exit 0 = no FAIL row; 1 = a FAIL row; 2 = could not run."""
import argparse, glob, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/Pyrelands/Source")
KERNELS = ["Kernel/RM_FireEcoKernel.cs", "Kernel/RM_BurnKernel.cs", "Kernel/RM_FireHawkRewardsKernel.cs", "FurnaceWarmthMath.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings>
<InvariantGlobalization>false</InvariantGlobalization></PropertyGroup></Project>"""

# Bars with a kernel row above, and the game-side half each still owes.
KERNEL_PART = {
    "fresh_burn_compounds_with_black_rain": "the fertility read and its clock are kernel (rows compound_*, burn_clock_random); crop growth on three live pads through day 7 is game-side",
    "ash_fertile_when_watered": "the season rule is kernel (wet_roots_season_random); the watered strip's growth beside a channel is game-side (the sweep's water radius, the postfix)",
    "fire_walks_with_wind": "the carry rule is kernel (wind_*); that the game reads the map's wind and that fires obey it is game-side (Fire tick patch)",
    "burn_line_walks": "the carry rule is kernel (wind_*); the relight in open grass, the scorched trail that regreens and 'never out for long' are game-side",
    "furnacebeast_warms": "the warmth curve is kernel (furnace_warmth_random); room heat, sleep ignition, the hide bank and the giant body size are game-side",
    "inv_firehawk_hunt_rewards": "the once-a-game gate and the flat chance are kernel (hawk_*); the butcher hook (only a hawk drops the feather) and the letter's jump are game-side",
}
OFFLINE = {"ash_fertility_probe", "biome_text_says_engineered", "inv_firebreak_firefoam", "inv_lightning_breaker", "inv_settings_gate", "inv_art_and_text"}


def csharp(kernels):
    stage = os.environ.get("LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c4_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    over = {os.path.basename(k): k for k in kernels}
    for k in KERNELS:
        b = os.path.basename(k)
        shutil.copy(over.get(b, os.path.join(SRC, k)), os.path.join(stage, b))
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))
    if not dn:
        return None, "no per-user Windows dotnet"
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn[0], "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        return None, "BUILD FAILED " + (b.stdout[-1500:] + b.stderr[-800:])
    r = subprocess.run([dn[0], win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not rows:
        return None, "RUN FAILED rc %s %s" % (r.returncode, r.stderr[-1500:])
    return rows, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--mod", default=os.path.join(REPO, "src/RimMandrake/Pyrelands"))
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    rows, err = csharp(a.kernel)
    if rows is None:
        print("LANE1 COULD NOT RUN:", err)
        sys.exit(2)
    p = subprocess.run([sys.executable, os.path.join(HERE, "BlindLane1.py"), "--mod", a.mod], capture_output=True, text=True, timeout=300)
    prow = [json.loads(l) for l in p.stdout.splitlines() if l.startswith("{")]
    if p.returncode not in (0, 1) or not prow:
        print("LANE1 COULD NOT RUN: BlindLane1.py rc %s %s" % (p.returncode, p.stderr[-800:]))
        sys.exit(2)
    rows += prow
    covered = {b for r in rows for b in r["bars"]}
    ids = json.load(open(os.path.join(REPO, "design/concepts/Pyrelands/version/locked_bars.json")))["ids"]
    for bar in ids:
        if bar in KERNEL_PART:
            rows.append({"id": "game_side_" + bar, "bars": [bar], "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
                         "detail": "kernel half PASS/FAIL above; still undecided: " + KERNEL_PART[bar] + ". Settled at Stage 6 by its live scene."})
        elif bar not in covered and bar not in OFFLINE:
            rows.append({"id": "game_side_" + bar, "bars": [bar], "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
                         "detail": "no Verse-free kernel holds this bar's logic (its behaviour lives in Harmony patches, comps, job drivers, "
                                   "GenSteps or defs read by the game); settled at Stage 6 by its live scene, not by stretching a kernel."})
    missing = [b for b in OFFLINE if b not in {x for r in rows for x in r["bars"]}]
    for b in missing:
        rows.append({"id": "offline_bar_untested_" + b, "bars": [b], "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
                     "detail": "lane 1 has no row for this offline bar"})
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    c = {}
    for r in rows:
        c[r["verdict"]] = c.get(r["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for r in rows:
        if r["verdict"] == "FAIL":
            print("FAIL", r["id"], r["detail"][:400])
    sys.exit(1 if c.get("FAIL") else 0)


if __name__ == "__main__":
    main()
