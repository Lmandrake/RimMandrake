"""Live contact board: stage a recipe, capture a clean plate and the board OFF-SCREEN, segment, check, report.

Run from WSL (numpy/PIL live there; Windows python has neither). The bridge binds Windows loopback, which WSL
cannot reach, so each bridge call is relayed through Windows python.exe running the mirror's
rimbridge_client.py (D:\\Luke\\dev\\RimMandrake\\src\\RimMandrake\\Utils). Under python.exe itself the calls go
in-process, but the analysis step then needs numpy.

    cd src/RimMandrake/Utils
    python3 -m artboard.live flowworks_pit_states --origin 40,30 [--out /mnt/d/...] [--ppc 48] [--no-plate] [--dry-run]

<recipe> is a name from artboard.recipes.RECIPES or a recipe JSON path. --origin is the map cell of the
recipe's local (0,0); the whole capture rect (printed by --dry-run) must lie on open map, and it is CLEARED
(non-player things destroyed, excavations filled back, ground terrain laid). Player pawns in it refuse the run.

Steps: artboard_stage phase=ground -> artboard_capture (plate.png) -> artboard_stage phase=subjects ->
artboard_capture (board.png) -> board.json with the capture's exact mapping -> artboard.run -> live_report.json.
A subject whose staging was refused is dropped from the board and listed as STAGE_REFUSED - never captured
on a cell it does not occupy. Nothing here moves the user's camera, resizes or focuses the window.
"""
import argparse
import datetime
import json
import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from artboard import recipes, run as runmod  # noqa: E402
else:
    from . import recipes, run as runmod

UTILS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIN = os.name == "nt"
DEFAULT_ROOT = r"D:\Luke\dev\_rmscratch\artboard" if WIN else "/mnt/d/Luke/dev/_rmscratch/artboard"
MIRROR_CLIENT = r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\rimbridge_client.py"


def to_win(path):
    """A path the GAME (a Windows process) can write: /mnt/d/x -> D:\\x. Pure; selftested."""
    if WIN or (len(path) > 1 and path[1] == ":"):
        return path
    parts = path.split("/")
    if len(parts) > 3 and parts[1] == "mnt" and len(parts[2]) == 1:
        return parts[2].upper() + ":\\" + "\\".join(parts[3:])
    raise ValueError("output must be on a Windows drive (/mnt/<letter>/...) so the game can write it: " + path)


def _bridge():
    if not WIN:
        import subprocess

        def relay(tool, **p):
            r = subprocess.run(["python.exe", MIRROR_CLIENT, "--call", tool, "--json", json.dumps(p),
                                "--yes-i-know-this-is-live", "--timeout", "600"],
                               capture_output=True, text=True)
            if r.returncode != 0:
                return {"success": False, "message": "bridge relay exit %d: %s" % (r.returncode, r.stderr.strip()[-600:])}
            out = json.loads(r.stdout)
            if isinstance(out, dict) and out.get("content"):
                try:
                    out = json.loads(out["content"][0]["text"])
                except Exception:
                    pass
            return out
        return relay
    sys.path.insert(0, UTILS)
    import rimbridge_client as rb
    host, port, token = rb.resolve_endpoint()
    s = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
    s.connect()

    def call(tool, **p):
        r = s.call(tool, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r
    return call


def subject_status(stage_result, by_id):
    """{subject id: [error strings]} for every subject with a refused op (pure; selftested)."""
    errs = {}
    rows = {r.get("id"): r for r in (stage_result or {}).get("ops", [])}
    for sid, oids in by_id.items():
        for oid in oids:
            r = rows.get(oid)
            if r is None:
                errs.setdefault(sid, []).append("%s: no result returned" % oid)
            elif not r.get("ok"):
                errs.setdefault(sid, []).append("%s: %s" % (oid, r.get("error")))
    return errs


def capture_warnings(cap):
    w = []
    if cap.get("foggedCells"):
        w.append("%d fogged cells in the capture rect" % cap["foggedCells"])
    if cap.get("roofedCells"):
        w.append("%d roofed cells in the capture rect" % cap["roofedCells"])
    if cap.get("skyGlow") is not None and cap["skyGlow"] < 0.9:
        w.append("sky glow %.2f < 0.9 - not full daylight; colour checks are unreliable" % cap["skyGlow"])
    if cap.get("cameraRestored") is False:
        w.append("the main camera did not read back as restored after the render")
    return w


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("recipe")
    ap.add_argument("--origin", required=True, help="map cell x,z of the recipe's local (0,0)")
    ap.add_argument("--out", help="output folder (default %s\\<recipe>_<time>)" % DEFAULT_ROOT)
    ap.add_argument("--ppc", type=int, help="pixels per cell (default: the recipe's)")
    ap.add_argument("--no-plate", action="store_true", help="skip the clean plate (ring-mode foreground)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan; touch nothing")
    a = ap.parse_args(argv)

    recipe = recipes.load(a.recipe)
    origin = [int(v) for v in a.origin.split(",")]
    pl = recipes.plan(recipe, origin)
    ppc = a.ppc or int(recipe.get("ppc", 48))
    cx, cz, cw, ch = pl["capture_rect"]
    print("PLAN %s: %d subjects, %d ops, capture/clear rect x=%d z=%d %dx%d cells -> %dx%d px at %d px/cell"
          % (recipe["name"], len(recipe["subjects"]), len(pl["ops"]), cx, cz, cw, ch, cw * ppc, ch * ppc, ppc))
    if a.dry_run:
        print("\n".join(pl["ops"]))
        return 0

    out = os.path.abspath(a.out or os.path.join(
        DEFAULT_ROOT, "%s_%s" % (recipe["name"], datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))))
    os.makedirs(out, exist_ok=True)
    win_out = to_win(out)
    ops_path = os.path.join(out, "stage_ops.txt")
    with open(ops_path, "w") as fh:
        fh.write("\n".join(pl["ops"]) + "\n")
    call = _bridge()
    rect_s = "%d,%d,%d,%d" % tuple(pl["clear_rect"])
    log = {"recipe": recipe["name"], "origin": origin, "plan": {k: v for k, v in pl.items() if k != "ops"},
           "ppc": ppc, "warnings": []}

    g = call("jawa/artboard_stage", phase="ground", clearRect=rect_s, ground=recipe.get("ground") or "")
    log["stage_ground"] = g
    if not g.get("success"):
        json.dump(log, open(os.path.join(out, "live_report.json"), "w"), indent=1)
        print("STAGE GROUND FAILED: %s -> %s" % (g.get("message"), out))
        return 2
    cap_args = dict(x=cx, z=cz, w=cw, h=ch, ppc=ppc)
    plate = None
    if not a.no_plate:
        pc = call("jawa/artboard_capture", path=win_out + "\\plate.png", **cap_args)
        log["capture_plate"] = pc
        if not pc.get("success"):
            print("PLATE CAPTURE FAILED: %s" % pc.get("message"))
            json.dump(log, open(os.path.join(out, "live_report.json"), "w"), indent=1)
            return 3
        plate = "plate.png"
    st = call("jawa/artboard_stage", phase="subjects", opsPath=to_win(ops_path))
    log["stage_subjects"] = st
    if pl.get("gss_ops"):
        # Gimme Some Slack state ops (charge, lay, flow, end, look, link, cut, ticks) after the things exist
        gpath = os.path.join(out, "gss_ops.txt")
        with open(gpath, "w") as fh:
            fh.write("\n".join(pl["gss_ops"]) + "\n")
        gs = call("jawa/gss_stage", opsPath=to_win(gpath))
        log["stage_gss"] = gs
        st = dict(st or {}, ops=list((st or {}).get("ops", [])) + list((gs or {}).get("ops", [])))
    refused = subject_status(st, pl["by_id"])
    log["stage_refused"] = refused
    bc = call("jawa/artboard_capture", path=win_out + "\\board.png", **cap_args)
    log["capture_board"] = bc
    if not bc.get("success"):
        print("BOARD CAPTURE FAILED: %s" % bc.get("message"))
        json.dump(log, open(os.path.join(out, "live_report.json"), "w"), indent=1)
        return 3
    log["warnings"] += capture_warnings(bc)
    board = recipes.board_json(recipe, origin, bc, "board.png", plate, drop=refused)
    bpath = os.path.join(out, "board.json")
    json.dump(board, open(bpath, "w"), indent=1)
    rep = runmod.run(bpath, out)
    log["artboard"] = {k: rep[k] for k in ("subjects", "passed_tier_a", "flagged", "by_check", "fg_mode")}
    json.dump(log, open(os.path.join(out, "live_report.json"), "w"), indent=1)
    print("ARTBOARD LIVE %s: staged %d/%d subjects (%d refused), %d passed tier a, %d flagged %s%s -> %s"
          % (recipe["name"], len(recipe["subjects"]) - len(refused), len(recipe["subjects"]), len(refused),
             rep["passed_tier_a"], rep["flagged"], {k: len(v) for k, v in rep["by_check"].items()},
             ("; WARN " + "; ".join(log["warnings"])) if log["warnings"] else "", out))
    for sid, errs in refused.items():
        print("  STAGE_REFUSED %s: %s" % (sid, "; ".join(errs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
