"""Companion proofs, night 2026-10-13: tools that died without GSS, then safe_advance disarm / menu mid-run.
Run: python.exe D:\\Luke\\dev\\_rmscratch\\companion_probe_20261013.py <phase>   phase = tools | disarm | menu
Prints one JSON object per step."""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0); S.connect()


def call(t, **p):
    try:
        r = S.call(t, p) or {}
    except Exception as e:  # report, never swallow
        return {"EXC": repr(e)[:400]}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r


def out(step, r, keep=None):
    if isinstance(r, dict) and keep:
        r = {k: r.get(k) for k in keep if k in r} or r
    s = json.dumps(r, default=str)
    print(json.dumps({"step": step}) + " " + (s[:700] + ("..." if len(s) > 700 else "")), flush=True)


def ensure_map():
    st = call("rimworld/get_ui_state")
    if st.get("programState") != "Playing":
        out("start_debug_game", call("rimworld/start_debug_game_ready", timeoutMs=200000, readiness="mapData", pauseIfNeeded=True), ["success", "error", "message"])
        for _ in range(90):
            if call("rimworld/get_ui_state").get("programState") == "Playing": break
            time.sleep(1)
    out("ui_state", call("rimworld/get_ui_state"), ["programState", "success"])
    out("close modals", call("jawa/window_list_close", action="close", typeName="Dialog_NodeTree"), ["success", "closed", "count", "message"])


phase = sys.argv[1]
if phase == "tools2":
    out("jawa/research_progress", call("jawa/research_progress", project="Electricity"))
    out("jawa/research_availability", call("jawa/research_availability", project="Electricity"))
    out("jawa/set_current_map refusal", call("jawa/set_current_map", mapId=99))
elif phase == "tools":
    ensure_map()
    out("jawa/time_clock", call("jawa/time_clock"))
    out("jawa/debug_settings", call("jawa/debug_settings"))
    out("jawa/map_info", call("jawa/map_info"))
    out("jawa/research_progress", call("jawa/research_progress", project="Electricity"))
    out("jawa/research_availability", call("jawa/research_availability", project="Electricity"))
    out("jawa/time_date_at", call("jawa/time_date_at"))
    out("jawa/set_current_map refusal", call("jawa/set_current_map", mapId=99))
    out("jawa/time_set_ticks refusal", call("jawa/time_set_ticks", ticks=-5))
elif phase == "disarm":
    ensure_map()
    out("vitals arm", call("jawa/vitals", action="arm", ttlMin=20, row="SAFE_ADVANCE_PROVE_DISARM_ENDS_THE_RUN", why="night proof"), ["success", "armed", "error", "refused"])
    s1 = call("jawa/safe_advance", action="start", ticks=30000, chunk=1, frameBudgetMs=5, timeoutMs=0)
    out("start A (timeoutMs=0)", s1, ["success", "state", "requested", "executed", "refused", "error", "message"])
    time.sleep(1.0)
    out("status A before disarm", call("jawa/safe_advance", action="status"))
    out("vitals disarm", call("jawa/vitals", action="disarm", why="proof: disarm mid-advance"), ["success", "armed", "error"])
    time.sleep(1.5)
    out("status A after disarm", call("jawa/safe_advance", action="status"))
    s2 = call("jawa/safe_advance", action="start", ticks=600, timeoutMs=60000)
    out("start B after disarm", s2, ["success", "state", "requested", "executed", "refused", "error", "message", "abortWhy", "tickFrom", "tickTo"])
elif phase == "menu":
    ensure_map()
    s1 = call("jawa/safe_advance", action="start", ticks=30000, chunk=1, frameBudgetMs=5, timeoutMs=0)
    out("start C (timeoutMs=0)", s1, ["success", "state", "requested", "executed", "refused", "error", "message"])
    time.sleep(1.0)
    out("status C before menu", call("jawa/safe_advance", action="status"))
    out("go_to_main_menu", call("rimworld/go_to_main_menu"), ["success", "error", "message"])
    for _ in range(30):
        if call("rimworld/get_ui_state").get("programState") == "Entry": break
        time.sleep(1)
    time.sleep(2)
    out("status C at menu", call("jawa/safe_advance", action="status"))
    out("start at menu (expect No game, NOT already running)", call("jawa/safe_advance", action="start", ticks=600, timeoutMs=0))
    ensure_map()
    out("status C after new map", call("jawa/safe_advance", action="status"))
    out("start D on new map", call("jawa/safe_advance", action="start", ticks=600, timeoutMs=60000),
        ["success", "state", "requested", "executed", "refused", "error", "message", "abortWhy", "tickFrom", "tickTo"])
