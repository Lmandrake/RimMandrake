import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
for i in range(10):
    with RimBridge(host, port, token) as rb:
        rb.call("jawa/room_heat",{"x":63,"z":103,"mode":"set","value":-15})
        rb.call("jawa/set_game_speed",{"speed":"Ultrafast"})
    time.sleep(3)
    with RimBridge(host, port, token) as rb:
        rb.call("jawa/set_game_speed",{"speed":"Paused"})
        t=rb.call("jawa/cell_temperature",{"cell":"63,103"}).get("temperature")
        cold=rb.call("jawa/inspect_string",{"rect":"61,101,5,5"}).get("things",[])
        ctl=rb.call("jawa/inspect_string",{"thingIds":"RUT_Tea_Bioregeneration39996"}).get("things",[])
        tg=rb.call("rimworld/get_game_info",{}).get("ticksGame")
        print(i,"ticks",tg,"coldTemp",round(t,1),"|COLD",[ (x["defName"],x.get("inspect")) for x in cold],"|CTRL",[(x["defName"],x.get("inspect")) for x in ctl], flush=True)
