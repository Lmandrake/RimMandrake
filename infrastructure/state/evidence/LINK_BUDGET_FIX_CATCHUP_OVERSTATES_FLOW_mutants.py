#!/usr/bin/env python3
"""Mutation proof for LINK_BUDGET_FIX_CATCHUP_OVERSTATES_FLOW.

Done-when (owner note 2026-10-29): RM_LevellingMath.Plan with n=65, maxLinks=64 moves the same aggregate units as
n=64 (rate scaled by the visited fraction, not ceil); a SelfTest asserts it.

1. CLEAN: the repo's own runner, selftest_flowworks_stock.py --only <CASE>, on the code as it stands (restages the
   whole tree, ~95 s). Must exit 0, print `ok    <CASE>` and the aggregate line.
2. The stage that run built must hold RM_LevellingMath.cs byte-identical to the repo (so the mutants below are
   mutants of THIS code), and the rate line must occur in it exactly once.
3. MUTANTS: each rewrites the rate line in the STAGE copy only (the repo source is never touched), rebuilds the stage
   (~3 s) and runs the built exe --only <CASE>. A mutant counts as CAUGHT only when the build succeeded, exactly one
   case ran, the exe exited non-zero and printed `FAIL  <CASE>`. A build failure or a run where the case did not run
   is BROKEN (the instrument saw nothing), which fails the proof, never counts as caught.
4. CONTROL: the stage copy is restored, rebuilt, and the exe must pass the case again (the stage path itself is sound).

Mutants (each one a way the item's done-when can break):
  ceil      the original bug: rate = R * min(ceil(n/visit), MaxCatchUp)  -> n=65 moves ~2x (128000)
  ceilnocap ceil without the cap                                         -> n=65 2x and n=1000 16x
  nocap     the MaxCatchUp cap dropped                                    -> n=1000 moves 15x
  noscale   no catch-up at all (rate = R always)                          -> n=128 moves only 1x
  capoff1   the cap one lower (MaxCatchUp - 1)                            -> n=1000 moves 7x, not 8x
  overhalf  n=65 rounded to nearest, not floored ((n*R + visit/2)/visit) -> n=65 per visit 1016, agg 65024 > 65000
Not a selftest (no `selftest` in the name). Run it alone:
    python3 infrastructure/state/evidence/LINK_BUDGET_FIX_CATCHUP_OVERSTATES_FLOW_mutants.py
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
SRC = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source", "RM_LevellingMath.cs")
CSPROJ = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source", "SelfTest", "RimMandrakeFlowWorks.SelfTest.csproj")
RUNNER = os.path.join(UTILS, "selftest_flowworks_stock.py")
CASE = "LEVELLING_link_budget_catch_up_scales_by_visited_fraction"
LINE = "long rate = n <= visit ? ratePerLink : Math.Min(ratePerLink * n / visit, ratePerLink * MaxCatchUp);"
MUTANTS = {
    "ceil": "long rate = ratePerLink * Math.Min((n + visit - 1) / visit, MaxCatchUp);",
    "ceilnocap": "long rate = ratePerLink * ((n + visit - 1) / visit);",
    "nocap": "long rate = n <= visit ? ratePerLink : ratePerLink * n / visit;",
    "noscale": "long rate = ratePerLink;",
    "capoff1": "long rate = n <= visit ? ratePerLink : Math.Min(ratePerLink * n / visit, ratePerLink * (MaxCatchUp - 1));",
    "overhalf": "long rate = n <= visit ? ratePerLink : Math.Min((ratePerLink * n + visit / 2) / visit, ratePerLink * MaxCatchUp);",
}

sys.path.insert(0, UTILS)
from selftest_flowworks_stock import _find_dotnet, dotnet_lock  # noqa: E402
from selftest_winstage import windows_project_path  # noqa: E402


def to_posix(win):
    m = re.match(r"^([A-Za-z]):\\(.*)$", win)
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")) if m else win


def clean_run():
    t = time.time()
    p = subprocess.run([sys.executable, RUNNER, "--only", CASE], cwd=REPO, capture_output=True, text=True, timeout=400)
    out = p.stdout + p.stderr
    agg = [l.strip() for l in out.splitlines() if "aggregate per cycle" in l]
    ok = p.returncode == 0 and ("ok    " + CASE) in out and bool(agg) and "1 case(s)" in out
    print("clean    %s rc=%d %.0fs %s" % ("PASS" if ok else "FAIL", p.returncode, time.time() - t, " | ".join(agg)))
    return ok


def stage_case(dotnet, win_csproj, exe):
    """Build the stage, run the case. Returns (verdict, detail): verdict in pass / fail / broken."""
    b = subprocess.run([dotnet, "build", win_csproj, "-c", "Release", "-nologo", "-v", "q"], capture_output=True, text=True,
                       timeout=200, cwd="/tmp")
    if b.returncode != 0:
        return "broken", "build rc=%d %s" % (b.returncode, "".join((b.stdout + b.stderr).strip().splitlines()[-1:]))
    r = subprocess.run([exe, "--only", CASE], capture_output=True, text=True, timeout=120, cwd="/tmp")
    out = r.stdout + r.stderr
    lines = out.splitlines()
    if "1 case(s)" not in out:
        return "broken", "rc=%d the case did not run" % r.returncode
    if ("ok    " + CASE) in out and r.returncode == 0:
        return "pass", next((l.strip() for l in lines if "aggregate per cycle" in l), "")
    if ("FAIL  " + CASE) in out and r.returncode != 0:
        i = lines.index("FAIL  " + CASE)
        return "fail", lines[i + 1].strip() if i + 1 < len(lines) else ""
    return "broken", "rc=%d neither ok nor FAIL for the case" % r.returncode


def main():
    t0 = time.time()
    with open(SRC, "rb") as f:
        repo_src = f.read()
    if repo_src.decode("utf-8").count(LINE) != 1:
        print("PROBE BROKEN: the rate line is not in the repo's RM_LevellingMath.cs exactly once")
        return 1
    if not clean_run():
        print("RESULT FAIL (clean run)")
        return 1
    dotnet = _find_dotnet()
    if dotnet is None:
        print("UNMEASURED: dotnet.exe not found")
        return 1
    win_csproj = windows_project_path(CSPROJ, restage=False)
    sdir = os.path.dirname(to_posix(win_csproj))
    stage_src = os.path.join(os.path.dirname(sdir), "RM_LevellingMath.cs")
    exe = os.path.join(sdir, "bin", "Release", "net8.0", "RimMandrakeFlowWorks.SelfTest.exe")
    bad = 0
    with dotnet_lock():
        with open(stage_src, "rb") as f:
            staged = f.read()
        if staged != repo_src:
            print("PROBE BROKEN: stage %s is not the repo's RM_LevellingMath.cs" % stage_src)
            return 1
        text = staged.decode("utf-8")
        try:
            for name, repl in MUTANTS.items():
                with open(stage_src, "wb") as f:
                    f.write(text.replace(LINE, repl).encode("utf-8"))
                v, d = stage_case(dotnet, win_csproj, exe)
                label = {"fail": "CAUGHT", "pass": "SURVIVED", "broken": "BROKEN"}[v]
                print("%-9s %s %s" % (name, label, d))
                if v != "fail":
                    bad += 1
        finally:
            with open(stage_src, "wb") as f:
                f.write(staged)
        v, d = stage_case(dotnet, win_csproj, exe)
        print("control   %s %s" % ("PASS" if v == "pass" else v.upper(), d))
        if v != "pass":
            bad += 1
    with open(SRC, "rb") as f:
        if f.read() != repo_src:
            print("REPO SOURCE CHANGED during the run")
            return 1
    print("repo RM_LevellingMath.cs untouched; stage restored; %.0fs" % (time.time() - t0))
    print("RESULT %s" % ("PASS" if bad == 0 else "FAIL (%d)" % bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
