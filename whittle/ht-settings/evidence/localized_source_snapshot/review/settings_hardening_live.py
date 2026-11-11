"""HUGETHINGS_SETTINGS_HARDENING_1: cold disk/Scribe load and native settings UI.

Windows Python reads the live bridge; WSL orchestrator owns cold-start fixture
writes/backups. This script NEVER sets a tested numeric field or calls Sanitize.
Compare a pre-start XML fixture (all numeric keys) with first-read loaded fields.
The baseline/restore arms prove absent-file defaults and exact active restoration.
Raw UI layouts come from real draw frames; scroll every visible page and retain
screenshots. No world/map/ticks/focus/fullscreen. UI close may WriteSettings;
the orchestrator stops the process before exact original file restoration.

RULED OUT: static set/Sanitize roundtrips prove Scribe — they do not; cold PID
identity, exact fixture bytes and untouched first reads are required together.
"""
import argparse
from datetime import datetime,timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib,json,math,re,struct,sys,time
from pathlib import Path
import xml.etree.ElementTree as ET
MOD=Path(__file__).resolve().parents[1]
SETTINGS='RimMandrake.HugeThings.RM_HugeThingsSettings'
MODTYPE='RimMandrake.HugeThings.RM_HugeThingsMod'
KERNEL='RimMandrake.TitanicCreatures.RM_TitanicKernel'
# Independent declared slider contract: low, high, nonfinite fallback, valid tuning.
SPEC={
 'plantTrunkScale':(.5,1.5,1,1.25),'pawnHitboxScale':(.5,1.5,1,.75),
 'tierT1MinBodySize':(1,30,4,5),'tierT2MinBodySize':(2,60,8,10),'tierT3MinBodySize':(3,100,20,25),
 'wakeCrushDamageMultiplier':(.25,3,1,1.5),'wakeFilthTrailChance':(0,1,.35,.42),
 'giantPlantSmashMinTier':(1,3,None,2),'titanClearingDetourFactor':(1.5,6,2.5,3.5),
 'squeezeSlowdownAtHalf':(1,4,2,2.5),'trampleBudgetPerBreadth':(25,400,100,150),
 'blowDamagePerBreadth':(5,80,20,30),'holdLineFactor':(.5,2,1,1.25),
 'roofWallHpFactor':(1,3,1.5,2),'roofWallDamageFactor':(.25,1,.6667,.5),
 'yieldCurveMinFactor':(.05,1,.15,.25),'corpseSiteHarvestMeatPerSession':(5,100,None,35),
 'corpseSiteHarvestLeatherPerSession':(2,50,None,15),'corpseSiteWorkHoursPerSession':(.25,6,1,1.5),
 'corpseSiteMeatSpoilagePerDay':(.02,.5,.15,.2),'corpseSiteLeatherSpoilagePerDay':(.02,.5,.08,.1),
 'corpseSiteScavengerDailyChance':(0,1,.35,.45),'corpseSiteScavengerMax':(1,8,None,4),
 'corpseSiteVisitorMeatPerDay':(5,100,None,30),'corpseSiteCampDailyChance':(0,1,.1,.2),
 'corpseSiteCampHours':(6,120,36,48),'titanEventWarningHours':(.5,24,2,6)}
INTS={k for k,v in SPEC.items() if v[2] is None}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fixture_values(arm):
 if arm=='valid':return {k:str(int(v[3])) if k in INTS else str(v[3]) for k,v in SPEC.items()}
 values={k:('-7' if k in INTS else ['NaN','Infinity','-Infinity','-5','0','99999'][i%6]) for i,k in enumerate(SPEC)}
 values.update(tierT1MinBodySize='30',tierT2MinBodySize='2',tierT3MinBodySize='3',titanEventWarningHours='NaN')
 return values
def expected(values):
 out={}
 for k,(lo,hi,fallback,_) in SPEC.items():
  x=float(values[k]);out[k]=max(lo,min(hi,x)) if math.isfinite(x) else fallback
 return out
def check_values(actual,want):
 failures={}
 for k,(lo,hi,_,_) in SPEC.items():
  try:
   x=float(actual[k]);w=float(want[k]);ok=math.isfinite(x) and lo<=x<=hi and math.isclose(x,w,rel_tol=1e-5,abs_tol=1e-5)
  except (KeyError,ValueError,TypeError):ok=False
  if not ok:failures[k]={'actual':actual.get(k),'expected':want.get(k),'range':[lo,hi]}
 return failures

def f32(number):
 return struct.unpack('f',struct.pack('f',float(number)))[0]

def format_ui_number(number, fmt):
 # RimWorld's Mono custom numeric format rounds midpoint away from zero.
 # Python's format uses ties-to-even (.25 -> .2), a false failure discovered
 # by the real zero-work cold-load fixture (.25 is displayed as .3).
 assert number>=0,'negative value outside declared UI setting contract'
 places={'"0"':0,'"0.0"':1,'"0.00"':2}
 assert fmt in places,'unknown numeric UI format'
 quantum=Decimal(1).scaleb(-places[fmt])
 # Mono Single.ToString uses seven significant decimal digits before custom
 # formatting. Reproduce float32 arithmetic too, especially percentage ties.
 digits=Decimal(format(f32(number),'.7g'))
 return format(digits.quantize(quantum,rounding=ROUND_HALF_UP),'f')

def capture_ui(call, report, out, arm):
 opened=call('rimworld/open_mod_settings',modId=MODTYPE,replaceExisting=False)
 report['opened']=opened
 target='window:'+str(opened['dialog']['windowId'])+':'+opened['dialog']['windowType']
 report['ui_pages']=[];report['screenshots']=[];report['hover_screenshots']=[]
 seen=set();hovered=set()
 try:
  for page in range(16):
   layout=call('rimworld/get_ui_layout',surfaceId=target,timeoutMs=15000)
   # Page transport separately from scrolling; never silently accept truncation.
   pages=[layout]
   while pages[-1].get('page',{}).get('nextOffset') is not None:
    pages.append(call('rimworld/get_ui_layout',surfaceId=target,timeoutMs=15000,offset=pages[-1]['page']['nextOffset']))
   report['ui_pages'].extend(pages)
   elements=[e for p in pages for s in p['surfaces'] for e in s['elements']]
   seen.update(e['label'].strip() for e in elements if e.get('label'))
   scrolls=[e for e in elements if e['kind']=='scroll_view']
   assert len(scrolls)==1,'expected single settings scroll'
   scroll=scrolls[0]
   report['screenshots'].append(call('rimworld/take_screenshot',fileName='ht_settings_'+arm+'_'+str(page),clipTargetId=target,clipPadding=0,outputDirectory=str(out.parent),suppressMessage=True))
   for label in ('Trunk hits damage the plant','Destruction wake'):
    hit=next((e for e in elements if e.get('label','').strip()==label and e['kind']=='checkbox'),None)
    if hit and label not in hovered:
     call('rimworld/set_hover_target',targetId=hit['targetId'],durationMs=6000,settleMs=1200)
     report['hover_screenshots'].append(call('rimworld/take_screenshot',fileName='ht_settings_'+arm+'_tooltip_'+str(len(hovered)),clipTargetId=target,clipPadding=0,outputDirectory=str(out.parent),suppressMessage=True))
     call('rimworld/clear_hover_target');hovered.add(label)
   if scroll['scroll']['atBottom']:break
   call('rimworld/scroll_ui_target',targetId=scroll['targetId'],deltaY=440,timeoutMs=15000)
  else:raise RuntimeError('settings scroll did not reach bottom')
  report['rendered_labels']=sorted(seen)
  assert not any('RM_HugeThings_' in s or re.search(r'\{\d+\}',s) for s in seen),'raw translation key/placeholder rendered'
  assert '- Titan events' in seen,'last settings section never rendered'
  # Every visible label key in production source must match a rendered label.
  source=(MOD/'Source/RM_HugeThingsSettings.cs').read_text()
  keys=set(re.findall(r'"(RM_HugeThings_\w+)"\.Translate\(',source))
  excluded={k for k in keys if k.endswith('_Desc')}|{'RM_HugeThings_WallsSlotsNeeds','RM_HugeThings_NeedsAnimals','RM_HugeThings_ScopeNewMaps'}
  if arm!='adversarial':excluded.add('RM_HugeThings_TierInvalid')
  if arm=='baseline':excluded|={'RM_HugeThings_TierT1','RM_HugeThings_TierT2','RM_HugeThings_TierT3'}
  keyed={e.tag:(e.text or '').strip() for e in ET.parse(MOD/'Languages/English/Keyed/RM_HugeThings.xml').getroot()}
  # Check numbers against the first loaded fields, not a wildcard that could
  # accept a label bound to the wrong setting. Expressions/formats are read
  # from the actual production label calls; unrecognized expressions refuse.
  values=report['first_loaded_fields'];rendered_numbers={}
  for key,expression,fmt in re.findall(r'"(RM_HugeThings_\w+)"\.Translate\((\([^\n]+?\)|\w+)\.ToString\(([^)]*)\)\)',source):
   expression=expression.strip('() ')
   if ' * ' in expression:
    match=re.fullmatch(r'(\w+) \* ([0-9.]+)f',expression)
    assert match,'unknown numeric UI expression'
    name,mult=match.groups();number=f32(f32(values[name])*f32(mult))
   else:
    assert expression in SPEC,'unknown numeric field'
    name=expression;number=f32(values[name])
   if fmt=='':
    assert name in INTS and expression==name,'untyped default numeric format'
    rendered_numbers[key]=str(int(values[name]))
   else:rendered_numbers[key]=format_ui_number(number,fmt)
  group_keys=set(re.findall(r'Group\(list,\s*"(RM_HugeThings_\w+)"\.Translate\(',source))
  checks={}
  normalized={re.sub(r'<color=#[0-9A-Fa-f]{8}>|</color>','',t) for t in seen}
  for k in sorted(keys-excluded):
   template=keyed[k]
   if '{0}' in template:
    assert k in rendered_numbers,'unaccounted numeric label: '+k
    pattern=re.escape(template.format(rendered_numbers[k]))
   else:pattern=re.escape(template)
   # Section buttons add their open/collapsed marker. Verse's label rendering
   # may capitalize the multiplier x after a colon. Keep all other text exact.
   if k in group_keys:pattern=r'[-+] '+pattern
   if k=='RM_HugeThings_SqueezeSlow':pattern=pattern.replace('x','[xX]')
   checks[k]={'template':template,'found':any(re.fullmatch(pattern,t) for t in normalized)}
  report['label_checks']=checks
  assert all(x['found'] for x in checks.values()),'missing rendered labels: '+str([k for k,v in checks.items() if not v['found']])
 finally:
  # Restore owned scroll state before close; no unrelated log window is closed.
  if 'scroll' in locals():call('rimworld/scroll_ui_target',targetId=scroll['targetId'],targetY=0,timeoutMs=15000)
  call('rimworld/clear_hover_target')
  call('jawa/window_list_close',action='close',typeName=opened['dialog']['windowType'])
  report['windows_after']=call('jawa/window_list_close',action='list')
  before=[(w['type'],w['id']) for w in report['windows_before']['windows']]
  after=[(w['type'],w['id']) for w in report['windows_after']['windows']]
  assert before==after,'unowned window stack changed'

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--fixture',type=Path);ap.add_argument('--arm',choices=['baseline','adversarial','valid','upgrade','restore'],required=True)
 ap.add_argument('--ui',action='store_true');a=ap.parse_args()
 sys.path.insert(0,str(MOD.parent/'Utils'));from validation_core import Bridge
 import game_paths
 a.out.parent.mkdir(parents=True,exist_ok=True)
 report={'started_utc':datetime.now(timezone.utc).isoformat(),'arm':a.arm,'calls':[],'errors':[],
         'script_sha256':digest(Path(__file__)),'tested_numeric_writes':0}
 def save():a.out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 b=Bridge();tools=b.S.list_tools();schemas={t['name']:t for t in tools}
 report['jawa_tool_count']=sum(k.startswith('jawa/') for k in schemas)
 def call(tool,**params):
  assert tool in schemas,tool+' absent';assert set(params)<=b.S._declared_params(schemas[tool]),'unknown params'
  r=b.call(tool,**params);report['calls'].append({'tool':tool,'params':params,'result':r});save()
  assert r.get('success') is True,(tool,r)
  return r
 try:
  # Must precede opening UI (its drawing calls Sanitize) or any static invocation.
  fields=call('jawa/mod_settings_field',typeName=SETTINGS,action='list')
  actual={f['name']:f['value'] for f in fields['fields']}
  report['first_loaded_fields']=actual
  report['semantic_settings']=call('rimworld/get_mod_settings',modId=MODTYPE)
  report['windows_before']=call('jawa/window_list_close',action='list')
  report['ui_before']=call('rimworld/get_ui_state')
  if a.fixture:
   values={e.tag:e.text for e in ET.parse(a.fixture).getroot().find('ModSettings')}
   report['fixture']={'path':str(a.fixture),'sha256':digest(a.fixture),'values':values}
   if a.arm=='upgrade':
    assert 'titanEventWarningHours' not in values,'upgrade must omit warning key'
    assert set(SPEC)-{'titanEventWarningHours'}<=set(values),'upgrade fixture misses additional numeric fields'
    effective=dict(values,titanEventWarningHours='2')
   else:
    assert set(SPEC)<=set(values),'fixture misses numeric fields'
    effective=values
   report['numeric_failures']=check_values(actual,expected(effective));assert not report['numeric_failures'],'loaded values differ'
  else:
   assert float(actual['titanEventWarningHours'])==2,'absent file must ship two hours'
  report['warning_ticks']=call('jawa/static_call',type=KERNEL,method='WarningTicks',args=actual['titanEventWarningHours'])
  assert str(report['warning_ticks']['result'])==('15000' if a.arm=='valid' else '5000')
  # Exact production getter; reports shipped/custom def identity without invented probe C#.
  report['thresholds']=call('jawa/static_call',type='RimMandrake.TitanicCreatures.TitanicTierUtility',method='get_Thresholds')
  if a.arm=='adversarial':assert report['thresholds']['result']=='RM_TitanicTierDef:RM_TitanicTiers_Default'
  if a.arm=='valid':assert 'RM_TitanicTiers_ModSettings' in report['thresholds']['result']
  save()
  if a.ui:
   assert not any('Dialog_ModSettings' in w['type'] for w in report['windows_before']['windows']),'settings dialog already owned by someone else'
   capture_ui(call,report,a.out,a.arm)
 except Exception as exc:report['errors'].append(str(exc))
 finally:
  try:
   log=Path(game_paths.PLAYER_LOG);raw=log.read_text(errors='replace').splitlines()
   safe=['[credential line redacted]' if re.search(r'bridge token:|authorization:|bearer ',s,re.I) else s for s in raw]
   logpath=a.out.with_suffix('.startup.sanitized.txt');logpath.write_text('\n'.join(safe)+'\n')
   ex=[(i+1,s) for i,s in enumerate(safe) if re.search(r'Exception|Traceback',s)]
   cfg=[(i+1,s) for i,s in enumerate(safe) if 'Config error' in s]
   parse=[(i+1,s) for i,s in enumerate(safe) if re.search(r'Error while loading|could not parse|exception parsing|XML error',s,re.I)]
   report['startup_log']={'sanitized_path':logpath.name,'sha256':digest(logpath),'first_exception':ex[0] if ex else None,'config_errors':cfg,'scribe_parse_errors':parse}
   if ex or cfg or parse:report['errors'].append('startup exception/config/Scribe parse error')
  except Exception as exc:report['errors'].append('log inspection: '+str(exc))
  report['finished_utc']=datetime.now(timezone.utc).isoformat();report['ok']=not report['errors'];save();b.S.close()
 print(json.dumps({'ok':report['ok'],'errors':report['errors'],'out':str(a.out)}))
 return 0 if report['ok'] else 1
if __name__=='__main__':sys.exit(main())
