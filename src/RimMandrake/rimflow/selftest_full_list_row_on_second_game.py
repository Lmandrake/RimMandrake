#!/usr/bin/env python3
"""A full-list check's row on the second game, written as its brief says, reads `not_counted` at the exit, never
`unclassed` (RIMMANDRAKE_ALIGN_SECOND_GAME_FULL_LIST_ROW_WITH_EXIT_READER).

Measured (Pyrelands visit 6, 2026-11-23, ArchSmall): game_instance.brief told the driver to give sc_walk "one row with
result UNMEASURED and detail `ArchSmall: tier list only beside ArchBig`"; maturation.py next then refused the exit on form,
"its last row reads UNMEASURED with no class", because line_class counts a FAIL or UNMEASURED row only with a class,
an `unrepaired` cause of EXPLAIN_WORDS words and an `owner`.

This test builds the row from the brief's own words (every field the brief names, with the values it gives) and reads it
with maturation.line_class. It also keeps the parts that must not move: the default game's brief names no such row,
and a row without the owner still reads unhandled.

  python3 src/RimMandrake/rimflow/selftest_full_list_row_on_second_game.py     exit 0 = every check PASS
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

import game_instance as GI  # noqa: E402
import maturation as M  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %r" % (detail,)))


def row_from_brief(text, check_id):
    """The row a driver writes for `check_id` by following the brief: each `field` `value` pair the brief names."""
    row = {"test": check_id}
    m = re.search(r"result (\w+)", text)
    row["verdict"] = m.group(1) if m else None
    for field in ("class", "detail", "unrepaired", "owner"):
        m = re.search(r"%s `([^`]*)`" % field, text)
        if m:
            row[field] = m.group(1)
    return row


def main():
    text = GI.brief("b", full_list=["sc_walk"])
    row = row_from_brief(text, "sc_walk")
    got = M.line_class(row, [])
    check("the second game's brief yields a full-list row that counts not_counted (row %r)" % row, got == "not_counted",
          got)
    check("that row is UNMEASURED, never a pass", str(row.get("verdict")).upper() == "UNMEASURED", row)
    bare = dict(row)
    bare.pop("owner", None)
    check("the same row without its owner still reads unhandled", M.line_class(bare, []) == "unhandled",
          M.line_class(bare, []))
    check("the default game's brief names no such row", "tier list only beside" not in GI.brief(GI.DEFAULT,
                                                                                              full_list=["sc_walk"]))
    bad = RESULTS.count(False)
    print("selftest_full_list_row_on_second_game: %d of %d checks failed" % (bad, len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
