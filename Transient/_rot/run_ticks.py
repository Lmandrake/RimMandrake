import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
target = int(sys.argv[1]); speed = sys.argv[2] if len(sys.argv)>2 else "Ultrafast"
with RimBridge(host, port, token) as rb:
    t0 = rb.call("rimworld/get_game_info",{}).get("ticksGame")
    print("start ticks", t0, "-> +", target, flush=True)
    rb.call("jawa/set_game_speed",{"speed":speed})
    last=t0; stall=0
    while True:
        time.sleep(1)
        with RimBridge(host,port,token) as rb2:
            t = rb2.call("rimworld/get_game_info",{}).get("ticksGame")
        print("  ticks", t, "(+%d)"%(t-t0), flush=True)
        if t-t0 >= target: break
        if t==last:
            stall+=1
            if stall>4:
                print("STALLED at", t, flush=True); break
        else: stall=0
        last=t
with RimBridge(host, port, token) as rb:
    rb.call("jawa/set_game_speed",{"speed":"Paused"})
    s=rb.call("rimbridge/get_bridge_status",{}).get("state",{})
    print("paused:", s.get("paused"), "timeSpeed:", s.get("timeSpeed"), "ticks:", rb.call("rimworld/get_game_info",{}).get("ticksGame"))
