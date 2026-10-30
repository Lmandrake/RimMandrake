#!/usr/bin/env python3
r"""judge_codex_home.py — the blind GPT judge's OWN Codex home, its lockdown, and the tool-call tripwire.

Item ARENA_GPTJUDGE_HARDEN_ISOLATED_CODEX_HOME. The GPT judge is codex.exe, a WINDOWS process: the Linux bubblewrap
sandbox that confines every other judge-side process does not reach it. Measured (BENCH, judge-1): it shared
C:\Users\<u>\.codex (sessions, history) with the arms' own gpt_consult calls, and 17 of 59 judge runs used shell tools
(code-mode exec_command, one web__run). Three layers, each enforced in code here:

  1. ITS OWN HOME. <windows home>\.codex_arena_judge ($ARENA_JUDGE_CODEX_HOME overrides), set up ONCE by
         python3 src/RimMandrake/Utils/arena/judge_codex_home.py setup
     : the login is FILE-COPIED from the shared home (auth.json, never printed), the elevated-sandbox state is copied
     from the shared home (codex_image.ensure_home_sandbox: the sandbox users are machine-wide, so a home carrying the
     current state never re-runs the UAC-gated setup), and config.toml is OURS (CONFIG_TEMPLATE: no plugins, no MCP
     servers, no notify hook, web search off, every tool feature off) — never the shared home's. Setup never launches
     codex. Each call only VERIFIES the home (verify_home: file compares, no machine query) and refuses otherwise.
  2. LOCKDOWN per call (gpt_consult.py --codex-home H --lockdown --events F): --ephemeral (no session files),
     --disable for every tool feature (gpt_consult.LOCKDOWN_FEATURES), -c web_search="disabled", --ignore-rules, and the prompt
     line PROMPT_NO_TOOLS (arena_judge.PROMPT carries it). After each call wipe_call_state() deletes the per-call state
     (WIPE_NAMES: sessions, history, logs, snapshots, sqlite thread/log stores); config, auth and sandbox state stay.
  3. TRIPWIRE. codex runs with --json; its event stream is the transcript. tripwire() marks the vote INVALID (not a
     vote; fail closed) when the stream is missing/unreadable/incomplete, shows ANY web call, any tool item it cannot
     vet, or any command naming a path outside the judge's own job folder.

Auth lineage (ARTPIPE_WORKER_AUTH_STALENESS_1 in codex_image.py): ChatGPT refresh tokens are single-use and rotate, so
two homes holding one lineage race. sync_auth_in() copies the shared login into the judge home before a call when the
shared one is newer; sync_auth_back() copies a login the judge ROTATED during the call back to the shared home, but
only when the shared file is byte-identical to what it was before the call (compare-and-swap), atomically.

RESIDUAL (not closable from here): codex.exe still runs as the owner's Windows user; with its tools disabled it has
no way to read a file, but the disable is codex's own feature switch, so the tripwire stays as the detector of record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
_IMG = ROOT / "skills" / "generating-images" / "scripts"

HOME_DIRNAME = ".codex_arena_judge"
# copied from the shared home at setup (codex_image.HOME_SEED_FILES minus config.toml, which is ours)
SEED_FILES = ("auth.json", "models_cache.json", "version.json", "installation_id")
PROMPT_NO_TOOLS = ("Judge ONLY from the text of this message. Do not run any command or tool, do not read, list or "
                   "search any file or directory, and do not browse or search the web: everything you may use is "
                   "below. A judge that runs a command, reads a file or makes a web call is discarded.")
# per-call state a codex run can leave in its home (names in the shared home, read 2026-10-30); wiped after each call
WIPE_NAMES = ("sessions", "archived_sessions", "history.jsonl", "session_index.jsonl", "log", "shell_snapshots",
              "tmp", ".tmp", "generated_images", "rollout-migrations", "thread-writer-locks", "memories")
WIPE_PREFIXES = ("logs_", "state_", "thread_history_", "goals_", "queue_", "memories_")   # sqlite stores (+ -wal/-shm)
# codex install / machine sandbox state (cap_sid: the sandbox capability SID; skills/.system: codex's bundled skills)
KEEP_NAMES = ("auth.json", "config.toml", "models_cache.json", "version.json", "installation_id", ".sandbox",
              ".sandbox-bin", ".sandbox-secrets", ".sandbox_migration", "cap_sid", "skills")


def gpt_consult():
    if str(ROOT / "src" / "RimMandrake" / "Utils") not in sys.path:
        sys.path.insert(0, str(ROOT / "src" / "RimMandrake" / "Utils"))
    import gpt_consult as gc                                          # noqa: PLC0415
    return gc


def lockdown_features() -> tuple:
    """The canonical list lives in gpt_consult.py (its --lockdown passes the same --disable set per call)."""
    return gpt_consult().LOCKDOWN_FEATURES


def codex_image():
    if str(_IMG) not in sys.path:
        sys.path.insert(0, str(_IMG))
    import codex_image as ci                                         # noqa: PLC0415
    return ci


class HomeError(RuntimeError):
    """The judge home is not usable; the message says what to run."""


def base_home() -> Path:
    env = os.environ.get("ARENA_JUDGE_CODEX_BASE", "").strip()
    return Path(env) if env else codex_image().base_codex_home()


def judge_home() -> Path:
    env = os.environ.get("ARENA_JUDGE_CODEX_HOME", "").strip()
    if env:
        return Path(env)
    win = codex_image().windows_home()
    if win is None:
        raise HomeError("no Windows home with a .codex install: set ARENA_JUDGE_CODEX_HOME")
    return win / HOME_DIRNAME


def _windows_sandbox_mode(base: Path) -> str | None:
    """The shared home's [windows] sandbox value (must match, or codex re-runs the sandbox setup)."""
    try:
        text = (base / "config.toml").read_text(encoding="utf-8")
    except OSError:
        return None
    sect = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("["):
            sect = s
            continue
        m = re.match(r'sandbox\s*=\s*"([^"]+)"', s)
        if sect == "[windows]" and m:
            return m.group(1)
    return None


def config_template(base: Path) -> str:
    lines = ["# The arena GPT judge's own Codex config. Written by judge_codex_home.py setup; edits are refused.",
             'web_search = "disabled"', 'sandbox_mode = "read-only"', 'approval_policy = "never"', "",
             "[history]", 'persistence = "none"', ""]
    mode = _windows_sandbox_mode(base)
    if mode:
        lines += ["[windows]", 'sandbox = "%s"' % mode, ""]
    lines += ["[features]"] + ["%s = false" % f for f in lockdown_features()]
    return "\n".join(lines) + "\n"


def _sandbox_blob(root: Path) -> bytes | None:
    return codex_image().sandbox_state_blob(root)


def _runner_fp(root: Path) -> str | None:
    return codex_image().sandbox_bin_fingerprint(root)


def verify_home(home: Path | None = None, base: Path | None = None) -> None:
    """Per-call check, file compares only (never launches codex, never queries the machine). Raises HomeError."""
    home, base = home or judge_home(), base or base_home()
    fix = "run: python3 src/RimMandrake/Utils/arena/judge_codex_home.py setup"
    if not (home / "auth.json").is_file():
        raise HomeError("judge Codex home %s has no login; %s" % (home, fix))
    try:
        cfg = (home / "config.toml").read_text(encoding="utf-8")
    except OSError:
        cfg = None
    if cfg != config_template(base):
        raise HomeError("judge Codex home %s config.toml is not the judge template; %s" % (home, fix))
    if _sandbox_blob(base) is not None and (_sandbox_blob(home) != _sandbox_blob(base)
                                            or _runner_fp(home) != _runner_fp(base)):
        raise HomeError("judge Codex home %s sandbox state differs from %s (a launch could raise the UAC sandbox "
                        "setup); %s" % (home, base, fix))


def setup(home: Path | None = None, base: Path | None = None, *, machine_check: bool = True) -> str:
    """ONE-TIME (idempotent) setup. File copies only; never launches codex. machine_check=False skips the
    net.exe proof that the shared sandbox state is current (selftests)."""
    home, base = home or judge_home(), base or base_home()
    ci = codex_image()
    if ci.in_wsl() and not str(home).startswith("/mnt/") and "ARENA_JUDGE_CODEX_HOME" not in os.environ:
        raise HomeError("%s is not visible to Windows" % home)
    home.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in SEED_FILES:
        src = base / name
        if src.is_file() and not (home / name).is_file():
            shutil.copy2(src, home / name)
            copied.append(name)
    if not (home / "auth.json").is_file():
        raise HomeError("shared home %s has no auth.json: log codex in first" % base)
    tmpl = config_template(base)
    if not (home / "config.toml").is_file() or (home / "config.toml").read_text(encoding="utf-8") != tmpl:
        (home / "config.toml").write_text(tmpl, encoding="utf-8")
        copied.append("config.toml (template)")
    if _sandbox_blob(base) is not None:
        if machine_check:
            ok, why = ci.ensure_home_sandbox(home, base)
            if not ok:
                raise HomeError(why)
        elif _sandbox_blob(home) != _sandbox_blob(base) or _runner_fp(home) != _runner_fp(base):
            ci._copy_sandbox_state(base, home)                       # noqa: SLF001 -- same copy ensure_home_sandbox does
    verify_home(home, base)
    return "judge Codex home %s ready (%s)" % (home, ", ".join(copied) or "already set up")


# ---------------------------------------------------------------- auth lineage

def _sha(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return None


def _last_refresh(p: Path) -> datetime | None:
    try:
        raw = json.loads(p.read_text(encoding="utf-8")).get("last_refresh")
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def _atomic_copy(src: Path, dst: Path) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(dst.parent), prefix=".%s." % dst.name)
    os.close(fd)
    try:
        shutil.copyfile(src, tmp)
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sync_auth_in(home: Path, base: Path) -> str | None:
    """Before a call: take the shared login when it differs and is at least as fresh. Returns the shared file's hash
    as seen now (the compare-and-swap token for sync_auth_back)."""
    b, h = base / "auth.json", home / "auth.json"
    bs = _sha(b)
    if bs is not None and bs != _sha(h):
        lb, lh = _last_refresh(b), _last_refresh(h)
        if lh is None or (lb is not None and lb >= lh):
            _atomic_copy(b, h)
    return bs


def sync_auth_back(home: Path, base: Path, base_sha_before: str | None, home_sha_before: str | None) -> bool:
    """After a call: if the judge home's login CHANGED during the call (codex rotated the refresh token) and is newer,
    the shared home's copy is now a spent lineage; replace it, but only if nobody touched it meanwhile."""
    h, b = home / "auth.json", base / "auth.json"
    hs = _sha(h)
    if hs is None or hs == home_sha_before or base_sha_before is None or _sha(b) != base_sha_before:
        return False
    lh, lb = _last_refresh(h), _last_refresh(b)
    if lh is None or (lb is not None and lh <= lb):
        return False
    _atomic_copy(h, b)
    return True


# ---------------------------------------------------------------- per-call wipe

def _is_call_state(name: str) -> bool:
    """The ONE predicate both the wipe and the leftover check use (GPT review r1: they used to differ)."""
    return name not in KEEP_NAMES and (name in WIPE_NAMES or name.startswith(WIPE_PREFIXES))


def wipe_call_state(home: Path) -> list[str]:
    """Delete what a call can leave behind; keep config, login and sandbox state. Returns the names removed."""
    gone = []
    for p in sorted(home.iterdir()) if home.is_dir() else []:
        n = p.name
        if _is_call_state(n):
            try:
                shutil.rmtree(p) if p.is_dir() and not p.is_symlink() else p.unlink()
                gone.append(n)
            except OSError:
                pass
    return gone


def leftover_state(home: Path) -> list[str]:
    """Anything a wipe should have removed and did not (a locked file on Windows): the caller fails closed."""
    return sorted(p.name for p in home.iterdir() if _is_call_state(p.name)
                  and (not p.is_dir() or any(p.rglob("*")))) if home.is_dir() else []


# ---------------------------------------------------------------- tripwire

# Item types a judge transcript may hold. agent_message/reasoning are its own text; `error` items carry codex's
# own notices (with tools off: "Code Mode is unavailable because code-mode host is disabled") and do no I/O.
TEXT_ITEMS = ("agent_message", "reasoning", "error", "todo_list")
WEB_ITEMS = ("web_search", "web_fetch", "web_run", "browser")
# The shell codex wraps a command in (measured 2026-10-30): `"C:\WINDOWS\System32\WindowsPowerShell\v1.0\
# powershell.exe" -Command "..."`; the wrapper path itself is not a file the judge reads.
SHELL_PREFIX_RE = re.compile(r'^\s*"?[A-Za-z]:\\[^"]*\\(?:powershell|pwsh|cmd|bash|sh)(?:\.exe)?"?\s*'
                             r'(?:-NoProfile\s+|-NoLogo\s+|-NonInteractive\s+)*(?:-Command|-c|/c|/d\s+/c|/s\s+/c)?\s*',
                             re.I)
# A path or location outside the cwd, in any spelling a Windows or WSL shell accepts. Each match is then tested
# against the job folder; anything not inside it trips.
OUTSIDE_PATH_RES = (
    re.compile(r"(?<![\w])[A-Za-z]:(?:[\\/][^\s'\"`;|,)]*)?", re.I),         # C:\x, D:/x, bare C:
    re.compile(r"(?<![\w:.\\$-])\\\\[^\s'\"`;|]+"),          # UNC \\server\share, \\wsl.localhost (not a C:\\x separator)
    re.compile(r"(?<![\w.~-])/(?:mnt|home|root|etc|usr|proc|tmp|var|opt|srv|run|dev|sys|bin|boot|lib)\b[^\s'\"`;|]*"),
    re.compile(r"(?<![\w])~(?:[\\/][^\s'\"`;|]*)?"),                          # ~, ~/x
    re.compile(r"(?<![\w])\.\.(?:[\\/]|(?=[\s'\"`;|]|$))"),                  # .. (parent)
)
# Not a path, but a way to name one indirectly, run hidden code, or reach the network: unvettable -> trips.
UNVETTABLE_RE = re.compile(
    r"\$env:|\$\{env:|\$HOME\b|\$PROFILE\b|\$PSHOME\b|\$PSScriptRoot\b|%[A-Za-z_][\w()]*%|\$\(\s*pwd|"
    r"\b(?:Env|Variable|Function|Alias|Cert|WSMan|HK[A-Z]{1,3})\s*:|Registry::|FileSystem::|"
    r"\[\s*(?:System\.)?(?:Environment|IO\.\w+)\s*\]|GetFolderPath|"
    r"-Enc(?:odedCommand)?\b|FromBase64String|\biex\b|Invoke-Expression|"
    r"\b(?:wsl|wslpath|bash|curl|wget|iwr|irm|ssh|scp|net|nslookup|ping|Start-Process|Invoke-WebRequest|"
    r"Invoke-RestMethod|New-PSDrive|subst|mklink)\b|\bhttps?://|\bftp://",
    re.I)
# the top-level --json event types of codex-cli 0.164 (exec_events: thread/turn/item lifecycle + a stream error)
EVENT_TYPES = ("thread.started", "turn.started", "turn.completed", "turn.failed", "item.started", "item.updated",
               "item.completed", "error")
OUTPUT_DIR_RE = re.compile(r"Directory:\s+(\S[^\r\n]*)")


def _norm_win(p: str) -> str:
    """codex's --json shows a command with its backslashes doubled (`C:\\\\WINDOWS`, measured 2026-10-30): collapse runs."""
    return re.sub(r"\\+", r"\\", p.replace("/", "\\")).rstrip("\\").lower()


def _inside(path: str, job_win: str) -> bool:
    j = _norm_win(job_win)
    q = _norm_win(path.strip().strip("'\"`"))
    return bool(j) and (q == j or q.startswith(j + "\\"))


def command_violations(command: str, job_win: str) -> list[str]:
    """Why a command run by the judge is not confined to its own job folder ([] = it named nothing outside)."""
    body = SHELL_PREFIX_RE.sub("", command or "", count=1)
    why = []
    m = UNVETTABLE_RE.search(body)
    if m:
        why.append("unvettable/indirect location or network %r" % m.group(0))
    for rx in OUTSIDE_PATH_RES:
        for m in rx.finditer(body):
            if not _inside(m.group(0), job_win):
                why.append("outside path %r" % m.group(0)[:120])
    return why


def tripwire(events_text: str | None, job_win: str | None) -> dict:
    """Read a codex --json event stream (the judge's transcript). Returns {valid, why, n_tools, commands, web,
    items}. INVALID (fail closed) when: no stream / a line that is not a JSON event / an event type codex 0.164 does
    not emit / a turn.failed / a turn or tool item started and never completed / no turn.completed; any web item;
    ANY command_execution (the judge runs with every tool off, so a command means the lockdown failed; a regex cannot
    prove what shell code touched -- GPT review r1 -- so command_violations only explains WHERE it reached); any
    other non-text item (unknown tool = cannot vet); no job_win to compare."""
    res = {"valid": False, "why": [], "n_tools": 0, "commands": [], "web": 0, "items": {}}
    why = res["why"]
    if not job_win:
        why.append("no job folder recorded for the call")
    lines = [ln for ln in (events_text or "").splitlines() if ln.strip()]
    if not lines:
        why.append("no event stream (the transcript is missing)")
    completed, tools, web = False, set(), set()
    open_items, in_turn = set(), False
    for ln in lines:
        try:
            ev = json.loads(ln)
        except ValueError:
            why.append("event stream line is not JSON: %r" % ln[:80])
            continue
        if not isinstance(ev, dict):
            why.append("event is not an object")
            continue
        et = ev.get("type")
        if et not in EVENT_TYPES:
            why.append("event type %r is not one codex emits (cannot vet)" % str(et)[:40])
            continue
        if et == "turn.started":
            if in_turn:
                why.append("turn.started inside an unfinished turn (not a codex transcript)")
            in_turn = True
        elif et == "turn.completed":
            if not in_turn:
                why.append("turn.completed without an active turn (not a codex transcript)")
            in_turn, completed = False, True
        elif et in ("turn.failed", "error"):
            why.append("codex reported %s" % et)
        if not str(et).startswith("item."):
            continue
        it = ev.get("item") if isinstance(ev.get("item"), dict) else {}
        ity, iid = str(it.get("type")), str(it.get("id"))
        if et == "item.started":
            open_items.add(iid)
        elif et == "item.completed":
            open_items.discard(iid)
            res["items"][ity] = res["items"].get(ity, 0) + 1
        if ity in TEXT_ITEMS:
            continue
        tools.add(iid)
        if ity in WEB_ITEMS or ity.startswith("web") or ity.startswith("browser"):
            web.add(iid)
            why.append("web call (%s)" % ity)
        elif ity == "command_execution":
            cmd = str(it.get("command") or "")
            if cmd not in res["commands"]:
                res["commands"].append(cmd)
            why.append("command executed with tools off: %r" % cmd[:160])
            for w in command_violations(cmd, job_win or ""):
                why.append("command %r: %s" % (cmd[:160], w))
            for d in OUTPUT_DIR_RE.findall(str(it.get("aggregated_output") or "")):
                if not _inside(d, job_win or ""):
                    why.append("command output lists %r" % d[:120])
        else:
            why.append("tool item %r cannot be vetted" % ity)
    if lines and not completed:
        why.append("no turn.completed (incomplete transcript)")
    elif lines and in_turn:
        why.append("a turn started and never completed (incomplete transcript)")
    if open_items:
        why.append("%d item(s) started and never completed: %s" % (len(open_items), sorted(open_items)[:3]))
    res["n_tools"], res["web"] = len(tools), len(web)
    res["why"] = list(dict.fromkeys(why))
    res["valid"] = not res["why"]
    return res


# ---------------------------------------------------------------- one call's session on the shared judge home

LOCK_DIR = "/tmp/rm_arena_judge_codex"


def _lock_path(home: Path) -> Path:
    """ONE lock per physical home for every seat (GPT review r1): a fixed dir, not $TMPDIR / $XDG_RUNTIME_DIR, which
    differ per seat, and the home's realpath, so aliases of one home share a lock. ARENA_JUDGE_LOCK_DIR: tests only."""
    d = Path(os.environ.get("ARENA_JUDGE_LOCK_DIR") or LOCK_DIR)
    d.mkdir(parents=True, exist_ok=True)
    try:
        d.chmod(0o1777)
    except OSError:
        pass
    rp = os.path.realpath(home)
    if re.match(r"^/mnt/[A-Za-z](/|$)", rp):                         # a Windows drive (drvfs): case-insensitive
        rp = rp.lower()
    return d / (hashlib.sha256(rp.encode()).hexdigest()[:16] + ".lock")


class CallSession:
    """Brackets ONE judge call on the shared judge home, safe under concurrent calls (the calibration runs 10):
    every call holds a SHARED flock for its duration. The FIRST in (exclusive lock obtainable) syncs the login in and
    records the auth snapshot; the LAST out (exclusive lock obtainable after its own release) wipes the per-call
    state, checks nothing was left, and writes a rotated login back. `after()` returns
    {wiped, leftover, auth_back}; a non-empty leftover is the caller's cue to fail closed."""

    def __init__(self, home: Path, base: Path):
        import fcntl                                                  # noqa: PLC0415 -- POSIX only, like the judge
        self._fcntl, self.home, self.base = fcntl, home, base
        self.lock = _lock_path(home)
        self.snap = self.lock.with_suffix(".auth.json")
        self.fd = None

    def __enter__(self) -> "CallSession":
        f = self._fcntl
        self.fd = os.open(str(self.lock), os.O_RDWR | os.O_CREAT, 0o600)
        try:
            f.flock(self.fd, f.LOCK_EX | f.LOCK_NB)
            first = True
        except OSError:
            first = False
        if first:
            hsha = _sha(self.home / "auth.json")
            bsha = sync_auth_in(self.home, self.base)
            # The snapshot is the login state at the last reconciliation and ALWAYS exists once written, so an
            # entrant that never held the exclusive lock still finds one (GPT review r2). Kept as is unless the
            # shared login was just taken in: an unreconciled rotation (an entrant slipped in between the last
            # call's unlock and relock -- GPT review r1) must still be seen by this cohort's last out.
            if not self.snap.exists() or _sha(self.home / "auth.json") != hsha:
                self._write_snap(bsha)
        f.flock(self.fd, f.LOCK_SH)                                   # downgrade (or wait out a wiping last-out)
        return self

    def _write_snap(self, base_sha: str | None) -> None:
        tmp = self.snap.with_suffix(".tmp")
        tmp.write_text(json.dumps({"base": base_sha, "home": _sha(self.home / "auth.json")}))
        os.replace(tmp, self.snap)

    def after(self) -> dict:
        f, out = self._fcntl, {"wiped": [], "leftover": [], "auth_back": False, "last_out": False}
        f.flock(self.fd, f.LOCK_UN)
        try:
            f.flock(self.fd, f.LOCK_EX | f.LOCK_NB)
        except OSError:
            return out                                                # another call is in flight: it wipes
        out["last_out"] = True
        out["wiped"] = wipe_call_state(self.home)
        out["leftover"] = leftover_state(self.home)
        try:
            s = json.loads(self.snap.read_text())
            out["auth_back"] = sync_auth_back(self.home, self.base, s.get("base"), s.get("home"))
            self._write_snap(_sha(self.base / "auth.json"))           # reconciled: the new baseline
        except (OSError, ValueError, AttributeError):
            pass
        return out

    def __exit__(self, *exc) -> None:
        if self.fd is not None:
            os.close(self.fd)                                         # releases any lock
            self.fd = None



def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup", help="one-time: create/repair the judge's own Codex home (file copies; no codex launch)")
    sub.add_parser("verify", help="check the judge home without changing it")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "setup":
            print(setup())
        else:
            verify_home()
            print("judge Codex home %s ok" % judge_home())
    except HomeError as ex:
        print("REFUSED: %s" % ex, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
