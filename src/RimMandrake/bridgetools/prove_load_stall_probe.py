"""Interrogate a cold-load stall live: call jawa/load_stall_probe twice, 30s apart.

COLD_LOAD_STALL_INTERMITTENT_1. Run under WINDOWS python.exe while RimWorld is
stuck loading (or healthy - a baseline reading is valuable too).

DELIBERATELY never calls start_debug_game_ready or anything that marshals to the
main thread: during a stall the main thread never services the queue, and such a
call would hang this script alongside the game. The probe reads static state from
the bridge thread; two readings 30s apart let the cpuSeconds diff name the
spinning native thread.
"""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=60.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

def snap(label):
    out = {"label": label, "t": time.strftime("%H:%M:%S")}
    try:
        out["probe"] = call("jawa/load_stall_probe")
    except Exception as ex:
        out["probe_error"] = repr(ex)
    return out

a = snap("first")
print(json.dumps(a, indent=1)[:6000])
time.sleep(30)
b = snap("second")

# name the spinner: biggest cpuSeconds delta between readings. A thread absent
# from the first snapshot (not yet in its top-8) is treated as a 0s baseline so a
# thread that only STARTS spinning during the 30s window still shows up here.
try:
    ta = {t["id"]: t for t in a["probe"]["topThreads"]}
    rows = []
    for t in b["probe"]["topThreads"]:
        prev = ta.get(t["id"], {"cpuSeconds": 0})
        rows.append((t["cpuSeconds"] - prev["cpuSeconds"], t))
    rows.sort(reverse=True, key=lambda r: r[0])
    print("\n=== cpuSeconds delta over 30s (top spinners) ===")
    for d, t in rows[:5]:
        print(f"  thread {t['id']}: +{d:.1f}s state={t['state']} wait={t.get('waitReason')}")
except Exception as ex:
    print("delta analysis failed:", repr(ex))

print("\n=== second reading, load-state core ===")
p = b.get("probe", {})
print(json.dumps({k: p.get(k) for k in
    ("programState", "coreStaticAssetsLoaded", "currentEvent",
     "queuedEventCount", "executingToExecuteWhenFinished",
     "toExecuteWhenFinished", "eventThread", "fieldErrors")}, indent=1))
