#!/usr/bin/env python3
"""ops_escalate: a Sonnet Operations run hands what it finds fishy to one Opus run.

RIMMANDRAKE_SONNET_OPS_REVISITS_SIX_GREPS_TIMED_OUT (owner's card 2026-11-19, "Sonnet for follow-ups only", his words:
"If we escalate to (4) then we would likely give Sonnet Escalation: recognize something is fishy, so call out Opus to
continue."). Page: design/specs/2026-11-26-ops-sonnet-revisits-escalate/boundary.md.

The record: `rimflow ops-escalate --what "<what is fishy>" [--incident <id>]`, typed inside a launched role run. It
appends one row to escalations.jsonl beside told.jsonl, stamped from the run's own environment (RM_ROLE_UNIT,
RM_ROLE_MODEL, RM_ROLE_CONTINUATION; role_launch.launch_argv sets them). The Dispatcher's incident pass reads the new
rows (dispatcher.escalation_pass): a row from a Sonnet run that is not itself a continuation asks ONE Opus run that
continues from that run's notes; any other row asks nothing. No loop: the continuation carries RM_ROLE_CONTINUATION, so
its own escalation is read and asks nothing.
"""
import json
import os
import re
import time

import incident as IN

UNIT_RE = re.compile(r"^[A-Za-z0-9_.@:-]{1,96}$")


def path(d=None):
    return os.path.join(d or IN.ops_dir(), "escalations.jsonl")


def read_rows(p=None):
    """-> the rows, or None when a line does not parse (said, never guessed at). An absent file is no rows."""
    try:
        with open(p or path(), encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        return None


def record(why, seat, env=None, incident=None, p=None, now=None):
    """The verb. -> the row written. Raises ValueError with the repair: an empty why, or no role run to continue."""
    env = os.environ if env is None else env
    why = (why or "").strip()
    if not why:
        raise ValueError("--what: say what is fishy, in one line the Opus run starts from")
    unit = env.get("RM_ROLE_UNIT", "")
    if not UNIT_RE.match(unit):
        raise ValueError("ops-escalate is typed inside a launched Operations run (RM_ROLE_UNIT is %s): outside one there is "
                         "no run to continue; write it as a note on the item it is about (rimflow note <ID> --text \"...\")"
                         % ("unset" if not unit else "not a unit name"))
    now = time.time() if now is None else now
    row = {"at": IN.iso(now), "t": now, "why": why, "by": seat, "unit": unit,
           "model": env.get("RM_ROLE_MODEL") or None, "continuation": env.get("RM_ROLE_CONTINUATION") or None,
           "incident": (incident or "").strip() or None}
    p = p or path()
    IN.guard(p)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return row


def due(row, done):
    """Pure. -> (True, None) when this row asks one Opus continuation, else (False, why it asks none).
    `done`: the units whose continuation was already asked."""
    if row.get("continuation"):
        return False, "from the Opus continuation of %s: a continuation does not escalate again" % row["continuation"]
    if row.get("model") != "sonnet":
        return False, "from a run on %s, not Sonnet: nothing stronger to hand to" % (row.get("model") or "an unknown model")
    if row.get("unit") in done:
        return False, "run %s already has its Opus continuation" % row.get("unit")
    return True, None


def continuation_text(row, notes):
    """The Opus run's launch message head: what the Sonnet run found and where its notes are."""
    inc = row.get("incident")
    return ("ESCALATED (on Opus) by Sonnet Operations run %s at %s%s: \"%s\". Continue from its notes: its run record "
            "%s, %s. Decide what the Sonnet run could not; you are the continuation, so `rimflow ops-escalate` asks "
            "nothing more." % (row["unit"], row["at"], (" on INCIDENT %s" % inc) if inc else "", row["why"], notes,
                                ("its rows on %s in `rimflow incidents`" % inc) if inc else "the items it noted"))
