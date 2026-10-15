#!/usr/bin/env python3
"""Wrapper for the Settings kit's offline C# selftest (SETTINGS_SCREEN_KIT_1, SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST):
src/RimMandrake/_Shared/SettingsKit/SelfTest compiles the PRODUCTION SettingsKitCore.cs (no Verse) and checks reset,
search, scope tags, master-switch liveness (chains, several masters, independents, cycles refused) and reset-all.
The Verse-side drawer (greying, the confirmation dialog) is not covered here: that needs the game.

dotnet.exe cannot build from a \\\\wsl.localhost path, so the project is staged on D: by winbuild first.

    python3 src/RimMandrake/Utils/selftest_settings_kit.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(REPO, "src", "RimMandrake", "_Shared", "SettingsKit", "SelfTest",
                      "RimMandrakeSettingsKit.SelfTest.csproj")
DOTNET_CANDIDATES = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]


def main():
    dotnet = next((c for c in DOTNET_CANDIDATES if os.path.isfile(c)), None)
    if dotnet is None:
        sys.exit("dotnet.exe not found at any of %r; UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)
    sys.path.insert(0, HERE)
    import winbuild
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SelfTest_settingskit")
    if rc:
        print("selftest build FAILED")
        sys.exit(rc)
    r = subprocess.run([dotnet, "run", "--project", winbuild.staged_win(rec, CSPROJ), "-c", "Release", "--no-build"],
                       capture_output=True, text=True)
    print(r.stdout, end="")
    if r.stderr.strip():
        print(r.stderr, end="", file=sys.stderr)
    if r.returncode == 0 and "settings kit selftest: PASS" not in r.stdout:
        print("FAIL: exit 0 without the PASS line")
        sys.exit(1)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
