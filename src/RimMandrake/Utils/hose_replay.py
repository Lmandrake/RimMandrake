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
  replanquota  no tick runs more CheckReplans than HoseReplanQueue.MaxStartsPerTick (HOSE_RECHECK_TAME_REPLAN_OFF_TICK)
A gate with nothing to check reads skip, never green (--no-oracle, no read event, no committed move, no warm patch).
Time is reported (mean, p99, max, over-bar, worst ticks with their events), never gated.

    python3 src/RimMandrake/Utils/hose_replay.py run                       # every scenario, gates on
    python3 src/RimMandrake/Utils/hose_replay.py run --scenario rain --inject Leak
    python3 src/RimMandrake/Utils/hose_replay.py run --write-baseline      # after a deliberate op-count change
    python3 src/RimMandrake/Utils/hose_replay.py gen --scenario dry --out /mnt/d/ClaudeWork/.../dry.rmreplay
    python3 src/RimMandrake/Utils/hose_replay.py mono [--write]            # Mono timing lane (advisory)
    python3 src/RimMandrake/Utils/hose_replay.py mono-check [REPORT]       # offline: is a Mono-lane report sound?

Mono timing lane (HOSE_REPLAY_WIRE_MONO_TIMING_LANE): the same sources also build as net472 (Replay/Mono/) and run under
the game's own Boehm-GC Mono, RimWorld\\MonoBleedingEdge\\EmbedRuntime\\mono-2.0-bdwgc.dll with the game's corlib, through
a tiny embedding host (Replay/Mono/Host/). `mono` runs every scenario on .NET 8 (gated, as `run`) and on Mono, requires
both green with identical fingerprint streams, and prints a side-by-side time table; --write also copies it to
Replay/mono_timing.txt (commit it). The time table is ADVISORY: the op-count gates stay the gate. Boehm Mono's allocation counter
is blind (answers 0), so on Mono the alloc gate skips and the bytes columns read UNMEASURED.

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
                    os.path.join(REPO, REPLAY_REL) + "/", os.path.join(root, REPLAY_REL) + "/"], check=True, timeout=600)
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


MONO_REPORT = os.path.join(os.path.dirname(CSPROJ), "mono_timing.txt")
TRACEGEN = os.path.join(os.path.dirname(CSPROJ), "TraceGen.cs")
GAME = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\RimWorld"
MONO_DLL_TAIL = "\\MonoBleedingEdge\\EmbedRuntime\\mono-2.0-bdwgc.dll"
SYSTEMS = ["World", "Recheck", "Lay", "Settle", "Move"]


def scenarios():
    """TraceGen.Scenarios, read from the source (the checker needs no build)."""
    import re
    src = open(TRACEGEN, encoding="utf-8").read()
    m = re.search(r"Scenarios\s*=\s*(?:new\s*(?:string)?\s*\[\s*\]\s*)?\{([^}]*)\}", src)
    if not m:
        raise SystemExit("cannot find TraceGen.Scenarios in %s" % TRACEGEN)
    return re.findall(r'"([^"]+)"', m.group(1))


def _report_facts(path):
    """(runtime, {sys: (mean, p99, max)}) from one scenario report."""
    runtime, times, in_time = None, {}, False
    for line in open(path, encoding="utf-8"):
        if line.startswith("hose replay: ") and "  runtime " in line:
            runtime = line.split("  runtime ", 1)[1].split("  inject ", 1)[0].strip()
        elif line.startswith("TIME per tick"):
            in_time = True
        elif in_time:
            f = line.split()
            if f and f[0] in SYSTEMS:
                times[f[0]] = tuple(float(x) for x in f[1:4])
            elif f and f[0] == "warm":
                in_time = False
    return runtime, times


def _fp_digest(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def mono_lane(write=False, timeout=520):
    """Run every scenario on .NET 8 (gated) and on the game's Mono; return (rc, report text, out_dir)."""
    dotnet = _find_dotnet()
    if dotnet is None:
        sys.exit("dotnet.exe not found at any of %r: UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)
    started = time.time()
    out_dir = os.path.join(RUNS, "mono-" + time.strftime("%Y%m%d-%H%M%S"))
    rc_n, out_n, err_n, _ = run_replay(["run"], out_dir=os.path.join(out_dir, "dotnet"), timeout=timeout)
    if rc_n == 4:
        return 4, "the .NET 8 replay did not build:\n" + out_n[-3000:], out_dir
    root = os.path.join(HARNESS, "stage", "tree")
    rdir = os.path.join(root, REPLAY_REL)
    host = os.path.join(rdir, "Mono", "Host", "bin", "Release", "net8.0", "RimMandrakeFlowWorks.MonoHost.dll")
    exe = os.path.join(rdir, "Mono", "bin", "Release", "net472", "RimMandrakeFlowWorks.Replay.Mono.exe")
    mono_out = os.path.join(out_dir, "mono")
    os.makedirs(mono_out, exist_ok=True)
    with stage_lock(root):
        for proj in ("Mono/RimMandrakeFlowWorks.Replay.Mono.csproj", "Mono/Host/RimMandrakeFlowWorks.MonoHost.csproj"):
            b = subprocess.run([dotnet, "build", _to_windows_path(os.path.join(rdir, proj)), "-c", "Release", "-nologo", "-v:q"],
                               capture_output=True, text=True, timeout=max(30, timeout - (time.time() - started)))
            if b.returncode != 0:
                return 4, "%s did not build:\n%s" % (proj, b.stdout[-3000:]), out_dir
        p = subprocess.run([dotnet, _to_windows_path(host), GAME, _to_windows_path(exe), "run", "--scenario", "all",
                            "--out", _to_windows_path(mono_out)],
                           capture_output=True, text=True, timeout=max(30, timeout - (time.time() - started)))
    dll = next((l.split("dll=", 1)[1].split(" corlib=", 1)[0] for l in p.stderr.splitlines() if l.startswith("MONOHOST ")), None)
    lines = ["# hose replay Mono timing lane (HOSE_REPLAY_WIRE_MONO_TIMING_LANE): written by `hose_replay.py mono --write`.",
             "# ADVISORY: times are never gated; the .NET 8 op-count gates stay the gate. Checked by `hose_replay.py mono-check`.",
             "# ms per tick from run 2 (no oracle); tick 0 includes JIT. ratio = mono mean / dotnet mean."]
    dn_rt = mono_rt = None
    rows, time_rows = [], []
    for sc in scenarios():
        fn, fm = (os.path.join(out_dir, d, sc + ".fp") for d in ("dotnet", "mono"))
        tn, tm = (os.path.join(out_dir, d, sc + ".txt") for d in ("dotnet", "mono"))
        if not all(os.path.isfile(x) for x in (fn, fm, tn, tm)):
            rows.append("SCENARIO %s MISSING" % sc)
            continue
        rn, timn = _report_facts(tn)
        rm, timm = _report_facts(tm)
        dn_rt, mono_rt = dn_rt or rn, mono_rt or rm
        res = lambda out: ("PASS" if ("RESULT %s PASS" % sc) in out else "FAIL")
        rows.append("SCENARIO %s dotnet=%s mono=%s fp_dotnet=%s fp_mono=%s" % (sc, res(out_n), res(p.stdout), _fp_digest(fn), _fp_digest(fm)))
        for s_ in SYSTEMS:
            a, b_ = timn.get(s_), timm.get(s_)
            if a and b_:
                ratio = "%.2f" % (b_[0] / a[0]) if a[0] > 0 else "-"
                time_rows.append("TIME %-10s %-8s dotnet %.4f %.4f %.4f  mono %.4f %.4f %.4f  ratio %s" % ((sc, s_) + a + b_ + (ratio,)))
    lines += ["MONO_DLL %s" % dll, "MONO_RUNTIME %s" % mono_rt, "DOTNET_RUNTIME %s" % dn_rt, "MONO_EXIT %d" % p.returncode,
              "DOTNET_EXIT %d" % rc_n, "#            scenario   system   dotnet mean p99 max  mono mean p99 max"]
    text = "\n".join(lines + rows + time_rows) + "\n"
    with open(os.path.join(out_dir, "mono_timing.txt"), "w") as f:
        f.write(text)
    if write:
        shutil.copyfile(os.path.join(out_dir, "mono_timing.txt"), MONO_REPORT)
    if p.returncode not in (0, 1):
        text += "mono host stderr:\n" + p.stderr[-3000:]
    return mono_check_text(text)[0], text, out_dir


def mono_check_text(text):
    """(rc, problems): 0 when the report names the game's Boehm Mono, covers every scenario, both runtimes passed every
    gate, every fingerprint stream matches across runtimes, and every scenario has a time row per system."""
    probs, kv, sc_rows, time_keys = [], {}, {}, set()
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if f[0] == "SCENARIO":
            sc_rows[f[1]] = dict(x.split("=", 1) for x in f[2:] if "=" in x)
        elif f[0] == "TIME" and len(f) >= 12:
            time_keys.add((f[1], f[2]))
        elif f[0] in ("MONO_DLL", "MONO_RUNTIME", "DOTNET_RUNTIME", "MONO_EXIT", "DOTNET_EXIT"):
            kv[f[0]] = line.split(" ", 1)[1].strip() if " " in line else ""
    if not kv.get("MONO_DLL", "").endswith(MONO_DLL_TAIL):
        probs.append("MONO_DLL is not the game's %s: %r" % (MONO_DLL_TAIL, kv.get("MONO_DLL")))
    if not kv.get("MONO_RUNTIME", "").startswith("Mono "):
        probs.append("MONO_RUNTIME is not Mono: %r" % kv.get("MONO_RUNTIME"))
    if not kv.get("DOTNET_RUNTIME", "").startswith(".NET 8"):
        probs.append("DOTNET_RUNTIME is not .NET 8: %r" % kv.get("DOTNET_RUNTIME"))
    for k in ("MONO_EXIT", "DOTNET_EXIT"):
        if kv.get(k) != "0":
            probs.append("%s %r, not 0" % (k, kv.get(k)))
    for sc in scenarios():
        r = sc_rows.get(sc)
        if r is None:
            probs.append("scenario %s absent" % sc)
            continue
        if r.get("dotnet") != "PASS" or r.get("mono") != "PASS":
            probs.append("scenario %s not PASS on both: %r" % (sc, r))
        if not r.get("fp_dotnet") or r.get("fp_dotnet") != r.get("fp_mono"):
            probs.append("scenario %s fingerprints differ: dotnet %s mono %s" % (sc, r.get("fp_dotnet"), r.get("fp_mono")))
        missing = [s_ for s_ in SYSTEMS if (sc, s_) not in time_keys]
        if missing:
            probs.append("scenario %s has no time row for %s" % (sc, ",".join(missing)))
    return (0 if not probs else 1), probs


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
    if argv and argv[0] == "mono-check":
        path = argv[1] if len(argv) > 1 else MONO_REPORT
        rc, probs = mono_check_text(open(path, encoding="utf-8").read())
        for pr in probs:
            print("MONO-CHECK FAIL " + pr)
        print("MONO-CHECK %s %s (%d scenarios)" % ("PASS" if rc == 0 else "FAIL", path, len(scenarios())))
        sys.exit(rc)
    if argv and argv[0] == "mono":
        rc, text, d = mono_lane(write="--write" in argv)
        print(text, end="")
        print("reports: %s%s" % (_to_windows_path(d), "; copied to %s" % MONO_REPORT if "--write" in argv else ""))
        sys.exit(rc)
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
