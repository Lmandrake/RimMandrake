#!/usr/bin/env python3
"""Offline kernel selftest for Kinetic Arms (RM_KineticMath, KA-01..KA-13).

Runs Source/SelfTest (net8.0, compiles the production RM_KineticMath.cs). dotnet.exe is Windows-native and
cannot build from an ext4 clone, so the two source files are staged into D:\\ClaudeWork\\rimmandrake\\build\\KineticArmsSelfTest
first (same staging root as winbuild.py).

    python3 src/RimMandrake/KineticArms/selftest_kineticarms_kernel.py
"""
# selftest-timeout: 300
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import fcntl
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = os.environ.get("WINBUILD_ROOT", rm_str("build")) + "/KineticArmsSelfTest"
DOTNET = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]


def win(p):
    p = os.path.abspath(p)
    return "%s:\\%s" % (p[5].upper(), p[7:].replace("/", "\\"))


def main():
    dotnet = next((d for d in DOTNET if os.path.isfile(d)), None)
    if dotnet is None or not os.path.isdir(os.path.dirname(STAGE)):
        print("UNMEASURED: no Windows dotnet.exe / D: staging root on this machine")
        return 1
    os.makedirs(os.path.join(STAGE, "SelfTest"), exist_ok=True)
    shutil.copy2(os.path.join(HERE, "Source", "RM_KineticMath.cs"), os.path.join(STAGE, "RM_KineticMath.cs"))
    for f in ("Program.cs", "RimMandrakeKineticArms.SelfTest.csproj"):
        shutil.copy2(os.path.join(HERE, "Source", "SelfTest", f), os.path.join(STAGE, "SelfTest", f))
    with open(os.path.join(tempfile.gettempdir(), "kineticarms_selftest.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        r = subprocess.run([dotnet, "run", "--project", win(os.path.join(STAGE, "SelfTest",
                            "RimMandrakeKineticArms.SelfTest.csproj")), "-c", "Release"],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
    out = (r.stdout or "").replace("\r", "")
    print(out.strip().splitlines()[-1] if r.returncode == 0 and out.strip() else out + (r.stderr or ""))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
