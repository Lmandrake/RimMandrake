"""keep_modlist() fails by name when WSLENV declares a MODCHECK_ variable that did not arrive (the dropped-variable
trap of 2026-11-15), and composed biome lists carry the deployed Biomes' dependencies. Offline."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import runner as R
fails = []
def check(c, m):
    if not c: fails.append(m)
try:
    R.keep_modlist({"WSLENV": "MODCHECK_KEEP_MODLIST/u"}); check(False, "dropped variable did not raise")
except RuntimeError as e:
    check("MODCHECK_KEEP_MODLIST" in str(e), "error does not name the variable")
check(R.keep_modlist({"WSLENV": "MODCHECK_KEEP_MODLIST/u", "MODCHECK_KEEP_MODLIST": "1"}) is True, "arrived var not kept")
check(R.keep_modlist({"WSLENV": "PATH/l"}) is False, "unrelated WSLENV raised")
check(R.keep_modlist({}) is False, "no variable should be the normal path")
check("mandrake.rm.luminouspigment" in R.composed_ids("Webwork"), "Webwork list lacks luminous pigment")
print("FAIL" if fails else "PASS", fails); sys.exit(1 if fails else 0)
