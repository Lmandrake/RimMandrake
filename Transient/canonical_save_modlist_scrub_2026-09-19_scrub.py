#!/usr/bin/env python3
"""CANONICAL_SAVE_MODLIST_DIVERGENCE_1 — scrub 5 retired packageIds from the
canonical save's <meta> mod-list metadata.

Owner-authorized 2026-09-19: "Yes, scrub it now".

Removes exactly one <li> line from each of the three parallel <meta> lists
(<modIds>, <modSteamIds>, <modNames>) for each of the 5 packageIds below,
keeping index alignment across the three lists. Nothing else in the save is
touched: raw whole-line byte edit, CRLF preserved, no XML re-serialisation.

The 5 are all deliberately retired mods whose CONTENT was ported natively under
the SAME defNames (RESEARCH_TRIO_RETIRE_1, POLLUTED_LANDS_FLORA_PORT_1), so the
save's game DATA does not depend on them — only the compat-gate header does.

Usage: python3 <this> <in.rws> <out.rws>
"""
import re
import sys

TARGETS = [
    "als.gravtech",
    "als.gravtech.bc",
    "halituisamaricanous.gravtechbigcannons",
    "petetimessix.researchreinvented.steppingstones",
    "biomesteam.biomespollutedlands",
]
EXPECTED_LEN = 635
LISTS = ("modIds", "modSteamIds", "modNames")


def list_bounds(lines, tag):
    """Return (first_li_idx, last_li_idx_exclusive) for <tag> inside <meta>."""
    open_i = close_i = None
    for i, l in enumerate(lines[:3000]):
        s = l.strip()
        if s == b"<%s>" % tag.encode():
            assert open_i is None, "duplicate <%s>" % tag
            open_i = i
        elif s == b"</%s>" % tag.encode():
            assert close_i is None, "duplicate </%s>" % tag
            close_i = i
    assert open_i is not None and close_i is not None, tag
    return open_i + 1, close_i


def main():
    src, dst = sys.argv[1], sys.argv[2]
    assert src != dst, "refusing to write in place"
    data = open(src, "rb").read()
    lines = data.split(b"\n")

    bounds = {}
    for tag in LISTS:
        a, b = list_bounds(lines, tag)
        n = b - a
        assert n == EXPECTED_LEN, "%s has %d entries, expected %d" % (tag, n, EXPECTED_LEN)
        for l in lines[a:b]:
            assert re.fullmatch(rb"\s*<li>.*</li>\r?", l), "not a one-line <li>: %r" % l
        bounds[tag] = (a, b)

    def val(line):
        m = re.fullmatch(rb"\s*<li>(.*)</li>\r?", line)
        return m.group(1).decode("utf-8")

    ids = [val(l) for l in lines[bounds["modIds"][0]:bounds["modIds"][1]]]

    # Resolve the target indices ONCE, from modIds, and apply the same indices
    # to all three lists -- that is what keeps them aligned.
    idx = []
    for t in TARGETS:
        hits = [i for i, p in enumerate(ids) if p.lower() == t.lower()]
        assert len(hits) == 1, "%s occurs %d times in modIds" % (t, len(hits))
        idx.append(hits[0])
    idx = sorted(idx)
    assert len(set(idx)) == len(TARGETS)

    print("removing indices:", idx)
    removed = []
    for i in idx:
        a = bounds["modIds"][0]
        s = bounds["modSteamIds"][0]
        n = bounds["modNames"][0]
        removed.append((i, val(lines[a + i]), val(lines[s + i]), val(lines[n + i])))
        print("  [%3d] id=%-50s steamId=%-12s name=%s" % removed[-1])

    # every removed id must be one of the targets
    for i, pid, _sid, _nm in removed:
        assert pid.lower() in {t.lower() for t in TARGETS}, pid

    drop = set()
    for tag in LISTS:
        a, _b = bounds[tag]
        for i in idx:
            drop.add(a + i)
    assert len(drop) == len(TARGETS) * 3 == 15

    out_lines = [l for j, l in enumerate(lines) if j not in drop]
    assert len(out_lines) == len(lines) - 15
    out = b"\n".join(out_lines)

    removed_bytes = sum(len(lines[j]) + 1 for j in drop)
    assert len(out) == len(data) - removed_bytes, (len(out), len(data), removed_bytes)

    open(dst, "wb").write(out)

    # ---- post-conditions, re-read from the written file ----
    lines2 = open(dst, "rb").read().split(b"\n")
    for tag in LISTS:
        a, b = list_bounds(lines2, tag)
        assert b - a == EXPECTED_LEN - len(TARGETS), (tag, b - a)
    a, b = list_bounds(lines2, "modIds")
    ids2 = [val(l) for l in lines2[a:b]]
    s, _ = list_bounds(lines2, "modSteamIds")
    n, _ = list_bounds(lines2, "modNames")
    steam2 = [val(l) for l in lines2[s:s + len(ids2)]]
    names2 = [val(l) for l in lines2[n:n + len(ids2)]]
    for t in TARGETS:
        assert t.lower() not in {p.lower() for p in ids2}, t
    # alignment: every surviving (id, steamId, name) triple must match the
    # source file's triple for the same packageId
    src_triples = {}
    a0, b0 = bounds["modIds"]
    s0, _ = bounds["modSteamIds"]
    n0, _ = bounds["modNames"]
    for i in range(EXPECTED_LEN):
        src_triples[val(lines[a0 + i])] = (val(lines[s0 + i]), val(lines[n0 + i]))
    for i, p in enumerate(ids2):
        assert src_triples[p] == (steam2[i], names2[i]), (p, src_triples[p], steam2[i], names2[i])
    print("OK: %d -> %d entries in each of the 3 lists; alignment verified for all %d survivors"
          % (EXPECTED_LEN, len(ids2), len(ids2)))
    print("bytes: %d -> %d (-%d)" % (len(data), len(out), removed_bytes))

    # XML still parses
    import xml.etree.ElementTree as ET
    ET.parse(dst)
    print("OK: whole-file ElementTree parse")


if __name__ == "__main__":
    main()
