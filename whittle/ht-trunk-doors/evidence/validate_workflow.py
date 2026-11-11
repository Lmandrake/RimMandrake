"""Invoke real Whittle validate(cwd); retain actual streams and return code."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[3]
here=Path(__file__).resolve().parent
os.environ['WHITTLE_DIR']='whittle/ht-trunk-doors'
path=Path('/home/mandrake/dev/MandrakeWorkflows-dev/whittle/run.py')
spec=importlib.util.spec_from_file_location('trunk_doors_whittle_validator',path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
out=io.StringIO()
err=io.StringIO()
started=time.time()
with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
    rc=module.validate(root)
(here/'workflow.stdout.txt').write_text(out.getvalue())
(here/'workflow.stderr.txt').write_text(err.getvalue())
r={'validator':str(path),'call':'validate(cwd)','cwd':str(root),
   'WHITTLE_DIR':os.environ['WHITTLE_DIR'],'started':started,
   'elapsed_seconds':time.time()-started,'workflow_rc':rc}
(here/'workflow.receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
print(out.getvalue(),end='')
print(err.getvalue(),end='',file=sys.stderr)
sys.exit(rc)
