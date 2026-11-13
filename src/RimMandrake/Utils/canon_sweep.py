#!/usr/bin/env python3
"""canon_sweep.py -- run check_canon.py when canon moves, on every commit, and nightly; findings to the Conductor.

WHY (CANON_BUILD_SWEEP_WHEN_CANON_MOVES)
========================================
check_canon.py ran only as a PreToolUse hook (.claude/hooks/block_canon_contradiction.py) on an agent's own Write/Edit
of a design doc and on an agent's `git commit` naming one. Two holes (GPT r2,
/mnt/d/ClaudeWork/rimmandrake/orphan_homes/r2_answer.md): a commit that reaches origin/main another way (a landing
script, a human, a non-Claude tool) is never checked, and a change to canon.yml itself never re-checks the documents
already on disk, which can contradict the new canon without anyone touching them.

What one run does, in the clone it is run in (the timer runs it in the dispatch clone, which only fast-forwards):

  * canon.yml's bytes differ from the last run  -> FULL sweep of design/**/*.md   (reason canon_moved)
  * check_canon.py changed since the last run   -> FULL sweep                     (reason checker_moved)
  * the last full sweep is older than --nightly-h -> FULL sweep                   (reason nightly)
  * first run, or the last swept sha is gone    -> FULL sweep                     (reason first / base_lost)
  * otherwise                                   -> only the design docs changed in last_sha..HEAD (reason commits)

The open set of contradictions is carried between runs (a commits run replaces only its own files' entries), written
to OUT/latest.json and OUT/findings.md, and every contradiction not yet reported is appended once to the Conductor log,
whose scheduled check (roles/conductor.md step 3b) fixes the doc to canon. A finding that clears and comes back is
reported again. A contradiction is keyed by (path, rule, value found), not line number, so an edit above it does not
re-ring it.

Exit 0 = measured (contradictions are findings, not a unit failure). Exit 2 = UNMEASURED (check_canon could not read
canon, e.g. no PyYAML, or git failed): nothing advances, latest.json says UNMEASURED, and the unit fails loudly.

    python3 src/RimMandrake/Utils/canon_sweep.py run [--full] [--repo R] [--out DIR] [--conductor-log P]
    python3 src/RimMandrake/Utils/canon_sweep.py show
    python3 src/RimMandrake/Utils/selftest_canon_sweep.py
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import conductor_log_guard  # noqa: E402

OUT = os.environ.get("RM_CANON_SWEEP_DIR", "/mnt/d/ClaudeWork/rimmandrake/canon_sweep")
CANON_REL = "infrastructure/state/canon.yml"
CHECKER_REL = "src/RimMandrake/Utils/check_canon.py"
NIGHTLY_H = 20.0
HIT = re.compile(r"^  (?P<path>\S+):(?P<line>\d+)  \[(?P<key>[\w-]+)\] found (?P<found>.+?), canon says (?P<canon>.*)$")
TOTAL = re.compile(r"^(\d+) file\(s\) checked\. (\d+) contradiction\(s\), (\d+) advisory\.")


def now_utc():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def stamp(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout


def file_hash(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


def load(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def decide(repo, state, head, canon_h, now, force, nightly_h):
    """-> (reason, changed_paths or None for a full sweep)."""
    if force:
        return "forced", None
    if not state.get("sha"):
        return "first", None
    if state.get("canon_sha256") != canon_h:
        return "canon_moved", None
    last_full = state.get("last_full")
    try:
        age_h = (now - dt.datetime.strptime(last_full, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=dt.timezone.utc)).total_seconds() / 3600.0
    except (TypeError, ValueError):
        age_h = None
    if age_h is None or age_h >= nightly_h:
        return "nightly", None
    rc, out = git(repo, "diff", "--name-only", state["sha"], head, "--")
    if rc != 0:
        return "base_lost", None
    names = [n for n in out.splitlines() if n]
    if CHECKER_REL in names:
        return "checker_moved", None
    return "commits", sorted(n for n in names if n.startswith("design/") and n.endswith(".md"))


def run_checker(repo, paths):
    """-> (state, hits, files, advisory). paths None = all of design/; [] = nothing to check."""
    if paths == []:
        return "MEASURED", [], 0, 0
    env = dict(os.environ, CLAUDE_PROJECT_DIR=repo)
    cmd = [sys.executable, os.path.join(repo, CHECKER_REL)]
    if paths:
        cmd += [p for p in paths if os.path.exists(os.path.join(repo, p))]
        if len(cmd) == 2:
            return "MEASURED", [], 0, 0       # every changed doc was deleted
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo, env=env, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        return "UNMEASURED: %s" % e, [], 0, 0
    if r.returncode not in (0, 1):
        return "UNMEASURED: check_canon exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()), [], 0, 0
    hits, files, adv, hard_n, section = [], 0, 0, None, None
    for line in r.stdout.splitlines():
        if line.startswith("CONTRADICTS CANON"):
            section = "hard"
        elif line.startswith("advisory"):
            section = "soft"
        m = TOTAL.match(line)
        if m:
            files, hard_n, adv = int(m.group(1)), int(m.group(2)), int(m.group(3))
        m = HIT.match(line)
        if m and section == "hard":
            hits.append({k: m.group(k) for k in ("path", "key", "found", "canon")} | {"line": int(m.group("line"))})
    if hard_n is None or hard_n != len(hits):
        # 🔴 a parse that disagrees with the checker's own total is a blind instrument, not a clean pass
        return "UNMEASURED: parsed %d contradiction(s), check_canon said %s" % (len(hits), hard_n), [], 0, 0
    return "MEASURED", hits, files, adv


def fp(h):
    return "%s|%s|%s" % (h["path"], h["key"], h["found"])


def tell_conductor(log_path, now, reason, new, out_dir):
    conductor_log_guard.refuse_if_test(log_path)
    shown = "; ".join("%s:%d [%s] found %s, canon says %s" % (h["path"], h["line"], h["key"], h["found"], h["canon"])
                      for h in new[:5])
    more = " (+%d more)" % (len(new) - 5) if len(new) > 5 else ""
    line = ("\n%s — CANON SWEEP (%s): %d new contradiction(s) of infrastructure/state/canon.yml: %s%s. List: %s. "
            "Step 3b: fix the doc to canon when it is a wording edit in one file; otherwise file it; an ambiguous "
            "reading goes to the owner on a card.\n" % (stamp(now), reason, len(new), shown, more,
                                                         os.path.join(out_dir, "findings.md")))
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(line)


def write_findings(path, latest):
    rows = ["# canon sweep findings", "",
            "%s · reason %s · head %s · %d file(s) checked this run · %d open contradiction(s)" % (
                latest["at"], latest["reason"], latest["head"][:10], latest["files_checked"], latest["contradictions"]),
            "", "Written by src/RimMandrake/Utils/canon_sweep.py; rules: `python3 src/RimMandrake/Utils/check_canon.py "
            "--list`.", ""]
    for h in latest["open"]:
        rows.append("- `%s:%d` [%s] found %s, canon says %s" % (h["path"], h["line"], h["key"], h["found"], h["canon"]))
    if not latest["open"]:
        rows.append("No design doc contradicts canon.")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")


def run(repo, out_dir, log_path, force=False, nightly_h=NIGHTLY_H, now=None):
    now = now or now_utc()
    os.makedirs(out_dir, exist_ok=True)
    state_p, latest_p = os.path.join(out_dir, "state.json"), os.path.join(out_dir, "latest.json")
    state = load(state_p, {})
    rc, head = git(repo, "rev-parse", "HEAD")
    head = head.strip()
    canon_h = file_hash(os.path.join(repo, CANON_REL))
    if rc != 0 or not head or canon_h is None:
        why = "git rev-parse HEAD failed" if rc != 0 or not head else "%s unreadable" % CANON_REL
        save(latest_p, {"at": stamp(now), "state": "UNMEASURED: " + why, "repo": repo})
        print("canon_sweep: UNMEASURED: %s" % why, file=sys.stderr)
        return 2
    reason, changed = decide(repo, state, head, canon_h, now, force, nightly_h)
    status, hits, files, adv = run_checker(repo, changed)
    if status != "MEASURED":
        save(latest_p, dict(load(latest_p, {}), at=stamp(now), state=status, reason=reason, head=head))
        print("canon_sweep: %s" % status, file=sys.stderr)
        return 2
    prev_open = state.get("open") or []
    if changed is None:
        open_ = hits
    else:
        scope = set(changed)
        open_ = [h for h in prev_open if h["path"] not in scope] + hits
    open_.sort(key=lambda h: (h["path"], h["line"], h["key"]))
    reported = set(state.get("reported") or [])
    new = [h for h in open_ if fp(h) not in reported]
    told = None
    if new:
        try:
            tell_conductor(log_path, now, reason, new, out_dir)
            told = log_path
        except OSError as e:
            told = "FAILED: %s" % e
    latest = {"at": stamp(now), "state": "MEASURED", "reason": reason, "head": head, "repo": repo,
              "files_checked": files, "advisory": adv, "changed": changed, "contradictions": len(open_),
              "open": open_, "new": new, "told": told}
    save(latest_p, latest)
    write_findings(os.path.join(out_dir, "findings.md"), latest)
    if told and told.startswith("FAILED"):
        keep_reported = sorted(reported & {fp(h) for h in open_})   # unsent findings ring again next run
    else:
        keep_reported = sorted({fp(h) for h in open_})
    save(state_p, {"sha": head, "canon_sha256": canon_h, "reported": keep_reported, "open": open_,
                   "last_full": stamp(now) if changed is None else state.get("last_full"),
                   "last_reason": reason})
    print("canon_sweep: %s, %d file(s) checked, %d open contradiction(s), %d new%s" % (
        reason, files, len(open_), len(new), (" -> " + told) if told else ""))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--full", action="store_true", help="sweep every design doc whatever moved")
    r.add_argument("--repo", default=REPO)
    r.add_argument("--out", default=OUT)
    r.add_argument("--conductor-log", default=conductor_log_guard.LIVE)
    r.add_argument("--nightly-h", type=float, default=NIGHTLY_H)
    s = sub.add_parser("show")
    s.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    if a.cmd == "show":
        latest = load(os.path.join(a.out, "latest.json"), None)
        if latest is None:
            print("canon_sweep: no reading at %s" % a.out)
            return 2
        print("%s %s reason=%s files=%s contradictions=%s" % (latest.get("at"), latest.get("state"), latest.get(
            "reason"), latest.get("files_checked"), latest.get("contradictions")))
        return 0 if latest.get("state") == "MEASURED" else 2
    return run(os.path.abspath(a.repo), a.out, a.conductor_log, a.full, a.nightly_h)


if __name__ == "__main__":
    sys.exit(main())
