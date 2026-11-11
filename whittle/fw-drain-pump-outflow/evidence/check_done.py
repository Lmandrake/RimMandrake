"""Call the actual local checker and MandrakeWorkflows validator with both requirements enabled."""
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
label = sys.argv[1]
assert not (here / (label + '.json')).exists()
os.environ.update(WHITTLE_DIR='whittle/fw-drain-pump-outflow', WHITTLE_NEED_JUDGE='1', WHITTLE_NEED_BROADEN='1')
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
hook = module('actual_whittle_stop', root / '.claude/hooks/whittle_stop.py')
problems = hook.done_problems(str(root), 'whittle/fw-drain-pump-outflow', True, True)
workflow = module('actual_whittle_run', '/home/mandrake/dev/MandrakeWorkflows/whittle/run.py')
out, err = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
    result = workflow.validate(root)
receipt = dict(time=time.time(), checker_path=str(root / '.claude/hooks/whittle_stop.py'),
    called='done_problems(root, work, True, True)', problems=problems,
    workflow_path='/home/mandrake/dev/MandrakeWorkflows/whittle/run.py',
    workflow_call='validate(root)', workflow_returncode=result,
    stdout=out.getvalue(), stderr=err.getvalue(), need_judge=True, need_broaden=True)
(here / (label + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
raise SystemExit(0 if not problems and result == 0 else 1)
