"""selftest_arbiter_tiers.py - python3 src/RimMandrake/rimflow/selftest_arbiter_tiers.py"""
import json, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import arbiter_tiers as at                            # noqa: E402
from rimflow import audit_prescreen as ap                          # noqa: E402

FAILED = []
HERE = os.path.dirname(os.path.abspath(__file__))


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


def tiers_of(events, **kw):
    kw.setdefault("git", git)
    kw.setdefault("clean", CLEAN)
    kw.setdefault("blob", blob)
    kw.setdefault("exists", exists)
    rows, cut = at.classify(events, R, since, **kw)
    return {r["item"]: r for r in rows}, rows, cut


# paths: cited evidence parsing
ok("windows path mapped", at.cited_paths(r"D:\ClaudeWork\x\a.png; ok"), ["/mnt/d/ClaudeWork/x/a.png"])
ok("trailing colon stripped", at.cited_paths("/mnt/d/x.json: regions 71"), ["/mnt/d/x.json"])
ok("remote host path not local", at.cited_paths("stevedesktop:/home/m/r.html (testq)"), [])

FILES = {"good": ["src/a.py"], "fail": ["src/b.py"], "nore": ["src/c.py"], "harn": ["src/RimMandrake/rimflow/x.py"],
         "docs": ["design/x.md"], "gerr": at.GIT_ERROR, "del": {"src/a.py": "M", "src/old.py": "D"},
         "unread": {"src/u.py": "M"}, "tested": {"src/m/mod.py": "M"}}
CLEAN = {("src/a.py", "H_src/a.py"): {"RUNNER"}, ("src/RimMandrake/rimflow/x.py", "H_src/RimMandrake/rimflow/x.py"):
         {"RUNNER"}}
git = lambda sha: FILES.get(sha)
blob = lambda sha, path: None if path == "src/u.py" else "H_" + path
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
    ev("claim", "FAILED", "2026-10-26T09:00:00Z"),
    ev("verify", "FAILED", "2026-10-26T11:00:00Z", seat="RUNNER", result="fail", evidence=r"D:\w\there.png"),
    ev("close", "FAILED", "2026-10-26T12:00:00Z", sha="fail", reason="tests pass"),
    ev("close", "NOSHA", "2026-10-26T12:00:00Z", sha="HEAD", reason="selftest PASS"),
    ev("verify", "GONE", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass", evidence="/mnt/d/w/gone.png"),
    ev("close", "GONE", "2026-10-26T12:00:00Z", sha="good", reason="verified"),
    ev("verify", "NOREVIEW", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
    ev("close", "NOREVIEW", "2026-10-26T12:00:00Z", sha="nore", reason="verified"),
    ev("verify", "HARNESS", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
    ev("close", "HARNESS", "2026-10-26T12:00:00Z", sha="harn", reason="verified"),
    ev("verify", "OWNERSPOKE", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
    ev("close", "OWNERSPOKE", "2026-10-26T12:00:00Z", sha="docs", reason="verified"),
    ev("note", "OWNERSPOKE", "2026-10-26T13:00:00Z", seat="OWNER", text="no", ownerSaid="this is wrong"),
]
T, rows, cut = tiers_of(events)
ok("later pass supersedes earlier fail", T["GOOD"]["gates"]["G2_verify"], "PASS")
ok("criteria covered", T["GOOD"]["gates"]["G3_criteria"], "PASS")
ok("reviewed at sha content", T["GOOD"]["gates"]["G5_review"], "PASS")
ok("good passes tier 0", T["GOOD"]["tier"], "T0_PASS")
ok("unsuperseded fail bounces", T["FAILED"]["tier"], "T0_BOUNCE")
ok("bounce carries failing evidence", T["FAILED"]["gate_evidence"]["G2_verify"], [r"D:\w\there.png"])
ok("HEAD sha bounces", T["NOSHA"]["tier"], "T0_BOUNCE")
ok("absent evidence bounces", T["GONE"]["tier"], "T0_BOUNCE")
ok("unreviewed code is not a tier-0 pass", T["NOREVIEW"]["gates"]["G5_review"], "OPEN")
ok("unreviewed code goes to rank", T["NOREVIEW"]["tier"] in ("T1_PASS", "T2_RISK"), True)
ok("gate code forced to tier 2", T["HARNESS"]["tier"], "T2_RISK")
ok("owner words after close forced to tier 2", T["OWNERSPOKE"]["tier"], "T2_RISK")
m = at.mix(rows)
ok("mix counts every claim", sum(m[t][0] for t in at.TIERS), len(rows))

# F1: most closes carry no evidence (the flag goes near-universal and weighs 0): none of them may pass by code
f1 = []
for i in range(30):
    iid = "N%02d" % i
    if i < 20:
        f1 += [ev("close", iid, "2026-10-26T12:00:00Z", sha="docs", reason="done")]
    else:
        f1 += [ev("verify", iid, "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
               ev("close", iid, "2026-10-26T12:00:00Z", sha="docs", reason="verified")]
T1, r1, _ = tiers_of(f1)
noev = [r for r in r1 if r["item"] < "N20"]
ok("F1 no-evidence closes never pass by code", sorted({r["tier"] for r in noev}), ["T2_NOEVIDENCE"])
ok("F1 no-evidence closes hold when AI refused",
   sorted({r["decision"] for r in tiers_of(f1, ai_refused=True)[1] if r["item"] < "N20"}), ["HOLD"])
ok("F1 evidenced closes are ranked, not forced", all(r["tier"] in ("T0_PASS", "T1_PASS", "T2_RISK")
                                                       for r in r1 if r["item"] >= "N20"), True)
ok("F1 prose 'tests pass' is not machine evidence",
   tiers_of([ev("close", "PROSE", "2026-10-26T12:00:00Z", sha="docs", reason="selftest PASS")])[0]["PROSE"]["tier"],
   "T2_NOEVIDENCE")

rk = at.rank_evidenced([{"item": "R%d" % i, "closed_at": i, "flags": ["review_by_closing_seat_only"] if i < 21 else []}
                        for i in range(30)], R)   # >= min_sample, so the window rate (0.7) is used
ok("F1 a gap on most evidenced claims still weighs > 0", all(r["score"] > 0 for r in rk if r["flags"]), True)

# F2: the judge list carries item and sha only, holds T2 and calibration, and does not group calibration claims
mixed = []
for i in range(60):
    iid = "J%02d" % i
    if i % 2:
        mixed += [ev("close", iid, "2026-10-26T12:00:00Z", sha="docs", reason="done")]          # no evidence: T2
    else:
        mixed += [ev("verify", iid, "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
                  ev("close", iid, "2026-10-26T12:00:00Z", sha="good", reason="verified")]
_, rj, _ = tiers_of(mixed, salt="s2")
jl = at.judge_list(rj, "s2")
ok("F2 judge rows are item+sha only", sorted({tuple(sorted(x)) for x in jl}), [("item", "sha")])
want = sorted(r["item"] for r in rj if r["tier"].startswith("T2") or r["calibration"])
ok("F2 judge list = T2 + calibration", sorted(x["item"] for x in jl), want)
cal = {r["item"] for r in rj if r["calibration"]}
pos = [i for i, x in enumerate(jl) if x["item"] in cal]
ok("F2 calibration claims interleaved (not all at one end)",
   bool(cal) and 0 < min(pos) and max(pos) < len(jl) - 1, True)
role = open(os.path.join(HERE, "roles", "arbiter.md")).read()
ok("F2 role text never names tiers.json or calibration",
   [w for w in ("tiers.json", "calibration", "arbiter_tiers", "tier`") if w in role], [])

# F3: a code file git cannot read is UNMEASURED (to tier 2), a file the commit deleted is skipped
u = [ev("verify", "UNREAD", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
     ev("close", "UNREAD", "2026-10-26T12:00:00Z", sha="unread", reason="verified"),
     ev("verify", "DELETED", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
     ev("close", "DELETED", "2026-10-26T12:00:00Z", sha="del", reason="verified")]
TU = tiers_of(u)[0]
ok("F3 unreadable blob is G5 UNMEASURED", TU["UNREAD"]["gates"]["G5_review"], "UNMEASURED")
ok("F3 unreadable blob goes to tier 2", TU["UNREAD"]["tier"], "T2_UNMEASURED")
ok("F3 deleted file is not a review gap", TU["DELETED"]["gates"]["G5_review"], "PASS")

# F4: a missing past-audits file is UNMEASURED, not "nothing failed"
td = tempfile.mkdtemp()
ok("F4 missing past audits exits 2", at.main(["--data", td, "--judge-dir", td, "--past-audits",
                                               os.path.join(td, "nope.jsonl"), "--evidence-dir", td],
                                              events=events), 2)
ok("F4 nothing written on UNMEASURED", sorted(os.listdir(td)), [])

# F5: verify and close by the same seat (no claim event) is not a tier-0 pass
f5 = [ev("verify", "SELF", "2026-10-26T11:00:00Z", seat="BENCH", result="pass"),
      ev("close", "SELF", "2026-10-26T12:00:00Z", seat="BENCH", sha="good", reason="verified")]
T5 = tiers_of(f5)[0]["SELF"]
ok("F5 builder's own verify is not independent", T5["gates"]["G2_independent"], "FAIL")
ok("F5 builder's own verify does not pass tier 0", T5["tier"] != "T0_PASS", True)

# F6: a later dirty record at the same content removes the clean mark; a later clean restores it
rv = tempfile.mkdtemp()
with open(os.path.join(rv, "A.jsonl"), "w") as f:
    for ts, vd, seat in (("2026-10-26T01:00:00Z", "clean", "BENCH"), ("2026-10-26T02:00:00Z", "dirty", "FOUNDRY")):
        f.write(json.dumps({"path": "p.py", "sha256": "h1", "verdict": vd, "ts": ts, "seat": seat}) + "\n")
    f.write(json.dumps({"path": "q.py", "sha256": "h2", "verdict": "dirty", "ts": "2026-10-26T01:00:00Z",
                        "seat": "BENCH"}) + "\n")
    f.write(json.dumps({"path": "q.py", "sha256": "h2", "verdict": "clean", "ts": "2026-10-26T03:00:00Z",
                        "seat": "FOUNDRY"}) + "\n")
lc = at.load_clean_hashes(os.path.join(rv, "*.jsonl"))
ok("F6 later dirty overrides clean", ("p.py", "h1") in lc, False)
ok("F6 later clean restores, with reviewer seat", lc.get(("q.py", "h2")), {"FOUNDRY"})
f6 = [ev("verify", "MAKERREV", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
      ev("close", "MAKERREV", "2026-10-26T12:00:00Z", seat="BENCH", sha="good", reason="verified")]
T6 = tiers_of(f6, clean={("src/a.py", "H_src/a.py"): {"BENCH"}})[0]["MAKERREV"]
ok("F6 review only by the closing seat is flagged", "review_by_closing_seat_only" in T6["flags"], True)
ok("F6 maker-seat review is not a tier-0 pass", T6["tier"] != "T0_PASS", True)

# F7: calibration is a keyed per-claim draw: about 1 in 10 at any size, the same pick in any window
big = []
for i in range(1000):
    big += [ev("verify", "C%04d" % i, "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
            ev("close", "C%04d" % i, "2026-10-26T12:00:00Z", sha="docs", reason="verified")]
_, rb, _ = tiers_of(big, salt="k1")
npass = sum(1 for r in rb if r["tier"] in ("T0_PASS", "T1_PASS"))
nc = sum(1 for r in rb if r["calibration"])
ok("F7 calibration rate near 1/10", 0.07 < nc / float(npass) < 0.13, True)
small_ids = [r["item"] for r in rb if r["calibration"]][:3] + [r["item"] for r in rb if not r["calibration"]][:6]
small = [e for e in big if e["id"] in small_ids]
_, rs, _ = tiers_of(small, salt="k1")
ok("F7 a 9-pass window still calibrates, same picks as the big window",
   sorted(r["item"] for r in rs if r["calibration"]), sorted(small_ids[:3]))
ok("F7 salt changes the picks", sorted(r["item"] for r in tiers_of(big, salt="k2")[1] if r["calibration"])
   != sorted(r["item"] for r in rb if r["calibration"]), True)
ok("calibration only from passes", all(r["tier"] in ("T0_PASS", "T1_PASS") for r in rb if r["calibration"]), True)

# F8 + F2: main keeps a per-run record and a history, writes the judge list away from the labels
d8, j8 = tempfile.mkdtemp(), tempfile.mkdtemp()
pa = os.path.join(d8, "audits.jsonl")
open(pa, "w").close()
os.environ[at.SALT_ENV] = "selftest"
rc = at.main(["--data", d8, "--judge-dir", j8, "--past-audits", pa, "--evidence-dir", j8,
              "--now", "2026-10-27T00:00:00Z"], events=events,
             _inject={"git": git, "clean": CLEAN, "blob": blob, "exists": exists})
ok("F8 main runs", rc, 0)
ok("F8 per-run file kept beside tiers.json",
   sorted(f for f in os.listdir(d8) if f.startswith("tiers")), ["tiers.json", "tiers_20261027T000000Z.json",
                                                                 "tiers_history.jsonl"])
hist = [json.loads(l) for l in open(os.path.join(d8, "tiers_history.jsonl"))]
ok("F8 history has a row per claim", len(hist), len(rows))
ok("F2 judge dir holds no tier labels", "tier" in open(os.path.join(j8, "judge_list.json")).read()
   or "calibration" in open(os.path.join(j8, "judge_list.json")).read(), False)
with open(os.path.join(j8, "verdicts.jsonl"), "w") as f:
    f.write(json.dumps({"item": "HARNESS", "sha": "harn", "verdict": "PASS"}) + "\n")
ok("F2 join adds the tier by code", at.main(["join", "--verdicts", os.path.join(j8, "verdicts.jsonl"),
                                             "--data", d8]), 0)
ok("F2 joined tier", json.loads(open(os.path.join(d8, "verdicts_tiered.jsonl")).readline())["tier"], "T2_RISK")

# F9 / F10 / F11: role and design text
ok("F9 advisory bounce is a record only", "nothing is sent back to the builder" in role.lower(), True)
ok("F10 no token, cost or quota talk in the role",
   re.findall(r"(?i)\b(tokens?|token-\w+|quotas?|budgets?|costs?|burn|spend\w*|caps?)\b", role), [])
ok("F10 role points at blind_view and digest_blind", "blind_view.py" in role and "digest_blind.md" in role, True)
ok("F11 role batch takes closes only", "implemented" not in role.split("## When you run")[1].split("##")[0], True)

# F12: G4 reads only the latest verify per criterion, and some-paths-gone is UNMEASURED with the missing listed
f12 = [ev("verify", "OLDFAIL", "2026-10-26T10:00:00Z", seat="RUNNER", result="fail", evidence="/mnt/d/w/gone.png"),
       ev("verify", "OLDFAIL", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass", evidence="/mnt/d/w/there.png"),
       ev("close", "OLDFAIL", "2026-10-26T12:00:00Z", sha="good", reason="verified"),
       ev("verify", "PART", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass",
          evidence="/mnt/d/w/there.png; /mnt/d/w/a.png; /mnt/d/w/b.png"),
       ev("close", "PART", "2026-10-26T12:00:00Z", sha="good", reason="verified")]
T12 = tiers_of(f12)[0]
ok("F12 superseded verify's gone path does not bounce", T12["OLDFAIL"]["gates"]["G4_evidence"], "PASS")
ok("F12 partial evidence is UNMEASURED", T12["PART"]["gates"]["G4_evidence"], "UNMEASURED")
ok("F12 missing paths reported", T12["PART"]["gate_evidence"]["G4_evidence"], ["/mnt/d/w/a.png", "/mnt/d/w/b.png"])
ok("F12 partial evidence goes to tier 2", T12["PART"]["tier"], "T2_UNMEASURED")

# F13: a git error is UNMEASURED, not a bounce
f13 = [ev("verify", "GERR", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
       ev("close", "GERR", "2026-10-26T12:00:00Z", sha="gerr", reason="verified")]
T13 = tiers_of(f13)[0]["GERR"]
ok("F13 git error is G1 UNMEASURED", T13["gates"]["G1_sha"], "UNMEASURED")
ok("F13 git error goes to tier 2, not a bounce", T13["tier"], "T2_UNMEASURED")
ok("F13 unknown sha in a real clone reads unresolvable", at.git_files_any("0" * 40, repos=(at.REPO,)), None)

# G6 close evidence (close_evidence records at the close sha)
def rec(sha, result, paths, seat=None, dirty=False, item=None, ts="2026-10-26T11:00:00+00:00", tool="selftest"):
    return {"sha": sha, "dirty": dirty, "result": result, "paths": paths, "seat": seat, "item": item, "ts": ts,
            "tool": tool}


SH = "abcdef1234567"
FILES[SH] = {"src/m/mod.py": "M"}
g6 = [ev("claim", "EV", "2026-10-26T09:00:00Z"),
      ev("close", "EV", "2026-10-26T12:00:00Z", sha=SH, reason="done")]
CL6 = {("src/m/mod.py", "H_src/m/mod.py"): {"RUNNER"}}


def t6(recs):
    return tiers_of(g6, clean=CL6, evidence_lookup=lambda sha, item, paths: at.covering(
        recs, sha, item, {p: "M" for p in paths}))[0]["EV"]


ok("G6 no lines and no review: no machine evidence -> T2",
   tiers_of(g6, clean={})[0]["EV"]["tier"], "T2_NOEVIDENCE")
ok("G6 selftest beside the module covers it, PASS",
   t6([rec(SH, "PASS", ["src/m/selftest_mod.py"])])["gates"]["G6_close_evidence"], "PASS")
ok("G6 any latest FAIL bounces", t6([rec(SH, "FAIL", ["src/m/selftest_mod.py"])])["tier"], "T0_BOUNCE")
ok("G6 later PASS of the same run supersedes a FAIL",
   t6([rec(SH, "FAIL", ["src/m"]), rec(SH, "PASS", ["src/m"], ts="2026-10-26T11:30:00+00:00")])
   ["gates"]["G6_close_evidence"], "PASS")
ok("G6 dirty-tree record is not evidence", t6([rec(SH, "PASS", ["src/m"], dirty=True)])["gates"]["G6_close_evidence"],
   "NONE")
ok("G6 other sha is not evidence", t6([rec("9999999aaaaaa", "PASS", ["src/m"])])["gates"]["G6_close_evidence"], "NONE")
ok("G6 unrelated paths are not evidence", t6([rec(SH, "PASS", ["src/other"])])["gates"]["G6_close_evidence"], "NONE")
ok("G6 item-tagged record covers", t6([rec(SH, "PASS", ["x"], item="EV")])["gates"]["G6_close_evidence"], "PASS")
ok("G6 UNMEASURED run goes to tier 2", t6([rec(SH, "UNMEASURED", ["src/m"])])["tier"], "T2_UNMEASURED")
ok("G6 PASS with no recorded seat: independence UNMEASURED, no tier-0 pass",
   (t6([rec(SH, "PASS", ["src/m"])])["gates"]["G6_independent"], t6([rec(SH, "PASS", ["src/m"])])["tier"] != "T0_PASS"),
   ("UNMEASURED", True))
ok("G6 PASS by the builder's seat is not independent",
   t6([rec(SH, "PASS", ["src/m"], seat="BENCH")])["gates"]["G6_independent"], "FAIL")
ok("G6 PASS by another seat passes tier 0", t6([rec(SH, "PASS", ["src/m"], seat="RUNNER")])["tier"], "T0_PASS")
ok("G6 PASS is machine evidence (ranked, not T2_NOEVIDENCE)",
   t6([rec(SH, "PASS", ["src/m"])])["tier"] != "T2_NOEVIDENCE", True)

# empty ledger is UNMEASURED, not a zero mix
# lookup_close_evidence against the close_evidence interface: lookup(sha=, item=, paths=) after the review-Z fix,
# the sha-only lookup before it. Injected evidence only; the live evidence files are never read here.
_real = at.ce.lookup
POOL = [rec(SH, "PASS", ["src/m"]), rec(SH, "PASS", ["src/other"]), rec(SH, "FAIL", ["x"], item="EV")]


def _new_lookup(sha=None, item=None, paths=None, folder=None, days=30, **kw):
    out = [r for r in POOL if r["sha"] == sha]
    if paths is not None:
        out = [r for r in out if any(at._covers(q, f) for q in r["paths"] for f in paths)]
    if item is not None:
        out = [r for r in out if r.get("item") == item]
    return [dict(r) for r in out]


def _old_lookup(sha=None, item=None, folder=None, days=30, tool=None, include_dirty=False):
    return [dict(r) for r in POOL if r["sha"] == sha and (item is None or r.get("item") == item)]


try:
    at.ce.lookup = _new_lookup
    got_new = sorted(r["result"] for r in at.lookup_close_evidence(SH, "EV", ["src/m/mod.py"]))
    at.ce.lookup = _old_lookup
    got_old = sorted(r["result"] for r in at.lookup_close_evidence(SH, "EV", ["src/m/mod.py"]))
finally:
    at.ce.lookup = _real
ok("lookup with paths=: covering run plus item-tagged run, unrelated run dropped", got_new, ["FAIL", "PASS"])
ok("lookup without paths= (pre-fix): same claim gets the same runs", got_old, ["FAIL", "PASS"])

ok("empty ledger exits 2", at.main(["--data", td, "--judge-dir", td], events=[]), 2)

print("\n%s" % ("ALL PASS" if not FAILED else "FAILED: %s" % FAILED))
sys.exit(1 if FAILED else 0)
