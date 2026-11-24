#!/usr/bin/env python3
"""Selftest: the PRODUCTION game-health core (JawaBenchHealthCore.cs) built and unit-tested offline.

Metrics tps.frame-hist, tps.log-counts, tps.bridge-occupancy, tps.capability-inventory, opt.profiler (with the merged
opt.own-counters preset) and spike.gc-timing (design/RimMandrake/game_health_record.md). Builds
bridgetools/HealthSelfTest (net8.0, no RimWorld references) through winbuild staging and runs its unit group:
status words (unavailable is never zero), switches, histogram merge (never averaged p99), Verse.Log cap wording,
occupancy interval union and queue-delay bound, recorder classification, GC coincidence with base rate, profiler
allowlist/expiry/recursion rules. Also checks the companion's frame-hist arm and load wiring.

Without dotnet.exe this FAILS as UNMEASURED (pass --no-cs to accept that). No game, no bridge.
Run: python3 src/RimMandrake/Utils/selftest_health_core.py
"""
import os
from pathlib import Path
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
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
    if not any(os.path.exists(c) for c in ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]):
        print("FAIL health metrics core UNMEASURED: no dotnet.exe on this machine (pass --no-cs to accept)")
        return 1
    import winbuild
    proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "HealthSelfTest")
    rc, rec = winbuild.stage_build(os.path.join(proj, "HealthSelfTest.csproj"), stage_name="HealthSelfTest")
    if rc:
        print("FAIL harness build FAILED (rc %s)" % rc)
        return 1
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\HealthSelfTest.dll"
    p = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d/Luke/dev")
    lines = [ln.strip() for ln in p.stdout.splitlines() if ln.startswith("U ")]
    count = [ln for ln in p.stdout.splitlines() if ln.startswith("U-count ")]
    bad = [ln for ln in lines if " FAIL" in ln]
    for ln in lines:
        print(("ok   " if " ok" in ln and " FAIL" not in ln else "FAIL ") + ln[2:])
    want = int(count[0].split()[1]) if count else -1
    if want != len(lines) or want < 50:
        print("FAIL unit count: printed %d, declared %s (expected >= 50) -- the harness did not run whole: %s"
              % (len(lines), want, p.stderr[-400:]))
        return 1
    print("health metrics core: %d/%d passed" % (len(lines) - len(bad), len(lines)))
    return 1 if bad or p.returncode or not wiring_ok else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
