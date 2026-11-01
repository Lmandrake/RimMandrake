#!/usr/bin/env python3
"""selftest_wasterun_kernel.py -- build and run the C# kernel selftest of mandrake.rut.wasterun.

    python3 src/RimUtinni/WasteRun/selftest_wasterun_kernel.py   (exit 0 = clean)

Source/SelfTest/Program.cs compiles the REAL WasteRunKernel.cs. dotnet.exe is Windows-native, so the project and
the src tree are staged by Utils/selftest_winstage.py. No dotnet.exe -> exits 2 saying UNMEASURED; neither pass nor fail.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
CSPROJ = os.path.join(HERE, "Source", "SelfTest", "WasteRunKernel.SelfTest.csproj")
DOTNET = ("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe")


def main():
    dotnet = next((c for c in DOTNET if os.path.exists(c)), None)
    if dotnet is None:
        print("UNMEASURED: dotnet.exe not found; the C# kernel selftest needs the Windows-side .NET SDK")
        return 2
    from selftest_winstage import windows_project_path
    win = windows_project_path(CSPROJ)
    r = subprocess.run([dotnet, "run", "--project", win, "-c", "Release"], capture_output=True, text=True)
    sys.stdout.write(r.stdout.replace("\r\n", "\n"))
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
