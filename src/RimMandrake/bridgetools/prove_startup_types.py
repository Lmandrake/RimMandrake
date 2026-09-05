import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r

if "--selftest" in sys.argv:
    print("selftest: no live assertions to make offline for this tool (pure live enumeration). OK")
    sys.exit(0)

r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
print("start_debug_game_ready:", json.dumps(r)[:300])
for _ in range(60):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)

r_full = call("jawa/startup_types", kind="both", excludeVanilla=True)
print("=== jawa/startup_types (excludeVanilla=True) ===")
print("success:", r_full.get("success"), "count:", r_full.get("count"),
      "staticCtorError:", r_full.get("staticCtorError"), "modSubclassError:", r_full.get("modSubclassError"))

with open(r"D:\Luke\dev\Rimworld\Transient\startup_types_full_sweep.json", "w") as f:
    json.dump(r_full, f, indent=1)
print("full sweep written, count:", r_full.get("count"))

# suspects: anything whose type name mentions biome/animal/wildlife
KEYWORDS = ["biome", "animal", "wildlife", "wildanimal", "commonality"]
suspects = [row for row in (r_full.get("types") or [])
            if any(k in (row.get("typeName") or "").lower() for k in KEYWORDS)]
print(f"=== {len(suspects)} suspect rows (typeName mentions biome/animal/wildlife) ===")
for row in suspects:
    print(" ", row)

# mod summary
from collections import Counter
mod_counts = Counter((row.get("modName") or "UNKNOWN", row.get("modPackageId")) for row in (r_full.get("types") or []))
print(f"=== {len(mod_counts)} distinct mods own a StaticCtor/ModSubclass row ===")
for (name, pkg), n in mod_counts.most_common(30):
    print(f"  {n:4d}  {name}  ({pkg})")

r_bigsmall = call("jawa/startup_types", kind="staticctor", filter="BigSmall")
print("=== filter=BigSmall (previously-ruled-out lead, sanity check on full list) ===")
print(json.dumps(r_bigsmall)[:2000])
