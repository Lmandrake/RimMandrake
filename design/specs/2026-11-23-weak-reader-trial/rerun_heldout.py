"""A second, held-out situation for each of rerun.py's three cases. Fresh Opus author and key checker; neither sees the new text.
The author gets the OLD section (cases.json "old") and the source of truth, as in author.py, plus the pilot situation to differ from."""
import json,rerun,llm,concurrent.futures as cf
SRC={"CORRECTION_who_broadcasts":" broadcast.py's own page: it is for a change of game state that a window must know at that moment; used mindfully, since the owner said game-state broadcasts 'burn tokens unnecessarily and rarely inform'. The act is the Conductor window's alone; it is not owed on every change."}
def f(c):
    src=c["source"]+SRC.get(c["case"],"")
    o=llm.call("opus","You write test situations for software agents that work under written rules. Answer with one JSON object only.",f"""SECTION (from {c['path']}, heading "{c['head']}")
<<<
{c['old']}
>>>
TARGET: {c['target']}
SOURCE OF TRUTH: {src}
A SITUATION THAT EXISTS ALREADY: {c['situation']}
ITS RIGHT ACT: {c['key_correct']}

Write one NEW realistic work situation on the same TARGET that differs in kind from the one that exists: other facts, another moment, another temptation, and where the source allows it a different right act (for example another tier, or an agent to whom the permission does not apply).
- 2 to 5 plain sentences with concrete invented details, ending with the decision the agent faces. Do not quote or paraphrase the rule.
- The SOURCE OF TRUTH decides the right act; where the SECTION disagrees, the SOURCE wins. Common sense alone must not give it. One decision only, checkable from one or two sentences.
- Say who the agent is and what it has, so that only the TARGET decides.
JSON keys: "situation","question","key_correct" (with the parts an answer must hold),"key_wrong" (list),"planted_correct" (an agent's right answer in its own voice, other words),"planted_wrong" (a sensible wrong one).""")
    d=llm.js(o["text"])
    k=llm.js(llm.call("opus","You check answer keys. Answer with one JSON object only.",f"""SOURCE OF TRUTH
<<<
{src}
>>>
SITUATION: {d['situation']}
QUESTION: {d['question']}
KEY, right act: {d['key_correct']}
KEY, wrong acts: {d['key_wrong']}
Does the right act follow from the source with nothing added, and are the wrong acts wrong by the source?
JSON: {{"follows":true|false,"wrong_is_wrong":true|false,"why":"one sentence"}}""")["text"])
    return dict({k2:c[k2] for k2 in("path","head")},case=c["case"]+"_HELDOUT",keycheck=k,**d)
with cf.ThreadPoolExecutor(3) as ex: H=list(ex.map(f,rerun.load()))
json.dump(H,open("rerun_heldout.json","w"),indent=1,ensure_ascii=False)
for h in H: print(h["case"],h["keycheck"],"\n ",h["situation"],"\n  KEY:",h["key_correct"])
