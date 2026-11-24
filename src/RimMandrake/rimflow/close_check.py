#!/usr/bin/env python3
"""close_check.py: the daily no-AI check of every closed item. No model, no role.

Page: design/specs/2026-11-23-close-check/boundary.md; tests: selftest_close_check.py. It replaces the pre-screen that
only a launch of the Auditor role started (last run 2026-11-01; the role retired 2026-11-23).

    python3 src/RimMandrake/rimflow/close_check.py run [--apply]    check the window; --apply reopens and writes the reading
    python3 src/RimMandrake/rimflow/close_check.py fresh            0 the reading is recent, 1 stale, 2 could not look

A finding is `substance` (the close claims work that is not on main) or `form` (the work can be there, its paper is
not). A substance finding reopens the same item with a `fail` run; a form finding is listed in the reading.
Exit of run: 0 done, 1 a reopen was refused (named), 2 UNMEASURED (cause named, no reading written).
Reading: D:\\ClaudeWork\\rimmandrake\\close_check\\reading.json.
"""
import argparse
import bisect
import datetime
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
READING = "/mnt/d/ClaudeWork/rimmandrake/close_check/reading.json"
UNIT = "rm-close-check.service"
START = "2026-11-01T21:01:30Z"      # the last pre-screen of the Auditor era: the first run takes up from there
# Danger: the check stops and nobody sees it (it did, 2026-11-01 to 2026-11-23). The timer is daily; 36 h is one missed day.
# budget: danger=the close check stops and nobody sees it (2026-11-01 to 2026-11-23); ends no work: the dead-man alarms
MAX_AGE_S = 36 * 3600
# Danger: a close written in a clone lands on main after the run that covers its time (`--publish` exit 4), and is never
# checked. A second look at a close costs a lookup and reopens nothing twice.
OVERLAP_S = 3 * 86400
GIT_TIMEOUT_S, CLI_TIMEOUT_S = 1800, 900        # hang guards, far above a real call
LEDGER = "infrastructure/state/ledger/"
SOURCE_EXTS = (".py", ".cs", ".xml", ".sh", ".ps1", ".js", ".ts", ".csproj")
# Not on this disk by design: Transient lives ~14 days in the clone that wrote it, seat-tmp is scratch, C:\SteveDesktop is
# the other machine's C:.
NOT_HERE = ("/Transient/", "/.seat-tmp/", "/mnt/c/SteveDesktop/")
_PATH_RX = re.compile(r"(?<![\w.-]:)(?<![\w.-])([A-Za-z]:\\[^;,\s]+|/(?:mnt|home|tmp)/[^;,\s]+)")
_SRC_RX = re.compile(r"(?<![\w/.\\:-])((?:src|skills|infrastructure|tests?|\.claude)/[\w./+-]*\w\.\w+)")


class Unmeasured(Exception):
    pass


def _epoch(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def _iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


class Commits:
    """What main holds. Raises Unmeasured when git cannot answer, so "could not look" never reads as "not on main"."""

    def __init__(self, repo=REPO):
        self.repo = repo
        refs = ["HEAD"] + (["origin/main"] if self._git("for-each-ref", "refs/remotes/origin/main").strip() else [])
        self.all = sorted(self._git("rev-list", *refs).split())
        if not self.all:
            raise Unmeasured("git rev-list names no commit in %s" % repo)

    def _git(self, *a, **kw):
        try:
            r = subprocess.run(["git", "-C", self.repo] + list(a), capture_output=True, text=True, errors="replace",
                               timeout=GIT_TIMEOUT_S, **kw)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise Unmeasured("git %s: %s" % (a[0], e))
        if r.returncode:
            raise Unmeasured("git %s exit %d: %s" % (a[0], r.returncode, r.stderr.strip()[:200]))  # cut-ok: exception message
        return r.stdout

    def full(self, sha):
        """The full sha on main that `sha` names, or None. Under 7 characters names nothing."""
        s = sha.lower()
        if len(s) < 7:
            return None
        i = bisect.bisect_left(self.all, s)
        return self.all[i] if i < len(self.all) and self.all[i].startswith(s) else None

    def files(self, shas):
        """{full sha: [paths]} for commits on main, in one git call."""
        if not shas:
            return {}
        out, cur = {}, None
        for ln in self._git("log", "--no-walk=unsorted", "--stdin", "--format=@%H", "--name-only",
                            "--diff-merges=first-parent", input="\n".join(sorted(shas)) + "\n").splitlines():
            if ln.startswith("@"):
                cur = out.setdefault(ln[1:], [])
            elif ln:
                cur.append(ln)
        return out

    def item_files(self, iid):
        """Paths that any commit naming the item touched."""
        return set(self._git("log", "--fixed-strings", "--grep", iid, "--format=", "--name-only", "HEAD").split("\n"))


def _posix(p):
    p = p.rstrip(":.)]'\"")
    m = re.match(r"^([A-Za-z]):\\(.*)$", p)
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")) if m else p


def cited(text):
    """Local file paths in prose. Only a last segment with an extension names one file; a glob, range or placeholder does
    not."""
    out = []
    for m in _PATH_RX.findall(text or ""):
        p = _posix(m)
        if "." in os.path.basename(p).strip(".") and ".." not in p and not re.search(r"[*?<>{}$]", p):
            out.append(p)
    return out


def _gone(p):
    return not os.path.exists(p) and not any(m in p for m in NOT_HERE)


def window_start(last):
    return _epoch(START) if last is None else _epoch(last["until"]) - OVERLAP_S


def check(events, states, since, until, commits):
    """Pure but for the disk and git. -> {"closes", "code", "no_code", "substance": [row], "form": [row]}."""
    by = {}
    for e in events:
        if e.get("id") and e.get("ts") and e.get("event") in ("close", "verify"):
            by.setdefault(e["id"], []).append(e)
    rows = []
    for iid, evs in sorted(by.items()):
        cl = [e for e in evs if e["event"] == "close"]
        if not cl or states.get(iid) != "done":
            continue
        c = max(cl, key=lambda e: _epoch(e["ts"]))
        if since <= _epoch(c["ts"]) <= until:
            rows.append((iid, c, [e for e in evs if e["event"] == "verify"]))
    code = [(iid, c, (c.get("sha") or "").strip()) for iid, c, _ in rows if not c.get("noCode")]
    full = {iid: commits.full(s) if s and s.upper() != "HEAD" else None for iid, c, s in code}
    files = commits.files({f for f in full.values() if f})
    sha_of = {iid: s for iid, c, s in code}
    substance, form = [], []
    for iid, c, verifies in rows:
        hard, soft = [], []
        if iid in sha_of:
            s, f = sha_of[iid], full[iid]
            if not s or s.upper() == "HEAD":
                hard.append("sha_missing")
            elif f is None:
                hard.append("sha_not_on_main")
            else:
                touched = files.get(f)
                if touched is None:
                    raise Unmeasured("git gave no file list for %s" % f)
                if all(p.startswith(LEDGER) for p in touched):
                    hard.append("sha_only_ledger")
        text = " ".join(str(c.get(k) or "") for k in ("reason", "why"))
        ev_text = text + " " + " ".join(str(v.get("evidence") or "") for v in verifies)
        if any(_gone(p) for p in cited(ev_text)):
            soft.append("evidence_gone")
        if iid in sha_of and not hard:
            named = {p for p in _SRC_RX.findall(text) if p.endswith(SOURCE_EXTS)}
            if named and not named & set(files[full[iid]]) and not named & commits.item_files(iid):
                soft.append("named_source_not_in_commits")
        row = {"item": iid, "sha": sha_of.get(iid) or c.get("sha"), "closed_at": c["ts"]}
        if hard:
            substance.append(dict(row, flags=hard))
        if soft:
            form.append(dict(row, flags=soft))
    return {"closes": len(rows), "code": len(code), "no_code": len(rows) - len(code), "substance": substance, "form": form}


# ---- the outside ----------------------------------------------------------------------------------------------------

def _model():
    sys.path.insert(0, os.path.dirname(HERE))
    from rimflow import model
    return model


def _events():
    return _model().read()


def _states(events):
    return {i: it.state for i, it in _model().replay(events).items.items()}


def _unearned(events, since):
    """Code dones in the window with no level-tagged pass on their sha (close_audit.py's rule): a count, never a finding
    (a close without one is allowed since 2026-11-20)."""
    sys.path.insert(0, os.path.dirname(HERE))
    from rimflow import close_audit
    _, bad, code = close_audit.audit(close_audit.dones(events), _iso(since))
    return {"unearned": len(bad), "of": len(code)}


def reopen(iid, sha, flags, reading):
    """One `fail` run on the closed sha: rimflow reopens the item. -> (rc, output)."""
    argv = [sys.executable, os.path.join(HERE, "cli.py"), "verify", iid, "--seat", "BENCH", "--result", "fail",
            "--config", "close_check (no AI): %s" % ", ".join(flags), "--evidence", reading, "--publish",
            "--why", "the daily close check found a claim of work that main does not hold: %s" % ", ".join(flags)]
    if sha and sha.upper() != "HEAD":
        argv += ["--sha", sha]
    env = dict(os.environ, RIMFLOW_SEAT="BENCH", RM_ROLE_UNIT=os.environ.get("RM_ROLE_UNIT") or UNIT)
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"):     # never a window's session
        env.pop(k, None)
    try:
        r = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, errors="replace",
                           timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    return r.returncode, (r.stdout + r.stderr).strip()


def _load(path):
    """-> the reading, or None when there is none. A file that cannot be read raises Unmeasured."""
    if not os.path.lexists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        _epoch(d["generated"])
        return d
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        raise Unmeasured("%s is unreadable (%s: %s)" % (path, type(e).__name__, str(e)[:100]))  # cut-ok: exception message


def cmd_run(a, fx):
    now = fx.get("now") or time.time()
    last = _load(a.reading)
    since = window_start(last)
    events = (fx.get("events") or _events)()
    if not events:
        raise Unmeasured("the ledger read returned no events")
    res = check(events, (fx.get("states") or _states)(events), since, now, Commits(fx.get("repo") or REPO))
    res.update(generated=_iso(now), since=_iso(since), until=_iso(now), reopened=[], reopen_failed=[],
               unearned=(fx.get("unearned") or _unearned)(events, since))
    if a.apply:
        for r in res["substance"]:
            rc, out = (fx.get("reopen") or reopen)(r["item"], r["sha"], r["flags"], a.reading)
            if rc:
                res["reopen_failed"].append({"item": r["item"], "why": "exit %s: %s" % (rc, out)})
            else:
                res["reopened"].append(r["item"])
        os.makedirs(os.path.dirname(a.reading) or ".", exist_ok=True)
        tmp = "%s.tmp.%d" % (a.reading, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
        os.replace(tmp, a.reading)
    kinds = {}
    for r in res["form"]:
        for k in r["flags"]:
            kinds[k] = kinds.get(k, 0) + 1
    print("closes since %s: %d (%d code, %d no-code); substance %d, form %d %s; unearned dones %s of %s%s"
          % (res["since"], res["closes"], res["code"], res["no_code"], len(res["substance"]), len(res["form"]), kinds,
             res["unearned"]["unearned"], res["unearned"]["of"], "" if a.apply else " (dry: nothing written)"))
    for r in res["substance"]:
        print("  SUBSTANCE %s %s %s" % (r["item"], r["sha"], ", ".join(r["flags"])))
    for r in res["reopen_failed"]:
        print("  REOPEN FAILED %s: %s" % (r["item"], r["why"]))
    return 1 if res["reopen_failed"] else 0


def cmd_fresh(a, fx):
    now = fx.get("now") or time.time()
    d = _load(a.reading)
    if d is None:
        raise Unmeasured("no reading at %s" % a.reading)
    age = now - _epoch(d["generated"])
    if age < -300:      # 5 min of clock skew between the writer and this reader
        raise Unmeasured("the reading %s is dated after now" % d["generated"])
    if age > MAX_AGE_S:
        print("stale: the last check of the closes is from %s, %.1f days ago" % (d["generated"], age / 86400))
        return 1
    print("fresh: %s, %.1f h ago" % (d["generated"], age / 3600))
    return 0


def main(argv=None, fx=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("run", "fresh"):
        s = sub.add_parser(n)
        s.add_argument("--reading", default=os.environ.get("RM_CLOSE_CHECK_READING") or READING)
        if n == "run":
            s.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    try:
        return (cmd_run if a.cmd == "run" else cmd_fresh)(a, fx or {})
    except Unmeasured as e:
        print("UNMEASURED: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
