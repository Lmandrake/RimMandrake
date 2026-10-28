#!/usr/bin/env python3
"""Offline hose/cord/liquid-net replay harness (HOSE_PERF_BUILD_OFFLINE_REPLAY_HARNESS; design: the advisory
design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md section 5).

Replays a 325x325 map plus an event stream against the REAL Verse-free FlowWorks cores (source-linked into
FlowWorks/Source/Replay/RimMandrakeFlowWorks.Replay.csproj, never copied) and gates the result:
  conserve     tank units are conserved every tick
  noflow       no committed move between two tanks with no live hose path (a cut earlier in the same tick counts)
  patch        every patched hose world equals a fresh HoseWorldPatch.Full of the same map
  comps        the cached liquid components equal an independent union-find over live links
  determinism  two replays give the identical per-tick fingerprint stream
  alloc        a warm HoseWorldPatch.Patch allocates 0 bytes
  ceiling      no op count (sum or per-tick max) exceeds the committed baseline (Replay/baseline.txt)
  trace        the trace has ticks and every event in it was applied (none outside ticks 0..N-1 or phases 0..2)
A gate with nothing to check reads skip, never green (--no-oracle, no read event, no committed move, no warm patch).
Time is reported (mean, p99, max, over-bar, worst ticks with their events), never gated.

    python3 src/RimMandrake/Utils/hose_replay.py run                       # every scenario, gates on
    python3 src/RimMandrake/Utils/hose_replay.py run --scenario rain --inject Leak
    python3 src/RimMandrake/Utils/hose_replay.py run --write-baseline      # after a deliberate op-count change
    python3 src/RimMandrake/Utils/hose_replay.py gen --scenario dry --out /mnt/d/ClaudeWork/.../dry.rmreplay

Reports land in D:\\ClaudeWork\\rimmandrake\\hose_harness\\runs\\<stamp>\\ (<scenario>.txt, .fp, summary.txt).
dotnet is the Windows-side SDK (see selftest_flowworks_stock.py). Only the linked sources are staged, into
D:\\ClaudeWork\\rimmandrake\\hose_harness\\stage\\{tree,head}; --head takes the production files from git HEAD (a peer's
uncommitted edits stay out), the Replay project always from the working tree. --no-build reuses the last build.
Exit code: 0 all gates green, 1 a gate red, 2 usage, 3 crash, 4 build failed.
"""
from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
from selftest_flowworks_stock import _find_dotnet, _to_windows_path, DOTNET_CANDIDATES  # noqa: E402

CSPROJ = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source", "Replay", "RimMandrakeFlowWorks.Replay.csproj")
BASELINE = os.path.join(os.path.dirname(CSPROJ), "baseline.txt")
HARNESS = "/mnt/d/ClaudeWork/rimmandrake/hose_harness"
RUNS = os.path.join(HARNESS, "runs")
# what the csproj source-links (repo-relative); staged alone, never the whole src: the generic winstage rsyncs all of src and
# queues on the shared FlowWorks dotnet lock behind every peer selftest (a 530 s timeout on 2026-10-28, build1.txt)
PROD_PATHS = ["src/RimMandrake/FlowWorks/Source/Hose", "src/RimMandrake/FlowWorks/Source/Machinery",
              "src/RimMandrake/FlowWorks/Source/RM_PumpMath.cs",
              "src/RimMandrake/FlowWorks/Source/RM_Volume.cs",
              "src/RimMandrake/FlowWorks/Source/RM_StockMath.cs", "src/RimMandrake/_Shared/SlackGeometry"]
REPLAY_REL = "src/RimMandrake/FlowWorks/Source/Replay"


def stage(head=False):
    """Copy the linked production sources (from git HEAD with head=True, so a peer's uncommitted edits stay out; else the
    working tree) plus the Replay project (always the working tree) into a stage of our own on D:. Returns the stage root."""
    root = os.path.join(HARNESS, "stage", "head" if head else "tree")
    for rel in PROD_PATHS:
        dst = os.path.join(root, rel)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        elif os.path.isfile(dst):
            os.remove(dst)
    os.makedirs(root, exist_ok=True)
    if head:
        arch = subprocess.run(["git", "-C", REPO, "archive", "HEAD"] + PROD_PATHS, capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", root], input=arch, check=True)
    else:
        for rel in PROD_PATHS:
            src, dst = os.path.join(REPO, rel), os.path.join(root, rel)
            if os.path.isdir(src):
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("bin", "obj"))
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
    subprocess.run(["rsync", "-rt", "--delete", "--exclude", "bin/", "--exclude", "obj/",
                    os.path.join(REPO, REPLAY_REL) + "/", os.path.join(root, REPLAY_REL) + "/"], check=True)
    return root


@contextlib.contextmanager
def stage_lock(root):
    """One build-and-run per stage at a time (two clones share D:); never the shared FlowWorks selftest lock."""
    import fcntl
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, ".lock"), "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def run_replay(args, out_dir=None, baseline=BASELINE, write_baseline=False, no_build=False, head=False, timeout=520):
    """Stage, build and run the replay. Returns (rc, stdout, stderr, out_dir); rc 4 = the build failed (stdout holds its log)."""
    dotnet = _find_dotnet()
    if dotnet is None:
        sys.exit("dotnet.exe not found at any of %r: UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)
    out_dir = out_dir or os.path.join(RUNS, time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(out_dir, exist_ok=True)
    cmd_args = list(args) + (["--out", _to_windows_path(out_dir)] if args and args[0] == "run" else [])
    if args and args[0] == "run":
        if write_baseline:
            cmd_args += ["--write-baseline", _to_windows_path(os.path.join(out_dir, "baseline.txt"))]
        elif baseline:
            if not os.path.isfile(baseline):
                sys.exit("no baseline at %s: run with --write-baseline first" % baseline)
            staged = os.path.join(out_dir, "baseline.in.txt")   # dotnet.exe cannot read the ext4 clone: hand it a copy
            shutil.copyfile(baseline, staged)
            cmd_args += ["--baseline", _to_windows_path(staged)]
    root = os.path.join(HARNESS, "stage", "head" if head else "tree")
    proj = os.path.join(root, REPLAY_REL, os.path.basename(CSPROJ))
    dll = os.path.join(root, REPLAY_REL, "bin", "Release", "net8.0", "RimMandrakeFlowWorks.Replay.dll")
    started = time.time()
    with stage_lock(root):
        if not no_build or not os.path.isfile(dll):
            stage(head)
            b = subprocess.run([dotnet, "build", _to_windows_path(proj), "-c", "Release", "-nologo", "-v:q"],
                               capture_output=True, text=True, timeout=timeout)
            if b.returncode != 0:
                return 4, b.stdout, b.stderr, out_dir
        p = subprocess.run([dotnet, _to_windows_path(dll)] + cmd_args, capture_output=True, text=True,
                           timeout=max(30, timeout - (time.time() - started)))
    if write_baseline and p.returncode in (0, 1) and os.path.isfile(os.path.join(out_dir, "baseline.txt")):
        shutil.copyfile(os.path.join(out_dir, "baseline.txt"), BASELINE)
    return p.returncode, p.stdout, p.stderr, out_dir


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    write_baseline = "--write-baseline" in argv
    no_build = "--no-build" in argv
    head = "--head" in argv
    argv = [a for a in argv if a not in ("--write-baseline", "--no-build", "--head")]
    out_dir = None
    if "--out" in argv and argv[0] == "run":
        i = argv.index("--out")
        out_dir = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    if not argv or argv[0] not in ("run", "gen"):
        sys.exit(__doc__)
    if argv[0] == "gen":
        i = argv.index("--out")
        argv[i + 1] = _to_windows_path(os.path.abspath(argv[i + 1]))
    rc, out, err, out_dir = run_replay(argv, out_dir=out_dir, write_baseline=write_baseline, no_build=no_build, head=head)
    print(out, end="")
    if err.strip():
        print(err, end="", file=sys.stderr)
    if argv[0] == "run":
        print("reports: %s" % _to_windows_path(out_dir))
        if write_baseline:
            print("baseline copied to %s (commit it with the change that moved the counts)" % BASELINE)
    sys.exit(rc)


if __name__ == "__main__":
    main()
