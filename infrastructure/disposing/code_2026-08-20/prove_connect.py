"""connect_cells: the owner's obstacle question, answered by running it."""
import sys, json, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
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
call("jawa/set_fog", action="unfogAll")

def show(tag, r):
    print("   [%s] success=%s route=%s len=%s mine=%s bridge=%s placed=%s cleared=%s" % (
        tag, r.get("success"), r.get("route"), r.get("routeLength"),
        r.get("wouldMine", r.get("cleared")), r.get("wouldBridge", r.get("bridged")),
        r.get("placed"), r.get("cleared")))
    if not r.get("success"): print("       ->", (r.get("message") or "")[:190])

print("== 1. OPEN GROUND: a clean run should need no obstacles ==")
a = call("jawa/connect_cells", **{"from":"100,100","to":"140,100"})
show("dry", a)

print("\n== 2. COMMIT it, then verify the conduits really exist and are contiguous ==")
b = call("jawa/connect_cells", dryRun=False, **{"from":"100,100","to":"140,100"})
show("live", b)
seen = 0
for x in range(100, 141):
    g = call("jawa/build_check", rect="%d,100,1,1" % x, **{"def":"PowerConduit"})
    occ = (g.get("cells") or [{}])[0].get("occupants") or []
    if "PowerConduit" in occ: seen += 1
print("   conduit cells actually present along the straight line: %d of 41" % seen)

print("\n== 3. BUILD A WALL ACROSS THE ROUTE, then retry each mode ==")
call("jawa/connect_cells", dryRun=False, **{"from":"100,120","to":"100,120"})
wall = ";".join("Wall:120,%d" % z for z in range(112, 129))
w = call("jawa/build_batch", ops=wall, stuff="Steel")
print("   wall placed:", w.get("placed"))
s1 = call("jawa/connect_cells", mode="strict", **{"from":"100,120","to":"140,120"})
show("strict", s1)
s2 = call("jawa/connect_cells", mode="mine", **{"from":"100,120","to":"140,120"})
show("mine-dry", s2)

print("\n== 4. THE REAL QUESTION: what happens with DEEP WATER in the way? ==")
call("jawa/set_terrain_batch", ops="WaterDeep:120,140,1,25")
d1 = call("jawa/connect_cells", mode="strict", **{"from":"100,150","to":"140,150"})
show("water-strict", d1)
d2 = call("jawa/connect_cells", mode="bridge", **{"from":"100,150","to":"140,150"})
show("water-bridge", d2)
print("   >>> does ANY mode force it through deep water?")

print("\n== 5. TRULY UNREACHABLE: box a target in with deep water ==")
for op in ("WaterDeep:180,180,9,1","WaterDeep:180,188,9,1","WaterDeep:180,180,1,9","WaterDeep:188,180,1,9"):
    call("jawa/set_terrain_batch", ops=op)
u = call("jawa/connect_cells", mode="bridge", **{"from":"100,150","to":"184,184"})
show("boxed", u)
