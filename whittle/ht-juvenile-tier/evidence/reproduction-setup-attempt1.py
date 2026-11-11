"""Reproduce preserved pre-fix source model; does not claim a compiled/live pre-fix run."""
from pathlib import Path
import hashlib
import json
import re

here=Path(__file__).resolve().parent
before=here/'before'
current=Path(__file__).resolve().parents[4]/'src/RimMandrake/HugeThings/Source'
u=(before/'TitanicTierUtility.cs').read_text()
k=(before/'RM_TitanicKernel.cs').read_text()
p=(before/'TitanPassage.cs').read_text()

def method(text,name):
    # Brace-balanced body allows independent before/after identity checks of unchanged authorities.
    match=re.search(r'public static [^\n]+ '+name+r'\([^\n]*\)\s*\{',text)
    assert match,name
    start=match.end()-1; depth=0
    for end in range(start,len(text)):
        depth+=(text[end]=='{')-(text[end]=='}')
        if not depth:return text[start:end+1]
    raise AssertionError(name)

assert 'float maxFactor = 1f;' in method(u,'AdultTier')
assert 'return !(adultTier == T3 && t3OnMap);' in k
assert 'TitanEventEligible(tier, optedOut,' in p
now=(current/'Titanic/Tiering/TitanicTierUtility.cs').read_text()
for name in ['AdultTier','GetTier','DefQualifies','ForceOf']:
    assert re.sub(r'\s+','',re.sub(r'//[^\n]*','',method(u,name)))==re.sub(r'\s+','',re.sub(r'//[^\n]*','',method(now,name))),name+' executable authority changed'
factors=[.2,.5]; ladder=[4,8,20]
tier=lambda size:sum(size>=t for t in ladder)
r={'mode':'preserved pre-fix source model plus current executable-token equality (comments excluded); no compiled/live pre-fix claim',
   'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in before.iterdir()},
   'base':32,'supported_factors':factors,'runtime_sizes':[32*f for f in factors],
   'runtime_tiers':[tier(32*f) for f in factors],'AdultTier':tier(32*max(1,*factors)),
   'pre_fix_spacing_tier':tier(32*max(1,*factors)),
   'pre_fix_eligible_no_T3_other_gates_true':True,'pre_fix_eligible_with_T3_other_gates_true':False,
   'unchanged_executable_methods':['AdultTier','GetTier','DefQualifies','ForceOf']}
print(json.dumps(r,indent=2))
