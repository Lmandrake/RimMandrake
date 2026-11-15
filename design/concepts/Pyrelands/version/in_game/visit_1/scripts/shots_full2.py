import sys, os, time, shutil
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
st=[(171,141),(126,217),(int(sys.argv[1]),int(sys.argv[2]))]
with RimBridge(h,p,tk) as rb:
    for i,(x,z) in enumerate(st):
        rb.call("jawa/clear_ui",{}); rb.call("rimworld/jump_camera_to_cell",{"x":x,"z":z})
        rb.call("rimworld/set_camera_zoom",{"rootSize":16}); time.sleep(0.4)
        pth=rb.call("rimworld/take_screenshot",{"fileName":"v1full_%d_%d"%(i,int(time.time()))}).get("path"); shutil.copy(pth, r"Transient\pv1\shots\full2_%d.png"%i); print("shot", i, pth[-30:])
    print(rb.call("rimworld/get_camera_state",{}).get("rootSize"))
