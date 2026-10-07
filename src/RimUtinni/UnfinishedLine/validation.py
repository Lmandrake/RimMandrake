"""validation.py -- first script for RimUtinni: The Unfinished Line (mandrake.rut.unfinishedline).

UNFINISHED_LINE_SPINE_COUNT_1 (split from DROID_MASS_PRODUCTION_QUEST_CHAIN_1). Walk:
design/validation_walks/RimUtinni/UnfinishedLine.md. Run:

    python3 src/RimUtinni/UnfinishedLine/validation.py                      offline: STATIC PASS/FAIL
    python.exe src/RimMandrake/Utils/modcheck/cli.py run UnfinishedLine      live

Environment: a list carrying the two authored factions (mandrake.rut.patches: RUT_Jawa_FreeDroidEnclaves and
RUT_Jawa_GeonosianFoundryHive, each with a settlement on the world), Droidworks, Droid Repair Jobs, this mod,
every DLC. Every live proof goes through jawa/static_call into RimMandrake.Utinni.UnfinishedLine.UnfinishedLineProof,
so nothing waits on the storyteller. NEVER RUN LIVE YET.
"""
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

from modcheck import Suite, ExpectationFailed  # noqa: E402

suite = Suite("UnfinishedLine")
suite.toggles = ["chainEnabled", "brokeredTruceEnabled", "coreBrokerEnabled", "lendSkillGateEnabled",
                 "lineInWorldEnabled", "empireStrikesEnabled"]

PROOF = "RimMandrake.Utinni.UnfinishedLine.UnfinishedLineProof"
SETTINGS_TYPE = "RimMandrake.Utinni.UnfinishedLine.UnfinishedLineSettings"
PARENT = "RUT_UnfinishedLine"
BEAT1 = "RUT_UnfinishedLine_1_Count"
BEAT2 = "RUT_UnfinishedLine_2_Envoy"
BEAT3 = "RUT_UnfinishedLine_3_Cores"
BEAT4 = "RUT_UnfinishedLine_4_Tithe"
NEEDLES = ("mandrake.rut.unfinishedline", "UnfinishedLine", "RUT_LineCount", "QuestPart_RUT_SequentialSubquests")


def _proof(t, method, args=None):
    kw = dict(type=PROOF, method=method)
    if args is not None:
        kw["args"] = args
    r = t.bridge_call("jawa/static_call", **kw)
    return str((r or {}).get("result", "")) or "no result: %r" % (r,)


@suite.chain("load_clean")
def load_clean(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


@suite.chain("defs")
def defs(t):
    with t.component("all_defs_resolve", beyond_toggle=True):
        want = ["QuestScriptDef/%s" % PARENT, "QuestScriptDef/%s" % BEAT1, "QuestScriptDef/%s" % BEAT2, "QuestScriptDef/%s" % BEAT3, "QuestScriptDef/%s" % BEAT4, "QuestScriptDef/RUT_UnfinishedLine_5_FirstLight",
                "HistoryEventDef/RUT_LineHandsLost",
                "HistoryEventDef/RUT_UnfinishedLineCompleted",
                "IncidentDef/RUT_UnfinishedLine_Offer", "SitePartDef/RUT_SilicaxFoundryRuin", "ThingDef/RUT_FoundryPatternCore",
                "MentalStateDef/RUT_WildDroidPack", "LetterDef/RUT_CoreBrokerOffer",
                "FactionDef/RUT_Jawa_FreeDroidEnclaves", "FactionDef/RUT_Jawa_GeonosianFoundryHive"]
        r = t.bridge_call("jawa/get_defs", defs=";".join(want), fields="defName")
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed("get_defs failed: %r" % r)
            if r.get("notFound"):
                raise ExpectationFailed("defs missing: %r" % r.get("notFound"))


@suite.chain("gates")
def gates(t):
    with t.component("gate_report_reads", beyond_toggle=True):
        text = _proof(t, "ProofGates")
        if t._guard() and not text.startswith("GATES "):
            raise ExpectationFailed("ProofGates returned no gate report: %s" % text)
    with t.component("disabled_chain_closes_the_gate", toggle="chainEnabled"):
        t.set_setting(SETTINGS_TYPE, {"chainEnabled": False})
        try:
            text = _proof(t, "ProofGates")
        finally:
            t.set_setting(SETTINGS_TYPE, {"chainEnabled": True})
        if t._guard() and "chain disabled" not in text:
            raise ExpectationFailed("chainEnabled OFF but the gate did not say so: %s" % text)


@suite.chain("chain")
def chain(t):
    with t.component("parent_offers_and_accepts", beyond_toggle=True):
        text = _proof(t, "ProofOffer", "true")
        if t._guard() and not (text.startswith("CHAIN Ongoing") and "part Enabled" in text):
            raise ExpectationFailed("the chain did not start on acceptance: %s" % text)
    with t.component("first_beat_is_the_count", beyond_toggle=True):
        text = _proof(t, "ProofNextBeat")
        if t._guard() and not (text.startswith("OFFERED %s" % BEAT1) and ("%s:NotYetAccepted" % BEAT1) in text):
            raise ExpectationFailed("forcing the next beat did not offer The Count: %s" % text)
    with t.component("one_beat_at_a_time", beyond_toggle=True):
        text = _proof(t, "ProofNextBeat")
        if t._guard() and "already offered" not in text:
            raise ExpectationFailed("a second beat was offered while the first was pending: %s" % text)


@suite.chain("truce")
def truce(t):
    """UNFINISHED_LINE_ENVOY_BEAT_1 (owner Q2 'both'): the brokered truce floors the Hive at Neutral. Not proven
    here: the truce starting on beat-2 acceptance and breaking (Hive hostile, chain failed) when an envoy dies --
    first poke: accept The Envoy via ProofNextBeat after a forced Count success, kill an overseer, read ProofChain."""
    with t.component("truce_holds_hive_neutral", toggle="brokeredTruceEnabled"):
        text = _proof(t, "ProofTruce", "true")
        try:
            gw = int(text.split("hive goodwill ")[1].split(" ")[0])
        except (IndexError, ValueError):
            gw = None
        if t._guard() and not (text.startswith("TRUCE active") and gw is not None and gw >= 0):
            raise ExpectationFailed("the truce did not hold the Hive at goodwill >= 0: %s" % text)
    with t.component("truce_off_does_nothing", toggle="brokeredTruceEnabled"):
        _proof(t, "ProofTruce", "false")
        t.set_setting(SETTINGS_TYPE, {"brokeredTruceEnabled": False})
        try:
            text = _proof(t, "ProofTruce", "true")
        finally:
            t.set_setting(SETTINGS_TYPE, {"brokeredTruceEnabled": True})
            _proof(t, "ProofTruce", "false")
        if t._guard() and not text.startswith("TRUCE off"):
            raise ExpectationFailed("brokeredTruceEnabled OFF but a truce started: %s" % text)


@suite.chain("wild_pack")
def wild_pack(t):
    """UNFINISHED_LINE_CORES_BEAT_1: the ruin's wild droids are a pack (not hostile to each other), still hostile to you."""
    with t.component("pack_does_not_fight_itself", beyond_toggle=True):
        text = _proof(t, "ProofWildPack", "3")
        if t._guard() and not ("in pack state 3" in text and "mutual hostile pairs 0" in text and "hostile to player 3" in text):
            raise ExpectationFailed("wild-droid pack contract broken: %s" % text)


@suite.chain("cores")
def cores(t):
    """UNFINISHED_LINE_CORES_BEAT_1: walk the chain to beat 3, carry the cores home, answer the broker. Run on a
    throwaway save: the 'sell' component turns both factions hostile. Not proven here: the site map's hall and pack
    (first poke: accept the beat, form a caravan to the site, screenshot), and Released->goodwill (capture one, release it)."""
    with t.component("beat3_offered_after_two_successes", beyond_toggle=True):
        _proof(t, "ProofOffer", "true")
        _proof(t, "ProofNextBeat")
        _proof(t, "ProofEndBeat", "true")
        _proof(t, "ProofNextBeat")
        _proof(t, "ProofEndBeat", "true")
        text = _proof(t, "ProofNextBeat")
        if t._guard() and not text.startswith("OFFERED %s" % BEAT3):
            raise ExpectationFailed("after two successes the spine did not offer The Pattern Cores: %s" % text)
    with t.component("cores_home_raises_the_broker", toggle="coreBrokerEnabled"):
        _proof(t, "ProofCores", "home")  # accepts the offered beat first
        t.bridge_call("rimworld/step_game_ticks", ticks=300, pauseFirst=True, timeoutMs=120000)
        text = _proof(t, "ProofCores", "state")
        if t._guard() and not ("home True" in text and "decided False" in text and "broker deadline -1" not in text):
            raise ExpectationFailed("all three cores home did not raise the broker's offer: %s" % text)
    with t.component("selling_fails_the_chain", toggle="coreBrokerEnabled"):
        text = _proof(t, "ProofCores", "sell")
        t.bridge_call("rimworld/step_game_ticks", ticks=60, pauseFirst=True, timeoutMs=120000)
        chain_text = _proof(t, "ProofChain")
        if t._guard() and not (text.startswith("CORES SOLD") and chain_text.startswith("CHAIN EndedFailed")):
            raise ExpectationFailed("the sell-out did not reach the parent: %s || %s" % (text, chain_text))


def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    qroot = ET.parse(os.path.join(HERE, "Defs", "QuestScriptDefs", "RUT_UnfinishedLine.xml")).getroot()
    quests = {e.findtext("defName"): e for e in qroot if e.tag == "QuestScriptDef"}
    parent = quests.get(PARENT)
    if parent is None:
        return ["no %s QuestScriptDef" % PARENT]
    if parent.findtext("isRootSpecial") != "true" or parent.findtext("rootSelectionWeight") != "0":
        bad.append("%s must be isRootSpecial with weight 0 (incident-given; IncidentDef.cs:235 ConfigError)" % PARENT)
    spine = [n for n in parent.iter("li") if (n.get("Class") or "").endswith("QuestNode_RUT_UnfinishedLineSpine")]
    beats = [li.text.strip() for li in spine[0].findall("beats/li")] if spine else []
    if not beats or beats[0] != BEAT1:
        bad.append("spine beats %r must start with %s" % (beats, BEAT1))
    for b in beats:
        if b not in quests:
            bad.append("beat %s has no QuestScriptDef" % b)
        elif quests[b].findtext("epicParent") != PARENT:
            bad.append("beat %s epicParent is not %s" % (b, PARENT))
    beat1 = quests.get(BEAT1)
    if beat1 is not None:
        job = [n for n in beat1.iter("li") if (n.get("Class") or "").endswith("QuestNode_DroidRepairJob")]
        if not job or job[0].findtext("gradeAllDroids") != "true":
            bad.append("The Count must grade all three droids (gradeAllDroids true)")
        gens = [n for n in beat1.iter("li") if n.get("Class") == "QuestNode_RandomNode"]
        if len(gens) != 3:
            bad.append("The Count brings three droids; parsed %d droid generators" % len(gens))
    beat2 = quests.get(BEAT2)
    if beat2 is None or BEAT2 not in beats:
        bad.append("%s missing or not on the spine" % BEAT2)
    else:
        truces = [n for n in beat2.iter("li") if (n.get("Class") or "").endswith("QuestNode_RUT_Truce")]
        if not any(n.findtext("breakIt") != "true" for n in truces):
            bad.append("The Envoy must start the truce on acceptance (QuestNode_RUT_Truce with no breakIt)")
        if sum(1 for n in truces if n.findtext("breakIt") == "true") < 2:
            bad.append("The Envoy must break the truce on both envoys.Destroyed and envoys.Arrested")
    beat3 = quests.get(BEAT3)
    if beat3 is None or BEAT3 not in beats:
        bad.append("%s missing or not on the spine" % BEAT3)
    else:
        classes = [(n.get("Class") or "") for n in beat3.iter("li")]
        if not any(c.endswith("QuestNode_RUT_PatternCores") for c in classes):
            bad.append("The Pattern Cores has no QuestNode_RUT_PatternCores (home watch / broker)")
        sp = [n for n in beat3.iter("li") if (n.get("Class") or "").endswith("QuestNode_RUT_SignalParent")]
        if not sp or sp[0].findtext("parentSignal") != "LineSold":
            bad.append("The Pattern Cores must tell the parent LineSold on the sell-out")
        if not any(n.findtext("inSignal") == "LineSold" and n.get("Class") == "QuestNode_End" for n in parent.iter("li")):
            bad.append("the parent has no End on LineSold (the sell-out would not end the chain)")
    beat4 = quests.get(BEAT4)
    if beat4 is None or BEAT4 not in beats:
        bad.append("%s missing or not on the spine" % BEAT4)
    else:
        if BEAT3 in beats and beats.index(BEAT4) != beats.index(BEAT3) + 1:
            bad.append("The Tithe must follow The Pattern Cores on the spine: %r" % beats)
        classes = [(n.get("Class") or "") for n in beat4.iter("li")]
        for need in ("QuestNode_RUT_TitheSetup", "QuestNode_RUT_TitheShuttleGate", "QuestNode_RUT_LineHands"):
            if not any(c.endswith(need) for c in classes):
                bad.append("The Tithe has no %s" % need)
        subs = [n for n in beat4.iter("li") if n.get("Class") == "QuestNode_SubScript" and n.findtext("def") == "Util_TransportShip_Pickup"]
        if not subs or subs[0].findtext("parms/requiredItems") != "$titheItems" or subs[0].findtext("parms/requireColonistCount") != "1":
            bad.append("The Tithe's shuttle must require the tithe ($titheItems) and one colonist")
        hands = [n for n in beat4.iter("li") if (n.get("Class") or "").endswith("QuestNode_RUT_LineHands")]
        died = hands[0].findtext("outSignalColonistsDied") if hands else None
        done = hands[0].findtext("outSignalComplete") if hands else None
        on_died = [n for n in beat4.iter("li") if n.findtext("inSignal") == died]
        if not died or not any(n.get("Class") == "QuestNode_End" and n.findtext("outcome") == "Fail" for n in on_died) \
                or sum(1 for n in on_died if n.get("Class") == "QuestNode_ChangeFactionGoodwill") < 2:
            bad.append("the lent crafter dying must Fail the beat and cost both factions goodwill")
        if not done or not any(n.findtext("inSignal") == done and n.get("Class") == "QuestNode_End"
                               and n.findtext("outcome") == "Success" for n in beat4.iter("li")):
            bad.append("the crafter's return must end The Tithe in Success")
        if not any(n.get("Class") == "QuestNode_Delay" and n.findtext("isQuestTimeout") == "true" for n in beat4.iter("li")):
            bad.append("The Tithe has no shown deadline (QuestNode_Delay isQuestTimeout)")
    bad.extend(world_static_checks(beats))
    about = open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read()
    if "brrainz.harmony" not in about:
        bad.append("About.xml does not depend on Harmony (the tithe's shuttle skill gate is a Harmony patch)")
    for rel in ("SitePartDefs/RUT_SilicaxFoundryRuin.xml", "ThingDefs_Items/RUT_FoundryPatternCore.xml",
                "MentalStateDefs/RUT_WildDroidPack.xml", "LetterDefs/RUT_CoreBrokerOffer.xml"):
        if not os.path.exists(os.path.join(HERE, "Defs", rel)):
            bad.append("missing Defs/%s" % rel)
    inc = ET.parse(os.path.join(HERE, "Defs", "IncidentDefs", "RUT_UnfinishedLine_Offer.xml")).getroot()
    incs = [e for e in inc if e.tag == "IncidentDef"]
    if not incs or incs[0].findtext("questScriptDef") != PARENT:
        bad.append("RUT_UnfinishedLine_Offer does not give %s" % PARENT)
    src_dir = os.path.join(HERE, "Source")
    proj = open(os.path.join(src_dir, "RimMandrake.Utinni.UnfinishedLine.csproj"), encoding="utf-8").read()
    for f in os.listdir(src_dir):
        if f.endswith(".cs") and ('Compile Include="%s"' % f) not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % f)
    mod = open(os.path.join(src_dir, "UnfinishedLineMod.cs"), encoding="utf-8").read()
    for f in suite.toggles:
        if '"%s"' % f not in mod:
            bad.append("toggle %s is not Scribed" % f)
    if not any(f.endswith(".dll") for f in os.listdir(os.path.join(HERE, "Assemblies"))):
        bad.append("no DLL in Assemblies")
    validator = os.path.join(REPO, ".claude", "skills", "rimworld-quests", "scripts", "validate_quest.py")
    if os.path.exists(validator):
        r = subprocess.run([sys.executable, validator, "--dir", os.path.join(HERE, "Defs", "QuestScriptDefs")],
                           capture_output=True, text=True)
        tail = (r.stdout or "").strip().splitlines()[-1:] or ["(no output)"]
        if " 0 error(s)" not in tail[0]:
            bad.append("validate_quest.py: %s" % tail[0])
    return bad


VOLUNTEER = "RUT_LineVolunteer"
WORLD_TOGGLES = ("lineInWorldEnabled", "empireStrikesEnabled")


def world_static_checks(beats):
    """UNFINISHED_LINE_WORLD_FOUNDRY_1: the volunteer quest the world component offers, and the strike incident."""
    bad = []
    src = open(os.path.join(HERE, "Source", "UnfinishedLineWorld.cs"), encoding="utf-8").read()
    if 'VolunteerQuestDefName = "%s"' % VOLUNTEER not in src:
        bad.append("UnfinishedLineWorld.cs does not offer %s by that name" % VOLUNTEER)
    path = os.path.join(HERE, "Defs", "QuestScriptDefs", "%s.xml" % VOLUNTEER)
    if not os.path.exists(path):
        return bad + ["no Defs/QuestScriptDefs/%s.xml (the world component would offer nothing)" % VOLUNTEER]
    qs = [e for e in ET.parse(path).getroot() if e.tag == "QuestScriptDef" and e.findtext("defName") == VOLUNTEER]
    if not qs:
        return bad + ["%s.xml holds no QuestScriptDef %s" % (VOLUNTEER, VOLUNTEER)]
    q = qs[0]
    if q.findtext("isRootSpecial") != "true" or q.findtext("rootSelectionWeight") != "0":
        bad.append("%s must be isRootSpecial with weight 0 (only the world component offers it)" % VOLUNTEER)
    if VOLUNTEER in beats:
        bad.append("%s is on the spine; it is the world component's recurring offer, not a beat" % VOLUNTEER)
    lis = list(q.iter("li"))
    gens = [n for n in lis if n.get("Class") == "QuestNode_GeneratePawn"]
    if not gens or any(n.findtext("addToList") != "volunteers" for n in gens):
        bad.append("%s must generate its droid into the list var 'volunteers'" % VOLUNTEER)
    if any((n.findtext("kindDef") or "").startswith("RSW_DW_Head_") for n in gens):
        bad.append("%s generates a head; the line never makes heads" % VOLUNTEER)
    arrive = [n for n in lis if n.get("Class") == "QuestNode_PawnsArrive"]
    if not arrive or arrive[0].findtext("joinPlayer") != "true" or arrive[0].findtext("pawns") != "$volunteers":
        bad.append("%s must bring $volunteers in with joinPlayer true" % VOLUNTEER)
    watch = [n for n in lis if (n.get("Class") or "").endswith("QuestNode_RUT_LineVolunteers")]
    if not watch or watch[0].findtext("pawns") != "$volunteers":
        bad.append("%s must hand $volunteers to the foundry watch (QuestNode_RUT_LineVolunteers)" % VOLUNTEER)
    elif watch[0].find("inSignal") is not None:
        bad.append("QuestNode_RUT_LineVolunteers must arm on acceptance (no inSignal)")
    if not any(n.get("Class") == "QuestNode_End" and n.findtext("outcome") == "Success" for n in lis):
        bad.append("%s has no Success end" % VOLUNTEER)
    if any(n.get("Class") == "QuestNode_End" and n.findtext("outcome") == "Fail" for n in lis):
        bad.append("%s must not be failable: the stake is the betrayal watch, outside the quest" % VOLUNTEER)
    inc = os.path.join(HERE, "Defs", "IncidentDefs", "RUT_FoundryStrike.xml")
    if not os.path.exists(inc) or "IncidentWorker_RUT_FoundryStrike" not in open(inc, encoding="utf-8").read():
        bad.append("RUT_FoundryStrike incident missing or not on IncidentWorker_RUT_FoundryStrike")
    mod = open(os.path.join(HERE, "Source", "UnfinishedLineMod.cs"), encoding="utf-8").read()
    for f in WORLD_TOGGLES + ("volunteerDays", "volunteerCap"):
        if '"%s"' % f not in mod:
            bad.append("world setting %s is not Scribed" % f)
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)


@suite.chain("first_light")
def first_light(t):
    """UNFINISHED_LINE_FIRSTLIGHT_BEAT_1: beat 5 can find a hostile strike faction (the Empire on the campaign). Not
    proven here: the strike landing, the run/strike PassAll, the hold-window failure and the epilogue's goodwill --
    first poke: offer the chain, force beats to 5 with ProofEndBeat true + ProofNextBeat, accept, and read ProofChain
    after the strike is broken and the run ends."""
    with t.component("strike_faction_found", beyond_toggle=True):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Utinni.UnfinishedLine.UnfinishedLineFirstLightProof",
                          method="ProofFirstLightSetup")
        text = str((r or {}).get("result", ""))
        if t._guard() and (not text.startswith("STRIKE ") or "STRIKE none" in text or "hostile=True" not in text):
            raise ExpectationFailed("no hostile strike faction for First Light: %s" % text)


@suite.chain("tithe")
def tithe(t):
    """UNFINISHED_LINE_TITHE_BEAT_1: the basket scales, the lend has a faction, and the skill gate follows its toggle. Not
    proven here: the shuttle refusing an unskilled colonist (CompShuttle.IsAllowed postfix), the shuttle leaving with the
    tithe, the 10-day lend and the XP gift -- first poke: force beats to 4 (ProofEndBeat true + ProofNextBeat x3), accept,
    try to load a Crafting-2 colonist (the load dialog must not list them), load the tithe and a Crafting-8 colonist,
    then dev-end the lend part and read the colonist's Crafting XP."""
    tp = "RimMandrake.Utinni.UnfinishedLine.UnfinishedLineTitheProof"
    with t.component("basket_and_lend_faction", beyond_toggle=True):
        r = t.bridge_call("jawa/static_call", type=tp, method="ProofTitheSetup")
        text = str((r or {}).get("result", ""))
        if t._guard() and (not text.startswith("TITHE ") or "lend to none" in text or "plasteel" not in text):
            raise ExpectationFailed("tithe setup unreadable: %s" % text)
    with t.component("skill_gate_off_drops_the_floor", toggle="lendSkillGateEnabled"):
        t.set_setting(SETTINGS_TYPE, {"lendSkillGateEnabled": False})
        try:
            r = t.bridge_call("jawa/static_call", type=tp, method="ProofTitheSetup")
            text = str((r or {}).get("result", ""))
        finally:
            t.set_setting(SETTINGS_TYPE, {"lendSkillGateEnabled": True})
        if t._guard() and "min crafting 0" not in text:
            raise ExpectationFailed("lendSkillGateEnabled OFF but a Crafting floor remains: %s" % text)


@suite.chain("world")
def world(t):
    """UNFINISHED_LINE_WORLD_FOUNDRY_1: the line runs in the world. Precondition: the Enclaves are the player's ALLY
    (volunteers need it). Not proven here: settlement regrowth on a generated Enclave map, the strike landing, the
    betrayal on a real bolt -- first poke: ProofWorld 'stand', bolt an arrived volunteer, read 'state' for betrayed=True."""
    tp = "RimMandrake.Utinni.UnfinishedLine.UnfinishedLineWorldProof"

    def w(action):
        r = t.bridge_call("jawa/static_call", type=tp, method="ProofWorld", args=action)
        return str((r or {}).get("result", ""))

    with t.component("line_stands", beyond_toggle=True):
        text = w("stand")
        if t._guard() and "runs=True" not in text:
            raise ExpectationFailed("marking the line completed did not make it run: %s" % text)
    with t.component("volunteer_offered", beyond_toggle=True):
        # Fixture (MEASURED live 2026-10-07: "VOLUNTEER REFUSED: Enclaves not allied"): VolunteerBlocker needs the
        # Enclaves to be the player's ALLY, which a quicktest world never is. Make them so, and read it back.
        ally = t.bridge_call("jawa/faction_relations_set", faction="Player", other="RUT_Jawa_FreeDroidEnclaves",
                             kind="Ally")
        if t._guard() and not (ally or {}).get("success"):
            raise ExpectationFailed("fixture: could not ally the Enclaves with the player: %s" % ally)
        text = w("volunteer")
        if t._guard() and not text.startswith("VOLUNTEER OFFERED"):
            raise ExpectationFailed("%s was not offered: %s" % (VOLUNTEER, text))
    with t.component("foundry_stock_is_good_grade", beyond_toggle=True):
        text = w("stock")
        try:
            n_f = int(text.split(" foundry ")[1].split(" ")[0])
            n_g = int(text.split(" good ")[1].split(" ")[0])
        except (IndexError, ValueError):
            n_f = n_g = -1
        if t._guard() and not (n_f > 0 and n_g == n_f):
            raise ExpectationFailed("Enclave stock lacks Good-grade Foundry frames/parts: %s" % text)
    with t.component("line_off_stops_it", toggle="lineInWorldEnabled"):
        t.set_setting(SETTINGS_TYPE, {"lineInWorldEnabled": False})
        try:
            text = w("state")
        finally:
            t.set_setting(SETTINGS_TYPE, {"lineInWorldEnabled": True})
        if t._guard() and "runs=False" not in text:
            raise ExpectationFailed("lineInWorldEnabled OFF but the line still runs: %s" % text)
    with t.component("strikes_off_never_ready", toggle="empireStrikesEnabled"):
        w("heat 999")
        t.set_setting(SETTINGS_TYPE, {"empireStrikesEnabled": False})
        try:
            text = w("state")
        finally:
            t.set_setting(SETTINGS_TYPE, {"empireStrikesEnabled": True})
            w("heat 0")
        if t._guard() and "strikeReady=False" not in text:
            raise ExpectationFailed("empireStrikesEnabled OFF but a strike is ready: %s" % text)
