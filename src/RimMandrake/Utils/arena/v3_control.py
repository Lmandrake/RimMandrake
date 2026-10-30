#!/usr/bin/env python3
r"""v3_control.py - the `v3` replay procedure (the control) and `v3c`, each with a fresh tester helper after a close.

ARENA_CONTROL_BUILD_V3_TESTER_AFTER_CLOSE. Design: architecture_switch_harness_2026-10-29.md step 9;
testpilot_merged_2026-10-29.md §2.3 (owner, binding: a different agent tests what was built, before the builder's
next build) and §6.2; rimflow_v3_collapse_compare_2026-10-29.md §4 I1 (done is earned) for v3c. The briefs are text
files beside this one in `v3/`: BRIEF.md (today's FOUNDRY helper brief, replay form), TESTER_BRIEF.md (the one
change), REVIEW.md (v3c's blind GPT review).

WHAT THE PROCEDURE IS. Today's FOUNDRY procedure for one item: brief a fresh helper with the item; the helper builds,
self-verifies and closes against its commit. In a replay the item order is fixed by arena_replay.schedule, so the
orchestrator's only remaining act is the brief, and this program writes it (BRIEF.md + the frozen spec). The
procedure is changed in ONE place: after each helper's close, a fresh tester helper tests that sha BEFORE any new
build is briefed. A tester FAIL re-briefs the same item with the tester's findings (as a verify fail re-opens an item
today), up to MAX_TRIES builds per item. One Procedure.work(task) call works one task inside one replay clone
(arena_replay.run_one builds and deletes the clone; replay_work() gives run_schedule its `work`).

  v3   build helper -> close (`build_end`, detail.via "close": today's self-accepted close) -> tester helper
       (`test_start` written BEFORE the tester model runs, then `test_end`) -> next brief.
  v3c  build helper -> candidate (`build_end`, via "candidate") -> tester helper -> blind GPT review of the sha
       (program-called, never by the helper: a `critic_round` event, detail.kind "gpt_review", bound to the sha by a
       record file under <ctl>/reviews/ whose sha256 the signed event holds) -> close() through the DONE GATE.

THE TWO HARD CHECKS (code, not prompt; both read the SIGNED event log, never procedure memory):
  require_tested(recs, arm)   the FIRST statement of every build brief: every build_end of this arm's replay records
                              must have a later test_start of that build by a DIFFERENT agent (arena_eventlog.
                              untested_builds, ids compared through ralph_a_loop.agent_key), and no test_start may be
                              its builder (flagged_same_agent). Otherwise NotTested: no brief, no model.
  done_gate(recs, arm, task, sha, review_dir)   v3c's close: refused unless, for exactly this 40-hex sha, (a) it is
                              the task's latest build_end; (b) the LATEST test_end of the sha after that build by an
                              agent other than every builder of the task is `pass`, and that tester's test_start of
                              the sha lies between the build and that end; (c) the LATEST gpt_review critic_round of
                              the sha after the build is `pass`, and its record file exists, hashes to the signed
                              record_sha256 and names the same task, sha and verdict. A newer fail of either refuses.
                              Every close attempt is logged (`pass_end`, detail.role "close", verdict done|refused).

SCOPE OF THE LOG. Both arms write arm "v3"/"v3c", lane "replay", run_id "<arm>.replay.<n>". The checks read only
records with that run_id prefix: arena_v3_adapter writes PRODUCTION v3 (the ledger) under arm "v3" with run_id
"v3-ledger" or a testq job id, and those closes are not this procedure's builds.

INJECTABLE (the selftest runs all of it offline): `model` (argv via --model-cmd / $V3_MODEL_CMD, prompt on stdin;
the tester runs in ralph_a_loop's isolation: history-less export, fresh private root per attempt, bubblewrap, an
allow-listed env), `writer` (default the signed arena_eventlog.HarnessWriter: v3_control.py is in ENTRYPOINTS),
`reviewer` (default gpt_consult.py from THIS checkout, medium effort), `runway`, `new_id`, `procs`.
No account, host or key is named here: the runway reading resolves the account from the environment.

THE BUILDER OWNS THE CLONE. Every git call on it ignores replace refs and grafts and disables diff drivers,
textconv, fsmonitor and hooks (safe_git), so the sha the log names is the tree the tester and the reviewer see. The
reviewer script runs only when byte-identical to the harness checkout's committed HEAD (pinned_harness_file).

RESIDUAL (stated, not fixed): the build helper runs unsandboxed as the harness user, as today's helpers do; it could
still commit to the harness checkout itself or read the event token. The v3/v3c comparison holds that exposure equal
across arms; isolating the build helper is a separate item. a procedure killed between build_end and test_start leaves an untested build whose
replay clone is gone; require_tested then refuses every later brief of that arm (fail closed, loud) until the harness
operator records the run invalid. Live tasks stop at "live owed" after the tester (the replay has no lane); v3c does
not close them. The bridge is never released by this program: the brief forbids it, and the replay clone's rimflow
is not the real ledger.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_eventlog as L  # noqa: E402
import ralph_a_loop as RA  # noqa: E402

ARMS = ("v3", "v3c")
BRIEF_DIR = HERE / "v3"
HARNESS_REPO = HERE.parents[3]
LANE = "replay"
MAX_TRIES = 3
PASS_TIMEOUT_S = 90 * 60
REVIEW_KIND = "gpt_review"
DEFAULT_CTL = "/mnt/d/ClaudeWork/rimmandrake/v3_control"
SHA40 = re.compile(r"[0-9a-f]{40}")
CLOSED_RE = re.compile(r"^\s*CLOSED:\s*([0-9a-fA-F]{7,40})\s*$", re.M)
NOTE_RE = re.compile(r"^\s*NOTE:\s*(.+)$", re.M)
RECORD_NAME = re.compile(r"[A-Za-z0-9_.-]{1,200}\.json")
REVIEW_STEP = {
    "v3": "If the item says blind GPT review before close, run it once via `python3 src/RimMandrake/Utils/gpt_consult.py`"
          " in fresh context (code + criteria only), fix confirmed findings (max 2 rounds).",
    "v3c": "Do not run a GPT review yourself: the procedure sends every closed sha to a blind GPT review, and the item "
           "is done only when that review and a tester helper both pass the sha.",
}

Refused = RA.Refused
NotTested = RA.NotTested


# ------------------------------------------------------------------------------------------------ log scope
def run_prefix(arm):
    return "%s.%s." % (arm, LANE)


def scoped(recs, arm):
    """This arm's replay records (run_id prefix), time-ordered, builder/tester ids canonicalised by agent_key."""
    pre = run_prefix(arm)
    out = []
    for r in L.ordered([r for r in recs if r.get("arm") == arm and str(r.get("run_id", "")).startswith(pre)]):
        d = r.get("detail")
        if isinstance(d, dict) and r.get("event") in ("build_end", "test_start", "test_end"):
            k = "builder" if r["event"] == "build_end" else "tester"
            if k in d:
                r = dict(r, detail=dict(d, **{k: RA.agent_key(d[k])}))
        out.append(r)
    return out


def require_tested(recs, arm):
    """Raise NotTested unless every replay build_end of `arm` has a later test_start of that build by a different
    agent, and no test_start is a builder testing itself."""
    mine = scoped(recs, arm)
    bad = L.untested_builds(mine)
    if bad:
        b = bad[0]
        raise NotTested("refused: %s build %s of %s (builder %s) has no test_start from a different agent; no new "
                        "build is briefed before the tester helper starts" % (
                            arm, (b.get("detail") or {}).get("build_id") or b.get("sha"), b.get("task"),
                            (b.get("detail") or {}).get("builder")))
    same = L.flagged_same_agent(mine)
    if same:
        raise NotTested("refused: %s test_start by the builder itself (%s)" % (
            arm, (same[0].get("detail") or {}).get("tester")))


# ------------------------------------------------------------------------------------------------ the done gate
def _valid_tester(key, builders):
    return bool(key) and not key.startswith(L.UNATTRIBUTED) and key not in builders


def tester_bound(recs, arm, task_id, sha):
    """The tester half of the done gate -> (ok, why, after, tester): (a) and (b) of the module doc. review() calls it
    too, so no GPT review is even run for a sha without a passing tester record bound to it."""
    if not (isinstance(sha, str) and SHA40.fullmatch(sha)):
        return False, "refused: close sha %r is not a full 40-hex sha" % (sha,), [], None
    tid = task_id.strip() if isinstance(task_id, str) else task_id
    seq = [r for r in scoped(recs, arm) if (r.get("task") or "").strip() == tid]
    builds = [i for i, r in enumerate(seq) if r.get("event") == "build_end"]
    if not builds:
        return False, "refused: no build_end of %s in the signed log" % tid, [], None
    last = builds[-1]
    if seq[last].get("sha") != sha:
        return False, "refused: %s is not the latest build of %s (latest %s)" % (
            sha, tid, seq[last].get("sha")), [], None
    builders = {(seq[i].get("detail") or {}).get("builder") for i in builds} - {None}
    after = [(i, r) for i, r in enumerate(seq) if i > last and r.get("sha") == sha]
    tkey = lambda r: (r.get("detail") or {}).get("tester")  # noqa: E731
    ends = [(i, r) for i, r in after if r.get("event") == "test_end" and _valid_tester(tkey(r), builders)]
    if not ends:
        return False, "refused: no tester record bound to %s (no test_end by an agent other than %s)" % (
            sha[:12], sorted(builders)), [], None
    ei, end = ends[-1]
    if end.get("verdict") != "pass":
        return False, "refused: the latest tester verdict on %s is %r" % (sha[:12], end.get("verdict")), [], None
    if not any(r.get("event") == "test_start" and tkey(r) == tkey(end) and i < ei for i, r in after):
        return False, "refused: tester %s has a test_end on %s but no earlier test_start" % (
            tkey(end), sha[:12]), [], None
    return True, "tester %s passed %s" % (tkey(end), sha[:12]), after, tkey(end)


def done_gate(recs, arm, task_id, sha, review_dir):
    """-> (ok, why). See the module doc. Pure over the signed records plus the review record files."""
    ok, why, after, tester = tester_bound(recs, arm, task_id, sha)
    if not ok:
        return False, why
    tid = task_id.strip() if isinstance(task_id, str) else task_id
    revs = [(i, r) for i, r in after if r.get("event") == "critic_round"
            and (r.get("detail") or {}).get("kind") == REVIEW_KIND]
    if not revs:
        return False, "refused: no review record bound to %s" % sha[:12]
    rv = revs[-1][1]
    if rv.get("verdict") != "pass":
        return False, "refused: the latest review of %s is %r" % (sha[:12], rv.get("verdict"))
    d = rv.get("detail") or {}
    name = d.get("record")
    if not (isinstance(name, str) and RECORD_NAME.fullmatch(name)):
        return False, "refused: review event names no usable record file (%r)" % (name,)
    f = Path(review_dir) / name
    try:
        raw = f.read_bytes()
    except OSError:
        return False, "refused: review record %s is missing" % f
    if hashlib.sha256(raw).hexdigest() != d.get("record_sha256"):
        return False, "refused: review record %s does not hash to the signed record_sha256" % f
    try:
        body = json.loads(raw)
    except ValueError:
        return False, "refused: review record %s is not JSON" % f
    if not (isinstance(body, dict) and body.get("sha") == sha and body.get("task") == tid
            and body.get("verdict") == "pass"):
        return False, "refused: review record %s is not a pass of %s on %s" % (f, tid, sha[:12])
    return True, "done gate passed: tester %s and review %s both pass %s" % (tester, name, sha[:12])


# ------------------------------------------------------------------------------------------------ git the builder cannot steer
# The build helper owns the clone's .git: a replace ref or graft would make `git archive`/`git diff` of sha A show
# commit B (review r1), and a diff driver or fsmonitor in .git/config would run its code as the harness. Every git
# call on the clone ignores replace objects and grafts and disables those execution hooks.
# (the env/config pins live in arena_safe_git, one copy: ARENA_GIT_FETCHES_AUDIT_STRAGGLERS)
import arena_safe_git as SG  # noqa: E402


def safe_git(root, *a, binary=False):
    r = SG.git_run(root, *a, capture_output=True, text=not binary)
    if r.returncode != 0:
        err = r.stderr.decode(errors="replace") if binary else r.stderr
        raise Refused("git %s failed: %s" % (" ".join(a), err.strip()[:300]))
    return r.stdout if binary else r.stdout.strip()


def export_tree(root, sha, dest):
    """A history-less copy of exactly `sha`'s tree, read object by object (ls-tree + cat-file): replace refs and
    grafts are ignored, and no attribute applies (`git archive` would honour the builder's export-ignore and
    export-subst, review r2). Submodule entries are skipped; a symlink is kept only if it stays inside dest."""
    if dest.exists():
        RA.shutil.rmtree(dest)
    dest.mkdir(parents=True)
    top = dest.resolve()
    ents = []
    for e in safe_git(root, "ls-tree", "-r", "-z", "--full-tree", sha, binary=True).split(b"\0"):
        if not e:
            continue
        meta, path = e.split(b"\t", 1)
        mode, kind, obj = meta.decode().split()
        if kind == "blob":
            ents.append((mode, obj, path.decode("utf-8", "surrogateescape")))
    if not ents:
        return dest
    r = SG.git_run(root, "cat-file", "--batch", input="".join(o + "\n" for _, o, _ in ents).encode(), capture_output=True)
    if r.returncode != 0:
        raise Refused("git cat-file failed: %s" % r.stderr.decode(errors="replace")[:300])
    buf, pos = r.stdout, 0
    for mode, obj, path in ents:
        nl = buf.index(b"\n", pos)
        head = buf[pos:nl].split()
        if len(head) != 3 or head[0].decode() != obj:
            raise Refused("git cat-file: unexpected header %r for %s" % (buf[pos:nl][:80], path))
        size = int(head[2])
        data = buf[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
        f = (dest / path)
        if ".." in Path(path).parts or not f.resolve().is_relative_to(top):
            raise Refused("refused: tree path %r escapes the export" % path)
        f.parent.mkdir(parents=True, exist_ok=True)
        if mode == "120000":
            tgt = data.decode("utf-8", "surrogateescape")
            if not os.path.isabs(tgt) and (f.parent / tgt).resolve().is_relative_to(top):
                os.symlink(tgt, f)
            continue
        f.write_bytes(data)
        if mode == "100755":
            f.chmod(0o755)
    return dest


def pinned_harness_file(rel):
    """The harness file `rel`, refused unless it is byte-identical to HARNESS_REPO's committed HEAD blob: the build
    helper runs as the harness user, so it could rewrite the reviewer it is judged by (review r1)."""
    f = HARNESS_REPO / rel
    want = subprocess.run(["git", "-C", str(HARNESS_REPO), "rev-parse", "HEAD:" + rel], capture_output=True,
                          text=True)
    have = subprocess.run(["git", "-C", str(HARNESS_REPO), "hash-object", "--no-filters", str(f)],
                          capture_output=True, text=True)
    if want.returncode or have.returncode or want.stdout.strip() != have.stdout.strip():
        raise Refused("refused: %s differs from the harness checkout's committed HEAD (or is not committed): no "
                      "review is run through a reviewer that may have been rewritten" % f)
    return f


# ------------------------------------------------------------------------------------------------ models
class CmdModel(RA.CmdModel):
    """ralph_a's CmdModel (tester: sandboxed, allow-listed env, pidfile, group killed after the pass); the build
    helper's env is tagged RM_ARM=<arm> instead of ralph_a and stripped of every ARENA_/V3_ variable."""

    def __init__(self, cmd, arm):
        super().__init__(cmd)
        self.arm = arm

    def __call__(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        if role == "test":
            return super().__call__(role, prompt, cwd=cwd, agent_id=agent_id, run_id=run_id, timeout_s=timeout_s,
                                    log=log, sandbox=sandbox)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ARENA_", "V3_", "RALPH_A_"))}
        env.update(RM_ARM=self.arm, V3_ROLE=role)
        with open(log, "w") as out:
            pr = subprocess.Popen(self.argv, cwd=str(cwd), env=env, stdin=subprocess.PIPE, stdout=out,
                                  stderr=subprocess.STDOUT, text=True, start_new_session=True)
            if self.pidfile:
                Path(self.pidfile).write_text(json.dumps({"pgid": pr.pid, "start": RA.proc_start(pr.pid),
                                                          "role": role, "agent": agent_id}))
            try:
                pr.communicate(prompt, timeout=timeout_s)
                rc = pr.returncode
            except subprocess.TimeoutExpired:
                rc = -9
            finally:
                try:
                    os.killpg(pr.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                pr.wait()
                if self.pidfile and not RA.group_alive(pr.pid):
                    Path(self.pidfile).unlink(missing_ok=True)
        raw = Path(log).read_text(errors="replace")
        try:
            j = json.loads(raw)
            text = j.get("result") if isinstance(j, dict) and isinstance(j.get("result"), str) else raw
        except ValueError:
            text = raw
        return {"rc": rc, "text": text}


def gpt_reviewer(task, sha, diff, *, log):
    """The default v3c reviewer: gpt_consult.py from the HARNESS checkout, a fresh context that sees REVIEW.md, the
    item's criteria and the diff, nothing else. -> {"verdict": pass|fail|None, "text"}."""
    with tempfile.TemporaryDirectory(prefix="v3c-review-") as td:
        q, df, out = Path(td) / "q.md", Path(td) / "diff.patch", Path(td) / "a.md"
        q.write_text((BRIEF_DIR / "REVIEW.md").read_text() + "\n## CRITERIA\n%s\n" % task.get("criteria"))
        df.write_text(diff)
        r = subprocess.run([sys.executable, str(pinned_harness_file("src/RimMandrake/Utils/gpt_consult.py")),
                            "--prompt-file", str(q), "-f", str(df), "--out", str(out), "--effort", "medium",
                            "--timeout", "500"], capture_output=True, text=True, timeout=600)
        text = out.read_text() if out.is_file() else ""
        Path(log).write_text("rc=%s\n%s\n--- stderr\n%s" % (r.returncode, text, r.stderr[-4000:]))
    return {"verdict": RA.parse_verdict(text) if r.returncode == 0 else None, "text": text}


# ------------------------------------------------------------------------------------------------ the procedure
class Procedure:
    def __init__(self, arm, clone, ctl, *, model, writer, reviewer=None, runway=None, new_id=None,
                 timeout_s=PASS_TIMEOUT_S, tester_tmp=None, procs=RA.procs_in, tester_workdir=None,
                 lock_dir=None):
        if arm not in ARMS:
            raise Refused("unknown arm %r (want one of %s)" % (arm, ARMS))
        self.arm, self.root, self.ctl = arm, Path(clone), Path(ctl)
        self.model, self.writer = model, writer
        self.reviewer = reviewer or gpt_reviewer
        self.runway = runway or RA.default_runway
        self.new_id = new_id or (lambda role: "%s-%s-%s" % (arm, role, uuid.uuid4().hex[:12]))
        self.timeout_s, self.tester_tmp, self.procs = timeout_s, tester_tmp, procs
        # ONE lock per arm whatever --ctl says: every procedure of an arm writes the same signed log, so its
        # require_tested -> brief -> test sequence must not interleave with another's (review r2)
        self.lock_dir = Path(lock_dir or os.environ.get("V3_LOCK_DIR") or DEFAULT_CTL)
        self.tester_workdir = tester_workdir or (lambda sha, dest: export_tree(self.root, sha, dest))
        self.log = self.ctl / "log"
        self.reviews = self.ctl / "reviews"
        self.log.mkdir(parents=True, exist_ok=True)
        self.reviews.mkdir(parents=True, exist_ok=True)
        self.pidfile = self.ctl / "pass.pid"
        if hasattr(model, "pidfile"):
            model.pidfile = self.pidfile
        self.n = self._next_n()

    def _next_n(self):
        f = self.ctl / "n"
        try:
            return int(f.read_text())
        except (OSError, ValueError):
            return 0

    def _bump(self):
        self.n += 1
        f = self.ctl / "n"
        f.with_suffix(".tmp").write_text(str(self.n))
        os.replace(f.with_suffix(".tmp"), f)

    def records(self):
        return self.writer.records()

    def emit(self, event, task, **kw):
        return self.writer.emit(self.arm, event, lane=LANE, run_id="%s%d" % (run_prefix(self.arm), self.n),
                                task=task["id"], **kw)

    def git(self, *a):
        return safe_git(self.root, *a)

    def runway_refusal(self):
        return RA.Loop.runway_refusal(self)

    def status(self, what):
        (self.ctl / "status").write_text("%s %s n=%d %s\n" % (L.now_ts(), self.arm, self.n, what))
        return what

    # ---- the build brief
    def brief(self, task, feedback):
        text = (BRIEF_DIR / "BRIEF.md").read_text().replace("{{REVIEW_STEP}}", REVIEW_STEP[self.arm])
        text += "\n## ITEM (frozen spec)\n" + json.dumps(RA.public_spec(task), indent=1, sort_keys=True) + "\n"
        if feedback:
            text += "\n## WHY THIS ITEM IS BACK (findings on the last close)\n" + feedback + "\n"
        return text

    def build(self, task, base, feedback=""):
        """Brief one fresh build helper. -> pending build dict, or (None, why) when nothing was closed."""
        require_tested(self.records(), self.arm)                  # HARD CHECK: before anything else of the brief
        why = self.runway_refusal()
        if why:
            raise Refused("runway: " + why)
        busy = self.procs(self.root) if self.procs else []
        if busy:
            raise Refused("refused: process(es) %s have their cwd in the clone %s" % (busy[:8], self.root))
        before = self.git("rev-parse", "HEAD")
        builder = self.new_id("build")
        self.emit("pass_start", task, detail={"role": "build", "agent": builder})
        res = self.model("build", self.brief(task, feedback), cwd=self.root, agent_id=builder, run_id=self.n,
                         timeout_s=self.timeout_s, log=self.log / ("build.%d.out" % self.n))
        head = self.git("rev-parse", "HEAD")
        text = res.get("text") or ""
        closed = CLOSED_RE.findall(text)
        if res.get("rc") != 0:
            why = "helper exit %r (killed or failed)" % res.get("rc")
        elif not closed:
            m = NOTE_RE.findall(text)
            why = "helper did not close: %s" % (m[-1].strip() if m else "no CLOSED or NOTE line")
        elif head == before:
            why = "helper claims a close but made no commit"
        elif not head.startswith(closed[-1].lower()):
            why = "helper closed %s but the clone HEAD is %s" % (closed[-1], head)
        else:
            why = None
        self.emit("pass_end", task, sha=head, verdict="fail" if why else "pass",
                  detail={"role": "build", "agent": builder, "rc": res.get("rc"), "why": why})
        if why:
            self._bump()
            return None, why
        bid = "%s.%s" % (task["id"], head[:12])
        self.emit("build_end", task, sha=head, detail={
            "builder": builder, "build_id": bid, "base": base, "via": "close" if self.arm == "v3" else "candidate"})
        self._bump()
        return {"build_id": bid, "base": base, "head": head, "builder": builder}, None

    # ---- the tester helper (the one change)
    def tester_prompt(self, task, diff):
        return ((BRIEF_DIR / "TESTER_BRIEF.md").read_text() + "\n## ITEM (frozen spec)\n" +
                json.dumps(RA.public_spec(task), indent=1, sort_keys=True) + "\n\n## TEST PLAN\n" +
                RA.test_plan(task) + "\n## DIFF\n" + diff + "\n")

    def _tester_root(self):
        return RA.Loop._tester_root(self)

    def test(self, task, pend):
        """A fresh tester helper on pend's sha; test_start is written BEFORE its model runs. -> (verdict, text)."""
        why = self.runway_refusal()
        if why:
            raise Refused("runway: " + why)
        diff = self.git("diff", "--no-ext-diff", "--no-textconv", pend["base"], pend["head"])
        prompt = self.tester_prompt(task, diff)
        verdict, text = None, ""
        for _ in range(RA.TESTER_TRIES):
            tester = self.new_id("test")
            if not RA.agent_key(tester) or RA.agent_key(tester) == RA.agent_key(pend["builder"]):
                raise Refused("tester id %r equals the builder's: refused" % tester)
            troot = self._tester_root()
            try:
                work = self.tester_workdir(pend["head"], troot / "tree")
                sandbox = {"root": troot, "hide": [self.ctl, self.root, HARNESS_REPO, Path.home() / ".claude"]}
                pf = getattr(self.model, "preflight", None)       # a refused tester never ran: before test_start
                if pf:
                    pf(sandbox, work)
                self.emit("test_start", task, sha=pend["head"],
                          detail={"tester": tester, "build_id": pend["build_id"]})
                res = self.model("test", prompt, cwd=work, agent_id=tester, run_id=self.n, sandbox=sandbox,
                                 timeout_s=self.timeout_s, log=self.log / ("test.%d.%s.out" % (self.n, tester)))
            finally:
                RA.shutil.rmtree(troot, ignore_errors=True)
            text = res.get("text") or ""
            verdict = RA.parse_verdict(text) if res.get("rc") == 0 else None
            self.emit("test_end", task, sha=pend["head"], verdict=verdict or "invalid",
                      detail={"tester": tester, "build_id": pend["build_id"], "rc": res.get("rc")})
            if verdict:
                break
        self._bump()
        return verdict, text

    # ---- v3c: review and the done gate
    def review(self, task, pend):
        sha = pend["head"]
        ok, why, _, _ = tester_bound(self.records(), self.arm, task["id"], sha)
        if not ok:                                                # the review requires the tester record (r2)
            raise Refused("no review of %s: %s" % (sha[:12], why))
        diff = self.git("diff", "--no-ext-diff", "--no-textconv", pend["base"], sha)
        r = self.reviewer(task, sha, diff, log=self.log / ("review.%d.out" % self.n)) or {}
        verdict = r.get("verdict") if r.get("verdict") in ("pass", "fail") else "invalid"
        body = {"schema": "v3c.review/1", "task": task["id"], "sha": sha, "verdict": verdict,
                "reviewer": "gpt_consult", "ts": L.now_ts(), "text": (r.get("text") or "")[-20000:]}
        name = "%s.%s.%d.json" % (re.sub(r"[^A-Za-z0-9_.-]", "_", task["id"]), sha[:12], self.n)
        raw = json.dumps(body, indent=1, sort_keys=True).encode()
        f = self.reviews / name
        f.with_suffix(".tmp").write_bytes(raw)
        os.replace(f.with_suffix(".tmp"), f)
        self.emit("critic_round", task, sha=sha, verdict=verdict, detail={
            "kind": REVIEW_KIND, "reviewer": "gpt_consult", "record": name,
            "record_sha256": hashlib.sha256(raw).hexdigest(), "build_id": pend["build_id"]})
        self._bump()
        return verdict, body["text"]

    def close(self, task, sha):
        """v3c's close: through the done gate, every attempt logged. -> (ok, why). v3's close is the build_end."""
        if self.arm != "v3c":
            raise Refused("close() is v3c's done gate; a v3 close is the helper's own (build_end via close)")
        ok, why = done_gate(self.records(), self.arm, task["id"], sha, self.reviews)
        self.emit("pass_end", task, sha=sha if isinstance(sha, str) and sha.strip() else None,
                  verdict="done" if ok else "refused", detail={"role": "close", "why": why})
        self._bump()
        return ok, why

    # ---- one task, start to end
    def work(self, task):
        """Work one task in this clone. -> {"outcome": closed|done|live_owed|parked|stop, ...}."""
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        lockp = self.lock_dir / ("%s.lock" % self.arm)
        lockf = open(lockp, "w")
        try:
            fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lockf.close()
            raise Refused("another %s procedure holds %s" % (self.arm, lockp))
        try:
            RA.reap_stale_pass(self.pidfile)
            base = self.git("rev-parse", "HEAD")
            feedback, history = "", []
            for attempt in range(1, MAX_TRIES + 1):
                if (self.ctl / "STOP").exists():
                    return {"outcome": "stop", "history": history}
                pend, why = self.build(task, base, feedback)
                if pend is None:
                    history.append(("build", why))
                    feedback = why
                    continue
                verdict, text = self.test(task, pend)
                history.append(("test", verdict))
                if verdict != "pass":
                    feedback = "tester helper on %s: %s\n%s" % (pend["head"], (verdict or "no verdict").upper(),
                                                                 text.strip()[-3000:])
                    continue
                if task.get("live", "none") not in (None, "none"):
                    self.status("live owed: %s %s" % (task["id"], pend["head"][:12]))
                    return {"outcome": "live_owed", "sha": pend["head"], "history": history}
                if self.arm == "v3":
                    self.status("closed and tested: %s %s" % (task["id"], pend["head"][:12]))
                    return {"outcome": "closed", "sha": pend["head"], "history": history}
                rv, rtext = self.review(task, pend)
                history.append(("review", rv))
                ok, why = self.close(task, pend["head"])
                history.append(("close", why))
                if ok:
                    self.status("done: %s %s" % (task["id"], pend["head"][:12]))
                    return {"outcome": "done", "sha": pend["head"], "history": history}
                feedback = why + ("\nreview findings:\n%s" % rtext.strip()[-3000:] if rv != "pass" else "")
            self.status("parked %s after %d tries" % (task["id"], MAX_TRIES))
            return {"outcome": "parked", "history": history}
        finally:
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()


def replay_work(arm, model, writer, ctl=None, load=None, **kw):
    """A `work(arm, task_id, clone)` for arena_replay.run_schedule: one Procedure per task clone."""
    if load is None:
        import arena_tasks as A
        load = A.load_frozen

    def work(arm_, task_id, clone):
        if arm_ != arm:
            raise Refused("replay_work for %s asked to work arm %s" % (arm, arm_))
        return Procedure(arm, clone, Path(ctl or DEFAULT_CTL) / arm, model=model, writer=writer, **kw).work(
            load(task_id))
    return work


# ------------------------------------------------------------------------------------------------ CLI
class SignedWriter(RA.SignedWriter):
    """The signed log of one arm, read only after its anchor/witness/roster check passes (fail closed)."""

    def __init__(self, arm, p=None, cap=None):
        super().__init__(p, cap)
        self.arm = arm

    def records(self):
        rep = L.report(self.w.p, self.w._token).get(self.arm) or {}
        if rep.get("refused"):
            raise Refused("refused: the signed %s log fails its anchor check: %s" % (
                self.arm, "; ".join(str(x) for x in rep["refused"])[:600]))
        return self.w.accepted(self.arm)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("run", "check-tested", "done-gate"))
    ap.add_argument("--arm", required=True, choices=ARMS)
    ap.add_argument("--clone", help="the replay clone (run)")
    ap.add_argument("--task", help="frozen task id (run, done-gate)")
    ap.add_argument("--sha", help="the sha to close (done-gate)")
    ap.add_argument("--ctl", default=os.environ.get("V3_CTL", DEFAULT_CTL))
    ap.add_argument("--model-cmd", default=os.environ.get("V3_MODEL_CMD"))
    a = ap.parse_args(argv)
    if os.environ.get("RM_ARM"):
        print("refused: the procedure is harness code; run it without RM_ARM")
        return 2
    import arena_tasks as A
    p = A.paths()
    ctl = Path(a.ctl) / a.arm
    with L.harness_pass(p) as cap:
        w = SignedWriter(a.arm, p, cap)
        if a.action == "check-tested":
            require_tested(w.records(), a.arm)
            print("every %s replay build has a test_start from a different agent" % a.arm)
            return 0
        if a.action == "done-gate":
            ok, why = done_gate(w.records(), a.arm, a.task, a.sha, ctl / "reviews")
            print(why)
            return 0 if ok else 1
        root = Path(a.clone or "").resolve()
        if not a.clone or Path.cwd().resolve().is_relative_to(root):
            print("refused: give --clone, and run from outside it")
            return 2
        pr = Procedure(a.arm, root, ctl, model=CmdModel(a.model_cmd, a.arm), writer=w,
                       timeout_s=float(os.environ.get("V3_PASS_TIMEOUT_S", PASS_TIMEOUT_S)))
        out = pr.work(A.load_frozen(a.task, p))
        print(json.dumps(out, indent=1))
    return 0 if out["outcome"] in ("closed", "done", "live_owed") else 3


if __name__ == "__main__":
    sys.exit(main())
