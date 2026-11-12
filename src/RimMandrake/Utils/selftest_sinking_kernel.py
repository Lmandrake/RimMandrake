#!/usr/bin/env python3
# selftest-timeout: 600   (winbuild.stage_build + one dotnet.exe run; interop retries as in selftest_ninefold_fuzz.py)
"""Offline selftest of the Sinking (SUMP_SINKING_RITE_BUILD_1, Salvation Rites, src/RimUtinni/Rites), no game. Two parts:

1. KERNEL GUARDS (lint_kernel_guards.kernel_guards): every Source/Kernel/*.cs of Rites stays engine-free and is compiled
   into the mod AND the selftest project, which compiles the production file directly.
2. KERNEL CASES: the selftest exe's `--sinking` run of SinkingKernelTests (one PASS/FAIL line per criterion the kernel
   decides and one per Mod Settings toggle). A SANITY probe fails when the run printed no case at all.

    python3 src/RimMandrake/Utils/selftest_sinking_kernel.py [--out FILE]   (FILE gets the full PASS/FAIL list)

Exits non-zero on any FAIL.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402
from lint_kernel_guards import kernel_guards  # noqa: E402

MOD = os.path.join(REPO, "src", "RimUtinni", "Rites")
SOURCE = os.path.join(MOD, "Source")
SELFTEST = os.path.join(SOURCE, "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrake.Utinni.Rites.SelfTest.csproj")


def main(argv):
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    lines = []
    errs = kernel_guards(MOD, "RimMandrake.Utinni.Rites.csproj", "SelfTest/RimMandrake.Utinni.Rites.SelfTest.csproj", "rites-kernel")
    for e in errs:
        lines.append("FAIL  kernel_guards  " + e)
    if not errs:
        lines.append("PASS  kernel_guards (Source/Kernel engine-free, compiled into the mod and the selftest)")
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SinkingKernelSelfTest", extra_dirs=[SOURCE])
    if rc:
        lines.append("FAIL  selftest build (rc %s)" % rc)
    else:
        dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrake.Utinni.Rites.SelfTest.dll"
        r = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll, "--sinking"], cwd="/mnt/d/Luke/dev",
                                          capture_output=True, text=True)
        got = [ln.rstrip("\r") for ln in (r.stdout or "").splitlines() if ln.strip()]
        lines += got
        cases = [ln for ln in got if re.match(r"^(PASS|FAIL)  sinking/", ln)]
        if not cases:
            lines.append("FAIL  SANITY: the --sinking run printed no case (rc %s) %s" % (r.returncode, (r.stderr or "")[-300:]))
        elif r.returncode != 0 and not any(ln.startswith("FAIL") for ln in cases):
            lines.append("FAIL  the --sinking run exited %s with no FAIL line" % r.returncode)
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
    bad = any(ln.startswith("FAIL") for ln in lines)
    print("%s selftest_sinking_kernel" % ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
