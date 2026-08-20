import sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)

print("== GAS ==")
g = call("jawa/set_gas", action="add", rect="140,140,8,8", gasType="ToxGas", density=200)
print("   add:", g.get("cellsChanged"), g.get("gasType"), " valid:", g.get("validGasTypes"))
g2 = call("jawa/set_gas", action="clear", rect="140,140,8,8")
print("   clear:", g2.get("cellsChanged"))

print("\n== ZONES ==")
z0 = call("jawa/map_zones", action="listZones")
print("   before:", z0.get("zones"))
z1 = call("jawa/map_zones", action="createZone", zoneType="stockpile", rect="150,150,6,6")
print("   created:", z1.get("created"), " cells:", z1.get("cells"), "of", z1.get("cellsRequested"), " refused:", z1.get("refusedCount"))
for rc in (z1.get("refusedCells") or [])[:3]: print("      refused:", rc)
print("   notes:", z1.get("notes"))
z2 = call("jawa/map_zones", action="createZone", zoneType="growing", rect="160,150,5,5", plant="Plant_Potato")
print("   created:", z2.get("created"), " cells:", z2.get("cells"), " notes:", z2.get("notes"))
z3 = call("jawa/map_zones", action="paintZone", zone=z1.get("created"), rect="150,157,6,2", value=True)
print("   painted +12 ->", z3.get("cells"))
z4 = call("jawa/map_zones", action="deleteZone", zone=z1.get("created"))
print("   deleted; zones now:", [z["label"] for z in (z4.get("zones") or [])])

print("\n== AREAS ==")
a0 = call("jawa/map_zones", action="listAreas")
print("   areas:", [(a["label"], a["trueCount"]) for a in (a0.get("areas") or [])][:6])
a1 = call("jawa/map_zones", action="paintArea", area="Home", rect="150,150,10,10", value=True)
print("   Home painted:", a1.get("cellsTouched"), " trueCount now:", a1.get("trueCount"))
a2 = call("jawa/map_zones", action="paintArea", area="NoRoof", rect="150,150,4,4", value=True)
print("   NoRoof painted:", a2.get("cellsTouched"), " trueCount:", a2.get("trueCount"))
