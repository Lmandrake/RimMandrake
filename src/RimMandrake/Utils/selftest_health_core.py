#!/usr/bin/env python3
"""Selftest: the PRODUCTION game-health core (JawaBenchHealthCore.cs) built and unit-tested offline.

Metrics tps.frame-hist, tps.log-counts and opt.profiler (with the merged opt.own-counters preset)
(design/RimMandrake/game_health_record.md). Builds bridgetools/HealthSelfTest (net8.0, no RimWorld references)
through winbuild staging and runs its unit group: status words (unavailable is never zero), switches, histogram
merge (never averaged p99), Verse.Log cap wording, profiler allowlist/expiry/recursion rules. Also checks the
companion's frame-hist arm and load wiring.

Without dotnet.exe this FAILS as UNMEASURED (pass --no-cs to accept that). No game, no bridge.
Run: python3 src/RimMandrake/Utils/selftest_health_core.py
"""
import os
from pathlib import Path
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# The Check(...) calls in bridgetools/HealthSelfTest/Program.cs (counted 2026-11-25 after the three metrics with no
# reader were cut, HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP). Fewer printed means the harness did not run whole.
MIN_UNITS = 45
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)


def frame_hist_wiring():
    companion = Path(REPO) / "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchHealth.cs"
    source = companion.read_text(encoding="utf-8")
    arm = source.split("internal static string ArmNow(", 1)[1].split("internal static void Disarm(", 1)[0]
    root = source.split("private static void RootPrefix(", 1)[1].split("internal static void CloseWindow(", 1)[0]
    before_sample, _, sample = root.partition("if (game != null && ReferenceEquals(game, _lastFrameGame))")
    recording, _, after_sample = sample.partition("}")
    checks = (
        ("arm_starts_fresh_histograms", "old frames survive arm in the session or minute windows",
         all(reset in arm for reset in ("CloseWindow(nowS);", "Session = new H.FrameHist();", "Ring = new H.HistRing(240);"))),
        ("frame_hist_skips_load_intervals", "Root.Update adds load intervals to both histograms",
         all(guard in before_sample for guard in ("Current.ProgramState != ProgramState.Playing", "game.World == null",
                                                 "LongEventHandler.ShouldWaitForEvent", "LongEventHandler.AnyEventNowOrWaiting)) game = null;"))
         and "Window.Add(ms); Session.Add(ms);" in recording and "_lastFrameGame = game;" in after_sample),
    )
    for name, reason, ok in checks:
        print(f"ok   {name}" if ok else f"FAIL {name}: {reason}")
    return all(ok for _, _, ok in checks)


def main(argv):
    wiring_ok = frame_hist_wiring()
    if "--no-cs" in argv:
        print("health metrics core: SKIPPED by --no-cs")
        return 0 if wiring_ok else 1
    import winbuild
    try:
        dotnet = winbuild.dotnet_exe()      # the one discovery rule (WINBUILD_DOTNET, any Windows user, Program Files)
    except SystemExit as e:
        print("FAIL health metrics core UNMEASURED: %s (pass --no-cs to accept)" % e)
        return 1
    proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "HealthSelfTest")
    rc, rec = winbuild.stage_build(os.path.join(proj, "HealthSelfTest.csproj"), stage_name="HealthSelfTest")
    if rc:
        print("FAIL harness build FAILED (rc %s)" % rc)
        return 1
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\HealthSelfTest.dll"
    os.makedirs(winbuild.BUILD_ROOT, exist_ok=True)
    p = winbuild.run_interop_captured([dotnet, dll], capture_output=True, text=True, cwd=winbuild.BUILD_ROOT)
    lines = [ln.strip() for ln in p.stdout.splitlines() if ln.startswith("U ")]
    count = [ln for ln in p.stdout.splitlines() if ln.startswith("U-count ")]
    bad = [ln for ln in lines if " FAIL" in ln]
    for ln in lines:
        print(("ok   " if " ok" in ln and " FAIL" not in ln else "FAIL ") + ln[2:])
    want = int(count[0].split()[1]) if count else -1
    if want != len(lines) or want < MIN_UNITS:
        print("FAIL unit count: printed %d, declared %s (expected >= %d) -- the harness did not run whole: %s"
              % (len(lines), want, MIN_UNITS, p.stderr[-400:]))
        return 1
    print("health metrics core: %d/%d passed" % (len(lines) - len(bad), len(lines)))
    return 1 if bad or p.returncode or not wiring_ok else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
