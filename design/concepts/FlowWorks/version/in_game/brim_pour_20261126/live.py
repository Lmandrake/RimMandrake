"""Live decider for RIMMANDRAKE_EXPLAIN_BRIM_POUR_LITRES_WITH_NOWHERE_TO_GO on a fresh quicktest map (python.exe, RM_REPO set).
A: the shipped OL_pour_never_no_room acts on a dug 3x3x3 m spare pit (want PASS, 'spilled 1 kL of 1 kL').
B: state known bad: a 10,000 kL pour at pit A fills the map's wet-square cap; the same acts on pit B, 157 squares away
   (want UNMEASURED, and the reply names the full cap); then the sheet is drained and B is run again (want PASS)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.environ["RM_REPO"], "src", "RimMandrake", "FlowWorks", "northstar"))
import owner_look_regressions as O
out = {}
def dig(x0, z0):
    for x in range(x0, x0 + 3):
        for z in range(z0, z0 + 3):
            r = O.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=6)
            assert r.get("success") and r.get("depth") == 6, r
def ledger():
    return O.static(O.SHEET_PROOFS, "ProofSheetLedger", "-")
A, Bp = (43, 203, 3, 6), (203, 203, 3, 6)
dig(*A[:2]); dig(*Bp[:2])
out["A_ledger_before"] = ledger()
keep = O.static
said = []
def spy(t, m, a):
    r = keep(t, m, a); said.append((m, a, r)); return r
O.static = spy
out["A_rows"] = O.acts(A)
out["A_replies"] = said[:]; said.clear()
O.static = keep
O.static(O.GL, "SetLevel", "44,204|RM_Fluid_Water|3.0")
out["fill_cap"] = O.static(O.GL, "PourOverflow", "44,204|RM_Fluid_Water|10000000")
out["B_ledger_full"] = ledger()
O.static = spy
out["B_rows_full"] = O.acts(Bp)
out["B_replies_full"] = said[:]; said.clear()
O.static = keep
out["drain_A_sheet"] = O.static(O.GL, "DrainAll", "42,204")
out["B_ledger_after_drain"] = ledger()
O.static = spy
out["B_rows_clean"] = O.acts(Bp)
out["B_replies_clean"] = said[:]
O.static = keep
O.static(O.GL, "DrainAll", "44,204")
out["ledger_end"] = ledger()
print(json.dumps(out, indent=1))
