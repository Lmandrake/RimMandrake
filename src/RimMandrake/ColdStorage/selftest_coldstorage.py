#!/usr/bin/env python3
"""selftest_coldstorage.py -- build and run the C# selftest of the cold storage engine (mandrake.rm.coldstorage).

    python3 src/RimMandrake/ColdStorage/selftest_coldstorage.py   (exit 0 = clean)

Source/SelfTest/Program.cs compiles the REAL Source/Kernel/ColdStorageKernel.cs and checks it against the shipped
Assembly-CSharp's GenTemperature.RotRateAtTemperature: rot per tick for each unit type, the temperature an item
on a unit reads, and every engine switch off giving vanilla rot at room temperature
(COLD_STORAGE_ENGINE_BUILD_CLIMATE_COMP). dotnet.exe is Windows-native, so the project is staged on D: by
Utils/winbuild.stage_build and run with `dotnet run --no-build`. No dotnet.exe -> exit 2, UNMEASURED.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
CSPROJ = os.path.join(HERE, "Source", "SelfTest", "RimMandrakeColdStorage.SelfTest.csproj")
DOTNET = ("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe")


def main():
    dotnet = next((c for c in DOTNET if os.path.exists(c)), None)
    if dotnet is None:
        print("UNMEASURED: dotnet.exe not found; the C# selftest needs the Windows-side .NET SDK")
        return 2
    import winbuild
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SelfTest_coldstorage")
    if rc:
        print("selftest build FAILED")
        return rc
    r = subprocess.run([dotnet, "run", "--project", winbuild.staged_win(rec, CSPROJ), "-c", "Release", "--no-build"],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout.replace("\r\n", "\n"))
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
