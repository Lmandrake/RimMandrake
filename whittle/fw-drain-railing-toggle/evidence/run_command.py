"""Retain exact stdout/stderr and invocation for one command. Never overwrite a prior receipt."""
from pathlib import Path
import sys,json,subprocess,time,os
here=Path(__file__).resolve().parent;root=here.parents[2]
label=sys.argv[1];cmd=sys.argv[2:]
if cmd and cmd[0]=='--':cmd=cmd[1:]
for suffix in ('_stdout.txt','_stderr.txt','_command.json'):assert not (here/(label+suffix)).exists(),label
started=time.time();env=dict(os.environ,TMPDIR='/home/mandrake/.seat-tmp/fw-railing-toggle')
with (here/(label+'_stdout.txt')).open('wb') as out,(here/(label+'_stderr.txt')).open('wb') as err:
 p=subprocess.run(cmd,cwd=root,env=env,stdout=out,stderr=err)
r=dict(command=cmd,cwd=str(root),started=started,elapsed=time.time()-started,returncode=p.returncode,TMPDIR=env['TMPDIR'])
(here/(label+'_command.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));print((here/(label+'_stdout.txt')).read_text(errors='replace')[-1800:]);print((here/(label+'_stderr.txt')).read_text(errors='replace')[-1000:]);sys.exit(p.returncode)
