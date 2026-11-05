"""Live proof A2 of WEEPINGSTONES_HANDLER_VANISHES_1: read a northstar_driver --out results file of a `--chains job_net`
run and exit 0 when job_net.site_ready_net is PASS and job_net.net_turns_wild_pawn_into_breeding_stock reads PASS or
FAIL without the handler-gone UNMEASURED; 1 when the run measured and that does not hold; 2 when the run did not
measure at all (results unreadable, the driver REFUSED at preflight, or no job_net rows), so a harness refusal never
reads as a verdict on the mod (2026-11-04: an UNKNOWN-outcome bridge call refused every preflight, bars=[], exit 1).
    python3 src/RimMandrake/WeepingStones/prove_job_net.py <results.json>
"""
import json
import sys

GONE = "is not alive on the map after the wait"


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as ex:
        print("UNMEASURED: results unreadable: %s" % ex)
        return 2
    b = dict((r.get("id"), r) for r in doc.get("bars") or [] if str(r.get("id") or "").startswith("job_net."))
    if doc.get("refused") or not b:
        print("UNMEASURED: the run measured no job_net row (refused: %s)" % (doc.get("refused") or "-"))
        return 2
    site = (b.get("job_net.site_ready_net") or {}).get("status")
    net = b.get("job_net.net_turns_wild_pawn_into_breeding_stock") or {}
    gone = GONE in str(net.get("evidenceFull") or net.get("evidence"))
    print("site", site, "net", net.get("status"), "handler-gone", gone)
    return 0 if (site == "PASS" and net.get("status") in ("PASS", "FAIL") and not gone) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
