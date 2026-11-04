"""OPS_FINDINGS_DIAGNOSE_XZLM proof: flow.untriaged_findings is 0 on the COMMITTED ledger, and its cause finding
(STEVE_LANE_SYNC_REFUSED_5E2C71) has an outcome. Reads only this tree: the ledger under the cwd and the committed
decisions file; the fold's table is rebuilt into a temp dir (testq done records are host state and decide no outcome),
then findings_fold.no_outcome, the alarm's own answer, is asked of it. A sanity probe drops the cause's retype and
must see the finding come back untriaged, so a 0 here is a measured 0, not a blind one. Run from the repo root.
Exit 0 = the clause holds, 1 = it does not, 2 = the instrument is blind."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / p) for p in ("src/RimMandrake/Utils", "src/RimMandrake/Utils/pulse", "src/RimMandrake/rimflow")]
os.environ["RIMFLOW_LEDGER"] = str(ROOT / "infrastructure/state/ledger/events.jsonl")
import findings_fold as ff  # noqa: E402
import model  # noqa: E402
import pulse_core as pc  # noqa: E402

CAUSE = "STEVE_LANE_SYNC_REFUSED_5E2C71"


def untriaged(events, drop=None):
    """-> (names with no outcome, table) from a fold of this tree's ledger, optionally without one event kind."""
    rules, read = ff.load_rules(), model.read
    if drop:
        model.read = lambda *a, **k: [e for e in read(*a, **k) if not drop(e)]
    try:
        t = ff.fold(*ff.read_ledger(rules), [], ff.read_decisions(ff.decisions_path(rules)), rules, ff.utcnow())
    finally:
        model.read = read
    d = tempfile.mkdtemp(prefix="xzlm_fold_")
    with open(os.path.join(d, ff.REPORT), "w", encoding="utf-8") as f:
        f.write(ff.render_report(t))
    return ff.no_outcome(events, out=d), t


def main():
    events = pc.read_ledger([ROOT])
    rules = ff.load_rules()
    finds = [e for e in events if e.get("event") == "finding" and e.get("type") in rules["finding_types"]]
    if len(events) < 10000 or len(finds) < 100 or not any(e.get("name") == CAUSE for e in finds):
        print("BLIND: %d events, %d findings, cause present=%s" % (len(events), len(finds),
                                                                  any(e.get("name") == CAUSE for e in finds)))
        return 2
    probe, _ = untriaged(events, drop=lambda e: e.get("name") == CAUSE and e.get("type") not in rules["finding_types"])
    if CAUSE not in probe:
        print("BLIND: with its retype dropped the cause still reads triaged")
        return 2
    u, t = untriaged(events)
    cause = (t["raw"].get(CAUSE) or {}).get("outcome")
    print("events %d findings %d untriaged %d %s cause_outcome %s probe_sees_cause True"
          % (len(events), len(finds), len(u), sorted(u)[:5], cause))
    return 0 if cause is True and not u else 1


if __name__ == "__main__":
    sys.exit(main())
