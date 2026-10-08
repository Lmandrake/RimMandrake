import sys, json, re, time
sys.path.insert(0, r"src\RimMandrake\Utils")
exec(open(r"Transient\belt_ledges_a23.py").read().split("with rbc.RimBridge")[0])
with rbc.RimBridge(host, port, token, timeout=300.0) as rb:
    for i in range(4):
        step(rb, 3600)
        print("refuge", act(rb, "Report ledge refuge (current map)", "refuge:")[100:330])
        print("flood ", act(rb, "Report flood state (current map)", "RMFloodedCanyonDebug")[:140], "..", act(rb, "Report flood state (current map)", "RMFloodedCanyonDebug")[-20:])
