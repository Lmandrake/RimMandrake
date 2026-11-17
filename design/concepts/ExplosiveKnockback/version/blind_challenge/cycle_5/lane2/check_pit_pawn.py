#!/usr/bin/env python3
"""Red/green check for RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER (bar pawn_hits_pawn_stops): at a given commit, does a
thrown pawn stop at another pawn standing on a pit cover? Two halves:
  1. the pure rule, run: RM_KnockbackMath.PitCell(covered, forPawn, pawnThere) from that commit's kernel, compiled with the
     Windows dotnet and called by reflection over its whole truth table (a pawn there blocks a thrown pawn, open pit or cover);
  2. the wiring, read: that commit's RM_MapKbGrid.At answers a superdeep cell through PitCell (the grid itself is Verse code and
     cannot run offline; without this a correct rule could sit unused).
    python3 check_pit_pawn.py [--rev <sha>]      (default: the working tree)
rc 0 = the rule holds and the grid uses it; rc 1 = it does not (the first failing line is printed)."""
import argparse, glob, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = "src/RimMandrake/ExplosiveKnockback/Source/"
STAGE = "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c5_pitcheck"
HARNESS = r"""
using System; using System.Reflection; using RimMandrake.ExplosiveKnockback;
public static class P { public static int Main() {
  MethodInfo m = typeof(RM_KnockbackMath).GetMethod("PitCell", new[] { typeof(bool), typeof(bool), typeof(bool) });
  if (m == null) { Console.WriteLine("FAIL the kernel has no pit-cell rule: the grid answers CoveredPit for a cover before it looks for a pawn on it"); return 1; }
  var want = new (bool c, bool f, bool o, KbCell k)[] {
    (true, true, true, KbCell.Pawn), (false, true, true, KbCell.Pawn), (true, true, false, KbCell.CoveredPit),
    (false, true, false, KbCell.Pit), (true, false, true, KbCell.CoveredPit), (false, false, true, KbCell.Pit) };
  int bad = 0;
  foreach (var w in want) { var got = (KbCell)m.Invoke(null, new object[] { w.c, w.f, w.o });
    if (got != w.k) { Console.WriteLine("FAIL PitCell(covered=" + w.c + ", forPawn=" + w.f + ", pawnThere=" + w.o + ") = " + got + ", want " + w.k); bad++; } }
  if (bad == 0) Console.WriteLine("RULE ok: a pawn on a cover or an open pit blocks a thrown pawn; goods pass; 6 of 6");
  return bad == 0 ? 0 : 1; } }
"""
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""


def read(rev, path):
    if not rev:
        return open(os.path.join(REPO, path), encoding="utf-8-sig").read()
    return subprocess.run(["git", "show", "%s:%s" % (rev, path)], cwd=REPO, capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="")
    a = ap.parse_args()
    tag = a.rev[:10] or "worktree"
    kernel, grid = read(a.rev, SRC + "RM_KnockbackMath.cs"), read(a.rev, SRC + "RM_MapComponent_Knockback.cs")
    os.makedirs(STAGE, exist_ok=True)
    for f in glob.glob(os.path.join(STAGE, "*.cs")):
        os.remove(f)
    shutil.rmtree(os.path.join(STAGE, "obj"), ignore_errors=True)
    open(os.path.join(STAGE, "RM_KnockbackMath.cs"), "w").write(kernel)
    open(os.path.join(STAGE, "P.cs"), "w").write(HARNESS)
    open(os.path.join(STAGE, "P.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\P.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=300)
    if b.returncode:
        print("FAIL %s: harness build failed %s" % (tag, (b.stdout + b.stderr)[-400:]))
        return 1
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\P.dll"], capture_output=True, text=True, timeout=120)
    out = r.stdout.strip()
    if r.returncode:
        print("%s: %s" % (tag, out.splitlines()[0] if out else "rc %s" % r.returncode))
        return 1
    m = re.search(r"if \(RM_KnockbackCompat\.IsSuperdeep\(map, c\)\)\s*\{(.*?)\n            \}", grid, re.S)
    if not m or "RM_KnockbackMath.PitCell(" not in m.group(1):
        print("FAIL %s: RM_MapKbGrid.At does not answer a superdeep cell through RM_KnockbackMath.PitCell" % tag)
        return 1
    print("PASS %s: %s; RM_MapKbGrid.At answers superdeep cells through it" % (tag, out.splitlines()[-1]))
    return 0


sys.exit(main())
