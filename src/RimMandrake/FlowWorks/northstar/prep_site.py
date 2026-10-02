#!/usr/bin/env python3
"""Build, classify and save the FlowWorks golden trial site + its sidecar (trial plan 3.4-3.8).

Run ONCE per version contract by the seat holding the bridge, on the `flowworks` tier, from a
`rimworld/start_debug_game_ready` map (>= 200x200):

    python.exe src/RimMandrake/FlowWorks/northstar/prep_site.py --seat FOUNDRY
    python3    src/RimMandrake/FlowWorks/northstar/prep_site.py --fake     # offline rehearsal

What it does, each write followed by an independent read (northstar_driver discipline):
  1. refuses unless loaded, paused (proved), dev mode on, map >= 200x200, bridge held by --seat;
  2. lays out the plots (site_spec.layout) and despawns every pawn on the map (roster must read 0);
  3. per plot: paints out water/marsh/mud within the 15-cell halo, clears Things over plot+buffer,
     paints Soil, paints the authored reservoirs, unroofs, roofs the rain twin, unfogs, drops Home;
  4. weather Clear (locked), ends every map GameCondition, clears the incident queue, moves the
     clock FORWARD to summer, grants research;
  5. reads the Mod Settings snapshot (must be shipped defaults);
  6. forces body classification once via jawa/flowworks_body_report and records each body --
     STOPS HERE today if that tool is not registered (site_spec.NEEDED_TOOLS): a golden save
     with unclassified bodies is not an accepted baseline (plan 3.4, GPT #9-11);
  7. re-reads every plot+buffer cell against the manifest and every check cell's temperature;
  8. saves NS_FlowWorks_TrialSite_v1 with a Saves-folder stat before/after (the wrong-slot trap),
     sets it read-only, and writes the sidecar (version contract + plots + bodies + per-cell
     manifest) beside it and to infrastructure/state/northstar/.
Exit codes: 0 saved; 2 refused (named step); 3 a NEEDED tool is missing (nothing saved).
"""
import argparse
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import site_spec as S  # noqa: E402
import preflight_flowworks as PF  # noqa: E402
from northstar_driver import PASS  # noqa: E402
from northstar_driver.preflight import check_paused, check_dev_god, check_loaded_not_zombie  # noqa: E402

QUADRUM_TICKS = 900000


class Refused(Exception):
    def __init__(self, step, msg, code=2):
        Exception.__init__(self, "%s: %s" % (step, msg))
        self.step, self.code = step, code


def _ok(r, step, what):
    if not isinstance(r, dict) or r.get("success") is False:
        raise Refused(step, "%s failed: %s" % (what, str(r)[:200]))
    return r


def game_build(player_log):
    try:
        with open(player_log, "rb") as f:
            head = f.read(65536).decode("utf-8", "replace")
    except (OSError, TypeError):
        return "UNMEASURED"
    m = re.search(r"RimWorld\s+(\d+\.\d+\.\d+\s*rev\d+)", head)
    return m.group(1) if m else "UNMEASURED"


def saves_stat(d):
    out = {}
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p):
            st = os.stat(p)
            out[f] = (st.st_size, st.st_mtime)
    return out


def paint_halo(s, plot, size, authored):
    """No natural water/marsh/mud within HALO cells of a plot except its own reservoir (plan 3.4)."""
    halo = S.clip(S._buffered(plot["rect"], S.HALO), size)
    terr = S.parse_ops(_ok(s.call("jawa/get_terrain_batch", rects=S.rect_str(halo)), "3", "get_terrain_batch")
                       .get("ops"))
    bad = sorted(c for c, t in terr.items() if c not in authored and any(w in str(t) for w in S.WET_OR_ROUGH))
    if bad:
        ops = ";".join("%s:%d,%d,1,1" % (S.SOIL, x, z) for x, z in bad)
        _ok(s.call("jawa/set_terrain_batch", ops=ops), "3", "set_terrain_batch(halo)")
    return len(bad)


def build_plot(s, plot, size, authored):
    big = S.clip(plot["buffered"], size)
    rs = S.rect_str(big)
    n_halo = paint_halo(s, plot, size, authored)
    _ok(s.call("jawa/destroy_batch", rects=rs, categories="All"), "3", "destroy_batch")
    ops = ["%s:%s" % (S.SOIL, rs)] + ["%s:%s" % (b["terrain"], S.rect_str(b["rect"])) for b in plot["bodies"]]
    _ok(s.call("jawa/set_terrain_batch", ops=";".join(ops)), "3", "set_terrain_batch")
    _ok(s.call("jawa/set_roof_batch", ops=rs, roofDef="None"), "3", "set_roof_batch(clear)")
    for x, z in plot["roofed"]:
        _ok(s.call("jawa/set_roof_batch", ops="%d,%d,1,1" % (x, z), roofDef="RoofConstructed"), "3",
            "set_roof_batch(twin)")
    _ok(s.call("jawa/set_fog", action="unfog", rect=rs), "3", "set_fog")
    s.call("jawa/paint_area", area="Home", ops=rs, value=False)
    return n_halo


def environment(s, log):
    _ok(s.call("jawa/weather_set", weather="Clear", lockWeather=True), "4", "weather_set")
    w = _ok(s.call("jawa/weather_get"), "4", "weather_get")
    for c in w.get("conditions") or []:
        if c.get("affectsThisMap"):
            _ok(s.call("jawa/game_condition", action="end", condition=c.get("def")), "4", "game_condition end")
    q = _ok(s.call("jawa/incident_queue_clear"), "4", "incident_queue_clear")
    log("incident queue: cleared %s" % q.get("clearedCount"))
    for _ in range(4):
        mi = _ok(s.call("jawa/map_info"), "4", "map_info")
        if "summer" in str(mi.get("season")).lower():
            break
        t = _ok(s.call("jawa/time_clock"), "4", "time_clock")["ticksGame"]
        _ok(s.call("jawa/time_set_ticks", ticks=int(t) + QUADRUM_TICKS), "4", "time_set_ticks(forward)")
    else:
        raise Refused("4", "season never reached summer: %s" % mi.get("season"))
    s.call("jawa/research_bulk", mode="finish_all")
    w = _ok(s.call("jawa/weather_get"), "4", "weather_get")
    if w.get("weather") != "Clear" or [c for c in w.get("conditions") or [] if c.get("affectsThisMap")]:
        raise Refused("4", "environment did not settle: %s" % w)
    return mi.get("season")


def classify_bodies(s, plots, log):
    if "jawa/flowworks_body_report" not in s.tools:
        raise Refused("6", "jawa/flowworks_body_report is not registered -- bodies cannot be classified, "
                           "so no golden save is written. Contract: %s"
                      % S.NEEDED_TOOLS["jawa/flowworks_body_report"], code=3)
    out = {}
    for p in plots:
        for b in p["bodies"]:
            x, z, w, h = b["rect"]
            probe = (x + w // 2, z + h // 2)
            r = _ok(s.call("jawa/flowworks_body_report", x=probe[0], z=probe[1]), "6", "body_report")
            rec = r.get("body") or {}
            if not r.get("classified"):
                raise Refused("6", "%s did not classify" % b["name"])
            if bool(rec.get("limitless")) != b["limitless"]:
                raise Refused("6", "%s limitless=%s, layout wants %s" % (b["name"], rec.get("limitless"),
                                                                         b["limitless"]))
            if rec.get("cellCount") != w * h:
                raise Refused("6", "%s classified %s cells, painted %d -- it joined other water"
                              % (b["name"], rec.get("cellCount"), w * h))
            out[b["name"]] = {"plot": p["id"], "probe": list(probe), "rect": list(b["rect"]),
                              "activeFluid": r.get("activeFluid"), "expect_limitless": b["limitless"],
                              "record": {k: rec.get(k) for k in ("id", "limitless", "cellCount", "capacity",
                                                                 "stock", "recededCount")}}
            log("body %s: %s" % (b["name"], out[b["name"]]["record"]))
    return out


def verify_site(s, plots, size):
    manifest, bad = {}, []
    for p in plots:
        want = S.expected_cells(p, size)
        manifest[p["id"]] = {"%d,%d" % c: v for c, v in sorted(want.items())}
        live = PF.read_plot_state(s, p, size)
        for msg in PF.diff_plot(p, live, manifest[p["id"]])[:4]:
            bad.append("plot %s: %s" % (p["id"], msg))
    pts = sorted({c for p in plots for c in S.check_points(p)})
    for c, r in zip(pts, s.call_many([("jawa/cell_temperature", {"cell": "%d,%d" % c}) for c in pts])):
        if not isinstance(r, dict) or not r.get("ok") or not (10.0 <= float(r["temperature"]) <= 45.0):
            bad.append("cell %d,%d temperature %s" % (c[0], c[1], r.get("temperature") if isinstance(r, dict) else r))
    r = _ok(s.call("jawa/flowworks_excavation_report", x=plots[0]["rect"][0], z=plots[0]["rect"][1]), "7",
            "excavation_report")
    if r.get("excavatedCellCount"):
        bad.append("map has %s excavated cells" % r["excavatedCellCount"])
    if bad:
        raise Refused("7", "site does not match its manifest: %s" % bad[:8])
    return manifest


def save_golden(s, saves_dir, rebuild, log):
    path = os.path.join(saves_dir, S.GOLDEN_NAME + ".rws")
    if os.path.exists(path):
        if not rebuild:
            raise Refused("8", "%s exists; golden saves are never overwritten (pass --rebuild to move it aside)"
                          % path)
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
        aside = path + ".superseded.%s" % time.strftime("%Y%m%dT%H%M%S")
        os.replace(path, aside)
        log("moved old golden aside -> %s" % aside)
    before = saves_stat(saves_dir)
    _ok(s.call("rimworld/save_game", saveName=S.GOLDEN_NAME), "8", "save_game")
    after = saves_stat(saves_dir)
    changed = [f for f in before if f in after and after[f] != before[f]]
    new = [f for f in after if f not in before]
    if changed:
        raise Refused("8", "save_game rewrote existing save(s) %s (the wrong-slot trap)" % changed)
    if os.path.basename(path) not in new:
        raise Refused("8", "save_game reported success but %s did not appear (new: %s)" % (path, new))
    os.chmod(path, stat.S_IREAD)
    return path


def prep(s, saves_dir, seat, prefs=None, player_log=None, repo_copy_dir=S.REPO_SIDECAR_DIR, rebuild=False,
         bridge_paths=None, log=print):
    # 1. refuse a game we cannot drive
    z = check_loaded_not_zombie(s)
    if z.status != PASS:
        raise Refused("1", z.evidence)
    if check_paused(s, fix=True).status != PASS:
        raise Refused("1", "could not prove the game paused")
    if check_dev_god(s, need_dev=True, need_god=False).status != PASS:
        raise Refused("1", "dev mode is off")
    b1 = PF.p_b1(s, bridge_paths or PF.Paths(), None, seat)
    if b1.status != PASS:
        raise Refused("1", b1.evidence)
    mi = _ok(s.call("jawa/map_info"), "1", "map_info")
    size = (mi["sizeX"], mi["sizeZ"])
    # 2. layout + roster
    try:
        plots = S.layout(size)
    except ValueError as ex:
        raise Refused("2", str(ex))
    roster = [q.get("id") for q in _ok(s.call("jawa/list_pawns", limit=500), "2", "list_pawns").get("pawns") or []]
    _ok(s.call("jawa/destroy_batch", rects="0,0,%d,%d" % size, categories="Pawn"), "2", "destroy_batch(Pawn)")
    left = _ok(s.call("jawa/list_pawns", limit=500), "2", "list_pawns").get("pawns") or []
    if left:
        raise Refused("2", "pawns survived the despawn: %s" % [q.get("id") for q in left][:6])
    log("despawned %d pawn(s): %s" % (len(roster), roster[:8]))
    # 3. plots
    authored = {c for p in plots for b in p["bodies"] for c in S.cells(b["rect"])}
    halo = sum(build_plot(s, p, size, authored) for p in plots)
    log("built %d plots; painted %d stray wet/rough halo cell(s) to Soil" % (len(plots), halo))
    # 4. environment
    season = environment(s, log)
    # 5. settings
    snap, drift = PF.settings_snapshot(s)
    if drift:
        raise Refused("5", "Mod Settings not at shipped defaults: %s" % drift)
    # 6. bodies (the step that needs a new tool)
    bodies = classify_bodies(s, plots, log)
    # 7. read everything back
    manifest = verify_site(s, plots, size)
    # 8. save + sidecar
    path = save_golden(s, saves_dir, rebuild, log)
    render = S.read_prefs(prefs) if prefs and os.path.isfile(prefs) else {}
    sidecar = {
        "item": "FLOWWORKS_NORTHSTAR_SITE_PREP_1", "save": os.path.basename(path),
        "built": time.strftime("%Y-%m-%dT%H:%M:%S"), "seat": seat,
        "contract": {"save_sha256": S.sha256_file(path), "game_build": game_build(player_log),
                     "flowworks_dll_sha256": S.sha256_file(os.path.join(S.MOD_DIR, S.DLL_REL)),
                     "flowworks_srchash_sha256": S.sha256_file(os.path.join(S.MOD_DIR, S.DLL_REL) + ".srchash"),
                     "defs_hash": S.defs_hash(), "settings": snap, "prep_version": S.PREP_VERSION},
        "generation": {"mapId": mi.get("mapId"), "tile": mi.get("tile"), "sizeX": size[0], "sizeZ": size[1],
                       "biome": mi.get("mapBiome"), "season": season,
                       "seed": "UNMEASURED (no bridge read of the world seed)"},
        "render_profile": {k: render.get(k) for k in S.RENDER_KEYS},
        "plots": [{k: v for k, v in p.items()} for p in plots],
        "bodies": bodies, "despawned": roster, "manifest": manifest,
    }
    out = os.path.join(saves_dir, S.GOLDEN_NAME + ".json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=1)
    if repo_copy_dir:
        os.makedirs(repo_copy_dir, exist_ok=True)
        shutil.copyfile(out, os.path.join(repo_copy_dir, S.GOLDEN_NAME + ".json"))
    log("golden save %s (read-only), sidecar %s" % (path, out))
    return sidecar


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seat", default="FOUNDRY", choices=S.SEATS)
    ap.add_argument("--rebuild", action="store_true", help="move an existing golden save aside first")
    ap.add_argument("--fake", action="store_true", help="rehearse against FakeFlowWorksGame in a temp dir")
    ap.add_argument("--fake-without-new-tools", action="store_true", help="rehearse today's live tool set")
    a = ap.parse_args(argv)
    try:
        if a.fake or a.fake_without_new_tools:
            from fakegame import FakeFlowWorksGame, FakeTransport
            from northstar_driver.session import FastSession
            tmp = tempfile.mkdtemp(prefix="ns_fw_prep_")
            g = FakeFlowWorksGame(saves_dir=tmp, shots_dir=tmp, new_tools=not a.fake_without_new_tools)
            bridge = os.path.join(tmp, "BRIDGE")
            with open(bridge, "w") as f:
                f.write("%s holds the bridge (fake)\n" % a.seat)
            with FastSession(transport=FakeTransport(g), strict=False) as s:
                prep(s, tmp, a.seat, repo_copy_dir=None, bridge_paths=PF.Paths(bridge_file=bridge))
            print("fake rehearsal OK -> %s" % tmp)
            return 0
        P = PF.Paths()
        from northstar_driver.session import FastSession
        with FastSession() as s:
            prep(s, P.saves, a.seat, prefs=P.prefs, player_log=P.player_log, rebuild=a.rebuild, bridge_paths=P)
        return 0
    except Refused as ex:
        print("PREP REFUSED at step %s" % ex)
        return ex.code


if __name__ == "__main__":
    sys.exit(main())
