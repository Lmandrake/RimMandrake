#!/usr/bin/env python3
"""gen_vault_quests.py - VAULT_THAW_QUEST_FAMILY_1: the QuestScriptDef family
that makes the six Forsaken vaults PLAY.

Design: design/Jawa/worldbuilding/vault_thaw_quest_family.md (read that
first; this file only carries the mechanical provenance).

Writes, all under ../Defs/:
  QuestScriptDefs/RUT_VaultThaw.xml   six vault quests + the Claim-Conflict +
                                      the Reclamation
  SitePartDefs_Vaults.xml             one SitePartDef + one GenStepDef per
                                      vault type (KCSG.GenStep_CustomStructureGen
                                      linked by linkWithSite - the vanilla way a
                                      site part owns map content)
  IncidentDefs_Vaults.xml             one GiveQuest IncidentDef per quest,
                                      baseChance 0: a deterministic trigger for
                                      dev mode / the bridge, and the hook the
                                      chain fires through (QuestNode_Incident)
  HistoryEventDefs_Vaults.xml         the memory: what the game records on each
                                      branch, for the Narrator/Reclamation to
                                      read back

No node class, field, signal suffix or defName below is guessed. Every one
was read in decompiled 1.6 source (rimsage) or vanilla Data on 2026-09-05:

  QuestNode_GenerateSite.tile is SlateRef<PlanetTile>; a literal "20853" goes
    string -> ConvertHelper.Convert -> ParseHelper (PlanetTile parser
    registered, ParseHelper.cs:402) -> PlanetTile(int) = Surface layer
    (PlanetTile.cs:22,37). So a FIXED tile is one QuestNode_Set.
  QuestNode_GetDefaultSitePartsParams / Util_GenerateSite: the exact call
    sequence Jawa_TheClaim.xml already ships; `faction` from a string resolves
    by FactionDef defName (ConvertHelper.cs:164-190); an inline <li> list is
    XML -> DirectXmlToObject (ConvertHelper.cs "IsXml" branch).
  SiteMaker.MakeSite never calls SitePartDef.FactionCanOwn, so a HIDDEN
    faction (Mechanoid, AncientsHostile) can own a quest site.
  SitePartDef.minMapSize (IntVec3?) - the ruled 325x325 lives on the def.
  GenStepDef.linkWithSite -> SitePartDef.ExtraGenSteps (SitePartDef.cs).
  KCSG.GenStep_CustomStructureGen { structureLayoutDefs, fullClear,
    clearFogInRect } (vendor/.../KCSG/GenStep/GenStep_CustomStructureGen.cs),
    generates CenteredOn(map.Center).
  QuestNode_RequirementsToAcceptResearch: field is spelled `reserach`
    (vanilla typo, Odyssey Script_Site.xml:52) and its TestRunInt returns
    FALSE until the project is finished - a full generation gate, not just an
    accept gate.
  QuestNode_QuestUnique { tag } - blocks a second ONGOING copy only.
  QuestNode_SignalActivable { inSignal, inSignalEnable, inSignalDisable, node }.
  QuestNode_Delay { inSignalEnable, delayTicks, outSignalComplete, node }.
  QuestNode_Incident { inSignal, incidentDef } -> QuestPart_Incident; with a
    GiveQuest incident, IncidentWorker_GiveQuest.TryExecuteWorker generates
    the named questScriptDef directly (no CanRun re-check).
  QuestNode_Raid reads slate `map`, `points`, `enemyFaction` (Slate.TryGet
    converts a string to Faction, Slate.cs:79); { raidPawnKind, arrivalMode,
    canTimeoutOrFlee, tag, customLetterLabel/Text }. A forced RaidEnemy with
    parms.faction set skips raidsForbidden (IncidentWorker_RaidEnemy.cs:58).
    The raid lord carries the tag, and Lord.cs:661 sends
    `<tag>.AllEnemiesDefeated` when its pawns are all dead or gone.
  QuestNode_ChangeFactionGoodwill { faction, change, ensureHostile,
    canSendLetter, reason(HistoryEventDef) }.
  QuestNode_AllSignals { inSignals, outSignals }.
  QuestNode_Less { value1, value2, node, elseNode }.
  QuestNode_RecordHistoryEvent { inSignal, historyDef }.
  Site.CheckAllEnemiesDefeated fires once per map whenever no hostile active
    threat remains - on a type-3 vault that is the moment of arrival, so the
    V6 branches do NOT use it (see the design doc, "the C# gap").
  Building_AncientCryptosleepCasket.EjectContents gives AncientsHostile
    contents a LordJob_AssaultColony(canTimeoutOrFlee: true) - the woken
    fight, and flee when losing; Designator_Open has no faction check.

Run: python3 gen_vault_quests.py
"""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "Defs")
DAY = 60000

# ---------------------------------------------------------------------------
# The six sites - RULED (dungeons_arc_spec.md SS3.2, VAULT_DUNGEON_BUILD_1).
# ---------------------------------------------------------------------------
VAULTS = [
    dict(id="V1", slug="RustCathedral", tile=678, vtype=1, rating=3,
         place="the Rust Cathedral", region="under the substellar glare",
         name="The Vault That Held: Rust Cathedral",
         desc=("The reading gave up a place, and the ship gave up a face for it. Under the "
               "Rust Cathedral, where the metal walls are the treasure, the Forsaken sank a "
               "vault and the vault did its job. Everything inside is still switched on.\n\n"
               "The outer works will tell you what kind of place it is before you are through "
               "the door. Walk the ring, or walk away. The core costs whatever it costs."),
         arrive=("Lights, under the dust. Patrol routes worn into the floor by machines that "
                 "never learned to stop. The short ones have found a thing that does not know "
                 "it lost."),
         cleared=("The garrison is down. Whatever the Forsaken meant to keep, they kept it "
                  "this long. Matter and weapons only - the machines' parts fit nothing you "
                  "own, and nothing you own will ever fit them."),
         left="You have been to the Cathedral's cellar and come back. The Cathedral noticed."),
    dict(id="V2", slug="Scorch", tile=4000, vtype=1, rating=2,
         place="the Scorch", region="in the Cathedral's pollution halo",
         name="The Vault That Held: Scorch",
         desc=("Outer works, the reading says - a vault the Forsaken built to guard the "
               "approaches to something larger. It sits in the Scorch, in ground the Enclaves "
               "still argue over, and it is still powered.\n\n"
               "Smaller than the one under the Cathedral. Not safer."),
         arrive=("A perimeter still counting the hours since the last order. It will count "
                 "you too."),
         cleared="The outer works have fallen quiet. Take what is metal and go; the Enclaves will have seen the smoke.",
         left="A vault visited in the Scorch. The Enclaves keep a ledger of who walks on their ground."),
    dict(id="V3", slug="FallLine", tile=9167, vtype=1, rating=3,
         place="the Fall Line", region="on the Empire's Ashgarrison road",
         name="The Vault That Held: Fall Line",
         desc=("A vault on the Fall Line, far from the Cathedral's trip - route-spread, the "
               "way the Forsaken built when they expected to fight along a road. It sits "
               "under the Empire's patrol ground now, which is a second garrison the reading "
               "did not mention.\n\n"
               "Still powered. Still held."),
         arrive="The garrison wakes the way a machine wakes: all at once and without surprise.",
         cleared="Silence on the Fall Line. Matter, weapons, the smell of ozone. The patrols will come to see what stopped shooting.",
         left="You went to the Fall Line vault. Somewhere an Imperial clerk wrote down the date."),
    dict(id="V4", slug="Deadstone", tile=17461, vtype=2, rating=3,
         place="Deadstone", region="on the warm edge of the nightside",
         name="The Vault That Fell: Deadstone",
         desc=("Not every vault held. The reading names one in Deadstone that was breached "
               "from the inside, and the thing that got out is still there, still "
               "multiplying, in ground that already breeds bioweapon leavings.\n\n"
               "There is nothing in it to carry home. There is something in it to learn."),
         arrive=("Torn open from within. The walls do not so much stand as remain. You are "
                 "not the first thing to walk in here, and everything that walked in before "
                 "you is still here in some form."),
         cleared=None,
         left=("You came out of Deadstone. The ship, which has its own memory of what was "
               "loosed there, offers no comment - only a direction: the deep dark, past the "
               "last of the refugee lights, where the cold kept something else.")),
    dict(id="V5", slug="Slough", tile=37, vtype=2, rating=3,
         place="the Slough", region="exactly on the terminator",
         name="The Vault That Fell: Slough",
         desc=("A second breach, from the other side of the world - a vault in the Slough, on "
               "the terminator line, lost the same way Deadstone was lost. The gelatinous "
               "thing that owns the ground there did not come from nowhere.\n\n"
               "No loot. Survival, and the shape of what happened."),
         arrive="It is wet in here, and it is moving, and none of it is water.",
         cleared=None,
         left=("The Slough gave you nothing you can sell. It gave you a direction: the vaults "
               "that fell all fell to the same thing, and the one that neither held nor fell "
               "is in the deep Umbra, frozen.")),
]

V6 = dict(id="V6", slug="Umbra", tile=20853, vtype=3, rating=4,
          name="The Vault That Sleeps: Umbra",
          desc=("The deepest of them, the coldest, the farthest from any road - a vault in the "
                "Umbra that neither held nor fell. It froze. The reading gives its place; the "
                "ship, which has been quiet about this one, gives the rest: there are people "
                "in it.\n\n"
                "The Forsaken put their children in the cold when they knew they were losing. "
                "The vault has no power. It cannot be woken until you bring it fire - a "
                "persona core, fed into the heart of the place, and there is no taking it "
                "back out.\n\n"
                "Wake them. Or take what is theirs. Or leave the door shut. The ship will "
                "remember which."))

# ---------------------------------------------------------------------------
# Site parts and gen steps - one per type.
# ---------------------------------------------------------------------------
SITEPARTS = [
    dict(vtype=1, defName="RUT_VaultSite_Type1", layout="RUT_VaultType1_MechanoidGarrison",
         label="Forsaken vault (held)",
         desc="A Forsaken vault that did its job. The garrison inside is still switched on.",
         icon="World/WorldObjects/Expanding/AncientStructure"),
    dict(vtype=2, defName="RUT_VaultSite_Type2", layout="RUT_VaultType2_FleshWeaponLoose",
         label="Forsaken vault (breached)",
         desc="A Forsaken vault torn open from the inside. What killed the defenders is still multiplying.",
         icon="World/WorldObjects/Expanding/AncientStructure"),
    dict(vtype=3, defName="RUT_VaultSite_Type3", layout="RUT_VaultType3_FrozenRakata",
         label="Forsaken vault (frozen)",
         desc="A Forsaken vault, dark and frost-locked. Nothing in it is switched on. Nothing in it is dead.",
         icon="World/WorldObjects/Expanding/AncientStructure"),
]

SITE_FACTION = {1: "Mechanoid", 2: None, 3: "AncientsHostile"}

# ---------------------------------------------------------------------------
# History events - the memory substrate.
# ---------------------------------------------------------------------------
HISTORY = [
    ("RUT_VaultVisited", "walked into a Forsaken vault and came back"),
    ("RUT_VaultGarrisonBroken", "broke a Forsaken garrison"),
    ("RUT_VaultSleepersWoken", "woke the Forsaken sleepers"),
    ("RUT_VaultSleepersKilled", "killed the Forsaken sleepers in their caskets"),
    ("RUT_VaultLeftSleeping", "left the Forsaken sleepers to their cold"),
    ("RUT_WokenClaimRefused", "refused the woken their ship"),
    ("RUT_HelixSidedWithTheWoken", "the Ascendant Helix sided with the woken Forsaken"),
    ("RUT_ReclamationSurvived", "survived the Reclamation"),
]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def rules(name_text, desc_text):
    return f"""    <questNameRules>
      <rulesStrings>
        <li>questName->{esc(name_text)}</li>
      </rulesStrings>
    </questNameRules>
    <questDescriptionRules>
      <rulesStrings>
        <li>questDescription->{esc(desc_text)}</li>
      </rulesStrings>
    </questDescriptionRules>
"""


def letter(label, text, in_signal=None, letter_def=None, indent=8):
    p = " " * indent
    xml = f'{p}<li Class="QuestNode_Letter">\n'
    if in_signal:
        xml += f"{p}  <inSignal>{in_signal}</inSignal>\n"
    if letter_def:
        xml += f"{p}  <letterDef>{letter_def}</letterDef>\n"
    xml += f"{p}  <label>{esc(label)}</label>\n{p}  <text>{esc(text)}</text>\n{p}</li>\n"
    return xml


def history(defname, in_signal=None, indent=8):
    p = " " * indent
    s = f'{p}<li Class="QuestNode_RecordHistoryEvent">\n'
    if in_signal:
        s += f"{p}  <inSignal>{in_signal}</inSignal>\n"
    s += f"{p}  <historyDef>{defname}</historyDef>\n{p}</li>\n"
    return s


def end(outcome, in_signal=None, indent=8, listen=None):
    p = " " * indent
    s = f'{p}<li Class="QuestNode_End">\n'
    if in_signal:
        s += f"{p}  <inSignal>{in_signal}</inSignal>\n"
    s += f"{p}  <outcome>{outcome}</outcome>\n"
    if listen:
        s += f"{p}  <signalListenMode>{listen}</signalListenMode>\n"
    s += f"{p}</li>\n"
    return s


def site_setup(tile, vtype):
    """Fixed-tile site generation: the one sequence, shared by all six."""
    faction = SITE_FACTION[vtype]
    part = next(s["defName"] for s in SITEPARTS if s["vtype"] == vtype)
    xml = f"""        <li Class="QuestNode_GetMap">
          <canBeSpace>true</canBeSpace>
        </li>

        <!-- The tile is FIXED (no-worldgen doctrine): a literal PlanetTile on the surface layer. -->
        <li Class="QuestNode_Set">
          <name>siteTile</name>
          <value>{tile}</value>
        </li>
"""
    if faction:
        xml += f"""        <!-- Site faction by FactionDef defName; hidden factions are fine here (SiteMaker never checks FactionCanOwn). -->
        <li Class="QuestNode_Set">
          <name>siteFaction</name>
          <value>{faction}</value>
        </li>
"""
    else:
        xml += "        <!-- No site faction: a breached vault belongs to nobody; its guardians are factionless by symbol. -->\n"
    xml += f"""        <li Class="QuestNode_GetDefaultSitePartsParams">
          <tile>$siteTile</tile>
          <faction>$siteFaction</faction>
          <sitePartDefs>
            <li>{part}</li>
          </sitePartDefs>
          <storeSitePartsParamsAs>sitePartsParams</storeSitePartsParamsAs>
        </li>

        <li Class="QuestNode_SubScript">
          <def>Util_GenerateSite</def>
        </li>

        <li Class="QuestNode_SpawnWorldObjects">
          <worldObjects>$site</worldObjects>
        </li>
"""
    return xml


def vault_quest(v):
    defname = f"RUT_VaultThaw_{v['id']}_{v['slug']}"
    tag = f"RUT_VaultThaw_{v['id']}"
    body = f"""  <QuestScriptDef>
    <defName>{defname}</defName>
    <rootSelectionWeight>1.0</rootSelectionWeight>
    <rootMinPoints>0</rootMinPoints>
    <minRefireDays>120</minRefireDays>
    <defaultChallengeRating>{v['rating']}</defaultChallengeRating>
    <expireDaysRange>15~25</expireDaysRange>
    <everAcceptableInSpace>true</everAcceptableInSpace>

{rules(v['name'], v['desc'])}
    <root Class="QuestNode_Sequence">
      <nodes>

        <!-- Reveal gate: the reading. Antiquities CARTOGRAPHY (RUT_Antiq_Cartography,
             antiquities_design.md: "vault sites revealed"). TestRunInt is false until the
             project is finished, so this quest cannot even be generated before then. -->
        <li Class="QuestNode_RequirementsToAcceptResearch">
          <reserach>RUT_Antiq_Cartography</reserach>
        </li>

        <!-- One copy at a time; minRefireDays covers the rest. -->
        <li Class="QuestNode_QuestUnique">
          <tag>{tag}</tag>
        </li>

{site_setup(v['tile'], v['vtype'])}
        <!-- Accepted: the ship remembers where it is. No inSignal = fires on accept. -->
{letter("The ship remembers", f"The reading gave a place. The ship gave a name it has not said aloud in an age. There is a Forsaken vault {v['region']}, and now there is a mark on your map where the short ones did not put one.")}
        <!-- Arrival. -->
{letter(f"Arrived: {v['place']}", v['arrive'], in_signal="site.MapGenerated")}
"""
    if v["cleared"]:
        body += f"""        <!-- The garrison ring falls silent (real hostiles exist on a type-1 site, so this fires when they are dead). -->
{letter("The garrison is silent", v['cleared'], in_signal="site.AllEnemiesDefeated", letter_def="PositiveEvent")}
{history("RUT_VaultGarrisonBroken", in_signal="site.AllEnemiesDefeated")}
"""
    body += f"""        <!-- Success = you went, and you came back. Armed only once the site map exists. -->
        <li Class="QuestNode_SignalActivable">
          <inSignal>site.MapRemoved</inSignal>
          <inSignalEnable>site.MapGenerated</inSignalEnable>
          <node Class="QuestNode_Sequence">
            <nodes>
{letter("Quest completed: " + v['place'], v['left'], indent=14)}
{history("RUT_VaultVisited", indent=14)}
{end("Success", indent=14)}
            </nodes>
          </node>
        </li>

      </nodes>
    </root>
  </QuestScriptDef>

"""
    return body


def v6_quest():
    v = V6
    defname = "RUT_VaultThaw_V6_Umbra"
    woken_line = ("They come up out of the cold fighting. Not for you - past you. They say Rakata, "
                  "which is their word for themselves, and Forsaken is not a word they know. "
                  "They look at the short ones the way the short ones look at a droid with a "
                  "loose panel.\n\n"
                  "Then one of them sees her, through the frost on the door, and stops.\n\n"
                  "\"And hey... isn't that a colonizer ship you're riding in?! What are you doing "
                  "with that?\"\n\n"
                  "No gratitude. No question about the war, which they believe is still on. "
                  "Only the ship, and whose she is. That question is now open, and they are "
                  "the ones who opened it.")
    body = f"""  <QuestScriptDef>
    <defName>{defname}</defName>
    <rootSelectionWeight>1.0</rootSelectionWeight>
    <rootMinPoints>0</rootMinPoints>
    <minRefireDays>200</minRefireDays>
    <defaultChallengeRating>{v['rating']}</defaultChallengeRating>
    <expireDaysRange>20~30</expireDaysRange>
    <everAcceptableInSpace>true</everAcceptableInSpace>

{rules(v['name'], v['desc'])}
    <root Class="QuestNode_Sequence">
      <nodes>

        <!-- Two gates: CARTOGRAPHY (the place) and VOICE (the register to address an
             ancient - antiquities_design.md SS7: the frozen vault "should require VOICE"). -->
        <li Class="QuestNode_RequirementsToAcceptResearch">
          <reserach>RUT_Antiq_Cartography</reserach>
        </li>
        <li Class="QuestNode_RequirementsToAcceptResearch">
          <reserach>RUT_Antiq_Voice</reserach>
        </li>
        <li Class="QuestNode_QuestUnique">
          <tag>RUT_VaultThaw_V6</tag>
        </li>

{site_setup(v['tile'], 3)}
{letter("The ship remembers", "The reading gave a place in the deep Umbra. The ship went quiet, and then said one word in the Cradle-register that the short ones do not have: a word for children. There is a mark on your map, and there are people under it.")}
{letter("Arrived: the Umbra vault", "Dark. Frost on every surface, thick enough to write in. The turrets on the ring are here, and they are asleep with everyone else - nothing in this place has drawn power in an age. At the core, a plinth with a socket the shape of a persona core, and beyond it, caskets.\\n\\nFeed the heart and the ring wakes with the hall. Open a casket and the war generation wakes with it. Break one and you have decided for them. Or shut the door and go; the ship will know which.", in_signal="site.MapGenerated")}
        <!-- ============================================================
             The three-way scene. Two of the three arrive on signals no
             vanilla QuestPart sends (see the design doc, "the C# gap"):
               site.RUT_SleepersWoken   first casket OPENED
               site.RUT_SleepersLooted  a casket BROKEN with sleepers in it
             The XML is complete and inert until a sender exists; only
             LEAVE can fire today. That is stated, not hidden.
             ============================================================ -->

        <!-- Either touch disarms the leave branch. -->
        <li Class="QuestNode_SendSignals">
          <inSignal>site.RUT_SleepersWoken</inSignal>
          <outSignals>
            <li>SleepersTouched</li>
          </outSignals>
        </li>
        <li Class="QuestNode_SendSignals">
          <inSignal>site.RUT_SleepersLooted</inSignal>
          <outSignals>
            <li>SleepersTouched</li>
          </outSignals>
        </li>

        <!-- WAKE: the reversal arrives in dialogue (canon.yml rakata.woken_brutality, verbatim line). -->
{letter("The woken", woken_line, in_signal="site.RUT_SleepersWoken", letter_def="ThreatBig")}
{history("RUT_VaultSleepersWoken", in_signal="site.RUT_SleepersWoken")}
        <!-- ...and when you have left them (dead, fled, or still there), the claim follows you home. -->
        <li Class="QuestNode_SignalActivable">
          <inSignal>site.MapRemoved</inSignal>
          <inSignalEnable>site.RUT_SleepersWoken</inSignalEnable>
          <outSignals>
            <li>WokenLeftBehind</li>
          </outSignals>
        </li>
        <li Class="QuestNode_Delay">
          <inSignalEnable>WokenLeftBehind</inSignalEnable>
          <delayTicks>$(8*60000)</delayTicks>
          <outSignalComplete>ClaimDue</outSignalComplete>
          <expiryInfoPart>The woken know where you are</expiryInfoPart>
        </li>
        <li Class="QuestNode_Incident">
          <inSignal>ClaimDue</inSignal>
          <incidentDef>RUT_GiveQuest_VaultClaimConflict</incidentDef>
        </li>
{end("Success", in_signal="ClaimDue")}

        <!-- LOOT: kills them, plainly. The game says so. -->
{letter("The caskets", "You broke the caskets open for what was in them. What was in them was people, and now it is not. The Forsaken tech is yours.\\n\\nThe game will not dress this up, and neither will the ship.", in_signal="site.RUT_SleepersLooted", letter_def="NegativeEvent")}
{history("RUT_VaultSleepersKilled", in_signal="site.RUT_SleepersLooted")}
{end("Success", in_signal="site.RUT_SleepersLooted")}

        <!-- LEAVE: nothing changes. The Narrator remembers. -->
        <li Class="QuestNode_SignalActivable">
          <inSignal>site.MapRemoved</inSignal>
          <inSignalEnable>site.MapGenerated</inSignalEnable>
          <inSignalDisable>SleepersTouched</inSignalDisable>
          <node Class="QuestNode_Sequence">
            <nodes>
{letter("Quest completed: the Umbra vault", "You shut the door on them. The cold will keep them the way it has kept them, and the war they are still fighting will go on without a single shot.\\n\\nThe ship, which once carried their parents here under another name, says nothing about it. It will remember that you did not decide for them. It remembers everything.", indent=14)}
{history("RUT_VaultLeftSleeping", indent=14)}
{end("Success", indent=14)}
            </nodes>
          </node>
        </li>

      </nodes>
    </root>
  </QuestScriptDef>

"""
    return body


def claim_conflict():
    demand = ("They found you. Not many - the ones you woke, and the ones they woke on the "
              "way, from halls the reading never showed you. Enough.\n\n"
              "The demand is short, and it is not a negotiation: the colonizer vessel is "
              "Rakata property, and the short ones aboard her are a cargo error. Hand her over.\n\n"
              "There is no version of this in which you hand her over. They know that. They "
              "came anyway. Ta'Baa, who does not root, has an opinion about whose she is.")
    gone = ("Dead, or gone into the dark with a grudge the size of a lost war. They will not "
            "forgive the refusal; they were never going to forgive the rescue.\n\n"
            "This is not the end of the claim. It is the first hearing.")
    return f"""  <QuestScriptDef>
    <defName>RUT_VaultClaimConflict</defName>
    <isRootSpecial>true</isRootSpecial>
    <rootSelectionWeight>0</rootSelectionWeight>
    <autoAccept>true</autoAccept>
    <defaultChallengeRating>3</defaultChallengeRating>
    <everAcceptableInSpace>true</everAcceptableInSpace>

{rules("The Claim on the Utinni", "The woken Forsaken have named the ship as theirs. They are coming to collect, and they will keep coming until the question is settled in their favour or in yours.")}
    <root Class="QuestNode_Sequence">
      <nodes>
        <li Class="QuestNode_GetMap" />
        <li Class="QuestNode_Set">
          <name>enemyFaction</name>
          <value>AncientsHostile</value>
        </li>
        <!-- A floor on the raid: the war generation does not arrive as three tired soldiers. -->
        <li Class="QuestNode_Less">
          <value1>$points</value1>
          <value2>1200</value2>
          <node Class="QuestNode_Set">
            <name>points</name>
            <value>1200</value>
          </node>
        </li>

{letter("The claim", demand, letter_def="ThreatBig")}
        <li Class="QuestNode_Delay">
          <delayTicks>$(2*60000)</delayTicks>
          <outSignalComplete>WokenArrive</outSignalComplete>
          <expiryInfoPart>They are walking</expiryInfoPart>
        </li>
        <li Class="QuestNode_Raid">
          <inSignal>WokenArrive</inSignal>
          <raidPawnKind>AncientSoldier</raidPawnKind>
          <arrivalMode>EdgeWalkIn</arrivalMode>
          <canTimeoutOrFlee>true</canTimeoutOrFlee>
          <tag>woken</tag>
          <customLetterLabel>The woken have come for the ship</customLetterLabel>
          <customLetterText>Forsaken soldiers, the ones you thawed, walking in from the dark with their frightening weaponry and no interest in you at all. Their interest is behind you, on the landing pad.</customLetterText>
        </li>

        <!-- Dead or fled: the refusal stands. Then the long wait for everyone. -->
{letter("Refused", gone, in_signal="woken.AllEnemiesDefeated")}
{history("RUT_WokenClaimRefused", in_signal="woken.AllEnemiesDefeated")}
        <li Class="QuestNode_Delay">
          <inSignalEnable>woken.AllEnemiesDefeated</inSignalEnable>
          <delayTicks>$(45*60000)</delayTicks>
          <outSignalComplete>ReclamationDue</outSignalComplete>
          <expiryInfoPart>The claim is not settled</expiryInfoPart>
        </li>
        <li Class="QuestNode_Incident">
          <inSignal>ReclamationDue</inSignal>
          <incidentDef>RUT_GiveQuest_Reclamation</incidentDef>
        </li>
{end("Success", in_signal="ReclamationDue")}

        <!-- The colony map is gone: no verdict. -->
{end("Unknown", in_signal="map.MapRemoved")}
      </nodes>
    </root>
  </QuestScriptDef>

"""


def reclamation():
    coming = ("All of them. Every casket you opened and every casket they opened after, "
              "walking together for the first time since the war they never finished - and "
              "beside them, the Ascendant Helix, who have decided that the way to be heard "
              "by their ancestors is to hand them a ship.\n\n"
              "The Helix boons stop today. You could have seen that coming; the ship did.\n\n"
              "This is the Reclamation. Survive it and it is over.")
    survived = ("It is over. The war generation broke on your walls, and something in them "
                "broke with it: they will not come for her again. Not gratitude. Not peace. "
                "The ancient word for it is closer to dominated.\n\n"
                "The Helix stood among them until the end, and were refused at the end - "
                "\"If you will not share your wisdom and power, then I will learn from what "
                "destroyed you,\" one of them said, to a Rakata who answered with a disgust "
                "that radiated like heat. The Helix have their answer now. So do you.")
    cathedral = ("Somewhere under the substellar glare a mind that has slept through empires "
                 "stirred long enough to say one thing to the woken who came to it afterward, "
                 "asking to be recognised:\n\n"
                 "\"I am bound to an Empire that no longer reigns, not their mongrel offspring "
                 "who managed to lose the war that broke me.\"\n\n"
                 "It said nothing to you. It never does. But it let you hear.")
    return f"""  <QuestScriptDef>
    <defName>RUT_Reclamation</defName>
    <isRootSpecial>true</isRootSpecial>
    <rootSelectionWeight>0</rootSelectionWeight>
    <autoAccept>true</autoAccept>
    <defaultChallengeRating>5</defaultChallengeRating>
    <everAcceptableInSpace>true</everAcceptableInSpace>

{rules("The Reclamation", "Every Forsaken the clan ever woke, united, with the Ascendant Helix beside them, in one concentrated attempt to take the Utinni back. Survive it and the woken are done with her - and the Helix's boons are done with you.")}
    <root Class="QuestNode_Sequence">
      <nodes>
        <li Class="QuestNode_GetMap" />
        <li Class="QuestNode_Less">
          <value1>$points</value1>
          <value2>2500</value2>
          <node Class="QuestNode_Set">
            <name>points</name>
            <value>2500</value>
          </node>
        </li>

{letter("The Reclamation", coming, letter_def="ThreatBig")}

        <!-- The Helix flip: hostile, with the reason on the faction tab. -->
        <li Class="QuestNode_ChangeFactionGoodwill">
          <faction>Jawa_AscendantHelix</faction>
          <change>-100</change>
          <ensureHostile>true</ensureHostile>
          <canSendLetter>true</canSendLetter>
          <reason>RUT_HelixSidedWithTheWoken</reason>
        </li>

        <!-- Wave one: the woken. -->
        <li Class="QuestNode_Set">
          <name>enemyFaction</name>
          <value>AncientsHostile</value>
        </li>
        <li Class="QuestNode_Delay">
          <delayTicks>$(1*60000)</delayTicks>
          <outSignalComplete>WokenArrive</outSignalComplete>
          <expiryInfoPart>They are coming</expiryInfoPart>
        </li>
        <li Class="QuestNode_Raid">
          <inSignal>WokenArrive</inSignal>
          <raidPawnKind>AncientSoldier</raidPawnKind>
          <arrivalMode>EdgeWalkIn</arrivalMode>
          <canTimeoutOrFlee>false</canTimeoutOrFlee>
          <tag>woken</tag>
          <customLetterLabel>The woken, all of them</customLetterLabel>
          <customLetterText>The war generation, together, for the ship.</customLetterText>
        </li>

        <!-- Wave two: the Helix, a day and a half behind - local collaboration, not a joint column. -->
        <li Class="QuestNode_Set">
          <name>enemyFaction</name>
          <value>Jawa_AscendantHelix</value>
        </li>
        <li Class="QuestNode_Delay">
          <delayTicks>$(1.5*60000)</delayTicks>
          <outSignalComplete>HelixArrive</outSignalComplete>
        </li>
        <li Class="QuestNode_Raid">
          <inSignal>HelixArrive</inSignal>
          <arrivalMode>EdgeWalkIn</arrivalMode>
          <canTimeoutOrFlee>true</canTimeoutOrFlee>
          <tag>helix</tag>
          <customLetterLabel>The Helix have chosen</customLetterLabel>
          <customLetterText>The Ascendant Helix arrive to stand with the ancestors who never claimed them. The boon economy is closed.</customLetterText>
        </li>

        <li Class="QuestNode_AllSignals">
          <inSignals>
            <li>woken.AllEnemiesDefeated</li>
            <li>helix.AllEnemiesDefeated</li>
          </inSignals>
          <outSignals>
            <li>ReclamationSurvived</li>
          </outSignals>
        </li>
{letter("Survived", survived, in_signal="ReclamationSurvived", letter_def="PositiveEvent")}
{history("RUT_ReclamationSurvived", in_signal="ReclamationSurvived")}
        <!-- The second scene, a day later: the Cathedral's refusal. -->
        <li Class="QuestNode_Delay">
          <inSignalEnable>ReclamationSurvived</inSignalEnable>
          <delayTicks>$(1*60000)</delayTicks>
          <outSignalComplete>CathedralSpoke</outSignalComplete>
        </li>
{letter("The Cathedral speaks", cathedral, in_signal="CathedralSpoke")}
{end("Success", in_signal="CathedralSpoke")}

{end("Fail", in_signal="map.MapRemoved")}
      </nodes>
    </root>
  </QuestScriptDef>

"""


def siteparts_xml():
    out = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n"]
    out.append("""  <!-- VAULT_THAW_QUEST_FAMILY_1: one SitePartDef per vault type. Map content comes
       from the linked GenStepDef running KCSG.GenStep_CustomStructureGen on the
       template VAULT_DUNGEON_BUILD_1 already ships - the vanilla site-part ->
       gen-step shape (Core/Defs/Sites/Parts/ItemStash.xml). minMapSize carries
       the RULED 325x325 (dungeons_arc_spec.md SS3.9). wantsThreatPoints is
       false: the layout IS the threat; nothing extra is rolled. -->
""")
    for s in SITEPARTS:
        out.append(f"""  <SitePartDef>
    <defName>{s['defName']}</defName>
    <label>{s['label']}</label>
    <description>{esc(s['desc'])}</description>
    <siteTexture>World/WorldObjects/Sites/GenericSite</siteTexture>
    <expandingIconTexture>{s['icon']}</expandingIconTexture>
    <minMapSize>(325,1,325)</minMapSize>
    <wantsThreatPoints>false</wantsThreatPoints>
    <gravShipsCanLandOn>true</gravShipsCanLandOn>
    <considerEnteringAsAttack>true</considerEnteringAsAttack>
    <forceExitAndRemoveMapCountdownDurationDays>4</forceExitAndRemoveMapCountdownDurationDays>
    <tags>
      <li>RUT_Vault</li>
    </tags>
  </SitePartDef>

  <GenStepDef>
    <defName>RUT_GenStep_VaultSite_Type{s['vtype']}</defName>
    <linkWithSite>{s['defName']}</linkWithSite>
    <order>400</order>
    <genStep Class="KCSG.GenStep_CustomStructureGen">
      <fullClear>true</fullClear>
      <clearFogInRect>false</clearFogInRect>
      <structureLayoutDefs>
        <li>{s['layout']}</li>
      </structureLayoutDefs>
    </genStep>
  </GenStepDef>

""")
    out.append("</Defs>\n")
    return "".join(out)


def incidents_xml():
    quests = [f"RUT_VaultThaw_{v['id']}_{v['slug']}" for v in VAULTS] + [
        "RUT_VaultThaw_V6_Umbra", "RUT_VaultClaimConflict", "RUT_Reclamation"]
    out = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n"]
    out.append("""  <!-- VAULT_THAW_QUEST_FAMILY_1: a named GiveQuest incident per quest, baseChance 0
       (never rolled by the storyteller - the vault quests live in the natural pool
       behind their research gates; the chain quests are isRootSpecial and fire ONLY
       through these, via QuestNode_Incident). Same shape as Core's
       GiveQuest_EndGame_ShipEscape. They are also the deterministic trigger: dev
       mode -> Incidents -> the def, or a bridge call; never "wait for it". -->
""")
    for q in quests:
        out.append(f"""  <IncidentDef ParentName="GiveQuestBase">
    <defName>RUT_GiveQuest_{q.replace('RUT_', '')}</defName>
    <label>{q.replace('RUT_', '').replace('_', ' ').lower()}</label>
    <letterLabel>Quest available</letterLabel>
    <questScriptDef>{q}</questScriptDef>
    <baseChance>0</baseChance>
  </IncidentDef>

""")
    out.append("</Defs>\n")
    return "".join(out)


def history_xml():
    out = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n"]
    out.append("""  <!-- VAULT_THAW_QUEST_FAMILY_1: what the game REMEMBERS. QuestNode_RecordHistoryEvent
       writes these into Find.HistoryEventsManager on each branch; nothing in vanilla
       QuestGen reads them back, but the Narrator (Oracle recap), Ideology precepts and
       the Reclamation's future roster can - this is the "the Narrator remembers"
       substrate, vanilla-persisted. RUT_HelixSidedWithTheWoken is also the goodwill
       reason on the Helix flip (the line on the faction tab). -->
""")
    for d, l in HISTORY:
        out.append(f"""  <HistoryEventDef>
    <defName>{d}</defName>
    <label>{esc(l)}</label>
  </HistoryEventDef>

""")
    out.append("</Defs>\n")
    return "".join(out)


def main():
    qdir = os.path.join(OUT_DIR, "QuestScriptDefs")
    os.makedirs(qdir, exist_ok=True)
    with open(os.path.join(qdir, "RUT_VaultThaw.xml"), "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>\n")
        f.write("  <!-- GENERATED by Source/gen_vault_quests.py - edit the generator, not this file.\n"
                "       Design: design/Jawa/worldbuilding/vault_thaw_quest_family.md -->\n\n")
        for v in VAULTS:
            f.write(vault_quest(v))
        f.write(v6_quest())
        f.write(claim_conflict())
        f.write(reclamation())
        f.write("</Defs>\n")
    with open(os.path.join(OUT_DIR, "SitePartDefs_Vaults.xml"), "w") as f:
        f.write(siteparts_xml())
    with open(os.path.join(OUT_DIR, "IncidentDefs_Vaults.xml"), "w") as f:
        f.write(incidents_xml())
    with open(os.path.join(OUT_DIR, "HistoryEventDefs_Vaults.xml"), "w") as f:
        f.write(history_xml())
    print("wrote RUT_VaultThaw.xml (8 quests), SitePartDefs_Vaults.xml, IncidentDefs_Vaults.xml, HistoryEventDefs_Vaults.xml")


if __name__ == "__main__":
    main()
