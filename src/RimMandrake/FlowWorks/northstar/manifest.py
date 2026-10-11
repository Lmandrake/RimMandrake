"""manifest.py -- the FlowWorks walk's `checkout:` (hose port step 8, design FINAL §3.10 "one manifest contract").

declared_rows() = the core live proof's rows (validation_v2.py, its clean --mock run) UNION the hose live proof's rows
(proof_hose.py: DECLARED_ROWS + the nine MX_H0* hose matrix scenes). modcheck/required_checks.py enumerates this in a
subprocess. Results reach FlowWorks/validation.py through the same current-mod-hash JSON path for both
(core_live_rows reads validation_v2_result_*.json; hose_live_rows reads proof_hose_*.json).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def declared_rows():
    import validation_v2 as V2
    import proof_hose as PH
    out = list(V2.declared_rows())
    out += [r for r in PH.declared_rows() if r not in out]
    return out


if __name__ == "__main__":
    rows = declared_rows()
    print("%d rows" % len(rows))
