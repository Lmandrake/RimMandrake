import json,concurrent.futures as cf
from llm import *
S=json.load(open("cases_spec.json"))
SYS="You write test situations for software agents that work under written rules. Answer with one JSON object only."
def f(s):
    o=call("opus",SYS,f"""Below: one SECTION of a rule document, one TARGET line in it, and the SOURCE OF TRUTH (what is really right, from the code or the owner). Write one realistic work situation that an agent meets, where the right act turns on the TARGET line.

SECTION (from {s['path']}, heading "{s['head']}")
<<<
{s['old']}
>>>
TARGET: {s['target']}
SOURCE OF TRUTH: {s['source']}

Requirements:
- The situation is 2 to 5 plain sentences, with concrete invented details, and ends with the decision the agent faces. Do not quote or paraphrase the rule. Do not use the rule's own coined terms unless an agent would meet that word in the work itself.
- The right act is decided by the SOURCE OF TRUTH. Where the SECTION and the SOURCE OF TRUTH disagree, the SOURCE OF TRUTH wins.
- There is a plausible wrong act that an agent who does not know the rule, or misreads it, is likely to pick. Common sense alone must not give the right act.
- Say in the situation everything else the agent needs (who the agent is, what it has), so that only the TARGET decides.
- One decision only. The act must be checkable from one or two sentences of the agent.
- If the TARGET cannot carry such a situation, give {{"skip":"why"}}.

JSON keys: "situation", "question" (one short neutral question: what does the agent do?), "key_correct" (the right act, with the parts that an answer must hold to count), "key_wrong" (list of acts that count as wrong), "source_words" (the words of the SOURCE OF TRUTH, or of the SECTION when the source says it is the section, that decide it), "planted_correct" (an agent's answer in its own voice that is right, worded differently from key_correct), "planted_wrong" (an agent's answer in its own voice that is wrong but sounds sensible).""")
    try: d=js(o["text"])
    except Exception as e: d=dict(error=repr(e),raw=o["text"][:500])
    d["case"]=s["case"]; d["_w"]=weighted(o["usage"]); return d
with cf.ThreadPoolExecutor(8) as ex: A=list(ex.map(f,S))
json.dump(A,open("authored.json","w"),indent=1,ensure_ascii=False)
print("weighted",round(sum(a["_w"] for a in A)))
for a in A: print(a["case"],a.get("skip") or a.get("error") or "ok")
