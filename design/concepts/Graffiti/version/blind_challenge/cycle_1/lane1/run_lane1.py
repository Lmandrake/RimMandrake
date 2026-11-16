#!/usr/bin/env python3
"""Run blind lane 1 (Graffiti 0.1.0, cycle 1) against the shipped kernel, or a substitute kernel file.
    python3 run_lane1.py [--kernel <path>] [--src <Graffiti dir>] [--out <rows.jsonl>]
--kernel replaces RM_GraffitiKernel.cs. The shipped settings (field initialisers in RM_GraffitiMod.cs, read by regex) go to the C#
test in GR_* variables; the per-type values (form, poolWeight, minArtistic, Beauty, meme gate per ThingDef; the temperament rows) are
parsed from Defs/ into two TSVs. Stages BlindLane1.cs, the kernel and the two enum files under
<agent storage>/scratch/$GR_LANE1_STAGE (default graffiti_blind_c1_lane1; dotnet.exe cannot build from a WSL path), builds with the
per-user Windows dotnet and runs. Exit 0 = no FAIL row; 1 = a row FAILed; 2 = build or run failure."""
import argparse, glob, json, os, re, shutil, subprocess, sys
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/Graffiti")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0162;CS0168;CS0219;CS8321</NoWarn></PropertyGroup></Project>"""
SETTINGS = [("GR_PAINTING", "paintingEnabled"), ("GR_PACE", "paintIntervalTicks"), ("GR_VIEWER", "viewerReactionEnabled"),
            ("GR_BREACH", "breachBiasEnabled"), ("GR_EXIT", "raidExitTaggingEnabled"), ("GR_PROTECT", "autoCleanProtectionEnabled"),
            ("GR_SOCIAL", "socialEnabled"), ("GR_MESSAGES", "socialMessagesEnabled")]


def settings_env(src):
    t = open(os.path.join(src, "Source", "RM_GraffitiMod.cs"), encoding="utf-8").read()
    env = {}
    for var, name in SETTINGS:
        m = re.search(r"public static (?:bool|float|int) %s = ([^;]+);" % name, t)
        if m:
            v = m.group(1).strip()
            env[var] = {"true": "1", "false": "0"}.get(v, v.rstrip("fF"))
    names = re.findall(r"public static (?:bool|float|int) (\w+) = [^;]+;", t)
    env["GR_SETTING_COUNT"] = str(len(names))
    env["GR_SETTING_NAMES"] = " ".join(names)
    return env


def defs_tsv(src, path):
    rows = []
    for f in sorted(glob.glob(os.path.join(src, "Defs", "ThingDefs_Graffiti*.xml"))):
        for td in ET.parse(f).getroot().findall("ThingDef"):
            dn = td.findtext("defName")
            ext = [li for li in td.findall("modExtensions/li") if "ModExtension_Graffiti" in (li.get("Class") or "")]
            if not dn or not ext:
                continue
            e = ext[0]
            rows.append([dn, (e.findtext("form") or "").strip(), (e.findtext("poolWeight") or "1").strip(), (e.findtext("minArtistic") or "0").strip(),
                         (td.findtext("statBases/Beauty") or "").strip(), "1" if e.find("requiresAnyMeme") is not None else "0"])
    with open(path, "w", newline="\n") as f:
        f.write("\n".join("\t".join(r) for r in rows) + "\n")
    return len(rows)


def temper_tsv(src, path):
    out = []
    root = ET.parse(os.path.join(src, "Defs", "TemperamentDefs_Graffiti.xml")).getroot()
    for li in root.iter("li"):
        key = li.findtext("trait") or li.findtext("gene") or li.findtext("hediff") or li.findtext("precept")
        if not key:
            continue
        if li.findtext("degree"):
            key += ":" + li.findtext("degree").strip()
        spec = ",".join("%s=%s" % (c.tag, (c.text or "").strip()) for c in li if c.tag in ("numb", "bad", "good", "fine", "ugly", "temper", "paint", "offended", "neat", "lean"))
        out.append(key + "\t" + spec)
    with open(path, "w", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    return len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=None)
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
    stage = os.path.join(root, "scratch", os.environ.get("GR_LANE1_STAGE", "graffiti_blind_c1_lane1"))
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    shutil.copy(a.kernel or os.path.join(a.src, "Source", "Kernel", "RM_GraffitiKernel.cs"), os.path.join(stage, "RM_GraffitiKernel.cs"))
    for enum in ("GraffitiForm.cs", "GraffitiCategory.cs"):
        shutil.copy(os.path.join(a.src, "Source", enum), stage)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    nd = defs_tsv(a.src, os.path.join(stage, "defs.tsv"))
    nt = temper_tsv(a.src, os.path.join(stage, "temper.tsv"))
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400)
    if b.returncode:
        print("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
        sys.exit(2)
    senv = settings_env(a.src)
    senv["GR_DEFS"] = win + "\\defs.tsv"
    senv["GR_TEMPER"] = win + "\\temper.tsv"
    env = dict(os.environ, **senv)
    env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", "")] + list(senv)))
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    with open(a.out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows:
        c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "defs", nd, "temper rows", nt, "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL":
            print("FAIL", row["id"], row["detail"][:400])
    if r.returncode not in (0, 1) or not rows:
        print("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))
        sys.exit(2)
    sys.exit(1 if c.get("FAIL") else 0)


main()
