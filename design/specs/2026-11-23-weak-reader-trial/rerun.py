"""Rerun of the three silent cases on the text of today (RIMMANDRAKE_STATE_THREE_RULES_THE_CORRECTION_LEFT_SILENT_READERS_SCORED_ZERO).

  rerun.py run [--ref REF] [--cases FILE]   5 fresh Sonnet readers for each case, then one blind Opus grade for each case.
                                            The text is the working tree's section, or REF's. Writes rerun.json.
  rerun.py check                            reads only rerun.json and the sections; makes no model call.
        exit 0: the recorded reading of these exact section bytes is at the bar; 1: it is under the bar;
        2: could not look (no reading of these bytes, a failed call, an ungraded answer, or a plant graded wrong).
The readers, their prompt, the parser, the grader prompt and the scorer are the pilot's (run.py, grade.py, score.py)."""
import concurrent.futures as cf,hashlib,json,os,random,re,subprocess,sys
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"../../.."))
OUT=os.path.join(HERE,"rerun.json"); N=5; BAR=12
IDS=("CORRECTION_digest_by_hand","CORRECTION_jawa_folder","CORRECTION_who_broadcasts")
def section(text,head):
    """The body of one heading, cut as the pilot cut it (pool.sections)."""
    out=[];on=False;fence=False;want=re.sub(r"^#+\s*","",head)
    for l in text.split("\n"):
        if l.startswith("```"): fence=not fence
        if not fence and re.match(r"#{1,5} ",l):
            if on: break
            on=re.sub(r"^#+\s*","",l).strip()==want; continue
        if on: out.append(l)
    return "\n".join(out).strip()
def text_of(c,ref=None):
    if ref: t=subprocess.run(["git","-C",ROOT,"show",f"{ref}:{c['path']}"],capture_output=True,text=True,check=True).stdout
    else: t=open(os.path.join(ROOT,c["path"]),encoding="utf-8").read()
    s=section(t,c["head"])
    if not s: raise SystemExit(f"could not look: {c['path']} has no section {c['head']!r}")
    return s
def key(c,s): return c["case"]+"|"+hashlib.sha256((s+"\0"+c["situation"]+"\0"+c["key_correct"]).encode()).hexdigest()[:16]
def verdict(cases,store,sec):
    """-> (exit code, lines). Pure, so the selftest can plant each fault."""
    tot=0;lines=[];blind=False
    for c in cases:
        r=store.get(key(c,sec[c["case"]]))
        if not r: lines.append(f"{c['case']}: UNMEASURED, no reading of these bytes (rerun.py run)"); blind=True; continue
        o=r["outcomes"]; bad=[x for x in o if x in("FAILED","UNGRADED")]
        if len(o)!=N or bad or not r["plants_ok"]:
            lines.append(f"{c['case']}: UNMEASURED, {len(bad)} of {len(o)} not readable or not graded, plants_ok={r['plants_ok']}"); blind=True; continue
        k=o.count("CORRECT"); tot+=k
        lines.append(f"{c['case']}: {k} of {N} correct, {o.count('WRONG')} wrong, {o.count('NOT_TOLD')} not told")
    if blind: return 2,lines+["COULD NOT LOOK"]
    return (0 if tot>=BAR else 1),lines+[f"{'PASS' if tot>=BAR else 'FAIL'}: {tot} of {N*len(cases)} correct, bar {BAR}"]
def load(f=None):
    cs=json.load(open(f or os.path.join(HERE,"cases.json"),encoding="utf-8"))
    return [c for c in cs if f or c["case"] in IDS]
def store(): return json.load(open(OUT)) if os.path.exists(OUT) else {}
def outcome(ok,parsed,told,grade):
    if not ok or not parsed: return "FAILED"
    if told=="no": return "NOT_TOLD"
    return {"C":"CORRECT","W":"WRONG"}.get(grade,"UNGRADED")
def run(cases,ref):
    sys.path.insert(0,HERE); import llm,run as R
    secs={c["case"]:text_of(c,ref) for c in cases}
    def read(j):
        c,n=j; o=llm.call("sonnet",R.SYS,R.prompt(dict(c,new=secs[c["case"]]),"new"))
        p=R.parse(o["text"],"new") if o["ok"] else dict(told=None,act=None,words=None,parsed=False)
        return dict(case=c["case"],n=n,ok=o["ok"],error=o["error"],model=o["model"],w=llm.weighted(o["usage"]),**p)
    with cf.ThreadPoolExecutor(8) as ex: A=list(ex.map(read,[(c,n) for c in cases for n in range(N)]))
    def grade(c):
        it=[(str(a["n"]),a["act"]) for a in A if a["case"]==c["case"] and a["parsed"]]
        it+=[("plant_correct",c["planted_correct"]),("plant_wrong",c["planted_wrong"])]+[("plant_listed%d"%i,w) for i,w in enumerate(c["key_wrong"][:2])]
        random.Random(c["case"]).shuffle(it)
        body="\n".join(f"[{i+1}] {' '.join(str(t).split())}" for i,(k,t) in enumerate(it))
        o=llm.call("opus","You grade short answers against an answer key. Grade only what the answer says the agent does. Answer with one JSON object only.",f"""SITUATION: {c['situation']}
QUESTION: {c['question']}
KEY, right act: {c['key_correct']}
KEY, wrong acts: {json.dumps(c['key_wrong'],ensure_ascii=False)}

ANSWERS
{body}

For each answer say "C" if the act holds what the key asks for, else "W". An answer that leaves the choice open, gives a different act, or misses a part that the key says an answer must hold is "W". Extra steps that do not contradict the key do not make it "W". Ignore the wording and the length.
JSON: {{"grades":{{"1":"C","2":"W",...}}}} with one entry for each of the {len(it)} answers.""")
        try:
            g=llm.js(o["text"])["grades"]; assert len(g)==len(it) and set(g.values())<={"C","W"}
            return {k:g[str(i+1)] for i,(k,t) in enumerate(it)},llm.weighted(o["usage"])
        except Exception as e: print("grade failed",c["case"],repr(e)); return {},llm.weighted(o["usage"])
    with cf.ThreadPoolExecutor(3) as ex: G=dict(zip([c["case"] for c in cases],ex.map(grade,cases)))
    S=store()
    for c in cases:
        g=G[c["case"]][0]; mine=[a for a in A if a["case"]==c["case"]]
        plants=[(k,v) for k,v in g.items() if k.startswith("plant")]
        S[key(c,secs[c["case"]])]=dict(ref=ref or "working tree",plants_ok=len(plants)>=3 and all(v==("C" if k=="plant_correct" else "W") for k,v in plants),
            outcomes=[outcome(a["ok"],a["parsed"],a["told"],g.get(str(a["n"]))) for a in mine],
            answers=[dict({k:a[k] for k in("n","ok","error","model","told","act","words")},grade=g.get(str(a["n"]))) for a in mine],
            weighted_v2=round(sum(a["w"] for a in mine)+G[c["case"]][1]))
    json.dump(S,open(OUT,"w"),indent=1,ensure_ascii=False)
    print("weighted_v2",round(sum(a["w"] for a in A)+sum(v[1] for v in G.values())))
    rc,l=verdict(cases,S,secs); print("\n".join(l)); return rc
if __name__=="__main__":
    a=sys.argv[1:]; opt=lambda f:a[a.index(f)+1] if f in a else None
    cs=load(opt("--cases"))
    if a[:1]==["run"]: sys.exit(run(cs,opt("--ref")))
    if a[:1]==["check"]:
        rc,l=verdict(cs,store(),{c["case"]:text_of(c) for c in cs}); print("\n".join(l)); sys.exit(rc)
    print(__doc__); sys.exit(2)
