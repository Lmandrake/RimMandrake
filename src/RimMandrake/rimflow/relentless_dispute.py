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


def job_path(store, item, job):
    return os.path.join(jobs_dir(store, item), job + ".json")


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


def session_lock(store, item):
    """The Setter session's lock: held for a whole answer turn, so two challenges never interleave in one session."""
    return _flock(os.path.join(E.item_dir(store, item), "setter.lock"))


def load(store, item, job):
    return E._read(job_path(store, item, job))


def jobs(store, item):
    d = jobs_dir(store, item)
    out = [E._read(p) for p in sorted(glob.glob(os.path.join(d, "*.json")))] if os.path.isdir(d) else []
    return sorted([j for j in out if isinstance(j, dict) and j.get("id")], key=lambda j: (j.get("asked_at", ""), j.get("id", "")))


def update(store, item, job, **kw):
    with jobs_lock(store, item):
        j = load(store, item, job) or {}
        hist = j.setdefault("history", [])
        if "state" in kw and kw["state"] != j.get("state"):
            hist.append({"state": kw["state"], "at": now_iso()})
        j.update(kw)
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
        if not j:
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
    item, job = j["item"], j["id"]
    if j.get("state") in ("asked", "answering") and int(j.get("attempts", 0)) >= int(cfg.get("answer_tries", 2)):
        update(store, item, job, state="replied", answer={"verdict": "no_answer", "why": "the answering worker died %s times"
                                                          % j.get("attempts")}, route="worker_died")
    elif j.get("state") in ("replied", "arbitrating") and int(j.get("arb_attempts", 0)) >= int(cfg.get("arbiter_tries", 2)):
        _void(store, load(store, item, job), "the arbiter's worker died %s times" % j.get("arb_attempts"))
        return
    elif j.get("state") == "answering":
        update(store, item, job, state="asked")
    elif j.get("state") == "arbitrating":
        update(store, item, job, state="replied")
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
    if not j:
        return None
    if j.get("state") in ("asked", "answering"):
        with session_lock(store, item):
            j = load(store, item, job)
            if j.get("state") in ("asked", "answering"):
                _answer(store, j, cfg, deps)
    j = load(store, item, job)
    if j.get("state") in ("replied", "arbitrating"):
        _arbitrate(store, j, cfg, deps)
    return (load(store, item, job) or {}).get("state")


def _answer(store, j, cfg, deps):
    item, job = j["item"], j["id"]
    j = update(store, item, job, state="answering", attempts=int(j.get("attempts", 0)) + 1, pid=os.getpid())
    exam = exam_of(store, item) or {}
    if exam.get("exam_hash") != j.get("exam_hash"):
        gone = [c for c in j["clauses"] if c not in {x.get("id") for x in exam.get("clauses") or []}]
        if gone:        # an earlier challenge's amend removed it: nothing left to dispute
            update(store, item, job, state="settled", answer={"verdict": "superseded", "why": "clause(s) %s left the exam "
                   "in an amendment since this challenge" % ",".join(gone), "exam_hash": exam.get("exam_hash")})
            row(store, load(store, item, job), "builder")
            return
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
    if ans["verdict"] == "stand":
        row(store, update(store, item, job, state="answered", answer=dict(ans, exam_hash=exam.get("exam_hash"))),
            "setter", final=False)
        return
    v = revalidate(store, item, exam, deps)
    if v["ok"]:
        update(store, item, job, state="settled", answer=dict(ans, exam_hash=v["exam_hash"], validated=True))
        row(store, load(store, item, job), "builder")
    else:
        update(store, item, job, state="replied", route="amend_refused",
               answer=dict(ans, verdict="amend_refused", refusals=v["refusals"][:12]))


def revalidate(store, item, old, deps):
    """An amend counts only after VALIDATE: the Setter's rewritten exam, run in a fresh box at the base sha. A pass
    freezes it (old exam kept in exam_history.jsonl, files replaced, exam_hash moved)."""
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
            E._append(os.path.join(d, "exam_history.jsonl"), dict(old, superseded_at=now_iso()))
            shutil.rmtree(os.path.join(d, "files"), ignore_errors=True)
            os.replace(stage, os.path.join(d, "files"))
            frozen = dict(new, item=item, base_sha=base, exam_hash=v["exam_hash"], mode=old.get("mode"),
                          setter=old.get("setter"), validated_at=now_iso(), amended_from=old.get("exam_hash"))
            E._write(os.path.join(d, "exam.json"), frozen)
            E.set_status(store, item, exam_hash=v["exam_hash"], amended_at=frozen["validated_at"])
        else:
            shutil.rmtree(stage, ignore_errors=True)
    E._append(os.path.join(d, "validation.jsonl"), dict(v, attempt="amend", at=now_iso()))
    return v


def _arbiter_run(store, item, base, prompt, ruling_path, out, cfg, deps, winners):
    """A fresh arbiter (Marker's Judge-mode agent) in a box at base. -> (ruling dict or None, session)."""
    d = E.item_dir(store, item)
    acfg = {"setter_agent": cfg.get("arbiter_agent", "rm-judge"), "setter_model": cfg.get("arbiter_model", "opus"),
            "setter_max_s": cfg.get("arbiter_max_s", 1500)}
    try:
        os.remove(ruling_path)
    except OSError:
        pass
    run, read_file, close = deps.boxer(_rules(deps), os.path.join(store.root, "books"), base, os.path.join(d, "files"), item=item)
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
    prompt = ARBITER_BRIEF.format(item=item, base=exam.get("base_sha"), text=deps.text_of(item)[:8000],
                                  body=_dispute_body(j, exam), ruling=os.path.join(jobs_dir(store, item), job + ".ruling.json"),
                                  choices=DISPUTE_CHOICES, winners="|".join(WINNERS))
    ruling = None
    for _ in range(int(cfg.get("arbiter_tries", 2))):
        ruling, _sid = _arbiter_run(store, item, exam.get("base_sha"), prompt,
                                    os.path.join(jobs_dir(store, item), job + ".ruling.json"),
                                    os.path.join(jobs_dir(store, item), job + ".arbiter.out"), cfg, deps, WINNERS)
        if ruling:
            break
    if not ruling:
        _void(store, load(store, item, job), "the arbiter wrote no ruling in %s launches" % cfg.get("arbiter_tries", 2))
        return
    j = update(store, item, job, state="ruled", ruling=ruling)
    row(store, j, ruling["winner"], ruling)


def _void(store, j, why):
    """Every job ends in an answer or a ruling: an arbiter that never rules leaves a recorded void ruling, not a hang."""
    ruling = {"winner": "void", "why": why, "session": None, "by": "supervisor", "at": now_iso()}
    j = update(store, j["item"], j["id"], state="ruled", ruling=ruling)
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
    st = E.status(store, item) or {}
    if st.get("state") != "arbiter_owed" or cfg.get("mode", "off") == "off":
        return None
    E.set_status(store, item, state="arbitrating")
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
