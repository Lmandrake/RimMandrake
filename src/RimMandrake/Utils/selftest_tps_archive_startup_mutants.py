#!/usr/bin/env python3
"""Mutation check for selftest_tps_archive_startup.py (JAWABENCH_TPS_ARCHIVE_DIAGNOSE_STARTUP_CRASH).

Runs the guard on temp copies of JawaBenchTpsSampler.cs / JawaBenchTpsWriter.cs. The unmutated copy must PASS.
Each mutant breaks one clause of the fix and must FAIL; M1 is the blind checker's gen-1 mutant (taking the parked
archive back out and running it inside ArchivePrevLog, i.e. at bridge-registration, during patching). A mutant
whose anchor is missing from the source counts as a FAIL here, so this cannot quietly go blind when the code moves.

Exit 0 = every mutant caught and the baseline green; 1 otherwise.
"""
import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tps_guard", HERE / "selftest_tps_archive_startup.py")
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

PARK = "Interlocked.Exchange(ref _pendingArchive, () => W.ArchiveLog(prev, name, from));"
TAKE = "var a = Interlocked.Exchange(ref _pendingArchive, null);\n            if (a != null) a();"
GATE = "if (now - _idleSince < ArchiveIdleSeconds) return;"

# (id, file, old, new, what it breaks)
MUTANTS = [
    ("M1", "S", PARK, PARK + " var a0 = Interlocked.Exchange(ref _pendingArchive, null); if (a0 != null) a0();",
     "archive taken back and run inside ArchivePrevLog (checker's mutant)"),
    ("M2", "S", PARK, "Action x = () => W.ArchiveLog(prev, name, from); Interlocked.Exchange(ref _pendingArchive, x); x();",
     "parked lambda aliased and invoked at registration"),
    ("M3", "S", "W.WarmHash();", "",
     "no JIT warm-up on the installing thread"),
    ("M4", "S", "internal const double ArchiveIdleSeconds = 10;", "internal const double ArchiveIdleSeconds = 0;",
     "idle gate removed"),
    ("M5", "S", GATE, "var a1 = Interlocked.Exchange(ref _pendingArchive, null); if (a1 != null) a1(); " + GATE,
     "archive taken before the idle gate"),
    ("M6", "W", "var t = new Thread(() => { try { ArchiveLogNow(source, name, fromSession)", "ThreadPool.QueueUserWorkItem(_ => { try { ArchiveLogNow(source, name, fromSession); } catch { } }); var t = new Thread(() => { try { ArchiveLogNow(source, name, fromSession)",
     "archive hashed on the threadpool"),
    ("M7", "S", "RootFinalizerCore(__state, __exception);\n            PumpIdleSafe();",
     "if (__exception != null) return; RootFinalizerCore(__state, __exception);\n            PumpIdleSafe();",
     "early return skips the per-frame pump"),
    ("M8", "S", TAKE, "var a = Interlocked.Exchange(ref _pendingArchive, null);",
     "pump takes the archive but never runs it"),
]


def run_guard(st, wt):
    with tempfile.TemporaryDirectory() as d:
        s, w = Path(d) / "JawaBenchTpsSampler.cs", Path(d) / "JawaBenchTpsWriter.cs"
        s.write_text(st, encoding="utf-8")
        w.write_text(wt, encoding="utf-8")
        G.SAMPLER, G.WRITER = s, w
        G.fails.clear()
        out = io.StringIO()
        with redirect_stdout(out):
            rc = G.main()
        return rc, out.getvalue()


def main():
    st0 = (G.SRC / "JawaBenchTpsSampler.cs").read_text(encoding="utf-8")
    wt0 = (G.SRC / "JawaBenchTpsWriter.cs").read_text(encoding="utf-8")
    bad = []
    rc, out = run_guard(st0, wt0)
    print("baseline: rc=%d %s" % (rc, out.strip().splitlines()[0] if out.strip() else ""))
    if rc != 0:
        bad.append("baseline (unmutated) is red")
    for mid, f, old, new, what in MUTANTS:
        src = st0 if f == "S" else wt0
        if src.count(old) != 1:
            bad.append("%s anchor found %d times (must be 1): %r" % (mid, src.count(old), old[:60]))
            continue
        mutated = src.replace(old, new)
        rc, out = run_guard(mutated if f == "S" else st0, mutated if f == "W" else wt0)
        first = next((l for l in out.splitlines() if l.startswith("FAIL")), out.strip()[:120])
        print("%s %s: rc=%d  %s" % (mid, "CAUGHT" if rc == 1 else "MISSED", rc, what))
        print("    " + first[:200])
        if rc != 1:
            bad.append("%s not caught: %s" % (mid, what))
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print("PASS: baseline green, %d/%d mutants caught" % (len(MUTANTS), len(MUTANTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
