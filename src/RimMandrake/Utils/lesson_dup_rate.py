#!/usr/bin/env python3
"""lesson_dup_rate.py - share of lessons filed in a window that have an EARLIER lesson at TF-IDF cosine >= THR (a re-filed lesson).

    python3 src/RimMandrake/Utils/lesson_dup_rate.py infrastructure/state/lessons START END THR [--list]

START and END are dates, YYYY-MM-DD or YYYYMMDD; a lesson's date is its file-name stamp. --list prints each twin pair.
Exit 0 with the count; exit 2 when the folder holds no lesson (could not look, never a rate of 0%).
Made by Crystallize 2026-W47 (sweeps lane) for the criterion of `lessons.py add` refusing a near-twin (commit 9cb6834d0e):
<= 1% in the 14 days after 2026-11-19. Moved into the repo by Crystallize 2026W48: kept in agent storage, it compared
dashed dates with YYYYMMDD stamps and read 0 lessons in every window, silently. selftest_crystallize_instruments.py.
"""
import sys,json,importlib.util,collections,math,re
from pathlib import Path
d=Path(sys.argv[1]); start=sys.argv[2].replace("-",""); end=sys.argv[3].replace("-","");  # 2026W48: dashed dates read 0 lessons before
thr=float(sys.argv[4])
docs={f.name:f.read_text(errors="replace") for f in sorted(d.glob("*.md")) if f.name!="README.md"}
def stamp(n):
    m=re.match(r"(\d{8})T",n) or re.match(r"(\d{4})-(\d{2})-(\d{2})",n)
    return "".join(m.groups()) if m else None
STOP=set("the a an and or of to in is it its on for be by with as at that this not from are was were when what which who but if then so no any all one has have had do does did can will would should must never always only than into out up their them they there these those each every via per our we he his you your same also more most other just".split())
def toks(t): return [x.strip(".-/") for x in re.findall(r"[a-z_][a-z0-9_\.\-/]{2,}",t.lower()) if x not in STOP]
tf={n:collections.Counter(toks(t)) for n,t in docs.items()}; df=collections.Counter(); [df.update(set(c)) for c in tf.values()]; N=len(docs)
vec={}
for n,c in tf.items():
    v={w:(1+math.log(k))*math.log(N/df[w]) for w,k in c.items() if 1<df[w]<N*0.2}; s=math.sqrt(sum(x*x for x in v.values())) or 1; vec[n]={w:x/s for w,x in v.items()}
win=[n for n in docs if stamp(n) and start<=stamp(n)<=end]; hit=0
if not docs:
    print("COULD NOT LOOK: no lesson files in %s" % d); sys.exit(2)
for a in win:
    best=max((sum(x*vec[b].get(w,0) for w,x in vec[a].items()) for b in docs if stamp(b) and stamp(b)<stamp(a)),default=0)
    hit+= best>=thr
    if best>=thr and "--list" in sys.argv:
        print("TWIN %.2f %s" % (best, a))
print(f"window {start}..{end}: {len(win)} lessons, {hit} with an earlier twin at cos>={thr} ({100*hit/max(1,len(win)):.0f}%)")
