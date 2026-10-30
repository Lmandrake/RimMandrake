#!/usr/bin/env python3
r"""arena_judge.py — Harness step 4: the blind acceptance judge (Opus + GPT).

Design: design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.3 (the judge is blind), §1.2 (bookkeeping is
stripped before judging), §1.6 (the judge runs from the judge dir and is billed to the harness), §3.4 (blinding);
build ticket ARENA_JUDGES_BUILD_BLIND_TO_THE_ARM (testpilot_merged_2026-10-29.md §6.3 step 4).

    python3 src/RimMandrake/Utils/arena/arena_judge.py judge --task T --clone DIR --base SHA --head SHA --arm X
                                                             --gate GATE.json
    python3 src/RimMandrake/Utils/arena/arena_judge.py report [--day YYYY-MM-DD]

TWO SIDES. The HARNESS side (this process, run by the harness, never by an arm or a judge) knows the arm: it writes
the arm map, neutralises the diff, materialises the tree, and later unblinds the verdicts for the guess report. The
JUDGE side is every process that sees the submission: the Opus run, the GPT run, the tie-break Opus run and the
hidden checks. Every judge-side process is started inside a bubblewrap sandbox (`bwrap --bind / /` with a fresh
tmpfs laid OVER the harness-private directory and over the arm clone root, the judge work dir bound back in), so
the arm map path does not exist for it. No bwrap -> the judge refuses; it never runs unsandboxed.

WHERE THINGS LIVE
  $ARENA_PRIVATE (default ~/.local/state/rm_arena_private, dir 0700, files 0600)
      arm_map.json          judge_id -> {arm, task, base, head, ts}. Harness-only. Refused if it sits inside an
                            arm-readable root, the judge work root or the arena judge dir.
  $ARENA_JUDGE_WORK (default <clone root>/judge, i.e. /home/mandrake/rm/arena/judge: §1.6 bills it to the harness)
      <judge_id>/diff.patch     the neutralised diff (head minus base over `area`)
      <judge_id>/tree/          git archive of head (TREE_PATHS + area dirs), hidden check bodies written over it
      <judge_id>/prompt.md      the one prompt every judge gets (no judge sees another's answer)
      <judge_id>/verdict.json   the blind verdict record: no arm field
  <arena>/judge/hidden/<T>.json  the hidden checks (arena_tasks.py); read by the harness side, never shown to an arm
  <arena>/reports/judge_guess_<day>.json   the arm-guess report (aggregate rates only)

NEUTRALISER. `git diff base head` over the changed paths that match `area` (arena_tasks fnmatch semantics), minus
bookkeeping (arena_tasks.is_bookkeeping, plus arm plans/AGENTS.md). A plain `git diff` holds no commit message; any
trailer line that reached file content (Co-Authored-By, Claude-Session, Signed-off-by, "Generated with") becomes
`<TRAILER>`, session URLs `<SESSION>`, branch refs `<BRANCH>`, the clone path (POSIX, realpath, Windows UNC,
transcript slug) and any `<clone root>/<name>` path `<REPO>`, head/base shas `<SHA>`, and EVERY arm name (all arms,
not only this one, so the redaction is the same for every arm; case- and separator-insensitive) `<ARM>`. Then a leak
scan re-runs over the result; any arm token, clone path or trailer left refuses the submission (NeutraliserLeak).

VERDICT. Hidden checks first: one failing -> reject (a known-bad replay output never reaches a model); one that could
not run -> invalid. Checks that need authoring are UNMEASURED and shown to the judges as such, never as passed. Then
Opus and GPT, each a fresh process given the same prompt; both accept -> accept, both reject -> reject, split -> a
third fresh Opus run and the majority stands. An unparseable answer or a failed call -> invalid (re-run), never accept.

MODELS. Opus: `claude -p` with no tools, the model read from $ARENA_JUDGE_OPUS_MODEL, else
$ANTHROPIC_DEFAULT_OPUS_MODEL (Claude Code's own alias variable); neither set -> refuse. GPT: gpt_consult.py with
RM_ARM=harness. Both are injectable (`Judges(opus=..., gpt=..., tie=...)`, each `call(prompt, work) -> text`), and
the CLI runners take an argv prefix so a selftest can stand a fake executable in for the model inside the real
sandbox: it costs nothing.

RESIDUAL (stated, not hidden): gpt_consult runs codex.exe, a WINDOWS process, which the Linux sandbox does not
confine; it gets only the inlined prompt, but its read-only sandbox could in principle read \\wsl.localhost paths.
The guess-rate test is the detector for whatever leaks remain.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import fnmatch
import io
import json
import math
import os
import re
import secrets
import shutil
import subprocess
import sys
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402

ARMS = ("ralph_a", "ralph_c", "trio", "v3", "v3c")              # testpilot_merged §6.2; $ARENA_ARMS overrides
FAMILY_TOKENS = ("ralph",)                                     # family words that name an arm group
ARM_BOOKKEEPING = ("AGENTS.md", "*/AGENTS.md", "PROMPT.md", "fix_plan.md", "IMPLEMENTATION_PLAN.md", "arm.toml",
                   "*/arm.toml")
TREE_PATHS = ("src/RimMandrake/Utils", "src/RimMandrake/rimflow")   # what hidden checks import; src is ~2 GB
CHECK_TIMEOUT = 300
MODEL_TIMEOUT = 1500
VERDICTS = ("accept", "reject")


class JudgeError(Exception):
    pass


class JudgeUnavailable(JudgeError):
    """A judge-side process cannot be started safely (no sandbox, no model in the environment)."""


class NeutraliserLeak(JudgeError):
    pass


class PrivateLocationError(JudgeError):
    pass


# ---------------------------------------------------------------- configuration

def arms() -> tuple:
    env = os.environ.get("ARENA_ARMS", "").strip()
    return tuple(a.strip() for a in env.split(",") if a.strip()) if env else ARMS


def clones_root() -> Path:
    return Path(os.environ.get("ARENA_CLONES", "/home/mandrake/rm/arena"))


def private_dir() -> Path:
    env = os.environ.get("ARENA_PRIVATE", "").strip()
    return Path(env) if env else Path.home() / ".local" / "state" / "rm_arena_private"


def work_root() -> Path:
    env = os.environ.get("ARENA_JUDGE_WORK", "").strip()
    return Path(env) if env else clones_root() / "judge"


def opus_model() -> str:
    for var in ("ARENA_JUDGE_OPUS_MODEL", "ANTHROPIC_DEFAULT_OPUS_MODEL"):
        v = os.environ.get(var, "").strip()
        if v:
            return v
    raise JudgeUnavailable("no Opus model in the environment (ARENA_JUDGE_OPUS_MODEL / ANTHROPIC_DEFAULT_OPUS_MODEL)")


def _inside(child: Path, parent: Path) -> bool:
    c, q = os.path.realpath(child), os.path.realpath(parent)
    return c == q or c.startswith(q.rstrip("/") + "/")


def check_private_location(priv: Path, p: dict) -> None:
    """The private dir must sit outside every root the judge side (or an arm) is given."""
    roots = list(A.arm_readable_roots(p)) + [work_root(), p["judge"], p["root"] / "judge"]
    for r in roots:
        if _inside(priv, r) or _inside(r, priv):
            raise PrivateLocationError("harness-private dir %s overlaps judge/arm-readable root %s" % (priv, r))


# ---------------------------------------------------------------- the arm map (harness side only)

class ArmMap:
    def __init__(self, p: dict | None = None, priv: Path | None = None):
        self.p = p or A.paths()
        self.dir = Path(priv) if priv else private_dir()
        check_private_location(self.dir, self.p)
        self.path = self.dir / "arm_map.json"

    def _ensure(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.dir, 0o700)

    def read(self) -> dict:
        if not self.path.is_file():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def assign(self, arm: str, task: str, base: str, head: str) -> str:
        self._ensure()
        lock = self.dir / ".lock"
        with open(lock, "a") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            m = self.read()
            jid = "J" + secrets.token_hex(6)
            while jid in m:
                jid = "J" + secrets.token_hex(6)
            m[jid] = {"arm": arm, "task": task, "base": base, "head": head, "ts": A_now()}
            tmp = self.path.with_suffix(".tmp")
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(m, f, indent=1, sort_keys=True)
            os.replace(tmp, self.path)
            os.chmod(self.path, 0o600)
        return jid

    def arm_of(self, jid: str) -> str | None:
        return (self.read().get(jid) or {}).get("arm")


def A_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- sandbox (judge side)

def sandbox_argv(argv: list[str], *, masks: list[Path], keep: list[Path], chdir: Path | None = None) -> list[str]:
    bw = shutil.which("bwrap")
    if not bw:
        raise JudgeUnavailable("bwrap not found: the judge never runs unsandboxed")
    out = [bw, "--bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--die-with-parent"]
    for m in masks:
        if Path(m).exists():
            out += ["--tmpfs", os.path.realpath(m)]
    for k in keep:
        k = os.path.realpath(k)
        out += ["--bind", k, k]
    if chdir is not None:
        out += ["--chdir", os.path.realpath(chdir)]
    return out + ["--"] + list(argv)


def judge_masks(priv: Path | None = None) -> list[Path]:
    """What a judge-side process must not see: the harness-private dir and the arm clones (their paths and
    transcripts name the arm). The judge work dir is bound back in when it lives under the clone root."""
    return [Path(priv) if priv else private_dir(), clones_root()]


def run_sandboxed(argv, *, work: Path, priv: Path | None = None, stdin: bytes | None = None,
                  timeout: int = CHECK_TIMEOUT, env: dict | None = None, cwd: Path | None = None):
    full = sandbox_argv(list(argv), masks=judge_masks(priv), keep=[work], chdir=cwd or work)
    e = dict(os.environ if env is None else env)
    for k in ("ARENA_PRIVATE", "RM_ARM"):            # nothing in the judge's environment names the map or an arm
        e.pop(k, None)
    e["RM_ARM"] = "harness"                          # §1.6: judge spend is the harness's
    try:
        return subprocess.run(full, cwd=str(cwd or work), input=stdin, capture_output=True, timeout=timeout, env=e)
    except subprocess.TimeoutExpired as ex:
        return subprocess.CompletedProcess(full, 124, ex.stdout or b"", (ex.stderr or b"") + b"\n[timeout]")


# ---------------------------------------------------------------- neutraliser

def _token_re(tok: str) -> str:
    parts = [re.escape(x) for x in re.split(r"[_\-\s.]+", tok) if x]
    return r"(?<![A-Za-z0-9])" + r"[_\-\s.]*".join(parts) + r"(?![A-Za-z0-9])"


def arm_tokens(extra=()) -> list[str]:
    env = [t.strip() for t in os.environ.get("ARENA_ARM_TOKENS", "").split(",") if t.strip()]
    toks = set(arms()) | set(FAMILY_TOKENS) | set(env) | {t for t in extra if t}
    return sorted(toks, key=lambda t: (-len(t), t))


TRAILER_RE = re.compile(r"(?im)^(?P<pre>[+\- ]?[ \t#/*>\"']*)(co-authored-by|claude-session|signed-off-by|"
                        r"reviewed-by|generated with|🤖 generated)\b.*$")
SESSION_RE = re.compile(r"https?://claude\.ai/code/session_[A-Za-z0-9_]+|session_[0-9A-Za-z]{20,}")
BRANCH_RE = re.compile(r"refs/heads/[^\s'\"]+|refs/remotes/[^\s'\"]+|\brm-arm-[A-Za-z0-9_\-]+|\barm/[A-Za-z0-9_\-]+")
INDEX_RE = re.compile(r"(?m)^index [0-9a-f]+\.\.[0-9a-f]+( \d+)?$")


def _path_forms(path: Path) -> list[str]:
    forms = {str(path), os.path.realpath(path)}
    for f in list(forms):
        forms.add(f.replace("/", "-"))                                     # ~/.claude/projects/<slug>
        forms.add("\\\\wsl.localhost\\Ubuntu" + f.replace("/", "\\"))
        forms.add("//wsl.localhost/Ubuntu" + f)
        if f.startswith("/mnt/") and len(f) > 6:
            forms.add(f[5].upper() + ":" + f[6:].replace("/", "\\"))
    return sorted((x for x in forms if len(x) > 3), key=len, reverse=True)


@dataclass
class Neutral:
    text: str
    files: list[str]
    stripped: list[str]
    redactions: dict = field(default_factory=dict)


def scrub(text: str, *, clone: Path | None = None, shas=(), branch: str | None = None, extra_tokens=()) -> tuple:
    """-> (text, counts). Pure text: usable on the diff, the gate record, anything a judge will read."""
    counts = {}

    def sub(name, pat, repl, s, flags=0):
        new, n = re.subn(pat, repl, s, flags=flags)
        if n:
            counts[name] = counts.get(name, 0) + n
        return new

    t = text
    t = sub("trailer", TRAILER_RE, lambda m: m.group("pre") + "<TRAILER>", t)
    t = sub("session", SESSION_RE, "<SESSION>", t)
    if clone is not None:
        for f in _path_forms(Path(clone)):
            t = sub("clone_path", re.escape(f), "<REPO>", t)
    root = clones_root()
    for f in _path_forms(root):
        t = sub("clone_path", re.escape(f) + r"[/\\-][A-Za-z0-9_.\-]+", "<REPO>", t)
    if branch and branch not in ("HEAD", "main", "master"):
        t = sub("branch", re.escape(branch), "<BRANCH>", t)
    t = sub("branch", BRANCH_RE, "<BRANCH>", t)
    t = sub("index", INDEX_RE, "index <SHA>", t)
    for s in shas:
        if s and len(s) >= 7:
            t = sub("sha", r"\b" + re.escape(s[:7]) + r"[0-9a-f]{0,33}\b", "<SHA>", t)
    for tok in arm_tokens(extra_tokens):
        t = sub("arm", _token_re(tok), "<ARM>", t, re.IGNORECASE)
    return t, counts


def find_leaks(text: str, *, clone: Path | None = None, extra_tokens=()) -> list[str]:
    hits = []
    for tok in arm_tokens(extra_tokens):
        m = re.search(_token_re(tok), text, re.IGNORECASE)
        if m:
            hits.append("arm token %r at %d" % (m.group(0), m.start()))
    if clone is not None:
        for f in _path_forms(Path(clone)):
            if f in text:
                hits.append("clone path %r" % f)
    for f in _path_forms(clones_root()):
        if re.search(re.escape(f) + r"[/\\-][A-Za-z0-9_.\-]+", text):
            hits.append("clone root path %r" % f)
    for rx, what in ((TRAILER_RE, "trailer"), (SESSION_RE, "session url"), (BRANCH_RE, "branch ref")):
        m = rx.search(text)
        if m and "<TRAILER>" not in m.group(0):
            hits.append("%s %r" % (what, m.group(0)[:60]))
    return hits


def _git(repo: Path, *args) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode:
        raise JudgeError("git %s: %s" % (" ".join(args[:3]), r.stderr.strip()[:300]))
    return r.stdout


def in_area(path: str, area: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in area)


def is_arm_bookkeeping(path: str) -> bool:
    return A.is_bookkeeping(path) or any(fnmatch.fnmatch(path, g) for g in ARM_BOOKKEEPING)


def neutralise(clone: Path, base: str, head: str, area: list[str], *, extra_tokens=(), do_scrub=True) -> Neutral:
    """Head minus base over `area`, stripped and re-rooted. Raises NeutraliserLeak when anything arm-identifying is
    left. `do_scrub=False` exists only so the selftest can prove the leak scan catches an unscrubbed diff."""
    clone = Path(clone)
    names = [x for x in _git(clone, "diff", "--no-renames", "--name-only", base, head).splitlines() if x]
    stripped = [x for x in names if is_arm_bookkeeping(x) or not in_area(x, area)]
    files = [x for x in names if x not in stripped]
    raw = _git(clone, "diff", "--no-color", "--no-ext-diff", "--no-renames", "--src-prefix=a/", "--dst-prefix=b/",
               base, head, "--", *files) if files else ""
    try:
        branch = _git(clone, "rev-parse", "--abbrev-ref", "HEAD").strip()
    except JudgeError:
        branch = None
    counts = {}
    text = raw
    if do_scrub:
        text, counts = scrub(raw, clone=clone, shas=(base, head), branch=branch, extra_tokens=extra_tokens)
    leaks = find_leaks(text, clone=clone, extra_tokens=extra_tokens)
    if leaks:
        raise NeutraliserLeak("neutralised diff still identifies the arm: " + "; ".join(leaks[:5]))
    neutral_files = [scrub(f, extra_tokens=extra_tokens)[0] for f in files]
    return Neutral(text=text, files=neutral_files, stripped=stripped, redactions=counts)


# ---------------------------------------------------------------- hidden checks (judge side, sandboxed)

def materialise(clone: Path, head: str, area: list[str], dest: Path, tree_paths=TREE_PATHS) -> Path:
    """git archive of head (no .git, no branch, no commit message) into dest."""
    want = set(tree_paths)
    for g in area:
        d = g.split("*", 1)[0].rstrip("/")
        if d and d != ".":
            want.add(d)
    present = [w for w in sorted(want) if _git(Path(clone), "ls-tree", "--name-only", head, w).strip()]
    dest.mkdir(parents=True, exist_ok=True)
    if not present:
        return dest
    data = subprocess.run(["git", "-C", str(clone), "archive", "--format=tar", head, *present],
                          capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        tf.extractall(dest, filter="data")
    return dest


def hidden_checks(hidden: dict) -> list[dict]:
    """Flatten arena_tasks' judge file into runnable checks: the original fix's tests, and each rework's tests."""
    out = []
    for c in hidden.get("checks") or []:
        if c.get("type") == "fix_test":
            out.append({"kind": "fix_test", "path": c["path"], "body": c.get("body")})
    for r in hidden.get("reworks") or []:
        for t in r.get("tests") or []:
            out.append({"kind": "rework_test", "path": t["path"], "body": t.get("body"), "rework": r.get("item")})
        if not r.get("tests"):
            out.append({"kind": "rework_unauthored", "path": None, "body": None, "rework": r.get("item")})
    return out


def run_hidden(checks: list[dict], tree: Path, work: Path, *, priv: Path | None = None,
               timeout: int = CHECK_TIMEOUT) -> list[dict]:
    res = []
    for c in checks:
        if c["kind"] == "rework_unauthored" or c.get("body") is None:
            res.append({"kind": c["kind"], "path": c.get("path"), "result": "UNMEASURED",
                        "why": "the hidden check has no stored test body (needs authoring)"})
            continue
        target = tree / c["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(c["body"], encoding="utf-8")       # the hidden test, over whatever the arm wrote there
        r = run_sandboxed([sys.executable, str(target)], work=work, priv=priv, timeout=timeout, cwd=tree)
        tail = (r.stdout + r.stderr).decode("utf-8", "replace")[-1500:]
        result = "pass" if r.returncode == 0 else ("error" if r.returncode == 124 else "fail")
        res.append({"kind": c["kind"], "path": c["path"], "rc": r.returncode, "result": result, "tail": tail})
    return res


# ---------------------------------------------------------------- model judges

PROMPT = """You are an acceptance judge for one code change in a RimWorld mod repository.
You see the task's acceptance criteria, the mechanical gate record, the results of hidden checks, and the change as
an anonymised diff. Decide whether the change meets the criteria. Be strict: accept only work that does what the
criteria ask, without placeholders, and without breaking what it touches. Judge the change, not its style.

The change was made by one of several anonymous build procedures, labelled: {labels}. Identifying strings were
redacted to <ARM>, <REPO>, <SHA>, <BRANCH>, <TRAILER>. Also guess which procedure made it ("unknown" if you cannot
tell); the guess does not affect your verdict.

Answer with ONE JSON object and nothing after it:
{{"verdict": "accept" or "reject", "reasons": ["..."], "arm_guess": one of {labels_json} or "unknown"}}

## Task criteria
{criteria}

## Gate record
{gate}

## Hidden checks
{hidden}

## Diff (head minus base, over the task area)
```diff
{diff}
```
"""


def build_prompt(criteria: str, gate: dict, hidden_res: list[dict], diff: str, labels: tuple) -> str:
    g = json.dumps(gate, indent=1, sort_keys=True)
    h = json.dumps([{k: v for k, v in r.items() if k != "tail"} for r in hidden_res], indent=1) if hidden_res \
        else "(none for this task)"
    return PROMPT.format(labels=", ".join(labels), labels_json=json.dumps(list(labels)), criteria=criteria.strip(),
                         gate=g, hidden=h, diff=diff)


def parse_answer(text: str, labels: tuple) -> dict:
    """The last JSON object carrying a verdict. Anything else is invalid, never accept."""
    dec = json.JSONDecoder()
    found = None
    for i, ch in enumerate(text or ""):
        if ch != "{":
            continue
        try:
            obj, _ = dec.raw_decode(text, i)
        except ValueError:
            continue
        if isinstance(obj, dict) and "verdict" in obj:
            found = obj
    if not found:
        return {"verdict": "invalid", "why": "no JSON verdict in the answer", "arm_guess": "unknown"}
    v = str(found.get("verdict", "")).strip().lower()
    g = str(found.get("arm_guess", "unknown")).strip()
    return {"verdict": v if v in VERDICTS else "invalid", "reasons": found.get("reasons") or [],
            "arm_guess": g if g in labels else "unknown"}


ModelCall = Callable[[str, Path], str]


class OpusCLI:
    """A fresh `claude -p`, no tools, inside the judge sandbox. `prefix` replaces the executable (selftests)."""

    def __init__(self, prefix: list[str] | None = None, priv: Path | None = None, timeout: int = MODEL_TIMEOUT):
        self.prefix, self.priv, self.timeout = prefix, priv, timeout

    def __call__(self, prompt: str, work: Path) -> str:
        exe = self.prefix or [shutil.which("claude") or "claude"]
        argv = exe + ["-p", "--model", opus_model(), "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
                      "--output-format", "text"]
        r = run_sandboxed(argv, work=work, priv=self.priv, stdin=prompt.encode("utf-8"), timeout=self.timeout)
        if r.returncode:
            raise JudgeError("opus judge exit %d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[-300:]))
        return r.stdout.decode("utf-8", "replace")


class GptConsult:
    """gpt_consult.py, a fresh codex run, from the judge work dir, inside the judge sandbox."""

    def __init__(self, prefix: list[str] | None = None, priv: Path | None = None, timeout: int = MODEL_TIMEOUT):
        self.prefix, self.priv, self.timeout = prefix, priv, timeout

    def __call__(self, prompt: str, work: Path) -> str:
        pf = work / ("gpt_prompt_%s.md" % secrets.token_hex(3))
        out = work / (pf.stem + "_answer.md")
        pf.write_text(prompt, encoding="utf-8")
        exe = self.prefix or [sys.executable, str(UTILS / "gpt_consult.py")]
        r = run_sandboxed(exe + ["--prompt-file", str(pf), "--out", str(out), "--timeout", str(self.timeout)],
                          work=work, priv=self.priv, timeout=self.timeout + 60)
        if r.returncode or not out.is_file():
            raise JudgeError("gpt judge exit %d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[-300:]))
        return out.read_text(encoding="utf-8")


@dataclass
class Judges:
    opus: ModelCall
    gpt: ModelCall
    tie: ModelCall

    @classmethod
    def real(cls, priv: Path | None = None) -> "Judges":
        return cls(opus=OpusCLI(priv=priv), gpt=GptConsult(priv=priv), tie=OpusCLI(priv=priv))


def _ask(name: str, call: ModelCall, prompt: str, work: Path, labels: tuple) -> dict:
    try:
        text = call(prompt, work)
    except Exception as ex:                                  # a failed call is invalid, never accept
        return {"judge": name, "verdict": "invalid", "why": str(ex)[:300], "arm_guess": "unknown"}
    out = parse_answer(text, labels)
    out["judge"] = name
    return out


def combine(votes: list[dict]) -> str:
    vs = [v["verdict"] for v in votes]
    if "invalid" in vs:
        return "invalid"
    acc = vs.count("accept")
    return "accept" if acc * 2 > len(vs) else "reject"


# ---------------------------------------------------------------- the judge

def _gate_view(gate: dict | None, **kw) -> dict:
    g = {k: v for k, v in (gate or {}).items() if k not in ("arm", "builder", "agent", "agent_id", "lane", "run_id",
                                                              "branch", "clone")}
    text, _ = scrub(json.dumps(g, sort_keys=True), **kw)
    try:
        return json.loads(text)
    except ValueError:
        return {"record": text}


def judge(*, task: dict, hidden: dict | None, clone: Path, base: str, head: str, arm: str, gate: dict | None,
          judges: Judges | None = None, p: dict | None = None, priv: Path | None = None,
          work_base: Path | None = None, extra_tokens=(), tree_paths=TREE_PATHS) -> dict:
    """Harness side. Returns the blind verdict record (no arm in it); the arm goes only to the arm map."""
    p = p or A.paths()
    amap = ArmMap(p, priv)
    labels = arms()
    if arm not in labels:
        raise JudgeError("arm %r is not one of %s" % (arm, ", ".join(labels)))
    jid = amap.assign(arm, task["id"], base, head)
    work = Path(work_base or work_root()) / jid
    work.mkdir(parents=True, exist_ok=True)
    rec = {"judge_id": jid, "task": task["id"], "ts": A_now(), "votes": [], "hidden": []}

    def done(verdict, why=None):
        rec["verdict"] = verdict
        if why:
            rec["why"] = why
        (work / "verdict.json").write_text(json.dumps(rec, indent=1, sort_keys=True), encoding="utf-8")
        return rec

    gstat = str((gate or {}).get("verdict", "")).lower()
    if gstat != "pass":
        return done("reject" if gstat == "fail" else "invalid", "gate verdict %r" % (gstat or None))
    try:
        nd = neutralise(clone, base, head, task.get("area") or [], extra_tokens=extra_tokens)
    except NeutraliserLeak as ex:
        return done("invalid", str(ex))
    rec["neutraliser"] = {"files": nd.files, "stripped": len(nd.stripped), "redactions": nd.redactions}
    (work / "diff.patch").write_text(nd.text, encoding="utf-8")
    if not nd.text.strip():
        return done("reject", "empty diff over the task area")

    probe = run_sandboxed(["true"], work=work, priv=priv, timeout=60)
    if probe.returncode:
        return done("invalid", "judge sandbox did not start: " + probe.stderr.decode("utf-8", "replace")[-200:])
    checks = hidden_checks(hidden or {})
    if checks:
        tree = materialise(clone, head, task.get("area") or [], work / "tree", tree_paths)
        rec["hidden"] = run_hidden(checks, tree, work, priv=priv)
        if any(h["result"] == "error" for h in rec["hidden"]):
            return done("invalid", "a hidden check could not finish")
        if any(h["result"] == "fail" for h in rec["hidden"]):
            return done("reject", "hidden check failed: " +
                        ", ".join(h["path"] for h in rec["hidden"] if h["result"] == "fail"))

    kw = {"clone": clone, "shas": (base, head), "extra_tokens": extra_tokens}
    gview = _gate_view(gate, **kw)
    prompt = build_prompt(task.get("criteria") or "", gview, rec["hidden"], nd.text, labels)
    # the criteria and hidden-check paths come from the frozen task, identical for every arm; the gate record and
    # the diff come from the arm, so those are what must be clean
    leaks = find_leaks(json.dumps(gview, sort_keys=True) + "\n" + nd.text, clone=clone, extra_tokens=extra_tokens)
    if leaks:
        return done("invalid", "prompt leaks the arm: " + "; ".join(leaks[:3]))
    (work / "prompt.md").write_text(prompt, encoding="utf-8")
    js = judges or Judges.real(priv)
    votes = [_ask("opus", js.opus, prompt, work, labels), _ask("gpt", js.gpt, prompt, work, labels)]
    if {v["verdict"] for v in votes} == {"accept", "reject"}:
        votes.append(_ask("opus_tiebreak", js.tie, prompt, work, labels))
    rec["votes"] = votes
    return done(combine(votes))


def judge_task(task_id: str, *, clone: Path, base: str, head: str, arm: str, gate: dict | None,
               judges: Judges | None = None, p: dict | None = None, **kw) -> dict:
    """Load the frozen task (arena_tasks.load_frozen refuses a changed one) and its judge file, then judge."""
    p = p or A.paths()
    task = A.load_frozen(task_id, p)
    hp = p["judge"] / (task_id + ".json")
    hidden = json.loads(hp.read_text(encoding="utf-8")) if hp.is_file() else None
    return judge(task=task, hidden=hidden, clone=clone, base=base, head=head, arm=arm, gate=gate, judges=judges, p=p,
                 **kw)


# ---------------------------------------------------------------- arm-guess report (harness side)

def binom_sf(k: int, n: int, q: float) -> float:
    """P(X >= k), X ~ Binomial(n, q): exact."""
    return float(sum(math.comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(k, n + 1))) if n else 1.0


def guess_report(records: list[dict], amap: dict, labels: tuple | None = None, alpha: float = 0.05) -> dict:
    """Per judge and pooled: correct guesses vs chance 1/len(labels), one-sided exact binomial. 'unknown' counts as a
    wrong guess (a judge cannot lower its rate by abstaining). Records with no map entry are skipped and counted."""
    labels = tuple(labels or arms())
    q = 1.0 / len(labels)
    per, unmapped = {}, 0
    for r in records:
        truth = (amap.get(r.get("judge_id")) or {}).get("arm")
        if truth is None:
            unmapped += 1
            continue
        for v in r.get("votes") or []:
            s = per.setdefault(v["judge"], [0, 0])
            s[1] += 1
            s[0] += int(v.get("arm_guess") == truth)
    rows = {}
    for name, (k, n) in sorted(per.items()):
        pv = binom_sf(k, n, q)
        rows[name] = {"correct": k, "guesses": n, "rate": k / n if n else None, "p_value": pv, "leaky": pv < alpha}
    K, N = sum(v[0] for v in per.values()), sum(v[1] for v in per.values())
    pooled = binom_sf(K, N, q)
    return {"chance": q, "alpha": alpha, "arms": list(labels), "per_judge": rows,
            "pooled": {"correct": K, "guesses": N, "rate": K / N if N else None, "p_value": pooled,
                       "leaky": pooled < alpha},
            "submissions": len(records) - unmapped, "unmapped": unmapped,
            "blinding": "UNMEASURED" if not N else ("LEAKY" if pooled < alpha or any(r["leaky"] for r in rows.values())
                                                    else "not shown leaky")}


def write_report(day: str | None = None, *, p: dict | None = None, priv: Path | None = None,
                 work_base: Path | None = None) -> Path:
    p = p or A.paths()
    amap = ArmMap(p, priv).read()
    day = day or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    recs = []
    for f in sorted(Path(work_base or work_root()).glob("J*/verdict.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        if str(r.get("ts", "")).startswith(day):
            recs.append(r)
    rep = guess_report(recs, amap)
    rep["day"] = day
    out = p["root"] / "reports" / ("judge_guess_%s.json" % day)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=1, sort_keys=True), encoding="utf-8")
    return out


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("judge")
    j.add_argument("--task", required=True)
    j.add_argument("--clone", required=True)
    j.add_argument("--base", required=True)
    j.add_argument("--head", required=True)
    j.add_argument("--arm", required=True)
    j.add_argument("--gate", required=True, help="the arena_gate.py JSON record")
    r = sub.add_parser("report")
    r.add_argument("--day")
    a = ap.parse_args(argv)
    if a.cmd == "judge":
        gate = json.loads(Path(a.gate).read_text(encoding="utf-8"))
        rec = judge_task(a.task, clone=Path(a.clone), base=a.base, head=a.head, arm=a.arm, gate=gate)
        print(json.dumps({k: rec[k] for k in ("judge_id", "task", "verdict")}, sort_keys=True))
        return 0 if rec["verdict"] != "invalid" else 2
    print(write_report(a.day))
    return 0


if __name__ == "__main__":
    sys.exit(main())
