import sys, json, time, re; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
T="0370ddcc7f524e24a54e6cff36301136"
def B(t=60): b=RimBridge(token=T,timeout=t); b.connect(); return b
LOG=r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
mark=len(open(LOG,'rb').read()); print("log mark",mark)
b=B(30)
print("saves:", json.dumps(b.call("rimworld/list_saves",{},check=False))[:400])
try:
    r=b.call("rimworld/load_game_ready",{"saveName":"CANONICAL_ASHKARR_START_2026-09-12","timeoutMs":240000},check=False); print("load:", json.dumps(r)[:300])
except Exception as e: print("load raised (may be late):", str(e)[:160])
for i in range(40):
    time.sleep(10)
    try:
        b=B(20); r=b.call("jawa/map_info",{},check=False)
        if r.get("success"): print("map ready ~%ds:"%((i+1)*10), json.dumps(r)[:300]); break
    except Exception as e: print("poll",i,str(e)[:60])
s=open(LOG,'rb').read()[mark:].decode('utf-8','replace')
print("NEW log bytes:", len(s))
print("Could not load reference:", len(re.findall(r"Could not load reference",s)), "| BMT_ named:", len(re.findall(r"Could not load reference.*BMT_",s)))
print("NRE:", s.count("NullReferenceException"), "| Exception lines:", len(re.findall(r"Exception",s)))
for l in [l for l in s.split("\n") if "NullReferenceException" in l or "Exception" in l][:8]: print("  ",l[:220])
