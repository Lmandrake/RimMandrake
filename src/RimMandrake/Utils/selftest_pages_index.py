#!/usr/bin/env python3
"""selftest_pages_index.py: every kept page links to every other kept page by its full Windows path.

    python3 src/RimMandrake/Utils/selftest_pages_index.py          offline: the lines, and each renderer calls them
    python3 src/RimMandrake/Utils/selftest_pages_index.py --live   also reads the head of each page file on disk

Boundary: design/specs/2026-11-24-monitors-consolidated/boundary.md (offline promises and the separate live check).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import pages_index as P  # noqa: E402

FAILS = []

# the renderer of each RimMandrake page, and the call that must be in it (FLEET_NOW is Augur's: its config links)
RENDERERS = {
    "maturation": ("src/RimMandrake/Utils/maturation_now.py", ['crossref_md("maturation")', 'crossref_html("maturation")']),
    "detail": ("src/RimMandrake/Utils/maturation_now.py", ['crossref_md("detail")', 'crossref_html("detail")']),
    "codebase": ("src/RimMandrake/Utils/codebase_now.py", ['crossref_html("codebase")']),
    "ops": ("src/RimMandrake/Utils/ops_watch.py", ['crossref_md("ops")']),
}
AUGUR_CONFIG = "/mnt/d/ClaudeWork/augur/config/dashboard.json"


def check(ok, what, got=None):
    print(("PASS " if ok else "FAIL ") + what + ("" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def t_crossref_names_every_other_page():
    for k in P.KEPT:
        md, ht = P.crossref_md(k), P.crossref_html(k)
        for o, (lab, path, _q) in P.KEPT.items():
            if o == k:
                check(path not in md and path not in ht, "%s does not link to itself" % k)
            else:
                check(path in md and path in ht, "%s names %s by its full path" % (k, lab), md)
    try:
        P.crossref_md("relentless")
        check(False, "an unknown page key is refused by name")
    except KeyError as e:
        check("relentless" in str(e), "an unknown page key is refused by name", str(e))


def t_each_renderer_prints_the_line():
    for k, (rel, calls) in RENDERERS.items():
        src = open(os.path.join(REPO, rel), encoding="utf-8").read()
        for c in calls:
            check(c in src, "%s calls pages_index.%s" % (os.path.basename(rel), c))


def t_fleet_config_links_the_others():
    import json
    try:
        links = {l.get("path") for l in json.load(open(AUGUR_CONFIG)).get("links") or []}
    except OSError as e:
        print("UNMEASURED t_fleet_config_links_the_others: cannot read %s (%s)" % (AUGUR_CONFIG, e))
        return
    for o, (lab, path, _q) in P.KEPT.items():
        if o != "fleet" and o != "detail":
            check(path in links, "Augur's FLEET_NOW config links %s" % lab, sorted(links))


def t_live_pages_carry_the_line():
    for k, (lab, path, _q) in P.KEPT.items():
        if k == "fleet":
            continue
        p = "/mnt/" + path[0].lower() + path[2:].replace("\\", "/")
        try:
            head = open(p, encoding="utf-8", errors="replace").read(8000)
        except OSError as e:
            print("UNMEASURED %s: %s" % (lab, e))
            continue
        others = [v[1] for o, v in P.KEPT.items() if o != k]
        check(all(x in head for x in others), "%s on disk names the other pages near its top" % lab)


def main(argv):
    t_crossref_names_every_other_page()
    t_each_renderer_prints_the_line()
    t_fleet_config_links_the_others()
    if "--live" in argv:
        t_live_pages_carry_the_line()
    print("RESULT: " + ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
