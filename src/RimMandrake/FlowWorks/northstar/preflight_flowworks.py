#!/usr/bin/env python3
"""FlowWorks trial preflight -- refuse a dirty site, naming the row (trial plan section 3.9).

Every row of the plan's 3.9 table is one function here, and each returns a Check whose name
IS the row id (P-O1 ... P-E8). Status PASS / FAIL / UNMEASURED; "could not ask" is UNMEASURED,
never a pass. Exit 0 only when every row run is PASS (--allow-unmeasured relaxes UNMEASURED,
never FAIL). Item FLOWWORKS_NORTHSTAR_SITE_PREP_1.

  python3  src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py offline
  python.exe src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py live --seat FOUNDRY
  python3  src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py backup      # before the swap
  python3  src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py restore <manifest.json>

`live` needs the bridge (Windows python, repo-relative paths) and the bridge lock. `backup`
writes ModsConfig + the FlowWorks ModSettings files byte-for-byte under deployed/config/;
`restore` puts them back and proves the hashes -- the one recovery command if a run dies.
Nothing here writes ModsConfig.xml except `restore`, and only with the captured bytes.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import site_spec as S  # noqa: E402
from northstar_driver import PASS, FAIL, UNMEASURED  # noqa: E402
from northstar_driver.preflight import Check, check_paused, check_no_modal, check_dev_god, \
    check_loaded_not_zombie, verdict  # noqa: E402

ROWS = {
    "P-O1": "north star VALIDATED and hash matches",
    "P-O2": "floor: every must-show claimed, no orphan shows=, every toggle covered",
    "P-O3": "deploy in sync; DLL + .srchash equal; srchash matches Source at HEAD",
    "P-O4": "FULL.LATEST differs from the pre-swap list only by the intended removal",
    "P-O5": "FlowWorks tree committed; golden-save version contract matches",
    "P-O6": "no duplicate FlowWorks/Pits copies; ModsConfig + ModSettings backups hashed",
    "P-L1": "live list == tier (ordered); five DLCs; mandrake.rm.pits absent",
    "P-L2": "Player.log: no FlowWorks config/XML error, duplicate RM_ defName, exception",
    "P-B1": "bridge reachable; BRIDGE held by this seat",
    "P-B2": "game Playing; current map == trial site (id, size, tile)",
    "P-B3": "FlowWorks bridge tools registered",
    "P-B4": "Mod Settings snapshot == shipped defaults",
    "P-S1": "every plot+buffer cell == sidecar manifest (top, temp, roof, things; D/F sampled)",
    "P-S2": "every authored body == its manifest record",
    "P-S3": "map-wide excavatedCellCount 0, sink/overflow totals 0, no RM_FluidCanalFlood",
    "P-E1": "weather Clear, no GameCondition on the map, incident queue empty",
    "P-E2": "every check cell 10..45 C; season summer; clock readable",
    "P-E3": "paused (proved); step rate measured; no open window; dev mode on",
    "P-E4": "map pawn roster empty; autosave off",
    "P-E5": "calibration shot passes the luma/variance gate",
    "P-E6": "loaded assembly identity == deployed DLL; ordered active list == tier",
    "P-E7": "nextPulseTick readable; step(PULSE) advances exactly PULSE, stays paused",
    "P-E8": "render profile == sidecar",
}
OFFLINE = ("P-O1", "P-O2", "P-O3", "P-O4", "P-O5", "P-O6")
PITS = "mandrake.rm.pits"


def row(rid, status, evidence):
    return Check(rid, status, evidence)


def _guard(rid, fn, *a, **k):
    """A row that raised could not ask: UNMEASURED with the reason, never PASS."""
    try:
        return fn(*a, **k)
    except Exception as ex:
        return row(rid, UNMEASURED, "%s raised %s: %s" % (rid, type(ex).__name__, str(ex)[:200]))


def _run(cmd, cwd=S.ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


class Paths(object):
    """Every external path a row reads, overridable for the selftest."""

    def __init__(self, **kw):
        try:
            import game_paths as G
            low, mods, ws, saves, log = G.LOCALLOW, G.LOCAL_MODS, G.WORKSHOP, G.SAVES, G.PLAYER_LOG
        except Exception:
            low = mods = ws = saves = log = None
        self.config_dir = os.path.join(low, "Config") if low else None
        self.mods_config = os.path.join(self.config_dir, "ModsConfig.xml") if low else None
        self.prefs = os.path.join(self.config_dir, "Prefs.xml") if low else None
        self.player_log = log
        self.saves = saves
        self.mod_roots = [r for r in (mods, ws) if r]
        self.deployed_mod = os.path.join(mods, "FlowWorks") if mods else None
        self.full_latest = os.path.join(S.ROOT, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
        self.backup_dir = os.path.join(S.ROOT, "deployed", "config")
        self.backup_manifest = None
        self.pre_swap = None
        self.sidecar = None
        self.bridge_file = os.path.join(S.ROOT, "infrastructure", "state", "BRIDGE")
        self.expected_tier = None          # ordered ids; None = compute via modset_builder
        self.run = _run
        for k, v in kw.items():
            setattr(self, k, v)
        if self.sidecar is None and self.saves:
            self.sidecar = os.path.join(self.saves, S.GOLDEN_NAME + ".json")
        if self.backup_manifest is None:
            self.backup_manifest = newest_backup(self.backup_dir)


def newest_backup(d):
    try:
        ms = sorted(f for f in os.listdir(d) if f.startswith("ns_flowworks_backup.") and f.endswith(".json"))
    except OSError:
        return None
    return os.path.join(d, ms[-1]) if ms else None


def active_ids(path):
    return [li.text.strip().lower() for li in ET.parse(path).getroot().find("activeMods") if li.text]


def expected_tier_list():
    import modset_builder as M
    installed = M.scan()
    t = M.TIERS[S.TIER]
    want = list(t["want"]) + [p for p in installed if p.startswith("ludeon.rimworld")] + [M.HARMONY]
    pids, missing = M.close_over(want, installed)
    if missing:
        raise RuntimeError("tier %s incomplete: %s not installed" % (S.TIER, missing))
    return M.order(pids, installed)


# ============================================================= offline rows

def p_o1(P):
    import runner
    walk, ns = runner.northstar_for("FlowWorks")
    if not walk:
        return row("P-O1", FAIL, "no FlowWorks validation walk")
    if ns["state"] != "VALIDATED":
        return row("P-O1", FAIL, "north star is %s: %s" % (ns["state"], ns["reason"]))
    return row("P-O1", PASS, "VALIDATED, %d must-show + %d cannot-show, hash %s"
               % (len(ns["must_show"]), len(ns["cannot_show"]), ns["current_hash"][:12]))


def p_o2(P):
    import floor
    import runner
    walk, ns = runner.northstar_for("FlowWorks")
    suite = runner.load_validation(runner.find_mod_dir("FlowWorks"))
    fl = runner.visual_floor(suite, ns)
    comps = suite.components_declared()
    unt = floor.uncovered(S.toggles(), comps)
    bad = []
    if fl["uncovered"]:
        bad.append("%d of %d must-show unclaimed (e.g. %s)" % (len(fl["uncovered"]), len(fl["bar"]),
                                                              fl["uncovered"][:3]))
    if fl["orphans"]:
        bad.append("orphan shows= %s" % fl["orphans"][:5])
    if unt:
        bad.append("%d of %d toggles uncovered (e.g. %s)" % (len(unt), len(S.toggles()), unt[:3]))
    if bad:
        return row("P-O2", FAIL, "; ".join(bad))
    return row("P-O2", PASS, "%d must-show claimed, %d toggles covered" % (len(fl["bar"]), len(S.toggles())))


def p_o3(P):
    bad = []
    rc, out = P.run([sys.executable, os.path.join(S.UTILS, "deploy_custom_mods.py"), "--mod", "FlowWorks"])
    if not re.search(r"in sync \(\d+ files", out):
        bad.append("deploy dry run is not 'in sync' (rc %s): %s" % (rc, out.strip().splitlines()[-1:] or out[:80]))
    repo_dll = os.path.join(S.MOD_DIR, S.DLL_REL)
    if not P.deployed_mod or not os.path.isdir(P.deployed_mod):
        return row("P-O3", UNMEASURED if not bad else FAIL,
                   "; ".join(bad + ["deployed mod folder unreadable: %s" % P.deployed_mod]))
    for suffix in ("", ".srchash"):
        a, b = repo_dll + suffix, os.path.join(P.deployed_mod, S.DLL_REL) + suffix
        if not os.path.isfile(b):
            bad.append("deployed %s missing" % os.path.basename(b))
        elif S.sha256_file(a) != S.sha256_file(b):
            bad.append("deployed %s differs from repo" % os.path.basename(b))
    rc, out = P.run([sys.executable, os.path.join(S.UTILS, "dll_source_stamp.py"), "check"])
    line = [l for l in out.splitlines() if "RimMandrakeFlowWorks.dll" in l and not l.startswith(" ")]
    if not line or not line[0].startswith("MATCH"):
        bad.append("dll_source_stamp: %s" % (line[0] if line else "no FlowWorks line"))
    return row("P-O3", FAIL if bad else PASS, "; ".join(bad) or "in sync; DLL+srchash identical; stamp MATCH")


def p_o4(P):
    pre = P.pre_swap
    if pre is None and P.backup_manifest:
        man = json.load(open(P.backup_manifest, encoding="utf-8"))
        e = [x for x in man["entries"] if x["src"] == "ModsConfig.xml"]
        pre = os.path.join(os.path.dirname(P.backup_manifest), e[0]["backup"]) if e else None
    pre = pre or P.mods_config
    full, live = active_ids(P.full_latest), active_ids(pre)
    if live == full:
        return row("P-O4", PASS, "pre-swap list == FULL.LATEST (%d mods)" % len(full))
    if live == [i for i in full if i != PITS]:
        return row("P-O4", PASS, "pre-swap list == FULL.LATEST minus %s (%d mods)" % (PITS, len(live)))
    extra = [i for i in live if i not in full]
    gone = [i for i in full if i not in live and i != PITS]
    return row("P-O4", FAIL, "unexpected diff vs FULL.LATEST: +%s -%s%s; restore_full() would change his list"
               % (extra[:5], gone[:5], " (order differs)" if not (extra or gone) else ""))


def p_o5(P):
    bad = []
    rc, out = P.run(["git", "status", "--porcelain", "--", "src/RimMandrake/FlowWorks"])
    if rc != 0:
        return row("P-O5", UNMEASURED, "git status failed: %s" % out[:120])
    if out.strip():
        bad.append("uncommitted FlowWorks changes: %s" % out.strip().splitlines()[:3])
    bad += contract_problems(P)
    return row("P-O5", FAIL if bad else PASS, "; ".join(bad) or "tree clean; golden contract matches")


def contract_problems(P):
    """The golden-save version contract (plan 3.4): any mismatch => rebuild, never 'probably fine'."""
    if not P.sidecar or not os.path.isfile(P.sidecar):
        return ["no golden sidecar %s -- run prep_site.py" % P.sidecar]
    sc = json.load(open(P.sidecar, encoding="utf-8"))
    c = sc.get("contract") or {}
    save = os.path.join(os.path.dirname(P.sidecar), sc.get("save", ""))
    out = []
    if not os.path.isfile(save):
        return ["golden save %s missing" % save]
    if os.access(save, os.W_OK):
        out.append("golden save is writable (must be read-only)")
    if S.sha256_file(save) != c.get("save_sha256"):
        out.append("golden save sha changed since prep")
    if S.sha256_file(os.path.join(S.MOD_DIR, S.DLL_REL)) != c.get("flowworks_dll_sha256"):
        out.append("FlowWorks DLL changed since prep")
    if S.defs_hash() != c.get("defs_hash"):
        out.append("FlowWorks Defs changed since prep")
    if c.get("prep_version") != S.PREP_VERSION:
        out.append("prep version %s != %s" % (c.get("prep_version"), S.PREP_VERSION))
    snap = c.get("settings") or {}
    drift = [f for t, fields in S.SETTINGS.items() for f, v in fields.items()
             if not S.settings_equal((snap.get(t) or {}).get(f), v)]
    if drift:
        out.append("prep settings snapshot not shipped defaults: %s" % drift[:4])
    return out


def p_o6(P):
    bad = []
    fw_pkg, fw_dll, pits_dll = [], [], []
    for root in P.mod_roots:
        if not os.path.isdir(root):
            return row("P-O6", UNMEASURED, "mod root unreadable: %s" % root)
        for d in os.listdir(root):
            about = os.path.join(root, d, "About", "About.xml")
            if os.path.isfile(about):
                try:
                    pid = (ET.parse(about).getroot().findtext("packageId") or "").strip().lower()
                except ET.ParseError:
                    pid = ""
                if pid == S.PACKAGE_ID:
                    fw_pkg.append(os.path.join(root, d))
            # RimWorld loads assemblies from <mod>/Assemblies and <mod>/<loadFolder>/Assemblies only;
            # walking every texture of 1,400 mods on drvfs is minutes, these two globs are seconds.
            for p in glob.glob(os.path.join(root, glob.escape(d), "Assemblies", "*.dll")) + \
                    glob.glob(os.path.join(root, glob.escape(d), "*", "Assemblies", "*.dll")):
                f = os.path.basename(p).lower()
                if f == "rimmandrakeflowworks.dll":
                    fw_dll.append(p)
                elif f == "rimmandrakepits.dll":
                    pits_dll.append(p)
    if len(fw_pkg) != 1:
        bad.append("%d folders carry packageId %s: %s" % (len(fw_pkg), S.PACKAGE_ID, fw_pkg))
    if len(fw_dll) != 1:
        bad.append("%d RimMandrakeFlowWorks.dll copies: %s" % (len(fw_dll), fw_dll[:3]))
    if pits_dll:
        bad.append("stale RimMandrakePits.dll present: %s (PITS_STALE_DEPLOY_COLLISION_1)" % pits_dll[:3])
    if not P.backup_manifest:
        bad.append("no ModsConfig/ModSettings backup manifest -- run `preflight_flowworks.py backup` first")
    else:
        bad += S.verify_backup(P.backup_manifest)
    return row("P-O6", FAIL if bad else PASS, "; ".join(bad) or "one FlowWorks copy; backups hash-verified")


def run_offline(P, only=None):
    fns = {"P-O1": p_o1, "P-O2": p_o2, "P-O3": p_o3, "P-O4": p_o4, "P-O5": p_o5, "P-O6": p_o6}
    return [_guard(r, fns[r], P) for r in OFFLINE if not only or r in only]


# ============================================================= live rows

def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        raise RuntimeError("%s failed: %s" % (what, str(r)[:160]))
    return r


def p_l1(s, P, sc):
    want = P.expected_tier or expected_tier_list()
    got = active_ids(P.mods_config)
    bad = []
    if PITS in got:
        bad.append("%s ACTIVE (22/22 defName collision)" % PITS)
    miss = [d for d in ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
                        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey") if d not in got]
    if miss:
        bad.append("DLC missing: %s" % miss)
    if got != list(want):
        bad.append("active list != tier %s: +%s -%s" % (S.TIER, [i for i in got if i not in want][:5],
                                                         [i for i in want if i not in got][:5]))
    return row("P-L1", FAIL if bad else PASS, "; ".join(bad) or "%d mods == tier, in order (disk = this load)"
               % len(got))


LOG_NEEDLES = (
    (re.compile(r"config error", re.I), re.compile(r"flowworks|\bRM_", re.I)),
    (re.compile(r"XML error|XmlException", re.I), re.compile(r"FlowWorks", re.I)),
    (re.compile(r"duplicate|already exists", re.I), re.compile(r"defName.*\bRM_|\bRM_\w+.*defName", re.I)),
    (re.compile(r"Exception", re.I), re.compile(r"RimMandrake\.FlowWorks|FlowWorks", re.I)),
)


def p_l2(s, P, sc):
    with open(P.player_log, "rb") as f:
        txt = f.read().decode("utf-8", "replace")
    hits = [l.strip() for l in txt.splitlines() if any(a.search(l) and b.search(l) for a, b in LOG_NEEDLES)]
    if hits:
        return row("P-L2", FAIL, "%d log line(s), first: %s" % (len(hits), hits[0][:160]))
    return row("P-L2", PASS, "%d log lines scanned, no FlowWorks error" % txt.count("\n"))


def p_b1(s, P, sc, seat):
    if not s.tools:
        return row("P-B1", FAIL, "bridge answered with no tools")
    holder = None
    if os.path.isfile(P.bridge_file):
        holder = open(P.bridge_file, encoding="utf-8", errors="replace").read().strip()
    else:
        rc, out = P.run([sys.executable, os.path.join(S.ROOT, "src", "RimMandrake", "rimflow", "cli.py"),
                         "bridge", "who"])
        holder = out.strip() if rc == 0 else None
    if holder is None:
        return row("P-B1", UNMEASURED, "bridge holder unreadable (no BRIDGE file, `rimflow bridge who` failed)")
    held = [t for t in S.SEATS if re.search(r"\b%s\b" % t, holder)]
    if held != [seat]:
        return row("P-B1", FAIL, "bridge held by %s, not %s: %s" % (held or "nobody", seat, holder[:120]))
    return row("P-B1", PASS, "%d tools; bridge held by %s" % (len(s.tools), seat))


def p_b2(s, P, sc):
    z = check_loaded_not_zombie(s)
    if z.status != PASS:
        return row("P-B2", z.status, z.evidence)
    mi = _ok(s.call("jawa/map_info"), "map_info")
    g = sc.get("generation") or {}
    bad = ["%s %s != sidecar %s" % (k, mi.get(k), g.get(k)) for k in ("mapId", "sizeX", "sizeZ", "tile")
           if mi.get(k) != g.get(k)]
    return row("P-B2", FAIL if bad else PASS, "; ".join(bad) or "map %s %sx%s tile %s == sidecar"
               % (mi["mapId"], mi["sizeX"], mi["sizeZ"], mi["tile"]))


def p_b3(s, P, sc):
    miss = [t for t in S.P_B3_TOOLS if t not in s.tools]
    return row("P-B3", FAIL if miss else PASS, "missing %s -- stale JawaBench deploy" % miss if miss
               else "all %d FlowWorks tools registered" % len(S.P_B3_TOOLS))


def settings_snapshot(s):
    snap, bad = {}, {}
    for t, fields in S.SETTINGS.items():
        snap[t] = {}
        for f, v in fields.items():
            got = _ok(s.call("jawa/mod_settings_field", typeName=t, action="get", field=f),
                      "mod_settings_field %s.%s" % (t, f)).get("value")
            snap[t][f] = got
            if not S.settings_equal(got, v):
                bad["%s.%s" % (t.rsplit(".", 1)[1], f)] = got
    return snap, bad


def p_b4(s, P, sc):
    snap, bad = settings_snapshot(s)
    if bad:
        return row("P-B4", FAIL, "not at shipped defaults: %s" % bad)
    return row("P-B4", PASS, "%d fields at shipped defaults" % sum(len(v) for v in S.SETTINGS.values()))


def read_plot_state(s, plot, size):
    """Live {(x,z): {base,temp,roof,things}} over a plot's clipped buffered rect."""
    r = S.clip(plot["buffered"], size)
    n = r[2] * r[3]
    lay = _ok(s.call("jawa/get_terrain_layers", rect=S.rect_str(r), limit=n), "get_terrain_layers")
    if lay.get("truncated") or len(lay.get("cells") or []) != n:
        raise RuntimeError("get_terrain_layers returned %s of %d cells" % (len(lay.get("cells") or []), n))
    roofs = S.parse_ops(_ok(s.call("jawa/get_roof_batch", rects=S.rect_str(r)), "get_roof_batch").get("ops"))
    th = _ok(s.call("jawa/list_things", rect=S.rect_str(r), includePawns=True, limit=5000), "list_things")
    if th.get("isCompleteList") is False:
        raise RuntimeError("list_things truncated over %s" % (r,))
    out = {}
    for c in lay["cells"]:
        k = (c["x"], c["z"])
        out[k] = {"base": c.get("top"), "temp": c.get("temp") or "none", "roof": roofs.get(k) or "none",
                  "things": []}
    for t in th.get("things") or []:
        pos = t.get("position") or t
        if isinstance(pos, str):                     # "(x, y, z)" form
            n = [int(v) for v in re.findall(r"-?\d+", pos)]
            pos = {"x": n[0], "z": n[-1]} if len(n) >= 2 else {}
        k = (pos.get("x"), pos.get("z"))
        if k in out:
            out[k]["things"].append(t.get("def") or t.get("defName"))
        else:
            out.setdefault("_unplaced", []).append(t.get("def") or t.get("defName"))
    return out


def diff_plot(plot, live, manifest_cells):
    bad = []
    for key, want in manifest_cells.items():
        x, z = [int(v) for v in key.split(",")]
        got = live.get((x, z))
        if got is None:
            bad.append("%s unread" % key)
            continue
        for f in ("base", "temp", "roof"):
            if got[f] != want[f]:
                bad.append("%s %s=%s want %s" % (key, f, got[f], want[f]))
        if sorted(got["things"]) != sorted(want["things"]):
            bad.append("%s things=%s" % (key, got["things"]))
    if live.get("_unplaced"):
        bad.append("things with no readable position in rect: %s" % live["_unplaced"][:4])
    return bad


def p_s1(s, P, sc):
    size = (sc["generation"]["sizeX"], sc["generation"]["sizeZ"])
    bad = []
    for plot in sc["plots"]:
        live = read_plot_state(s, plot, size)
        for msg in diff_plot(plot, live, sc["manifest"][plot["id"]])[:3]:
            bad.append("plot %s: %s" % (plot["id"], msg))
        # D/F: every FOOTPRINT cell, batched (no rect read exists yet, plan 6.3); the buffer is
        # covered by P-S3's map-wide excavatedCellCount == 0 (F <= D, so D=0 implies F=0).
        pts = S.cells(plot["rect"])
        for (x, z), r in zip(pts, s.call_many([("jawa/flowworks_excavation_report", {"x": x, "z": z})
                                               for x, z in pts])):
            if not isinstance(r, dict) or r.get("success") is False:
                raise RuntimeError("excavation_report %d,%d unreadable: %s" % (x, z, str(r)[:100]))
            if r.get("depth") or r.get("fill"):
                bad.append("plot %s: %d,%d D=%s F=%s" % (plot["id"], x, z, r.get("depth"), r.get("fill")))
    return row("P-S1", FAIL if bad else PASS, "; ".join(bad[:6]) or "%d plots match the manifest cell by cell"
               % len(sc["plots"]))


def p_s2(s, P, sc):
    if "jawa/flowworks_body_report" not in s.tools:
        return row("P-S2", UNMEASURED, "needs jawa/flowworks_body_report (site_spec.NEEDED_TOOLS)")
    bad = []
    for name, want in sc["bodies"].items():
        x, z = want["probe"]
        r = _ok(s.call("jawa/flowworks_body_report", x=x, z=z), "body_report")
        got = r.get("body") or {}
        if not r.get("classified"):
            bad.append("%s unclassified" % name)
            continue
        for k in ("id", "limitless", "cellCount", "capacity", "stock", "recededCount"):
            if got.get(k) != want["record"].get(k):
                bad.append("%s %s=%s want %s" % (name, k, got.get(k), want["record"].get(k)))
        if r.get("activeFluid") != want["activeFluid"]:
            bad.append("%s fluid %s want %s" % (name, r.get("activeFluid"), want["activeFluid"]))
    return row("P-S2", FAIL if bad else PASS, "; ".join(bad) or "%d bodies match" % len(sc["bodies"]))


def p_s3(s, P, sc):
    first = sc["plots"][0]["rect"]
    r = _ok(s.call("jawa/flowworks_excavation_report", x=first[0], z=first[1]), "excavation_report")
    bad = ["%s=%s" % (k, r.get(k)) for k in ("excavatedCellCount", "sinkTransferredTotal", "overflowDestroyedTotal")
           if r.get(k) is None or float(r.get(k)) != 0.0]
    fl = _ok(s.call("jawa/list_things", defName="RM_FluidCanalFlood", limit=50), "list_things")
    if fl.get("isCompleteList") is False or fl.get("things"):
        bad.append("RM_FluidCanalFlood present: %d" % len(fl.get("things") or []))
    return row("P-S3", FAIL if bad else PASS, "; ".join(bad) or "no excavation, no flow totals, no flood Thing")


def p_e1(s, P, sc, fix=False):
    w = _ok(s.call("jawa/weather_get"), "weather_get")
    bad = []
    if w.get("readErrors"):
        return row("P-E1", UNMEASURED, "weather_get readErrors %s" % w["readErrors"])
    if w.get("weather") != "Clear":
        bad.append("weather %s (rain fills excavations)" % w.get("weather"))
    conds = [c.get("def") for c in w.get("conditions") or [] if c.get("affectsThisMap")]
    if conds:
        bad.append("GameCondition(s) on the map: %s" % conds)
    q = _ok(s.call("jawa/incident_queue_clear"), "incident_queue_clear")   # no read-only queue tool exists
    if q.get("clearedCount"):
        bad.append("%d incident(s) were queued (now cleared; re-run)" % q["clearedCount"])
    return row("P-E1", FAIL if bad else PASS, "; ".join(bad) or "Clear, no conditions, incident queue empty")


def p_e2(s, P, sc):
    pts = sorted({c for plot in sc["plots"] for c in S.check_points(plot)})
    res = s.call_many([("jawa/cell_temperature", {"cell": "%d,%d" % c}) for c in pts])
    bad, unk = [], []
    for c, r in zip(pts, res):
        if not isinstance(r, dict) or not r.get("ok"):
            unk.append(c)
        elif not (10.0 <= float(r["temperature"]) <= 45.0):
            bad.append("%d,%d %.1fC" % (c[0], c[1], float(r["temperature"])))
    mi = _ok(s.call("jawa/map_info"), "map_info")
    if "summer" not in str(mi.get("season")).lower():
        bad.append("season %s" % mi.get("season"))
    if _ok(s.call("jawa/time_clock"), "time_clock").get("ticksGame") is None:
        unk.append("clock")
    if bad:
        return row("P-E2", FAIL, "out of 10..45 C / season: %s" % bad[:6])
    if unk:
        return row("P-E2", UNMEASURED, "temperature unreadable at %s" % unk[:6])
    return row("P-E2", PASS, "%d check cells 10..45 C; %s" % (len(pts), mi.get("season")))


def p_e3(s, P, sc, fix=False):
    parts = [check_paused(s, fix=fix), check_no_modal(s), check_dev_god(s, need_dev=True, need_god=False, fix=fix)]
    perf = s.call("jawa/time_perf") or {}
    if perf.get("meanTickTime") is None:
        parts.append(Check("step_rate", UNMEASURED, "time_perf gave no meanTickTime"))
    else:
        parts.append(Check("step_rate", PASS, "meanTickTime %s ms" % perf["meanTickTime"]))
    worst = FAIL if any(p.status == FAIL for p in parts) else UNMEASURED if any(
        p.status == UNMEASURED for p in parts) else PASS
    return row("P-E3", worst, "; ".join("%s %s (%s)" % (p.name, p.status, p.evidence) for p in parts))


def p_e4(s, P, sc):
    pw = _ok(s.call("jawa/list_pawns", limit=500), "list_pawns").get("pawns") or []
    bad = ["map pawns present: %s" % [p.get("id") for p in pw][:5]] if pw else []
    prefs = S.read_prefs(P.prefs) if P.prefs and os.path.isfile(P.prefs) else {}
    a = prefs.get("autosaveIntervalDays")
    if a is None:
        return row("P-E4", FAIL if bad else UNMEASURED, "; ".join(bad + ["autosave interval unreadable "
                                                                         "(Prefs.xml autosaveIntervalDays)"]))
    if float(a) > 0:
        bad.append("autosave every %s day(s) -- the working map must never be saved" % a)
    return row("P-E4", FAIL if bad else PASS, "; ".join(bad) or "roster empty; autosave off")


def p_e5(s, P, sc, out_dir=None):
    plot = S.plot_by_id(sc["plots"], "R")
    x, z, w, h = plot["rect"]
    r = _ok(s.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=3),
            "screenshot_cell_rect")
    path = r.get("path")
    if not path or not os.path.isfile(path):
        return row("P-E5", UNMEASURED, "screenshot path unreadable from here: %s" % path)
    from PIL import Image, ImageStat
    st = ImageStat.Stat(Image.open(path).convert("L"))
    mean, var = st.mean[0], st.var[0]
    if mean < 8.0 or var < 4.0:
        return row("P-E5", FAIL, "calibration shot blank/black: mean %.1f var %.1f (%s)" % (mean, var, path))
    return row("P-E5", PASS, "mean %.1f var %.1f" % (mean, var))


def p_e6(s, P, sc):
    r = _ok(s.call("jawa/type_probe", typeName="RimMandrake.FlowWorks.RM_MapComponent_Excavation"), "type_probe")
    need = ("assemblyLocation", "assemblyMvid", "assemblyFileSha256")
    if any(r.get(k) is None for k in need):
        return row("P-E6", UNMEASURED, "type_probe has no assembly identity (needs %s)"
                   % "jawa/type_probe+identity")
    dep = os.path.join(P.deployed_mod or "", S.DLL_REL)
    if not os.path.isfile(dep):
        return row("P-E6", UNMEASURED, "deployed DLL unreadable: %s" % dep)
    bad = []
    if r["assemblyFileSha256"].lower() != S.sha256_file(dep):
        bad.append("loaded assembly sha != deployed DLL (the process runs a different build)")
    l1 = p_l1(s, P, sc)
    if l1.status != PASS:
        bad.append("ordered list: %s" % l1.evidence)
    return row("P-E6", FAIL if bad else PASS, "; ".join(bad) or "loaded %s mvid %s == deployed; list ordered"
               % (os.path.basename(r["assemblyLocation"]), r["assemblyMvid"]))


def p_e7(s, P, sc):
    if "jawa/flowworks_engine_state" not in s.tools:
        return row("P-E7", UNMEASURED, "needs jawa/flowworks_engine_state for nextPulseTick (site_spec.NEEDED_TOOLS)")
    st = _ok(s.call("jawa/flowworks_engine_state"), "engine_state")
    pulse = int(st.get("pulseIntervalTicks") or 0)
    t0 = _ok(s.call("rimworld/get_game_info"), "get_game_info").get("ticksGame")
    if st.get("nextPulseTick") is None or not pulse or t0 is None:
        return row("P-E7", UNMEASURED, "engine state incomplete: %s" % st)
    _ok(s.call("rimworld/step_game_ticks", ticks=pulse), "step_game_ticks")
    t1 = _ok(s.call("rimworld/get_game_info"), "get_game_info").get("ticksGame")
    time.sleep(0.15)
    t2 = _ok(s.call("rimworld/get_game_info"), "get_game_info").get("ticksGame")
    bad = []
    if t1 - t0 != pulse:
        bad.append("step(%d) advanced %d" % (pulse, t1 - t0))
    if t2 != t1:
        bad.append("not paused after step (%s -> %s)" % (t1, t2))
    return row("P-E7", FAIL if bad else PASS, "; ".join(bad) or "nextPulseTick %s; step(%d) exact, paused"
               % (st["nextPulseTick"], pulse))


def p_e8(s, P, sc):
    if not P.prefs or not os.path.isfile(P.prefs):
        return row("P-E8", UNMEASURED, "Prefs.xml unreadable: %s" % P.prefs)
    got = S.read_prefs(P.prefs)
    want = sc.get("render_profile") or {}
    bad = ["%s %s != %s" % (k, got.get(k), want.get(k)) for k in S.RENDER_KEYS if got.get(k) != want.get(k)]
    return row("P-E8", FAIL if bad else PASS, "; ".join(bad) or "render profile == sidecar")


def run_live(s, P, seat, fix=False, only=None):
    sc = json.load(open(P.sidecar, encoding="utf-8")) if P.sidecar and os.path.isfile(P.sidecar) else None
    if sc is not None:
        sc["plots"] = S.plots_from_json(sc["plots"])
    rows = [("P-L1", p_l1), ("P-L2", p_l2), ("P-B1", lambda s_, P_, sc_: p_b1(s_, P_, sc_, seat)),
            ("P-B2", p_b2), ("P-B3", p_b3), ("P-B4", p_b4), ("P-S1", p_s1), ("P-S2", p_s2), ("P-S3", p_s3),
            ("P-E1", lambda s_, P_, sc_: p_e1(s_, P_, sc_, fix)), ("P-E2", p_e2),
            ("P-E3", lambda s_, P_, sc_: p_e3(s_, P_, sc_, fix)), ("P-E4", p_e4), ("P-E6", p_e6),
            ("P-E7", p_e7), ("P-E8", p_e8), ("P-E5", p_e5)]
    out = []
    for rid, fn in rows:
        if only and rid not in only:
            continue
        needs_sc = rid not in ("P-L1", "P-L2", "P-B1", "P-B3", "P-B4", "P-E3", "P-E4")
        if needs_sc and sc is None:
            out.append(row(rid, FAIL, "no golden sidecar %s -- run prep_site.py" % P.sidecar))
            continue
        out.append(_guard(rid, fn, s, P, sc))
    return out


def report(checks, allow_unmeasured=False, stream=sys.stdout):
    for c in checks:
        stream.write("%-10s %-4s %s\n" % (c.status, c.name, c.evidence))
    ok, bad, unk = verdict(checks, allow_unmeasured)
    for c in bad:
        stream.write("REFUSED %s (%s): %s\n" % (c.name, ROWS.get(c.name, ""), c.evidence))
    if not allow_unmeasured:
        for c in unk:
            stream.write("REFUSED %s (%s) UNMEASURED: %s\n" % (c.name, ROWS.get(c.name, ""), c.evidence))
    stream.write("%s: %d rows, %d FAIL, %d UNMEASURED\n" % ("CLEAN" if ok else "DIRTY SITE", len(checks),
                                                            len(bad), len(unk)))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("offline", "live", "all"):
        p = sub.add_parser(name)
        p.add_argument("--seat", default="FOUNDRY", choices=S.SEATS)
        p.add_argument("--only", nargs="*", help="row ids to run (default: every row)")
        p.add_argument("--fix", action="store_true", help="pause / god-mode fixes, each re-read")
        p.add_argument("--allow-unmeasured", action="store_true")
        p.add_argument("--sidecar")
        p.add_argument("--backup-manifest")
        p.add_argument("--json", help="also write the rows here")
    sub.add_parser("backup")
    rp = sub.add_parser("restore")
    rp.add_argument("manifest")
    a = ap.parse_args(argv)
    P = Paths()
    if a.cmd == "backup":
        m = S.backup_configs(P.config_dir, P.backup_dir)
        print("backed up -> %s" % m)
        return 0
    if a.cmd == "restore":
        print(json.dumps(S.restore_configs(a.manifest)))
        return 0
    if a.sidecar:
        P.sidecar = a.sidecar
    if a.backup_manifest:
        P.backup_manifest = a.backup_manifest
    checks = []
    if a.cmd in ("offline", "all"):
        checks += run_offline(P, a.only)
    if a.cmd in ("live", "all"):
        from northstar_driver.session import FastSession
        with FastSession() as s:
            checks += run_live(s, P, a.seat, fix=a.fix, only=a.only)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump([c.as_dict() for c in checks], f, indent=1)
    return report(checks, a.allow_unmeasured)


if __name__ == "__main__":
    sys.exit(main())
