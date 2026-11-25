"""RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON: the pawn-in-liquid matrix, one live scene.

    python.exe pawn_in_liquid_matrix.py <repo_win_path> <out_win_dir> [stage|read|shots|off|all|save:<name>]
    python3    pawn_in_liquid_matrix.py <repo> <out_dir> sheets          (WSL, PIL: the grid images, no bridge)
    python3    pawn_in_liquid_matrix.py <repo> <out_dir> verdict:<row>,<row>  (no bridge: 0 when each row PASSes in the newest read)

Owner, 2026-11-22: "We will have to confirm this on a variety of worn gear to ensure it works well for the large variety
of things Pawns can wear. We should think about animals as well, and droids. ... Mechanoids, Droids, Colonists/humanoids,
and animals should be tested on things like this. We should also test this out on a Star Wars alien (as strange as
possible) to ensure that it still works, like a Hutt or something, as well as a Jawa of course." and "you can still
select something beneath the water, can you not?"

ONE grid map, paused, no hostiles: a row per body (KINDS), a column per state (COLS). Every cell is a 5x5 pit dug 4
notches (2 m) with the pawn on its centre square, facing south; the liquid is written through the engine's driver
write (RM_SubmergeDraw.ProofFillRect). Grid key labels sit on the map and travel with the keeper save.

Rows (PASS/FAIL per cell, from state reads):
  - mode:       RM_SubmergeDraw.ProofPawnCutId reports the mode the pure rule gives for this body, depth and liquid
                (dry: Whole; standing: Cut, or Tinted/Hidden when wholly under; lying: Tinted or Hidden, never Cut);
  - line:       for a Cut, the line lies inside her picture (foot < line < crown) and her picture was measured;
  - no cache:   a wet humanlike is drawn from her render tree, not vanilla's far-zoom atlas quad (noCache=True);
  - selectable: a click at her drawn position (vanilla's Selector rule, ProofSelectAt) selects her, in every cell,
                hidden ones included;
  - setting off (step `off`): with pitSubmergeCutEnabled false every pawn reads dry (drawn whole) and still selects.
Captures: each cell at default zoom (rootSize 24, cropped) and close (rootSize 8): pim_<row>_<col>_{def,close}.png;
`sheets` tiles them into grid_close.png and grid_default.png.
"""
import json
import os
import shutil
import sys
import time

REPO = sys.argv[1]
OUT = sys.argv[2]
STEP = sys.argv[3] if len(sys.argv) > 3 else "all"
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
B = None
LOG = []
ROWS = []
P, S = 5, 8                     # pit side, stride
DEPTH = 4                       # notches (2 m): the deepest fill (1.5 m) stays under the bank
OX, OZ = (int(v) for v in os.environ.get("RM_PIM_ORIGIN", "40,40").split(","))   # SW corner of the bottom-left pit
SUB = "RimMandrake.FlowWorks.RM_SubmergeDraw"
TAR = "RM_Fluid_Tar"
LIE_H = 0.3                     # RM_UnderLiquid.CorpseMetres

# (key, liquid fluid or None for water, metres, lying)
COLS = [
    ("DRY", None, 0.0, False),
    ("WATER_0_5", None, 0.5, False),
    ("WATER_1_5", None, 1.5, False),
    ("TAR_0_5", TAR, 0.5, False),
    ("TAR_1_5", TAR, 1.5, False),
    ("LYING_WATER_0_25", None, 0.25, True),
    ("LYING_TAR_0_25", TAR, 0.25, True),
]
# (key, kindDef, faction, label, apparel)
KINDS = [
    # garments the owner's game has: ArchBig's Cherry Picker list removes Apparel_PowerArmor, Apparel_PowerArmorHelmet,
    # Apparel_Robe and Apparel_PackJump, and Wear() of a removed def leaves the pawn bare (28 FAIL rows on ArchBig,
    # 2026-11-25; RIMMANDRAKE_FIND_WHY_PAWN_GEAR_WEAR_KEPT_NONE). Check a new garment against that list first.
    ("COLONIST_ARMOUR", "Colonist", "player", "colonist, flak jacket + advanced helmet", ["Apparel_FlakJacket", "Apparel_AdvancedHelmet"]),
    ("COLONIST_ROBE_HAT", "Colonist", "player", "colonist, royal robe + cowboy hat", ["Apparel_RobeRoyal", "Apparel_CowboyHat"]),
    ("COLONIST_PACK", "Colonist", "player", "colonist, parka + broadshield pack", ["Apparel_Parka", "Apparel_PackBroadshield"]),
    ("HARE", "Hare", "none", "hare (small animal)", []),
    ("COBRA", "Cobra", "none", "cobra (long animal)", []),
    ("MUFFALO", "Muffalo", "none", "muffalo (quadruped)", []),
    ("THRUMBO", "Thrumbo", "none", "thrumbo (huge animal)", []),
    ("MECH_CENTIPEDE", "Mech_CentipedeBlaster", "none", "centipede (mechanoid)", []),
    ("DROID_T3", "RSW_DW_KotORDroidColonist_T3UD", "player", "T3 utility droid (Droidworks)", []),
    ("JAWA", "RSW_RimMandrakeJawa_Kind", "player", "Jawa", []),
    ("HUTT", "RSW_RimMandrakeHutt_Kind", "player", "Hutt", []),
    ("ITHORIAN", "RSW_RimMandrakeIthorian_Kind", "player", "Ithorian (hammerhead)", []),
]
PAWNS = {}                      # (row, col) -> ThingID


def cells():
    """-> [(rowKey, colKey, fluid, metres, lying, x0, z0)]: rows run north from OZ, columns east from OX."""
    out = []
    for r, k in enumerate(KINDS):
        for c, col in enumerate(COLS):
            out.append((k[0], col[0], col[1], col[2], col[3], OX + c * S, OZ + (len(KINDS) - 1 - r) * S))
    return out


def site():
    return OX - 6, OZ - 3, len(COLS) * S + 8, len(KINDS) * S + 8


def log(k, v):
    LOG.append({k: v})
    print(k, json.dumps(v)[:300])
    sys.stdout.flush()


def bridge():
    global B
    if B is None:
        import validation_core as V
        B = V.Bridge()
    return B


def call(tool, **kw):
    try:
        return bridge().call(tool, **kw) or {}
    except Exception as ex:  # noqa: BLE001
        return {"success": False, "error": str(ex)}


def static(method, arg):
    r = call("jawa/static_call", type=SUB, method=method, args=arg)
    return str(r.get("result") or r.get("error") or r)


def row(name, ok, got):
    ROWS.append({"row": name, "verdict": "PASS" if ok else "FAIL", "got": got})
    if not ok:
        log("FAIL", ROWS[-1])


def dump():
    stamp = time.strftime("%Y%m%dT%H%M%S")
    with open(os.path.join(OUT, "pim_%s_%s.json" % (STEP.replace(":", "_"), stamp)), "w") as fh:
        json.dump({"log": LOG, "rows": ROWS, "pawns": {"%s|%s" % k: v for k, v in PAWNS.items()}}, fh, indent=1)


def pawn_file():
    return os.path.join(OUT, "pim_pawns.json")


def save_pawns():
    with open(pawn_file(), "w") as fh:
        json.dump({"%s|%s" % k: v for k, v in PAWNS.items()}, fh, indent=1)


def load_pawns():
    if os.path.exists(pawn_file()):
        with open(pawn_file()) as fh:
            for k, v in json.load(fh).items():
                a, b = k.split("|", 1)
                PAWNS[(a, b)] = v


def label_ops():
    from modcheck.reviewmap import label_line
    x, z, w, h = site()
    ops = [label_line(OX - 5, OZ + len(KINDS) * S + 2, "PAWN IN LIQUID MATRIX",
                      "her own picture cut at the surface; rows = body, columns = liquid and depth (pit 2 m deep)",
                      "#ffffff", "medium", "pim")]
    for c, col in enumerate(COLS):
        what = "dry" if not col[2] else "%s %.2g m%s" % ("tar" if col[1] else "water", col[2], ", lying" if col[3] else "")
        ops.append(label_line(OX + c * S, OZ + len(KINDS) * S, col[0].replace("_", " "), what, "#ffd27f", "small", "pim"))
    for r, k in enumerate(KINDS):
        ops.append(label_line(OX - 5, OZ + (len(KINDS) - 1 - r) * S + 2, k[0].replace("_", " "), k[3], "#bfe4ff", "small", "pim"))
    return ops


def labels():
    call("jawa/review_label", action="clear", tag="pim")
    r = call("jawa/review_label", action="add", ops="\n".join(label_ops()))
    log("labels", {k: r.get(k) for k in ("success", "added", "message") if k in r})


def sky_gate(when, clear=False):
    import validation_core as V
    v = V.open_sky_site(bridge(), site()) if clear else V.assert_open_sky(bridge(), site())
    log("open_sky_" + when, {k: v.get(k) for k in ("ok", "rect", "roofCells", "rockCells", "why", "cleared")})
    if not v.get("ok"):
        ROWS.append({"row": "site_open_sky_" + when, "verdict": "UNMEASURED", "got": v.get("why")})
        dump()
        sys.exit(2)


def spawned_id(r):
    for v in r.values() if isinstance(r, dict) else []:
        if isinstance(v, list):
            for it in v:
                if isinstance(it, dict) and it.get("id"):
                    return it["id"]
    return None


def stage():
    x, z, w, h = site()
    # which companion staged it: on 2026-11-25 another run's proof build on ArchBig failed every wear, and no record named
    # the build (RIMMANDRAKE_FIND_WHY_PAWN_GEAR_WEAR_KEPT_NONE); compare its commit with origin/main before reading a wear row
    hs = call("jawa/companion_handshake")
    log("companion", {k: hs.get(k) for k in ("companionSha", "companionVersion", "companionFileSha256", "companionPath", "compileProfile", "error")
                      if hs.get(k) is not None} or str(hs)[:300])
    r = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
             args="%d;%d;%d;%d" % (x, z, w, h))
    log("reset", str(r.get("result") or r)[:200])
    # jawa/destroy_batch never destroys pawns (by design): a restage left the last stage's pawns standing in every pit, two
    # bodies on one square z-fighting into stripes (measured 2026-11-22). Vanish every pawn in the site first. Clear the
    # site's things before the sky gate reads them: its list_things read caps at 5000 and a busy map refused the site.
    gone = 0
    for p in (call("jawa/list_pawns", rect="%d,%d,%d,%d" % (x, z, w, h), limit=500).get("pawns") or []):
        pid = p.get("id") or p.get("thingId") or p.get("pawnId")
        if pid and call("jawa/pawn_force_incapacitate", pawn=str(pid), action="vanish").get("success") is True:
            gone += 1
    log("vanished_old_pawns", gone)
    call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (x, z, w, h), categories="All")
    sky_gate("before_stage", clear=True)
    call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (x, z, w, h), categories="All")
    call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (x, z, w, h))
    call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % (x, z, w, h))
    sky_gate("after_clear")
    call("jawa/kill_hostiles")
    call("jawa/weather_set", weather="Clear", lockWeather=True)
    call("rimworld/pause_game")
    for rk, ck, fluid, m, lying, x0, z0 in cells():
        for i in range(P):
            for j in range(P):
                call("jawa/flowworks_excavation_drive", x=x0 + i, z=z0 + j, deepenLevels=DEPTH, setBodyWaterM=-1, fillInLevels=0)
    for rk, ck, fluid, m, lying, x0, z0 in cells():
        if m > 0:
            log("fill_%s_%s" % (rk, ck), static("ProofFillRect", "%d,%d,%d,%d,%g%s" % (x0, z0, P, P, m, "," + fluid if fluid else "")))
    for rk, ck, fluid, m, lying, x0, z0 in cells():
        kind = next(k for k in KINDS if k[0] == rk)
        r = call("jawa/spawn_pawn", kindDef=kind[1], x=x0 + 2, z=z0 + 2, faction=kind[2], count=1)
        pid = spawned_id(r)
        if not pid:
            row("%s_%s_spawned" % (rk, ck), False, str(r)[:300])
            continue
        PAWNS[(rk, ck)] = pid
        call("jawa/pawn_gear", pawn=pid, action="clear", clearWhat="equipment")
        for ap in kind[4]:
            g = call("jawa/pawn_gear", pawn=pid, action="wear", **{"def": ap})
            # a PASS row too, so "no failing wear row" cannot hold on a stage that wore nothing; a FAIL keeps the read-back's
            # wrong block and the worn list whole (the first 200 characters cut both off, 2026-11-25)
            rb = g.get("readBack") or {}
            worn = [a.get("def") if isinstance(a, dict) else a for a in ((g.get("pawn") or {}).get("apparel") or [])]
            row("%s_%s_wears_%s" % (rk, ck, ap), g.get("success") is True,
                {"faults": rb.get("faults"), "wrong": rb.get("wrong"), "made": rb.get("made"), "notes": g.get("notes"),
                 "worn": worn, "error": g.get("error") or g.get("message")})
        if lying:
            # lie down without wounds (anesthetic: the forced downing's wound decals swamped the look, 2026-11-22); a body
            # that takes no anesthetic (a mechanoid, a droid) lies as its clean corpse (Pawn.Kill, no damage)
            d = call("jawa/pawn_health", pawn=pid, action="add", hediff="Anesthetic", severity=1.0)
            if "lying=False" in static("ProofPawnCutId", pid):
                d = call("jawa/pawn_force_incapacitate", pawn=pid, action="kill")
            log("lying_%s_%s" % (rk, ck), str(d)[:200])
    # facing south, so the owner sees faces: one call per pawn (a comma list turned none, measured 2026-11-22)
    turned = sum(1 for pid in PAWNS.values() if call("jawa/set_pawn_rotation", pawnId=pid, dir="south").get("success") is True)
    log("turned_south", turned)
    call("jawa/kill_hostiles")
    save_pawns()
    labels()
    log("staged", {"pawns": len(PAWNS)})


def kv_of(text):
    return dict(p.split("=", 1) for p in text.split() if "=" in p)


def lerp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return ys[-1]


def want_mode(kv, lying):
    """The mode the pure rule gives (RM_PawnCutMath.Decide) for the pawn's own read height, level and clarity."""
    lv, h, cl = float(kv.get("level", 0)), float(kv.get("height", 0)), float(kv.get("clarity", 0))
    if lv <= 0:
        return "Whole"
    if lying:
        s = min(1.0, lv / LIE_H)
        return ("Tinted" if cl > 0 else "Hidden") if s >= 1 else "Tinted"
    d = lv / h if h > 0 else 1.0
    return ("Tinted" if cl > 0 else "Hidden") if d >= 1 else "Cut"


# A colonist's picture spans 1.015..1.231 cells foot to crown standing (this matrix, 2026-11-22) for 1.75 m: the scale that
# turns any humanlike's own picture into metres, read from the picture, never from the height the mod printed.
COLONIST_SPAN, COLONIST_M = 1.22, 1.75


def in_line_with_picture(kv, level):
    """RIMMANDRAKE_CLASS_DROID_AND_JAWA_GONE_IN_SHALLOW_TAR: the `_mode` row wants the mode for the pawn's OWN printed
    height, so it agreed when a Jawa and a T3 droid were given a rat's 0.5 m. This row reads her picture instead: a
    standing humanlike whose picture is clearly taller than the liquid (by its span against a colonist's) is Cut, with
    some of her picture above the line. -> (ok, text)"""
    try:
        span = float(kv["crown"]) - float(kv["foot"])
    except (KeyError, ValueError):
        return False, "UNMEASURED: no picture extent: %s" % kv
    est = span / COLONIST_SPAN * COLONIST_M
    text = "picture %.3f cells = about %.2f m; liquid %.2f m; mode %s share %s height %s" % (
        span, est, level, kv.get("mode"), kv.get("share"), kv.get("height"))
    if level >= 0.9 * est:
        return True, "deep enough to cover her: " + text
    return kv.get("mode") == "Cut" and float(kv.get("share", 1)) < 1.0, text


def read(tag=""):
    load_pawns()
    off = tag == "off"
    for rk, ck, fluid, m, lying, x0, z0 in cells():
        pid = PAWNS.get((rk, ck))
        rid = "%s_%s%s" % (rk, ck, "_SETTING_OFF" if off else "")
        if not pid:
            row(rid + "_present", False, "no pawn staged")
            continue
        text = static("ProofPawnCutId", pid)
        kv = kv_of(text)
        if off or m == 0:
            row(rid + "_drawn_whole", " dry" in text or kv.get("mode") == "Whole", text)
        else:
            is_lying = kv.get("lying") == "True"
            row(rid + "_lying_as_staged", is_lying == lying, text)
            want = want_mode(kv, is_lying)
            row(rid + "_mode", kv.get("mode") == want, "want %s: %s" % (want, text))
            if not is_lying and kv.get("humanlike") == "True":
                row(rid + "_shows_in_line_with_her_picture", *in_line_with_picture(kv, m))
            if kv.get("mode") == "Cut":
                try:
                    f, c, l = float(kv["foot"]), float(kv["crown"]), float(kv["line"])
                    row(rid + "_line_inside_her_picture", f < l < c, "foot=%s line=%s crown=%s" % (f, l, c))
                except (KeyError, ValueError):
                    row(rid + "_line_inside_her_picture", False, "UNMEASURED: no picture extent: " + text)
            if kv.get("humanlike") == "True" and kv.get("mode") in ("Cut", "Tinted"):
                row(rid + "_drawn_from_her_tree_not_the_atlas", kv.get("noCache") == "True", text)
        # the click: at her drawn position, by vanilla's Selector rule
        info = call("jawa/pawn_get", pawn=pid)
        pos = (info.get("drawPos") or info.get("position") or {}) if isinstance(info, dict) else {}
        px, pz = pos.get("x", x0 + 2.5), pos.get("z", z0 + 2.5)
        sel = static("ProofSelectAt", "%s,%s" % (px, pz))
        skv = kv_of(sel)
        row(rid + "_click_selects_her", skv.get("selected") in (pid, pid.replace("Thing_", ""), "Corpse_" + pid),
            "%s (mode %s)" % (sel, kv.get("mode")))
    fails = [r for r in ROWS if r["verdict"] != "PASS"]
    log("rows", {"rows": len(ROWS), "fail": len(fails), "first_fails": [r["row"] for r in fails[:20]]})


def set_cut(on):
    r = call("jawa/mod_settings_field", typeName="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings", action="set",
             field="pitSubmergeCutEnabled", value="true" if on else "false")
    log("setting_%s" % ("on" if on else "off"), str(r)[:200])
    return r


def midday():
    """Noon light for the captures WITHOUT running time: downed pawns lie in the liquid and would drown (the governor
    stops a tick advance for that, measured 2026-11-22). The clock is set (jawa/time_set_ticks simulates nothing)."""
    t = call("jawa/time_clock")
    ta, tg = t.get("ticksAbs"), t.get("ticksGame")
    if ta is None or tg is None:
        log("hour", "UNMEASURED: " + str(t)[:160])
        return
    hour = (ta % 60000) / 2500.0
    if 10 <= hour <= 14:
        log("hour", hour)
        return
    delta = (12 * 2500 - ta % 60000) % 60000
    r = call("jawa/time_set_ticks", ticks=int(tg + delta), timeException=True,
             why="pawn-in-liquid matrix: noon light for the captures; no tick may run (downed pawns lie in liquid)")
    log("hour_set", {"from": hour, "delta": delta, "r": str(r)[:160]})
    call("rimworld/pause_game")


def shot(name, cx, cz, root):
    call("jawa/clear_ui", all=True)
    call("rimworld/jump_camera_to_cell", x=int(cx), z=int(cz))
    call("rimworld/set_camera_zoom", rootSize=root)
    time.sleep(1.2)
    r = call("jawa/take_screenshot", fileName="pim_%s_%d" % (name, int(time.time())))
    src = r.get("filePath")
    for _ in range(12):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    if not src or not os.path.exists(src):
        log("shot_failed", {"name": name, "r": str(r)[:200]})
        return None
    dst = os.path.join(OUT, name + ".png")
    shutil.copyfile(src, dst)
    return dst


CLOSE, DEFAULT = 8.0, 24.0


def shots(suffix=""):
    call("rimworld/pause_game")
    call("jawa/review_label", action="hide")
    n = 0
    for rk, ck, fluid, m, lying, x0, z0 in cells():
        n += bool(shot("pim_%s_%s_close%s" % (rk, ck, suffix), x0 + 2, z0 + 2, CLOSE))
        n += bool(shot("pim_%s_%s_def%s" % (rk, ck, suffix), x0 + 2, z0 + 2, DEFAULT))
    call("jawa/review_label", action="show")
    x, z, w, h = site()
    shot("pim_overview%s" % suffix, x + w // 2, z + h // 2, 40.0)
    log("shots", {"count": n})


def sheets():
    """WSL python3 (PIL): crop each cell's close and default shot to its pit and tile them, labelled, row by row."""
    from PIL import Image, ImageDraw
    for kind, root, crop in (("close", CLOSE, 6.0), ("def", DEFAULT, 6.0)):
        T = 260
        rows = []
        for k in KINDS:
            tiles = []
            for col in COLS:
                p = os.path.join(OUT, "pim_%s_%s_%s.png" % (k[0], col[0], kind))
                if not os.path.exists(p):
                    tiles.append(None)
                    continue
                im = Image.open(p).convert("RGB")
                w, h = im.size
                ppc = h / (2.0 * root)
                half = crop * ppc / 2.0
                cx, cy = w / 2.0, h / 2.0        # the camera sits on the pit's centre square (her square)
                t = im.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half)))
                tiles.append(t.resize((T, T), Image.LANCZOS))
            rows.append(tiles)
        LW, HH = 230, 30
        sheet = Image.new("RGB", (LW + T * len(COLS), HH + T * len(KINDS)), (18, 18, 18))
        d = ImageDraw.Draw(sheet)
        for c, col in enumerate(COLS):
            d.text((LW + c * T + 6, 8), col[0], fill=(255, 210, 127))
        for r, k in enumerate(KINDS):
            d.text((6, HH + r * T + T // 2 - 10), k[0], fill=(191, 228, 255))
            d.text((6, HH + r * T + T // 2 + 4), k[3][:32], fill=(150, 170, 190))
            for c, t in enumerate(rows[r]):
                if t is not None:
                    sheet.paste(t, (LW + c * T, HH + r * T))
        out = os.path.join(OUT, "grid_%s.png" % ("close" if kind == "close" else "default"))
        sheet.save(out)
        print("sheet", out)


def verdict(names):
    """No bridge: exit 0 when every named row PASSes in the newest read (pim_read_<stamp>.json, or pim_all_<stamp>.json
    from the `all` step, in OUT; newest by its stamp), else 1, printing each row's state (MISSING: the newest read has no
    such row, i.e. no read since the row was written)."""
    names_ok = lambda f: f.endswith(".json") and (f.startswith("pim_read_") or f.startswith("pim_all_"))
    reads = sorted((f for f in os.listdir(OUT) if names_ok(f)), key=lambda f: f.rsplit("_", 1)[-1]) if os.path.isdir(OUT) else []
    if not reads:
        print("VERDICT: FAIL (no pim_read_*.json or pim_all_*.json in %s)" % OUT)
        return 1
    rows = {r["row"]: r for r in json.load(open(os.path.join(OUT, reads[-1]), encoding="utf-8")).get("rows", [])}
    ok = True
    for n in names:
        r = rows.get(n)
        print("%-9s %s  %s" % (r["verdict"] if r else "MISSING", n, str((r or {}).get("got", ""))[:200]))
        ok = ok and r is not None and r["verdict"] == "PASS"
    print("VERDICT: %s (%s)" % ("PASS" if ok else "FAIL", reads[-1]))
    return 0 if ok else 1


if __name__ == "__main__":
    if STEP.startswith("verdict:"):
        sys.exit(verdict(STEP.split(":", 1)[1].split(",")))
    t0 = time.time()
    if STEP in ("all", "stage"):
        stage()
    if STEP in ("all", "shots"):
        midday()
        shots()             # before the read: a pawn's render tree holds its draw requests only once she was drawn
    if STEP in ("all", "read"):
        read()
    if STEP in ("all", "off"):
        set_cut(False)
        time.sleep(1.0)
        read("off")
        load_pawns()
        k = KINDS[0][0]
        for col in COLS:
            x0 = OX + COLS.index(col) * S
            z0 = OZ + (len(KINDS) - 1) * S
            shot("pim_%s_%s_close_SETTING_OFF" % (k, col[0]), x0 + 2, z0 + 2, CLOSE)
        set_cut(True)
    if STEP == "sheets":
        sheets()
        sys.exit(0)
    if STEP == "labels":
        labels()
    if STEP.startswith("save:"):
        from modcheck.reviewmap import save_keeper
        call("rimworld/pause_game")
        log("save", save_keeper(bridge(), STEP.split(":", 1)[1], signs=label_ops()))
    log("elapsed_s", round(time.time() - t0, 1))
    dump()
    sys.exit(2 if any(r["verdict"] == "UNMEASURED" for r in ROWS) else 1 if any(r["verdict"] != "PASS" for r in ROWS) else 0)
