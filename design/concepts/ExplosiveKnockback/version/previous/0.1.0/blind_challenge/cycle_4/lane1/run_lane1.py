#!/usr/bin/env python3
"""Run blind lane 1 (ExplosiveKnockback 0.1.0, cycle 4) against the shipped kernel, or a substitute kernel file.
    python3 run_lane1.py [--kernel <path> ...] [--src <ExplosiveKnockback dir>] [--out <rows.jsonl>]
--kernel replaces the shipped file of the same name: RM_KnockbackMath.cs (the C# kernel) or proof_build_gate.py.
The shipped settings (field initialisers in RM_KnockbackMod.cs, read by regex, never hand-copied) go to the C# test in
EK_* variables (WSLENV carries them to dotnet.exe). Stages BlindLane1.cs + the kernel under
<agent storage>/scratch/explosiveknockback_blind_c4_lane1 (dotnet.exe cannot build from a WSL path), builds with the
per-user Windows dotnet, runs, then runs blind_lane1_proof.py; writes one JSON row per line and prints verdict counts.
Exit 0 = no FAIL row; 1 = a row FAILed; 2 = build or run failure."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0162;CS0168;CS0219;CS8321</NoWarn></PropertyGroup></Project>"""
SETTINGS = [  # (env var, field name, type) read from `public static <type> <name> = <v>;` (or const)
    ("EK_STRENGTH", "strength"), ("EK_MAXCELLS", "maxThrowCells"), ("EK_OWNCAPSCALE", "ownCapScale"),
    ("EK_CREATURE", "creatureMassLimit"), ("EK_LIGHT", "lightMassLimit"), ("EK_IMPACT_ON", "impactDamageEnabled"),
    ("EK_IMPACT_PER", "impactDamagePerCell"), ("EK_SANDBAGS", "sandbagsStopThrow"), ("EK_PITS", "throwIntoPits"),
    ("EK_POWER_ON", "blastPowerFromDamage"), ("EK_REFPCT", "blastPowerRefPercent"), ("EK_CONTAINER", "closedContainerMassLimit"),
    ("EK_HEAVY_MIN", "heavyGoodsMinMass"), ("EK_HEAVY_DMIN", "heavyGoodsDamageMin"), ("EK_HEAVY_DMAX", "heavyGoodsDamageMax"),
    ("EK_STAGGER", "heavyGoodsStaggerTicks"), ("EK_KEEP", "goodsReboundKeepPercent"), ("EK_GAS_GOODS", "gasBurstGoodsCells"),
    ("EK_RECOVERY", "recoveryWindowTicks"), ("EK_WILD", "GoodsThrowWild"),
]


def settings_env(src):
    t = open(os.path.join(src, "Source", "RM_KnockbackMod.cs"), encoding="utf-8").read()
    env = {}
    for var, name in SETTINGS:
        m = re.search(r"public (?:static|const) (?:bool|float|int) %s = ([^;]+);" % name, t)
        if not m:
            continue  # unread: the C# row reports it
        v = m.group(1).strip()
        env[var] = {"true": "1", "false": "0"}.get(v, v.rstrip("fF"))
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    subs = {os.path.basename(k): os.path.abspath(k) for k in a.kernel}
    bad = set(subs) - {"RM_KnockbackMath.cs", "proof_build_gate.py"}
    if bad:
        sys.exit("no shipped kernel named " + ", ".join(sorted(bad)))
    root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
    stage = os.path.join(root, "scratch", os.environ.get("EK_LANE1_STAGE", "explosiveknockback_blind_c4_lane1"))
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    shutil.copy(subs.get("RM_KnockbackMath.cs", os.path.join(a.src, "Source", "RM_KnockbackMath.cs")), os.path.join(stage, "RM_KnockbackMath.cs"))
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
    p = subprocess.run([sys.executable, os.path.join(HERE, "blind_lane1_proof.py"), "--src", a.src, "--gate", subs.get("proof_build_gate.py", os.path.join(a.src, "proof_build_gate.py"))],
                       capture_output=True, text=True, timeout=120)
    prow = [json.loads(l) for l in p.stdout.splitlines() if l.startswith("{")]
    if p.returncode or not prow:
        print("PROOF PART FAILED rc %s\n%s" % (p.returncode, p.stderr[-2000:]))
    rows += prow
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
    if r.returncode not in (0, 1) or not rows or p.returncode or not prow:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
        sys.exit(2)
    sys.exit(1 if c.get("FAIL") else 0)


main()
