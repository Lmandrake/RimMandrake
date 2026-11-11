"""Replay the actual pre-compatibility production helper against a GSS-only bridge double."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
from unittest import mock

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / 'src/RimMandrake/GimmeSomeSlack'))
import selftest_gss_kinetic_sway as T

rel = 'src/RimMandrake/GimmeSomeSlack/validation_aerial.py'
data = subprocess.check_output(['git', 'show', '913a415fdf:' + rel], cwd=root)
raw = Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/kinetic-sway-raw')
snapshot = raw / 'generic_missing_mod_source.py.txt'
assert not snapshot.exists()
snapshot.write_bytes(data)
old = types.ModuleType('old_generic_aerial')
old.__file__ = str(root / rel)  # dependencies resolve in this clone; the executed module text is exactly git-show bytes
exec(compile(data, str(snapshot), 'exec'), old.__dict__)
bridge, rows = T.Bridge(registered_available=False), []
with mock.patch.object(old, '_scene_pair', side_effect=bridge.scene):
    old.kinetic_sway_rows(bridge, rows)
print(json.dumps(dict(commit='913a415fdf', source_sha256=hashlib.sha256(data).hexdigest(),
                     mode='generic default with no registered KineticArms definition', rows=rows, calls=bridge.calls), indent=2))
assert [r['status'] for r in rows] == ['FAIL', 'FAIL']
assert any(isinstance(c, str) and c.endswith(',RM_Repulse_Palm') for c in bridge.calls)
print('RED: generic GSS-only default must pass with the synthetic token; pre-fix production helper fails both rows')
sys.exit(1)
