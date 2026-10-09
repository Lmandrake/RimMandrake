import sys,time; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
show(call("rimworld/go_to_main_menu"),200)
for i in range(30):
    time.sleep(3)
    try:
        r=call("rimworld/get_game_info")
        if r.get("state",{}).get("programState")=="Entry": print("entry"); break
    except Exception: pass
