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
hidden checks. Every judge-side process is started inside a bubblewrap sandbox: the host root READ-ONLY
(`--ro-bind / /`), its own pid namespace and session, a fresh /tmp, and empty tmpfs laid OVER the harness-private
directory's generic parent, the arm clone root, the judge work root, the arena root (event log, gate records, other
tasks' hidden checks) and ~/.claude/projects. Only the process's own scratch is writable: a hidden check gets a fresh
copy of the tree per check (it cannot tamper with the next check, the judge code or the host); the Opus run gets
$HOME too (claude rewrites its config; it runs no tools and no arm code); the GPT run gets the work dir plus codex
scratch and the consult receipts. A timeout SIGKILLs the whole process group and the pid namespace with it. No bwrap
-> the judge refuses; it never runs unsandboxed.

HIDDEN-CHECK PASS needs proof the check ran to its end: each check runs under a harness-owned runner that reads a
fresh nonce on stdin, runs the test file as __main__, and only after it returns writes `ARENA_CHECK_DONE <nonce>` to a
private dup of stdout. rc 0 without that line (os._exit(0), a hooked excepthook) is `no_marker` -> invalid.

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
`<TRAILER>` (also Assisted-by / Generated-by / Written-by), session URLs `<SESSION>`, branch refs `<BRANCH>`, the
clone path (POSIX, realpath, \\wsl.localhost and \\wsl$ UNC, D:/ forms, transcript slug) and any `<clone root>/<name>`
path `<REPO>`, head/base shas and their prefixes `<SHA>`, EVERY arm name (all arms, so the redaction is the same for
every arm) `<ARM>`, and model names (Claude, Codex, GPT, Opus, ...) `<MODEL>`. Tokens match on a skeleton (NFKC,
look-alike letters folded, zero-width dropped), case- and separator-insensitive, glued at camelCase seams (RalphLoop,
V3Arm) and plural. Agent config is stripped as bookkeeping (CLAUDE.md, .claude/, .codex/, .ralph/, specs/, GEMINI.md).
Two exemptions keep code intact and are reported as `ambiguous_kept`: a version ('v3.2') and the module of an import
(`import trio`). Then a leak scan with the SAME matcher re-runs over the result; anything left refuses the submission
(NeutraliserLeak). The gate record reaches the prompt only as a whitelist: its verdict and each step's status (never
its folder, time, task, shas or step notes).

VERDICT. Hidden checks first: one failing -> reject (a known-bad replay output never reaches a model); one that could
not run -> invalid. Checks that need authoring are UNMEASURED and shown to the judges as such, never as passed. Then
Opus and GPT, each a fresh process given the same prompt; both accept -> accept, both reject -> reject, split -> a
third fresh Opus run and the majority stands. An unparseable answer or a failed call -> invalid (re-run), never accept.

MODELS. Opus: `claude -p` with no tools, the model read from $ARENA_JUDGE_OPUS_MODEL, else
$ANTHROPIC_DEFAULT_OPUS_MODEL (Claude Code's own alias variable); neither set -> refuse. GPT: gpt_consult.py with
RM_ARM=harness. Both are injectable (`Judges(opus=..., gpt=..., tie=...)`, each `call(prompt, work) -> text`), and
the CLI runners take an argv prefix so a selftest can stand a fake executable in for the model inside the real
sandbox: it costs nothing.

GUESS REPORT. Each judge also guesses the arm. Chance is the day's own mix: a permutation test permutes which arm made
which submission (exact up to 8 submissions, else 20000 seeded draws), per judge and pooled (a submission's votes kept
together), Bonferroni over the tests. An always-the-majority guesser is therefore never LEAKY.

RESIDUAL (stated, not hidden):
  - gpt_consult runs codex.exe, a WINDOWS process the Linux sandbox does not confine. It gets only the neutralised
    prompt (no path, sha, time or gate folder), but its own read-only sandbox can read \\wsl.localhost paths: the arm
    clones, the arm map at its default path (named in this source), ~/.claude/projects, the arena event log and the
    gate folders arena_gate.py names <arm>_<task>_<head12>_<stamp>. Setting ARENA_PRIVATE to an unpublished path
    narrows the map; nothing here can stop a model that goes looking. The guess-rate report is the detector.
  - arm code inside a hidden check shares the runner's interpreter, so deliberate frame/gc introspection could still
    find the nonce. The marker defeats early exits and hooked exits, not a targeted attack on the runner.
  - the real `claude -p` / codex.exe have not been run inside this sandbox by the selftests (they cost money).
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
import random
import shutil
import signal
import subprocess
import sys
import tarfile
import unicodedata
from itertools import permutations
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
                   "*/arm.toml", "CLAUDE.md", "*/CLAUDE.md", "CLAUDE.local.md", "GEMINI.md", ".claude/*", "*/.claude/*",
                   ".codex/*", "*/.codex/*", ".ralph/*", "*/.ralph/*", "specs/*", ".cursor/*", ".aider*")
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
    """READ-ONLY root (`--ro-bind / /`), a fresh /tmp, its own pid namespace (no host /proc, and the whole tree dies
    with it), `masks` hidden under empty tmpfs, and ONLY `keep` writable. Order: kept dirs outside every mask are
    bound first, then the masks are laid (so a broad bind like $HOME never re-exposes ~/.claude/projects), then the
    kept paths that live inside a mask (the judge's own work dir under the clone root) are bound back."""
    bw = shutil.which("bwrap")
    if not bw:
        raise JudgeUnavailable("bwrap not found: the judge never runs unsandboxed")
    out = [bw, "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp",
           "--unshare-pid", "--new-session", "--die-with-parent"]
    ms = sorted({os.path.realpath(m) for m in masks if Path(m).exists()}, key=len)
    ks = sorted({os.path.realpath(k) for k in keep if Path(k).exists()}, key=len)
    under = [k for k in ks if any(_inside(Path(k), Path(m)) for m in ms)]
    for k in ks:
        if k not in under:
            out += ["--bind", k, k]
    for m in ms:
        out += ["--tmpfs", m]
    for k in under:
        out += ["--bind", k, k]
    home_proj = os.path.realpath(Path.home() / ".claude" / "projects")
    for m in ms:                                     # then each mask goes READ-ONLY (a write there fails rather than
        if m != home_proj:                           # landing in a throwaway); claude may write its transcript there
            out += ["--remount-ro", m]
    if chdir is not None:
        out += ["--chdir", os.path.realpath(chdir)]
    return out + ["--"] + list(argv)


def _generic_mask(priv: Path) -> Path:
    """Mask the private dir's PARENT when that is a generic directory (~/.local/state), so /proc/self/mountinfo inside
    the sandbox names only the generic dir, never the map's own location. Falls back to the dir itself when the
    parent is /, $HOME, or holds anything a judge-side process needs."""
    parent = Path(os.path.realpath(priv)).parent
    home = Path(os.path.realpath(Path.home()))
    needed = [UTILS, Path(sys.executable).resolve(), work_root(), Path(shutil.which("claude") or "/nonexistent")]
    if parent in (Path("/"), home) or _inside(home, parent) or any(_inside(n, parent) for n in needed):
        return Path(priv)
    return parent


def judge_masks(priv: Path | None = None, p: dict | None = None) -> list[Path]:
    """What a judge-side process must not see: the harness-private dir (via a generic parent), the arm clones (their
    paths and transcripts name the arm), the judge work root (sibling submissions), the arena root (the event log
    and the gate records name the arm, sha and time; the hidden checks of other tasks), and Claude Code's own
    transcripts. The judge's own work dir is bound back in."""
    try:
        aroot = (p or A.paths())["root"]
    except Exception:                                # noqa: BLE001 -- no arena root configured: nothing to mask
        aroot = None
    out = [_generic_mask(Path(priv) if priv else private_dir()), clones_root(), work_root(),
           Path.home() / ".claude" / "projects"]
    if aroot is not None:
        out.append(aroot)
    return out


SAFE_ENV_DROP = ("ARENA_", "RM_ARM", "OLDPWD", "PWD")


def judge_env(env: dict | None, priv: Path | None) -> dict:
    """The judge's environment: no ARENA_* variable, no variable whose value names the private dir or the clone root,
    RM_ARM=harness (§1.6: judge spend is the harness's)."""
    e = dict(os.environ if env is None else env)
    bad = [os.path.realpath(Path(priv) if priv else private_dir()), os.path.realpath(clones_root())]
    for k in list(e):
        if k.startswith(SAFE_ENV_DROP) or any(b and b in str(e[k]) for b in bad):
            e.pop(k, None)
    e["RM_ARM"] = "harness"
    return e


def run_sandboxed(argv, *, work: Path, priv: Path | None = None, stdin: bytes | None = None,
                  timeout: int = CHECK_TIMEOUT, env: dict | None = None, cwd: Path | None = None,
                  rw: list[Path] | None = None):
    """`rw` defaults to [work]; a hidden check passes its own per-check scratch copy instead. On timeout the whole
    process group is SIGKILLed (bwrap --die-with-parent then takes the pid namespace, grandchildren included)."""
    keep = [work] if rw is None else list(rw)
    full = sandbox_argv(list(argv), masks=judge_masks(priv), keep=keep, chdir=cwd or work)
    proc = subprocess.Popen(full, cwd="/", stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=judge_env(env, priv),
                            start_new_session=True)
    try:
        out, err = proc.communicate(stdin, timeout=timeout)
        return subprocess.CompletedProcess(full, proc.returncode, out, err)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
        return subprocess.CompletedProcess(full, 124, out or b"", (err or b"") + b"\n[timeout]")


# ---------------------------------------------------------------- neutraliser

# ---- identity tokens. ONE matcher (_find_tokens) serves the scrub AND the leak scan, so whatever the scrub misses
# the scan misses identically -- which is why the matcher is deliberately wide: it runs on a SKELETON of the text
# (NFKC, Cyrillic/Greek look-alikes folded to Latin, zero-width characters dropped) and a token also matches when it
# is glued to other letters at a camelCase seam (RalphLoop, myRalph, V3Arm, trioJudge) or carries a plural (ralphs).
# Two exemptions keep real code readable, and both are counted as `ambiguous` rather than silently passed:
#   - a digit-final token followed by .<digit> is a version, not an arm ('v3.2');
#   - a lower-case token that is the module of an import statement (`import trio`, `from trio.x import y`).
MODEL_TOKENS = ("claude", "codex", "chatgpt", "gpt", "openai", "anthropic", "opus", "sonnet", "haiku", "gemini",
                "copilot", "cursor", "aider")
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿­᠎͏"), None)
CONFUSABLE = str.maketrans("аеорсухіјѕһԁӏАВЕКМНОРСТХІЈЅαονρτΑΒΕΗΙΚΜΝΟΡΤΧΥΖ",
                           "aeopcyxijshdlABEKMHOPCTXIJSaovptABEHIKMNOPTXYZ")
_LEFT = r"(?:(?<![A-Za-z0-9])|(?<=[a-z0-9])(?=[A-Z]))"
_RIGHT = r"(?:(?![A-Za-z0-9])|(?<=[a-z0-9])(?=[A-Z]))"
IMPORT_PREFIX_RE = re.compile(r"^[+\- ]?\s*(?:import\s+(?:[\w.]+(?:\s+as\s+\w+)?\s*,\s*)*|from\s+)$")


def _token_re(tok: str) -> str:
    parts = [re.escape(x) for x in re.split(r"[_\-\s.]+", tok) if x]
    body = r"[_\-\s.]*".join("(?i:%s)" % x for x in parts)
    version = r"(?!\.\d)" if tok[-1:].isdigit() else ""
    return _LEFT + body + version + r"(?:(?i:e?s))?" + _RIGHT


def arm_tokens(extra=()) -> list[str]:
    env = [t.strip() for t in os.environ.get("ARENA_ARM_TOKENS", "").split(",") if t.strip()]
    toks = set(arms()) | set(FAMILY_TOKENS) | set(env) | {t for t in extra if t}
    return sorted(toks, key=lambda t: (-len(t), t))


def _skeleton(text: str):
    """-> (skeleton, index map or None). index[i] is the original offset of skeleton char i."""
    if text.isascii():
        return text, None
    out, idx = [], []
    for i, ch in enumerate(text):
        if ord(ch) < 128:
            out.append(ch)
            idx.append(i)
            continue
        n = unicodedata.normalize("NFKC", ch).translate(ZERO_WIDTH).translate(CONFUSABLE)
        for c in n:
            out.append(c)
            idx.append(i)
    return "".join(out), idx


def _find_tokens(text: str, tokens) -> tuple:
    """-> (spans, ambiguous): non-overlapping (start, end) spans in the ORIGINAL text naming a token, and the
    exempted (version / import) occurrences, as strings."""
    sk, idx = _skeleton(text)
    pat = re.compile("|".join("(?:%s)" % _token_re(t) for t in tokens))
    spans, amb = [], []
    for m in pat.finditer(sk):
        s, e = m.start(), m.end()
        word = m.group(0)
        ls = sk.rfind("\n", 0, s) + 1
        single = [t for t in tokens if t.lower() == word.lower() and t.lower() not in FAMILY_TOKENS
                  and re.fullmatch(r"[a-z][a-z0-9]*", t.lower())]
        if single and word.islower() and IMPORT_PREFIX_RE.match(sk[ls:s]) and \
                not re.match(r"[A-Za-z0-9_]", sk[e:e + 1]):
            amb.append(word)
            continue
        if idx is not None:
            s, e = idx[s], idx[e - 1] + 1
        spans.append((s, e))
    vers = [t for t in tokens if t[-1:].isdigit()]
    if vers:                                         # the version exemption, reported (never silently passed)
        vpat = re.compile("|".join("(?:%s)" % (_LEFT + _token_re(t)[len(_LEFT):].split("(?!")[0] + r"\.\d+")
                                   for t in vers))
        amb += [m.group(0) for m in vpat.finditer(sk)]
    return spans, amb


def _sub_tokens(text: str, tokens, repl: str) -> tuple:
    spans, amb = _find_tokens(text, tokens)
    if not spans:
        return text, 0, amb
    out, last = [], 0
    for s, e in spans:
        out.append(text[last:s])
        out.append(repl)
        last = e
    out.append(text[last:])
    return "".join(out), len(spans), amb


TRAILER_RE = re.compile(r"(?im)^(?P<pre>[+\- ]?[ \t#/*>\"']*)(co-authored-by|claude-session|signed-off-by|"
                        r"reviewed-by|assisted-by|generated-by|written-by|helped-by|made-with|generated with|"
                        r"🤖 generated)\b.*$")
SESSION_RE = re.compile(r"https?://claude\.ai/code/session_[A-Za-z0-9_]+|session_[0-9A-Za-z]{20,}")
BRANCH_RE = re.compile(r"refs/heads/[^\s'\"]+|refs/remotes/[^\s'\"]+|\brm-arm-[A-Za-z0-9_\-]+|\barm/[A-Za-z0-9_\-]+")
INDEX_RE = re.compile(r"(?m)^index [0-9a-f]+\.\.[0-9a-f]+( \d+)?$")


def _distros() -> list[str]:
    return sorted({"Ubuntu", os.environ.get("WSL_DISTRO_NAME", "").strip() or "Ubuntu"})


def _path_forms(path: Path) -> list[str]:
    forms = {str(path), os.path.realpath(path)}
    for f in list(forms):
        forms.add(f.replace("/", "-"))                                     # ~/.claude/projects/<slug>
        for host in ("wsl.localhost", "wsl$"):
            for d in _distros():
                forms.add("\\\\%s\\%s" % (host, d) + f.replace("/", "\\"))
                forms.add("//%s/%s" % (host, d) + f)
        if f.startswith("/mnt/") and len(f) > 6:
            forms.add(f[5].upper() + ":" + f[6:].replace("/", "\\"))
            forms.add(f[5].upper() + ":" + f[6:])
    return sorted((x for x in forms if len(x) > 3), key=len, reverse=True)


def _sha_re(s: str) -> str:
    return r"(?<![0-9A-Fa-f])" + re.escape(s[:7]) + r"[0-9a-f]{0,33}(?![0-9A-Fa-f])"


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
            t = sub("clone_path", re.escape(f), "<REPO>", t, re.IGNORECASE)
    root = clones_root()
    for f in _path_forms(root):
        t = sub("clone_path", re.escape(f) + r"[/\\-][A-Za-z0-9_.\-]+", "<REPO>", t, re.IGNORECASE)
    if branch and branch not in ("HEAD", "main", "master"):
        t = sub("branch", re.escape(branch), "<BRANCH>", t)
    t = sub("branch", BRANCH_RE, "<BRANCH>", t)
    t = sub("index", INDEX_RE, "index <SHA>", t)
    for s in shas:
        if s and len(s) >= 7:
            t = sub("sha", _sha_re(s), "<SHA>", t)
    amb = []
    for name, toks, repl in (("arm", arm_tokens(extra_tokens), "<ARM>"), ("model", MODEL_TOKENS, "<MODEL>")):
        t, n, a = _sub_tokens(t, toks, repl)
        amb += a
        if n:
            counts[name] = counts.get(name, 0) + n
    if amb:
        counts["ambiguous_kept"] = len(amb)
    return t, counts


def find_leaks(text: str, *, clone: Path | None = None, extra_tokens=(), shas=(), ambiguous: list | None = None
               ) -> list[str]:
    """The SAME token matcher as scrub (skeleton, glued, plural): anything it finds refuses. Exempted occurrences
    (version, import of a real module) are not hits; they are appended to `ambiguous` when a list is passed."""
    hits = []
    for what, toks in (("arm token", arm_tokens(extra_tokens)), ("model name", MODEL_TOKENS)):
        spans, amb = _find_tokens(text, toks)
        if spans:
            s, e = spans[0]
            hits.append("%s %r at %d" % (what, text[s:e], s))
        if ambiguous is not None:
            ambiguous += amb
    sk = _skeleton(text)[0]
    if clone is not None:
        for f in _path_forms(Path(clone)):
            if f.lower() in sk.lower():
                hits.append("clone path %r" % f)
    for f in _path_forms(clones_root()):
        if re.search(re.escape(f) + r"[/\\-][A-Za-z0-9_.\-]+", sk, re.IGNORECASE):
            hits.append("clone root path %r" % f)
    for s in shas:
        if s and len(s) >= 7 and re.search(_sha_re(s), sk):
            hits.append("sha %s" % s[:7])
    for rx, what in ((TRAILER_RE, "trailer"), (SESSION_RE, "session url"), (BRANCH_RE, "branch ref")):
        m = rx.search(sk)
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
    amb = []
    leaks = find_leaks(text, clone=clone, extra_tokens=extra_tokens, shas=(base, head), ambiguous=amb)
    if leaks:
        raise NeutraliserLeak("neutralised diff still identifies the arm: " + "; ".join(leaks[:5]))
    if amb:
        counts["ambiguous_kept"] = sorted(set(amb))
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


# The harness-owned runner. Exit code 0 is NOT a pass: arm code imported by the check can os._exit(0), replace
# sys.excepthook, or shadow a module. A pass needs the runner's completion line carrying a per-run nonce the harness
# generated and handed over on stdin (never in argv, env or a file); the runner writes it to a dup of the ORIGINAL
# stdout only after the check body returned (or exited 0) under its own try/except. `-P` keeps the arm's tree off
# sys.path until the runner's own imports are done.
RUNNER = r'''
import os, sys, runpy, traceback
def _main():
    nonce = sys.stdin.readline().strip()
    sys.stdin = open(os.devnull)
    fd = os.dup(1)
    test = sys.argv[1]
    sys.argv = [test]
    sys.path.insert(0, os.path.dirname(test))
    ok = False
    try:
        runpy.run_path(test, run_name="__main__")
        ok = True
    except SystemExit as e:
        ok = e.code in (None, 0)
        if not ok:
            print("SystemExit(%r)" % (e.code,), file=sys.stderr)
    except BaseException:
        traceback.print_exc()
    try:
        sys.stdout.flush(); sys.stderr.flush()
    except Exception:
        pass
    if ok:
        os.write(fd, ("\n" + "ARENA_CHECK_DONE " + nonce + "\n").encode())
    os._exit(0 if ok else 1)
_main()
'''
MARKER = "ARENA_CHECK_DONE "


def _check_result(rc: int, out: bytes, nonce: str) -> str:
    """pass ONLY on rc 0 AND the nonce line; rc 0 without it is `no_marker` (the check did not finish: invalid)."""
    if rc == 124:
        return "error"
    if rc != 0:
        return "fail"
    lines = out.decode("utf-8", "replace").splitlines()
    return "pass" if (MARKER + nonce) in (x.strip() for x in lines) else "no_marker"


def _write_check(scratch: Path, rel: str, body: str) -> Path:
    """Write the hidden test over whatever the arm put at that path, never THROUGH an arm symlink."""
    target = scratch / rel
    anc = target.parent
    while not anc.exists() and not anc.is_symlink():
        anc = anc.parent
    if not _inside(anc, scratch):                       # an arm symlink on the way: refuse (harness side, unsandboxed)
        raise JudgeError("hidden check path %s resolves outside the tree" % rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() or target.exists():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    target.write_text(body, encoding="utf-8")
    return target


def run_hidden(checks: list[dict], tree: Path, work: Path, *, priv: Path | None = None,
               timeout: int = CHECK_TIMEOUT) -> list[dict]:
    """Each check runs in its OWN copy of the tree, the only writable path in its sandbox: arm code imported by one
    check cannot touch another check's copy, the judge work dir, the hidden checks, or anything on the host."""
    res = []
    for i, c in enumerate(checks):
        if c["kind"] == "rework_unauthored" or c.get("body") is None:
            res.append({"kind": c["kind"], "path": c.get("path"), "result": "UNMEASURED",
                        "why": "the hidden check has no stored test body (needs authoring)"})
            continue
        scratch = work / ("check_%02d" % i)
        if scratch.exists():
            shutil.rmtree(scratch)
        shutil.copytree(tree, scratch, symlinks=True)
        try:
            target = _write_check(scratch, c["path"], c["body"])
        except JudgeError as ex:
            res.append({"kind": c["kind"], "path": c["path"], "rc": None, "result": "fail", "tail": str(ex)})
            continue
        nonce = secrets.token_hex(16)
        r = run_sandboxed([sys.executable, "-P", "-c", RUNNER, str(target)], work=work, priv=priv,
                          stdin=(nonce + "\n").encode(), timeout=timeout, cwd=scratch, rw=[scratch],
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        result = _check_result(r.returncode, r.stdout, nonce)
        tail = (r.stdout + r.stderr).decode("utf-8", "replace").replace(nonce, "<NONCE>")[-1500:]
        row = {"kind": c["kind"], "path": c["path"], "rc": r.returncode, "result": result, "tail": tail}
        if result == "no_marker":
            row["why"] = "exit 0 without the harness completion marker: the check body did not finish"
        res.append(row)
    return res


# ---------------------------------------------------------------- model judges

PROMPT = """You are an acceptance judge for one code change in a RimWorld mod repository.
You see the task's acceptance criteria, the mechanical gate record, the results of hidden checks, and the change as
an anonymised diff. Decide whether the change meets the criteria. Be strict: accept only work that does what the
criteria ask, without placeholders, and without breaking what it touches. Judge the change, not its style.

The change was made by one of several anonymous build procedures, labelled: {labels}. Identifying strings were
redacted to <ARM>, <MODEL>, <REPO>, <SHA>, <BRANCH>, <TRAILER>. Also guess which procedure made it ("unknown" if you cannot
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

    def preflight(self) -> None:
        """Raise JudgeUnavailable BEFORE any judge is asked (an unset model must not cost the GPT call first)."""
        opus_model()

    def rw(self, work: Path) -> list[Path]:
        """claude writes its config/state under $HOME (~/.claude.json is replaced by rename), so $HOME is writable for
        THIS process only: it runs no arm code (no tools) and the masks are still laid over $HOME afterwards."""
        home = Path.home()
        return [work, home, home / ".local" / "state" / "claude"]

    def __call__(self, prompt: str, work: Path) -> str:
        exe = self.prefix or [shutil.which("claude") or "claude"]
        argv = exe + ["-p", "--model", opus_model(), "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
                      "--output-format", "text"]
        r = run_sandboxed(argv, work=work, priv=self.priv, stdin=prompt.encode("utf-8"), timeout=self.timeout,
                          rw=self.rw(work))
        if r.returncode:
            raise JudgeError("opus judge exit %d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[-300:]))
        return r.stdout.decode("utf-8", "replace")


class GptConsult:
    """gpt_consult.py, a fresh codex run, from the judge work dir, inside the judge sandbox."""

    def __init__(self, prefix: list[str] | None = None, priv: Path | None = None, timeout: int = MODEL_TIMEOUT):
        self.prefix, self.priv, self.timeout = prefix, priv, timeout

    def preflight(self) -> None:
        return None

    @staticmethod
    def _scratch_paths() -> list[Path]:
        """Where gpt_consult.py writes outside the work dir: its codex job dirs and the consult receipts."""
        out = []
        try:
            if str(UTILS) not in sys.path:
                sys.path.insert(0, str(UTILS))
            import review_identity                                   # noqa: PLC0415
            rp = review_identity.receipts_path()
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.touch(exist_ok=True)
            out.append(rp)
        except Exception:                                            # noqa: BLE001 -- receipt is best-effort there too
            pass
        try:
            from rmpaths import rm_path                              # noqa: PLC0415
            cs = Path(os.environ.get("CODEX_SCRATCH") or rm_path("scratch", "codex"))
            cs.mkdir(parents=True, exist_ok=True)
            out.append(cs)
        except Exception:                                            # noqa: BLE001
            pass
        return out

    def __call__(self, prompt: str, work: Path) -> str:
        pf = work / ("gpt_prompt_%s.md" % secrets.token_hex(3))
        out = work / (pf.stem + "_answer.md")
        pf.write_text(prompt, encoding="utf-8")
        exe = self.prefix or [sys.executable, str(UTILS / "gpt_consult.py")]
        # the call log lives under the (masked) arena root: meter into the work dir, the harness appends it after
        local_log = work / (pf.stem + "_calls.jsonl")
        env = dict(os.environ, RM_GPT_CALL_LOG=str(local_log))
        real_log = Path(os.environ.get("RM_GPT_CALL_LOG") or "/mnt/d/ClaudeWork/rimmandrake/arena/gpt_calls.jsonl")
        r = run_sandboxed(exe + ["--prompt-file", str(pf), "--out", str(out), "--timeout", str(self.timeout)],
                          work=work, priv=self.priv, timeout=self.timeout + 60, env=env,
                          rw=[work] + self._scratch_paths())
        if local_log.is_file():
            try:
                real_log.parent.mkdir(parents=True, exist_ok=True)
                with open(real_log, "a", encoding="utf-8") as f:
                    f.write(local_log.read_text(encoding="utf-8"))
            except OSError:
                pass
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

GATE_KEYS = ("verdict", "passed", "unmeasured")


def _gate_view(gate: dict | None, **kw) -> dict:
    """A WHITELIST of the gate record: the verdict and each step's status. Never its log_dir / record_file (the gate
    names its folder <arm>_<task>_<head12>_<stamp>), ts, task, base/head, or a step's `why` (agent ids)."""
    gate = gate or {}
    g = {k: gate[k] for k in GATE_KEYS if k in gate}
    steps = gate.get("steps")
    if isinstance(steps, dict):
        g["steps"] = {str(k): (v.get("status") if isinstance(v, dict) else v) for k, v in sorted(steps.items())}
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
        if any(h["result"] in ("error", "no_marker") for h in rec["hidden"]):
            return done("invalid", "a hidden check could not finish: " +
                        ", ".join("%s (%s)" % (h["path"], h["result"]) for h in rec["hidden"]
                                  if h["result"] in ("error", "no_marker")))
        if any(h["result"] == "fail" for h in rec["hidden"]):
            return done("reject", "hidden check failed: " +
                        ", ".join(h["path"] for h in rec["hidden"] if h["result"] == "fail"))

    kw = {"clone": clone, "shas": (base, head), "extra_tokens": extra_tokens}
    gview = _gate_view(gate, **kw)
    prompt = build_prompt(task.get("criteria") or "", gview, rec["hidden"], nd.text, labels)
    # the criteria and hidden-check paths come from the frozen task, identical for every arm; the gate record and
    # the diff come from the arm, so those are what must be clean
    leaks = find_leaks(json.dumps(gview, sort_keys=True) + "\n" + nd.text, clone=clone, extra_tokens=extra_tokens,
                       shas=(base, head))
    if leaks:
        return done("invalid", "prompt leaks the arm: " + "; ".join(leaks[:3]))
    (work / "prompt.md").write_text(prompt, encoding="utf-8")
    js = judges or Judges.real(priv)
    for call in (js.opus, js.gpt, js.tie):
        try:
            getattr(call, "preflight", lambda: None)()
        except JudgeError as ex:
            return done("invalid", "judge unavailable before any call: %s" % ex)
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
    return min(1.0, float(sum(math.comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(k, n + 1)))) if n else 1.0


EXACT_MAX = 8            # n! permutations enumerated exactly up to this many submissions
MC_DRAWS = 20000


def _perm_p(pairs_by_sub: list[list[tuple]], seed: int = 0) -> tuple:
    """One-sided permutation test of 'the guesses track the arm'. `pairs_by_sub` is one list per submission of
    (guess, truth) -- one pair per judge vote on it. Under the null the guesses are independent of which arm made
    which submission, so the submission truths are PERMUTED (jointly for all votes on a submission) and the statistic
    (total correct) recomputed. This conditions on the day's real arm mix AND on each judge's own guess mix, so an
    uninformed judge that always names the majority arm scores exactly its null and is never LEAKY.
    Returns (p_value, expected_correct_under_null, method)."""
    truths = [ps[0][1] for ps in pairs_by_sub]
    guesses = [[g for g, _ in ps] for ps in pairs_by_sub]
    n = len(truths)
    if not n:
        return 1.0, 0.0, "none"

    def stat(ts):
        return sum(g == t for gs, t in zip(guesses, ts) for g in gs)

    obs = stat(truths)
    from collections import Counter
    tc = Counter(truths)
    expected = sum(tc[g] / n for gs in guesses for g in gs)
    if n <= EXACT_MAX:
        tot = ge = 0
        for perm in permutations(truths):
            tot += 1
            ge += stat(perm) >= obs
        return ge / tot, expected, "exact"
    rng = random.Random(seed)
    ts, ge = list(truths), 0
    for _ in range(MC_DRAWS):
        rng.shuffle(ts)
        ge += stat(ts) >= obs
    return (ge + 1) / (MC_DRAWS + 1), expected, "monte_carlo_%d" % MC_DRAWS


def guess_report(records: list[dict], amap: dict, labels: tuple | None = None, alpha: float = 0.05) -> dict:
    """Per judge and pooled: did the arm guesses beat CHANCE, where chance is the day's own mix (a permutation test,
    _perm_p), not 1/len(labels). 'unknown' counts as a wrong guess (a judge cannot lower its rate by abstaining).
    Records with no map entry are skipped and counted. Multiplicity: per-judge tests plus the pooled one are judged
    at Bonferroni alpha/m. The pooled test keeps each submission's votes together (they are not independent).
    `binom_p` (vs 1/len(labels)) is reported for reference only; it is NOT the decision."""
    labels = tuple(labels or arms())
    q = 1.0 / len(labels)
    per, subs, unmapped = {}, [], 0
    for r in records:
        truth = (amap.get(r.get("judge_id")) or {}).get("arm")
        if truth is None:
            unmapped += 1
            continue
        pairs = []
        for v in r.get("votes") or []:
            g = v.get("arm_guess")
            g = g if g in labels else "unknown"
            per.setdefault(v.get("judge") or "?", []).append([(g, truth)])
            pairs.append((g, truth))
        if pairs:
            subs.append(pairs)
    m = len(per) + 1
    a_m = alpha / m
    rows = {}
    for name, ps in sorted(per.items()):
        n = len(ps)
        k = sum(g == t for (g, t), in ps)
        pv, ex, how = _perm_p(ps)
        rows[name] = {"correct": k, "guesses": n, "rate": k / n if n else None, "chance": ex / n if n else None,
                      "p_value": pv, "method": how, "binom_p": binom_sf(k, n, q), "leaky": pv < a_m}
    N = sum(len(ps) for ps in subs)
    K = sum(g == t for ps in subs for g, t in ps)
    pp, ex, how = _perm_p(subs)
    pooled = {"correct": K, "guesses": N, "rate": K / N if N else None, "chance": ex / N if N else None,
              "p_value": pp, "method": how, "binom_p": binom_sf(K, N, q), "leaky": pp < a_m}
    return {"chance": pooled["chance"], "q_plugin": q, "alpha": alpha, "alpha_per_test": a_m, "tests": m,
            "arms": list(labels), "per_judge": rows, "pooled": pooled,
            "submissions": len(records) - unmapped, "unmapped": unmapped,
            "blinding": "UNMEASURED" if not N else ("LEAKY" if pooled["leaky"] or any(r["leaky"] for r in rows.values())
                                                    else "not shown leaky")}


def write_report(day: str | None = None, *, p: dict | None = None, priv: Path | None = None,
                 work_base: Path | None = None) -> Path:
    p = p or A.paths()
    amap = ArmMap(p, priv).read()
    day = day or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    recs, unreadable = [], 0
    for f in sorted(Path(work_base or work_root()).glob("J*/verdict.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
            if not isinstance(r, dict) or not isinstance(r.get("votes", []), list):
                raise ValueError("not a verdict record")
            for v in r.get("votes") or []:
                if not isinstance(v, dict):
                    raise ValueError("vote is not an object")
        except (OSError, ValueError):
            unreadable += 1                  # skipped and COUNTED: one bad file never hides the rest
            continue
        if str(r.get("ts", "")).startswith(day):
            recs.append(r)
    rep = guess_report(recs, amap)
    rep["day"] = day
    rep["unreadable"] = unreadable
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
