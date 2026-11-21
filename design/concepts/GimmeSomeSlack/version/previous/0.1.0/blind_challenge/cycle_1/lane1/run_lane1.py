#!/usr/bin/env python3
"""Blind lane 1 for Gimme Some Slack 0.1.0: game-logic tests written from the bars alone.
    python3 run_lane1.py [--kernel <path> ...] [--src <GimmeSomeSlack dir>] [--out <rows.jsonl>] [--stage <dir>]
Stages BlindLane1.cs + the game-free kernels (Source/Core, the three Aerial kernels, _Shared/SlackGeometry) under
D:\\ClaudeWork\\rimmandrake\\scratch\\gss_blind_lane1 (dotnet.exe cannot build from a WSL path), builds and runs it with the
per-user Windows dotnet, adds the Python rows (settings defaults, hose scan), writes one JSON row per line and prints the
verdict counts. --kernel <path> replaces the shipped kernel of the same file name (planted faults reuse this).
Exit 0 = every decided row PASS; 1 = a FAIL; 2 = build or run failure."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
GSS = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
SHARED = os.path.join(REPO, "src/RimMandrake/_Shared/SlackGeometry")
AERIAL_KERNELS = ["AerialMath.cs", "ShockRule.cs", "TapWindow.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0162;CS0168;CS0219;CS0414;CS0649;CS0169;CS8632</NoWarn>
<Optimize>true</Optimize></PropertyGroup></Project>"""

def sources(src):
    files = sorted(glob.glob(os.path.join(src, "Source/Core/*.cs")))
    files += [os.path.join(src, "Source/Aerial", f) for f in AERIAL_KERNELS]
    files += sorted(glob.glob(os.path.join(SHARED, "*.cs")))
    return files

def settings_rows(src):
    """Settings as shipped, read from the source text (the Verse-bound files are not compiled)."""
    rows, out = [], {}
    aer = open(os.path.join(src, "Source/Aerial/AerialSettings.cs")).read()
    mod = open(os.path.join(src, "Source/GimmeSomeSlackMod.cs")).read()
    m = re.search(r"public static ShockReach shockReach = ShockReach\.(\w+);", aer)
    s = re.search(r'Scribe_Values\.Look\(ref shockReach, "shockReach", ShockReach\.(\w+)\);', aer)
    out["shockReach_field"] = m.group(1) if m else None
    out["shockReach_scribe"] = s.group(1) if s else None
    ok = out["shockReach_field"] == "All" and out["shockReach_scribe"] == "All"
    rows.append(dict(id="L1_SHOCK_DEFAULT_ALL", bars=["shock_reach_setting"], kind="fixed", verdict="PASS" if ok else "FAIL", cases=2,
                     detail="field default %s, Scribe default %s (bar: All on a fresh install)" % (out["shockReach_field"], out["shockReach_scribe"])))
    nums = {}
    for name, rx in [("slack", r"slack = list\.Slider\(slack, ([\d.]+)f, ([\d.]+)f\)"), ("loopBudget", r"loopBudget = list\.Slider\(loopBudget, ([\d.]+)f, ([\d.]+)f\)"),
                     ("cordsPerConnection", r"Slider\(cordsPerConnection, ([\d.]+)f, ([\d.]+)f\)"), ("tangleMin", r"Slider\(tangleMin, ([\d.]+)f, ([\d.]+)f\)"),
                     ("maxSparkingEnds", r"Slider\(maxSparkingEnds, ([\d.]+)f, ([\d.]+)f\)")]:
        g = re.search(rx, mod)
        nums[name] = [float(g.group(1)), float(g.group(2))] if g else None
    for name, rx in [("maxSpan", r"Slider\(maxSpan, ([\d.]+)f, ([\d.]+)f\)"), ("sag", r"sag = list\.Slider\(sag, ([\d.]+)f, ([\d.]+)f\)"),
                     ("theftGoodwillPerDay", r"Slider\(theftGoodwillPerDay, ([\d.]+)f, ([\d.]+)f\)"), ("theftSightRange", r"Slider\(theftSightRange, ([\d.]+)f, ([\d.]+)f\)"),
                     ("tapRate", r"Slider\(tapRate, ([\d.]+)f, ([\d.]+)f\)"), ("maxStrands", r"Slider\(maxStrands, ([\d.]+)f, ([\d.]+)f\)")]:
        g = re.search(rx, aer)
        nums[name] = [float(g.group(1)), float(g.group(2))] if g else None
    defaults = {}
    for name, rx in [("slack", r"public static float slack = ([\d.]+)f;"), ("loopBudget", r"public static float loopBudget = ([\d.]+)f;"),
                     ("cordsPerConnection", r"public static int cordsPerConnection = (\d+);"), ("tangleMin", r"public static int tangleMin = (\d+);"),
                     ("maxSparkingEnds", r"public static int maxSparkingEnds = (\d+);")]:
        g = re.search(rx, mod); defaults[name] = float(g.group(1)) if g else None
    for name, rx in [("maxSpan", r"public static float maxSpan = ([\d.]+)f;"), ("sag", r"public static float sag = ([\d.]+)f;"),
                     ("theftGoodwillPerDay", r"public static int theftGoodwillPerDay = (\d+);"), ("theftSightRange", r"public static float theftSightRange = ([\d.]+)f;"),
                     ("tapRate", r"public static float tapRate = ([\d.]+)f;"), ("maxStrands", r"public static int maxStrands = (\d+);")]:
        g = re.search(rx, aer); defaults[name] = float(g.group(1)) if g else None
    out["ranges"], out["defaults"] = nums, defaults
    bad = [k for k in nums if nums[k] is None or defaults.get(k) is None or not (nums[k][0] <= defaults[k] <= nums[k][1])]
    rows.append(dict(id="L1_SETTINGS_DEFAULT_IN_RANGE", bars=["settings_switch_cleanly", "mod_settings"], kind="fixed", verdict="FAIL" if bad else "PASS",
                     cases=len(nums), detail="every shipped default inside its slider range; out or unread: %s; ranges %s; defaults %s" % (bad, json.dumps(nums), json.dumps(defaults))))
    return rows, out

def hose_scan(src):
    """no_hose / no_hose_in_gss from the bar alone: no hose or reel ThingDef, texture or class under the mod. SelfTest/ and
    northstar/ are skipped in lane 1 (the blind rule closes them); a lane-2 rerun widens it."""
    hits, scanned = [], 0
    word = re.compile(r"hose|reel", re.I)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        if rel.split(os.sep)[0] in ("northstar", "SelfTest") or "SelfTest" in rel.split(os.sep): dirs[:] = []; continue
        for f in files:
            p = os.path.join(root, f); r = os.path.relpath(p, src); scanned += 1
            if word.search(f) and not f.endswith((".md", ".py", ".json")): hits.append("file:" + r)
            if f.endswith(".xml"):
                t = open(p, errors="replace").read()
                for m in re.finditer(r"<defName>([^<]*)</defName>|<texPath>([^<]*)</texPath>|<thingClass>([^<]*)</thingClass>", t):
                    v = next(x for x in m.groups() if x)
                    if word.search(v): hits.append("xml:%s:%s" % (r, v))
            if f.endswith(".cs"):
                t = open(p, errors="replace").read()
                for m in re.finditer(r"\b(class|struct)\s+(\w+)", t):
                    if word.search(m.group(2)): hits.append("cs-class:%s:%s" % (r, m.group(2)))
    return dict(id="L1_NO_HOSE_SCAN", bars=["no_hose", "no_hose_in_gss"], kind="fixed", verdict="FAIL" if hits else "PASS", cases=scanned,
                detail="files scanned %d (northstar/ and SelfTest/ skipped, blind); hose/reel defName, texPath, thingClass, file name or C# class hits: %s" % (scanned, hits[:20]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[]); ap.add_argument("--src", default=GSS)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    ap.add_argument("--stage", default="/mnt/d/ClaudeWork/rimmandrake/scratch/gss_blind_lane1")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    stage = a.stage
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")): os.remove(f)
    repl = {os.path.basename(k): k for k in a.kernel}
    for f in sources(a.src):
        b = os.path.basename(f); shutil.copy(repl.pop(b, f), os.path.join(stage, b))
    if repl: sys.exit("no shipped kernel named %s" % list(repl))
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    prow, sett = settings_rows(a.src)
    json.dump(sett, open(os.path.join(stage, "settings.json"), "w"))
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        print("BUILD FAILED\n" + "\n".join(l for l in b.stdout.splitlines() if "error" in l)[-3000:]); sys.exit(2)
    env = dict(os.environ, GSS_BLIND_SETTINGS=win + "\\settings.json", GSS_BLIND_ONLY=a.only)
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", ""), "GSS_BLIND_SETTINGS", "GSS_BLIND_ONLY"]))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, env=env, timeout=480)
    rows = prow + [hose_scan(a.src)] + [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows: c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] in ("FAIL", "UNSETTLED"): print(row["verdict"], row["id"], row["detail"][:300])
    if r.returncode not in (0, 1) or len(rows) <= len(prow) + 1:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:])); sys.exit(2)
    sys.exit(1 if c.get("FAIL") else 0)
main()
