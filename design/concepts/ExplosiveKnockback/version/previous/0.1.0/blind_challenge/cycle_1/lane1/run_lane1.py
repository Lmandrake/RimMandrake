#!/usr/bin/env python3
"""Run blind lane 1 against a kernel file (default: the shipped RM_KnockbackMath.cs).
    python3 run_lane1.py [--kernel <path>] [--out <rows.jsonl>]
Stages BlindLane1.cs + the kernel under <agent storage>/scratch/ek_blind_lane1 (dotnet.exe cannot build from a WSL
path), builds and runs it with the per-user Windows dotnet, writes one JSON row per line, prints the verdict counts.
Exit 0 = every decided row PASS."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
KERNEL = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackMath.cs")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--kernel", default=KERNEL); ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
    stage = os.path.join(root, "scratch", "ek_blind_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")): os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage); shutil.copy(a.kernel, os.path.join(stage, "RM_KnockbackMath.cs"))
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True)
    if b.returncode: sys.exit("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
    # numbers the kernel does not hold, read from the shipped game-side files and handed over (WSLENV carries them to dotnet.exe)
    src = os.environ.get("EK_SRC") or os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback/Source")
    flyer = open(os.path.join(src, "RM_ThingFlyer_Knockback.cs")).read(); mod = open(os.path.join(src, "RM_KnockbackMod.cs")).read()
    mb = re.search(r"public const int MaxBounces = (\d+);", flyer); gw = re.search(r"public const float GoodsThrowWild = ([\d.]+)f;", mod)
    env = dict(os.environ, EK_MAX_BOUNCES=mb.group(1) if mb else "-1", EK_GOODS_WILD=gw.group(1) if gw else "0")
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", ""), "EK_MAX_BOUNCES", "EK_GOODS_WILD"]))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, env=env)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows: c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL": print("FAIL", row["id"], row["detail"][:400])
    if r.returncode not in (0, 1) or not rows: sys.exit("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
    sys.exit(r.returncode)
main()
