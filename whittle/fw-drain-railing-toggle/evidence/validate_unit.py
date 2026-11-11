"""Run both real Whittle checks, explicitly requiring judge and broaden."""
from pathlib import Path
import importlib.util,json,os,sys,time
here=Path(__file__).resolve().parent;root=here.parents[2]
os.environ.update(WHITTLE_DIR='whittle/fw-drain-railing-toggle',WHITTLE_NEED_JUDGE='1',WHITTLE_NEED_BROADEN='1',WHITTLE='1')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
hook=module('unit_stop',root/'.claude/hooks/whittle_stop.py')
problems=hook.done_problems(str(root),'whittle/fw-drain-railing-toggle',True,True)
runner=module('unit_whittle_run','/home/mandrake/dev/MandrakeWorkflows/whittle/run.py')
rc=runner.validate(root)
r=dict(time=time.time(),root=str(root),WHITTLE_DIR=os.environ['WHITTLE_DIR'],require_judge=True,require_broaden=True,done_problems=problems,actual_validate_result=rc)
p=here/('validator_'+sys.argv[1]+'.json');assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));sys.exit(0 if not problems and rc==0 else 1)
