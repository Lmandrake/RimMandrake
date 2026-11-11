"""Driver transport/restoration checks only; fixtures are canned, never production algorithm evidence."""
import importlib.util,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'src/RimMandrake/FlowWorks/northstar/reel_body_inlet_live.py'
spec=importlib.util.spec_from_file_location('driver',p);d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Sites:
 loads=[]
 @classmethod
 def load_site(cls,call,site,**kw):cls.loads.append(kw);return {'verified':True}
 @staticmethod
 def save_site(call,name,saves):return {'path':'new.rws','bytes':100,'expanded':{'bytes':100}}
class Bridge:
 def __init__(self,fault):self.rules=False;self.index=0;self.fault=fault
 def call(self,tool,**kw):
  if tool=='jawa/mod_settings_field':
   if kw['action']=='set':self.rules=kw['value'].lower()=='true'
   return {'success':True,'value':self.rules}
  if tool=='jawa/static_call':
   m=kw['method']
   if m=='Identity':return {'result':'IDENTITY sha256=expected'}
   if m=='Rect':return {'result':'RECT sha256=unchanged beds=0'}
   if m=='ProofResetRect':return {'result':'RESET left=0'}
   if m=='ProofBodyInlet':
    rows=[(1,[1,0],[40,36]),(1,[1,0],[40,37]),(-1,[0,0],[0,0]),(1,[1,0],[40,36]),(2,[-1,0],[37,36]),(2,[-1,0],[37,36])]
    pid,s,c=rows[self.index]
    if self.fault and self.index==2:pid=1
    self.index+=1
    return {'result':json.dumps(dict(success=True,reel=100,rect=[38,36,2,2],portId=pid,hydraulicPortId=pid,side=s,contact=c,bodyBand=0,contactBand=0))}
  if tool=='jawa/build_batch':return {'success':True,'placed':len(kw['ops'].split(';'))}
  if tool=='jawa/flowworks_excavation_report':return dict(depth=4,fill=0,isExcavated=True)
  return {'success':True}
 def shot_rect(self,*a):return 'fake.png'
results=[]
for fault in [False,True]:
 b=Bridge(fault);r={};Sites.loads=[];err=None
 try:d.run(b,Sites,'unused',r,'expected')
 except AssertionError as e:err=str(e)
 assert bool(err)==fault,(fault,err)
 assert r['restore']['status']=='PASS' and b.rules is False
 assert len(Sites.loads)==3 and 'name' in Sites.loads[-1]
 if fault:assert err=='body inlet crossed sheer wall'
 results.append(dict(fault=fault,error=err,restore=r['restore'],loads=Sites.loads))
p=Path(__file__).with_name('live_driver_checks_final.json');assert not p.exists();p.write_text(json.dumps(results,indent=2)+'\n');print('PASS canned transport success and assertion-failure restoration')
