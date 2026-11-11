"""Execute the production pour row with real modcheck verdicts; inject only transport/volume readings."""
import ast
from copy import deepcopy
import inspect
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
for p in (ROOT/'src/RimMandrake/Utils',ROOT/'src/RimMandrake/Utils/modcheck',HERE): sys.path.insert(0,str(p))
import extensions as E
from modcheck import TestContext


def row_code():
    tree=ast.parse(inspect.getsource(E.liquid_pump))
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.With) and isinstance(n.items[0].context_expr,ast.Call)
              and n.items[0].context_expr.args and isinstance(n.items[0].context_expr.args[0],ast.Constant)
              and n.items[0].context_expr.args[0].value=='pump_pours_back')
    return compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(HERE/'extensions.py'),'exec')


def exercise(reply,guard=True,rise=True):
    events=[]
    class S:
        def call(self,tool,**kw):
            events.append({'tool':tool,'args':kw})
            return deepcopy(reply)
    t=TestContext(S())
    if not guard: t.upstream_failed=True;t.upstream_reason='UNMEASURED: injected prior failure'
    def rd(mode): events.append({'pump_request':mode}); return {'pour':'True','running':'True'}
    levels=iter([3.0,6.0 if rise else 3.0])
    t.wait_ticks=lambda n:events.append({'wait':n})
    exec(row_code(),dict(t=t,tank=(1,2),level=lambda:next(levels),rd=rd,_tank_set=E._tank_set,_expect=E._expect,PUMP_LEVEL_TOL=E.PUMP_LEVEL_TOL))
    return {'verdict':t.components[0].verdict,'detail':t.components[0].detail,'events':events}


def run():
    good={'success':True,'result':'TANK mode=Dump effective=Dump liquid=RM_Liquid_FreshWater units=30000'}
    cases={'valid':(good,'PASS'), 'no_rise':(good,'FAIL')}
    bad=[None,{},'TANK mode=Dump effective=Dump',{'success':False,'result':good['result']},
         {'result':good['result'],'error':'tank not found'},
         {'result':'REFUSED: no RM_LiquidTank'},
         {'result':good['result'].replace('effective=Dump','effective=Store')},
         {'result':good['result'].replace('effective=Dump','effective=DumpPending')},
         {'result':good['result'].replace('effective=Dump','effective=Dump;')},
         {'result':'TANK mode=Dump effective=Dump'},
         {'result':good['result']+' actual=Store'}]
    for i,reply in enumerate(bad): cases['bad_'+str(i)]=(reply,'UNMEASURED')
    rows={}
    for name,(reply,expected) in cases.items():
        result=exercise(reply,rise=name!='no_rise'); rows[name]=result
        assert result['verdict']==expected,(name,result,expected)
        if name.startswith('bad_'): assert not any('pump_request' in x or 'wait' in x for x in result['events']),(name,result)
    rows['guard_off']=exercise({'result':'TANK mode=Dump effective=Store'},guard=False)
    assert rows['guard_off']['verdict']=='UNMEASURED',rows['guard_off']
    assert rows['valid']['events'][0]['args']['method']=='ProofTank'
    assert rows['valid']['events'][1]=={'pump_request':'pour'}
    assert rows['valid']['events'][2]=={'wait':600}
    print(json.dumps(rows,indent=2))
    return rows

if __name__=='__main__':run()
