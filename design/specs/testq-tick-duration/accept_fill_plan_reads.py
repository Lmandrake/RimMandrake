"""Acceptance: fill_plan on a braked mod reads each done record at most once. exit 0 pass, 1 fail, 2 could not look."""
import glob, sys
sys.path.insert(0, sys.argv[1] + "/src/RimMandrake/Utils/testq")
import testq as T
n = len(glob.glob(T.q("done", "*.json")))
if n < 50:
    print("UNMEASURED: only %d done records, cannot tell one read from three" % n); sys.exit(2)
calls = [0]; orig = T.read_json
def counted(p):
    calls[0] += "/done/" in p.replace("\\", "/"); return orig(p)
T.read_json = counted
p = T.fill_plan(sys.argv[2], 4, T.FILL_CAP_DEFAULT)
ok = calls[0] <= n + 5
print("%s: fill_plan(%s) verdict=%s read %d done files for %d records" % ("PASS" if ok else "FAIL", sys.argv[2], p["verdict"], calls[0], n))
sys.exit(0 if ok else 1)
