"""rollout_gate: may `modcheck run` default to --situational yet? (NORTHSTAR_SITUATIONAL_ROLLOUT_1)

The item: "Flip modcheck --situational to default after an abort-only pass over every suite". This reads the record
of that pass; it never touches the game, so it is a read-only live-proof:

    python3 src/RimMandrake/Utils/modcheck/live_queue/rollout_gate.py [--results <live_queue_results.jsonl>]

Exit 0 when the LATEST live `situational_rerun` record (that job always runs --policy abort) satisfies all of:
  * it is MEASURED PASS (its own judge: no suite crashed, every chain bland, every surprise has its evidence, ...);
  * it ran on a commit that already holds the newest change to the situational envelope (ENVELOPE files), so a pass
    on an older envelope does not license the flip;
  * its digests cover EVERY modcheck suite on disk that composes onto the minimal list (suite_set.py; on 2026-11-02
    the status registry situational_rerun then read offered 57 suites of 105 on disk);
  * the registry holds no key whose mod folder is gone (a dead key makes every pass fail "no suite raised").
Exit 1 otherwise, printing every reason; exit 2 when there is no record at all (nothing was measured).
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import MEASURED, PASS, ROOT, read_results   # noqa: E402

REGISTRY = os.path.join(ROOT, "infrastructure", "state", "modcheck_status.json")
# the code a situational verdict depends on: a pass recorded before the newest change here proves an older envelope
ENVELOPE = ["src/RimMandrake/Utils/modcheck/" + p for p in
            ("runner.py", "watch.py", "detectors.py", "clockgate.py", "helpers.py", "surprise.py", "contract.py",
             "bland_world.py", "live_queue/situational_rerun.py")]
JOB_IDS = ("situational_rerun", "J1_situational_rerun")
SUITE_RE = re.compile(r"^suite\s*=", re.M)


def disk_suites(root=ROOT):
    """The suites the pass owes: suite_set.py's disk-derived set (a suite whose walk doc says `list: full`, or whose
    closure needs a donor the minimal list lacks, runs on its own list, not in the shared minimal session)."""
    import suite_set
    return set(suite_set.situational_suites(root))


def dead_keys(registry_keys, root=ROOT):
    """Registry keys with no mod folder in any tier: runner.find_mod_dir would raise on every pass."""
    tiers = [d for d in glob.glob(os.path.join(root, "src", "Rim*")) if os.path.isdir(d)]
    return sorted(k for k in registry_keys if not any(os.path.isdir(os.path.join(t, k)) for t in tiers))


def latest_rerun(records):
    live = [r for r in records if r.get("job") in JOB_IDS and not r.get("dry_run")]
    return live[-1] if live else None


def envelope_head(root=ROOT):
    r = subprocess.run(["git", "-C", root, "log", "-1", "--format=%H", "--"] + ENVELOPE,
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip() or None


def is_ancestor(old, new, root=ROOT):
    """True when `old` is `new` or an ancestor of it; None when git cannot say (unknown sha)."""
    r = subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", old, new],
                       capture_output=True, text=True, timeout=60)
    return {0: True, 1: False}.get(r.returncode)


def evaluate(rec, suites, registry_keys, dead, env_sha, ancestor):
    """-> list of problems (empty = the flip is licensed). Pure: every input is passed in."""
    if rec is None:
        return ["no live situational_rerun record"]
    probs = []
    if rec.get("status") != MEASURED or rec.get("verdict") != PASS:
        probs.append("latest situational_rerun is %s %s (failed: %s; unmeasured: %s)"
                     % (rec.get("status"), rec.get("verdict"), ", ".join(rec.get("failed") or []) or "-",
                        rec.get("unmeasured_reason") or "-"))
    ev = rec.get("evidence") or {}
    sha = (((ev.get("run_identity") or {}).get("git")) or {}).get("sha")
    if not sha:
        probs.append("the record carries no git sha (run_identity.git): cannot tell which envelope it proved")
    elif env_sha:
        a = ancestor(env_sha, sha)
        if a is None:
            probs.append("git cannot relate the run's sha %s to the envelope head %s" % (sha[:12], env_sha[:12]))
        elif not a:
            probs.append("the run's sha %s predates the newest envelope change %s" % (sha[:12], env_sha[:12]))
    ran = {d.get("mod") for d in (ev.get("digests") or [])}
    missing = sorted(set(suites) - ran)
    if missing:
        unreg = [m for m in missing if m not in registry_keys]
        probs.append("%d suite(s) never ran in the pass: %s%s" % (
            len(missing), ", ".join(missing),
            (" (%d of them never recorded in the status registry)" % len(unreg))
            if unreg else ""))
    if dead:
        probs.append("dead registry key(s) (no mod folder): %s -- modcheck cli.py rename-key/forget-key" % ", ".join(dead))
    return probs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default=None, help="live_queue_results.jsonl (default: this checkout's live file)")
    a = ap.parse_args(argv)
    with open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)
    keys = set(reg.get("mods", reg))
    rec = latest_rerun(read_results(False, a.results))
    probs = evaluate(rec, disk_suites(), keys, dead_keys(keys), envelope_head(), is_ancestor)
    if rec is None:
        print("UNMEASURED rollout_gate: no live situational_rerun record in %s" % (a.results or "the live results file"))
        return 2
    print("%s rollout_gate: record %s" % ("PASS" if not probs else "FAIL", rec.get("finished")))
    for p in probs:
        print("  - " + p)
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main())
