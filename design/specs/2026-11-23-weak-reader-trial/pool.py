#!/usr/bin/env python3
"""Pool of old/new section pairs. A file's old text is `git show <base>:<path>`; its new text is `git show NEW:<path>`."""
import subprocess,re,json,sys,difflib
NEW="4b95f0e62a"
B={}
def add(base,*paths):
    for p in paths: B[p]=base
add("cf7ef42ad2","design/RimMandrake/biome_rulings.md")
add("d4d5729aeb","infrastructure/agents/CHARTER.md","infrastructure/agents/Agent_Policy.md","src/RimMandrake/rimflow/roles/operations.md")
add("25c18fb733","src/RimMandrake/rimflow/roles/conductor.md","src/RimMandrake/rimflow/roles/conductor_restart.md","infrastructure/agents/CONDUCTOR.md")
add("9308e4fc60","design/RimMandrake/delegation_policy.md","design/RimMandrake/debug_process.md")
add("d41afe8aee","src/RimMandrake/rimflow/roles/designer.md","src/RimMandrake/rimflow/roles/designer_grounding.md","src/RimMandrake/rimflow/roles/designer_dialogue.md","src/RimMandrake/rimflow/roles/designer_write.md")
add("4391e9d6e3","src/RimMandrake/rimflow/roles/designer_exam.md","src/RimMandrake/rimflow/roles/designer_examples.md","src/RimMandrake/rimflow/roles/designer_cleanse.md")
add("9be9c8fb34","design/RimMandrake/GIT_WORKFLOW.md","infrastructure/GAME_STATE_WORKFLOW.md","PURPOSE.md")
add("beebcb2c06","src/RimMandrake/rimflow/roles/runner_options.md")
add("e6dd7e02a2","infrastructure/state/facts/instrument_traps.md")
add("6d6f1822bc","design/specs/2026-11-13-maturation-pipeline.md")
add("5d5cf515ce","infrastructure/STRUCTURE.md","infrastructure/VALIDATION_LADDER.md","LEXICON.md")
add("9850da2ca2","src/RimMandrake/rimflow/roles/fable_rescue.md","src/RimMandrake/rimflow/roles/walk_brief.md","src/RimMandrake/rimflow/roles/criteria_fixer.md")
add("eedce76251","skills/clone-landing-commits/SKILL.md")
add("5d750f4059","skills/live-debugging-proof-harness/SKILL.md")
add("2b0248fa7f","skills/rimbridge/SKILL.md")
add("7256ba3831","skills/rimbridge-companion/SKILL.md")
add("2c4b78e144","infrastructure/state/facts/tool_traps.md")
add("2093cc9e10","infrastructure/state/facts/distress_signals.md","infrastructure/state/facts/biome_paint_list.md")
add("97b1d5273d","design/RimMandrake/standing_rulings.md")
add("bc042932f1","infrastructure/state/facts/operations.md")
def show(c,p):
    r=subprocess.run(["git","show",f"{c}:{p}"],capture_output=True,text=True)
    return r.stdout if r.returncode==0 else None
def sections(t):
    """heading -> body, whole section down to the next heading of any level; duplicate headings get #n"""
    out={};cur="(top)";buf=[];fence=False
    def put():
        k=cur;n=2
        while k in out: k=f"{cur} #{n}";n+=1
        out[k]="\n".join(buf).strip()
    for l in t.split("\n"):
        if l.startswith("```"): fence=not fence
        if not fence and re.match(r"#{1,5} ",l):
            put();cur=l.strip();buf=[]
        else: buf.append(l)
    put();return out
def norm(h): return re.sub(r"[^a-z0-9 ]","",h.lower()).strip()
def pool():
    rows=[]
    for p,b in B.items():
        o,n=show(b,p),show(NEW,p)
        if o is None or n is None: rows.append(dict(path=p,base=b,error="missing old" if o is None else "missing new"));continue
        so,sn=sections(o),sections(n)
        nn={norm(k):k for k in sn}
        for k,t in so.items():
            k2=nn.get(norm(k))
            if k2 is None: continue
            t2=sn[k2]
            rows.append(dict(path=p,base=b,head=k,old=t,new=t2,ow=len(t.split()),nw=len(t2.split()),
                ratio=round(difflib.SequenceMatcher(None,t.split(),t2.split(),autojunk=False).ratio(),3)))
    return rows
if __name__=="__main__":
    rows=pool()
    bad=[r for r in rows if "error" in r]
    print("errors",bad)
    ok=[r for r in rows if "error" not in r]
    print(len(ok),"pairs; identical",sum(r["old"]==r["new"] and r["ow"]>=60 for r in ok))
    if len(sys.argv)>1: json.dump(ok,open(sys.argv[1],"w"),indent=1)
    for r in ok:
        if 60<=r["ow"]<=450: print(r["path"].split("/")[-1],"|",r["head"][:60],"|",r["ow"],r["nw"],r["ratio"])
