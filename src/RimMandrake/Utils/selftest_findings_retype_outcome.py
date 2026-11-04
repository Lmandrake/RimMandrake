#!/usr/bin/env python3
"""selftest_findings_retype_outcome.py - a finding retyped out of the alarm's types reads as triaged
(class guard of OPS_FINDINGS_DIAGNOSE_XZLM, the twice-fired UNTRIAGED alarm on flow.untriaged_findings).

Folds the COMMITTED ledger of this tree (never a host path) with findings_fold, publishes the table into a temp dir and
asks findings_fold.no_outcome, the alarm's own answer:
  R1 the instance: STEVE_LANE_SYNC_REFUSED_5E2C71 (retyped RESOLVED_LANE_HEALTHY by Operations) has an outcome;
  R2 the class: every finding whose name carries a later retype out of the finding types reads with an outcome;
  R0 the instrument sees: >10000 events and >100 findings, else exit 2 (a blind 0 is not a pass).
Replay the instance with `--drop-retype STEVE_LANE_SYNC_REFUSED_5E2C71`: its retype is withheld from the fold, and
R1 must fail (exit 1).
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

INSTANCE = "STEVE_LANE_SYNC_REFUSED_5E2C71"


def no_outcome(events, rules, drop=None):
    """-> names with no outcome from a fold of this tree's ledger; `drop` withholds that name's retypes."""
    keep = (lambda e: not (e.get("name") == drop and e.get("event") == "finding"
                           and e.get("type") not in rules["finding_types"]))
    evs = [e for e in events if keep(e)]
    read = model.read
    model.read = lambda *a, **k: [e for e in read(*a, **k) if keep(e)]
    try:
        t = ff.fold(*ff.read_ledger(rules), [], ff.read_decisions(ff.decisions_path(rules)), rules, ff.utcnow())
    finally:
        model.read = read
    d = tempfile.mkdtemp(prefix="retype_outcome_")
    with open(os.path.join(d, ff.REPORT), "w", encoding="utf-8") as f:
        f.write(ff.render_report(t))
    return ff.no_outcome(evs, out=d)


def main(argv):
    drop = argv[argv.index("--drop-retype") + 1] if "--drop-retype" in argv else None
    rules = ff.load_rules()
    events = pc.read_ledger([Path(ROOT)])
    finds = [e for e in events if e.get("event") == "finding"]
    alarm = [e for e in finds if e.get("type") in rules["finding_types"]]
    if len(events) < 10000 or len(alarm) < 100:
        print("R0 BLIND: %d events, %d findings" % (len(events), len(alarm)))
        return 2
    alarmed, last = {e.get("name") for e in alarm}, {}
    for e in finds:                                     # the ledger is in order: a name's last finding event wins
        last[e.get("name")] = e.get("type")
    retyped = {n for n in alarmed if last.get(n) not in rules["finding_types"]}
    if drop:
        retyped.discard(drop)
    u = no_outcome(events, rules, drop)
    fails = []
    if INSTANCE in u:
        fails.append("R1 %s reads untriaged" % INSTANCE)
    bad = sorted(retyped & u)
    if bad:
        fails.append("R2 %d retyped findings read untriaged: %s" % (len(bad), bad[:5]))
    print("events %d findings %d retyped %d untriaged %d%s" % (len(events), len(alarm), len(retyped), len(u),
                                                             " drop=%s" % drop if drop else ""))
    for f in fails:
        print("FAIL", f)
    print("ALL PASS" if not fails else "FAILED %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
