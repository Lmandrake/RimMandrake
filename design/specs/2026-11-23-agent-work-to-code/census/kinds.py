import pickle,os,re,sys
from collections import defaultdict,Counter
D='/mnt/d/ClaudeWork/rimmandrake/scratch/a2c/'
S=pickle.load(open(D+'scan2.pkl','rb'));R=pickle.load(open(D+'rows.pkl','rb'))
sess2row={};item2stage={}
for r in R:
    if r['session']: sess2row.setdefault(r['session'],r)
    it=r['item'];st=r['env'].get('RM_CONTROL_STAGE')
    if st: item2stage[it]=st
MODS='FLOWWORKS|PYRELANDS|PYRE|SLACK|GIMMESOMESLACK|KNOCKBACK|EXPLOSIVEKNOCKBACK|PIT|MOAT|PITS|ULLAI|GSS|JETTY|DRAWBRIDGE|BURN|FIREHAWK|INFERNO|CABLE|TANK|TANKS|LIQUID|WATER|CORD|THISTLE|KELP'
def role(x):
    p=x['p'];k=p.split('/projects/')[1].split('/')[0]; f=(x['first'] or '')
    sub='/subagents/' in p
    if k.endswith('-det'):
        it=k.split('clones-')[1][:-4].replace('-','_')
        st=item2stage.get(it) or next((v for a,v in item2stage.items() if a.startswith(it) or it.startswith(a)),None)
        m=re.sub('^(RIMMANDRAKE|RIMMASTER)_','',it); v=m.split('_')[0]
        mod=bool(re.search(r'(^|_)(%s)(_|$)'%MODS,m))
        if v=='DRIVE' : return 'mod: in-game driver'
        if st=='offline_build': return 'mod: offline build'
        if re.search(r'JUDGE_.*(BLIND_CYCLE|COVERAGE)',m) or st=='blind_challenge': return 'mod: blind challenge judge'
        if v=='JUDGE': return 'judge (coverage, look, other)'
        if v=='STEWARD' or st=='pre_human': return 'mod: steward and walk brief'
        if st=='in_game': return 'mod: in-game fixer (stage in_game)'
        if v in('ROUTE','CONFIRM'): return 'mod: route or confirm a visit result'
        if v in('RECHECK','REWRITE') or (v in('DESIGN','ENACT','SETTLE','RETIRE') and re.search('BIOME|SEA|UTINNI',m)): return 'design text rewrite (biomes, seas)'
        if re.search('DRAW|ART|LOOK|TANK_DESIGNS|PICTURE|JETTY|ICON|MOCK',m) and v in('REDRAW','DRAW','GENERATE','REDESIGN','MOCK','LIGHT','DEPLOY','JUDGE','FADE','SMOOTH'): return 'art work'
        if mod: return 'mod: fix or trace, launched by item'
        return 'list item: machinery or other'
    if 'rm-bench' in k: return 'Conductor window subagents' if sub else 'Conductor window'
    if 'roles-Operations' in k: return 'Operations role'
    if 'roles-Conductor' in k: return 'Conductor role (quick checks)'
    if 'roles-Designer' in k or 'clones-cleanse' in k: return 'Designer and Designer cleanse'
    if 'coverage-cal' in k: return 'coverage judge (calibration)'
    if 'arteval' in k: return 'art judge (arteval)'
    if 'Hestia' in k or 'lodestar' in k.lower() or 'Dispatch' in k: return 'other project'
    return 'other: '+k[:50]
def kind(n,cmd):
    c=cmd or ''
    if n in('Read',):
        return 'look at image' if re.search(r'\.(png|jpg|bmp)$',c,re.I) else 'read file'
    if n in('Edit','Write','NotebookEdit'):
        if re.search(r'\.(md|txt)$',c): return 'write prose or record (.md)'
        if re.search(r'\.(json|jsonl|csv|tsv)$',c): return 'write record (.json)'
        return 'edit code or def'
    if n in('Agent','Task','SendMessage','TaskStop'): return 'agents'
    if n=='Skill' or n=='ToolSearch': return 'skill load'
    if n in('Grep','Glob'): return 'search'
    if n in('ScheduleWakeup','Monitor'): return 'wait'
    if n!='Bash': return 'tool '+n.split('__')[0]+n.split('__')[-1][:12] if n.startswith('mcp') else 'tool '+n
    q=re.sub(r'^\s*(cd [^;&\n]+[;&\n]+\s*)+','',c).strip()
    if re.search(r'cli\.py"? (--\S+ )*(note|claim|close|file|wait|start|drop|supersede|verify|live|hold|bridge take|bridge release)\b|rimflow (note|claim|close|file|wait|drop)',q): return 'ledger write'
    if re.search(r'\./publish|git (commit|add|pull|push|merge|rebase|stash|checkout)|\./sync|\bland\.sh',q): return 'land (publish, commit, sync)'
    if re.search(r'maturation\.py|designer_stage\.py|coverage_judge\.py|modledger\.py|concept_tree\.py|judge_certificate|accept_coverage|shortfall\.py|stage_dispute|maturation_dispatch\.py',q): return 'stage record tools'
    if re.search(r'gpt_consult|codex |imagegen|delegate ',q): return 'ask GPT or Codex'
    if re.search(r'winbuild|deploy_custom_mods|dotnet|build\.py|refresh\.py|modlist|ModsConfig',q): return 'build and deploy'
    if re.search(r'(sleep \d{2,}|waitfor|until .*sleep|while .*sleep|for .*sleep)',q): return 'wait'
    if re.search(r'game_lock|game_instance|\./game\b|\./bridge\b|bridge (take|release|who)',q): return 'game lock and game state'
    if re.search(r'run_selftests|selftest_|pytest|unittest|validate_patch|code_review_status|_lint\.py',q): return 'run offline tests'
    if re.search(r'testq|test_queue|live_queue|scene|modcheck|validation|proof_|northstar|jawabench|rimbridge|bridge_call|gabp|capture|screenshot|live_',q) and re.search(r'python3|\.py',q): return 'live scene or bridge call'
    if re.search(r'python3? - ?<<|python3? -c|<<',q):
        if re.search(r"write\(|write_text|open\([^)]*['\"]w|json\.dump\(|cat >|tee ",q): return 'inline script that writes'
        return 'inline script that reads'
    if re.match(r'(cat|sed -n|head|tail|jq|less|awk|wc|python3 -m json)',q): return 'read file'
    if re.match(r'(grep|rg|find|ls|tree|stat|file|which)',q): return 'search'
    if re.search(r'git (log|show|diff|status|blame|grep|rev-parse|fetch|ls-)',q): return 'git read'
    if re.search(r'cli\.py|rimflow|owner_rulings|\./pipe|owed\.py|journalctl|systemctl|account_usage|ops_',q): return 'state read (ledger, pipe, units)'
    if re.match(r'(cp|mv|rm|mkdir|rsync|ln|chmod|sed -i|perl -)',q): return 'file move or sed edit'
    if 'python3' in q or '.py' in q: return 'run a project tool'
    return 'bash other'
if __name__=='__main__':
    RT=Counter();RN=Counter();KT=Counter();RK=defaultdict(Counter);KN=Counter()
    for x in S:
        if not x['turns']: continue
        r=role(x);RT[r]+=x['total'];RN[r]+=1
        for t in x['turns']:
            tl=t[2]
            if not tl: ks=['text only']
            else: ks=[kind(a,b) for a,b,_,_ in tl]
            for kk in ks: KT[kk]+=t[0]/len(ks);RK[r][kk]+=t[0]/len(ks);KN[kk]+=1
    T=sum(RT.values())
    for k,v in RT.most_common(40): print('%7.1fM %5.1f%% n=%d  %s'%(v/1e6,100*v/T,RN[k],k))
    print()
    for k,v in KT.most_common(45): print('%7.1fM %5.1f%% calls=%d %s'%(v/1e6,100*v/T,KN[k],k))
    print()
    for r,_ in RT.most_common(14):
        print(r,'; '.join('%s %.0f%%'%(k,100*v/RT[r]) for k,v in RK[r].most_common(12)))
