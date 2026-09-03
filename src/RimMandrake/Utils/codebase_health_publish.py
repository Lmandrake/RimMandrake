#!/usr/bin/env python3
"""Rebuild the codebase-health artifact page — but only when it is worth rebuilding.

Owner's rule, SUPERSEDED 2026-09-03: ceiling lowered from one rebuild/hour to one
rebuild/5min ("regenerate the board up to every 5 minutes"). The original
2026-09-02 rule — *"regenerated once per hour (if many changes are occurring) or
upon change (if it's been longer than an hour)"* — is the same shape, just a
tighter MIN_INTERVAL; nothing else about the condition changed.

Both halves are ONE condition, and this is it:

    regenerate  ⇔  the repo has changed since the last build
                   AND at least MIN_INTERVAL has passed since the last build

During a busy stretch that yields at most one rebuild per MIN_INTERVAL, however
many commits land. During a quiet stretch MIN_INTERVAL has long since passed, so
the next change is picked up on the very next check. Nothing regenerates when
nothing changed — a picture identical to the last one is not worth a run, and
republishing it would put a meaningless new version on the artifact.

🔑 CHANGE MEANS THE WORKING TREE, NOT JUST HEAD. Blue on that page is "uncommitted
in the working tree", so a fingerprint built from `HEAD` alone would sit still
through exactly the edits the page exists to show. The fingerprint is HEAD plus a
hash of `git status --porcelain`.

⚠️ The fingerprint recorded is the one measured BEFORE the build, not after. The
build writes into `Transient/`, which `git status` reports, so re-measuring after
would fold this run's own output into the state — and, worse, would swallow any
real edit that landed while the generator ran. One spurious rebuild the first time
those output files appear is the cheaper error.

    codebase_health_publish.py            # check, and rebuild only if the rule says so
    codebase_health_publish.py --force    # rebuild regardless (still records the run)
    codebase_health_publish.py --check    # say what it WOULD do; write nothing

Exit codes are the point when a scheduler drives this:
    0  rebuilt — the caller should republish the artifact
       (with --check: WOULD rebuild. --check never writes, so never republish on it)
    3  skipped — nothing to do, do NOT republish
    1  something failed, including "git could not be read" — never assume unchanged
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GEN = os.path.join(HERE, "codebase_health.py")
TMPL = os.path.join(HERE, "codebase_health_artifact.tmpl.html")
STATE = os.path.join(REPO, "infrastructure", "state", "codebase_health_last.json")
JSON_OUT = os.path.join(REPO, "Transient", "codebase_health.json")
PAGE_OUT = os.path.join(REPO, "Transient", "codebase_health_artifact.html")

MIN_INTERVAL = 300           # seconds. The owner's ceiling, lowered from 3600 2026-09-03.

# The page's status codes. `green` and `grey` both start with "g", which is exactly
# the kind of collision that turns a health map into a lie, so they are spelled out.
CODE = {"red": "r", "blue": "b", "green": "n", "grey": "y", "unmeasured": "u"}


def sh(*args):
    """Run a command and return stdout — or None if it failed.

    🔴 A FAILURE MUST NOT LOOK LIKE AN EMPTY ANSWER. This used to return
    `.stdout.strip()` unconditionally, so a `git status` that lost the race for
    `index.lock` — an everyday event with four agent threads on one checkout —
    came back as `""`, indistinguishable from a clean tree. The fingerprint then
    silently described a repo state that did not exist, and the rule this whole
    file implements ("rebuild only when the repo changed") was deciding on it.
    """
    r = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    return None if r.returncode != 0 else r.stdout.strip()


def fingerprint():
    """HEAD + the working tree. Either moving is a real change to this picture.

    Returns None when git could not be read at all — the caller must not treat
    that as "nothing changed".
    """
    head = sh("git", "rev-parse", "HEAD")
    dirty = sh("git", "status", "--porcelain")
    if head is None or dirty is None:
        return None
    return hashlib.sha256((head + "\n" + dirty).encode("utf-8")).hexdigest()[:16]


def write_atomic(path, text):
    """Temp beside the target, then `os.replace` — the shape `write_bridge_file` uses.

    Both files this writes are read by something else: the page by whoever publishes
    the artifact, and the state file by the next run of this script, which decides
    from it whether to rebuild at all. A truncated page publishes as a blank map; a
    truncated state file at least fails loudly into `load_state`'s except.
    """
    tmp = "%s.tmp.%d.%d" % (path, os.getpid(), time.time_ns())
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_state():
    try:
        with open(STATE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def flatten(node, rows):
    """The generator's tree -> one compact row per file: path, lines, status, why.

    ⚠️ `"loc" in node`, NOT `node.get("loc")`. A truthiness test dropped every
    zero-line file — the three empty `__init__.py` package markers — so the page
    drew 1585 tiles while its own header, fed by the generator's `counts.total`,
    said 1588 files. A health map that silently omits files is the one thing it
    must never be (review finding, 2026-09-02).
    """
    if node.get("children"):
        for c in node["children"]:
            flatten(c, rows)
    elif "loc" in node:
        rows.append([node["path"], node["loc"],
                     CODE.get(node.get("status", "grey"), "u"),
                     (node.get("why") or [""])[0][:110],
                     node.get("cycles", 0)])
    return rows


def build():
    # A traceback here would be read as "the publisher is broken" when the generator
    # is the thing that failed, and its stderr has already said why.
    r = subprocess.run([sys.executable, GEN], cwd=REPO, stdout=subprocess.DEVNULL)
    if r.returncode != 0:
        sys.exit("REFUSING: %s exited %d. Its error is above; nothing was published."
                 % (os.path.basename(GEN), r.returncode))
    with open(JSON_OUT, encoding="utf-8") as fh:
        src = json.load(fh)
    rows = flatten(src["tree"], [])
    # 🔴 COVERAGE, NOT A SPOT CHECK. The page's header count comes from the
    # generator and its tiles come from `rows`; nothing else would ever notice
    # them drifting apart, and the drift is invisible on a 1588-tile map.
    total = src["counts"].get("total")
    if total is not None and len(rows) != total:
        sys.exit("REFUSING: flattened %d rows but the generator scanned %d files. "
                 "The map would be missing tiles it claims to show." % (len(rows), total))
    payload = json.dumps({"head": src["head"], "generated": src["generated"],
                          "counts": src["counts"], "reviewEntries": src["reviewEntries"],
                          "loc": src["loc"], "rows": rows,
                          "recidivists": src.get("recidivists", [])},
                         separators=(",", ":"))
    # ⚠️ The data rides inside <script type="application/json">, so a literal
    # "</script>" anywhere in a path or a reason would end the block early and
    # silently truncate the page. Refuse rather than publish a half-page.
    if "</script" in payload.lower():
        sys.exit("REFUSING: the data contains a </script> sequence, which would "
                 "truncate the page. Find it before publishing.")
    with open(TMPL, encoding="utf-8") as fh:
        page = fh.read()
    if "__DATA__" not in page:
        sys.exit("REFUSING: %s has no __DATA__ placeholder." % TMPL)
    os.makedirs(os.path.dirname(PAGE_OUT), exist_ok=True)
    write_atomic(PAGE_OUT, page.replace("__DATA__", payload))
    return src["counts"], len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="rebuild even if the rule says no")
    ap.add_argument("--check", action="store_true", help="report only; write nothing")
    a = ap.parse_args()

    st, fp, now = load_state(), fingerprint(), time.time()
    if fp is None:
        # 🔴 UNMEASURED, NOT UNCHANGED. Skipping here would quietly stop the page ever
        # updating again for as long as git stayed unreadable, with exit 3 ("nothing to
        # do") telling the scheduler everything was fine.
        print("FAIL: git could not be read (rev-parse or status failed), so 'has the "
              "repo changed' is UNMEASURED. Not guessing.", file=sys.stderr)
        return 1
    age = now - st.get("ts", 0)
    changed = fp != st.get("fingerprint")

    if not a.force:
        if not changed:
            print("SKIP: repo unchanged since the last build (%s, %d min ago)."
                  % (st.get("fingerprint", "never"), age / 60))
            return 3
        if age < MIN_INTERVAL:
            print("SKIP: changed, but only %d min since the last build — the owner's "
                  "ceiling is one per %d min." % (age / 60, MIN_INTERVAL / 60))
            return 3

    if a.check:
        print("WOULD REBUILD: changed=%s, %d min since last." % (changed, age / 60))
        return 0

    counts, n = build()
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    write_atomic(STATE, json.dumps(
        {"ts": now, "fingerprint": fp, "counts": counts,
         "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}, indent=1) + "\n")
    print("REBUILT %d files — red %d, blue %d, green %d, grey %d, unmeasured %d"
          % (n, counts.get("red", 0), counts.get("blue", 0), counts.get("green", 0),
             counts.get("grey", 0), counts.get("unmeasured", 0)))
    print("  page -> %s" % PAGE_OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
