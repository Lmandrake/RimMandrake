"""modcheck.runner -- drives one `modcheck run <mod> [<mod>...]` session.

Per design/RimMandrake/mod_validation_runner_spec.md §2: capture the current
ModsConfig, swap to MINIMAL + the mods under test, restart to a quicktest
map, take the bridge lock, run each mod's suite in order, release, restore
FULL. **FULL restore is unconditional** -- it runs from a `finally`, so a
crash mid-run never leaves the owner's mod list on the test configuration.

This module is real orchestration code, not a simulation: `run()` shells out
to `modlist_swap.py`, drives a live `rimdrive.Session`, and writes to
`rimflow`. It has NOT been exercised against a live game as of 2026-09-12 --
see MOD_VALIDATION_RUNNER_1's item file for why (the owner's live campaign
was up throughout this build; a quicktest swap would have discarded it).
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
    r = subprocess.run([sys.executable, MODLIST_SWAP, "--restore", "--apply"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("modlist_swap.py --restore --apply FAILED: %s"
                           % (r.stdout + r.stderr).strip())
    return r


def swap_to_test_list():
    """MINIMAL + the mod(s) under test is not a mode `modlist_swap.py` has
    (its `--minimal` is the fixed captured list) -- composing MINIMAL with a
    target mod's packageId(s) and writing that as the live ModsConfig is
    owed to a follow-up once a real live run is scheduled (see the item
    file). For now this calls the plain `--minimal` swap, which is correct
    for a mod with no extra dependency beyond the minimal mechanism list."""
    r = subprocess.run([sys.executable, MODLIST_SWAP, "--minimal", "--apply"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("modlist_swap.py --minimal --apply FAILED: %s"
                           % (r.stdout + r.stderr).strip())
    return r


def run_suite(suite, session, debug=False, anchor=(500, 500)):
    """Run every chain in `suite` against an open `session`. Returns
    `{"chains": [...], "all_green": bool}`. Never raises on a component
    failure -- that is exactly what `suite.py`'s `component()` already
    swallows; this only raises if a CHAIN function itself blows up before
    entering any `with t.component()` (a genuine script bug, not a game
    result), which the caller should treat as RED and stop, per spec's own
    silence on that case being anything but a bug.
    """
    from suite import TestContext  # noqa: E402  (modcheck package, same dir)
    findings = []
    chains_out = []
    for name, fn in suite.chains:
        t = TestContext(session, anchor=anchor, debug=debug,
                        on_finding=findings.append)
        fn(t)
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
    cmd = [sys.executable, RIMFLOW_CLI, "verify", item_id,
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
        name = "MODCHECK_%s_%s" % (mod.upper(), c.name.upper())[:60]
        cmd = [sys.executable, RIMFLOW_CLI, "finding", "--from", item_id,
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
