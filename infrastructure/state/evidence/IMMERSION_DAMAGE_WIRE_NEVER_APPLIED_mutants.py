#!/usr/bin/env python3
"""Mutation proof for IMMERSION_DAMAGE_WIRE_NEVER_APPLIED.

Item: a pawn in chest-deep liquid (RM_AcidDeep: contact 1, immersion 3) must take damageOnImmersion, not
damageOnContact; LiquidCorrosion.DoCorrosionPass is the consumer. The SelfTest case CASE (in
src/RimMandrake/FlowWorks/Source/SelfTest/ImmersionChecks.cs) reads DoCorrosionPass's deciding statements from the
LiquidCorrosion.cs that sits in the staged mod tree, interprets them and runs them on every shipped liquid terrain.

1. CLEAN: the repo's own runner, selftest_flowworks_stock.py --only CASE, on the code as it stands (restages the
   whole tree). Must exit 0, print `ok    CASE`, exactly one case run.
2. The stage that run built must hold LiquidCorrosion.cs byte-identical to the repo, and every mutated line must
   occur in it exactly once (so the mutants are mutants of THIS code).
3. MUTANTS: each rewrites the STAGE copy only (the repo source is never touched) and runs the built exe --only CASE
   (the case reads the source at run time, from the mod root above the exe). CAUGHT only when exactly one case ran,
   the exe exited non-zero and printed `FAIL  CASE`. A run where the case did not run is BROKEN, never caught.
4. CONTROL: the stage copy is restored and the exe must pass the case again.

Mutants (each a way the item's fix can break):
  pick_contact   spec pick Immersion -> props.damageOnContact (the blind checker's named mutant: the original defect)
  pick_swapped   Immersion -> damageOnContact and Contact -> damageOnImmersion
  suite_false    SuiteDeep(terrain) replaced by false (slime deep stops immersing)
  no_chestdeep   the terrainSuite.chestDeep set.Add dropped
  no_takedamage  pawn.TakeDamage(dinfo) removed (spec chosen, never applied)
  imm_dead       Select's immersionLive argument replaced by false
Not a selftest (no `selftest` in the name). Run it alone:
    python3 infrastructure/state/evidence/IMMERSION_DAMAGE_WIRE_NEVER_APPLIED_mutants.py
Exit 0 and last line `RESULT PASS` only when all four steps hold.
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
SRC = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source", "LiquidTypes", "LiquidCorrosion.cs")
CSPROJ = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source", "SelfTest", "RimMandrakeFlowWorks.SelfTest.csproj")
RUNNER = os.path.join(UTILS, "selftest_flowworks_stock.py")
CASE = "ImmersionDamage_corrosion_pass_wiring_runs_on_shipped_defs"

PICK = "exposure == RM_LiquidImmersionMath.Exposure.Immersion ? props.damageOnImmersion"
PICK2 = ": exposure == RM_LiquidImmersionMath.Exposure.Contact ? props.damageOnContact : null;"
SUITE = "IsImmersing(terrain.passability == Traversability.Impassable, SuiteDeep(terrain), terrain.tags)"
CHEST = "if (l.terrainSuite?.chestDeep != null) set.Add(l.terrainSuite.chestDeep);"
TAKE = "pawn.TakeDamage(dinfo);"
SELECT = "RM_LiquidImmersionMath.Select(immersing, contactLive, immersionLive)"

MUTANTS = {
    "pick_contact": [(PICK, PICK.replace("damageOnImmersion", "damageOnContact"))],
    "pick_swapped": [(PICK, PICK.replace("damageOnImmersion", "damageOnContact")),
                     (PICK2, PICK2.replace("damageOnContact", "damageOnImmersion"))],
    "suite_false": [(SUITE, SUITE.replace("SuiteDeep(terrain)", "false"))],
    "no_chestdeep": [(CHEST, "")],
    "no_takedamage": [(TAKE, "")],
    "imm_dead": [(SELECT, SELECT.replace("immersionLive)", "false)"))],
}

sys.path.insert(0, UTILS)
from selftest_flowworks_stock import dotnet_lock  # noqa: E402
from selftest_winstage import windows_project_path  # noqa: E402


def to_posix(win):
    m = re.match(r"^([A-Za-z]):\\(.*)$", win)
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")) if m else win


def clean_run():
    t = time.time()
    p = subprocess.run([sys.executable, RUNNER, "--only", CASE], cwd=REPO, capture_output=True, text=True, timeout=480)
    out = p.stdout + p.stderr
    ok = p.returncode == 0 and ("ok    " + CASE) in out and "1 case(s)" in out
    print("clean    %s rc=%d %.0fs" % ("PASS" if ok else "FAIL", p.returncode, time.time() - t))
    if not ok:
        print("\n".join(out.splitlines()[-8:]))
    return ok


def run_case(exe):
    """Run the built exe on CASE. Returns (verdict, detail): verdict in pass / fail / broken."""
    r = subprocess.run([exe, "--only", CASE], capture_output=True, text=True, timeout=120, cwd="/tmp")
    out = r.stdout + r.stderr
    if "1 case(s)" not in out:
        return "broken", "rc=%d the case did not run" % r.returncode
    if ("ok    " + CASE) in out and r.returncode == 0:
        return "pass", ""
    if ("FAIL  " + CASE) in out and r.returncode != 0:
        msg = [l.strip() for l in out.splitlines() if "LiquidCorrosion" in l or "SuiteDeep" in l or "expected" in l]
        return "fail", msg[-1] if msg else ""
    return "broken", "rc=%d neither ok nor FAIL for the case" % r.returncode


def main():
    t0 = time.time()
    for d in ("/tmp", os.environ.get("TMPDIR") or "/tmp"):
        if os.path.isdir(d):
            st = os.statvfs(d)
            if st.f_bavail * st.f_frsize // (1024 * 1024) < 200:
                print("UNMEASURED: %s has under 200 MB free; free scratch there first" % d)
                return 1
    with open(SRC, "rb") as f:
        repo_src = f.read()
    text0 = repo_src.decode("utf-8")
    for name, edits in MUTANTS.items():
        for old, _ in edits:
            if text0.count(old) != 1:
                print("PROBE BROKEN: mutant %s: line not in the repo's LiquidCorrosion.cs exactly once: %s" % (name, old))
                return 1
    if not clean_run():
        print("RESULT FAIL (clean run)")
        return 1
    win_csproj = windows_project_path(CSPROJ, restage=False)
    sdir = os.path.dirname(to_posix(win_csproj))
    stage_src = os.path.join(os.path.dirname(sdir), "LiquidTypes", "LiquidCorrosion.cs")
    exe = os.path.join(sdir, "bin", "Release", "net8.0", "RimMandrakeFlowWorks.SelfTest.exe")
    bad = 0
    with dotnet_lock():
        with open(stage_src, "rb") as f:
            staged = f.read()
        if staged != repo_src:
            print("PROBE BROKEN: stage %s is not the repo's LiquidCorrosion.cs" % stage_src)
            return 1
        try:
            for name, edits in MUTANTS.items():
                text = text0
                for old, new in edits:
                    text = text.replace(old, new)
                assert text != text0
                with open(stage_src, "wb") as f:
                    f.write(text.encode("utf-8"))
                v, d = run_case(exe)
                print("%-14s %s %s" % (name, {"fail": "CAUGHT", "pass": "SURVIVED", "broken": "BROKEN"}[v], d))
                if v != "fail":
                    bad += 1
        finally:
            with open(stage_src, "wb") as f:
                f.write(staged)
        v, d = run_case(exe)
        print("control        %s %s" % ("PASS" if v == "pass" else v.upper(), d))
        if v != "pass":
            bad += 1
    with open(SRC, "rb") as f:
        if f.read() != repo_src:
            print("REPO SOURCE CHANGED during the run")
            return 1
    print("repo LiquidCorrosion.cs untouched; stage restored; %.0fs" % (time.time() - t0))
    print("RESULT %s" % ("PASS" if bad == 0 else "FAIL (%d)" % bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
