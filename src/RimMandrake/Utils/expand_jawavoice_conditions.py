"""Fan single-condition JawaVoice rule lines out to the four speaker conditions
the corpus uses.

WHY THIS EXISTS
===============
RimWorld grammar ANDs the conditions inside a single r_logentry and offers no
OR. Covering four speaker cases therefore means writing the same rule four
times. Authoring 4x by hand invites drift, where one copy gets edited and the
other three keep the old text, which is invisible in play because the engine
just picks a different copy.

So: author each line ONCE with INITIATOR_faction==PlayerColony, then run this.
It rewrites the file in place, replacing every PlayerColony rule with the full
set of four.

IDEMPOTENCY
===========
Not idempotent by design. It matches only PlayerColony lines and emits four,
so a second run would quadruple the PlayerColony copy again. Run it once on a
freshly authored file. If you need to re-run after editing, delete the three
non-PlayerColony copies first, or restore from git and re-author.

USAGE
=====
    python src/RimMandrake/Utils/expand_jawavoice_conditions.py <path-to-patch.xml>
"""
import io
import os
import re
import sys

CONDS = [
    "INITIATOR_faction==PlayerColony",
    "INITIATOR_faction==PlayerTribe",
    "INITIATOR_kind==OuterRim_Jawa",
    "INITIATOR_kind==OuterRim_JawaTribal",
]

# Only <li> rule lines. Never the comment header, which mentions the condition
# in prose and must not be rewritten.
RULE = re.compile(
    r'^(\s*)<li>r_logentry\(INITIATOR_faction==PlayerColony,priority=250\)'
    r'(-&gt;.*)</li>\s*$'
)


def expand(path):
    with io.open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    already = sum(1 for ln in lines if "INITIATOR_kind==OuterRim_Jawa" in ln)
    if already:
        sys.stderr.write(
            "refusing: %s already contains %d expanded line(s).\n"
            "Re-running would quadruple the PlayerColony copies. See the\n"
            "IDEMPOTENCY note at the top of this script.\n" % (path, already)
        )
        return 1

    out, n = [], 0
    for line in lines:
        m = RULE.match(line)
        if not m:
            out.append(line)
            continue
        indent, body = m.group(1), m.group(2)
        for cond in CONDS:
            out.append("%s<li>r_logentry(%s,priority=250)%s</li>"
                       % (indent, cond, body))
        n += 1

    if not n:
        sys.stderr.write("no PlayerColony rule lines matched in %s\n" % path)
        return 1

    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))

    print("%s: expanded %d authored line(s) -> %d rules"
          % (os.path.basename(path), n, n * len(CONDS)))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        sys.exit(2)
    sys.exit(expand(sys.argv[1]))
