import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, cell_center, grid_label

FAMROW = ["A_Colo", "B_Colossi", "C_Opee", "D_Sando", "E_Scalefish", "F_Swarm"]
out = {}


def shot(b, x, z, root, name):
    b.call("jawa/clear_ui", {})
    b.call("rimworld/set_camera_zoom", {"rootSize": root})
    b.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
    b.call("rimworld/set_camera_zoom", {"rootSize": root})
    cs = b.call("rimworld/get_camera_state", {})
    r = b.call("jawa/take_screenshot", {"fileName": name})
    p = r.get("path") or r.get("filePath")
    out[name] = p
    print(name, "root", cs.get("rootSize"), "view", json.dumps(cs.get("viewRect")), "->", str(p)[-70:])


with rb() as b:
    b.call("rimworld/set_camera_zoom_extension", {"enabled": True})
    b.call("jawa/screenshot_mode", {"enabled": True})
    shot(b, 103, 122, 65, "sb_overview_noon")
    for i, nm in enumerate(FAMROW):
        shot(b, 103, 32 + 36 * i, 29, "sb_row_%s" % nm)
    for i, c in enumerate(CREATURES):
        cx, cz = cell_center(i)
        shot(b, cx, cz, 10, "sb_cell_%s_%s" % (grid_label(i), c[0]))
    b.call("jawa/screenshot_mode", {"enabled": False})
json.dump(out, open(r"D:\Luke\dev\Rimworld\Transient\seabeast_review\shots.json", "w"), indent=1)
