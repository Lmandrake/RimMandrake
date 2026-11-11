"""Run both explicitly required Whittle validators without substituting a checker."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
def module(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

os.environ.update(WHITTLE_DIR='whittle/fw-drain-tank-theft',WHITTLE='1',
                  WHITTLE_NEED_JUDGE='1',WHITTLE_NEED_BROADEN='1',PYTHONDONTWRITEBYTECODE='1')
hook = module('actual_project_whittle_stop',root/'.claude/hooks/whittle_stop.py')
problems = hook.done_problems(str(root),'whittle/fw-drain-tank-theft',True,True)
workflow_path = Path('/home/mandrake/dev/MandrakeWorkflows/whittle/run.py')
workflow = module('actual_workflows_whittle_run',workflow_path)
rc = workflow.validate(root)
receipt = dict(time=time.time(),project_checker=str(root/'.claude/hooks/whittle_stop.py'),
               done_problems=problems,need_judge=True,need_broaden=True,
               workflow_checker=str(workflow_path),actual_validate_returncode=rc)
target = here/(sys.argv[1] if len(sys.argv)>1 else 'whittle_validation.json')
assert not target.exists(), 'Preserve prior validation attempts'
target.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
sys.exit(0 if not problems and rc == 0 else 1)
