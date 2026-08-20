"""connect_cells: paint a known test bed, then answer the obstacle question.

Each quicktest generates a DIFFERENT map, so hunting for naturally dry ground is
flaky. Paint Concrete and the terrain is known.
"""
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
    print("   [%-12s] ok=%-5s route=%-18s len=%-4s mine=%-4s bridge=%-4s placed=%s" % (
        tag, r.get("success"), r.get("route"), r.get("routeLength"),
        r.get("wouldMine", r.get("cleared")), r.get("wouldBridge", r.get("bridged")), r.get("placed")))
    if not r.get("success"): print("        ->", (r.get("message") or "")[:180])

sz = call("jawa/map_commit").get("mapSize") or {}
MX, MZ = sz.get("x", 250), sz.get("z", 250)
print("map is %d x %d (NOT assumed square)" % (MX, MZ))
W = min(45, MX - 20)
X0 = 10
X1 = X0 + W - 1
base = 40
ROWS = {"open": base, "wall": base+15, "shallow": base+30, "deep": base+45}
# a known-good test bed: concrete accepts a conduit everywhere
for z in ROWS.values():
    call("jawa/set_terrain_batch", ops="Concrete:%d,%d,%d,3" % (X0-2, z-1, W+4))
chk = call("jawa/build_check", rect="%d,%d,%d,1" % (X0, ROWS["open"], W), limit=W, **{"def":"PowerConduit"})
print("test bed painted: %d/%d cells accept a conduit" % (chk.get("acceptableCells"), W))

print("\n== 1. OPEN GROUND ==")
show("dry-run", call("jawa/connect_cells", **{"from":"%d,%d"%(X0,ROWS['open']),"to":"%d,%d"%(X1,ROWS['open'])}))
show("committed", call("jawa/connect_cells", dryRun=False, **{"from":"%d,%d"%(X0,ROWS['open']),"to":"%d,%d"%(X1,ROWS['open'])}))
c = call("jawa/build_check", rect="%d,%d,%d,1"%(X0,ROWS['open'],W), limit=W, **{"def":"PowerConduit"})
n = sum(1 for x in (c.get("cells") or []) if "PowerConduit" in (x.get("occupants") or []))
print("   conduit cells actually present: %d of %d" % (n, W))

print("\n== 2. STEEL WALL ACROSS IT ==")
z = ROWS["wall"]
call("jawa/build_batch", ops=";".join("Wall:%d,%d"%(X0+22,zz) for zz in range(z-1, z+2)), stuff="Steel")
show("strict", call("jawa/connect_cells", mode="strict", **{"from":"%d,%d"%(X0,z),"to":"%d,%d"%(X1,z)}))
show("mine", call("jawa/connect_cells", mode="mine", **{"from":"%d,%d"%(X0,z),"to":"%d,%d"%(X1,z)}))

print("\n== 3. SHALLOW WATER (bridgeable) ==")
z = ROWS["shallow"]
call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,1,3"%(X0+22,z-1))
show("strict", call("jawa/connect_cells", mode="strict", **{"from":"%d,%d"%(X0,z),"to":"%d,%d"%(X1,z)}))
show("bridge", call("jawa/connect_cells", mode="bridge", **{"from":"%d,%d"%(X0,z),"to":"%d,%d"%(X1,z)}))

print("\n== 4. DEEP WATER (not bridgeable) ==")
z = ROWS["deep"]
call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,1,3"%(X0+22,z-1))
show("bridge", call("jawa/connect_cells", mode="bridge", **{"from":"%d,%d"%(X0,z),"to":"%d,%d"%(X1,z)}))
print("   (a 1-wide strip inside a 3-wide bed is routed AROUND - correct)")

print("\n== 5. ENDPOINT ITSELF UNBUILDABLE ==")
call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,1,1"%(X1,ROWS['open']))
show("bad-endpoint", call("jawa/connect_cells", mode="bridge", **{"from":"%d,%d"%(X0,ROWS['open']),"to":"%d,%d"%(X1,ROWS['open'])}))
