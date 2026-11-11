#!/usr/bin/env python3
# selftest-timeout: 240
"""Compile actual production AerialMath and exact AerialProbe explode branch with explicit engine doubles.

This proves parsing, registered lookup dispatch and reply identity offline; no real engine effects.
The ordinary GSS SelfTest separately retains SwitchFlipChecks and AerialSelfTest entry points.
"""
import hashlib
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "Utils"))
import winbuild


def run(source=HERE):
    source = Path(source)
    probe = (source / "Source/Aerial/AerialProbe.cs").read_text()
    start = probe.index('            if (cmd.StartsWith("explode:"))')
    end = probe.index('            if (cmd.StartsWith("set:"))', start)
    branch = probe[start:end]
    start = probe.index('            string cmd = request.')
    end = probe.index('            request = "";', start)
    normalization = probe[start:end]
    harness = (HERE / "Source/SelfTest/ExplodeProbeChecks.cs").read_text()
    math = (source / "Source/Aerial/AerialMath.cs").read_bytes()
    base = Path(winbuild.BUILD_ROOT) / "gss-explode-checks"
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="parse-", dir=base) as directory:
        work = Path(directory)
        (work / "AerialMath.cs").write_bytes(math)
        (work / "Program.cs").write_text(harness.replace("// PRODUCTION_EXPLODE_BRANCH", branch).replace(
            "// PRODUCTION_REQUEST_NORMALIZATION", normalization))
        project = work / "Parse.csproj"
        project.write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType>'
                           '<TargetFramework>net8.0</TargetFramework><ImplicitUsings>disable</ImplicitUsings>'
                           '<Nullable>disable</Nullable></PropertyGroup></Project>')
        print("source=" + str(source), flush=True)
        print("production_math_sha256=" + hashlib.sha256(math).hexdigest(), flush=True)
        print("production_branch_sha256=" + hashlib.sha256(branch.encode()).hexdigest(), flush=True)
        print("production_normalization_sha256=" + hashlib.sha256(normalization.encode()).hexdigest(), flush=True)
        result = winbuild.run_interop_captured([winbuild.dotnet_exe(), "run", "--project", winbuild.win(str(project)),
                                               "-c", "Release"], cwd=str(work), timeout=180,
                                              capture_output=True, text=True)
        print(result.stdout, end="", flush=True)
        print(result.stderr, end="", file=sys.stderr, flush=True)
        return result.returncode


if __name__ == "__main__":
    sys.exit(run())
