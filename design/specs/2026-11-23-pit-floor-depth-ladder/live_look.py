"""The live look of the depth ladder (RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR): load the stepped-pit save, dig a
row of one-depth 3x3 pits (2, 3, 4, 6, 8, 12, 16 m) beside the 12 stepped cases, stand a colonist beside them, and capture at
default zoom and close, by day and by night. Run once on the build before the change ("before") and once after ("after").
This decides no bar: it stages and captures, and a person or a judge LOOKS.

    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python.exe design/specs/2026-11-23-pit-floor-depth-ladder/live_look.py <out_dir> <tag> [--load RM_STEPPED_PIT_12_CASES]
        [--save NAME]

LIES: a refused call is HARNESS (named in look.json); a pit that did not dig to its depth is SITE. Exit 0 when every capture
was written, 2 otherwise.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "src", "RimMandrake", "FlowWorks", "northstar"))
for p in (NS, os.path.abspath(os.path.join(NS, "..", "..", "Utils"))):
    if p not in sys.path:
        sys.path.insert(0, p)
import stepped_pit_stage as S  # noqa: E402

NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
LADDER_M = [2, 3, 4, 6, 8, 12, 16]
DEFAULT_ROOT, CLOSE_ROOT = 24.0, 8.0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("tag")
    ap.add_argument("--load", default=None)
    ap.add_argument("--save", default=None)
    ap.add_argument("--cases-origin", default="40,40")
    ap.add_argument("--ladder-origin", default="80,44")   # east of the 12 cases (x 40..72) and the water set (z 70..78)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    import validation_core as V      # noqa: E402
    import proof_hose as PH          # noqa: E402
    B = V.guard(PH.PB())
    res = {"tag": a.tag, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "harness": [], "site": [], "captures": {}}
    out_json = os.path.join(a.out_dir, "look_%s.json" % a.tag)

    def save():
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def call(method, arg):
        r = B.call("jawa/static_call", type=NPROOF, method=method, args=arg, _answer=True) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (r.get("success") is True and not txt.startswith("REFUSED")), txt

    if a.load:
        B.call("rimworld/load_game", saveName=a.load)
        ok = False
        for _ in range(150):
            time.sleep(6)
            try:
                if (B.call("rimworld/get_game_info") or {}).get("status") == "game_loaded":
                    ok = True
                    break
            except Exception:
                pass
        if not ok:
            res["harness"].append("load of %s never reached game_loaded" % a.load)
            save()
            return 2
        time.sleep(20)
        res["loaded"] = a.load
    B.call("rimworld/set_time_speed", speed="Paused")

    def set_hour(h):
        t = B.call("jawa/time_clock") or {}
        ta, tg = t.get("ticksAbs"), t.get("ticksGame")
        if ta is None or tg is None:
            res["harness"].append("time_clock unreadable: %s" % str(t)[:120])
            return
        delta = (int(h * 2500) - ta % 60000) % 60000
        B.call("jawa/time_set_ticks", ticks=int(tg + delta), timeException=True, why="pit depth ladder look: %g h light" % h)
        B.call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000)
        time.sleep(1.5)

    lx, lz = (int(v) for v in a.ladder_origin.split(","))
    w = len(LADDER_M) * 4 + 1
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (lx - 3, lz - 3, w + 6, 9), categories="All")
    B.call("jawa/set_terrain", x=lx - 3, z=lz - 3, terrainDef="Soil", width=w + 6, height=9)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % (lx - 3, lz - 3, w + 6, 9))
    ok, txt = call("ProofResetRect", "%d;%d;%d;%d" % (lx - 1, lz - 1, w + 1, 5))
    if not ok:
        res["harness"].append("ProofResetRect refused: " + txt[:160])
    B.call("jawa/mod_settings_field", typeName="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings", field="pitSteppedReliefEnabled",
           action="set", value="True")
    res["ladder"] = []
    for i, m in enumerate(LADDER_M):
        n = int(m * 2)
        ok, txt = call("ProofStageBasin", "%d;%d;3;3;%d;0.0;RM_Fluid_Water" % (lx + i * 4, lz, n))
        res["ladder"].append([m, lx + i * 4, lz, ok, txt[:100]])
        if not ok:
            res["site"].append("pit %g m: %s" % (m, txt[:120]))
    # a colonist for scale: beside the 2 m pit, and one beside his L (case 1)
    cx, cz = (int(v) for v in a.cases_origin.split(","))
    sx, sz = S.slot_origin(0, cx, cz)
    for x, z in ((lx - 2, lz + 1), (sx + 5, sz + 7)):
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, count=1) or {}
        if not (r.get("pawns") or r.get("success")):
            res["harness"].append("colonist at %d,%d: %s" % (x, z, str(r)[:120]))
    B.call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000)
    B.call("jawa/clear_ui", all=True)
    save()

    stamp = time.strftime("%H%M%S")

    def shot(key, x, z, wd, ht, root, pad=1):
        name = "pdl_%s_%s_%s" % (a.tag, stamp, key)
        r = B.call("rimworld/screenshot_cell_rect", x=x, z=z, width=wd, height=ht, paddingCells=pad, fileName=name,
                   rootSize=root, suppressMessage=True) or {}
        src = r.get("path")
        S.wait_file(src)
        if not src:
            res["harness"].append("no capture %s: %s" % (key, str(r.get("message") or r)[:120]))
            return
        dst = os.path.join(a.out_dir, "%s_%s.png" % (a.tag, key))
        try:
            if os.name != "nt":
                from game_paths import win_to_wsl
                src = win_to_wsl(src)
            shutil.copyfile(src, dst)
            res["captures"][key] = dst
        except OSError as e:
            res["harness"].append("copy %s: %s" % (key, e))
        save()

    for hour, label in ((12, "day"), (0, "night")):
        set_hour(hour)
        g = B.call("jawa/glow_at", cells="%d,%d" % (lx + 1, lz + 1)) or {}
        res["light_" + label] = {"hour": g.get("hour"), "skyGlow": g.get("skyGlow"),
                                 "groundGlow": ((g.get("cells") or [{}])[0]).get("groundGlow")}
        shot("ladder_default_" + label, lx - 3, lz - 1, w + 2, 5, DEFAULT_ROOT)
        shot("cases_default_" + label, cx, cz, S.NCOL * S.SLOT, 3 * S.SLOT, DEFAULT_ROOT)
        if label == "day":
            for i, m in enumerate(LADDER_M):
                shot("ladder_close_%02dm" % m, lx + i * 4 - (2 if i == 0 else 0), lz, 3 + (2 if i == 0 else 0), 3, CLOSE_ROOT)
            for k in range(len(S.CASES)):
                ox, oz = S.slot_origin(k, cx, cz)
                shot("case_close_%02d" % (k + 1), ox, oz, S.SLOT, S.SLOT, CLOSE_ROOT, pad=0)
    set_hour(12)
    if a.save:
        sv = B.call("rimworld/save_game", saveName=a.save) or {}
        res["save"] = {"name": a.save, "ok": sv.get("success"), "reply": str(sv)[:160]}
    res["verdict"] = "CAPTURED" if not res["harness"] else "HARNESS"
    save()
    print(res["verdict"], len(res["captures"]), "captures;", out_json, "; site:", res["site"][:3], "; harness:", res["harness"][:3])
    return 0 if not res["harness"] else 2


if __name__ == "__main__":
    sys.exit(main())
