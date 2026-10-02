import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
with Session(strict=False, quiet=True, focus=False) as s:
    names = sorted(s.tools)
    open("Transient/northstar_probe/tools.txt","w").write("\n".join(names))
    print(len(names))
    for t in ("jawa/time_clock","jawa/map_info","rimworld/get_game_info"):
        try: print(t, json.dumps(s.call(t))[:400])
        except Exception as e: print(t, "ERR", e)
