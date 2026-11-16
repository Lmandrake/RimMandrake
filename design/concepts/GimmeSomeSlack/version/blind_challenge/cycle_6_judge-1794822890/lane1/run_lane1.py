#!/usr/bin/env python3
"""Run blind lane 1 (GimmeSomeSlack 0.1.0, cycle 6) against the kernels and the mod tree.
    python3 run_lane1.py [--kernel <AerialMath.cs>] [--shockrule <ShockRule.cs>] [--mod-root <mod dir>] [--dll <dll>] [--out <rows.jsonl>]
Stages BlindLane1.cs + the two Verse-free kernels (and a stub of Core.WallMount's two shipped face numbers, which AerialMath reaches) under <agent storage>/scratch/gimmesomeslack_blind_c6_lane1 (dotnet.exe
cannot build from a WSL path; LANE1_STAGE overrides), builds and runs them with the per-user Windows dotnet, adds the rows of
blind_no_hose.py (with its planted-hose self-check), writes one JSON row per line, prints the counts. Exit 0 = no FAIL row.
The shipped settings (defaults and slider ranges) are read from AerialSettings.cs and handed over as env vars."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""


def settings_env(mod):
    s = open(os.path.join(mod, "Source/Aerial/AerialSettings.cs"), encoding="utf-8").read()
    def val(name, typ=r"[\d.]+"):
        m = re.search(r"public static \w+ " + name + r"\s*=\s*(" + typ + r")f?;", s); return m.group(1) if m else None
    def slider(name):
        m = re.search(name + r"\s*=.*?Slider\(" + name + r",\s*([\d.]+)f,\s*([\d.]+)f\)", s); return (m.group(1), m.group(2)) if m else (None, None)
    env = {}
    for k, n in (("GSS_MAXSPAN", "maxSpan"), ("GSS_SAG", "sag"), ("GSS_TAPRATE", "tapRate"), ("GSS_SIGHT", "theftSightRange"),
                 ("GSS_PERDAY", "theftGoodwillPerDay"), ("GSS_STRANDS", "maxStrands")):
        v = val(n)
        if v: env[k] = v
        lo, hi = slider(n)
        if lo: env[k + "_LO"], env[k + "_HI"] = lo, hi
    m = re.search(r"public static ShockReach shockReach\s*=\s*ShockReach\.(\w+);", s)
    if m: env["GSS_SHOCK_DEFAULT"] = m.group(1)
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=os.path.join(MOD, "Source/Aerial/AerialMath.cs"))
    ap.add_argument("--shockrule", default=os.path.join(MOD, "Source/Aerial/ShockRule.cs"))
    ap.add_argument("--mod-root", default=MOD)
    ap.add_argument("--dll", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    dll = a.dll or os.path.join(a.mod_root, "Assemblies/RimMandrakeGimmeSomeSlack.dll")
    stage = os.environ.get("LANE1_STAGE")
    if not stage:
        root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
        stage = os.path.join(root, "scratch", "gimmesomeslack_blind_c6_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")): os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    shutil.copy(a.kernel, os.path.join(stage, "AerialMath.cs")); shutil.copy(a.shockrule, os.path.join(stage, "ShockRule.cs"))
    # AerialMath's one outside reference (BracketInset reads Core.WallMount's two face numbers): a stub carrying the shipped values
    wm = open(os.path.join(a.mod_root, "Source/Core/WallMount.cs"), encoding="utf-8").read()
    consts = "".join("public const double %s = %s; " % (n, re.search(r"const double " + n + r"\s*=\s*([\d.]+)", wm).group(1)) for n in ("SouthBand", "SideBevel"))
    open(os.path.join(stage, "WallMountStub.cs"), "w").write("namespace RimMandrake.GimmeSomeSlack.Core { public static class WallMount { " + consts + "} }\n")
    dllstage = os.path.join(stage, "gss_under_test.dll"); shutil.copy(dll, dllstage)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    rows = []
    if b.returncode:
        rows.append(dict(id="L1_KERNEL_BUILD", bars=[], kind="fixed", verdict="FAIL", cases=1, detail="kernel + tests did not compile: " + (b.stdout[-600:] + b.stderr[-300:]).replace("\n", " ")))
    else:
        env = dict(os.environ, **settings_env(a.mod_root), GSS_DLL=win + "\\gss_under_test.dll")
        env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", "")] + [k for k in env if k.startswith("GSS_")]))
        r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, env=env, timeout=400)
        rows += [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        if r.returncode not in (0, 1) or not rows:
            rows.append(dict(id="L1_KERNEL_RUN", bars=[], kind="fixed", verdict="FAIL", cases=1, detail="run failed rc %s: %s" % (r.returncode, r.stderr[-600:])))
    nh = subprocess.run([sys.executable, os.path.join(HERE, "blind_no_hose.py"), "--mod-root", a.mod_root, "--selfcheck"], capture_output=True, text=True, timeout=400)
    rows += [json.loads(l) for l in nh.stdout.splitlines() if l.startswith("{")]
    if not any(r["id"] == "NH_TEXTURES" for r in rows):
        rows.append(dict(id="NH_SCAN_RUN", bars=["no_hose", "no_hose_in_gss"], kind="fixed", verdict="FAIL", cases=1, detail="scanner failed: " + nh.stderr[-600:]))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows: c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL": print("FAIL", row["id"], row["detail"][:400])
    sys.exit(1 if c.get("FAIL") else 0)


main()
