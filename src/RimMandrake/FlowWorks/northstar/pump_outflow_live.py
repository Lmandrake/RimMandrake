#!/usr/bin/env python3
"""Focused paused production-draw proof; registered disposable site, explicit restoration.

--selftest checks the actual restoration routine with injected transport failures.
Live requires a held BENCH bridge and the exact published, deployed FlowWorks DLL.
The draw hook bypasses hash scheduling only; source discovery, ports, room, transfer and Running are real.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
UTILS = ROOT / 'src/RimMandrake/Utils'
sys.path.insert(0, str(UTILS))
sys.path.insert(0, str(UTILS / 'modcheck'))
FW = 'RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings'
HS = 'RimMandrake.FlowWorks.Hose.RM_HoseSettings'
PUMP = 'RimMandrake.FlowWorks.LiquidTypes.Building_LiquidPump'
LINE = 'RimMandrake.FlowWorks.Machinery.RM_LineProofs'
NS = 'RimMandrake.FlowWorks.RM_NorthstarProofs'
PRISON = 'RimMandrake.FlowWorks.RM_PitPrisonProof'
RECT = '30,30,28,20'


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def sources(text):
    match = re.search(r'sources=\[([^]]*)\]', text)
    require(match is not None, 'missing sources: ' + text)
    rows = []
    for entry in filter(None, match[1].split(';')):
        xz, amount = entry.split(':')
        rows.append((tuple(map(int, xz.split(','))), int(amount)))
    return rows


def restore_scene(load, rect, setting, flags, set_flag, name, baseline, settings, debug):
    """Discharge each independent debt even if an earlier restore fails."""
    result = {'errors': [], 'settings': []}
    if name and baseline is not None:
        try:
            result['load'] = load(name)
            require(result['load']['verified'], 'baseline load refused')
            result['rect'] = rect()
            require(result['rect'] == baseline, 'restored rectangle differs')
        except Exception as exc:
            result['errors'].append('scene: ' + repr(exc))
    for typ, field, value in settings:
        try:
            setting(typ, field, value)
            after = setting(typ, field)
            result['settings'].append([typ, field, value, after])
            require(after == value, 'setting mismatch ' + field)
        except Exception as exc:
            result['errors'].append('setting: ' + repr(exc))
    try:
        now = flags()
        for key, value in debug.items():
            if now.get(key) != value:
                set_flag(key, value)
        result['debug'] = flags()
        require(result['debug'] == debug, 'debug mismatch')
    except Exception as exc:
        result['errors'].append('debug: ' + repr(exc))
    result['status'] = 'FAIL' if result['errors'] else 'PASS'
    return result


def set_fill(call, water, cell, levels):
    """A whole-notch driver write preserves interior parts; drain first for exact fixture quantities."""
    call('jawa/flowworks_excavation_drive', x=cell[0], z=cell[1], setBodyWaterM=0.0)
    require(water(cell) == 0, 'fixture drain readback')
    if levels:
        call('jawa/flowworks_excavation_drive', x=cell[0], z=cell[1], setBodyWaterM=(levels) * 0.5)
    require(water(cell) == levels * 10000, 'fixture fill readback')


def selftest():
    require(sources('PUMPDRAW sources=[4,5:900;6,7:20000]') == [((4, 5), 900), ((6, 7), 20000)], 'source parser')
    for text in ('', 'sources=[bad]'):
        try:
            sources(text)
        except (AssertionError, ValueError):
            pass
        else:
            raise AssertionError('malformed candidates accepted')
    for failure in ('none', 'load', 'first_setting'):
        state = {('A', 'first'): 'changed', ('A', 'second'): 'changed'}
        debug = {'godMode': True}
        attempted = []
        def load(name):
            attempted.append('load')
            if failure == 'load':
                raise RuntimeError('injected load failure')
            return {'verified': True}
        def setting(typ, field, *value):
            attempted.append(field)
            if value:
                if failure == 'first_setting' and field == 'first':
                    raise RuntimeError('injected setting failure')
                state[(typ, field)] = value[0]
            return state[(typ, field)]
        result = restore_scene(load, lambda: 'same', setting, lambda: dict(debug),
                               lambda k, v: debug.update({k: v}), 'new', 'same',
                               [('A', 'first', 'old'), ('A', 'second', 'old')], {'godMode': False})
        require('second' in attempted and state[('A', 'second')] == 'old' and debug == {'godMode': False}, 'independent debt skipped')
        require(result['status'] == ('PASS' if failure == 'none' else 'FAIL'), 'fault relabelled')
    for refuse_drain in (False, True):
        state = {'dl': 900}
        writes = []
        def call(tool, **kw):
            level = int(round(float(kw['setBodyWaterM']) * 2))
            writes.append(level)
            if level == 0:
                if not refuse_drain:
                    state['dl'] = 0
            else:
                state['dl'] = level * 10000 + state['dl'] % 10000
            return {'success': True}
        try:
            set_fill(call, lambda cell: state['dl'], (40, 41), 2)
            require(not refuse_drain and state['dl'] == 20000 and writes == [0, 2], 'retained-part fixture not reset')
        except AssertionError:
            if not refuse_drain:
                raise
            require(writes == [0], 'bad drain must stop staging')
    print('PASS pump outflow parser and independent restoration failure controls')
    return 0


def live(out):
    import test_site_saves as T
    import validation_core as V
    from game_paths import SAVES
    class Bridge(V.Bridge):
        probe_type = 'RimMandrake.FlowWorks.Hose.HoseProbe'
    B = Bridge()
    result = {'mode': 'live', 'started': time.time(), 'calls': [], 'status': 'FAIL'}
    settings, debug = [], {}
    baseline = None
    name = None
    dev_mode = None
    saves = Path(SAVES)
    saves_before = T.saves_stat(SAVES)
    protected = [p for p in saves.glob('*.rws') if p.name.startswith('CANONICAL_') or p.name in
                 ('ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws', 'WORLDMAP_V1_original.rws')]
    site_file = saves / (T.SITES['calm']['save'] + '.rws')
    require(site_file.is_file(), 'registered original site absent')
    if site_file not in protected:
        protected.append(site_file)
    protected_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    def persist():
        out.write_text(json.dumps(result, indent=2, default=str), encoding='utf-8')
    def call(tool, **kw):
        response = B.call(tool, **kw)
        result['calls'].append({'tool': tool, 'args': kw, 'result': response})
        persist()
        require(isinstance(response, dict) and response.get('success') is not False, str((tool, response)))
        return response
    def sc(typ, method, arg):
        response = call('jawa/static_call', type=typ, method=method, args=arg)
        text = str(response.get('result', ''))
        require(text and not text.startswith('REFUSED'), str(response))
        return text
    def setting(typ, field, *value):
        if value:
            call('jawa/mod_settings_field', typeName=typ, field=field, action='set', value=str(value[0]))
        return call('jawa/mod_settings_field', typeName=typ, field=field, action='get')['value']
    def flags():
        return {row['name']: row['value'] for row in call('jawa/debug_settings', action='list')['fields']}
    def rect():
        return sc(PRISON, 'Rect', RECT)
    def reload(name):
        return T.load_site(call, 'calm', name=name, check=False)
    def hp(command):
        response = B.probe(command)
        result['calls'].append({'probe': command, 'result': response})
        persist()
        require(response.get('success') is True, str(response))
        return response
    def water(cell):
        return int(re.search(r'dl=(\d+)', sc(LINE, 'ProofPitWater', '%d,%d,1,1' % cell))[1])
    def fill(cell, levels):
        set_fill(call, water, cell, levels)
    try:
        result['running'] = call('jawa/running_mods')
        result['identity'] = call('jawa/type_probe', typeName=PUMP)
        expected = hashlib.sha256((ROOT / 'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll').read_bytes()).hexdigest()
        require(result['identity'].get('mvidMatchesFile') is True and result['identity'].get('assemblyFileSha256') == expected, 'loaded DLL identity mismatch')
        debug = flags()
        for typ, field in [(FW, 'depthEngineEnabled'), (FW, 'depthEngineLiveForTests'), (FW, 'liquidPumpEnabled'),
                           (HS, 'enabled'), (HS, 'freeEndRolesEnabled'), (HS, 'hoseHoldsLiquid'), (HS, 'gravityLevellingEnabled'),
                           ('RimMandrake.FlowWorks.Machinery.RM_MachinerySettings', 'lineCrossingRulesEnabled')]:
            settings.append((typ, field, setting(typ, field)))
        require(str(setting('RimMandrake.FlowWorks.Machinery.RM_MachinerySettings', 'lineCrossingRulesEnabled')).lower() == 'true', 'line-crossing rules must stay enabled')
        result['settings_before'] = settings
        result['protected_before'] = protected_hashes
        result['site'] = T.load_site(call, 'calm')
        require(result['site']['verified'], 'registered calm site failed')
        # The original registered site is never saved. Guarded save verifies only one NEW slot changed.
        name = 'WHITTLE_PumpOutflow_Begin_' + time.strftime('%Y%m%dT%H%M%S')
        backup = Path('D:/ClaudeWork/rimmandrake/codex_wsl/fw-drain/pump-outflow-raw') / ('saves_before_' + name)
        result['save_backups'] = {'path': str(backup), 'files': T.backup_saves(SAVES, str(backup))}
        result['snapshot'] = T.save_site(call, name, SAVES)
        require(reload(name)['verified'], 'begin reload failed')
        baseline = rect()
        result['baseline_rect'] = baseline
        call('rimworld/pause_game', pause=True)
        for typ, field, value in [(FW, 'depthEngineEnabled', True), (FW, 'depthEngineLiveForTests', True),
                                  (FW, 'liquidPumpEnabled', True), (HS, 'enabled', True), (HS, 'freeEndRolesEnabled', True),
                                  (HS, 'hoseHoldsLiquid', False), (HS, 'gravityLevellingEnabled', False)]:
            setting(typ, field, value)
            require(str(setting(typ, field)).lower() == str(value).lower(), 'setting readback ' + field)
        call('jawa/set_roof_batch', ops='None:' + RECT)
        call('jawa/destroy_batch', rects=RECT, categories='All')
        sc(NS, 'ProofResetRect', RECT.replace(',', ';'))
        call('jawa/set_terrain_batch', ops='Soil:' + RECT)
        call('jawa/set_fog', action='unfog', rect=RECT)
        for cell in ((40, 41), (40, 39), (52, 40)):
            call('jawa/flowworks_excavation_drive', x=cell[0], z=cell[1], deepenLevels=4, setBodyWaterM=0.0)
        built = call('jawa/build_batch', ops='RM_LiquidPump:40,40;RM_HoseReel:41,41,1', faction='player', wipeExisting=False)
        require(built.get('survived') == 2, 'fixture buildings did not survive')
        call('jawa/map_commit')
        # Keep the hose mouth on ground; the real outlet pours into the adjacent D4 cell.
        route = hp('check:41,41,51,40')
        require(route.get('reason') is None, 'ground outlet route refused: ' + str(route))
        hp('lay:41,41,51,40')
        sc(LINE, 'ProofHoseRole', '41,41;Outflow')
        # Toggle the real CompPowerTrader dev gizmo; no production power predicate is bypassed.
        dev_mode = hp('gizmos:41,41')['devMode']
        hp('devmode:41,41=on')
        call('jawa/debug_settings', action='set', field='godMode', value=True)
        call('jawa/select_things', ids=next(t['id'] for t in call('jawa/list_things', defName='RM_LiquidPump', rect=RECT, limit=5)['things']), jumpCamera=False)
        gizmos = call('rimworld/list_selected_gizmos')
        result['power_gizmos'] = gizmos
        # Exact gizmo contract is read from the response, never invented.
        power_gizmo = next(g for g in gizmos['gizmos'] if 'power' in str(g.get('label', '')).lower() and 'dev' in str(g.get('label', '')).lower())
        call('rimworld/execute_gizmo', gizmoId=power_gizmo.get('gizmoId') or power_gizmo['id'])
        for cell in ((40, 41), (40, 39)):
            fill(cell, 2)
        read = sc(PUMP, 'ProofDrawCycle', '40,40;read')
        ordered = sources(read)
        require(len(ordered) == 2 and 'outflows=[51,40]' in read and 'tankRoom=0' in read and 'hoseNeed=0' in read and 'running=True' in read, 'fixture candidates/port/power mismatch: ' + read)
        first, second = [row[0] for row in ordered]
        result['actual_order'] = ordered
        result['arms'] = []
        for mode in ('full', 'exact', 'off'):
            setting(FW, 'liquidPumpEnabled', True)
            fill(first, 2)
            fill(second, 2)
            fill((52, 40), 0)
            if mode != 'full':
                taken = sc('RimMandrake.FlowWorks.RM_WaterLookProofs', 'ProofWaterLook', 'take:%d;%d;1;1;19100' % first)
                require('took=19100' in taken and water(first) == 900, '900 dL stage failed')
            if mode == 'off':
                setting(FW, 'liquidPumpEnabled', False)
            before_tick = call('jawa/map_info')['ticksGame']
            before = [water(first), water(second), water((52, 40))]
            candidates = sc(PUMP, 'ProofDrawCycle', '40,40;read')
            step = sc(PUMP, 'ProofDrawCycle', '40,40;step')
            after = [water(first), water(second), water((52, 40))]
            after_tick = call('jawa/map_info')['ticksGame']
            require(before_tick == after_tick, 'isolated proof unexpectedly ticked')
            arm = {'before_tick': before_tick, 'after_tick': after_tick, 'mode': mode, 'before': before, 'candidates': candidates, 'step': step, 'after': after}
            result['arms'].append(arm)
            persist()
            expected_after = {'full': [10000, 20000, 10000], 'exact': [0, 20000, 900], 'off': [900, 20000, 0]}[mode]
            require(after == expected_after and sum(before) == sum(after), 'quantity/conservation failure: ' + str(arm))
        result['status'] = 'PASS'
    except BaseException as exc:
        result['error'] = repr(exc)
    finally:
        dev_restore_error = None
        if dev_mode is not None:
            try:
                hp('devmode:41,41=' + ('on' if dev_mode else 'off'))
                require(hp('gizmos:41,41')['devMode'] == dev_mode, 'dev mode restore')
            except Exception as exc:
                dev_restore_error = repr(exc)
        result['restore'] = restore_scene(reload, rect, setting, flags,
                                          lambda k, v: call('jawa/debug_settings', action='set', field=k, value=v),
                                          name, baseline, settings, debug)
        if dev_restore_error:
            result['restore']['errors'].append(dev_restore_error)
            result['restore']['status'] = 'FAIL'
        after_saves = T.saves_stat(SAVES)
        result['changed_existing_saves'] = [key for key, value in saves_before.items() if after_saves.get(key) != value]
        result['protected_after'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
        result['saves_added'] = sorted(set(after_saves) - set(saves_before))
        if result['restore']['status'] != 'PASS' or result['changed_existing_saves'] or result['protected_after'] != protected_hashes:
            result['status'] = 'FAIL'
        result['finished'] = time.time()
        persist()
    print(result['status'], result.get('error', ''), 'restore=' + result['restore']['status'])
    return 0 if result['status'] == 'PASS' else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.out is None:
        parser.error('--out is required for live')
    return live(args.out)


if __name__ == '__main__':
    sys.exit(main())
