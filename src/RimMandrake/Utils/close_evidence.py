#!/usr/bin/env python3
"""close_evidence.py -- machine evidence per commit sha, so the Arbiter's no-AI gates can decide a close.

CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE (design/RimMandrake/rimflow_v3_arbiter_tiers_2026-10-27.md, "Missing gates"):
94% of closes recorded no machine evidence, although selftests, C# builds, patch validation and modcheck all ran.
Each of those tools now appends ONE line here when it finishes; a gate looks the sha up at claim time with no AI and
no re-run. Review Z (D:/ClaudeWork/rimmandrake/review_v3_Z/answer.md) hardened it to v2.

Where: one JSONL per UTC day, `<agent storage>/rimmandrake/evidence/YYYY-MM-DD.jsonl`. The root comes from
`python3 ~/dev/Lodestar/bin/lib/agent_storage.py rimmandrake` (never hard-wired); `RM_CLOSE_EVIDENCE_DIR` overrides it
(selftests). Append-only: a line is never rewritten. Appends hold an flock on `<day>.jsonl.lock`: on D: (drvfs)
O_APPEND alone is NOT atomic -- 24 concurrent writers kept 41 of 960 lines (review Z F1).

A line (v4): {v, ts, tool, clone, sha, dirty, dirty_n, dirty_paths, start, paths, covers, result, item, seat, who,
              origin, live_only, variant, detail, mac}
  * seat/who -- WHO ran it (whoami(): rimflow's seat order, the session id, the bridge session that commit trailers
              name, the agent); seat None when nothing names a valid rimflow seat.
  * sha/dirty -- HEAD and uncommitted state of the clone at the END of the run (dirty: tracked or untracked changes
              outside DIRTY_IGNORE, limited to `scope` pathspecs when the tool knows exactly what it read; None when
              git could not say).
  * start  -- {sha, dirty, dirty_n} taken when the run STARTED (snapshot()). A run is evidence for a sha only when
              start and end are the same sha and both clean: a commit landing mid-run is not tested (review Z F2).
  * covers -- what the run actually read (paths are what it was pointed at). lookup(paths=) returns a record only
              for the paths it covers: a partial run never speaks for the whole item (F5). A covers entry beyond the
              paths matches only that FILE, never as a folder (review AD3: a build's staged `src/` is not what it
              compiled -- see cover_entries).
  * nonce  -- a fresh random id per line, under the mac, so two genuine runs never seal alike (review AD5).
  * live_only -- the result describes a running game, not a tree (modcheck: the game holds whatever it loaded at
              launch, and nothing fingerprints that load). Never sha evidence (F3).
  * variant -- a weaker form of the tool (validate_patch "static" / "defnames"): summarize keys it apart (F6) and the
              Arbiter never counts it as a pass (review AA3).
  * result -- PASS / FAIL / UNMEASURED, nothing else.
  * origin -- what the WRITER can vouch for (review AA4): {via: "inproc" | "cli", start, end, pid, host}. start is
              "snapshot" only when the start state carries a token minted by snapshot()/tree_state() IN THIS PROCESS
              (an HMAC under a per-process random secret), else "caller"; end is "git" when record() asked git itself
              or the caller's end state carries such a token, else "caller". via "cli" is the `record` subcommand: a
              payload from another process, whose start/end nothing here can vouch for.
  * mac    -- HMAC-SHA256 over the rest of the line under the user's key file (KEY_ENV, else ~/.config/rimmandrake/
              close_evidence.key, 0600, created on first write). A line written by anything but record() fails it.
  * origin.tree -- "isolated" when the run's clone is a private checkout make_isolated()/`isolated` made for the
              end sha (marker under the mac key), else "shared" (review AB2: seat clones are shared by concurrent
              agents, so a file can change and be restored mid-run and equal clean endpoints prove nothing).
Schema: counts_as_evidence() takes v == 4 lines only, with every REQUIRED field, via "inproc", start "snapshot",
end "git", tree "isolated" and a valid mac. v1 lines (racy end-only recorder), v2 lines (written while `record`
trusted its payload), v3 lines (shared-clone runs) and v-less lines (hand-built) are never evidence (review AA5, AB2).
To make evidence: `close_evidence.py isolated [--sha S] -- <tool command>` (a ~11 s, ~3.6 GB transient checkout).

THE LIMIT, honestly: these are plain files written by the same Unix user that runs every agent. The mac and the origin
check stop ACCIDENTAL and LAZY forgery -- a hand-appended or `echo >>` line, a payload piped to `record`, a fixture
dict, a copied line with one field edited, a start state typed in by a caller. They do NOT stop a determined forger:
code running as this user can read the key, import this module and call its internals, or set RIMFLOW_SEAT to any
seat. Treat a line as "written by record() in a process that ran git itself", never as proof of who ran it.

Reads hold a SHARED flock on `<day>.jsonl.lock` (review AA1): on drvfs a reader racing appenders made 1-3 of 960
lines vanish with no unreadable fragment left behind; with the shared lock, 960/960.

Under Windows python.exe (modcheck's interpreter) a record is shipped as JSON to `wsl.exe -e python3 close_evidence.py
record`, so the store, git and the lock are the WSL ones (F4).

Writing evidence never fails the tool: every error is printed loudly to stderr and swallowed.
Under the selftest runner (`RM_SELFTEST_NESTED`) a tool run by a test writes nothing unless the test pointed
`RM_CLOSE_EVIDENCE_DIR` somewhere, so fixtures never pose as evidence; the runner itself records with force=True.

    python3 src/RimMandrake/Utils/close_evidence.py lookup --sha <sha> [--item ID] [--tool T] [--path P ...] [--all]
    python3 src/RimMandrake/Utils/close_evidence.py where
    python3 src/RimMandrake/Utils/close_evidence.py isolated [--clone C] [--sha S] -- <cmd ...>
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import hmac
import json
import os
import re
import secrets
import socket
import subprocess
import sys
from pathlib import Path

V = 4                          # v4: origin.tree (review AB2); v3 and older lines are never evidence
RESULTS = ("PASS", "FAIL", "UNMEASURED")
ENV_DIR = "RM_CLOSE_EVIDENCE_DIR"
KEY_ENV = "RM_CLOSE_EVIDENCE_KEY"            # path of the mac key file (selftests); default DEFAULT_KEY
DEFAULT_KEY = Path.home() / ".config" / "rimmandrake" / "close_evidence.key"
#: Fields every v4 line carries; a line missing one is not evidence.
REQUIRED = ("v", "ts", "tool", "clone", "sha", "dirty", "start", "paths", "covers", "result", "seat", "who", "origin",
            "live_only", "variant", "mac")
#: Per-process secret: a start/end state carrying a token under it was made by tree_state() in THIS process.
_PROC_SECRET = secrets.token_bytes(32)
_TOKEN = "_token"
AGENT_STORAGE = Path.home() / "dev/Lodestar/bin/lib/agent_storage.py"
#: Paths whose uncommitted state never feeds a tool's result: session transcripts are written continuously
#: into the bench clone, so counting them would make every run "dirty" and the record worthless.
DIRTY_IGNORE = ("conversations/",)
DIRTY_KEEP = 20
ALL = "*"                      # a covers entry that covers every path (an unreadable-line marker)
_ROOT_CACHE: list = []
_SHA_RE = re.compile(r"\b[0-9a-f]{40}\b")


# ------------------------------------------------------------------ paths and git

def to_wsl(p) -> str:
    """`\\\\wsl.localhost\\<distro>\\home\\x` -> `/home/x`; `D:\\x` -> `/mnt/d/x`; a POSIX path passes through."""
    s = str(p)
    u = re.match(r"^[\\/]{2}wsl(?:\.localhost|\$)[\\/][^\\/]+[\\/]?(.*)$", s, re.I)
    if u:
        return "/" + u.group(1).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):[\\/]?(.*)$", s)
    if m:
        return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    return s


def evidence_dir() -> Path:
    """The evidence folder (created). Raises when the storage root cannot be found."""
    env = os.environ.get(ENV_DIR, "").strip()
    if env:
        p = Path(env)
    else:
        if not _ROOT_CACHE:
            r = subprocess.run([sys.executable or "python3", str(AGENT_STORAGE), "rimmandrake"],
                               capture_output=True, text=True, timeout=30)
            out = r.stdout.strip()
            if r.returncode != 0 or not out:
                raise RuntimeError("agent_storage.py rimmandrake failed: %s" % (r.stderr.strip() or "no output"))
            _ROOT_CACHE.append(out)
        p = Path(_ROOT_CACHE[0]) / "evidence"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _git(clone, *args, timeout=60):
    """`git -C clone args`, never taking optional locks (a shared clone: `git status` refreshing the index must not
    make another agent's commit fail on index.lock -- F8). Under Windows python a \\\\wsl.localhost clone is reached
    through `wsl.exe -e git`."""
    base = ["git", "--no-optional-locks", "-C"]
    if os.name == "nt":
        cmd = ["wsl.exe", "-e"] + base + [to_wsl(clone)] + list(args)
    else:
        cmd = base + [str(clone)] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    return r.returncode, r.stdout


def clone_of(path) -> str | None:
    """The git toplevel holding `path` (a file or dir), or None."""
    p = Path(path).resolve()
    d = p if p.is_dir() else p.parent
    while not d.exists() and d != d.parent:
        d = d.parent
    try:
        rc, out = _git(d, "rev-parse", "--show-toplevel", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.strip() if rc == 0 and out.strip() else None


def tree_state(clone, scope=None) -> dict:
    """{sha, dirty, dirty_n, dirty_paths} for a clone. dirty None when git status could not run. `scope`: repo-relative
    pathspecs -- dirtiness counted only there (a tool that knows exactly what it read, e.g. winbuild's staged dirs)."""
    st = {"sha": None, "dirty": None, "dirty_n": None, "dirty_paths": []}
    try:
        rc, out = _git(clone, "rev-parse", "HEAD", timeout=30)
        if rc == 0 and out.strip():
            st["sha"] = out.strip()
        spec = ["--", *scope] if scope else []
        rc, out = _git(clone, "status", "--porcelain=v1", "-z", "--untracked-files=normal", *spec)
    except (OSError, subprocess.SubprocessError):
        return st
    if rc != 0:
        return st
    paths, recs, i = [], out.split("\0"), 0
    while i < len(recs):
        e = recs[i]
        i += 1
        if len(e) < 4:
            continue
        code, path = e[:2], e[3:]
        both = [path]
        if code[0] in "RC" and i < len(recs):    # rename/copy: the next NUL field is the source path
            both.append(recs[i])
            i += 1
        # review AB3: a rename INTO conversations/ removed a tracked file from outside it -- dirty when EITHER side
        # lies outside DIRTY_IGNORE (both are named, so the source is never hidden behind an ignored destination)
        if any(p and not p.startswith(DIRTY_IGNORE) for p in both):
            paths += [p for p in both if p and not p.startswith(DIRTY_IGNORE)]
    st.update(dirty=bool(paths), dirty_n=len(paths), dirty_paths=sorted(paths)[:DIRTY_KEEP])
    st[_TOKEN] = _state_token(st)
    return st


def _state_token(st) -> str:
    """HMAC of (sha, dirty, dirty_n) under this process's secret: record() can tell a state git produced here from
    one a caller typed in (review AA4)."""
    msg = json.dumps([st.get("sha"), st.get("dirty"), st.get("dirty_n")]).encode()
    return hmac.new(_PROC_SECRET, msg, hashlib.sha256).hexdigest()


def _minted_here(st) -> bool:
    return isinstance(st, dict) and isinstance(st.get(_TOKEN), str) and \
        hmac.compare_digest(st[_TOKEN], _state_token(st))


def snapshot(clone, scope=None) -> dict:
    """Tree state at the START of a run: pass it to record(start=...). Never raises."""
    try:
        clone = os.path.realpath(str(clone)) if os.name != "nt" else str(clone)
        st = tree_state(clone, scope)
    except Exception:  # noqa: BLE001
        st = {"sha": None, "dirty": None, "dirty_n": None}
    out = {"sha": st["sha"], "dirty": st["dirty"], "dirty_n": st["dirty_n"]}
    if _TOKEN in st:
        out[_TOKEN] = st[_TOKEN]
    return out


def by_clone(paths) -> dict:
    """{clone or None: [paths]} -- a run over several clones is recorded once per clone (F6, F9)."""
    out: dict = {}
    for p in paths:
        out.setdefault(clone_of(p), []).append(p)
    return out


def _rel(path, clone) -> str:
    p = os.path.abspath(str(path))
    if clone:
        try:
            r = os.path.relpath(p, os.path.realpath(clone))
            if not r.startswith(".."):
                return r.replace(os.sep, "/")
        except ValueError:
            pass
    return p


# ------------------------------------------------------------------ who ran it

#: rimflow's seat vocabulary (rimflow/model.py SEATS), read at call time; a fallback copy only if it cannot be imported
_SEATS_FALLBACK = ("BENCH", "FOUNDRY", "OWNER", "DECIDE", "BUILD", "CHECK", "REP", "RUNNER", "DISPATCHER")
_RIMFLOW = Path(__file__).resolve().parents[1] / "rimflow"


def _seats_and_root():
    try:
        sys.path.insert(0, str(_RIMFLOW.parent))
        from rimflow import model
        return tuple(model.SEATS), model.ROOT
    except Exception:  # noqa: BLE001
        return _SEATS_FALLBACK, str(Path(__file__).resolve().parents[3])
    finally:
        if sys.path and sys.path[0] == str(_RIMFLOW.parent):
            sys.path.pop(0)


def whoami() -> dict:
    """WHO ran a tool, in rimflow's own seat order (rimflow/cli.py resolve_seat, minus --seat): RIMFLOW_SEAT, AGENT_SEAT,
    then `.claude/session_roles/<this session id>` -- this session's file only, never the newest. A value that is not a
    rimflow seat is kept as `seat_raw` and the seat stays None: a wrong seat is worse than none. Never raises.
    bridge_session is the id a commit's `Claude-Session:` trailer names, so the Arbiter can tell a run made by the
    session that made the commit. -> {seat, seat_from, seat_raw, session, bridge_session, agent}"""
    seats, root = _seats_and_root()
    sid = os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("CLAUDE_CODE_SESSION_ID") or None
    out = {"seat": None, "seat_from": None, "seat_raw": None, "session": sid,
           "bridge_session": os.environ.get("CLAUDE_CODE_BRIDGE_SESSION_ID") or None,
           "agent": os.environ.get("AI_AGENT") or None}
    cands = [("RIMFLOW_SEAT", os.environ.get("RIMFLOW_SEAT")), ("AGENT_SEAT", os.environ.get("AGENT_SEAT"))]
    if sid:
        try:
            words = (Path(root) / ".claude" / "session_roles" / sid).read_text(encoding="utf-8").replace("-", " ").split()
            cands.append(("session role file", next((w for w in words if w.upper() in seats), None)))
        except OSError:
            pass
    for src, val in cands:
        if not val or not val.strip():
            continue
        v = val.strip().upper()
        if v in seats:
            out.update(seat=v, seat_from=src)
        else:
            out.update(seat_raw=val.strip(), seat_from=src)
        break
    return out


# ------------------------------------------------------------------ write

def _key_path() -> Path:
    return Path(os.environ.get(KEY_ENV, "").strip() or DEFAULT_KEY)


def publish_once(path, content: str, mode=0o600) -> bool:
    """Publish `content` at `path` only if nothing is there, never exposing a partial file (review AB7/AB9): the text
    goes into a create-exclusive tmp file with a unique name, is fsynced, then hard-linked into place -- a link is a
    rename that refuses to replace, so of N racing initialisers exactly one wins and the rest read the winner's
    complete file. A reader can never see an empty or half-written key/salt. True when this call published it."""
    p = Path(path)
    if p.exists():
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.parent / (".%s.%d.%s.tmp" % (p.name, os.getpid(), secrets.token_hex(6)))
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.link(str(tmp), str(p))
            return True
        except FileExistsError:
            return False
    finally:
        try:
            os.unlink(str(tmp))
        except OSError:
            pass


def _key(create=False) -> bytes:
    """The mac key. Reading: a missing key raises (nothing could be verified -- that is UNMEASURED, not 'no
    evidence'). Writing: created once, 0600, published atomically by publish_once() (review AB7: a writer racing the
    initialiser read an empty file and dropped its FAIL)."""
    p = _key_path()
    if not p.is_file():
        if not create:
            raise RuntimeError("close-evidence key %s missing: no line can be verified" % p)
        publish_once(p, secrets.token_hex(32))
    k = p.read_text(encoding="utf-8").strip()
    if len(k) < 32:
        raise RuntimeError("close-evidence key %s is empty or short" % p)
    return k.encode()


def _mac(rec, key) -> str:
    body = {k: v for k, v in rec.items() if k != "mac"}
    return hmac.new(key, json.dumps(body, sort_keys=True, default=str).encode(), hashlib.sha256).hexdigest()


def _route_mac(sha, tool, key) -> str:
    return hmac.new(key, ("route\0%s\0%s" % (sha, tool)).encode(), hashlib.sha256).hexdigest()


def route_ok(sha, tool, route, key) -> bool:
    """`route` seals this (sha, tool) pair on its own (review AC1): a line whose body is damaged can still be routed to
    its commit by a sha nobody without the key could have altered."""
    return (isinstance(sha, str) and isinstance(tool, str) and isinstance(route, str) and bool(_MAC_RX.fullmatch(route))
            and hmac.compare_digest(route, _route_mac(sha, tool, key)))


def seal(rec, key=None) -> dict:
    """The line as written: JSON-normalised, route (sha+tool) and mac (whole line) added."""
    key = key or _key(create=True)
    rec = json.loads(json.dumps({k: v for k, v in rec.items() if k not in ("mac", "route")}, default=str))
    rec["route"] = _route_mac(rec.get("sha"), rec.get("tool"), key)
    rec["mac"] = _mac(rec, key)
    return rec


_MAC_RX = re.compile(r"[0-9a-f]{64}")


def mac_ok(rec, key) -> bool:
    """The line's mac verifies. A mac that is not 64 lowercase hex (e.g. non-ASCII, on which compare_digest raises)
    is simply unverifiable (review AC5)."""
    m = rec.get("mac")
    return isinstance(m, str) and bool(_MAC_RX.fullmatch(m)) and hmac.compare_digest(m, _mac(rec, key))


# ------------------------------------------------------------------ isolated checkouts (review AB2)
#
# The seat clones are shared by concurrent agents: a file can change and be restored DURING a run, so equal clean
# snapshots at start and end do not prove the run read that sha (A -> B -> A passes both; a content hash of the
# covered paths at both ends is blind to it for the same reason). Only a run inside a private checkout of the sha,
# which no other agent knows the path of, speaks for the sha. make_isolated() makes one (`git clone --shared
# --no-checkout` + detached checkout: ~11 s and ~3.6 GB transient for the bench clone, deleted afterwards) and leaves
# a marker in its .git under the mac key; record() writes origin.tree "isolated" only for a clone carrying a valid
# marker for its end sha. Runs in a shared clone stay recorded (audit) but are never evidence.

ISOLATED_MARK = "rm_isolated"
ISOLATED_ROOT_ENV = "RM_ISOLATED_ROOT"     # where checkouts go; default the temp dir (ext4, not drvfs)


def _iso_msg(clone, sha) -> bytes:
    return json.dumps(["isolated", os.path.realpath(str(clone)), (sha or "").lower()]).encode()


def isolated_ok(clone, sha) -> bool:
    """`clone` is a checkout make_isolated() made for exactly `sha` (marker valid under the mac key)."""
    if not clone or not sha:
        return False
    try:
        mark = (Path(clone) / ".git" / ISOLATED_MARK).read_text(encoding="utf-8").strip()
        return hmac.compare_digest(mark, hmac.new(_key(), _iso_msg(clone, sha), hashlib.sha256).hexdigest())
    except (OSError, RuntimeError):
        return False


def make_isolated(clone, sha="HEAD", root=None) -> tuple:
    """A private checkout of `sha` from `clone` -> (checkout dir, full sha, temp dir to delete). Raises on failure."""
    import tempfile
    rc, out = _git(clone, "rev-parse", "--verify", "%s^{commit}" % sha, timeout=30)
    if rc != 0 or not _SHA_RE.fullmatch(out.strip()):
        raise RuntimeError("%s does not resolve in %s" % (sha, clone))
    full = out.strip()
    base = root or os.environ.get(ISOLATED_ROOT_ENV) or tempfile.gettempdir()
    Path(base).mkdir(parents=True, exist_ok=True)
    td = tempfile.mkdtemp(prefix="ce_iso_", dir=str(base))
    co = os.path.join(td, "c")
    for args in (["clone", "-q", "--shared", "--no-checkout", os.path.realpath(str(clone)), co],
                 ["-C", co, "checkout", "-q", "--detach", full]):
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=540)
        if r.returncode != 0:
            import shutil
            shutil.rmtree(td, ignore_errors=True)
            raise RuntimeError("git %s failed: %s" % (args[0] if args[0] != "-C" else args[2], r.stderr.strip()[-300:]))
    key = _key(create=True)
    (Path(co) / ".git" / ISOLATED_MARK).write_text(
        hmac.new(key, _iso_msg(co, full), hashlib.sha256).hexdigest(), encoding="utf-8")
    return os.path.realpath(co), full, td


def _isolated_cli(argv) -> int:
    """`isolated [--clone C] [--sha S] -- cmd ...`: run cmd (cwd = a private checkout of S) and delete the checkout.
    Evidence the cmd records there is sha evidence; e.g. `close_evidence.py isolated -- python3
    src/RimMandrake/Utils/run_selftests.py --only <tests>` (run_selftests' repo root is its own file's clone)."""
    import shutil
    ap = argparse.ArgumentParser(prog="close_evidence.py isolated")
    ap.add_argument("--clone", default=os.getcwd())
    ap.add_argument("--sha", default="HEAD")
    ap.add_argument("--keep", action="store_true", help="leave the checkout (debugging)")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("a command is needed after --")
    clone = clone_of(a.clone) or a.clone
    co, full, td = make_isolated(clone, a.sha)
    print("close_evidence: isolated checkout of %s at %s" % (full[:12], co), file=sys.stderr, flush=True)
    try:
        return subprocess.run(cmd, cwd=co).returncode
    finally:
        if not a.keep:
            shutil.rmtree(td, ignore_errors=True)


def build_record(tool, result, paths, clone=None, detail=None, item=None, now=None, start=None, end=None,
                 scope=None, covers=None, live_only=False, variant=None, seat=None, who=None, via="inproc") -> dict:
    if result not in RESULTS:
        raise ValueError("result must be one of %s, got %r" % (RESULTS, result))
    paths = [str(p) for p in (paths or [])]
    if clone is None and paths:
        clone = clone_of(paths[0])
    clone = os.path.realpath(str(clone)) if clone else None
    if end is None:
        end = tree_state(clone, scope) if clone else {"sha": None, "dirty": None, "dirty_n": None, "dirty_paths": []}
    who_from = "caller" if isinstance(who, dict) else "whoami"
    origin = {"via": via, "start": "snapshot" if (via == "inproc" and _minted_here(start)) else "caller",
              "end": "git" if (via == "inproc" and _minted_here(end)) else "caller",
              "tree": "isolated" if (via == "inproc" and isolated_ok(clone, end.get("sha"))) else "shared",
              "who": who_from, "pid": os.getpid(), "host": socket.gethostname()}
    st = {"sha": end.get("sha"), "dirty": end.get("dirty"), "dirty_n": end.get("dirty_n"),
          "dirty_paths": list(end.get("dirty_paths") or [])}
    start = ({"sha": start.get("sha"), "dirty": start.get("dirty"), "dirty_n": start.get("dirty_n")}
             if isinstance(start, dict) else None)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    rel = [_rel(p, clone) for p in paths]
    who = dict(who) if isinstance(who, dict) else whoami()
    if seat:
        who.update(seat=seat, seat_from=who.get("seat_from") or "caller")
    # nonce (review AD5): a fresh random id per record, under the mac. Without it two runs with the same result in the
    # same second by the same process (FAIL -> PASS -> FAIL) seal to the SAME mac and lookup's replay dedupe drops the
    # second FAIL, leaving the PASS standing; a true replay (the same line again) still dedupes.
    return {"v": V, "ts": now.isoformat(timespec="seconds"), "nonce": secrets.token_hex(16), "tool": tool,
            "clone": clone, **st, "start": start,
            "paths": rel, "covers": [_rel(p, clone) for p in covers] if covers is not None else rel,
            "result": result, "item": item if item is not None else (os.environ.get("RIMFLOW_ITEM") or None),
            "seat": who.get("seat"), "who": who, "origin": origin,
            "live_only": bool(live_only), "variant": variant, "detail": detail or {}}


def _append(path: Path, data: bytes) -> None:
    """Append under an exclusive flock on `<file>.lock` (drvfs O_APPEND is not atomic across processes -- F1);
    a short write is retried until the whole line is down."""
    import fcntl
    lfd = os.open(str(path) + ".lock", os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(lfd, fcntl.LOCK_EX)
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            view = memoryview(data)
            while view:
                n = os.write(fd, view)
                if n <= 0:
                    raise OSError("short write (%d of %d bytes left)" % (n, len(view)))
                view = view[n:]
        finally:
            os.close(fd)
    finally:
        try:
            fcntl.flock(lfd, fcntl.LOCK_UN)
        finally:
            os.close(lfd)


def _ship_to_wsl(payload: dict) -> dict | None:
    """Windows python: the WSL side records (its store, its git, its flock)."""
    if os.environ.get(ENV_DIR):
        payload["evidence_dir"] = to_wsl(os.environ[ENV_DIR])
    payload.setdefault("item", os.environ.get("RIMFLOW_ITEM") or None)
    payload.setdefault("who", whoami())          # the CALLER's environment: wsl.exe does not carry it across
    payload["paths"] = [to_wsl(p) for p in payload.get("paths") or []]
    if payload.get("covers") is not None:
        payload["covers"] = [to_wsl(p) for p in payload["covers"]]
    if payload.get("clone"):
        payload["clone"] = to_wsl(payload["clone"])
    r = subprocess.run(["wsl.exe", "-e", "python3", to_wsl(os.path.abspath(__file__)), "record"],
                       input=json.dumps(payload, default=str), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("wsl.exe close_evidence record exit %d: %s" % (r.returncode, (r.stderr or r.stdout)[-400:]))
    return json.loads(r.stdout.strip().splitlines()[-1])


def record(tool, result, paths, clone=None, detail=None, item=None, force=False, start=None, end=None, scope=None,
           covers=None, live_only=False, variant=None) -> dict | None:
    """Append one evidence line. NEVER raises: a failure is printed loudly and None returned.
    start: snapshot() taken when the run began (without it the line is recorded but is not evidence)."""
    try:
        if os.environ.get("RM_SELFTEST_NESTED") and not force and not os.environ.get(ENV_DIR):
            return None                       # a tool run by a selftest: fixture, not evidence
        if os.name == "nt":
            return _ship_to_wsl({"tool": tool, "result": result, "paths": [str(p) for p in paths or []],
                                 "clone": str(clone) if clone else None, "detail": detail, "item": item,
                                 "start": start, "end": end, "scope": scope,
                                 "covers": [str(c) for c in covers] if covers is not None else None,
                                 "live_only": live_only, "variant": variant})
        rec = seal(build_record(tool, result, paths, clone, detail, item, start=start, end=end, scope=scope,
                                covers=covers, live_only=live_only, variant=variant))
        line = (json.dumps(rec, sort_keys=True, default=str) + "\n").encode("utf-8")
        _append(evidence_dir() / ("%s.jsonl" % rec["ts"][:10]), line)
        return rec
    except Exception as exc:  # noqa: BLE001 -- evidence is a side channel; the tool's own verdict stands
        print("!!! CLOSE-EVIDENCE WRITE FAILED (%s, tool=%s): %s: %s -- the tool's result is unaffected, but no "
              "gate will see this run" % (__file__, tool, type(exc).__name__, exc), file=sys.stderr, flush=True)
        return None


# ------------------------------------------------------------------ read

def _days(n, today=None):
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    return [(today - datetime.timedelta(days=k)).isoformat() for k in range(n)]


def _read_locked(f: Path) -> list:
    """The day file's lines, read under a SHARED flock on `<file>.lock` (review AA1): appenders hold it exclusively,
    so a read never overlaps an append. On drvfs an unlocked reader made appends vanish without a trace."""
    import fcntl
    lock = str(f) + ".lock"
    try:
        lfd = os.open(lock, os.O_RDWR | os.O_CREAT, 0o644)
    except PermissionError:
        lfd = os.open(lock, os.O_RDONLY)
    try:
        fcntl.flock(lfd, fcntl.LOCK_SH)
        with f.open(encoding="utf-8", errors="replace") as fh:
            return fh.readlines()
    finally:
        try:
            fcntl.flock(lfd, fcntl.LOCK_UN)
        finally:
            os.close(lfd)


def read_all(days=30, folder=None, bad_out=None):
    """Every record in the last `days` day files, oldest first. Unreadable lines are skipped, counted on stderr and,
    when `bad_out` (a list) is given, appended to it as (day, fragment) so a caller can refuse to call the day clean."""
    folder = Path(folder) if folder else evidence_dir()
    out, bad = [], 0
    for day in sorted(_days(days)):
        f = folder / ("%s.jsonl" % day)
        if not f.is_file():
            continue
        for ln in _read_locked(f):
            if not ln.strip():
                continue
            try:
                r = json.loads(ln)
                if not isinstance(r, dict):
                    raise ValueError("not an object")
                out.append(r)
            except ValueError:
                bad += 1
                if bad_out is not None:
                    bad_out.append((day, ln))
    if bad:
        print("close_evidence: %d unreadable line(s) skipped" % bad, file=sys.stderr)
    return out


def _sha_match(a, b) -> bool:
    if not a or not b:
        return False
    n = min(len(a), len(b))
    return n >= 7 and a[:n].lower() == b[:n].lower()


def schema_problems(rec) -> list:
    """Why a line is not a v4 line this module wrote: [] when it is (mac not checked here; see mac_ok)."""
    probs = []
    if rec.get("v") != V:
        probs.append("v=%r (only v%d lines are evidence)" % (rec.get("v"), V))
    probs += ["missing %s" % k for k in REQUIRED if k not in rec]
    o = rec.get("origin") if isinstance(rec.get("origin"), dict) else {}
    if o.get("via") != "inproc":
        probs.append("origin.via=%r (a payload from another process)" % o.get("via"))
    if o.get("start") != "snapshot":
        probs.append("origin.start=%r (start state not minted by snapshot() in the writing process)" % o.get("start"))
    if o.get("end") != "git":
        probs.append("origin.end=%r (end state not read from git by the writer)" % o.get("end"))
    if o.get("tree") != "isolated":
        probs.append("origin.tree=%r (run in a clone other agents share: the tree may have changed mid-run)"
                     % o.get("tree"))
    return probs


def counts_as_evidence(rec, key=None) -> bool:
    """A record speaks for its sha only when it is a v4 line record() wrote in an isolated checkout (schema_problems() empty; mac valid under
    `key` when given -- lookup() always gives it), from a clean tree at a known sha, the same at the start and the end
    of the run, and describes a tree (not a live game). v1, v2 and v-less lines never do."""
    if not (bool(rec.get("sha")) and rec.get("dirty") is False and rec.get("result") in RESULTS):
        return False
    if rec.get("live_only") or schema_problems(rec):
        return False
    if key is not None and not mac_ok(rec, key):
        return False
    st = rec.get("start")
    return isinstance(st, dict) and st.get("dirty") is False and bool(st.get("sha")) and \
        st["sha"].lower() == rec["sha"].lower()


def _covers(rp, f) -> bool:
    """Record path rp covers touched file f: equal, or f under rp/. Never by name: selftest_<stem>.py beside <stem>.py
    covers <stem>.py only when the run's trace or declaration says so (a `covers` entry of its own, see cover_entries)."""
    if rp == ALL:
        return True
    rp, f = rp.rstrip("/"), f.rstrip("/")
    return f == rp or f.startswith(rp + "/") or rp in ("", ".")


#: tools whose covers beyond `paths` must each be vouched for by detail.covers_by (evidence_covers.py)
DERIVED_COVERS = ("selftest",)
#: tools none of whose entries is a folder: a build vouches for the files it compiled, never the dirs it staged (AD3)
EXACT_TOOLS = ("winbuild",)


def _bad_source(c) -> bool:
    return (not isinstance(c, str) or c in ("", ".", ALL) or c.endswith("/") or os.path.isabs(c)
            or c.startswith("..") or "/../" in c)


def cover_entries(rec) -> list:
    """[(entry, exact)] -- what a record may vouch for. A path the run was pointed at matches as itself or as a folder
    (_covers) -- except for an EXACT_TOOLS build, whose every entry is a file it compiled. Any other covers entry (not
    in paths) is a plain relative FILE path matching only itself, never as a folder (review AD3: winbuild used to
    cover its staged dirs, so a passing build of one csproj covered every .py under src/; it now names the compile
    items its own .srchash stamp lists). A selftest's SOURCE entry (SELFTEST_EVIDENCE_FIX_COVERS_TESTS_ONLY) counts
    only when detail.covers_by names it with a non-empty list of tests that are all among the run's paths. Anything
    else in covers is a forged (or pre-AD folder) claim and is dropped."""
    cov = rec.get("covers")
    cov = cov if isinstance(cov, list) else (rec.get("paths") or [])
    paths = set(p for p in (rec.get("paths") or []) if isinstance(p, str))
    if rec.get("tool") not in DERIVED_COVERS:
        exact_tool = rec.get("tool") in EXACT_TOOLS
        return [(c, exact_tool) if c in paths else (c, True) for c in cov
                if (c in paths and not exact_tool) or not _bad_source(c)]
    det = rec.get("detail") if isinstance(rec.get("detail"), dict) else {}
    by = det.get("covers_by") if isinstance(det.get("covers_by"), dict) else {}
    out = []
    for c in cov:
        if c in paths:
            out.append((c, False))
            continue
        tests = by.get(c)
        if (not _bad_source(c) and isinstance(tests, list) and tests
                and all(isinstance(t, str) and t in paths for t in tests)):
            out.append((c, True))
    return out


def _entry_covers(entry, f) -> bool:
    c, exact = entry
    return c == f.rstrip("/") if exact else _covers(c, f)


def _norm_path(p, clone) -> str:
    s = str(p)
    if os.path.isabs(s):
        return _rel(s, clone)
    s = s.replace(os.sep, "/")
    while s.startswith("./"):
        s = s[2:]
    return s


def covered(rec, paths) -> list:
    """The subset of `paths` this record actually covers (its `covers`, else its `paths`)."""
    ents = cover_entries(rec)
    return [p for p in paths if any(_entry_covers(e, _norm_path(p, rec.get("clone"))) for e in ents)]


def uncovered(records, paths) -> list:
    """`paths` that no record covers: a gate that needs every touched path tested reads this."""
    return [p for p in paths if not any(covered(r, [p]) for r in records)]


def _bad_marker(sha, frags, unverifiable=0) -> dict:
    """An UNMEASURED record standing for unreadable or unverifiable line(s) that may have held a run at `sha` (F1,
    review AB5: a lost or damaged FAIL must never leave an older PASS standing)."""
    return {"v": V, "ts": "", "tool": "close_evidence", "clone": None, "sha": sha, "dirty": False, "dirty_n": 0,
            "dirty_paths": [], "start": {"sha": sha, "dirty": False, "dirty_n": 0}, "paths": [ALL], "covers": [ALL],
            "result": "UNMEASURED", "item": None, "seat": None, "live_only": False, "variant": None,
            "detail": {"unreadable_lines": len(frags) - unverifiable, "unverifiable_lines": unverifiable,
                       "days": sorted({d for d, _ in frags})}}


def _top_level(text, key):
    """The string value of TOP-LEVEL `key` in a possibly truncated JSON object text, or None when it cannot be
    recovered unambiguously: absent, cut off, not a string, or present twice at the top level (review AB6: a hash
    inside `detail` says nothing about whose line this was)."""
    found, depth, i, n, last = [], 0, 0, len(text), None
    while i < n:
        c = text[i]
        if c == '"':
            j, esc = i + 1, False
            while j < n and (esc or text[j] != '"'):
                esc = (not esc) and text[j] == "\\"
                j += 1
            if j >= n:
                break                                 # string cut off
            last = (depth, text[i:j + 1])
            i = j + 1
            continue
        if c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
        elif c == ":" and depth == 1 and last and last[0] == 1:
            try:
                k = json.loads(last[1])
            except ValueError:
                k = None
            if k == key:
                m = re.match(r'\s*("(?:[^"\\]|\\.)*")', text[i + 1:])
                try:
                    found.append(json.loads(m.group(1)) if m else None)
                except ValueError:
                    found.append(None)
        last = None if c not in " \t\r\n" else last
        i += 1
    return found[0] if len(found) == 1 and isinstance(found[0], str) else None


_SHA_ANY = re.compile(r"[0-9a-fA-F]{7,40}")
_SHA_FULL = re.compile(r"[0-9a-f]{40}")


def _legacy(r) -> bool:
    """An unsealed line (pre-seal v1/v2, or hand-written: no mac and no route). It never was evidence, so its plain
    sha may route it; stripping both seals off a sealed line is the same act as deleting it, which no reader of an
    append-only file can detect. A line that carries either seal and fails is routed only by a route that verifies."""
    return "mac" not in r and "route" not in r


def _routed(sha, tool, route, key, want_sha, want_tool) -> bool:
    """May an unverifiable line concern lookup (want_sha, want_tool)? Only a route that verifies lets its sha/tool
    exclude it (review AC1: an unsealed sha is the forger's word)."""
    if route is not None and route_ok(sha, tool, route, key):
        return sha == want_sha and not (want_tool and tool != want_tool)
    return True


def lookup(sha=None, item=None, tool=None, days=30, folder=None, include_dirty=False, paths=None,
           include_live=False):
    """Evidence for sha S and/or item X, oldest first.

    sha given: records at that commit (prefix match, >=7 chars), whatever item they name.
    item given: records tagged with that item; with sha too, both must match.
    paths given: only records that cover at least one of them (repo-relative or absolute), so a partial run counts
    only for what it tested; uncovered(records, paths) names the rest.
    Dirty, unknown-tree, start/end-drift, shared-clone, cli-origin and pre-v4 records are excluded unless include_dirty
    (audit only); live-only (modcheck) records unless include_live. Lines that cannot be trusted are never dropped
    silently: an unreadable line, or a JSON line whose mac does not verify (a damaged FAIL, a UTF-8 replacement, a
    hand-written or pre-v3 line), adds ONE UNMEASURED `close_evidence` record when it may concern this lookup -- its
    TOP-LEVEL sha matches or cannot be recovered, and (with tool) its top-level tool matches or cannot be recovered."""
    if not sha and not item:
        raise ValueError("lookup needs a sha or an item")
    if sha is not None and not (isinstance(sha, str) and _SHA_FULL.fullmatch(sha)):
        raise ValueError("lookup needs ONE full 40-hex lowercase sha, got %r (review AC2: resolve a short sha or rev "
                         "expression to its commit first, e.g. arbiter_tiers.resolve_sha_any)" % (sha,))
    key = _key()                       # raises when missing: nothing verifiable is UNMEASURED, not "no evidence"
    bad: list = []
    hits, unver = [], []
    seen_macs = set()
    for r in read_all(days, folder, bad_out=bad):
        if not mac_ok(r, key):                        # review AB5: unverifiable is UNMEASURED, never absent
            rs, rt = r.get("sha"), r.get("tool")
            if not sha:
                continue                              # an item lookup cannot attribute an unverifiable line
            if _legacy(r):
                if not (isinstance(rs, str) and _SHA_ANY.fullmatch(rs) and _sha_match(rs, sha)):
                    continue                          # pre-seal line naming another commit
                if tool and isinstance(rt, str) and rt != tool:
                    continue
            elif not _routed(rs, rt, r.get("route"), key, sha, tool):
                continue                              # its sealed route names another commit or tool
            unver.append(("?", json.dumps(r, default=str)))
            continue
        if r["mac"] in seen_macs:
            continue                                  # review AC3: a replayed line never re-enters, nor moves later
        seen_macs.add(r["mac"])
        if sha and r.get("sha") != sha:
            continue
        if item and r.get("item") != item:
            continue
        if tool and r.get("tool") != tool:
            continue
        if r.get("live_only"):
            if not include_live:
                continue
        elif not include_dirty and not counts_as_evidence(r, key):
            continue
        if paths and not covered(r, list(paths)):
            continue
        hits.append(r)
    if sha:
        def maybe_ours(ln):                   # a torn line: only a sealed route recoverable from it may exclude it
            return _routed(_top_level(ln, "sha"), _top_level(ln, "tool"), _top_level(ln, "route"), key, sha, tool)
        frags = [(d, ln) for d, ln in bad if maybe_ours(ln)] + unver
        if frags:
            hits.append(_bad_marker(sha, frags, unverifiable=len(unver)))
    return hits


def _toolkey(r) -> str:
    return r["tool"] + (":%s" % r["variant"] if r.get("variant") else "")


def _cov(r) -> list:
    """The record's vouched-for entries (cover_entries); a run that names nothing is its own key (covers no path)."""
    return cover_entries(r) or [("\0", True)]


def latest_covering(records, path) -> dict:
    """{tool key: the latest record (ts, then file order) whose actual coverage includes `path`} (review AB4)."""
    out = {}
    for r in sorted(records, key=lambda r: r.get("ts") or ""):
        if covered(r, [path]):
            out[_toolkey(r)] = r
    return out


def summarize(records) -> dict:
    """{tool: PASS|FAIL|UNMEASURED} by ACTUAL coverage (review AB4): for each path any run of the tool covered, the
    latest run covering that path decides it; the tool reads the worst over its paths (FAIL < UNMEASURED < PASS). A
    later narrow PASS of {a} therefore never erases an earlier FAIL of {b}, whatever paths the runs were pointed at;
    a later run covering b does. A variant (validate_patch without --defs) is its own key, `tool:variant`."""
    order = ("FAIL", "UNMEASURED", "PASS").index
    by: dict = {}
    for r in sorted(records, key=lambda r: r.get("ts") or ""):
        by.setdefault(_toolkey(r), []).append(r)
    out = {}
    for k, rs in by.items():
        worst = None
        for p in {c for r in rs for c, _x in _cov(r)}:
            last = None
            for r in rs:
                if any(_entry_covers(e, p) for e in _cov(r)):
                    last = r
            res = last["result"] if last else "UNMEASURED"
            worst = res if worst is None else min(worst, res, key=order)
        out[k] = worst
    return out


# ------------------------------------------------------------------ cli

def _record_cli() -> int:
    """`record`: one JSON payload on stdin (from a Windows python.exe caller) -> one line; prints the record.
    The payload's start and WHO are another process's word: the line is origin.via "cli", its end is re-read from git
    here (the payload's end is ignored), and it is never sha evidence (review AA4). Its one caller, modcheck, writes
    live_only lines, which are never sha evidence anyway."""
    p = json.loads(sys.stdin.read())
    if p.get("evidence_dir"):
        os.environ[ENV_DIR] = p["evidence_dir"]
    for k in ("RM_SELFTEST_NESTED",):
        os.environ.pop(k, None)               # the Windows side already applied the nested rule
    try:
        who = dict(p["who"]) if isinstance(p.get("who"), dict) else {}
        who["seat_from"] = "shipped:%s" % who.get("seat_from")      # asserted by the caller, never verified here
        rec = seal(build_record(p["tool"], p["result"], p.get("paths"), p.get("clone"), p.get("detail"), p.get("item"),
                                start=p.get("start"), end=None, scope=p.get("scope"), covers=p.get("covers"),
                                live_only=p.get("live_only", False), variant=p.get("variant"), who=who, via="cli"))
        _append(evidence_dir() / ("%s.jsonl" % rec["ts"][:10]),
                (json.dumps(rec, sort_keys=True, default=str) + "\n").encode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print("record failed: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1
    print(json.dumps(rec, sort_keys=True, default=str))
    return 0


def _main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["isolated"]:
        return _isolated_cli(argv[1:])
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    lk = sub.add_parser("lookup", help="evidence for a sha and/or item")
    lk.add_argument("--sha")
    lk.add_argument("--item")
    lk.add_argument("--tool")
    lk.add_argument("--path", action="append", default=[], help="only records covering this path (repeatable)")
    lk.add_argument("--days", type=int, default=30)
    lk.add_argument("--all", action="store_true", help="include dirty-tree records (audit; never evidence)")
    lk.add_argument("--live", action="store_true", help="include live-only (modcheck) records (never sha evidence)")
    sub.add_parser("where", help="print the evidence folder")
    sub.add_parser("record", help="internal: one JSON record payload on stdin (Windows python.exe callers)")
    sub.add_parser("isolated", help="isolated [--clone C] [--sha S] -- cmd ...: run cmd in a private checkout of S")
    a = ap.parse_args(argv)
    if a.cmd == "where":
        print(evidence_dir())
        return 0
    if a.cmd == "record":
        return _record_cli()
    if not (a.sha or a.item):
        ap.error("lookup needs --sha or --item")
    hits = lookup(a.sha, a.item, a.tool, a.days, include_dirty=a.all, paths=a.path or None, include_live=a.live)
    for r in hits:
        ps = r.get("paths") or []
        print("%s %-14s %-10s %s%s%s %s%s" % (r["ts"], r["tool"], r["result"], (r.get("sha") or "-")[:12],
                                              "" if counts_as_evidence(r) else " NOT-EVIDENCE",
                                              " LIVE" if r.get("live_only") else "", ",".join(ps[:4]),
                                              " (+%d)" % (len(ps) - 4) if len(ps) > 4 else ""))
    print("%d record(s); summary %s" % (len(hits), json.dumps(summarize(hits), sort_keys=True)))
    if a.path:
        print("uncovered: %s" % (", ".join(uncovered(hits, a.path)) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
