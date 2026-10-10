"""Live check of the 2026-10-10 Cracked Lands + Wastes enactment: a cleared, lit, unfogged plot with each
changed creature/plant spawned on a grid, one wide shot plus one shot per subject. python.exe, repo root."""
import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from scenes import scenelib as S

SUBJECTS = ["RM_Uttaqar", "RM_Muttavaq", "RSW_Borcatu", "RM_Frethik", "RM_Kroffa", "VAEWaste_Megatardi",
            "RSW_SandLeaper", "RSW_MutagenicNorphea", "RSW_SandPillar", "RUT_EmperorVulture", "RM_Tarruq",
            "RM_VaultRoot", "RM_WastelandScorchedStars", "RM_TwistingThorngrass"]
PLANTS = SUBJECTS[-3:]
X0, Z0, COLS, PITCH = 100, 100, 7, 6
W, H = COLS * PITCH + 2, 2 * PITCH + 4
OUT = os.path.join("Transient", "live_sheet_check_2026-10-10")

sc = S.Scene("sheetcheck", x=X0, z=Z0, w=W, h=H)
S.quiet(); sc.clear(); sc.floor("Soil")
S.call("jawa/set_fog", action="unfog", rect=sc.rect)
sc.time_of_day(12)
S.call("jawa/clear_ui")
res = {}
for i, k in enumerate(SUBJECTS):
    dx, dz = 3 + (i % COLS) * PITCH, 3 + (i // COLS) * PITCH
    r = sc.put(k, dx, dz) if k in PLANTS else S.call("jawa/spawn_pawn", kindDef=k, x=X0 + dx, z=Z0 + dz, faction="none")
    res[k] = {"cell": [X0 + dx, Z0 + dz], "spawn_ok": S.ok(r), "spawn": json.dumps(r, default=str)[:160]}
S.call("jawa/set_game_speed", speed=0)
S.call("rimworld/jump_camera_to_cell", x=X0 + W // 2, z=Z0 + H // 2)
wide = S.call("rimworld/screenshot_cell_rect", x=X0, z=Z0, width=W, height=H, paddingCells=1, fileName="sheetcheck_wide")
res["_wide"] = wide.get("path") if isinstance(wide, dict) else str(wide)
for k in SUBJECTS:
    x, z = res[k]["cell"]
    s = S.call("rimworld/screenshot_cell_rect", x=x - 2, z=z - 2, width=5, height=5, paddingCells=0, fileName="sheetcheck3_" + k)
    res[k]["shot"] = s.get("path") if isinstance(s, dict) else str(s)
    print(k, res[k]["spawn_ok"], res[k]["spawn"][:90])
json.dump(res, open(os.path.join(OUT, "result.json"), "w"), indent=1)
print("wide", res["_wide"])
