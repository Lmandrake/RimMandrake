"""Live proofs of SETTLEMENT_VERBS_WAVE_1, one clause per call:

    python.exe src/RimMandrake/RimProperty/settlement_verbs_live_proof.py A1|A2|A3|A4|A5|A6

Calls RimMandrake.Property.RM_SettlementVerbsProof.RunOne(<verb>) through jawa/static_call on the current (quicktest)
map. The probe gives a colonist silver, spawns its own target beside it, builds the REAL right-click menu
(FloatMenuMakerMap.GetOptions), clicks the verb's option, reads the property ledger, checks the option is gone with
the verb's toggle off, then destroys what it made and takes the silver back. It answers "PASS <verb> ..." or
"FAIL <verb> <reason>".
Exit 0 = the clause holds, 1 = the probe answered FAIL, 2 = UNMEASURED (no bridge, REFUSED, no PASS/FAIL line).
  A1 salvage     weakly foreign-claimed revolver: fee = ComputeFeeSilver, ClaimFeePaid, payer wins, fee scales
  A2 droid       the claim fee on a downed (alive) mechanoid
  A3 commerce    merchant-claimed revolver: "Buy X (price silver)", Purchased for the buyer
  A4 pickpocket  non-hostile faction pawn carrying gold: item moves to the thief, Stolen naming the victim
  A5 hire        factionless WildMan: fee taken, Purchased on the hired pawn
  A6 bribe       non-hostile faction pawn: fee taken, payer's suspicion falls by bribeDampenFraction
verdict() is pure and is exercised offline by src/RimMandrake/Utils/selftest_settlement_verbs_static.py.
"""
import json
import os
import re
import sys

PROBE = "RimMandrake.Property.RM_SettlementVerbsProof"
VERBS = {"A1": "salvage", "A2": "droid", "A3": "commerce", "A4": "pickpocket", "A5": "hire", "A6": "bribe"}


def verdict(clause, text):
    """-> (exit code, reason) for the probe's reply text. Only a PASS line naming THIS clause's verb passes."""
    verb = VERBS[clause]
    s = str(text)
    m = re.search(r"\b(PASS|FAIL) %s\b([^\"\\]*)" % verb, s)
    if not m:
        if "REFUSED" in s:
            return 2, "probe refused: " + s[s.find("REFUSED"):][:300]
        return 2, "no PASS/FAIL %s line: %s" % (verb, s[:300])
    line = (m.group(1) + " " + verb + m.group(2)).strip()
    return (0, line) if m.group(1) == "PASS" else (1, line)


def main(argv):
    if len(argv) != 2 or argv[1] not in VERBS:
        print(__doc__)
        return 2
    clause = argv[1]
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
    try:
        import rimbridge_client as R
        host, port, token = R.resolve_endpoint()
        if not token:
            print("UNMEASURED: no bridge token")
            return 2
        with R.RimBridge(host, port, token, timeout=120) as rb:
            out = rb.call("jawa/static_call", {"type": PROBE, "method": "RunOne", "args": VERBS[clause]})
    except Exception as ex:  # any transport failure means the proof could not see
        print("UNMEASURED: bridge call failed: %s" % str(ex)[:300])
        return 2
    code, why = verdict(clause, json.dumps(out))
    print("%s %s: %s" % (clause, {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[code], why))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
