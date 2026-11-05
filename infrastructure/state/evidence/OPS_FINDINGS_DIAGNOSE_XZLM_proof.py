"""OPS_FINDINGS_DIAGNOSE_XZLM proof: flow.untriaged_findings is 0 on the COMMITTED ledger, and its cause finding
(STEVE_LANE_SYNC_REFUSED_5E2C71) has an outcome. Reads only this tree: the ledger under the cwd and the committed
decisions file; the fold's table is rebuilt into a temp dir (testq done records are host state and decide no outcome),
then findings_fold.no_outcome, the alarm's own answer, is asked of it. A finding's signature is cut from its testq done
record, and a findings_fold decide is keyed on it, so the done records are read too: from the dir given as --done, else the
fold's own queue_dir() (the host's testq queue, /mnt/d/ClaudeWork/rimmandrake/testq); unreadable is blind (exit 2), never a fold without them. A sanity probe drops the cause's retype and
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
# 2026-11-05 reopen: three steve-targeted FlowWorks FAILs, routed by findings_fold decide (sig -> owning item)
ROUTED = {"FLOWWORKS_CROPS_IRRIGATE_THEN_DROWN_FAILS_2B0937": "CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED",
          "FLOWWORKS_CROPS_IRRIGATE_THEN_DROWN_FAILS_54F48C": "CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED",
          "FLOWWORKS_FINDS_OFF_NONE_FAILS_2B0937": "DIG_FINDS_PROVE_NEVER_FINISHES_ON_STEVE"}


def untriaged(events, drop=None, drop_decision=None):
    """-> (names with no outcome, table) from a fold of this tree's ledger, optionally without one event kind or
    without the decision lines one predicate picks."""
    rules, read = ff.load_rules(), model.read
    if drop:
        model.read = lambda *a, **k: [e for e in read(*a, **k) if not drop(e)]
    try:
        dec = ff.read_decisions(ff.decisions_path(rules))
        if drop_decision:
            dec = [d for d in dec if not drop_decision(d)]
        finds, spawns, states, timeline = ff.read_ledger(rules)
        t = ff.fold(finds, spawns, states, DONE, dec, rules, ff.utcnow(), timeline)
    finally:
        model.read = read
    d = tempfile.mkdtemp(prefix="xzlm_fold_")
    with open(os.path.join(d, ff.REPORT), "w", encoding="utf-8") as f:
        f.write(ff.render_report(t))
    return ff.no_outcome(events, out=d), t


DONE = []


def main():
    global DONE
    if len(sys.argv) not in (1, 3) or len(sys.argv) == 3 and sys.argv[1] != "--done":
        print("usage: OPS_FINDINGS_DIAGNOSE_XZLM_proof.py [--done <testq queue dir>]")
        return 2
    qd = sys.argv[2] if len(sys.argv) == 3 else ff.queue_dir()
    try:
        DONE = ff.read_done(qd)
    except ff.Unmeasured as e:
        print("BLIND: %s" % e)
        return 2
    if len(DONE) < 100:
        print("BLIND: %d done records in %s" % (len(DONE), qd))
        return 2
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
    names = {e.get("name") for e in finds}
    if not set(ROUTED) <= names:
        print("BLIND: routed causes absent from the ledger: %s" % sorted(set(ROUTED) - names))
        return 2
    sigs = {(t["raw"].get(n) or {}).get("sig") for n in ROUTED}
    probe2, _ = untriaged(events, drop_decision=lambda d: d.get("sig") in sigs)
    if not set(ROUTED) <= probe2:
        print("BLIND: with their decisions withheld the routed causes still read triaged: %s"
              % sorted(set(ROUTED) - probe2))
        return 2
    cause = (t["raw"].get(CAUSE) or {}).get("outcome")
    routed = {n: (t["raw"].get(n) or {}).get("outcome") for n in ROUTED}
    print("events %d findings %d untriaged %d %s cause_outcome %s routed_outcomes %s probe_sees_cause True "
          "probe_sees_routed True" % (len(events), len(finds), len(u), sorted(u)[:5], cause,
                                      sorted(n for n, o in routed.items() if o is True)))
    return 0 if cause is True and all(o is True for o in routed.values()) and not u else 1


if __name__ == "__main__":
    sys.exit(main())
