import json,re
P=json.load(open("/mnt/d/ClaudeWork/scratch/weak_reader_trial/pool.json"))
t=open("../2026-11-19-plain-english-rule-docs/undefined_terms_and_conflicts.md").read().split("## Table 2")[0]
n=0
for l in t.split("\n"):
    c=[x.strip() for x in l.split("|")][1:-1]
    if len(c)!=5 or c[0] in("file","---"): continue
    f=re.findall(r"[\w/.\-]+\.md",c[0]); q=re.findall(r'"([^"]+)"',c[1]) or [c[1]]
    for r in P:
        if any(r["path"].endswith(x.split("/")[-1]) for x in f):
            for s in q:
                for piece in s.split("…"):
                    piece=piece.strip().strip("`")
                    if len(piece)>3 and piece.lower() in re.sub(r"\s+"," ",r["old"]).lower():
                        print(c[2][:8],"|",r["path"].split("/")[-1],"|",r["head"][:45],"|",piece[:50],"| old",r["ow"],"| still in new:",piece.lower() in re.sub(r"\s+"," ",r["new"]).lower());n+=1
print(n)
