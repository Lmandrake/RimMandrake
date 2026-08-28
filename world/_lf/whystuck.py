# -*- coding: utf-8 -*-
"""set_time_speed reported Superfast and the clock did not move. Why?"""
import sys, json, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=240); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
u=c('rimworld/get_ui_state')
for k in ('programState','windowsForcePause','windowCount','focusedWindowType','topWindowType',
          'nonImmediateDialogWindowOpen','anyWindowAbsorbingAllInput'):
    print("  %-28s %s"%(k, u.get(k)))
print("  open windows:", [w.get('type') for w in (u.get('windows') or [])][:8])
st=c('rimworld/get_cell_info',{'x':103,'z':205}).get('state') or {}
print("  cell_info state: paused=%s timeSpeed=%s"%(st.get('paused'), st.get('timeSpeed')))
t0=c('rimworld/get_game_info').get('ticksGame'); time.sleep(6)
t1=c('rimworld/get_game_info').get('ticksGame')
print("  clock over 6s: %s -> %s  (delta %s)"%(t0,t1,(t1 or 0)-(t0 or 0)))
print("\n  step_game_ticks 600 ->", json.dumps(c('rimworld/step_game_ticks',{'ticks':600,'timeoutMs':120000}))[:180])
print("  ticks now:", c('rimworld/get_game_info').get('ticksGame'))
