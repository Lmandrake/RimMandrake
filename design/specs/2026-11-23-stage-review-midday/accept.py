"""Acceptance test: stage_review.py ends --daylight at 10-14 h from any start hour, and --clear chunks destroys only chunks.
A fake bridge, no game. RED on 78750f480b. Run from the repo root."""
import sys,types; sys.path.insert(0,'src/RimMandrake/Utils')
import stage_review as S
class RB:
    def __init__(s,hour): s.t=int(hour*2500); s.d=[]
    def call(s,tool,p=None,**k):
        p=p or {}
        if tool in('rimworld/step_game_ticks','jawa/safe_advance'): s.t+=int(p.get('ticks',0)); return {'success':True}
        if tool=='jawa/time_set_ticks': s.t=int(p['ticks']); return {'success':True}
        if tool=='jawa/destroy_batch': s.d.append(p.get('category') or p.get('categories')); return {'destroyed':1}
        return {'success':True,'ticksGame':s.t,'hour':(s.t/2500)%24,'things':[],'countMatched':0,'pawns':[]}
bad=[]
for h in (0,3,6,9,12,15,18,21):
    rb=RB(h); S.daylight(rb); e=(rb.t/2500)%24
    if not 10<=e<=14: bad.append('start %s -> hour %.1f'%(h,e))
rb=RB(12); S.clear(rb,['chunks'],'0,0,50,50')
if rb.d: bad.append('--clear chunks destroyed category %s over the whole rect with no chunk on the map'%rb.d)
print('FAIL' if bad else 'PASS',bad); sys.exit(1 if bad else 0)
