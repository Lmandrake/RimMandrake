"""ask.py <name> <prompt-file> img1 img2 ... : codex exec with images (-i), answer to <name>.answer.md"""
import sys,os,time,shutil,subprocess
from pathlib import Path
sys.path.insert(0,'/home/mandrake/rm/bench/skills/generating-images/scripts')
import codex_image as ci
name,pf,*imgs=sys.argv[1:]
job=ci.CODEX_SCRATCH/('review-%s-%d'%(name,os.getpid())); job.mkdir(parents=True,exist_ok=True)
local=[]
for i in imgs:
    d=job/Path(i).name; shutil.copy(i,d); local.append(d)
ans=job/'answer.md'
cmd=[str(ci.find_codex_cli()),'exec','--sandbox','read-only','--skip-git-repo-check','-o',ci.wsl_to_win(ans),'-c','model_reasoning_effort="high"','-m',os.environ.get('CODEX_CONSULT_MODEL','gpt-6.1-sol')]
for d in local: cmd+=['-i',ci.wsl_to_win(d)]
cmd+=['--','-']
t=time.time()
with open(pf,'rb') as f, open(job/'codex.log','wb') as log:
    rc=subprocess.run(cmd,cwd=str(job),stdin=f,stdout=log,stderr=subprocess.STDOUT,timeout=2400).returncode
out=Path('/home/mandrake/rm/bench/Transient/river_hose_art_review_2026-10-16/answers')/(name+'.answer.md'); out.parent.mkdir(exist_ok=True)
if ans.is_file() and ans.read_text().strip():
    out.write_text(ans.read_text()); print(name,'ok',int(time.time()-t),'s',len(ans.read_text()))
else:
    print(name,'FAILED rc',rc,(job/'codex.log').read_text(errors='replace')[-1500:])
