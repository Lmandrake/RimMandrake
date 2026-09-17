"""validation.py -- modcheck suite for RimMandrake StrandedQuest
(mandrake.rm.strandedquest).

Grounded in the mod's actual (and ENTIRE) source: `Defs/QuestScriptDefs/
Quest_Stranded.xml` (the one QuestScriptDef) and `Defs/HistoryEventDefs/
HistoryEvents_Stranded.xml` (the one goodwill reason), both read whole, plus
`design/validation_walks/RimMandrake/StrandedQuest.md`. There is no C# here
at all -- pure XML on vanilla RimWorld.QuestGen nodes, confirmed by `find
src/RimMandrake/StrandedQuest -name '*.cs'` returning nothing. No Mod
Settings class exists either, so `suite.toggles` is empty (nothing to gate).

WHAT THIS MOD ACTUALLY DOES: a `QuestNode_Sequence` finds a nearby
settlement (`QuestNode_GetNearbySettlement`, `maxTileDistance=32`), drops one
factionless `SpaceRefugee` pawn on the map (`QuestNode_GeneratePawn` with
`addToList=lodgers`, then `QuestNode_PawnsArrive` with `joinPlayer=false`,
`arrivalMode=RandomDrop`), and starts a `randInt(6,10)*60000`-tick shown
timer. On timeout (`outSignalComplete=PickupDue`) the quest gives a standard
reward and ends Success; the lodger leaves on cleanup regardless
(`QuestNode_LeaveOnCleanup`). Recruiting/enslaving/arresting the lodger ends
the quest Fail with goodwill -12/-20/-12 against the asker's faction
(reason `RM_StrandedTravellerTaken` in all three); the lodger dying ends
Fail with -6 (reason `QuestPawnLost`, vanilla's own def); the lodger walking
off ends Unknown with no goodwill change.

HOW THE THREE "TAKEN" SIGNALS ACTUALLY FIRE -- traced through Assembly-CSharp
via RimSage, not assumed from the XML alone, because `addToList=lodgers`
gives no hint by itself that a signal named "lodgers.Recruited" will ever
exist:
  `QuestNode_Signal`'s `inSignal="lodgers.Recruited"` runs through
  `QuestGenUtility.HardcodedSignalWithQuestID`, which (for any dotted signal
  not already namespaced) calls `QuestGen.AddSlateQuestTagToAddWhenFinished
  ("lodgers")` -- so at the END of quest generation the framework walks the
  slate's `lodgers` list and stamps a per-quest tag (e.g. "Q7/lodgers") onto
  every pawn in it via `Pawn.questTags`. The three outcomes are then plain
  `QuestUtility.SendQuestTargetSignals(pawn.questTags, "<Part>", ...)` calls
  made from THREE DIFFERENT, UNRELATED call sites, each reachable by a
  different bridge tool (or not reachable at all):
    * "Recruited" -- `InteractionWorker_RecruitAttempt.DoRecruit`, line 197
      of that file, ONLY on the humanlike branch. `jawa/instant_recruit`
      calls this exact method (its own tool description: "InteractionWorker_
      RecruitAttempt.DoRecruit"). `jawa/set_pawn_faction(recruit=true)` does
      NOT reach this signal -- its own tool description says it "calls only
      the bare RecruitUtility.Recruit", and reading `RecruitUtility.Recruit`
      confirms it: apparel unlock, `SetFaction`, `guest.Notify_
      PawnRecruited()` (which only clears `slaveFactionInt`) -- no
      `SendQuestTargetSignals` call anywhere in it. Using the wrong tool
      here would silently prove nothing.
    * "Enslaved" -- `InteractionWorker_EnslaveAttempt.Interacted`, fired only
      once a prisoner's `guest.will` reaches 0 through repeated
      ReduceWill interactions (a real, ticking social-interaction loop) AND
      `TryEnslavePrisoner` succeeds. `jawa/pawn_set_guest_status` (Slave)
      calls `Pawn_GuestTracker.SetGuestStatus` directly, and reading THAT
      method shows its only quest-signal call is `SendQuestTargetSignals
      (..., "ChangedHostFaction", ...)` -- never "Enslaved". No bridge tool
      reaches the real call site.
    * "Arrested" -- `JobDriver_TakeToBed`, fired from inside a warden's own
      Arrest job toil on a downed pawn being carried to a prison bed -- a
      multi-tick job, not a single settable field, and nothing on this
      bridge drives that specific job to completion and reads the signal
      back independently of the job simply finishing.
  So of the three, only Recruited is provably drivable from this bridge in
  one call; Enslaved and Arrested are REAL, documented gaps below, not
  oversights.

A REAL, ENGINE-LEVEL PRECONDITION RISK, also traced rather than guessed:
`QuestGen.Generate()` calls `root.Run()` with NO preceding TestRun pass (that
pass only exists for the *storyteller's* natural-fire selection, which
`jawa/fire_quest` bypasses on purpose). `QuestNode_GetNearbySettlement.
RunInt()` does `settlement.Faction` with no null-check, while its own
`RandomNearbyTradeableSettlement` returns null with nothing in range --
so on a quicktest map with no AI settlement within `maxTileDistance=32`
(same distance the walk doc itself flags at step 4), quest generation throws
a `NullReferenceException` inside `Generate()`'s own try/catch, which logs
"Error in QuestGen" and returns null, and `jawa/fire_quest` reports Fail from
its own try/catch around `GenerateQuestAndMakeAvailable`. This is a real
engine trap (not this mod's bug), but it means `quest_fires_and_lodger_
arrives` below can only run where a real settlement sits within 32 tiles of
the test map's tile -- this is an environmental precondition, not a toggle.

Still not proven / likely first-live-run corrections:
  1. The Enslaved and Arrested Fail branches (goodwill -20 / -12) are
     UNCOVERED -- no bridge tool reaches either real signal call site (see
     above). A future pass could drive Arrested through `jawa/ordered_job`
     with a JobDef of "Arrest" against a downed lodger, once someone
     confirms `jawa/ordered_job` can force a job whose driver requires a
     downed target; Enslaved has no forceable path at all without a new
     bridge tool (e.g. a raw `SendQuestTargetSignals` test hook).
  2. No bridge tool reports a goodwill change's RECORDED REASON (the
     `HistoryEventDef` shown on the faction tab) -- `jawa/faction_relations_
     get` reports only the numeric goodwill, so `ordered_reading...` -style
     reason confirmation (as Antiquities does via inspect strings) has no
     equivalent here. The suite can prove the -12 delta happened, not that
     it was filed under `RM_StrandedTravellerTaken` specifically.
  3. `lodgers.LeftMap` (Unknown, no goodwill change) and `map.MapRemoved` /
     `faction.BecameHostileToPlayer` (both Fail) are UNCOVERED -- forcing a
     factionless pawn off the map, or a faction hostile flip, mid-chain adds
     a second live mutation this pass did not attempt; left for a future
     pass rather than faked.
  4. Which faction is actually "the asker" is never known ahead of time
     (`QuestNode_GetNearbySettlement` picks randomly among everything in
     range) -- `recruiting_lodger_fails_quest_and_costs_goodwill` identifies
     the affected pair by DIFFING the whole `jawa/faction_relations_get`
     matrix before/after the recruit, not by naming a faction. This assumes
     no other goodwill-changing event fires in the same tick window
     (`clear_area` + a fresh chain make that likely, not certain).
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("StrandedQuest")
suite.toggles = []   # no Mod Settings class ships with this mod -- confirmed
                      # by `find src/RimMandrake/StrandedQuest -iname "*Settings*"`

QUEST = "RM_Stranded"
LODGER_KIND = "SpaceRefugee"
TAKEN_REASON = "RM_StrandedTravellerTaken"
GOODWILL_RECRUITED = -12


def _find_lodger(t):
    r = t.bridge_call("jawa/list_pawns", limit=200)
    rows = (r or {}).get("pawns") or []
    for p in rows:
        if p.get("kind") == LODGER_KIND and not p.get("faction"):
            return p
    return None


@suite.chain("quest_fires_and_lodger_arrives")
def quest_fires_and_lodger_arrives(t):
    """`jawa/fire_quest` bypasses the storyteller's own selection weight
    entirely (see module docstring on why that also means no TestRun pass
    runs first) and generates+accepts RM_Stranded directly. Proves the
    quest is actually IN the manager as Ongoing and that exactly one
    factionless SpaceRefugee landed on the map -- NOT that the storyteller
    would ever pick it on its own (rootSelectionWeight/rootMinProgressScore/
    minRefireDays are unexercised by this route, same as every other
    `jawa/fire_quest`-based check on this bridge)."""
    t.clear_area(size=30)
    with t.component("lodger_arrives_factionless", beyond_toggle=True):
        r = t.bridge_call("jawa/fire_quest", questDef=QUEST, accept=True)
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/fire_quest(%s, accept=True) reported failure -- most likely "
                "no Settlement is within QuestNode_GetNearbySettlement's "
                "maxTileDistance=32 of this map's tile (see module docstring's "
                "NullReferenceException note): %r" % (QUEST, r))

        listed = t.bridge_call("jawa/quest_lifecycle", action="list")
        rows = (listed or {}).get("quests") or []
        match = next((q for q in rows if q.get("name") and QUEST in str(q.get("name"))
                      or q.get("id") == (r or {}).get("id")), None)
        if match is None:
            match = next((q for q in rows if q.get("state") == "Ongoing"), None)
        if match is None or match.get("state") != "Ongoing":
            raise ExpectationFailed(
                "no Ongoing quest found in jawa/quest_lifecycle(list) after firing "
                "%s: %r" % (QUEST, rows))

        lodger = _find_lodger(t)
        if lodger is None:
            raise ExpectationFailed(
                "no factionless %s pawn found via jawa/list_pawns after firing "
                "%s (RandomDrop arrival may not have landed on this map, or the "
                "quest generated with no pawns)" % (LODGER_KIND, QUEST))
        t.screenshot()


@suite.chain("recruiting_lodger_fails_quest_and_costs_goodwill")
def recruiting_lodger_fails_quest_and_costs_goodwill(t):
    """Drives the ONE of the three "Taken" branches that a bridge tool can
    actually reach (see module docstring): `jawa/instant_recruit` calls
    `InteractionWorker_RecruitAttempt.DoRecruit`, the one real call site
    that sends the `lodgers.Recruited` quest-tag signal for a humanlike
    pawn. Proves the quest ends and the goodwill hit lands -- does NOT
    identify the asker faction by name (see docstring #4), and does NOT
    confirm the goodwill change's recorded reason (see docstring #2)."""
    t.clear_area(size=30)
    with t.component("recruit_ends_quest_fail_goodwill_minus_12", beyond_toggle=True):
        r = t.bridge_call("jawa/fire_quest", questDef=QUEST, accept=True)
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/fire_quest(%s, accept=True) failed -- see module docstring's "
                "settlement-in-range precondition: %r" % (QUEST, r))

        lodger = _find_lodger(t)
        if lodger is None:
            raise ExpectationFailed(
                "no factionless %s pawn found after firing %s" % (LODGER_KIND, QUEST))
        lodger_id = lodger.get("id")

        before = t.bridge_call("jawa/faction_relations_get", includeNeutral=True)
        before_pairs = {(p.get("a"), p.get("b")): p.get("goodwill")
                         for p in ((before or {}).get("pairs") or [])}

        rec = t.bridge_call("jawa/instant_recruit", pawn=lodger_id, audiovisual=False)
        if not (rec or {}).get("success") or rec.get("after") != "PlayerColony" and \
           not rec.get("isColonist"):
            raise ExpectationFailed(
                "jawa/instant_recruit(%s) did not report a successful recruit: %r"
                % (lodger_id, rec))

        after = t.bridge_call("jawa/faction_relations_get", includeNeutral=True)
        after_pairs = {(p.get("a"), p.get("b")): p.get("goodwill")
                       for p in ((after or {}).get("pairs") or [])}

        drops = [(k, before_pairs.get(k), v) for k, v in after_pairs.items()
                 if k in before_pairs and before_pairs[k] != v
                 and (v - before_pairs[k]) == GOODWILL_RECRUITED]
        if not drops:
            raise ExpectationFailed(
                "no faction pair dropped by exactly %d goodwill after recruiting "
                "the lodger -- expected the asker's goodwill-with-player pair to "
                "move by QuestNode_End's own goodwillChangeAmount. before/after "
                "diffs with any change: %r"
                % (GOODWILL_RECRUITED,
                   [(k, before_pairs.get(k), v) for k, v in after_pairs.items()
                    if before_pairs.get(k) != v]))

        listed = t.bridge_call("jawa/quest_lifecycle", action="list")
        rows = (listed or {}).get("quests") or []
        still_ongoing = any(q.get("historical") is False and
                             (QUEST in str(q.get("name") or "")) for q in rows)
        if still_ongoing:
            raise ExpectationFailed(
                "RM_Stranded is still non-historical after recruiting the lodger -- "
                "expected QuestNode_End(outcome=Fail) on lodgers.Recruited to have "
                "closed it: %r" % rows)
        t.screenshot()
