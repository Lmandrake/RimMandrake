#!/usr/bin/env python3
"""walled-residue diagnostic (diag.py plus Residue.cs): stage lane-1's harness (Main renamed) + Diag.cs + the kernels from a source dir, build, run a mode.
   diag.py <mode> <N> [--src <GSS dir>] [--b0 <seed offset>]"""
import glob, os, re, shutil, subprocess, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("N", type=int); ap.add_argument("--src"); ap.add_argument("--b0", type=int, default=0)
ap.add_argument("--repo", default=os.getcwd()); ap.add_argument("--base", action="store_true"); ap.add_argument("--stage", default="/mnt/d/ClaudeWork/rimmandrake/scratch/gss_walled/rstage")
a = ap.parse_args()
R = a.repo; G = a.src or os.path.join(R, "src/RimMandrake/GimmeSomeSlack"); SH = os.path.join(os.path.dirname(G), "_Shared/SlackGeometry")
L1 = os.path.join(R, "design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane1/BlindLane1.cs")
st = a.stage; os.makedirs(st, exist_ok=True)
for f in glob.glob(st + "/*.cs"): os.remove(f)
fs = sorted(glob.glob(G + "/Source/Core/*.cs")) + [G + "/Source/Aerial/" + k for k in ("AerialMath.cs", "ShockRule.cs", "TapWindow.cs")] + sorted(glob.glob(SH + "/*.cs"))
for f in fs: shutil.copy(f, st)
t = open(L1).read().replace("static class BlindLane1", "static partial class BlindLane1", 1)
t = t.replace("static int Main()", "static int Main(string[] args)\n    {\n        if (args.Length > 0 && args[0].StartsWith(\"r_\")) return ResidueMain(args[0], int.Parse(args[1]), int.Parse(args[2]));\n        if (args.Length > 0) return DiagMain(args[0], int.Parse(args[1]), int.Parse(args[2]));\n        return MainL1();\n    }\n    static int MainL1()", 1)
open(st + "/BlindLane1.cs", "w").write(t)
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../judge_the_judge/Diag.cs"), st); shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Residue.cs"), st)
open(st + "/Diag.csproj", "w").write("""<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0162;CS0168;CS0219;CS0414;CS0649;CS0169;CS8632</NoWarn>
<Optimize>true</Optimize>""" + ("<DefineConstants>BASE</DefineConstants>" if a.base else "") + """</PropertyGroup></Project>""")
open(st + "/settings.json", "w").write("{}")
dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
win = subprocess.run(["wslpath", "-w", st], capture_output=True, text=True, check=True).stdout.strip()
b = subprocess.run([dn, "build", win + "\\Diag.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
if b.returncode: print("BUILD FAILED\n" + "\n".join(l for l in b.stdout.splitlines() if "error" in l)[-3000:]); sys.exit(2)
r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\Diag.dll", a.mode, str(a.N), str(a.b0)], capture_output=True, text=True, timeout=590)
print(r.stdout); print(r.stderr[-2000:]); sys.exit(r.returncode)
