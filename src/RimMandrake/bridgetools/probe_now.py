import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=45.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
def one(label):
    try:
        p = call("jawa/load_stall_probe")
        print(f"=== {label} @ {time.strftime('%H:%M:%S')} ===")
        for k in ("programState","coreStaticAssetsLoaded","queuedEventCount",
                  "executingToExecuteWhenFinished","currentEvent","toExecuteWhenFinished",
                  "eventThread","fieldErrors"):
            print(k, "=", json.dumps(p.get(k))[:1200])
        print("topThreads =", json.dumps(p.get("topThreads")))
        return p
    except Exception as ex:
        print(f"{label} PROBE FAILED: {ex!r}")
        return None
a = one("READING 1")
time.sleep(30)
b = one("READING 2")
if a and b:
    ta = {t["id"]: t["cpuSeconds"] for t in (a.get("topThreads") or [])}
    print("\n=== cpu delta over 30s ===")
    for t in (b.get("topThreads") or []):
        d = t["cpuSeconds"] - ta.get(t["id"], t["cpuSeconds"])
        print(f"  thread {t['id']}: +{d:.1f}s  (now {t['cpuSeconds']}s) state={t['state']} wait={t.get('waitReason')}")
