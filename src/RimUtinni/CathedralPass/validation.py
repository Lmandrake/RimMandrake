"""validation.py -- first north-star script for RimUtinni: CathedralPass (mandrake.rut.cathedralpass).

CATHEDRAL_MECHANOID_PASS_VERBS_1. Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run CathedralPass

INTENDED FUNCTION (About.xml): a clan pawn carrying RUT_CathedralPass is read as non-hostile by faction-13
(Faction.OfMechanoids) machines, on Rust Cathedral maps (RM_RustCathedral) only, gated by
the cathedralPassEnabled setting.

WHAT IT PROVES (live, through existing bridge tools):
  * every Mod Settings bool flips and reads back through jawa/mod_settings_field
  * GenHostility.HostileTo lists this mod's Harmony id as an owner (jawa/harmony_patches)
  * the shipped HediffDef is loaded and its scalar fields read back equal to the XML

CATHEDRAL_MISSION_BOON_OFFERS_1 (the favours) -- offline proof: src/RimMandrake/RustCathedral/
selftest_rustcathedral_offers.py. Static here: the favour defs load (shipped_defs sanity below) and their strings
pass cathedral_arc_lint at stage 1 (favour_text_problems).

LIVE RUN RECIPE (the item's last criterion: >=1 mission shape + the boon-offer gate end to end on a quicktest).
Bridge held by the live lane; every step reads its result back, none is assumed:
  0. Build + deploy: winbuild.py src/RimUtinni/CathedralPass/Source/RimMandrake.Utinni.CathedralPass.csproj;
     deploy_custom_mods.py --mod CathedralPass (plan) then --apply. Companion: JawaBench built with --gm
     (jawa/storyteller_fire is #if JAWA_GM_TOOLS) and with the quest_lifecycle `root` field (daeea61eb8); without
     `root` the blackboard falls back to matching the quest's fixed name. Mod list: Harmony + CathedralPass + all
     five DLC (+ JawaBench); a quicktest map is enough -- no Cathedral biome needed for the quest itself.
  1. Defs loaded: jawa/get_defs for RUT_CathedralAssailantMission_EnclaveRunner (QuestScriptDef) and
     RUT_CathedralGravtechBoon_Gravcore (IncidentDef). Player.log: no "Could not find type" for
     RimMandrake.Utinni.CathedralPass.* (a missing Class throws the whole def away).
  2. Mission offer: jawa/storyteller_fire incidentDef=RUT_GiveQuest_CathedralAssailantMission_EnclaveRunner
     dryRun=true (canFireNow must be true), then dryRun=false. jawa/quest_lifecycle action=list: a row
     name "A request from the enclaves", root RUT_CathedralAssailantMission_EnclaveRunner, state NotYetAccepted.
     Screenshot the quest tab: description is the def text, and NO asker / faction is shown.
  3. Mission run: quest_lifecycle action=accept questId=<id>. Expect the "The pack the enclaves warned of" letter
     and a manhunter pack on the map (jawa/list_things or map pawns). Exploit check first: spawn a tame animal of the
     pack's race for the colony and kill it -- the quest must stay Ongoing (RUT_QuestPart_PackDown counts only
     pawns carrying the quest's tag; vanilla QuestNode_PawnsKilled would have counted it). Then jawa/kill_hostiles;
     expect the "The pack is down" letter and state EndedSuccess. A pack that never arrives within 2 days, or walks
     off alive, fails the quest by design (no Regard).
  4. Regard feedback live: gm_blackboard_shadow.py --polls 2 --log <file> (live, no --fixture): the poll after
     step 3 logs mission_completions_this_poll=1 and mission_completion_regard_gain_this_poll=4.0, heat unchanged.
  5. Boon gate: gm_blackboard_shadow.py live with --story-flags-file holding {"assailant_mission_completions": 3,
     "restore_choice_made": true} on a Cathedral-ground map (biome RM_RustCathedral) so posture reaches VOUCHED in
     ~6 polls; read cathedral_offers.boons[*].state == open and a cathedral_boon_offer would_fire. Then fire it:
     jawa/storyteller_fire incidentDef=RUT_CathedralGravtechBoon_Gravcore dryRun=false -> letter "A gravcore in
     the sand" and one Gravcore at the trade drop spot (jawa/list_things defName=Gravcore count +1). Heat side:
     drop the colony's Force_KyberCrystal count by 2 between polls (sell to a trader, or destroy for the read):
     the next poll's Gravcore row reads withheld_heat and no boon would_fire, same stage.
  6. Settings: jawa/mod_settings_field cathedralBoonsEnabled=false -> storyteller_fire dryRun=true canFireNow false.
  7. Go-dark withdrawal: with a request fired but not accepted, run the blackboard with --pursuit-event-on-poll N
     --exposure-godark-threshold 15: poll N logs cathedral_mission_offer_withdrawn naming the quest id; the firer's
     act is jawa/quest_lifecycle action=end questId=<id> outcome=unknown sendLetter=false (the blackboard itself is
     read-only); the list then reads EndedUnknownOutcome and no request or gift is offered for 10 game days.
  8. CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1 -- the survey, all three branches (offline proof:
     src/RimMandrake/RustCathedral/selftest_rustcathedral_survey.py). Mod list as above plus EmpirePursuit (the pursuit
     spine), on a scenario whose pursuit faction is the Empire. jawa/get_defs RUT_CathedralSurveyMisdirection
     (QuestScriptDef) and RUT_CathedralSurveyHail (LetterDef); Player.log has no "Could not find type
     RimMandrake.Utinni.CathedralPass.RUT_*". Three rounds, one per answer (b, c, a), each:
       - jawa/storyteller_fire incidentDef=RUT_GiveQuest_CathedralSurveyMisdirection dryRun=true (canFireNow true), then
         dryRun=false. quest_lifecycle list: a row root RUT_CathedralSurveyMisdirection, state Ongoing (auto-accepted),
         and NOT on the Quests tab (hidden). The letter stack holds "An Imperial survey hails the ship"; open it: the
         faction strip shows the pursuing faction, the text names it in place of {FACTION}, four buttons (three answers
         + Postpone). Screenshot it.
       - (b) "Give him the guild's answer..." -> letter "The survey moves on", row EndedSuccess; blackboard poll after:
         survey_regard_gain_this_poll=12.0, heat unchanged against the poll before.
       - (c) "Tell him what the crews have seen..." -> a drop pod with 150~250 silver at the trade drop spot, letter
         "The survey stays", row EndedFailed; blackboard: survey_exposure_gain_this_poll=20.0, heat unchanged.
       - (a) "Leave the channel unanswered" -> letter "The channel goes quiet", row EndedUnknownOutcome; nothing moves.
         Also once with no answer: step 2 game days; the hail letter leaves the stack, "The survey leaves", Unknown.
       - Save and reload with a hail unanswered: the letter is still there and still answers (part found by quest).
     Settings: jawa/mod_settings_field cathedralSurveyEnabled=false -> storyteller_fire dryRun=true canFireNow false.
NOT PROVEN offline (owed to that run): that QuestNode_ManhunterPack's pack spawns on accept with the quest tag
and that RUT_QuestPart_PackDown sees it to EndedSuccess in this mod list; that the boon lands at TradeDropSpot on a
gravship map.

NOT PROVEN HERE (first pokes for the next live pass -- the item's own verify bar):
  * on a Cathedral-biome quicktest with hostile faction-13 mechs, MANY pass-holders are untargeted and
    non-holders are targeted (one pawn is RNG)
  * the same pawns ARE targeted on a non-Cathedral map (scope holds)
  * revoking (debug action "Revoke pass") returns targeting; no manhunt/raid behaviour introduced
  * war-lab access unchanged with the pass held (the war lab is not a Cathedral-biome map)
  * GM-verb GRANT/REVOKE: not built (CATHEDRAL_REGARD_BLACKBOARD_1 unbuilt)

STATIC (offline): `python3 validation.py` runs modcheck.mod_static over the mod.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from modcheck import mod_static  # noqa: E402


def favour_text_problems():
    """Every player-facing string in the favour defs passes the arc linter at TOLERATED (the earliest stage any of
    them can appear), and the linter actually read them."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cathedral_arc_lint", os.path.join(REPO, "src", "RimMandrake", "RustCathedral", "cathedral_arc_lint.py"))
    lint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lint)
    seen, bad = [], []
    for rel in ("Defs/QuestScriptDefs/RUT_CathedralAssailantMissions.xml", "Defs/IncidentDefs/RUT_CathedralFavours.xml"):
        bad += lint.xml_findings(os.path.join(HERE, rel), 1, seen)
    # CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1: the survey can come at any stage, so its strings meet the any-stage rules
    for rel in ("Defs/QuestScriptDefs/RUT_CathedralSurveyMisdirection.xml", "Defs/IncidentDefs/RUT_CathedralSurvey.xml"):
        bad += lint.xml_findings(os.path.join(HERE, rel), -1, seen)
    if len(seen) < 45:
        bad.append("favours: only %d strings read from the favour defs (sanity probe failed)" % len(seen))
    return bad


def static_checks():
    return mod_static.static_findings(HERE) + favour_text_problems()


def _build_suite():
    from modcheck import Suite, ExpectationFailed, shipped_defs  # noqa: F401
    suite = Suite("CathedralPass")
    suite.toggles = sorted(mod_static.bool_settings(HERE))

    mod_static.add_settings_chain(suite, __file__)
    mod_static.add_harmony_chain(suite, __file__)
    shipped_defs.add_chain(suite, __file__, sanity=('RUT_CathedralPass', 'RUT_CathedralGravtechBoon_Gravcore',
                                                    'RUT_CathedralAssailantMission_EnclaveRunner',
                                                    'RUT_CathedralSurveyMisdirection'), min_count=1)
    return suite


try:
    suite = _build_suite()
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL (%d)" % len(problems)))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
