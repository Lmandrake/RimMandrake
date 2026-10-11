#!/usr/bin/env python3
"""selftest_atmosphericbase_kernel.py -- build and run the C# kernel selftest of mandrake.rm.atmosphericbase.

    python3 src/RimMandrake/AtmosphericBase/selftest_atmosphericbase_kernel.py   (exit 0 = clean)

Source/SelfTest/Program.cs compiles the REAL RM_AtmosphericKernel.cs and RM_GlowAccess.cs against the shipped
Assembly-CSharp: the hard exclusion list, and snapshot / drive / release over the real CompGlower override fields.
dotnet.exe is Windows-native, so the project and the src tree are staged by Utils/selftest_winstage.py and run with
`dotnet run`. Phase 2 adds the scheme kernel, the change tracker, and the shipped scheme Defs read off disk. No dotnet.exe (the Mac) -> exits 2 saying UNMEASURED; that is neither a pass nor a fail.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
CSPROJ = os.path.join(HERE, "Source", "SelfTest", "RimMandrakeAtmosphericBase.SelfTest.csproj")
DOTNET = ("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe")


def main():
    dotnet = next((c for c in DOTNET if os.path.exists(c)), None)
    if dotnet is None:
        print("UNMEASURED: dotnet.exe not found; the C# kernel selftest needs the Windows-side .NET SDK")
        return 2
    # selftest_winstage stages the project AND the whole src tree (the Phase 2 checks read the shipped
    # Defs/RM_AtmosphericSchemes.xml by walking up from the exe), from an ext4 clone or the /mnt tree alike.
    from selftest_winstage import windows_project_path
    win = windows_project_path(CSPROJ)
    r = subprocess.run([dotnet, "run", "--project", win, "-c", "Release"], capture_output=True, text=True)
    sys.stdout.write(r.stdout.replace("\r\n", "\n"))
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
