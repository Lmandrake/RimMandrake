"""Offline exercise of the actual live driver's success and failed on paths, including finally restoration.
Canned bridge responses test transport/assertions/cleanup only, never substitute for production/runtime evidence.
"""
from pathlib import Path
import importlib.util,json
p=Path(__file__).resolve().parents[3]/'src/RimMandrake/FlowWorks/northstar/railing_toggle_live.py'
s=importlib.util.spec_from_file_location('driver',p);d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
d.time.sleep=lambda _:None
class Sites:
 @staticmethod
 def load_site(call,site,**kw):return {'verified':True}
 @staticmethod
 def save_site(call,name,saves):return {'bytes':100,'path':'new.rws'}
class Bridge:
 def __init__(self,fault):self.fault=fault;self.on=True;self.marked=False;self.ctrl=False;self.god=True
 def call(self,t,**kw):
  if t=='jawa/debug_settings':
   if kw['action']=='set':self.god=kw['value']
   return dict(success=True,fields=[dict(name='godMode',value=self.god)])
  if t=='jawa/static_call':
   m=kw['method']
   if m=='Identity':return dict(result='IDENTITY sha256=expected')
   if m=='Rect':return dict(result='RECT unchanged')
   if m=='ProofBuild':return dict(result='BUILD ok=True decks=4')
   if m=='ProofRails':
    on=kw['args'].split(';')[1]=='on'
    self.on=on
    if not (on and self.fault and self.ctrl):self.marked=not on
    return dict(result='RAILS on='+str(on)+' railed=4')
   if m=='ProofSpan':return dict(result='SPAN railings='+str(self.on))
   return dict(result='RESET')
  if t=='jawa/list_things':return dict(success=True,countMatched=4,isCompleteList=True,things=[dict(id=str(i),x=37+i,z=36,spawned=True,stuff='WoodLog',hitPoints=40,**{'def':d.RAIL}) for i in range(4)])
  if t=='jawa/flowworks_excavation_report':return dict(depth=4,fill=0)
  if t=='jawa/build_batch':return dict(placed=1)
  if t=='jawa/designate_batch':
   if kw['action']=='add':self.ctrl=True;return dict(success=True)
   rows=[]
   if self.ctrl:rows=[dict(defname='Plan',x=38,z=36,thing=None),dict(defname='Deconstruct',x=48,z=40,thing='Wall')]
   if self.marked:rows += [dict(defname='Deconstruct',x=37+i,z=36,thing=d.RAIL) for i in range(4)]
   rows=[dict(**{'def':r.pop('defname')},**r) for r in rows]
   return dict(success=True,total=len(rows),truncated=False,designations=rows,ticksGame=123)
  return dict(success=True)
results=[]
for fault in [False,True]:
 b=Bridge(fault);r={};error=None
 try:d.run(b,Sites,'unused',r,'expected')
 except AssertionError as e:error=str(e)
 assert bool(error)==fault,(fault,error)
 assert r['restore']['status']=='PASS' and b.god is True
 results.append(dict(fault=fault,error=error,restore=r['restore']))
out=Path(__file__).with_name('live_driver_checks.json');assert not out.exists();out.write_text(json.dumps(results,indent=2)+'\n');print('PASS driver success/failure assertions and restoration')
