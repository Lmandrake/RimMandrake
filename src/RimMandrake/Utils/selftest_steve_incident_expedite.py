#!/usr/bin/env python3
"""Guard for OPS_STEVE_UNSTICK_UNCLAIMED_ETBS (STEVE_INCIDENT_UNCLAIMED came back 12+ times).

Class: a steward incident (STEVE_LANE_UNSTICK_*) is handed to Relentless only when the 30-min alarm rings. Relentless
enrols enrol_per_tick (2) items a tick, ticks ~5 min apart, so a fresh incident ranked eleventh among system items waited
27 min for a slot (2026-11-06: 5CB3 spawned 11:56:22Z, enrolled 12:22:59Z, alarm 33.9 at 12:40Z). The fix: Operations'
pass expedites (relentless expedite set --by Operations, past every cap) any incident unclaimed for
rules steve_incident.expedite_after_min, once per renew window, never an OWNER rung, a live-leased or a young one.
Exit 0 all checks pass, 1 any fails.
"""
import json
import os
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_tmp = tempfile.mkdtemp(prefix="steve_expedite_")
os.environ["RM_OPS_WATCH_DIR"] = _tmp
import ops_watch as OW  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(name)


NOW = 1793966400.0      # 2026-11-06T12:00:00Z
RULES = OW.load_rules()
P = "STEVE_LANE_UNSTICK_"
M = types.SimpleNamespace(epoch=lambda ts: ts, lease_status=lambda it, now: it.lease)


def item(iid, state, age_min, lease=None, blocked=False):
    return types.SimpleNamespace(id=iid, state=state, open=state != "done", blocked=blocked, lease=lease,
                                 created_at=NOW - age_min * 60)


def world(*its):
    return types.SimpleNamespace(items={i.id: i for i in its})


cfg = RULES.get("steve_incident") or {}
after = cfg.get("expedite_after_min")
check("rules: steve_incident.expedite_after_min is a number well under the alarm's 30 min",
      isinstance(after, (int, float)) and 0 < after <= 15, after)
after = after if isinstance(after, (int, float)) else 5
early = getattr(OW, "steve_incident_early", None)
check("ops_watch has steve_incident_early (Operations' early hand of an incident to Relentless)", callable(early))

if callable(early):
    asked = []

    def expediter(ids, why):
        asked.append((list(ids), why))
        return {i: None for i in ids}

    # the instance: 5CB3 at 12:00Z, 3.6 min after birth (young), then 10 min (over the line)
    w = world(item(P + "BRAKED_UNOWNED_5CB3", "proposed", 3.6))
    pt = OW.steve_incident_unclaimed(w, M, NOW, RULES)
    flags = early(pt, RULES, NOW, expediter)
    check("a young incident is not expedited", asked == [] and flags == [], (asked, flags))

    w = world(item(P + "BRAKED_UNOWNED_5CB3", "proposed", after + 5), item(P + "BRAKED_OWNER_2E27", "proposed", 90),
              item(P + "PAUSED_UNOWNED_AAAA", "ready", 60, lease="live"), item(P + "PAUSED_UNOWNED_BBBB", "proposed", 1))
    pt = OW.steve_incident_unclaimed(w, M, NOW, RULES)
    check("the reading names each unclaimed incident's age", (pt.get("x") or {}).get("ages", {}).get(P + "BRAKED_UNOWNED_5CB3")
          == round(after + 5, 1), pt)
    flags = early(pt, RULES, NOW, expediter)
    check("the instance: 5CB3 unclaimed past the line is expedited by Operations, and only it",
          [a[0] for a in asked] == [[P + "BRAKED_UNOWNED_5CB3"]] and flags == [], (asked, flags))

    asked.clear()
    early(pt, RULES, NOW + 120, expediter)
    check("the next pass does not expedite it again", asked == [], asked)
    early(OW.steve_incident_unclaimed(w, M, NOW + OW.STEVE_EXPEDITE_RENEW_S + 60, RULES), RULES,
          NOW + OW.STEVE_EXPEDITE_RENEW_S + 60, expediter)
    check("past the renew window, still unclaimed, it is expedited again (BBBB has grown old beside it)",
          [a[0] for a in asked] == [[P + "BRAKED_UNOWNED_5CB3", P + "PAUSED_UNOWNED_BBBB"]], asked)

    asked.clear()

    def refuser(ids, why):
        asked.append(list(ids))
        return {i: "exit 2: no" for i in ids}

    w2 = world(item(P + "STALLED_UNOWNED_CCCC", "proposed", 20))
    flags = early(OW.steve_incident_unclaimed(w2, M, NOW, RULES), RULES, NOW, refuser)
    check("a refusal is said as a flag", len(flags) == 1 and "STALLED_UNOWNED_CCCC" in flags[0]["detail"], flags)
    early(OW.steve_incident_unclaimed(w2, M, NOW + 60, RULES), RULES, NOW + 60, refuser)
    check("a refused expedite is retried the next pass", len(asked) == 2, asked)

    asked.clear()
    flags = early({"m": "UNMEASURED", "why": "x"}, RULES, NOW, expediter)
    check("an UNMEASURED reading expedites nothing", asked == [] and flags == [], (asked, flags))
    no_rule = json.loads(json.dumps(RULES))
    no_rule["steve_incident"].pop("expedite_after_min", None)
    flags = early(OW.steve_incident_unclaimed(w2, M, NOW + 9 * 3600, RULES), no_rule, NOW + 9 * 3600, expediter)
    check("no expedite_after_min rule: nothing expedited, nothing flagged", asked == [] and flags == [], (asked, flags))

print("%d failed" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
