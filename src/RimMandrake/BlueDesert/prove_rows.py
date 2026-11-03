"""Read a northstar_driver --out results file and exit 0 when every named row (`chain.component`) is PASS, 1 when any
is FAIL, 2 when any is missing or UNMEASURED. Used by BLUEDESERT_GPT_ENRICHMENT_1's live proofs A2 and A5, whose
driver run selects one chain with --chains (the other chains read 'chain not run', so the run's own exit is not
the clause's verdict).
    python3 src/RimMandrake/BlueDesert/prove_rows.py <results.json> cold_rack.rack_cools_loaded_room_only ...
"""
import json
import sys


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as ex:
        print("UNMEASURED: results unreadable: %s" % ex)
        return 2
    rows = dict((r.get("id"), r) for r in doc.get("bars") or [])
    code = 0
    for want in argv[2:]:
        r = rows.get(want)
        st = (r or {}).get("status")
        print("%-11s %s  %s" % (st or "MISSING", want, str((r or {}).get("evidence") or "")[:200]))
        if st == "FAIL":
            code = max(code, 1)
        elif st != "PASS":
            code = 2 if code == 0 else code
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
