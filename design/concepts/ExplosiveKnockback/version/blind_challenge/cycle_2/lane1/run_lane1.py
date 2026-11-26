#!/usr/bin/env python3
"""Run blind lane 1 (ExplosiveKnockback 0.2.0, cycle 2) against the shipped kernel, or a substitute kernel file.
    python3 run_lane1.py [--kernel <path>] [--src <ExplosiveKnockback/Source>] [--out <rows.jsonl>]
--kernel replaces RM_KnockbackMath.cs. The shipped settings (defaults, read from RM_KnockbackMod.cs with a regex, never
hand-copied) go to the test in KB_* variables (WSLENV carries them to dotnet.exe). Stages BlindLane1.cs + the kernel under
/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c2_lane1 (dotnet.exe cannot build from a WSL path), builds
and runs it with the per-user Windows dotnet, then appends the Python rows of lane1_proof_scenes.py (bar inv_proof_scenes)
and the not_kernel rows, writes one JSON row per line, prints the verdict counts.
Exit 0 = no FAIL row; 1 = a row FAILed; 2 = build or run failure."""
import argparse, glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback/Source")
STAGE = os.environ.get("KB_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c2_lane1")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0162;CS0168;CS0219</NoWarn></PropertyGroup></Project>"""
NUM = r"(-?[\d.]+)f?"
SETTINGS = [  # (env var, field in RimMandrakeExplosiveKnockbackSettings)
    ("KB_STRENGTH", "strength"), ("KB_MAX", "maxThrowCells"), ("KB_CREATURE_LIMIT", "creatureMassLimit"),
    ("KB_LIGHT_LIMIT", "lightMassLimit"), ("KB_IMPACT_ON", "impactDamageEnabled"), ("KB_IMPACT_PER_CELL", "impactDamagePerCell"),
    ("KB_SANDBAGS_STOP", "sandbagsStopThrow"), ("KB_INTO_PITS", "throwIntoPits"), ("KB_REBOUND_KEEP", "goodsReboundKeepPercent"),
    ("KB_UNPATCHED_PCT", "unpatchedHarmfulPercent"), ("KB_RECOVERY", "recoveryWindowTicks"), ("KB_SHIELD_DEBIT", "shieldDebitPerForce"),
    ("KB_HEAVY_MIN", "heavyGoodsMinMass"), ("KB_HEAVY_DMIN", "heavyGoodsDamageMin"), ("KB_HEAVY_DMAX", "heavyGoodsDamageMax"),
    ("KB_HEAVY_STAGGER", "heavyGoodsStaggerTicks"), ("KB_CONTAINER_LIMIT", "closedContainerMassLimit"),
]


def settings_env(src):
    text = open(os.path.join(src, "RM_KnockbackMod.cs"), encoding="utf-8").read()
    env, missing = {}, []
    for var, field in SETTINGS:
        m = re.search(r"public static (?:bool|int|float) %s = (true|false|%s);" % (field, NUM), text)
        if not m:
            missing.append(field)
            continue
        v = m.group(1)
        env[var] = {"true": "1", "false": "0"}.get(v, v.rstrip("f"))
    m = re.search(r"public const float GoodsThrowWild = %s;" % NUM, text)
    if m:
        env["KB_WILD"] = m.group(1)
    else:
        missing.append("GoodsThrowWild")
    return env, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel")
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    os.makedirs(STAGE, exist_ok=True)
    for f in glob.glob(os.path.join(STAGE, "*.cs")):
        os.remove(f)
    shutil.copy(a.kernel or os.path.join(a.src, "RM_KnockbackMath.cs"), os.path.join(STAGE, "RM_KnockbackMath.cs"))
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), STAGE)
    open(os.path.join(STAGE, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=400)  # hang guard; a build takes ~20 s
    if b.returncode:
        print("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
        sys.exit(2)
    senv, missing = settings_env(a.src)
    env = dict(os.environ, **senv)
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", "")] + list(senv)))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=400)  # hang guard; the run takes ~10 s
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if missing:
        rows.append({"id": "L1_SETTINGS_READ", "bars": ["inv_settings"], "kind": "info", "verdict": "UNSETTLED", "cases": 0,
                     "detail": "shipped defaults not read from RM_KnockbackMod.cs: " + ", ".join(missing) + " (the C# test used its own fallback)"})
    if not a.kernel:
        p = subprocess.run([sys.executable, os.path.join(HERE, "lane1_proof_scenes.py")], capture_output=True, text=True, timeout=540)
        rows += [json.loads(l) for l in p.stdout.splitlines() if l.startswith("{")]
        if p.returncode not in (0, 1):
            print("PROOF ROWS FAILED rc %s\n%s" % (p.returncode, p.stderr[-2000:]))
            sys.exit(2)
        rows += json.load(open(os.path.join(HERE, "not_kernel_rows.json")))
    with open(a.out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows:
        c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL":
            print("FAIL", row["id"], row["detail"][:600])
    if r.returncode not in (0, 1) or not rows:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
        sys.exit(2)
    sys.exit(1 if c.get("FAIL") else 0)


main()
