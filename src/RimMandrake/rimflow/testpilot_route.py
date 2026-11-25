"""testpilot_route.py -- which items go to a Test Pilot instead of another code-and-retest cycle.

Owner, 2026-10-31: "Ok, so the "test pilot" agent is a real idea we should simply implement and accept, period."
This is the PERMANENT sitting agent (.claude/agents/rm-testpilot.md, one live debugging session on one item).

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
import os
import sys

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import failure_class as FC  # noqa: E402

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
# Owner 2026-11-16 10:13 PM: "Test Pilot should also run as Fable 5.2 when it's called. For obvious reasons. And it should
# get that same inspirational prompting we worked out, just with a live game flare". The builders' steps
# (maturation.HOW_A_BAR_HOLDS; the positive steps verbatim) with the game as the instrument. The agent file carries the
# same section; selftest_testpilot_route pins both. The model: the agent file's `model:` line, which run_store.pilot_tier reads.
HOLDS = "HOW A SITTING HOLDS"     # the brief's marker for these steps (selftest pins it)
POSITIVE_STEPS = ("The owner's positive steps: Get inventive. Innovate; do not just tune, and do not just diagnose: "
                  "provide or repair what is broken. Provide bars where they are missing: that is not cheating, it is making "
                  "it harder on yourself. Create instruments to prove your diagnoses. Think outside the box: collapse "
                  "classes into one or invent new "
                  "ones as needed to find a way around the problem.")
HOLDS_LINES = [
    "%s (owner, 2026-11-16): the builders' steps, with the live game as your instrument." % HOLDS,
    "- " + POSITIVE_STEPS,
    "- Hunt parameter regimes and regions, not examples. One failing scene is a sample of a region: find its edges.",
    "- In every \"it cannot be done\" claim, tag each limit \"bar\" (the owner's) or \"our own rule\" (code, habit, a "
    "site or harness choice, an earlier builder's choice), and attack our own rules first. Then unify the two things in "
    "conflict into one, invent something that satisfies both, or propose a relaxation with its evidence (the map of "
    "where each holds, the failing moment). Relaxing a bar is never yours: it is a question to your parent.",
    "- You may not end with open cases. Every case you saw fail is fixed and committed, proved unreachable by a check "
    "you land, filed as its own item carrying the check that goes red and the captured failing moment, or is a hunt "
    "that stopped unresolved and left its whole record (standing_rulings.md §Live tests have three kinds, section 5). "
    "\"Unexplained\" with no record is not an ending; only what truly needs the owner stays open, as his question.",
    "- The game is the instrument: run experiments in it instead of code-and-retest.",
    "- First make the failure happen on demand, and capture it (state read, save, picture).",
    "- Vary one thing at a time across the regimes the game really produces: ordinary play conditions, weather "
    "unlocked, the mechanics switched on. Never judge a mechanic on a site that switches it off.",
    "- Read the game's own state, not only the picture, and prove any offline copy you reason from (a def dump, a save "
    "read, a script's model) agrees with the live game before you trust it.",
    "- At the first error storm, stop and read the FIRST exception in Player.log, not the loudest.",
    "- Never leave a broken game running: repair it live, or take it down by the reload rule, before you move on or stop.",
    "- Look at every capture before you keep it.",
    "- Show the owner the failing moment as a picture or a keeper save, with one question whose answer changes what "
    "gets built.",
    "- Two games exist on this machine (`python3 src/RimMandrake/Utils/game_instance.py status`): never report waiting "
    "for a game.",
    "- Never state spend.",
    "- The standing limits hold: no flyer flight test of any kind; never unpause while the owner is watching; the "
    "bridge rules.",
]


def counts(r):
    """A pass, a run whose writer named no outcome (as before), or an outcome that is the work's own (failure_class)."""
    return r.result == "pass" or not getattr(r, "outcome", None) or FC.read(r.outcome).counts


def left_out(runs):
    """-> {word: n} of the runs that no streak counts, for the verdict's words."""
    return FC.count(FC.read(r.outcome) for r in runs if not counts(r))[1]


def streaks(runs):
    """-> (non-pass runs in a row at the end of `runs`, the worst such count in one criterion or config, its name).
    Criteria and configs count apart, though they may share a name, and a run with a criterion counts in both."""
    whole, per = 0, collections.Counter()
    for r in runs:
        if not counts(r):       # no pass, and not the item's own failure: it neither counts nor ends a streak
            continue
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


def voids():
    """-> (the standing hand voids (run_void.active), None), or ({}, why) when the void file cannot be read: every run
    then counts, as the books had it, and the verdict says the voids are UNMEASURED. A verify run is voided by its run
    name, `<ID>/run-N@<config>` (RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS: a fail recorded because
    of a harness fault)."""
    try:
        import run_void
        return run_void.active(), None
    except Exception as e:  # noqa: BLE001 - could not look: nothing is voided, and that is said
        return {}, "%s: %s" % (type(e).__name__, e)


DEFAULT_RULE = "the streak is %d non-pass runs in a row (`pipe limit <ITEM> pilot_streak N` moves one item's)" % STREAK


def _runs(item, evs, void):
    sat = _last_note(evs, item, SAT)
    return [r for r in item.runs if r.index > sat and r.config not in NOT_A_TEST and r.name not in void]


def streak_count(item, evs, void):
    """-> (the item's streak: the worse of its whole-item and one criterion or config non-pass runs in a row since its
    last sitting, voided runs out; whole; worst; worst's name). The pipeline's own count of the `pilot_streak`
    account (pipeline_control.m_pilot_streak reads it too)."""
    runs = _runs(item, evs, void)
    whole, worst, key = streaks(runs)
    return max(whole, worst), whole, worst, key


def judge(item, evs, void=None, unread=None, adjusted=None):
    """-> None, or {"id", "kind": streak|wanted|diagnose, "why"} for an item that goes to a Test Pilot. Pure given
    `void` ({run name: void line}; None reads the standing voids): a voided run is in no streak. The streak is the
    item's `pilot_streak` account (RIMMANDRAKE_TYPE_PILOT_STREAK_AS_ITEM_ACCOUNT_ALREADY_ORDERED): its count and limit
    are read through the control store, so `pipe add|limit <ITEM> pilot_streak` moves the verdict. `adjusted`: the
    item ids holding a live adjustment (pipeline_control.subjects, read once by `routed`), or None to ask the store
    for this item; a string is the store's read error. An unreadable store routes by the derived count and the
    default limit, nothing new, and the verdict says so."""
    if item.state not in OPEN_STATES or item.blocked or item.needs == "owner" or "_JUDGE_" in item.id:
        return None
    if void is None:
        void, unread = voids()
    n, whole, worst, key = streak_count(item, evs, void)
    u, lim, blind = n, STREAK, adjusted if isinstance(adjusted, str) else None
    if blind is None and (adjusted is None or item.id in adjusted):
        try:
            import pipeline_control as PC
            u, lim = PC.used(item.id, "pilot_streak", n), PC.limit(item.id, "pilot_streak", STREAK)
        except Exception as e:  # noqa: BLE001 - could not look: the derived count and default stand, and that is said
            u, lim, blind = n, STREAK, "%s: %s" % (type(e).__name__, e)
    if u >= lim:
        where = "in a row" if whole >= worst else "in a row on %s" % key
        out = FC.named(left_out(_runs(item, evs, void)))
        return {"id": item.id, "kind": "streak", "why": "%d non-pass runs %s%s%s%s%s" % (
            n, where, "; not counted: %s" % out if out else "", "" if (u, lim) == (n, STREAK) else " (account %d of limit %d, pipe pilot_streak)" % (u, lim),
            "; the void ledger is UNMEASURED (%s): no run was taken out" % unread if unread else "",
            "; the control store is UNMEASURED (%s): the derived count and limit %d stood" % (blind, STREAK)
            if blind else "")}
    sat = _last_note(evs, item, SAT)
    if _last_note(evs, item, WANTED) > sat:
        return {"id": item.id, "kind": "wanted", "why": "a seat asked for live observation"}
    if "_DIAGNOSE_" in item.id and item.needs in LIVE_NEEDS and sat < 0:
        return {"id": item.id, "kind": "diagnose", "why": "a DIAGNOSE that needs the live game"}
    return None


def routed(world, evs):
    """-> every judge() verdict, in no promised order. The control store is read once for the items holding a
    `pilot_streak` adjustment; an unreadable store is said in each streak verdict."""
    void, unread = voids()
    try:
        import pipeline_control as PC
        adjusted = PC.subjects("pilot_streak")
    except Exception as e:  # noqa: BLE001 - could not look: judge() says so on each verdict it gives
        adjusted = "%s: %s" % (type(e).__name__, e)
    return [v for v in (judge(item, evs, void, unread, adjusted) for item in world.items.values()) if v]


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


HOST_NOTES = {
    "stevedesktop": "Every live call runs on SteveDesktop: ssh \"$STEVE_WSL\" 'cd ~/rm/runner && ...'. That clone is "
                    "read-only to you; code and deploys go by remote_modcheck.sh --sync --no-run from your own clone. "
                    "A running testq job holds the guard: a refused take means pick the other host, never --force.",
    "archmagi": "Archmagi: back up ModsConfig.xml before any list change and restore it with the game down at the "
                "end. Take with --idle-ok; his OWNER hold still refuses, and then you pick the other host.",
}
# a detached run that IS the sitting (the Maturation tick's Test Pilot step, RIMMANDRAKE_ROUTE_SPENT_LIVE_FIXER_PILOT_BY_HAND)
SIT = ("You are this sitting: a RimMandrake builder in the Sitting setting (the Test Pilot, rm-testpilot). Read "
       "`src/RimMandrake/rimflow/roles/builder.md` in full first, as your role file, and load the `test-pilot-sitting` "
       "skill: it is your method. Do not spawn a subagent: you sit. One sitting, one item.")


# the same, for a sitting launched as `claude --agent rm-testpilot` (detached_helper AGENT_ENV): the agent file is its
# system prompt and only points at the builder role, so a Read of the agent file would put it into every later request
# twice (RIMMANDRAKE_STOP_RESUME_REWRITING_CONTEXT_A_MILLION_AT_ONCE); the role is read once
SIT_AGENT = ("You are this sitting: a RimMandrake builder in the Sitting setting (the Test Pilot, rm-testpilot). You were "
             "launched as that agent, so `.claude/agents/rm-testpilot.md` is your system prompt: do not Read it again. "
             "Read `src/RimMandrake/rimflow/roles/builder.md` in full once: it is your role. Load the "
             "`test-pilot-sitting` skill: it is your method. Do not spawn a subagent: you sit. One sitting, one item.")
PROGRESS_LINE = ("After each experiment, write your progress record on the item: `rimflow note <ID> --text \"PROGRESS: "
                 "theory: ... | experiment: ... | reading: ... | next: ...\"`. A stopped sitting with a large context is "
                 "carried on by a fresh session that has only this brief and those notes.")


def brief(verdict, host, detached=False, agent=False):
    """The ready-to-paste brief for an rm-testpilot subagent on `host`; detached: the brief of a run that is the sitting
    itself (agent: launched as `--agent rm-testpilot`), and host None: the sitting picks the first free host when it
    starts."""
    i = verdict["id"]
    lines = [(SIT_AGENT if agent else SIT) if detached else
             "Spawn subagent_type rm-testpilot with model \"fable\" (Fable 5.2, owner 2026-11-16) and this brief. One "
             "sitting, one item.",
             "",
             "Item %s. Routed by the Test Pilot rule: %s." % (i, verdict["why"])]
    if host is None:
        lines += ["Host: the first free one of %s (`python3 src/RimMandrake/rimflow/cli.py pilot %s` names it). Take: "
                  "rimflow bridge take --host <host> --for \"test pilot %s\"" % (", ".join(HOSTS), i, i)]
        lines += ["On %s: %s" % (h, HOST_NOTES[h]) for h in HOSTS]
    else:
        lines += ["Host: %s. Take: rimflow bridge take --host %s --for \"test pilot %s\"" % (host, host, i),
                  HOST_NOTES["stevedesktop" if host == "stevedesktop" else "archmagi"]]
    # LIVE_FAILURES_EXPLAIN_MORE_THAN_A_LABEL (owner 2026-11-04): "Make sure the Test Pilot's job is to EXPLAIN the
    # failure, not just try to execute a test. ... Then there needs to be follow-up work to address them."
    lines += ["Read first: `rimflow show %s` and Player.log's first exception." % i, PROGRESS_LINE.replace("<ID>", i)] \
        + HOLDS_LINES
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
