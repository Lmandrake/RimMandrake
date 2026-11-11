#!/usr/bin/env python3
"""Codex loops have separate handoffs, ledger shards, bridge holds and host guards."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'Utils')]
import model
import handoff
import lessons
import host_guard
import bridge_holder

for seat in model.CODEX_SEATS:
    assert seat in model.SEATS
    assert handoff.seat_from_ready(seat + ' is ready') == seat
    assert model.read_name(seat) == model.write_name(seat) == seat
    assert lessons.seat_of(seat) == seat
    handoff.require_worker_seat(seat, {'CODEX_CI': '1'})
    with patch.dict(os.environ, {'RIMFLOW_SEAT': seat, 'RIMFLOW_BRIDGE_SEAT': seat}):
        assert handoff.seat() == seat
        assert model.ambient_window_seat() == seat
        assert handoff.own_hold('HELD BENCH', seat) is False
    with patch.object(host_guard, '_shared_window_holder', return_value=None), \
            patch.object(host_guard.driver_lock, 'acquire', return_value={'ok': True}) as take:
        host_guard.acquire(seat, 'fixture', identity={'pid': 1}, path='/unused')
        assert take.call_args.args[1] == seat

    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ, RIMFLOW_SEAT=seat, AGENT_SEAT=seat, RIMFLOW_BRIDGE_SEAT=seat,
                   RIMFLOW_LEDGER=d+'/events.jsonl', RIMFLOW_ITEMS=d+'/items',
                   RIMFLOW_SHARED_BRIDGE=d+'/shared.json', RIMFLOW_DRIVER_LOCK='',
                   RIMFLOW_DISPATCH_LOCK=d+'/dispatch.lock', RIMFLOW_BRIDGE_LOCK=d+'/bridge.lock',
                   RIMFLOW_PROBE='no-reading', RIMFLOW_OWNER_ACT_STAMP=d+'/act.json')
        Path(d+'/items').mkdir()
        def rf(*args):
            p = subprocess.run([sys.executable, str(HERE/'cli.py'), *args], env=env,
                               cwd=d, capture_output=True, text=True, timeout=120)
            assert p.returncode == 0, p.stdout + p.stderr
        rf('file', 'CODEX_SEAT_DISTINCT_IDENTITY', '--title', 'fixture', '--kind', 'task', '--for', 'BENCH')
        rf('reassign', 'CODEX_SEAT_DISTINCT_IDENTITY', '--to', seat)
        rf('note', 'CODEX_SEAT_DISTINCT_IDENTITY', '--text', 'fixture')
        rf('bridge', 'take', '--host', 'stevedesktop', '--for', 'fixture')
        rf('bridge', 'release', '--host', 'stevedesktop')
        rows = [json.loads(line) for line in Path(d+'/events/'+seat+'.jsonl').read_text().splitlines()]
        assert rows and all(row['seat'] == seat for row in rows)
        assert not Path(d+'/events/BENCH.jsonl').exists()
        world = model.replay(model.read_clone(d+'/events.jsonl'))
        assert not world.errors, world.errors
        assert world.items['CODEX_SEAT_DISTINCT_IDENTITY'].owner == seat
    print('PASS', seat, 'separate ledger, bridge and handoff identity')

for seat in ('BENCH', 'CONDUCTOR'):
    for marker in ('CODEX_THREAD_ID', 'CODEX_SESSION_ID', 'CODEX_CI'):
        try:
            handoff.require_worker_seat(seat, {marker: 'fixture'})
        except SystemExit as e:
            assert 'REFUSED' in str(e)
        else:
            raise AssertionError('Codex may write '+seat)
    handoff.require_worker_seat(seat, {})
print('PASS Codex cannot write Conductor handoffs; Conductor still can')
