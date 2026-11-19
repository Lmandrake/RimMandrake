#!/usr/bin/env python3
"""Row and source check for one rewrite_choices.md (second reader, 2026-11-18). Offline, documents only."""
import re,sys
def check(path,probe="made-up source name zzqx"):
    t=open(path,encoding='utf-8').read()
    m=re.search(r'^## Every idea, row by row\n(.*?)(?=^## )',t,re.S|re.M)
    if not m: return None
    body=m.group(1)
    src_par=body.split('\n\n### ')[0]
    names=re.findall(r'\*([^*\n]+?)\*\s*=',src_par)
    names=[n for n in names]
    rows=[];bad=[];section='';sec_rows={}
    for line in body.splitlines():
        if line.startswith('### '): section=line[4:]
        if not line.startswith('| ') or line.startswith('| idea') : continue
        cells=[c.strip() for c in re.split(r'(?<!\\)\|',line.strip().strip('|'))]
        if len(cells)!=5: bad.append(line[:60]); continue
        rows.append((section,cells)); sec_rows[section]=sec_rows.get(section,0)+1
    def kind(w):
        w=w.lower()
        if w.startswith('lost'): return 'lost'
        if w.startswith('moved'): return 'moved'
        if w.startswith('kept, reshaped'): return 'reshaped'
        if w.startswith('folded'): return 'folded'
        if w.startswith('kept'): return 'kept'
        return 'other'
    counts={}
    for s,c in rows: counts[kind(c[2])]=counts.get(kind(c[2]),0)+1
    partial_moves=sum(1 for s,c in rows if kind(c[2])!='moved' and 'moved' in c[2].lower())
    empty=[c[0][:50] for s,c in rows if not c[2]]
    allsrc=' ; '.join(c[1] for s,c in rows).lower()
    missing=[n for n in names+[probe] if n.lower() not in allsrc and not any(w in allsrc for w in [n.lower().rstrip('s')])]
    noreason=[c[0][:50] for s,c in rows if kind(c[2]) in('lost','moved','reshaped') and not c[3] and not c[4]]
    added=sum(v for k,v in sec_rows.items() if k.lower().startswith('added by the second reader'))
    return dict(rows=len(rows),added=added,first=len(rows)-added,counts=counts,partial_moves=partial_moves,bad=bad,empty=empty,names=len(names),missing=missing,probe_seen=probe in missing,noreason=len(noreason))
if __name__=='__main__':
    rc=0
    for p in sys.argv[1:]:
        r=check(p)
        ok = r and not r['bad'] and not r['empty'] and r['probe_seen'] and [m for m in r['missing'] if 'zzqx' not in m]==[]
        print(p); print('  ',r); print('   VERDICT:', 'PASS' if ok else 'FAIL')
        if not ok: rc=1
    sys.exit(rc)
