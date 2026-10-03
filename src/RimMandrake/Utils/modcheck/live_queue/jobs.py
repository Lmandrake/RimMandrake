"""The ordered northstar live queue. One entry per job file; order is the order run_next.py offers them.

A job is DONE when its latest live record is MEASURED (PASS or FAIL -- a measured FAIL is a finding to file,
not a reason to re-run). UNMEASURED or never-run jobs are offered again. All jobs fit in ONE game session on
the minimal list with the suite mods composed in (prep_wsl.py), in this order.
"""
import json
import os

from common import ROOT, MEASURED, read_results

JOBS = [
    {"id": "preflight", "file": "preflight.py",
     "title": "Playing map, required tools, companion recorder, suite mods active",
     "fails_when": "any required tool is missing, the recorder is not installed, or a suite mod is not active"},
    {"id": "situational_rerun", "file": "situational_rerun.py",
     "title": "--situational re-run of every registered suite on the fixed runner",
     "fails_when": "a suite crashes, FlowWorks is refused, Antiquities' long chain is UNMEASURED by budget, "
                   "or a chain records a surprise whose detector is the chain's own declared act"},
    {"id": "abort_proof", "file": "abort_proof.py",
     "title": "deliberate hazards must trip their detector and abort with evidence; controls must not",
     "fails_when": "a hazard does not abort, aborts on the wrong detector, leaves no sidecar, or a control aborts"},
    {"id": "bland_tile", "file": "bland_tile.py",
     "title": "pick a flat dry tile, generate its map, clear wildlife, found a colony, prove it bland",
     "fails_when": "the map is not current, wildlife remains, no colonist stands on it, or ruins are present"},
    {"id": "companion_live", "file": "companion_live.py",
     "title": "companion-backed detectors fire live with via=pawn_census/damage_log/incident_queue_peek",
     "fails_when": "a direct-read detector does not fire, or fires without its direct-read evidence"},
    {"id": "motion_frames", "file": "motion_frames.py",
     "title": "FlowWorks canal fill-front frame sequence (capture stub, no judge)",
     "fails_when": "fewer than N valid frames, all frames byte-identical, or the fill state never moved"},
    {"id": "bland_base", "file": "bland_base.py",
     "title": "one-time: build the bland world, name the colony, save BLAND_NORTHSTAR_BASE (suites load it between runs)",
     "fails_when": "the colony is left unnamed or a naming dialog stays open, assert_bland fails, or no NEW save file appears "
                   "(or an existing save changes size)"},
]

# Historical records (live_queue_results.jsonl, per-job outdirs) carry the pre-2026-10-03 ids; map them forward.
OLD_IDS = {"J0_preflight": "preflight", "J1_situational_rerun": "situational_rerun", "J2_abort_proof": "abort_proof",
           "J3_bland_tile": "bland_tile", "J4_companion_live": "companion_live", "J5_motion_frames": "motion_frames",
           "J6_bland_base": "bland_base"}


def canonical_id(job_id):
    return OLD_IDS.get(job_id, job_id)


SUITE_REGISTRY = os.path.join(ROOT, "infrastructure", "state", "modcheck_status.json")


def suite_mods():
    """The suites situational_rerun re-runs: every mod in the modcheck status registry (13 on 2026-10-01). Derived, never listed."""
    with open(SUITE_REGISTRY, encoding="utf-8") as f:
        d = json.load(f)
    mods = sorted(d.get("mods", d))
    import re
    import runner
    out = []
    for m in mods:      # a standalone script with no `suite =` is not a modcheck suite (MessyConduit has one since 2026-10-03)
        try:
            src = open(os.path.join(runner.find_mod_dir(m), "validation.py"), encoding="utf-8").read()
        except Exception:                                       # noqa: BLE001
            out.append(m)       # unreadable: keep it, so situational_rerun reports the load error instead of hiding it
            continue
        if re.search(r"^suite\s*=", src, re.M):
            out.append(m)
    return out


def latest(dry_run=False, path=None):
    out = {}
    for r in read_results(dry_run, path):
        out[canonical_id(r.get("job"))] = r
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
