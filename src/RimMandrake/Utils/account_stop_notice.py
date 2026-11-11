"""Read the account switcher's hard-stop reason for handoff and restart wakes. No actions."""
import json
import os
from pathlib import Path


def hard_stop_reason(path=None):
    if path is None:
        root = os.environ.get('RM_SWITCH_PLAN_DIR')
        path = Path(root) / 'notice.json' if root else Path(
            r'D:\ClaudeWork\rimmandrake\switching_plan\notice.json' if os.name == 'nt' else
            '/mnt/d/ClaudeWork/rimmandrake/switching_plan/notice.json')
    try:
        notice = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    if not isinstance(notice, dict) or notice.get('state') != 'stop':
        return None
    at = notice.get('since') or notice.get('at') or 'an unmeasured time'
    reset = notice.get('reset_at') or 'the next account reset (time unmeasured)'
    return f'hard stop by the account switcher at {at}, until {reset}'
