"""Own one Steam launch, production proof, restoration, shutdown and immediate release."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/restring-live-raw')
TIER = 'mods__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_hugethings__mandrake_rm_patches'
sys.path.insert(0, str(ROOT / 'src/RimMandrake/Utils'))
import game_paths as GP


def win(path):
    return subprocess.check_output(['wslpath', '-w', str(path)], text=True).strip()


def main(label):
    path = HERE / (label + '_session.json')
    assert not path.exists(), 'Preserve attempts'
    result = dict(started=time.time(), status='FAIL', commands=[])

    def command(argv, name, timeout=600, required=True):
        started = time.time()
        with (RAW / (label + '_' + name + '.stdout.txt')).open('wb') as out, (RAW / (label + '_' + name + '.stderr.txt')).open('wb') as err:
            p = subprocess.run(argv, cwd=ROOT, stdout=out, stderr=err, timeout=timeout, check=False)
        result['commands'].append(dict(command=argv, name=name, returncode=p.returncode, started=started, finished=time.time()))
        path.write_text(json.dumps(result, indent=2) + '\n')
        print(name, p.returncode, flush=True)
        if required and p.returncode:
            raise RuntimeError(name + ' failed ' + str(p.returncode))

    def scan(name):
        copy = RAW / (label + '_Player_' + name + '.log')
        shutil.copy2(GP.PLAYER_LOG, copy)
        lines = copy.read_text(encoding='utf-8-sig', errors='replace').splitlines()
        needles = ('Exception', 'Config error', 'Could not resolve', 'Error in ', 'Error while', 'Failed to',
                   'Recovered from incompatible', 'Resetting mods config', 'Reached max messages limit')
        hits = [s for s in lines if any(n in s for n in needles)]
        report = dict(path=str(copy), sha256=hashlib.sha256(copy.read_bytes()).hexdigest(), bytes=copy.stat().st_size, needles=needles, hits=hits)
        (HERE / (label + '_log_' + name + '.json')).write_text(json.dumps(report, indent=2) + '\n')
        return hits

    try:
        command(['./game', '--why', 'FW drain restring controlled Steam launch', 'loading'], 'stamp_loading', required=False)
        command(['python3', str(HERE / 'control_session.py'), 'launch'], 'launch')
        command(['./game'], 'measured_state')
        command(['python.exe', win(HERE / 'live_census.py'), label], 'census')
        command(['python3', 'src/RimMandrake/Utils/preflight_bridge.py', '--tier', 'quicktest', '--modset', TIER,
                 '--deep', '--live', '--seat', 'CODEX_ARCHMAGI_FWDRAIN', '--json', str(HERE / (label + '_preflight_live.json'))], 'preflight_live')
        assert not scan('loaded'), 'Investigate fresh load diagnostics'
        command(['./game', '--why', 'FW drain restring fresh live preflight GREEN', 'up'], 'stamp_up', required=False)
        command(['python.exe', win(HERE / 'live_guard.py'), label], 'guard', timeout=1500)
        result['status'] = 'PASS'
    except BaseException as exc:
        result['error'] = repr(exc)
    finally:
        try:
            scan('final')
        except BaseException as exc:
            result.setdefault('cleanup_errors', []).append('final log ' + repr(exc))
        for argv, name in [
            (['python3', str(HERE / 'control_session.py'), 'stop'], 'stop'),
            (['./game', '--why', 'FW drain restring proof ended and saved scene restored', 'down'], 'stamp_down'),
            (['python3', 'src/RimMandrake/rimflow/cli.py', 'bridge', 'release'], 'release'),
            (['python3', 'src/RimMandrake/rimflow/cli.py', 'bridge', 'who'], 'free'),
            (['./game'], 'measured_down'),
        ]:
            try:
                command(argv, name, timeout=180)
            except BaseException as exc:
                result.setdefault('cleanup_errors', []).append(name + ' ' + repr(exc))
        free = (RAW / (label + '_free.stdout.txt')).read_text()
        result['bridge_and_host_free'] = 'driver lock: FREE' in free and 'bridge FREE' in free
        if result.get('cleanup_errors') or not result['bridge_and_host_free']:
            result['status'] = 'FAIL'
        result['finished'] = time.time()
        path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
