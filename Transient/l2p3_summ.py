import re,sys
m=sys.argv[1]
c={"PASS":0,"FAIL":0,"UNMEASURED":0}; fails=[]
for l in open("Transient/l2p2_%s.log"%m,encoding="utf-8",errors="replace"):
    r=re.match(r"\[[\w-]+\] \d\d:\d\d:\d\d (\S+) (PASS|FAIL|UNMEASURED)\b ?(.*)",l)
    if r:
        c[r.group(2)]+=1
        if r.group(2)=="FAIL": fails.append((r.group(1),r.group(3)[:int(sys.argv[2]) if len(sys.argv)>2 else 260]))
print(m,c); 
for f in fails: print(" FAIL",f[0],"::",f[1])
