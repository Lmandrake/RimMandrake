"""Run the production launcher inside a guarded disposable saved scene.

Windows Python owns the bridge. The parent owns Steam lifecycle and bridge release.
Every earlier attempt keeps its own result and raw production output directory.
"""
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for directory in (ROOT / 'src/RimMandrake/Utils', ROOT / 'src/RimMandrake/Utils/modcheck',
                  ROOT / 'src/RimMandrake/GimmeSomeSlack'):
    sys.path.insert(0, str(directory))
import validation_aerial as A
import test_site_saves as T
from game_paths import SAVES, LOCALLOW

RAW = Path('D:/ClaudeWork/rimmandrake/codex_wsl/fw-drain/restring-live-raw')
SETTINGS = ('RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings',
            'RimMandrake.GimmeSomeSlack.Aerial.AerialSettings')
RECT = '86,130,52,72'
PRISON = 'RimMandrake.FlowWorks.RM_PitPrisonProof'


def require(ok, reason):
    if not ok:
        raise AssertionError(reason)


def run(label):
    path = RAW / (label + '_guard.json')
    require(not path.exists(), 'preserve prior attempt')
    result = dict(started=time.time(), status='FAIL', calls=[], cleanup_errors=[])
    result['script_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (Path(__file__),
                                         ROOT / 'src/RimMandrake/GimmeSomeSlack/restring_style_proof.py',
                                         ROOT / 'src/RimMandrake/GimmeSomeSlack/validation_aerial.py',
                                         ROOT / 'src/RimMandrake/GimmeSomeSlack/validation.py')}
    B = A.A()
    name, baseline = None, None
    settings, debug = {}, {}
    difficulty = None
    begin_hash = None
    production_finished = True
    config = Path(LOCALLOW) / 'Config'
    config_before = {p.name: p.read_bytes() for p in config.glob('*') if p.is_file() and 'gimmesomeslack' in p.name.lower()}
    saves = Path(SAVES)
    original_saves = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in saves.glob('*.rws')}
    result['saves_before'] = original_saves
    result['config_before'] = {n: hashlib.sha256(b).hexdigest() for n,b in config_before.items()}

    def persist():
        path.write_text(json.dumps(result, indent=2, default=str), encoding='utf-8')

    def call(tool, **kw):
        r = B.call(tool, **kw)
        result['calls'].append(dict(tool=tool, args=kw, result=r))
        persist()
        require(isinstance(r, dict) and r.get('success') is not False, str((tool, r)))
        return r

    def settings_read(typ):
        leaf = typ.rsplit('.', 1)[-1]
        source = ROOT / 'src/RimMandrake/GimmeSomeSlack/Source'
        source = source / ('GimmeSomeSlackMod.cs' if leaf == 'GimmeSomeSlackSettings' else 'Aerial/AerialSettings.cs')
        text = source.read_text(encoding='utf-8-sig')
        start = text.index('public class ' + leaf + ' : ModSettings')
        end = text.find('\n    public class ', start + 1)
        section = text[start:end] if end >= 0 else text[start:]
        fields = re.findall(r'^\s*public static [\w<>]+\s+(\w+)\s*(?:=(?!>)|;)', section, re.M)
        require(fields and len(fields) == len(set(fields)), 'settings source field census')
        values = {}
        # Individual static gets avoid the list tool's instance lookup, which logs on a second settings class.
        for field in fields:
            r = call('jawa/mod_settings_field', typeName=typ, action='get', field=field)
            require(r.get('success') is True and r.get('fieldKind') == 'static' and r.get('field') == field, 'settings static readback')
            values[field] = r['value']
        return values

    def flags():
        return {f['name']: f['value'] for f in call('jawa/debug_settings', action='list')['fields']}

    def scene():
        rect = call('jawa/static_call', type=PRISON, method='Rect', args=RECT)['result']
        require(str(rect).startswith('RECT '), 'rectangle state unreadable')
        pawns = call('jawa/list_pawns', includeHealth=True, includeCorpses=True, limit=500)
        require(not pawns.get('truncated') and isinstance(pawns.get('pawns'), list), 'pawn census incomplete')
        site = call('jawa/site_state', rect=RECT)
        info = call('jawa/map_info')
        colonists = B.probe('colonists')
        require(colonists.get('success') is True and colonists.get('pawns'), 'draft/job census unreadable')
        return dict(rect=rect, pawns=pawns['pawns'], jobs=site['pawns'],
                    colonists=colonists, autoHome=site['autoHome'], tick=info['ticksGame'])

    def reload(slot):
        r = T.load_site(call, 'calm', name=slot, check=False)
        require(r.get('verified') is True, 'guarded scene reload failed')
        return r

    def driver_processes():
        script = "Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'python*'} | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress"
        p = subprocess.run(['powershell.exe', '-NoProfile', '-Command', script], capture_output=True, text=True, timeout=60, check=True)
        rows = json.loads(p.stdout) if p.stdout.strip() else []
        rows = rows if isinstance(rows, list) else [rows]
        return [r for r in rows if str(ROOT).lower() in str(r.get('CommandLine', '')).lower() and
                any(name in str(r.get('CommandLine', '')) for name in ('validation_aerial.py', 'restring_style_proof.py'))]

    try:
        for required in ('CANONICAL_ASHKARR_START_2026-09-12.rws',
                         'ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws', T.SITES['calm']['save'] + '.rws'):
            require(required in original_saves, 'protected save absent ' + required)
        result['debug_before'] = debug = flags()
        for typ in SETTINGS:
            settings[typ] = settings_read(typ)
        result['settings_before'] = settings
        result['site'] = T.load_site(call, 'calm')
        require(result['site'].get('verified') is True, 'registered calm site refused')
        result['difficulty_before'] = difficulty = call('jawa/difficulty_tune')['before']
        for flag in ('enableStoryteller', 'enableRandomMentalStates', 'enableRandomDiseases'):
            call('jawa/debug_settings', action='set', field=flag, value=False)
        result['isolation_debug'] = flags()
        require(all(result['isolation_debug'].get(f) is False for f in
                    ('enableStoryteller', 'enableRandomMentalStates', 'enableRandomDiseases')), 'quiet flag readback')
        result['log_start'] = A.V.VC.log_revive(B)
        require(result['log_start']['alive'], 'logging unavailable')
        # Idle wander targets can be reassigned by load-time toil initialization. Prepare a stable held baseline.
        result['prebaseline_colonists'] = B.probe('colonists')
        require(result['prebaseline_colonists'].get('success') is True, 'prebaseline pawn readback')
        for pawn in result['prebaseline_colonists']['pawns']:
            r = B.probe('pawn:%d=draft' % pawn['id'])
            result.setdefault('baseline_parking', []).append(r)
            require(r.get('success') is True, 'baseline parking failed')
        name = 'WHITTLE_Restring_Begin_' + label + '_' + time.strftime('%Y%m%dT%H%M%S')
        backup = RAW / ('saves_before_' + name)
        result['save_backups'] = T.backup_saves(SAVES, str(backup))
        result['snapshot'] = T.save_site(call, name, SAVES)
        begin_hash = result['begin_sha256'] = hashlib.sha256((saves / (name + '.rws')).read_bytes()).hexdigest()
        result['begin_reload'] = reload(name)
        call('rimworld/pause_game', pause=True)
        baseline = result['baseline'] = scene()
        require(all(p.get('drafted') is True for p in baseline['colonists']['pawns']), 'stable held baseline missing')
        result['identity'] = call('jawa/type_probe', typeName='RimMandrake.GimmeSomeSlack.Aerial.CompAerialAnchor')
        dll = ROOT / 'src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll'
        expected = hashlib.sha256(dll.read_bytes()).hexdigest()
        require(result['identity'].get('mvidMatchesFile') is True and
                result['identity'].get('assemblyFileSha256') == expected, 'loaded GSS artifact mismatch')
        result['running'] = call('jawa/running_mods')
        # The proof's first colonist job has free workers, and final reload restores the held baseline.
        for pawn in result['prebaseline_colonists']['pawns']:
            r = B.probe('pawn:%d=undraft' % pawn['id'])
            result.setdefault('workers_released', []).append(r)
            require(r.get('success') is True, 'worker release failed')
        production = [sys.executable, str(ROOT / 'src/RimMandrake/GimmeSomeSlack/restring_style_proof.py'),
                      '--out-dir', str(RAW / label), '--max-seconds', '900']
        result['production_command'] = production
        os.environ['RIMBRIDGE_EVIDENCE_LOG'] = str(RAW / (label + '_bridge_calls.jsonl'))
        persist()
        require(not driver_processes(), 'another production driver is active')
        production_finished = False
        with (RAW / (label + '_launcher_stdout.txt')).open('wb') as out, (RAW / (label + '_launcher_stderr.txt')).open('wb') as err:
            child = subprocess.Popen(production, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                     creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            result['launcher_pid'] = child.pid
            try:
                child.wait(timeout=960)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'], capture_output=True, timeout=30)
                child.wait(timeout=30)
                raise
        result['drivers_after_command'] = driver_processes()
        require(not result['drivers_after_command'], 'production descendant remains active')
        production_finished = True
        result['production_returncode'] = child.returncode
        result['after_proof_tick'] = call('jawa/map_info')['ticksGame']
        require(child.returncode == 0, 'production launcher failed')
        result['status'] = 'PASS'
    except BaseException as exc:
        result['error'] = repr(exc)
    finally:
        if not production_finished:
            try:
                for process in driver_processes():
                    subprocess.run(['taskkill.exe', '/PID', str(process['ProcessId']), '/T', '/F'], capture_output=True, timeout=30, check=True)
                result['drivers_before_restore'] = driver_processes()
                require(not result['drivers_before_restore'], 'driver remains active before restoration')
                production_finished = True
            except BaseException as exc:
                result['cleanup_errors'].append('driver quiescence ' + repr(exc))
        if baseline is not None and production_finished:
            try:
                result['begin_sha256_before_restore'] = hashlib.sha256((saves / (name + '.rws')).read_bytes()).hexdigest()
                require(result['begin_sha256_before_restore'] == begin_hash, 'guarded begin save changed')
                result['restore_load'] = reload(name)
                call('rimworld/pause_game', pause=True)
                for flag in ('enableStoryteller', 'enableRandomMentalStates', 'enableRandomDiseases'):
                    call('jawa/debug_settings', action='set', field=flag, value=False)
                after = result['restored_scene'] = scene()
                require(after == baseline, 'scene/pawn/job/tick state differs from guarded baseline')
            except BaseException as exc:
                result['cleanup_errors'].append('scene ' + repr(exc))
        for typ, want in settings.items():
            try:
                current = settings_read(typ)
                for field, value in want.items():
                    if current.get(field) != value:
                        call('jawa/mod_settings_field', typeName=typ, action='set', field=field, value=value)
                require(settings_read(typ) == want, 'settings restoration mismatch ' + typ)
                result.setdefault('settings_restored', []).append(typ)
            except BaseException as exc:
                result['cleanup_errors'].append('settings ' + repr(exc))
        try:
            # Rebuild cached materials after restoring scalar fields, then verify the fields again.
            for typ in SETTINGS:
                call('jawa/static_call', type=typ, method='Apply', args='')
            for typ, want in settings.items():
                require(settings_read(typ) == want, 'Apply changed restored settings')
            if difficulty is not None:
                r = call('jawa/difficulty_tune', threatScale=difficulty['threatScale'], allowBigThreats=difficulty['allowBigThreats'])
                require(r['after'] == difficulty, 'difficulty restoration mismatch')
            current = flags()
            for field, value in debug.items():
                if current.get(field) != value:
                    call('jawa/debug_settings', action='set', field=field, value=value)
            result['debug_after'] = flags()
            require(result['debug_after'] == debug, 'debug restoration mismatch')
            call('rimworld/pause_game', pause=True)
        except BaseException as exc:
            result['cleanup_errors'].append('controls ' + repr(exc))
        now = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in saves.glob('*.rws')}
        result['saves_after'] = now
        result['changed_existing_saves'] = [p for p,h in original_saves.items() if now.get(p) != h]
        result['new_saves'] = sorted(set(now) - set(original_saves))
        if result['cleanup_errors'] or result['changed_existing_saves']:
            result['status'] = 'FAIL'
        config_after = {p.name: p.read_bytes() for p in config.glob('*') if p.is_file() and 'gimmesomeslack' in p.name.lower()}
        result['config_after'] = {n: hashlib.sha256(b).hexdigest() for n,b in config_after.items()}
        if config_after != config_before:
            result['cleanup_errors'].append('GSS Config files changed on disk')
            for n,b in config_before.items():
                (config / n).write_bytes(b)
            for n in set(config_after) - set(config_before):
                (config / n).unlink()
            result['status'] = 'FAIL'
        result['finished'] = time.time()
        persist()
        B.S.close()
    print(result['status'], result.get('error', ''), 'cleanup', result['cleanup_errors'])
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    label = sys.argv[1]
    require(label.startswith('attempt') and label.isalnum(), 'invalid attempt label')
    sys.exit(run(label))
