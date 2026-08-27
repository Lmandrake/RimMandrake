# -*- coding: utf-8 -*-
"""FIRST DRIVE of the 45 tools deployed 2026-08-26. None had ever been called.

For each: one minimal call, and a verdict in four buckets.

  WORKS    success true AND the payload actually answers the question
  REFUSES  success false with a message that tells you what to do  <- a GOOD outcome
  LIES     success true and the payload is empty / null / unchanged
  ERROR    an exception came back

⚠️ Read-only pass first. The write pass is separate and runs only with --writes,
because several of these are marked *** ACTS ON THE LIVE COLONY ***.
Scratch quicktest map only - never point this at the campaign.
"""
import sys, json, io, argparse, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\shakedown.log"
OUT=r"D:\Luke\dev\Rimworld\world\_lf\shakedown.json"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")

h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
results={}
def drive(tool, args, note=""):
    try:
        r=b.call(tool,args or {}); r.pop('operation',None)
    except Exception as e:
        results[tool]={"verdict":"ERROR","detail":str(e)[:200],"args":args}
        P("  %-32s ERROR   %s"%(tool.split('/')[-1], str(e)[:90])); return None
    ok=r.get('success')
    body={k:v for k,v in r.items() if k not in ('success','message','ticksGame')}
    empty = not body or all(v in (None,[],{},0) for v in body.values())
    verdict = "REFUSES" if ok is False else ("LIES?" if empty else "WORKS")
    results[tool]={"verdict":verdict,"args":args,"note":note,
                   "message":(r.get('message') or "")[:200],
                   "keys":sorted(body.keys())[:12],
                   "sample":json.dumps(body)[:400]}
    P("  %-32s %-8s %s"%(tool.split('/')[-1], verdict, (r.get('message') or json.dumps(body))[:96]))
    return r

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--writes",action="store_true"); a=ap.parse_args()
    cols=(b.call('rimworld/list_colonists',{}).get('colonists') or [])
    pawn = cols[0]['pawnId'].replace('Thing_','') if cols else None
    P("subject pawn:", pawn, "of", len(cols), "colonists")
    P("\n=== READ-ONLY PASS ===")
    drive('jawa/time_clock',{})
    drive('jawa/time_perf',{})
    drive('jawa/time_date_at',{'ticks':100000})
    drive('jawa/research_availability',{})
    drive('jawa/cell_temperature',{'cell':'103,205'})
    drive('jawa/incident_parms_preview',{'incident':'RaidEnemy'})
    if pawn:
        drive('jawa/pawn_thoughts',{'pawn':pawn})
        drive('jawa/pawn_break_thresholds',{'pawn':pawn})
        drive('jawa/pawn_stats',{'pawn':pawn,'stats':'MoveSpeed'})
    drive('jawa/room_get',{'x':103,'z':205})
    drive('jawa/map_zones',{'action':'listZones'})
    if not a.writes:
        P("\nread-only pass done; re-run with --writes for the rest"); dump(); return
    P("\n=== WRITE PASS (scratch map) ===")
    if pawn:
        drive('jawa/pawn_refresh_needs',{'pawn':pawn})
        drive('jawa/pawn_dirty_situational',{'pawn':pawn})
        drive('jawa/pawn_memory',{'pawn':pawn,'action':'add','thought':'AteFineMeal'})
        drive('jawa/set_draft',{'pawnId':pawn,'drafted':True})
        drive('jawa/set_draft',{'pawnId':pawn,'drafted':False})
        drive('jawa/stop_job',{'pawnId':pawn,'action':'StopAll'})
        drive('jawa/set_player_settings',{'pawnId':pawn,'medicalCare':'NormalOrWorse'})
        drive('jawa/timetable',{'pawnId':pawn,'hour':3,'assignment':'Work'})
    drive('jawa/new_allowed_area',{'name':'CHECK_shakedown'})
    drive('jawa/paint_area',{'area':'home','action':'add','rect':'200,20,4,4'})
    drive('jawa/time_pin_normal_speed',{})
    drive('jawa/weather_roll_next',{})
    drive('jawa/rain_suppress',{'ticks':600})
    drive('jawa/sky_glow_set',{'glow':0.8})
    drive('jawa/difficulty_tune',{})
    drive('jawa/research_progress',{})
    drive('jawa/incident_schedule',{'incident':'VisitorGroup','delayTicks':60000})
    drive('jawa/signal_send',{'signal':'CHECK_shakedown_signal'})
    dump()

def dump():
    io.open(OUT,"w",encoding="utf-8").write(json.dumps(results,indent=1,ensure_ascii=False))
    c=collections.Counter(v['verdict'] for v in results.values())
    P("\nVERDICTS: %s"%dict(c))

main()
