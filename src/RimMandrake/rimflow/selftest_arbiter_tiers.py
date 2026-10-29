"""selftest_arbiter_tiers.py - python3 src/RimMandrake/rimflow/selftest_arbiter_tiers.py"""
import hashlib, hmac, json, os, re, sys, tempfile
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
# The fixtures below forge, replay and hand-append lines into TODAY's file to test the arbiter's reading of them; on/after
# ce.CHAIN_CUTOVER every such line is a chain TAMPER that poisons every later lookup. Pin today before the cutover so
# these checks keep testing what they name; the chain itself is pinned in Utils/selftest_close_evidence_chain.py.
ce.CHAIN_CUTOVER = "9999-12-31"


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
def SELF(seat, session=None):
    """A clean mark whose recorder (a whoami-sure seat) reviewed it (review_identity.identity)."""
    return {("self", seat, session)}


CLEAN = {("src/a.py", "H_src/a.py"): SELF("RUNNER"), ("src/RimMandrake/rimflow/x.py", "H_src/RimMandrake/rimflow/x.py"):
         SELF("RUNNER")}
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
# review AB1: an independent ledger verify never substitutes for independent isolated-checkout runs (G6): GOOD has
# no close evidence, so it ranks in tier 1 instead of passing tier 0 (the AB1 group shows it passing WITH G6)
ok("good (independent verify, no close evidence) is not PASS0 (AB1)", T["GOOD"]["tier"], "T1_PASS")
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
ok("F6 later clean restores; a record with no review block is reviewer-unknown", lc.get(("q.py", "h2")),
   {("unknown", "FOUNDRY", None)})
f6 = [ev("verify", "MAKERREV", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
      ev("close", "MAKERREV", "2026-10-26T12:00:00Z", seat="BENCH", sha="good", reason="verified")]
T6 = tiers_of(f6, clean={("src/a.py", "H_src/a.py"): SELF("BENCH")})[0]["MAKERREV"]
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
             _inject={"git": git, "clean": CLEAN, "blob": blob, "exists": exists,
                      "evidence_lookup": lambda sha, item, paths: []})   # fixture names, not shas; j8 holds no runs
ok("F8 main runs", rc, 0)
ok("F8 per-run file kept beside tiers.json",
   sorted(f for f in os.listdir(d8) if f.startswith("tiers")), ["tiers.json", "tiers_20261027T000000Z.json",
                                                                 "tiers_history.jsonl", "tiers_history.jsonl.lock"])
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


def iso_mark(sha):
    """Stamp REPO6 as an isolated checkout of `sha` (what ce.make_isolated leaves; the test is the forger here)."""
    os.makedirs(os.path.join(REPO6, ".git"), exist_ok=True)
    with open(os.path.join(REPO6, ".git", ce.ISOLATED_MARK), "w") as f:
        f.write(hmac.new(ce._key(), ce._iso_msg(REPO6, sha), hashlib.sha256).hexdigest())


def put(sha, result, paths, seat="RUNNER", item=None, variant=None, dirty=False, session=None, tool=None,
        shared=False, loads=None, covers=None, covers_by=None):
    """One line written by ce.record() from a process whose environment names `seat` (None: names no seat), in an
    isolated checkout of `sha` unless `shared` (a seat clone other agents use: never evidence -- review AB2).
    loads: sources the run's trace showed paths[0] loading (run_selftests records them as covers + detail.covers_by);
    covers / covers_by: raw values, for forging."""
    detail = None
    if loads:
        covers = list(paths) + list(loads)
        covers_by = {l: [paths[0]] for l in loads}
    if covers_by is not None:
        detail = {"covers_by": covers_by}
    saved = {k: os.environ.get(k) for k in _WHO_ENV}
    try:
        for k in _WHO_ENV:
            os.environ.pop(k, None)
        if seat:
            os.environ["RIMFLOW_SEAT"] = seat
        if session:
            os.environ["CLAUDE_CODE_BRIDGE_SESSION_ID"] = session
        st = minted(sha, dirty)
        if shared:
            try:
                os.unlink(os.path.join(REPO6, ".git", ce.ISOLATED_MARK))
            except OSError:
                pass
        else:
            iso_mark(sha)
        r = ce.record(tool or ("validate_patch" if variant else "selftest"), result,
                      [os.path.join(REPO6, p) for p in paths], clone=REPO6, item=item, start=st, end=st,
                      variant=variant, force=True, detail=detail,
                      covers=[os.path.join(REPO6, c) for c in covers] if covers is not None else None)
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


def run6(iid, evs, clean=None, session_of=lambda sha: None, **kw):
    files = {p for sha in FILES for p in (FILES[sha] if isinstance(FILES[sha], dict) else ())}
    cl = {(p, "H_" + p): SELF("CHECK") for p in files} if clean is None else clean
    return tiers_of(evs, builder=None, clean=cl, session_of=session_of, **kw,
                    evidence_lookup=lambda sha, item, paths: at.lookup_close_evidence(sha, item, paths,
                                                                                       folder=EVD))[0][iid]


def g6(row):
    return row["gates"]["G6_close_evidence"], row["gates"]["G6_independent"]


i, s6, e6 = claim6()
ok("G6 no lines and no review: no machine evidence -> T2", run6(i, e6, clean={})["tier"], "T2_NOEVIDENCE")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"])
r6 = run6(i, e6)
ok("G6 selftest that LOADED the module (traced), by another seat: PASS, independent, tier 0", (g6(r6), r6["tier"]),
   (("PASS", "PASS"), "T0_PASS"))
# SELFTEST_EVIDENCE_FIX_COVERS_TESTS_ONLY: coverage comes from the trace/declaration, never from the name.
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"])
r6 = run6(i, e6)
ok("COVERS a selftest beside the module that never loaded it covers only itself: not evidence for the module (NONE)",
   (g6(r6)[0], r6["tier"] == "T0_PASS"), ("NONE", False))
i, s6, e6 = claim6({"src/m/mod.py": "M", "src/m/other.py": "M"})
put(s6, "PASS", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"])
r6 = run6(i, e6)
ok("COVERS a touched source no ran test loads or declares stays OPEN",
   (g6(r6)[0], r6["gate_evidence"].get("G6_uncovered")), ("OPEN", ["src/m/other.py"]))
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], covers=["src/m/selftest_mod.py", "src/m/mod.py"])
ok("COVERS-FORGE a source in covers with no covers_by is refused (record vouches for nothing touched: NONE)", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], covers=["src/m/selftest_mod.py", "src/m/mod.py"],
    covers_by={"src/m/mod.py": ["src/m/selftest_other.py"]})
ok("COVERS-FORGE covers_by naming a test that did not run is refused (record vouches for nothing touched: NONE)", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], covers=["src/m/selftest_mod.py", "src/m"],
    covers_by={"src/m": ["src/m/selftest_mod.py"]})
ok("COVERS-FORGE a derived source never covers as a folder (record vouches for nothing touched: NONE)", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], covers=["src/m/selftest_mod.py", "*"],
    covers_by={"*": ["src/m/selftest_mod.py"]})
ok("COVERS-FORGE a derived '*' (cover everything) is refused (record vouches for nothing touched: NONE)", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6()
r = put(s6, "PASS", ["src/m/selftest_mod.py"])
append_raw(dict(r, covers=["src/m/selftest_mod.py", "src/m/mod.py"],
                detail=dict(r["detail"], covers_by={"src/m/mod.py": ["src/m/selftest_mod.py"]}),
                ts="2026-10-27T23:59:58+00:00"))
ok("COVERS-FORGE covers added to a sealed line after the fact (bad mac) is never a PASS",
   g6(run6(i, e6))[0] != "PASS", True)
i, s6, e6 = claim6()
put(s6, "FAIL", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"])
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
put(s6, "PASS", ["src/selftest_a.py"], seat="FOUNDRY", loads=["src/a.py"])
r6 = run6(i, e6)
ok("AA-PART a run covering some paths is OPEN, uncovered named", (g6(r6)[0], r6["gate_evidence"].get("G6_uncovered")),
   ("OPEN", ["src/z.cs"]))
ok("AA-PART is no tier-0 pass", r6["tier"] != "T0_PASS", True)
i, s6, e6 = claim6({"src/a.py": "M", "src/z.cs": "M"})
put(s6, "PASS", ["src/selftest_a.py"], seat="FOUNDRY", loads=["src/a.py"])
put(s6, "PASS", ["src/z.cs"], seat="FOUNDRY", tool="winbuild")
ok("AA-PART control: every path covered is PASS", g6(run6(i, e6)), ("PASS", "PASS"))
# OWN: no claim in the ledger, OWNER closes, the builder's seat ran the selftest.
i, s6, e6 = claim6({"src/b.py": "M"}, close_seat="OWNER", builder=None)
put(s6, "PASS", ["src/selftest_b.py"], seat="BENCH", loads=["src/b.py"])
r6 = run6(i, e6)
ok("AA-OWN no builder named: independence UNMEASURED -> AI review", (g6(r6)[1], r6["tier"]),
   ("UNMEASURED", "T2_UNMEASURED"))
i, s6, e6 = claim6({"src/b.py": "M"}, close_seat="OWNER", builder="BENCH")
put(s6, "PASS", ["src/selftest_b.py"], seat="BENCH", loads=["src/b.py"])
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
iso_mark(s6)
append_raw(ce.seal(ce.build_record("selftest", "PASS", [os.path.join(REPO6, "src/selftest_d.py")], clone=REPO6,
                                   start=st, end=st)))
ok("AA-FORGE in-process line with a typed-in start/end is not evidence", g6(run6(i, e6))[0], "NONE")
i, s6, e6 = claim6({"src/d.py": "M"})
iso_mark(s6)
append_raw(ce.seal(ce.build_record("selftest", "PASS", [os.path.join(REPO6, "src/selftest_d.py")], clone=REPO6,
                                   covers=[os.path.join(REPO6, c) for c in ("src/selftest_d.py", "src/d.py")],
                                   detail={"covers_by": {"src/d.py": ["src/selftest_d.py"]}},
                                   start=minted(s6), end=minted(s6), who={"seat": "RUNNER",
                                                                         "seat_from": "RIMFLOW_SEAT"})))
ok("AA-FORGE a caller-supplied WHO never makes a run independent", g6(run6(i, e6)), ("PASS", "UNMEASURED"))
# NOV: a hand-appended line with no v (and v2, and an edited sealed line).
i, s6, e6 = claim6({"src/e.py": "M"})
append_raw({"tool": "selftest", "sha": s6, "dirty": False, "result": "PASS", "paths": ["src/selftest_e.py"],
            "seat": "RUNNER", "ts": "2026-10-27T00:00:01+00:00"})
ok("AA-NOV a line with no v is not evidence (AB5: unverifiable -> UNMEASURED)", g6(run6(i, e6))[0], "UNMEASURED")
i, s6, e6 = claim6({"src/e.py": "M"})
append_raw({"v": 2, "tool": "selftest", "sha": s6, "dirty": False, "result": "PASS", "paths": ["src/selftest_e.py"],
            "covers": ["src/selftest_e.py"], "start": {"sha": s6, "dirty": False, "dirty_n": 0}, "seat": "RUNNER",
            "ts": "2026-10-27T00:00:02+00:00", "live_only": False, "variant": None})
ok("AA-NOV a v2 line is not evidence (AB5: unverifiable -> UNMEASURED)", g6(run6(i, e6))[0], "UNMEASURED")
i, s6, e6 = claim6({"src/e.py": "M"})
fake = put(s6, "FAIL", ["src/selftest_e.py"], loads=["src/e.py"])
fake = dict(fake, result="PASS", ts="2026-10-27T23:59:59+00:00")          # FAIL edited to PASS, mac left as it was
append_raw(fake)
ok("AA-NOV an edited sealed line (bad mac) is not evidence; the real FAIL still bounces", run6(i, e6)["tier"],
   "T0_BOUNCE")

# Review AB, one check group per real finding in arbiter_tiers (AB2-AB7 live in selftest_close_evidence).
# AB1: an independent ledger verify (G2) never substitutes for independent G6 coverage.
i, s6, e6 = claim6()
e6 = e6[:1] + [ev("verify", i, "2026-10-26T11:00:00Z", seat="RUNNER", result="pass")] + e6[1:]
r6 = run6(i, e6)
ok("AB1 a RUNNER verify with no close evidence is no tier-0 pass", (g6(r6)[0], r6["tier"] != "T0_PASS"), ("NONE", True))
i, s6, e6 = claim6()
e6 = e6[:1] + [ev("verify", i, "2026-10-26T11:00:00Z", seat="RUNNER", result="pass")] + e6[1:]
put(s6, "PASS", ["src/m"], seat="BENCH")
r6 = run6(i, e6)
ok("AB1 a RUNNER verify over builder-only runs (G6_independent FAIL) is no tier-0 pass",
   (g6(r6), r6["tier"] != "T0_PASS"), (("PASS", "FAIL"), True))
i, s6, e6 = claim6()
e6 = e6[:1] + [ev("verify", i, "2026-10-26T11:00:00Z", seat="RUNNER", result="pass")] + e6[1:]
put(s6, "PASS", ["src/m"])
ok("AB1 control: the verify WITH independent close evidence passes tier 0", run6(i, e6)["tier"], "T0_PASS")
# AB2: a run in a shared seat clone is recorded but never evidence
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m"], shared=True)
ok("AB2 a shared-clone run is not evidence", g6(run6(i, e6))[0], "NONE")
# AB4: PASS{m/*}, FAIL{m/b.py}, PASS{m/mod.py}: b's FAIL stands
i, s6, e6 = claim6({"src/m/mod.py": "M", "src/m/b.py": "M"})
put(s6, "PASS", ["src/m"])
put(s6, "FAIL", ["src/m/b.py"])
put(s6, "PASS", ["src/m/mod.py"])
r6 = run6(i, e6)
ok("AB4 a later narrow PASS never erases another path's FAIL", (g6(r6)[0], r6["tier"]), ("FAIL", "T0_BOUNCE"))
i, s6, e6 = claim6({"src/m/mod.py": "M", "src/m/b.py": "M"})
put(s6, "PASS", ["src/m"], seat="BENCH")
put(s6, "PASS", ["src/m/mod.py"])
r6 = run6(i, e6)
ok("AB4 an old builder-run wide PASS lends no independence to a path only it covers", (g6(r6)[1], r6["tier"] != "T0_PASS"),
   ("FAIL", True))
# AB8: a calibration pick with --ai-refused is HOLD, never a silent PASS
_, rr, _ = tiers_of(big, salt="k1", ai_refused=True)
cal = [r for r in rr if r["calibration"]]
ok("AB8 with ai_refused every calibration pick is HOLD", (bool(cal), {r["decision"] for r in cal}), (True, {"HOLD"}))
ok("AB8 control: without ai_refused calibration picks go to AI", {r["decision"] for r in rb if r["calibration"]}, {"AI"})


def _salt(d):
    os.environ.pop(at.SALT_ENV, None)
    try:
        return at.load_salt(d)
    except Exception as e:                                          # noqa: BLE001 -- the race outcome IS the result
        return "ERR %r" % e


def _mainrun(args):
    d, j = args
    return at.main(["--data", d, "--judge-dir", j, "--past-audits", pa, "--evidence-dir", j8,
                    "--now", "2026-10-27T00:00:00Z"], events=with_builder(events),
                   _inject={"git": git, "clean": CLEAN, "blob": blob, "exists": exists,
                            "evidence_lookup": lambda sha, item, paths: []})


import contextlib, io, multiprocessing                              # noqa: E401,E402
_ctx = multiprocessing.get_context("fork")
d9s = tempfile.mkdtemp()
with _ctx.Pool(16) as _pool:
    salts = _pool.map(_salt, [d9s] * 48)
ok("AB9 48 racing first-time salt initialisers read one complete salt",
   (len(set(salts)), len(salts[0]), sorted(os.listdir(d9s))), (1, 64, [".calib_salt"]))
d10, j10 = tempfile.mkdtemp(), tempfile.mkdtemp()
with contextlib.redirect_stdout(io.StringIO()), _ctx.Pool(6) as _pool:
    rcs = _pool.map(_mainrun, [(d10, j10)] * 6)
runs = sorted(f for f in os.listdir(d10) if f.startswith("tiers_2"))
ok("AB10 six concurrent runs all succeed and keep six per-run files", (rcs, runs),
   ([0] * 6, ["tiers_20261027T000000Z-%d.json" % k for k in range(2, 7)] + ["tiers_20261027T000000Z.json"]))
ok("AB10 no history line lost", sum(1 for _ in open(os.path.join(d10, "tiers_history.jsonl"))), 6 * len(rows))
ok("AB10 no tmp file left, judge list parses",
   ([f for f in os.listdir(d10) + os.listdir(j10) if f.endswith(".tmp")],
    isinstance(json.load(open(os.path.join(j10, "judge_list.json")))["claims"], list)), ([], True))

# ARBITER_DECIDE_BACKLOG_NEVER_DRAINS (BENCH delegated ruling 2026-10-27): the Arbiter judges claims closed after the
# cutoff stamp, oldest first, at most --cap a batch (UNRESOLVED re-judges count against it), never one that has a
# verdict line, never one isolated_evidence carried (it was not run yet: judged next batch with its evidence)
jr = [{"item": "Q%d" % k, "sha": "%07d" % k, "tier": "T2_NOEVIDENCE", "calibration": False,
       "closed_at": "2026-10-26T%02d:00:00Z" % (9 - k)} for k in range(6)]          # Q5 oldest ... Q0 newest
ok("CAP no cap: every T2 claim (unchanged)", len(at.judge_list(jr, "s")), 6)
ok("CAP cap 3 takes the 3 OLDEST", sorted(x["item"] for x in at.judge_list(jr, "s", cap=3)), ["Q3", "Q4", "Q5"])
ok("CAP excluded claims (verdict line / carried) are skipped, the next oldest fills in",
   sorted(x["item"] for x in at.judge_list(jr, "s", cap=3, exclude=[("Q5", "0000005"), ("Q4", "0000004abcdef")])),
   ["Q1", "Q2", "Q3"])
ok("CAP unresolved re-judges count against the cap", sorted(x["item"] for x in at.judge_list(jr, "s", cap=3, unresolved=2)),
   ["Q5"])
ok("CAP unresolved >= cap: no new claim this batch", at.judge_list(jr, "s", cap=3, unresolved=3), [])
FILES["docs1234"] = FILES["docs"]
ce_ = [ev("close", "K0", "2026-10-25T00:00:00Z", sha="docs1234", reason="pre-enable"),
       ev("close", "K1", "2026-10-26T01:00:00Z", sha="docs1234", reason="done"),
       ev("close", "K2", "2026-10-26T02:00:00Z", sha="docs1234", reason="done"),
       ev("close", "K3", "2026-10-26T03:00:00Z", sha="docs1234", reason="done"),
       ev("close", "K4", "2026-10-26T04:00:00Z", sha="docs1234", reason="done")]
dc, jc = tempfile.mkdtemp(), tempfile.mkdtemp()
_cut, _car = os.path.join(dc, "cutoff.json"), os.path.join(dc, "carried.json")
os.environ["RM_ARBITER_CUTOFF"], os.environ["RM_ISOLATED_CARRIED"] = _cut, _car
with open(os.path.join(jc, "verdicts.jsonl"), "w") as f:
    f.write(json.dumps({"item": "K1", "sha": "docs1234", "disposition": "PASS", "ts": "2026-10-26T20:00:00Z"}) + "\n")
    f.write(json.dumps({"item": "K3", "sha": "docs123", "disposition": "UNRESOLVED", "ts": "2026-10-26T20:00:00Z"}) + "\n")


def _cutrun(*extra):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return at.main(["--data", dc, "--judge-dir", jc, "--past-audits", pa, "--evidence-dir", j8,
                        "--now", "2026-10-27T00:00:00Z", "--since-cutoff"] + list(extra), events=with_builder(ce_),
                       _inject={"git": git, "clean": CLEAN, "blob": blob, "exists": exists,
                                "evidence_lookup": lambda sha, item, paths: []})


ok("CUT --since-cutoff with no stamp exits 2, nothing written", (_cutrun("--cap", "2"), os.listdir(jc)),
   (2, ["verdicts.jsonl"]))
from rimflow import arbiter_pending as PW                                    # noqa: E402
PW.stamp(_cut, "2026-10-25T12:00:00Z", by="SELFTEST", why="test")
ok("CUT no carried list from isolated_evidence exits 2 (its pre-step did not run)", _cutrun("--cap", "2"), 2)
with open(_car, "w") as f:
    json.dump({"generated": "2026-10-27T00:00:00Z", "carried": [{"item": "K2", "sha": "docs1234"}]}, f)
ok("CUT runs", _cutrun("--cap", "2"), 0)
_doc = json.load(open(os.path.join(dc, "tiers.json")))
ok("CUT since = the cutoff; pre-cutoff K0 and carried K2 are not tiered this batch",
   (_doc["since"], sorted(r["item"] for r in _doc["rows"])), ("2026-10-25T12:00:00Z", ["K1", "K3", "K4"]))
ok("CUT judge list: K1 has a verdict, K3 is an UNRESOLVED re-judge (1 of cap 2), so only K4",
   [x["item"] for x in json.load(open(os.path.join(jc, "judge_list.json")))["claims"]], ["K4"])
with open(_car, "w") as f:
    json.dump({"generated": "2026-10-27T00:00:00Z", "carried": []}, f)
_cutrun("--cap", "2")
ok("CUT once run, the carried claim is the oldest unjudged and goes first",
   [x["item"] for x in json.load(open(os.path.join(jc, "judge_list.json")))["claims"]], ["K2"])

# ARBITER run-now (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE trial path): --claim ITEM@SHA (repeatable) tiers only the named
# claims and forces EVERY one onto the judge list -- a T0 bounce, a PASS-tier claim, one that already has a verdict --
# so a hand-picked claim is judged by the Arbiter itself. A named claim not among the closes is UNMEASURED (exit 2,
# nothing written): the run must not start judging a list that silently lost a claim.
dk, jk = tempfile.mkdtemp(), tempfile.mkdtemp()


def _claimrun(*extra):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return at.main(["--data", dk, "--judge-dir", jk, "--past-audits", pa, "--evidence-dir", j8,
                        "--now", "2026-10-27T00:00:00Z", "--days", "5"] + list(extra), events=with_builder(ce_),
                       _inject={"git": git, "clean": CLEAN, "blob": blob, "exists": exists,
                                "evidence_lookup": lambda sha, item, paths: []})


with open(os.path.join(jk, "verdicts.jsonl"), "w") as f:
    f.write(json.dumps({"item": "K1", "sha": "docs1234", "disposition": "PASS", "ts": "2026-10-26T20:00:00Z"}) + "\n")
ok("CLAIM runs", _claimrun("--claim", "K1@docs1234", "--claim", "K4@docs123"), 0)
ok("CLAIM only the named claims are tiered",
   sorted(r["item"] for r in json.load(open(os.path.join(dk, "tiers.json")))["rows"]), ["K1", "K4"])
ok("CLAIM every named claim is on the judge list, one with a verdict too (short sha matches)",
   sorted(x["item"] for x in json.load(open(os.path.join(jk, "judge_list.json")))["claims"]), ["K1", "K4"])
for bad, why in ((("--claim", "NOPE@docs1234"), "not among the closes"), (("--claim", "K1"), "no @sha"),
                 (("--claim", "K1@zz"), "sha too short"), (("--claim", "K1@docs1234", "--cap", "3"), "with --cap"),
                 (("--claim", "K1@docs1234", "--since-cutoff"), "with --since-cutoff")):
    os.remove(os.path.join(jk, "judge_list.json")) if os.path.exists(os.path.join(jk, "judge_list.json")) else None
    ok("CLAIM refused (%s): exit 2, no judge list written" % why,
       (_claimrun(*bad), os.path.exists(os.path.join(jk, "judge_list.json"))), (2, False))

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
# AUDITOR_BUILD_AUDITS_FILE: arbiter_tiers reads audits.jsonl through audits.schema.json, not "item + verdict"
with open(pa9, "w") as f:
    f.write('{"item": "GOOD", "verdict": "DEFECT"}\n')       # JSON, item and verdict, but not the schema's line
ok("AF a line missing the schema's required fields exits 2", at.main(
    ["--data", d9, "--judge-dir", d9, "--past-audits", pa9, "--evidence-dir", EVD], events=events,
    _inject={"clean": CLEAN}), 2)
_full = {"ts": "2026-10-27T00:00:00Z", "item": "GOOD", "sha": "abc1234", "run": "rm-role-auditor-1",
         "why_picked": "rank", "flags": [], "verdict": "DEFECT", "defect_class": "check", "evidence": []}
with open(pa9, "w") as f:
    f.write(json.dumps(_full) + "\n" + json.dumps(dict(_full, item="OTHER", verdict="SOUND", defect_class=None)) + "\n")
ok("AF a schema line reads: DEFECT items only", at.past_failed_strict(pa9), {"GOOD"})

ok("empty ledger exits 2", at.main(["--data", td, "--judge-dir", td], events=[]), 2)

# ---- review AC (ARBITER_EVIDENCE_FIX_REPLAY_ERASES_FAIL). Last: a damaged line whose routing cannot be verified
# taints every later lookup in EVD, by design.
def _rewrite(rec, **changes):
    """Replace rec's line in its day file with the same line edited (no re-seal: the forger has no key)."""
    fn = os.path.join(EVD, "%s.jsonl" % rec["ts"][:10])
    lines = open(fn).read().splitlines()
    out = [json.dumps(dict(json.loads(l), **changes), sort_keys=True) if json.loads(l).get("mac") == rec["mac"] else l
           for l in lines]
    with open(fn, "w") as f:
        f.write("\n".join(out) + "\n")


# AC3: a byte-identical replay of a signed PASS (same second as the FAIL after it) never erases the FAIL
i, s6, e6 = claim6()
iso_mark(s6)
_t = __import__("datetime").datetime(2026, 10, 27, 13, 0, 0, tzinfo=__import__("datetime").timezone.utc)
_w = {"seat": "RUNNER", "seat_from": "RIMFLOW_SEAT"}
_kw = dict(clone=REPO6, covers=[os.path.join(REPO6, c) for c in ("src/m/selftest_mod.py", "src/m/mod.py")],
           detail={"covers_by": {"src/m/mod.py": ["src/m/selftest_mod.py"]}}, now=_t, who=_w)
_pass = ce.seal(ce.build_record("selftest", "PASS", [os.path.join(REPO6, "src/m/selftest_mod.py")],
                                start=minted(s6), end=minted(s6), **_kw))
_fail = ce.seal(ce.build_record("selftest", "FAIL", [os.path.join(REPO6, "src/m/selftest_mod.py")],
                                start=minted(s6), end=minted(s6), **_kw))
append_raw(_pass); append_raw(_fail)
ok("AC3 control: PASS then FAIL in the same second -> FAIL", g6(run6(i, e6))[0], "FAIL")
append_raw(_pass)
ok("AC3 a replayed signed PASS (same ts) does not erase the later FAIL", g6(run6(i, e6))[0], "FAIL")

# AC2: evidence is matched to ONE full sha; a rev expression or short sha never matches by prefix
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"])
def _refused(sha):
    try:
        ce.lookup(sha=sha, folder=EVD)
        return "accepted"
    except ValueError:
        return "refused"
ok("AC2 lookup refuses a rev expression (child^) and a short sha", (_refused(s6 + "^"), _refused(s6[:12])),
   ("refused", "refused"))
ok("AC2 a full sha still finds its runs", len(ce.lookup(sha=s6, folder=EVD)) >= 1, True)
_revs = {"/c1": "a" * 40, "/c2": "b" * 40}
ok("AC2 a short sha naming different commits in two clones is unresolvable (UNMEASURED), not either",
   at.resolve_sha_any("abcdef1", repos=["/c1", "/c2"], rev=lambda s, r: _revs[r]), at.GIT_ERROR)
ok("AC2 the same commit in both clones resolves to it",
   at.resolve_sha_any("abcdef1", repos=["/c1", "/c2"], rev=lambda s, r: "c" * 40), "c" * 40)
ok("AC2 a rev expression is not a sha", at.resolve_sha_any(s6 + "^", repos=["/c1"], rev=lambda s, r: "c" * 40), None)
_short = [dict(e, sha=s6[:12]) if e.get("event") == "close" else e for e in e6]
r6 = tiers_of(_short, builder=None, clean={(p, "H_" + p): SELF("CHECK") for p in FILES[s6]},
              resolve=lambda s: s6 if s6.startswith(s) else None,
              evidence_lookup=lambda sha, item, paths: at.lookup_close_evidence(sha, item, paths, folder=EVD))[0][i]
ok("AC2 classify resolves a short close sha once and matches evidence on the full sha", g6(r6), ("PASS", "PASS"))

# AC4: a Claude-Session lookup that could not read the commit is UNMEASURED independence, never PASS
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"], session="session_01Other")
ok("AC4 an unreadable commit session -> G6_independent UNMEASURED",
   g6(run6(i, e6, session_of=lambda sha: at.SESSION_UNREADABLE))[1], "UNMEASURED")
ok("AC4 commit_session with no clone able to read the commit says so",
   at.commit_session("f" * 40, repos=[os.path.join(EVD, "no_such_clone")]), at.SESSION_UNREADABLE)

# AC5: a non-ASCII mac is an unverifiable line, never a crash
ok("AC5 mac_ok on a non-ASCII mac is False", ce.mac_ok({"mac": "\u00e9"}, ce._key()), False)
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"])
_r = put(s6, "FAIL", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"])
_rewrite(_r, mac="\u00e9")
d5 = tempfile.mkdtemp()
open(os.path.join(d5, "audits.jsonl"), "w").close()
try:
    _rc = at.main(["--data", d5, "--judge-dir", d5, "--past-audits", os.path.join(d5, "audits.jsonl"),
                   "--evidence-dir", EVD, "--now", "2026-10-27T12:00:00Z"], events=with_builder(e6),
                  _inject={"clean": {(p, "H_" + p): SELF("CHECK") for p in FILES[s6]}, "git": git, "blob": blob,
                           "exists": exists})
    _row = [r for r in json.load(open(os.path.join(d5, "tiers.json")))["rows"] if r["item"] == i] if _rc == 0 else []
    ok("AC5 a non-ASCII mac line does not crash the batch; its claim is not a tier-0 PASS",
       (_rc, [r["tier"] == "T0_PASS" for r in _row]), (0, [False]))
except TypeError as ex:
    ok("AC5 a non-ASCII mac line does not crash the batch; its claim is not a tier-0 PASS", "crash %s" % ex, "no crash")

# AC1: a FAIL whose sha was damaged (one hex digit) is unverifiable and may be ours: UNMEASURED, not the older PASS
i, s6, e6 = claim6()
put(s6, "PASS", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"])
_r = put(s6, "FAIL", ["src/m/selftest_mod.py"], loads=["src/m/mod.py"])
_rewrite(_r, sha=s6[:-1] + ("0" if s6[-1] != "0" else "1"))
r6 = run6(i, e6)
ok("AC1 a damaged-sha FAIL leaves the claim UNMEASURED, not T0_PASS", (g6(r6)[0], r6["tier"] == "T0_PASS"),
   ("UNMEASURED", False))

# TIERS_FIX_G6_BLIND_WITHOUT_BUILDER: no claim/start/implemented before the close -> the builder is inferred from the
# close seat and the seats the commit's session ran shared-tree runs as. Agreeing sources name it; disagreeing or no
# sources stay UNMEASURED. With an inferred builder only the runner seat's (DISPATCHER) isolated runs, from another
# session, can show independence.
MS = "session_01Maker"
_mk = lambda sha: MS
EVD = tempfile.mkdtemp()                 # a fresh store: AC1/AC5 above left damaged lines that taint every claim
os.environ[ce.ENV_DIR] = EVD


def dispatch_run(sha, session=None, seat="DISPATCHER"):
    return put(sha, "PASS", ["src/m/selftest_mod.py"], seat=seat, loads=["src/m/mod.py"], session=session)


i, s6, e6 = claim6(builder=None)
dispatch_run(s6)
r6 = run6(i, e6, session_of=_mk)
ok("INF close seat is the only source: builder BENCH, a DISPATCHER isolated run is independent",
   (g6(r6)[1], (r6["gate_evidence"].get("G6_builder_inferred") or {}).get("seat")), ("PASS", "BENCH"))
ok("INF nothing is left unmeasured: the claim is ranked, not sent to AI as T2_UNMEASURED",
   (r6["tier"] != "T2_UNMEASURED", r6["unmeasured"]), (True, []))
i, s6, e6 = claim6(builder=None)
dispatch_run(s6)
ok("INF close seat and commit session agree: PASS",
   g6(run6(i, e6, session_of=_mk, session_seats={MS: {"BENCH"}}))[1], "PASS")
i, s6, e6 = claim6(builder=None)
dispatch_run(s6)
r6 = run6(i, e6, session_of=_mk, session_seats={MS: {"FOUNDRY"}})
ok("INF close seat BENCH but the commit's session ran as FOUNDRY: UNMEASURED", g6(r6)[1], "UNMEASURED")
ok("INF disagreement goes to AI review", r6["tier"], "T2_UNMEASURED")
i, s6, e6 = claim6(builder=None)
dispatch_run(s6)
ok("INF the commit's session ran as two seats: UNMEASURED",
   g6(run6(i, e6, session_of=_mk, session_seats={MS: {"BENCH", "FOUNDRY"}}))[1], "UNMEASURED")
i, s6, e6 = claim6(close_seat="OWNER", builder=None)
dispatch_run(s6)
ok("INF OWNER close and no session record: no source, UNMEASURED", g6(run6(i, e6, session_of=_mk))[1], "UNMEASURED")
i, s6, e6 = claim6(close_seat="OWNER", builder=None)
dispatch_run(s6)
ok("INF OWNER close, commit session ran as BENCH: builder BENCH, DISPATCHER run PASS",
   g6(run6(i, e6, session_of=_mk, session_seats={MS: {"BENCH"}}))[1], "PASS")
i, s6, e6 = claim6(builder=None)
dispatch_run(s6, seat="FOUNDRY")
ok("INF a FOUNDRY run never shows independence of an inferred builder (only the runner seat can)",
   g6(run6(i, e6, session_of=_mk))[1] == "PASS", False)
i, s6, e6 = claim6(builder=None)
dispatch_run(s6, seat="BENCH")
ok("INF the inferred builder's own run is not independent", g6(run6(i, e6, session_of=_mk))[1] == "PASS", False)
i, s6, e6 = claim6(builder=None)
dispatch_run(s6, session=MS)
ok("INF a DISPATCHER run inside the commit's session is not independent",
   g6(run6(i, e6, session_of=_mk))[1] == "PASS", False)
i, s6, e6 = claim6(builder=None)
dispatch_run(s6)
ok("INF a commit with no Claude-Session trailer: UNMEASURED", g6(run6(i, e6))[1], "UNMEASURED")
i, s6, e6 = claim6(builder=None)
dispatch_run(s6)
ok("INF an unreadable commit session: UNMEASURED",
   g6(run6(i, e6, session_of=lambda sha: at.SESSION_UNREADABLE))[1], "UNMEASURED")
i, s6, e6 = claim6(close_seat="DISPATCHER", builder=None)
dispatch_run(s6)
ok("INF a DISPATCHER close: the runner is the builder, never independent",
   g6(run6(i, e6, session_of=_mk))[1] == "PASS", False)
i, s6, e6 = claim6(builder="DISPATCHER")
dispatch_run(s6)
ok("INF the ledger builder still rules: a DISPATCHER claim's DISPATCHER run FAILs",
   g6(run6(i, e6, session_of=_mk))[1], "FAIL")

# session_seat_map: only mac-verified, whoami-sure, SHARED-tree lines say which seat a session ran as (an isolated
# DISPATCHER run inside a seat's session is the runner, not the session's seat).
_sx = "%040x" % 0x5e55
_a = put(_sx, "PASS", ["src/m"], seat="BENCH", session="session_01Map", shared=True)
_b = put(_sx, "PASS", ["src/m"], seat="DISPATCHER", session="session_01Map")
_c = put(_sx, "PASS", ["src/m"], seat="FOUNDRY", session="session_01Map", shared=True)
_d = put(_sx, "PASS", ["src/m"], seat="CHECK", session="session_01Other", shared=True)
_key = ce._key()
ok("SMAP shared-tree runs map a session to its seats; isolated runs do not",
   at.session_seat_map([_a, _b, _d], _key), {"session_01Map": {"BENCH"}, "session_01Other": {"CHECK"}})
ok("SMAP a line with a bad mac is ignored", at.session_seat_map([dict(_c, mac="0" * 64)], _key), {})
ok("SMAP a seat its writer only asserted is ignored",
   at.session_seat_map([ce.seal(dict(_c, origin=dict(_c["origin"], who="caller")), _key)], _key), {})

# CODE_REVIEW_WIRE_REVIEWER_SEAT: G5 independence reads the REVIEWER, not the shard's (recording) seat.
import review_identity as RI                                     # noqa: E402
rv2 = tempfile.mkdtemp()
os.environ[RI.RECEIPTS_ENV] = os.path.join(rv2, "receipts.jsonl")
RI.write_receipt("consult-9", "m", True, [("p.py", b"x")])
_hx = RI.sha256_bytes(b"x")
_who = {"seat": "FOUNDRY", "seat_from": "RIMFLOW_SEAT", "bridge_session": "session_01R"}
with open(os.path.join(rv2, "A.jsonl"), "w") as f:
    for path, rvw, rec in (("p.py", {"kind": "self"}, _who),
                           ("s.py", {"kind": "external", "tool": "gpt_consult", "job": "consult-9", "model": "m"}, _who)):
        d = {"path": path, "sha256": _hx, "verdict": "clean", "ts": "2026-10-26T01:00:00Z", "seat": "BENCH"}
        d.update(RI.review_block(path, _hx, rvw, recorder=rec, key=_key))
        f.write(json.dumps(d) + "\n")
lc2 = at.load_clean_hashes(os.path.join(rv2, "*.jsonl"), key=_key)
ok("REV a verified self review names the recorder's seat and session, not the shard seat", lc2.get(("p.py", _hx)),
   {("self", "FOUNDRY", "session_01R")})
ok("REV a gpt_consult review whose receipt inlined other bytes is only asserted", lc2.get(("s.py", _hx)),
   {("asserted", "gpt_consult:consult-9", None)})
ok("REV with no key every record is reviewer-unknown",
   at.load_clean_hashes(os.path.join(rv2, "*.jsonl"), key=None).get(("p.py", _hx)), {("unknown", "BENCH", None)})


def rcso(clean_ids, builder="BENCH", session=None):
    f = [ev("verify", "REVX", "2026-10-26T11:00:00Z", seat="RUNNER", result="pass"),
         ev("close", "REVX", "2026-10-26T12:00:00Z", seat="BENCH", sha="good", reason="verified")]
    r = tiers_of(f, builder=builder, clean={("src/a.py", "H_src/a.py"): clean_ids},
                 session_of=lambda sha: session)[0]["REVX"]
    return "review_by_closing_seat_only" in r["flags"]


ok("REV an old record (reviewer unknown) by another seat never counts as independent",
   rcso({("unknown", "FOUNDRY", None)}), True)
ok("REV a self review by a non-maker seat from another session is independent",
   rcso({("self", "FOUNDRY", "session_01R")}, session=MS), False)
ok("REV a self review by the maker's seat is a self-review", rcso({("self", "BENCH", "session_01R")}), True)
ok("REV a non-maker seat inside the commit's session is the maker's session: not independent",
   rcso({("self", "FOUNDRY", MS)}, session=MS), True)
ok("REV an unreadable commit session: no seat review is independent",
   rcso({("self", "FOUNDRY", "session_01R")}, session=at.SESSION_UNREADABLE), True)
ok("REV an asserted reviewer never counts", rcso({("asserted", "CHECK", "session_01C")}), True)
ok("REV a receipt-verified external review is independent", rcso({("external", "gpt_consult:consult-9", None)}),
   False)
ok("REV no builder in the ledger: a seat review is not independent", rcso({("self", "FOUNDRY", None)}, builder=None),
   True)
ok("REV no builder in the ledger: an external review still is", rcso({("external", "gpt_consult:j", None)},
                                                                     builder=None), False)
ok("REV the reviewers are listed", tiers_of(f6, clean={("src/a.py", "H_src/a.py"): {("self", "CHECK", None)}})[0][
    "MAKERREV"]["gate_evidence"].get("G5_reviewers"), [["self", "CHECK", None]])

print("\n%s" % ("ALL PASS" if not FAILED else "FAILED: %s" % FAILED))
sys.exit(1 if FAILED else 0)
