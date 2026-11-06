#!/usr/bin/env python3
# selftest-timeout: 520
"""selftest_relentless_close_crash.py - kill a close at every step between its writes; the records agree or a tick recovers
them (RELENTLESS_PROVE_CLOSE_CRASH_EACH_STEP, owner card 2026-11-06).

Completing an item writes four places: the Relentless store, the ledger, git, the verdict record. This test forks a child
that carries the item from a waiting check to its end, and SIGKILLs it (a real kill: no finally, no flush, no flock release
but the kernel's) straight after one durable write. The parent then runs fresh ticks, as the next timer firing would, and
reads all four records. One kill per boundary, for each of the three endings of a check.

Real: Store, verdict(), tick(), step(), finished(), Effects.ledger_close/flush/sync/level_books/item_state, cli.py as a
subprocess on a ledger inside a throwaway git repo with a bare origin. Not real: `./publish` there is a four-line stand-in
(commit, then pull --rebase and push; publish.py's own selftests cover it), and every other effect is FakeWorld's.

THE BOUNDARIES are not typed by hand from reading the code: a clean run traces them, and that trace must equal the list
below, so a new write in the close path turns this test red until someone says what a kill there does. Each name is the
write just done:
  state:<status>             Store.save of the item's state.json, with the status it wrote
  attempt:<end>              a row of attempts.jsonl
  journal:<do>               a row of journal.jsonl naming the item
  shadow                     the shadow row beside a verdict
  receipt                    the worker's durable receipt from `finish`
  evidence:marker            the Marker's entry in the evidence record
  ledger:<verb>              a `rimflow <verb>` subprocess returned
  land                       ./publish returned: the ledger is on origin
Beside the trace, three kills inside a write:
  cli:event-before-prose     `rimflow close`: the close event on disk, the item's prose not yet moved
  publish:commit-before-push the ledger committed in books, not pushed
  store:tmp-before-rename    Store._write: the new state.json in its temp file, not yet renamed over the old

The kills are between the writes of one child; the first kill is after the first write, so "before anything" is covered by
the clean run. A kill before verdict()'s save leaves no verdict: nothing to recover, a fresh checker answers.
Two kills also recover with origin moved by another seat meanwhile, so the tick levels the books around the wreck.

What it found on its first run, all fixed in the close path: a kill after the blind result's `verify` wrote a second run on the
next tick (PASS and FAIL); a kill between `rimflow close`'s event and its prose move left a done item in the live glob for
good; a kill after the done save lost the `done` journal row, and one before it doubled the `done` attempt; a WEAK or
UNMEASURED verdict's ledger note was lost by any kill before it was written; a kill between verdict() and its evidence receipt
lost the receipt when UNMEASURED consumed the check first; a kill before a return's save doubled that ending's attempt row.

Left as they are, with the reason: a kill straight after verdict()'s save loses that one shadow row (it "is read by nothing
that acts"), and a kill straight after a done save leaves the clones in place, because FakeWorld stands in for them here and
the real pool reclaims an ended item's clone first (make_room ranks ENDED 0). The game road and the foreign tomb's wait are
not driven: they reach this close through finished() and ledger_close(), which are.

    python3 src/RimMandrake/rimflow/selftest_relentless_close_crash.py [--ending PASS|FAIL|WEAK] [--trace] [--keep]
Prints FIXTURE_VERDICT: PASS|FAIL; exit 0 on PASS, 1 on FAIL.
"""
import json, os, shutil, signal, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import relentless as R                                          # noqa: E402
import selftest_relentless as SL                                # noqa: E402

ITEM = "CLOSECRASH_PROVE_FIXTURE_KILLED_REPEATEDLY"
LED = "infrastructure/state/ledger/"
PROSE = "infrastructure/state/items/%s.md" % ITEM
CLOSED = "infrastructure/state/items/closed/%s.md" % ITEM
SEAT = "BENCH"

PUBLISH = """#!/bin/bash
set -e
if [ "$1" = "-m" ]; then m="$2"; shift 2; git add -- "$@"; git commit -qm "$m"; fi
if [ -n "$CRASH_ARMED_PUBLISH" ] && [ -e "$CRASH_ARMED_PUBLISH" ]; then kill -9 "$PPID"; kill -9 $$; fi
git pull -q --rebase origin main
git push -q origin HEAD:main
"""

CLI_KILL = """import os, signal, sys
sys.path.insert(0, %r)
sys.path.insert(0, %r)
import cli
def die(_i):
    if os.path.exists(%r):
        os.kill(os.getppid(), signal.SIGKILL)
        os.kill(os.getpid(), signal.SIGKILL)
    return real(_i)
real, cli._move_prose_to_closed = cli._move_prose_to_closed, die
sys.exit(cli.main())
"""

FAILS = []
TRACE_PATH = None
ARMED = None        # the boundary this process dies at: an index into the trace, or a named kill


def ok(cond, what):
    if not cond:
        FAILS.append(what)
        print("FAIL  " + what)
    return cond


def sh(cwd, *a):
    r = subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("%s -> %d: %s" % (" ".join(a), r.returncode, r.stderr[-400:]))
    return r.stdout.strip()


# ---------------------------------------------------------------- the world: real ledger and git, the rest fake

REAL = ("git", "git_ok", "sync", "ignored_collision", "level_books", "_level_rows", "_unlevel", "_carry_late", "flush",
        "prose_moves", "append_dirs_locked", "shards_locked", "ledger_dir_locked", "drop_stray_untracked",
        "shuffled_shards", "ledger_items", "item_state", "state_of", "closed", "ledger_close", "work_sha", "touched",
        "ledger_marker_fail", "ledger_note", "ledger_note_once", "published", "contains", "marker_said", "settle_prose")


class CrashWorld(SL.FakeWorld):
    def __init__(self, store, r):
        super().__init__(n=0)
        self.items = {ITEM: "doing"}
        del self.touched                # FakeWorld's canned list: Effects.touched reads the real commit here
        self.store, self.s, self.r = store, store, r
        self.base = store.root
        self.books = os.path.join(store.root, "books")
        self.marked = set()
        self._ledger = None
        self._budget = self._helpers = R.NOT_READ
        self.bounce = set()

    def commit_time(self, sha):
        return 0

    def live_round_launch(self, *a, **k):   # no live lane in this test
        return None

    def changed(self, base, sha, item):     # FakeWorld's reads the canned list deleted above
        return ["src/x.py"]

    def alive(self, run):       # the worker and the checker went with the kill; the fixture runs none of its own
        return False

    def paused(self):
        """Past its check the item waits in line: no new worker, or the fixture would rebuild it for ever."""
        return self.s.load(ITEM)["status"] not in ("candidate", "checking")

    def env(self, seat):
        e = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
        e.update(RIMFLOW_LEDGER=os.path.join(self.books, LED, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(self.books, "infrastructure/state/items"),
                 RIMFLOW_SEAT=seat, AGENT_SEAT=seat, RELENTLESS_SUPERVISOR="1", RIMFLOW_BRIDGE_SEAT=R.BRIDGE_HOLDER, CLAUDE_PROJECT_DIR=self.books,
                 RIMFLOW_GIT_CWD=self.books)
        return e

    def rimflow(self, *args, timeout=60, seat=None):
        cmd = [sys.executable, os.path.join(self.base, "cli_kill.py"), *args]
        r = subprocess.run(cmd, cwd=self.books, env=self.env(seat or self.r["seat"]), capture_output=True, text=True,
                           timeout=timeout, stdin=subprocess.DEVNULL)
        boundary("ledger:%s" % args[0])
        return r

    def flush(self):
        head = self.git(self.books, "rev-parse", "origin/main").stdout.strip()
        out = R.Effects.flush(self)
        if self.git(self.books, "rev-parse", "origin/main").stdout.strip() != head:     # nothing to land is no write
            boundary("land")
        return out


for name in REAL:
    if name != "flush":
        setattr(CrashWorld, name, getattr(R.Effects, name))


# ---------------------------------------------------------------- the kill

def boundary(name):
    """A write was just done. Trace it; die here if this is the armed one. fsync: a trace row must survive the kill."""
    n = COUNT[0]
    COUNT[0] += 1
    if TRACE_PATH:
        with open(TRACE_PATH, "a") as f:
            f.write(name + "\n")
            f.flush()
            os.fsync(f.fileno())
    if ARMED == n:
        os.kill(os.getpid(), signal.SIGKILL)


COUNT = [0]


def arm_store():
    """Wrap Store's two writers so each write of THIS item's records is a boundary."""
    wr, ap = R.Store._write, R.Store._append

    def _write(self, path, text):
        if ARMED == "store:tmp-before-rename" and path.endswith(os.path.join(ITEM, "state.json")) \
                and json.loads(text).get("status") == "closing":
            real_replace = os.replace

            def die(a, b):
                os.replace = real_replace
                os.kill(os.getpid(), signal.SIGKILL)
            os.replace = die
        wr(self, path, text)
        if path.endswith(os.path.join(ITEM, "state.json")):
            boundary("state:%s" % json.loads(text).get("status"))
        elif ITEM in path and os.path.basename(os.path.dirname(path)) == "receipts":
            boundary("receipt")

    def _append(self, path, line):
        ap(self, path, line)
        base = os.path.basename(path)
        try:
            rec = json.loads(line)
        except ValueError:
            return
        if base == "attempts.jsonl" and ITEM in path:
            boundary("attempt:%s" % rec.get("end"))
        elif base == "journal.jsonl" and rec.get("item") == ITEM:
            boundary("journal:%s" % rec.get("do"))
        elif base == "shadow.jsonl" and rec.get("item") == ITEM:
            boundary("shadow")
    R.Store._write, R.Store._append = _write, _append
    em = R.evidence.append_marker

    def append_marker(*a, **k):
        out = em(*a, **k)
        if out:     # None: this nonce is already there, nothing was written
            boundary("evidence:marker")
        return out
    R.evidence.append_marker = append_marker


# ---------------------------------------------------------------- the fixture

class Rig:
    """One item, its check launched and waiting, on disk. restore() puts that moment back for the next kill."""
    def __init__(self):
        self.d = tempfile.mkdtemp(prefix="rl-closecrash-")
        self.base = os.path.join(self.d, "base")
        self.snap = os.path.join(self.d, "snap")
        self.snap_finish = os.path.join(self.d, "snap_finish")
        os.makedirs(self.base)
        self.origin = os.path.join(self.d, "origin.git")
        sh(self.d, "git", "init", "-q", "--bare", "-b", "main", self.origin)
        self.books = os.path.join(self.base, "books")
        sh(self.base, "git", "clone", "-q", self.origin, self.books)
        for k, v in (("user.name", "t"), ("user.email", "t@t"), ("commit.gpgsign", "false")):
            sh(self.books, "git", "config", k, v)
        self.put("src/x.py", "x = 1\n")
        self.put(PROSE, "## spec\nthe fixture\n")
        self.put(LED + "events/.keep", "")
        self.put("publish", PUBLISH)
        self.put(".gitignore", "infrastructure/state/queue/\ninfrastructure/state/ledger/.rimflow-dispatch.lock\n")
        os.chmod(os.path.join(self.books, "publish"), 0o755)
        sh(self.books, "git", "add", "-A")
        sh(self.books, "git", "commit", "-qm", "seed")
        sh(self.books, "git", "push", "-q", "origin", "HEAD:main")
        sh(self.books, "git", "branch", "-q", "-u", "origin/main")
        self.armed_cli = os.path.join(self.base, "armed_cli")
        self.armed_publish = os.path.join(self.base, "armed_publish")
        os.environ["CRASH_ARMED_PUBLISH"] = self.armed_publish
        with open(os.path.join(self.base, "cli_kill.py"), "w") as f:
            f.write(CLI_KILL % (os.path.dirname(HERE), HERE, self.armed_cli))

        self.r = dict(SL.RULES, **{"snag_again_wait_h": 0, "pool_parked_lists": [], "share": 1.0, "seat": SEAT})
        self.now = 1000000.0
        R.clock = lambda: self.now
        self.s = R.Store(self.base)
        R.pkg("model").EVENTS = os.path.join(self.books, LED, "events.jsonl")
        self.w = self.fresh()
        for a, seat in ((("file", ITEM, "--for", SEAT, "--title", "fixture"), SEAT), (("claim", ITEM), SEAT), (("start", ITEM), SEAT)):
            got = self.w.rimflow(*a, seat=seat)
            if got.returncode:
                raise RuntimeError("%s: %s" % (a, (got.stderr or got.stdout)[-400:]))
        self.w.flush()
        self.put("src/x.py", "x = 2\n")
        sh(self.books, "git", "add", "src/x.py")
        sh(self.books, "git", "commit", "-qm", "%s: the work" % ITEM)
        sh(self.books, "git", "push", "-q", "origin", "HEAD:main")
        self.sha = sh(self.books, "git", "rev-parse", "HEAD")
        self.to_checking()
        self.now0 = self.now
        shutil.copytree(self.base, self.snap, symlinks=True)

    def put(self, rel, text):
        p = os.path.join(self.books, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)

    def fresh(self):
        """A new process's Effects: nothing in memory from the one before."""
        return CrashWorld(self.s, self.r)

    def st(self):
        return self.s.load(ITEM)

    def tick(self, w=None):
        """A timer firing."""
        self.now += 120
        return R.tick(self.s, w or self.fresh(), self.r, self.now)

    def to_checking(self):
        w = SL.FakeWorld(n=0)       # to the check on the fakes alone; the real ledger above already says doing
        w.items = {ITEM: "proposed"}
        for _ in range(12):
            st = self.st()
            if st and st["status"] == "running":
                break
            self.now += 120
            R.tick(self.s, w, self.r, self.now)
        st = self.st()
        if not st or st["status"] != "running":
            raise RuntimeError("never ran: %s; launches=%s" % (st and st["status"], w.launches))
        R.contract(self.s, ITEM, st["gen"], "proof", live="once: test")
        self.gen, self.now_finish = st["gen"], self.now
        shutil.copytree(self.base, self.snap_finish, symlinks=True)
        self.do_finish()
        w.up[st["run"]["unit"]] = False
        for _ in range(4):
            self.now += 120
            R.tick(self.s, w, self.r, self.now)
            if self.st()["status"] == "checking":
                return
        raise RuntimeError("never reached its check: %s" % self.st()["status"])

    def do_finish(self):
        R.finish(self.s, ITEM, self.gen, self.sha, "evidence", root=self.books)

    def restore(self, snap=None, now=None):
        shutil.rmtree(self.base)
        shutil.copytree(snap or self.snap, self.base, symlinks=True)
        self.s = R.Store(self.base)
        self.now = now or self.now0
        sh(self.origin, "git", "update-ref", "refs/heads/main", self.origin_head)

    def done(self):
        shutil.rmtree(self.d, ignore_errors=True)

    # ---- one check's ending
    def give_verdict(self, word):
        st = self.st()
        chk = st["check"]
        reasons = "ran it" + (SL.STRONG_WEAK if word == "WEAK" else "")
        R.verdict(self.s, ITEM, chk["nonce"], word, reasons, defects=["ran it"] if word == "FAIL" else None,
                  unreached=["the box cannot see it"] if word == "UNMEASURED" else None)

    def carry(self, word, ticks=4):
        """What a checker and the timer do: the verdict, then ticks to the end."""
        self.give_verdict(word)
        for _ in range(ticks):
            self.tick()


# ---------------------------------------------------------------- the four records

def reading(rig):
    model = R.pkg("model")
    model.EVENTS = os.path.join(rig.books, LED, "events.jsonl")
    evs = [e for e in model.read() if e.get("id") == ITEM]
    st = rig.st()
    journal = []
    with open(rig.s.p("journal.jsonl"), encoding="utf-8") as f:
        for ln in f:
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if rec.get("item") == ITEM:
                journal.append(rec)
    marks = R.evidence.read(rig.s.dir, ITEM, rig.sha, strict=False)
    return {
        "status": st["status"],
        "st": st,
        "ledger": model.replay(model.read()).items[ITEM].state,
        "closes": [e for e in evs if e.get("event") == "close"],
        "pass_runs": [e for e in evs if e.get("event") == "verify" and e.get("result") == "pass"],
        "fail_runs": [e for e in evs if e.get("event") == "verify" and e.get("result") == "fail"],
        "notes": [e for e in evs if e.get("event") == "note"],
        "journal": journal,
        "attempts": rig.s.attempts(ITEM),
        "evidence": marks,
        "origin": sh(rig.books, "git", "show", "origin/main:" + LED + "events/%s.jsonl" % SEAT) if on_origin(rig, LED + "events/%s.jsonl" % SEAT) else "",
        "origin_runner": sh(rig.books, "git", "show", "origin/main:" + LED + "events/RUNNER.jsonl") if on_origin(rig, LED + "events/RUNNER.jsonl") else "",
        "dirty": sh(rig.books, "git", "status", "--porcelain", "--", "infrastructure/state"),
        "ahead": sh(rig.books, "git", "rev-list", "--count", "origin/main..HEAD"),
    }


def on_origin(rig, rel):
    return subprocess.run(["git", "cat-file", "-e", "origin/main:" + rel], cwd=rig.books, capture_output=True).returncode == 0


def marker_entries(rec):
    """The evidence record's Marker entries, however evidence.read shapes them."""
    if not rec:
        return []
    rows = rec.get("entries") if isinstance(rec, dict) else rec
    return [e for e in (rows or []) if isinstance(e, dict) and e.get("kind", e.get("type")) == "marker"]


def judge_common(case, got, rig):
    out = [not got["dirty"] or ok(False, "%s: books left dirty after recovery: %s" % (case, got["dirty"][:200])),
           got["ahead"] == "0" or ok(False, "%s: the books hold %s commits origin does not" % (case, got["ahead"]))]
    return all(out)


def judge_pass(case, rig):
    g = reading(rig)
    judge_common(case, g, rig)
    ok(g["status"] == "done", "%s: store says %s" % (case, g["status"]))
    ok(g["ledger"] == "done", "%s: ledger says %s" % (case, g["ledger"]))
    ok(len(g["closes"]) == 1, "%s: %d close events" % (case, len(g["closes"])))
    ok(g["closes"] and g["closes"][0].get("sha") == rig.sha, "%s: the close names the wrong sha" % case)
    ok(len(g["pass_runs"]) == 1, "%s: %d blind PASS runs on the ledger" % (case, len(g["pass_runs"])))
    ok(rig.sha[:12] in sh(rig.books, "git", "log", "origin/main", "--format=%H", "-n", "9") or
       sh(rig.books, "git", "merge-base", "--is-ancestor", rig.sha, "origin/main") == "", "%s: the work left origin" % case)
    ok('"close"' in g["origin"], "%s: the close never reached origin" % case)
    ok(on_origin(rig, CLOSED) and not on_origin(rig, PROSE), "%s: the prose move never landed on origin" % case)
    ok(len([j for j in g["journal"] if j.get("do") == "done"]) == 1,
       "%s: %d `done` journal rows" % (case, len([j for j in g["journal"] if j.get("do") == "done"])))
    ok(len([a for a in g["attempts"] if a.get("end") == "done"]) == 1,
       "%s: %d `done` attempts" % (case, len([a for a in g["attempts"] if a.get("end") == "done"])))
    ok(len(marker_entries(g["evidence"])) == 1, "%s: %d Marker entries in the evidence record" % (case, len(marker_entries(g["evidence"]))))
    ok((g["st"].get("check") or {}).get("verdict") == "PASS", "%s: the store's verdict is %s" % (case, (g["st"].get("check") or {}).get("verdict")))


def once(case, g, end):
    n = len([a for a in g["attempts"] if a.get("end") == end])
    ok(n == 1, "%s: %d `%s` attempts" % (case, n, end))


def judge_unmeasured(case, rig):
    g = reading(rig)
    judge_common(case, g, rig)
    ok(g["status"] not in ("done", "closing", "checking"), "%s: store says %s after an UNMEASURED" % (case, g["status"]))
    ok(not g["closes"], "%s: a close event on an UNMEASURED" % case)
    ok(g["st"]["returns"] == 0, "%s: returns=%s: an UNMEASURED sends no work back" % (case, g["st"]["returns"]))
    once(case, g, "unmeasured")
    ok(len(marker_entries(g["evidence"])) == 1, "%s: %d Marker entries in the evidence record" % (case, len(marker_entries(g["evidence"]))))
    lines = [n for n in g["notes"] if "UNMEASURED" in str(n.get("text"))]
    ok(len(lines) == 1, "%s: %d UNMEASURED notes on the ledger" % (case, len(lines)))
    ok(not g["st"].get("ledger_note_owed"), "%s: the note is still owed" % case)


def judge_fail(case, rig):
    g = reading(rig)
    judge_common(case, g, rig)
    ok(g["status"] not in ("done", "closing", "checking", "candidate"), "%s: store says %s after a FAIL" % (case, g["status"]))
    ok(g["ledger"] != "done", "%s: the ledger closed a FAILed item" % case)
    ok(not g["closes"], "%s: a close event on a FAIL" % case)
    ok(len(g["fail_runs"]) == 1, "%s: %d blind FAIL runs on the ledger" % (case, len(g["fail_runs"])))
    ok("fail" in g["origin_runner"], "%s: the FAIL never reached origin" % case)
    ok(not g["st"].get("marker_fail_owed"), "%s: the FAIL is still owed" % case)
    ok(g["st"]["returns"] == 1, "%s: returns=%s after one FAIL" % (case, g["st"]["returns"]))
    rows = [a for a in g["attempts"] if a.get("end") == "blind_fail"]     # a structured FAIL: its gate row, then its blame row
    ok(len([a for a in rows if a.get("gated")]) == 1 and len([a for a in rows if not a.get("gated")]) == 1,
       "%s: `blind_fail` attempts: %d gated, %d attributed" % (case, len([a for a in rows if a.get("gated")]),
                                                              len([a for a in rows if not a.get("gated")])))
    ok(len(marker_entries(g["evidence"])) == 1, "%s: %d Marker entries in the evidence record" % (case, len(marker_entries(g["evidence"]))))


def judge_weak(case, rig):
    g = reading(rig)
    judge_common(case, g, rig)
    ok(g["status"] not in ("done", "closing", "checking", "candidate"), "%s: store says %s after a WEAK" % (case, g["status"]))
    ok(not g["closes"], "%s: a close event on a WEAK" % case)
    ok(g["st"]["returns"] == 1, "%s: returns=%s after one WEAK" % (case, g["st"]["returns"]))
    once(case, g, "proof_weak")
    ok(len(marker_entries(g["evidence"])) == 1, "%s: %d Marker entries in the evidence record" % (case, len(marker_entries(g["evidence"]))))
    weak = [n for n in g["notes"] if "WEAK" in str(n.get("text"))]
    ok(len(weak) == 1, "%s: %d WEAK notes on the ledger" % (case, len(weak)))


JUDGE = {"PASS": judge_pass, "FAIL": judge_fail, "WEAK": judge_weak, "UNMEASURED": judge_unmeasured}


# ---------------------------------------------------------------- a kill, and what follows it

def child(rig, word, armed, trace, work=None):
    """Fork: the child carries the check to its end (or does `work`) and dies at `armed`. -> how it ended (the signal number, or 0)."""
    global ARMED, TRACE_PATH
    sys.stdout.flush()
    sys.stderr.flush()
    pid = os.fork()
    if pid == 0:
        try:
            ARMED, TRACE_PATH = armed, trace
            COUNT[0] = 0
            arm_store()
            if armed == "cli:event-before-prose":
                open(rig.armed_cli, "w").close()
            if armed == "publish:commit-before-push":
                open(rig.armed_publish, "w").close()
            work() if work else rig.carry(word)
            os._exit(0)
        except BaseException as e:      # noqa: BLE001  a child that raises is no kill: the parent reports it
            print("child raised %s: %s" % (type(e).__name__, str(e)[:400]), file=sys.stderr)
            os._exit(3)
    _, status = os.waitpid(pid, 0)
    return os.WTERMSIG(status) if os.WIFSIGNALED(status) else -os.WEXITSTATUS(status)


def disarm(rig):
    for p in (rig.armed_cli, rig.armed_publish):
        if os.path.exists(p):
            os.unlink(p)


def recover(rig, word, ticks=8):
    """The next timer firings, each a fresh process's Effects. A check whose verdict died with the kill gets a fresh
    checker's, as the belt would launch one. A verdict already in the store is never given twice."""
    for _ in range(ticks):
        st = rig.st()
        chk = st.get("check") or {}
        if st["status"] == "checking" and chk.get("verdict") is None:
            rig.give_verdict(word)
        rig.tick()


def blame_if_waiting(rig):
    """A structured FAIL waits for its diagnosis (relentless_attrib); the seat answers PRODUCT, as in selftest_relentless."""
    if (rig.st().get("wait") or {}).get("kind") == "attribution":
        SL.blame_product(rig, ITEM)


def landed_there(rig, word, armed):
    """A named kill is inside a write: read the wreck, or a kill that missed its moment would pass as recovered."""
    if armed == "cli:event-before-prose":
        g = reading(rig)
        ok(len(g["closes"]) == 1 and os.path.exists(os.path.join(rig.books, PROSE)),
           "%s %s: wanted a close event and unmoved prose: %d closes" % (word, armed, len(g["closes"])))
    elif armed == "publish:commit-before-push":
        ok(sh(rig.books, "git", "rev-list", "--count", "origin/main..HEAD") == "1", "%s %s: no commit waiting to be pushed" % (word, armed))
    elif armed == "store:tmp-before-rename":
        d = rig.s.item_dir(ITEM)
        ok(any(".tmp." in f for f in os.listdir(d)) and rig.st()["status"] == "checking",
           "%s %s: wanted a temp file and the old state, got %s" % (word, armed, rig.st()["status"]))


def origin_moved(rig):
    """Another seat lands while the belt is down, so the recovering tick starts behind origin with its wreck in the tree."""
    other = os.path.join(rig.d, "other")
    shutil.rmtree(other, ignore_errors=True)
    sh(rig.d, "git", "clone", "-q", rig.origin, other)
    with open(os.path.join(other, "another_seat.txt"), "w") as f:
        f.write("landed during the outage\n")
    sh(other, "git", "add", "another_seat.txt")
    sh(other, "git", "-c", "user.name=o", "-c", "user.email=o@o", "commit", "-qm", "another seat")
    sh(other, "git", "push", "-q", "origin", "HEAD:main")


def run_case(rig, word, armed, name, moved=False):
    rig.restore()
    rc = child(rig, word, armed, None)
    disarm(rig)
    ok(rc == signal.SIGKILL, "%s %s: the child was not killed there (ended %s)" % (word, name, rc))
    landed_there(rig, word, armed)
    if moved:
        origin_moved(rig)
    recover(rig, word)
    blame_if_waiting(rig)
    rig.tick()
    JUDGE[word]("%s kill after %s" % (word, name), rig)


NAMED = {"PASS": ("cli:event-before-prose", "publish:commit-before-push", "store:tmp-before-rename"),
         "FAIL": ("publish:commit-before-push",),
         "WEAK": ("publish:commit-before-push",),
         "UNMEASURED": ("publish:commit-before-push",)}


def run_ending(rig, word, want):
    rig.restore()
    trace = os.path.join(rig.d, "trace_%s.txt" % word)
    if os.path.exists(trace):
        os.unlink(trace)
    rc = child(rig, word, None, trace)
    if not ok(rc == 0, "%s: the clean run ended %s" % (word, rc)):
        return []
    with open(trace) as f:
        names = f.read().split()
    blame_if_waiting(rig)
    rig.tick()
    JUDGE[word]("%s clean run" % word, rig)
    if want is not None:
        ok(names == list(want), "%s: the close path's writes changed: say what a kill does at each\n  now  %s\n  list %s"
           % (word, names, list(want)))
    for i, nm in enumerate(names):
        run_case(rig, word, i, "%d:%s" % (i, nm))
    for nm in NAMED[word]:
        run_case(rig, word, nm, nm)
    if word == "PASS":      # the two wrecks a behind-origin level could trip on: a dirty shard, and a half-moved prose pair
        run_case(rig, word, names.index("ledger:close"), "ledger:close, origin moved meanwhile", moved=True)
        run_case(rig, word, "cli:event-before-prose", "cli:event-before-prose, origin moved meanwhile", moved=True)
    return names


def run_control(rig):
    """The judge can see: a clean close with one defect planted per record must read red, or a green above means nothing."""
    plants = {
        "a second blind PASS": lambda: rig.fresh().rimflow("verify", ITEM, "--sha", rig.sha, "--result", "pass", "--level", "L0",
                                                           "--config", R.pkg("model").MARKER_CONFIG, "--evidence", "planted", seat="RUNNER"),
        "a lost done row": lambda: lost_done_row(rig),
        "a doubled done attempt": lambda: rig.s.attempt(ITEM, {"at": "planted", "end": "done", "sha": rig.sha}),
        "a store that never finished": lambda: rig.s.save(dict(rig.st(), status="closing")),
        "prose left in the live glob": lambda: rig.put(PROSE, "planted\n"),
    }
    global FAILS
    for what, plant in plants.items():
        rig.restore()
        rig.carry("PASS")
        rig.tick()
        plant()
        kept, FAILS = FAILS, []
        print_kept, sys.stdout = sys.stdout, open(os.devnull, "w")
        try:
            judge_pass("control", rig)
        finally:
            sys.stdout.close()
            sys.stdout = print_kept
            caught, FAILS = FAILS, kept
        ok(caught, "control: %s went unseen: the judge is blind" % what)
    return len(plants)


def lost_done_row(rig):
    with open(rig.s.p("journal.jsonl"), encoding="utf-8") as f:
        rows = [ln for ln in f if '"do": "done"' not in ln]
    with open(rig.s.p("journal.jsonl"), "w", encoding="utf-8") as f:
        f.writelines(rows)


def run_finish(rig):
    """The landing's receipt: the worker's `finish`, killed after each write. The work is on origin before it runs."""
    trace = os.path.join(rig.d, "trace_finish.txt")
    rig.restore(rig.snap_finish, rig.now_finish)
    if not ok(child(rig, None, None, trace, rig.do_finish) == 0, "finish: the clean run did not end"):
        return []
    with open(trace) as f:
        names = f.read().split()
    ok(names == list(FINISH), "finish: the writes changed: say what a kill does at each\n  now  %s\n  list %s" % (names, list(FINISH)))
    for i, nm in enumerate(names):
        rig.restore(rig.snap_finish, rig.now_finish)
        case = "finish kill after %d:%s" % (i, nm)
        ok(child(rig, None, i, None, rig.do_finish) == signal.SIGKILL, "%s: the child was not killed there" % case)
        for _ in range(4):
            if rig.st()["status"] == "checking":
                break
            rig.tick()
        st = rig.st()
        ok(st["status"] == "checking", "%s: store says %s" % (case, st["status"]))
        ok((st.get("candidate") or {}).get("sha") == rig.sha, "%s: the candidate is %s" % (case, st.get("candidate")))
        n = len([a for a in rig.s.attempts(ITEM) if a.get("end") == "finish"])
        ok(n == 1, "%s: %d `finish` attempts" % (case, n))
    return names


FINISH = ("receipt", "attempt:finish", "state:candidate")
BOUNDARIES = {
    "PASS": ("state:checking", "shadow", "evidence:marker", "state:checking", "state:closing", "state:closing", "ledger:verify",
             "ledger:close", "attempt:done", "journal:done", "state:done", "land"),
    "FAIL": ("state:checking", "shadow", "evidence:marker", "state:checking", "journal:cause_routed", "attempt:blind_fail",
             "state:stopping", "ledger:verify", "state:stopping", "state:held", "land", "state:held"),
    "WEAK": ("state:checking", "shadow", "evidence:marker", "state:checking", "attempt:proof_weak", "state:stopping", "ledger:note",
             "state:stopping", "state:queued", "land"),
    "UNMEASURED": ("state:checking", "shadow", "evidence:marker", "state:checking", "attempt:unmeasured", "state:blocked",
                   "ledger:note", "state:blocked", "land", "state:blocked", "journal:reach_ticket", "state:blocked", "journal:blocked"),
}


def main():
    words = ["PASS", "FAIL", "WEAK", "UNMEASURED"]
    if "--ending" in sys.argv:
        words = [sys.argv[sys.argv.index("--ending") + 1]]
    rig = Rig()
    rig.origin_head = sh(rig.origin, "git", "rev-parse", "refs/heads/main")
    try:
        if len(words) > 1:
            print("finish: %s" % " ".join(run_finish(rig)))
            print("control: %d planted defects" % run_control(rig))
        for word in words:
            names = run_ending(rig, word, BOUNDARIES[word])
            print("%s: %d boundaries: %s" % (word, len(names), " ".join(names)))
    finally:
        if "--keep" in sys.argv:
            print("kept " + rig.d)
        else:
            rig.done()
    print("FIXTURE_VERDICT: %s" % ("FAIL" if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
