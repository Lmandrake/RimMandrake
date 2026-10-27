"""selftest_arbiter_tiers.py - python3 src/RimMandrake/rimflow/selftest_arbiter_tiers.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import arbiter_tiers as at                            # noqa: E402
from rimflow import audit_prescreen as ap                          # noqa: E402

FAILED = []


def ok(name, got, want):
    if got == want:
        print("ok    %s" % name)
    else:
        FAILED.append(name)
        print("FAIL  %s\n      got  %r\n      want %r" % (name, got, want))


R = ap.load_rules()
since = ap._epoch("2026-10-20T00:00:00Z")


def ev(e, i, ts, seat="BENCH", **k):
    d = {"event": e, "id": i, "ts": ts, "seat": seat}
    d.update(k)
    return d


# paths: cited evidence parsing
ok("windows path mapped", at.cited_paths(r"D:\ClaudeWork\x\a.png; ok"), ["/mnt/d/ClaudeWork/x/a.png"])
ok("trailing colon stripped", at.cited_paths("/mnt/d/x.json: regions 71"), ["/mnt/d/x.json"])
ok("remote host path not local", at.cited_paths("stevedesktop:/home/m/r.html (testq)"), [])

FILES = {"good": ["src/a.py"], "fail": ["src/b.py"], "nore": ["src/c.py"], "harn": ["src/RimMandrake/rimflow/x.py"],
         "docs": ["design/x.md"]}
CLEAN = {("src/a.py", "H_src/a.py"), ("src/RimMandrake/rimflow/x.py", "H_src/RimMandrake/rimflow/x.py")}
git = lambda sha: FILES.get(sha)
blob = lambda sha, path: "H_" + path
exists = lambda p: p.endswith("there.png")

events = [
    # verified by another seat, evidence on disk, code reviewed at that content: tier-0 pass
    ev("claim", "GOOD", "2026-10-26T09:00:00Z"),
    ev("implemented", "GOOD", "2026-10-26T10:00:00Z", sha="good", criteria=[{"id": "A1", "level": "L0"}]),
    ev("verify", "GOOD", "2026-10-26T11:00:00Z", seat="RUNNER", result="fail", criterion="A1",
       evidence=r"D:\w\there.png"),
    ev("verify", "GOOD", "2026-10-26T11:30:00Z", seat="RUNNER", result="pass", criterion="A1",
       evidence=r"D:\w\there.png"),
    ev("close", "GOOD", "2026-10-26T12:00:00Z", sha="good", reason="verified"),
    # a fail never superseded by a pass: bounce
    ev("claim", "FAILED", "2026-10-26T09:00:00Z"),
    ev("verify", "FAILED", "2026-10-26T11:00:00Z", seat="RUNNER", result="fail", evidence=r"D:\w\there.png"),
    ev("close", "FAILED", "2026-10-26T12:00:00Z", sha="fail", reason="tests pass"),
    # names no build: bounce
    ev("close", "NOSHA", "2026-10-26T12:00:00Z", sha="HEAD", reason="selftest PASS"),
    # evidence cited but gone: bounce
    ev("verify", "GONE", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass", evidence="/mnt/d/w/gone.png"),
    ev("close", "GONE", "2026-10-26T12:00:00Z", sha="good", reason="verified"),
    # passes verify but code never reviewed at that content: open, ranked
    ev("verify", "NOREVIEW", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
    ev("close", "NOREVIEW", "2026-10-26T12:00:00Z", sha="nore", reason="verified"),
    # clean on every gate but touches the gate code itself: forced to tier 2
    ev("verify", "HARNESS", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
    ev("close", "HARNESS", "2026-10-26T12:00:00Z", sha="harn", reason="verified"),
    # owner spoke after the close: forced to tier 2
    ev("verify", "OWNERSPOKE", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
    ev("close", "OWNERSPOKE", "2026-10-26T12:00:00Z", sha="docs", reason="verified"),
    ev("note", "OWNERSPOKE", "2026-10-26T13:00:00Z", seat="OWNER", text="no", ownerSaid="this is wrong"),
]
rows, cut = at.classify(events, R, since, git=git, clean=CLEAN, blob=blob, exists=exists)
tier = {r["item"]: r["tier"] for r in rows}
gates = {r["item"]: r["gates"] for r in rows}
ok("later pass supersedes earlier fail", gates["GOOD"]["G2_verify"], "PASS")
ok("criteria covered", gates["GOOD"]["G3_criteria"], "PASS")
ok("reviewed at sha content", gates["GOOD"]["G5_review"], "PASS")
ok("good passes tier 0", tier["GOOD"], "T0_PASS")
ok("unsuperseded fail bounces", tier["FAILED"], "T0_BOUNCE")
ok("bounce carries failing evidence", [r for r in rows if r["item"] == "FAILED"][0]["gate_evidence"]["G2_verify"],
   [r"D:\w\there.png"])
ok("HEAD sha bounces", tier["NOSHA"], "T0_BOUNCE")
ok("absent evidence bounces", tier["GONE"], "T0_BOUNCE")
ok("unreviewed code is not a tier-0 pass", gates["NOREVIEW"]["G5_review"], "OPEN")
ok("unreviewed code goes to rank", tier["NOREVIEW"] in ("T1_PASS", "T2_RISK"), True)
ok("gate code forced to tier 2", tier["HARNESS"], "T2_RISK")
ok("owner words after close forced to tier 2", tier["OWNERSPOKE"], "T2_RISK")
m = at.mix(rows)
ok("mix counts every claim", sum(m[t][0] for t in ("T0_BOUNCE", "T0_PASS", "T1_PASS", "T2_RISK")), len(rows))

# calibration: 1 in CALIB_EVERY of the passes, seeded and repeatable, never a bounce or a tier-2 claim
many = []
for i in range(40):
    iid = "P%02d" % i
    many += [ev("verify", iid, "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
             ev("close", iid, "2026-10-26T12:00:00Z", sha="good", reason="verified")]
r1, _ = at.classify(many, R, since, git=git, clean=CLEAN, blob=blob, exists=exists, seed=5)
r2, _ = at.classify(many, R, since, git=git, clean=CLEAN, blob=blob, exists=exists, seed=5)
c1 = sorted(r["item"] for r in r1 if r["calibration"])
ok("calibration size", len(c1), 40 // at.CALIB_EVERY)
ok("calibration repeatable", c1, sorted(r["item"] for r in r2 if r["calibration"]))
ok("calibration only from passes", all(r["tier"] in ("T0_PASS", "T1_PASS") for r in r1 if r["calibration"]), True)

# empty ledger is UNMEASURED, not a zero mix
ok("empty ledger exits 2", at.main(["--out", os.devnull], events=[]), 2)

print("\n%s" % ("ALL PASS" if not FAILED else "FAILED: %s" % FAILED))
sys.exit(1 if FAILED else 0)
