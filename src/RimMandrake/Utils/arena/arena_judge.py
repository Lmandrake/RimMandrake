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
copy of the tree per check (it cannot tamper with the next check, the judge code or the host); each MODEL call gets a
FRESH private workspace <work root>/.jw/<random> (0700, empty, its cwd, deleted after the call), so no two judges
share a directory and none can leave the next a note; the Opus run gets $HOME too (claude rewrites its config; it
runs no tools, no arm code, --no-session-persistence); the GPT run gets codex scratch and the consult receipts.
The environment is an ALLOW-LIST (judge_env: locale/PATH/HOME basics, plus for a model call only its own CLI/auth
variables), never the harness's inherited environment; ARENA_* and any value naming the private dir or clone root are
dropped. A timeout SIGKILLs the whole process group and the pid namespace with it. No bwrap -> the judge refuses.

NO JUDGE SEES THE RAW TREE (fix round 2, GPT review #1/#4). The head tree is materialised only for the hidden checks
and is DELETED (with every per-check copy) before any model is asked; a model receives the neutralised diff and the
whitelisted gate view in its prompt on stdin, never a path to anything. The prompt, argv and env of a model call name
no submission directory (selftest t_isolation).

GIT IS NEVER RUN ON ARM-CONTROLLED CONFIG (GPT review #3). The arm owns its clone's .git/config, info/attributes and
.gitattributes, any of which can name a textconv / external diff / filter / fsmonitor / hook COMMAND that git would
run as the harness. So the harness never runs git in the clone: SafeRepo makes a throwaway bare repo whose object
store BORROWS the clone's objects (GIT_ALTERNATE_OBJECT_DIRECTORIES, read-only), with GIT_CONFIG_NOSYSTEM,
GIT_CONFIG_GLOBAL=/dev/null, core.attributesFile=/dev/null, core.hooksPath=/dev/null, core.fsmonitor= and
diff.external= forced, and every diff `--no-ext-diff --no-textconv --no-renames`. The tree is read by
`ls-tree -z` + `cat-file --batch` (no `git archive`: no export-subst, no filters, no commit timestamps). Names are
NUL-delimited with core.quotepath=off and passed as --literal-pathspecs (GPT review #7: a tab, newline, non-ASCII or
leading-dash name is diffed, not silently dropped); a changed file whose diff comes back empty fails CLOSED.

HIDDEN-CHECK PASS needs proof the check ran to its end: each check runs under a harness-owned runner that reads a
fresh nonce on stdin, compiles and runs the test file as __main__, and only after it returns writes
`ARENA_CHECK_DONE <nonce>` to a private dup of stdout. EVERY pass needs that marker. A SystemExit(0/None) counts as
the check finishing only when it was raised by the check file's OWN code (the deepest traceback frame is one of the
test file's code objects, so `sys.exit(main())` works); raised inside an imported arm module (GPT review #2) it is
"raised outside the check body" -> fail. rc 0 without the line (os._exit(0), atexit, a hooked excepthook, a forged
marker without the nonce) is `no_marker` -> invalid. A REPLAY task with no hidden-check file fails CLOSED -> invalid
(GPT review #8).

WHERE THINGS LIVE
  $ARENA_PRIVATE (default ~/.local/state/rm_arena_private, dir 0700, files 0600)
      arm_map.json          judge_id -> {arm, task, base, head, ts}. Harness-only. Refused if it sits inside an
                            arm-readable root, the judge work root or the arena judge dir.
  $ARENA_JUDGE_WORK (default <clone root>/judge, i.e. /home/mandrake/rm/arena/judge: §1.6 bills it to the harness)
      <judge_id>/diff.patch     the neutralised diff (head minus base over `area`)
      <judge_id>/tree/          head (TREE_PATHS + area dirs) for the hidden checks; deleted before any model call
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
(NeutraliserLeak). A second, boundary-blind scan (glued_residue, GPT review #6) looks for an arm name glued inside a
longer identifier (`xralph_afoo`, `trioxide`) that the boundary matcher cannot see; any such identifier refuses the
submission unless a human listed it in <arena>/glued_allowlist.txt (one identifier per line). The gate record reaches the prompt only as a whitelist: its verdict and each step's status (never
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
together), Bonferroni over the tests. The test is TWO-SIDED (GPT review #10): consistently naming the wrong arm is
knowledge too. An always-the-majority guesser is therefore never LEAKY.
DECISION RULE, deliberately NOT the spec's (GPT review #9): the spec asked for "binomial p<0.05 vs 1/len(arms)". That
binomial assumes every arm equally likely on every submission (the day's mix is unequal) and, pooled, treats the
correlated votes on one submission as independent trials; it calls a blind majority-guesser leaky. LEAKY is decided by
the permutation p_value; `binom_p` (log-space, safe at any n) is still printed in every row for reference, and the
report carries this rule as its `decision` field.

RESIDUAL (stated, not hidden):
  - gpt_consult runs codex.exe, a WINDOWS process the Linux sandbox does not confine. It gets only the neutralised
    prompt (no path, sha, time or gate folder), but its own read-only sandbox can read \\wsl.localhost paths: the arm
    clones, the arm map at its default path (named in this source), ~/.claude/projects, the arena event log and the
    gate folders arena_gate.py names <arm>_<task>_<head12>_<stamp>. Setting ARENA_PRIVATE to an unpublished path
    narrows the map; nothing here can stop a model that goes looking. The guess-rate report is the detector.
  - SAME-UID ARMS (GPT round 2 #2, criterion-breaking, NOT fixed here): the arms run as the same OS user as the
    harness. 0700/0600 modes do not stop a same-uid process, so an arm acting BEFORE a judge runs can read or copy the
    arm map, plant it in model config, edit a hidden-check JSON before judge_task() reads it, or edit verdict.json
    before the report. The sandbox masks only bind what runs INSIDE the judge; the only real fix is a separate uid (or
    host) for the arms, which is outside this module.
  - WINDOWS codex.exe (GPT round 2 #1, criterion-breaking, NOT fixed here): the GPT judge is a Windows process that
    bubblewrap cannot confine (below); the selftest's Linux stand-in IS confined, so the green arm-map test does not
    cover the production GPT path.
  - arm code inside a hidden check shares the runner's interpreter. Round 3 seals the nonce (see the runner comment):
    gone from every Python frame, readable only by native code, a CPython memory bug, or an arm that rewrites the check
    namespace it shares; an arm object with a lying __eq__ can still satisfy an assert.
  - the Opus run's writable $HOME means claude still auto-loads the user's own ~/.claude config/CLAUDE.md (it names
    no arm); the model has no tools to read further.
  - the guess test assumes exchangeable submissions (no task/replay-family/time structure), DECIDES on accuracy, and
    alpha is per report, not across repeated daily reports (see DESIGN CALLS #11 for the secondary MI statistic).

FIX ROUND 3 (GPT review of round 2), each with a forced-failure selftest red against round-2 code:
  #3 nonce: the runner reads the nonce from stdin into a sealed generator, never a frame local; an audit hook denies
     frame/gc/trace/monitoring/ctypes/code-object/marshal access, /proc and `mem` opens (the check sandbox also gets a
     tmpfs /proc); module-level sys.exit/SystemExit in the CHECK's own source is rewritten to a seal send at a known
     bytecode offset, so only the check's own top frame can finish it; exactly one marker line, or no_marker.
  #4 a replay whose hidden file runs nothing ({} / empty / unsupported / unauthored / body-less / malformed) or where
     no hidden check passed is invalid before any model call.
  #5 a non-string judge_id, vote judge or arm_guess is skipped and counted unreadable; guess_report guards too.
  #6 one fixture per leak detector, each firing alone; glued_residue no longer re-reports what the boundary matcher
     sees, and find_leaks(_off=...) lets each detector be mutated off in the selftest.
  #10 a binary change (numstat `-`, "Binary files differ", GIT binary patch) is a JudgeError: never judged blind.
  #12 parse_answer requires exactly one distinct verdict object.
DESIGN CALLS (documented, not changed):
  #7 judge_masks() masks the CONFIGURED roots (ARENA_CLONES, ARENA_PRIVATE, arena root); a clone or work_base passed
     from elsewhere is not masked. Callers must keep submissions under those roots (not enforced here).
  #8 judges are fresh processes, not independent ones: Opus shares the real $HOME (~/.claude auto-loads), GPT shares
     its scratch/receipt dirs, and a same-uid arm can pre-seed both. opus_model() accepts any non-empty model string;
     that the primary and tie-break are really Opus is the operator's configuration, not verified here.
  #9 the leak scan is lexical: the `import trio` / `v3.2` exemptions are deliberate (reported ambiguous) and an arm
     can choose them as a signal; escaped, encoded or respelled names outside the skeleton map are not caught. The
     guess report is the backstop, not a proof that identity was removed.
  #11 accuracy stays the pre-registered decision (`blinding`). A secondary mutual-information statistic (bits, same
     submission-level one-sided permutation, `mi_bits`/`mi_p`, `blinding_secondary`) catches a one-to-one relabelling
     at chance accuracy; it is upward-biased with few submissions per arm, so it flags for investigation only and
     does not enter the Bonferroni count.
  - glued_residue refuses legitimate words that contain an arm name until a human allowlists them (fail closed).
  - the real `claude -p` / codex.exe have not been run inside this sandbox by the selftests (they cost money).
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import fnmatch
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
import unicodedata
from itertools import permutations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402
import judge_codex_home as JH  # noqa: E402

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


GLUED_ALLOW_FILE = "<arena root>/glued_allowlist.txt"


def glued_allowlist(p: dict | None = None) -> tuple:
    """Identifiers a HUMAN has ruled are not arm names although one is glued inside (`trioxide`): one per line in
    <arena root>/glued_allowlist.txt, '#' comments. Harness-side only (the arena root is masked from judges). No file
    -> empty: every glued residue refuses."""
    try:
        f = (p or A.paths())["root"] / "glued_allowlist.txt"
        lines = f.read_text(encoding="utf-8").splitlines() if f.is_file() else []
    except Exception:                                # noqa: BLE001 -- no arena root configured: nothing allowed
        return ()
    return tuple(x.split("#", 1)[0].strip() for x in lines if x.split("#", 1)[0].strip())


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

def sandbox_argv(argv: list[str], *, masks: list[Path], keep: list[Path], chdir: Path | None = None,
                 proc: bool = True) -> list[str]:
    """READ-ONLY root (`--ro-bind / /`), a fresh /tmp, its own pid namespace (no host /proc, and the whole tree dies
    with it), `masks` hidden under empty tmpfs, and ONLY `keep` writable. Order: kept dirs outside every mask are
    bound first, then the masks are laid (so a broad bind like $HOME never re-exposes ~/.claude/projects), then the
    kept paths that live inside a mask (the judge's own work dir under the clone root) are bound back."""
    bw = shutil.which("bwrap")
    if not bw:
        raise JudgeUnavailable("bwrap not found: the judge never runs unsandboxed")
    # proc=False (a hidden check: arm code runs there) lays an empty tmpfs over /proc instead (fix round 3, #3)
    out = [bw, "--ro-bind", "/", "/", "--dev", "/dev"] + (["--proc", "/proc"] if proc else ["--tmpfs", "/proc"]) + [
           "--tmpfs", "/tmp",
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


# The judge-side environment is an ALLOW-LIST (fix round 2): nothing the harness inherited reaches a judge unless it
# is named here. `check` (a hidden check: arm code runs in it) gets only the basics, never a model credential.
ENV_BASIC = ("PATH", "HOME", "USER", "LOGNAME", "LANG", "LANGUAGE", "TZ", "TERM")
ENV_BASIC_PREFIX = ("LC_",)
ENV_MODEL = ("SHELL", "CLAUDE_CONFIG_DIR", "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "http_proxy",
             "https_proxy", "no_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "RM_DATA_ROOT", "AGENT_STORAGE_ROOT",
             "RM_CONSULT_RECEIPTS", "XDG_RUNTIME_DIR")
ENV_MODEL_PREFIX = ("ANTHROPIC_", "CLAUDE_CODE_USE_", "OPENAI_", "CODEX_", "WSL", "RM_GPT_")


def judge_env(extra: dict | None, priv: Path | None, kind: str = "model", base: dict | None = None,
              own: Path | None = None) -> dict:
    """The judge's environment, built from an allow-list over `base` (default os.environ): `check` -> ENV_BASIC only;
    `model` -> also what claude / gpt_consult / codex.exe need (auth, proxy, WSL interop, codex scratch). Then `extra`
    (the caller's own explicit settings). Any value naming the private dir or the clone root is dropped; RM_ARM=harness
    (§1.6: judge spend is the harness's). EXCEPT (ARENA_JUDGE_GPT_METER_STRIPPED_BY_ENV): an `extra` value that is a
    path inside `own`, the call's own workspace, survives the clone-root filter -- the default work root sits under
    clones_root, so the filter used to drop GptConsult's RM_GPT_CALL_LOG=<work>/calls.jsonl and no judge GPT call was
    ever metered. The call already holds that dir read-write, so naming it leaks nothing."""
    src = dict(os.environ if base is None else base)
    names, prefixes = ENV_BASIC, ENV_BASIC_PREFIX
    if kind == "model":
        names, prefixes = names + ENV_MODEL, prefixes + ENV_MODEL_PREFIX
    e = {k: v for k, v in src.items() if k in names or k.startswith(prefixes)}
    e.update(extra or {})
    pv, cr = os.path.realpath(Path(priv) if priv else private_dir()), os.path.realpath(clones_root())
    ownr = os.path.realpath(own) if own else None

    def owned(k):
        if not ownr or k not in (extra or {}):
            return False
        return JH.posix_within(extra[k], ownr)               # separator-aware: <own>_evil is not inside <own>
    for k in list(e):
        v = str(e[k])
        if k.startswith("ARENA_") or (pv and pv in v) or (cr and cr in v and not owned(k)):
            e.pop(k, None)
    e["RM_ARM"] = "harness"
    return e


def run_sandboxed(argv, *, work: Path, priv: Path | None = None, stdin: bytes | None = None,
                  timeout: int = CHECK_TIMEOUT, env: dict | None = None, cwd: Path | None = None,
                  rw: list[Path] | None = None, kind: str = "model"):
    """`rw` defaults to [work]; a hidden check passes its own per-check scratch copy instead. `env` holds only the
    caller's EXTRA variables (the rest is judge_env's allow-list for `kind`). On timeout the whole process group is
    SIGKILLed (bwrap --die-with-parent then takes the pid namespace, grandchildren included)."""
    keep = [work] if rw is None else list(rw)
    full = sandbox_argv(list(argv), masks=judge_masks(priv), keep=keep, chdir=cwd or work, proc=kind != "check")
    proc = subprocess.Popen(full, cwd="/", stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=judge_env(env, priv, kind, own=work),
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


def _find_tokens_sk(text: str, tokens) -> tuple:
    """-> (skeleton, idx, spans, ambiguous, exempt): `spans` in the ORIGINAL text, `ambiguous` the exempted (version /
    import) occurrences as strings, `exempt` their (start, end) in the SKELETON."""
    sk, idx = _skeleton(text)
    pat = re.compile("|".join("(?:%s)" % _token_re(t) for t in tokens))
    spans, amb, exempt = [], [], []
    for m in pat.finditer(sk):
        s, e = m.start(), m.end()
        word = m.group(0)
        ls = sk.rfind("\n", 0, s) + 1
        single = [t for t in tokens if t.lower() == word.lower() and t.lower() not in FAMILY_TOKENS
                  and re.fullmatch(r"[a-z][a-z0-9]*", t.lower())]
        if single and word.islower() and IMPORT_PREFIX_RE.match(sk[ls:s]) and \
                not re.match(r"[A-Za-z0-9_]", sk[e:e + 1]):
            amb.append(word)
            exempt.append((s, e))
            continue
        if idx is not None:
            s, e = idx[s], idx[e - 1] + 1
        spans.append((s, e))
    vers = [t for t in tokens if t[-1:].isdigit()]
    if vers:                                         # the version exemption, reported (never silently passed)
        vpat = re.compile("|".join("(?:%s)" % (_LEFT + _token_re(t)[len(_LEFT):].split("(?!")[0] + r"\.\d+")
                                   for t in vers))
        for m in vpat.finditer(sk):
            amb.append(m.group(0))
            exempt.append((m.start(), m.end()))
    return sk, idx, spans, amb, exempt


def _find_tokens(text: str, tokens) -> tuple:
    """-> (spans, ambiguous): non-overlapping (start, end) spans in the ORIGINAL text naming a token, and the
    exempted (version / import) occurrences, as strings."""
    _, _, spans, amb, _ = _find_tokens_sk(text, tokens)
    return spans, amb


def glued_residue(text: str, tokens, allow=()) -> list[str]:
    """Fix round 2 (GPT review #6): an arm name GLUED inside a longer identifier with no seam (`xralph_afoo`,
    `trioxide`) escapes the boundary matcher, so the scrub leaves it and the matcher-based scan cannot see it. This
    scan looks for the bare token (separator-insensitive, case-insensitive, on the skeleton) ANYWHERE, minus the
    reported version/import exemptions; each hit names its whole enclosing identifier, which is refused unless a
    human-listed allowlist (`allow`: identifiers, case-insensitive) covers it. Returns the refused identifiers.
    Fix round 3 (GPT round 2 #6): an occurrence the boundary matcher ALREADY sees is that detector's hit, not glued
    residue, so each detector can be proven alone (find_leaks always runs the boundary matcher on the same text)."""
    sk, _, _, _, exempt = _find_tokens_sk(text, tokens)
    if tokens:
        exempt = exempt + [m.span() for m in re.finditer("|".join("(?:%s)" % _token_re(t) for t in tokens), sk)]
    allow = {a.lower() for a in allow}
    out = []
    for t in tokens:
        parts = [re.escape(x) for x in re.split(r"[_\-\s.]+", t) if x]
        for m in re.finditer(r"[_\-\s.]*".join(parts), sk, re.IGNORECASE):
            s, e = m.start(), m.end()
            if any(a <= s and e <= b for a, b in exempt):
                continue
            ws, we = s, e
            while ws > 0 and (sk[ws - 1].isalnum() or sk[ws - 1] == "_"):
                ws -= 1
            while we < len(sk) and (sk[we].isalnum() or sk[we] == "_"):
                we += 1
            word = sk[ws:we]
            if word.lower() not in allow and word not in out:
                out.append(word)
    return out


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


LEAK_DETECTORS = ("arm token", "model name", "glued", "clone path", "clone root path", "sha", "trailer", "session url",
                  "branch ref")


def find_leaks(text: str, *, clone: Path | None = None, extra_tokens=(), shas=(), ambiguous: list | None = None,
               allow=None, _off=()) -> list[str]:
    """The SAME token matcher as scrub (skeleton, glued, plural): anything it finds refuses. Exempted occurrences
    (version, import of a real module) are not hits; they are appended to `ambiguous` when a list is passed. Then the
    glued-residue scan (glued_residue): an arm name inside a longer identifier the scrub could not cut refuses unless
    `allow` (default: glued_allowlist()) lists that identifier; the refused identifier is also reported ambiguous.
    `_off` (selftest only, fix round 3 #6) names LEAK_DETECTORS to skip, so each detector's forced-failure fixture
    can be shown to depend on that detector alone. Every hit string starts with its detector's label."""
    hits = []
    for what, toks in (("arm token", arm_tokens(extra_tokens)), ("model name", MODEL_TOKENS)):
        if what in _off:
            continue
        spans, amb = _find_tokens(text, toks)
        if spans:
            s, e = spans[0]
            hits.append("%s %r at %d" % (what, text[s:e], s))
        if ambiguous is not None:
            ambiguous += amb
    glued = [] if "glued" in _off else glued_residue(text, arm_tokens(extra_tokens),
                                                      glued_allowlist() if allow is None else allow)
    if glued:
        hits.append("glued arm name in identifier(s) %s (ambiguous: refused; a human may list the identifier in %s)"
                    % (", ".join(repr(g) for g in glued[:5]), GLUED_ALLOW_FILE))
        if ambiguous is not None:
            ambiguous += ["glued:" + g for g in glued]
    sk = _skeleton(text)[0]
    if clone is not None and "clone path" not in _off:
        for f in _path_forms(Path(clone)):
            if f.lower() in sk.lower():
                hits.append("clone path %r" % f)
    for f in () if "clone root path" in _off else _path_forms(clones_root()):
        if re.search(re.escape(f) + r"[/\\-][A-Za-z0-9_.\-]+", sk, re.IGNORECASE):
            hits.append("clone root path %r" % f)
    for s in () if "sha" in _off else shas:
        if s and len(s) >= 7 and re.search(_sha_re(s), sk):
            hits.append("sha %s" % s[:7])
    for rx, what in ((TRAILER_RE, "trailer"), (SESSION_RE, "session url"), (BRANCH_RE, "branch ref")):
        m = None if what in _off else rx.search(sk)
        if m and "<TRAILER>" not in m.group(0):
            hits.append("%s %r" % (what, m.group(0)[:60]))
    return hits


# ---- git, harness side, against an ARM-CONTROLLED clone (fix round 2, GPT review #3/#7). The clone's own
# .git/config, .gitattributes, hooks and fsmonitor are never consulted: every git call runs in a throwaway BARE
# repository the harness creates (its own empty config, no templates) that borrows the arm's object store through
# GIT_ALTERNATE_OBJECT_DIRECTORIES. On top of that each call carries the hardening flags and a scrubbed environment
# (no system/global config or attributes, no inherited GIT_*), diffs run with --no-ext-diff --no-textconv, and the
# tree is written from `ls-tree -z` + `cat-file --batch` blobs (git archive would apply in-tree attributes:
# export-subst, filters). Filenames are consumed NUL-delimited (-z), with --literal-pathspecs and core.quotepath=off.
GIT_HARDEN = ("-c", "diff.external=", "-c", "core.fsmonitor=", "-c", "core.hooksPath=/dev/null",
              "-c", "core.quotepath=off", "-c", "core.attributesFile=/dev/null", "-c", "protocol.allow=never",
              "--literal-pathspecs", "--no-replace-objects")
DIFF_SAFE = ("--no-color", "--no-ext-diff", "--no-textconv", "--no-renames")


def _arm_gitdirs(clone: Path) -> tuple:
    """-> (gitdir holding HEAD, objects dir) of a clone, read from the filesystem without running git in it."""
    clone = Path(clone)
    g = clone / ".git"
    if g.is_file():                                          # a linked worktree / submodule: `gitdir: X`
        m = re.match(r"gitdir:\s*(.+)", g.read_text(encoding="utf-8", errors="replace").strip())
        if not m:
            raise JudgeError("unreadable .git file in %s" % clone)
        g = (clone / m.group(1).strip()).resolve()
    elif not g.is_dir():
        if (clone / "objects").is_dir() and (clone / "HEAD").is_file():
            g = clone                                        # a bare clone
        else:
            raise JudgeError("%s is not a git clone" % clone)
    common = g
    if (g / "commondir").is_file():
        common = (g / (g / "commondir").read_text(encoding="utf-8").strip()).resolve()
    objs = common / "objects"
    if not objs.is_dir():
        raise JudgeError("no object store under %s" % common)
    return g, objs.resolve()


class SafeRepo:
    """A harness-owned bare repo over the arm clone's objects. Use as a context manager; `git()` returns bytes."""

    def __init__(self, clone: Path):
        import tempfile                                      # noqa: PLC0415
        self.gitdir, objs = _arm_gitdirs(clone)
        self.tmp = Path(tempfile.mkdtemp(prefix="arena_git_"))
        self.env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp), "LC_ALL": "C",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_ATTR_NOSYSTEM": "1",
                    "GIT_TERMINAL_PROMPT": "0", "GIT_NO_REPLACE_OBJECTS": "1", "GIT_DIR": str(self.tmp),
                    "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(objs), "XDG_CONFIG_HOME": str(self.tmp / "xdg")}
        r = subprocess.run(["git", *GIT_HARDEN, "init", "-q", "--bare", "--template=", str(self.tmp)],
                           capture_output=True, env=self.env, cwd=str(self.tmp))
        if r.returncode:
            self.close()
            raise JudgeError("git init (shadow): %s" % r.stderr.decode("utf-8", "replace")[:300])

    def git(self, *args, stdin: bytes | None = None) -> bytes:
        r = subprocess.run(["git", *GIT_HARDEN, *args], input=stdin, capture_output=True, env=self.env,
                           cwd=str(self.tmp))
        if r.returncode:
            raise JudgeError("git %s: %s" % (" ".join(args[:3]), r.stderr.decode("utf-8", "replace").strip()[:300]))
        return r.stdout

    def branch(self) -> str | None:
        """The clone's checked-out branch name, read from its HEAD file (no git run in the clone)."""
        try:
            h = (self.gitdir / "HEAD").read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            return None
        return h[len("ref: refs/heads/"):] if h.startswith("ref: refs/heads/") else None

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def _z(out: bytes) -> list[str]:
    """NUL-delimited git output -> names (surrogateescape keeps the exact bytes for reuse as a pathspec)."""
    return [x.decode("utf-8", "surrogateescape") for x in out.split(b"\0") if x]


def in_area(path: str, area: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in area)


def is_arm_bookkeeping(path: str) -> bool:
    return A.is_bookkeeping(path) or any(fnmatch.fnmatch(path, g) for g in ARM_BOOKKEEPING)


def neutralise(clone: Path, base: str, head: str, area: list[str], *, extra_tokens=(), do_scrub=True,
               allow=None) -> Neutral:
    """Head minus base over `area`, stripped and re-rooted. Raises NeutraliserLeak when anything arm-identifying is
    left. `do_scrub=False` exists only so the selftest can prove the leak scan catches an unscrubbed diff."""
    clone = Path(clone)
    with SafeRepo(clone) as g:
        names = _z(g.git("diff", *DIFF_SAFE, "--name-only", "-z", base, head, "--"))
        stripped = [x for x in names if is_arm_bookkeeping(x) or not in_area(x, area)]
        files = [x for x in names if x not in stripped]
        parts = []
        for f in files:                       # one diff per changed file: a file that yields nothing fails CLOSED
            d = g.git("diff", *DIFF_SAFE, "--src-prefix=a/", "--dst-prefix=b/", base, head, "--", f)
            if not d.strip():
                raise JudgeError("changed file %r produced no diff: a partial diff is never judged" % f)
            # fix round 3 (GPT round 2 #10): a binary change shows only "Binary files ... differ", hiding both the
            # implementation and any identity it carries: it can never be judged blind (git's own numstat decides)
            ns = g.git("diff", *DIFF_SAFE, "--numstat", "-z", base, head, "--", f)
            if ns.startswith(b"-\t-\t") or re.search(rb"(?m)^(Binary files .* differ|GIT binary patch)$", d):
                raise JudgeError("changed file %r is a binary change: its content cannot be shown, so it cannot be "
                                 "judged blind" % f)
            parts.append(d.decode("utf-8", "replace"))
        branch = g.branch()
    raw = "".join(parts)
    counts = {}
    text = raw
    if do_scrub:
        text, counts = scrub(raw, clone=clone, shas=(base, head), branch=branch, extra_tokens=extra_tokens)
    amb = []
    leaks = find_leaks(text, clone=clone, extra_tokens=extra_tokens, shas=(base, head), ambiguous=amb, allow=allow)
    if leaks:
        raise NeutraliserLeak("neutralised diff still identifies the arm: " + "; ".join(leaks[:5]))
    if amb:
        counts["ambiguous_kept"] = sorted(set(amb))
    neutral_files = [scrub(f, extra_tokens=extra_tokens)[0] for f in files]
    return Neutral(text=text, files=neutral_files, stripped=stripped, redactions=counts)


# ---------------------------------------------------------------- hidden checks (judge side, sandboxed)

def materialise(clone: Path, head: str, area: list[str], dest: Path, tree_paths=TREE_PATHS) -> Path:
    """head's blobs under TREE_PATHS + the area dirs, written into dest (no .git, no branch, no commit message, no
    commit timestamps, no in-tree attribute processing). Read from a SafeRepo: `ls-tree -r -z` then `cat-file
    --batch`. A symlink is kept only when relative and resolving inside dest; submodules are skipped; a path with a
    `..`/`.git` component, or one reaching through a symlink, refuses (JudgeError)."""
    want = set(tree_paths)
    for g in area:
        d = g.split("*", 1)[0].rstrip("/")
        if d and d != ".":
            want.add(d)
    dest.mkdir(parents=True, exist_ok=True)
    root = os.path.realpath(dest)
    with SafeRepo(Path(clone)) as g:
        entries = []
        for rec in g.git("ls-tree", "-r", "-z", "--full-tree", head, "--", *sorted(want)).split(b"\0"):
            if not rec:
                continue
            meta, _, name = rec.partition(b"\t")
            mode, typ, sha = meta.decode().split()
            if typ == "blob":
                entries.append((mode, sha, name.decode("utf-8", "surrogateescape")))
        if not entries:
            return dest
        out = g.git("cat-file", "--batch", stdin="".join(s + "\n" for _, s, _ in entries).encode())
    pos = 0
    for mode, sha, name in entries:
        nl = out.index(b"\n", pos)
        hdr = out[pos:nl].split()
        if len(hdr) != 3 or hdr[0].decode() != sha:
            raise JudgeError("cat-file --batch out of step at %s" % name)
        size = int(hdr[2])
        body = out[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
        parts = name.split("/")
        if any(x in ("", ".", "..") or x.lower() == ".git" for x in parts):
            raise JudgeError("tree path %r has an unsafe component" % name)
        target = Path(root, *parts)
        anc = target.parent
        while not anc.exists() and not anc.is_symlink():
            anc = anc.parent
        if not _inside(anc, Path(root)):
            raise JudgeError("tree path %r reaches outside the tree through a symlink" % name)
        target.parent.mkdir(parents=True, exist_ok=True)
        if mode == "120000":
            link = body.decode("utf-8", "surrogateescape")
            if not os.path.isabs(link) and _inside(Path(os.path.normpath(target.parent / link)), Path(root)):
                os.symlink(link, target)
            continue
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o755 if mode == "100755" else 0o644)
        with os.fdopen(fd, "wb") as f:
            f.write(body)
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
# generated and handed over on stdin (never in argv, env or a file). `-P` keeps the arm's tree off sys.path until the
# runner's own imports are done. atexit handlers never run (posix._exit).
#
# Fix round 3 (GPT round 2, #3): the round-2 runner kept the nonce in `_main()`'s locals while arm code ran in the same
# interpreter, so an imported module could walk frames (sys._getframe / inspect.stack), read it, print the real marker
# and os._exit(0). A completion signal emitted by the process that also runs the arm's code can never be made
# unforgeable in principle (exit status and stdout are both the arm's), so the parent-only nonce of the brief is not
# achievable for an in-process Python check; the runner instead makes the nonce UNREACHABLE from Python:
#   * it is read with posix.read(0) (stdin is then replaced by /dev/null) and lives ONLY in the frame of a suspended
#     generator (`_seal`), never in a module, a global, `_main()`'s locals, argv, env or a file;
#   * an irremovable audit hook (no audit hook can be removed or listed) kills the process (rc 86, `denied`) on every
#     Python route to that frame or to raw memory: `gi_frame` on the seal; any frame acquisition (sys._getframe,
#     tb_frame, gi/cr/ag_frame) while the seal runs; sys._current_frames/_current_exceptions; gc.get_objects/
#     get_referrers/get_referents; settrace/setprofile (all-threads too)/sys.monitoring callbacks/sys.remote_exec;
#     code.__new__ (code.replace too) and marshal.load(s) (crafted bytecode; pyc lookup is pointed at a nonexistent
#     pycache_prefix so source imports never call marshal, and every FROZEN stdlib module (ntpath, runpy,
#     importlib.util...: FrozenImporter unmarshals them, and `_imp.get_frozen_object(name, data)` would unmarshal
#     arm bytes, so marshal stays denied) is imported before the hook goes in; ARENA_RUNNER_FIX_FROZEN_PATHLIB_DENIED:
#     `import pathlib` was denied, ~70% of real fix_tests); ctypes (import and every ctypes.* event), _test*/subinterpreter
#     modules and interpreter creation (a subinterpreter has no hooks); further audit hooks; setrlimit (core dumps are
#     disabled with a hard RLIMIT_CORE of 0 before any arm code); any open of a file named `mem` or on procfs, and the
#     check sandbox mounts an empty tmpfs on /proc (no /proc/self/mem, environ or cmdline at all);
#   * the seal writes the marker only when resumed from `_main()` after exec() returned normally, or from the check's
#     OWN top-level frame at an injected call: the runner parses the check and rewrites each module-level
#     `sys.exit(X)` / `raise SystemExit(X)` (also inside top-level `if` blocks, i.e. `if __name__ == "__main__"`) into
#     `__arena_seal__.send(X)` followed by a `[][0]` trap; the seal checks the caller frame by identity (`f_back`,
#     `f_code is top`, `f_lasti` at the injected CALL) and that the same top frame registered itself at the first
#     statement, so a re-run of the check code from arm code is refused (rc 87). A SystemExit raised ANYWHERE else (an
#     arm module, a C slot aliased to sys.exit, a nested function) is never a success, so the round-2 rule "SystemExit
#     from a check code object" (forgeable through C-slot aliases such as `__bool__ = staticmethod(partial(gen.throw,
#     SystemExit(0)))`) is gone;
#   * the parent accepts exactly ONE marker line and it must carry the nonce (`_check_result`): any other marker line
#     means the output was tampered with and the check is not a pass.
# RESIDUAL (stated, not closed): native code in the check process runs below every audit hook: an arm-shipped
# extension module loaded through importlib, or a CPython memory-safety bug, can read the generator's frame and forge
# the marker; and arm code can still rewrite the check's own namespace (its imported helpers, its globals) so that
# assertions test something else. Only running the check in a process that never loads the arm's code would close
# those, and an import-based Python check cannot do that.
RUNNER = r'''
import os, sys, posix, types, ast, dis, io, resource, traceback
SENT_S, SENT_E = 999998, 999999
def _nonce():
    b = b""
    while len(b) < 200 and not b.endswith(b"\n"):
        c = posix.read(0, 64)
        if not c:
            break
        b += c
    z = posix.open(os.devnull, posix.O_RDONLY)
    posix.dup2(z, 0)
    posix.close(z)
    return b.strip()
def _seal(nonce, fd, s_offs, e_offs, top, w, x, gf, T, I):
    me = gf(0)
    home = me.f_back
    gf = None
    try:
        yield
        c = me.f_back
        if not (c is not None and c.f_back is home and c.f_code is top and c.f_lasti in s_offs):
            x(87)
        orig = c
        c = None
        v = yield
        c = me.f_back
        if c is home:
            ok = True
        elif c is orig and c.f_lasti in e_offs:
            ok = v is None or v is False or (T(v) is I and v == 0)
        else:
            x(87)
        if ok:
            w(fd, b"\nARENA_CHECK_DONE " + nonce + b"\n")
            x(0)
        x(1)
    except BaseException:
        x(87)
    x(87)
def _hook(g, x, w, T, S, B, N, st, pdev):
    ALWAYS = frozenset(("sys._current_frames", "sys._current_exceptions", "gc.get_objects", "gc.get_referrers",
                        "gc.get_referents", "sys.settrace", "sys.setprofile", "sys._settraceallthreads",
                        "sys._setprofileallthreads", "sys.monitoring.register_callback", "sys.remote_exec",
                        "code.__new__", "marshal.loads", "marshal.load", "sys.addaudithook",
                        "cpython.PyInterpreterState_New", "resource.setrlimit", "resource.prlimit"))
    FRAMEY = frozenset(("tb_frame", "gi_frame", "cr_frame", "ag_frame"))
    BADMOD = ("ctypes", "_ctypes", "_test", "_interp", "_xxsub", "_xxinterp", "concurrent.interpreters")
    def deny(ev):
        try:
            w(2, b"\nARENA_RUNNER_DENIED " + ev.encode("ascii", "replace") + b"\n")
        finally:
            x(86)
    def h(ev, args):
        if T(ev) is not S:
            return
        try:
            if ev == "object.__getattr__":
                o, n = args[0], args[1]
                if o is g or (g.gi_running and (T(n) is not S or n in FRAMEY)):
                    deny(ev)
            elif ev in ALWAYS or ev.startswith("ctypes."):
                deny(ev)
            elif ev == "sys._getframe":
                if g.gi_running:
                    deny(ev)
            elif ev == "import":
                m = args[0]
                if T(m) is not S or m.startswith(BADMOD):
                    deny(ev)
            elif ev == "open":
                p = args[0]
                if T(p) is N:
                    return
                if T(p) is not S and T(p) is not B:
                    deny(ev)
                q = p if T(p) is S else p.decode("utf-8", "surrogateescape")
                if q.rstrip("/").rsplit("/", 1)[-1] == "mem":
                    deny(ev)
                try:
                    if st(q).st_dev == pdev:
                        deny(ev)
                except OSError:
                    pass
        except BaseException:
            deny("hook")
    return h
def _exit_stmt(n):
    if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call):
        f, c = n.value.func, n.value
        if (isinstance(f, ast.Attribute) and f.attr == "exit" and isinstance(f.value, ast.Name)
                and f.value.id == "sys" and not c.keywords and len(c.args) <= 1
                and not any(isinstance(a, ast.Starred) for a in c.args)):
            return True, (c.args[0] if c.args else None)
    if isinstance(n, ast.Raise) and n.cause is None:
        e = n.exc
        if isinstance(e, ast.Name) and e.id == "SystemExit":
            return True, None
        if (isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id == "SystemExit"
                and not e.keywords and len(e.args) <= 1 and not any(isinstance(a, ast.Starred) for a in e.args)):
            return True, (e.args[0] if e.args else None)
    return False, None
def _send(arg, line):
    call = ast.Call(func=ast.Attribute(value=ast.Name(id="__arena_seal__", ctx=ast.Load()), attr="send",
                                       ctx=ast.Load()), args=[arg if arg is not None else ast.Constant(None)],
                    keywords=[])
    for k in (call, call.func, call.func.value):
        k.lineno, k.end_lineno, k.col_offset, k.end_col_offset = line, line, 0, 1
    s = ast.Expr(value=call)
    s.lineno, s.end_lineno, s.col_offset, s.end_col_offset = line, line, 0, 1
    return s
def _trap(line):
    s = ast.parse("[][0]").body[0]
    for k in ast.walk(s):
        if hasattr(k, "lineno"):
            k.lineno, k.end_lineno = line, line
    return s
def _rewrite(body):
    out = []
    for n in body:
        hit, a = _exit_stmt(n)
        if hit:
            out += [_send(a, SENT_E), _trap(SENT_E)]
            continue
        if isinstance(n, ast.If):
            n.body, n.orelse = _rewrite(n.body), _rewrite(n.orelse)
        out.append(n)
    return out
def _frozen():
    try:
        import _imp
        names = _imp._frozen_module_names()
    except BaseException:
        names = ("ntpath", "runpy", "importlib.machinery", "importlib.util", "io")
    for n in sorted(names):
        if n.startswith("__") or n in sys.modules:
            continue
        try:
            __import__(n)
        except BaseException:
            pass
def _main():
    so, se, fl, pe = sys.stdout, sys.stderr, io.TextIOWrapper.flush, traceback.print_exception
    test = sys.argv[1]
    with open(test, "rb") as f:
        tree = ast.parse(f.read(), test)
    body = _rewrite(tree.body)
    i = 0
    while i < len(body) and (isinstance(body[i], ast.ImportFrom) and body[i].module == "__future__" or
                             i == 0 and isinstance(body[i], ast.Expr) and isinstance(body[i].value, ast.Constant)
                             and isinstance(body[i].value.value, str)):
        i += 1
    body.insert(i, _send(None, SENT_S))
    tree.body = body
    ast.fix_missing_locations(tree)
    top = compile(tree, test, "exec", dont_inherit=True)
    ins = [(k.offset, k.positions.lineno if k.positions else None) for k in dis.get_instructions(top)
           if k.opname.startswith("CALL")]
    s_offs = frozenset(o for o, l in ins if l == SENT_S)
    e_offs = frozenset(o for o, l in ins if l == SENT_E)
    g = _seal(_nonce(), os.dup(1), s_offs, e_offs, top, posix.write, posix._exit, sys._getframe, type, int)
    next(g)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    sys.pycache_prefix = "/nonexistent/arena-no-pycache"
    _frozen()
    sys.addaudithook(_hook(g, posix._exit, posix.write, type, str, bytes, int, posix.stat, posix.stat("/proc").st_dev))
    sys.argv = [test]
    sys.path.insert(0, os.path.dirname(test))
    mod = types.ModuleType("__main__")
    mod.__file__ = test
    mod.__builtins__ = __builtins__
    mod.__dict__["__arena_seal__"] = g
    sys.modules["__main__"] = mod
    try:
        exec(top, mod.__dict__)
    except BaseException as e:
        try:
            pe(e)
        finally:
            posix._exit(1)
    for s in (so, se):
        try:
            fl(s)
        except BaseException:
            pass
    g.send(None)
    posix._exit(87)
_main()
'''
MARKER = "ARENA_CHECK_DONE "
UNFINISHED = ("error", "no_marker", "denied")
RUNNER_DENIED, RUNNER_TAMPER = 86, 87


def _check_result(rc: int, out: bytes, nonce: str) -> str:
    """pass ONLY on rc 0 AND exactly one marker line, the nonce's. rc 0 without it is `no_marker` (the check did not
    finish: invalid); a second or foreign marker line is `no_marker` too (output tampered); rc 86 is `denied` (the
    runner's audit hook stopped an introspection/memory route: invalid); rc 87 (the seal was resumed from a frame that
    is not the check's own) is `no_marker`."""
    if rc == 124:
        return "error"
    if rc == RUNNER_DENIED:
        return "denied"
    if rc == RUNNER_TAMPER:
        return "no_marker"
    if rc != 0:
        return "fail"
    lines = [x.strip() for x in out.decode("utf-8", "replace").splitlines()]
    marks = [x for x in lines if x.startswith(MARKER.strip())]
    return "pass" if marks == [MARKER + nonce] else "no_marker"


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
                          env={"PYTHONDONTWRITEBYTECODE": "1"}, kind="check")
        result = _check_result(r.returncode, r.stdout, nonce)
        tail = (r.stdout + r.stderr).decode("utf-8", "replace").replace(nonce, "<NONCE>")[-1500:]
        row = {"kind": c["kind"], "path": c["path"], "rc": r.returncode, "result": result, "tail": tail}
        if result == "no_marker":
            row["why"] = "no single harness completion marker: the check body did not finish, or its output was forged"
        elif result == "denied":
            row["why"] = "the runner's audit hook stopped an introspection or raw-memory route (see tail)"
        res.append(row)
    return res


# ---------------------------------------------------------------- model judges

PROMPT = """You are an acceptance judge for one code change in a RimWorld mod repository.
You see the task's acceptance criteria, the mechanical gate record, the results of hidden checks, and the change as
an anonymised diff. Decide whether the change meets the criteria. Be strict: accept only work that does what the
criteria ask, without placeholders, and without breaking what it touches. Judge the change, not its style.
{no_tools}

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
    return PROMPT.format(no_tools=JH.PROMPT_NO_TOOLS, labels=", ".join(labels), labels_json=json.dumps(list(labels)), criteria=criteria.strip(),
                         gate=g, hidden=h, diff=diff)


def parse_answer(text: str, labels: tuple) -> dict:
    """Exactly ONE JSON verdict object (fix round 3, GPT round 2 #12: the round-2 parser took the LAST one, so a
    rejection followed by a quoted acceptance example became `accept`). Each decoded verdict object's span is skipped
    (its nested braces are not re-read); a second DISTINCT verdict object, or none, is invalid, never accept. An
    identical repeat is the same answer and is tolerated."""
    dec = json.JSONDecoder()
    text = text or ""
    found, seen, i = None, set(), 0
    while True:
        i = text.find("{", i)
        if i < 0:
            break
        try:
            obj, end = dec.raw_decode(text, i)
        except ValueError:
            i += 1
            continue
        if isinstance(obj, dict) and "verdict" in obj:
            seen.add(json.dumps(obj, sort_keys=True, default=str))
            found = obj
            i = end
        else:
            i += 1
    if not found:
        return {"verdict": "invalid", "why": "no JSON verdict in the answer", "arm_guess": "unknown"}
    if len(seen) > 1:
        return {"verdict": "invalid", "why": "more than one verdict object in the answer (%d)" % len(seen),
                "arm_guess": "unknown"}
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
                      "--no-session-persistence", "--output-format", "text"]
        r = run_sandboxed(argv, work=work, priv=self.priv, stdin=prompt.encode("utf-8"), timeout=self.timeout,
                          rw=self.rw(work))
        if r.returncode:
            raise JudgeError("opus judge exit %d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[-300:]))
        return r.stdout.decode("utf-8", "replace")


class JudgeTripwire(JudgeError):
    """The GPT judge's transcript shows it reached outside its own job folder (or the web, or a tool we cannot vet),
    or its home kept per-call state: the vote is not a vote. `.meta` is the tool record for the vote."""

    def __init__(self, msg: str, meta: dict):
        super().__init__(msg)
        self.meta = meta


class JudgeAnswer(str):
    """A judge's answer text carrying `.meta` (the GPT judge's tool record) into its vote."""
    meta: dict | None = None


class GptConsult:
    """gpt_consult.py, a fresh codex run, from the judge work dir, inside the judge sandbox -- HARDENED, with no
    bypass (ARENA_GPTJUDGE_HARDEN_ISOLATED_CODEX_HOME, see judge_codex_home.py): codex.exe is a Windows process the
    bubblewrap sandbox does not confine, so it runs in the judge's OWN Codex home (verified before every call), with
    every tool feature and web search off (--lockdown), and its --json transcript (--events) goes through the
    tripwire: a web call, a tool item we cannot vet, or a command naming any path outside its job folder makes the
    vote INVALID. The home's per-call state is wiped after the call (JH.CallSession)."""

    def __init__(self, prefix: list[str] | None = None, priv: Path | None = None, timeout: int = MODEL_TIMEOUT):
        self.prefix, self.priv, self.timeout = prefix, priv, timeout

    def preflight(self) -> None:
        """The judge home must already be set up (one-time `judge_codex_home.py setup`); never seeded mid-run."""
        self._home()

    @staticmethod
    def _home() -> tuple[Path, Path]:
        try:
            home, base = JH.judge_home(), JH.base_home()
            JH.verify_home(home, base)
            ci = JH.codex_image()
            win = ci.windows_home()
            Path(ci.CODEX_SCRATCH).mkdir(parents=True, exist_ok=True)
            JH.verify_cwd(ci.CODEX_SCRATCH, user_home=win)       # gpt_consult's job dirs live under CODEX_SCRATCH
        except (JH.HomeError, OSError) as ex:
            raise JudgeUnavailable("gpt judge home: %s" % ex) from ex
        return home, base

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
        # `work` is this judge's OWN fresh private workspace (judge() makes one per call and deletes it after): the
        # prompt file is a copy of the neutralised prompt; gpt_consult hands codex.exe the TEXT on stdin from its own
        # job dir, so no tree or workspace path reaches the Windows process
        home, base = self._home()
        pf = work / "prompt.md"
        out = work / "answer.md"
        events = work / "events.jsonl"
        pf.write_text(prompt, encoding="utf-8")
        exe = self.prefix or [sys.executable, str(UTILS / "gpt_consult.py")]
        # the call log lives under the (masked) arena root: meter into the work dir, the harness appends it after
        local_log = work / "calls.jsonl"
        env = {"RM_GPT_CALL_LOG": str(local_log)}
        real_log = Path(os.environ.get("RM_GPT_CALL_LOG") or "/mnt/d/ClaudeWork/rimmandrake/arena/gpt_calls.jsonl")
        with JH.CallSession(home, base) as sess:
            try:
                r = run_sandboxed(exe + ["--prompt-file", str(pf), "--out", str(out), "--timeout", str(self.timeout),
                                         "--codex-home", str(home), "--lockdown", "--events", str(events)],
                                  work=work, priv=self.priv, timeout=self.timeout + 60, env=env,
                                  rw=[work] + self._scratch_paths())
            finally:
                try:
                    pre_wipe = JH.home_violations(home)              # before the last-out wipe can erase a plant
                except Exception as ex:                              # noqa: BLE001 -- fail closed, still leave
                    pre_wipe = ["home scan failed (%s)" % ex.__class__.__name__]
                finally:
                    post = sess.after()
        if local_log.is_file():
            try:
                real_log.parent.mkdir(parents=True, exist_ok=True)
                with open(real_log, "a", encoding="utf-8") as f:
                    f.write(local_log.read_text(encoding="utf-8"))
            except OSError:
                pass
        try:
            meta = json.loads(Path(str(events) + ".meta.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            meta = {}
        try:
            etext = events.read_text(encoding="utf-8", errors="replace")
        except OSError:
            etext = None
        trip = JH.tripwire(etext, meta.get("job_win") if isinstance(meta, dict) else None)
        info = {"n_tools": trip["n_tools"], "web": trip["web"], "commands": [c[:200] for c in trip["commands"][:3]],
                "refused_tool_calls": meta.get("refused_tool_calls") if isinstance(meta, dict) else None,
                "tripwire": trip["why"][:5], "wiped": post["wiped"], "leftover": post["leftover"]}
        failed = r.returncode or not out.is_file()
        # a failed call with no tool use is a failed call (JudgeError); tool use, or a bad transcript on a call that
        # answered, is a tripwire. Both are invalid votes.
        if not trip["valid"] and (trip["n_tools"] or trip["web"] or not failed):
            raise JudgeTripwire("gpt judge tripwire: %s" % "; ".join(trip["why"][:3]), info)
        if post["leftover"]:
            raise JudgeTripwire("gpt judge home kept per-call state after the wipe: %s" % post["leftover"], info)
        # the allow-list again AFTER the call: an entry planted between the pre-call check and codex's start shows here
        info["home_after"] = sorted(set(pre_wipe) | set(JH.home_violations(home)))
        if info["home_after"]:
            raise JudgeTripwire("gpt judge home off its allow-list after the call: %s" % info["home_after"][:5], info)
        if failed:
            raise JudgeError("gpt judge exit %d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[-300:]))
        ans = JudgeAnswer(out.read_text(encoding="utf-8"))
        ans.meta = info
        return ans


@dataclass
class Judges:
    opus: ModelCall
    gpt: ModelCall
    tie: ModelCall

    @classmethod
    def real(cls, priv: Path | None = None) -> "Judges":
        return cls(opus=OpusCLI(priv=priv), gpt=GptConsult(priv=priv), tie=OpusCLI(priv=priv))


def judge_workspace() -> Path:
    """A FRESH private workspace for ONE model call (fix round 2, GPT review #5): <work root>/.jw/<random>, mode 0700,
    empty. It is the call's cwd and its only writable judge dir; the submission's own dir (diff, prompt, verdict) and
    every sibling are under the masked work root, so judges share no directory and none can leave the next a note.
    The name is random, so it says nothing about the submission."""
    d = work_root() / ".jw" / secrets.token_hex(8)
    d.mkdir(parents=True, mode=0o700)
    os.chmod(d, 0o700)
    return d


def remove_raw_tree(work: Path) -> None:
    for d in [work / "tree"] + sorted(work.glob("check_*")):
        shutil.rmtree(d, ignore_errors=True)


def is_replay(task: dict) -> bool:
    """A replay task (arena_tasks census): it carries a source item / an RP_ id, and always has a judge file."""
    return bool(task.get("source_item")) or str(task.get("id", "")).startswith("RP_")


def _ask(name: str, call: ModelCall, prompt: str, labels: tuple) -> dict:
    ws = judge_workspace()
    try:
        text = call(prompt, ws)
    except JudgeTripwire as ex:                              # the judge reached outside: not a vote (fail closed)
        return {"judge": name, "verdict": "invalid", "why": str(ex)[:300], "arm_guess": "unknown", "tools": ex.meta}
    except Exception as ex:                                  # a failed call is invalid, never accept
        return {"judge": name, "verdict": "invalid", "why": str(ex)[:300], "arm_guess": "unknown"}
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    out = parse_answer(text, labels)
    out["judge"] = name
    if getattr(text, "meta", None) is not None:
        out["tools"] = text.meta
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
          work_base: Path | None = None, extra_tokens=(), tree_paths=TREE_PATHS,
          record: Callable[[dict], object] | None = None) -> dict:
    """Harness side. Returns the blind verdict record (no arm in it); the arm goes only to the arm map.
    `record(rec)`, if given, is called with every final verdict right after verdict.json is written (main() passes
    record_judge_event: the signed `judge` event arena_analysis.py reads). If it raises, the error propagates."""
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
        if record is not None:
            record(rec)
        return rec

    gstat = str((gate or {}).get("verdict", "")).lower()
    if gstat != "pass":
        return done("reject" if gstat == "fail" else "invalid", "gate verdict %r" % (gstat or None))
    if hidden is None and is_replay(task):
        # fix round 2 (GPT review #8): a replay task's hidden checks are part of its definition; a missing judge file
        # fails CLOSED (the known-bad output it exists to catch would otherwise reach the models)
        return done("invalid", "replay task %s has no hidden-check file: refusing to judge without it" % task["id"])
    try:
        runnable = [c for c in hidden_checks(hidden or {}) if c.get("body") is not None]
    except (AttributeError, KeyError, TypeError) as ex:
        return done("invalid", "hidden-check file is malformed: %s" % ex)
    if is_replay(task) and not runnable:
        # fix round 3 (GPT round 2 #4): fail closed before any work when nothing in the judge file can run
        return done("invalid", "replay task %s: its hidden-check file holds no runnable check (no stored body)"
                    % task["id"])
    allow = glued_allowlist(p)
    try:
        nd = neutralise(clone, base, head, task.get("area") or [], extra_tokens=extra_tokens, allow=allow)
    except JudgeError as ex:                         # a leak, or git could not produce a complete diff
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
        try:
            tree = materialise(clone, head, task.get("area") or [], work / "tree", tree_paths)
            rec["hidden"] = run_hidden(checks, tree, work, priv=priv)
        finally:
            # fix round 2 (GPT review #1/#4): the raw head tree and the per-check copies are gone BEFORE any model
            # is asked, so no judge (codex.exe included, which the Linux sandbox does not confine) can read them
            remove_raw_tree(work)
        if any(h["result"] in UNFINISHED for h in rec["hidden"]):
            return done("invalid", "a hidden check could not finish: " +
                        ", ".join("%s (%s)" % (h["path"], h["result"]) for h in rec["hidden"]
                                  if h["result"] in UNFINISHED))
        if any(h["result"] == "fail" for h in rec["hidden"]):
            return done("reject", "hidden check failed: " +
                        ", ".join(h["path"] for h in rec["hidden"] if h["result"] == "fail"))
    if is_replay(task) and not any(h["result"] == "pass" for h in rec["hidden"]):
        # fix round 3 (GPT round 2 #4): a replay exists to catch a known-bad output; `{}`, an empty `checks` list, or
        # checks that are all UNMEASURED (no stored body) ran nothing, so the models would judge it unchecked
        return done("invalid", "replay task %s: no hidden check ran and passed (%s); refusing to judge without one"
                    % (task["id"], ", ".join(sorted({h["result"] for h in rec["hidden"]})) or "no runnable checks"))

    kw = {"clone": clone, "shas": (base, head), "extra_tokens": extra_tokens}
    gview = _gate_view(gate, **kw)
    prompt = build_prompt(task.get("criteria") or "", gview, rec["hidden"], nd.text, labels)
    # the criteria and hidden-check paths come from the frozen task, identical for every arm; the gate record and
    # the diff come from the arm, so those are what must be clean
    leaks = find_leaks(json.dumps(gview, sort_keys=True) + "\n" + nd.text, clone=clone, extra_tokens=extra_tokens,
                       shas=(base, head), allow=allow)
    if leaks:
        return done("invalid", "prompt leaks the arm: " + "; ".join(leaks[:3]))
    (work / "prompt.md").write_text(prompt, encoding="utf-8")
    js = judges or Judges.real(priv)
    for call in (js.opus, js.gpt, js.tie):
        try:
            getattr(call, "preflight", lambda: None)()
        except JudgeError as ex:
            return done("invalid", "judge unavailable before any call: %s" % ex)
    votes = [_ask("opus", js.opus, prompt, labels), _ask("gpt", js.gpt, prompt, labels)]
    if {v["verdict"] for v in votes} == {"accept", "reject"}:
        votes.append(_ask("opus_tiebreak", js.tie, prompt, labels))
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


def record_judge_event(writer, *, arm: str, base: str, head: str, rec: dict, pending: bool = False) -> dict:
    """Append the signed `judge` event to the arm's log through an open arena_eventlog.HarnessWriter: the record
    arena_analysis.py reads (task, verdict, ts, sha = the judged head). Deliberately NOT in it: votes, arm guesses,
    reasons and the judge_id (the log names the arm; joining judge ids to arms there would publish the private arm
    map). pending=True writes the START marker main() appends before judging (verdict 'invalid', detail.pending): if
    the verdict append then fails, the marker stays the task's last judge event and arena_analysis.py refuses the
    arm, instead of an earlier accept silently standing (GPT review r1 #6)."""
    detail = {"base": base, "pending": True} if pending else {"base": base}
    return writer.emit(arm, "judge", lane="judge", run_id="judge", task=rec["task"], sha=head,
                       verdict=rec["verdict"], detail=detail)


# ---------------------------------------------------------------- arm-guess report (harness side)

def binom_sf(k: int, n: int, q: float) -> float:
    """P(X >= k), X ~ Binomial(n, q), summed in LOG space (lgamma + log-sum-exp), so a large report cannot overflow
    math.comb * float powers (fix round 2, GPT review #11). Reference statistic only (see guess_report)."""
    if k <= 0 or not n:
        return 1.0
    if k > n:
        return 0.0
    if q <= 0.0:
        return 0.0
    if q >= 1.0:
        return 1.0
    lq, l1q, lgn = math.log(q), math.log1p(-q), math.lgamma(n + 1)
    terms = [lgn - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lq + (n - i) * l1q for i in range(k, n + 1)]
    mx = max(terms)
    return max(0.0, min(1.0, math.exp(mx) * sum(math.exp(t - mx) for t in terms)))


DECISION_NOTE = ("LEAKY is decided by a TWO-SIDED PERMUTATION test (p_value < alpha_per_test, Bonferroni over this "
                 "report's tests), NOT by the spec's naive binomial p<0.05 against 1/len(arms): that binomial assumes "
                 "every arm is equally likely on every submission (the day's arm mix is unequal) and, pooled, treats "
                 "the correlated votes on one submission as independent trials, so it calls a majority-guessing blind "
                 "judge leaky. binom_p is printed for reference only. Residual: the permutation null assumes "
                 "submissions are exchangeable (no task/replay-family/time structure), the DECISION statistic is "
                 "accuracy (a truth-dependent mapping that keeps accuracy at chance is not detected by it), and alpha "
                 "is per report, not across repeated daily reports. Fix round 3 (GPT round 2 #11): a SECONDARY "
                 "statistic, the mutual information of guess x truth (bits) with its own one-sided permutation p "
                 "(mi_p, same submission-level permutation), is printed per judge and pooled, and "
                 "`blinding_secondary` says LEAKY when any mi_p < alpha_per_test: it catches a one-to-one relabelling "
                 "at chance accuracy. It does not change `blinding` (the pre-registered decision), and with few "
                 "submissions per arm MI is biased upward, so it is evidence to investigate, not a verdict.")
MI_DRAWS = 1000          # permutations for the secondary mutual-information statistic
EXACT_MAX = 8            # n! permutations enumerated exactly up to this many submissions
MC_DRAWS = 20000


def _perm_p(pairs_by_sub: list[list[tuple]], seed: int = 0) -> tuple:
    """TWO-SIDED permutation test of 'the guesses depend on the arm' (fix round 2, GPT review #10: a judge that
    consistently names the WRONG arm knows the arm just as well as one that names the right one). `pairs_by_sub` is one list per submission of
    (guess, truth) -- one pair per judge vote on it. Under the null the guesses are independent of which arm made
    which submission, so the submission truths are PERMUTED (jointly for all votes on a submission) and the statistic
    (total correct) recomputed. This conditions on the day's real arm mix AND on each judge's own guess mix, so an
    uninformed judge that always names the majority arm scores exactly its null and is never LEAKY.
    p_high = P(stat >= obs), p_low = P(stat <= obs) under the null; p_value = min(1, 2 * min(p_high, p_low)).
    Returns (p_value, expected_correct_under_null, method, p_high, p_low)."""
    truths = [ps[0][1] for ps in pairs_by_sub]
    guesses = [[g for g, _ in ps] for ps in pairs_by_sub]
    n = len(truths)
    if not n:
        return 1.0, 0.0, "none", 1.0, 1.0

    def stat(ts):
        return sum(g == t for gs, t in zip(guesses, ts) for g in gs)

    obs = stat(truths)
    from collections import Counter
    tc = Counter(truths)
    expected = sum(tc[g] / n for gs in guesses for g in gs)
    if n <= EXACT_MAX:
        tot = ge = le = 0
        for perm in permutations(truths):
            tot += 1
            s_ = stat(perm)
            ge += s_ >= obs
            le += s_ <= obs
        hi, lo, how = ge / tot, le / tot, "exact"
    else:
        rng = random.Random(seed)
        ts, ge, le = list(truths), 0, 0
        for _ in range(MC_DRAWS):
            rng.shuffle(ts)
            s_ = stat(ts)
            ge += s_ >= obs
            le += s_ <= obs
        hi, lo, how = (ge + 1) / (MC_DRAWS + 1), (le + 1) / (MC_DRAWS + 1), "monte_carlo_%d" % MC_DRAWS
    return min(1.0, 2 * min(hi, lo)), expected, how, hi, lo


def _mi(pairs: list[tuple]) -> float:
    """Plug-in mutual information (bits) of the (guess, truth) pairs."""
    from collections import Counter
    n = len(pairs)
    if not n:
        return 0.0
    j, g, t = Counter(pairs), Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (g[a] * t[b])) for (a, b), c in j.items())


def _mi_perm(pairs_by_sub: list[list[tuple]], seed: int = 1) -> tuple:
    """(observed MI, one-sided permutation p = P(MI >= obs) under the null), permuting submission truths exactly as
    _perm_p does. High MI = the guess depends on the arm, whatever the mapping (round 3, #11)."""
    truths = [ps[0][1] for ps in pairs_by_sub]
    guesses = [[g for g, _ in ps] for ps in pairs_by_sub]
    if not truths:
        return 0.0, 1.0

    def stat(ts):
        return _mi([(g, t) for gs, t in zip(guesses, ts) for g in gs])

    obs, rng, ts, ge = stat(truths), random.Random(seed), list(truths), 0
    for _ in range(MI_DRAWS):
        rng.shuffle(ts)
        ge += stat(ts) >= obs - 1e-12
    return obs, (ge + 1) / (MI_DRAWS + 1)


def guess_report(records: list[dict], amap: dict, labels: tuple | None = None, alpha: float = 0.05) -> dict:
    """Per judge and pooled: did the arm guesses beat CHANCE, where chance is the day's own mix (a permutation test,
    _perm_p), not 1/len(labels). 'unknown' counts as a wrong guess (a judge cannot lower its rate by abstaining).
    Records with no map entry are skipped and counted. Multiplicity: per-judge tests plus the pooled one are judged
    at Bonferroni alpha/m. The pooled test keeps each submission's votes together (they are not independent).
    `binom_p` (vs 1/len(labels)) is reported for reference only; it is NOT the decision: see DECISION_NOTE."""
    labels = tuple(labels or arms())
    q = 1.0 / len(labels)
    per, subs, unmapped = {}, [], 0
    for r in records:
        jid = r.get("judge_id")                      # round 3 #5: a non-string id or judge never reaches a dict key
        truth = ((amap.get(jid) if isinstance(jid, str) else None) or {}).get("arm")
        if not isinstance(truth, str):
            unmapped += 1
            continue
        pairs = []
        for v in r.get("votes") or []:
            g = v.get("arm_guess")
            g = g if isinstance(g, str) and g in labels else "unknown"
            name = v.get("judge")
            per.setdefault(name if isinstance(name, str) and name else "?", []).append([(g, truth)])
            pairs.append((g, truth))
        if pairs:
            subs.append(pairs)
    m = len(per) + 1
    a_m = alpha / m
    rows = {}
    for name, ps in sorted(per.items()):
        n = len(ps)
        k = sum(g == t for (g, t), in ps)
        pv, ex, how, hi, lo = _perm_p(ps)
        mi, mp = _mi_perm(ps)
        rows[name] = {"correct": k, "guesses": n, "rate": k / n if n else None, "chance": ex / n if n else None,
                      "p_value": pv, "p_high": hi, "p_low": lo, "method": how, "binom_p": binom_sf(k, n, q),
                      "leaky": pv < a_m, "mi_bits": mi, "mi_p": mp}
    N = sum(len(ps) for ps in subs)
    K = sum(g == t for ps in subs for g, t in ps)
    pp, ex, how, hi, lo = _perm_p(subs)
    mi, mp = _mi_perm(subs)
    pooled = {"correct": K, "guesses": N, "rate": K / N if N else None, "chance": ex / N if N else None,
              "p_value": pp, "p_high": hi, "p_low": lo, "method": how, "binom_p": binom_sf(K, N, q),
              "leaky": pp < a_m, "mi_bits": mi, "mi_p": mp}
    return {"decision": DECISION_NOTE, "chance": pooled["chance"], "q_plugin": q, "alpha": alpha,
            "alpha_per_test": a_m, "tests": m,
            "arms": list(labels), "per_judge": rows, "pooled": pooled,
            "submissions": len(records) - unmapped, "unmapped": unmapped,
            "blinding": "UNMEASURED" if not N else ("LEAKY" if pooled["leaky"] or any(r["leaky"] for r in rows.values())
                                                    else "not shown leaky"),
            "blinding_secondary": "UNMEASURED" if not N else (
                "LEAKY (mutual information)" if min([pooled["mi_p"]] + [r["mi_p"] for r in rows.values()]) < a_m
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
            if not isinstance(r.get("judge_id"), str):
                raise ValueError("judge_id is not a string")      # round 3 #5: `"judge_id": []` crashed the report
            for v in r.get("votes") or []:
                if not isinstance(v, dict):
                    raise ValueError("vote is not an object")
                if any(v.get(k) is not None and not isinstance(v.get(k), str) for k in ("judge", "arm_guess")):
                    raise ValueError("vote judge/arm_guess is not a string")
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
        import arena_eventlog as L
        p = A.paths()
        # the signed writer is opened BEFORE any model call: a log the harness cannot sign stops the judging, rather
        # than spending judge tokens on a verdict arena_analysis.py would never see
        with L.harness_pass(p) as cap:
            w = L.HarnessWriter(p, cap=cap)
            record_judge_event(w, arm=a.arm, base=a.base, head=a.head, rec={"task": a.task, "verdict": "invalid"},
                               pending=True)
            rec = judge_task(a.task, clone=Path(a.clone), base=a.base, head=a.head, arm=a.arm, gate=gate, p=p,
                             record=lambda r: record_judge_event(w, arm=a.arm, base=a.base, head=a.head, rec=r))
        print(json.dumps({k: rec[k] for k in ("judge_id", "task", "verdict")}, sort_keys=True))
        return 0 if rec["verdict"] != "invalid" else 2
    print(write_report(a.day))
    return 0


if __name__ == "__main__":
    sys.exit(main())
