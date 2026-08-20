"""W8: calibrate the linter by INJECTING known defects and checking it finds exactly them."""
import sys, json, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=900.0); S.connect()
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

def show(tag, L):
    c = L.get("checks") or {}
    print("  [%s] total=%s" % (tag, L.get("totalFindings")))
    for k, v in c.items():
        if isinstance(v, dict):
            n = v.get("count")
            if n is None:
                print("     %-28s systems=%s noSea=%s trunkNoSea=%s" % (k, v.get("total"), v.get("reachingNoSea"), v.get("trunkSystemsReachingNoSea")))
            else:
                print("     %-28s %s" % (k, n))
    return c

print("== BASELINE on the untouched generated world ==")
b = call("jawa/world_lint")
cb = show("baseline", b)

print("\n== INJECT three defects we can name exactly ==")
# 1. Ocean biome on raised land
call("jawa/world_tile_set", tiles="7001,7002,7003", biome="Ocean", elevation=800.0)
# 2. Land biome submerged
call("jawa/world_tile_set", tiles="7010,7011", biome="TemperateForest", elevation=-50.0)
# 3. Coast mutator far inland (pick tiles that are not coastal)
call("jawa/world_mutators_set", action="add", mutators="Coast", tiles="7020,7021,7022,7023")
call("jawa/world_commit")
print("   injected: 3 waterBiomeOnRaisedLand, 2 landBiomeSubmerged, up to 4 stale Coast")

print("\n== AFTER injection ==")
a = call("jawa/world_lint")
ca = show("after", a)

print("\n== DELTAS - the linter must move by what we injected ==")
for k in ("waterBiomeOnRaisedLand", "landBiomeSubmerged", "staleMarineMutators"):
    before = (cb.get(k) or {}).get("count", 0)
    after = (ca.get(k) or {}).get("count", 0)
    print("   %-28s %s -> %s  (delta %+d)" % (k, before, after, after - before))
print("\n   examples the linter returned:")
for k in ("waterBiomeOnRaisedLand", "landBiomeSubmerged", "staleMarineMutators"):
    for e in ((ca.get(k) or {}).get("examples") or [])[:3]:
        print("     %-28s %s" % (k, e))

print("\n== RIVER RULE: trunks vs rivers allowed to die inland ==")
rs = ca.get("riverSystems") or {}
print("   systems:", rs.get("total"), " reachingNoSea:", rs.get("reachingNoSea"),
      " TRUNK systems reaching no sea:", rs.get("trunkSystemsReachingNoSea"))
print("   ", rs.get("note"))
