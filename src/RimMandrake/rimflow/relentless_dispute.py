"""relentless_dispute.py -- the live builder <-> Setter dispute loop (RELENTLESS_BUILD_LIVE_DISPUTE_LOOP; owner-ordered
pipeline redesign 2026-11-06, redesign_final.md §3.3 and G11/G12/G13, §5 row 08).

Owner, 2026-11-05 ~23:35 PST: "The test builder should make a test, then the solution builder makes its solution, then
immediately the test builder responds to any challenges, then the solution builder immediately responds back... and the
third party arbitration if needed. That's it, in rapid succession, with no 'filing tickets and nobody's working on this
right now' moments."

One loop inside the item's run. No ledger item, no queue, no wait verb, no sleep between turns:

  1. builder: `relentless.py challenge --item ID --gen N --clause c3[,c4] --claim wrong|unbindable|unfair --evidence PATH`
     -> a durable job (<store>/exams/<ID>/disputes/<job>.json) and a detached worker unit (`relentless_dispute.py work ID
     JOB`, the supervisor's books code), so an answer outlives the builder's 540 s tool ceiling.
  2. worker: takes the Setter session's lock (two challenges are answered one at a time, never interleaved in one
     session), RESUMES the Setter's own session (`claude -p --resume`, relentless_exam.run_setter, in a box re-made at the
     path the session was started in, read from its transcript's cwd) with the challenge. The Setter `stand`s or `amend`s
     (rewrites its exam); an amend is re-VALIDATED at once (relentless_exam.validate, red on base / under break) and only
     then frozen with a new exam_hash. An amend that fails VALIDATE, a session that cannot be resumed, or a Setter that
     writes no answer twice goes straight to the arbiter.
  3. the answer prints on the builder's stdout if it lands within `in_call_s`; else at its next `boxrun` or
     `challenge --status` (deliver()). The builder never blocks past its call.
  4. builder: `challenge --reply JOB "..."` ONCE (a second reply is refused).
  5. arbiter: a fresh instance (the Marker's Judge-mode agent, never builder/Setter of the item; recorded in
     excluded.json so it never marks the item) rules setter | builder | environment | bar. Final for the run.

Bounds: one challenge per clause per generation; a challenge that would put more than `max_clauses` clauses of one
generation under dispute sends the WHOLE exam back to the Setter once (kind `malformed`), not a refusal (G11).
Who-was-right is a by-product row, <store>/items/<ID>/runs/<gen>/dispute.jsonl: {job, clause, claim, setter_answer,
builder_reply, arbiter, winner, at}. Nothing here files a ledger item.

Also the arbiter of WP-03's R4: an exam whose second VALIDATE refusal left it `arbiter_owed` is ruled
setter | environment | bar by arbitrate_exam() (relentless_exam.py's unit calls it).

SHADOW (mode in relentless_dispute.json): the loop runs and its rows are kept; nothing gates a close, a `builder` or `bar`
ruling changes no item state (WP-03's posture, until the exam gates in WP-09b).
"""
import argparse
import contextlib
import fcntl
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import relentless_exam as E  # noqa: E402

CONFIG = os.path.join(HERE, "relentless_dispute.json")
CLAIMS = ("wrong", "unbindable", "unfair")
WINNERS = ("setter", "builder", "environment", "bar")
EXAM_WINNERS = ("setter", "environment", "bar")
ANSWERED = ("answered", "settled", "ruled")          # a job here has reached an answer or a ruling
OPEN = ("asked", "answering", "replied", "arbitrating")
POLL_S = 0.5                                         # the in-call answer wait: a file read per tick while work is running


def config(path=None):
    try:
        with open(path or os.environ.get("RELENTLESS_DISPUTE_CONFIG") or CONFIG, encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, dict) else {"mode": "off"}
    except (OSError, ValueError):
        return {"mode": "off"}


def now_iso():
    return E.iso(time.time())


# ------------------------------------------------------------------------------------------------------------- paths
def jobs_dir(store, item):
    return os.path.join(E.item_dir(store, item), "disputes")


JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")   # what ask() mints: no separators, no dots, no path parts


def job_id(job):
    """A job id names one file in the item's own disputes dir: anything else (../../B/disputes/J, an absolute path) is
    refused before it reaches a path. -> the id."""
    if not isinstance(job, str) or not JOB_ID.match(job):
        raise ValueError("not a dispute job id: %r (ids look like d20261106T120000-ab12cd)" % (job,))
    return job


def job_path(store, item, job):
    return os.path.join(jobs_dir(store, item), job_id(job) + ".json")


def rows_path(store, item, gen):
    return store.p("items", item, "runs", str(gen), "dispute.jsonl")


@contextlib.contextmanager
def _flock(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def jobs_lock(store, item):
    """Short read-modify-write lock over the item's job files (the builder's verb and the worker both write them)."""
    return _flock(os.path.join(jobs_dir(store, item), ".lock"))


@contextlib.contextmanager
def _claim(path):
    """An exclusive, NON-blocking claim: yields True to the one process holding it, False to every other. The kernel
    drops it when its holder dies, so a claim left by a killed worker is free again (that is what makes a retry safe)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def live_gen(store, item):
    with store.lock():
        return (store.load(item) or {}).get("gen")


def session_lock(store, item):
    """The Setter session's lock: held for a whole answer turn, so two challenges never interleave in one session."""
    return _flock(os.path.join(E.item_dir(store, item), "setter.lock"))


def load(store, item, job):
    return E._read(job_path(store, item, job))


def jobs(store, item):
    d = jobs_dir(store, item)
    out = [E._read(p) for p in sorted(glob.glob(os.path.join(d, "*.json")))] if os.path.isdir(d) else []
    return sorted([j for j in out if isinstance(j, dict) and j.get("id")], key=lambda j: (j.get("asked_at", ""), j.get("id", "")))


def _apply(j, **kw):
    """Mutate a job held under jobs_lock (no lock of its own: flock is per open file, so nesting would deadlock)."""
    hist = j.setdefault("history", [])
    if "state" in kw and kw["state"] != j.get("state"):
        hist.append({"state": kw["state"], "at": now_iso()})
    j.update(kw)
    return j


def update(store, item, job, **kw):
    with jobs_lock(store, item):
        j = _apply(load(store, item, job) or {}, **kw)
        E._write(job_path(store, item, job), j)
        return j


def row(store, j, winner, arbiter=None, final=True):
    """The who-was-right row (by-product, not a filing). A Setter's stand writes a provisional `setter` row (final
    false): it is the outcome unless the builder replies, and then the arbiter's row is final."""
    E._append(rows_path(store, j["item"], j["gen"]), {
        "job": j["id"], "clause": j["clauses"], "claim": j["claim"], "kind": j.get("kind", "clause"),
        "setter_answer": (j.get("answer") or {}).get("verdict"), "builder_reply": bool(j.get("reply")),
        "arbiter": (arbiter or {}).get("session"), "winner": winner, "final": final, "at": now_iso()})


def exam_of(store, item):
    recover_publish(store, item)
    return E._read(os.path.join(E.item_dir(store, item), "exam.json"))


# ------------------------------------------------------------------------------------------------- the builder's verb
def unit_name(item, job):
    return "rm-relentless-dispute-" + hashlib.sha1(("%s/%s" % (item, job)).encode("utf-8")).hexdigest()[:10]


def kick(store, item, job, cfg=None, runner=subprocess.run):
    """Start the job's worker, detached (systemd-run --user), from the supervisor's books code. -> None or why not."""
    cfg = config() if cfg is None else cfg
    books = os.path.join(store.root, "books", "src", "RimMandrake", "rimflow", "relentless_dispute.py")
    tool = books if os.path.exists(books) else os.path.abspath(__file__)
    d = jobs_dir(store, item)
    os.makedirs(d, exist_ok=True)
    argv = ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit_name(item, job),
            "-p", "StandardOutput=append:" + os.path.join(d, job + ".out"),
            "-p", "StandardError=append:" + os.path.join(d, job + ".out"),
            "-p", "RuntimeMaxSec=%d" % int(cfg.get("unit_max_s", 3600)), "--working-directory", os.path.dirname(tool),
            "--setenv", "RELENTLESS_ROOT=" + store.root, "--setenv", "PATH=" + os.environ.get("PATH", "/usr/bin:/bin"),
            "--setenv", "PYTHONDONTWRITEBYTECODE=1", "--", sys.executable, tool, "work", item, job]
    try:
        r = runner(argv, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return "%s: %s" % (type(e).__name__, e)
    return ("systemd-run exit %d: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or ""))[-200:])) if r.returncode else None


def unit_alive(item, job, runner=subprocess.run):
    try:
        r = runner(["systemctl", "--user", "is-active", "--quiet", unit_name(item, job)], capture_output=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def wait(store, item, job, states, secs, clock=time.monotonic, nap=time.sleep):
    """Block the builder's own call until the job reaches `states` or `secs` pass. -> the job."""
    end = clock() + max(0.0, float(secs))
    while True:
        j = load(store, item, job) or {}
        if j.get("state") in states or clock() >= end:
            return j
        nap(POLL_S)


def _gen_check(store, item, gen):
    with store.lock():
        st = store.load(item)
    if not st:
        raise ValueError("%s is not enrolled" % item)
    if gen is None or st.get("gen") != gen:
        raise ValueError("stale generation: %s is at gen %s, you are gen %s; a challenge belongs to the item's live run"
                         % (item, st.get("gen"), gen))
    return st


def ask(store, item, gen, clauses, claim, evidence, text="", cfg=None, kicker=None, waiter=wait, say=print):
    """`challenge`: open a job, start its worker, wait in-call for the answer. -> the job."""
    cfg = config() if cfg is None else cfg
    if cfg.get("mode", "off") == "off":
        raise ValueError("the dispute loop is off (relentless_dispute.json mode)")
    if claim not in CLAIMS:
        raise ValueError("--claim must be one of %s" % "|".join(CLAIMS))
    clauses = [c.strip() for c in (clauses if isinstance(clauses, list) else str(clauses or "").split(",")) if c.strip()]
    if not clauses:
        raise ValueError("--clause names the exam clause(s) challenged, e.g. c3 or c3,c4")
    _gen_check(store, item, gen)
    exam = exam_of(store, item)
    if not exam:
        raise ValueError("%s has no validated exam to challenge" % item)
    have = {c.get("id") for c in exam.get("clauses") or []}
    missing = [c for c in clauses if c not in have]
    if missing:
        raise ValueError("no such clause in the exam: %s (it has %s)" % (",".join(missing), ",".join(sorted(have))))
    try:
        with open(evidence, encoding="utf-8", errors="replace") as f:
            ev_text = f.read(8000)
    except (OSError, TypeError):
        raise ValueError("--evidence must be a readable file: the box output or diff the claim rests on")
    with jobs_lock(store, item):
        mine = [j for j in jobs(store, item) if j.get("gen") == gen]
        taken = {c for j in mine for c in j.get("clauses") or []}
        dup = [c for c in clauses if c in taken]
        if dup:
            raise ValueError("already challenged this run: %s (one challenge per clause; reply to its job instead)" % ",".join(dup))
        kind = "clause"
        if len(taken | set(clauses)) > int(cfg.get("max_clauses", 3)):
            if any(j.get("kind") == "malformed" for j in mine):
                raise ValueError("the whole exam already went back to the Setter once this run")
            kind = "malformed"
        job = "d%s-%s" % (time.strftime("%Y%m%dT%H%M%S", time.gmtime()), uuid.uuid4().hex[:6])
        j = {"id": job, "item": item, "gen": gen, "clauses": clauses, "claim": claim, "kind": kind, "text": (text or "")[:4000],
             "evidence": os.path.abspath(evidence), "evidence_text": ev_text, "exam_hash": exam.get("exam_hash"),
             "state": "asked", "asked_at": now_iso(), "attempts": 0, "arb_attempts": 0, "delivered": [],
             "history": [{"state": "asked", "at": now_iso()}]}
        E._write(job_path(store, item, job), j)
    why = (kicker or (lambda s, i, k: kick(s, i, k, cfg)))(store, item, job)
    if why:
        update(store, item, job, kick_error=why)
        say("relentless challenge: the worker did not start (%s); the next boxrun / challenge --status restarts it" % why)
    j = waiter(store, item, job, ANSWERED, cfg.get("in_call_s", 420))
    _say_job(store, j, say)
    return j


def reply(store, item, gen, job, text, cfg=None, kicker=None, waiter=wait, say=print):
    """`challenge --reply JOB`: the builder's one answer back; then the arbiter. -> the job."""
    cfg = config() if cfg is None else cfg
    if not (text or "").strip():
        raise ValueError("--reply needs the builder's answer to the Setter")
    _gen_check(store, item, gen)
    with jobs_lock(store, item):
        j = load(store, item, job)
        if not j or j.get("item") != item or j.get("id") != job:
            raise ValueError("no dispute job %s on %s" % (job, item))
        if j.get("gen") != gen:
            raise ValueError("job %s belongs to gen %s" % (job, j.get("gen")))
        if j.get("reply"):
            raise ValueError("job %s already has your reply: one reply, then the arbiter rules" % job)
        if j.get("state") != "answered":
            raise ValueError("job %s is %s: a reply answers a Setter's stand (nothing to reply to)" % (job, j.get("state")))
        j["reply"] = {"text": text[:4000], "at": now_iso()}
        j["state"] = "replied"
        j["history"].append({"state": "replied", "at": now_iso()})
        E._write(job_path(store, item, job), j)
    why = (kicker or (lambda s, i, k: kick(s, i, k, cfg)))(store, item, job)
    if why:
        update(store, item, job, kick_error=why)
    j = waiter(store, item, job, ("ruled",), cfg.get("in_call_s", 420))
    _say_job(store, j, say)
    return j


def _say_job(store, j, say):
    st = j.get("state")
    a, r = j.get("answer") or {}, j.get("ruling") or {}
    if st in ("answered", "settled"):
        say("relentless challenge %s: Setter %s on %s: %s" % (j["id"], a.get("verdict"), ",".join(j["clauses"]), a.get("why", "")))
        if st == "answered":
            say("  disagree? `relentless.py challenge --item %s --gen %s --reply %s \"...\"` (once; then the arbiter rules)"
                % (j["item"], j["gen"], j["id"]))
        else:
            say("  the exam is amended and re-VALIDATED (exam_hash %s)" % str(a.get("exam_hash"))[:12])
    elif st == "ruled":
        say("relentless challenge %s: arbiter ruled %s: %s" % (j["id"], r.get("winner"), r.get("why", "")))
    else:
        say("relentless challenge %s: pending (%s): the answer prints at your next `boxrun` or `challenge --status`; keep "
            "working on other clauses" % (j["id"], st))
    _mark_delivered(store, j)


def _mark_delivered(store, j):
    st = j.get("state")
    if st in ANSWERED and st not in (j.get("delivered") or []):
        update(store, j["item"], j["id"], delivered=list(j.get("delivered") or []) + [st])


def deliver(store, item, gen=None, say=print, kicker=None, alive=unit_alive, cfg=None):
    """Called by the builder's `boxrun` and `challenge --status`: print every answer/ruling not yet shown, and restart a
    job whose worker died (a killed answerer: re-kicked up to answer_tries, then the arbiter). -> jobs printed."""
    cfg = config() if cfg is None else cfg
    shown = []
    for j in jobs(store, item):
        if gen is not None and j.get("gen") != gen:
            continue
        if j.get("state") in OPEN and not alive(item, j["id"]):
            _restart(store, j, cfg, kicker)
            j = load(store, item, j["id"]) or j
        if j.get("state") in ANSWERED and j["state"] not in (j.get("delivered") or []):
            _say_job(store, j, say)
            shown.append(j["id"])
    return shown


def _restart(store, j, cfg, kicker):
    """Recover a job whose worker is gone. Every decision is taken on the job as it stands NOW, re-read under jobs_lock:
    the copy deliver() listed may predate the worker's last write (answering -> answered, then the unit exits)."""
    item, job = j["item"], j["id"]
    voided = None
    with jobs_lock(store, item):
        cur = load(store, item, job) or {}
        st = cur.get("state")
        if st not in OPEN:
            return                           # it reached an answer or a ruling since deliver() looked: nothing to recover
        if st in ("asked", "answering") and int(cur.get("attempts", 0)) >= int(cfg.get("answer_tries", 2)):
            _apply(cur, state="replied", route="worker_died",
                   answer={"verdict": "no_answer", "why": "the answering worker died %s times" % cur.get("attempts")})
        elif st in ("replied", "arbitrating") and int(cur.get("arb_attempts", 0)) >= int(cfg.get("arbiter_tries", 2)):
            voided = _void_ruling("the arbiter's worker died %s times" % cur.get("arb_attempts"))
            _apply(cur, state="ruled", ruling=voided)
        elif st == "answering":
            _apply(cur, state="asked")
        elif st == "arbitrating":
            _apply(cur, state="replied")
        E._write(job_path(store, item, job), cur)
    if voided:
        row(store, cur, "void", voided)
        return
    why = (kicker or (lambda s, i, k: kick(s, i, k, cfg)))(store, item, job)
    if why:
        update(store, item, job, kick_error=why)


# ----------------------------------------------------------------------------------------------------------- worker
def find_session(sid):
    """-> the cwd a Claude session was started in (its transcript's first `cwd`), or None when no transcript exists."""
    if not sid:
        return None
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    for p in glob.glob(os.path.join(base, "projects", "*", sid + ".jsonl")):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for n, line in enumerate(f):
                    if n > 200:
                        break
                    try:
                        cwd = json.loads(line).get("cwd")
                    except (ValueError, AttributeError):
                        continue
                    if cwd:
                        return cwd
        except OSError:
            continue
    return None


def box_nonce(cwd):
    """A box tree is <box_root>/<nonce>/tree: re-making the box with that nonce puts the resumed session at its own cwd."""
    if cwd and os.path.basename(cwd.rstrip("/")) == "tree":
        return os.path.basename(os.path.dirname(cwd.rstrip("/")))
    return None


ANSWER_BRIEF = """The builder of item {item} CHALLENGES your exam (claim: {claim}; clause(s): {clauses}).
{kindline}
Builder's words: {text}
Builder's evidence ({evidence}):
---
{ev}
---
Current exam (exam_hash {exam_hash}):
{exam}

Answer NOW, in this turn. Write {answer} as JSON: {{"verdict": "stand" | "amend", "why": "<the evidence you rest on>"}}.
- stand: the clause is right as written; say why, with what you ran.
- amend: rewrite {exam_json} (the whole exam, same format and rules as before; your test files under {files}). The
  supervisor re-VALIDATEs it at once (red on base / under break); it counts only if it passes.
End with one line: ANSWER WRITTEN."""

KIND_MALFORMED = ("More than {n} clauses of this exam are under challenge in one run: treat the WHOLE exam as malformed "
                  "and either stand on all of it or rewrite it (amend).")


def _write_answer_prompt(j, exam, answer, exam_json, files, n):
    view = {k: exam.get(k) for k in ("clauses", "maps", "no_code")}
    return ANSWER_BRIEF.format(item=j["item"], claim=j["claim"], clauses=",".join(j["clauses"]),
                               kindline=KIND_MALFORMED.format(n=n) if j.get("kind") == "malformed" else "",
                               text=j.get("text") or "(none)", evidence=j.get("evidence"), ev=j.get("evidence_text", "")[:6000],
                               exam_hash=exam.get("exam_hash"), exam=json.dumps(view, indent=1)[:12000], answer=answer,
                               exam_json=exam_json, files=files)


ARBITER_BRIEF = """You are the ARBITER of one dispute on RimMandrake pipeline item {item}. You are not its builder, its exam
Setter, nor its Marker, and you never will be. Your working directory is a read-only export of the repo at the item's
base sha {base}; the exam's own test files are under .exam/. You may run commands here.

The item, in its own words:
---
{text}
---
{body}

{choices}
Write {ruling} as JSON: {{"winner": "{winners}", "why": "<what you read and ran>"}}. Your ruling is final for this run.
End with one line: RULING WRITTEN."""

DISPUTE_CHOICES = ("Rule ONE of: setter (the exam is right; the builder must meet it), builder (the exam is wrong or "
                   "unbindable; the builder's reading stands), environment (the check cannot run where it must: reach the "
                   "box lacks), bar (both are wrong: the item text itself is the problem).")


def _dispute_body(j, exam):
    cl = [c for c in exam.get("clauses") or [] if c.get("id") in j["clauses"]] if exam else []
    a = j.get("answer") or {}
    return ("Clause(s) challenged ({kind}):\n{cl}\n\nBuilder's challenge (claim {claim}): {text}\nBuilder's evidence:\n---\n"
            "{ev}\n---\nSetter's answer: {av}: {aw}\nBuilder's reply: {reply}").format(
        kind=j.get("kind"), cl=json.dumps(cl, indent=1)[:8000], claim=j["claim"], text=j.get("text") or "(none)",
        ev=j.get("evidence_text", "")[:6000], av=a.get("verdict"), aw=a.get("why", "")[:3000],
        reply=(j.get("reply") or {}).get("text") or "(none: the Setter's answer could not stand on its own)")


class Deps:
    """The worker's seams: the Setter/arbiter runner (claude -p), the box, item text, session lookup."""
    def __init__(self, setter=None, boxer=None, text_of=None, find=None, rules=None):
        self.setter = setter or E.run_setter
        self.boxer = boxer or E.box_runner
        self.text_of = text_of or E._item_text
        self.find = find or find_session
        self.rules = rules


def _rules(deps):
    if deps.rules is None:
        import relentless
        deps.rules = relentless.rules()
    return deps.rules


def work(store, item, job, cfg=None, deps=None):
    """The worker unit's body: answer (under the Setter session lock), then the arbiter if owed. -> final state."""
    cfg = config() if cfg is None else cfg
    deps = deps or Deps()
    j = load(store, item, job)
    if not j or j.get("item") != item:
        return None
    if j.get("state") in ("asked", "answering"):
        with session_lock(store, item):
            j = load(store, item, job)
            if j.get("state") in ("asked", "answering") and not _stale(store, j):
                _answer(store, j, cfg, deps)
    if (load(store, item, job) or {}).get("state") in ("replied", "arbitrating"):
        with _claim(os.path.join(jobs_dir(store, item), job + ".arbiter.lock")) as mine:
            if not mine:                     # another worker is arbitrating this job right now: it owns the ruling
                return (load(store, item, job) or {}).get("state")
            j = load(store, item, job)       # re-read under the claim: the holder before us may have ruled already
            if j.get("state") in ("replied", "arbitrating") and not _stale(store, j):
                _arbitrate(store, j, cfg, deps)
    return (load(store, item, job) or {}).get("state")


def _stale(store, j):
    """An open job of a generation the item has left is void: its worker never answers, amends or arbitrates against
    the live generation's exam. Called only under the lock that owns the job's next step (the Setter session lock or
    the arbiter claim), so no live worker of this job can write after the void. -> True when it was voided."""
    if j.get("state") not in OPEN:
        return False
    g = live_gen(store, j["item"])
    if g == j.get("gen"):
        return False
    _void(store, j, "stale generation: the item is at gen %s, this challenge was gen %s" % (g, j.get("gen")), only_open=True)
    return True


def _answer(store, j, cfg, deps):
    item, job = j["item"], j["id"]
    j = update(store, item, job, state="answering", attempts=int(j.get("attempts", 0)) + 1, pid=os.getpid())
    exam = exam_of(store, item) or {}
    if exam.get("exam_hash") != j.get("exam_hash"):
        have = {x.get("id") for x in exam.get("clauses") or []}
        gone = [c for c in j["clauses"] if c not in have]
        left = [c for c in j["clauses"] if c in have]
        if gone and not left:   # an earlier challenge's amend removed every clause disputed here: nothing left
            update(store, item, job, state="settled", answer={"verdict": "superseded", "why": "clause(s) %s left the exam "
                   "in an amendment since this challenge" % ",".join(gone), "exam_hash": exam.get("exam_hash")})
            row(store, load(store, item, job), "builder")
            return
        if gone:                # some left, some stand: the job narrows to the clauses still in the exam
            j = update(store, item, job, clauses=left, clauses_gone=sorted(set(j.get("clauses_gone") or []) | set(gone)))
    sid = (exam.get("setter") or {}).get("session")
    cwd = deps.find(sid)
    if not cwd:
        update(store, item, job, state="replied", route="no_session",
               answer={"verdict": "no_session", "why": "the Setter session %s cannot be resumed (no transcript)" % sid})
        return
    d = E.item_dir(store, item)
    work_dir = os.path.join(d, "setter")
    exam_json, wfiles = os.path.join(work_dir, "exam.json"), os.path.join(work_dir, "files")
    os.makedirs(wfiles, exist_ok=True)
    answer_path = os.path.join(jobs_dir(store, item), job + ".answer.json")
    scfg = {"setter_agent": cfg.get("setter_agent", "rm-judge"), "setter_model": cfg.get("setter_model", "opus"),
            "setter_max_s": cfg.get("setter_max_s", 1500)}
    source, base = os.path.join(store.root, "books"), exam.get("base_sha")
    prompt = _write_answer_prompt(j, exam, answer_path, exam_json, wfiles, cfg.get("max_clauses", 3))
    ans = None
    sbox = deps.boxer(_rules(deps), source, base, os.path.join(d, "files"), item=item, nonce=box_nonce(cwd))
    try:
        tree = getattr(sbox[1], "tree", cwd)
        for turn in (1, 2):
            try:
                os.remove(answer_path)
            except OSError:
                pass
            deps.setter(tree, prompt, scfg, os.path.join(jobs_dir(store, item), job + ".setter.out"), resume=sid)
            ans = E._read(answer_path)
            if isinstance(ans, dict) and ans.get("verdict") in ("stand", "amend"):
                break
            ans = None
            prompt = "You wrote no valid answer at %s. Write it now: {\"verdict\": \"stand\"|\"amend\", \"why\": \"...\"}." % answer_path
    finally:
        sbox[2]()
    if not ans:
        update(store, item, job, state="replied", route="no_answer",
               answer={"verdict": "no_answer", "why": "the resumed Setter wrote no answer in two turns"})
        return
    ans = {"verdict": ans["verdict"], "why": str(ans.get("why", ""))[:3000], "at": now_iso()}
    if ans["verdict"] == "stand":         # the clauses it stood on, as defended: the arbiter judges THESE, even if a later
        defended = [c for c in exam.get("clauses") or [] if c.get("id") in j["clauses"]]   # amend moves the exam on
        row(store, update(store, item, job, state="answered", answer=dict(ans, exam_hash=exam.get("exam_hash"),
                                                                        clauses=defended)), "setter", final=False)
        return
    v = revalidate(store, item, exam, deps, gen=j.get("gen"))
    if v.get("stale"):
        _void(store, load(store, item, job), "stale generation: the item left gen %s before the amend could publish"
              % j.get("gen"))
        return
    if v["ok"]:
        update(store, item, job, state="settled", answer=dict(ans, exam_hash=v["exam_hash"], validated=True))
        row(store, load(store, item, job), "builder")
    else:
        update(store, item, job, state="replied", route="amend_refused",
               answer=dict(ans, verdict="amend_refused", refusals=v["refusals"][:12]))


def revalidate(store, item, old, deps, gen=None):
    """An amend counts only after VALIDATE: the Setter's rewritten exam, run in a fresh box at the base sha. A pass
    freezes it (old exam kept in exam_history.jsonl, files replaced, exam_hash moved) through publish(): journaled, so
    a crash at any step rolls forward to one consistent exam. With `gen`, it publishes only while the item is still at
    that generation (v["stale"] otherwise)."""
    d = E.item_dir(store, item)
    work_dir = os.path.join(d, "setter")
    new = E._read(os.path.join(work_dir, "exam.json"))
    base = old.get("base_sha")
    text = deps.text_of(item)
    if not isinstance(new, dict):
        v = {"ok": False, "refusals": [{"clause": None, "code": "SCHEMA", "why": "no exam.json written"}], "rows": []}
    else:
        stage = os.path.join(d, "files.amend")
        shutil.rmtree(stage, ignore_errors=True)
        shutil.copytree(os.path.join(work_dir, "files"), stage)
        run, read_file, close = deps.boxer(_rules(deps), os.path.join(store.root, "books"), base, stage, item=item)
        try:
            v = E.validate(new, run, text, E._prose(os.path.join(store.root, "books"), base, item), read_file)
        finally:
            close()
        if v["ok"]:
            frozen = dict(new, item=item, base_sha=base, exam_hash=v["exam_hash"], mode=old.get("mode"),
                          setter=old.get("setter"), validated_at=now_iso(), amended_from=old.get("exam_hash"))
            if not publish(store, item, old, frozen, stage, gen=gen):
                shutil.rmtree(stage, ignore_errors=True)
                v = dict(v, ok=False, stale=True)
        else:
            shutil.rmtree(stage, ignore_errors=True)
    E._append(os.path.join(d, "validation.jsonl"), dict(v, attempt="amend", at=now_iso()))
    return v


# ------------------------------------------------------------------------------------- the journaled amend publish
PUBLISH_STEPS = ("history", "files", "exam", "status")


def _publish_paths(d):
    return {"journal": os.path.join(d, "amend.journal.json"), "lock": os.path.join(d, "publish.lock"),
            "stage": os.path.join(d, "files.amend"), "files": os.path.join(d, "files")}


def files_of(d, exam_hash):
    """Where a superseded exam's test files are kept (publish moves them there)."""
    return os.path.join(d, "files.%s" % re.sub(r"[^0-9A-Za-z]", "", str(exam_hash or "none"))[:32])


def publish(store, item, old, frozen, stage, gen=None, crash_after=None):
    """Install a validated amend as ONE act: write a journal naming the new exam, then run the steps (history line,
    files swap, exam.json, owed.json) and drop the journal. A crash anywhere leaves the journal, and the next reader
    (recover_publish, via exam_of) finishes it: the exam's files and its exam_hash never disagree for longer than that.
    `crash_after` (tests) raises after the named step. -> False when the item left `gen` (nothing published)."""
    d = E.item_dir(store, item)
    p = _publish_paths(d)
    with _flock(p["lock"]):
        _roll_forward(store, item, p)            # finish a predecessor's publish before starting ours
        if gen is not None and live_gen(store, item) != gen:
            return False
        if os.path.abspath(stage) != p["stage"]:
            shutil.rmtree(p["stage"], ignore_errors=True)
            os.replace(stage, p["stage"])
        E._write(p["journal"], {"old": old, "frozen": frozen, "done": [], "at": now_iso()})
        _roll_forward(store, item, p, crash_after=crash_after)
    return True


def recover_publish(store, item):
    """Finish an amend publish a dead worker left half-done (its journal is still there). Idempotent; cheap when none."""
    d = E.item_dir(store, item)
    p = _publish_paths(d)
    if not os.path.exists(p["journal"]):
        return False
    with _flock(p["lock"]):
        return _roll_forward(store, item, p)


def _roll_forward(store, item, p, crash_after=None):
    jn = E._read(p["journal"])
    if not isinstance(jn, dict):
        return False
    old, frozen, done = jn.get("old") or {}, jn.get("frozen") or {}, list(jn.get("done") or [])
    d = E.item_dir(store, item)
    for step in PUBLISH_STEPS:
        if step in done:
            continue
        if step == "history":
            hp = os.path.join(d, "exam_history.jsonl")
            if not any(h.get("exam_hash") == old.get("exam_hash") and h.get("superseded_by") == frozen.get("exam_hash")
                       for h in (E._lines(hp) if os.path.exists(hp) else [])):     # a crash after the append: once only
                    E._append(hp, dict(old, superseded_at=jn.get("at") or now_iso(), superseded_by=frozen.get("exam_hash")))
        elif step == "files":
            if os.path.isdir(p["stage"]):        # absent: an earlier pass already moved it in (rename is atomic)
                if os.path.isdir(p["files"]):    # the old exam's files are kept by hash: an arbiter of a dispute the
                    arch = files_of(d, old.get("exam_hash"))          # Setter defended on that exam judges THEM
                    shutil.rmtree(arch, ignore_errors=True)
                    os.replace(p["files"], arch)
                os.replace(p["stage"], p["files"])
        elif step == "exam":
            E._write(os.path.join(d, "exam.json"), frozen)
        elif step == "status":
            E.set_status(store, item, exam_hash=frozen.get("exam_hash"), amended_at=frozen.get("validated_at"))
        done.append(step)
        E._write(p["journal"], dict(jn, done=done))
        if crash_after == step:
            raise RuntimeError("test crash after %s" % step)
    os.remove(p["journal"])
    return True


def _arbiter_run(store, item, base, prompt, ruling_path, out, cfg, deps, winners, files=None):
    """A fresh arbiter (Marker's Judge-mode agent) in a box at base. -> (ruling dict or None, session)."""
    d = E.item_dir(store, item)
    acfg = {"setter_agent": cfg.get("arbiter_agent", "rm-judge"), "setter_model": cfg.get("arbiter_model", "opus"),
            "setter_max_s": cfg.get("arbiter_max_s", 1500)}
    try:
        os.remove(ruling_path)
    except OSError:
        pass
    run, read_file, close = deps.boxer(_rules(deps), os.path.join(store.root, "books"), base, files or os.path.join(d, "files"),
                                       item=item)
    try:
        sid = deps.setter(getattr(read_file, "tree", d), prompt, acfg, out)
    finally:
        close()
    excl = os.path.join(d, "excluded.json")
    with _flock(excl + ".lock"):
        cur = E._read(excl, {"sessions": []}) or {"sessions": []}
        cur["sessions"] = sorted(set(cur.get("sessions", [])) | {sid})
        cur["why"] = "arbiters of this item's disputes: never its Marker (redesign_final G13)"
        E._write(excl, cur)
    r = E._read(ruling_path)
    if isinstance(r, dict) and r.get("winner") in winners:
        return {"winner": r["winner"], "why": str(r.get("why", ""))[:3000], "session": sid, "at": now_iso()}, sid
    return None, sid


def _arbitrate(store, j, cfg, deps):
    item, job = j["item"], j["id"]
    j = update(store, item, job, state="arbitrating", arb_attempts=int(j.get("arb_attempts", 0)) + 1, pid=os.getpid())
    exam = exam_of(store, item) or {}
    a = j.get("answer") or {}
    files = None
    if a.get("clauses") is not None and a.get("exam_hash") != exam.get("exam_hash"):
        exam = dict(exam, clauses=a["clauses"])  # the Setter defended an exam since amended: judge what it defended,
        kept = files_of(E.item_dir(store, item), a.get("exam_hash"))                   # with that exam's own files
        files = kept if os.path.isdir(kept) else None
    prompt = ARBITER_BRIEF.format(item=item, base=exam.get("base_sha"), text=deps.text_of(item)[:8000],
                                  body=_dispute_body(j, exam), ruling=os.path.join(jobs_dir(store, item), job + ".ruling.json"),
                                  choices=DISPUTE_CHOICES, winners="|".join(WINNERS))
    ruling = None
    for _ in range(int(cfg.get("arbiter_tries", 2))):
        ruling, _sid = _arbiter_run(store, item, exam.get("base_sha"), prompt,
                                    os.path.join(jobs_dir(store, item), job + ".ruling.json"),
                                    os.path.join(jobs_dir(store, item), job + ".arbiter.out"), cfg, deps, WINNERS,
                                    files=files)
        if ruling:
            break
    if not ruling:
        _void(store, load(store, item, job), "the arbiter wrote no ruling in %s launches" % cfg.get("arbiter_tries", 2))
        return
    j = update(store, item, job, state="ruled", ruling=ruling)
    row(store, j, ruling["winner"], ruling)


def _void_ruling(why):
    return {"winner": "void", "why": why, "session": None, "by": "supervisor", "at": now_iso()}


def _void(store, j, why, only_open=False):
    """Every job ends in an answer or a ruling: an arbiter that never rules leaves a recorded void ruling, not a hang.
    `only_open`: a compare-and-set under jobs_lock: a job that reached an answer or a ruling meanwhile is left alone."""
    ruling = _void_ruling(why)
    with jobs_lock(store, j["item"]):
        cur = load(store, j["item"], j["id"]) or {}
        if only_open and cur.get("state") not in OPEN:
            return cur
        j = _apply(cur, state="ruled", ruling=ruling)
        E._write(job_path(store, j["item"], j["id"]), j)
    row(store, j, "void", ruling)


# ------------------------------------------------------------------------------ WP-03 R4: the refused exam's arbiter
EXAM_ARBITER_BODY = """The Setter's exam for this item was REFUSED twice by the supervisor's mechanical VALIDATE:
{refusals}"""
EXAM_CHOICES = ("Rule ONE of: setter (the Setter wrote a bad exam; a fresh Setter should set it), environment (the box "
                "cannot run what the item needs), bar (the item text cannot be examined as written: it goes back to its author).")


def arbitrate_exam(store, item, cfg=None, deps=None):
    """relentless_exam's `arbiter_owed` (a second VALIDATE refusal): one fresh arbiter rules setter|environment|bar.
    Shadow: the ruling is recorded on the exam's owed.json; nothing is filed. -> the ruling or None."""
    cfg = config() if cfg is None else cfg
    deps = deps or Deps()
    with _claim(os.path.join(E.item_dir(store, item), "exam_arbiter.lock")) as mine:
        if not mine:                     # another process is ruling this exam now
            return None
        return _arbitrate_exam(store, item, cfg, deps)


def _arbitrate_exam(store, item, cfg, deps):
    """Under the exam's arbiter claim. `arbitrating` with the claim free means its arbiter died: it is retried, and
    after arbiter_tries dead launches it gets a recorded void ruling instead of hanging."""
    st = E.status(store, item) or {}
    if st.get("state") not in ("arbiter_owed", "arbitrating") or cfg.get("mode", "off") == "off":
        return None
    tries = int(cfg.get("arbiter_tries", 2))
    n = int(st.get("arb_attempts", 0))
    if st.get("state") == "arbitrating" and n >= tries:
        ruling = _void_ruling("the exam's arbiter died %s times" % n)
        E.set_status(store, item, state="arbiter_ruled", ruling=ruling)
        return ruling
    E.set_status(store, item, state="arbitrating", arb_attempts=n + 1)
    refs = "\n".join("- %s %s: %s" % (r.get("code"), r.get("clause") or "", r.get("why")) for r in st.get("refusals") or [])
    d = E.item_dir(store, item)
    ruling_path = os.path.join(d, "exam_ruling.json")
    prompt = ARBITER_BRIEF.format(item=item, base=st.get("base"), text=deps.text_of(item)[:8000],
                                  body=EXAM_ARBITER_BODY.format(refusals=refs or "(none recorded)"), ruling=ruling_path,
                                  choices=EXAM_CHOICES, winners="|".join(EXAM_WINNERS))
    ruling = None
    for _ in range(int(cfg.get("arbiter_tries", 2))):
        ruling, _sid = _arbiter_run(store, item, st.get("base"), prompt, ruling_path, os.path.join(d, "arbiter.out"),
                                    cfg, deps, EXAM_WINNERS)
        if ruling:
            break
    ruling = ruling or {"winner": "void", "why": "the arbiter wrote no ruling", "by": "supervisor", "at": now_iso()}
    E.set_status(store, item, state="arbiter_ruled", ruling=ruling)
    return ruling


# ------------------------------------------------------------------------------ WP-15: the rejected role stage's arbiter
ROLE_BODY = """The role {role} ({concept}) had its stage close REJECTED by the supervisor twice with the same signature
{sig}. The reasons given:
{reasons}"""
ROLE_CHOICES = ("Rule ONE of: builder (the role's output is right; the stage check is wrong), setter (the check is right; "
                "the role must meet it), environment (the check cannot run where it must), bar (the item text is the problem).")


def role_stage_dispute(role, concept, item, sig, reasons, store=None, cfg=None, deps=None):
    """role_launch.to_arbiter's entry (a 2nd identical rejected role stage): one fresh arbiter rules, the who-was-right
    row is logged under the item's exam dir, nothing is filed. Shadow like the rest: mode off -> None. -> a sentence for
    the ledger, or None (any fault, no mode, no base: today's behaviour, the alarm stands)."""
    try:
        cfg = config() if cfg is None else cfg
        if cfg.get("mode", "off") == "off":
            return None
        import relentless
        store = store or relentless.Store()
        deps = deps or Deps()
        key = item or "ROLE_" + re.sub(r"\W+", "_", os.path.basename(os.path.normpath(concept or "none")))[:60]
        base = (E.status(store, key) or {}).get("base") or (exam_of(store, key) or {}).get("base_sha")
        if not base:
            r = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=60)
            base = r.stdout.strip()
        if not base:
            return None
        d = E.item_dir(store, key)
        ruling_path = os.path.join(d, "role_ruling.json")
        prompt = ARBITER_BRIEF.format(
            item=key, base=base, text=deps.text_of(item)[:8000] if item else "(no ledger item)",
            body=ROLE_BODY.format(role=role, concept=concept, sig=sig, reasons="\n".join("- %s" % r for r in reasons)[:6000]),
            ruling=ruling_path, choices=ROLE_CHOICES, winners="|".join(WINNERS))
        ruling = None
        for _ in range(int(cfg.get("arbiter_tries", 2))):
            ruling, _sid = _arbiter_run(store, key, base, prompt, ruling_path, os.path.join(d, "role_arbiter.out"),
                                        cfg, deps, WINNERS)
            if ruling:
                break
        ruling = ruling or {"winner": "void", "why": "the arbiter wrote no ruling", "by": "supervisor", "at": now_iso()}
        E._append(os.path.join(d, "role_dispute.jsonl"), {
            "role": role, "concept": concept, "sig": sig, "winner": ruling["winner"], "final": True,
            "arbiter": ruling.get("session"), "at": now_iso()})
        return "arbiter ruled %s (shadow; %s; nothing filed)" % (ruling["winner"], str(ruling.get("why", ""))[:200])
    except Exception:  # noqa: BLE001 - the caller's alarm already stands; a fault here must not break the role launch
        return None


# ---------------------------------------------------------------------------------------------------------- reading
def summary(store):
    """Who-was-right counts over every dispute row (the error-rate by-product; X/Y proper come from the regrade sample)."""
    out = {"jobs": 0, "states": {}, "winners": {}}
    for p in glob.glob(os.path.join(E.exam_root(store), "*", "disputes", "*.json")):
        j = E._read(p) or {}
        if not j.get("id"):
            continue
        out["jobs"] += 1
        out["states"][j.get("state")] = out["states"].get(j.get("state"), 0) + 1
        w = (j.get("ruling") or {}).get("winner") or ("builder" if j.get("state") == "settled" else None)
        if w:
            out["winners"][w] = out["winners"].get(w, 0) + 1
    return out


def verb(store, a, cfg=None, say=print):
    """relentless.py `challenge` dispatch. -> process exit (0)."""
    if a.status:
        shown = deliver(store, a.item, a.gen, say=say, cfg=cfg)
        for j in jobs(store, a.item):
            if j["id"] not in shown and (a.gen is None or j.get("gen") == a.gen):
                say("relentless challenge %s: %s on %s (%s)" % (j["id"], j.get("state"), ",".join(j["clauses"]), j["claim"]))
        return 0
    if a.reply_to:
        reply(store, a.item, a.gen, a.reply_to, a.text, cfg=cfg, say=say)
        return 0
    if not (a.clause and a.claim and a.evidence):
        raise ValueError("challenge needs --clause, --claim and --evidence (or --reply JOB TEXT, or --status)")
    ask(store, a.item, a.gen, a.clause, a.claim, a.evidence, a.text or "", cfg=cfg, say=say)
    return 0


def add_parser(sub):
    p = sub.add_parser("challenge", help="dispute an exam clause with its Setter, live (relentless_dispute): answer in "
                       "this call or at your next boxrun; one --reply, then an arbiter rules")
    p.add_argument("--item", required=True)
    p.add_argument("--gen", type=int)
    p.add_argument("--clause", help="c3 or c3,c4")
    p.add_argument("--claim", choices=CLAIMS)
    p.add_argument("--evidence", help="a file: the box output or diff the claim rests on")
    p.add_argument("--reply", dest="reply_to", metavar="JOB", help="your one reply to the Setter's stand on JOB")
    p.add_argument("--status", action="store_true", help="print answers not yet shown, and every job's state")
    p.add_argument("text", nargs="?", help="your words (the challenge, or the reply)")
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("work", help="the worker unit: answer one job, then arbitrate if owed")
    p.add_argument("item")
    p.add_argument("job")
    sub.add_parser("summary")
    a = ap.parse_args(argv)
    if a.cmd == "work":
        try:
            job_id(a.job)
        except ValueError as e:
            print("worker refused: %s" % e)
            return 2
    import relentless
    store = relentless.Store()
    if a.cmd == "work":
        try:
            print(work(store, a.item, a.job))
        except Exception as e:  # noqa: BLE001 - recorded on the job; deliver() restarts or routes it
            update(store, a.item, a.job, worker_error="%s: %s" % (type(e).__name__, str(e)[:300]))
            print("worker failed: %s" % e)
            return 1
        return 0
    print(json.dumps(summary(store), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
