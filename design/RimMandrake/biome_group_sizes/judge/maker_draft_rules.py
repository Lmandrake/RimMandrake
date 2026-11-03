import json, re, sys, collections
F = json.load(open(sys.argv[1]))
def rng(t):
    if not t or t=='unset': return None
    a,_,b = t.partition('~'); return int(float(a)), int(float(b or a))
def fmt(r): return str(r[0]) if r[0]==r[1] else f"{r[0]}~{r[1]}"
KW_GROUP = re.compile(r'\b(swarm|swarms|school|schools|shoal|flock|flocks|herd|herds|colony|colonies|hive|brood|pod|pods|troop|drove|horde|hordes|mobs?|packs?|clutch|in groups|gregarious|cluster)\b', re.I)
KW_SOLO = re.compile(r'\b(solitary|alone|lone|loner|singly|territorial)\b', re.I)
out = []
for v in F:
    cur = rng(v['wgs']); body = float(v['body'] or 1); desc = v['desc']
    why = []
    if v['canon'] == 'solitary':
        s = (1,1); why.append('canon solitary')
    elif cur and v['wgs'] != 'unset' and not (v['canon']=='herd' and cur[1] <= 1):
        s = cur; why.append('keep today\'s value')
    elif v['canon'] == 'herd' or v['herd'] == 'true':
        s = (2,5) if body < 2 else (2,4); why.append('herd (canon or herdAnimal) with no size')
    elif KW_GROUP.search(desc) and not KW_SOLO.search(desc):
        s = (3,8) if body < 0.5 else (2,5); why.append(f'description says "{KW_GROUP.search(desc).group(0)}"')
    elif v['predator'] == 'true':
        s = (1,1) if body >= 1 else (1,2); why.append('predator, no grouping cue')
    else:
        s = (1,3) if body < 0.6 else (1,2) if body < 2 else (1,1); why.append(f'no grouping cue, body {body}')
    out.append(dict(kind=v['kind'], today=v['wgs'], draft=fmt(s), why='; '.join(why)))
json.dump(out, open(sys.argv[2],'w'), indent=1)
c = collections.Counter(o['why'].split(';')[0][:30] for o in out); print(c)
print('changed', sum(1 for o in out if rng(o['today']) != rng(o['draft'])))
