"""modcheck.runner -- drives one `modcheck run <mod> [<mod>...]` session.

Per design/RimMandrake/mod_validation_runner_spec.md §2: capture the current
ModsConfig, swap to MINIMAL + the mods under test, restart to a quicktest
map, take the bridge lock, run each mod's suite in order, release, restore
FULL. **FULL restore is unconditional** -- it runs from a `finally`, so a
crash mid-run never leaves the owner's mod list on the test configuration.

This module is real orchestration code, not a simulation: `run()` shells out
to `modlist_swap.py` and `rimflow`, and drives a live `rimdrive.Session`.

`run_suite()` (the part that actually drives the game) RAN LIVE 2026-09-12
against the Pits mod -- see MOD_VALIDATION_PIT_PILOT_1's item file for that
run's own findings. `run()`'s modlist-swap path (`swap_to_test_list()` /
`restore_full()`) and the `rimflow` calls (`emit_verify()`/
`file_findings()`) were fixed after a live crash (subprocess targets that
need plain `python3` were being launched via `sys.executable`, which is
`python.exe` in the process that can actually drive the bridge) but have
NOT been re-exercised live after that fix -- the successful Pits run
called `load_validation()`/`run_suite()` directly, bypassing `run()`'s
orchestration entirely, once the swap path was found broken. Whoever next
runs `cli.py run <mod>` for real is the first live test of the fixed
subprocess targets.

Every function below that does not itself need a socket is written to be
called and asserted on in isolation, which is what `selftest.py` does.
"""
import json
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_UTILS)))
RIMFLOW_CLI = os.path.join(ROOT, "src", "RimMandrake", "rimflow", "cli.py")
MODLIST_SWAP = os.path.join(_UTILS, "modlist_swap.py")
SHEET_DIR = os.path.join(ROOT, "Transient", "modcheck")
QUICKTEST_STARTER = os.path.join(os.path.dirname(_UTILS), "bridgetools", "prove_quicktest_world.py")


def _wsl_path(p):
    """`D:\\Luke\\dev\\x` -> `/mnt/d/Luke/dev/x` (a POSIX path passes through unchanged)."""
    import re
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p)
    if not m:
        return p
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))


def py_cmd(script, *args):
    """Command line for a script that must run under POSIX python3 (modlist_swap, rimflow and
    deploy_custom_mods import `fcntl`). Under Windows python.exe -- the only place the bridge is reachable --
    it is shelled through `wsl.exe python3` with the script path translated; elsewhere plain `python3`."""
    if os.name == "nt":
        return ["wsl.exe", "python3", _wsl_path(script)] + [str(a) for a in args]
    return ["python3", script] + [str(a) for a in args]


def ensure_playing_map(dry_run=False, _client=None, _starter=None):
    """If the bridge reports no Playing map, run the existing quicktest-world starter
    (`bridgetools/prove_quicktest_world.py`, exit 0 = Playing with a world) under THIS interpreter. The runner
    used to assume a map already existed (MEASURED 2026-10-01). Returns "playing" | "started" | "dry-run".
    Raises RuntimeError when the bridge cannot be asked or the starter fails -- never guesses."""
    if dry_run:
        return "dry-run"
    state = None
    try:
        if _client is None:
            import rimbridge_client as rb
            host, port, token = rb.resolve_endpoint()
            _client = rb.RimBridge(host=host, port=port, token=token, timeout=30.0)
            _client.connect()
        r = _client.call("rimworld/get_ui_state", {}) or {}
        if isinstance(r, dict) and r.get("content"):
            r = json.loads(r["content"][0]["text"])
        state = r.get("programState")
    except Exception as e:  # noqa: BLE001
        raise RuntimeError("ensure_playing_map: cannot ask the bridge for programState (%s: %s)"
                           % (type(e).__name__, e))
    if state == "Playing":
        return "playing"
    starter = _starter or (lambda: subprocess.run([sys.executable, QUICKTEST_STARTER], cwd=ROOT,
                                                  capture_output=True, text=True))
    r = starter()
    if r.returncode != 0:
        raise RuntimeError("quicktest world start FAILED (programState was %r): %s"
                           % (state, (r.stdout + r.stderr).strip()[-500:]))
    return "started"


def find_mod_dir(mod_folder_name):
    """A mod's source folder, by its repo folder name (not packageId) --
    `src/RimMandrake/<Folder>` or `src/RimStarWars/<Folder>` or
    `src/RimUtinni/<Folder>`, whichever exists. Refuses ambiguity rather
    than guessing between two tiers that both have a folder of this name."""
    hits = []
    for tier in ("RimMandrake", "RimStarWars", "RimUtinni"):
        cand = os.path.join(ROOT, "src", tier, mod_folder_name)
        if os.path.isdir(cand):
            hits.append(cand)
    if not hits:
        raise RuntimeError("no mod folder named %r under src/{RimMandrake,"
                           "RimStarWars,RimUtinni}" % mod_folder_name)
    if len(hits) > 1:
        raise RuntimeError("ambiguous: %r exists in more than one tier: %s"
                           % (mod_folder_name, hits))
    return hits[0]


def load_validation(mod_dir):
    """Import `validation.py` from `mod_dir` and return its `suite`
    (a `modcheck.suite.Suite`). Refuses a validation.py with no module-level
    `suite` -- a script that defines chains but never assigns them to that
    name would otherwise silently validate nothing."""
    import importlib.util
    path = os.path.join(mod_dir, "validation.py")
    if not os.path.isfile(path):
        raise RuntimeError("%s has no validation.py" % mod_dir)
    spec = importlib.util.spec_from_file_location(
        "modcheck_validation_%s" % os.path.basename(mod_dir), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    suite = getattr(mod, "suite", None)
    if suite is None:
        raise RuntimeError(
            "%s defines no module-level `suite` -- nothing to run" % path)
    return suite


def restore_full():
    """Unconditional: called from `run()`'s `finally`. Best-effort -- a
    failure here is loud (non-zero exit propagates to the caller) but never
    swallowed, because leaving the owner's mod list on MINIMAL silently is
    exactly the failure mode this function exists to prevent."""
    r = subprocess.run(py_cmd(MODLIST_SWAP, "--restore", "--apply"),
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("modlist_swap.py --restore --apply FAILED: %s"
                           % (r.stdout + r.stderr).strip())
    return r


def mod_package_id(mod_dir):
    """The packageId from the mod's About/About.xml -- the FIRST <packageId>
    in document order is the mod's own (later ones belong to <modDependencies>
    entries, as in Pits' About.xml where Ludeon.RimWorld appears below)."""
    import re
    about = os.path.join(mod_dir, "About", "About.xml")
    with open(about, encoding="utf-8") as f:
        m = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", f.read())
    if not m:
        raise RuntimeError("%s has no <packageId>" % about)
    return m.group(1).lower()


def mod_dependency_ids(mod_dir):
    """Hard `<modDependencies>` packageIds of the mod's About.xml, lowercased, in document order, minus the
    base game and DLCs (`Ludeon.*`, always in the list) and the mod's own id. `run()` composes these BEFORE
    the mod: appending only the mod's own id left every donor gene / def a suite depends on out of the load
    (MEASURED 2026-10-01: StarWarsRaces read 24 of its xenotype's 38 genes). RimWorld drops an id whose
    folder is not installed, so a missing dependency stays visible only as the suite's own failure."""
    import re
    about = os.path.join(mod_dir, "About", "About.xml")
    with open(about, encoding="utf-8") as f:
        xml = f.read()
    own = mod_package_id(mod_dir)
    m = re.search(r"<modDependencies>(.*?)</modDependencies>", xml, re.S)
    out = []
    for pid in re.findall(r"<packageId>\s*([^<\s]+)\s*</packageId>", m.group(1) if m else ""):
        pid = pid.lower()
        if pid.startswith("ludeon.") or pid == own or pid in out:
            continue
        out.append(pid)
    return out


def composed_into(mod_folder):
    """`None`, or `(compose_name, packageId)` when this dev folder ships FOLDED INTO a composed mod
    (Biomes.compose.json): such a folder is refused as a standalone deploy and its own packageId is not a
    mod the game can load, so the run must deploy the composed mod and compose ITS id instead."""
    sys.path.insert(0, _UTILS)
    import biomes_compose
    src = os.path.join(ROOT, "src")
    try:
        manifest = biomes_compose.load_manifest(src)
        folded = biomes_compose.folded_sources(src)
    except Exception:     # noqa: BLE001 - a broken manifest must not hide an ordinary mod
        return None
    if not manifest or mod_folder not in folded:
        return None
    return "biomes", manifest["about"]["packageId"].lower()


def compose_test_list(package_ids, config_path=None):
    """Append `package_ids` (the mods under test) to the live ModsConfig's
    <activeMods>, after `modlist_swap.py --minimal --apply` has made MINIMAL
    live. Appending at the END is deliberate: our mods patch/extend the
    mechanism list, never the other way round, so they load after all of it
    (rimworld-start-prep: a patch belongs after what it patches). Ids already
    present are not duplicated. ⚠️ ModsConfig names the NEXT load only -- an
    id whose mod folder is not deployed is silently dropped by RimWorld, so
    `run()` deploys before composing."""
    import re
    if config_path is None:
        sys.path.insert(0, _UTILS)
        from game_paths import MODS_CONFIG
        config_path = MODS_CONFIG
    MODS_CONFIG = config_path
    with open(MODS_CONFIG, encoding="utf-8") as f:
        xml = f.read()
    live = set(re.findall(r"<li>([^<]+)</li>", xml))
    add = [p for p in package_ids if p not in live]
    if add:
        lis = "".join("    <li>%s</li>\n" % p for p in add)
        xml = xml.replace("</activeMods>", lis + "  </activeMods>")
        tmp = MODS_CONFIG + ".modcheck.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(xml)
        os.replace(tmp, MODS_CONFIG)
    # read back -- ModsConfig is the instrument for the NEXT load
    with open(MODS_CONFIG, encoding="utf-8") as f:
        now = set(re.findall(r"<li>([^<]+)</li>", f.read()))
    missing = [p for p in package_ids if p not in now]
    if missing:
        raise RuntimeError("compose_test_list read-back missing %s" % missing)
    return add


def swap_to_test_list(package_ids=()):
    """MINIMAL + the mod(s) under test: `modlist_swap.py --minimal --apply`
    (which captures FULL first), then `compose_test_list` appends the mods
    under test. With no `package_ids` this is the plain minimal swap."""
    r = subprocess.run(py_cmd(MODLIST_SWAP, "--minimal", "--apply"),
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("modlist_swap.py --minimal --apply FAILED: %s"
                           % (r.stdout + r.stderr).strip())
    if package_ids:
        compose_test_list(list(package_ids))
    return r


def northstar_for(mod):
    """`(walk_path, parsed_north_star)` for `mod`, or `(None, None)` when it has
    no validation walk at all. A mod with a walk but no `## north star` section
    parses to `present=False`, which binds nothing -- the per-mod rollout the
    owner ruled for on 2026-09-15 means an untouched mod must stay untouched."""
    import northstar  # noqa: E402
    walk = northstar.find_walk(ROOT, mod)
    if not walk:
        return None, None
    return walk, northstar.parse(walk)


def visual_floor(suite, ns):
    """Answer the VISUAL floor for one mod, offline, before its run.

    Returns `{"bar", "uncovered", "orphans"}`. A DRAFT or absent section yields
    an empty bar and therefore no findings: `northstar.bar_for`'s rule, restated
    here because this is the only place a run can be refused over appearance.

    `orphans` is checked against must-show AND cannot-show ids, because a
    component legitimately claims a cannot-show line -- photographing the defect
    he would reject is exactly how that line gets tested.
    """
    import floor       # noqa: E402
    import northstar   # noqa: E402
    if not ns or ns["state"] != northstar.VALIDATED:
        return {"bar": [], "uncovered": [], "orphans": []}
    bar = list(ns["must_show"])
    declared = bar + list(ns["cannot_show"])
    components = suite.components_declared()
    return {"bar": bar,
            "uncovered": floor.uncovered_shows(bar, components),
            "orphans": floor.orphan_shows(declared, components)}


def refusal(fl):
    """The one-line reason this mod cannot be run, or "" if it can.

    An uncovered must-show line is as fatal as an uncovered Mod Settings toggle
    (spec §3): the mod's stated experience has no test. An orphaned `shows=` is
    a lint error for the same reason a patch that matches nothing is -- it
    claims to cover something that does not exist.
    """
    parts = []
    if fl["uncovered"]:
        parts.append("validated must-show lines no component claims: %s"
                     % ", ".join(fl["uncovered"]))
    if fl["orphans"]:
        parts.append("`shows=` ids absent from the validated checklist: %s"
                     % ", ".join(fl["orphans"]))
    return "; ".join(parts)


def apply_judgement(summary, must_show_text, cannot_show_text=None,
                    judge_runner=None, kinds=None):
    """Grade the run's screenshots and fold the result into `all_green`.

    Before this existed, `all_green` was the state assertions alone, so a mod
    whose state was right and whose appearance was absent went GREEN -- the pit.
    Both halves are now required, and neither can stand in for the other.

    A run where no component claims anything judges nothing, `visual_all_green`
    is trivially true, and `all_green` is untouched: pre-2026-09-15 behaviour for
    every mod he has not validated.
    """
    import judge  # noqa: E402
    visual = judge.judge_run(summary, must_show_text or {}, cannot_show_text or {},
                             cwd=ROOT, runner=judge_runner, kinds=kinds)
    summary["visual"] = visual
    summary["visual_all_green"] = judge.visual_all_green(visual)
    summary["state_all_green"] = summary["all_green"]
    summary["all_green"] = bool(summary["all_green"] and
                                summary["visual_all_green"])
    return summary


FIXTURE_LEDGER = os.path.join(SHEET_DIR, "fixtures.json")


def load_fixtures(ticks, path=None):
    """Pawn ids earlier runs spawned and tore down on THIS game. Thing ids restart with every new game,
    so a clock that went BACKWARDS means a new game and the ledger is discarded rather than risk an old
    id exempting a real colonist."""
    path = path or FIXTURE_LEDGER
    try:
        with open(path) as f:
            d = json.load(f)
    except (OSError, ValueError):
        return set()
    if ticks is None or d.get("tick") is None or ticks < d["tick"]:
        return set()
    return set(d.get("ids", []))


def save_fixtures(ids, ticks, path=None):
    path = path or FIXTURE_LEDGER
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"tick": ticks, "ids": sorted(ids)}, f)
    os.replace(tmp, path)


def _default_anchor(session):
    """MEASURED live 2026-09-12: a fixed guess (originally (500, 500)) was
    out of bounds on a 174x174 quicktest map and `get_cell_info` raising a
    bare `KeyError` on that made it look like an unrelated bug. Map centre
    is always in-bounds regardless of quicktest size; ask the map rather
    than guess a constant."""
    r = session.call("jawa/map_info")
    if not r.get("success"):
        return 100, 100   # last-resort fallback if map_info itself fails
    return r.get("sizeX", 200) // 2, r.get("sizeZ", 200) // 2


def run_suite(suite, session, debug=False, anchor=None, mod=None,
              judge_runner=None, situational=False, policy="abort", bland_world=False):
    """Run every chain in `suite` against an open `session`. Returns
    `{"chains": [...], "all_green": bool}`. Never raises on a component
    failure -- that is exactly what `suite.py`'s `component()` already
    swallows; this only raises if a CHAIN function itself blows up before
    entering any `with t.component()` (a genuine script bug, not a game
    result), which the caller should treat as RED and stop, per spec's own
    silence on that case being anything but a bug.

    `anchor`: (x, z) to build the test area around. Defaults to the current
    map's centre (queried live) rather than a hardcoded guess -- see
    `_default_anchor`.

    `situational`: wrap every chain in a `watch.Watch` (bland map, python-enforced tick budget, a detector
    sweep every chunk, evidence + screenshot on any surprise). OFF by default until the abort-only pilot has
    run live; `policy` is 'abort' (a surprise ends the component UNMEASURED) or 'record' (diagnostics).
    A chain whose map cannot be made bland records every component UNMEASURED, never FAIL against the mod.

    `mod`: the mod's folder name. Supplying it brings in the VISUAL half -- the
    floor is checked before any chain runs (an uncovered validated must-show
    line returns `refused` and drives nothing), and the judge grades the
    screenshots at the end. ⚠️ Omitting it gives a state-only verdict, which is
    exactly the hole the pit fell through; `run()` always passes it, and the one
    live Pits run of 2026-09-12 bypassed `run()` to call this directly.
    """
    from suite import TestContext  # noqa: E402  (modcheck package, same dir)
    walk, ns = northstar_for(mod) if mod else (None, None)
    if mod:
        fl = visual_floor(suite, ns)
        why = refusal(fl)
        if why:
            return {"chains": [], "all_green": False, "findings": [],
                    "refused": why, "visual": [], "visual_all_green": False,
                    "state_all_green": False, "walk": walk, "bar": fl["bar"]}
    anchor_given = anchor
    if anchor is None:
        anchor = _default_anchor(session)
    findings = []
    chains_out = []
    if situational and anchor_given is None:
        # MEASURED 2026-10-01: the map centre is where the colony spawns; an explosion test there killed
        # two starting colonists. Pick the point farthest from every colonist instead.
        try:
            import helpers as _H  # noqa: E402
            ax, az, dist = _H.safe_anchor(session)
            if dist >= 0:
                anchor = (ax, az)
        except Exception:     # noqa: BLE001 - keep the centre rather than fail the run over a heuristic
            pass
    watch_dir = os.path.join(SHEET_DIR, "surprises", time.strftime("%Y%m%dT%H%M%S"))
    fixtures = set()      # pawns spawned and later torn down (this run, plus earlier runs on this game):
    #                       their corpses are the harness's own litter, never contamination
    if situational:
        try:
            import clockgate  # noqa: E402
            fixtures = load_fixtures(clockgate.read_ticks(session))
        except Exception:     # noqa: BLE001 - no clock: start with none, never guess
            fixtures = set()
    world_before = None
    if bland_world:
        # Re-establish AND prove the featureless world before this suite (no game relaunch): hostiles, wildlife,
        # corpses, fires, queued incidents, injuries and hunger left by the previous suite or hazard job are removed
        # and read back. A world that cannot be made bland records every chain UNMEASURED, never FAIL.
        import bland_world as _BW  # noqa: E402
        world_before = _BW.reset(session, expected_ids=sorted(fixtures))
    for name, fn in suite.chains:
        watch = None
        if situational:
            from watch import Watch  # noqa: E402
            cap_kw = ({"session_cap": suite.chain_caps[name]}
                      if name in getattr(suite, "chain_caps", {}) else {})
            watch = Watch(session, anchor, watch_dir, mod=mod or suite.name, chain=name, policy=policy,
                          expected_ids=sorted(fixtures), resurrect=True, **cap_kw)
            watch.__enter__()
        t = TestContext(session, anchor=anchor, debug=debug,
                        on_finding=findings.append, watch=watch)
        if watch is not None and not watch.bland:
            t.upstream_failed = True
            t.upstream_reason = ("could not establish a bland map -- not a verdict on the mod: %s"
                                 % "; ".join(watch.report.problems)[:300])
        try:
            try:
                fn(t)
            except Exception as e:  # noqa: BLE001
                # A check or a wait OUTSIDE any `with t.component()` (chain setup) used to kill the whole
                # run on the first failure (Droidworks' salvage_on_death, MEASURED live 2026-10-01). A failed
                # expectation or a detector abort there is a RESULT: record it as a component and go on.
                # Any other exception is still a genuine script bug and still propagates.
                from suite import Component, FAIL, UNMEASURED  # noqa: E402
                surprise = getattr(e, "is_surprise_abort", False)
                if not (surprise or type(e).__name__ == "ExpectationFailed"):
                    raise
                comp = Component("<chain setup, outside any component>", None, False)
                if surprise:
                    comp.verdict, comp.surprises = UNMEASURED, e.summary()
                    comp.detail = "%s: %s" % (e.kind, e)
                else:
                    comp.verdict, comp.detail = FAIL, "%s: %s" % (type(e).__name__, e)
                    findings.append(comp)
                t.components.append(comp)
                t.upstream_failed = True
            if watch is not None and not t.upstream_failed:
                watch.final()
        finally:
            fixtures.update(l["id"] for l in getattr(session, "litter", []) if l.get("kind") == "pawn")
            if watch is not None:
                fixtures.update(watch.fixture_ids)
            # MEASURED live 2026-09-12: a chain that raises during its own
            # SETUP (before any `with t.component()`) used to skip this
            # entirely -- the pit it had already spawned sat on the map
            # forever, and the NEXT run's read-backs got confused by a
            # stale pit/pawn from a run that technically failed. Build-up
            # and tear-down are absolute (spec 1b) even when the chain
            # itself is broken, not only when its components are.
            session.sweep()
            if watch is not None:
                watch.__exit__(None, None, None)
        chains_out.append({"name": name,
                           "components": [c.as_dict() for c in t.components],
                           "situational": watch.summary() if watch is not None else None})
    if situational:
        try:
            import clockgate  # noqa: E402
            save_fixtures(fixtures, clockgate.read_ticks(session))
        except Exception:     # noqa: BLE001
            pass
    all_green = all(c["verdict"] == "PASS" or
                    (isinstance(c["verdict"], str) and c["verdict"].startswith("PASS"))
                    for chain in chains_out for c in chain["components"])
    summary = {"chains": chains_out, "all_green": all_green,
               "findings": findings, "refused": "", "walk": walk}
    if bland_world:
        try:
            after = _BW.assert_world(session, expected_ids=sorted(fixtures))
        except Exception as e:                                  # noqa: BLE001
            after = ["UNMEASURED: assert_world raised %r" % (e,)]
        summary["bland_world"] = {"before": world_before, "after_problems": after}
    if mod:
        import northstar  # noqa: E402
        must_text, cannot_text = (northstar.text_for(walk) if walk
                                  else ({}, {}))
        apply_judgement(summary, must_text, cannot_text,
                        judge_runner=judge_runner,
                        kinds=northstar.kinds_for(walk) if walk else {})
    return summary


def emit_verify(item_id, mod, config, result_summary, sheet_path, dry_run=False):
    n_pass = sum(1 for chain in result_summary["chains"]
                for c in chain["components"] if c["verdict"] != "FAIL"
                and c["verdict"] != "UNMEASURED")
    n_total = sum(len(chain["components"]) for chain in result_summary["chains"])
    result = "pass" if result_summary["all_green"] else "fail"
    cmd = py_cmd(RIMFLOW_CLI, "verify", item_id,
                 "--result", result, "--config", config, "--evidence", _wsl_path(sheet_path)
                 if os.name == "nt" else sheet_path)
    if dry_run:
        return {"cmd": cmd, "n_pass": n_pass, "n_total": n_total}
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("rimflow verify FAILED: %s" % (r.stdout + r.stderr).strip())
    return {"n_pass": n_pass, "n_total": n_total}


def file_findings(item_id, mod, findings, dry_run=False):
    """One `rimflow finding` per failed component, per spec §1's "auto-file
    a rimflow finding (screenshot attached) and CONTINUE the run"."""
    filed = []
    for c in findings:
        name = ("MODCHECK_%s_%s" % (mod.upper(), c.name.upper()))[:60]
        cmd = py_cmd(RIMFLOW_CLI, "finding", "--from", item_id,
                     "--name", name, "--type", "modcheck-failure",
                     "--severity", "major")
        if dry_run:
            filed.append({"cmd": cmd})
            continue
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("rimflow finding FAILED: %s"
                               % (r.stdout + r.stderr).strip())
        filed.append({"component": c.name})
    return filed


def run(mods, debug=False, dry_run=False, situational=False, policy="abort"):
    """`mods`: list of (mod_folder_name, item_id) pairs. Full orchestration
    per spec §2. `dry_run=True` skips every live/subprocess side effect and
    is how `selftest.py` exercises the sequencing without a game or a
    filesystem write outside `Transient/`."""
    from status import record_run  # noqa: E402

    results = {}
    if not dry_run:
        swap_to_test_list()
    try:
        if not dry_run:
            # Deploy each mod, THEN compose its packageId into the live
            # list: ModsConfig names the next load only, and RimWorld
            # silently drops an activeMods id whose folder is absent from
            # the game's Mods directory (the repo is never what the game
            # loads). Inside the try so any failure still restores FULL.
            # ⚠️ Composition changes the NEXT load -- the caller owns the
            # game restart between run()'s swap and the first Session, and
            # a locked companion DLL (game still up) fails the deploy here
            # loudly rather than the suite failing silently later.
            package_ids = []
            for mod_folder, _item in mods:
                mod_dir = find_mod_dir(mod_folder)
                folded = composed_into(mod_folder)
                deploy_args = (("--compose", folded[0]) if folded
                               else ("--mod", mod_folder))
                r = subprocess.run(
                    py_cmd(os.path.join(_UTILS, "deploy_custom_mods.py"),
                           *deploy_args, "--apply"),
                    cwd=ROOT, capture_output=True, text=True)
                if r.returncode != 0:
                    raise RuntimeError(
                        "deploy of %s FAILED: %s"
                        % (mod_folder, (r.stdout + r.stderr).strip()[-500:]))
                # dependencies first, then the mod: a composed folder loads as its composed mod
                package_ids.extend(d for d in mod_dependency_ids(mod_dir) if d not in package_ids)
                own = folded[1] if folded else mod_package_id(mod_dir)
                if own not in package_ids:
                    package_ids.append(own)
            compose_test_list(package_ids)
        for mod_folder, item_id in mods:
            if dry_run:
                # Deliberately does not resolve the mod folder or import its
                # validation.py -- dry_run proves the ORCHESTRATION sequence
                # (swap/restore/status calls) without needing a real mod on
                # disk, which is what lets a mod-agnostic selftest exercise it.
                results[mod_folder] = {"chains": [], "all_green": True,
                                       "findings": [], "dry_run": True}
                continue
            mod_dir = find_mod_dir(mod_folder)
            suite = load_validation(mod_dir)
            walk, ns = northstar_for(mod_folder)
            fl = visual_floor(suite, ns)
            why = refusal(fl)
            if why:
                # Refused BEFORE the game is touched: a mod whose stated
                # experience has no test cannot be validated by running it.
                summary = {"chains": [], "all_green": False, "findings": [],
                           "refused": why, "visual": [],
                           "visual_all_green": False, "state_all_green": False,
                           "walk": walk, "bar": fl["bar"]}
                results[mod_folder] = summary
                record_run(mod_folder, mod_dir,
                          "%s@%d" % (mod_folder, int(time.time())),
                          False, walk=walk, refused=why)
                continue
            ensure_playing_map()
            from rimdrive import Session  # noqa: E402
            with Session(lock=None) as s:
                summary = run_suite(suite, s, debug=debug, mod=mod_folder,
                                    situational=situational, policy=policy)
            if situational:
                try:           # SHADOW-mode Jev routing of FAIL components; absent key => one UNAVAILABLE row
                    import jev_triage  # noqa: E402
                    summary["jev_shadow"] = jev_triage.triage_summary(summary)
                except Exception:   # noqa: BLE001 - Jev must never be able to break a run
                    summary["jev_shadow"] = []
            results[mod_folder] = summary
            sheet_path = write_sheet(mod_folder, summary)
            emit_verify(item_id, mod_folder, "min+%s" % mod_folder, summary,
                       sheet_path)
            if summary["findings"]:
                file_findings(item_id, mod_folder, summary["findings"])
            record_run(mod_folder, mod_dir,
                      "%s@%d" % (mod_folder, int(time.time())),
                      summary["all_green"], walk=walk)
    finally:
        if not dry_run:
            restore_full()
    return results


def write_sheet(mod, summary):
    from report import render  # noqa: E402
    os.makedirs(SHEET_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = os.path.join(SHEET_DIR, "%s_%s.html" % (mod, stamp))
    with open(path, "w", encoding="utf-8") as f:
        f.write(render(mod, summary))
    return path
