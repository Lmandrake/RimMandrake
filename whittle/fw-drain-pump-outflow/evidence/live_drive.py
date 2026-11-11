"""WSL orchestration after published deploy and offline GREEN. Always stop/stamp/release."""
import json
import os
from pathlib import Path
import shutil
import hashlib
import subprocess
import time
import traceback

here = Path(__file__).resolve().parent
root = here.parents[2]
raw = Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/pump-outflow-raw')
log = Path('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log')
tier = 'mods__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_hugethings__mandrake_rm_patches'
os.environ['RIMFLOW_SEAT'] = 'BENCH'
record = dict(started=time.time(), status='FAIL', commands=[])

def win(path):
    return subprocess.check_output(['wslpath', '-w', str(path)], text=True).strip()

def run(name, command, timeout=600):
    assert not (here / (name + '_command.json')).exists(), 'preserve prior invocation'
    start = time.time()
    with (here / (name + '_stdout.txt')).open('wb') as out, (here / (name + '_stderr.txt')).open('wb') as err:
        proc = subprocess.run(command, cwd=root, env=dict(os.environ, TMPDIR='/home/mandrake/.seat-tmp/fw-pump-outflow'), stdout=out, stderr=err, timeout=timeout)
    receipt = dict(command=command, started=start, elapsed=time.time() - start, returncode=proc.returncode)
    (here / (name + '_command.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    record['commands'].append(receipt)
    if proc.returncode:
        raise RuntimeError(name + ' returned ' + str(proc.returncode))

def scan(name):
    target = raw / ('Player_' + name + '.log')
    assert not target.exists()
    shutil.copy2(log, target)
    lines = target.read_text(encoding='utf-8-sig', errors='replace').splitlines()
    patterns = ('Exception', 'Config error', 'Could not resolve', 'Error in ', 'Error while', 'Failed to')
    hits = [line for line in lines if any(word in line for word in patterns)]
    receipt = dict(time=time.time(), raw_path=str(target), sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                   patterns=patterns, hits=hits, first_exception=next((line for line in lines if 'Exception' in line), None))
    (here / ('log_' + name + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    assert not hits, 'first exception/config diagnostics require investigation'

try:
    run('game_loading', ['./game', '--why', 'FW drain pump outflow: offline proof and deployment verified', 'loading'])
    run('launch', ['python.exe', win(here / 'launch_game.py')])
    run('census', ['python.exe', win(here / 'live_census.py')])
    run('preflight_live', ['python3', 'src/RimMandrake/Utils/preflight_bridge.py', '--tier', 'quicktest', '--modset', tier, '--deep', '--live', '--seat', 'BENCH', '--json', str(here / 'preflight_live.json')])
    scan('loaded')
    run('game_up', ['./game', '--why', 'FW drain pump outflow: fresh process, actual ordered list and live preflight GREEN', 'up'])
    run('scene', ['python.exe', win(root / 'src/RimMandrake/FlowWorks/northstar/pump_outflow_live.py'), '--out', win(here / 'live_scene.json')], 900)
    scan('after_scene')
    record['status'] = 'PASS'
except BaseException as exc:
    record['error'] = repr(exc)
    record['traceback'] = traceback.format_exc()
finally:
    errors = []
    for name, command in (
        ('shutdown', ['python.exe', win(here / 'stop_game.py')]),
        ('game_down', ['./game', '--why', 'FW drain pump outflow: restoration ended; release immediately', 'down']),
        ('bridge_release', ['python3', 'src/RimMandrake/rimflow/cli.py', 'bridge', 'release']),
        ('bridge_final', ['python3', 'src/RimMandrake/rimflow/cli.py', 'bridge', 'who']),
        ('game_final', ['./game'])):
        try:
            run(name, command, 180)
        except BaseException as exc:
            errors.append(name + ': ' + repr(exc))
    record['cleanup_errors'] = errors
    text = (here / 'bridge_final_stdout.txt').read_text() if (here / 'bridge_final_stdout.txt').exists() else ''
    record['both_locks_free'] = 'driver lock: FREE' in text and 'bridge FREE' in text
    if errors or not record['both_locks_free']:
        record['status'] = 'FAIL'
    record['finished'] = time.time()
    (here / 'live_drive.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))
raise SystemExit(0 if record['status'] == 'PASS' else 1)
