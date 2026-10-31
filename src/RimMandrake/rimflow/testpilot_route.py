"""testpilot_route.py -- which items go to a Test Pilot instead of another code-and-retest cycle.

Owner, 2026-10-31: "Ok, so the "test pilot" agent is a real idea we should simply implement and accept, period."
This is the PERMANENT sitting agent (.claude/agents/rm-testpilot.md, one live debugging session on one item). It is not
the arena's `trio` lane, src/RimMandrake/Utils/arena/testpilot.py, which is a trial arm and has its own rules.

THE RULE: an open item goes to a Test Pilot when any of these holds (since its last TESTPILOT_SAT note):
  streak    3 or more non-pass runs (fail or partial) in a row, over the whole item or within one criterion or config;
  wanted    a seat wrote a TESTPILOT_WANTED note: this defect needs live observation;
  diagnose  the item's INTENT is DIAGNOSE and it needs the live game (needs bridge or game-up), and no pilot has sat.

WHY 3. Measured from the ledger 2026-10-31, 858 items and 2664 runs, chance the next run passes after N non-pass runs
in a row. Whole item: N=0 .75, 1 .52, 2 .42, 3 .21, 4 .11, 5 or more about .05. Per criterion or config: 0 .72, 1 .54,
2 .40, 3 .06, 4 .07, 5 or more under .01. A third miss is the cliff: the retest stops being worth its run.
CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP had 314 and stayed red; one sitting found the cause.

A sitting ends with `rimflow note <ID> --text "TESTPILOT_SAT: ..."`. That restarts the count, so a pilot's finding is
given its fix and retest, and three fresh misses send the item back to a pilot. Items that never route: closed,
blocked (something else is wrong), needs owner (his look, not a live debug), intent JUDGE (an art verdict: no live
debugging answers it). Runs in NOT_A_TEST are not tests of the
item: testq records lane pauses there.

The Dispatcher reads the ROUTE line `rimflow next` prints (dispatcher.parse_peek), so the marker wording below is a
contract with it and with selftest_testpilot_route.py.
"""
import collections
import json

STREAK = 3
OPEN_STATES = ("proposed", "ready", "doing", "built", "validated")      # model.OPEN_STATES (selftest pins them equal)
LIVE_NEEDS = ("bridge", "game-up")
NOT_A_TEST = ("steve-lane",)        # STEVE_LANE_MONITOR_PAUSE_FINDINGS: a lane pause, recorded as a failed run
SAT, WANTED = "TESTPILOT_SAT", "TESTPILOT_WANTED"
ROUTE = "ROUTE rm-testpilot"
HOSTS = ("stevedesktop", "archmagi")    # preference order: SteveDesktop's game is ours, Archmagi's list is his
FREE_STATES = ("FREE", "STALE")


def streaks(runs):
    """-> (non-pass runs in a row at the end of `runs`, the worst such count in one criterion or config, its name).
    Criteria and configs count apart, though they may share a name, and a run with a criterion counts in both."""
    whole, per = 0, collections.Counter()
    for r in runs:
        keys = [("config", r.config)] + ([("criterion", r.criterion)] if r.criterion else [])
        whole = 0 if r.result == "pass" else whole + 1
        for key in keys:
            per[key] = 0 if r.result == "pass" else per[key] + 1
    key, worst = max(per.items(), key=lambda kv: kv[1], default=((None, None), 0))
    return whole, worst, key[1]


def _last_note(evs, item, marker):
    """The ledger index of the item's last note whose text starts with `marker`, or -1."""
    for i in reversed(item.history):
        if evs[i].get("event") == "note" and (evs[i].get("text") or "").startswith(marker):
            return i
    return -1


def judge(item, evs):
    """-> None, or {"id", "kind": streak|wanted|diagnose, "why"} for an item that goes to a Test Pilot. Pure."""
    if item.state not in OPEN_STATES or item.blocked or item.needs == "owner" or "_JUDGE_" in item.id:
        return None
    sat = _last_note(evs, item, SAT)
    runs = [r for r in item.runs if r.index > sat and r.config not in NOT_A_TEST]
    whole, worst, key = streaks(runs)
    if whole >= STREAK or worst >= STREAK:
        where = "in a row" if whole >= worst else "in a row on %s" % key
        return {"id": item.id, "kind": "streak", "why": "%d non-pass runs %s" % (max(whole, worst), where)}
    if _last_note(evs, item, WANTED) > sat:
        return {"id": item.id, "kind": "wanted", "why": "a seat asked for live observation"}
    if "_DIAGNOSE_" in item.id and item.needs in LIVE_NEEDS and sat < 0:
        return {"id": item.id, "kind": "diagnose", "why": "a DIAGNOSE that needs the live game"}
    return None


def routed(world, evs):
    """-> every judge() verdict, in no promised order."""
    return [v for v in (judge(item, evs) for item in world.items.values()) if v]


def route_line(verdict):
    return "%s %s: %s" % (ROUTE, verdict["id"], verdict["why"])


def pick_host(statuses):
    """statuses: {host: driver-lock state, None when unreachable} -> the first free host in HOSTS, or None. Pure."""
    for host in HOSTS:
        if statuses.get(host) in FREE_STATES:
            return host
    return None


def read_statuses(host_guard):
    """Each host's guard state, read-only. SteveDesktop over ssh; unreachable reads None, and is simply not picked."""
    out = {}
    try:
        out["archmagi"] = host_guard.status().get("state")
    except Exception:  # noqa: BLE001 - an unread guard is not a free one
        out["archmagi"] = None
    rc, txt = host_guard.remote("stevedesktop", ["status", "--json"], timeout=20)
    try:
        out["stevedesktop"] = json.loads(txt).get("state") if rc == 0 else None
    except ValueError:
        out["stevedesktop"] = None
    return out


def brief(verdict, host):
    """The ready-to-paste brief for an rm-testpilot subagent on `host`."""
    i = verdict["id"]
    lines = ["Spawn subagent_type rm-testpilot (Opus) with this brief. One sitting, one item.",
             "",
             "Item %s. Routed by the Test Pilot rule: %s." % (i, verdict["why"]),
             "Host: %s. Take: rimflow bridge take --host %s --for \"test pilot %s\"" % (host, host, i)]
    if host == "stevedesktop":
        lines.append("Every live call runs on SteveDesktop: ssh \"$STEVE_WSL\" 'cd ~/rm/runner && ...'. That clone is "
                     "read-only to you; code and deploys go by remote_modcheck.sh --sync --no-run from your own clone. "
                     "A running testq job holds the guard: a refused take means pick the other host, never --force.")
    else:
        lines.append("Archmagi: back up ModsConfig.xml before any list change and restore it with the game down at the "
                     "end. Take with --idle-ok; his OWNER hold still refuses, and then you pick the other host.")
    lines += ["Read first: `rimflow show %s` and Player.log's first exception." % i,
              "End: write the sitting into the mod's functional script, then "
              "rimflow note %s --text \"%s: <sha>, cause, false theories\", then release the bridge." % (i, SAT)]
    return "\n".join(lines)
