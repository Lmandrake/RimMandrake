import sys,json,time
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
sys.path.insert(0,"src/RimMandrake/Utils")
import rimbridge_client as rb
h,p,t=rb.resolve_endpoint()
S=rb.RimBridge(host=h,port=p,token=t,timeout=600.0);S.connect()
def call(tool,**a):
    r=S.call(tool,a) or {}
    if isinstance(r,dict) and r.get("content"):
        try: r=json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
def J(x,n=1500): print(json.dumps(x,ensure_ascii=False)[:n])
st=call("rimworld/get_ui_state"); print(st.get("programState"))
if st.get("programState")!="Playing":
    J(call("rimworld/start_debug_game_ready",timeoutMs=180000,readiness="mapData",pauseIfNeeded=True),400)
for _ in range(90):
    if call("rimworld/get_ui_state").get("programState")=="Playing": break
    time.sleep(2)
J(call("jawa/map_info"),600)
J(call("jawa/destroy_bulk",filter="nonColonists",dryRun=False),200)
J(call("jawa/list_pawns",faction="player",limit=3),1500)
