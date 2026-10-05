"""belt_bridge5: capture the post-v2 FlowWorks map for the owner -- one screenshot per scene group, then a
review savegame (Saves stat before/after: the wrong-slot trap). python.exe, from the repo root."""
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.join("src", "RimMandrake", "FlowWorks", "northstar"))
import validation_v2 as V  # noqa: E402

SAVES = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"
NAME = "NS_FlowWorks_Review_20261005"
OUT = os.path.join("Transient", "belt_bridge5_review")
GROUPS = [  # (key, x, z, w, h, what)
    ("X_promoted", 128, 67, 16, 21, "X scenes: pawn sink strip (z70), two fluids + junction (z74-76), tar/water/viscosity-off races (z79/82/85), cover deck (140,70)"),
    ("P_pits", 128, 96, 47, 9, "P scenes: 1x1 / trench / 2x2 pits, small vs large occupant; walk-in + ladder (166,100); control (172,100)"),
    ("S_ladder", 128, 58, 11, 9, "S scenes: fill ladder D1..D4 (z60), fill clamp (z64)"),
    ("J_jobs", 178, 57, 24, 6, "J scenes: open vs roofed cell (180/182,60), fill-in, overflow, dig job (190-200,60)"),
    ("E5_sinks", 198, 3, 25, 28, "E5 sink scenes: sink on (x200), inner (x210), sink off (x220)"),
    ("E2_flow", 10, 54, 12, 16, "E2 flow from bodies: east/north/south arms"),
    ("E3_E4", 58, 140, 25, 12, "E3 budget (x60), E3b recede (x70), E4 engine (x80)"),
]


def stat(d):
    return {f: os.path.getsize(os.path.join(d, f)) for f in os.listdir(d) if f.endswith(".rws")}


def main():
    os.makedirs(OUT, exist_ok=True)
    B = V.RealBridge()
    B.call("jawa/clear_ui", all=True)
    B.call("jawa/window_list_close", action="close", typeName="EditWindow_Log")
    rep = {"shots": {}, "pawns": None}
    for key, x, z, w, h, what in GROUPS:
        r = B.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=1)
        p = r.get("path")
        local = None
        if p and os.path.isfile(p):
            local = os.path.join(OUT, key + os.path.splitext(p)[1])
            shutil.copyfile(p, local)
        rep["shots"][key] = dict(what=what, rect=[x, z, w, h], ok=bool(r.get("success")), src=p, file=local)
        print(key, r.get("success"), local)
    rep["pawns"] = [(q.get("id"), q.get("faction"), q.get("x"), q.get("z"))
                    for q in B.call("jawa/list_pawns", limit=200).get("pawns") or []]
    before = stat(SAVES)
    if NAME + ".rws" in before:
        raise SystemExit("review save already exists; never overwritten")
    rs = B.call("rimworld/save_game", saveName=NAME)
    time.sleep(3)
    after = stat(SAVES)
    changed = [f for f in before if f in after and after[f] != before[f]]
    new = [f for f in after if f not in before]
    rep["save"] = dict(call=bool(rs.get("success")), new=new, changed=changed)
    print("save:", rep["save"])
    json.dump(rep, open(os.path.join(OUT, "capture.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
