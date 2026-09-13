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
    r = subprocess.run(["python3", MODLIST_SWAP, "--restore", "--apply"],
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
    r = subprocess.run(["python3", MODLIST_SWAP, "--minimal", "--apply"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("modlist_swap.py --minimal --apply FAILED: %s"
                           % (r.stdout + r.stderr).strip())
    if package_ids:
        compose_test_list(list(package_ids))
    return r


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


def run_suite(suite, session, debug=False, anchor=None):
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
    """
    from suite import TestContext  # noqa: E402  (modcheck package, same dir)
    if anchor is None:
        anchor = _default_anchor(session)
    findings = []
    chains_out = []
    for name, fn in suite.chains:
        t = TestContext(session, anchor=anchor, debug=debug,
                        on_finding=findings.append)
        try:
            fn(t)
        finally:
            # MEASURED live 2026-09-12: a chain that raises during its own
            # SETUP (before any `with t.component()`) used to skip this
            # entirely -- the pit it had already spawned sat on the map
            # forever, and the NEXT run's read-backs got confused by a
            # stale pit/pawn from a run that technically failed. Build-up
            # and tear-down are absolute (spec 1b) even when the chain
            # itself is broken, not only when its components are.
            session.sweep()
        chains_out.append({"name": name,
                           "components": [c.as_dict() for c in t.components]})
    all_green = all(c["verdict"] == "PASS" or
                    (isinstance(c["verdict"], str) and c["verdict"].startswith("PASS"))
                    for chain in chains_out for c in chain["components"])
    return {"chains": chains_out, "all_green": all_green, "findings": findings}


def emit_verify(item_id, mod, config, result_summary, sheet_path, dry_run=False):
    n_pass = sum(1 for chain in result_summary["chains"]
                for c in chain["components"] if c["verdict"] != "FAIL"
                and c["verdict"] != "UNMEASURED")
    n_total = sum(len(chain["components"]) for chain in result_summary["chains"])
    result = "pass" if result_summary["all_green"] else "fail"
    cmd = ["python3", RIMFLOW_CLI, "verify", item_id,
          "--result", result, "--config", config, "--evidence", sheet_path]
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
        cmd = ["python3", RIMFLOW_CLI, "finding", "--from", item_id,
              "--name", name, "--type", "modcheck-failure",
              "--severity", "major"]
        if dry_run:
            filed.append({"cmd": cmd})
            continue
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("rimflow finding FAILED: %s"
                               % (r.stdout + r.stderr).strip())
        filed.append({"component": c.name})
    return filed


def run(mods, debug=False, dry_run=False):
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
                r = subprocess.run(
                    ["python3", os.path.join(_UTILS, "deploy_custom_mods.py"),
                     "--mod", mod_folder, "--apply"],
                    cwd=ROOT, capture_output=True, text=True)
                if r.returncode != 0:
                    raise RuntimeError(
                        "deploy of %s FAILED: %s"
                        % (mod_folder, (r.stdout + r.stderr).strip()[-500:]))
                package_ids.append(mod_package_id(mod_dir))
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
            from rimdrive import Session  # noqa: E402
            with Session(lock=None) as s:
                summary = run_suite(suite, s, debug=debug)
            results[mod_folder] = summary
            sheet_path = write_sheet(mod_folder, summary)
            emit_verify(item_id, mod_folder, "min+%s" % mod_folder, summary,
                       sheet_path)
            if summary["findings"]:
                file_findings(item_id, mod_folder, summary["findings"])
            record_run(mod_folder, mod_dir,
                      "%s@%d" % (mod_folder, int(time.time())),
                      summary["all_green"])
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
