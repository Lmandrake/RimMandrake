import sys,time,json
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar"); sys.path.insert(0,"src/RimMandrake/FlowWorks")
import proof_hose as PH
def st():
    try: return PH.PB().call("rimworld/get_game_info").get("state",{}).get("programState")
    except Exception: return None
def wait(f,s):
    t=time.time()
    while time.time()-t<s:
        if f(): return True
        time.sleep(4)
    return False
if st()=="Playing":
    try: PH.PB().call("rimworld/go_to_main_menu")
    except Exception as e: print("menu call",type(e).__name__)
    print("entry", wait(lambda: st()=="Entry",180))
try: PH.PB().call("rimworld/load_game",saveName="RM_FW_walk_20261016",ignoreModCompatibility=True)
except Exception as e: print("load call",type(e).__name__)
print("playing", wait(lambda: st()=="Playing",420))
time.sleep(45)
b=PH.PB(); g=b.call("rimworld/get_game_info"); print(g.get("ticksGame"),g.get("state"))
print(b.call("jawa/map_info").get("tile"))
