import json,random,re,concurrent.futures as cf
from llm import *
P=json.load(open(W+"/pool.json"))
skip=("facts/","PURPOSE","LEXICON","STRUCTURE","designer_examples")
c=[r for r in P if 60<=r["ow"]<=450 and .45<=r["ratio"]<=.93 and not any(s in r["path"] for s in skip) and r["head"]!="(top)"]
random.Random(20261123).shuffle(c); c=c[:36]
SYS="You compare two versions of one section of a rule document for software agents. Answer with one JSON object only."
def f(r):
    o=call("opus",SYS,f"""VERSION A
<<<
{r['old']}
>>>
VERSION B
<<<
{r['new']}
>>>
Classify what B changed against A. Report every change that applies:
- "binding": B defines, glosses or names a term, pronoun or reference that A left undefined.
- "correction": B changes, deletes or adds a fact, a permission, a number, a command, a pointer or an instruction.
- "style": sentences became shorter, active or split, or were reordered.
Then find in A one sentence that (1) tells an agent to do or not to do something, (2) B rewrote a lot in style only, with the same meaning and the same terms. Pick the sentence that B rewrote the most. Copy it word for word from A.
JSON: {{"binding":[short strings],"correction":[short strings],"style":true|false,"only_style":true|false,"target_sentence_in_A":"..." or null,"same_sentence_in_B":"..." or null}}""")
    try: return dict(path=r["path"],head=r["head"],cls=js(o["text"]),usage=o["usage"])
    except Exception as e: return dict(path=r["path"],head=r["head"],error=repr(e),raw=o)
with cf.ThreadPoolExecutor(8) as ex: out=list(ex.map(f,c))
json.dump(out,open(W+"/classify.json","w"),indent=1)
print("weighted",round(sum(weighted(o.get("usage")) for o in out)))
for o in out:
    k=o.get("cls",{}); print(o["path"].split("/")[-1],"|",o["head"][:40],"| only_style",k.get("only_style"),"| b",len(k.get("binding",[])),"c",len(k.get("correction",[])),o.get("error",""))
