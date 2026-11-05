#!/usr/bin/env python3
"""selftest_sarlacc_fuzz_interop_marker.py -- NIGHTLY_COP_FIX_RED_CAHLTS_WGAG guard.

run_selftests.py reruns a red whose output carries INTEROP_DROP ("UtilAcceptVsock": WSL dropped the launch of a Windows exe,
nothing was measured). selftest_sarlacc_pit_sizes.py runs the kernel fuzz as a child and reported only the child's stdout
tail, so a dropped dotnet.exe launch (marker on the child's STDERR) reached the nightly as a plain red, never rerun.
This test fakes that child (rc 1, staging noise on stdout, the marker on stderr) and requires the marker in the test's
own output, where the runner looks. No Windows, no build.
    python3 src/RimStarWars/SWBestiary/selftest_sarlacc_fuzz_interop_marker.py
"""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import run_selftests  # noqa: E402

MARKER = run_selftests.INTEROP_DROP
STDOUT = "staging x -> D:\\ClaudeWork\\rimmandrake\\build\\SWBestiaryFuzzSelfTest\n" + "".join(
    "  src/RimStarWars/SWBestiary/Source/%s/Kernel/\n" % d for d in ("JawaIkee", "Livestock", "BeastMechanics"))
STDERR = "<3>WSL (123) ERROR: UtilAcceptVsock:271: accept4 failed 110\n"


def load():
    spec = importlib.util.spec_from_file_location("sarlacc_pit_sizes", os.path.join(HERE, "selftest_sarlacc_pit_sizes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_with_fake_fuzz(mod, stdout, stderr, rc):
    real = subprocess.run
    seen = []

    def fake(args, *a, **kw):
        if any("selftest_swbestiary_fuzz.py" in str(x) for x in (args if isinstance(args, (list, tuple)) else [args])):
            seen.append(args)
            return subprocess.CompletedProcess(args, rc, stdout, stderr)
        return real(args, *a, **kw)

    buf = io.StringIO()
    subprocess.run = fake
    try:
        with contextlib.redirect_stdout(buf):
            got = mod.main([])
    finally:
        subprocess.run = real
    return got, buf.getvalue(), seen


def main():
    fails = []
    mod = load()
    rc, out, seen = run_with_fake_fuzz(mod, STDOUT, STDERR, 1)
    if not seen:
        fails.append("the fake fuzz child was never called: the test no longer runs selftest_swbestiary_fuzz.py via subprocess.run")
    if rc == 0:
        fails.append("a failed fuzz child (rc 1) still reported OK")
    if MARKER not in out:
        fails.append("a dropped interop launch (%s on the child's stderr) is not in the test's output, so run_selftests "
                     "cannot rerun it: %r" % (MARKER, out[-400:]))
    # sanity: a plain red with no marker must not invent one
    _, out2, _ = run_with_fake_fuzz(mod, STDOUT + "fuzz sarlacc: 10 cases, 40 steps, 0.01s, 3 failures\n", "", 1)
    if MARKER in out2:
        fails.append("the marker appeared in output of a run whose child never printed it")
    for f in fails:
        print("FAIL " + f)
    print("selftest_sarlacc_fuzz_interop_marker: %s" % ("OK" if not fails else "%d FAILURES" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
