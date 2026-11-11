#!/usr/bin/env python3
# selftest-timeout: 600
"""Compile the production tier adapter/kernel, then check independent policy and complete gate truth tables. L0 only."""
import os
import sys
import hashlib
import json
from pathlib import Path
import subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild


def main():
    relative = "src/RimMandrake/HugeThings/Source/SelfTest/JuvenileTier"
    project = os.path.join(winbuild.ROOT, relative, "JuvenileTier.csproj")
    rc, record = winbuild.stage_build(project, stage_name="HugeThingsJuvenileTierSelfTest")
    if rc:
        return rc
    dll = winbuild.staged_win(record, os.path.dirname(project)) + "\\bin\\Release\\net8.0\\JuvenileTier.dll"
    return winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd=record['stage'], timeout=None)


if __name__ == '__main__':
    if '--child' in sys.argv:
        sys.exit(main())
    # Keep actual process bytes before safely rendering to the UTF8-only shared test runner.
    # This also preserves build chatter which run_selftests suppresses on a successful test.
    child = subprocess.run([sys.executable, __file__, '--child'], capture_output=True)
    raw_dir = os.environ.get('HT_JUVENILE_TEST_RAW')
    streams = {}
    for name, data in [('stdout', child.stdout), ('stderr', child.stderr)]:
        streams[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        if raw_dir:
            folder = Path(raw_dir)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / (name+'.bin')).write_bytes(data)
        rendered = data.decode('utf-8', 'backslashreplace').encode('ascii', 'backslashreplace').decode('ascii')
        print(rendered, end='')
    if raw_dir:
        (Path(raw_dir)/'process.json').write_text(json.dumps({'command': [sys.executable, __file__, '--child'], 'rc': child.returncode, 'streams': streams}, indent=2)+'\n')
    # After invariant-culture repair, our test output must be ASCII. A decode fault cannot become PASS.
    if any(byte>127 for byte in child.stdout+child.stderr):
        print('FAIL non-ASCII test/build output; raw bytes retained')
        sys.exit(3)
    sys.exit(child.returncode)
