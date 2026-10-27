"""selftest_arbiter_tiers.py - python3 src/RimMandrake/rimflow/selftest_arbiter_tiers.py"""
import json, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import arbiter_tiers as at                            # noqa: E402
from rimflow import audit_prescreen as ap                          # noqa: E402

FAILED = []
HERE = os.path.dirname(os.path.abspath(__file__))
ce = at.ce
EVD = tempfile.mkdtemp()                                   # the close_evidence store and its mac key for this run only:
os.environ[ce.ENV_DIR] = EVD                               # the live store is never read or written here
os.environ[ce.KEY_ENV] = os.path.join(tempfile.mkdtemp(), "close_evidence.key")
ce._key(create=True)


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


def with_builder(events, builder="BENCH"):
    """A claim event by `builder` for every item the fixture gives no claim/start/implemented event, so the builder
    is known (review AA7: with none, independence is UNMEASURED)."""
    named = {e["id"] for e in events if e.get("event") in ("claim", "start", "reclaim", "implemented")}
    return [ev("claim", i, "2026-10-26T08:00:00Z", seat=builder)
            for i in sorted({e["id"] for e in events} - named)] + list(events)


def tiers_of(events, builder="BENCH", **kw):
    """builder: see with_builder (None: leave the builder unknown)."""
    if builder:
        events = with_builder(events, builder)
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

# F5: verify and close by the builder's seat is not a tier-0 pass; with no builder named, independence is unknown
f5 = [ev("verify", "SELF", "2026-10-26T11:00:00Z", seat="BENCH", result="pass"),
      ev("close", "SELF", "2026-10-26T12:00:00Z", seat="BENCH", sha="good", reason="verified")]
T5 = tiers_of(f5)[0]["SELF"]
ok("F5 builder's own verify is not independent", T5["gates"]["G2_independent"], "FAIL")
ok("F5 builder's own verify does not pass tier 0", T5["tier"] != "T0_PASS", True)
ok("AA6 builder's bare self-verify is not machine evidence",
   tiers_of([dict(e, sha="docs") if e["event"] == "close" else e for e in f5])[0]["SELF"]["tier"], "T2_NOEVIDENCE")
T5n = tiers_of(f5, builder=None)[0]["SELF"]
ok("AA7 no builder in the ledger: G2 independence UNMEASURED", T5n["gates"]["G2_independent"], "UNMEASURED")
ok("AA7 no builder in the ledger goes to AI review", T5n["tier"], "T2_UNMEASURED")
f5o = [ev("verify", "OWNCL", "2026-10-26T11:00:00Z", seat="BENCH", result="pass", evidence=r"D:\w\there.png"),
       ev("close", "OWNCL", "2026-10-26T12:00:00Z", seat="OWNER", sha="good", reason="relayed")]
ok("AA7 OWNER close, no claim: a BENCH verify is not independent",
   tiers_of(f5o, builder=None)[0]["OWNCL"]["gates"]["G2_independent"], "UNMEASURED")
ok("AA7 OWNER is never the builder: claim by BENCH, close by OWNER, BENCH verify FAILs independence",
   tiers_of(f5o)[0]["OWNCL"]["gates"]["G2_independent"], "FAIL")
ok("AA6 a self-verify citing evidence that exists is still machine evidence",
   tiers_of(f5o)[0]["OWNCL"]["machine_evidence"], True)

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
              "--now", "2026-10-27T00:00:00Z"], events=with_builder(events),
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

# G6 close evidence, through the REAL close_evidence store (temp folder + temp key, set at the top): lines are written
# by ce.record() as a tool would, or forged the way review AA forged them, and read back by lookup_close_evidence.
REPO6 = tempfile.mkdtemp()
_N6 = [0]
_WHO_ENV = ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_BRIDGE_SESSION_ID")


def minted(sha, dirty=False):
    """A tree state as snapshot()/tree_state() mint it in this process (the git read itself is not under test)."""
    st = {"sha": sha, "dirty": dirty, "dirty_n": 1 if dirty else 0}
    st[ce._TOKEN] = ce._state_token(st)
    return st


def put(sha, result, paths, seat="RUNNER", item=None, variant=None, dirty=False, session=None, tool=None):
    """One line written by ce.record() from a process whose environment names `seat` (None: names no seat)."""
    saved = {k: os.environ.get(k) for k in _WHO_ENV}
    try:
        for k in _WHO_ENV:
            os.environ.pop(k, None)
        if seat:
            os.environ["RIMFLOW_SEAT"] = seat
        if session:
            os.environ["CLAUDE_CODE_BRIDGE_SESSION_ID"] = session
        st = minted(sha, dirty)
        r = ce.record(tool or ("validate_patch" if variant else "selftest"), result,
                      [os.path.join(REPO6, p) for p in paths], clone=REPO6, item=item, start=st, end=st,
                      variant=variant, force=True)
        assert r, "ce.record wrote nothing"
        return r
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def append_raw(rec):
    with open(os.path.join(EVD, "%s.jsonl" % (rec.get("ts") or "2026-10-27")[:10]), "a") as f:
        f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")


def claim6(files=None, close_seat="BENCH", builder="BENCH"):
    """A fresh claim (its own sha and item) -> (item, sha)."""
    _N6[0] += 1
    sha, iid = "%040x" % (0xabc0000 + _N6[0]), "EV%02d" % _N6[0]
    FILES[sha] = dict(files or {"src/m/mod.py": "M"})
    evs = ([ev("claim", iid, "2026-10-26T09:00:00Z", seat=builder)] if builder else []) + \
          [ev("close", iid, "2026-10-26T12:00:00Z", seat=close_seat, sha=sha, reason="done; selftest PASS")]
    return iid, sha, evs


def run6(iid, evs, clean=None, session_of=lambda sha: None):
    files = {p for sha in FILES for p in (FILES[sha] if isinstance(FILES[sha], dict) else ())}
    cl = {(p, "H_" + p): {"CHECK"} for p in files} if clean is None else clean
    return tiers_of(evs, builder=None, clean=cl, session_of=session_of,
                    evidence_lookup=lambda sha, item, paths: at.lookup_close_evidence(sha, item, paths,
                                                                                       folder=EVD))[0][iid]


def g6(row):
    return row["gates"]["G6_close_evidence"], row["gates"]["G6_independent"]


i, s6, e6 = claim6()
ok("G6 no lines and no review: no machine evidence -> T2", run6(i, e6, clean={})["tier"], "T2_NOEVIDENCE")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"])
r6 = run6(i, e6)
ok("G6 selftest beside the module, by another seat: PASS, independent, tier 0", (g6(r6), r6["tier"]),
   (("PASS", "PASS"), "T0_PASS"))
i, s6, e6 = claim6()
put(s6, "FAIL", ["src/m/selftest_mod.py"])
ok("G6 any latest FAIL bounces", run6(i, e6)["tier"], "T0_BOUNCE")
i, s6, e6 = claim6()
put(s6, "FAIL", ["src/m"])
put(s6, "PASS", ["src/m"])
ok("G6 later PASS of the same run supersedes a FAIL", g6(run6(i, e6))[0], "PASS")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m"], dirty=True)
ok("G6 dirty-tree record is not evidence", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6()
put("9" * 40, "PASS", ["src/m"])
ok("G6 other sha is not evidence", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/other"])
ok("G6 unrelated paths are not evidence", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6()
put(s6, "UNMEASURED", ["src/m"])
ok("G6 UNMEASURED run goes to tier 2", run6(i, e6)["tier"], "T2_UNMEASURED")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m"], seat=None)
r6 = run6(i, e6)
ok("G6 PASS with no recorded seat: independence UNMEASURED, no tier-0 pass", (g6(r6)[1], r6["tier"] != "T0_PASS"),
   ("UNMEASURED", True))
ok("G6 PASS is machine evidence (not T2_NOEVIDENCE)", r6["tier"] != "T2_NOEVIDENCE", True)
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m"], seat="BENCH")
ok("G6 PASS by the builder's seat is not independent", g6(run6(i, e6))[1], "FAIL")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m"], session="session_01Maker")
r6 = run6(i, e6, session_of=lambda sha: "session_01Maker" if sha == s6 else None)
ok("G6 a run by the session that made the commit (Claude-Session) is not independent", g6(r6)[1], "FAIL")
ok("G6 same-session run is no tier-0 pass", r6["tier"] != "T0_PASS", True)
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m"], session="session_01Other")
ok("G6 a run by another session and seat stays independent",
   g6(run6(i, e6, session_of=lambda sha: "session_01Maker"))[1], "PASS")

# Review AA's six forged claims (tierprobe): each must be refused tier 0.
# PART: two paths touched, a selftest covers one of them.
i, s6, e6 = claim6({"src/a.py": "M", "src/z.cs": "M"})
put(s6, "PASS", ["src/selftest_a.py"], seat="FOUNDRY")
r6 = run6(i, e6)
ok("AA-PART a run covering some paths is OPEN, uncovered named", (g6(r6)[0], r6["gate_evidence"].get("G6_uncovered")),
   ("OPEN", ["src/z.cs"]))
ok("AA-PART is no tier-0 pass", r6["tier"] != "T0_PASS", True)
i, s6, e6 = claim6({"src/a.py": "M", "src/z.cs": "M"})
put(s6, "PASS", ["src/selftest_a.py"], seat="FOUNDRY")
put(s6, "PASS", ["src/z.cs"], seat="FOUNDRY", tool="winbuild")
ok("AA-PART control: every path covered is PASS", g6(run6(i, e6)), ("PASS", "PASS"))
# OWN: no claim in the ledger, OWNER closes, the builder's seat ran the selftest.
i, s6, e6 = claim6({"src/b.py": "M"}, close_seat="OWNER", builder=None)
put(s6, "PASS", ["src/selftest_b.py"], seat="BENCH")
r6 = run6(i, e6)
ok("AA-OWN no builder named: independence UNMEASURED -> AI review", (g6(r6)[1], r6["tier"]),
   ("UNMEASURED", "T2_UNMEASURED"))
i, s6, e6 = claim6({"src/b.py": "M"}, close_seat="OWNER", builder="BENCH")
put(s6, "PASS", ["src/selftest_b.py"], seat="BENCH")
ok("AA-OWN OWNER close never makes the builder's run independent", g6(run6(i, e6))[1], "FAIL")
# STAT: a static validate_patch never stands in for the --defs run.
i, s6, e6 = claim6({"Patches/p.xml": "M"})
put(s6, "PASS", ["Patches/p.xml"], seat="FOUNDRY", variant="static")
r6 = run6(i, e6)
ok("AA-STAT a static validate_patch is OPEN, not PASS", (g6(r6)[0], r6["tier"] != "T0_PASS"), ("OPEN", True))
put(s6, "PASS", ["Patches/p.xml"], seat="FOUNDRY", tool="validate_patch")
ok("AA-STAT control: the full (--defs) run passes", g6(run6(i, e6)), ("PASS", "PASS"))
i, s6, e6 = claim6({"Patches/p.xml": "M"})
put(s6, "PASS", ["Patches/p.xml"], seat="FOUNDRY", variant="defnames")
ok("AA-STAT a --live/--defnames validate_patch is not the full run either", g6(run6(i, e6))[0], "OPEN")
# TAG: a run tagged with the item but covering none of its paths.
i, s6, e6 = claim6({"src/c.py": "M"})
put(s6, "PASS", ["src/unrelated/selftest_q.py"], seat="FOUNDRY", item=i)
r6 = run6(i, e6)
ok("AA-TAG an item tag never supplies a PASS", (g6(r6)[0], r6["tier"] != "T0_PASS"), ("NONE", True))
i, s6, e6 = claim6({"src/c.py": "M"})
put(s6, "FAIL", ["src/unrelated/selftest_q.py"], seat="FOUNDRY", item=i)
ok("AA-TAG an item-tagged FAIL still bounces", run6(i, e6)["tier"], "T0_BOUNCE")
# FORGE: a `record` CLI payload asserting sha, clean start and end, and seat RUNNER.
import subprocess                                                          # noqa: E402
i, s6, e6 = claim6({"src/d.py": "M"})
pay = {"tool": "selftest", "result": "PASS", "paths": [os.path.join(REPO6, "src/selftest_d.py")], "clone": REPO6,
       "start": {"sha": s6, "dirty": False, "dirty_n": 0}, "end": {"sha": s6, "dirty": False, "dirty_n": 0},
       "who": {"seat": "RUNNER", "seat_from": "RIMFLOW_SEAT"}, "evidence_dir": EVD}
cp = subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), "Utils", "close_evidence.py"), "record"],
                    input=json.dumps(pay), capture_output=True, text=True, timeout=120)
ok("AA-FORGE the record CLI still writes its line", cp.returncode, 0)
ok("AA-FORGE a record-CLI payload is never sha evidence", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6({"src/d.py": "M"})
st = {"sha": s6, "dirty": False, "dirty_n": 0}                             # typed in, not minted by snapshot()
append_raw(ce.seal(ce.build_record("selftest", "PASS", [os.path.join(REPO6, "src/selftest_d.py")], clone=REPO6,
                                   start=st, end=st)))
ok("AA-FORGE in-process line with a typed-in start/end is not evidence", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6({"src/d.py": "M"})
append_raw(ce.seal(ce.build_record("selftest", "PASS", [os.path.join(REPO6, "src/selftest_d.py")], clone=REPO6,
                                   start=minted(s6), end=minted(s6), who={"seat": "RUNNER",
                                                                         "seat_from": "RIMFLOW_SEAT"})))
ok("AA-FORGE a caller-supplied WHO never makes a run independent", g6(run6(i, e6)), ("PASS", "UNMEASURED"))
# NOV: a hand-appended line with no v (and v2, and an edited sealed line).
i, s6, e6 = claim6({"src/e.py": "M"})
append_raw({"tool": "selftest", "sha": s6, "dirty": False, "result": "PASS", "paths": ["src/selftest_e.py"],
            "seat": "RUNNER", "ts": "2026-10-27T00:00:01+00:00"})
ok("AA-NOV a line with no v is not evidence", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6({"src/e.py": "M"})
append_raw({"v": 2, "tool": "selftest", "sha": s6, "dirty": False, "result": "PASS", "paths": ["src/selftest_e.py"],
            "covers": ["src/selftest_e.py"], "start": {"sha": s6, "dirty": False, "dirty_n": 0}, "seat": "RUNNER",
            "ts": "2026-10-27T00:00:02+00:00", "live_only": False, "variant": None})
ok("AA-NOV a v2 line is not evidence", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6({"src/e.py": "M"})
fake = put(s6, "FAIL", ["src/selftest_e.py"])
fake = dict(fake, result="PASS", ts="2026-10-27T23:59:59+00:00")          # FAIL edited to PASS, mac left as it was
append_raw(fake)
ok("AA-NOV an edited sealed line (bad mac) is not evidence; the real FAIL still bounces", run6(i, e6)["tier"],
   "T0_BOUNCE")

# lookup_close_evidence: covering runs plus item-tagged non-PASS runs; an item-tagged PASS elsewhere is dropped
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m"])
put(s6, "PASS", ["src/other"])
put(s6, "PASS", ["x"], item=i)
put(s6, "FAIL", ["y"], item=i)
ok("lookup: covering run + item-tagged FAIL; unrelated run and item-tagged PASS dropped",
   sorted((r["result"], tuple(r["paths"])) for r in at.lookup_close_evidence(s6, i, ["src/m/mod.py"], folder=EVD)),
   [("FAIL", ("y",)), ("PASS", ("src/m",))])
_kp = os.environ[ce.KEY_ENV]
os.environ[ce.KEY_ENV] = os.path.join(EVD, "no_such.key")
try:
    at.lookup_close_evidence(s6, i, ["src/m/mod.py"], folder=EVD)
    ok("missing mac key raises (UNMEASURED, never 'no evidence')", "no raise", "raise")
except RuntimeError:
    ok("missing mac key raises (UNMEASURED, never 'no evidence')", "raise", "raise")
d9 = tempfile.mkdtemp()
pa9 = os.path.join(d9, "audits.jsonl")
open(pa9, "w").close()
ok("main with no mac key exits 2", at.main(["--data", d9, "--judge-dir", d9, "--past-audits", pa9,
                                             "--evidence-dir", EVD], events=events, _inject={"clean": CLEAN}), 2)
os.environ[ce.KEY_ENV] = _kp
with open(pa9, "w") as f:
    f.write('{"item": "GOOD", "verdict": "DEFECT"}\n{"item": "X", "verd')
ok("main with a torn past-audit line exits 2", at.main(["--data", d9, "--judge-dir", d9, "--past-audits", pa9,
                                                         "--evidence-dir", EVD], events=events,
                                                        _inject={"clean": CLEAN}), 2)
ok("nothing written on either", sorted(f for f in os.listdir(d9) if f != "audits.jsonl"), [])

ok("empty ledger exits 2", at.main(["--data", td, "--judge-dir", td], events=[]), 2)

print("\n%s" % ("ALL PASS" if not FAILED else "FAILED: %s" % FAILED))
sys.exit(1 if FAILED else 0)
