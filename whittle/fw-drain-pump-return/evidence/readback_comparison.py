import ast,importlib.util,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
p=ROOT/'src/RimMandrake/FlowWorks/northstar/selftest_pump_return_readback.py'
spec=importlib.util.spec_from_file_location('pump_readback_tests',p);T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
raw=json.loads((HERE/'result.json').read_text());pour=raw['chains'][0]['components'][-1]
reply=next(e['result'] for e in pour['evidence'] if isinstance(e['result'],dict) and 'ProofTank(' in e['result'].get('method',''))
replay=T.exercise(reply);assert replay['verdict']=='PASS'
new=T.E._tank_set
source=subprocess.check_output(['git','show','HEAD:src/RimMandrake/FlowWorks/northstar/extensions.py'],text=True)
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='_tank_set')
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'HEAD:_tank_set','exec'),T.E.__dict__)
old=T.E._tank_set
rows=[]
for label,r in [('effective-prefix',{'result':reply['result'].replace('effective=Dump','effective=DumpPending')}),('error-payload',{'result':reply['result'],'error':'missing tank'}),('false-success',dict(reply,success=False))]:
 T.E._tank_set=old;before=T.exercise(r)
 T.E._tank_set=new;after=T.exercise(r)
 assert before['verdict']=='PASS' and after['verdict']=='UNMEASURED',(label,before,after)
 rows.append({'case':label,'old':before,'fixed':after})
(HERE/'readback-comparison.json').write_text(json.dumps({'actual_live_reply_replay':replay,'cases':rows,'note':'Original live receipt is unchanged; new parser is replayed offline against its exact raw reply.'},indent=2))
print('PASS exact actual live response replay; old false accepts reproduced and fixed readbacks refuse')
