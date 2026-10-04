"""validation_aerial.py -- Messy Conduit L5 (aerial power lines) functional script, beside validation.py.

Design: design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 2 (walk rows M13-M16, M19).
Offline half: the Verse-free AerialMath.cs is checked by the C# SelfTest (AerialSelfTest.cs, run by
validation.py's O3 row). State is read through RimMandrake.MessyConduit.Aerial.AerialProbe (written/read with
jawa/mod_settings_field, answered by RM_MapComponent_Aerial on its next frame), never from screenshots.

    python.exe validation_aerial.py --live                      # on the current map (after validation.py --live)
    python.exe validation_aerial.py --save-load NAME            # M16: links + span states survive save/load
    python.exe validation_aerial.py --removal-check NAME        # M9b: a save WITH anchors on a tier WITHOUT the mod
    python.exe validation_aerial.py --merge OUT base.json [more.json ...]   # one 'live' result for modcheck record

Batch order (one session): validation.py --live --fresh-map, validation.py --save-load A (a cords-only save, so M9
stays the clean check), THEN this --live and --save-load B, then the tier swap and both removal checks.

LEARNED (each line is a check below):
  * The despawn gap (design 2.2) is REAL, not only reasoned: row M14_gap_control removes the middle mast with the
    re-seed switched off (test-only AerialProbe "skipreseed:true") and the far mast must read NO net; with the fix
    on (M14a) it must read a net. If the control ever reads a net, the theory went false and the fix is dead code.
  * A clamp built as a TRANSMITTER would merge the grids by adjacency (every vanilla generator is a transmitter);
    the clamp is a plain CompPowerTrader connector, guarded onto our faction's nets (M19 net ids must differ).
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

APROBE = "RimMandrake.MessyConduit.Aerial.AerialProbe"
AX0, AZ0 = 90, 180
SITE = (AX0 - 2, AZ0 - 2, 46, 20)
BAT = (AX0 + 1, AZ0 + 5)                     # Battery 1x2 rot N: cells z..z+1; M1 is cardinally adjacent
M1, M2, M3 = (AX0 + 2, AZ0 + 5), (AX0 + 14, AZ0 + 5), (AX0 + 26, AZ0 + 5)      # 12-cell spans, range 20
LAMP = (AX0 + 27, AZ0 + 7)                   # hooks up to M3 (nearest transmitter)
ROOM = (AX0 + 6, AZ0 + 2, AX0 + 10, AZ0 + 8)  # walled + roofed room under the M1-M2 span
HMAST = (AX0 + 20, AZ0 + 15)                 # a HOSTILE mast: never a link target
HBAT = (AX0 + 30, AZ0 + 12)                  # victim grid: hostile battery + 2 conduit
HCOND = [(AX0 + 31, AZ0 + 12), (AX0 + 32, AZ0 + 12)]
CLAMP = (AX0 + 33, AZ0 + 12)
OCOND = [(AX0 + 35, AZ0 + 12), (AX0 + 36, AZ0 + 12)]                          # our cable, not adjacent to theirs
OLAMP = (AX0 + 38, AZ0 + 13)                 # our only consumer on the tapped side; no source of our own
BLAST = (AX0 + 20, AZ0 + 4)                  # under the M2-M3 span, 6 cells from both masts
SHOTS = os.path.join(V.REPO, "Transient", "messy_conduit_live_20261002")


class A(V.Bridge):
    def ap(self, cmd, wait_s=20.0):
        before = self.call("jawa/mod_settings_field", typeName=APROBE, action="get", field="serial").get("value")
        s = self.call("jawa/mod_settings_field", typeName=APROBE, action="set", field="request", value=cmd)
        if not s.get("success"):
            return {"success": False, "error": "aerial probe set failed", "raw": s}
        t0 = time.time()
        while time.time() - t0 < wait_s:
            now = self.call("jawa/mod_settings_field", typeName=APROBE, action="get", field="serial").get("value")
            if now != before:
                res = self.call("jawa/mod_settings_field", typeName=APROBE, action="get", field="result").get("value")
                try:
                    return json.loads(res)
                except Exception:  # noqa: BLE001
                    return {"success": False, "raw": res}
            time.sleep(0.3)
        return {"success": False, "error": "aerial probe timed out (no frame serviced it)"}

    def shot(self, name, rect):
        self.call("jawa/clear_ui", all=True)
        self.call("rimworld/frame_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=1)
        time.sleep(2.0)
        r = self.call("jawa/take_screenshot", fileName=name)
        src = r.get("filePath")
        for _ in range(10):
            if src and os.path.exists(src):
                break
            time.sleep(0.5)
        try:
            os.makedirs(SHOTS, exist_ok=True)
            dst = os.path.join(SHOTS, name + ".png")
            shutil.copyfile(src, dst)
            return dst
        except Exception as ex:  # noqa: BLE001
            return "copy failed: %s (%s)" % (ex, src)


def anchors_by_pos(c):
    return {(a["x"], a["z"]): a for a in c.get("anchors") or []}


def net_at(B, cell):
    return B.ap("net:%d,%d" % cell)


def build_mast(B, cell, faction="player", d="RM_AerialMast"):
    return B.call("jawa/build_batch", ops="%s:%d,%d" % (d, cell[0], cell[1]), faction=faction, wipeExisting=False)


def run_live(args):
    B = A()
    rows, log = [], []
    res = {"mod": V.MOD, "mode": "live", "script": "validation_aerial.py", "tier": V.TIER,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "screenshots": []}
    env = {}
    rm = B.call("jawa/running_mods", assembly="RimMandrakeMessyConduit", details=False)
    if rm.get("success"):
        import hashlib
        env["running"] = [p.lower() for p in rm.get("packageIds") or []]
        env["running_sha256"] = hashlib.sha256("\n".join(env["running"]).encode("utf-8")).hexdigest()
    res["env"] = env
    try:
        sys.path.insert(0, os.path.join(V.UTILS, "modcheck"))
        import status as _mc  # noqa: E402
        res["mod_hash"] = _mc.mod_hash(HERE)
    except Exception as ex:  # noqa: BLE001
        res["mod_hash"] = None
        log.append("mod_hash unavailable: %s" % ex)
    lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    log_base = max([x.get("Sequence", 0) for x in lg0.get("logs") or []] or [0])
    d = B.ap("defaults")
    if not d.get("success"):
        V.row(rows, "A_probe_channel", "FAIL", "HARNESS", d)
        res["aborted"] = "aerial probe dead"
        return res
    B.ap("skipreseed:false")

    # ---------------------------------------------------------------- scene
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % SITE)
    walls = V.perimeter(*ROOM)
    b_w = B.call("jawa/build_batch", ops=V.ops("Wall", walls), stuff="Steel", faction="player")
    rx0, rz0, rx1, rz1 = ROOM
    roof = B.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,%d,%d" % (rx0 + 1, rz0 + 1, rx1 - rx0 - 1, rz1 - rz0 - 1))
    b_b = B.call("jawa/build_batch", ops="Battery:%d,%d,0" % BAT, faction="player")
    b_m = B.call("jawa/build_batch", ops=V.ops("RM_AerialMast", [M1, M2, M3]), faction="player", wipeExisting=False)
    b_l = B.call("jawa/build_batch", ops="StandingLamp:%d,%d" % LAMP, faction="player")
    b_h = build_mast(B, HMAST, faction="hostile")
    B.call("jawa/map_commit")
    lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % BAT, limit=3)
    bat_id = next((t.get("id") or t.get("thingId") for t in lt.get("things") or []), None)
    bs = B.call("jawa/battery_set", thing=bat_id, mode="setPct", value=1.0) if bat_id else {}
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    B.ticks(3)                                      # tick 1: auto-link queue; tick 2: nets rebuilt
    time.sleep(1.0)
    c0 = B.ap("census")
    ap0 = anchors_by_pos(c0)
    ok = all(p in ap0 for p in (M1, M2, M3, HMAST)) and (bs.get("storedEnergyAfter") or 0) > 0
    V.row(rows, "A0_scene_built", "PASS" if ok else "FAIL", "SITE",
          {"walls": b_w.get("survived"), "roof": roof.get("success"), "battery": bat_id, "stored": bs.get("storedEnergyAfter"),
           "masts": b_m.get("survived"), "lamp": b_l.get("survived"), "hostileMast": b_h.get("survived"), "anchors": sorted(ap0)})
    if not ok:
        res["aborted"] = "scene not built"
        res["log"] = [c0]
        return res
    i1, i2, i3, ih = (ap0[p]["id"] for p in (M1, M2, M3, HMAST))

    def nets(c):
        a = anchors_by_pos(c)
        return {k: (a[p]["net"] if p in a else None) for k, p in (("m1", M1), ("m2", M2), ("m3", M3))}

    # ---------------------------------------------------------------- M13: one net across the gap
    n0 = nets(c0)
    lamp0 = net_at(B, LAMP)
    lamp_on = any(t.get("powerOn") for t in lamp0.get("things") or [])
    m13 = n0["m1"] != -1 and n0["m1"] == n0["m2"] == n0["m3"] and ap0[M1]["netLive"] and c0.get("spansUp") == 2 \
        and c0.get("autoLinks", 0) >= 2 and c0.get("postfixAppends", 0) > 0
    V.row(rows, "M13a_linked_one_net_across_gap", "PASS" if m13 else "FAIL", "MOD",
          {"nets": n0, "gapCells": M2[0] - M1[0], "spansUp": c0.get("spansUp"), "autoLinks": c0.get("autoLinks"),
           "postfixAppends": c0.get("postfixAppends"), "m1Live": ap0[M1]["netLive"]})
    B.ticks(210)                                    # a consumer is switched on at most every 200 ticks (PowerNetTick)
    lamp1 = net_at(B, LAMP)
    lamp_on = any(t.get("powerOn") for t in lamp1.get("things") or [])
    V.row(rows, "M13b_far_consumer_powered", "PASS" if lamp_on else "FAIL", "MOD",
          {"lamp": lamp1.get("things"), "net": lamp1.get("net"), "live": lamp1.get("live"),
           "note": "the lamp hooks to M3, 24 cells from the battery, across a walled ROOFED room (spans may pass over roofs)"})
    # unlink -> two nets; relink -> one
    B.ap("unlink:%d,%d" % (i2, i3))
    B.ticks(30)
    c1 = B.ap("census")
    n1 = nets(c1)
    lamp2 = net_at(B, LAMP)
    off = not any(t.get("powerOn") for t in lamp2.get("things") or [])
    B.ap("link:%d,%d" % (i2, i3))
    B.ticks(3)
    n1b = nets(B.ap("census"))
    V.row(rows, "M13c_unlink_two_nets_relink_one", "PASS" if (n1["m3"] not in (-1, n1["m1"]) and n1["m1"] == n1["m2"] and off and
                                                           n1b["m1"] == n1b["m3"] != -1) else "FAIL", "MOD",
          {"afterUnlink": n1, "lampOffAfterUnlink": off, "afterRelink": n1b})
    v_far = B.ap("link:%d,%d" % (i1, i3))
    v_hm = B.ap("link:%d,%d" % (i3, ih))
    bat_num = int("".join(ch for ch in str(bat_id) if ch.isdigit()) or 0)      # list_things ids read "Battery19643"
    v_bat = B.ap("link:%d,%d" % (i1, bat_num)) if bat_num else {}
    V.row(rows, "M13d_refusals", "PASS" if (v_far.get("verdict") == "OutOfRange" and v_hm.get("verdict") == "Foreign"
                                          and v_bat.get("verdict") == "NotAnchor") else "FAIL", "MOD",
          {"m1->m3 (24 cells)": v_far.get("verdict"), "m3->hostile mast": v_hm.get("verdict"), "m1->battery": v_bat.get("verdict")})
    hm_links = anchors_by_pos(B.ap("census")).get(HMAST, {}).get("links")
    V.row(rows, "M13e_hostile_mast_not_autolinked", "PASS" if hm_links == [] else "FAIL", "MOD", {"hostileMastLinks": hm_links})

    # ---------------------------------------------------------------- drawing: altitude + spans drawn
    time.sleep(0.6)
    c2 = B.ap("census")
    al = c2.get("altitudes") or {}
    alt_ok = al and al["pawn"] < al["pawnState"] < al["top"] < al["span"] < al["blueprint"] < al["weather"]
    V.row(rows, "R1_span_altitude_above_pawns_below_blueprints", "PASS" if alt_ok else "FAIL", "MOD", al)
    V.row(rows, "R2_spans_and_heads_drawn", "PASS" if c2.get("spanDraws", 0) >= 2 and c2.get("topDraws", 0) >= 3 and c2.get("spanMeshes", 0) >= 2 else "FAIL",
          "MOD", {k: c2.get(k) for k in ("spanDraws", "topDraws", "spanMeshes", "groundVerts")})
    res["screenshots"].append(B.shot("aerial_01_lines_up", (AX0 - 1, AZ0 + 1, 30, 10)))

    # ---------------------------------------------------------------- M14: the despawn gap
    B.ap("skipreseed:true")
    B.ap("dismantle:%d" % i2)
    B.ticks(2)
    cg = B.ap("census")
    ng = nets(cg)
    B.ap("skipreseed:false")
    agc = anchors_by_pos(cg)
    raw = {k: agc[p].get("compNet") for k, p in (("m1", M1), ("m3", M3)) if p in agc}
    V.row(rows, "M14_gap_control_without_fix", "PASS" if ng["m3"] == -1 and ng["m1"] == -1 else "FAIL", "HARNESS",
          {"registeredNets": ng, "compNets(stale pointer)": raw,
           "meaning": "PASS = the despawn gap is real: with the re-seed OFF both sides are left on NO registered net (their "
                      "CompPower.transNet still points at the same deleted net: a same-net read alone looks healthy)"})
    B.ap("reseed:%d" % i3)
    B.ap("reseed:%d" % i1)                         # the gap strands BOTH sides: the shared net was destroyed whole
    B.ticks(2)

    def rebuild_m2():
        B.call("jawa/destroy_batch", rects="%d,%d,1,1" % M2, categories="All")   # a killed mast leaves debris on its cell
        build_mast(B, M2)
        B.ticks(3)
        cc = B.ap("census")
        m2 = anchors_by_pos(cc).get(M2)
        if not m2:
            return None
        linked = {l["other"] for l in m2["links"]}
        for o in (i1, i3):
            if o not in linked:
                B.ap("link:%d,%d" % (m2["id"], o))
        B.ticks(3)
        return m2["id"]

    i2 = rebuild_m2()
    nr0 = B.ap("census").get("netRepairs")
    B.ap("dismantle:%d" % i2)
    B.ticks(2)
    cd = B.ap("census")
    nd = nets(cd)
    B.ticks(260)                                    # one watchdog sweep
    cd2 = B.ap("census")
    m14a = nd["m1"] != -1 and nd["m3"] != -1 and nd["m1"] != nd["m3"] and cd.get("fallenCords") == 0 and \
        cd2.get("netRepairs") == nr0 and cd2.get("watchdogRuns", 0) > 0
    V.row(rows, "M14a_remove_middle_both_ends_resolve", "PASS" if m14a else "FAIL", "MOD",
          {"nets": nd, "fallenCords(dismantle coils)": cd.get("fallenCords"), "netRepairs": [nr0, cd2.get("netRepairs")],
           "watchdogRuns": cd2.get("watchdogRuns")})

    # kill (not dismantle) -> each survivor holds a fallen live/dead cord
    i2 = rebuild_m2()
    B.ap("kill:%d" % i2)
    B.ticks(2)
    B.ap("poll")
    ck = B.ap("census")
    ak = anchors_by_pos(ck)
    f1, f3 = ak[M1]["fallen"], ak[M3]["fallen"]
    nk = nets(ck)
    # M1's cable falls toward M2 across the walled room: it must stop at the room's west wall ("the rest is over the
    # wall"); M3's lies on open ground and must reach out its full length (12 cells x 1.05).
    m14b = len(f1) == 1 and len(f3) == 1 and ak[M1]["fallenLive"] is True and ak[M3]["fallenLive"] is False and \
        nk["m1"] != -1 and nk["m3"] != -1 and f1[0]["toward"] == list(M2) and f1[0]["blocked"] and f1[0]["tip"][0] < ROOM[0] and \
        not f3[0]["blocked"] and f3[0]["laidLen"] > 0.85 * 12.6
    V.row(rows, "M14b_dead_pole_drops_live_and_dead_cords", "PASS" if m14b else "FAIL", "MOD",
          {"m1Fallen": f1, "m1Live": ak[M1]["fallenLive"], "m3Fallen": f3, "m3Live": ak[M3]["fallenLive"], "nets": nk})
    time.sleep(0.5)
    V.row(rows, "M14c_live_tip_glows", "PASS" if B.ap("census").get("glowDraws", 0) >= 1 else "FAIL", "MOD",
          "look only (owner 2026-10-02): no shock; glow per frame at the live tip")
    res["screenshots"].append(B.shot("aerial_02_dead_pole_fallen_cords", (AX0 - 1, AZ0 + 1, 30, 10)))

    # ---------------------------------------------------------------- M15: explosion cuts a span
    i2 = rebuild_m2()
    ce = B.ap("explode:%d,%d,2.5,50" % BLAST)
    B.ticks(30)
    B.ap("poll")
    cx = B.ap("census")
    ax = anchors_by_pos(cx)
    nx = nets(cx)
    halves = [f for p in (M2, M3) for f in ax.get(p, {}).get("fallen", []) if f.get("cutPartner", -1) != -1]
    m15 = ce.get("cuts") == 1 and cx.get("spansCut") == 1 and len(halves) == 2 and nx["m1"] == nx["m2"] != -1 and nx["m3"] not in (-1, nx["m1"])
    V.row(rows, "M15_explosion_cuts_span", "PASS" if m15 else "FAIL", "MOD",
          {"cuts": ce.get("cuts"), "spansCut": cx.get("spansCut"), "halves": halves, "nets": nx,
           "m2Live": ax.get(M2, {}).get("fallenLive"), "m3Live": ax.get(M3, {}).get("fallenLive")})
    res["screenshots"].append(B.shot("aerial_03_explosion_cut_halves", (AX0 + 10, AZ0, 20, 10)))
    rs = B.ap("restring:%d,%d" % (i2, i3)) if i2 else {}
    B.ticks(3)
    nrs = nets(B.ap("census"))
    V.row(rows, "M15b_restring_rejoins", "PASS" if rs.get("done") and nrs["m1"] == nrs["m3"] != -1 else "FAIL", "MOD", {"nets": nrs})

    # ---------------------------------------------------------------- sway (motion is NOT a bar; state proxy only)
    B.ap("set:sway=CPU")
    time.sleep(0.6)
    s_on = B.ap("census")
    B.ap("set:sway=Off")
    time.sleep(0.6)
    s_off = B.ap("census")
    B.ap("set:sway=Auto")
    on_ok = s_on.get("swayDraws", 0) > 0 if s_on.get("swayReason") == "cpu" else s_on.get("swayReason") in ("no wind", "game plant-sway preference off")
    V.row(rows, "R3_sway_proxy", "PASS" if on_ok and s_off.get("swayDraws") == 0 and s_off.get("swayReason") == "setting off" else "FAIL", "MOD",
          {"on": {k: s_on.get(k) for k in ("swayReason", "swayDraws", "wind", "plantSwayPref")},
           "off": {k: s_off.get(k) for k in ("swayReason", "swayDraws")}})

    # ---------------------------------------------------------------- M19: the one-way power tap
    tb = [B.call("jawa/build_batch", ops="Battery:%d,%d,0" % HBAT, faction="hostile"),
          B.call("jawa/build_batch", ops=V.ops("PowerConduit", HCOND), faction="hostile", wipeExisting=False),
          B.call("jawa/build_batch", ops=V.ops("PowerConduit", OCOND), faction="player", wipeExisting=False),
          B.call("jawa/build_batch", ops="StandingLamp:%d,%d" % OLAMP, faction="player"),
          B.call("jawa/build_batch", ops="RM_PowerTapClamp:%d,%d" % CLAMP, faction="player")]
    lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % HBAT, limit=3)
    hb_id = next((t.get("id") or t.get("thingId") for t in lt.get("things") or []), None)
    hs = B.call("jawa/battery_set", thing=hb_id, mode="setPct", value=1.0) if hb_id else {}
    B.ticks(5)
    ct = B.ap("census")
    tap = (ct.get("taps") or [{}])[0]
    v0 = net_at(B, HBAT)
    B.ticks(210)
    ol = net_at(B, OLAMP)
    lamp_on = any(t.get("powerOn") for t in ol.get("things") or [])
    v1 = net_at(B, HBAT)
    B.ticks(600)
    v2 = net_at(B, HBAT)
    ct2 = B.ap("census")
    tap2 = (ct2.get("taps") or [{}])[0]
    drop = (v1.get("storedWd") or 0) - (v2.get("storedWd") or 0)
    m19 = tap.get("connected") and tap.get("ourNet", -1) != -1 and tap.get("victimNet", -1) != -1 and tap["ourNet"] != tap["victimNet"] \
        and tap2.get("ourNet") != tap2.get("victimNet") and (tap2.get("outputW") or 0) > 400 and lamp_on and drop > 3.0
    V.row(rows, "M19_tap_drains_one_way", "PASS" if m19 else "FAIL", "MOD",
          {"built": [b.get("survived") for b in tb], "victimStoredSet": hs.get("storedEnergyAfter"), "tap": tap2,
           "ourLamp": ol.get("things"), "victimStored": [v0.get("storedWd"), v1.get("storedWd"), v2.get("storedWd")],
           "victimDrop600": round(drop, 3), "expectedDrop600~": round(500 * 600 * 1.6666667e-05, 3),
           "victimNet": v2.get("net"), "ourNet": tap2.get("ourNet"), "guardRefused": ct2.get("tapGuardRefused"),
           "tapEvents": ct2.get("tapEventsRaised")})
    res["screenshots"].append(B.shot("aerial_04_power_tap_clamp", (AX0 + 28, AZ0 + 9, 12, 7)))
    # control: taps off -> victim stops draining, our lamp goes dark
    B.ap("set:tapsEnabled=False")
    B.ticks(40)
    w0 = net_at(B, HBAT)
    B.ticks(600)
    w1 = net_at(B, HBAT)
    ol2 = net_at(B, OLAMP)
    dark = not any(t.get("powerOn") for t in ol2.get("things") or [])
    drop_off = (w0.get("storedWd") or 0) - (w1.get("storedWd") or 0)
    B.ap("set:tapsEnabled=True")
    V.row(rows, "M19n_taps_off_control", "PASS" if dark and drop_off < 0.5 else "FAIL", "MOD",
          {"ourLampDark": dark, "victimDrop600": round(drop_off, 3), "note": "battery self-discharge only (5 W ~ 0.05 Wd/600 ticks)"})

    # ---------------------------------------------------------------- log budget
    lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > log_base]
    errs = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
    V.row(rows, "AZ_log_budget", "PASS" if not errs else "FAIL", "MOD",
          {"errors": [str(e.get("Message", ""))[:240] for e in errs[:8]], "newWarnings": len(new)})
    B.ap("defaults")
    res["log"] = log
    res["sceneIds"] = {"m1": i1, "m3": i3, "hostileMast": ih, "battery": bat_id, "hostileBattery": hb_id}
    return res


# ============================================================================ M16 / M9b
def _aerial_set(c):
    pos = {a["id"]: (a["x"], a["z"]) for a in c.get("anchors") or []}
    links = sorted({tuple(sorted([pos[a["id"]], pos.get(l["other"], (-1, -1))])) + (l["state"],)
                    for a in c.get("anchors") or [] for l in a["links"]})
    fallen = sorted((pos[a["id"]], tuple(f["toward"]), f["cutPartner"] != -1) for a in c.get("anchors") or [] for f in a["fallen"])
    netgroups = {}
    for a in c.get("anchors") or []:
        netgroups.setdefault(a["net"], []).append((a["x"], a["z"]))
    return {"anchors": sorted(pos.values()), "links": links, "fallen": fallen,
            "netGroups": sorted(sorted(v) for v in netgroups.values()), "taps": len(c.get("taps") or [])}


def run_save_load(args):
    B = A()
    rows = []
    res = {"mod": V.MOD, "mode": "save-load", "script": "validation_aerial.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    name = args.save_load
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    B.ticks(2)
    ca = B.ap("census")
    # the save must carry a CUT span and its two fallen halves too, not only UP links
    ap_ = anchors_by_pos(ca)
    if M2 in ap_ and M3 in ap_ and not any(l["state"] == "Cut" for a in ca.get("anchors") or [] for l in a["links"]):
        B.ap("cut:%d,%d" % (ap_[M2]["id"], ap_[M3]["id"]))
        B.ticks(3)
        B.ap("poll")
        ca = B.ap("census")
    if not ca.get("anchors"):
        V.row(rows, "M16_save_load_links", "FAIL", "SITE", "no anchors on the current map")
        return res
    before = V._saves_stat()
    if name + ".rws" in before:
        V.row(rows, "M16_save_load_links", "FAIL", "HARNESS", "%s.rws exists" % name)
        return res
    B.call("rimworld/save_game", saveName=name)
    time.sleep(3.0)
    after = V._saves_stat()
    new = sorted(set(after) - set(before))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    ok_save = new == [name + ".rws"] and not changed
    V.row(rows, "M16a_save_landed_new_file_only", "PASS" if ok_save else "FAIL", "HARNESS", {"new": new, "changed": changed})
    if not ok_save:
        res["aborted"] = "save did not land as a new file only"
        return res
    with open(os.path.join(V.SAVES, name + ".rws"), "rb") as f:
        blob = f.read()
    comp_hits = blob.count(b"RM_MapComponent_Aerial")
    V.row(rows, "M16b_component_not_in_save", "PASS" if comp_hits == 0 else "FAIL", "MOD", {"RM_MapComponent_Aerial mentions": comp_hits})
    B.call("rimworld/load_game", saveName=name)
    ok, waited = V._wait_playing(B)
    if not ok:
        V.row(rows, "M16_save_load_links", "FAIL", "SITE", {"state": waited})
        return res
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    B.ticks(2)
    time.sleep(1.0)
    cb = B.ap("census")
    # LEARNED live 2026-10-04: the census read right after load can be EMPTY (anchors register a little later); the
    # first failure of this row was that race, not lost state -- poll up to 12 s and report how long it took.
    t_poll = time.time()
    while not cb.get("anchors") and time.time() - t_poll < 12.0:
        B.ticks(10)
        time.sleep(1.0)
        cb = B.ap("census")
    registered_after_s = round(time.time() - t_poll, 1)
    sa, sb = _aerial_set(ca), _aerial_set(cb)
    diff = sorted(k for k in sa if sa[k] != sb[k])
    V.row(rows, "M16_save_load_links", "PASS" if not diff and sa["links"] and sa["fallen"] else "FAIL", "MOD",
          {"differs": diff, "links": len(sa["links"]), "fallen": len(sa["fallen"]), "netGroups": sb["netGroups"], "loadSeconds": waited,
           "netRepairsAfterLoad": cb.get("netRepairs"), "registeredAfterS": registered_after_s})
    res["before"], res["after"] = sa, sb
    res["screenshots"] = [B.shot("aerial_05_after_save_load", (AX0 - 1, AZ0 + 1, 42, 16))]
    return res


def run_removal_check(args):
    """M9b: a save holding anchors, loaded on a tier WITHOUT the mod. Expected (design 2.4): vanilla's missing-def
    errors name ONLY our defs and the game loads; nothing may name one of our C# classes."""
    B = A()
    rows = []
    res = {"mod": V.MOD, "mode": "removal-check", "script": "validation_aerial.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    rm = B.call("jawa/running_mods", details=False)
    running = [p.lower() for p in rm.get("packageIds") or []]
    if not running or V.PKG in running:
        V.row(rows, "M9b_remove_mod_with_anchors", "UNMEASURED", "SITE", "mod list unreadable or the mod still running")
        return res
    lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    base = max([x.get("Sequence", 0) for x in lg0.get("logs") or []] or [0])
    B.call("rimworld/load_game", saveName=args.removal_check, ignoreModCompatibility=True)
    ok, waited = V._wait_playing(B)
    if not ok:
        V.row(rows, "M9b_remove_mod_with_anchors", "FAIL", "MOD", {"state": waited})
        return res
    B.ticks(60)
    time.sleep(1.0)
    lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > base]
    errs = [str(e.get("Message", "")) + " " + str(e.get("StackTrace", "")) for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
    our_defs = ("RM_AerialMast", "RM_AerialLampMast", "RM_AerialWallBracket", "RM_PowerTapClamp", "RM_AerialLines")
    class_hits = [e[:240] for e in errs if "RimMandrake.MessyConduit" in e]
    def_hits = [e[:200] for e in errs if any(d in e for d in our_defs)]
    other = [e[:160] for e in errs if e not in class_hits and not any(d in e for d in our_defs)]
    V.row(rows, "M9b_remove_mod_with_anchors", "PASS" if not class_hits else "FAIL", "MOD",
          {"loadSeconds": waited, "errorsNamingOurClasses": class_hits[:6], "errorsNamingOurDefs(expected)": len(def_hits),
           "firstDefErrors": def_hits[:3], "otherErrors": other[:6]})
    return res


def merge(out, paths):
    """One 'live' result for `modcheck record`: rows of every input, each tagged with its source file. The FIRST
    input must be a live run (it provides mod_hash and env); an UNCOVERED row is dropped when another input
    measured that same id."""
    parts = [json.load(open(p, encoding="utf-8")) for p in paths]
    base = dict(parts[0])
    assert base.get("mode") == "live", "first input must be a live run"
    measured = {r["id"] for p in parts for r in p.get("rows") or [] if r.get("status") not in ("UNCOVERED",)}
    rows = []
    for p, path in zip(parts, paths):
        if p.get("mod_hash") and base.get("mod_hash") and p["mod_hash"] != base["mod_hash"]:
            raise SystemExit("REFUSED: %s ran at another mod hash" % path)
        for r in p.get("rows") or []:
            if r.get("status") == "UNCOVERED" and r["id"] in measured:
                continue
            rows.append(dict(r, source=os.path.basename(path)))
    base.update(rows=rows, merged_from=[os.path.basename(p) for p in paths], script="validation.py+validation_aerial.py")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(base, f, indent=1, default=str)
    t = {}
    for r in rows:
        t[r["status"]] = t.get(r["status"], 0) + 1
    print("merged %d rows %s -> %s" % (len(rows), t, out))
    return 0


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--save-load", default=None, metavar="NAME")
    ap.add_argument("--removal-check", default=None, metavar="NAME")
    ap.add_argument("--merge", nargs="+", default=None, metavar="OUT IN")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.merge:
        return merge(a.merge[0], a.merge[1:])
    if a.save_load:
        res = run_save_load(a)
    elif a.removal_check:
        res = run_removal_check(a)
    elif a.live:
        res = run_live(a)
    else:
        ap.print_help()
        return 2
    os.makedirs(os.path.join(HERE, "northstar"), exist_ok=True)
    out = a.out or os.path.join(HERE, "northstar", "validation_aerial_%s_%s.json" % (res["mode"], time.strftime("%Y%m%dT%H%M%S")))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    t = {}
    for r in res["rows"]:
        t[r["status"]] = t.get(r["status"], 0) + 1
    print("aerial %s: %s -> %s" % (res["mode"], t, out))
    return 0 if not res.get("aborted") and not t.get("FAIL") and not t.get("UNMEASURED") else 1


if __name__ == "__main__":
    sys.exit(main())
