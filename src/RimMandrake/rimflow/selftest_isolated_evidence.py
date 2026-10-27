"""selftest_isolated_evidence.py - python3 src/RimMandrake/rimflow/selftest_isolated_evidence.py

The Arbiter's independent pre-step (isolated_evidence.py) on a throwaway git repo: claim selection, the test plan,
dry run writes nothing, --run records isolated close_evidence under the runner seat that arbiter_tiers counts as
independent, the checkout is deleted, the journal skips a repeat, a maker seat is refused, a failing test is FAIL.
The live evidence store, key and journal are never touched (all pointed into temp dirs)."""
import io, json, os, subprocess, sys, tempfile, contextlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

T = tempfile.mkdtemp(prefix="st_isoev_")
os.environ["RM_CLOSE_EVIDENCE_DIR"] = os.path.join(T, "evidence")
os.environ["RM_CLOSE_EVIDENCE_KEY"] = os.path.join(T, "key", "close_evidence.key")
os.environ["RM_ISOLATED_JOURNAL"] = os.path.join(T, "journal.jsonl")
os.environ["RM_ISOLATED_DEFS_ROOTS"] = ""
os.environ["RM_ISOLATED_CARRIED"] = os.path.join(T, "carried.json")         # never the live carried list
os.environ["RM_ARBITER_CUTOFF"] = os.path.join(T, "arbiter", "cutoff.json")  # never the live stamp
for k in ("RIMFLOW_SEAT", "AGENT_SEAT", "RIMFLOW_ITEM"):
    os.environ.pop(k, None)
from rimflow import isolated_evidence as ie        # noqa: E402
from rimflow import arbiter_tiers as at            # noqa: E402
ce = ie.ce
ce._key(create=True)
ROOT = os.path.join(T, "iso")
FAILED = []


def ok(name, got, want):
    if got == want:
        print("ok    %s" % name)
    else:
        FAILED.append(name)
        print("FAIL  %s\n      got  %r\n      want %r" % (name, got, want))


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout.strip()


def put(rel, text):
    p = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


PASS_T = "import sys\nprint('ok')\nsys.exit(0)\n"
FAIL_T = "import sys\nprint('FAIL planted')\nsys.exit(1)\n"
REPO = os.path.join(T, "repo")
os.makedirs(REPO)
subprocess.run(["git", "init", "-q", REPO], check=True)
git("config", "user.email", "t@t"); git("config", "user.name", "t")
put("src/A/foo.py", "X = 1\n")
put("src/A/selftest_foo.py", PASS_T)
put("src/B/selftest_cited.py", PASS_T)
put("src/C/selftest_dup.py", PASS_T)
put("src/D/selftest_dup.py", PASS_T)
put("src/E/selftest_unrelated.py", FAIL_T)
git("add", "-A"); git("commit", "-qm", "base")
put("src/A/foo.py", "X = 2\n")                                # touched source: sibling selftest_foo.py runs
git("add", "-A"); git("commit", "-qm", "c1")
SHA1 = git("rev-parse", "HEAD")
put("src/B/selftest_cited.py", PASS_T + "# v2\n")            # only a selftest touched: full coverage possible
git("add", "-A"); git("commit", "-qm", "c2")
SHA2 = git("rev-parse", "HEAD")
put("src/E/selftest_unrelated.py", FAIL_T + "# v2\n")
git("add", "-A"); git("commit", "-qm", "c3")
SHA3 = git("rev-parse", "HEAD")


def ev(e, i, ts, seat="BENCH", **k):
    d = {"event": e, "id": i, "ts": ts, "seat": seat}
    d.update(k)
    return d


EVENTS = [
    ev("claim", "IT_ONE", "2026-10-27T10:00:00Z"),
    ev("close", "IT_ONE", "2026-10-27T10:05:00Z", sha="HEAD", reason="first try"),
    ev("close", "IT_ONE", "2026-10-27T10:10:00Z", sha=SHA1[:12],
       reason="see src/B/selftest_cited.py and selftest_dup.py and selftest_nosuch.py"),
    ev("claim", "IT_TWO", "2026-10-27T11:00:00Z"),
    ev("close", "IT_TWO", "2026-10-27T11:05:00Z", sha=SHA2[:10], reason="green"),
    ev("claim", "IT_FAIL", "2026-10-27T11:00:00Z"),
    ev("close", "IT_FAIL", "2026-10-27T11:06:00Z", sha=SHA3, reason="green"),
    ev("claim", "IT_OLD", "2026-10-01T11:00:00Z"),
    ev("close", "IT_OLD", "2026-10-01T11:05:00Z", sha=SHA2, reason="old"),
    ev("claim", "IT_GHOST", "2026-10-27T11:00:00Z"),
    ev("close", "IT_GHOST", "2026-10-27T11:07:00Z", sha="deadbeefdead", reason="x"),
    ev("claim", "IT_RUNNER", "2026-10-27T11:00:00Z", seat="RUNNER"),
    ev("close", "IT_RUNNER", "2026-10-27T11:08:00Z", sha=SHA2, reason="x", seat="RUNNER"),
]
NOW = "2026-10-27T12:00:00Z"

# ---- claim selection
cl = ie.done_claims(EVENTS, ie._epoch(NOW) - 86400 * 2)
ok("claims: latest close with a sha per item, window applied", [c["item"] for c in cl],
   ["IT_ONE", "IT_TWO", "IT_FAIL", "IT_GHOST", "IT_RUNNER"])
ok("claims: the latest close wins (not the HEAD one)", cl[0]["sha"], SHA1[:12])

# ---- plan
p1 = ie.plan_claim(cl[0], [REPO], roots=[])
ok("plan: abbreviated sha resolves to full", p1["full"], SHA1)
ok("plan: sibling of touched foo.py + cited path; ambiguous bare name not guessed", p1["selftests"],
   ["src/A/selftest_foo.py", "src/B/selftest_cited.py"])
ok("plan: ambiguous name reported", any("selftest_dup.py" in n for n in p1["notes"]), True)
ok("plan: uncovered source path noted (a sibling selftest that never imports foo.py does not cover it)",
   (any("no selftest here is predicted to load" in n for n in p1["notes"]), p1["uncovered"], p1["predicted"]),
   (True, ["src/A/foo.py"], []))
put("src/G/bar.py", "Y = 1\n"); put("src/G/selftest_bar.py", "import bar\n" + PASS_T)
put("src/G/baz.py", "Z = 1\n")
git("add", "-A"); git("commit", "-qm", "bar")
put("src/G/bar.py", "Y = 2\n"); put("src/G/baz.py", "Z = 2\n")
git("add", "-A"); git("commit", "-qm", "bar2")
pb = ie.plan_claim({"item": "IT_BAR", "sha": git("rev-parse", "HEAD"), "close": {"ts": "z"}, "events": []},
                   [REPO], roots=[])
ok("plan: a selftest that imports the touched module is predicted to cover it; an unimported neighbour is not",
   (pb["selftests"], pb["predicted"], pb["uncovered"]), (["src/G/selftest_bar.py"], ["src/G/bar.py"], ["src/G/baz.py"]))
ok("plan: unresolvable sha is skipped", bool(ie.plan_claim(cl[3], [REPO], roots=[])["skip"]), True)
put("src/Mod/Defs/x.xml", "<Defs/>\n"); put("src/Mod/Source/y.cs", "class Y{}\n")
git("add", "-A"); git("commit", "-qm", "xml")
SHA4 = git("rev-parse", "HEAD")
p4 = ie.plan_claim({"item": "IT_XML", "sha": SHA4, "close": {"ts": "z"}, "events": []}, [REPO], roots=[])
ok("plan: xml with no defs root is owed, not run statically; C# owed", (p4["validate"], len(p4["owed"]), bool(p4["skip"])),
   ([], 2, True))
p4b = ie.plan_claim({"item": "IT_XML", "sha": SHA4, "close": {"ts": "z"}, "events": []}, [REPO], roots=[T])
ok("plan: xml under Defs/ validated when a defs root exists", (p4b["validate"], p4b["defs"]),
   (["src/Mod/Defs/x.xml"], [T]))


def main(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ie.main(["--now", NOW, "--root", ROOT] + list(args), events=EVENTS, repos=[REPO])
    return rc, buf.getvalue()


def iso_dirs():
    return [d for d in os.listdir(ROOT) if d.startswith("ce_iso_")] if os.path.isdir(ROOT) else []


# ---- dry run
rc, out = main()
ok("dry run: exit 0", rc, 0)
ok("dry run: says dry run", "dry run: pass --run" in out, True)
ok("dry run: no journal, no checkout, no evidence", (os.path.exists(os.environ["RM_ISOLATED_JOURNAL"]), iso_dirs(),
   os.path.isdir(os.environ["RM_CLOSE_EVIDENCE_DIR"]) and bool(os.listdir(os.environ["RM_CLOSE_EVIDENCE_DIR"]))),
   (False, [], False))
ok("dry run: DISPATCHER may run the RUNNER-built claim", [l.split()[0] for l in out.splitlines() if "IT_RUNNER" in l],
   ["PLAN"])
ok("dry run: unresolvable sha skipped", [l.split()[0] for l in out.splitlines() if "IT_GHOST" in l], ["SKIP"])
rc, out = main("--seat", "RUNNER", "--item", "IT_RUNNER")
ok("maker seat refused (RUNNER built IT_RUNNER)", "would not be independent" in out, True)

# ---- run
rc, out = main("--run", "--item", "IT_TWO", "--item", "IT_FAIL")
ok("run: exit 0", rc, 0)
ok("run: checkouts deleted", iso_dirs(), [])
rows = [json.loads(l) for l in open(os.environ["RM_ISOLATED_JOURNAL"])]
ok("run: one journal row per claim", sorted(r["item"] for r in rows), ["IT_FAIL", "IT_TWO"])
two = [r for r in rows if r["item"] == "IT_TWO"][0]
ok("run: IT_TWO selftest PASS recorded as evidence, isolated, seat DISPATCHER",
   [(r["tool"], r["result"], r["evidence"], r["tree"], r["seat"]) for r in two["records"]],
   [("selftest", "PASS", True, "isolated", "DISPATCHER")])
fl = [r for r in rows if r["item"] == "IT_FAIL"][0]
ok("run: a failing test records FAIL", [(r["tool"], r["result"]) for r in fl["records"]], [("selftest", "FAIL")])

# ---- the Arbiter counts it: G6 PASS and independent for the builder BENCH
evid = at.lookup_close_evidence(SHA2, "IT_TWO", ["src/B/selftest_cited.py"])
tw = [e for e in EVENTS if e["id"] == "IT_TWO"]
g, gev = at.gates(tw, tw[-1], {"src/B/selftest_cited.py": "M"}, {}, evidence=evid)
ok("arbiter: G6 PASS and G6_independent PASS from the pre-step's record",
   (g["G6_close_evidence"], g["G6_independent"]), ("PASS", "PASS"))
ok("arbiter: the record carries the item and RIMFLOW_SEAT provenance",
   [(r.get("item"), r["who"].get("seat_from")) for r in evid], [("IT_TWO", "RIMFLOW_SEAT")])

# ---- repeat is skipped by the journal; --again re-runs
rc, out = main("--item", "IT_TWO")
ok("journal: a repeat is skipped", "already run" in out, True)
rc, out = main("--item", "IT_TWO", "--again")
ok("journal: --again plans it again", "already run" not in out and "PLAN" in out, True)

# ---- the lock refuses a second concurrent run
with ie._lock(ROOT):
    rc, out = main("--run", "--item", "IT_TWO", "--again")
ok("lock: a second run is UNMEASURED (exit 2)", rc, 2)

# ---- unreadable ledger
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    rc = ie.main(["--now", NOW, "--root", ROOT], events=[], repos=[REPO])
ok("no ledger: exit 2 UNMEASURED", (rc, "UNMEASURED" in buf.getvalue()), (2, True))

# ---- ARBITER_MEASURE_PRELAUNCH_EVIDENCE_TIME / ARBITER_DECIDE_BACKLOG_NEVER_DRAINS: --since-cutoff, budget, carry
rc, out = main("--since-cutoff")
ok("cutoff: no stamp -> exit 2, nothing planned", (rc, "PLAN" in out), (2, False))
from rimflow import arbiter_pending as PW  # noqa: E402
PW.stamp(os.environ["RM_ARBITER_CUTOFF"], "2026-10-27T11:05:30Z", by="SELFTEST", why="test")
rc, out = main("--since-cutoff", "--json")
ok("cutoff: only closes at/after the stamp, oldest first (no day window)",
   (rc, [p["item"] for p in json.loads(out)["plans"]]), (0, ["IT_FAIL", "IT_GHOST", "IT_RUNNER"]))

clock, calls = [0.0], []


def fake_run(p, seat, root, timeout=None, **kw):
    calls.append((p["item"], timeout))
    clock[0] += 100
    return {"item": p["item"], "sha": p["full"], "key": ie.plan_key(p), "seat": seat, "runs": [], "records": [],
            "total_s": 100, "ts": "2026-10-27T12:00:00Z"}


real_run, real_clock = ie.run_claim, ie.CLOCK
ie.run_claim, ie.CLOCK = fake_run, (lambda: clock[0])
try:
    n0 = sum(1 for _ in open(os.environ["RM_ISOLATED_JOURNAL"]))
    rc, out = main("--run", "--again", "--budget-s", "250", "--claim-reserve-s", "100")
    car = json.load(open(os.environ["RM_ISOLATED_CARRIED"]))
    ok("budget: claims start oldest first while elapsed + reserve <= budget, each tool bounded by what is left",
       (rc, calls), (0, [("IT_ONE", 250), ("IT_TWO", 150)]))
    ok("budget: the rest are CARRIED (carried.json, oldest first), not journaled",
       ([c["item"] for c in car["carried"]], sum(1 for _ in open(os.environ["RM_ISOLATED_JOURNAL"])) - n0),
       (["IT_FAIL", "IT_RUNNER"], 2))
    ok("budget: carried rows carry the full sha and the budget", (car["carried"][0]["sha"], car["budget_s"]),
       (SHA3, 250))
    ok("budget: the run says what it carried", "CARRIED" in out and "IT_FAIL" in out, True)
    del calls[:]
    rc, out = main("--run", "--again", "--budget-s", "50", "--claim-reserve-s", "180")
    ok("budget: the oldest claim always runs (never starves behind its own reserve)",
       ([c[0] for c in calls], len(json.load(open(os.environ["RM_ISOLATED_CARRIED"]))["carried"])), (["IT_ONE"], 3))
    del calls[:]
    rc, out = main("--run", "--again")
    ok("budget: none -> every claim runs, carried.json rewritten empty (never stale); no budget = no claim deadline, RUN_TIMEOUT per tool",
       (len(calls), json.load(open(os.environ["RM_ISOLATED_CARRIED"]))["carried"], calls[0][1]),
       (4, [], None))
finally:
    ie.run_claim, ie.CLOCK = real_run, real_clock

import shutil  # noqa: E402
shutil.rmtree(T, ignore_errors=True)
print("ALL PASS" if not FAILED else "FAILED: %s" % ", ".join(FAILED))
sys.exit(1 if FAILED else 0)
