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

A sitting's core job is MEASURING SURPRISE (owner 2026-11-04): it LOOKs at the screen regularly, reads the test-state
monitor (jawa/vitals) and the window stack, and scores each observation EXPECTED / ODD / ALARMING given the biome, the
test's purpose and the map's history, with the one bridge read that explains it. Each ODD or ALARMING one gets one
EXPLAIN-AWAY from context (the SURPRISE BOOK, surprise_book.py: the biome's real roster, the test's purpose, recent
letters, what earlier sittings learned) before it is filed; a (kind, context) that keeps ending explained or not a
bug is retired there, and a real bug revives it (owner 2026-11-04: "This can be the agent learning.").

Once the item is answered or blocked, a sitting explores the same loaded map like a player would (EXPLORATION PASS,
TEST_PILOT_WIDEN_PAST_THE_CHECKLIST) and files what surprised it as checkable events.

A sitting ends with `rimflow note <ID> --text "TESTPILOT_SAT: ..."`. That restarts the count, so a pilot's finding is
given its fix and retest, and three fresh misses send the item back to a pilot. Items that never route: closed,
blocked (something else is wrong), needs owner (his look, not a live debug), intent JUDGE (an art verdict: no live
debugging answers it). Runs in NOT_A_TEST are not tests of the
item: testq records lane pauses and item-less filler FAILs there.

The Dispatcher reads the ROUTE line `rimflow next` prints (dispatcher.parse_peek), so the marker wording below is a
contract with it and with selftest_testpilot_route.py.
"""
import collections
import json

STREAK = 3
OPEN_STATES = ("proposed", "ready", "doing", "built", "validated")      # model.OPEN_STATES (selftest pins them equal)
LIVE_NEEDS = ("bridge", "game-up")
NOT_A_TEST = ("steve-lane",         # STEVE_LANE_MONITOR_PAUSE_FINDINGS: a lane pause, recorded as a failed run
              "steve-filler", "archmagi-filler")   # STEVE_FILLER_MONITOR_FAIL_FINDINGS: item-less filler FAILs (ingest)
SAT, WANTED = "TESTPILOT_SAT", "TESTPILOT_WANTED"
ROUTE = "ROUTE rm-testpilot"
HOSTS = ("stevedesktop", "archmagi")    # preference order: SteveDesktop's game is ours, Archmagi's list is his
FREE_STATES = ("FREE", "STALE")
EXPLORE = "EXPLORATION PASS"      # the brief's marker for the after-the-item pass (selftest pins it)
EXPLORE_MAX_FILED = 5             # new items one sitting files from exploring; the rest wait in its PROGRESS file
SURPRISE = "MEASURING SURPRISE"   # the brief's marker for the pilot's core framing (owner 2026-11-04; selftest pins it)
LOOK_EVERY_MIN = 10               # a LOOK at sitting start, after every experiment, and at least this often
SCORES = ("EXPECTED", "ODD", "ALARMING")   # each observation's surprise score
BOOK = "SURPRISE BOOK"            # the brief's marker for surprise_book.py (SURPRISE_BOOK_BUILD_RETIRE_THE_BORING; selftest pins it)
BOOK_CLI = "python3 src/RimMandrake/rimflow/surprise_book.py"
EXPLAIN = "EXPLAIN-AWAY"          # one attempt to prove an ODD/ALARMING observation unsurprising before filing it


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
    # LIVE_FAILURES_EXPLAIN_MORE_THAN_A_LABEL (owner 2026-11-04): "Make sure the Test Pilot's job is to EXPLAIN the
    # failure, not just try to execute a test. ... Then there needs to be follow-up work to address them."
    lines += ["Read first: `rimflow show %s` and Player.log's first exception." % i]
    # TEST_PILOT_WIDEN_PAST_THE_CHECKLIST, owner 2026-11-04: "it should regularly "look at" the screen and reason about
    # what it's seeing. ... It should be given latitude to gather context and then reason about how surprising any of it
    # is. That's what's the test pilot is really about. Measuring surprise."
    lines += ["Your core job is %s: gather context (you have latitude to), then reason how surprising each observation "
              "is given the biome, the test's purpose and the map's history. The bridge says why; the screen says what a "
              "player sees. Use both." % SURPRISE,
              "LOOK at sitting start (after the take and the PROGRESS skeleton; arm the monitor then: `jawa/vitals "
              "action=arm`), after every experiment, and at least every ~%d minutes: `jawa/vitals action=status` (the "
              "test-state monitor: tombstones, threats, blocking windows and their age, letters), `jawa/window_list_close "
              "action=list` (a stale modal blocks every later call), then capture BEFORE any `jawa/clear_ui` (clearing "
              "hides the modal you look for): at the Windows desktop `python3 src/RimMandrake/Utils/system_screenshot.py "
              "<out.bmp>` (OS capture, sees dialogs, works when a modal blocks the bridge) and `jawa/take_screenshot` "
              "(game render, either host; clear_ui first only for a map-only shot). Record a modal, then close it. "
              "Never take focus or fullscreen. Crop to the subject, view at <=1500 px, and actually reason about "
              "it." % LOOK_EVERY_MIN,
              "Each look, ask at least: do the creatures shown belong in this biome; dead animals or colonists with no "
              "cause; mechanoids, raiders, merchants or visitors present, and why; fire outside a fire test; a modal "
              "dialog or error on screen; weather and temperature plausible; the red error counter (rimbridge/list_logs, "
              "a ring). Score each %s with the bridge state read that explains or confirms it (one at least; dig further when it does not) (jawa/pawn_census, "
              "jawa/damage_log, jawa/weather_get, jawa/incident_queue_peek, jawa/vitals), in your PROGRESS file; an "
              "unexplained %s or %s one is filed as a strange thing below." % (" / ".join(SCORES), SCORES[1], SCORES[2]),
              # SURPRISE_BOOK_BUILD_RETIRE_THE_BORING, owner 2026-11-04: "when it finds what seems surprising (omg there
              # are mushrooms everywhere) it then has a chance to prove it's not surprising (oh, this is the rot biome,
              # that makes sense) ... If it keeps thinking boring things are surprising we will need to retire some
              # surprise. ... This can be the agent learning."
              "%s: at sitting start, once you know the map's biome, read what earlier sittings learned: `%s settle` "
              "(earlier filings whose item has ended become not_a_bug, abandoned or co_occurred), then `%s start --context "
              "biome=<BiomeDef defName> --sitting %s@<YYYY-MM-DDTHHMM>` (retired keys score EXPECTED in that context "
              "only; it names this sitting's SAMPLE, a retired entry you re-check by state read and record `--sample "
              "--outcome sample_ok|real_bug`, so silence is tested). A real bug revives a retired key only with `--cause "
              "'<fix_commit|pilot_cause|gone_after_fix>: <evidence>'` showing the observation directly causes or results "
              "from it; without one it is recorded as co_occurred and the key stays retired (owner 2026-11-04: \"not "
              "just 'a mushroom was nearby'\")." % (BOOK, BOOK_CLI, BOOK_CLI, i),
              "%s: each %s or %s observation gets ONE attempt to prove it unsurprising from context before it is filed: "
              "`%s explain --kind <slug> --context biome=<defName> --sitting %s@<YYYY-MM-DDTHHMM> --def <defName seen>...` "
              "checks the book and the biome's real roster (BiomeDef wildAnimals/wildPlants plus the patch-added cast); "
              "the test's purpose and recent letters (jawa/vitals) are yours to cite. EXPLAINED (cite the fact): `record "
              "--outcome explained --evidence \"<source>: <fact>\"`. STANDS: file it, then `record --outcome filed --item "
              "<ID>`. Reuse a kind slug the book already has. Never retire by hand: the book retires and revives." % (
                  EXPLAIN, SCORES[1], SCORES[2], BOOK_CLI, i),
              "Flyers are state-read only. Owner: \"Don't try to capture images of flight. It doesn't work.\" Never "
              "capture, stage or test a flyer's flight to look at it.",
              "Your job is to EXPLAIN the failure, not just to run the test: what the proof expected, what the game did, "
              "the mechanism linking them, the evidence for each step, and the theories you ruled out and why.",
              "Each cause you explain gets ONE open follow-up item: this item when the fault is its own, else reuse the "
              "open item for that cause (`python3 src/RimMandrake/rimflow/relentless.py causes`) or `rimflow namecheck` "
              "then `rimflow file <NAME> --for BENCH` (a closed one is never reopened: file a new one --caused-by it)."]
    # TEST_PILOT_WIDEN_PAST_THE_CHECKLIST (owner 2026-11-04): "capable of filing tickets about strange things beyond
    # its specified checklist items ... and tries to "make something productive" come from a live test".
    lines += ["Then go %s: with the item answered or blocked, explore the same loaded map for up to ~25%% of the "
              "sitting, never a reload for it. Make something productive: if the checklist cannot be reached, diagnose "
              "the test itself (HARNESS / SITE is a full result), narrow the cause, or write a guard; 'nothing learned' "
              "is not an ending." % EXPLORE,
              "Neighbour expectations: for each thing you test, list 2-3 things a player would also expect to still work "
              "there (a water-filled pit: pawns swim in it, path around it, animals drink, fishing, save/load keeps it) "
              "and check them cheaply by bridge state read.",
              "Strange things beyond the checklist: search src/ and the items first, then file each as its own item, a "
              "checkable event (design/RimMandrake/player_role_2026-10-31/03-merged.md): what the screen or state led "
              "you to expect, what the game did, the bridge read proving it and that your call landed, class "
              "MOD / SITE / HARNESS / EXPECTATION. At most ~%d new items; the rest go in your PROGRESS file. The hard "
              "limits (no flyer flight, no fullscreen or focus, never force a bridge, burden of proof before a reload, "
              "no worldgen, ModsConfig backup and restore) do not loosen for it." % EXPLORE_MAX_FILED,
              "End: write the sitting into the mod's functional script, then rimflow note %s --text \"%s: <sha> | "
              "expected: ... | observed: ... | mechanism: ... | evidence: <one per step> | ruled out: <theory: why> | "
              "follow-up: <ITEM> | explored: <what> | surprises: <n scored, ids filed> | book: explained <n>, retired <keys> "
              "(`%s summary --sitting %s@<YYYY-MM-DDTHHMM>`) | filed: <ids>\", then commit the book "
              "(infrastructure/state/testpilot/surprise_book.jsonl) and release the bridge." % (i, SAT, BOOK_CLI, i)]
    return "\n".join(lines)
