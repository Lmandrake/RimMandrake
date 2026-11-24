"""close_020_stations.py -- the five stations of the 0.2.0 close-out, staged on the walk map that is up, read and captured
(RIMMANDRAKE_CLOSE_SLACK_VERSION_ALL_REAL_WORK_ONE_RUN_ONE_CONTEXT). python.exe, the bridge of the game held, tier gimmesomeslack_walk.

    python.exe src\\RimMandrake\\GimmeSomeSlack\\review\\close_020_stations.py <out dir> [--no-stage] [--save NAME]

Stations, west to east on the free ground south of stations 32 and 33 (z 22 to 36):
  34 battery in the four looks: an unstyled battery on a run of each look, then "Restyle, all connected" on the run
  35 three poles built together: they wire as a line (2 spans), not a triangle
  36 a lamp wired to a pole, a cord run ending beside it: the cord plugs into the lamp, no loose live end
  37 Futuristic switch: closed with power (cyan glow), closed with no power (glow out)
  38 a cut span: the fallen wires have no flat corner
Prints one row per read: PASS / FAIL / COULD NOT LOOK. Exit 0 all PASS, 1 any FAIL, 2 could not stage or read."""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GSS = os.path.dirname(HERE)
sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(os.path.dirname(GSS), "Utils")]
import validation as V  # noqa: E402
import validation_aerial as VA  # noqa: E402
from modcheck import reviewmap as RM  # noqa: E402

SITE = (14, 20, 100, 18)
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
KEY = {"Modern": "Modern_Orange"}            # a Modern conduit's menu key carries its colour
BX = [18, 23, 28, 33]                       # station 34: one run per look
EAST = (40, 28)                             # and one battery lying east-west on an Industrial run
POLES = [(52, 30), (59, 30), (66, 30)]      # station 35
P36 = (74, 30)                              # station 36: the mast
LAMP36 = (77, 31)
SW_ON, SW_OFF = (86, 30), (91, 30)          # station 37
CUT = [(98, 30), (107, 30)]                 # station 38
RECTS = {"st34_battery_four_looks": (15, 22, 34, 14), "st35_three_poles_in_a_row": (49, 26, 21, 9), "st36_pole_lamp_cord_end": (71, 23, 10, 12),
         "st37_futuristic_switch_power_no_power": (83, 23, 12, 13), "st38_fallen_wire_no_corner": (95, 25, 16, 10)}
rows = []


def row(name, verdict, detail):
    rows.append((name, verdict, detail))
    print("%-16s %s  %s" % (verdict, name, json.dumps(detail, default=str)[:600]), flush=True)


def charge(B, rect):
    for t in B.call("jawa/list_things", defName="Battery", rect="%d,%d,%d,%d" % rect, limit=40).get("things") or []:
        B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)


def stage(B):
    r = "%d,%d,%d,%d" % SITE
    B.call("jawa/destroy_batch", rects=r, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:" + r, clearOverlays=True)
    B.call("jawa/set_fog", action="unfog", rect=r)
    B.call("jawa/set_roof_batch", ops="None:" + r)
    B.ap("cclearpicks")
    # 34: a run per look, an UNSTYLED battery at its north end, a lamp at its south end
    for x, look in zip(BX, LOOKS):
        B.ap("cline:PowerConduit:%s:%d,26:%d,30:god" % (KEY.get(look, look), x, x))
        B.call("jawa/build_batch", ops="Battery:%d,31,0;StandingLamp:%d,25" % (x, x), faction="player", wipeExisting=False)
    B.ap("cline:PowerConduit:Industrial:%d,%d:%d,%d:god" % (EAST[0] - 4, EAST[1], EAST[0] - 1, EAST[1]))
    B.call("jawa/build_batch", ops="Battery:%d,%d,1" % EAST, faction="player", wipeExisting=False)
    # 35: three masts in ONE batch
    B.call("jawa/build_batch", ops=";".join("RM_AerialMast:%d,%d" % p for p in POLES), faction="player", wipeExisting=False)
    # 36: battery, conduit to the mast; the lamp FIRST (vanilla wires it to the mast, the nearest transmitter), then the run that ends beside it
    x, z = P36
    B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x, z - 5), faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", [(x, z - 3), (x, z - 2), (x, z - 1)]) + ";RM_AerialMast:%d,%d" % P36, faction="player", wipeExisting=False)
    B.call("jawa/map_commit"); B.ticks(3)
    B.call("jawa/build_batch", ops="StandingLamp:%d,%d" % LAMP36, faction="player", wipeExisting=False)
    B.call("jawa/map_commit"); B.ticks(3)
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", [(x + 1, z - 1), (x + 2, z - 1), (x + 3, z - 1), (x + 3, z)]), faction="player", wipeExisting=False)
    # 37: two Futuristic switches, one fed by a battery, one with no power at all
    for (sx, sz), fed in ((SW_ON, True), (SW_OFF, False)):
        B.ap("cline:PowerConduit:Futuristic:%d,%d:%d,%d:god" % (sx, sz - 2, sx, sz - 1))
        B.ap("cplace:PowerSwitch:Futuristic:%d,%d:god" % (sx, sz))
        B.ap("cline:PowerConduit:Futuristic:%d,%d:%d,%d:god" % (sx, sz + 1, sx, sz + 2))
        if fed:
            B.call("jawa/build_batch", ops="Battery:%d,%d,0;StandingLamp:%d,%d" % (sx, sz - 4, sx, sz + 3), faction="player", wipeExisting=False)
    # 38: two masts, linked, then cut
    B.call("jawa/build_batch", ops=";".join("RM_AerialMast:%d,%d" % p for p in CUT), faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(5)
    B.ap("cprocess")
    charge(B, SITE)
    B.ticks(60)
    pos = {(a["x"], a["z"]): a for a in B.ap("census").get("anchors") or []}
    a, b = pos.get(CUT[0]), pos.get(CUT[1])
    if a and b:
        if not any(q.get("other") == b["id"] for q in a.get("links") or []):
            B.ap("link:%d,%d" % (a["id"], b["id"]))
        B.ticks(3)
        B.ap("cut:%d,%d" % (a["id"], b["id"]))
    # 34: "Restyle, all connected" on each run, as the gizmo does: the unstyled battery follows its run
    for x, look in zip(BX, LOOKS):
        B.ap("crestyle:%d,28:%s" % (x, KEY.get(look, look)))
    B.ap("crestyle:%d,%d:Industrial" % (EAST[0] - 2, EAST[1]))
    B.ap("cprocess")
    B.ticks(30)


def read(B):
    V.frame_fit(B, SITE)
    time.sleep(1.0)
    B.probe("rebuild"); B.probe("poll"); B.ap("poll")
    st = B.ap("cstyles:%d,%d,%d,%d" % SITE)
    lamps = {(l["x"], l["z"]): l for l in st.get("lamps") or []}
    # 34
    got = {}
    for x, look in zip(BX, LOOKS):
        b = next((l for (lx, lz), l in lamps.items() if lx == x and lz in (31, 32) and l.get("def") == "Battery"), None)
        got[look] = (b or {}).get("look")
    be = next((l for (lx, lz), l in lamps.items() if lz == EAST[1] and EAST[0] - 1 <= lx <= EAST[0] + 1 and l.get("def") == "Battery"), None)
    got["east"] = (be or {}).get("look")
    if not lamps:
        row("st34_battery_follows_run", "COULD NOT LOOK", {"cstyles": str(st)[:300]})
    else:
        row("st34_battery_follows_run", "PASS" if all(got[l] == l for l in LOOKS) and got["east"] == "Industrial" else "FAIL", got)
    labels = B.ap("creach:%d,28:open" % BX[0]).get("reaches") or []
    B.ap("cclosemenus")
    row("st34_menu_counts", "COULD NOT LOOK" if not labels else "PASS" if any("1 lamp, 1 battery" in t for t in labels) and not any("1 lamps" in t for t in labels) else "FAIL", labels)
    # 35
    cen = B.ap("census")
    pos = {(a["x"], a["z"]): a for a in cen.get("anchors") or []}
    if not all(p in pos for p in POLES):
        row("st35_three_in_a_row_two_spans", "COULD NOT LOOK", {"anchors": len(pos)})
    else:
        ids = {pos[p]["id"]: p for p in POLES}
        pairs = sorted({tuple(sorted((ids[a["id"]][0], ids[q["other"]][0]))) for a in (pos[p] for p in POLES) for q in a.get("links") or [] if q.get("other") in ids})
        row("st35_three_in_a_row_two_spans", "PASS" if pairs == [(52, 59), (59, 66)] else "FAIL", {"spans": pairs})
    # 36
    c = B.probe("rect:%d,%d,%d,%d" % (P36[0] - 2, P36[1] - 6, 9, 10))
    ok = isinstance(c, dict) and c.get("success") and "cordEdges" in c
    ends = [tuple(e["cell"]) + (e.get("registryLive"), e.get("netLive")) for e in c.get("ends") or []] if ok else None
    if ends is None:
        row("st36_no_loose_end_beside_pole_lamp", "COULD NOT LOOK", {"reply": str(c)[:300]})
    else:
        row("st36_no_loose_end_beside_pole_lamp", "PASS" if not ends and c.get("cordEdges") else "FAIL", {"ends": ends, "cordEdges": c.get("cordEdges")})
    # 37: the switch lamps are drawn only in view
    V.frame_fit(B, RECTS["st37_futuristic_switch_power_no_power"])
    time.sleep(1.0)
    sl = B.probe("switchlights")
    sw = {(q.get("x"), q.get("z")): q for q in sl.get("switches") or []}
    if "drawnGlowOut" not in sl:
        row("st37_glow_out_with_no_power", "COULD NOT LOOK", {"reply": str(sl)[:300]})
    else:
        row("st37_glow_out_with_no_power", "PASS" if sl.get("drawnGlowOut") == 1 and sl.get("drawnGreen", 0) >= 1 else "FAIL",
            {"drawnGlowOut": sl.get("drawnGlowOut"), "drawnGreen": sl.get("drawnGreen"), "drawnDark": sl.get("drawnDark"), "on": sw.get(SW_ON), "off": sw.get(SW_OFF)})
    # 38
    fallen = [a for a in cen.get("anchors") or [] if (a["x"], a["z"]) in CUT and a.get("fallen")]
    row("st38_span_cut_wires_down", "PASS" if len(fallen) == 2 else "FAIL" if all(p in pos for p in CUT) else "COULD NOT LOOK", {"anchorsWithFallen": len(fallen)})


def signs(B):
    ops = [RM.sign_book(16, 34, "34", "Battery in the four looks", look="Each battery wears its run's look: Scrapper, Industrial, Modern, Futuristic; one lies east-west. Fault: a vanilla battery, or a charge bar off the picture.",
                        do="Select a cord, Restyle, All connected, pick a look: the battery follows. The menu reads '1 lamp, 1 battery' and marks (current)."),
           RM.sign_book(50, 34, "35", "Three poles built together", look="Two spans, pole to pole. Fault: a third span from the first pole through the middle one. (The span going east from the third pole leads to station 36's pole.)"),
           RM.sign_book(72, 34, "36", "Lamp wired to a pole, cord end beside it", look="The cord plugs into the lamp. Fault: a loose sparking end beside the lamp."),
           RM.sign_book(84, 34, "37", "Futuristic switch with and without power", look="West: power, cyan glow, green lamp. East: no power, glow out, dark lamp. Fault: cyan on the east one."),
           RM.sign_book(96, 34, "38", "A cut span", look="The fallen wires drop and lie in curves. Fault: a wire that runs straight between two sharp corners.")]
    labels = [RM.label_line(16, 36, "34 BATTERY, FOUR LOOKS"), RM.label_line(50, 36, "35 THREE POLES, TWO SPANS"), RM.label_line(72, 36, "36 POLE LAMP TAKES THE CORD END"),
              RM.label_line(84, 36, "37 SWITCH GLOW OUT, NO POWER"), RM.label_line(96, 36, "38 FALLEN WIRE, NO CORNER")]
    print("labels", str(B.call("jawa/review_label", action="add", ops="\n".join(labels)))[:200])
    return labels


def main(a):
    out = a[0]
    os.makedirs(out, exist_ok=True)
    B = VA.A()
    if "--no-stage" not in a:
        stage(B)
    read(B)
    for name, rc in RECTS.items():
        log = []
        d = V.shot(B, name, rc, log, pad=0, root=max(4.0, max(rc[3], rc[2] * 9.0 / 16.0) / 2.0 + 1.0))
        if d and os.path.exists(str(d)):
            shutil.copy(str(d), os.path.join(out, name + ".png"))
            print("shot", name)
        else:
            row("capture " + name, "COULD NOT LOOK", log[-1:])
    if "--save" in a:
        labels = signs(B)
        B.call("jawa/clear_ui", all=True)
        print(json.dumps(RM.save_keeper(B, a[a.index("--save") + 1], saves=V.SAVES, signs=labels), default=str)[:400])
    bad = [r for r in rows if r[1] != "PASS"]
    return 0 if not bad else 2 if any(r[1] == "COULD NOT LOOK" for r in bad) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
