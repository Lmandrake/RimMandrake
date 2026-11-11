#!/usr/bin/env python3
"""Phone idempotency, delivery retry and actual reset restart paths; all commands and transport are fake."""
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import switching_plan as SP
from pulse import phone_push as PP

NOW = 1_800_000_000
plan = SP.load_plan()
def rec(left, reset, stale=False):
    return {'source': 'MEASURED', 'week_pct_left': left, 'week_resets_at': SP.iso(reset),
            'age_min': 1, 'stale': stale}

with tempfile.TemporaryDirectory() as d:
    out = Path(d)/'out'
    live = ['system']
    meter = {n: rec(0, NOW+(i+1)*36000) for i, n in enumerate(plan['order'])}
    commands, sent = [], []
    fail = [None]
    def run(argv, **kwargs):
        verb = argv[1]
        if verb == '--json':
            return 0, json.dumps({'machine': 'fixture', 'live': live[0], 'armed': True})
        commands.append(verb)
        if verb == fail[0]:
            return 3, 'fixture failure'
        if verb == 'use':
            live[0] = argv[2]  # real claude-account use relaunches by default; no second fleet-start
        return 0, '{}'
    with patch.object(SP, 'OUT', out), patch.object(SP, 'SWITCH_LOG', Path(d)/'no-log'), \
            patch.object(SP, 'run', side_effect=run), patch.object(SP, 'clock', return_value=NOW), \
            patch.object(PP, 'STATE', Path(d)/'phone.json'), \
            patch.object(PP, 'todoist_transport', side_effect=lambda title, body: sent.append((title, body))):
        def go(dry=False, now=NOW):
            return SP.check(dry=dry, now=now, meter_fn=lambda: meter, poll_fn=lambda: None)
        go(dry=True)
        assert not commands and not sent and not (out/'notice.json').exists()
        fail[0] = 'fleet-stop'
        assert go() == 1
        assert not sent and not SP.load_state().get('stopped')
        fail[0] = None
        assert go() == 0 and len(sent) == 1
        assert sent[0][0] == 'Claude stopped: all accounts are out'
        original = SP.read_json(out/'notice.json')['since']
        go(now=NOW+300)
        assert len(sent) == 1 and SP.read_json(out/'notice.json')['since'] == original
        # A crash after delivery but before state save must not duplicate the phone notice.
        st = SP.load_state(); st['stopped'].pop('phone_notified'); SP.save_state(st)
        go(now=NOW+600)
        assert len(sent) == 1
        # A stale reset reading or a small amount of headroom must never launch windows.
        for left, stale in ((100, True), (3, False)):
            commands.clear()
            meter['system'] = rec(left, NOW+SP.WEEK+72000, stale=stale)
            go()
            assert 'fleet-start' not in commands and 'use' not in commands
        meter['system'] = rec(100, NOW+SP.WEEK+72000)
        commands.clear(); fail[0] = 'fleet-start'
        assert go() == 1 and SP.load_state().get('stopped')
        fail[0] = None
        assert go() == 0 and commands.count('fleet-start') == 2
        assert not SP.load_state().get('stopped') and SP.read_json(out/'notice.json')['state'] == 'none'
        commands.clear(); go()
        assert 'fleet-start' not in commands
        # A new hard stop gets one new incident; transport failure retries without another fleet-stop.
        meter['system'] = rec(0, NOW+SP.WEEK+72000)
        with patch.object(PP, 'todoist_transport', side_effect=OSError('offline')):
            go(now=NOW+3600)
        assert not SP.load_state()['stopped'].get('phone_notified')
        commands.clear(); go(now=NOW+3900)
        assert commands == [] and len(sent) == 2
        assert SP.load_state()['stopped']['phone_notified']
        # Another account's reset takes the default-relaunch use path from the stopped fleet.
        meter['lukas'] = rec(100, NOW+SP.WEEK+108000)
        commands.clear(); go(now=NOW+4200)
        assert commands == ['use'] and live[0] == 'lukas' and not SP.load_state().get('stopped')
    assert SP.next_refill({}, plan, NOW) == {}
    no_headroom = {**plan, 'accounts': {n: {'leave_pct_left': 100} for n in plan['order']}}
    assert SP.next_refill(meter, no_headroom, NOW) == {}
print('PASS dry run, once-per-stop phone, failures/retry, post-reset headroom and restart idempotency')
