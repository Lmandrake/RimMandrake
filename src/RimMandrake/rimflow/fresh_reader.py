#!/usr/bin/env python3
"""fresh_reader.py: the run that fixes code files the fresh reader of its fix; the ticket lane launches the reader.

Page design/specs/2026-11-26-fresh-reader-ticket/boundary.md; selftest selftest_fresh_reader.py. Item
RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX, part 7. His answer by card, 2026-11-26: "The fixing run files it
(Recommended)": a binding rule in every brief; the run files the reader as a ticket, and the ticket lane launches the
reader. Why: 5 of 6 fresh-reader runs in the 7 days to 2026-11-26 were launched by hand.

    python3 src/RimMandrake/rimflow/fresh_reader.py file --fix <sha> <path>...   the fixing run, before it ends
    python3 src/RimMandrake/rimflow/fresh_reader.py holds <sha> <path>...        the ticket's outcome check

The ticket's check holds when each fixed file carries a review record on its present bytes (`code_review_status.py
mark-clean`, or `flag` when the reader found and fixed something). The lane's brief for it names the fixed files, their
boundary pages and tests, and never the diff of the fix or the findings that led to it.
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PREFIX = "Fresh read of a fix: "
CRS = os.path.join(REPO, "src", "RimMandrake", "Utils", "code_review_status.py")
PAGE_RX = re.compile(r"(design/specs/[^\s:()]+/boundary\.md)")
TESTS_RX = re.compile(r"((?:src|infrastructure|\.claude)/[^\s:(),]*selftest_[^\s:(),]+\.py)")
NOT_NOW = ("independent: the fresh reader of a fix is a run that did not make it "
           "(CLAUDE.md §Code is clean when its promises are tested)")


def ticket_id(sha):
    return "RIMMANDRAKE_READ_FIX_%s_WITH_FRESH_EYES" % re.sub(r"[^0-9A-Fa-f]", "", str(sha))[:10].upper()


def effect(sha, paths):
    return "cmd:python3 src/RimMandrake/rimflow/fresh_reader.py holds %s %s" % (sha, " ".join(paths))


def title(sha, paths, maker):
    return "%s%s at %s (made by %s; the reader is never that run)" % (PREFIX, ", ".join(paths), sha, maker or "unknown")


def file_argv(sha, paths, maker, seat="BENCH"):
    """-> the `rimflow file` line the fixing run runs (exactly one ticket per fix)."""
    return [sys.executable, os.path.join(HERE, "cli.py"), "file", ticket_id(sha), "--for", "BENCH",
            "--title", title(sha, paths, maker), "--effect", effect(sha, paths), "--not-now", NOT_NOW,
            "--seat", seat, "--why", "the fixing run files the fresh reader of its fix (his card, 2026-11-26)", "--publish"]


def is_reader(it):
    return str((it or {}).get("title") if isinstance(it, dict) else getattr(it, "title", "") or "").startswith(PREFIX)


def parse_title(t):
    """-> (paths, sha, maker) from a reader ticket's title."""
    m = re.match(re.escape(PREFIX) + r"(.+) at ([0-9a-f]{7,40}) \(made by (\S+?);", str(t or ""))
    if not m:
        return [], None, None
    return [p.strip() for p in m.group(1).split(",") if p.strip()], m.group(2), m.group(3)


def pages(paths, runner=None):
    """-> {path: (page or None, tests or None)} from code_review_status.page_states."""
    try:
        import code_review_status as CR
        states = CR.page_states(paths) if runner is None else runner(paths)
    except Exception:       # noqa: BLE001 - the brief then says the page could not be read, never "none"
        states = [("UNREADABLE", p, "code_review_status could not be read") for p in paths]
    out = {}
    for state, rel, detail in states:
        pg, ts = PAGE_RX.search(detail or ""), TESTS_RX.search(detail or "")
        out[rel] = (pg.group(1) if pg else None, ts.group(1) if ts else None, state)
    return out


def brief_block(it, runner=None):
    """-> the reader part of the lane's Work brief for a reader ticket."""
    paths, sha, maker = parse_title(it.get("title") if isinstance(it, dict) else getattr(it, "title", ""))
    pg = pages(paths, runner)
    rows = []
    for p in paths:
        page, tests, state = pg.get(p, (None, None, "UNREADABLE"))
        rows.append("   - %s; its page: %s; its tests: %s (%s)" % (p, page or "no page reads it (NO PAGE or could not "
                                                                     "look)", tests or "none named", state))
    return """
You are the FRESH READER of a fix (CLAUDE.md §Code is clean when its promises are tested). You are not {maker}, the run
that made the fix. Read only these, as they stand on origin/main:
{rows}
Do NOT read the diff of the fix (no `git show`, `git diff` or `git log -p` of {sha}) and do NOT read the findings, notes
or tickets that led to it: judge each file against its page and its tests. Read each file once.
- Nothing significant: `python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path>` for each file.
- A significant finding (measured, or a concrete case: this input, this wrong result): write a test and see it fail,
  fix, see it pass, then `python3 src/RimMandrake/Utils/code_review_status.py flag <path> --why "..."`. There is no
  third read. A nit goes on the page's polish.md, never a ticket.
""".format(maker=maker or "unknown", sha=sha or "?", rows="\n".join(rows) or "   (the title names no file)")


def holds(sha, paths, runner=None):
    """-> 0 when each path has a review record on its present bytes (READ-CLEAN or FLAGGED), 1 when one lacks it,
    2 when the record could not be read."""
    import time_budget
    run = runner or (lambda argv: subprocess.run(argv, cwd=REPO, capture_output=True, text=True,
                                                 timeout=time_budget.CALL_S))
    worst = 0
    for p in paths:
        try:
            r = run([sys.executable, CRS, "check", "--record", p])
        except (OSError, subprocess.SubprocessError) as e:
            print("could not look: %s: %s" % (p, e))
            worst = 2
            continue
        out = (r.stdout or "").strip()
        print(out or "could not look: %s printed nothing (rc %s)" % (p, r.returncode))
        if r.returncode == 0 or out.startswith("FLAGGED"):
            continue
        worst = max(worst, 1 if out.startswith(("DIRTY", "STALE", "OPEN")) or r.returncode == 1 else 2)
    return worst


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("file")
    f.add_argument("--fix", required=True, help="the published sha of the fix")
    f.add_argument("--maker", default=os.environ.get("RM_ROLE_UNIT") or os.environ.get("RM_DETACHED_UNIT") or "a window")
    f.add_argument("paths", nargs="+")
    h = sub.add_parser("holds")
    h.add_argument("sha")
    h.add_argument("paths", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "holds":
        return holds(a.sha, a.paths)
    argv = file_argv(a.fix, a.paths, a.maker)
    print(" ".join(argv[1:3]) + " " + ticket_id(a.fix))
    return subprocess.run(argv, cwd=REPO, timeout=6 * 3600).returncode    # budget: danger=a publish that never returns; longest=1800s (a publish in the door's line, 2026-11-26)


if __name__ == "__main__":
    sys.exit(main())
