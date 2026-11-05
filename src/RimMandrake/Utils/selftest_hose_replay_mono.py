#!/usr/bin/env python3
# selftest-timeout: 60   (offline: pure Python, no dotnet, no game)
"""Selftest of the hose replay Mono timing lane's checker (`hose_replay.py mono-check`; HOSE_REPLAY_WIRE_MONO_TIMING_LANE).
The committed report Replay/mono_timing.txt (written by `hose_replay.py mono --write`, which needs Windows dotnet.exe and the
game's mono-2.0-bdwgc.dll) must pass the checker; then each way a report can lie is injected into a copy and must FAIL:
a .NET runtime posing as Mono, a Mono DLL that is not the game's, one scenario's fingerprint diverging across runtimes,
a scenario dropped, a scenario not PASS on Mono, a missing time row, and a nonzero Mono exit.
    python3 src/RimMandrake/Utils/selftest_hose_replay_mono.py
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hose_replay  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def main():
    with open(hose_replay.MONO_REPORT, encoding="utf-8") as f:
        text = f.read()
    rc, probs = hose_replay.mono_check_text(text)
    check(rc == 0, "committed %s passes mono-check %s" % (os.path.basename(hose_replay.MONO_REPORT), probs[:3]))
    sc = hose_replay.scenarios()
    check(len(sc) >= 10, "TraceGen.Scenarios read from source: %d (sanity: the parser can see them)" % len(sc))
    first = sc[0]
    bad = {
        "runtime not Mono": re.sub(r"(?m)^MONO_RUNTIME .*$", "MONO_RUNTIME .NET 8.0.29", text),
        "dll not the game's": re.sub(r"(?m)^MONO_DLL .*$", r"MONO_DLL C:\\mono\\bin\\mono-2.0-sgen.dll", text),
        "fingerprint diverges": re.sub(r"(?m)^(SCENARIO %s .*fp_mono=)[0-9a-f]+" % first, r"\g<1>deadbeefdeadbeef", text),
        "scenario dropped": re.sub(r"(?m)^SCENARIO %s .*\n" % first, "", text),
        "scenario FAIL on mono": re.sub(r"(?m)^(SCENARIO %s .*)mono=PASS" % first, r"\g<1>mono=FAIL", text),
        "time row missing": re.sub(r"(?m)^TIME %s +Lay .*\n" % first, "", text),
        "mono exit nonzero": re.sub(r"(?m)^MONO_EXIT .*$", "MONO_EXIT 3", text),
    }
    for what, t in bad.items():
        check(t != text, "injection '%s' changed the report" % what)
        rc_b, probs_b = hose_replay.mono_check_text(t)
        check(rc_b == 1 and probs_b, "mono-check FAILS on '%s' (%s)" % (what, probs_b[:1]))
    print("SELFTEST %s (%d failures)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
