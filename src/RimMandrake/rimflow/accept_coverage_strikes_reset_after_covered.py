import sys; sys.path.insert(0, "src/RimMandrake/rimflow")
import coverage_judge as C
def st(vs): return {"coverage_rounds": [{"at": "2026-11-1%dT00:00:00Z" % i, "verdict": v, "tokens": 1000} for i, v in enumerate(vs)]}
cases = [
 (["not_covered", "not_covered", "covered", "not_covered"], None),          # a covered sign-off resets the count
 (["not_covered", "not_covered", "covered"], None),
 (["not_covered", "not_covered", "not_covered"], "stop"),                    # the limit still binds with no pass
 (["covered", "not_covered", "not_covered", "not_covered"], "stop"),         # three after a pass still stop
 ([], None),
]
ok = 0
for vs, want in cases:
    got = C.stop_reason(st(vs))
    good = (got is None) if want is None else (got is not None)
    ok += good; print("PASS" if good else "FAIL", vs, "->", got)
print("%d of %d" % (ok, len(cases))); sys.exit(0 if ok == len(cases) else 1)
