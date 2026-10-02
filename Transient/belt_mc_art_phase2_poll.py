import json,os,subprocess,time,glob,sys
A='/mnt/d/Luke/dev/_artpipe'; S='/tmp/claude-1000/-home-mandrake-rm-foundry/da789fc3-922a-4a0b-9b44-9c7703580d73/scratchpad'
jobs={j['id']:j for j in json.load(open('Transient/belt_mc_art_phase2_jobs.json'))}
ST=S+'/state.json'
st=json.load(open(ST)) if os.path.exists(ST) else {'n':1,'refiled':[]}
def fam(i): return [x for x in jobs if x in i or i.startswith(x)]
end=time.time()+int(sys.argv[1])
while time.time()<end:
    p=len(os.listdir(A+'/pending'));a=len(os.listdir(A+'/active'))
    failed=[f[:-5] for f in os.listdir(A+'/failed') if f.endswith('.json') and not f.endswith('.manifest.json') and f.startswith('RM_MessyConduit_') and not f[:-5].endswith('_v2')]
    for f in failed:
        if f in jobs and f not in st['refiled']:
            j=dict(jobs[f]);j['id']=f+'_v2'
            open(S+'/r.json','w').write(json.dumps([j]));subprocess.run(['python3','src/RimMandrake/Utils/artpipe/fill_queue.py','--input',S+'/r.json'],capture_output=True)
            st['refiled'].append(f);print('refiled',f)
    if p+a<=3 and os.path.exists(f'{S}/b{st["n"]}.json'):
        subprocess.run(['python3','src/RimMandrake/Utils/artpipe/fill_queue.py','--input',f'{S}/b{st["n"]}.json'],capture_output=True);st['n']+=1
    json.dump(st,open(ST,'w'))
    ids=[x for x in jobs]
    done=sum(os.path.exists(f'{A}/done/{i}.manifest.json') or os.path.exists(f'{A}/done/{i}_v2.manifest.json') for i in ids)
    print(f'pending={p} active={a} done={done}/{len(ids)} failed={len(failed)} nextbatch={st["n"]}',flush=True)
    if done==len(ids): break
    time.sleep(60)
