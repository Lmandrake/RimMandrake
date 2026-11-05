#!/usr/bin/env python3
"""walk_metrics.py - the owner's live walk, measured: W1-W4 of work_allocation_framework_2026-10-26.md §3.6.

Item OWNER_WALK_MEASURE_STAGED_AND_DONE. Before it, no ledger event marked a walk or its staging (`ranBy` held only
BENCH and FOUNDRY), so W2-W4 were UNMEASURED. They now read the `walk` verb (model.VERBS):

    rimflow walk staged <ID> --save "<save or scene>"          any seat: the walk is ready for him
    rimflow walk done <ID> --found N [--findings A,B] --owner-said "<his words>"   OWNER only: he walked it

| metric | reads |
|---|---|
| W1 walks owed   | open items with needs=owner whose title asks for his eyes in game (WALK_TITLE), or that carry a walk event |
| W2 readiness    | of W1, those whose latest walk event is `staged` (a `done` after a staging consumes it) |
| W3 last walk age| days since the latest `walk done` on any item, and what it found |
| W4 walk yield   | findings per walk: mean `found` over every `done` |

A metric with no source event prints UNMEASURED with the reason, never 0 (owner 2026-11-03). W1's title match is the
spec's own weak instrument, kept so W1 does not go blind on items nobody has staged yet; it is named in the output.

    python3 src/RimMandrake/rimflow/walk_metrics.py [--json] [--now 2026-11-05T00:00:00Z]
    python3 src/RimMandrake/rimflow/cli.py walks [--json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                      # noqa: E402

UNMEASURED = "UNMEASURED"
# The framework's W1 instrument: "6 items whose title says walk; 2 say in game".
WALK_TITLE = re.compile(r"\bwalk|\bin[- ]game\b|\blive look\b|\bL4\b", re.I)


def _ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def _latest_open_phase(item):
    """The phase of the item's latest walk event, or None."""
    return item.walks[-1]["phase"] if item.walks else None


def measure(world, now=None):
    """-> {W1..W4: {...}} from a replayed world. Pure: no file is read."""
    now = now or dt.datetime.now(dt.timezone.utc)
    owed = sorted(i.id for i in world.items.values()
                  if i.open and i.needs == "owner" and (i.walks or WALK_TITLE.search(i.title or "")))
    staged = [iid for iid in owed if _latest_open_phase(world.items[iid]) == "staged"]
    dones = sorted(((w["ts"], iid, w) for iid, i in world.items.items() for w in i.walks if w["phase"] == "done"),
                   key=lambda t: t[0])
    out = {"W1": {"value": len(owed), "items": owed,
                  "instrument": "open needs=owner items with a walk event or a walk/in-game title (title match is weak)"}}
    out["W2"] = ({"value": UNMEASURED, "why": "no walk is owed, so readiness has no denominator"} if not owed else
                 {"value": "%d/%d" % (len(staged), len(owed)), "staged": staged,
                  "unstaged": [x for x in owed if x not in staged]})
    if not dones:
        why = "no `walk done` event on the ledger yet"
        out["W3"] = {"value": UNMEASURED, "why": why}
        out["W4"] = {"value": UNMEASURED, "why": why}
        return out
    ts, iid, last = dones[-1]
    out["W3"] = {"value": round((now - _ts(ts)).total_seconds() / 86400.0, 1), "unit": "days", "item": iid,
                 "ts": ts, "found": last["found"], "findings": last["findings"], "detail": last["detail"]}
    counted = [w["found"] for _, _, w in dones if w["found"] is not None]
    out["W4"] = ({"value": UNMEASURED, "why": "%d walk(s) done, none recorded `found`" % len(dones)} if not counted else
                 {"value": round(sum(counted) / float(len(counted)), 2), "unit": "findings/walk",
                  "walks": len(counted), "findings": sum(counted),
                  "uncounted": len(dones) - len(counted)})
    return out


def render(m):
    lines = ["W1 walks owed     %s   (%s)" % (m["W1"]["value"], m["W1"]["instrument"])]
    lines += ["    %s" % x for x in m["W1"]["items"]]
    for k, label in (("W2", "walk readiness"), ("W3", "last walk age"), ("W4", "walk yield")):
        v = m[k]
        if v["value"] == UNMEASURED:
            lines.append("%s %-14s UNMEASURED: %s" % (k, label, v["why"]))
        elif k == "W2":
            lines.append("%s %-14s %s staged%s" % (k, label, v["value"],
                                                  ("; unstaged: " + ", ".join(v["unstaged"])) if v["unstaged"] else ""))
        elif k == "W3":
            lines.append("%s %-14s %s days (%s, %s; found %s)" % (k, label, v["value"], v["item"], v["ts"], v["found"]))
        else:
            lines.append("%s %-14s %s findings/walk over %d walk(s)" % (k, label, v["value"], v["walks"]))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--now", help="UTC stamp to measure ages against (default: the clock)")
    a = ap.parse_args(argv)
    world = model.replay(model.read())
    m = measure(world, _ts(a.now) if a.now else None)
    print(json.dumps(m, indent=1, sort_keys=True) if a.json else render(m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
