"""Acceptance test: stage_review.py ends --daylight at 10-14 h from any start hour, --clear chunks destroys only chunks, and
--two-pass has clear weather, 4000 ticks in, at its _clear shot. A fake bridge, no game. RED on 78750f480b. Run from the repo root."""
import sys,types; sys.path.insert(0,'src/RimMandrake/Utils')
import stage_review as S
class RB:
    def __init__(s,hour): s.t=int(hour*2500); s.d=[]; s.w,s.age='Rain',0; s.shots=[]
    def call(s,tool,p=None,**k):
        p=p or {}
        if tool in('rimworld/step_game_ticks','jawa/safe_advance'): s.t+=int(p.get('ticks',0)); s.age+=int(p.get('ticks',0)); return {'success':True}
        if tool=='jawa/time_set_ticks': s.t=int(p['ticks']); return {'success':True}
        if tool=='jawa/destroy_batch': s.d.append(p.get('category') or p.get('categories')); return {'destroyed':1}
        if tool=='jawa/weather_set': s.w,s.age=p['weather'],0; return {'success':True,'after':s.w}
        if tool=='rimworld/take_screenshot': s.shots.append((p['fileName'],s.w,s.age,(s.t/2500)%24)); return {'path':'x.png'}
        return {'success':True,'ticksGame':s.t,'hour':(s.t/2500)%24,'things':[],'countMatched':0,'pawns':[]}
bad=[]
for h in (0,3,6,9,12,15,18,21):
    rb=RB(h); S.daylight(rb); e=(rb.t/2500)%24
    if not 10<=e<=14: bad.append('start %s -> hour %.1f'%(h,e))
rb=RB(12); S.clear(rb,['chunks'],'0,0,50,50')
if rb.d: bad.append('--clear chunks destroyed category %s over the whole rect with no chunk on the map'%rb.d)
rb=RB(18); S.connect=lambda: rb; S.pause=lambda r: True; S.time.sleep=lambda n: None
S.wrapup_debt.owe=lambda *a,**k: 't'; S.wrapup_debt.paid=lambda t: None
sys.argv=['stage_review.py','--frame','1,1,9,9','--shot','s','--two-pass','Fog']; S.main()
c=[x for x in rb.shots if x[0]=='s_clear']
if not c or c[0][1]!='Clear' or c[0][2]<4000 or not 10<=c[0][3]<=14: bad.append('--two-pass _clear shot (name, weather, ticks in it, hour): %s'%rb.shots)
print('FAIL' if bad else 'PASS',bad); sys.exit(1 if bad else 0)
