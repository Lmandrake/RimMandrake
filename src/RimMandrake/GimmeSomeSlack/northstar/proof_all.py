"""proof_all.py -- Gimme Some Slack: the ONE live proof (owner densification, 2026-10-05).

Design: design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md (section 6 is this file's spec,
section 2 the cut-by-cut reasoning, section 3 the row table). Owner, typed: "reduce the number of north Star
verifications and verification stations for the human review sheet as well. If so, remove them. Then run them;
and finally handoff." and "Yes you should examine the hash bound ones too. This is a full densification."

    python3    src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --offline-gate        # WSL: the offline tier only (seconds)
    python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live [--no-shots]   # gimmesomeslack tier, bridge held
    python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --only core,aerial --no-fresh-map   # debug a block
    python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --fresh-map    # the old path: a new quicktest map

THE MAP (TESTSITE_SAVES_BUILD_ONE_CALM_MAP, owner by card 2026-10-15: "Clean saved maps"): by default P1 LOADS the clean
saved site `calm` (Utils/modcheck/test_site_saves.py: cleaned once -- no shrine, casket, trigger, hive, ruin, fog or
hostile -- and read back clean after every load) instead of generating a quicktest map. --fresh-map generates one as
before; --no-fresh-map uses whatever map is current; --site-save NAME picks another registered site.

Run python.exe from the repo root (bridge calls only work under python.exe; pipe through tr -d '\\r').

ORDER (section 6; one map -- the clean saved site by default -- one calm-world setup, the census save + load, then S12d's own save + load):
  0. offline gate, run in WSL python3 (numpy, the C# SelfTest): validation.py O1-O8 (O3 = C# SelfTest vs the Python
     oracle + its --probe mutation + the DeterminismChecks floor replay), northstar_matrix/selftest.py,
     human_review.py --plan, selftest_human_review.py, and the design spec JSON for the matrix. Any red refuses to go
     live, except an id named with --allow-red (recorded in the result).
  1. P1 the map (250x250: the loaded site save, or --fresh-map)  P2 tier running + startup log clean  P2c control noise (on a map already swept: calm_map)
     P3 probe channels (cord/aerial) + site pinned (weather Clear locked, calm_map again: fog triggers disarmed, hostile
     buildings and non-colonists destroyed, the whole map unfogged, then re-swept for what the unfog released; noon,
     incident queue cleared, colonists moved out of
     the matrix REGION) + no pawn in REGION + matrix board pitch. These replace every script's own harness rows (L0-L6, O0, I0,
     H0, S0, A0, H1, RL1, CR0, P1B_plot_built): in this session such a row is written only if it is NOT PASS.
  2. matrix, reduced (30 scenes, northstar_matrix/reduced.py) FIRST: it clears map-wide and tears every board down.
  3. core (validation.live_battery) -> aerial -> style, each on its own site (disjoint from each other). The hose blocks
     (hose, maze, relay, carry, style-hose, the nine hose matrix scenes, SL4) moved with the hose to FlowWorks at the hose
     port (2026-10-11): FlowWorks/northstar/proof_hose.py.
  4. D1/D2 (matrix determinism: zero-tick re-reads; a fresh CordBuilder == the incremental one, guard for the ring-board
     defect of 2026-10-02), then the ONE save: SL1 only the new .rws appeared; SL2 the save names no class of ours
     (guard: the MapComponent written into saves, 2026-10-02); SL3 after the load every subsystem's census equals the
     one before (guard: no cords on ANY loaded save, the MapDrawer NRE of 2026-10-02).
  4b. S12d (D4): a SECOND save written by csavenow with a member still pending, reloaded, read against a control --
     after SL3, so its staging cannot touch SL1-SL3's sets (d4_save; 2026-10-22).
  5. Z: one log budget over the whole session (startup excluded, the load included).
  Not here: the removal check (walk E1, paused by the owner) -- `validation.py --removal-check <the SL save>` after one
  cold load onto `modset_builder.py --tier flowworks`. And not a proof: `human_review.py --build --fresh-map`.

--no-shots: no screenshot is rendered anywhere; every camera move the shots made is kept (frame_cell_rect), because the
cord graph rebuilds off camera-driven section regeneration (northstar_matrix/run_live.py LEARNED 2026-10-04).

Output: ONE result JSON northstar/proof_all_<stamp>.json (mode "live" for a full run; "partial" with --only, which
`modcheck record` refuses) and a one-screen summary.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
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

SCRATCH_WIN = rm_win("scratch", "gss_proof")
SCRATCH_POSIX = rm_str("scratch", "gss_proof")
SPEC_NAME = "scenes_design.json"
BLOCKS = ["matrix", "core", "aerial", "style", "save_load", "d4_save"]   # hose/maze/relay/carry/style_hose moved to FlowWorks/northstar/proof_hose.py (hose port)
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
             "B4b_sparks_thrown_ticking", "B4c_spark_intensity_scales_downed", "B4d_spark_budget_shared_visible_first", "B7_sway_cpu_two_frame", "B7b_sway_shader_path", "B7c_floor_ripple",
             "B5_selection_highlight", "B8_lod_far_zoom", "B9_cutscene_guard_idle", "B6b_strips_dark_when_dead",
             "M10_tangle_threshold_setting", "M11_dive_through_setting", "P1B_perf_rebuild", "ST1_styles_textures_load", "ST2_switch_changes_textures",
             "ST3_extcord_colour_modes", "ST4_settings_roundtrip", "ST5_restore_default_and_master",
             "M8c_source_off_reads_dead_250", "M7_off_restores_vanilla", "M7b_on_again_invisible"],
    "aerial": ["M13a_linked_one_net_across_gap", "M13b_far_consumer_powered", "M13c_unlink_two_nets_relink_one",
               "M13d_refusals", "M13e_hostile_mast_not_autolinked", "R1_span_altitude_above_pawns_below_blueprints",
               "R2_spans_and_heads_drawn", "M14_gap_control_without_fix", "M14a_remove_middle_both_ends_resolve",
               "M14b_dead_pole_drops_live_and_dead_cords", "M14c_live_tip_glows", "M15_explosion_cuts_span",
               "M15a_wire_down_alert_lists_cut", "M15b_restring_rejoins", "M15c_wire_down_alert_clears_on_restring", "M15e_restring_is_a_colonist_job", "R3_sway_proxy", "M19_tap_drains_one_way", "M19n_taps_off_control",
               "M20a_fallen_wire_shock_flip", "M20b_fallen_wire_knockback_flip", "M20c_fallen_wire_ignites_flip", "M20d_keep_wires_setting_roundtrip"],
    "style": ["S1_pick_reaches_blueprint", "S2_blueprint_frame_building", "S3_god_mode", "S4_copy_carries_look",
              "S5_reinstall_keeps_look", "S8_legacy_unstyled_draws_default", "S6_spans_in_pole_look",
              "S9a_two_runs_two_styles", "S9b_bridge_largest_wins", "S9c_split_keeps_styles",
              "S9d_restyle_and_materials", "S10_legacy_default_materials", "S11_lamp_master_off_vanilla", "S12a_D1_legacy_run_one_look", "S12b_D7_bulk_spawn_cost"],
    "session": ["D1_zero_tick_rereads_same", "D2_fresh_builder_same", "Z_log_budget"],
    "save_load": ["SL1_save_landed_new_file_only", "SL2_save_names_no_class_of_ours", "SL3_after_load_census_equal",
                  "S12d_D4_pending_queue_save"],
}


_REF = re.compile(r"\[Ref ([0-9A-F]{8})\]")


def _err_text(e):
    return str(e.get("Message", "")) + "\n" + str(e.get("StackTrace", ""))


def _norm_err(e):
    """An error's identity across sessions: its message with every digit run collapsed (thing ids, ticks, counts)."""
    return re.sub(r"\d+", "#", str(e.get("Message", "")).split("\n[Ref ")[0].strip())[:400]


_REF_CACHE = {}


def _err_key(e):
    return (_norm_err(e), _thrower(e))


def _thrower(e):
    """The first stack frame of an error, resolving BetterStackTraces' "[Ref X] Duplicate stacktrace" against the original
    in Player.log (the bridge log keeps only the duplicate). '?' when no frame is known."""
    txt = _err_text(e)
    m = _REF.search(txt)
    if m and "Duplicate stacktrace" in txt:
        ref = m.group(1)
        if ref not in _REF_CACHE:
            _REF_CACHE[ref] = ""
            try:
                with open(V.PLAYER_LOG, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.read().splitlines()
                for i, ln in enumerate(lines):
                    if ln.strip() == "[Ref %s]" % ref:
                        _REF_CACHE[ref] = "\n".join(lines[i + 1:i + 4])
                        break
            except OSError:
                pass
        txt += "\n" + _REF_CACHE[ref]
    for ln in txt.splitlines():
        ln = ln.strip()
        if ln.startswith("at "):
            return ln[3:].split(" [0x")[0][:160]
    return "?"


_VANILLA_NS = ("Verse.", "RimWorld.", "System.", "UnityEngine.", "Unity.", "Mono.", "LudeonTK.", "(wrapper", "RimMandrake.GimmeSomeSlack")
_SOURCE = re.compile(r"\[Source: ([^\]]+)\]")


def _foreign_source(e):
    """The other mod an error's own text names as its source, or None: its first stack frame's namespace when that is not
    vanilla/system/GSS, else a DefDatabase error's "[Source: <mod name>]"."""
    t = _thrower(e)
    if t != "?" and not t.startswith(_VANILLA_NS):
        return t.split("(")[0].rsplit(".", 1)[0]
    m = _SOURCE.search(str(e.get("Message", "")))
    if m and "Gimme Some Slack" not in m.group(1):
        return "[Source: %s]" % m.group(1)
    return None


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


def _VC():
    """Utils/validation_core (log_alive / log_revive); this file's V is Gimme Some Slack's validation.py."""
    if V.UTILS not in sys.path:
        sys.path.append(V.UTILS)
    import validation_core  # noqa: E402
    return validation_core


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
        if V.UTILS not in sys.path:
            sys.path.append(V.UTILS)   # append: Utils/scenes (a package) must not shadow northstar_matrix/scenes.py
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
import validation_style as VS  # noqa: E402



def _no_hose(scenes):
    """The hose scenes (group "hose", H00-H08) moved to FlowWorks with the hose port; FlowWorks' proof_hose.py runs
    them. A GSS run never places them, even with --full-matrix (the GSS tier has no HoseProbe)."""
    return [s for s in scenes if s.get("group") != "hose"]


def _QS():
    """The shared quiet isolated test-site profile (Utils/modcheck/quiet_site.py)."""
    d = os.path.join(V.UTILS, "modcheck")
    if d not in sys.path:
        sys.path.append(d)
    import quiet_site
    return quiet_site


def _TSS():
    """The clean saved test sites (Utils/modcheck/test_site_saves.py)."""
    d = os.path.join(V.UTILS, "modcheck")
    if d not in sys.path:
        sys.path.append(d)
    import test_site_saves
    return test_site_saves


def _TG():
    """The shared test-environment guards (Utils/modcheck/testenv_guards.py): fog-trigger disarm, whole-map unfog."""
    d = os.path.join(V.UTILS, "modcheck")
    if d not in sys.path:
        sys.path.append(d)
    import testenv_guards
    return testenv_guards


class PB(VA.A):
    """call / probe (cords) / ap (aerial) / ticks on the shared socket. (The hose's hp channel moved to FlowWorks.)"""


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

    V.shot = v_shot
    VA.A.shot = a_shot


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
        if name not in ("preflight", "log_budget"):
            # 2026-10-10 (550-mod list): wild animals keep spawning after P3's sweep; a predator stabbed two colonists down
            # mid-session (CR6's carrier dropped the hose, SL's hose staging failed). Every block starts on a calm map.
            try:
                calm = self.B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
                self.blocks_calm = getattr(self, "blocks_calm", {})
                self.blocks_calm[name] = calm.get("matchedCount")
                # 2026-10-11 (full list, RM_TheRot map): a giant plant outside a site re-plans its trunk blockers into the
                # cleared site (validation_core.clear_huge_plants); the style site read UNMEASURED and the block aborted
                self.res.setdefault("huge_plants_cleared", {})[name] = _VC().clear_huge_plants(self.B)
            except Exception as ex:  # noqa: BLE001
                # a block that ran on an un-calmed map must say so (as FlowWorks' proof_hose does): recorded, not swallowed
                self.res.setdefault("site_calm_errors", {})[name] = repr(ex)
        try:
            out = fn()
        except Exception as ex:  # noqa: BLE001
            import traceback
            err = "%r" % ex
            self.row(name, "%s_block" % name.upper(), "FAIL", "HARNESS", {"raised": err, "trace": traceback.format_exc()[-1200:]})
        if _VC().TAP:
            try:
                _VC().TAP[0].poll()
            except Exception:  # noqa: BLE001
                pass
        self.blocks[name] = {"wall_s": round(time.time() - t, 1), "rows": len(self.rows) - n0, "raised": err,
                             "nonColonistsDestroyedFirst": getattr(self, "blocks_calm", {}).get(name)}
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
        st, r, site = None, {}, None
        mode = getattr(self.args, "map_mode", None) or ("current" if self.args.no_fresh_map else "fresh")
        if mode == "save":
            site = _TSS().load_site(B.call, getattr(self.args, "site_save", None) or "calm")
            self.res["site_save"] = site
            r = {"success": site.get("verified")}
        elif mode == "fresh":
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
        ok = st == "Playing" and mi.get("sizeX") == 250 and mi.get("sizeZ") == 250 and (site is None or site.get("verified") is True)
        self.row("preflight", "P1_fresh_map", "PASS" if ok else "FAIL", "SITE",
                 {"fresh": mode == "fresh", "mapMode": mode, "start": r.get("success"), "programState": st, "map": self.map_info,
                  "wait_s": round(time.time() - t, 1),
                  "siteSave": None if site is None else {k: site.get(k) for k in ("save", "load_s", "ready_s", "verified", "problems")}})
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
        self.res["log_revive"] = _VC().log_revive(B)    # Z is blind once Verse.Log hit its 10,000-message cap
        lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
        logs0 = lg0.get("logs") or []
        self.log_base = max([x.get("Sequence", 0) for x in logs0] or [0])
        _VC().tap_start(B)                           # the journal is a 1,000-entry ring: keep warn+ as they pass
        bridge_line = any("[RimBridge]" in (x.get("Message") or "") for x in logs0)
        pre = [x.get("Message", "")[:200] for x in logs0 if "GimmeSomeSlack" in (x.get("Message", "") + x.get("StackTrace", ""))
               and (x.get("Level") or "").lower() in ("error", "exception")]
        log_src = "bridge"
        if not bridge_line:
            # 2026-10-10 (550-mod list): chatty mods push the startup out of the bridge's last 500 warning+ entries within
            # minutes, so the [RimBridge] sanity line was never seen and P2 read UNMEASURED. Player.log holds the whole
            # session from startup; read the startup there (to the first map), same two questions.
            try:
                with open(V.PLAYER_LOG, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.read().splitlines()
                bridge_line = any("[RimBridge]" in ln for ln in lines)
                pre = [ln[:200] for ln in lines if "GimmeSomeSlack" in ln and ("Exception" in ln or "rror" in ln)][:6]
                log_src = "Player.log"
            except OSError:
                pass
        on = V.PKG in env.get("running", [])
        # the rename (2026-10-05): ONE Mod Settings entry, named for the new mod (aerial folds into it)
        cats = self.B.probe("settingscats")
        one_entry = cats.get("listed") == ["RimMandrake: Gimme Some Slack"]
        st = ("PASS" if on and not pre and env.get("assembly_matches") == 1 and one_entry else "FAIL") if bridge_line else "UNMEASURED"
        self.row("preflight", "P2_tier_running_startup_log_clean", st, "MOD" if on and (pre or not one_entry) else "SITE",
                 {"running": len(env.get("running", [])), "mod_on": on, "assembly_matches": env.get("assembly_matches"),
                  "modSettingsEntries": cats.get("listed"), "modHandles": cats.get("modHandles"),
                  "startupErrorsNamingMod": pre[:6], "warnPlusEntries": len(logs0), "sanity_RimBridge_line_seen": bridge_line,
                  "startupLogSource": log_src})

    def calm_map(self):
        """The map-wide sweep, run BEFORE the clock first moves (p2c's control advance) and again in P3:
        TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL (r5 2026-10-15): a fog reveal woke an ancient-danger room -- a ThreatBig
        "Area revealed" letter 2 ticks after the noon pin, then a hostile militor (run 1) and a Lancer + 2 HullBolts (run 3)
        downed a colonist in the aerial block. So: disarm every fog/proximity trigger and signal action (TriggerUnfogged ->
        SignalAction_Ambush/DormancyWakeUp), take the hostile structures down FIRST (a destroyed container can leave a pawn
        behind), THEN vanish every non-colonist pawn -- fogged sleepers included, since vanilla FloodUnfog wakes any pawn it
        uncovers.
        r6 map 3 (2026-10-15): all of that read back clean and an "Area revealed" ThreatBig still came 32 ticks after the
        pin, with 3 mechs (map-gen ids, never in the spawned set at P3) arriving inside the matrix block. The only 1.6 path
        that letters mid-run is Building.DeSpawn -> FogGrid.Notify_FogBlockerRemoved -> FloodUnfogAdjacent: a site clear
        (destroy_batch All) removed rock beside a fogged pocket. So the LAST step unfogs the whole map (testenv_guards.
        clear_map_fog, refused while a hostile is listed): with no fog left, no later clear can flood, letter or wake.
        TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG (r7 2026-10-15): that unfog itself released 2-5 fleshbeasts (or a mech
        group) on 4 of 5 fresh maps, after its own hostile check read 0, so p2c's advance stopped at arm. clear_map_fog now
        sweeps again after the unfog until the hostile listing is empty (mapFog.releasedByUnfog records what it took);
        a map that keeps releasing is not calm (P2c / P3 FAIL SITE).
        TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM (r6 attempts 1b/1c/3a): p2c's 600-tick control advance ran before this
        sweep, so a map-gen Megaspider or a dormant hive stopped it and aborted the preflight; p2c now calls this first."""
        B, G = self.B, _TG()
        disarm = G.disarm_fog_triggers(B)
        # 2026-10-10 (550-mod list): map-gen hostile structures keep the world uncalm too -- a BetterInfestations hive
        # (BI_Hive, faction Insect) threw "Exception ticking BI_Hive" (CompSpawnerPawns.CompTick NRE) into Z mid-session.
        # Every building of a non-player faction goes, like the non-colonist pawns below.
        hostile = [t for t in (B.call("jawa/list_things", group="BuildingArtificial", limit=5000).get("things") or [])
                   if t.get("faction") and not str(t.get("faction")).startswith("Player") and t.get("x") is not None]
        for t in hostile:
            B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t["x"], t["z"]), categories="Building")
        db = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        fog = G.clear_map_fog(B)
        return {"fogTriggersDisarmed": disarm, "hostileBuildings": hostile, "destroyBulk": db, "mapFog": fog,
                "calm": disarm.get("verified") is True and fog.get("verified") is True}

    def p3_probes_and_site(self, boards):
        import run_live as RL
        B = self.B
        pd, rc = B.probe("defaults"), B.probe("rect:0,0,1,1")
        ad = B.ap("defaults")
        chans = {"cord": bool(pd.get("success") and rc.get("success")), "aerial": bool(ad.get("success"))}
        w = B.call("jawa/weather_set", weather="Clear", lockWeather=True)
        sweep = self.calm_map()
        disarm, hostile, db, fog = sweep["fogTriggersDisarmed"], sweep["hostileBuildings"], sweep["destroyBulk"], sweep["mapFog"]
        clk = B.call("jawa/time_clock")
        lon = self.map_info.get("longitude")
        pin, hour = None, None
        if isinstance(clk.get("ticksAbs"), int) and isinstance(lon, (int, float)):
            local = (clk["ticksAbs"] + int(round(lon / 360.0 * 60000))) % 60000      # GenDate.HourOfDay (run_live LEARNED)
            hour = local // 2500
            add = (12 * 2500 - local) % 60000
            if add:
                # timeException=True: noon pin for light; nothing simulated (safe-advance gate)
                pin = B.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add, timeException=True)
        B.call("jawa/incident_queue_clear")
        # the shared quiet isolated profile on top (storyteller off read back, proximity letters, queue drain, modal
        # broker): TESTENV_MONOLITH_HARDEN_UNINVITED_GUEST arrived on these maps with only the queue cleared
        self.res["quiet_site"] = _QS().site_profile_receipt(B, "gss_proof_all")
        disarm_after = _TG().disarm_fog_triggers(B)
        hp = B.call("jawa/list_pawns", faction="hostile", limit=200)
        hostiles_left = [p.get("id") for p in hp.get("pawns") or [] if not p.get("dead")] if hp.get("success") else None
        armed_clean = (disarm.get("error") is None and disarm_after.get("verified") is True and hostiles_left == []
                       and fog.get("verified") is True)
        rx, rz, rw, rh = RL.REGION
        inside = lambda p: p and rx - 2 <= p[0] < rx + rw + 2 and rz - 2 <= p[1] < rz + rh + 2  # noqa: E731
        moved = []
        # HARNESS (run 3, 2026-10-05): a fixed park cell can be unstandable on a random map ("cell not standable"); try
        # cells along a short row near PARK until the teleport is accepted
        cand = [(PARK[0] + dx, PARK[1] + dz) for dz in (0, 2, 4, -2) for dx in range(0, 24, 2)]
        for p in (B.probe("colonists").get("pawns") or []):
            if inside(p.get("pos")):
                ok, to = False, None
                while cand and not ok:
                    to = cand.pop(0)
                    ok = bool(B.probe("pawn:%d=tp:%d,%d" % ((p["id"],) + to)).get("success"))
                moved.append((p["id"], p.get("pos"), to, ok))
        # 2026-10-10 (audit, 550-mod list): idle colonists wander -- fast, on that list -- into sites during the long tick
        # windows; all are drafted here (validation.reveal restores the state it found).
        drafted = [p["id"] for p in (B.probe("colonists").get("pawns") or []) if B.probe("pawn:%d=draft" % p["id"]).get("success")]
        rr = "%d,%d,%d,%d" % (rx - 2, rz - 2, rw + 4, rh + 4)
        pw = B.call("jawa/list_pawns", rect=rr, limit=50)
        left = [p.get("id") or p.get("label") for p in pw.get("pawns") or []]
        pitch = RL.board_overlap_check(boards) if boards is not None else []
        ok = all(chans.values()) and w.get("success") is True and not left and not pitch and armed_clean
        self.row("preflight", "P3_probes_site_pinned_region_empty", "PASS" if ok else "FAIL", "HARNESS" if not all(chans.values()) else "SITE",
                 {"channels": chans, "weatherLocked": w.get("success"), "local_hour_before": hour, "pinned_noon": bool(pin and pin.get("success")),
                  "nonColonistsDestroyed": db.get("matchedCount"), "hostileBuildingsDestroyed": sorted({t.get("def") for t in hostile}),
                  "fogTriggersDisarmed": disarm, "fogTriggersAfterQuiet": disarm_after, "hostilePawnsLeft": hostiles_left,
                  "mapFogCleared": fog,
                  "colonistsMoved": moved, "colonistsDrafted": drafted, "pawnsInRegion": left,
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
        scenes = _no_hose(spec["scenes"])
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
        finally:
            R.switch("post")
            B.probe("defaults")
            B.ap("defaults")
            B.call("jawa/screenshot_mode", enabled=False)
            R.finish_copies()
        for r in R.rows:
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
    def save_load(self):
        """The ONE save + load. Hoses (H10, R4, SL4) moved with the hose to FlowWorks/northstar/proof_hose.py (hose port)."""
        B = self.B
        notes = {}
        # ---- staging (ticks allowed here; nothing is read for the comparison until the staging is done)
        ca = B.ap("census")                           # M16 asserted a CUT span and its two fallen halves survive
        apos = VA.anchors_by_pos(ca)
        if VA.M2 in apos and VA.M3 in apos and not any(l["state"] == "Cut" for a in ca.get("anchors") or [] for l in a["links"]):
            notes["aerialCut"] = B.ap("cut:%d,%d" % (apos[VA.M2]["id"], apos[VA.M3]["id"]))
            B.ticks(3)
            B.ap("poll")
        VS._cst(B)                                    # stage-2 runs processed (2 ticks)
        # ---- the BEFORE read: zero ticks from here to the save
        B.call("rimworld/frame_cell_rect", x=V.SITE[0], z=V.SITE[1] - 6, width=V.SITE[2], height=V.SITE[3] + 6, paddingCells=1)
        time.sleep(1.0)
        B.probe("poll")
        cords_a = B.probe("census")
        aer_a = B.ap("census")
        sty_a = B.ap("styles")
        s9_a = B.ap("cstyles:%d,%d,%d,%d" % VS.SITE2)
        name = self.args.save_name or "RM_gss_proof_%s" % time.strftime("%Y%m%d%H%M%S")
        self.res["save"] = name + ".rws"
        before = V._saves_stat()
        if name + ".rws" in before:
            self.row("save_load", "SL1_save_landed_new_file_only", "FAIL", "HARNESS", "%s.rws exists" % name)
            return
        sv = B.call("rimworld/save_game", saveName=name)
        V._wait_saved(name)
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
        # SL2 = M9a (no "GimmeSomeSlack" anywhere) U M16b (no aerial MapComponent) + the legacy namespace (the rename:
        # nothing may still be written as MessyConduit). Since the hose port GSS has no class that may legitimately be in a
        # save (the carried-hose job driver is FlowWorks'), so EVERY occurrence of our namespace is a fault.
        hits = {k: blob.count(k.encode()) for k in ("GimmeSomeSlack", "RM_MapComponent_Aerial", "RM_MapComponent_CordGraph", "MessyConduit")}
        offending = [blob[max(0, i - 120):i + 60].decode("utf-8", "replace").strip()[-160:] for i in V._find_all(blob, b"GimmeSomeSlack")]
        sl2 = all(v == 0 for v in hits.values())
        self.row("save_load", "SL2_save_names_no_class_of_ours", "PASS" if sl2 else "FAIL", "MOD",
                 {"counts": hits, "first": offending[:3]})
        ld = B.call("rimworld/load_game", saveName=name)
        ok, waited = V._wait_playing(B)
        if not ok:
            self.row("save_load", "SL3_after_load_census_equal", "FAIL", "SITE", {"load": ld.get("success"), "state": waited})
            return
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
        parts = {
            "cords(M4)": (V._cord_set(cords_a), V._cord_set(cords_b)),
            "aerial(M16)": (VA._aerial_set(aer_a), VA._aerial_set(aer_b)),
            "mastStyles(S7)": (VS._snapshot(sty_a), VS._snapshot(sty_b)),
            "runStyles(S9e)": (VS._s9_snap(s9_a), VS._s9_snap(s9_b)),
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
        sl3 = not differ and not empty and bool(parts["aerial(M16)"][0]["fallen"])
        self.row("save_load", "SL3_after_load_census_equal", "PASS" if sl3 else "FAIL", "MOD",
                 {"differs": differ, "emptyBefore": empty, "loadSeconds": waited,
                  "sizes": {"edges": len(parts["cords(M4)"][0].get("edgeHashes") or {}), "geometryHash": [parts["cords(M4)"][0].get("geometryHash"), parts["cords(M4)"][1].get("geometryHash")],
                            "aerialLinks": len(parts["aerial(M16)"][0]["links"]), "aerialFallen": len(parts["aerial(M16)"][0]["fallen"]),
                            "masts": len(parts["mastStyles(S7)"][0]), "runCells": len(parts["runStyles(S9e)"][0][0])},
                  "spawned": cords_b.get("spawnedConduitTexture")})
        self.res["save_load_notes"] = notes

    # ------------------------------------------------------------------ 4b. S12d: a SECOND save, after SL3
    def d4_save(self):
        """S12d (GPT D4) measured IN the session. Until 2026-10-22 the style block wrote S12d as SHARED/UNMEASURED and left it
        to a standalone `validation_style.py --live --save`, so every full proof_all result carried one UNMEASURED row and
        `modcheck record` (any UNMEASURED row -> RED) could never read it GREEN. The reason it was left out still holds: a
        member staged pending in the ONE save would change M4/S7/S9e's before/after sets. So D4 gets its own save + load
        here, AFTER SL3 has compared them -- nothing it stages can reach SL1-SL3. Z (next block) covers this load too; the
        control's save/load noise is the same list's. Reuses validation_style's own staging, save and read verbatim."""
        if self.res.get("aborted"):
            return                                           # the SHARED placeholder row stays, honestly UNMEASURED
        B = self.B
        self.rows = [r for r in self.rows if r.get("id") != "S12d_D4_pending_queue_save"]
        built = VS.s12d_stage(B)
        name = (self.args.save_name or "RM_gss_proof_%s" % time.strftime("%Y%m%d%H%M%S")) + "_d4"
        self.res["save_d4"] = name + ".rws"
        rows = []
        VS._save_load(B, rows, name, B.ap("styles"), stage=built)
        bad = [r for r in rows if r.get("status") != "PASS"]
        if bad:                                              # the save or the load itself failed: D4 was not read
            self.row("save_load", "S12d_D4_pending_queue_save", "UNMEASURED", "HARNESS",
                     {"why": "the D4 save/load did not complete", "saveLoad": bad, "built": built})
            return
        VS.s12d_after_load(B, rows, built)
        for r in rows:
            if r.get("id") == "S12d_D4_pending_queue_save":
                self.rows.append(dict(r, block="save_load"))
            else:                                            # its S7 re-read of the second load: evidence, not a row
                self.res.setdefault("d4_save_notes", []).append(r)

    # ------------------------------------------------------------------ control: the list's own noise
    def p2c_control_noise(self):
        """2026-10-10 (full 550-mod list): Z charged GSS with other mods' errors that ANY save/load on that list emits --
        ReGrowthCore Map_FinalizeInit_Patch.RecolorMineables NRE, RimFridge.RimFridgeComponent.StartedOrLoadedGame NRE (+ its
        missing ResearchProjectDef), 'Could not get load ID ... /sourcePrecept' on the colonists' apparel, 'forgetTimers', a
        disabled-stat consistency check on a quicktest colonist. Measured here, BEFORE any GSS scene exists: one save, one
        load, 600 ticks; every error message (digits normalised) is the control set. Z excludes only errors in this set that do
        not name GSS; an error the session adds beyond it (a clash) is still charged. Not a row unless the control fails."""
        B = self.B
        self.control = set()
        # the window opens at P2's log base, not here: no GSS scene exists yet, and the game ran between the two (a vanilla
        # Log.ErrorOnce "Faction leader for <campaign faction> is null." from Faction.FactionTick fired once in that gap,
        # 2026-10-10, and being ErrorOnce never came back inside the control's own ticks)
        seq0 = getattr(self, "log_base", 0)
        # TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM: the map is swept BEFORE the control's first tick (P3 sweeps again).
        # What the control measures is unchanged: the list's own save/load + tick noise on the map the session will run
        # on -- and that map has no hives or wild hostiles from P3 on, so a control taken on the swept map is the faithful
        # one (hive tick errors it no longer sees cannot recur later in the session either).
        calm = self.calm_map()
        self.res["control_noise_calm"] = {"calm": calm["calm"], "fogTriggers": calm["fogTriggersDisarmed"],
                                          "nonColonistsDestroyed": (calm["destroyBulk"] or {}).get("matchedCount"),
                                          "hostileBuildingsDestroyed": sorted({t.get("def") for t in calm["hostileBuildings"]}),
                                          "mapFog": calm["mapFog"]}
        if not calm["calm"]:
            self.row("preflight", "P2c_control_save_load", "FAIL", "SITE",
                     {"why": "the map would not calm before the control advance (a hostile or a trigger left)",
                      "calm": self.res["control_noise_calm"]})
            return
        name = "RM_gss_control_%s" % time.strftime("%Y%m%d%H%M%S")
        B.call("rimworld/save_game", saveName=name)
        V._wait_saved(name)
        B.call("rimworld/load_game", saveName=name)
        ok, waited = V._wait_playing(B)
        if ok:
            B.ticks(600)
        lg = B.call("rimbridge/list_logs", limit=1000, minimumLevel="warning")
        errs = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > seq0 and str(e.get("Level", "")).lower() in ("error", "exception")]
        # identity = message AND throwing frame, so a generic "NullReferenceException" in the control does not hide an NRE
        # thrown somewhere else later
        self.control = {_err_key(e) for e in errs if "GimmeSomeSlack" not in _err_text(e)}
        self.res["control_noise"] = {"save": name + ".rws", "loaded": ok, "loadSeconds": waited, "errors": len(errs),
                                     "distinct": sorted("%s @ %s" % (m[:120], t) for m, t in self.control)[:24]}
        if not ok:
            self.row("preflight", "P2c_control_save_load", "FAIL", "SITE", self.res["control_noise"])

    # ------------------------------------------------------------------ 5. Z
    def log_budget(self):
        tap = _VC().TAP[0] if _VC().TAP else None
        if tap is not None:
            new, lg = tap.since(self.log_base), {"logs": None}
        else:
            lg = self.B.call("rimbridge/list_logs", limit=1000, minimumLevel="warning")
            new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > self.log_base]
        errs = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
        # the sites' own clears over a geyser/monolith ("Tried to destroy non-destroyable thing") and a donor mod's
        # map-creation NRE (ReGrowthCore Map_FinalizeInit) are the harness/site, never charged to the mod (run_live LEARNED)
        site = [e for e in errs if "non-destroyable" in str(e.get("Message", ""))]
        donor = [e for e in errs if "Map_FinalizeInit" in str(e.get("Message", "")) and "GimmeSomeSlack" not in str(e.get("Message", ""))]
        errs = [e for e in errs if e not in site and e not in donor]
        ctl = getattr(self, "control", set())
        noise = [e for e in errs if "GimmeSomeSlack" not in _err_text(e) and _err_key(e) in ctl]
        errs = [e for e in errs if e not in noise]
        # 2026-10-10: the control misses list noise that fires on its own clock (RimFridge's LoadedGame NRE was in one run's
        # control and not the next). An error whose own text names ANOTHER mod as its source -- a first stack frame (refs
        # resolved) in a non-vanilla, non-GSS namespace, or a def error's "[Source: <mod>]" -- is that mod's, listed with its
        # thrower; vanilla frames, unresolved stacks and anything naming GSS stay charged.
        foreign = [e for e in errs if "GimmeSomeSlack" not in _err_text(e) and _foreign_source(e)]
        errs = [e for e in errs if e not in foreign]
        alive = _VC().log_alive(self.B, "Z")
        if tap is not None and tap.lost:
            self.row("session", "Z_log_budget", "UNMEASURED", "HARNESS", {"why": "%d journal entries scrolled out of RimBridge's "
                     "1,000-entry ring between two polls: the budget did not see the whole run" % tap.lost, "polls": tap.polls, "gaps": tap.gaps,
                     "errorsSeen": len(errs), "errors": [str(e.get("Message", ""))[:200] for e in errs[:6]]})
            return
        if not alive["alive"]:
            self.row("session", "Z_log_budget", "UNMEASURED", "HARNESS", {"why": "logging is dead (Verse.Log message cap?): "
                     "the sentinel warning never reached the journal, so 0 errors here is not evidence", "sentinel": alive,
                     "revive": self.res.get("log_revive"), "errorsSeen": len(errs)})
            return
        self.row("session", "Z_log_budget", "PASS" if not errs else "FAIL", "MOD",
                 {"errors": [str(e.get("Message", ""))[:240] for e in errs[:10]],
                  "throwers": [_thrower(e) for e in errs[:10]], "newWarnings": len(new),
                  "siteClearErrorsExcluded": len(site), "donorMapInitErrorsExcluded": len(donor),
                  "controlNoiseExcluded": len(noise), "controlNoiseThrowers": sorted({_thrower(e) for e in noise})[:10],
                  "foreignSourceExcluded": len(foreign), "foreignSources": sorted({_foreign_source(e) for e in foreign})[:10],
                  "sinceSequence": self.log_base, "readBack": len(lg.get("logs") or new or []),
                  "tap": {"polls": tap.polls, "lost": tap.lost, "kept": len(tap.entries)} if tap else None})

    def restore(self):
        B = self.B
        self.res["quiet_site_restore"] = _QS().restore_attached(B)
        for f in (lambda: B.probe("defaults"), lambda: B.ap("defaults"),
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
            boards = RL.make_boards(_no_hose(sp["scenes"]))
        self.block("preflight", lambda: (self.p1_fresh_map(), self.p2_tier_and_startup_log(), self.p2c_control_noise(),
                                          self.p3_probes_and_site(boards)))
        if any(r["status"] != "PASS" for r in self.rows if r.get("block") == "preflight"):
            self.res["aborted"] = "preflight not green"
            return
        self.block("matrix", lambda: self.matrix(spec))
        self.block("core", self.core)
        self.block("aerial", lambda: self.take("aerial", VA.run_live(self.ns())))
        self.block("style", lambda: self.take("style", VS.run_live(self.ns())))
        if self.want("matrix"):
            self.block("determinism", self.determinism)
        self.block("save_load", self.save_load)
        self.block("d4_save", self.d4_save)
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
    ap.add_argument("--fresh-map", action="store_true", help="generate a new quicktest map (the pre-2026-10-15 path) "
                                                             "instead of loading the clean saved site")
    ap.add_argument("--site-save", default="calm", help="the clean saved site P1 loads (test_site_saves.py; default calm)")
    ap.add_argument("--skip-offline", action="store_true", help="do not run the offline gate (recorded; debug only)")
    ap.add_argument("--allow-red", action="append", default=[], help="an offline red id to accept (recorded in the result)")
    ap.add_argument("--spec", default=None, help="design spec JSON (default: the one the offline gate writes)")
    ap.add_argument("--full-matrix", action="store_true", help="the full matrix minus its 9 H hose scenes (FlowWorks runs those) instead of the reduced 30")
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
    if a.fresh_map and a.no_fresh_map:
        ap.error("--fresh-map and --no-fresh-map exclude each other")
    a.map_mode = "fresh" if a.fresh_map else ("current" if a.no_fresh_map else "save")
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
