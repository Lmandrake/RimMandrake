import re,sys,collections
for m in sys.argv[1:]:
    c=collections.Counter(); fails=[]; seen=set()
    for l in open("Transient/l2p2_%s.log"%m,errors="replace"):
        l=l.rstrip("\r\n")
        r=re.match(r"\[[^\]]+\] \d\d:\d\d:\d\d (\S+) (PASS|FAIL|UNMEASURED)\b ?(.*)",l)
        if r:
            c[r.group(2)]+=1
            if r.group(2)=="FAIL": fails.append((r.group(1),r.group(3)[:500]))
    print(m,dict(c))
    for f in fails: print("  FAIL",f)
