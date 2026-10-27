"""selftest_audit_prescreen.py - python3 src/RimMandrake/rimflow/selftest_audit_prescreen.py"""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import audit_prescreen as ap                          # noqa: E402

FAILED = []


def ok(name, got, want):
    if got == want:
        print("ok    %s" % name)
    else:
        FAILED.append(name)
        print("FAIL  %s\n      got  %r\n      want %r" % (name, got, want))


R = ap.load_rules()
T0 = "2026-10-27T10:00:00Z"
since = ap._epoch("2026-10-20T00:00:00Z")


def ev(e, i, ts, seat="BENCH", **k):
    d = {"event": e, "id": i, "ts": ts, "seat": seat}
    d.update(k)
    return d


good = [ev("claim", "GOOD_ITEM", "2026-10-26T10:00:00Z"),
        ev("verify", "GOOD_ITEM", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
        ev("close", "GOOD_ITEM", "2026-10-26T12:00:00Z", sha="abc1234")]
bad = [ev("claim", "BAD_FLOWWORKS_ITEM", "2026-10-26T10:00:00Z"),
       ev("close", "BAD_FLOWWORKS_ITEM", "2026-10-26T10:01:00Z", sha="HEAD")]
old = [ev("close", "OLD_ITEM", "2026-09-01T10:00:00Z", sha="abc1234")]
git = lambda sha: ["src/a.py"]
rows = ap.score(good + bad + old, R, since, git=git)
ok("old close excluded", sorted(r["item"] for r in rows), ["BAD_FLOWWORKS_ITEM", "GOOD_ITEM"])
ok("bad ranks first", rows[0]["item"], "BAD_FLOWWORKS_ITEM")
ok("good has no flags", rows[1]["flags"], [])
ok("bad flags", set(rows[0]["flags"]) >= {"no_check_evidence", "sha_head_literal", "closed_by_maker_only",
                                           "short_claim_to_close", "flowworks_or_live"}, True)
r2 = ap.score(good, R, since, git=lambda s: None)
ok("unresolvable sha hard", r2[0]["hard"], ["sha_unresolvable"])
r3 = ap.score(good, R, since, git=lambda s: [], past_failed={"GOOD_ITEM"})
ok("touches nothing + past audit", r3[0]["flags"], ["sha_touches_nothing", "past_audit_failed"])
reo = good + [ev("claim", "GOOD_ITEM", "2026-10-26T13:00:00Z")]
ok("reopened", "reopened_before" in ap.score(reo, R, since, git=git)[0]["flags"], True)
ok("weights are multipliers from rules file",
   ap.score(bad, dict(R, weights={"no_check_evidence": 0}), since, git=git)[0]["score"] <
   ap.score(bad, R, since, git=git)[0]["score"], True)
# check evidence: close text naming a test counts; plain text does not
txt = lambda t: [ev("close", "T_ITEM", "2026-10-26T12:00:00Z", sha="a", reason=t)]
ok("selftest in reason = checked", "no_check_evidence" in ap.score(txt("ran selftest, 5 PASS"), R, since, git=git)[0]["flags"], False)
ok("bare reason = unchecked", "no_check_evidence" in ap.score(txt("done"), R, since, git=git)[0]["flags"], True)
ok("note counts", "no_check_evidence" in ap.score(txt("done") + [ev("note", "T_ITEM", "2026-10-26T11:00:00Z", text="measured 3 rows")], R, since, git=git)[0]["flags"], False)
# near-universal signal must not hard-flag nor score
crowd = [ev("close", "C%d_ITEM" % i, "2026-10-26T12:00:00Z", sha="HEAD" if i < 24 else "a") for i in range(25)]
cr = ap.score(crowd, R, since, git=git)
ok("near-universal signal: no hard flag", [r for r in cr if r["hard"]], [])
ok("near-universal signal: zero weight", cr[0]["score"], 0)
ok("rate reported", ap.signal_rates(cr)["sha_head_literal"], [24, 0.96])
# a rare signal does hard-flag and ranks first
crowd[3]["sha"] = "a"; crowd[0]["sha"] = "HEAD"
rare = [ev("close", "C%d_ITEM" % i, "2026-10-26T12:00:00Z", sha="a" if i else "HEAD") for i in range(25)]
rr = ap.score(rare, R, since, git=git)
ok("rare signal hard-flags first", (rr[0]["item"], rr[0]["hard"]), ("C0_ITEM", ["sha_head_literal"]))

many = [ev("close", "X_ITEM", "2026-10-26T12:00:00Z", sha="a")]
ok("many files", "many_files" in ap.score(many, R, since, git=lambda s: ["f%d" % i for i in range(30)])[0]["flags"], True)

many5 = []
for i in range(10):
    many5 += [ev("close", "I%d_ITEM" % i, "2026-10-26T12:00:00Z", sha="a")]
d = ap.build(ap.score(many5, R, since, git=git), R, seed=1)
ok("calibration 1 in 5", len(d["calibration_picks"]), 2)
ok("calibration deterministic", d["calibration_picks"], ap.build(ap.score(many5, R, since, git=git), R, seed=1)["calibration_picks"])

# unreadable ledger => exit non-zero, nothing written
out = os.path.join(tempfile.mkdtemp(), "p.json")
ok("empty ledger -> exit 2", ap.main(["--out", out], events=[]), 2)
ok("no file on unmeasured", os.path.exists(out), False)
pa = out + ".audits.jsonl"
ok("missing past audits -> exit 2 (UNMEASURED, not 'no past failures')",
   ap.main(["--out", out, "--past-audits", pa], events=good + bad), 2)
ok("no file when past audits missing", os.path.exists(out), False)
with open(pa, "w") as f:
    f.write('{"item": "X", "verdict": "DEFECT"}\n{"item": "Y", "verd')
ok("torn past-audit line -> exit 2", ap.main(["--out", out, "--past-audits", pa], events=good + bad), 2)
open(pa, "w").close()
ok("good ledger -> exit 0", ap.main(["--out", out, "--now", "2026-10-27T00:00:00Z", "--past-audits", pa],
                                    events=good + bad), 0)
ok("file written", json.load(open(out))["closes_seen"], 2)
with open(pa, "w") as f:
    f.write('{"item": "X", "verdict": "DEFECT"}\n\n{"item": "Y", "verdict": "SOUND"}\n')
ok("past_failed_items reads DEFECT only", ap.past_failed_items(pa), {"X"})
for bad in ('{"item": "X", "verdict": "defect"}\n', '{"verdict": "DEFECT"}\n', '["X", "DEFECT"]\n'):
    with open(pa, "w") as f:
        f.write(bad)
    try:
        ap.past_failed_items(pa)
        ok("schema-breaking line %r raises" % bad.strip(), "no raise", "ValueError")
    except ValueError:
        ok("schema-breaking line %r raises" % bad.strip(), "ValueError", "ValueError")
sch = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audits.schema.json")))
ok("audits.schema.json verdicts = the reader's", sch["properties"]["verdict"]["enum"], ["SOUND", "DEFECT", "UNRESOLVED"])

print("FAILED: %s" % FAILED if FAILED else "all ok")
sys.exit(1 if FAILED else 0)
