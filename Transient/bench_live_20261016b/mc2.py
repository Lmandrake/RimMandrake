from afk_lib import *
MC="RimMandrake.FlowWorks.MapControls.RM_MapControls"
def canal(): rows=rect(74,208,16,14); return wetn(rows),vol(rows)
for i in range(8):
    step(250); r=sc(MC,"Report").split("\n"); print(canal(),[x[-60:] for x in r if "sink" in x or x.startswith("controls")],flush=True)
