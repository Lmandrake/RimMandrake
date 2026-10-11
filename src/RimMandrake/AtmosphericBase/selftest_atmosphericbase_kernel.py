#!/usr/bin/env python3
"""selftest_atmosphericbase_kernel.py -- build and run the C# kernel selftest of mandrake.rm.atmosphericbase.

    python3 src/RimMandrake/AtmosphericBase/selftest_atmosphericbase_kernel.py   (exit 0 = clean)

Source/SelfTest/Program.cs compiles the REAL RM_AtmosphericKernel.cs and RM_GlowAccess.cs against the shipped
Assembly-CSharp: the hard exclusion list, and snapshot / drive / release over the real CompGlower override fields.
dotnet.exe is Windows-native, so the project is staged by winbuild.py (D:\\Luke\\dev\\_rmbuild\\AtmosphericBase) and the
exe run from there. No dotnet.exe (the Mac) -> exits 2 saying UNMEASURED; that is neither a pass nor a fail.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REL = "src/RimMandrake/AtmosphericBase/Source/SelfTest/RimMandrakeAtmosphericBase.SelfTest.csproj"
BUILD_ROOT = os.environ.get("WINBUILD_ROOT", "/mnt/d/Luke/dev/_rmbuild")
EXE = os.path.join(BUILD_ROOT, "AtmosphericBase", "src", "RimMandrake", "AtmosphericBase", "Source", "SelfTest",
                   "bin", "Release", "net472", "RimMandrakeAtmosphericBase.SelfTest.exe")


def main():
    if not any(os.path.exists(c) for c in ("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe")):
        print("UNMEASURED: dotnet.exe not found; the C# kernel selftest needs the Windows-side .NET SDK")
        return 2
    b = subprocess.run([sys.executable, os.path.join(ROOT, "src", "RimMandrake", "Utils", "winbuild.py"), REL],
                       cwd=ROOT, capture_output=True, text=True)
    if b.returncode != 0 or not os.path.isfile(EXE):
        print(b.stdout[-3000:], b.stderr[-2000:])
        print("FAIL  the selftest project did not build")
        return 1
    r = subprocess.run([EXE], capture_output=True, text=True)
    sys.stdout.write(r.stdout.replace("\r\n", "\n"))
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
