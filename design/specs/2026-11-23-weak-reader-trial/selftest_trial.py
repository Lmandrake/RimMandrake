"""The parser and the scorer: the four outcomes stay apart. Mutants at the end must each turn a check red."""
import run,score
ok=lambda **k:dict(dict(case="X",model="sonnet",arm="old",n=0,ok=True,parsed=True,told="yes"),**k)
def checks(outcome,parse):
    G={"X":{"sonnet|old|0":"C","sonnet|old|1":"W"}}
    return [("correct",outcome(ok(),G)=="CORRECT"),("wrong",outcome(ok(n=1),G)=="WRONG"),
      ("not_told_even_when_act_graded_right",outcome(ok(told="no"),G)=="NOT_TOLD"),
      ("failed_call",outcome(ok(ok=False,parsed=False,told=None),G)=="FAILED"),
      ("unreadable_is_failed",outcome(ok(parsed=False,told=None),G)=="FAILED"),
      ("ungraded_is_not_wrong",outcome(ok(n=9),G)=="UNGRADED"),
      ("parse_bold",parse("**TOLD:** no\n**ACT:** z\n**WORDS:** none","old")["told"]=="no"),
      ("parse_refusal",not parse("I'm blocked by tool access","old")["parsed"]),
      ("parse_act_without_told",not parse("ACT: q","old")["parsed"]),
      ("parse_two_line_act",parse("TOLD: yes\nACT: a\nb\nWORDS: c","new")["act"]=="a\nb")]
def red(c): return [n for n,v in c if not v]
assert not red(checks(score.outcome,run.parse)),red(checks(score.outcome,run.parse))
def no_told(r,g): return score.outcome(dict(r,told="yes"),g)
def fail_wrong(r,g): o=score.outcome(r,g); return "WRONG" if o=="FAILED" else o
def ungraded_wrong(r,g): o=score.outcome(r,g); return "WRONG" if o=="UNGRADED" else o
for m,want in((no_told,"not_told_even_when_act_graded_right"),(fail_wrong,"failed_call"),(ungraded_wrong,"ungraded_is_not_wrong")):
    assert want in red(checks(m,run.parse)),m.__name__
def lax(t,a): return dict(told="yes",act=t,words=None,parsed=True)
assert {"parse_refusal","parse_act_without_told"}<=set(red(checks(score.outcome,lax)))
print("10 checks green; 4 of 4 mutants red")
