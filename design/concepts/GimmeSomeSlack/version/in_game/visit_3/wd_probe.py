"""wd_probe.py: sc_save_reload_wire_down's plot staged on the map that is up, read at several waits (no save, no load). python.exe."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA, save_wire_down as WD
B = VA.A()
print("time", B.call("rimworld/get_game_info").get("ticksGame"))
WD.stage(B, V)
def show(tag):
    r = WD.read(B)
    print(tag, "whole", WD.whole(r), "midway", WD.midway(r), "lamps", {str(k): v for k, v in r["lamps"].items()}, "ends", r["ends"], "edges", r["edges"], r["cords"])
    print("  floor lamp net", json.dumps(B.ap("net:%d,%d" % WD.FLOOR_LAMP))[:900])
show("t0")
B.ticks(250); show("t250")
print("down", WD.wire_down(B)); show("cut")
B.ticks(250); show("cut+250")
print(json.dumps(B.probe("rect:%d,%d,%d,%d" % WD.RECT))[:3000])
