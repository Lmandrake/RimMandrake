"""DEEPFIRE_FAMILY_SETTINGS_SAVE_LOAD_1 (L1): live Verse Scribe round trip of the keyed Cuisine family toggles through the
REAL settings file, by jawa/static_call of RimMandrake.LuminousPigment.RM_LuminousFamilySettingsProbe.RoundTrip().
  A1: a disabled family is written by KEY (familyDisabledKeys, no positional list) and is disabled again after the file is
      read back (LoadedModManager.ReadModSettings) with memory reset to all-on.
  A2: a file in the pre-keyed shape (positional <familyEnabled> list, no keys) loads with the right family off and is
      re-written as that key with no positional list.
The probe puts the pre-test file and toggles back and reports `restored`; a run that fails to restore is a FAIL.
python.exe, bridge held, LuminousPigment deployed from this sha; any game state (main menu is enough).
argv: A1 | A2 | all (default). Exit 0 = every asked clause PASS and restored."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
import rimbridge_client as rb
want = (sys.argv[1] if len(sys.argv) > 1 else "all").upper()
clauses = ["A1", "A2"] if want == "ALL" else [want]
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=120.0); S.connect()
r = S.call("jawa/static_call", {"type": "RimMandrake.LuminousPigment.RM_LuminousFamilySettingsProbe", "method": "RoundTrip"}) or {}
outer = json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
if not outer.get("success"):
    print("FAIL: UNMEASURED: static_call refused: %s" % json.dumps(outer)[:600]); sys.exit(1)
try:
    res = json.loads(outer.get("result") or "")
except ValueError:
    print("FAIL: UNMEASURED: probe result is not JSON: %r" % (outer.get("result") or "")[:600]); sys.exit(1)
print(json.dumps(res, indent=1))
ok = res.get("restored") == "True" and all(res.get(c) == "PASS" for c in clauses)
print("%s %s restored=%s" % ("PASS" if ok else "FAIL", " ".join("%s=%s" % (c, res.get(c)) for c in clauses), res.get("restored")))
sys.exit(0 if ok else 1)
