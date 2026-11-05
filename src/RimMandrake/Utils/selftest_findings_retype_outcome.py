#!/usr/bin/env python3
"""selftest_findings_retype_outcome.py - a finding given an outcome (retyped out of the alarm's types, or routed by a
findings_fold decide) reads as triaged (class guard of OPS_FINDINGS_DIAGNOSE_XZLM, the repeatedly fired UNTRIAGED alarm
on flow.untriaged_findings).

Folds the COMMITTED ledger and decisions of this tree with findings_fold, together with the testq done records (a
finding's signature, and so the decide keyed on it, is cut from its done record; dir from --done, else the fold's own
queue_dir()), publishes the table into a temp dir and asks findings_fold.no_outcome, the alarm's own answer:
  R1 the instances: STEVE_LANE_SYNC_REFUSED_5E2C71 (retyped RESOLVED_LANE_HEALTHY) and the three steve-targeted FlowWorks
     FAILs of 2026-11-05 (routed by decide) have an outcome;
  R2 the class: every finding whose name carries a later retype out of the finding types reads with an outcome;
  R3 the class: every finding whose signature a decision names reads with an outcome;
  R0 the instrument sees: >10000 events, >100 findings, >100 done records, else exit 2 (a blind 0 is not a pass).
Replay an instance with `--drop-retype NAME` (its retypes withheld) or `--drop-decide NAME` (the decisions on its
signature withheld): R1 must fail (exit 1).
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(HERE, "pulse"), os.path.join(ROOT, "src", "RimMandrake", "rimflow")]
os.environ["RIMFLOW_LEDGER"] = os.path.join(ROOT, "infrastructure", "state", "ledger", "events.jsonl")
import findings_fold as ff  # noqa: E402
import model  # noqa: E402
import pulse_core as pc  # noqa: E402

INSTANCES = ("STEVE_LANE_SYNC_REFUSED_5E2C71", "FLOWWORKS_CROPS_IRRIGATE_THEN_DROWN_FAILS_2B0937",
             "FLOWWORKS_CROPS_IRRIGATE_THEN_DROWN_FAILS_54F48C", "FLOWWORKS_FINDS_OFF_NONE_FAILS_2B0937")


def fold(rules, done, keep=lambda e: True, keep_dec=lambda d: True):
    """-> (names with no outcome, table) from a fold of this tree's ledger, without the events/decisions dropped."""
    read = model.read
    model.read = lambda *a, **k: [e for e in read(*a, **k) if keep(e)]
    try:
        dec = [d for d in ff.read_decisions(ff.decisions_path(rules)) if keep_dec(d)]
        finds, spawns, states, timeline = ff.read_ledger(rules)
        t = ff.fold(finds, spawns, states, done, dec, rules, ff.utcnow(), timeline)
    finally:
        model.read = read
    d = tempfile.mkdtemp(prefix="retype_outcome_")
    with open(os.path.join(d, ff.REPORT), "w", encoding="utf-8") as f:
        f.write(ff.render_report(t))
    return ff.no_outcome([e for e in EVENTS if keep(e)], out=d), t


EVENTS = []


def main(argv):
    global EVENTS
    arg = lambda k: argv[argv.index(k) + 1] if k in argv else None  # noqa: E731
    drop_rt, drop_dc = arg("--drop-retype"), arg("--drop-decide")
    rules = ff.load_rules()
    qd = arg("--done") or ff.queue_dir()
    try:
        done = ff.read_done(qd)
    except ff.Unmeasured as e:
        print("R0 BLIND: %s" % e)
        return 2
    EVENTS = pc.read_ledger([Path(ROOT)])
    finds = [e for e in EVENTS if e.get("event") == "finding"]
    alarm = [e for e in finds if e.get("type") in rules["finding_types"]]
    alarmed = {e.get("name") for e in alarm}
    if len(EVENTS) < 10000 or len(alarm) < 100 or len(done) < 100 or not set(INSTANCES) <= alarmed:
        print("R0 BLIND: %d events, %d findings, %d done records in %s, instances absent %s"
              % (len(EVENTS), len(alarm), len(done), qd, sorted(set(INSTANCES) - alarmed)))
        return 2
    last = {}
    for e in finds:                                     # the ledger is in order: a name's last finding event wins
        last[e.get("name")] = e.get("type")
    retyped = {n for n in alarmed if last.get(n) not in rules["finding_types"]}
    _, t0 = fold(rules, done)
    sig = lambda n: (t0["raw"].get(n) or {}).get("sig")  # noqa: E731
    decided_sigs = {d.get("sig") for d in ff.read_decisions(ff.decisions_path(rules))}
    decided = {n for n in alarmed if sig(n) and sig(n) in decided_sigs}
    keep = lambda e: True  # noqa: E731
    keep_dec = lambda d: True  # noqa: E731
    if drop_rt:
        retyped.discard(drop_rt)
        keep = lambda e: not (e.get("name") == drop_rt and e.get("event") == "finding"  # noqa: E731
                              and e.get("type") not in rules["finding_types"])
    if drop_dc:
        s = sig(drop_dc)
        decided = {n for n in decided if sig(n) != s}
        keep_dec = lambda d: d.get("sig") != s  # noqa: E731
    u, _ = fold(rules, done, keep, keep_dec)
    fails = []
    for n in INSTANCES:
        if n in u:
            fails.append("R1 %s reads untriaged" % n)
    bad = sorted(retyped & u)
    if bad:
        fails.append("R2 %d retyped findings read untriaged: %s" % (len(bad), bad[:5]))
    bad = sorted(decided & u)
    if bad:
        fails.append("R3 %d decided findings read untriaged: %s" % (len(bad), bad[:5]))
    print("events %d findings %d done %d retyped %d decided %d untriaged %d%s" % (
        len(EVENTS), len(alarm), len(done), len(retyped), len(decided), len(u),
        "".join(" %s=%s" % (k, v) for k, v in (("drop-retype", drop_rt), ("drop-decide", drop_dc)) if v)))
    for f in fails:
        print("FAIL", f)
    print("ALL PASS" if not fails else "FAILED %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
