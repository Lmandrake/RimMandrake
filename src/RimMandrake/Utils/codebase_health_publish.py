#!/usr/bin/env python3
"""Rebuild the codebase-health artifact page — but only when it is worth rebuilding.

Owner's rule, 2026-09-02: *"regenerated once per hour (if many changes are occurring)
or upon change (if it's been longer than an hour)"*.

Both halves are ONE condition, and this is it:

    regenerate  ⇔  the repo has changed since the last build
                   AND at least MIN_INTERVAL has passed since the last build

During a busy stretch that yields exactly one rebuild an hour, however many commits
land. During a quiet stretch the hour has long since passed, so the next change is
picked up on the very next check. Nothing regenerates when nothing changed — a
picture identical to the last one is not worth a run, and republishing it would put
a meaningless new version on the artifact.

🔑 CHANGE MEANS THE WORKING TREE, NOT JUST HEAD. Blue on that page is "uncommitted
in the working tree", so a fingerprint built from `HEAD` alone would sit still
through exactly the edits the page exists to show. The fingerprint is HEAD plus a
hash of `git status --porcelain`.

    codebase_health_publish.py            # check, and rebuild only if the rule says so
    codebase_health_publish.py --force    # rebuild regardless (still records the run)
    codebase_health_publish.py --check    # say what it WOULD do; write nothing

Exit codes are the point when a scheduler drives this:
    0  rebuilt — the caller should republish the artifact
    3  skipped — nothing to do, do NOT republish
    1  something failed
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

MIN_INTERVAL = 3600          # seconds. The owner's "once per hour" ceiling.

# The page's status codes. `green` and `grey` both start with "g", which is exactly
# the kind of collision that turns a health map into a lie, so they are spelled out.
CODE = {"red": "r", "blue": "b", "green": "n", "grey": "y", "unmeasured": "u"}


def sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True).stdout.strip()


def fingerprint():
    """HEAD + the working tree. Either moving is a real change to this picture."""
    head = sh("git", "rev-parse", "HEAD")
    dirty = sh("git", "status", "--porcelain")
    return hashlib.sha256((head + "\n" + dirty).encode("utf-8")).hexdigest()[:16]


def load_state():
    try:
        with open(STATE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def flatten(node, rows):
    """The generator's tree -> one compact row per file: path, lines, status, why."""
    if node.get("children"):
        for c in node["children"]:
            flatten(c, rows)
    elif node.get("loc"):
        rows.append([node["path"], node["loc"],
                     CODE.get(node.get("status", "grey"), "u"),
                     (node.get("why") or [""])[0][:110]])
    return rows


def build():
    subprocess.run([sys.executable, GEN], cwd=REPO, check=True,
                   stdout=subprocess.DEVNULL)
    with open(JSON_OUT, encoding="utf-8") as fh:
        src = json.load(fh)
    rows = flatten(src["tree"], [])
    payload = json.dumps({"head": src["head"], "generated": src["generated"],
                          "counts": src["counts"], "reviewEntries": src["reviewEntries"],
                          "loc": src["loc"], "rows": rows}, separators=(",", ":"))
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
    with open(PAGE_OUT, "w", encoding="utf-8") as fh:
        fh.write(page.replace("__DATA__", payload))
    return src["counts"], len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="rebuild even if the rule says no")
    ap.add_argument("--check", action="store_true", help="report only; write nothing")
    a = ap.parse_args()

    st, fp, now = load_state(), fingerprint(), time.time()
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
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump({"ts": now, "fingerprint": fp, "counts": counts,
                   "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}, fh, indent=1)
    print("REBUILT %d files — red %d, blue %d, green %d, grey %d, unmeasured %d"
          % (n, counts.get("red", 0), counts.get("blue", 0), counts.get("green", 0),
             counts.get("grey", 0), counts.get("unmeasured", 0)))
    print("  page -> %s" % PAGE_OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
