"""Distinct error/exception signatures in the load segment (lines after the menu-stage copy). usage: delta.py menu.txt full.txt"""
import sys,re,collections
a=open(sys.argv[1],encoding='utf-8',errors='replace').read().splitlines(); b=open(sys.argv[2],encoding='utf-8',errors='replace').read().splitlines()
seg=b[len(a):]; c=collections.Counter()
pat=re.compile(r"Exception|Could not|Failed to|Error|error while|Tried loading")
for l in seg:
    if pat.search(l) and not l.startswith(("  at ","(Filename","UnityEngine.","Verse.Log","RimWorld.","System.")):
        c[re.sub(r"\d+","#",l)[:150]]+=1
print("segment lines",len(seg)); [print(n,s) for s,n in c.most_common(40)]
