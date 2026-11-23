import json,concurrent.futures as cf
from llm import *
S={s["case"]:s for s in json.load(open("cases_spec.json"))}; A=[a for a in json.load(open("authored.json")) if "situation" in a]
SYS="You check answer keys. Answer with one JSON object only."
def f(a):
    s=S[a["case"]]; own=s["kind"] in("STYLE","CONTROL")
    o=call("opus",SYS,f"""SOURCE OF TRUTH
<<<
{s['source']}
{('SECTION:'+chr(10)+s['old']) if own else ''}
>>>
SITUATION: {a['situation']}
QUESTION: {a['question']}
KEY, right act: {a['key_correct']}
KEY, wrong acts: {a['key_wrong']}

1. Does the right act follow from the SOURCE OF TRUTH{' (the section)' if own else ''}, with nothing added that the source does not support?
2. Is a listed wrong act really wrong by the source?
3. Does the key ask for a detail (a path, a flag, a name, a second step) that the source does not force for this question?
JSON: {{"follows":true|false,"wrong_is_wrong":true|false,"extra_detail":null or "...","why":"one sentence"}}""")
    try: d=js(o["text"])
    except Exception as e: d=dict(error=repr(e))
    d["case"]=a["case"]; d["_w"]=weighted(o["usage"]); return d
with cf.ThreadPoolExecutor(8) as ex: K=list(ex.map(f,A))
json.dump(K,open("keycheck.json","w"),indent=1)
print("weighted",round(sum(k["_w"] for k in K)))
for k in K: print(k["case"],k.get("follows"),k.get("wrong_is_wrong"),"|",(k.get("extra_detail") or "")[:140],"|",k.get("error") or k["why"][:180] if not(k.get("follows") and k.get("wrong_is_wrong") and not k.get("extra_detail")) else "")
