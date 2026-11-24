import re,pickle,kinds
from collections import Counter,defaultdict
S=pickle.load(open('scan3.pkl','rb'));seen=set()
A=Counter();N=Counter();R=defaultdict(Counter);names=Counter()
for x in S:
    ro=kinds.role(x)
    for i,t in enumerate(x['turns']):
        key=(t[4],round(t[0],3))
        if key in seen: continue
        seen.add(key)
        if i==0 or not t[2]: continue
        cm=' ;; '.join(c or '' for _,c,*_ in t[2]);hd=' '.join(h or '' for *_,h in t[2])
        def add(k):
            A[k]+=t[0];N[k]+=1;R[k][ro]+=t[0]
        live=ro.startswith('mod:') or ro in('art work','judge (coverage, look, other)')
        if live and re.search(r'cat > \S+\.(py|sh) <<',cm): 
            add('writes a throwaway script (live and judge roles)')
            for m in re.finditer(r'cat > (\S+)\.(py|sh) <<',cm): names[re.sub(r'.*/','',m.group(1))]+=1
        if live and re.search(r'cp \S*(visit|cycle)_\d|sed -e .*visit|visit_\d+/scripts|cycle_\d+/lane2',cm): add('touches per-visit or per-cycle copied scripts')
        if live and re.search(r'SUMMARY\.md|rows\.jsonl|make_rows|strange\.jsonl|overrides\.json|chain_rows|visit_rows|scene_rows_add|polish\.md',cm): add('writes or reads visit/cycle records')
        if ro in('mod: in-game driver',) and re.search(r'game_instance|modset_builder|deploy_custom|modlist_swap|build\.py|winbuild|game_lock|bridge (take|release)|host_guard|HOST_GUARD|modset_swaps|ModsConfig',cm): add('driver: get or keep the game up')
        if live and re.search(r'from PIL|import Image',cm): add('PIL crops, sheets')
        if ro in('Operations role','Conductor role (quick checks)'):
            if re.search(r'status\.json|series/|told\.jsonl|incidents|alarms\.json|digest\.md|ops_watch|told',cm) or re.search(r'grep [^|]*src/',cm): add('ops: reads readings and metric definitions')
            if re.search(r'\back\b|incident-line|rimflow note|cli\.py note|conductor/log',cm): add('ops: writes ack, line, note')
for k,v in A.most_common(): print('%6.1fM n=%d %s | %s'%(v/1e6,N[k],k,'; '.join('%s %.1f'%(a[:26],b/1e6) for a,b in R[k].most_common(6))))
print(names.most_common(25))
