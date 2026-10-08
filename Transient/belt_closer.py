import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils/modcheck/live_queue"); sys.path.insert(0, "src/RimMandrake/Utils/rimbench"); sys.path.insert(0, "src/RimMandrake/Utils")
from common import call, open_session
end = time.time() + float(sys.argv[1])
n = 0
while time.time() < end:
    try:
        with open_session(False) as s:
            while time.time() < end:
                r = call(s, "jawa/window_list_close", action="close", typeName="Dialog_NamePlayerFactionAndSettlement", closeAll=True)
                n += (r or {}).get("closedCount") or 0
                time.sleep(2)
    except Exception as e:
        time.sleep(3)
print("closed", n)
