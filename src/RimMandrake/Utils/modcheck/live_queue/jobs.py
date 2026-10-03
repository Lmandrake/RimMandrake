"""The ordered northstar live queue. One entry per job file; order is the order run_next.py offers them.

A job is DONE when its latest live record is MEASURED (PASS or FAIL -- a measured FAIL is a finding to file,
not a reason to re-run). UNMEASURED or never-run jobs are offered again. All jobs fit in ONE game session on
the minimal list with the suite mods composed in (prep_wsl.py), in this order.
"""
import json
import os

from common import ROOT, MEASURED, read_results

JOBS = [
    {"id": "J0_preflight", "file": "j0_preflight.py",
     "title": "Playing map, required tools, companion recorder, suite mods active",
     "fails_when": "any required tool is missing, the recorder is not installed, or a suite mod is not active"},
    {"id": "J1_situational_rerun", "file": "j1_situational_rerun.py",
     "title": "--situational re-run of every registered suite on the fixed runner",
     "fails_when": "a suite crashes, FlowWorks is refused, Antiquities' long chain is UNMEASURED by budget, "
                   "or a chain records a surprise whose detector is the chain's own declared act"},
    {"id": "J2_abort_proof", "file": "j2_abort_proof.py",
     "title": "deliberate hazards must trip their detector and abort with evidence; controls must not",
     "fails_when": "a hazard does not abort, aborts on the wrong detector, leaves no sidecar, or a control aborts"},
    {"id": "J3_bland_tile", "file": "j3_bland_tile.py",
     "title": "pick a flat dry tile, generate its map, clear wildlife, found a colony, prove it bland",
     "fails_when": "the map is not current, wildlife remains, no colonist stands on it, or ruins are present"},
    {"id": "J4_companion_live", "file": "j4_companion_live.py",
     "title": "companion-backed detectors fire live with via=pawn_census/damage_log/incident_queue_peek",
     "fails_when": "a direct-read detector does not fire, or fires without its direct-read evidence"},
    {"id": "J5_motion_frames", "file": "j5_motion_frames.py",
     "title": "FlowWorks canal fill-front frame sequence (capture stub, no judge)",
     "fails_when": "fewer than N valid frames, all frames byte-identical, or the fill state never moved"},
    {"id": "J6_bland_base", "file": "j6_bland_base.py",
     "title": "one-time: build the bland world, name the colony, save BLAND_NORTHSTAR_BASE (suites load it between runs)",
     "fails_when": "the colony is left unnamed or a naming dialog stays open, assert_bland fails, or no NEW save file appears "
                   "(or an existing save changes size)"},
]

SUITE_REGISTRY = os.path.join(ROOT, "infrastructure", "state", "modcheck_status.json")


def suite_mods():
    """The suites J1 re-runs: every mod in the modcheck status registry (13 on 2026-10-01). Derived, never listed."""
    with open(SUITE_REGISTRY, encoding="utf-8") as f:
        d = json.load(f)
    mods = sorted(d.get("mods", d))
    import re
    import runner
    out = []
    for m in mods:      # a standalone script (MessyConduit: own --live runner) has no `suite =`; it is not a modcheck suite
        try:
            src = open(os.path.join(runner.find_mod_dir(m), "validation.py"), encoding="utf-8").read()
        except Exception:                                       # noqa: BLE001
            out.append(m)       # unreadable: keep it, so J1 reports the load error instead of hiding it
            continue
        if re.search(r"^suite\s*=", src, re.M):
            out.append(m)
    return out


def latest(dry_run=False, path=None):
    out = {}
    for r in read_results(dry_run, path):
        out[r.get("job")] = r
    return out


def next_job(dry_run=False, path=None, skip=()):
    last = latest(dry_run, path)
    for j in JOBS:
        if j["id"] in skip:
            continue
        r = last.get(j["id"])
        if r is None or r.get("status") != MEASURED:
            return j
    return None
