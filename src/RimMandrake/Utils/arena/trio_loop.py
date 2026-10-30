#!/usr/bin/env python3
"""trio_loop.py - the trio arm's build half (design/RimMandrake/testpilot_merged_2026-10-29.md section 2.1 L2-L5).

FOUNDRY runs a fresh builder per item, then AT ONCE a fresh blind critic (a different agent) that runs the item's
offline tests itself and reviews code, plan and evidence. Round cap: 2 rounds, then ONE automatic simplify-or-split
pass, then 2 more rounds, then the item parks to the Conductor with the last verdict. The loop script runs the
gate and counts the rounds; nothing is self-reported.

A ROUND is one build pass of the item (or of one of its parts): it is counted from the signed arena log (the
trio's `pass_start` records with role "build" for the item id), so a restart, a deleted state.json or a pass killed
mid-way never gives a 5th round (a killed pass is a spent round: fail closed). Each round ends in one `critic_round`
record (detail.kind "verdict"): accept / reject / invalid, with the sha, the git tree and the critic that saw it.

  rounds 1-2   build -> critic ("reject" or a failed build/final gate consumes the round)
  after 2      ONE simplify pass (critic_round kind "simplify"): a fresh agent rewrites the spec smaller
               ({"action": "simplify"}) or splits it into 2-3 parts ({"action": "split"}); invalid output keeps it
  rounds 3-4   the simplified spec or the parts in order; the parts share the item's remaining budget (2 rounds)
  after 4      park (critic_round kind "park"; one line appended to <ctl>/parks.jsonl for the Conductor; the
               candidate kept on branch trio/failed/<id>); never a 5th round

Ids, priority, area, proof, live and base_sha always come from the FROZEN task: a simplify/split only rewrites
prompt and criteria. Parts build cumulatively on the work branch; only the last part goes through the final gate
(the frozen proof) and publishes, so the parts together must deliver the parent's outcome.

Inherited from ralph_a_loop (subclassed, not edited): STOP file, runway refusal, sync, precheck, busy-clone check,
pidfile reaping, the gate run by the loop, build_end -> test_start AT ONCE, the hard check (a build pass is refused
while any trio build_end lacks a test_start by a different agent), recovery of a pending build from the log.

Binding (L4): `_final` publishes only when the item's latest round record is an accept whose sha is the head being
merged, whose tree is that head's tree, by a critic that is not the builder, and the work branch still points at
that sha after the gate; it then merges THAT sha (--ff-only). Anything else writes STOP and publishes nothing.
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_eventlog as L  # noqa: E402
import ralph_a_loop as RA  # noqa: E402
from ralph_a_loop import Refused, NotTested, agent_key, neutral_id  # noqa: E402,F401

ARM = "trio"
ARM_DIR = HERE / "trio"
ROUND_CAP = 4
SIMPLIFY_AFTER = 2
CRITIC_TRIES = 2
MAX_PARTS = 3
DEFAULT_CTL = "/mnt/d/ClaudeWork/rimmandrake/trio"
FAILED_BRANCH = "trio/failed/%s"
ROUND2_BRANCH = "trio/round2/%s"
SPEC_KEEP = ("prompt", "criteria")            # the only fields a simplify/split may change


# ------------------------------------------------------------------------------------------------ the hard check
def canon_records(recs):
    """The trio's records, builder/tester ids folded with ralph_a's agent_key, a repeated build_end of the same
    (task, build_id, sha) dropped (same rules as ralph_a_loop.canon_records, for arm trio)."""
    out, seen = [], set()
    for r in L.ordered([r for r in recs if r.get("arm") == ARM]):
        d = r.get("detail")
        if isinstance(d, dict) and r.get("event") in ("build_end", "test_start"):
            k = "builder" if r["event"] == "build_end" else "tester"
            if k in d:
                r = dict(r, detail=dict(d, **{k: agent_key(d[k])}))
            if r["event"] == "build_end":
                key = (L.norm_id(r.get("task")), L.norm_id(str(d.get("build_id"))), r.get("sha"))
                if key in seen:
                    continue
                seen.add(key)
        out.append(r)
    return out


def require_tested(recs):
    """NotTested unless every trio build_end has a later test_start of that build by a different agent (section
    2.3: a builder whose last candidate has no test_start from a different agent gets no new pass)."""
    mine = canon_records(recs)
    bad = L.untested_builds(mine)
    if bad:
        b = bad[0]
        raise NotTested("refused: trio build %s of %s (builder %s) has no test_start from a different agent; the "
                        "critic must start before the next build pass" % (
                            (b.get("detail") or {}).get("build_id") or b.get("sha"), b.get("task"),
                            (b.get("detail") or {}).get("builder")))
    same = L.flagged_same_agent(mine)
    if same:
        raise NotTested("refused: test_start by the builder itself (%s)" % (same[0].get("detail") or {}).get("tester"))


def _task_recs(recs, tid, event=None, kind=None):
    t = L.norm_id(tid)
    out = []
    for r in canon_records(recs):
        if L.norm_id(r.get("task")) != t or (event and r.get("event") != event):
            continue
        if kind and (r.get("detail") or {}).get("kind") != kind:
            continue
        out.append(r)
    return out


def rounds_used(recs, tid):
    """Build passes STARTED for the item (all parts): the round count. Read from the log, never from state."""
    return sum(1 for r in _task_recs(recs, tid, "pass_start") if (r.get("detail") or {}).get("role") == "build")


def verdicts(recs, tid):
    return _task_recs(recs, tid, "critic_round", "verdict")


def simplify_rec(recs, tid):
    s = _task_recs(recs, tid, "critic_round", "simplify")
    return s[-1] if s else None


RIMFLOW_CLI = Path(__file__).resolve().parents[2] / "rimflow" / "cli.py"
PARK_FOR = "BENCH"          # the Conductor's ledger seat (infrastructure/agents/CONDUCTOR.md: still seat BENCH)


def park_item_name(tid, force_hash=False):
    """PARKED-style rimflow name for a park: the task's subject words + _VET_PARKED (intent VET), within the 44-char cap
    and namecheck's 3-7 word cap (so at most 5 task words), no trailing number (the retired legacy form); a hash tail
    keeps a truncated name unique. force_hash gives the disambiguated variant used when the plain name belongs to
    another item (two ids differing only in a trailing number share the plain name)."""
    import re
    words = [w for w in re.sub(r"[^A-Z0-9]+", "_", tid.upper()).split("_") if w]
    while words and words[-1].isdigit():
        words.pop()
    suffix, name = "VET_PARKED", "_".join(words)
    if force_hash or len(words) > 5 or len(name) + 1 + len(suffix) > 44:
        h = hashlib.sha1(tid.encode()).hexdigest()[:3].upper()
        keep = []
        for w in words:
            if len(keep) >= 4 or len("_".join(keep + [w])) + 1 + len(h) + 1 + len(suffix) > 44:
                break
            keep.append(w)
        name = "_".join(keep + [h])
    return "%s_%s" % (name, suffix)


def park_item_text(line):
    return ("task %s (%s) parked after %s rounds. last verdict %s at sha %s. why: %s. evidence branch: %s. "
            "audit line: parks.jsonl. NEXT: read the branch and the critic note, then retry, split or drop the task."
            % (line.get("task"), line.get("priority"), line.get("rounds"), line.get("last_verdict"),
               line.get("last_sha"), (line.get("last_why") or "")[:600].replace("\n", " "), line.get("evidence")))


def parked(recs, tid):
    return bool(_task_recs(recs, tid, "critic_round", "park"))


def parse_simplify(text):
    """The simplify agent's LAST JSON object that starts with {"action": ...} -> a checked dict, or None."""
    text = text or ""
    i = text.rfind('{"action"')
    if i < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[i:])
    except ValueError:
        return None
    ok = lambda s: isinstance(s, dict) and all(isinstance(s.get(k), str) and s[k].strip() for k in SPEC_KEEP)
    if obj.get("action") == "simplify" and ok(obj.get("spec")):
        return {"action": "simplify", "spec": {k: obj["spec"][k] for k in SPEC_KEEP}}
    parts = obj.get("parts")
    if obj.get("action") == "split" and isinstance(parts, list) and 2 <= len(parts) <= MAX_PARTS \
            and all(ok(p) for p in parts):
        return {"action": "split", "parts": [{k: p[k] for k in SPEC_KEEP} for p in parts]}
    return None


# ------------------------------------------------------------------------------------------------ writers / model
class SignedWriterT(RA.SignedWriter):
    def records(self):
        rep = L.report(self.w.p, self.w._token).get(ARM) or {}
        if rep.get("refused"):
            raise Refused("refused: the signed %s log fails its anchor check: %s" % (ARM, "; ".join(
                str(x) for x in rep["refused"])[:600]))
        return self.w.accepted(ARM)


class CmdModelT(RA.CmdModel):
    """ralph_a's CmdModel with the child tagged RM_ARM=trio (build and simplify roles)."""

    def __call__(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ARENA_", "RALPH_A_CTL", "TRIO_CTL"))}
        env.update(RALPH_A_ROLE=role, RALPH_A_AGENT_ID=agent_id, RM_ARM=ARM)
        rc = self.spawn(role, self.argv, env, cwd=cwd, sandbox=sandbox, agent_id=agent_id, log=log, prompt=prompt,
                        timeout_s=timeout_s)               # sandboxed: arm_sandbox via RA.CmdModel.spawn
        return self.result(log, rc)


def cmd_gate_t(task, base, head, phase, *, root, log):
    cmd = os.environ.get("RALPH_A_GATE_CMD")
    argv = shlex.split(cmd) if cmd else [sys.executable, str(HERE / "arena_gate.py")]
    argv += ["--task", task["id"], "--base", base, "--head", head, "--arm", ARM, "--repo", str(root)]
    r = subprocess.run(argv, cwd=str(RA.HARNESS_REPO), capture_output=True, text=True, timeout=3 * 3600)
    Path(log).write_text(r.stdout + "\n--- stderr\n" + r.stderr)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {"verdict": "invalid", "steps": {}, "why": "gate printed no JSON record (rc %s)" % r.returncode}


def precheck_t(root, log):
    r = subprocess.run([sys.executable, "src/RimMandrake/Utils/run_selftests.py", "--quick"], cwd=str(root),
                       capture_output=True, text=True, timeout=3600, env=dict(os.environ, RM_ARM=ARM))
    Path(log).write_text(r.stdout + r.stderr)
    return RA.precheck_verdict(r.returncode, r.stdout)


def default_critic():
    import arena_critic_calib as CC
    return CC.L4OpusCritic()


def critic_base():
    import arena_critic_calib as CC
    return CC.work_base()


def _critic_input(**kw):
    try:
        import arena_critic_calib as CC
        return CC.CriticInput(**kw)
    except ImportError:                       # pragma: no cover - the calib module ships beside this one
        return type("CriticInput", (), kw)()


def live_plan_refusal(task):
    """Why a task's live TestPilot step may not run (arena_tasks.live_plan_refusal: a live task without a valid
    frozen `live_plan`), or None. Fail closed: the offline proof is never substituted for a live plan."""
    import arena_tasks as A                   # lazy: the census module pulls in the ledger model
    return A.live_plan_refusal(task)


class TestPilotLane:
    """The live half: a critic-accepted candidate of a live task is enqueued on TestPilot; the result is the newest
    record of that item's candidate for this sha (resolved verdict; parked/quarantined count as a fail)."""

    def __init__(self, root=None):
        import testpilot as TP
        self.TP = TP
        self.p = TP.ppaths(root) if root else TP.ppaths()

    def publish(self, task, sha, builder, files):
        bad = live_plan_refusal(task)
        if bad or task.get("live", "none") == "none":
            raise Refused("refused: %s not published to TestPilot: %s" % (task["id"], bad or "it is live: none"))
        self.TP.enqueue(self.p, task["id"], sha, builder, task["live_plan"], changed_files=files)

    def result(self, task, sha):
        mine = [c for c in self.TP.candidates(self.p) if c.get("item") == task["id"] and c.get("sha") == sha]
        if not mine:
            return None
        c = max(mine, key=lambda c: int(c.get("attempt") or 0))
        r = self.TP.states(self.p).get(c["cand"]) or {}
        st = r.get("state")
        if st == "resolved":
            return {"verdict": r.get("verdict"), "why": r.get("why"), "run_id": c["cand"]}
        if st in ("parked", "quarantined", "superseded"):
            return {"verdict": "fail", "why": "testpilot %s" % st}
        return None


# ------------------------------------------------------------------------------------------------ the loop
class TrioLoop(RA.Loop):
    def __init__(self, root, ctl, tasks, *, model, critic=None, **kw):
        kw.setdefault("new_id", lambda role: "%s-%s-%s" % (ARM, role, uuid.uuid4().hex[:12]))
        if kw.get("gate") is None:
            kw["gate"] = lambda t, b, h, ph, log: cmd_gate_t(t, b, h, ph, root=self.root, log=log)
        if kw.get("precheck") is None:
            kw["precheck"] = lambda log: precheck_t(self.root, log)
        if kw.get("tester_tmp") is None:
            kw["tester_tmp"] = str(critic_base())
        inner = model
        self._inner_model = inner
        super().__init__(root, ctl, tasks, model=lambda role, prompt, **k: inner(
            role, self.build_prompt(prompt) if role == "build" else prompt, **k), **kw)
        if hasattr(inner, "pidfile"):
            inner.pidfile = self.pidfile
        self.critic = critic if critic is not None else default_critic()
        inner_gate = self.gate
        self.gate = lambda t, b, h, ph, log: self.part_gate(inner_gate, t, b, h, ph, log)
        (self.ctl / "specs").mkdir(parents=True, exist_ok=True)

    # ---- identity, records
    def emit(self, event, task, **kw):
        return self.writer.emit(ARM, event, lane="build", run_id="%s.%s" % (ARM, self.state["n"]),
                                task=task["id"], **kw)

    def recs(self):
        return self.writer.records()

    def frozen(self):
        i = self.state["task_i"]
        return self.tasks[i] if i < len(self.tasks) else None

    def rounds(self, tid):
        return rounds_used(self.recs(), tid)

    def build_prompt(self, prompt):
        head = (RA.ARM_DIR / "PROMPT.md").read_text()
        if prompt.startswith(head):
            prompt = (ARM_DIR / "PROMPT.md").read_text() + prompt[len(head):]
        t = self.task() or {}
        k = self.rounds(t.get("id")) if t else 0
        return prompt + "\n## ROUND\nthis is round %d of at most %d for %s%s\n" % (
            k, ROUND_CAP, t.get("id"), (" (%s)" % t["_part_label"]) if t.get("_part_label") else "")

    # ---- the effective task: frozen + simplified spec / current part
    def part_index(self, tid, spec):
        """Parts accepted since the simplify record, in order: the next part is the first not accepted."""
        recs = self.recs()
        s = simplify_rec(recs, tid)
        if not spec or spec.get("action") != "split" or s is None:
            return 0
        seq = canon_records(recs)
        after = seq[seq.index(s) + 1:] if s in seq else []
        done = {(r.get("detail") or {}).get("part") for r in after
                if r.get("event") == "critic_round" and (r.get("detail") or {}).get("kind") == "verdict"
                and r.get("verdict") == "accept" and L.norm_id(r.get("task")) == L.norm_id(tid)}
        i = 0
        while i in done:
            i += 1
        return min(i, len(spec["parts"]) - 1)

    def task(self):
        t = self.frozen()
        if t is None:
            return None
        s = simplify_rec(self.recs(), t["id"])
        spec = None
        if s is not None:
            f = self.ctl / "specs" / ("%s.json" % t["id"])
            want = (s.get("detail") or {}).get("spec_sha256")
            if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != want:
                raise Refused("refused: %s's simplified spec %s is missing or is not the one the log recorded"
                              % (t["id"], f))
            spec = json.loads(f.read_text())
        if not spec or spec.get("action") == "keep":
            return dict(t, _part=None, _last=True, _part_label=None)
        if spec["action"] == "simplify":
            return dict(t, prompt=spec["spec"]["prompt"], criteria=spec["spec"]["criteria"], _part=None,
                        _last=True, _part_label="simplified")
        n = len(spec["parts"])
        i = self.part_index(t["id"], spec)
        p = spec["parts"][i]
        prompt = ("PART %d of %d of a split item. The parts together must deliver the parent outcome:\n%s\n\n"
                  "Parts before this one are already on the work branch. THIS PART:\n%s" % (
                      i + 1, n, t["prompt"], p["prompt"]))
        crit = p["criteria"] + (("\n\nAND THE PARENT'S CRITERIA (this is the last part):\n" + t["criteria"])
                                if i == n - 1 else "")
        return dict(t, prompt=prompt, criteria=crit, _part=i, _last=(i == n - 1),
                    _part_label="part %d of %d" % (i + 1, n))

    def part_gate(self, inner, task, base, head, phase, log):
        """A non-last part cannot meet the parent's frozen proof yet: on the BUILD phase its proof step is NA."""
        rec = inner(task, base, head, phase, log)
        if phase == "build" and not task.get("_last", True) and isinstance(rec, dict) \
                and isinstance(rec.get("steps"), dict) and "proof" in rec["steps"]:
            rec = dict(rec, steps=dict(rec["steps"], proof={"status": "NA",
                                                             "why": "part %s: the parent proof is the last part's"
                                                                    % task.get("_part_label")}))
        return rec

    # ---- one step
    def step(self):
        if (self.ctl / "STOP").exists():
            return self.status("STOP")
        fz = self.frozen()
        if fz is not None and parked(self.recs(), fz["id"]):   # killed after the park record, before state was saved
            self._file_park_item(fz["id"])                       # a filing that failed last time is retried
            return self._advance(fz, "parked %s (from the log)" % fz["id"])   # before task(): a lost spec file cannot wedge it
        task = self.task()
        if task is None:
            return self.status("done: no task left")
        bad = live_plan_refusal(task)
        if bad and not self.state.get("lane_wait"):    # before any round is spent: no plan, no live verdict, ever
            return self._park(task, "no valid live_plan: " + bad)
        if self.state.get("lane_wait"):
            return self._lane_step(task)
        why = self.runway_refusal()
        if why:
            return self.status("runway: " + why)
        self._recover(task)
        if self.state.get("pending"):
            return self.tester_pass(task)
        k = self.rounds(task["id"])
        if k >= ROUND_CAP:
            return self._park(task, "round cap %d reached" % ROUND_CAP)
        if k >= SIMPLIFY_AFTER and simplify_rec(self.recs(), task["id"]) is None:
            return self.simplify_pass(task)
        return self.build_pass(task)

    def _recover(self, task):
        """ralph_a's recovery from the signed log, over the trio's records."""
        if self.state.get("pending") or self.state.get("lane_wait"):
            return None
        recs = canon_records(self.recs())
        tid = L.norm_id(task["id"])
        last = None
        for i, r in enumerate(recs):
            if r.get("event") == "build_end" and L.norm_id(r.get("task")) == tid:
                last = i
        if last is None:
            return None
        b = recs[last]
        d = b.get("detail") or {}
        bid = d.get("build_id")
        if any(r.get("event") in ("test_start", "test_end") and (r.get("detail") or {}).get("build_id") == bid
               for r in recs[last + 1:]):
            return None
        sha = b.get("sha")
        if not (isinstance(sha, str) and d.get("base") and d.get("builder")) or \
                RA.SG.git_run(self.root, "cat-file", "-e", sha + "^{commit}",
                              capture_output=True).returncode != 0 or \
                RA.SG.git_run(self.root, "merge-base", "--is-ancestor", sha, RA.MAIN,
                              capture_output=True).returncode == 0:
            return None
        self.state["pending"] = {"build_id": bid, "base": d["base"], "head": sha, "builder": d["builder"],
                                 "recovered": True}
        self._save()
        self.status("recovered from the log: build %s has no critic yet; the critic runs next" % bid)
        return bid

    # ---- build
    def _round_open(self, tid):
        recs = self.recs()
        return rounds_used(recs, tid) > len(verdicts(recs, tid))

    def _verdict(self, task, verdict, sha=None, **detail):
        k = self.rounds(task["id"])
        d = dict(kind="verdict", round=k, part=task.get("_part"), **detail)
        return self.emit("critic_round", task, sha=sha, verdict=verdict, detail={a: b for a, b in d.items()
                                                                                  if b is not None})

    def build_pass(self, task):
        require_tested(self.recs())                                # HARD CHECK (trio records)
        k = self.rounds(task["id"])
        if k >= ROUND_CAP:
            raise Refused("refused: %s has used %d of %d rounds; it parks, it gets no 5th" % (task["id"], k, ROUND_CAP))
        if self._round_open(task["id"]):                           # a pass killed before its verdict: a spent round
            self._verdict(task, "invalid", stage="killed", why="build pass started and never reached a verdict")
        return super().build_pass(task)

    def _failed(self, task, base, head, why, n, record=True):   # record: the base loop's failed-sha ledger; the trio keeps rounds instead
        if self._round_open(task["id"]):                           # a build-side failure ends the round
            self._verdict(task, "reject", sha=head, stage="build", why=why[:600])
        k = self.rounds(task["id"])
        self.state["pending"] = None
        self._fail_note(task, "item %s round %d of %d%s\nwhy: %s\nbase %s head %s\nlogs %s (pass %d)\n" % (
            task["id"], k, ROUND_CAP, (" (%s)" % task["_part_label"]) if task.get("_part_label") else "", why,
            base, head, self.log, n))
        self._save()
        if k >= ROUND_CAP:
            return self._park(task, why)
        return self.status("failed %s round %d of %d: %s" % (task["id"], k, ROUND_CAP, why[:300]))

    # ---- simplify-or-split (once, after round 2)
    def simplify_pass(self, task):
        frozen = self.frozen()
        n = self.state["n"]
        agent = self.new_id("simplify")
        last = [dict(round=(r.get("detail") or {}).get("round"), verdict=r.get("verdict"),
                     why=((r.get("detail") or {}).get("why") or "")[:1500]) for r in verdicts(self.recs(), task["id"])]
        prompt = ((ARM_DIR / "SIMPLIFY.md").read_text() + "\n## FROZEN SPEC\n" +
                  json.dumps(RA.public_spec(frozen), indent=1, sort_keys=True) + "\n\n## ROUND VERDICTS\n" +
                  json.dumps(last, indent=1) + "\n\n## LAST FAILURE\n" + self._note("last_failure.md")[-4000:] +
                  "\n\n## LAST CRITIC VERDICT\n" + self._note("last_verdict.md")[-4000:] + "\n")
        troot = Path(tempfile.mkdtemp(prefix="trio-simplify-", dir=str(self.ctl)))
        try:
            work = self._export_tree(RA.MAIN, troot / "tree")
            self.status("simplify pass running (%s)" % agent)
            try:
                res = self.model("simplify", prompt, cwd=work, agent_id=agent, run_id=n, timeout_s=self.timeout_s,
                                 log=self.log / ("simplify.%d.out" % n))
            finally:
                self.release()
        finally:
            shutil.rmtree(troot, ignore_errors=True)
        self.state["n"] = n + 1
        got = parse_simplify(res.get("text")) if res.get("rc") == 0 else None
        spec = got or {"action": "keep"}
        spec.update(id=frozen["id"], frozen_sha256=hashlib.sha256(json.dumps(
            RA.public_spec(frozen), sort_keys=True).encode()).hexdigest())
        f = self.ctl / "specs" / ("%s.json" % frozen["id"])
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(spec, indent=1, sort_keys=True))
        os.replace(tmp, f)
        wip = self.git("rev-parse", "--verify", "-q", RA.WIP, check=False)
        if wip:                                                    # rounds 1-2's candidate kept as evidence
            self.git("branch", "-f", ROUND2_BRANCH % frozen["id"], wip)
            if self.git("rev-parse", "--abbrev-ref", "HEAD", check=False) == RA.WIP:
                self.git("switch", "-q", RA.MAIN)
            self.git("branch", "-f", RA.WIP, RA.MAIN)
        self._clear_notes()
        self.emit("critic_round", frozen, verdict=spec["action"], detail={
            "kind": "simplify", "action": spec["action"], "agent": agent, "rc": res.get("rc"),
            "parts": len(spec.get("parts") or []) or None, "spec_sha256": hashlib.sha256(
                f.read_bytes()).hexdigest(), "round": self.rounds(frozen["id"])})
        self._save()
        return self.status("simplified %s: %s" % (frozen["id"], spec["action"]))

    # ---- park
    def _advance(self, task, what):
        self.state.update(pending=None, lane_wait=None, task_i=self.state["task_i"] + 1)
        self._clear_notes()
        self._save()
        return self.status(what)

    def _park(self, task, why):
        tid = task["id"]
        recs = self.recs()
        if parked(recs, tid):
            self._file_park_item(tid)
            return self._advance(task, "parked %s" % tid)
        vs = verdicts(recs, tid)
        lastv = vs[-1] if vs else {}
        k = rounds_used(recs, tid)
        wip = self.git("rev-parse", "--verify", "-q", RA.WIP, check=False) if k else None   # no round: no candidate
        if wip:
            self.git("branch", "-f", FAILED_BRANCH % tid, wip)
            if self.git("rev-parse", "--abbrev-ref", "HEAD", check=False) == RA.WIP:
                self.git("switch", "-q", RA.MAIN)
            self.git("branch", "-f", RA.WIP, RA.MAIN)
        line = {"ts": L.now_ts(), "task": tid, "priority": self.frozen().get("priority"), "rounds": k,
                "last_verdict": lastv.get("verdict"), "last_why": ((lastv.get("detail") or {}).get("why") or why)[:1500],
                "last_sha": lastv.get("sha"), "evidence": FAILED_BRANCH % tid if wip else None,
                "critic_note": self._note("last_verdict.md")[-3000:]}
        pf = self.ctl / "parks.jsonl"
        have = pf.read_text().splitlines() if pf.is_file() else []
        if not any(json.loads(x).get("task") == tid for x in have if x.strip()):   # killed before the record: once only
            with open(pf, "a") as fh:
                fh.write(json.dumps(line, sort_keys=True) + "\n")
        self.emit("critic_round", task, verdict="park", sha=wip or None, detail={
            "kind": "park", "rounds": k, "last_verdict": lastv.get("verdict"), "to": "conductor", "why": why[:600]})
        self._file_park_item(tid)
        return self._advance(task, "parked %s after %d rounds (evidence %s): %s" % (tid, k, line["evidence"], why[:200]))

    def _file_park_item(self, tid):
        """File the park as a rimflow item for the Conductor's queue (the Conductor works through rimflow items;
        parks.jsonl stays the audit log). Idempotent: <ctl>/parks_filed.json remembers the item per task, and an
        item that already exists counts as filed. Never raises: a failed filing is retried on the next visit."""
        try:
            mark = self.ctl / "parks_filed.json"
            try:
                done = json.loads(mark.read_text()) if mark.is_file() else {}
            except ValueError:
                done = {}          # a torn marker file: the exists-check keeps a re-filing idempotent
            if tid in done:
                return done[tid]
            pf = self.ctl / "parks.jsonl"
            line = next((json.loads(x) for x in (pf.read_text().splitlines() if pf.is_file() else [])
                         if x.strip() and json.loads(x).get("task") == tid), None)
            if line is None:
                return None
            name = park_item_name(tid)
            have = self._rimflow("namecheck", name)
            if " exists:" in have.stdout and ("caused_by=%s " % tid) not in self._rimflow("show", name).stdout:
                name = park_item_name(tid, force_hash=True)       # the plain name is another task's item: never adopt it
                have = self._rimflow("namecheck", name)
            if " exists:" not in have.stdout:   # real namecheck exits 0 for a free name too: only "exists:" means filed
                have = self._rimflow("file", name, "--for", PARK_FOR, "--kind", "task", "--needs", "offline",
                                     "--title", "Trio parked %s after %s rounds: look at trio/failed branch, then retry, "
                                     "split or drop" % (tid, line.get("rounds")),
                                     "--spec", str(self._park_spec(tid, line)), "--caused-by", tid, "--why",
                                     "trio_loop park: the Conductor works through rimflow items (delegated design default)")
                if have.returncode != 0 and "caused" in (have.stdout + have.stderr).lower():
                    have = self._rimflow("file", name, "--for", PARK_FOR, "--kind", "task", "--needs", "offline",
                                         "--title", "Trio parked %s" % tid, "--spec", str(self._park_spec(tid, line)),
                                         "--why", "trio_loop park (caused-by %s is not an item)" % tid)
                if have.returncode == 0:   # --spec is only a provenance path: the verdict/why/sha/branch go in a note the Conductor sees
                    nt = self._rimflow("note", name, "--text", park_item_text(line), "--why", "trio_loop park detail")
                    if nt.returncode != 0:
                        print("trio: park note for %s not added: %s" % (name, (nt.stdout + nt.stderr)[-300:]), file=sys.stderr)
                if have.returncode != 0:
                    print("trio: park item %s not filed: %s" % (name, (have.stdout + have.stderr)[-300:]), file=sys.stderr)
                    return None
            done[tid] = name
            mark.write_text(json.dumps(done, sort_keys=True))
            return name
        except Exception as e:  # noqa: BLE001  a filing failure never loses the park or stops the loop
            print("trio: park item for %s not filed: %s: %s" % (tid, type(e).__name__, e), file=sys.stderr)
            return None

    def _park_spec(self, tid, line):
        """The park text as a file (rimflow --spec takes a path): <ctl>/parks/<tid>.md."""
        d = self.ctl / "parks"
        d.mkdir(parents=True, exist_ok=True)
        f = d / ("%s.md" % tid)
        f.write_text(park_item_text(line) + "\n")
        return f

    def _rimflow(self, *argv):
        cmd = shlex.split(os.environ.get("TRIO_RIMFLOW_CMD") or "") or [sys.executable, str(RIMFLOW_CLI)]
        env = dict(os.environ)
        env.setdefault("RIMFLOW_SEAT", "FOUNDRY")
        return subprocess.run(cmd + list(argv), capture_output=True, text=True, timeout=120, env=env)

    # ---- the critic (in place of ralph_a's tester)
    def tester_pass(self, task):
        why = self.runway_refusal()
        if why:
            return self.status("runway: " + why)
        pend = self.state["pending"]
        done = self._logged_verdict(task, pend)
        if done is not None:
            return done
        n = self.state["n"]
        diff = self.git("diff", *RA.NO_DRIVER, pend["base"], pend["head"])
        tree_id = self.git("rev-parse", pend["head"] + "^{tree}")
        criteria = task["criteria"]
        if task.get("_last", True) and task.get("_part_label"):
            criteria += "\n\nTHE ITEM'S FROZEN CRITERIA (must hold too):\n" + self.frozen()["criteria"]
        v, critic = None, None
        for _ in range(CRITIC_TRIES):
            critic = self.new_id("critic")
            if agent_key(critic) == agent_key(pend["builder"]) or not agent_key(critic):
                raise Refused("critic id %r equals the builder's: refused" % critic)
            work = self._tester_root()                 # fresh per attempt, never nested with ctl/clone/harness
            try:
                tree = self.tester_workdir(pend["head"], work / "tree")
                self.emit("test_start", task, sha=pend["head"], detail={
                    "tester": critic, "build_id": pend["build_id"], "role": "critic"})
                self.status("critic pass running (%s on %s)" % (critic, pend["build_id"]))
                try:
                    v = self.critic.review(_critic_input(cid=neutral_id(critic), prompt=task["prompt"],
                                                         criteria=criteria, diff=diff, tree=tree, work=work))
                except Exception as e:  # noqa: BLE001 - a crashed critic is an invalid verdict, never an accept
                    v = type("V", (), {"verdict": "invalid", "reasons": ["critic raised %s: %s" % (
                        type(e).__name__, str(e)[:300])], "meta": {}})()
                finally:
                    self.release()
            finally:
                shutil.rmtree(work, ignore_errors=True)
            verdict = getattr(v, "verdict", None)
            verdict = verdict if verdict in ("accept", "reject") else "invalid"
            self.emit("test_end", task, sha=pend["head"], verdict={"accept": "pass", "reject": "fail"}.get(
                verdict, "invalid"), detail={"tester": critic, "build_id": pend["build_id"], "role": "critic"})
            if verdict != "invalid":
                break
        reasons = [str(x)[:500] for x in (getattr(v, "reasons", None) or [])][:8]
        self.state["n"] = n + 1
        self._verdict(task, verdict, sha=pend["head"], stage="critic", critic=critic, builder=pend["builder"],
                      build_id=pend["build_id"], tree=tree_id, why="; ".join(reasons)[:1500] or None)
        (self.ctl / "last_verdict.md").write_text("critic %s on %s: %s\n%s\n" % (
            critic, pend["build_id"], verdict.upper(), "\n".join("- " + r for r in reasons)))
        if verdict != "accept":
            return self._failed(task, pend["base"], pend["head"], "critic %s: %s" % (
                verdict.upper(), "; ".join(reasons)[:1500]), n)
        return self._after_accept(task, pend, n)

    def _logged_verdict(self, task, pend):
        """Killed after this build's verdict was logged, before state was saved: the logged verdict stands."""
        seen = [v for v in verdicts(self.recs(), task["id"])
                if (v.get("detail") or {}).get("build_id") == pend.get("build_id")]
        if not seen:
            return None
        v, n = seen[-1], self.state["n"]
        if v.get("verdict") != "accept":
            return self._failed(task, pend["base"], pend["head"], "critic %s (from the log): %s" % (
                str(v.get("verdict")).upper(), (v.get("detail") or {}).get("why") or ""), n)
        if (v.get("detail") or {}).get("part") != task.get("_part"):   # an earlier part's accept: that part is done
            self.state["pending"] = None
            self._clear_notes()
            self._save()
            return self.status("accepted %s part %s (from the log); the next part builds next" % (
                task["id"], (v.get("detail") or {}).get("part")))
        return self._after_accept(task, pend, n)

    def _after_accept(self, task, pend, n):
        if not task.get("_last", True):
            self.state["pending"] = None
            self._clear_notes()
            self._save()
            return self.status("accepted %s %s at %s; the next part builds next" % (
                task["id"], task["_part_label"], pend["head"][:12]))
        if task.get("live", "none") != "none":
            bad = live_plan_refusal(task)
            if bad:                                   # step() parks it first; this is the last line of defence
                raise Refused("refused: %s accepted but not published to TestPilot: %s" % (task["id"], bad))
            if self.lane is None:
                raise Refused("task %s needs a live lane and none is configured" % task["id"])
            files = self.git("diff", *RA.NO_DRIVER, "--name-only", pend["base"], pend["head"]).splitlines()
            self.lane.publish(task, pend["head"], pend["builder"], files)
            self.state["lane_wait"] = dict(pend)
            self.state["pending"] = None
            self._save()
            return self.status("waiting on lane for %s %s" % (task["id"], pend["head"][:12]))
        return self._final(task, pend, n)

    # ---- bound publish
    def binding_refusal(self, task, pend):
        vs = verdicts(self.recs(), task["id"])
        if not vs:
            return "no critic verdict for %s" % task["id"]
        v, d = vs[-1], vs[-1].get("detail") or {}
        head = pend["head"]
        if v.get("verdict") != "accept":
            return "the latest round of %s is %r, not an accept" % (task["id"], v.get("verdict"))
        if v.get("sha") != head:
            return "the accept is bound to %s, the candidate is %s" % (str(v.get("sha"))[:12], head[:12])
        if d.get("tree") != self.git("rev-parse", head + "^{tree}"):
            return "the accept's tree is not %s's tree" % head[:12]
        if not agent_key(d.get("critic")) or agent_key(d.get("critic")) == agent_key(pend["builder"]):
            return "the accepting critic %r is not a different agent from builder %r" % (d.get("critic"),
                                                                                        pend["builder"])
        wip = self.git("rev-parse", "--verify", "-q", RA.WIP, check=False)
        if wip != head:
            return "%s is %s, not the accepted %s" % (RA.WIP, (wip or "missing")[:12], head[:12])
        return None

    def _final(self, task, pend, n):
        g = self.gate(task, pend["base"], pend["head"], "final", self.log / ("gate.final.%d" % n))
        ok, why = RA.final_gate_ok(g)
        if not ok:
            return self._failed(task, pend["base"], pend["head"], "final gate: " + why, n)
        bad = self.binding_refusal(task, pend)
        if bad:
            self.state.update(pending=None, lane_wait=None)
            self._save()
            (self.ctl / "STOP").touch()
            return self.status("STOP: accept not bound to the published sha (%s); nothing published" % bad)
        self.git("switch", "-q", RA.MAIN)
        self.git("merge", "-q", "--ff-only", pend["head"])
        now = self.git("rev-parse", "HEAD")
        if now != pend["head"]:                                    # main was already past the accepted sha
            self.git("switch", "-q", RA.WIP)
            self.state.update(pending=None, lane_wait=None)
            self._save()
            (self.ctl / "STOP").touch()
            return self.status("STOP: %s is %s after the merge, not the accepted %s; nothing published" % (
                RA.MAIN, now[:12], pend["head"][:12]))
        pub =subprocess.run(shlex.split(self.publish_cmd), cwd=str(self.root), capture_output=True, text=True)
        self.git("switch", "-q", RA.WIP)
        if pub.returncode != 0:
            self.state["pending"] = None
            self._save()
            (self.ctl / "STOP").touch()
            return self.status("STOP: publish failed after a passed gate (%s)" % pub.stderr.strip()[:200])
        return self._advance(task, "published %s %s" % (task["id"], pend["head"][:12]))


# ------------------------------------------------------------------------------------------------ CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("run", "check-tested", "status"))
    ap.add_argument("--root", required=True, help="the trio arm clone")
    ap.add_argument("--ctl", default=os.environ.get("TRIO_CTL", DEFAULT_CTL))
    ap.add_argument("--tasks", default="", help="comma-separated frozen task ids, worked in order")
    ap.add_argument("--model-cmd", default=os.environ.get("TRIO_MODEL_CMD"))
    ap.add_argument("--max-steps", type=int, default=0)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if os.environ.get("RM_ARM") or Path.cwd().resolve().is_relative_to(root):
        print("refused: the loop is harness code; run it from outside the arm clone, without RM_ARM")
        return 2
    import arena_tasks as A
    p = A.paths()
    with L.harness_pass(p) as cap:
        w = SignedWriterT(p, cap)
        if a.action == "check-tested":
            require_tested(w.records())
            print("every trio build has a test_start from a different agent")
            return 0
        tasks = [A.load_frozen(t, p) for t in a.tasks.split(",") if t]
        if a.action == "status":
            recs = w.records()
            for t in tasks:
                vs = verdicts(recs, t["id"])
                print("%s rounds=%d/%d simplified=%s parked=%s last=%s" % (
                    t["id"], rounds_used(recs, t["id"]), ROUND_CAP, bool(simplify_rec(recs, t["id"])),
                    parked(recs, t["id"]), vs[-1].get("verdict") if vs else None))
            return 0
        lp = TrioLoop(root, a.ctl, tasks, model=CmdModelT(a.model_cmd), writer=w, lane=TestPilotLane(),
                      timeout_s=float(os.environ.get("TRIO_PASS_TIMEOUT_S", RA.PASS_TIMEOUT_S)))
        for r in lp.run(a.max_steps):
            print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
