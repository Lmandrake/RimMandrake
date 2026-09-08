import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, cell_center, grid_label

FAMROW = ["A_Colo", "B_Colossi", "C_Opee", "D_Sando", "E_Scalefish", "F_Swarm"]
out = {}
with rb() as b:
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    b.call("rimworld/set_camera_zoom_extension", {"enabled": True})

    r = b.call("rimworld/screenshot_cell_rect",
               {"x": 20, "z": 20, "width": 170, "height": 198,
                "paddingCells": 0, "rootSize": 100,
                "fileName": "sb_overview_20260903"})
    out["overview"] = r.get("path") or r.get("filePath") or r.get("message")
    print("OVERVIEW:", json.dumps(r)[:300])

    for i, nm in enumerate(FAMROW):
        cz = 32 + 36 * i
        r = b.call("rimworld/screenshot_cell_rect",
                   {"x": 20, "z": cz - 15, "width": 170, "height": 30,
                    "paddingCells": 0, "rootSize": 60,
                    "fileName": "sb_row_%s_20260903" % nm})
        out[nm] = r.get("path") or r.get("filePath") or r.get("message")
        print(nm, json.dumps(r)[:200])

    for i, c in enumerate(CREATURES):
        cx, cz = cell_center(i)
        r = b.call("rimworld/screenshot_cell_rect",
                   {"x": cx - 26, "z": cz - 15, "width": 52, "height": 30,
                    "paddingCells": 0, "rootSize": 20,
                    "fileName": "sb_cell_%s_%s_20260903" % (grid_label(i), c[0])})
        out[grid_label(i)] = r.get("path") or r.get("filePath") or r.get("message")
        print(grid_label(i), c[0], str(out[grid_label(i)])[:140])

    b.call("jawa/screenshot_mode", {"enabled": False})
json.dump(out, open(r"D:\Luke\dev\Rimworld\Transient\seabeast_review\shots.json", "w"), indent=1)
