"""RIMMANDRAKE_REPIN_PYRE_AFTER_ROUND_NINE_GAPS acceptance: the 2026-11-17T18:24:41Z grant no longer waits on the
re-pin, and stage.json holds a locked_change after the round-8 stop (2026-11-17T18:05:37Z) citing only OWNER sources.
FAILED before the re-pin (waits listed 'the re-pin', 0 locked_change after the stop). Run from the repo root."""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import designer_stage as DS, coverage_judge as CJ
d = os.path.join(ROOT, "design", "concepts", "Pyrelands")
st = DS.load_state(d)
waits = CJ.grant_waits(st, d=d) or []
hs = [h for h in st.get("history") or [] if isinstance(h, dict)]
lc = [h for h in hs if h.get("what") == "locked_change" and h.get("at", "") > "2026-11-17T18:05:37Z"]
srcs = [s for h in lc for s in re.findall(r"\b([A-Z]+):\d+@", h.get("why", ""))]
ok = (not any(w.startswith("the re-pin") for w in waits)) and bool(lc) and bool(srcs) and set(srcs) == {"OWNER"}
print("waits %s | locked_change after stop %d | @-sources %d, kinds %s | %s" % (
    waits, len(lc), len(srcs), sorted(set(srcs)), "PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
