#!/usr/bin/env python3
"""check_margin: the one line a check prints for how near it came to its limit (tuning tripwire T2, item
RIMMANDRAKE_LIST_THINNEST_MARGINS_IN_CERTIFICATE_RUN; the owner, 2026-11-16: every check prints its worst value, its
limit and how many cases it read). `maturation.py certificate --run` lists the thinnest margins first.

    import check_margin
    check_margin.line(worst, limit, cases, name="sag at noon")   # MARGIN worst=0.101 limit=0.1 cases=36 name=sag at noon

Page: design/specs/2026-11-19-maturation-tripwires/boundary.md."""
import math
import re

RX = re.compile(r"^MARGIN worst=(\S+) limit=(\S+) cases=(\d+)(?: name=(.*))?$")


def text(worst, limit, cases, name=None):
    return "MARGIN worst=%r limit=%r cases=%d%s" % (float(worst), float(limit), int(cases),
                                                    (" name=%s" % name) if name else "")


def line(worst, limit, cases, name=None):
    print(text(worst, limit, cases, name), flush=True)


def parse(out):
    """-> [{"worst", "limit", "cases", "name"?}] for every well-formed MARGIN line in OUT; [] when none (a check that
    printed no margin). A line with a non-number or a missing field is not a margin."""
    got = []
    for ln in str(out or "").splitlines():
        m = RX.match(ln.strip())
        if not m:
            continue
        try:
            w, lim = float(m.group(1)), float(m.group(2))
        except ValueError:
            continue
        if not (math.isfinite(w) and math.isfinite(lim)):
            continue
        row = {"worst": w, "limit": lim, "cases": int(m.group(3))}
        if m.group(4):
            row["name"] = m.group(4).strip()
        got.append(row)
    return got


def thinness(row):
    """|worst - limit| / |limit|: smaller is thinner; a zero limit reads the absolute distance."""
    d = abs(row["worst"] - row["limit"])
    return d / abs(row["limit"]) if row["limit"] else d
