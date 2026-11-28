#!/usr/bin/env python3
"""fresh_reader.py: the run that fixes code files the fresh reader of its fix; the ticket lane launches the reader.

Page design/specs/2026-11-26-fresh-reader-ticket/boundary.md; selftest selftest_fresh_reader.py. Item
RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX, part 7. His answer by card, 2026-11-26: "The fixing run files it
(Recommended)": a binding rule in every brief; the run files the reader as a ticket, and the ticket lane launches the
reader. Why: 5 of 6 fresh-reader runs in the 7 days to 2026-11-26 were launched by hand.

    python3 src/RimMandrake/rimflow/fresh_reader.py file --fix <sha> <path>...   the fixing run, before it ends
                                                    (a file with a review record already, FLAGGED included, is left out;
                                                    so is a file that a reader ticket of this fix names: exit 0)
    python3 src/RimMandrake/rimflow/fresh_reader.py holds <sha> <path>...        the ticket's outcome check

The ticket's check holds when each fixed file carries a review record: `code_review_status.py mark-clean` on its
present bytes, or a flag (`flag`, when the reader found and fixed something; or a flag from before the fix, since nobody
reviews a FLAGGED file again). The lane's brief for it names the fixed files, their
boundary pages and tests, and never the diff of the fix or the findings that led to it.
"""
import argparse
import hashlib
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


def twin_id(sha, paths):
    """-> the id of a second reader ticket of one fix: the files that the fix's own ticket does not name. The id keys on
    the files, so the same files give the same twin (a numbered `_2` does not parse: numbered ids are retired)."""
    h = hashlib.sha1("\n".join(sorted(paths)).encode("utf-8")).hexdigest()[:6].upper()
    return "RIMMANDRAKE_READ_FIX_%s_%s_WITH_FRESH_EYES" % (re.sub(r"[^0-9A-Fa-f]", "", str(sha))[:10].upper(), h)


def resolve(sha, paths, tickets):
    """-> (id, rest). tickets: {id: [path]} of the reader tickets that exist, in any state. rest is the paths that no
    reader ticket of this fix names; id is the ticket to file them under (the fix's id, or its twin when that id is
    taken), or, when rest is empty, the ticket that names them (nothing to file: a second filing is not a refusal)."""
    base = ticket_id(sha)
    fam = sorted(i for i in tickets or {} if i == base or (i.startswith(base[:-len("_WITH_FRESH_EYES")] + "_")
                                                           and i.endswith("_WITH_FRESH_EYES")))
    named = {p for i in fam for p in tickets[i] or []}
    rest = [p for p in paths if p not in named]
    if not rest:
        return next((i for i in fam if set(paths) & set(tickets[i] or [])), base), []
    return (base if base not in (tickets or {}) else twin_id(sha, rest)), rest


def reader_tickets():
    """-> {id: [path]} of every reader ticket in this repo's ledger, in any state. Raises when the ledger cannot be read."""
    import model
    return {i: parse_title(x.title)[0] for i, x in model.replay(model.read()).items.items() if is_reader(x)}


def file_argv(sha, paths, maker, seat="BENCH", tid=None):
    """-> the `rimflow file` line the fixing run runs (exactly one ticket per fix; `tid` names its twin, `resolve`)."""
    return filing_argv(tid or ticket_id(sha), title(sha, paths, maker), effect(sha, paths), NOT_NOW,
                       "the fixing run files the fresh reader of its fix (his card, 2026-11-26)", seat)


def filing_argv(tid, title_text, check, not_now, why, seat="BENCH"):
    """Build the ledger filing command shared by a fresh reread and a blind machinery review."""
    return [sys.executable, os.path.join(HERE, "cli.py"), "file", tid, "--for", "BENCH",
            "--title", title_text, "--effect", check, "--not-now", not_now, "--seat", seat, "--why", why, "--publish"]


def is_reader(it):
    return str((it or {}).get("title") if isinstance(it, dict) else getattr(it, "title", "") or "").startswith(PREFIX)


def parse_title(t):
    """-> (paths, sha, maker) from a reader ticket's title."""
    m = re.match(re.escape(PREFIX) + r"(.+) at ([0-9a-f]{7,40}) \(made by (.+?); the reader is never that run\)",
                 str(t or ""))    # the maker may hold a space: `file` names a window with no unit "a window"
    if not m:
        return [], None, None
    return [p.strip() for p in m.group(1).split(",") if p.strip()], m.group(2), m.group(3)


def pages(paths, runner=None):
    """-> {path: (page or None, tests or None, state)} from code_review_status.page_states."""
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
Publish the changed review record shard under `infrastructure/state/code_review/` before closing the reader ticket.
""".format(maker=maker or "unknown", sha=sha or "?", rows="\n".join(rows) or "   (the title names no file)")


def flag_kind(rel):
    """-> "present" when `rel` is FLAGGED now and the flag was made on its present bytes, "older" when it is FLAGGED on
    older bytes (flagged before a later fix changed it), None when it is not flagged. Raises when the flags cannot be
    read. `check --record` reads DIRTY on a FLAGGED file (selftest_code_review_page_state.py pins it), so the flag is
    read here."""
    import code_review_status as CRS
    path = rel if os.path.isabs(rel) else os.path.join(REPO, rel)    # as `check --record` reads it: cwd=REPO
    try:
        rec = CRS.flags().get(CRS.canonical_rel(CRS.repo_rel(path)))
    except CRS.FlagsUnreadable as e:
        raise OSError(str(e))
    if not rec:
        return None
    return "present" if rec.get("sha256") is not None and rec.get("sha256") == CRS.file_hash(rec["path"]) else "older"


def flagged_on_bytes(rel):
    """-> True when `rel` is FLAGGED now and the flag was made on its present bytes."""
    return flag_kind(rel) == "present"


def holds(sha, paths, runner=None, flagged=None):
    """-> 0 when each path has a review record (READ-CLEAN on its present bytes, or FLAGGED: on its present bytes, or
    before a later fix, since nobody reviews a FLAGGED file again), 1 when one lacks it, 2 when it could not be read."""
    import time_budget
    run = runner or (lambda argv: subprocess.run(argv, cwd=REPO, capture_output=True, text=True,
                                                 timeout=time_budget.CALL_S))
    # a flag on older bytes holds too: a file FLAGGED before a later fix is never reviewed again (code_review.md, "If
    # you are the reader of a FLAGGED file, stop"); its weekly examination reads it
    is_flagged = flagged or flag_kind
    worst = 0
    for p in paths:
        try:
            r = run([sys.executable, CRS, "check", "--record", p])
        except (OSError, subprocess.SubprocessError) as e:
            print("could not look: %s: %s" % (p, e))
            worst = 2
            continue
        out = (r.stdout or "").strip()
        if r.returncode == 0:
            print(out or "could not look: %s printed nothing (rc 0)" % p)
            worst = max(worst, 0 if out else 2)
            continue
        try:
            k = is_flagged(p)
            if k:
                print("FLAGGED  %s  (%s)" % (p, "a flag on its present bytes: the reader found and fixed" if k is True
                                             or k == "present" else "flagged on older bytes, before a later fix: nobody "
                                             "reviews it again; the weekly examination reads it"))
                continue
        except Exception as e:  # noqa: BLE001 - flags that cannot be read leave the answer unknown, never DIRTY
            print(out or "could not look: %s printed nothing (rc %s)" % (p, r.returncode))
            print("could not look: the flags of %s: %s" % (p, e))
            worst = 2
            continue
        print(out or "could not look: %s printed nothing (rc %s)" % (p, r.returncode))
        worst = max(worst, 1 if out.startswith(("DIRTY", "STALE", "OPEN")) or (r.returncode == 1 and out) else 2)
    return worst


def owed_paths(sha, paths, holds_fn=None):
    """-> the paths that still owe a fresh read: those whose `holds` is not 0. A file READ-CLEAN on its present bytes, or
    FLAGGED (nobody reviews it again), owes none, and a ticket for it is refused by the filing gate (its check holds)."""
    return [p for p in paths if (holds_fn or holds)(sha, [p]) != 0]


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
    owed = owed_paths(a.fix, a.paths)
    if not owed:
        print("no reader owed: each file already has a review record (READ-CLEAN on its bytes, or FLAGGED: nobody "
              "reviews it again); nothing filed")
        return 0
    try:
        tickets = reader_tickets()
    except Exception as e:  # noqa: BLE001 - the filing goes on under the fix's id; rimflow itself refuses a taken name
        print("could not read the reader tickets (%s: %s); filing under the fix's own id" % (type(e).__name__, e))
        tickets = {}
    tid, owed = resolve(a.fix, owed, tickets)
    if not owed:
        print("already filed: %s names each file; nothing filed" % tid)
        return 0
    argv = file_argv(a.fix, owed, a.maker, tid=tid)
    print(" ".join(argv[1:3]) + " " + tid)
    return subprocess.run(argv, cwd=REPO, timeout=6 * 3600).returncode    # budget: danger=a publish that never returns; longest=1800s (a publish in the door's line, 2026-11-26)


if __name__ == "__main__":
    sys.exit(main())
