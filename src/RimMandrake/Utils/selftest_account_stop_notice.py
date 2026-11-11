#!/usr/bin/env python3
"""Hard-stop cause reaches both wake paths and the handoff restart's launch prompt."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'rimflow')]
from account_stop_notice import hard_stop_reason
import handoff
import seat_restart as SR

with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'RM_SWITCH_PLAN_DIR': d}):
    p = Path(d)/'notice.json'
    assert hard_stop_reason() is None
    for value in ('garbage', '[]', '{"state":"none"}', '{"state":"soft"}'):
        p.write_text(value)
        assert hard_stop_reason() is None
    p.write_text(json.dumps({'state': 'stop', 'since': '2026-11-11T05:15:15-08:00',
                             'at': '2026-11-11T05:45:00-08:00', 'reset_at': '2026-11-11T13:00:00-08:00'}))
    reason = hard_stop_reason()
    assert reason == 'hard stop by the account switcher at 2026-11-11T05:15:15-08:00, until 2026-11-11T13:00:00-08:00'
    out = io.StringIO()
    with patch.object(handoff, 'show_last_reply'), patch.object(handoff, 'previous_handoff', return_value=(None, None)), \
            patch.object(handoff, 'seat', return_value='BENCH'), contextlib.redirect_stdout(out):
        handoff.wake()
    assert reason in out.getvalue(), out.getvalue()
    cfg = {'clone': d, 'session_name': 'CONDUCTOR', 'kind': 'conductor'}
    prompt = SR.relaunch_argv('BENCH', cfg, why='HANDOFF READY')[-1]
    assert reason in prompt
    assert SR.RESTART_PROMPT_RE.fullmatch(prompt), 'the restart remains recognizable as a program prompt'
    out = io.StringIO()
    with patch.object(SR, 'last_dead_window', return_value=(d+'/dead.jsonl', 'old reply')), \
            contextlib.redirect_stdout(out):
        SR._wake_last_reply({}, cfg)
    assert reason in out.getvalue() and 'a boot, crash' not in out.getvalue()
    p.write_text(json.dumps({'state': 'stop', 'since': 'original stop'}))
    assert 'time unmeasured' in hard_stop_reason()
    p.write_text('{"state":"none"}')
    assert 'hard stop' not in SR.relaunch_argv('BENCH', cfg, why='HANDOFF READY')[-1]
print('PASS hard-stop wake, restart prompt, malformed/legacy notice and recovery')
