#!/usr/bin/env python3
"""Land a seat's helpers' `submit/<seat>/*` refs onto origin/main (plan §2.1/§2.2, Phase 7).

    land_submissions.py [--seat S] [--clone PATH] [--dry-run] [NAME ...]

Owner's ruling (by card): each seat lands its own helpers' work; helpers push
`submit/<seat>/<name>` (worktree_pool.py submit) and never push main.

Per submission: fetch -> rebase onto origin/main (`git replay --ref-action=print` on a throwaway branch, which needs no checkout, so the
seat's own working tree is never touched) -> `push --atomic origin <new>:main` together with the
deletion of the submit ref (leased on the sha we landed, so a newer re-submission is never
deleted) -> record `refs/landed/<seat>/<name>` = the submitted sha, so the pool recycles that slot
as landed even though rebasing changed its commit ids. Already-landed submissions are only
cleaned up. A push that fails or times out is resolved with `merge-base --is-ancestor <new>
origin/main` before any retry (it may have landed). A conflict leaves the submit ref in place and
is reported; nothing is ever force-pushed. Prints `LANDED <name> <sha>` per submission.
"""
import argparse
import os
import subprocess
import sys

SEAT_ROOT = os.path.realpath(os.environ.get("RM_SEAT_ROOT", "/home/mandrake/rm"))
RETRIES = 3


def run(clone, *args, check=True, timeout=180):
    p = subprocess.run(["git", "-C", clone, *args], capture_output=True, text=True, timeout=timeout)
    if check and p.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr.strip()))
    return p


def ok(clone, *args):
    return run(clone, *args, check=False).returncode == 0


def fetch(clone, seat):
    run(clone, "fetch", "-q", "--prune", "origin", "+refs/heads/main:refs/remotes/origin/main",
        "+refs/heads/submit/%s/*:refs/remotes/origin/submit/%s/*" % (seat, seat))


def landed_on_main(clone, sha):
    return ok(clone, "merge-base", "--is-ancestor", sha, "refs/remotes/origin/main")


def record_landed(clone, seat, name, sha):
    run(clone, "update-ref", "refs/landed/%s/%s" % (seat, name), sha)


def delete_submit(clone, seat, name, sha, dry):
    ref = "refs/heads/submit/%s/%s" % (seat, name)
    if dry:
        return True
    p = run(clone, "push", "-q", "--force-with-lease=%s:%s" % (ref, sha), "origin", ":" + ref, check=False)
    return p.returncode == 0


def land_one(clone, seat, name, dry):
    tracking = "refs/remotes/origin/submit/%s/%s" % (seat, name)
    sha = run(clone, "rev-parse", tracking).stdout.strip()
    if landed_on_main(clone, sha):
        record_landed(clone, seat, name, sha)
        delete_submit(clone, seat, name, sha, dry)
        print("LANDED %s %s (already on origin/main; submit ref deleted)" % (name, sha))
        return True
    files = run(clone, "diff", "--name-only", "refs/remotes/origin/main...%s" % sha).stdout.split()
    dlls = [f for f in files if f.lower().endswith(".dll")]
    if dlls:
        print("REFUSED %s: carries DLLs %s — slots never commit DLLs" % (name, dlls), file=sys.stderr)
        return False
    for attempt in range(1, RETRIES + 1):
        main = run(clone, "rev-parse", "refs/remotes/origin/main").stdout.strip()
        base = run(clone, "merge-base", main, sha).stdout.strip()
        if base == main:
            new = sha
        else:
            # replay only reports refs/heads/*, and its default --ref-action is `update`: replay a
            # throwaway local branch in print mode, so no ref the seat cares about moves.
            tmp = "refs/heads/land-tmp/%s/%s" % (seat, name)
            run(clone, "update-ref", tmp, sha)
            try:
                p = run(clone, "replay", "--ref-action=print", "--onto", main, "%s..%s" % (base, tmp),
                        check=False)
            finally:
                run(clone, "update-ref", "-d", tmp, check=False)
            line = [l for l in p.stdout.splitlines() if l.startswith("update %s " % tmp)]
            if p.returncode != 0 or not line:
                print("CONFLICT %s %s: does not rebase cleanly onto origin/main %s — rebase it in the "
                      "slot (worktree_pool.py submit) or by hand; submit ref left in place. %s"
                      % (name, sha, main[:10], p.stderr.strip()[:300]), file=sys.stderr)
                return False
            new = line[-1].split()[2]
        if dry:
            print("DRY-RUN would land %s %s as %s on %s" % (name, sha, new, main[:10]))
            return True
        ref = "refs/heads/submit/%s/%s" % (seat, name)
        try:
            p = run(clone, "push", "-q", "--atomic", "--force-with-lease=%s:%s" % (ref, sha), "origin",
                    "%s:refs/heads/main" % new, ":" + ref, check=False)
            pushed = p.returncode == 0
            err = p.stderr.strip()
        except subprocess.TimeoutExpired:
            pushed, err = False, "push timed out"
        fetch(clone, seat)
        if pushed or landed_on_main(clone, new):   # ambiguity check before any retry
            record_landed(clone, seat, name, sha)
            if not pushed:
                delete_submit(clone, seat, name, sha, dry)
            print("LANDED %s %s -> %s" % (name, sha, new))
            return True
        print("push of %s rejected (attempt %d/%d): %s" % (name, attempt, RETRIES, err[:300]),
              file=sys.stderr)
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("names", nargs="*")
    ap.add_argument("--seat")
    ap.add_argument("--clone")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    clone = a.clone
    if not clone:
        top = run(os.getcwd(), "rev-parse", "--show-toplevel", check=False).stdout.strip()
        common = run(os.getcwd(), "rev-parse", "--path-format=absolute", "--git-common-dir",
                     check=False).stdout.strip()
        clone = os.path.dirname(common) if common.endswith("/.git") else top
    if not clone:
        print("run inside a seat clone or pass --clone", file=sys.stderr)
        return 2
    seat = (a.seat or os.environ.get("AGENT_SEAT") or os.path.basename(clone)).lower()
    fetch(clone, seat)
    refs = run(clone, "for-each-ref", "--format=%(refname)",
               "refs/remotes/origin/submit/%s/" % seat).stdout.split()
    names = [r.split("/", 5)[5] for r in refs]
    if a.names:
        names = [n for n in names if n in a.names]
    if not names:
        print("nothing to land: no submit/%s/* refs on origin" % seat)
        return 0
    bad = [n for n in names if not land_one(clone, seat, n, a.dry_run)]
    print("%d/%d submissions landed%s" % (len(names) - len(bad), len(names),
                                           "; NOT landed: " + ", ".join(bad) if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
