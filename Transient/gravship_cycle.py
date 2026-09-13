import sys, os, time, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
SAVE="gravship_f_consolidated_names_2026-09-09"
SAVES = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
try:
    with fresh() as rb:
        print("queue:", str(rb.call("rimworld/load_game", {"saveName": SAVE, "ignoreModCompatibility": True}))[:150], flush=True)
except Exception as e: print("queue call ended:", str(e)[:120], flush=True)
saw_quiet=False; answered=0
for i in range(48):
    time.sleep(10)
    try:
        with fresh() as rb:
            rb.call("rimbridge/ping", {}) if False else None
            fx = rb.call("jawa/list_factions", {})
            answered+=1
            if saw_quiet or answered>=6:  # either we watched the reload gap, or 60s of steady answers post-queue
                txt=str(fx); print(f"loaded (poll {i}); probes:", flush=True)
                for p in ("RUT_Jawa_Junkers","Jawa_Junkers"):
                    print(" ", p, "PRESENT" if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])"%p, txt) else "absent", flush=True)
                break
    except Exception as e:
        saw_quiet=True; print(f"poll {i}: quiet ({str(e)[:60]})", flush=True)
else:
    print("NEVER settled — no mutation", flush=True); sys.exit(2)
print("settling 45s", flush=True); time.sleep(45)
before={f:os.path.getsize(os.path.join(SAVES,f)) for f in os.listdir(SAVES) if f.endswith('.rws')}
with fresh() as rb:
    print("save_game:", str(rb.call("rimworld/save_game", {"saveName": SAVE}))[:150], flush=True)
time.sleep(8)
after={f:os.path.getsize(os.path.join(SAVES,f)) for f in os.listdir(SAVES) if f.endswith('.rws')}
print("new:", [f for f in after if f not in before], flush=True)
print("changed:", [f"{f}: {before[f]}->{after[f]}" for f in after if f in before and after[f]!=before[f]], flush=True)
print("DONE", flush=True)
