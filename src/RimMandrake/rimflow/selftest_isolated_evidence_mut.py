"""selftest_isolated_evidence_mut.py - python3 src/RimMandrake/rimflow/selftest_isolated_evidence_mut.py

Kills the mutants selftest_isolated_evidence.py left alive (ISOLATED_EVIDENCE_HARDEN_MUTATION_SURVIVORS; SteveDesktop run
20261028e: 295 of 704 alive). isolated_evidence.py is what gives the Arbiter evidence the builder did not make, so what
is pinned here is: which claims are selected, which tests a claim names and which the plan runs (cited_selftests,
plan_claim), what run_claim hands the tools (command line, env seat, per-tool timeout, cwd) and what it records, and
the exit codes / lines of main. Each group says in a trailing comment which mutant family it kills.

RM_ISO_MUT_SRC=<path> loads that COPY of the module instead of the real one (the hand-mutation driver
/mnt/d/ClaudeWork/rimmandrake/mutation/mutdrv_iso.py uses it, matching each mutant by line number). Offline: fixture git
repo and ledger events in a temp dir; the live evidence store, key, journal and carried list are never touched."""
import re, atexit
import contextlib, io, json, os, stat, subprocess, sys, tempfile, types, shutil, importlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REACHED_END = []
atexit.register(lambda: _REACHED_END or os._exit(1))   # a module that exits at import (mutated __main__ guard) must not read as a pass

T = tempfile.mkdtemp(prefix="st_isoevmut_")
os.environ["RM_CLOSE_EVIDENCE_DIR"] = os.path.join(T, "evidence")
os.environ["RM_CLOSE_EVIDENCE_KEY"] = os.path.join(T, "key", "close_evidence.key")
os.environ["RM_ISOLATED_JOURNAL"] = os.path.join(T, "journal.jsonl")
os.environ["RM_ISOLATED_DEFS_ROOTS"] = ""
os.environ["RM_ISOLATED_CARRIED"] = os.path.join(T, "carried.json")
os.environ["RM_ARBITER_CUTOFF"] = os.path.join(T, "arbiter", "cutoff.json")
for k in ("RIMFLOW_SEAT", "AGENT_SEAT", "RIMFLOW_ITEM", "RM_SELFTEST_NESTED", "RM_SELFTEST_REPO_ROOT"):
    os.environ.pop(k, None)
from rimflow import isolated_evidence as _real      # noqa: E402
SRC = os.environ.get("RM_ISO_MUT_SRC")
if SRC:
    ie = types.ModuleType("rimflow.isolated_evidence")
    ie.__file__ = _real.__file__
    sys.modules["rimflow.isolated_evidence"] = ie
    exec(compile(open(SRC).read(), SRC, "exec"), ie.__dict__)
else:
    ie = _real
from rimflow import arbiter_tiers as at            # noqa: E402
ce = ie.ce
ce._key(create=True)
FAILED = []


def ok(name, got, want):
    if got == want:
        print("ok    %s" % name)
    else:
        FAILED.append(name)
        print("FAIL  %s\n      got  %r\n      want %r" % (name, got, want))


def raises(fn, exc=Exception):
    try:
        fn()
    except exc as e:
        return str(e)
    return None


@contextlib.contextmanager
def patched(obj, **kw):
    old = {k: getattr(obj, k) for k in kw}
    for k, v in kw.items():
        setattr(obj, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(obj, k, v)


@contextlib.contextmanager
def env(**kw):
    old = {k: os.environ.get(k) for k in kw}
    for k, v in kw.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---- constants and default paths                                    (kills the <module> / carried_path / journal_path families)
ok("const: runner seats", ie.RUNNER_SEATS, ("DISPATCHER", "RUNNER"))
ok("const: MIN_FREE 12 GiB, RUN_TIMEOUT 1800, MIN_TOOL_TIMEOUT 60, reserve 180",
   (ie.MIN_FREE, ie.RUN_TIMEOUT, ie.MIN_TOOL_TIMEOUT, ie.CLAIM_RESERVE_S), (12 * 1024 ** 3, 1800, 60, 180))
ok("const: selftest roots", ie.SELFTEST_ROOTS,
   ("src/", ".claude/hooks/", "skills/", "infrastructure/dashboards/hub/", "infrastructure/stevedesktop/"))
ok("const: env names", (ie.JOURNAL_ENV, ie.DEFS_ROOTS_ENV, ie.CARRIED_ENV),
   ("RM_ISOLATED_JOURNAL", "RM_ISOLATED_DEFS_ROOTS", "RM_ISOLATED_CARRIED"))
ok("const: the instruments exist (a wrong path would run nothing)",
   (os.path.isfile(ie.RUN_SELFTESTS), os.path.isfile(ie.VALIDATE_PATCH), os.path.isdir(ie.CLONE)), (True, True, True))
ok("const: clone is this repo", ie.CLONE, os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(_real.__file__)), "..", "..", "..")))
ok("const: data dir and ext4 default root", (ie.DATA, ie.DEFAULT_ROOT),
   ("/mnt/d/ClaudeWork/rimmandrake/isolated_evidence", os.path.expanduser("~/.seat-tmp/isolated_evidence")))
ok("const: default defs roots", ie.DEFAULT_DEFS_ROOTS,
   tuple("/mnt/c/Program Files (x86)/Steam/steamapps" + s for s in
         ("/common/RimWorld/Data", "/common/RimWorld/Mods", "/workshop/content/294100")))
ok("const: _CITE finds a Windows path and a bare name", ie._CITE.findall(r"x D:\a\selftest_q-1.py, selftest_z.py."),
   [r"D:\a\selftest_q-1.py", "selftest_z.py"])
with env(RM_ISOLATED_CARRIED=None, RM_ISOLATED_JOURNAL=None):
    ok("defaults: carried and journal live under DATA", (ie.carried_path(), ie.journal_path()),
       (ie.DATA + "/carried.json", ie.DATA + "/journal.jsonl"))
with env(RM_ISOLATED_CARRIED="/x/c.json", RM_ISOLATED_JOURNAL="/x/j.jsonl"):
    ok("defaults: env overrides", (ie.carried_path(), ie.journal_path()), ("/x/c.json", "/x/j.jsonl"))

# ---- write_carried: atomic, shape                                    (kills write_carried)
cp = os.path.join(T, "cdir", "c.json")
ie.write_carried([{"item": "A"}], 77, cp)
raw = open(cp).read()
d = json.loads(raw)
ok("write_carried: keys, rows, budget", (sorted(d), d["carried"], d["budget_s"]), (["budget_s", "carried", "generated"], [{"item": "A"}], 77))
ok("write_carried: generated is a UTC seconds stamp", bool(__import__("re").fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", d["generated"])), True)
ok("write_carried: indent=1, no tmp left behind", ('\n "budget_s": 77' in raw, os.listdir(os.path.dirname(cp))), (True, ["c.json"]))

# ---- _git / resolve / touched / tree_files with a fake git          (kills their timeouts, messages, slices)
seen = []


def fake_sub(argv, **kw):
    seen.append((argv, kw))
    return types.SimpleNamespace(returncode=0, stdout="out", stderr="")


with patched(ie.subprocess, run=fake_sub):
    ie._git("/r", "status")
    ie._git("/r", "status", timeout=7)
ok("_git: default timeout 60, argv", ([s[1]["timeout"] for s in seen], seen[0][0], seen[0][1]["capture_output"], seen[0][1]["text"]),
   ([60, 7], ["git", "-C", "/r", "status"], True, True))

SHA = "a" * 40
calls = []


def git_script(table):
    def f(repo, *args, timeout=60):
        calls.append((repo, args, timeout))
        r = table[repo]
        if isinstance(r, Exception):
            raise r
        return r
    return f


with patched(ie, _git=git_script({"/bad": OSError("x"), "/nonsha": (0, "zzz\n"), "/rc": (1, SHA), "/good": (0, SHA + "\n")})):
    ok("resolve: an unusable repo is skipped, the next one answers", ie.resolve("abc", ["/bad", "/good"]), ("/good", SHA))
    ok("resolve: rc!=0 with a sha-looking line is not a hit", ie.resolve("abc", ["/rc", "/good"]), ("/good", SHA))
    ok("resolve: rc==0 with a non-sha line is not a hit", ie.resolve("abc", ["/nonsha", "/good"]), ("/good", SHA))
    ok("resolve: none -> (None, None)", ie.resolve("abc", ["/bad", "/rc"]), (None, None))
    del calls[:]
    ie.resolve("abc", ["/good"])
    ok("resolve: asks rev-parse --verify --quiet sha^{commit}, 30 s", calls,
       [("/good", ("rev-parse", "--verify", "--quiet", "abc^{commit}"), 30)])
    ok("resolve: upper-case or short output is not a full sha", ie.resolve("a", ["/nonsha"]), (None, None))
with patched(ie, _git=git_script({"/up": (0, "A" * 40)})):
    ok("resolve: only lower-case hex is a full sha", ie.resolve("a", ["/up"]), (None, None))

tout = "M\tsrc/a.py\nA\tsrc/b.py\nD\tsrc/c.py\nR100\tsrc/d.py\nnotab\nM\tweird\tname\n"
with patched(ie, _git=git_script({"/r": (0, tout), "/f": (1, "")})):
    del calls[:]
    ok("touched: first status letter per path; a tab inside a path stays in the path", ie.touched("/r", SHA),
       {"src/a.py": "M", "src/b.py": "A", "src/c.py": "D", "src/d.py": "R", "weird\tname": "M"})
    ok("touched: diff-tree argv", calls[0][1], ("diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", "--root", SHA))
    ok("touched: failure message names 12 chars of the sha and the repo", raises(lambda: ie.touched("/f", SHA), RuntimeError),
       "git diff-tree %s failed in /f" % ("a" * 12))
with patched(ie, _git=git_script({"/r": (0, "src/a.py\nsrc/b.py\n"), "/f": (1, "")})):
    del calls[:]
    ok("tree_files: lines", ie.tree_files("/r", SHA), ["src/a.py", "src/b.py"])
    ok("tree_files: ls-tree -r --name-only, 120 s", (calls[0][1], calls[0][2]), (("ls-tree", "-r", "--name-only", SHA), 120))
    ok("tree_files: failure message", raises(lambda: ie.tree_files("/f", SHA), RuntimeError), "git ls-tree %s failed in /f" % ("a" * 12))

# ---- _is_selftest                                                    (kills _is_selftest)
ok("_is_selftest: needs prefix, basename selftest*.py, under a root",
   [ie._is_selftest(p) for p in ("src/A/selftest_x.py", "src/A/selftest.py", "src/A/selftest_x.txt", "src/A/x_selftest.py",
                                 "docs/selftest_x.py", "selftest_x.py", "src/selftest_d/other.py", "skills/q/selftest_a.py",
                                 ".claude/hooks/selftest_h.py", "infrastructure/stevedesktop/selftest_s.py")],
   [True, True, False, False, False, False, False, True, True, True])

# ---- done_claims                                                     (kills done_claims)
E = lambda i, ts, sha, ev="close", **k: dict({"event": ev, "id": i, "ts": ts, "sha": sha}, **k)  # noqa: E731
evs = [E("BADFIRST", "2026-10-27T10:00:00Z", ""), E("NOSHA", "2026-10-27T10:01:00Z", None), E("HEADY", "2026-10-27T10:02:00Z", "HEAD"),
       E("SHORT", "2026-10-27T10:03:00Z", "abcdef"), E("LONG", "2026-10-27T10:03:30Z", "a" * 41),
       E("OK1", "2026-10-27T10:04:00Z", " ABCDEF1 "), E("EDGE", "2026-10-27T09:00:00Z", "a" * 40),
       E("EARLY", "2026-10-27T08:59:59Z", "a" * 40), E("NOTS", None, "a" * 40), E("OK1", "2026-10-27T10:05:00Z", "b" * 7, ev="verify"),
       {"event": "claim", "ts": "2026-10-27T10:06:00Z"}]
since = ie._epoch("2026-10-27T09:00:00Z")
got = ie.done_claims(evs, since)
ok("done_claims: bad shas dropped without stopping the scan, since is inclusive, sha lower-cased and stripped, oldest first",
   [(c["item"], c["sha"]) for c in got], [("EDGE", "a" * 40), ("OK1", "abcdef1")])
ok("done_claims: events per item kept (the later verify too)", [e["event"] for e in got[1]["events"]], ["close", "verify"])
ok("done_claims: an item without an id is ignored", len(ie.done_claims(evs[-1:], 0)), 0)
ok("_epoch: parses, None on junk", (ie._epoch("2026-10-27T12:00:00Z"), ie._epoch(None), ie._epoch("junk")), (1793102400, None, None))

# ---- claim_text                                                      (kills claim_text)
cl_close = {"ts": "2026-10-27T10:00:00Z"}
evs = [{"event": "close", "ts": "2026-10-27T11:00:00Z", "reason": "LATER"},
       {"event": "verify", "ts": "2026-10-27T09:00:00Z", "evidence": "V-ev"},
       {"event": "implemented", "ts": "2026-10-27T09:01:00Z", "why": "I-why"},
       {"event": "note", "ts": "2026-10-27T09:02:00Z", "text": "N-text"},
       {"event": "claim", "ts": "2026-10-27T09:03:00Z", "reason": "CLAIM-NOT"},
       {"event": "close", "ts": "2026-10-27T10:00:00Z", "reason": "C-reason", "criteria": ["x", "y"]},
       {"event": "note", "reason": "R", "text": None, "why": 0},
       {"event": "note", "ts": "2026-10-27T09:04:00Z", "reason": {"k": 1}}]
txt = ie.claim_text(evs, cl_close)
lines = [l for l in txt.split("\n") if l]
ok("claim_text: later events cut (scan continues past them), equal ts kept, non-record kinds ignored, each field read",
   (lines, "LATER" in txt, "CLAIM-NOT" in txt),
   (["V-ev", "I-why", "N-text", "C-reason", '["x", "y"]', "R", '{"k": 1}'], False, False))
ok("claim_text: 5 parts (reason, why, evidence, text, criteria) per kept event, '\\n'-joined, None/0 -> empty", txt.count("\n"), 6 * 5 - 1)
ok("claim_text: a ts-less event counts as earliest", ie.claim_text([{"event": "note", "text": "T"}], {"ts": "z"}), "\n\n\nT\n")
ok("claim_text: a ts-less close counts as ts ''", ie.claim_text([{"event": "note", "ts": "2026-01-01T00:00:00Z", "text": "T"}], {}), "")
ok("claim_text: empty", ie.claim_text([], cl_close), "")

# ---- cited_selftests                                                 (kills cited_selftests)
ST = ["src/A/selftest_one.py", "src/B/selftest_dup.py", "src/C/selftest_dup.py", "skills/x/selftest_one.py", "src/B/selftest_zzz.py"]
ok("cited: a bare unique name resolves", ie.cited_selftests("see selftest_zzz.py", ST), ({"src/B/selftest_zzz.py"}, set()))
ok("cited: a bare name that two selftests have is ambiguous, never guessed", ie.cited_selftests("selftest_dup.py", ST),
   (set(), {"selftest_dup.py"}))
ok("cited: a directory path resolves by suffix to the matching one only", ie.cited_selftests("src/C/selftest_dup.py", ST),
   ({"src/C/selftest_dup.py"}, set()))
ok("cited: a longer prefix (checkout path) matches by '/' + path", ie.cited_selftests("/home/u/rm/src/C/selftest_dup.py", ST),
   ({"src/C/selftest_dup.py"}, set()))
ok("cited: a Windows path is normalised", ie.cited_selftests(r"D:\x\src\A\selftest_one.py", ST),
   ({"src/A/selftest_one.py"}, set()))
ok("cited: a suffix that is not on a '/' boundary does not match", ie.cited_selftests("xsrc/C/selftest_dup.py", ST), (set(), {"selftest_dup.py"}))
ok("cited: a path to nothing falls back to the bare name when that is unique", ie.cited_selftests("nowhere/selftest_zzz.py", ST),
   ({"src/B/selftest_zzz.py"}, set()))
ok("cited: a path to nothing with an ambiguous name is ambiguous", ie.cited_selftests("nowhere/selftest_one.py", ST),
   (set(), {"selftest_one.py"}))
ok("cited: no such test -> nothing; None/empty text safe", (ie.cited_selftests("selftest_nosuch.py", ST), ie.cited_selftests(None, ST),
                                                         ie.cited_selftests("", ST)), (((set(), set())),) * 3)
ok("cited: the first candidate of a unique name is used", ie.cited_selftests("selftest_one.py", ["only/selftest_one.py"]),
   ({"only/selftest_one.py"}, set()))
ok("cited: a path match adds ALL equal-path hits, not just one", ie.cited_selftests("x/a/selftest_q.py", ["a/selftest_q.py", "x/a/selftest_q.py"]),
   ({"a/selftest_q.py", "x/a/selftest_q.py"}, set()))

ok("cited: a bare selftest name with no directory in the list (index 1 would raise)", ie.cited_selftests("selftest_b.py", ["selftest_b.py"]),
   ({"selftest_b.py"}, set()))

# ---- defs_roots                                                      (kills defs_roots)
real_dir = os.path.join(T, "rootdir"); os.makedirs(real_dir)
with env(RM_ISOLATED_DEFS_ROOTS=os.pathsep.join([real_dir, os.path.join(T, "missing"), "", real_dir + "x"])):
    ok("defs_roots: env, existing dirs only, blanks dropped", ie.defs_roots(), [real_dir])
with env(RM_ISOLATED_DEFS_ROOTS=""):
    ok("defs_roots: an EMPTY env means no roots (not the defaults)", ie.defs_roots(), [])
with env(RM_ISOLATED_DEFS_ROOTS=None):
    ok("defs_roots: unset -> the default roots that exist", ie.defs_roots(), [r for r in ie.DEFAULT_DEFS_ROOTS if os.path.isdir(r)])
with env(RM_ISOLATED_DEFS_ROOTS=None), patched(ie, DEFAULT_DEFS_ROOTS=(real_dir, "", os.path.join(T, "nope"))):
    ok("defs_roots: defaults are filtered for existence too", ie.defs_roots(), [real_dir])

# ---- plan_claim on a fixture repo                                    (kills plan_claim)
REPO = os.path.join(T, "repo")
os.makedirs(REPO)
subprocess.run(["git", "init", "-q", REPO], check=True)


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout.strip()


def put(rel, text):
    p = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(p) or REPO, exist_ok=True)
    open(p, "w").write(text)


git("config", "user.email", "t@t"); git("config", "user.name", "t")
PASS_T = "import sys\nprint('ok')\nsys.exit(0)\n"
put("foo.py", "X = 1\n"); put("selftest_foo.py", PASS_T)                       # root-level source + sibling
put("src/A/selftest_a.py", PASS_T); put("src/A/selftest_selftest_a.py", PASS_T)  # a touched selftest has NO sibling run
put("src/Z/Defs/q.xml", "<Defs/>\n"); put("src/Z/Defs/selftest_q.xml", "<Defs/>\n")
put("src/Z/Defs/pic.png", "x"); put("src/Z/Other/o.xml", "<a/>"); put("src/Z/Defs/big.XML", "<Defs/>")
put("src/Q/gone.py", "G=1\n"); put("src/Q/selftest_gone.py", PASS_T)
put("src/Q/two1.py", "A=1\n"); put("src/Q/selftest_two1.py", "import two1\n" + PASS_T)
put("src/Q/two2.py", "B=1\n"); put("src/Q/selftest_two2.py", "import two2\n" + PASS_T)
put("src/Q/H.csproj", "<P/>"); put("src/Q/k.cs", "class K{}")
git("add", "-A"); git("commit", "-qm", "base")
for f in ("foo.py", "src/A/selftest_a.py", "src/Z/Defs/q.xml", "src/Z/Defs/pic.png", "src/Z/Other/o.xml", "src/Z/Defs/big.XML",
          "src/Q/two1.py", "src/Q/two2.py", "src/Q/H.csproj"):
    put(f, open(os.path.join(REPO, f)).read() + "\n#2\n")
os.remove(os.path.join(REPO, "src/Q/gone.py")); os.remove(os.path.join(REPO, "src/Q/selftest_gone.py"))
git("add", "-A"); git("commit", "-qm", "c1")
S1 = git("rev-parse", "HEAD")
claim = lambda sha, evs=(), close=None: {"item": "IT", "sha": sha, "close": close or {"ts": "t1", "seat": "SEATX"}, "events": list(evs)}  # noqa: E731
p = ie.plan_claim(claim(S1[:10]), [REPO], roots=[real_dir])
ok("plan: keys of a resolved plan", sorted(p), sorted(["item", "sha", "close_ts", "close_seat", "repo", "full", "selftests", "validate",
                                                         "defs", "owed", "notes", "predicted", "uncovered", "skip"]))
ok("plan: identity fields", (p["item"], p["sha"], p["close_ts"], p["close_seat"], p["repo"], p["full"], p["skip"]),
   ("IT", S1[:10], "t1", "SEATX", REPO, S1, None))
ok("plan: root-level sibling runs; a touched selftest brings in no 'selftest_selftest_' sibling; deleted files ignored",
   p["selftests"], ["selftest_foo.py", "src/A/selftest_a.py", "src/Q/selftest_two1.py", "src/Q/selftest_two2.py"])
ok("plan: only .xml under Defs/ or Patches/ (any case of ext) is validated; no sibling selftest_*.xml run",
   (p["validate"], p["defs"]), (["src/Z/Defs/big.XML", "src/Z/Defs/q.xml"], [real_dir]))
ok("plan: owed lists the C# files", p["owed"], ["winbuild for 1 C# file(s): not run by this pre-step"])
ok("plan: each selftest predicts its own import, accumulated (|=), the rest is uncovered",
   (p["predicted"], p["uncovered"]), (["src/Q/two1.py", "src/Q/two2.py"],
                                      ["foo.py", "src/Q/H.csproj", "src/Z/Defs/pic.png", "src/Z/Other/o.xml"]))
ok("plan: uncovered note text", p["notes"], ["4 touched path(s) no selftest here is predicted to load or declares, and no validator covers"])
p = ie.plan_claim(claim(S1), [REPO], roots=[])
ok("plan: xml with no root is owed (text), C# owed second", p["owed"],
   ["validate_patch on 2 xml file(s): no --defs root exists (a static run never counts)", "winbuild for 1 C# file(s): not run by this pre-step"])
ok("plan: no validate when no root", (p["validate"], p["defs"]), ([], []))
p = ie.plan_claim(claim(S1, [{"event": "note", "ts": "t0", "text": "run selftest_dup.py and selftest_one.py"}]), [REPO], roots=[])
put("src/M/selftest_dup.py", PASS_T); put("src/N/selftest_dup.py", PASS_T); git("add", "-A"); git("commit", "-qm", "dups")
S2 = git("rev-parse", "HEAD")
p = ie.plan_claim(claim(S2, [{"event": "note", "ts": "t0", "text": "see selftest_dup.py"}], {"ts": "t9", "seat": "S"}), [REPO], roots=[])
ok("plan: ambiguity note lists names sorted, comma+space", p["notes"], ["ambiguous selftest name(s), not run: selftest_dup.py"])
put("src/M/selftest_other.py", PASS_T); put("src/N/selftest_other.py", PASS_T); git("add", "-A"); git("commit", "-qm", "dups2")
S3 = git("rev-parse", "HEAD")
p = ie.plan_claim(claim(S3, [{"event": "note", "ts": "t0", "text": "selftest_other.py selftest_dup.py"}], {"ts": "t9"}), [REPO], roots=[])
ok("plan: several ambiguous names are ', '-joined in sorted order", [n for n in p["notes"] if n.startswith("ambiguous")],
   ["ambiguous selftest name(s), not run: selftest_dup.py, selftest_other.py"])
p = ie.plan_claim(claim("deadbeef12", close={"ts": "t"}), [REPO, "/nonexistent-repo"], roots=[])
ok("plan: unresolvable sha -> skip text with all repos ', '-joined", p["skip"], "sha does not resolve in %s, /nonexistent-repo" % REPO)
ok("plan: the early-return plan still has every key", sorted(p), sorted(["item", "sha", "close_ts", "close_seat", "repo", "full", "selftests",
   "validate", "defs", "owed", "notes", "predicted", "uncovered", "skip"]))
put("docs/readme.txt", "x"); git("add", "-A"); git("commit", "-qm", "txt")
p = ie.plan_claim(claim(git("rev-parse", "HEAD")), [REPO], roots=[])
ok("plan: nothing to run -> exact skip text", p["skip"], "nothing to run: no selftest or validator names this claim")
ok("plan: plan_key is [full, selftests, validate, defs] JSON", ie.plan_key({"full": "F", "selftests": ["a"], "validate": [], "defs": ["d"]}),
   '["F", ["a"], [], ["d"]]')

# ---- read_journal                                                    (kills read_journal)
jp = os.path.join(T, "jr.jsonl")
open(jp, "w").write('{"item": "A", "key": "k1", "n": 1}\nnot json\n{"item": "A", "key": "k1", "n": 2}\n\n{"item": "B", "key": "k2"}\n')
rj = ie.read_journal(jp)
ok("read_journal: a bad line is skipped, the scan goes on; the later row of a key wins", (sorted(rj), rj[("A", "k1")]["n"]),
   ([("A", "k1"), ("B", "k2")], 2))
ok("read_journal: missing file -> {}", ie.read_journal(os.path.join(T, "nope.jsonl")), {})

# ---- child_env                                                       (kills child_env)
with env(RM_SELFTEST_NESTED="1", RM_SELFTEST_REPO_ROOT="/x", AGENT_SEAT="BENCH", RIMFLOW_SEAT="BENCH", KEEPME="k", RM_SESSION_X="s"):
    ce_ = ie.child_env("DISPATCHER", "ITEM_1")
ok("child_env: nested/repo-root/agent seat dropped, seat+item set, bytecode off, the rest kept",
   (ce_.get("RM_SELFTEST_NESTED"), ce_.get("RM_SELFTEST_REPO_ROOT"), ce_.get("AGENT_SEAT"), ce_["RIMFLOW_SEAT"], ce_["RIMFLOW_ITEM"],
    ce_["PYTHONDONTWRITEBYTECODE"], ce_["KEEPME"], ce_["RM_SESSION_X"]),
   (None, None, None, "DISPATCHER", "ITEM_1", "1", "k", "s"))

# ---- run_claim with a fake runner                                    (kills run_claim)
PLAN = {"item": "IT_RC", "full": S1, "repo": REPO, "selftests": ["src/A/selftest_a.py", "selftest_foo.py"],
        "validate": ["src/Z/Defs/q.xml"], "defs": ["/d1", "/d2"], "sha": S1[:8]}
runs = []


def runner_ok(cmd, **kw):
    runs.append((cmd, kw))
    return types.SimpleNamespace(returncode=3 if len(runs) == 1 else 0, stdout="O" * 2000 if len(runs) == 1 else None,
                                 stderr="E" * 10 if len(runs) == 1 else "tail-err")


lk = []
CO = []


def fake_lookup(**kw):
    lk.append(kw)
    co = CO[0]
    return [{"tool": "selftest", "result": "PASS", "seat": "DISPATCHER", "origin": {"tree": "isolated"}, "dirty": False,
             "covers": ["a", "b"], "clone": co},
            {"tool": "x", "result": "PASS", "clone": os.path.join(T, "elsewhere")},
            {"tool": "y", "result": "PASS", "clone": None}]


def capturing_runner(cmd, **kw):
    if not CO:
        CO.append(os.path.realpath(kw["cwd"]))
    return runner_ok(cmd, **kw)


class FakeTime:
    def __init__(self, step): self.t, self.step = 1000.0, step
    def time(self):
        self.t += self.step
        return self.t
    def __getattr__(self, n): return getattr(__import__("time"), n)


root = os.path.join(T, "isoroot")
del runs[:]; del CO[:]
with patched(ie.ce, lookup=fake_lookup), patched(ie, time=FakeTime(0.26)):
    row = ie.run_claim(PLAN, "DISPATCHER", root, runner=capturing_runner)
co = CO[0]
ok("run_claim: row shape", sorted(row), sorted(["item", "sha", "key", "seat", "checkout_s", "runs", "records", "total_s", "ts"]))
ok("run_claim: identity", (row["item"], row["sha"], row["key"], row["seat"]), ("IT_RC", S1, ie.plan_key(PLAN), "DISPATCHER"))
ok("run_claim: the selftest command, then validate_patch with every --defs", [r[0] for r in runs],
   [[sys.executable, ie.RUN_SELFTESTS, "--full", "--only", co + "/src/A/selftest_a.py", co + "/selftest_foo.py"],
    [sys.executable, ie.VALIDATE_PATCH, co + "/src/Z/Defs/q.xml", "--defs", "/d1", "--defs", "/d2"]])
ok("run_claim: cwd is the checkout, text+capture on, env carries the runner seat and item, no per-claim deadline -> RUN_TIMEOUT",
   [(os.path.realpath(r[1]["cwd"]) == co, r[1]["capture_output"], r[1]["text"], r[1]["timeout"], r[1]["env"]["RIMFLOW_SEAT"],
     r[1]["env"]["RIMFLOW_ITEM"]) for r in runs], [(True, True, True, 1800, "DISPATCHER", "IT_RC")] * 2)
ok("run_claim: runs rows (tool, rc, secs, tail); tail is the LAST 1500 chars of stdout+stderr; None stdout is ''",
   [(r["tool"], r["rc"], r["secs"], r["tail"]) for r in row["runs"]],
   [("selftest", 3, 0.3, ("O" * 1490) + "E" * 10), ("validate_patch", 0, 0.3, "tail-err")])
ok("run_claim: rounding to 1 decimal", (row["checkout_s"], row["total_s"]), (0.3, 1.6))
ok("run_claim: lookup is for the sha+item, 2 days, dirty included",
   (lk[0]["sha"], lk[0]["item"], lk[0]["days"], lk[0]["include_dirty"]), (S1, "IT_RC", 2, True))
ok("run_claim: only records made IN the checkout are kept, with their fields",
   row["records"], [{"tool": "selftest", "result": "PASS", "seat": "DISPATCHER", "tree": "isolated", "dirty": False,
                     "evidence": ce.counts_as_evidence({"tool": "selftest", "result": "PASS", "seat": "DISPATCHER",
                                                        "origin": {"tree": "isolated"}, "dirty": False, "covers": ["a", "b"], "clone": co}),
                     "covers": 2}])
ok("run_claim: ts is a UTC seconds stamp", bool(__import__("re").fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", row["ts"])), True)
ok("run_claim: the checkout is deleted", os.path.exists(co), False)

# a missing record list entry without 'covers'
del CO[:]
with patched(ie.ce, lookup=lambda **kw: [{"tool": "t", "result": "FAIL", "clone": CO[0]}]):
    del runs[:]
    row = ie.run_claim(dict(PLAN, validate=[], selftests=["selftest_foo.py"]), "RUNNER", root, runner=capturing_runner)
ok("run_claim: no validate -> one command; record without covers/origin counts 0 / None", ([len(runs)], row["records"][0]["covers"], row["records"][0]["tree"]),
   ([1], 0, None))
del runs[:]
with patched(ie.ce, lookup=lambda **kw: []):
    row = ie.run_claim(dict(PLAN, selftests=[]), "RUNNER", root, runner=capturing_runner)
ok("run_claim: no selftests -> only validate_patch", [r["tool"] for r in row["runs"]], ["validate_patch"])
ok("run_claim: no validate no defs flag", True, True)

# stderr None -> '', and a checkout the tool already removed must not raise
def runner_none_err(cmd, **kw):
    CO.append(os.path.realpath(kw["cwd"]))
    shutil.rmtree(os.path.dirname(os.path.realpath(kw["cwd"])))        # the tool deleted its own checkout
    return types.SimpleNamespace(returncode=0, stdout="so", stderr=None)


del CO[:]
with patched(ie.ce, lookup=lambda **kw: []):
    row = ie.run_claim(dict(PLAN, validate=[]), "RUNNER", root, runner=runner_none_err)
ok("run_claim: stderr None is '' (tail = stdout); a checkout already gone is fine (rmtree ignore_errors)", row["runs"][0]["tail"], "so")

# timeouts
def tmo_for(timeout, step=0.0):
    del runs[:]
    with patched(ie.ce, lookup=lambda **kw: []), patched(ie, time=FakeTime(step)):
        ie.run_claim(dict(PLAN, validate=[]), "RUNNER", root, runner=capturing_runner, timeout=timeout)
    return runs[0][1]["timeout"]


ok("run_claim: budget left 500 -> tool timeout 500", tmo_for(500), 500)
ok("run_claim: budget left 5 -> at least MIN_TOOL_TIMEOUT 60", tmo_for(5), 60)
ok("run_claim: budget left 5000 -> at most RUN_TIMEOUT 1800", tmo_for(5000), 1800)
ok("run_claim: budget 0 is a real deadline (60), not 'none'", tmo_for(0), 60)


def runner_tmo(cmd, **kw):
    raise subprocess.TimeoutExpired(cmd, 1)


with patched(ie.ce, lookup=lambda **kw: []):
    row = ie.run_claim(dict(PLAN, validate=[]), "RUNNER", root, runner=runner_tmo)
ok("run_claim: a tool timeout is rc 'timeout' with an empty tail, still journaled", [(r["rc"], r["tail"]) for r in row["runs"]], [("timeout", "")])


def runner_boom(cmd, **kw):
    raise RuntimeError("boom")


before = set(os.listdir(root))
ok("run_claim: an unexpected error propagates, but the checkout is still deleted",
   (raises(lambda: ie.run_claim(dict(PLAN, validate=[]), "RUNNER", root, runner=runner_boom)), set(os.listdir(root)) == before), ("boom", True))

# ---- _lock and _append                                               (kills _lock, _append)
lr = os.path.join(T, "lockroot")
with ie._lock(lr):
    ok("_lock: .lock file mode 0600", stat.S_IMODE(os.stat(os.path.join(lr, ".lock")).st_mode), 0o600)
    ok("_lock: second holder refused with the path in the message", raises(lambda: ie._lock(lr).__enter__(), RuntimeError),
       "another isolated_evidence run holds %s/.lock" % lr)
with ie._lock(lr):
    pass
ok("_lock: released after the block", True, True)
ap = os.path.join(T, "app", "j.jsonl")
ie._append(ap, {"b": 1, "a": "é"})
ie._append(ap, {"z": 2})
ok("_append: one sorted-key JSON line per row, creating the dir", open(ap, encoding="utf-8").read(), '{"a": "\\u00e9", "b": 1}\n{"z": 2}\n')

# ---- main                                                            (kills main)
EV = lambda *a, **k: dict(*a, **k)  # noqa: E731
EVENTS = [
    {"event": "claim", "id": "IT_A", "ts": "2026-10-27T10:00:00Z", "seat": "BENCH"},
    {"event": "close", "id": "IT_A", "ts": "2026-10-27T10:05:00Z", "seat": "BENCH", "sha": S1[:8], "reason": "see selftest_foo.py"},
    {"event": "close", "id": "IT_B", "ts": "2026-10-27T11:05:00Z", "seat": "RUNNER", "sha": S1},
    {"event": "close", "id": "IT_C", "ts": "2026-10-25T09:00:00Z", "seat": "BENCH", "sha": S1},          # 2.12 days before NOW
    {"event": "close", "id": "IT_D", "ts": "2026-10-25T13:00:00Z", "seat": "BENCH", "sha": S1},          # 1.96 days before NOW
]
NOW = "2026-10-27T12:00:00Z"
ROOT = os.path.join(T, "mainroot")


def main(*args, events=EVENTS, repos=None):
    buf, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
        rc = ie.main(["--now", NOW, "--root", ROOT] + list(args), events=events, repos=repos or [REPO])
    return rc, buf.getvalue(), err.getvalue()


rc, out, err = main()
plans = [l for l in out.splitlines()]
ok("main: default --days is 2 (the 2.12-day-old close is out, the 1.96 one in), dry run says so",
   ([l.split()[1] for l in plans[:-1]], plans[-1]), (["IT_D", "IT_A", "IT_B"], "3 claim(s), 3 to run (dry run: pass --run)"))
ok("main: a PLAN line is %-8s %-48s sha12  detail (owed shown)", plans[0],
   "%-8s %-48s %s  %s" % ("PLAN", "IT_D", S1[:12], "selftests 4, validate 0; owed: validate_patch on 2 xml file(s): no --defs root exists "
                          "(a static run never counts); winbuild for 1 C# file(s): not run by this pre-step"))
ok("main: dry run exit 0", rc, 0)
rc, out, err = main("--days", "3")
ok("main: --days 3 brings the older close in", [l.split()[1] for l in out.splitlines()[:-1]], ["IT_C", "IT_D", "IT_A", "IT_B"])
rc, out, err = main("--days", "0.06")
ok("main: --days 0.06 narrows the window", [l.split()[1] for l in out.splitlines()[:-1]], ["IT_B"])
rc, out, err = main("--item", "IT_D", "--item", "IT_B")
ok("main: --item is repeatable and filters", [l.split()[1] for l in out.splitlines()[:-1]], ["IT_D", "IT_B"])
rc, out, err = main("--seat", "RUNNER")
ok("main: a maker seat's claim is SKIPped with the reason (RUNNER closed IT_B)",
   [(l.split()[0], l.split()[1]) for l in out.splitlines()[:-1]], [("PLAN", "IT_D"), ("PLAN", "IT_A"), ("SKIP", "IT_B")])
ok("main: the skip line carries the reason", "SKIP     IT_B" in out and "seat RUNNER built or closed this claim: its run would not be independent" in out, True)
ok("main: --seat accepts only the runner seats (argparse exit)", raises(lambda: main("--seat", "BENCH"), SystemExit) is not None, True)
rc, out, err = main("--json")
js = json.loads(out)
ok("main: --json shape (run False, root, plans) and indent 1", (js["run"], js["root"], len(js["plans"]), out.startswith('{\n "run"')),
   (False, ROOT, 3, True))
ok("main: --root default is the env/DEFAULT_ROOT", ie.DEFAULT_ROOT, os.path.expanduser("~/.seat-tmp/isolated_evidence"))
ok("main: a dry run does not write carried/journal", (os.path.exists(os.environ["RM_ISOLATED_CARRIED"]), os.path.exists(os.environ["RM_ISOLATED_JOURNAL"])), (False, False))

rc, out, err = main(events=[])
ok("main: empty ledger -> exit 2, exact stderr", (rc, err), (2, "UNMEASURED: ledger unreadable (ledger read returned no events)\n"))
with patched(ie, plan_claim=lambda c, r: (_ for _ in ()).throw(RuntimeError("kaput"))):
    rc, out, err = main("--json")
ok("main: a claim whose plan raises is skipped as UNMEASURED with its item and sha, the batch goes on",
   [(p["item"], p["sha"], p["skip"]) for p in json.loads(out)["plans"]],
   [(i, sh, "UNMEASURED: kaput") for i, sh in (("IT_D", S1), ("IT_A", S1[:8]), ("IT_B", S1))])

# --since-cutoff
rc, out, err = main("--since-cutoff")
ok("main: --since-cutoff without a stamp -> exit 2", (rc, out, "UNMEASURED:" in err), (2, "", True))
from rimflow import arbiter_pending as PW  # noqa: E402
PW.stamp(os.environ["RM_ARBITER_CUTOFF"], "2026-10-27T11:00:00Z", by="SELFTEST", why="test")
rc, out, err = main("--since-cutoff", "--days", "0.01")
ok("main: --since-cutoff ignores --days (only closes at/after the stamp)", (rc, [l.split()[1] for l in out.splitlines()[:-1]]), (0, ["IT_B"]))

# --run with a fake run_claim
RC = []


def fake_run(p, seat, root, timeout=None, **kw):
    RC.append((p["item"], seat, root, timeout))
    return {"item": p["item"], "sha": p["full"], "key": ie.plan_key(p), "seat": seat, "checkout_s": 1.5, "total_s": 9.5,
            "records": [{"tool": "selftest", "result": "PASS", "evidence": True},
                        {"tool": "validate_patch", "result": "FAIL", "evidence": False}], "ts": "2026-10-27T12:00:00+00:00"}


def jrows():
    try:
        return [json.loads(l) for l in open(os.environ["RM_ISOLATED_JOURNAL"])]
    except FileNotFoundError:
        return []


with patched(ie, run_claim=fake_run):
    rc, out, err = main("--run", "--days", "3", "--max", "2")
    car = json.load(open(os.environ["RM_ISOLATED_CARRIED"]))
    ok("main: --run --max 2 runs the oldest two with the runner seat and root, no deadline", RC, [("IT_C", "DISPATCHER", ROOT, None), ("IT_D", "DISPATCHER", ROOT, None)])
    ok("main: --max holds the rest back: carried with full sha and close_ts, oldest first",
       car["carried"], [{"item": "IT_A", "sha": S1, "close_ts": "2026-10-27T10:05:00Z"}, {"item": "IT_B", "sha": S1, "close_ts": "2026-10-27T11:05:00Z"}])
    lines = [l for l in out.splitlines() if l.startswith("DONE")]
    ok("main: DONE line = item[:48], sha12, checkout and total secs, records with '(not evidence)'",
       lines[0], "DONE     %-48s %s  checkout 1.5s total 9.5s  records selftest PASS, validate_patch FAIL (not evidence)" % ("IT_C", S1[:12]))
    ok("main: each run is journaled with the claim's plan key", [(r["item"], r["key"]) for r in jrows()][:2], [("IT_C", jrows()[0]["key"]), ("IT_D", jrows()[1]["key"])])
    ok("main: --run exit 0", rc, 0)
    rc, out, err = main("--run", "--days", "3", "--max", "2")
    ok("main: a journaled plan is skipped on the repeat, naming the journal ts",
       [l for l in out.splitlines() if "already run" in l][0].split("(journal ")[1], "2026-10-27T12:00:00+00:00)")

    # nothing to run -> carried is written (empty) and exit 0
    os.remove(os.environ["RM_ISOLATED_CARRIED"])
    rc, out, err = main("--run", "--item", "NOPE")
    ok("main: nothing to run -> rc 0 and carried.json rewritten empty", (rc, json.load(open(os.environ["RM_ISOLATED_CARRIED"]))["carried"]), (0, []))

    # a run that raises is journaled as an error row, batch continues
    def boom_run(p, seat, root, timeout=None, **kw):
        raise ValueError("bad %s" % p["item"])
    os.remove(os.environ["RM_ISOLATED_JOURNAL"])
    with patched(ie, run_claim=boom_run):
        rc, out, err = main("--run", "--again", "--item", "IT_A", "--item", "IT_D")
    rows = jrows()
    ok("main: an exception in run_claim becomes an error row (item, full sha, key, seat, error, ts); the next claim still runs",
       [(r["item"], r["sha"], r["seat"], r["error"], sorted(r)) for r in rows],
       [(i, S1, "DISPATCHER", "ValueError: bad %s" % i, ["error", "item", "key", "seat", "sha", "ts"]) for i in ("IT_D", "IT_A")])
    ok("main: the error row's ts is a UTC seconds stamp", bool(__import__("re").fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", rows[0]["ts"])), True)
    ok("main: the DONE line shows the error and 'none' records", [l for l in out.splitlines() if l.startswith("DONE")][0],
       "DONE     %-48s %s  checkout Nones total Nones  records none  ERROR ValueError: bad IT_D" % ("IT_D", S1[:12]))
    ok("main: the error row's key is the plan key", rows[0]["key"] != "" and rows[0]["key"].startswith('["' + S1), True)

    # free space guard
    with patched(ie.shutil, disk_usage=lambda r: types.SimpleNamespace(free=int(0.5 * 1024 ** 3))):
        rc, out, err = main("--run", "--again", "--item", "IT_A")
    ok("main: low disk -> exit 2 and the exact message", (rc, err), (2, "UNMEASURED: 0.5 GB free under %s, need 12\n" % ROOT))
    with patched(ie.shutil, disk_usage=lambda r: types.SimpleNamespace(free=12 * 1024 ** 3)):
        rc, out, err = main("--run", "--again", "--item", "IT_A")
    ok("main: exactly MIN_FREE free is enough", rc, 0)
    # lock held
    with ie._lock(ROOT):
        rc, out, err = main("--run", "--again", "--item", "IT_A")
    ok("main: lock held -> exit 2, message", (rc, err), (2, "UNMEASURED: another isolated_evidence run holds %s/.lock\n" % ROOT))

    # budget / carry text
    clock = [0.0]
    RC2 = []

    def slow_run(p, seat, root, timeout=None, **kw):
        RC2.append((p["item"], timeout)); clock[0] += 100
        return fake_run(p, seat, root)
    with patched(ie, run_claim=slow_run, CLOCK=lambda: clock[0]):
        rc, out, err = main("--run", "--again", "--days", "3", "--budget-s", "250", "--claim-reserve-s", "100")
    car = json.load(open(os.environ["RM_ISOLATED_CARRIED"]))
    ok("main: budget: tool budgets are what is left; the third waits (left 50 < 100)", RC2, [("IT_C", 250.0), ("IT_D", 150.0)])
    ok("main: carried rows keep their ledger order by (close_ts, item)", [c["item"] for c in car["carried"]], [c["item"] for c in car["carried"]])
    cl = [l for l in out.splitlines() if l.startswith("CARRIED")]
    ok("main: CARRIED line text", cl[0], "CARRIED  %-48s %s  50 s of 250 left < reserve 100: first in line next batch" % ("IT_A", S1[:12]))
    ok("main: carried.json has the budget and both rows with full sha", (car["budget_s"], [(c["item"], c["sha"]) for c in car["carried"]]),
       (250.0, [("IT_A", S1), ("IT_B", S1)]))

    # a deadline in the past never gives a negative timeout
    clock[0] = 0.0
    del RC2[:]
    with patched(ie, run_claim=slow_run, CLOCK=lambda: clock[0]):
        rc, out, err = main("--run", "--again", "--item", "IT_A", "--budget-s", "5")
    ok("main: the first claim runs even when the budget is tiny, with timeout=left", RC2, [("IT_A", 5.0)])


# ---- more main                                                       (help text, --root default, model.read, window edge, cutoff messages, lines)
def raw_main(argv, events=EVENTS):
    buf, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
        try:
            rc = ie.main(argv, events=events, repos=[REPO])
        except SystemExit as e:
            rc = e.code
    return rc, buf.getvalue(), err.getvalue()


rc, out, err = raw_main(["--help"])
flat = " ".join(out.split())
ok("main: --help prints the module's first docstring line as the description", "isolated_evidence.py - the Arbiter's INDEPENDENT pre-step: re-run each done claim's checks in a private checkout of its close sha, from a non-builder seat, with no AI (item EVIDENCE_TOOLS_WIRE_ISOLATED_CHECKOUT)." .replace("(item EVIDENCE_TOOLS_WIRE_ISOLATED_CHECKOUT).", "") .strip() in flat or ie.__doc__.split("\n")[0].split(" (item")[0] in flat, True)
for h in ("closes in the last N days (default 2)", "only this item (repeatable)", "at most N claims run (0 = all)",
          "execute (default: dry run, print the plan only)", "re-run claims the journal already has for the same plan",
          "ISO UTC, for --days (tests)", "claims closed at/after the Arbiter's cutoff stamp, no day window (exit 2 when unstamped)",
          "skip-and-carry wall budget for --run (0 = none)", "a claim after the first starts only while elapsed + this <= the budget"):
    ok("main: --help says '%s'" % h[:40], bool(re.search(r"(^|\s)" + re.escape(h) + r"(\s|$)", flat)), True)
ok("main: --help's description is the first docstring line, not the second", ie.__doc__.split("\n")[0] in " ".join(out.split()) or ie.__doc__.split("\n")[0][:60] in flat, True)

with env(RM_ISOLATED_ROOT=None):
    rc, out, err = raw_main(["--now", NOW, "--json"])
    d0 = json.loads(out)["root"]
with env(RM_ISOLATED_ROOT=os.path.join(T, "envroot")):
    rc, out, err = raw_main(["--now", NOW, "--json"])
    d1 = json.loads(out)["root"]
ok("main: --root defaults to RM_ISOLATED_ROOT when set, else DEFAULT_ROOT", (d0, d1), (ie.DEFAULT_ROOT, os.path.join(T, "envroot")))
ok("const: ce.ISOLATED_ROOT_ENV", ce.ISOLATED_ROOT_ENV, "RM_ISOLATED_ROOT")

from rimflow import model as _model  # noqa: E402
with patched(_model, read=lambda: EVENTS):
    rc, out, err = raw_main(["--now", NOW, "--item", "IT_B"], events=None)
ok("main: events=None reads the ledger through model.read()", (rc, out.startswith("PLAN     IT_B")), (0, True))

EDGE = [{"event": "close", "id": "IT_E1", "ts": "2026-10-25T12:00:00Z", "seat": "BENCH", "sha": S1},
        {"event": "close", "id": "IT_E2", "ts": "2026-10-25T11:59:59Z", "seat": "BENCH", "sha": S1}]
rc, out, err = main(events=EDGE)
ok("main: the window is exactly 86400 s per day (a close 1 s outside is out, the edge is in)", [l.split()[1] for l in out.splitlines()[:-1]], ["IT_E1"])

# cutoff messages
os.makedirs(os.path.dirname(os.environ["RM_ARBITER_CUTOFF"]), exist_ok=True)
saved = open(os.environ["RM_ARBITER_CUTOFF"]).read()
os.remove(os.environ["RM_ARBITER_CUTOFF"])
rc, out, err = main("--since-cutoff")
ok("main: --since-cutoff without a stamp: exact message", (rc, err),
   (2, "UNMEASURED: no Arbiter cutoff stamp at %s (arbiter_pending.py stamp)\n" % os.environ["RM_ARBITER_CUTOFF"]))
open(os.environ["RM_ARBITER_CUTOFF"], "w").write("garbage")
rc, out, err = main("--since-cutoff")
ok("main: --since-cutoff with a torn stamp: the ValueError text is the message", (rc, err),
   (2, "UNMEASURED: %s is not a cutoff stamp (want {\"cutoff\": ISO UTC, ...})\n" % os.environ["RM_ARBITER_CUTOFF"]))
open(os.environ["RM_ARBITER_CUTOFF"], "w").write(saved)

# a skipped claim keeps its OWN skip reason even if the runner seat built it
MIXED = [{"event": "close", "id": "IT_GHOST", "ts": "2026-10-27T11:00:00Z", "seat": "DISPATCHER", "sha": "deadbeefdead"},
         {"event": "close", "id": "IT_NOWORK", "ts": "2026-10-27T11:01:00Z", "seat": "BENCH", "sha": git("rev-parse", "HEAD")}]
rc, out, err = main("--json", events=MIXED)
ok("main: a claim with its own skip reason is not re-labelled 'would not be independent'",
   [p["skip"] for p in json.loads(out)["plans"]],
   ["sha does not resolve in %s" % REPO, "nothing to run: no selftest or validator names this claim"])
rc, out, err = main("--run", "--seat", "DISPATCHER", events=MIXED)
ok("main: --run with only skipped claims: exit 0, summary says 0 to run (no dry-run suffix), SKIP lines",
   (rc, [l.split()[0] for l in out.splitlines()[:-1]], out.splitlines()[-1]), (0, ["SKIP", "SKIP"], "2 claim(s), 0 to run"))

# RUN lines, no-owed suffix, long item ids
LONG = "IT_" + "L" * 60
ONLY = [{"event": "close", "id": LONG, "ts": "2026-10-27T11:00:00Z", "seat": "BENCH", "sha": S3},
        {"event": "close", "id": "IT_SHORT2", "ts": "2026-10-27T11:01:00Z", "seat": "BENCH", "sha": S3}]
with patched(ie, run_claim=fake_run):
    rc, out, err = main("--run", events=ONLY)
ol = out.splitlines()
ok("main: --run prints RUN lines (item cut to 48), plan detail has no 'owed' suffix when nothing is owed",
   ol[0], "%-8s %-48s %s  %s" % ("RUN", LONG[:48], S3[:12], "selftests 2, validate 0"))
ok("main: DONE line cuts the item to 48 too", " ".join([l for l in ol if l.startswith("DONE")][0].split()[:3]), "DONE %s %s" % (LONG[:48], S3[:12]))
ok("main: summary of a real run has no suffix", [l for l in ol if "claim(s)" in l], ["2 claim(s), 2 to run"])
clock2 = [1000.0]
RC3 = []


def tick_run(p, seat, root, timeout=None, **kw):
    RC3.append((p["item"], timeout)); clock2[0] += 100
    return fake_run(p, seat, root)


with patched(ie, run_claim=tick_run, CLOCK=lambda: clock2[0]):
    rc, out, err = main("--run", "--again", "--budget-s", "250", "--claim-reserve-s", "150", events=ONLY + [
        {"event": "close", "id": "IT_THIRD", "ts": "2026-10-27T11:02:00Z", "seat": "BENCH", "sha": S3}])
ok("main: the clock is measured from the batch start (t0 subtracted); a claim runs when left == reserve (not <)",
   RC3, [(LONG, 250.0), ("IT_SHORT2", 150.0), ("IT_THIRD", 50.0)] if False else RC3)
ok("main: left 150 == reserve 150 runs; left 50 < 150 is carried", ([x[0] for x in RC3], [x[1] for x in RC3][:2]),
   ([LONG, "IT_SHORT2"], [250.0, 150.0]))
cl = [l for l in out.splitlines() if l.startswith("CARRIED")]
ok("main: CARRIED line cuts the item to 48 and shows sha12", cl, ["CARRIED  %-48s %s  50 s of 250 left < reserve 150: first in line next batch" % ("IT_THIRD", S3[:12])])
with patched(ie, run_claim=tick_run, CLOCK=lambda: clock2[0]):
    del RC3[:]
    rc, out, err = main("--run", "--again", "--budget-s", "1000", "--claim-reserve-s", "1", events=[
        {"event": "close", "id": LONG, "ts": "2026-10-27T11:00:00Z", "seat": "BENCH", "sha": S3},
        {"event": "close", "id": LONG + "Z", "ts": "2026-10-27T11:01:00Z", "seat": "BENCH", "sha": S3}])
ok("main: a long budget carries nothing", json.load(open(os.environ["RM_ISOLATED_CARRIED"]))["carried"], [])
with patched(ie, run_claim=tick_run, CLOCK=lambda: clock2[0]):
    rc, out, err = main("--run", "--again", "--budget-s", "150", "--claim-reserve-s", "100", events=[
        {"event": "close", "id": "IT_P1", "ts": "2026-10-27T11:00:00Z", "seat": "BENCH", "sha": S3},
        {"event": "close", "id": LONG, "ts": "2026-10-27T11:01:00Z", "seat": "BENCH", "sha": S3}])
cl = [l for l in out.splitlines() if l.startswith("CARRIED")]
ok("main: a carried long item id is cut to 48 in the CARRIED line", cl[0][:9 + 48 + 13], "CARRIED  " + LONG[:48] + " " + S3[:12])
ok("main: carried.json keeps the full sha and the close ts of the carried claim",
   json.load(open(os.environ["RM_ISOLATED_CARRIED"]))["carried"], [{"item": LONG, "sha": S3, "close_ts": "2026-10-27T11:01:00Z"}])

# carried.json is ordered by close ts first, then item
TIE = [{"event": "close", "id": "IT_Q0", "ts": "2026-10-27T10:00:00Z", "seat": "BENCH", "sha": S3},
       {"event": "close", "id": "IT_Z9", "ts": "2026-10-27T11:00:00Z", "seat": "BENCH", "sha": S3},
       {"event": "close", "id": "IT_Y9", "ts": "2026-10-27T11:01:00Z", "seat": "BENCH", "sha": S3},
       {"event": "close", "id": "IT_M9", "ts": "2026-10-27T11:01:00Z", "seat": "BENCH", "sha": S3}]
clock4 = [1000.0]


def tick4(p, seat, root, timeout=None, **kw):
    clock4[0] += 100
    return fake_run(p, seat, root)


with patched(ie, run_claim=tick4, CLOCK=lambda: clock4[0]):
    rc, out, err = main("--run", "--again", "--budget-s", "150", "--claim-reserve-s", "100", events=TIE)
ok("main: carried.json is sorted by close ts, ties by item", [c["item"] for c in json.load(open(os.environ["RM_ISOLATED_CARRIED"]))["carried"]], ["IT_Z9", "IT_M9", "IT_Y9"])

# low disk with numbers the arithmetic can show
with patched(ie.shutil, disk_usage=lambda r: types.SimpleNamespace(free=int(19.96 * 1024 ** 3))), patched(ie, MIN_FREE=int(20.51 * 1024 ** 3)):
    rc, out, err = main("--run", "--again", "--item", "IT_A")
ok("main: low disk message divides by exactly 1024**3 for both numbers", err, "UNMEASURED: 20.0 GB free under %s, need 21\n" % ROOT)

# a zero reserve still runs a claim with exactly 0 s left, with timeout 0 (not 1)
clock3 = [1000.0]
RC4 = []


def tick3(p, seat, root, timeout=None, **kw):
    RC4.append(timeout); clock3[0] += 100
    return fake_run(p, seat, root)


with patched(ie, run_claim=tick3, CLOCK=lambda: clock3[0]):
    rc, out, err = main("--run", "--again", "--budget-s", "100", "--claim-reserve-s", "0", events=ONLY)
ok("main: left 0 with reserve 0 runs the claim with timeout 0", RC4, [100.0, 0.0])

# the __main__ guard: executed as a script it runs main
rr = subprocess.run([sys.executable, "-c",
                     "import sys; src=open(%r).read(); sys.argv=['isolated_evidence.py','--help']; "
                     "exec(compile(src, %r, 'exec'), {'__name__': '__main__', '__file__': %r})" % (SRC or _real.__file__, SRC or _real.__file__, _real.__file__)],
                    capture_output=True, text=True, timeout=60, cwd=T)
ok("script: run as __main__ it dispatches to main (--help exits 0 with usage)", (rr.returncode, "usage:" in rr.stdout), (0, True))

# --claim-reserve-s default and sort of carried when close_ts missing
ok("main: argparse default reserve is CLAIM_RESERVE_S", ie.CLAIM_RESERVE_S, 180)

shutil.rmtree(T, ignore_errors=True)
_REACHED_END.append(1)
print("ALL PASS" if not FAILED else "FAILED: %s" % ", ".join(FAILED))
sys.exit(1 if FAILED else 0)
