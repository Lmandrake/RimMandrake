import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
b=RimBridge(token="0370ddcc7f524e24a54e6cff36301136",timeout=60); b.connect()
r=b.call("rimworld/load_game_ready",{"saveName":"CANONICAL_ASHKARR_START_2026-09-12","timeoutMs":240000,"ignoreModCompatibility":True},check=False)
print(r.get("message")); print(json.dumps({k:v for k,v in r.items() if k not in ("message",)})[:1200])
import time,re
LOG=r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
for i in range(40):
    time.sleep(10)
    try:
        b2=RimBridge(token="0370ddcc7f524e24a54e6cff36301136",timeout=20); b2.connect()
        g=b2.call("rimworld/get_game_info",{},check=False)
        if g.get("programState")=="Playing" or g.get("status")=="game_loaded":
            print("loaded ~%ds:"%((i+1)*10), json.dumps(g)[:300]); break
    except Exception as e: print("poll",i,str(e)[:60])
