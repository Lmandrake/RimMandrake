"""
Selftest: `handoff.py --cull` deletes exactly the handoffs the owner's card allows, and nothing else.

Owner, by card 2026-11-18 (RIMMASTER_SETTLE_HANDOFF_CULL_AGE_TWO_RULINGS_DISAGREE), picked
"7 days after replaced (Recommended)": a handoff goes once a newer handoff from the same window
replaced it 7 or more days ago AND its lessons are filed. The 30-day rule it replaced (2026-09-18)
culled by the handoff's own age and by "committed before the last lessons drain", which says
nothing about whether THIS handoff's lessons were filed.

The five cases, each run through the real `cull(apply_=True)` on a temp folder:
  1. replaced 6 days ago -> stays
  2. replaced 8 days ago, lessons filed -> goes
  3. replaced 8 days ago, a lesson line nowhere filed -> stays
  4. the newest handoff of each window -> stays, however old and however filed
  5. "could not tell" (unreadable file, no date, no lesson headings) -> stays AND is listed
"""

import contextlib
import datetime
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["RIMFLOW_SEAT"] = "BENCH"

import handoff  # noqa: E402

fails = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        fails.append(what)


NOW = datetime.datetime.now(datetime.timezone.utc)


def stamp(days):
    return (NOW - datetime.timedelta(days=days, minutes=5)).strftime("%Y%m%d%H%M")


def iso(st):
    return datetime.datetime.strptime(st, "%Y%m%d%H%M").strftime("%Y-%m-%dT%H:%M:00Z")


def body(trap):
    return ("# handoff\n\n## The one thing to carry forward\n\nnothing this wave\n\n"
            "## What the owner should see\n\nnothing\n\n## Traps learned\n\n%s\n\n## Commits\n\n- abc\n" % trap)


FILED = body("- a count lied about a missing dir (filed: infrastructure/state/lessons/x.md)")
UNFILED = body("- the probe reads a stale cache unless the bridge is restarted first")
NO_HEADINGS = "# FOUNDRY handoff, free-form\n\nTraps: the grid writer drops the last row.\n"

d = tempfile.mkdtemp(prefix="handoff_cull_")
files = {}     # name -> (text or None for unreadable, committed?)


def add(seat, days, text, name=None):
    fn = name or "%s_REBOOT_HANDOFF_%s.md" % (seat, stamp(days))
    files[fn] = text
    with io.open(os.path.join(d, fn), "w", encoding="utf-8") as fh:
        fh.write(text if text is not None else FILED)
    return fn


ONE_1 = add("WONE", 40, FILED)           # replaced 6 days ago by ONE_2
ONE_2 = add("WONE", 6, FILED)
TWO_1 = add("WTWO", 20, FILED)           # replaced 8 days ago by TWO_2, filed
TWO_2 = add("WTWO", 8, FILED)            # newest of its window, old and filed
THREE_1 = add("WTHREE", 40, UNFILED)     # replaced 8 days ago, not filed
THREE_2 = add("WTHREE", 8, FILED)
FOUR_1 = add("WFOUR", 40, None)          # unreadable
FOUR_2 = add("WFOUR", 8, FILED)
FIVE_0 = add("WFIVE", 40, FILED)
FIVE_X = add("WFIVE", 0, FILED, name="WFIVE_REBOOT_HANDOFF_2notastamp.md")   # no date at all
SIX_1 = add("WSIX", 40, NO_HEADINGS)     # no lesson headings: cannot tell what it taught
SIX_2 = add("WSIX", 8, FILED)
os.chmod(os.path.join(d, FOUR_1), 0)

times = {fn: iso(fn.rsplit("_", 1)[1][:-3]) for fn in files if fn != FIVE_X}

handoff.HANDOFFS = d
handoff._corpus_commit_times = lambda: dict(times)
handoff.last_drain_ts = lambda: NOW.strftime("%Y-%m-%dT%H:%M:%SZ")   # the old rule's "harvest-covered"
handoff.lessons_corpus = lambda: ""                                  # nothing filed except by citation

out = io.StringIO()
with contextlib.redirect_stdout(out):
    try:
        rc = handoff.cull(True)
    except Exception as e:      # noqa: BLE001  a crash is a FAIL of every case, shown, not a traceback
        rc = "raised %r" % e
text = out.getvalue()
left = set(os.listdir(d))
os.chmod(os.path.join(d, FOUR_1), 0o600) if FOUR_1 in left else None

print("handoff --cull: 7 days after replaced, lessons filed (owner card 2026-11-18)")
check(ONE_1 in left, "1. replaced 6 days ago stays")
check(TWO_1 not in left, "2. replaced 8 days ago, lessons filed, goes")
check(THREE_1 in left, "3. replaced 8 days ago, a lesson nowhere filed, stays")
check(all(f in left for f in (ONE_2, TWO_2, THREE_2, FOUR_2, FIVE_0, SIX_2)),
      "4. the newest dated handoff of each window stays")
check(all(f in left and f in text for f in (FOUR_1, FIVE_X, SIX_1)) and "could not tell" in text.lower(),
      "5. could-not-tell (unreadable, undated, no lesson headings) stays and is listed")
print("  (cull returned %s)" % (rc,))
if fails:
    print(text)

print("\n%d FAIL" % len(fails) if fails else "\nALL PASS")
sys.exit(1 if fails else 0)
