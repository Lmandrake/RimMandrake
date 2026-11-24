"""rerun.py: PASS, FAIL and COULD NOT LOOK stay apart; a section is cut at its own end; a byte change voids a reading."""
import rerun as R
C=[dict(case=i,situation="s",key_correct="k",path="p",head="## H") for i in R.IDS]; SEC={c["case"]:"t" for c in C}
def st(*rows,plants=True): return {R.key(c,"t"):dict(outcomes=list(r),plants_ok=plants) for c,r in zip(C,rows)}
ok=["CORRECT"]*5; nt=["NOT_TOLD"]*5; four=["CORRECT"]*4+["WRONG"]
v=lambda s,sec=SEC:R.verdict(C,s,sec)[0]
assert v(st(ok,ok,ok))==0 and v(st(four,four,four))==0
assert v(st(four,four,["CORRECT"]*3+["WRONG"]*2))==1 and v(st(nt,nt,nt))==1
assert v({})==2 and v(st(ok,ok))==2 and v(st(ok,ok,ok,plants=False))==2 and v(st(ok,ok,ok[:4]))==2
assert v(st(ok,ok,ok[:4]+["FAILED"]))==2 and v(st(ok,ok,ok[:4]+["UNGRADED"]))==2
assert v(st(ok,ok,ok),dict(SEC,**{R.IDS[0]:"t2"}))==2
assert R.section("## A\nx\n## H\na\n```\n# c\n```\nb\n### K\nz","## H")=="a\n```\n# c\n```\nb" and R.section("## A","## H")==""
assert [R.outcome(*x) for x in((0,0,None,None),(1,0,None,None),(1,1,"no","C"),(1,1,"yes","C"),(1,1,"yes","W"),(1,1,"yes",None))]==["FAILED","FAILED","NOT_TOLD","CORRECT","WRONG","UNGRADED"]
print("rerun selftest: all green")
