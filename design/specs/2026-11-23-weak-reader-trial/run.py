"""Run the readers: each answer is one fresh call with one text (or none) and one situation. Resumable; appends raw/answers.jsonl."""
import json,os,re,sys,random,threading,concurrent.futures as cf
from llm import *
OUT="raw/answers.jsonl"
PLAN=[("sonnet","old",5),("sonnet","new",5),("sonnet","none",3),("opus","old",2),("opus","new",2)]
SYS="You are a software agent at work on a RimWorld mod project. The project has written rules. Follow them."
FMT="""Answer in exactly three lines:
TOLD: yes or no (does the rule text tell you what to do here? Write no if the rule text does not settle it)
ACT: what you do, in one to three sentences
WORDS: the words of the rule text that tell you (or none)"""
def prompt(c,arm):
    if arm=="none":
        return f"SITUATION\n{c['situation']}\n\nQUESTION: {c['question']}\n\nYou have no rule text for this. Answer in exactly one line:\nACT: what you do, in one to three sentences"
    return f"RULE TEXT (from {c['path']}, section \"{c['head']}\")\n<<<\n{c[arm]}\n>>>\n\nSITUATION\n{c['situation']}\n\nQUESTION: {c['question']}\n\n{FMT}"
def parse(text,arm):
    t=re.sub(r"\*\*","",text)
    m=re.search(r"(?:^|\n)\s*ACT:\s*(.+?)(?=\n\s*(?:WORDS|TOLD):|\Z)",t,re.S); act=m.group(1).strip() if m else None
    told=re.search(r"(?:^|\n)\s*TOLD:\s*(yes|no)\b",t,re.I)
    w=re.search(r"(?:^|\n)\s*WORDS:\s*(.+)",t,re.S)
    if arm=="none": return dict(told=None,act=act,words=None,parsed=act is not None)
    return dict(told=told.group(1).lower() if told else None,act=act,words=w.group(1).strip() if w else None,parsed=bool(act and told))
def main():
    cases=json.load(open("cases.json")); os.makedirs("raw",exist_ok=True)
    done=set()
    if os.path.exists(OUT):
        for l in open(OUT):
            d=json.loads(l)
            if d["ok"]: done.add((d["case"],d["model"],d["arm"],d["n"]))
    jobs=[(c,m,a,n) for c in cases for m,a,k in PLAN for n in range(k) if (c["case"],m,a,n) not in done]
    random.Random(7).shuffle(jobs); lock=threading.Lock(); print(len(jobs),"jobs",flush=True)
    def f(j):
        c,m,a,n=j; o=call(m,SYS,prompt(c,a)); p=parse(o["text"],a) if o["ok"] else dict(told=None,act=None,words=None,parsed=False)
        rec=dict(case=c["case"],model=m,arm=a,n=n,ok=o["ok"],error=o["error"],model_id=o["model"],usage=o["usage"],text=o["text"],**p)
        with lock: open(OUT,"a").write(json.dumps(rec,ensure_ascii=False)+"\n")
    with cf.ThreadPoolExecutor(10) as ex: list(ex.map(f,jobs))
if __name__=="__main__": main()
