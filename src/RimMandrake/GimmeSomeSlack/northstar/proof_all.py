"""proof_all.py -- Gimme Some Slack: the ONE live proof (owner densification, 2026-10-05).

Design: design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md (section 6 is this file's spec,
section 2 the cut-by-cut reasoning, section 3 the row table). Owner, typed: "reduce the number of north Star
verifications and verification stations for the human review sheet as well. If so, remove them. Then run them;
and finally handoff." and "Yes you should examine the hash bound ones too. This is a full densification."

    python3    src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --offline-gate        # WSL: the offline tier only (seconds)
    python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live [--no-shots]   # gimmesomeslack tier, bridge held
    python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --only core,aerial --no-fresh-map   # debug a block

Run python.exe from the repo root (bridge calls only work under python.exe; pipe through tr -d '\\r').

ORDER (section 6; one fresh quicktest map, one calm-world setup, ONE save + ONE load):
  0. offline gate, run in WSL python3 (numpy, the C# SelfTest): validation.py O1-O6 (O3 = C# SelfTest vs the Python
     oracle + its --probe mutation + the DeterminismChecks floor replay), northstar_matrix/selftest.py,
     human_review.py --plan, selftest_human_review.py, and the design spec JSON for the matrix. Any red refuses to go
     live, except an id named with --allow-red (recorded in the result).
  1. P1 fresh map (250x250)  P2 tier running + startup log clean  P3 probe channels (cord/aerial/hose) + site pinned
     (weather Clear locked, noon, incident queue cleared, non-colonists destroyed, colonists moved out of the matrix
     REGION) + no pawn in REGION + matrix board pitch. These replace every script's own harness rows (L0-L6, O0, I0,
     H0, S0, A0, H1, RL1, CR0, P1B_plot_built): in this session such a row is written only if it is NOT PASS.
  2. matrix, reduced (39 scenes, northstar_matrix/reduced.py) FIRST: it clears map-wide and tears every board down.
  3. core (validation.live_battery) -> aerial -> hose -> maze -> relay -> carry -> style -> style-hose, each on its own
     site (disjoint from each other; the hose/maze/relay/carry sites lie inside the matrix REGION, which is empty by then).
  4. D1/D2 (matrix determinism: zero-tick re-reads; a fresh CordBuilder == the incremental one, guard for the ring-board
     defect of 2026-10-02), then the ONE save: SL1 only the new .rws appeared; SL2 the save names no class of ours
     (guard: the MapComponent written into saves, 2026-10-02); SL3 after the load every subsystem's census equals the
     one before (guard: no cords on ANY loaded save, the MapDrawer NRE of 2026-10-02); SL4 carried-hose states survive.
  5. Z: one log budget over the whole session (startup excluded, the load included).
  Not here: the removal check (walk E1, paused by the owner) -- `validation.py --removal-check <the SL save>` after one
  cold load onto `modset_builder.py --tier flowworks`. And not a proof: `human_review.py --build --fresh-map`.

--no-shots: no screenshot is rendered anywhere; every camera move the shots made is kept (frame_cell_rect), because the
cord graph rebuilds off camera-driven section regeneration (northstar_matrix/run_live.py LEARNED 2026-10-04).

Output: ONE result JSON northstar/proof_all_<stamp>.json (mode "live" for a full run; "partial" with --only, which
`modcheck record` refuses) and a one-screen summary.
"""
import argparse
import collections
import hashlib
import json
import os
import re
import subprocess
import sys
import time

OUT_DIR = os.path.dirname(os.path.abspath(__file__))      # .../GimmeSomeSlack/northstar (this file lives here, outside mod_hash)
HERE = os.path.dirname(OUT_DIR)                           # the mod root: validation.py, human_review.py, northstar_matrix/
MX_DIR = os.path.join(HERE, "northstar_matrix")
for _p in (HERE, MX_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import validation as V  # noqa: E402

SCRATCH_WIN = r"D:\Luke\dev\_rmscratch\gss_proof"
SCRATCH_POSIX = "/mnt/d/Luke/dev/_rmscratch/gss_proof"
SPEC_NAME = "scenes_design.json"
BLOCKS = ["matrix", "core", "aerial", "hose", "maze", "relay", "carry", "style", "style_hose", "save_load"]
PARK = (125, 165)                     # colonists moved here, out of the matrix REGION and every site

# The row ids a full live run emits, per block, for the required-check manifest (the walk's `checkout:` header names
# this file; modcheck/required_checks.py calls declared_rows(); NORTHSTAR_RESULTS_JOIN_1). Seeded from the live runs
# of 2026-10-05 08:24-08:52 (144 rows each). The matrix block is NOT listed: its ids are the reduced spec's scenes,
# computed below. A row the run emits that is not declared shows in the report as "observed, not in manifest"; a
# declared row the run no longer emits shows as not reached -- so this list can drift visibly, never silently.
DECLARED_ROWS = {
    "preflight": ["P1_fresh_map", "P2_tier_running_startup_log_clean", "P3_probes_site_pinned_region_empty"],
    "core": ["M1_conduit_transparent", "M1_cords_exist", "M1_node_census", "M1c_end_pieces", "M2b_no_vertex_unwalkable",
             "M6_overlay_lines_intact", "M5_local_invalidation", "M8_break_two_ends_live_dead", "M2_cords_only_within_net",
             "B1_rope_settle", "B6_tangle_lit_strips", "B3_whip_live_ends", "B4_downed_wire_bursts",
             "B4b_sparks_thrown_ticking", "B7_sway_cpu_two_frame", "B7b_sway_shader_path", "B7c_floor_ripple",
             "B5_selection_highlight", "B8_lod_far_zoom", "B9_cutscene_guard_idle", "B6b_strips_dark_when_dead",
             "M10_tangle_threshold_setting", "P1B_perf_rebuild", "ST1_styles_textures_load", "ST2_switch_changes_textures",
             "ST3_extcord_colour_modes", "ST4_settings_roundtrip", "ST5_restore_default_and_master",
             "M8c_source_off_reads_dead_250", "M7_off_restores_vanilla", "M7b_on_again_invisible"],
    "aerial": ["M13a_linked_one_net_across_gap", "M13b_far_consumer_powered", "M13c_unlink_two_nets_relink_one",
               "M13d_refusals", "M13e_hostile_mast_not_autolinked", "R1_span_altitude_above_pawns_below_blueprints",
               "R2_spans_and_heads_drawn", "M14_gap_control_without_fix", "M14a_remove_middle_both_ends_resolve",
               "M14b_dead_pole_drops_live_and_dead_cords", "M14c_live_tip_glows", "M15_explosion_cuts_span",
               "M15b_restring_rejoins", "R3_sway_proxy", "M19_tap_drains_one_way", "M19n_taps_off_control"],
    "hose": ["H1b_install_validity", "H2_hose_laid_as_hose_cord", "H6_plump_within_transition",
             "H7_no_flicker_fast_toggle", "H8_collapse_after_release", "H9_stiffness_setting"],
    "maze": ["M1_open_maze_short_route", "M2_gap_walled_reroutes", "M3_length_cap_install",
             "M3b_laid_hose_over_cap_retracts", "M4_unreachable_retracts", "M5_walls_removed_recovers",
             "P1_reel_couples_to_tank", "P2_lone_reel_not_coupled"],
    "relay": ["RL2_one_hose_cannot_reach", "RL3_hose_onto_relay_B", "RL4_relay_B_onward_to_C", "RL5_ring_refused",
              "RL6_flow_passes_through", "RL7_no_latch", "RL8_chain_beyond_one_hose", "RL9_overhead_drawn_over_hose"],
    "carry": ["CR1_deploy_carrying", "CR2_trail_follows_walk", "CR3_draft_drops_end", "CR5_resume_laid_at_target",
              "CR5b_laid_hose_plumps", "CR5c_end_kind", "CR6_retract_stored", "CR7_no_instant_gizmos_without_devmode"],
    "style": ["S1_pick_reaches_blueprint", "S2_blueprint_frame_building", "S3_god_mode", "S4_copy_carries_look",
              "S5_reinstall_keeps_look", "S8_legacy_unstyled_draws_default", "S6_spans_in_pole_look",
              "S9a_two_runs_two_styles", "S9b_bridge_largest_wins", "S9c_split_keeps_styles",
              "S9d_restyle_and_materials", "S10_legacy_default_materials"],
    "style_hose": ["R1_pick_reaches_reel", "R2_built_reels_stored_art", "R3_laid_out_per_look", "R5_reeled_in_per_look",
                   "R6_reinstall_keeps_look", "R7_legacy_reel_default_look"],
    "session": ["D1_zero_tick_rereads_same", "D2_fresh_builder_same", "Z_log_budget"],
    "save_load": ["SL1_save_landed_new_file_only", "SL2_save_names_no_class_of_ours", "SL3_after_load_census_equal",
                  "SL4_carry_states_survive"],
}


def declared_rows():
    """Every row id a full `--live` run emits (offline, no bridge): DECLARED_ROWS plus "MX_<scene>" for each scene of
    the reduced design matrix, exactly the ids run_live.py writes."""
    import run_live as RL
    import reduced as RD
    with open(os.devnull, "w") as dn:
        so, sys.stdout = sys.stdout, dn
        try:
            spec = RD.reduce_spec(RL.load_catalog("design"))
        finally:
            sys.stdout = so
    out = list(DECLARED_ROWS["preflight"]) + ["MX_" + s["id"] for s in spec["scenes"]]
    for b, ids in DECLARED_ROWS.items():
        if b != "preflight":
            out += ids
    return out


# ============================================================================ 0. offline gate (WSL python3)
def _run(cmd, timeout=1800):
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=V.REPO)
    return r.returncode, (r.stdout or "") + (r.stderr or ""), round(time.time() - t, 1)


def offline_gate():
    """Every offline check, as {"red": [ids], "steps": {...}, "spec": path}. Runs in WSL python3."""
    red, steps = [], {}
    t = time.time()
    rows = V.run_offline()
    steps["validation_offline"] = {"rows": len(rows), "not_pass": [r["id"] for r in rows if r["status"] != "PASS"],
                                   "wall_s": round(time.time() - t, 1)}
    red += ["validation:" + i for i in steps["validation_offline"]["not_pass"]]
    rc, out, w = _run([sys.executable, os.path.join(MX_DIR, "selftest.py")])
    fails = [ln.split()[1] for ln in out.splitlines() if ln.startswith("FAIL ")]
    tail = [ln for ln in out.splitlines() if "checks passed" in ln]
    steps["matrix_selftest"] = {"exit": rc, "fail": fails, "summary": tail[-1:] , "wall_s": w}
    red += ["matrix_selftest:" + f for f in fails] + (["matrix_selftest:exit%d" % rc] if rc and not fails else [])
    rc, out, w = _run([sys.executable, os.path.join(HERE, "human_review.py"), "--plan"])
    steps["human_review_plan"] = {"exit": rc, "tail": out.strip().splitlines()[-2:], "wall_s": w}
    if rc:
        red.append("human_review:plan")
    rc, out, w = _run([sys.executable, os.path.join(HERE, "selftest_human_review.py")])
    steps["selftest_human_review"] = {"exit": rc, "tail": out.strip().splitlines()[-1:], "wall_s": w}
    if rc:
        red.append("selftest_human_review")
    os.makedirs(SCRATCH_POSIX, exist_ok=True)
    spec = os.path.join(SCRATCH_POSIX, SPEC_NAME)
    rc, out, w = _run([sys.executable, os.path.join(MX_DIR, "design_spec.py"), "--out", spec])
    steps["design_spec"] = {"exit": rc, "tail": out.strip().splitlines()[-1:], "wall_s": w}
    if rc:
        red.append("design_spec")
    return {"red": red, "steps": steps, "spec_posix": spec, "spec_win": SCRATCH_WIN + "\\" + SPEC_NAME}


def offline_gate_from_windows():
    me = V._posix(os.path.abspath(__file__))
    r = subprocess.run(["wsl.exe", "python3", me, "--offline-gate"], capture_output=True, text=True, timeout=3600)
    for ln in reversed((r.stdout or "").splitlines()):
        if ln.startswith("GATE_JSON "):
            return json.loads(ln[len("GATE_JSON "):])
    return {"red": ["gate:no GATE_JSON (exit %s): %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-300:])],
            "steps": {}}


# ============================================================================ the one bridge connection
_SOCKET = []


def _shared_socket():
    if not _SOCKET:
        sys.path.insert(0, V.UTILS)
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        s = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        s.connect()
        _SOCKET.append(s)
    return _SOCKET[0]


def _bridge_init(self):
    self.S = _shared_socket()


V.Bridge.__init__ = _bridge_init       # every script's A()/H()/Bridge() now rides the one socket
import validation_aerial as VA  # noqa: E402
import validation_hose as VH  # noqa: E402
import validation_style as VS  # noqa: E402
import validation_style_hose as VSH  # noqa: E402


class PB(VA.A, VH.H):
    """call / probe (cords) / ap (aerial) / hp (hose) / ticks on the shared socket."""


def install_no_shots():
    """--no-shots: keep each shot's camera move, drop the render + copy."""
    def v_shot(B, name, rect, log, pad=1, root=None):
        B.call("rimworld/frame_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=pad)
        log.append({"shot": name, "skipped": "--no-shots"})
        return None

    def a_shot(self, name, rect):
        self.call("rimworld/frame_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=1)
        time.sleep(0.5)
        return None

    def h_shot(self, name):
        s = VH.SHOT
        self.call("rimworld/frame_cell_rect", x=s[0], z=s[1], width=s[2], height=s[3], paddingCells=1)
        time.sleep(0.5)
        return None
    V.shot = v_shot
    VA.A.shot = a_shot
    VH.H.shot = h_shot


# ============================================================================ the session
class Proof(object):
    def __init__(self, args):
        self.args = args
        self.rows = []
        self.blocks = collections.OrderedDict()
        self.t0 = time.time()
        self.B = PB()
        self.res = {"mod": V.MOD, "script": "proof_all.py", "tier": V.TIER, "mode": "live" if not args.only else "partial",
                    "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "no_shots": bool(args.no_shots), "rows": self.rows,
                    "blocks": self.blocks, "doc": "design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md"}

    def row(self, block, rid, status, cls, detail):
        self.rows.append({"id": rid, "status": status, "class": cls, "detail": detail, "block": block})
        print("%-34s %-10s %-8s %s" % (rid, status, cls, json.dumps(detail, default=str)[:150]), flush=True)

    def want(self, name):
        # preflight is the precondition of every other block: --only never skips it (log_budget always ran too)
        if name == "determinism":
            name = "matrix"
        return not self.args.only or name in ("preflight", "log_budget") or name in self.args.only

    def checkpoint(self, final=False):
        """Write the result JSON NOW (called after every block): a late exception loses nothing. Until the run
        finishes cleanly it is marked mode "partial" + certifiable False, which `modcheck record` refuses."""
        path = getattr(self, "out_path", None)
        if not path:
            return
        res = self.res
        res["wall_s"] = round(time.time() - self.t0, 1)
        res["out"] = path
        res["site_notes"] = V.SITE_NOTES
        if not final:
            res["mode"] = "partial"
            res["certifiable"] = False
            res["incomplete"] = "run not finished (checkpoint after block %s)" % (list(self.blocks)[-1:] or ["-"])[0]
        else:
            res.pop("incomplete", None)
            res["mode"] = "live" if not (self.args.only or self.args.skip_offline) else "partial"
            res["certifiable"] = (res["mode"] == "live" and not res.get("aborted") and not res.get("run_raised")
                                  and not any(b.get("raised") for b in self.blocks.values()))
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)
            os.replace(tmp, path)
        except Exception as ex:  # noqa: BLE001
            print("CHECKPOINT WRITE FAILED: %r" % ex, flush=True)

    def block(self, name, fn):
        """Run one block; its rows are tagged; an exception is ONE harness FAIL row, never silence, and the session goes on."""
        if not self.want(name):
            return None
        try:
            return self._block(name, fn)
        finally:
            self.checkpoint()

    def _block(self, name, fn):
        t = time.time()
        n0 = len(self.rows)
        print("== %s" % name, flush=True)
        out, err = None, None
        try:
            out = fn()
        except Exception as ex:  # noqa: BLE001
            import traceback
            err = "%r" % ex
            self.row(name, "%s_block" % name.upper(), "FAIL", "HARNESS", {"raised": err, "trace": traceback.format_exc()[-1200:]})
        self.blocks[name] = {"wall_s": round(time.time() - t, 1), "rows": len(self.rows) - n0, "raised": err}
        return out

    def take(self, name, res):
        """Fold a script's result (its rows, aborted flag) into the session."""
        for r in (res or {}).get("rows") or []:
            self.rows.append(dict(r, block=name))
        if (res or {}).get("aborted"):
            self.row(name, "%s_aborted" % name.upper(), "FAIL", "HARNESS", res["aborted"])
        return res

    # ------------------------------------------------------------------ 1. preflight P1-P3
    def p1_fresh_map(self):
        B = self.B
        st, r = None, {}
        if not self.args.no_fresh_map:
            B.call("rimworld/go_to_main_menu")
            r = B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        t = time.time()
        for _ in range(480):
            st = B.call("rimworld/get_ui_state").get("programState")
            if st == "Playing" and B.call("jawa/map_info").get("success"):
                break
            time.sleep(0.5)
        mi = B.call("jawa/map_info")
        self.map_info = {k: mi.get(k) for k in ("sizeX", "sizeZ", "mapBiome", "longitude")}
        ok = st == "Playing" and mi.get("sizeX") == 250 and mi.get("sizeZ") == 250
        self.row("preflight", "P1_fresh_map", "PASS" if ok else "FAIL", "SITE",
                 {"fresh": not self.args.no_fresh_map, "start": r.get("success"), "programState": st, "map": self.map_info,
                  "wait_s": round(time.time() - t, 1)})
        if not ok:
            raise RuntimeError("no 250x250 map")

    def p2_tier_and_startup_log(self):
        B = self.B
        env = {}
        rm = B.call("jawa/running_mods", assembly="RimMandrakeGimmeSomeSlack", details=False)
        if rm.get("success"):
            env["running"] = [p.lower() for p in rm.get("packageIds") or []]
            env["running_sha256"] = hashlib.sha256("\n".join(env["running"]).encode("utf-8")).hexdigest()
            ms = (rm.get("assembly") or {}).get("matches") or []
            env["assembly_matches"] = len(ms)
            env["assembly_sha256"] = ms[0].get("sha256") if len(ms) == 1 else None
        self.res["env"] = env
        try:
            sys.path.insert(0, os.path.join(V.UTILS, "modcheck"))
            import status as _mc  # noqa: E402
            self.res["mod_hash"] = _mc.mod_hash(HERE)
        except Exception as ex:  # noqa: BLE001
            self.res["mod_hash"] = None
            self.res["mod_hash_error"] = repr(ex)
        lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
        logs0 = lg0.get("logs") or []
        self.log_base = max([x.get("Sequence", 0) for x in logs0] or [0])
        bridge_line = any("[RimBridge]" in (x.get("Message") or "") for x in logs0)
        pre = [x.get("Message", "")[:200] for x in logs0 if "GimmeSomeSlack" in (x.get("Message", "") + x.get("StackTrace", ""))
               and (x.get("Level") or "").lower() in ("error", "exception")]
        on = V.PKG in env.get("running", [])
        # the rename (2026-10-05): ONE Mod Settings entry, named for the new mod (aerial + hose fold into it)
        cats = self.B.probe("settingscats")
        one_entry = cats.get("listed") == ["RimMandrake: Gimme Some Slack"]
        st = ("PASS" if on and not pre and env.get("assembly_matches") == 1 and one_entry else "FAIL") if bridge_line else "UNMEASURED"
        self.row("preflight", "P2_tier_running_startup_log_clean", st, "MOD" if on and (pre or not one_entry) else "SITE",
                 {"running": len(env.get("running", [])), "mod_on": on, "assembly_matches": env.get("assembly_matches"),
                  "modSettingsEntries": cats.get("listed"), "modHandles": cats.get("modHandles"),
                  "startupErrorsNamingMod": pre[:6], "warnPlusEntries": len(logs0), "sanity_RimBridge_line_seen": bridge_line})

    def p3_probes_and_site(self, boards):
        import run_live as RL
        B = self.B
        pd, rc = B.probe("defaults"), B.probe("rect:0,0,1,1")
        ad, hd = B.ap("defaults"), B.hp("defaults")
        chans = {"cord": bool(pd.get("success") and rc.get("success")), "aerial": bool(ad.get("success")), "hose": bool(hd.get("success"))}
        w = B.call("jawa/weather_set", weather="Clear", lockWeather=True)
        clk = B.call("jawa/time_clock")
        lon = self.map_info.get("longitude")
        pin, hour = None, None
        if isinstance(clk.get("ticksAbs"), int) and isinstance(lon, (int, float)):
            local = (clk["ticksAbs"] + int(round(lon / 360.0 * 60000))) % 60000      # GenDate.HourOfDay (run_live LEARNED)
            hour = local // 2500
            add = (12 * 2500 - local) % 60000
            if add:
                pin = B.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add)
        B.call("jawa/incident_queue_clear")
        db = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        rx, rz, rw, rh = RL.REGION
        inside = lambda p: p and rx - 2 <= p[0] < rx + rw + 2 and rz - 2 <= p[1] < rz + rh + 2  # noqa: E731
        moved = []
        # HARNESS (run 3, 2026-10-05): a fixed park cell can be unstandable on a random map ("cell not standable"); try
        # cells along a short row near PARK until the teleport is accepted
        cand = [(PARK[0] + dx, PARK[1] + dz) for dz in (0, 2, 4, -2) for dx in range(0, 24, 2)]
        for p in (B.hp("colonists").get("pawns") or []):
            if inside(p.get("pos")):
                ok, to = False, None
                while cand and not ok:
                    to = cand.pop(0)
                    ok = bool(B.hp("pawn:%d=tp:%d,%d" % ((p["id"],) + to)).get("success"))
                moved.append((p["id"], p.get("pos"), to, ok))
        rr = "%d,%d,%d,%d" % (rx - 2, rz - 2, rw + 4, rh + 4)
        pw = B.call("jawa/list_pawns", rect=rr, limit=50)
        left = [p.get("id") or p.get("label") for p in pw.get("pawns") or []]
        pitch = RL.board_overlap_check(boards) if boards is not None else []
        ok = all(chans.values()) and w.get("success") is True and not left and not pitch
        self.row("preflight", "P3_probes_site_pinned_region_empty", "PASS" if ok else "FAIL", "HARNESS" if not all(chans.values()) else "SITE",
                 {"channels": chans, "weatherLocked": w.get("success"), "local_hour_before": hour, "pinned_noon": bool(pin and pin.get("success")),
                  "nonColonistsDestroyed": db.get("matchedCount"), "colonistsMoved": moved, "pawnsInRegion": left,
                  "boardPitch": pitch or ("%s boards, every plot pair >= GAP %d apart" % (len(boards) if boards is not None else "no", RL.GAP))})
        if not all(chans.values()):
            raise RuntimeError("a probe channel is dead: %s" % chans)

    # ------------------------------------------------------------------ 2. matrix (reduced)
    def matrix(self, spec_path):
        import run_live as RL
        B = object.__new__(RL.LiveBridge)
        B.S, B.n = _shared_socket(), 0
        a = argparse.Namespace(catalog=spec_path, scenes="full" if self.args.full_matrix else "reduced", only=None, max_boards=0,
                               progress=None, verbose=False, fresh_map=False, no_shots=self.args.no_shots, sweep_shots=None,
                               shot_settle=None, profile=False)
        spec = RL.load_catalog(spec_path)
        if a.scenes == "reduced":
            import reduced as RD
            spec = RD.reduce_spec(spec)
        scenes = spec["scenes"]
        boards = RL.make_boards(scenes)
        R = RL.Run(B, a)
        R.fresh, R.map_info, R.env, R.log_base = None, self.map_info, self.res.get("env"), self.log_base
        ap = B.ap("set:autoLink=False")              # matrix L4: no auto-link across scenes (restored by ap defaults below)
        if not ap.get("success"):
            self.row("matrix", "MX_aerial_autolink_off", "FAIL", "HARNESS", ap)
        if not self.args.no_shots:
            B.call("jawa/screenshot_mode", enabled=True)
        R.switch("boards")
        try:
            for b in boards:
                R.board(b)
            hose = [sc for sc in scenes if sc["group"] == "hose"]
            if hose:
                R.switch("hose")
                R.hose_scenes(hose)
        finally:
            R.switch("post")
            B.probe("defaults")
            B.ap("defaults")
            B.hp("defaults")
            B.call("jawa/screenshot_mode", enabled=False)
            R.finish_copies()
        for r in R.rows:
            if r["id"] == "H0_probe_channel" and r["status"] == "PASS":   # harness row folded into P3 (hose channel)
                continue
            self.rows.append(dict(r, block="matrix"))
        R.switch("done")
        self.matrix_run = R
        t = collections.Counter(s.get("status") for s in R.scenes.values())
        self.res["matrix"] = {"scenes_run": len(R.scenes), "status": dict(t), "spec_hash": spec.get("spec_hash"),
                              "reduced": spec.get("reduced"), "boards": R.boards_out, "phases_s": {k: round(v, 1) for k, v in R.tm.items()},
                              "scenes": R.scenes}

    def determinism(self):
        R = getattr(self, "matrix_run", None)
        if R is None:
            return
        det = [s.get("determinism", {}).get("same") for s in R.scenes.values() if s.get("determinism")]
        self.row("session", "D1_zero_tick_rereads_same", "PASS" if det and all(det) else "FAIL", "MOD",
                 "%d/%d scenes: geometry hash + census identical on 2 re-reads after all view toggles" % (sum(1 for d in det if d), len(det)))
        bad = ["%s %s %s" % (b["id"], b["scenes"], {k: (b.get("fresh") or {}).get(k) for k in ("edges", "different", "missing")})
               for b in R.boards_out if not b.get("fresh") or (b.get("fresh") or {}).get("different") or (b.get("fresh") or {}).get("missing")]
        rings = [b["id"] for b in R.boards_out if any("_T3_" in s for s in b["scenes"])]
        self.row("session", "D2_fresh_builder_same", "PASS" if R.boards_out and not bad else "FAIL", "MOD",
                 bad or "%d boards (ring boards %s): a fresh CordBuilder on the same map reproduces every laid edge" % (len(R.boards_out), rings))

    # ------------------------------------------------------------------ 3. the sites
    def ns(self, **kw):
        return argparse.Namespace(**dict({"save": None, "save_load": None, "removal_check": None, "fresh_map": False, "out": None}, **kw))

    def core(self):
        V._set_origin(150, 150)
        rows = []
        res = V.live_battery(V.Bridge(), fresh_map=False, rows=rows)
        self.take("core", {"rows": rows, "aborted": res.get("aborted")})
        self.res["core_ticks"] = res.get("ticks")

    # ------------------------------------------------------------------ 4. the one save
    def _hose_by(self, c, reel):
        for h in c.get("hoses") or []:
            if tuple(h["reel"]) == tuple(reel):
                return h
        return {}

    def _poll_reel(self, reel, pred, max_ticks, step=30):
        B, waited, seen = self.B, 0, []
        while True:
            h = self._hose_by(B.hp("census"), reel)
            if h.get("carry") not in seen:
                seen.append(h.get("carry"))
            if pred(h) or waited >= max_ticks:
                return h, waited, seen
            B.ticks(step)
            waited += step

    def stage_carry_for_save(self):
        """SL4 staging: reel 1 DROPPED (deploy, carry, draft mid-walk) and reel 2 CARRYING at the moment of the save."""
        B = self.B
        reel1, tgt1 = VH.CREEL, VH.CTARGET
        reel2, tgt2 = (VH.CX0 + 2, VH.CZ0 + 14), (VH.CX0 + 26, VH.CZ0 + 14)
        st = {"reel1": list(reel1), "reel2": list(reel2)}
        B.call("jawa/build_batch", ops="RM_HoseReel:%d,%d" % reel2, faction="player", wipeExisting=False)
        B.ticks(2)
        pawns = [p for p in B.hp("colonists").get("pawns") or [] if not p.get("downed")]
        st["colonists"] = len(pawns)
        if not pawns:
            return dict(st, error="no colonist")
        p1 = pawns[0]["id"]
        for p in pawns:
            if p.get("drafted"):
                B.hp("pawn:%d=undraft" % p["id"])
        B.hp("pawn:%d=tp:%d,%d" % ((p1,) + VH.CSTAND))
        B.hp("order:%d,%d=deploy:%d,%d" % (reel1 + tgt1))
        B.hp("startjob:%d,%d=forced;%d" % (reel1 + (p1,)))
        h, w, seen = self._poll_reel(reel1, lambda x: x.get("carry") == "Carrying", 600)
        B.ticks(60)
        B.hp("pawn:%d=draft" % p1)
        B.ticks(35)
        h1 = self._hose_by(B.hp("census"), reel1)
        st["reel1_staged"] = {"carry": h1.get("carry"), "seen": seen, "pawn": p1}
        if len(pawns) < 2:
            st["reel2_staged"] = {"error": "only one free colonist: the CARRYING half cannot be staged"}
            return st
        p2 = pawns[1]["id"]
        B.hp("pawn:%d=tp:%d,%d" % ((p2,) + (VH.CX0 + 5, VH.CZ0 + 14)))
        B.hp("order:%d,%d=deploy:%d,%d" % (reel2 + tgt2))
        B.hp("startjob:%d,%d=forced;%d" % (reel2 + (p2,)))
        h, w, seen = self._poll_reel(reel2, lambda x: x.get("carry") == "Carrying", 600)
        B.ticks(60)
        st["reel2_staged"] = {"carry": self._hose_by(B.hp("census"), reel2).get("carry"), "seen": seen, "pawn": p2}
        st["p1"], st["p2"] = p1, p2
        return st

    def save_load(self):
        B = self.B
        notes = {}
        # ---- staging (ticks allowed here; nothing is read for the comparison until the carry staging is done)
        c0 = B.hp("census")
        tt = c0.get("transitionTicks") or 30
        B.hp("flow:%d,%d=on" % VH.R1)                 # H10 asserted a PLUMP hose survives: hose 1 plump again
        B.ticks(tt + 5)
        ca = B.ap("census")                           # M16 asserted a CUT span and its two fallen halves survive
        apos = VA.anchors_by_pos(ca)
        if VA.M2 in apos and VA.M3 in apos and not any(l["state"] == "Cut" for a in ca.get("anchors") or [] for l in a["links"]):
            notes["aerialCut"] = B.ap("cut:%d,%d" % (apos[VA.M2]["id"], apos[VA.M3]["id"]))
            B.ticks(3)
            B.ap("poll")
        VS._cst(B)                                    # stage-2 runs processed (2 ticks)
        carry = self.stage_carry_for_save() if self.want("carry") else {"error": "carry block not run"}
        notes["carry"] = carry
        reel1, reel2 = VH.CREEL, (VH.CX0 + 2, VH.CZ0 + 14)
        carry_reels = {tuple(reel1), tuple(reel2)}
        # ---- the BEFORE read: zero ticks from here to the save
        B.call("rimworld/frame_cell_rect", x=V.SITE[0], z=V.SITE[1] - 6, width=V.SITE[2], height=V.SITE[3] + 6, paddingCells=1)
        time.sleep(1.0)
        B.probe("poll")
        cords_a = B.probe("census")
        aer_a = B.ap("census")
        sty_a = B.ap("styles")
        s9_a = B.ap("cstyles:%d,%d,%d,%d" % VS.SITE2)
        hose_a = B.hp("census")
        keys = ("carry", "far", "trailCount", "trailLast", "pending", "pendingAt")
        r1a = {k: VH._carry_view(self._hose_by(hose_a, reel1))[k] for k in keys}
        r2a = VH._carry_view(self._hose_by(hose_a, reel2))
        name = self.args.save_name or "RM_gss_proof_%s" % time.strftime("%Y%m%d%H%M%S")
        self.res["save"] = name + ".rws"
        before = V._saves_stat()
        if name + ".rws" in before:
            self.row("save_load", "SL1_save_landed_new_file_only", "FAIL", "HARNESS", "%s.rws exists" % name)
            return
        sv = B.call("rimworld/save_game", saveName=name)
        time.sleep(3.0)
        after = V._saves_stat()
        new = sorted(set(after) - set(before))
        changed = sorted(n for n in before if n in after and after[n] != before[n])
        gone = sorted(set(before) - set(after))
        ok_save = new == [name + ".rws"] and not changed and not gone
        self.row("save_load", "SL1_save_landed_new_file_only", "PASS" if ok_save else "FAIL", "HARNESS",
                 {"new": new, "changed": changed, "gone": gone, "size": after.get(name + ".rws"), "tool": sv.get("success")})
        if not ok_save:
            self.res["aborted"] = "save did not land as a new file only -- not loading"
            return
        with open(os.path.join(V.SAVES, name + ".rws"), "rb") as f:
            blob = f.read()
        # SL2 = M9a (no "GimmeSomeSlack" anywhere) U M16b (no aerial MapComponent) U H10b (no hose MapComponent / Hose class,
        # the hose's own state IS saved) + the legacy namespace (the rename: nothing may still be written as MessyConduit) + R4's
        # half (every hose-reel look's style def is in the save).
        hits = {k: blob.count(k.encode()) for k in ("GimmeSomeSlack", "RM_MapComponent_Aerial", "RM_MapComponent_Hoses",
                                                    "RM_MapComponent_CordGraph", "MessyConduit", "rmHoseState")}
        styles = {l: blob.count(("RM_HoseReel_%s" % l).encode()) for l in VSH.LOOKS}
        # A pawn CARRYING a hose at save time has his job deep-saved by vanilla, driver class included: hose_carry_design
        # 2026-10-04 section 11 ("the pawn's job is deep-saved by vanilla and resumes at its toil index"; mod removal: "Accepted,
        # same class as M9"). Those hits are counted apart and capped at the pawns the staging left carrying (SL4); every other
        # occurrence of our namespace is a fault (found live 2026-10-05: RM_MapComponent_ConduitRuns written as a map component).
        expected, offending = 0, []
        for i in V._find_all(blob, b"GimmeSomeSlack"):
            if blob[max(0, i - 40):i].endswith(b'<curDriver Class="RimMandrake.') and blob[i:i + 30].startswith(b"GimmeSomeSlack.Hose.Jobs."):
                expected += 1
            else:
                offending.append(blob[max(0, i - 120):i + 60].decode("utf-8", "replace").strip()[-160:])
        carrying = 1 if (carry.get("reel2_staged") or {}).get("carry") == "Carrying" else 0
        hits["GimmeSomeSlack"] = len(offending)
        hits["carryJobDriver(expected)"] = expected
        ctx = offending[:3]
        sl2 = all(hits[k] == 0 for k in hits if k not in ("rmHoseState", "carryJobDriver(expected)")) and expected <= carrying \
            and hits["rmHoseState"] >= 1 and all(v >= 1 for v in styles.values())
        self.row("save_load", "SL2_save_names_no_class_of_ours", "PASS" if sl2 else "FAIL", "MOD",
                 {"counts": hits, "hoseReelStylesInSave": styles, "first": ctx})
        ld = B.call("rimworld/load_game", saveName=name)
        ok, waited = V._wait_playing(B)
        if not ok:
            self.row("save_load", "SL3_after_load_census_equal", "FAIL", "SITE", {"load": ld.get("success"), "state": waited})
            return
        # ---- AFTER: hoses first, before any tick (a carried reel moves with every tick)
        B.call("rimworld/frame_cell_rect", x=VH.CSITE[0], z=VH.CSITE[1], width=VH.CSITE[2], height=VH.CSITE[3], paddingCells=1)
        time.sleep(1.0)
        hose_b = B.hp("census")
        r1b = {k: VH._carry_view(self._hose_by(hose_b, reel1))[k] for k in keys}
        r2b = VH._carry_view(self._hose_by(hose_b, reel2))
        t_poll = time.time()
        while len(hose_b.get("hoses") or []) < len(hose_a.get("hoses") or []) and time.time() - t_poll < 12.0:
            B.ticks(10)
            time.sleep(1.0)
            hose_b = B.hp("census")
        cords_b = V._frame_poll_census(B)
        aer_b = B.ap("census")
        t_poll = time.time()
        while len(aer_b.get("anchors") or []) < len(aer_a.get("anchors") or []) and time.time() - t_poll < 12.0:
            B.ticks(10)
            time.sleep(1.0)
            aer_b = B.ap("census")
        sty_b = B.ap("styles")
        s9_b = B.ap("cstyles:%d,%d,%d,%d" % VS.SITE2)
        t_poll = time.time()
        while len(s9_b.get("members") or []) < len(s9_a.get("members") or []) and time.time() - t_poll < 12.0:
            B.ticks(10)
            time.sleep(1.0)
            s9_b = B.ap("cstyles:%d,%d,%d,%d" % VS.SITE2)
            sty_b = B.ap("styles")

        def no_carry(c):
            return dict(c, hoses=[h for h in c.get("hoses") or [] if tuple(h["reel"]) not in carry_reels])
        parts = {
            "cords(M4)": (V._cord_set(cords_a), V._cord_set(cords_b)),
            "aerial(M16)": (VA._aerial_set(aer_a), VA._aerial_set(aer_b)),
            "hoses(H10)": (VH._hose_set(no_carry(hose_a)), VH._hose_set(no_carry(hose_b))),
            "mastStyles(S7)": (VS._snapshot(sty_a), VS._snapshot(sty_b)),
            "runStyles(S9e)": (VS._s9_snap(s9_a), VS._s9_snap(s9_b)),
            "reelStyles(R4)": (VSH._snapshot(no_carry(hose_a)), VSH._snapshot(no_carry(hose_b))),
        }
        empty = [k for k, (a, b) in parts.items() if not a or (isinstance(a, tuple) and not a[0]) or
                 (isinstance(a, dict) and not a.get("edgeHashes") and k.startswith("cords"))]
        differ = {}
        for k, (a, b) in parts.items():
            if a != b:
                if isinstance(a, dict):
                    differ[k] = sorted(x for x in a if a[x] != b.get(x))
                elif isinstance(a, tuple):
                    differ[k] = {"missing": [x for x in a[0] if x not in b[0]][:4], "extra": [x for x in b[0] if x not in a[0]][:4]}
                else:
                    differ[k] = {"missing": [x for x in a if x not in b][:4], "extra": [x for x in b if x not in a][:4]}
        plump = any(s[3] == "Plump" for s in parts["hoses(H10)"][0])
        sl3 = not differ and not empty and plump and bool(parts["aerial(M16)"][0]["fallen"])
        self.row("save_load", "SL3_after_load_census_equal", "PASS" if sl3 else "FAIL", "MOD",
                 {"differs": differ, "emptyBefore": empty, "plumpHoseInSave": plump, "loadSeconds": waited,
                  "sizes": {"edges": len(parts["cords(M4)"][0].get("edgeHashes") or {}), "geometryHash": [parts["cords(M4)"][0].get("geometryHash"), parts["cords(M4)"][1].get("geometryHash")],
                            "aerialLinks": len(parts["aerial(M16)"][0]["links"]), "aerialFallen": len(parts["aerial(M16)"][0]["fallen"]),
                            "hoses": len(parts["hoses(H10)"][0]), "masts": len(parts["mastStyles(S7)"][0]), "runCells": len(parts["runStyles(S9e)"][0][0])},
                  "spawned": cords_b.get("spawnedConduitTexture")})
        # ---- SL4: carried-hose states (pawn job/driver state, not geometry)
        good1 = r1a.get("carry") == "Dropped" and r1a == r1b
        good2 = r2a.get("carry") == "Carrying" and r2b.get("carry") in ("Carrying", "Dropped") and (r2b.get("trailCount") or 0) > 0 \
            and r2b.get("pending") == "Deploy"
        laid = {}
        if good2 and carry.get("p2"):
            if r2b.get("carry") == "Dropped":
                B.hp("startjob:%d,%d=work;%d" % (reel2 + (carry["p2"],)))
            h, w, seen = self._poll_reel(reel2, lambda x: x.get("carry") == "Laid", 1200)
            laid = {"carry": h.get("carry"), "far": h.get("far"), "pending": h.get("pending"), "ticks": w, "seen": seen}
        good3 = laid.get("carry") == "Laid" and tuple(laid.get("far") or ()) == (VH.CX0 + 26, VH.CZ0 + 14)
        st = "PASS" if good1 and good2 and good3 else ("UNMEASURED" if carry.get("error") or (carry.get("reel2_staged") or {}).get("error") else "FAIL")
        self.row("save_load", "SL4_carry_states_survive", st, "MOD",
                 {"dropped(CR4a)": {"before": r1a, "after": r1b}, "carrying(CR4b)": {"before": r2a, "after": r2b},
                  "resumedAfterLoad(CR5)": laid, "staging": carry})
        if carry.get("p1"):
            B.hp("pawn:%d=undraft" % carry["p1"])
        self.res["save_load_notes"] = notes

    # ------------------------------------------------------------------ 5. Z
    def log_budget(self):
        lg = self.B.call("rimbridge/list_logs", limit=1000, minimumLevel="warning")
        new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > self.log_base]
        errs = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
        # the sites' own clears over a geyser/monolith ("Tried to destroy non-destroyable thing") and a donor mod's
        # map-creation NRE (ReGrowthCore Map_FinalizeInit) are the harness/site, never charged to the mod (run_live LEARNED)
        site = [e for e in errs if "non-destroyable" in str(e.get("Message", ""))]
        donor = [e for e in errs if "Map_FinalizeInit" in str(e.get("Message", "")) and "GimmeSomeSlack" not in str(e.get("Message", ""))]
        errs = [e for e in errs if e not in site and e not in donor]
        self.row("session", "Z_log_budget", "PASS" if not errs else "FAIL", "MOD",
                 {"errors": [str(e.get("Message", ""))[:240] for e in errs[:10]], "newWarnings": len(new),
                  "siteClearErrorsExcluded": len(site), "donorMapInitErrorsExcluded": len(donor), "sinceSequence": self.log_base,
                  "readBack": len(lg.get("logs") or [])})

    def restore(self):
        B = self.B
        for f in (lambda: B.probe("defaults"), lambda: B.ap("defaults"), lambda: B.hp("defaults"),
                  lambda: B.call("jawa/weather_set", weather="Clear", unlock=True), lambda: B.call("jawa/screenshot_mode", enabled=False)):
            try:
                f()
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------ run
    def run(self, gate):
        a = self.args
        self.res["offline"] = gate
        spec = a.spec or (gate or {}).get("spec_win") or (SCRATCH_WIN + "\\" + SPEC_NAME)
        boards = None
        if self.want("matrix"):
            import run_live as RL
            sp = RL.load_catalog(spec)
            if not a.full_matrix:
                import reduced as RD
                sp = RD.reduce_spec(sp)
            boards = RL.make_boards(sp["scenes"])
        self.block("preflight", lambda: (self.p1_fresh_map(), self.p2_tier_and_startup_log(), self.p3_probes_and_site(boards)))
        if any(r["status"] != "PASS" for r in self.rows if r.get("block") == "preflight"):
            self.res["aborted"] = "preflight not green"
            return
        self.block("matrix", lambda: self.matrix(spec))
        self.block("core", self.core)
        self.block("aerial", lambda: self.take("aerial", VA.run_live(self.ns())))
        self.block("hose", lambda: self.take("hose", VH.run_live(self.ns())))
        self.block("maze", lambda: self.take("maze", VH.run_maze(self.ns())))
        self.block("relay", lambda: self.take("relay", VH.run_relay(self.ns())))
        self.block("carry", lambda: self.take("carry", VH.run_carry(self.ns())))
        self.block("style", lambda: self.take("style", VS.run_live(self.ns())))
        self.block("style_hose", lambda: self.take("style_hose", VSH.run_live(self.ns())))
        if self.want("matrix"):
            self.block("determinism", self.determinism)
        self.block("save_load", self.save_load)
        self.block("log_budget", self.log_budget)


def summary(res):
    t = collections.Counter(r["status"] for r in res["rows"])
    print("\n" + "=" * 100)
    print("proof_all %s  %s  rows %d %s  wall %ss  shots %s" % (res["mode"], res.get("started"), len(res["rows"]), dict(t),
                                                               res.get("wall_s"), "off" if res.get("no_shots") else "on"))
    for name, b in res["blocks"].items():
        bt = collections.Counter(r["status"] for r in res["rows"] if r.get("block") == name)
        print("  %-11s %6.1fs  %s%s" % (name, b["wall_s"], dict(bt), ("  RAISED " + b["raised"][:60]) if b.get("raised") else ""))
    bad = [r for r in res["rows"] if r["status"] not in ("PASS",)]
    for r in bad[:25]:
        print("  NOT PASS  %-34s %-10s %s" % (r["id"], r["status"], json.dumps(r["detail"], default=str)[:120]))
    if res.get("aborted"):
        print("  ABORTED: %s" % res["aborted"])
    print("  -> %s" % res.get("out"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline-gate", action="store_true", help="(WSL) run the offline tier and print GATE_JSON")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--no-shots", action="store_true", help="state only: no screenshot renders (camera moves kept)")
    ap.add_argument("--only", default=None, help="comma list of blocks (%s): a PARTIAL run, for debugging" % ",".join(BLOCKS))
    ap.add_argument("--no-fresh-map", action="store_true", help="use the current map (debug)")
    ap.add_argument("--skip-offline", action="store_true", help="do not run the offline gate (recorded; debug only)")
    ap.add_argument("--allow-red", action="append", default=[], help="an offline red id to accept (recorded in the result)")
    ap.add_argument("--spec", default=None, help="design spec JSON (default: the one the offline gate writes)")
    ap.add_argument("--full-matrix", action="store_true", help="the full 109-scene matrix instead of the reduced 39")
    ap.add_argument("--save-name", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.offline_gate:
        g = offline_gate()
        print("GATE_JSON " + json.dumps(g, default=str))
        return 1 if g["red"] else 0
    if not a.live:
        ap.print_help()
        return 2
    a.only = [x.strip() for x in a.only.split(",")] if a.only else None
    gate = None
    if not a.skip_offline:
        t = time.time()
        gate = offline_gate_from_windows()
        gate["wall_s"] = round(time.time() - t, 1)
        unaccepted = [r for r in gate["red"] if not any(r == x or r.endswith(":" + x) for x in a.allow_red)]
        gate["accepted_red"] = [r for r in gate["red"] if r not in unaccepted]
        print("offline gate: %d red %s, accepted %s (%ss)" % (len(gate["red"]), unaccepted, gate["accepted_red"], gate["wall_s"]), flush=True)
        if unaccepted:
            print("REFUSED: offline red -- not going live")
            return 1
    V.SHARED = True
    if a.no_shots:
        install_no_shots()
    P = Proof(a)
    if a.skip_offline:
        P.res["offline"] = {"skipped": "--skip-offline"}
        P.res["mode"] = "partial"
    out = a.out or os.path.join(OUT_DIR, "proof_all_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    P.out_path = out
    try:
        P.run(gate)
    except BaseException as ex:  # noqa: BLE001
        P.res["run_raised"] = repr(ex)
        raise
    finally:
        P.restore()
        P.checkpoint(final=True)
    summary(P.res)
    bad = [r for r in P.res["rows"] if r["status"] in ("FAIL", "UNMEASURED")]
    return 1 if bad or P.res.get("aborted") else 0


if __name__ == "__main__":
    sys.exit(main())
