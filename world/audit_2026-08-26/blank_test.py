# -*- coding: utf-8 -*-
import sys, json, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
try: b.call('jawa/drain_log',{})          # clear, so anything below is ours
except Exception: pass
P=json.load(open(os.path.join(A,'blank.json'),encoding='utf-8'))
def read(tile):
    r=b.call('jawa/world_mutators_get',{'tiles':str(tile),'limit':3})
    rows=r.get('tiles') or []
    return [m['def'] for m in rows[0]['mutators']] if rows else None
print("%-7s %-16s %-12s %-20s %-8s %-8s"%('tile','biome','hilliness','def','added','LANDED'))
for x in P:
    for kind in ('gl','ctl'):
        d=x[kind]
        before=read(x['tile'])
        w=b.call('jawa/world_mutators_set',{'action':'add','mutators':d,'tiles':str(x['tile']),'readBack':0})
        after=read(x['tile'])
        landed = after is not None and d in after
        print("%-7d %-16s %-12s %-20s %-8s %-8s  before=%s after=%s"%(
            x['tile'],x['biome'],x['hil'],d,w.get('added'),'YES' if landed else 'NO',before,after))
        if landed:   # leave the planet as we found it
            b.call('jawa/world_mutators_set',{'action':'remove','mutators':d,'tiles':str(x['tile']),'readBack':0})
lg=b.call('jawa/drain_log',{})
msgs=lg.get('entries') or lg.get('lines') or []
keep=[str(m)[:150] for m in msgs if 'utator' in str(m) or 'andform' in str(m) or 'GL_' in str(m)]
print("\nlog lines mentioning mutators/landforms: %d"%len(keep))
for k in keep[:8]: print("   ",k)
print("final state check:", [read(x['tile']) for x in P])
