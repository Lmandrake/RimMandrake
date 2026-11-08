"""g8_harness.py -- debug the FlowWorks-free half of the g8 harness on whatever game A runs (a quick-test colony is started
from the main menu if no game is up). Reads the shapes the g8 scripts depend on and records them in a g8 run folder:

  python.exe ralph/live/g8_harness.py [--no-start]

  shot      screenshot_cell_rect into the run's shots/ through outputDirectory (a \\\\wsl path), and the PNG size of a known
            rect at root 7.2 and 20 (how many cells a frame holds on Steve's window)
  rows      the row keys of pawn_census, list_things and build_batch (position, rotation, id names)
  pawn      subject(): spawn on a cell, uniform look, draft, face south; walk_to one cell; settle (play_for + settle_tweens)
  quiet     storyteller_swap / difficulty_tune / weather_set / incident_queue_clear answers
  ground    clear_area + set_roof_batch + set_terrain_batch Soil on a small rect, read back
"""
import argparse
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g8_common as C  # noqa: E402
from g8_common import j, safe  # noqa: E402


def png_size(path):
    try:
        with open(path, "rb") as f:
            head = f.read(24)
        return struct.unpack(">II", head[16:24])
    except (OSError, struct.error):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-start", action="store_true")
    a = ap.parse_args()
    B = C.bridge()
    R = C.Run("harness", "probe")
    try:
        gi = B.call("rimworld/get_game_info") or {}
        R.log("game", j(gi.get("state"), 200))
        if (gi.get("state") or {}).get("programState") != "Playing" and not a.no_start:
            r = safe(B, R, "rimworld/start_debug_game_ready", readiness="playable", pauseIfNeeded=True, timeoutMs=240000)
            R.log("start", j(r, 300))
            time.sleep(5)
        C.pause(B, R)
        cols = C.colonists(B)
        R.result("census_keys", sorted(cols[0].keys()) if cols else None, source="pawn_census")
        cx = sum(p["x"] for p in cols) // max(1, len(cols))
        cz = sum(p["z"] for p in cols) // max(1, len(cols))
        x0, z0 = cx + 12, cz - 6
        R.log("colonists", [(p.get("id"), p.get("x"), p.get("z"), p.get("drafted")) for p in cols], "work at", (x0, z0))
        # ground
        rect = "%d,%d,20,12" % (x0, z0)
        r = safe(B, R, "jawa/clear_area", rect=rect, dryRun=False)
        R.result("clear_area_keys", sorted(r.keys()), source="clear_area")
        r = safe(B, R, "jawa/set_roof_batch", ops="None:%s" % rect, refresh=True)
        R.result("roof_keys", j(r, 300), source="set_roof_batch")
        r = safe(B, R, "jawa/set_terrain_batch", ops="Soil:%s" % rect, layer="top", refresh=True, clearOverlays=True)
        R.result("terrain_reply", j(r, 400), source="set_terrain_batch")
        safe(B, R, "jawa/set_fog", action="unfog", rect=rect)
        # rows of things
        r = safe(B, R, "jawa/build_batch", ops="Wall:%d,%d;Door:%d,%d,1" % (x0 + 1, z0 + 1, x0 + 2, z0 + 1), stuff="WoodLog",
                 faction="player")
        R.result("build_batch_reply", j(r, 600), source="build_batch")
        r = safe(B, R, "jawa/spawn_batch", ops="Apparel_PackJump:%d,%d" % (x0 + 4, z0 + 1))
        R.result("spawn_batch_reply", j(r, 400), source="spawn_batch")
        r = B.call("jawa/list_things", rect="%d,%d,6,2" % (x0, z0 + 1), limit=20) or {}
        th = r.get("things") or r.get("rows") or []
        R.result("list_things_rows", [dict((k, t.get(k)) for k in sorted(t.keys())) for t in th][:4], source="list_things")
        # pawn
        pid = C.subject(B, R, (x0 + 6, z0 + 6), "probe subject")
        if pid:
            pg = B.call("jawa/pawn_get", pawn=pid) or {}
            R.result("pawn_get_keys", sorted(pg.keys())[:40], source="pawn_get")
            p0 = pg.get("pawn") or ((pg.get("pawns") or [None])[0]) or pg
            R.result("pawn_get_look", {k: p0.get(k) for k in ("gender", "bodyType", "headType", "hair", "beard", "ageBiologicalYears",
                                                              "age", "apparel", "drafted") if isinstance(p0, dict) and k in p0},
                     source="pawn_get")
            t0 = C.tick(B)
            ok, at = C.walk_to(B, R, pid, (x0 + 9, z0 + 6))
            R.result("walk_to", {"arrived": ok, "at": at, "ticks": (C.tick(B) or 0) - (t0 or 0)}, ok=ok, source="order_pawn")
            C.settle(B, 500)
            R.result("pause_after_settle", C.pause(B, R), ok=None, source="get_game_info")
        # shots: outputDirectory into the run folder; frame size at the two roots
        for root in (C.ROOT_PLAY, C.ROOT_WIDE):
            C.shot(B, R, "probe_rect20x12", (x0, z0, 20, 12), root)
        C.shot(B, R, "probe_rect60x30", (x0 - 20, z0 - 10, 60, 30), C.ROOT_WIDE)
        cam = B.call("rimworld/get_camera_state") or {}
        R.result("camera", j(cam, 600), source="get_camera_state")
        C.finish_shots(R)
        for s in R.shots:
            R.result("png_" + s["name"] + "_r%g" % s["root"], png_size(os.path.join(R.shotdir, s["file"])),
                     source="png header", rect=s["rect"], path=s["path"])
        # quiet
        C.quiet(B, R)
        R.result("hour", C.local_hour(B), source="time_date_at")
    except Exception as e:  # noqa: BLE001
        import traceback
        R.harness_error("UNCAUGHT %s: %s | %s" % (type(e).__name__, e, traceback.format_exc()[-900:]))
    finally:
        try:
            C.pause(B)
        except Exception:  # noqa: BLE001
            pass
        R.close()


if __name__ == "__main__":
    main()
