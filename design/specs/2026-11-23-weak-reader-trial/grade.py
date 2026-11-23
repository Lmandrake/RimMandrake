"""Grade each ACT against the key, blind: no arm, model, quoted words. One call per case, shuffled, plants mixed in.
NOT_TOLD (reader's own mark) and FAILED (no readable answer) are set by this program, not by the grader.
The grader grades every ACT; score.py then reads the TOLD mark."""
import json,random,concurrent.futures as cf,os,sys
from llm import *
CASES=json.load(open("cases.json")); R=[json.loads(l) for l in open("raw/answers.jsonl")]
SYS="You grade short answers against an answer key. Grade only what the answer says the agent does. Answer with one JSON object only."
def items(c,only_plants):
    it=[]
    if not only_plants:
        for r in R:
            if r["case"]==c["case"] and r["parsed"]: it.append((f"{r['model']}|{r['arm']}|{r['n']}",r["act"]))
    other=CASES[(CASES.index(c)+7)%len(CASES)]
    it+= [("plant_correct",c["planted_correct"]),("plant_wrong",c["planted_wrong"]),("plant_other",other["planted_correct"])]
    it+= [("plant_wrong_listed%d"%i,w) for i,w in enumerate((c["key_wrong"] if isinstance(c["key_wrong"],list) else [c["key_wrong"]])[:2])]
    random.Random(c["case"]).shuffle(it); return it
def f(a):
    c,op=a; it=items(c,op)
    body="\n".join(f"[{i+1}] {' '.join(str(t).split())}" for i,(k,t) in enumerate(it))
    o=call("opus",SYS,f"""SITUATION: {c['situation']}
QUESTION: {c['question']}
KEY, right act: {c['key_correct']}
KEY, wrong acts: {json.dumps(c['key_wrong'],ensure_ascii=False)}

ANSWERS
{body}

For each answer say "C" if the act holds what the key asks for, else "W". An answer that leaves the choice open, gives a different act, or misses a part that the key says an answer must hold is "W". Extra steps that do not contradict the key do not make it "W". Ignore the wording and the length.
JSON: {{"grades":{{"1":"C","2":"W",...}}}} with one entry for each of the {len(it)} answers.""")
    try:
        g=js(o["text"])["grades"]; assert len(g)==len(it) and set(g.values())<={"C","W"}
        return dict(case=c["case"],grades={k:g[str(i+1)] for i,(k,t) in enumerate(it)},w=weighted(o["usage"]))
    except Exception as e: return dict(case=c["case"],error=repr(e),raw=o["text"][:800],w=weighted(o["usage"]))
op=sys.argv[1]=="plants"
with cf.ThreadPoolExecutor(8) as ex: G=list(ex.map(f,[(c,op) for c in CASES]))
json.dump(G,open("raw/grades_%s.json"%sys.argv[1],"w"),indent=1)
print("errors",[g["case"] for g in G if "error" in g],"weighted",round(sum(g["w"] for g in G)))
tot=ok=0;bad=[]
for g in G:
    for k,v in g.get("grades",{}).items():
        if k.startswith("plant"):
            tot+=1; want="C" if k=="plant_correct" else "W"; ok+=v==want
            if v!=want: bad.append((g["case"],k,v))
print("plants as planted %d of %d"%(ok,tot),bad)
