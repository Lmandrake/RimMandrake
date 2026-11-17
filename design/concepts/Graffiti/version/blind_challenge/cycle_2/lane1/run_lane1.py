#!/usr/bin/env python3
"""Run the cycle-2 blind lane 1 against a kernel file (default: the shipped RM_GraffitiKernel.cs).
    python3 run_lane1.py [--kernel <path>] [--src <Source dir>] [--out <rows.jsonl>]
Stages BlindLane1.cs, the kernel and the two enum files it compiles with under
/mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c2_lane1 (or $LANE1_STAGE; dotnet.exe cannot build from a WSL path), builds and runs it
with the per-user Windows dotnet, writes one JSON row per line, prints the verdict counts. The shipped settings (defaults and
slider ranges) are read from <src>/RM_GraffitiMod.cs, the temperament rows from <src>/../Defs/TemperamentDefs_Graffiti.xml.
Exit 0 = no FAIL row."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/Graffiti/Source")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""


def settings(src, kernel_text):
    mod = open(os.path.join(src, "RM_GraffitiMod.cs")).read()
    def val(tok):
        tok = tok.strip().rstrip("f")
        m = re.match(r"RM_GraffitiKernel\.(\w+)", tok)
        if m:
            k = re.search(r"\b" + m.group(1) + r"\s*=\s*([-\d.]+)f?", kernel_text)
            return k.group(1) if k else "nan"
        return tok
    out = {}
    m = re.search(r"public static int paintIntervalTicks = ([^;]+);", mod); out["GR_PACE_DEFAULT"] = val(m.group(1)) if m else "nan"
    m = re.search(r"Slider\(paintIntervalTicks, ([^,]+), ([^)]+)\)", mod); out["GR_PACE_MIN"], out["GR_PACE_MAX"] = (val(m.group(1)), val(m.group(2))) if m else ("nan", "nan")
    m = re.search(r"public static int raiderPressureMode = ([^;]+);", mod); out["GR_MODE_DEFAULT"] = val(m.group(1)) if m else "-9"
    m = re.search(r"public static float raiderPressurePush = ([^;]+);", mod); out["GR_PUSH_DEFAULT"] = val(m.group(1)) if m else "nan"
    m = re.search(r"Slider\(raiderPressurePush, ([^,]+), ([^)]+)\)", mod); out["GR_PUSH_MIN"], out["GR_PUSH_MAX"] = (val(m.group(1)), val(m.group(2))) if m else ("nan", "nan")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=os.path.join(SRC, "Kernel/RM_GraffitiKernel.cs"))
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    stage = os.environ.get("LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c2_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")) + glob.glob(os.path.join(stage, "*.xml")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    shutil.copy(a.kernel, os.path.join(stage, "RM_GraffitiKernel.cs"))
    for f in ("GraffitiForm.cs", "GraffitiCategory.cs"):
        shutil.copy(os.path.join(a.src, f), stage)
    shutil.copy(os.path.join(a.src, "..", "Defs", "TemperamentDefs_Graffiti.xml"), stage)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        sys.exit("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
    env = dict(os.environ, **settings(a.src, open(a.kernel).read()))
    keys = [k for k in env if k.startswith("GR_")]
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", "")] + keys))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll", win + "\\TemperamentDefs_Graffiti.xml"],
                       capture_output=True, text=True, env=env, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
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
    if r.returncode not in (0, 1) or not rows:
        sys.exit("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
    sys.exit(r.returncode)


main()
