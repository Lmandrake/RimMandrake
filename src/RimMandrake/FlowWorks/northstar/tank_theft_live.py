#!/usr/bin/env python3
"""Paused production pump/theft proof on a guarded disposable calm site.

Pump ProofDrawCycle runs real discovery, planning, transfer and power predicates.
Theft Proof tick bypasses only scheduling; prime compresses a caught day's remainder.
No automatic machine scheduling, bottle-job scheduling or full-list claim is made.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
for directory in (ROOT / 'src/RimMandrake/Utils', ROOT / 'src/RimMandrake/Utils/modcheck'):
    sys.path.insert(0, str(directory))
from pump_outflow_live import restore_scene, set_fill

FW = 'RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings'
HS = 'RimMandrake.FlowWorks.Hose.RM_HoseSettings'
MS = 'RimMandrake.FlowWorks.Machinery.RM_MachinerySettings'
PUMP = 'RimMandrake.FlowWorks.LiquidTypes.Building_LiquidPump'
THEFT = 'RimMandrake.FlowWorks.Machinery.RM_LiquidTheft'
NS = 'RimMandrake.FlowWorks.RM_NorthstarProofs'
LINE = 'RimMandrake.FlowWorks.Machinery.RM_LineProofs'
PRISON = 'RimMandrake.FlowWorks.RM_PitPrisonProof'
RECT = '30,30,28,20'


def require(ok, reason):
    if not ok:
        raise AssertionError(reason)


def fields(text):
    return dict(re.findall(r'(\w+)=(\[[^]]*\]|\S+)', text))


def run(out):
    import validation_core as V
    import test_site_saves as T
    from game_paths import SAVES
    class Bridge(V.Bridge):
        probe_type = 'RimMandrake.FlowWorks.Hose.HoseProbe'
    B = Bridge()
    result = dict(mode='live', started=time.time(), calls=[], status='FAIL', arms=[])
    settings, debug, baseline, name, dev_mode = [], {}, None, None, None
    tap = None
    control_error_messages = set()
    refresh_ticks = 0
    saves = Path(SAVES)
    saves_before = T.saves_stat(SAVES)
    protected = [p for p in saves.glob('*.rws') if p.name.startswith('CANONICAL_') or p.name in
                 ('ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws', 'WORLDMAP_V1_original.rws', T.SITES['calm']['save'] + '.rws')]
    for required in ('CANONICAL_ASHKARR_START_2026-09-12.rws', 'ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws', T.SITES['calm']['save'] + '.rws'):
        require((saves / required).is_file(), 'protected save absent: ' + required)
    protected_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}

    def persist():
        out.write_text(json.dumps(result, indent=2, default=str), encoding='utf-8')

    def call(tool, **kw):
        response = B.call(tool, **kw)
        result['calls'].append(dict(tool=tool, args=kw, result=response))
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
        return {r['name']: r['value'] for r in call('jawa/debug_settings', action='list')['fields']}

    def rect():
        return sc(PRISON, 'Rect', RECT)

    def reload(slot):
        return T.load_site(call, 'calm', name=slot, check=False)

    def hp(command):
        response = B.probe(command)
        result['calls'].append(dict(probe=command, result=response))
        persist()
        require(response.get('success') is True, str(response))
        return response

    def water(cell):
        return int(re.search(r'dl=(\d+)', sc(LINE, 'ProofPitWater', '%d,%d,1,1' % cell))[1])

    def fill(cell, levels):
        set_fill(call, water, cell, levels)

    def theft(action='read'):
        text = sc(THEFT, 'Proof', '38,38;' + action)
        return dict(text=text, **fields(text))

    def pump(cell, action='step'):
        text = sc(PUMP, 'ProofDrawCycle', '%d,%d;%s' % (*cell, action))
        return dict(text=text, **fields(text))

    def refresh_hose_index():
        nonlocal refresh_ticks
        before = theft()
        setting(FW, 'liquidPumpEnabled', False)
        tick_before = call('jawa/map_info')['ticksGame']
        advance = B.ticks(1)
        tick_after = call('jawa/map_info')['ticksGame']
        setting(FW, 'liquidPumpEnabled', True)
        after = theft()
        require(tick_after-tick_before == 1 and after['units'] == before['units'] and after['pending'] == before['pending'], 'hose-index setup tick moved foreign stock or attribution')
        refresh_ticks += tick_after-tick_before
        result.setdefault('hose_refreshes',[]).append(dict(before_tick=tick_before,after_tick=tick_after,before=before,after=after,advance=advance))

    def things(defname):
        response = call('jawa/list_things', defName=defname, rect=RECT, limit=50)
        require(response.get('isCompleteList') is True and response.get('countMatched') == len(response['things']), 'incomplete thing census')
        return response['things']

    try:
        result['log_start'] = V.log_revive(B)
        require(result['log_start']['alive'] and result['log_start']['cleared'], 'initial logging sentinel missing')
        tap = V.tap_start(B)
        result['running'] = call('jawa/running_mods')
        result['identity'] = call('jawa/type_probe', typeName=PUMP)
        expected = hashlib.sha256((ROOT / 'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll').read_bytes()).hexdigest()
        require(result['identity'].get('mvidMatchesFile') is True and result['identity'].get('assemblyFileSha256') == expected, 'loaded DLL identity mismatch')
        result['protected_before'] = protected_hashes
        debug = flags()
        for typ, field in [(FW, 'depthEngineEnabled'), (FW, 'depthEngineLiveForTests'), (FW, 'levelExactEnabled'), (FW, 'liquidPumpEnabled'),
                           (HS, 'enabled'), (HS, 'freeEndRolesEnabled'), (HS, 'hoseHoldsLiquid'), (HS, 'gravityLevellingEnabled'),
                           (MS, 'liquidTheftEnabled'), (MS, 'liquidTheftGoodwillPerDay'), (MS, 'liquidTheftSightRange')]:
            settings.append((typ, field, setting(typ, field)))
        result['settings_before'] = settings
        result['site'] = T.load_site(call, 'calm')
        require(result['site']['verified'], 'registered calm load failed')
        name = 'WHITTLE_TankTheft_Begin_' + time.strftime('%Y%m%dT%H%M%S')
        backup = Path('D:/ClaudeWork/rimmandrake/codex_wsl/fw-drain/tank-theft-raw') / ('saves_before_' + name)
        result['save_backups'] = dict(path=str(backup), files=T.backup_saves(SAVES, str(backup)))
        result['snapshot'] = T.save_site(call, name, SAVES)
        require(reload(name)['verified'], 'guarded begin reload failed')
        baseline = rect()
        result['baseline_rect'] = baseline
        # Preserve site-load noise before any test fixture exists. This exact error
        # was observed on the unchanged registered site, not on a theft transfer.
        control = tap.since()
        control_errors = [e for e in control if str(e.get('Level','')).lower() in ('error','exception')]
        result['site_control_errors'] = control_errors
        control_error_messages = {str(e.get('Message','')) for e in control_errors}
        require(control_error_messages.issubset({'Tried to get CurKindLifeStage from humanlike pawn Shiki'}), 'unexpected error in unchanged site control')
        call('rimworld/pause_game', pause=True)
        for typ, field, value in [(FW, 'depthEngineEnabled', True), (FW, 'depthEngineLiveForTests', True), (FW, 'levelExactEnabled', True),
                                  (FW, 'liquidPumpEnabled', True), (HS, 'enabled', True), (HS, 'freeEndRolesEnabled', True),
                                  (HS, 'hoseHoldsLiquid', False), (HS, 'gravityLevellingEnabled', False),
                                  (MS, 'liquidTheftEnabled', True), (MS, 'liquidTheftGoodwillPerDay', 2), (MS, 'liquidTheftSightRange', 12)]:
            setting(typ, field, value)
            require(str(setting(typ, field)).lower() == str(value).lower(), 'setting readback ' + field)
        call('jawa/set_roof_batch', ops='None:' + RECT)
        call('jawa/destroy_batch', rects=RECT, categories='All')
        sc(NS, 'ProofResetRect', RECT.replace(',', ';'))
        call('jawa/set_terrain_batch', ops='Soil:' + RECT)
        call('jawa/set_fog', action='unfog', rect=RECT)
        for cell in ((38,36), (40,41), (52,40)):
            call('jawa/flowworks_excavation_drive', x=cell[0], z=cell[1], deepenLevels=4, setFill=0)
        build = call('jawa/build_batch', ops='RM_LiquidTank:38,38;RM_LiquidPump:38,37;RM_LiquidPump:37,38;RM_LiquidPump:40,40;RM_HoseReel:41,41,1', faction='player', wipeExisting=False)
        require(build.get('survived') == 5, 'fixture cardinality')
        call('jawa/map_commit')
        dev_mode = hp('gizmos:41,41')['devMode']
        hp('devmode:41,41=on')
        call('jawa/debug_settings', action='set', field='godMode', value=True)
        pumps = {(p['x'],p['z']):p for p in things('RM_LiquidPump')}
        require(set(pumps) == {(38,37),(37,38),(40,40)}, 'pump footprint census')
        for cell in ((38,37),(40,40)):
            call('jawa/select_things', ids=pumps[cell]['id'], jumpCamera=False)
            gizmos = call('rimworld/list_selected_gizmos')
            g = next(g for g in gizmos['gizmos'] if 'power' in str(g.get('label','')).lower() and 'dev' in str(g.get('label','')).lower())
            call('rimworld/execute_gizmo', gizmoId=g.get('gizmoId') or g['id'])
        factions = call('jawa/list_factions', limit=500)
        owners = [f for f in factions['factions'] if not f['isPlayer'] and not f['hostile'] and not f['hidden'] and not f['permanentEnemy'] and f['goodwill'] > -90]
        require(owners, 'no calm non-player faction for witness')
        owner = owners[0]['defName']
        tank = things('RM_LiquidTank')[0]
        for identity in (tank['id'],pumps[(38,37)]['id']):
            changed = call('jawa/set_thing_props', thing=identity, faction=owner)
            require('faction' in changed['changed'], 'faction write not honored')
        result['fixtures'] = dict(owner_faction=owner, tank=things('RM_LiquidTank')[0], pumps=things('RM_LiquidPump'))
        witness = call('jawa/spawn_pawn', kindDef='Colonist', x=43, z=37, faction=owner, count=1)
        require(witness.get('spawnedCount') == 1 and len(witness['pawns']) == 1 and witness['pawns'][0]['ok'] and witness['pawns'][0]['faction'] == owner, 'witness actor/cardinality mismatch')
        result['witness_fixture'] = witness
        call('jawa/map_commit')
        require(pump((38,37),'read')['running'] == 'True' and pump((40,40),'read')['running'] == 'True', 'working actor controls')
        require(pump((37,38),'read')['running'] == 'False', 'idle player pump must be off')
        initial = theft('tick')
        require(initial['reach'] == 'True' and initial['witness'] != 'none' and initial['caughtBy'] == 'none', 'non-vacuous reach/witness baseline')
        require(initial['witness'] == witness['pawns'][0]['id'], 'witness is not the staged faction member')
        result['initial'] = initial
        start_tick = call('jawa/map_info')['ticksGame']

        # Owner fills its foreign tank through the real powered pump, with idle player reach.
        fill((38,36),2)
        before = theft(); src = water((38,36)); owner_step = pump((38,37)); after_owner = theft()
        require(owner_step['units'] == '10000' and int(after_owner['units']) - int(before['units']) == 10000 and src-water((38,36)) == 10000, 'owner actual production transfer/deltas')
        require(after_owner['pending'] == '[]', 'owner action attributed to player')
        # Activate a reachable player mover that sends world water to an outflow, never through this tank.
        route = hp('check:41,41,51,40'); require(route.get('reason') is None, 'outflow fixture route refused')
        hp('lay:41,41,51,40'); sc(LINE,'ProofHoseRole','41,41;Outflow')
        refresh_hose_index()
        require('outflows=[51,40]' in pump((40,40),'read')['text'], 'active mover lacks its actual outflow port')
        fill((40,41),2)
        src = water((40,41)); dest = water((52,40)); unrelated_step = pump((40,40)); after_active = theft()
        require(unrelated_step['units'] == '10000' and src-water((40,41)) == 10000 and water((52,40))-dest == 10000, 'unrelated active production move did not occur')
        require(after_active['units'] == after_owner['units'] and after_active['pending'] == '[]' and after_active['reach'] == 'True', 'unrelated player move touched/blamed foreign tank')
        negative = theft('tick')
        require(negative['caughtBy'] == 'none' and negative['caught'] == initial['caught'] and negative['charges'] == initial['charges'] and negative['ticks'] == '0' and negative['victimGoodwill'] == initial['victimGoodwill'], 'owner-use negative caught/charged player')
        result['arms'].append(dict(name='owner_with_idle_and_unrelated_active_player', before=before, owner=owner_step, after_owner=after_owner, active=unrelated_step, after_active=after_active, verdict=negative))

        # Cap the outflow: the same player pump now successfully puts water into the foreign tank.
        sc(LINE,'ProofHoseRole','41,41;Capped')
        refresh_hose_index()
        require('outflows=[]' in pump((40,40),'read')['text'], 'capped outflow remained active')
        fill((40,41),2)
        before = theft(); src = water((40,41)); player_step = pump((40,40)); pending = theft()
        require(player_step['units'] == '10000' and int(pending['units'])-int(before['units']) == 10000 and src-water((40,41)) == 10000 and pending['pending'] != '[]', 'player transfer/attribution missing')
        occupied = name.replace('_Begin_', '_Pending_')
        result['pending_snapshot'] = T.save_site(call, occupied, SAVES)
        result['pending_reload'] = T.load_site(call, 'calm', name=occupied, check=False, map_controls=('modal_broker',))
        require(result['pending_reload']['verified'], 'occupied pending reload failed')
        call('rimworld/pause_game', pause=True)
        reloaded = theft()
        for key in ('tank','faction','units','liquid','pending','caughtBy','ticks','witness'):
            require(reloaded[key] == pending[key], 'pending save/load changed ' + key)
        result['pending_roundtrip'] = dict(before=pending, after=reloaded, file=occupied)
        caught = theft('tick')
        require(caught['caughtBy'] == caught['faction'] and int(caught['caught']) == int(initial['caught'])+1 and caught['witness'] != 'none', 'existing real witness/caught path failed')
        require(caught['ticks'] == '0' and caught['charges'] == initial['charges'], 'first catch accrued early')
        prime = theft('prime')
        # A dev-forced power state is not an energy source and may reset on load.
        # Reapply the same real CompPowerTrader gizmo if needed, then recheck Running.
        if pump((40,40),'read')['running'] != 'True':
            call('jawa/select_things', ids=pumps[(40,40)]['id'], jumpCamera=False)
            gizmos = call('rimworld/list_selected_gizmos')
            g = next(g for g in gizmos['gizmos'] if 'power' in str(g.get('label','')).lower() and 'dev' in str(g.get('label','')).lower())
            call('rimworld/execute_gizmo', gizmoId=g.get('gizmoId') or g['id'])
            require(pump((40,40),'read')['running'] == 'True', 'post-load power control')
        fill((40,41),2)
        player_second = pump((40,40)); charged = theft('tick')
        require(player_second['units'] == '10000' and int(charged['charges']) == int(initial['charges'])+1 and int(charged['goodwill']) == int(initial['goodwill'])-2 and int(charged['victimGoodwill']) == int(initial['victimGoodwill'])-2 and charged['ticks'] == '0', 'preserved goodwill charge failed')
        idle = theft('tick')
        require(idle['charges'] == charged['charges'] and idle['ticks'] == charged['ticks'], 'idle caught tank accrues')
        result['arms'].append(dict(name='actual_player_transfer_caught_and_goodwill', before=before, step=player_step, pending=pending, caught=caught, compressed_remainder=prime, second=player_second, charged=charged, idle=idle))
        end_tick = call('jawa/map_info')['ticksGame']
        require(end_tick-start_tick == refresh_ticks, 'time advanced outside the declared hose-index setup ticks')
        result['timing'] = dict(before=start_tick, after=end_tick, hose_refresh_ticks=refresh_ticks, boundary='real production entries; two pump-disabled setup ticks refresh hose indexes; one-day remainder seeded after genuine catch')
        result['status'] = 'PASS'
    except BaseException as exc:
        result['error'] = repr(exc)
    finally:
        dev_error = None
        if dev_mode is not None:
            try:
                hp('devmode:41,41=' + ('on' if dev_mode else 'off'))
                require(hp('gizmos:41,41')['devMode'] == dev_mode, 'dev mode restore')
            except Exception as exc:
                dev_error = repr(exc)
        result['restore'] = restore_scene(reload, rect, setting, flags, lambda k,v: call('jawa/debug_settings',action='set',field=k,value=v), name, baseline, settings, debug)
        if dev_error:
            result['restore']['errors'].append(dev_error); result['restore']['status'] = 'FAIL'
        after = T.saves_stat(SAVES)
        result['changed_existing_saves'] = [k for k,v in saves_before.items() if after.get(k) != v]
        result['protected_after'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
        result['saves_added'] = sorted(set(after)-set(saves_before))
        if result['restore']['status'] != 'PASS' or result['changed_existing_saves'] or result['protected_after'] != protected_hashes:
            result['status'] = 'FAIL'
        try:
            alive = V.log_alive(B, 'tank-theft-final')
            entries = tap.since() if tap is not None else []
            errors = [e for e in entries if str(e.get('Level','')).lower() in ('error','exception')]
            new_errors = [e for e in errors if str(e.get('Message','')) not in control_error_messages]
            result['log_budget'] = dict(sentinel=alive, lost=tap.lost if tap is not None else None, entries=entries, errors=errors, new_errors=new_errors, site_control_messages=sorted(control_error_messages))
            require(alive['alive'] and tap is not None and tap.lost == 0 and not new_errors, 'log budget unreadable or new error/exception')
        except Exception as exc:
            result['status'] = 'FAIL'
            result['log_budget_error'] = repr(exc)
        result['finished'] = time.time(); persist()
    print(result['status'], result.get('error',''), 'restore=' + result['restore']['status'])
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    sys.exit(run(parser.parse_args().out))
