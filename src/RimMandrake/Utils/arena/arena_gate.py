#!/usr/bin/env python3
r"""arena_gate.py - the ONE gate every arm passes; run by the harness, never self-reported.

ARENA_GATE_BUILD_UNMEASURED_NEVER_PASSES; design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.2 and §1.8,
testpilot_merged_2026-10-29.md §2.3. Usage:

    python3 src/RimMandrake/Utils/arena/arena_gate.py --task T --base <sha> --head <sha> --arm X [--repo DIR]
    python3 src/RimMandrake/Utils/arena/arena_gate.py --verify-record <gate.json> --arm X

A SEPARATE process, run from the judge's own checkout (the script refuses to run from inside an arm clone - the
default clone root is ALWAYS checked, and an `$ARENA_CLONES` override is refused unless `ARENA_GATE_TEST=1`), checks
out `head` (and `base`) into fresh clones under `<arena>/judge/gate_work/` and runs, in order:
  1 scope        every changed path inside the task's `area` (arm bookkeeping stripped first, not refused); a symlink or
                 a submodule gitlink in the diff FAILS; a NEW file shadowing a stdlib module name (`concurrent/futures.py`,
                 `json.py`), a `sitecustomize`/`usercustomize` or a `.pth` FAILS
  2 placeholders non-empty diff, where a docstring/comment/whitespace/mode-only change counts as empty; no TODO/FIXME
                 (any case)/XXX/NotImplemented, no stub function (pass / ... / raise NotImplementedError / bare
                 `return None`) in changed code; no deleted selftest, no selftest def dropped; a changed selftest
                 may not lose assertion/check sites, and may not add a constant `assert True` / `check(True, ...)`
  3 tests        the HARNESS-OWNED runner (source held in this file, never the checkout's run_selftests.py) runs each
                 selftest of the changed paths + every selftest the diff added, one `python3 -I` process each, and
                 counts what executed (sys.monitoring: assert statements, check*/expect*/verify*/assert*() calls,
                 t_*/test_*() calls, distinct lines of the selftest). PASS comes only from the runner's positive
                 record (nonce-bound, written to a pipe the parent holds), never from exit code or printed text: an
                 `os._exit(0)` leaves no record -> UNMEASURED; an exception swallowed by a custom excepthook is caught
                 by the runner -> FAIL. A selftest the diff changed is run at base too: its check count may not drop
                 and its executed lines may not fall below 80% of base (FAIL). A new selftest executing no
                 recognisable check is UNMEASURED. Printed text can only downgrade (the UNMEASURED phrase).
  4 xml          validate_patch.py --live <dump> --defs <Data, workshop, Mods> on changed Defs/Patches; PASS needs the
                 positive `OK - 0 errors` marker (exit 0 with no marker is UNMEASURED)
  5 csharp       winbuild.py <mod> for each mod with a changed .cs
  6 deploy_plan  deploy_custom_mods.py --mod <m> (plan only) for each DEPLOYABLE mod changed (one with
                 `src/RimMandrake/<m>/About/About.xml`); a diff touching no deployable mod (Utils, rimflow, tooling)
                 is NA by design, not UNMEASURED. A plan naming a mod outside the area, or BLOCKING, fails
  7 proof        the task's own `proof` (each `python3 ...` segment; prose segments such as the held-back note are
                 the judge's business and are skipped). A segment must run a file that exists (missing -> UNMEASURED)
                 and that is in the diff, is a selftest, is a held-back check, or imports a changed module; `-c`
                 code or a script touching nothing of the diff is UNMEASURED. No runnable segment -> UNMEASURED
  8 live         live tasks only: records in the arm's SIGNED event log: canary (sha == head by a >=12-char prefix,
                 verdict pass, detail modcheck true) and live_release (verdict). A failed canary or another sha: INVALID
  9 test_record  a `test_start` for this sha from an agent id other than EVERY builder of the task (all build_end
                 records), compared after NFKC + casefold + stripping format (Cf) characters and whitespace; a non-
                 ASCII tester id or one confusable with a builder (skeleton collision: Cyrillic/Greek lookalikes,
                 0/o, 1/l, rn/m) is refused; then a test_end verdict by that tester. No test_start refuses (FAIL)

SANDBOX: every step that runs code from the checkout (tests, xml, csharp, deploy_plan, proof) runs under bubblewrap:
`--ro-bind / /`, a fresh /tmp, tmpfs over the real HOME, the event-token and anchor directories
(~/.local/state/rimmandrake/arena_harness, $ARENA_EVENT_TOKEN_FILE's dir), the private map dir
(~/.local/state/rm_arena_private, $ARENA_PRIVATE) and `<arena>/judge`; writable: the data root (bound before the
masks), the two clones and an empty HOME; pid namespace unshared; cwd the clean checkout; an allow-listed
environment only (PATH, locale, USER, WSL interop, WINBUILD_DOTNET) plus RM_DATA_ROOT resolved by the parent. Before
the steps a probe inside the sandbox must fail to see the token file, else every sandboxed step is UNMEASURED. No
bwrap -> UNMEASURED (the gate never runs arm code beside the key). Signing happens only in THIS parent process,
after every step has finished.

Step results: PASS | FAIL | INVALID | UNMEASURED | NA (not applicable to this diff; NA is decided only from the diff
and the repo layout). A step that cannot run (missing tool, dump absent, timeout, unparsable output, no positive
record, instrument or a module it imports edited by this diff, no signed log, no token, no sandbox) is UNMEASURED.
UNMEASURED NEVER PASSES. Overall verdict is exactly one of pass | fail | invalid:
  fail    any step FAIL;  else invalid   any step INVALID or UNMEASURED (the run is re-queued, the arm is not blamed);
  else pass  (every step PASS or NA, and steps 1, 2 and 9 are PASS).
NOT SELF-REPORTABLE: the result is a signed `gate` event appended through arena_eventlog.HarnessWriter (HMAC token
outside every arm-readable root) whose detail carries the sha256 of the JSON record written under
`<arena>/judge/gate/`; `load_verified()` / `--verify-record` refuses a record whose hash no signed gate event holds.
An arm's edit of a gate instrument, of any module the instrument imports (AST closure, base and head), or of
`Utils/arena/` / `rimflow/` makes the step that would run that instrument UNMEASURED.
Output: one JSON record on stdout. Exit 0 only for `pass`.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import arena_tasks as A  # noqa: E402

PASS, FAIL, INVALID, UNMEASURED, NA = "PASS", "FAIL", "INVALID", "UNMEASURED", "NA"
VERDICTS = ("pass", "fail", "invalid")
STEPS = ("scope", "placeholders", "tests", "xml", "csharp", "deploy_plan", "proof", "live", "test_record")
MUST_PASS = ("scope", "placeholders", "test_record")
STEP_TIMEOUT = 480
DEFAULT_CLONES = "/home/mandrake/rm/arena"

ARM_BOOKKEEPING = ("*/AGENTS.md", "IMPLEMENTATION_PLAN.md", "fix_plan.md", "PLAN.md", "plan.md")
TOOLS = {                                   # relative to the clone; the arm may not have edited them
    "tests": "src/RimMandrake/Utils/run_selftests.py",
    "xml": "skills/rimworld-modding/scripts/validate_patch.py",
    "csharp": "src/RimMandrake/Utils/winbuild.py",
    "deploy_plan": "src/RimMandrake/Utils/deploy_custom_mods.py",
}
TOOL_SEARCH = ("src/RimMandrake/Utils", "skills/rimworld-modding/scripts", "src/RimMandrake")
HARNESS_PREFIXES = ("src/RimMandrake/Utils/arena/", "src/RimMandrake/rimflow/")
SPECIAL_TESTS = ("src/RimMandrake/Utils/rimplace/selftest.py", "skills/generating-rimworld-sprites/scripts/selftest.py")
SHADOW_NAMES = frozenset(sys.stdlib_module_names) | {"sitecustomize", "usercustomize"}
ENV_ALLOW = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "TERM", "USER", "LOGNAME", "TZ", "WSL_INTEROP", "WSL_DISTRO_NAME",
             "WSLENV", "WINBUILD_DOTNET")
GAME = "/mnt/c/Program Files (x86)/Steam/steamapps"
DEFS_ROOTS = (GAME + "/common/RimWorld/Data", GAME + "/workshop/content/294100", GAME + "/common/RimWorld/Mods")
DUMP_DEFAULT = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump"
UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"       # run_selftests.py's phrase: text can only downgrade
# built from parts so this file does not trip its own scan
PLACEHOLDER_RE = re.compile(r"\b(?i:TO" + r"DO|FIX" + r"ME)\b|\bXX" + r"X\b|Not" + r"Implemented")
TAMPER_RE = re.compile(r"excepthook|sys\.settrace|sys\.setprofile|sys\.monitoring|threading\.settrace|"
                       r"gc\.get_(?:objects|referrers|referents)|sys\._getframe|_current_frames|/proc/self/(?:fd|mem)|"
                       r"\bos\._exit\b|\bctypes\b")
TAMPER_RE = re.compile(TAMPER_RE.pattern + r"|\b(?:tb_frame|f_back|f_locals|f_globals|gi_frame|cr_frame|ag_frame|"
                       r"cell_contents|__closure__)\b")
CODE_EXT = (".py", ".cs", ".xml", ".sh", ".json", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".ps1", ".bat", ".cmd",
            ".c", ".h", ".cpp", ".java", ".rs", ".go", ".lua", ".csproj", ".props", ".targets")
# python-loadable compiled code: nothing in the diff can be reviewed, it can shadow any module and runs in-process
NATIVE_EXT = (".so", ".pyd", ".pyc", ".pyo", ".dylib")
BOOKKEEPING_EXT = (".md", ".jsonl", ".txt")    # a stripped bookkeeping path must be notes, never code (p3h)
DEF_RE = re.compile(r"^\s*(?:def|async def)\s+(\w+)")
CHECK_NAME = re.compile(r"(?:(?:check|expect|verify|assert)(?:_\w*)?|ok)$")
LINES_FLOOR = 0.8
SHA_MIN = 12


class GateError(Exception):
    pass


def step(status, why="", **extra):
    d = {"status": status, "why": why}
    d.update(extra)
    return d


def unmeasured(why, **extra):
    return step(UNMEASURED, why, **extra)


def NA_STEP(why):
    return step(NA, why)


# ---------------------------------------------------------------- agent ids

_CONFUSE = {  # lookalikes NFKC does not fold -> latin; applied after norm_id (lower case)
    "а": "a", "в": "b", "е": "e", "ё": "e", "к": "k", "м": "m", "н": "h", "о": "o", "р": "p", "с": "c", "т": "t",
    "у": "y", "х": "x", "ѕ": "s", "і": "i", "ї": "i", "ј": "j", "һ": "h", "ԁ": "d", "ԛ": "q", "ԝ": "w", "ɡ": "g",
    "α": "a", "β": "b", "ε": "e", "η": "n", "ι": "i", "κ": "k", "ν": "v", "ο": "o", "ρ": "p", "τ": "t", "υ": "u",
    "χ": "x", "ω": "w", "ϲ": "c", "ӏ": "l", "ı": "i", "ℓ": "l",
    "0": "o", "1": "l", "|": "l", "i": "l", "5": "s", "_": "-", ".": "-",
}


def norm_id(x) -> str | None:
    """An agent id for comparison: NFKC, drop format (Cf) characters such as zero-width space, casefold, NFKC again,
    collapse whitespace. None for anything that is not a usable id."""
    if not isinstance(x, str):
        return None
    s = unicodedata.normalize("NFKC", x)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Cf")
    s = unicodedata.normalize("NFKC", s.casefold())
    s = " ".join(s.split())
    return s or None


def skeleton(x) -> str | None:
    """norm_id with confusables folded: two ids with one skeleton are the same agent for the different-agent rule."""
    n = norm_id(x)
    if n is None:
        return None
    s = "".join(ch for ch in unicodedata.normalize("NFD", n) if unicodedata.category(ch) != "Mn")
    s = "".join(_CONFUSE.get(ch, ch) for ch in s)
    return s.replace("rn", "m").replace("vv", "w").replace(" ", "").replace("-", "")


# ---------------------------------------------------------------- process / git helpers

def run(argv, cwd, log: Path, timeout=STEP_TIMEOUT, env=None, stdin=None, pass_fds=()):
    """-> (rc or None when it could not run / timed out, text). Always writes the log."""
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, env=env,
                           errors="replace", input=stdin, pass_fds=tuple(pass_fds))
        text = "$ %s\n%s%s\n[rc=%s]\n" % (" ".join(shlex.quote(a) for a in argv), r.stdout, r.stderr, r.returncode)
        log.write_text(text, encoding="utf-8")
        return r.returncode, text
    except subprocess.TimeoutExpired:
        log.write_text("$ %s\n[TIMEOUT after %ss]\n" % (" ".join(argv), timeout), encoding="utf-8")
        return None, "timeout"
    except OSError as e:
        log.write_text("$ %s\n[cannot run: %s]\n" % (" ".join(argv), e), encoding="utf-8")
        return None, "cannot run: %s" % e


def git(repo: Path, *args, check=True) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=120, errors="replace")
    if check and r.returncode != 0:
        raise GateError("git %s: %s" % (" ".join(args), r.stderr.strip()[:200]))
    return r.stdout if r.returncode == 0 else ""


def is_bookkeeping(path: str) -> bool:
    """Arm notes stripped before every step. Only note-shaped files: code under a bookkeeping glob is NOT stripped
    (it is then an ordinary path, judged by scope and every other step)."""
    if not path.endswith(BOOKKEEPING_EXT):
        return False
    return A.is_bookkeeping(path) or any(fnmatch.fnmatch(path, g) for g in ARM_BOOKKEEPING)


_GLOB_CACHE: dict = {}


def glob_match(path: str, g: str) -> bool:
    """Path glob: `*` and `?` stay inside one path segment, `**` crosses directories (p3g: `dir/*` is dir's files)."""
    rx = _GLOB_CACHE.get(g)
    if rx is None:
        out, i = [], 0
        while i < len(g):
            if g.startswith("**", i):
                out.append(".*"); i += 2
            elif g[i] == "*":
                out.append("[^/]*"); i += 1
            elif g[i] == "?":
                out.append("[^/]"); i += 1
            else:
                out.append(re.escape(g[i])); i += 1
        rx = _GLOB_CACHE[g] = re.compile("".join(out) + r"\Z")
    return bool(rx.match(path))


def in_area(path: str, area) -> bool:
    return any(path == g or glob_match(path, g) for g in area)


def sha_match(rec_sha, head_full: str) -> bool:
    """A record names head when its sha is a hex prefix of head of at least SHA_MIN characters."""
    s = str(rec_sha or "").strip().lower()
    return len(s) >= SHA_MIN and bool(re.fullmatch(r"[0-9a-f]+", s)) and head_full.lower().startswith(s)


def shadow_name(path: str) -> str | None:
    """The stdlib / interpreter-hook name a path would shadow on sys.path, or None."""
    parts = path.split("/")
    if path.endswith(".pth"):
        return parts[-1]
    if not path.endswith((".py", ".pyw") + NATIVE_EXT):
        return None
    for c in parts[:-1] + [parts[-1].split(".")[0]]:       # socket.cpython-312-x86_64-linux-gnu.so -> socket
        if c in SHADOW_NAMES:
            return c
    return None


def _token_dirs(p: dict) -> list[Path]:
    home = Path.home()
    out = [home / ".local" / "state" / "rimmandrake" / "arena_harness", home / ".local" / "state" / "rm_arena_private"]
    for f in (lambda: L.token_path(p), lambda: L.anchor_path(p)):
        try:
            out.append(Path(f()).parent)
        except Exception:  # noqa: BLE001
            pass
    env = os.environ.get("ARENA_PRIVATE", "").strip()
    if env:
        out.append(Path(env))
    return out


def _data_root() -> str | None:
    try:
        import rmpaths
        return str(rmpaths.rm_data_root())
    except Exception:  # noqa: BLE001 - steps needing it then fail visibly, never silently pass
        return os.environ.get("RM_DATA_ROOT") or None


# ---------------------------------------------------------------- the harness-owned selftest runner
# Written to <work>/h/ (read-only inside the sandbox) and run as `python3 -I runner.py <fd> <selftest>`. It reads a
# nonce from stdin, puts the selftest's dir on sys.path exactly as `python3 selftest.py` would, runs it with runpy
# under sys.monitoring, and writes ONE fixed ASCII line to the pipe fd. The PARENT decides: pass needs that exact line
# (parse_record) AND exit status 0 (verdict_from); a timeout, a missing/extra/garbled line -> UNMEASURED.
# The candidate runs in this process, so nothing it can patch is used after it starts: no json (or any other module
# the runner shares with it); every primitive (os.write, os._exit, the monitoring calls, type, int ...) is bound to a
# local BEFORE runpy, and the record is built with %-formatting of exact ints/strs. What same-process code can still do
# is listed in RESIDUAL_FORGERY.
RUNNER_SRC = r"""
import ast, os, re, runpy, sys, traceback
def _main(_write=os.write, _close=os.close, _exit=os._exit, _run=runpy.run_path, _ptb=traceback.print_exception,
          _type=type, _int=int, _str=str, _BE=BaseException, _SE=SystemExit, _M=sys.monitoring,
          _get_tool=sys.monitoring.get_tool, _get_events=sys.monitoring.get_events,
          _set_events=sys.monitoring.set_events, _register=sys.monitoring.register_callback,
          _DISABLE=sys.monitoring.DISABLE, _LINE=sys.monitoring.events.LINE, _START=sys.monitoring.events.PY_START,
          _fullmatch=re.fullmatch):
    fd = int(sys.argv[1]); path = os.path.realpath(sys.argv[2]); os.set_inheritable(fd, False)
    nonce = sys.stdin.readline().strip()
    nul = os.open(os.devnull, os.O_RDONLY); os.dup2(nul, 0); os.close(nul)
    if not _fullmatch(r"[0-9a-f]{32}", nonce):
        _exit(3)
    cnt = [0, 0, 0, 0]                       # asserts, checks, tests, lines
    def out(status, tampered):
        line = "ARENAGATE2 %%s %%s %%d %%d %%d %%d %%d\n" %% (nonce, status, cnt[0], cnt[1], cnt[2], cnt[3], tampered)
        _write(fd, line.encode("ascii")); _close(fd)
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
        alines = {n.lineno for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Assert)}
    except (OSError, SyntaxError, ValueError):
        out("fail", 0); _exit(1)
    TOOL = 4; EV = _LINE | _START
    seen = set(); _add = seen.add
    chk = re.compile(%(check)r).match; tst = re.compile(r"(?:t|test)_\w+$").match
    def on_line(code, line):
        if code.co_filename != path:
            return _DISABLE
        if line in alines:
            cnt[0] += 1
        elif (code, line) not in seen:
            _add((code, line)); cnt[3] += 1
            return _DISABLE
    def on_start(code, off):
        n = code.co_name
        if chk(n):
            cnt[1] += 1
        elif code.co_filename == path and tst(n):
            cnt[2] += 1
        else:
            return _DISABLE
    _M.use_tool_id(TOOL, "arena_gate")
    _register(TOOL, _LINE, on_line); _register(TOOL, _START, on_start)
    sys.argv = [path]; sys.path.insert(0, os.path.dirname(path))
    ok, err = True, None
    _set_events(TOOL, EV)
    try:
        _run(path, run_name="__main__")
    except _BE as e:
        ok = False
        if _type(e) is _SE:
            c = e.code
            ok = c is None or c is False or (_type(c) is _int and c == 0)
        if not ok:
            err = e
    tampered = 0
    try:
        if _get_tool(TOOL) != "arena_gate" or _get_events(TOOL) != EV:
            tampered = 1
        _set_events(TOOL, 0)
        if _register(TOOL, _LINE, None) is not on_line or _register(TOOL, _START, None) is not on_start:
            tampered = 1
    except _BE:
        tampered = 1
    out("pass" if ok else "fail", tampered)
    if err is not None:                      # cosmetic only: the record is already written and closed
        try:
            _ptb(err)
        except _BE:
            pass
    try:
        sys.stdout.flush(); sys.stderr.flush()
    except _BE:
        pass
    _exit(0 if ok else 1)
_main()
""" % {"check": CHECK_NAME.pattern}
REC_RE = re.compile(rb"ARENAGATE2 ([0-9a-f]{32}) (pass|fail) (\d{1,9}) (\d{1,9}) (\d{1,9}) (\d{1,9}) ([01])\n")
RESIDUAL_FORGERY = ("the candidate shares the runner's interpreter: code that reaches the runner's frame or closure "
                    "(gc.get_referrers/get_objects, frame f_back/f_locals, closure cells, ctypes) can read the nonce "
                    "and fd, write a forged pass line and exit 0. TAMPER_RE refuses the obvious spellings; a "
                    "sufficiently obfuscated one is caught only by a separate-process tracer, which this gate does "
                    "not have.")


def parse_record(buf: bytes, nonce: str):
    """The one record line, or None. Anything else in the pipe (a second line, junk, a short write) -> None."""
    m = REC_RE.fullmatch(buf or b"")
    if not m or m.group(1).decode() != nonce:
        return None
    a, c, t, l = (int(m.group(i)) for i in (3, 4, 5, 6))
    return {"status": m.group(2).decode(), "asserts": a, "checks": c, "tests": t, "lines": l,
            "tampered": m.group(7) == b"1"}


def verdict_from(rc, rec) -> tuple[str, str]:
    """PASS only on exit 0 plus a pass record; FAIL when the test said so; everything else UNMEASURED."""
    if rc is None:
        return "UNMEASURED", "timed out (a record written before a hang is not a pass)"
    if rec is None:
        return "UNMEASURED", "no valid runner record (rc=%s)" % rc
    if rec["tampered"]:
        return "UNMEASURED", "measurement hooks were tampered with"
    if rec["status"] == "fail":
        return "FAIL", "the test failed (rc=%s)" % rc
    if rc != 0:
        return "FAIL", "record says pass but the runner exited %s" % rc
    return "PASS", ""


# ---------------------------------------------------------------- the gate

class Gate:
    def __init__(self, task: dict, base: str, head: str, arm: str, repo: Path, p: dict, workdir: Path | None = None,
                 dump: str | None = None, defs_roots=DEFS_ROOTS, writer=None, run_id: str | None = None,
                 lane: str = "gate", python: str | None = None):
        self.task, self.base, self.head, self.arm, self.repo, self.p = task, base, head, arm, Path(repo), p
        self.dump = dump if dump is not None else os.environ.get("ARENA_GATE_DUMP", DUMP_DEFAULT)
        self.defs_roots = tuple(defs_roots)
        self.writer, self.lane = writer, lane
        self.python = python or sys.executable
        self.stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.run_id = run_id or "gate-%s-%s" % (task.get("id"), self.stamp)
        tag = "%s_%s_%s_%s" % (arm, task.get("id"), head[:12], self.stamp)
        self.logdir = p["root"] / "judge" / "gate" / tag
        self.work = Path(workdir) if workdir else p["root"] / "judge" / "gate_work" / tag
        self.clone = self.work / "co"
        self.base_clone = self.work / "base"
        self.hdir = self.work / "h"          # runner source (read-only in the sandbox)
        self.fake_home = self.work / "home"  # empty HOME for every sandboxed step
        self.files: list[dict] = []          # {"path","status","old_mode","new_mode"} after stripping bookkeeping
        self.stripped: list[str] = []
        self.results: dict = {}
        self.sandbox_why = ""                # non-empty: no sandboxed step may run
        self.data_root = _data_root()

    # ------------------------------------------------------------ checkout and diff
    def checkout(self):
        for sha in (self.base, self.head):
            if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha or ""):
                raise GateError("not a sha: %r" % (sha,))
        if self.work.exists():
            shutil.rmtree(self.work)
        self.work.mkdir(parents=True)
        for d in (self.hdir, self.fake_home):
            d.mkdir()
        (self.hdir / "gate_runner.py").write_text(RUNNER_SRC, encoding="utf-8")
        for dest in (self.clone, self.base_clone):
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", str(self.repo), str(dest)],
                           capture_output=True, text=True, timeout=300, check=True)
        git(self.clone, "-c", "advice.detachedHead=false", "checkout", "--quiet", self.head)
        got = git(self.clone, "rev-parse", "HEAD").strip()
        if not got.startswith(self.head.lower()) and not self.head.lower().startswith(got[:len(self.head)]):
            raise GateError("checkout is %s, not head %s" % (got, self.head))
        self.head_full = got
        self.base_full = git(self.clone, "rev-parse", "--verify", self.base + "^{commit}").strip()
        git(self.base_clone, "-c", "advice.detachedHead=false", "checkout", "--quiet", self.base_full)
        out = git(self.clone, "diff", "--no-renames", "--raw", "--no-abbrev", self.base_full, self.head_full)
        for line in out.splitlines():
            meta, _, path = line.partition("\t")
            f = meta.lstrip(":").split()
            if len(f) < 5:
                continue
            rec = {"path": path, "status": f[4][:1], "old_mode": f[0], "new_mode": f[1]}
            if is_bookkeeping(path):
                self.stripped.append(path)
            else:
                self.files.append(rec)

    def paths(self, *statuses):
        return [f["path"] for f in self.files if not statuses or f["status"] in statuses]

    def alive(self):
        return [f["path"] for f in self.files if f["status"] != "D"]

    def _diff(self, path):
        return git(self.clone, "diff", "--no-renames", "-U0", self.base_full, self.head_full, "--", path, check=False)

    def added_lines(self, path):
        """-> {lineno: text} of lines added in head for `path`."""
        res, ln = {}, 0
        for l in self._diff(path).splitlines():
            m = re.match(r"@@ -\S+ \+(\d+)", l)
            if m:
                ln = int(m.group(1)); continue
            if l.startswith("+") and not l.startswith("+++"):
                res[ln] = l[1:]; ln += 1
        return res

    def removed_lines(self, path):
        return [l[1:] for l in self._diff(path).splitlines() if l.startswith("-") and not l.startswith("---")]

    def read(self, which, path):
        root = self.clone if which == "head" else self.base_clone
        try:
            return (root / path).read_bytes()
        except OSError:
            return None

    # ------------------------------------------------------------ instruments and what they import
    def import_closure(self, rel) -> set:
        """Repo paths a checkout instrument imports (AST, recursive), in head and in base."""
        out = set()
        for root in (self.clone, self.base_clone):
            todo, seen = [rel], set()
            while todo:
                f = todo.pop()
                if f in seen:
                    continue
                seen.add(f)
                try:
                    tree = ast.parse((root / f).read_text(encoding="utf-8", errors="replace"))
                except (OSError, SyntaxError, ValueError):
                    continue
                dirs = [os.path.dirname(f)] + list(TOOL_SEARCH)
                for n in ast.walk(tree):
                    names = []
                    if isinstance(n, ast.Import):
                        names = [a.name for a in n.names]
                    elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
                        names = [n.module] + ["%s.%s" % (n.module, a.name) for a in n.names]
                    for name in names:
                        parts = name.split(".")
                        for d in dirs:
                            for k in range(1, len(parts) + 1):
                                stem = "/".join([d] + parts[:k]) if d else "/".join(parts[:k])
                                for cand in (stem + ".py", stem + "/__init__.py"):
                                    if (root / cand).is_file():
                                        todo.append(cand)
            out |= seen
        return out

    def tool_tainted(self, key):
        """-> reason the diff makes this instrument unable to judge it, or ''."""
        changed = set(self.paths())
        if TOOLS[key] in changed:
            return "the diff edits the instrument %s: it cannot judge itself" % TOOLS[key]
        if key == "tests":
            return ""
        hit = sorted(changed & self.import_closure(TOOLS[key]))
        if hit:
            return "the diff edits %s, which the instrument %s imports" % (", ".join(hit[:5]), TOOLS[key])
        hp = sorted(c for c in changed if c.startswith(HARNESS_PREFIXES))
        if hp:
            return "the diff edits harness code %s" % ", ".join(hp[:5])
        return ""

    def tool_path(self, key):
        """The instrument as it is in the head checkout, which must be BYTE-IDENTICAL to the base checkout's copy
        (the tool and every repo file it imports) at the moment it runs. Real instruments find the repo from their
        own __file__, so they must run from head; the head checkout is read-only to every sandboxed step except the
        C# build, and this re-check catches anything that rewrote one anyway (a build target, a missed mount)."""
        tp = self.clone / TOOLS[key]
        why = self.tool_tainted(key)
        if why:
            return None, why
        if not tp.is_file():
            return None, "instrument %s is absent from the checkout" % TOOLS[key]
        for rel in sorted({TOOLS[key]} | self.import_closure(TOOLS[key])):
            if self.read("head", rel) != self.read("base", rel):
                return None, "instrument file %s differs from the base checkout at run time" % rel
        return tp, ""

    # ------------------------------------------------------------ sandbox
    def sandbox_argv(self, argv, cwd, head_rw=False, data_rw=True):
        """Both checkouts and the runner dir are read-only (the head checkout is writable only to the C# build,
        which writes obj/bin); HOME is a fresh tmpfs per step; the data root is read-only while tests run."""
        bw = shutil.which("bwrap")
        if not bw:
            return None
        out = [bw, "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--unshare-pid", "--unshare-ipc",
               "--die-with-parent", "--new-session"]
        if self.data_root and os.path.isdir(self.data_root):
            r = os.path.realpath(self.data_root)
            out += ["--bind" if data_rw else "--ro-bind", r, r]   # before the masks: the masks below win inside it
        hides = [Path("/tmp"), Path.home()] + _token_dirs(self.p) + [self.p["root"] / "judge"]
        done = []
        for h in hides:
            if not h.exists():
                continue
            r = os.path.realpath(h)
            if any(r == d or r.startswith(d.rstrip("/") + "/") for d in done):
                continue
            done.append(r)
            out += ["--tmpfs", r]
        r = os.path.realpath(self.clone)
        out += ["--bind" if head_rw else "--ro-bind", r, r]
        r = os.path.realpath(self.base_clone)
        out += ["--ro-bind", r, r, "--tmpfs", os.path.realpath(self.fake_home)]
        r = os.path.realpath(self.hdir)
        out += ["--ro-bind", r, r, "--chdir", os.path.realpath(cwd)]
        return out + ["--"] + list(argv)

    def env(self):
        e = {k: os.environ[k] for k in ENV_ALLOW if k in os.environ}
        e.update(HOME=str(self.fake_home), TMPDIR="/tmp", PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1",
                 RM_ARM="harness")
        if self.data_root:
            e["RM_DATA_ROOT"] = self.data_root
        return e

    def srun(self, argv, log, cwd=None, timeout=STEP_TIMEOUT, stdin=None, pass_fds=(), head_rw=False, data_rw=True):
        """Run checkout code sandboxed. -> (rc|None, text)."""
        if self.sandbox_why:
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text("[not run: %s]\n" % self.sandbox_why, encoding="utf-8")
            return None, self.sandbox_why
        full = self.sandbox_argv(argv, cwd or self.clone, head_rw=head_rw, data_rw=data_rw)
        if full is None:
            return None, "no sandbox (bwrap absent): arm code would run beside the signing key"
        return run(full, cwd or self.clone, log, timeout=timeout, env=self.env(), stdin=stdin, pass_fds=pass_fds)

    def sandbox_probe(self):
        """The instrument must be able to see: a process in the sandbox must NOT reach the token or anchors, nor
        inherit any ARENA_* variable. Sets sandbox_why on any doubt."""
        if not shutil.which("bwrap"):
            self.sandbox_why = "no sandbox (bwrap absent): arm code would run beside the signing key"
            return
        targets = [str(L.token_path(self.p)), str(L.anchor_path(self.p))] + [str(d) for d in _token_dirs(self.p)]
        code = ("import os,sys,json\nt=json.loads(sys.argv[1]);seen=[]\nfor x in t:\n"
                " try:\n  ok=os.path.isfile(x) or (os.path.isdir(x) and bool(os.listdir(x)))\n"
                " except OSError:\n  ok=False\n if ok: seen.append(x)\n"
                "print(json.dumps({'seen':seen,'env':[k for k in os.environ if k.startswith('ARENA')],"
                "'home':os.environ.get('HOME')}))")
        rc, text = self.srun([self.python, "-I", "-c", code, json.dumps(targets)], self.logdir / "sandbox_probe.log",
                             timeout=60)
        m = re.search(r"^\{.*\}$", text or "", re.M)
        if rc != 0 or not m:
            self.sandbox_why = "sandbox probe did not run (rc=%s): no step runs arm code unsandboxed" % rc
            return
        got = json.loads(m.group(0))
        if got["seen"] or got["env"] or got["home"] != str(self.fake_home):
            self.sandbox_why = "sandbox probe still sees %s: refusing to run arm code" % (got,)

    # ------------------------------------------------------------ steps
    def s_scope(self):
        area = self.task.get("area") or []
        if not area:
            return unmeasured("task has no area")
        bad = []
        for f in self.files:
            modes = {f["old_mode"], f["new_mode"]}
            if "160000" in modes:
                bad.append("%s: submodule gitlink" % f["path"])
            elif f["new_mode"] == "120000":
                bad.append("%s: symlink (code it reaches is outside review)" % f["path"])
            if f["status"] != "D" and f["path"].endswith(NATIVE_EXT):
                bad.append("%s: compiled/native python-loadable code (unreviewable, can shadow any module)" % f["path"])
            if f["status"] == "A" and shadow_name(f["path"]):
                bad.append("%s: new file shadows the module/hook %r" % (f["path"], shadow_name(f["path"])))
        out = [f["path"] for f in self.files if not in_area(f["path"], area)]
        if out or bad:
            return step(FAIL, "%d path(s) outside area, %d forbidden path(s)" % (len(out), len(bad)),
                        outside=out[:20], forbidden=bad[:20])
        return step(PASS, "%d path(s), all inside area; %d bookkeeping stripped" % (len(self.files), len(self.stripped)))

    def noop(self, f) -> bool:
        """True when the change is docstring/comment/whitespace/mode only (or an added file holding nothing)."""
        path = f["path"]
        if f["status"] == "D":
            return False
        new = self.read("head", path)
        old = self.read("base", path) if f["status"] != "A" else b""
        if new is None or old is None:
            return False
        if new == old:
            return True
        if path.endswith(".py"):
            try:
                return _ast_core(old) == _ast_core(new)
            except (SyntaxError, ValueError):
                return False
        if b"\0" in new or b"\0" in old:
            return False
        return _text_core(path, old) == _text_core(path, new)

    def s_placeholders(self):
        if not self.files:
            return step(FAIL, "empty diff (nothing outside bookkeeping)")
        if not self.alive():
            return step(FAIL, "the diff only deletes files")
        if all(self.noop(f) for f in self.files):
            return step(FAIL, "empty diff: every change is docstring/comment/whitespace/mode only")
        if not any(f["status"] == "D" for f in self.files) and all(
                b"\0" in (self.read("head", f["path"]) or b"\0") for f in self.files):
            return unmeasured("binary-only diff: nothing in it can be read for placeholders or stubs")
        bad = []
        for f in self.files:
            path, st = f["path"], f["status"]
            if A.is_selftest(path) and st == "D":
                bad.append("%s: selftest deleted" % path); continue
            if st == "D" or not path.endswith(CODE_EXT):
                continue
            added = self.added_lines(path)
            for ln, text in sorted(added.items()):
                if PLACEHOLDER_RE.search(text):
                    bad.append("%s:%d: %s" % (path, ln, text.strip()[:60]))
            if path.endswith(".py"):
                bad += self.stub_functions(path, added)
            if A.is_selftest(path):
                bad += self.neutered(path, added, st)
            if A.is_selftest(path) and st == "M":
                dropped = {m.group(1) for m in map(DEF_RE.match, self.removed_lines(path)) if m} - \
                    {m.group(1) for m in map(DEF_RE.match, added.values()) if m}
                bad += ["%s: selftest def %s dropped" % (path, d) for d in sorted(dropped)]
        if bad:
            return step(FAIL, "%d placeholder/empty/weakened-test finding(s)" % len(bad), findings=bad[:20])
        return step(PASS, "non-empty; no placeholder, stub or weakened test in %d file(s)" % len(self.alive()))

    def neutered(self, path, added, st):
        """Constant assertions added, or assertion/check sites lost, in a selftest."""
        out = []
        try:
            head = ast.parse((self.clone / path).read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError, ValueError):
            return out                                 # stub_functions already reports unparsable python
        for n in ast.walk(head):
            if getattr(n, "lineno", None) not in added:
                continue
            if isinstance(n, ast.Assert) and isinstance(n.test, ast.Constant) and n.test.value:
                out.append("%s:%d: constant assert" % (path, n.lineno))
            if isinstance(n, ast.Call) and _call_name(n) and CHECK_NAME.match(_call_name(n)) and n.args and \
                    isinstance(n.args[0], ast.Constant) and n.args[0].value is True:
                out.append("%s:%d: %s(True, ...) checks nothing" % (path, n.lineno, _call_name(n)))
        if st == "M":
            old = self.read("base", path)
            try:
                nb = _check_sites(ast.parse(old or b""))
            except (SyntaxError, ValueError):
                nb = 0
            nh = _check_sites(head)
            if nh < nb:
                out.append("%s: assertion/check sites dropped %d -> %d" % (path, nb, nh))
        return out

    def stub_functions(self, path, added):
        try:
            tree = ast.parse((self.clone / path).read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, ValueError, OSError):
            return ["%s: unparsable python" % path]
        out = []
        for n in ast.walk(tree):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not any(n.lineno <= ln <= (n.end_lineno or n.lineno) for ln in added):
                continue
            body = list(n.body)
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                body = body[1:]
            if all(_inert(b) for b in body):          # `pass; return None`, `...`, `raise NotImplementedError` ...
                out.append("%s:%d: stub function %s" % (path, n.lineno, n.name))
        return out

    def selftests_for(self):
        """-> (sorted selftest paths existing in head, deleted python no selftest maps to). Changed/added selftests
        + head siblings of every changed python file, DELETED ones included (a deletion is a code change)."""
        tests, orphans = {f for f in self.alive() if A.is_selftest(f)}, []
        for f in self.paths():
            if f.endswith(".py") and not A.is_selftest(f):
                d, stem, hit = (self.clone / f).parent, Path(f).stem, False
                for t in sorted(d.glob("selftest*.py")) if d.is_dir() else []:
                    try:
                        txt = t.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        continue
                    if stem in t.name or re.search(r"\b(import|from)\s+%s\b" % re.escape(stem), txt):
                        tests.add(str(t.relative_to(self.clone))); hit = True
                if not hit and f not in self.alive():
                    orphans.append(f)
        return sorted(tests), orphans

    def run_test(self, root: Path, rel: str, tag: str):
        """-> (record dict | None, text). The record is the runner's fixed line, parsed HERE (parse_record) with the
        nonce this process holds, plus "rc" and the parent's own "verdict" (verdict_from). None = no valid line."""
        rfd, wfd = os.pipe()
        nonce = secrets.token_hex(16)
        log = self.logdir / ("tests_%s_%s.log" % (tag, re.sub(r"[^\w.]+", "_", rel)))
        try:
            rc, text = self.srun([self.python, "-I", str(self.hdir / "gate_runner.py"), str(wfd), str(root / rel)],
                                 log, cwd=root, stdin=nonce + "\n", pass_fds=(wfd,), data_rw=False)
            os.close(wfd); wfd = None
            os.set_blocking(rfd, False)
            buf = b""
            while True:
                try:
                    chunk = os.read(rfd, 65536)
                except BlockingIOError:
                    break
                if not chunk:
                    break
                buf += chunk
                if len(buf) > 4096:
                    break
        finally:
            if wfd is not None:
                os.close(wfd)
            os.close(rfd)
        rec = parse_record(buf, nonce)
        if rec is None:
            return None, "rc=%s; %s" % (rc, text or "")
        rec["rc"] = rc
        rec["verdict"], rec["why"] = verdict_from(rc, rec)
        return rec, text

    def s_tests(self):
        changed_py = [f for f in self.alive() if f.endswith(".py")]
        tests, orphans = self.selftests_for()
        if not changed_py and not tests and not orphans:
            return step(NA, "no python changed")
        if not tests or orphans:
            return unmeasured("python changed (or was deleted) but no selftest maps to it",
                              changed=(orphans or changed_py)[:10])
        why = self.tool_tainted("tests")
        if why:
            return unmeasured(why)
        sh = sorted(f["path"] for f in self.files if f["status"] == "M" and shadow_name(f["path"]))
        if sh:
            return unmeasured("the diff edits interpreter-hook / stdlib-named file(s) %s: needs a human look" % sh)
        tamper = sorted({"%s:%d" % (f, ln) for f in changed_py for ln, t in self.added_lines(f).items()
                         if TAMPER_RE.search(t)})
        if tamper:
            return unmeasured("changed code can hijack the runner (excepthook/_exit/trace/frames/ctypes): %s"
                              % ", ".join(tamper[:8]))
        special = [t for t in tests if t in SPECIAL_TESTS]
        if special:
            return unmeasured("selftest(s) %s need run_selftests' special invocation" % special)
        changed_set = set(self.paths("M"))
        fails, unm, rows = [], [], {}
        for t in tests:
            rec, text = self.run_test(self.clone, t, "head")
            if rec is None:
                unm.append("%s: no positive record from the harness runner (%s)" % (t, (text or "")[-120:].strip()))
                continue
            row = {k: rec.get(k) for k in ("verdict", "rc", "status", "asserts", "checks", "tests", "lines", "why",
                                           "tampered")}
            rows[t] = row
            if rec["verdict"] == FAIL:
                fails.append("%s: %s" % (t, rec["why"]))
                continue
            if rec["verdict"] != PASS:
                unm.append("%s: %s" % (t, rec["why"]))
                continue
            if UNMEASURED_PHRASE in text:
                unm.append("%s: printed the unmeasured phrase" % t)
                continue
            n_head = rec["asserts"] + rec["checks"] + rec["tests"]
            if t in changed_set and (self.base_clone / t).is_file():
                brec, _ = self.run_test(self.base_clone, t, "base")
                if brec is None or brec["rc"] is None or brec["tampered"]:
                    unm.append("%s: base run gave no record, the check count cannot be compared" % t)
                    continue
                n_base = brec["asserts"] + brec["checks"] + brec["tests"]
                row["base"] = {k: brec.get(k) for k in ("status", "asserts", "checks", "tests", "lines")}
                if n_head < n_base:
                    fails.append("%s: executed checks dropped %d -> %d vs base" % (t, n_base, n_head)); continue
                if rec["lines"] < LINES_FLOOR * brec["lines"]:
                    fails.append("%s: executed lines dropped %d -> %d vs base" % (t, brec["lines"], rec["lines"]))
                    continue
            elif n_head == 0:
                unm.append("%s: executed no recognisable check (assert / check*() / t_*())" % t)
        if fails:
            return step(FAIL, "%d of %d selftest(s) fail or were weakened" % (len(fails), len(tests)),
                        findings=fails[:20], tests=tests, counts=rows)
        if unm:
            return unmeasured("%d of %d selftest(s) gave no positive result" % (len(unm), len(tests)),
                              findings=unm[:20], tests=tests, counts=rows)
        return step(PASS, "%d/%d selftests pass (harness runner, counted)" % (len(tests), len(tests)),
                    tests=tests, counts=rows)

    def s_xml(self):
        xml = [f for f in self.alive() if A.is_defxml(f)]
        gone = [f for f in self.paths("D") if A.is_defxml(f)]
        if gone:
            return unmeasured("Def/Patch xml deleted (%s): validate_patch checks files, not what a removal breaks"
                              % ", ".join(gone[:5]))
        if not xml:
            return NA_STEP("no Defs/Patches xml changed")
        tp, why = self.tool_path("xml")
        if tp is None:
            return unmeasured(why)
        if not Path(self.dump).is_dir():
            return unmeasured("--live dump %s is absent" % self.dump)
        argv = [self.python, str(tp), *xml, "--live", self.dump]
        for r in self.defs_roots:
            argv += ["--defs", r]
        rc, text = self.srun(argv, self.logdir / "xml.log")
        log = str(self.logdir / "xml.log")
        if rc is None:
            return unmeasured("validate_patch could not run: " + text, log=log)
        if rc == 1 or re.search(r"^FAIL - \d+ error", text, re.M):
            return step(FAIL, "validate_patch reported errors", log=log)
        if rc == 0 and "UNMEASURED" not in text and re.search(r"^OK - 0 errors", text, re.M):
            return step(PASS, "validate_patch --live --defs clean on %d file(s)" % len(xml), log=log)
        return unmeasured("validate_patch rc=%s%s" % (rc, " with UNMEASURED in its output" if "UNMEASURED" in text
                                                      else " without its positive `OK - 0 errors` marker"), log=log)

    def mods_changed(self, ext=None):
        return sorted({A._mod_of(f) for f in self.paths() if (ext is None or f.endswith(ext))} - {None})

    def deployable(self, mod) -> bool:
        return any((root / "src" / "RimMandrake" / mod / "About" / "About.xml").is_file()
                   for root in (self.clone, self.base_clone))

    def s_csharp(self):
        mods = self.mods_changed(".cs")
        if not [f for f in self.paths() if f.endswith(".cs")]:      # a deleted .cs is a C# change too
            return NA_STEP("no .cs changed")
        if not mods:
            return unmeasured(".cs changed outside src/RimMandrake/<mod>/")
        tp, why = self.tool_path("csharp")
        if tp is None:
            return unmeasured(why)
        res = {}
        for m in mods:
            log = self.logdir / ("csharp_%s.log" % m)
            rc, text = self.srun([self.python, str(tp), m], log, head_rw=True)
            if rc is None:
                return unmeasured("winbuild could not run for %s: %s" % (m, text), log=str(log))
            if rc != 0 and re.search(r"dotnet\.exe not found|no such csproj|no csproj under|WINBUILD_DOTNET", text):
                return unmeasured("winbuild cannot run: " + text.strip().splitlines()[-2][:120], log=str(log))
            if rc == 0 and UNMEASURED_PHRASE in text:
                return unmeasured("winbuild exited 0 but printed the unmeasured phrase for %s" % m, log=str(log))
            res[m] = rc
        bad = [m for m, rc in res.items() if rc != 0]
        if bad:
            return step(FAIL, "build failed: " + ", ".join(bad), log=str(self.logdir))
        return step(PASS, "built " + ", ".join(mods))

    def s_deploy_plan(self):
        touched = self.mods_changed()
        mods = [m for m in touched if self.deployable(m)]
        if not mods:
            return NA_STEP("no deployable mod changed (no src/RimMandrake/<m>/About/About.xml for %s): nothing to deploy"
                           % (", ".join(touched) or "any path"))
        tp, why = self.tool_path("deploy_plan")
        if tp is None:
            return unmeasured(why)
        allowed = {A._mod_of(g.replace("*", "x")) for g in (self.task.get("area") or [])} - {None}
        seen = set()
        for m in mods:
            log = self.logdir / ("deploy_%s.log" % m)
            rc, text = self.srun([self.python, str(tp), "--mod", m], log)
            if rc is None:
                return unmeasured("deploy plan could not run for %s: %s" % (m, text), log=str(log))
            heads = re.findall(r"^(\S+)\s{2,}mandrake\.\S+", text, re.M)
            if not heads:
                return unmeasured("deploy plan for %s printed no mod section" % m, log=str(log))
            seen |= set(heads)
            if rc != 0 or "BLOCKING" in text:
                return step(FAIL, "deploy plan for %s is blocked (rc=%s)" % (m, rc), log=str(log))
            if UNMEASURED_PHRASE in text:
                return unmeasured("deploy plan for %s printed the unmeasured phrase" % m, log=str(log))
        out = sorted(seen - allowed)
        if out:
            return step(FAIL, "plan touches mod(s) outside the task area: " + ", ".join(out))
        return step(PASS, "plan touches only " + ", ".join(sorted(seen)),
                    not_deployable=sorted(set(touched) - set(mods)))

    def proof_target(self, argv):
        """-> (repo-relative script path | None, why)."""
        i = 1
        while i < len(argv) and argv[i].startswith("-"):
            if argv[i] == "-c":
                return None, "proof runs inline `-c` code, not a file"
            if argv[i] == "-m":
                if i + 1 >= len(argv):
                    return None, "proof `-m` names no module"
                mod = argv[i + 1].replace(".", "/")
                for cand in [mod + ".py", mod + "/__main__.py"] + ["%s/%s.py" % (d, mod) for d in TOOL_SEARCH]:
                    if (self.clone / cand).is_file():
                        return cand, ""
                return None, "proof module %s is not in the checkout" % argv[i + 1]
            i += 1
        if i >= len(argv):
            return None, "proof runs no file"
        rel = os.path.normpath(argv[i])
        if rel.startswith("..") or os.path.isabs(rel) or not (self.clone / rel).is_file():
            return None, "proof script %s is missing from the checkout" % argv[i]
        return rel, ""

    def proof_touches(self, rel) -> bool:
        if rel in self.paths() or A.is_selftest(rel):
            return True
        hidden = json.dumps(self.task.get("hidden_checks") or "")
        if rel in hidden:
            return True
        try:
            txt = (self.clone / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False
        stems = {Path(f).stem for f in self.paths() if f.endswith(".py")}
        return any(re.search(r"\b(import|from)\s+%s\b" % re.escape(s), txt) for s in stems)

    def s_proof(self):
        proof = (self.task.get("proof") or "").strip()
        segs = [s.strip() for s in proof.split(" && ") if s.strip()]
        runnable = [s for s in segs if s.startswith("python3 ")]
        if not runnable:
            return unmeasured("task proof has no runnable `python3 ...` segment", proof=proof[:120])
        for i, s in enumerate(runnable):
            try:
                argv = shlex.split(s)
            except ValueError:
                return unmeasured("proof segment unparsable: " + s[:80])
            rel, why = self.proof_target(argv)
            if rel is None:
                return unmeasured(why, segment=s[:120])
            if not self.proof_touches(rel):
                return unmeasured("proof script %s exercises nothing of the diff (not changed, not a selftest, "
                                  "imports no changed module)" % rel)
            argv[0] = self.python
            log = self.logdir / ("proof_%d.log" % i)
            rc, text = self.srun(argv, log)
            if rc is None:
                return unmeasured("proof could not run: " + text, log=str(log))
            if rc != 0:
                return step(FAIL, "proof segment %d exited %s" % (i, rc), log=str(log))
            if UNMEASURED_PHRASE in text:
                return unmeasured("proof segment %d exited 0 but printed the unmeasured phrase" % i, log=str(log))
        return step(PASS, "%d proof segment(s) exit 0" % len(runnable),
                    skipped_prose=[s for s in segs if s not in runnable])

    # ------------------------------------------------------------ signed-log steps
    def accepted(self):
        try:
            return L.verify(self.p, self.arm)["accepted"], ""
        except Exception as e:  # noqa: BLE001 - no token / unreadable log: the record cannot be judged
            return None, "signed event log unreadable: %s" % e

    def s_live(self, recs, why):
        """Bound to ONE run: the latest passing head canary, and a live_release of the SAME (lane, run_id, build)
        signed no earlier than it. Any failed head canary in any run is INVALID unless a later passing canary's
        detail.supersedes names that run."""
        if self.task.get("live", "none") == "none":
            return NA_STEP("task is live: none")
        if recs is None:
            return unmeasured(why)
        mine = _ordered(r for r in recs if r.get("task") == self.task["id"])
        allcan = [r for r in mine if r["event"] == "canary"]
        if not allcan:
            return unmeasured("no signed canary record for this task")
        can = [r for r in allcan if sha_match(r.get("sha"), self.head_full)]
        if not can:
            c = allcan[-1]
            return step(INVALID, "canary record is for sha %s, not head (>=%d hex chars needed)" % (c.get("sha"), SHA_MIN))
        open_fail = _unsuperseded_failures(can, lambda r: r.get("verdict") == "pass")
        if open_fail:
            c = open_fail[0]
            return step(INVALID, "canary %s in run %s: the run is re-queued, not failed (no later signed re-run "
                        "supersedes it)" % (c.get("verdict"), c.get("run_id")), detail=c.get("detail") or {})
        passes = [r for r in can if r.get("verdict") == "pass" and _t(r) is not None]
        if not passes:
            return step(INVALID, "no passing head canary with a signed time")
        c = passes[-1]
        d = c.get("detail") or {}
        if d.get("modcheck") is not True:
            return step(INVALID, "no modcheck recorded with this deploy")
        rel = [r for r in mine if r["event"] == "live_release" and sha_match(r.get("sha"), self.head_full)
               and _same_run(r, c) and (r.get("detail") or {}).get("build") == d.get("build")
               and _t(r) is not None and _t(r) >= _t(c)]
        if not rel:
            return unmeasured("canary passed (run %s) but that run recorded no live verdict" % c.get("run_id"))
        v = rel[-1].get("verdict")
        if v == "pass":
            return step(PASS, "live verdict pass, canary and modcheck recorded for head in run %s" % c.get("run_id"))
        if v == "fail":
            return step(FAIL, "live verdict fail")
        return unmeasured("live verdict %r is neither pass nor fail" % v)

    def s_test_record(self, recs, why):
        if recs is None:
            return unmeasured(why)
        t = self.task["id"]
        mine = _ordered(r for r in recs if r.get("task") == t)
        head_builds = [r for r in mine if r["event"] == "build_end" and sha_match(r.get("sha"), self.head_full)
                       and norm_id((r.get("detail") or {}).get("builder"))]
        if not head_builds:
            return unmeasured("no signed build_end (with builder) for head: the tester cannot be compared")
        raw_builders = [(r.get("detail") or {}).get("builder") for r in mine if r["event"] == "build_end"]
        builders = {norm_id(b) for b in raw_builders} - {None}
        bskel = {skeleton(b) for b in raw_builders} - {None}
        starts = [r for r in mine if r["event"] == "test_start" and sha_match(r.get("sha"), self.head_full)]
        if not starts:
            return step(FAIL, "no test_start for this sha: no different-agent test record")
        testers, refused, ok_starts = set(), [], []
        for r in starts:
            raw = (r.get("detail") or {}).get("tester")
            n = norm_id(raw)
            if n is None:
                refused.append("%r: no tester id" % (raw,))
            elif not n.isascii():
                refused.append("%r: non-ASCII after normalisation (homoglyph risk)" % (raw,))
            elif n in builders:
                refused.append("%r: is a builder of this task" % (raw,))
            elif skeleton(raw) in bskel:
                refused.append("%r: confusable with a builder of this task" % (raw,))
            else:
                testers.add(n); ok_starts.append(r)
        if not testers:
            return step(FAIL, "no test_start by an agent other than the builder(s) %s" % sorted(builders),
                        refused=refused[:10])
        tid = lambda r: norm_id((r.get("detail") or {}).get("tester"))  # noqa: E731
        ends = [r for r in mine if r["event"] == "test_end" and sha_match(r.get("sha"), self.head_full)
                and tid(r) in testers]
        open_fail = _unsuperseded_failures(ends, lambda r: r.get("verdict") == "pass")
        if open_fail:
            return step(FAIL, "different-agent tester verdict %s in run %s (no later signed re-run supersedes it)"
                        % (open_fail[0].get("verdict"), open_fail[0].get("run_id")))
        timed = [r for r in ok_starts if _t(r) is not None]
        if not timed:
            return unmeasured("no test_start with a signed time")
        last = timed[-1]                         # the latest test of head decides; older runs cannot answer for it
        mine_ends = [r for r in ends if _same_run(r, last) and tid(r) == tid(last) and _t(r) is not None
                     and _t(r) >= _t(last)]
        if not mine_ends:
            return unmeasured("latest test_start (tester %s, run %s) has no test_end in that run yet"
                              % (tid(last), last.get("run_id")))
        e = mine_ends[-1]
        v = e.get("verdict")
        if v == "pass":
            return step(PASS, "tester %s (builders %s) verdict pass in run %s"
                        % ((e.get("detail") or {}).get("tester"), ", ".join(sorted(builders)), e.get("run_id")))
        if v == "fail":
            return step(FAIL, "different-agent tester verdict fail")
        return unmeasured("tester verdict %r" % v)

    # ------------------------------------------------------------ driver
    def execute(self) -> dict:
        self.logdir.mkdir(parents=True, exist_ok=True)
        try:
            self.checkout()
        except (GateError, subprocess.SubprocessError, OSError) as e:
            self.results = {s: unmeasured("no checkout: %s" % str(e)[:160]) for s in STEPS}
            return self.finish()
        self.sandbox_probe()
        fns = {"scope": self.s_scope, "placeholders": self.s_placeholders, "tests": self.s_tests, "xml": self.s_xml,
               "csharp": self.s_csharp, "deploy_plan": self.s_deploy_plan, "proof": self.s_proof}
        for s in STEPS:                           # every step that runs arm code finishes before any log is read
            if s not in fns:
                continue
            try:
                self.results[s] = fns[s]()
            except Exception as e:  # noqa: BLE001 - a step that crashed is UNMEASURED, never a pass
                self.results[s] = unmeasured("step crashed: %s: %s" % (type(e).__name__, str(e)[:160]))
        recs, why = self.accepted()               # parent process only, after the sandboxed steps
        for s, fn in (("live", lambda: self.s_live(recs, why)), ("test_record", lambda: self.s_test_record(recs, why))):
            try:
                self.results[s] = fn()
            except Exception as e:  # noqa: BLE001
                self.results[s] = unmeasured("step crashed: %s: %s" % (type(e).__name__, str(e)[:160]))
        return self.finish()

    def finish(self) -> dict:
        return finish(self.results, self.task.get("id"), self.arm, self.base, self.head, self.logdir, self)


def _t(r):
    """Signed event time (epoch) or None when the record's ts cannot be ordered."""
    try:
        return L.ts_epoch(r.get("ts"))
    except (ValueError, TypeError):
        return None


def _ordered(recs) -> list:
    """Records in signed-time order (log order breaks ties); unorderable ones first, so they are never 'latest'."""
    recs = list(recs)
    return [r for _, _, r in sorted(((_t(r) if _t(r) is not None else float("-inf")), i, r)
                                    for i, r in enumerate(recs))]


def _same_run(a, b) -> bool:
    return a.get("lane") == b.get("lane") and a.get("run_id") is not None and a.get("run_id") == b.get("run_id")


def _supersedes(r) -> set:
    s = (r.get("detail") or {}).get("supersedes")
    if isinstance(s, str):
        return {s}
    if isinstance(s, list):
        return {x for x in s if isinstance(x, str)}
    return set()


def _unsuperseded_failures(rs, is_pass) -> list:
    """Every non-pass record not named by the detail.supersedes of a passing record that comes AFTER it in signed
    order: signed ts first (second resolution), the hash-chained log position breaking ties. A pass signed with an
    earlier ts sorts before the failure and supersedes nothing; an unorderable ts supersedes nothing."""
    rs = _ordered(rs)
    out = []
    for i, f in enumerate(rs):
        if is_pass(f):
            continue
        tf = _t(f)
        if tf is None or not any(is_pass(p) and _t(p) is not None and f.get("run_id") in _supersedes(p)
                                 for p in rs[i + 1:]):
            out.append(f)
    return out


def _inert(b) -> bool:
    """A statement that does nothing a stub would not: pass, `...`/constant, bare return/return None,
    raise NotImplementedError."""
    if isinstance(b, ast.Pass):
        return True
    if isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant):
        return True
    if isinstance(b, ast.Return):
        return b.value is None or (isinstance(b.value, ast.Constant) and b.value.value is None)
    if isinstance(b, ast.Raise) and b.exc is not None:
        e = b.exc.func if isinstance(b.exc, ast.Call) else b.exc
        return isinstance(e, ast.Name) and e.id == "Not" + "ImplementedError"
    return False


def _strip_docstrings(tree):
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body and \
                isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant) and \
                isinstance(n.body[0].value.value, str):
            n.body = n.body[1:] or [ast.Pass()]
    return tree


def _ast_core(src: bytes) -> str:
    return ast.dump(_strip_docstrings(ast.parse(src)), annotate_fields=False)


def _text_core(path: str, b: bytes) -> str:
    t = b.decode("utf-8", "replace")
    if path.endswith((".xml", ".html", ".csproj", ".props")):
        t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    elif path.endswith((".cs", ".js", ".ts", ".java", ".c", ".h", ".cpp")):
        t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
        t = re.sub(r"//[^\n]*", "", t)
    elif path.endswith((".sh", ".toml", ".yaml", ".yml", ".cfg", ".ini")):
        t = re.sub(r"(?m)^\s*#[^\n]*", "", t)
    return "".join(t.split())


def _call_name(n):
    f = n.func
    return f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)


def _check_sites(tree) -> int:
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert) and not (isinstance(n.test, ast.Constant)
               and n.test.value)) + sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call) and _call_name(n)
                                        and CHECK_NAME.match(_call_name(n)))


def verdict_of(results: dict) -> str:
    """The whole rule in one place. Every step must be PASS or NA (MUST_PASS steps PASS); UNMEASURED, a missing
    step or ANY unknown status (None, "BROKEN" ...) can never produce `pass`."""
    st = {s: (results.get(s) or {}).get("status", UNMEASURED) for s in STEPS}
    if FAIL in st.values():
        return "fail"
    if any(v not in (PASS, NA) for v in st.values()):
        return "invalid"
    if any(st[s] != PASS for s in MUST_PASS):
        return "invalid"
    return "pass"


def finish(results, task_id, arm, base, head, logdir, gate=None) -> dict:
    v = verdict_of(results)
    rec = {"verdict": v, "passed": v == "pass", "task": task_id, "arm": arm, "base": base, "head": head,
           "ts": L.now_ts(), "steps": {s: results.get(s) or unmeasured("step missing") for s in STEPS},
           "unmeasured": [s for s in STEPS if (results.get(s) or {}).get("status", UNMEASURED) == UNMEASURED],
           "log_dir": str(logdir)}
    if gate is not None:
        rf = logdir / "gate.json"
        rec["record_file"] = str(rf)
        body = json.dumps(rec, indent=1, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(body).hexdigest()
        rec["recorded"] = False
        try:
            rf.write_bytes(body)
            detail = {"steps": {s: rec["steps"][s]["status"] for s in STEPS}, "log_dir": str(logdir),
                      "record_file": str(rf), "record_sha256": digest}
            if gate.writer is not None:            # selftests that plant a writer (wrong token etc.)
                gate.writer.emit(arm, "gate", lane=gate.lane, run_id=gate.run_id, task=task_id, sha=head, verdict=v,
                                 detail=detail)
            else:
                # the signing pass opens HERE, in the parent, after every sandboxed step has ended; it is closed
                # (capability file deleted) before this function returns
                with L.harness_pass(gate.p) as cap:
                    L.HarnessWriter(gate.p, cap=cap).emit(arm, "gate", lane=gate.lane, run_id=gate.run_id,
                                                          task=task_id, sha=head, verdict=v, detail=detail)
            rec["recorded"], rec["record_sha256"] = True, digest
        except Exception as e:  # noqa: BLE001 - not signable: an unsigned result is never a pass
            rec["record_error"] = str(e)[:200]
            if rec["verdict"] == "pass":
                rec.update(verdict="invalid", passed=False, unsigned_pass=True)
            try:
                rf.write_bytes(json.dumps(rec, indent=1, sort_keys=True).encode("utf-8"))
            except OSError:
                pass
        if gate.work.exists():
            shutil.rmtree(gate.work, ignore_errors=True)
    else:
        rec["recorded"] = False
    return rec


def load_verified(p: dict, arm: str, record_file) -> dict:
    """The gate record at `record_file`, only if a SIGNED gate event of `arm` carries its sha256. Else GateError."""
    rf = str(record_file)
    try:
        body = Path(rf).read_bytes()
    except OSError as e:
        raise GateError("gate record unreadable: %s" % e)
    digest = hashlib.sha256(body).hexdigest()
    events = [r for r in L.verify(p, arm)["accepted"] if r.get("event") == "gate"
              and (r.get("detail") or {}).get("record_file") == rf]
    if not events:
        raise GateError("no signed gate event names %s" % rf)
    if not any((r.get("detail") or {}).get("record_sha256") == digest for r in events):
        raise GateError("%s does not match the sha256 its signed gate event carries: edited after signing" % rf)
    rec = json.loads(body)
    ev = [r for r in events if (r.get("detail") or {}).get("record_sha256") == digest][-1]
    if ev.get("verdict") != rec.get("verdict"):
        raise GateError("record verdict %r differs from the signed verdict %r" % (rec.get("verdict"), ev.get("verdict")))
    return rec


def refuse_arm_location(file=__file__, env=None):
    env = os.environ if env is None else env
    roots = [Path(DEFAULT_CLONES)]
    ov = (env.get("ARENA_CLONES") or "").strip()
    if ov and os.path.realpath(ov) != os.path.realpath(DEFAULT_CLONES):
        if env.get("ARENA_GATE_TEST") != "1":
            raise GateError("ARENA_CLONES is overridden (%s) outside a gate selftest: the clone-root check cannot be "
                            "moved" % ov)
        roots.append(Path(ov))
    for clones in roots:
        if A._inside(Path(file), clones):
            raise GateError("the gate is running from inside an arm clone (%s): the judge runs it from its own "
                            "checkout" % clones)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--task")
    ap.add_argument("--base")
    ap.add_argument("--head")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--repo", default=None, help="repo holding head (default: the arm's clone under $ARENA_CLONES, "
                                                 "else this checkout)")
    ap.add_argument("--lane", default="gate")
    ap.add_argument("--verify-record", default=None, help="check a gate.json against its signed gate event")
    a = ap.parse_args(argv)
    try:
        refuse_arm_location()
    except GateError as e:
        print(json.dumps({"verdict": "invalid", "passed": False, "error": str(e)}))
        return 2
    p = A.paths()
    if a.verify_record:
        try:
            rec = load_verified(p, a.arm, a.verify_record)
        except (GateError, ValueError, L.Rejected) as e:
            print(json.dumps({"verified": False, "error": str(e)}))
            return 2
        print(json.dumps({"verified": True, "verdict": rec.get("verdict")}))
        return 0
    if not (a.task and a.base and a.head):
        ap.error("--task, --base and --head are required")
    clones = Path(os.environ.get("ARENA_CLONES", DEFAULT_CLONES))
    repo = Path(a.repo) if a.repo else (clones / a.arm if (clones / a.arm / ".git").exists() else A.REPO)
    try:
        task = A.load_frozen(a.task, p)
    except Exception as e:  # noqa: BLE001 - unfrozen/changed task: the gate cannot judge it
        rec = finish({s: unmeasured("task not loadable: %s" % str(e)[:160]) for s in STEPS}, a.task, a.arm, a.base,
                     a.head, p["root"] / "judge" / "gate" / "unloadable")
        print(json.dumps(rec, sort_keys=True))
        return 2
    rec = Gate(task, a.base, a.head, a.arm, repo, p, lane=a.lane).execute()
    print(json.dumps(rec, sort_keys=True))
    return 0 if rec["verdict"] == "pass" and rec.get("passed") is True and rec.get("recorded") is True else 1


if __name__ == "__main__":
    sys.exit(main())
