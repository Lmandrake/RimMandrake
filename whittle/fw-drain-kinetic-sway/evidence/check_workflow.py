"""Invoke the real claim check and full Whittle validator, preserving refusals."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
os.environ.update(WHITTLE_DIR='whittle/fw-drain-kinetic-sway', WHITTLE='1',
                  WHITTLE_NEED_JUDGE='1', WHITTLE_NEED_BROADEN='1')
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

hook = module('whittle_stop', root / '.claude/hooks/whittle_stop.py')
work, limit, need_judge, need_broaden = hook.settings()
problems = hook.done_problems(str(root), work, need_judge, need_broaden)
runner = module('whittle_runner', Path('/home/mandrake/dev/MandrakeWorkflows/whittle/run.py'))
stdout, stderr = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
    code = runner.validate(root)
receipt = dict(time=time.time(), WHITTLE_DIR=work, need_judge=need_judge, need_broaden=need_broaden,
               last_change=hook.last_change(str(root), work), done_problems=problems,
               full_validator='MandrakeWorkflows/whittle/run.py validate(root)',
               full_validator_returncode=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())
path = here / ('workflow_' + sys.argv[1] + '.json')
assert not path.exists(), 'Preserve previous receipts'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
sys.exit(1 if problems or code else 0)
