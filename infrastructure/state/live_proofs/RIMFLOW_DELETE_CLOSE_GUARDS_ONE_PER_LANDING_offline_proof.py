#!/usr/bin/env python3
"""Offline proof of RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING: both files gone, each in its own commit citing its reading,
no live reference left, corpus still passes. Prints PROOF_OK; an assert fails it. This item's record, not a tool."""
import subprocess as S,os,re
H,T,L='warn_close_live_proof_owed','.claude/hooks/','src/RimMandrake/rimflow/'
R=lambda *a:S.run(a,capture_output=True,text=True).stdout
for p in (T+H+'.py',T+'selftest_'+H+'.py',L+'live_proof_lint.py'): assert not os.path.exists(p),p
assert re.search(r'(?m)^hook='+H+r'\.py\s+#',open(L+'live_retired.txt').read())
g=R('git','grep','-l','-E',H+'|live_proof_lint','--','.claude','src','design/RimMandrake/rimflow_system_and_stuck_state_2026-10-07.md','design/RimMandrake/git_workflow_plan_2026-10-01.md','design/RimMandrake/parallel_review_2026-10-31/folded_into_operations.md').split()
assert g==[L+'live_retired.txt'],g
assert R('python3',L+'entrypoint_inventory.py','show',H,'live_proof_lint').count('0 entry points')==2
assert S.run(['python3',L+'evidence_gate.py','corpus','check']).returncode==0
assert S.run(['python3','src/RimMandrake/Utils/selftest_live_retired.py'],capture_output=True).returncode==0
A=R('git','log','-1','--format=%H','--',T+H+'.py').strip(); B=R('git','log','-1','--format=%H','--',L+'live_proof_lint.py').strip()
assert A and B and A!=B,(A,B)
for s in (A,B): assert 'reading:' in R('git','log','-1','--format=%B',s),s
assert L+'live_proof_lint.py' not in R('git','show','--name-only','--format=',A)
assert T+H+'.py' not in R('git','show','--name-only','--format=',B)
print('PROOF_OK',A[:10],B[:10])
