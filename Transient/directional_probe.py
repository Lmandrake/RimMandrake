import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
rb = RimBridge(host=host, port=port, token=token).connect()

# Holmes at (112,12) per live list_pawns
hx, hz = 112, 12
rootsize = 12.0

def shoot(cx, cz, name):
    rb.call("jawa/clear_ui", {})
    rb.call("rimworld/jump_camera_to_cell", {"x": cx, "z": cz})
    rb.call("rimworld/set_camera_zoom", {"rootSize": rootsize})
    time.sleep(0.6)
    cam = rb.call("rimworld/get_camera_state", {})
    print(name, "cam mapPos", cam.get("mapPosition"), "root", cam.get("rootSize"))
    r = rb.call("rimworld/take_screenshot", {"fileName": name, "suppressMessage": True})
    print("  shot:", r.get("path"))

# camera centered ON Holmes but approached differently doesn't change framing;
# to test "camera north of him" vs "camera south of him" we center the CAMERA
# at a point north or south of Holmes, so Holmes sits off-center in the frame
# (south of screen-center when camera is north of him, and vice versa) while
# keeping Holmes in view at rootSize 12.
shoot(hx, hz + 8, "dirprobe_cam_north_of_holmes")   # camera north (higher z) of Holmes -> Holmes appears toward bottom/south of frame
shoot(hx, hz - 8, "dirprobe_cam_south_of_holmes")   # camera south (lower z) of Holmes -> Holmes appears toward top/north of frame
shoot(hx, hz, "dirprobe_cam_centered_on_holmes")
