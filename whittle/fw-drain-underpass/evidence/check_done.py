"""Invoke the workflow's real done_problems with its environment-derived settings."""
import importlib.util
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[3]
path = root / '.claude/hooks/whittle_stop.py'
spec = importlib.util.spec_from_file_location('whittle_stop', path)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)
work, limit, need_judge, need_broaden = hook.settings()
problems = hook.done_problems(str(root), work, need_judge, need_broaden)
print(json.dumps({'work': work, 'need_judge': need_judge, 'need_broaden': need_broaden,
                  'last_change': hook.last_change(str(root), work), 'problems': problems}, indent=2))
sys.exit(1 if problems else 0)
