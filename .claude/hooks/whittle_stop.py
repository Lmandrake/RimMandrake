#!/usr/bin/env python3
"""Whittle's Stop hook: the session is asked to keep working until its files show the work is done, with evidence.

Claude Code runs this when the agent tries to end a turn. It reads the hook JSON on stdin and either prints nothing
(the turn ends) or prints {"decision": "block", "reason": ...}, which hands the reason back to the agent as its next
instruction.

Armed only in a session started with WHITTLE=1 in its environment, in a project with <project>/whittle/STATEMENT.md.
Other sessions in the same project are untouched. While armed, a turn may end only when one of these holds:

  whittle/STOP exists            the owner's off switch. Stays until deleted.
  whittle/BLOCKED.md has text    the agent's way out ("I'm blocked, here's why", or a question for the owner). Filed in
                                 whittle/history/ and the hook re-arms, so one blocked stop doesn't disarm the session.
  the claim is complete          DONE.md has one "true" line per statement bullet; every evidence file it names is a
                                 regular file inside the project and newer than the last change to the project's files;
                                 BROADEN.md has text; JUDGE.md is newer than DONE.md and every evidence file and ends
                                 with the line "would show: yes"; NOTES.md is not newer than DONE.md.
  refusals ran out               LOOP_LIMIT refusals in a row with the same problems and no change to the project. The
                                 turn ends and whittle/STALLED.md says so. A stop the agent makes on its own (not one
                                 driven by this hook, per Claude Code's stop_hook_active) starts the count again.

What it checks is files, not behaviour: who wrote JUDGE.md or BROADEN.md, and whether the evidence shows anything, it
cannot tell. Freshness is by modification time (directories included, so deletions count); an edit that preserves
mtimes is invisible to it. Any unexpected error blocks with the error as the reason, under the same refusal limit.

Stdlib only. Optional settings: WHITTLE_DIR, WHITTLE_LOOP_LIMIT, WHITTLE_NEED_JUDGE=0, WHITTLE_NEED_BROADEN=0.
"""
import json
import os
import re
import subprocess
import sys
import time

ARM = "WHITTLE"
VERDICT = re.compile(r"^\s*[-*]\s*(true|false|unseen|cannot tell)\s*:\s*(.+)$", re.I)
EVIDENCE = re.compile(r"\|\s*evidence\s*:(.*)$", re.I)
BACKTICK = re.compile(r"`([^`]+)`")
HIDDEN = re.compile(r"<!--.*?-->|^(```|~~~).*?^\1[^\n]*$", re.S | re.M)


def settings():
    work = os.path.normpath(os.environ.get("WHITTLE_DIR", "whittle")).replace("\\", "/").strip("/")
    if not work or work.startswith("..") or os.path.isabs(work):
        raise ValueError("WHITTLE_DIR must be a folder inside the project, got %r" % os.environ.get("WHITTLE_DIR"))
    limit = int(os.environ.get("WHITTLE_LOOP_LIMIT", "3"))
    return work, max(limit, 1), os.environ.get("WHITTLE_NEED_JUDGE", "1") != "0", \
        os.environ.get("WHITTLE_NEED_BROADEN", "1") != "0"


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def has_text(path):
    return os.path.isfile(path) and read(path).strip() != ""


def statement_lines(path):
    """The frozen statement's bullet lines ('- ...' or '* ...'), outside comments and code fences."""
    return [norm(m.group(1)) for m in re.finditer(r"^\s*[-*]\s+(.+)$", HIDDEN.sub("", read(path)), re.M)]


def mtime(path):
    try:
        return os.stat(path).st_mtime
    except OSError:
        return None


def project_files(root):
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-co", "--exclude-standard", "-z"],
                             capture_output=True, timeout=30, check=True).stdout
        return [os.fsdecode(f) for f in out.split(b"\0") if f]
    except (OSError, subprocess.SubprocessError):
        files = []
        for d, dirs, names in os.walk(root):
            dirs[:] = [x for x in dirs if x != ".git"]
            files += [os.path.relpath(os.path.join(d, n), root).replace(os.sep, "/") for n in names]
        return files


def last_change(root, work):
    """Newest mtime among the project's files and their folders, outside the Whittle folder. A folder's mtime moves
    when a file in it is added, deleted or renamed, so a deletion counts as a change."""
    skip = work + "/"
    paths = set()
    for f in project_files(root):
        if (f + "/").startswith(skip):
            continue
        paths.add(f)
        d = os.path.dirname(f)
        while d:
            paths.add(d)
            d = os.path.dirname(d)
    times = [mtime(os.path.join(root, p)) for p in paths] + [mtime(root)]
    return max([t for t in times if t is not None], default=0.0)


def evidence_problem(root, rel):
    """None if `rel` names a regular file inside the project, else what is wrong with it."""
    if os.path.isabs(rel) or re.match(r"^[A-Za-z]:", rel):
        return "'%s' is an absolute path; name evidence relative to the project" % rel
    real_root = os.path.realpath(root)
    real = os.path.realpath(os.path.join(root, rel))
    if os.path.commonpath([real_root, real]) != real_root:
        return "'%s' points outside the project" % rel
    if not os.path.isfile(real):
        return "'%s' is not a file that exists" % rel
    return None


def done_problems(root, work, need_judge, need_broaden):
    """Everything standing between this session and a finished turn. Empty means the claim is complete."""
    w = lambda name: os.path.join(root, work, name)
    wanted = statement_lines(w("STATEMENT.md"))
    if not wanted:
        return ["%s/STATEMENT.md has no bullet lines ('- ...'), so there is nothing to check a claim against. Ask the "
                "owner to fix it: write %s/BLOCKED.md and stop." % (work, work)]
    if not os.path.isfile(w("DONE.md")):
        return ["There is no %s/DONE.md yet. Keep working. When you would show this to the owner, write it: one line per "
                "statement bullet, '- true: <the bullet, copied> | evidence: `path` `path`', naming saved evidence files."
                % work]
    rows, problems = {}, []
    for line in HIDDEN.sub("", read(w("DONE.md"))).splitlines():
        m = VERDICT.match(line)
        if not m:
            continue
        text, ev = m.group(2), ""
        e = EVIDENCE.search(text)
        if e:
            text, ev = text[:e.start()], e.group(1)
        key = norm(text)
        if key in rows:
            problems.append("DONE.md has two verdict lines for '%s'. Keep one." % key)
        rows[key] = (m.group(1).lower(), BACKTICK.findall(ev))
    changed = last_change(root, work)
    evidence_times = []
    for line in wanted:
        if line not in rows:
            problems.append("DONE.md has no verdict line for the statement bullet '%s'. Copy the bullet exactly." % line)
            continue
        verdict, paths = rows[line]
        if verdict != "true":
            problems.append("'%s' is marked %s. Make it true, or write %s/BLOCKED.md saying why you can't." % (line, verdict, work))
            continue
        if not paths:
            problems.append("'%s' names no evidence (put paths in backticks after '| evidence:')." % line)
            continue
        for p in paths:
            bad = evidence_problem(root, p)
            if bad:
                problems.append("Evidence for '%s': %s." % (line, bad))
                continue
            t = mtime(os.path.join(root, p))
            evidence_times.append(t)
            if t < changed:
                problems.append("The evidence '%s' for '%s' is older than your last change to the project. Look again "
                                "and save fresh evidence." % (p, line))
    done_t = mtime(w("DONE.md"))
    notes_t = mtime(w("NOTES.md"))
    if notes_t and notes_t > done_t:
        problems.append("The owner's notes (%s/NOTES.md) changed after DONE.md was written. Reread them, act on them, and "
                        "write DONE.md again." % work)
    if need_broaden and not has_text(w("BROADEN.md")):
        problems.append("No %s/BROADEN.md. Ask a different model what a real user would try that you haven't, try the "
                        "most revealing one or two, and write the question, the answer and what you found there." % work)
    if need_judge:
        judge_t = mtime(w("JUDGE.md"))
        if not os.path.isfile(w("JUDGE.md")) or judge_t < max([done_t] + evidence_times):
            problems.append("No judge's verdict newer than DONE.md and the evidence. Spawn a fresh subagent (not a fork) "
                            "with %s/JUDGE_PROMPT.md as its whole brief. It writes %s/JUDGE.md." % (work, work))
        else:
            lines = [l.strip().lower() for l in read(w("JUDGE.md")).splitlines() if l.strip()]
            if not lines or lines[-1] != "would show: yes":
                problems.append("The judge (%s/JUDGE.md) would not show this yet: its last line is not 'would show: yes'. "
                                "Work on what it found." % work)
    return problems


def remember(state, session, fingerprint, active):
    """Count identical refusals in a row for this session. Returns the count including this one."""
    try:
        old = json.loads(read(state))
        old = old if isinstance(old, dict) else {}
    except (OSError, ValueError):
        old = {}
    mine = old.get(session) if isinstance(old.get(session), dict) else {}
    count = int(mine.get("count", 0)) + 1 if active and mine.get("fingerprint") == fingerprint else 1
    old[session] = {"fingerprint": fingerprint, "count": count}
    tmp = state + ".%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(old, f)
    os.replace(tmp, state)
    return count


def stamp():
    return time.strftime("%Y-%m-%dT%H%M%S") + "_%d" % (time.time_ns() % 10 ** 9)


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        event = {}
    if os.environ.get(ARM) != "1":
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    try:
        work, limit, need_judge, need_broaden = settings()
    except ValueError as e:
        block("Whittle's hook is misconfigured: %s. Write BLOCKED.md for the owner and stop." % e)
        return 0
    wdir = os.path.join(root, work)
    if not os.path.isfile(os.path.join(wdir, "STATEMENT.md")) or os.path.exists(os.path.join(wdir, "STOP")):
        return 0
    blocked = os.path.join(wdir, "BLOCKED.md")
    if os.path.isfile(blocked):
        try:
            ok = has_text(blocked)
        except (OSError, UnicodeDecodeError):
            ok = os.path.getsize(blocked) > 0
        if ok:
            os.makedirs(os.path.join(wdir, "history"), exist_ok=True)
            os.replace(blocked, os.path.join(wdir, "history", "BLOCKED_%s.md" % stamp()))
            return 0
    try:
        problems = done_problems(root, work, need_judge, need_broaden)
        changed = last_change(root, work)
    except Exception as e:                                     # never let an error silently end the turn
        problems, changed = ["The hook could not read the claim (%s: %s). Fix the file it names." % (type(e).__name__, e)], 0
    if not problems:
        return 0
    fingerprint = "\n".join(problems) + "|%r" % changed
    count = remember(os.path.join(wdir, ".stop_state.json"), str(event.get("session_id", "")), fingerprint,
                     bool(event.get("stop_hook_active")))
    if count > limit:
        with open(os.path.join(wdir, "STALLED.md"), "a", encoding="utf-8") as f:
            f.write("%s: the hook let the turn end after %d refusals in a row with nothing changed.\n%s\n\n"
                    % (stamp(), limit, "\n".join("- " + p for p in problems)))
        return 0
    block("Whittle: not done yet.\n" + "\n".join("- " + p for p in problems) +
          "\nIf you truly can't go on, or need the owner, write %s/BLOCKED.md saying why, then stop." % work)
    return 0


if __name__ == "__main__":
    sys.exit(main())
