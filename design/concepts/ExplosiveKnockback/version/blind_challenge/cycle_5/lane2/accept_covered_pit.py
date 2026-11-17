#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_STOP_THROWS_OVER_COVERED_PITS_K08_SAYS_GROUND (bar thrown_into_pit_falls, scene sc_pit_fall:
"a second colonist and stack aimed at a covered pit cell ... the kernel's planned landing cell ... lies beyond the pit's far
rim ... on the covered cell the colonist and the stack fall through, one descent each, and the cover is broken").
Runs the kernel (RM_KnockbackMath.cs at --rev, default the working tree) with the Windows dotnet:
  A1 a pawn thrown 4 cells over a covered cell 2 out ends IN that cell (not beyond)
  A2 a stack likewise
  A3 with throw-into-pits off the covered cell is a wall (stops before it), as an open pit is
  A4 a blast-thrown pawn landing on a cover breaks it (LandingBreaksCover(Pawn, covered, not container, id 7))
  A5 a gas shove (negative id) onto a cover still never breaks it, a stack's or a pawn's
  A6 an empty covered cell the throw does not reach is untouched: a 1-cell throw with the cover 2 out lands 1 out
rc 0 = all six hold. Expected 6 of 6 on a correct fix; on 42225e0686 it fails A1, A2, A3 and A4."""
import argparse, glob, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
KERNEL = "src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackMath.cs"
STAGE = "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c5_accept_cover"
HARNESS = r"""
using System; using System.Collections.Generic; using RimMandrake.ExplosiveKnockback;
sealed class G : IKbGrid { public Dictionary<(int,int),KbCell> c = new Dictionary<(int,int),KbCell>();
  public KbCell At(int x, int z) => x < 0 || z < 0 || x > 20 || z > 4 ? KbCell.OutOfBounds : (c.TryGetValue((x, z), out var v) ? v : KbCell.Open); }
public static class P { static int ok, bad; static void T(string n, bool b) { if (b) ok++; else { bad++; Console.WriteLine("FAIL " + n); } }
 public static int Main() {
  var g = new G(); g.c[(3, 2)] = KbCell.CoveredPit; var s = new KbSettings();
  var a = RM_KnockbackMath.Resolve(g, 1, 2, 1f, 0f, 4, KbKind.Pawn, 70f, s); T("A1 pawn ends in the covered cell (dest " + a.destX + ", stop " + a.stop + ")", a.destX == 3);
  var b = RM_KnockbackMath.Resolve(g, 1, 2, 1f, 0f, 4, KbKind.Item, 1f, s); T("A2 stack ends in the covered cell (dest " + b.destX + ")", b.destX == 3);
  var off = RM_KnockbackMath.Resolve(g, 1, 2, 1f, 0f, 4, KbKind.Pawn, 70f, new KbSettings { intoPits = false }); T("A3 into pits off: stops before (dest " + off.destX + ")", off.destX == 2);
  T("A4 a blast-thrown pawn landing on a cover breaks it", RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, 7));
  T("A5 a gas shove never breaks a cover", !RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, -2) && !RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, false, -2));
  var one = RM_KnockbackMath.Resolve(g, 1, 2, 1f, 0f, 1, KbKind.Pawn, 70f, s); T("A6 a short throw lands short (dest " + one.destX + ")", one.destX == 2);
  Console.WriteLine("covered pit acceptance: " + ok + " of " + (ok + bad)); return bad == 0 ? 0 : 1; } }
"""
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="")
    a = ap.parse_args()
    src = (subprocess.run(["git", "show", "%s:%s" % (a.rev, KERNEL)], cwd=REPO, capture_output=True, text=True, check=True).stdout
           if a.rev else open(os.path.join(REPO, KERNEL), encoding="utf-8-sig").read())
    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE)
    open(os.path.join(STAGE, "RM_KnockbackMath.cs"), "w").write(src)
    open(os.path.join(STAGE, "P.cs"), "w").write(HARNESS)
    open(os.path.join(STAGE, "P.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\P.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=300)
    if b.returncode:
        print("FAIL build: " + (b.stdout + b.stderr)[-400:])
        return 1
    r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\P.dll"], capture_output=True, text=True, timeout=120)
    print(r.stdout.strip())
    return r.returncode


sys.exit(main())
