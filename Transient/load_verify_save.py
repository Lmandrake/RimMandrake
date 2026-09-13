import sys, time, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
SAVE = sys.argv[1]
SAVES = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
print(f"=== loading {SAVE}", flush=True)
try:
    with fresh() as rb:
        r = rb.call("rimworld/load_game", {"saveName": SAVE, "ignoreModCompatibility": True})
        print("load_game:", str(r)[:200], flush=True)
except Exception as e:
    print("load_game call ended (expected if long):", str(e)[:150], flush=True)
ready = False
for i in range(60):
    time.sleep(10)
    try:
        with fresh() as rb:
            r = rb.call("rimworld/load_game_ready", {})
            print(f"poll {i}: {str(r)[:150]}", flush=True)
            if r.get("ready") or r.get("loaded") or r.get("success") and r.get("gameLoaded"): ready=True; break
    except Exception as e:
        print(f"poll {i} err: {str(e)[:100]}", flush=True)
if not ready: print("NOT READY after 10min — stopping before any mutation", flush=True); sys.exit(2)
print("settling 45s", flush=True); time.sleep(45)
with fresh() as rb:
    fx = rb.call("jawa/list_factions", {})
    txt = str(fx)
    for probe in ("RUT_Jawa_Junkers","RUT_Jawa_HuttCartel","RUT_Jawa_DeepwaterCompact","Jawa_Junkers"):
        print(f"faction probe {probe}: {'PRESENT' if probe in txt else 'absent'}", flush=True)
before = {f: os.path.getsize(os.path.join(SAVES,f)) for f in os.listdir(SAVES) if f.endswith('.rws')}
with fresh() as rb:
    sv = rb.call("rimworld/save_game", {"saveName": SAVE})
    print("save_game:", str(sv)[:200], flush=True)
time.sleep(8)
after = {f: os.path.getsize(os.path.join(SAVES,f)) for f in os.listdir(SAVES) if f.endswith('.rws')}
changed = [f for f in after if after[f] != before.get(f)]
new = [f for f in after if f not in before]
print("files new:", new, "· files changed:", changed, flush=True)
print("DONE", flush=True)
