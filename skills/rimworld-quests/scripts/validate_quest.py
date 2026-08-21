#!/usr/bin/env python3
"""validate_quest.py - offline gate for a RimWorld QuestScriptDef.

A cold RimWorld load is 20-30 minutes. Everything here is a defect that would
otherwise cost one of those loads to discover, and every check is derived from a
failure that actually happened (see skills/rimworld-quests/SKILL.md).

    python3 validate_quest.py MyQuest.xml [more.xml ...]
    python3 validate_quest.py --dir MyMod/Defs/QuestScriptDefs
    python3 validate_quest.py --refresh ...       rebuild the corpus cache
    python3 validate_quest.py --quiet ...         errors and warnings only

Exit code 1 if any ERROR was reported, else 0.

It indexes two things off the local RimWorld install and caches them:
  * every QuestNode_* type name in Assembly-CSharp.dll  (a guessed class name is
    the commonest way a quest def fails to load)
  * every shipped QuestScriptDef, and the slate vars each one stores, so that a
    <QuestNode_SubScript> into Util_GenerateSite is understood rather than
    guessed at.
Point it at a different install with --game.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_GAME = Path(
    "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld"
)
CACHE = Path(
    os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
) / "rimworld_quests" / "corpus.json"

# ---------------------------------------------------------------------------
# Facts read out of the 1.6 assembly. See references/vanilla_corpus.md §9.
# ---------------------------------------------------------------------------

# The complete legal set of QuestTargetSignalPart_* suffixes. A signal
# "<slateVar>.<Suffix>" whose suffix is not here can never fire.
SIGNAL_SUFFIXES = set(
    """Activated AllEnemiesDefeated AllHivesDestroyed AllPawnsLost Arrested
    Banished BecameMutant BeingAttacked CeremonyDone CeremonyExpired
    CeremonyFailed ChangedFaction ChangedFactionToNonPlayer
    ChangedFactionToPlayer ChangedHostFaction CoreDefeated Despawned Destroyed
    Enslaved ExitMentalState FactionBecameHostileToPlayer FactionBuiltBuilding
    FactionMemberArrested FactionPlacedBlueprint Fleeing Hacked HackingStarted
    Inspected Kidnapped Killed KilledLeavingsLeft LaunchedShip LeftBehind
    LeftMap LockedOut MapGenerated MapRemoved MapSettled MonumentCancelled
    MonumentCompleted MonumentDestroyed NoActiveThreats NoLongerFactionLeader
    NodeClosed PeaceTalksResolved PlayerTended PsychicRitualTarget QuestEnded
    RanWild ReactorDestroyed ReceivedItems Recruited Released Rescued
    ShipArrived ShipDisposed ShipFlewAway ShipThingAdded ShuttleSentSatisfied
    ShuttleSentUnsatisfied ShuttleSentWithExtraColonists ShuttleUnloaded
    Spawned StartedExtractingFromContainer Studied SurgeryViolation SwappedMap
    TitleAwardedWhenUpdatingChanged TitleChanged TookDamage TookDamageFromPlayer
    TradeRequestFulfilled Unfogged XenogermAbsorbed XenogermReimplanted
    BecameHostileToPlayer Resolved SentSatisfied SentUnsatisfied Sent
    SentWithExtraColonists SurveyCompleted""".split()
)

# Suffixes a shipped def actually listens for. Legal-but-unprecedented ones are
# worth a note: .Killed in particular is a trap, vanilla uses .Destroyed for
# "the quest pawn died".
SIGNAL_PRECEDENT = set(
    """MapGenerated Destroyed MonumentCompleted MapRemoved LeftBehind
    BecameHostileToPlayer SentSatisfied SentUnsatisfied AllEnemiesDefeated
    Resolved TradeRequestFulfilled SurgeryViolation Arrested Recruited RanWild
    Kidnapped TitleChanged LaunchedShip NoActiveThreats Enslaved LeftMap
    ReceivedItems ShipArrived MapSettled""".split()
)

# Reserved rule parameters, assigned with '=' not '=='. Anything else inside the
# parens is a constant constraint, which is what makes a rule conditional.
RESERVED_RULE_PARAMS = {"p", "priority", "tag", "requiredTag", "uses", "debug"}

# Slate vars the engine seeds before the root node runs.
SEEDED_SLATE = {"map", "points", "questTag", "inSignal", "signalListenMode"}

# $( ) expression builtins - a call, not a slate read.
EXPR_FUNCS = {"randInt", "randFloat", "roundToTicksRough", "round", "min", "max"}

# Nodes that write a slate var under an implicit default name when <storeAs> is
# omitted. Read off shipped defs that use the var without ever storing it.
DEFAULT_STORE = {
    "QuestNode_GetMap": "map",
    "QuestNode_GetFaction": "faction",
    "QuestNode_GetPlayerFaction": "playerFaction",
    "QuestNode_GetSiteTile": "tile",
    "QuestNode_GetPawn": "asker",
    "QuestNode_GetWalkInSpot": "walkInSpot",
    "QuestNode_GetDropSpot": "dropSpot",
    "QuestNode_GenerateSite": "site",
    "QuestNode_GetDefaultRewardValueFromPoints": "rewardValue",
}

# The conventional slate vocabulary, harvested from every shipped QuestScriptDef:
# names a vanilla node or a C# root writes without any <storeAs> this validator
# can see. Reading one is normal; it is only worth a warning when the name is
# outside this set AND nothing in the def stores it.
CORPUS_SLATE = set(
    """AdjectiveAngsty AdjectiveBadass AdjectiveFriendly LEADER Letter
    PersonJob PersonalCharacteristic RomanNumeral SylE WEAPON acceptChildren
    acceptColonists allButOneChildren allChildren allLodgerInfo
    allSitePartsDescriptions allSitePartsDescriptionsExceptFirst allThreats
    allowViolence allowViolentQuests animalCount animalKind animalKindDef
    animalsAllowed arrivalMode arrivingPawns arrivingPawnsLabelDef asker
    askerIsNull askerMustBeNonHostileToPlayer atLandmark beggarCount
    beggars0 betrayalRewardMarketValue betrayalRewards
    bloodRotAndParalysisWeight bloodRotWeight canBeSpace canTimeoutOrFlee
    challengeRating childCount civilOutlander civilianCountMinusOne
    civilians classicMode colonistCount colonistsAllowed commonDescEnding
    complex contents customLetterLabel customLetterLabelRules
    customLetterText customLetterTextRules decreeDays decreeIntro
    decreeThreatInfo destroyDelayTicks discovered discoveryMethod
    enemiesCount enemiesLabel enemyFaction enemyFactionNeolithic
    enemyGroupsParagraph escortees0 excludeAskerFactionDefs
    excludeFactionDefs faction factionOf factionOpponent factionless
    firstRaidDelayTicks forcedWeather fugitive generateShuttleOrPods
    generatedItemStashThings goodwillChangeIfMonumentDestroyed
    goodwillPenalty goodwillRewardForMood hasHave healthInfo helpers
    helpers0 helpersChance helpersParagraph hiddenSitePartsPossible ideo
    ifWorldPawnThenMustBeFree ifWorldPawnThenMustBeFreeOrLeader
    investigation itemPodsTotalMarketValue itemStashContents
    itemStashContentsValue joinPlayer joiner joiningPawns keepMonumentTicks
    laborers laborersCount laborersDurationDays laborersPawnKind
    landmarkName leaveDelay leaveDelayTicks leaveImmediatelyWhenSatisfied
    lerp listOfRewards lodgerCount lodgers lodgers0 lodgersAreParalyzed
    lodgersArePrisoners lodgersCount lodgersCountMinusOne
    lodgersCountWithMoodThreshold lodgersDisease lodgersDiseasePartsToAffect
    lodgersHaveBloodRot lodgersHaveBloodRotAndParalysis
    lodgersHaveMoodThreshold lodgersHaveNoConditions lodgersLabel
    lodgersLabelPlural lodgersLabelSingOrPluralDef lodgersMoodThreshold
    lodgersMoodThresholdNormalized lodgersPawnKind lodgersPronoun
    lodgersSingularOrPluralDef lodgersWillNotWork lodgersWithRoyalTitles
    loot lumpThreatDescription makePrisoners mech mechList mechViolation
    mechanitor mercenaryList minAge moodThresholdPawns moodThresholdWeight
    mustHaveSettlementOnLayer newTitle noConditionsWeight noWorkWeight
    numGroupsOf onlyAcceptColonists onlyAcceptHealthy overrideMass
    owningFaction paralysisWeight pawn pawnKindsParagraph pawnLabel
    pawnLabelPlural pawnLabelSingleOrPlural pawnOnMap pawns0
    peacefulChallengeRating permitFaction permitShuttle pilgrimCount
    pilgrimFaction pilgrimsLabelSingularOrPlural place playerSettlements
    playerSettlementsCount pointsCurve pointsOriginal prisoner
    prisonerFullRelationInfo problemCauserLabel psychicDroneGender
    psychicDroneLevel psychicSuppressorGender psylinkLevel
    punishmentOnDestroy questDurationTicks raid raid1 raidArrivalModeInfo
    raidCount raidIntervalAvg raidPawnKind raidPawnKinds refugee relic
    relicGlobalCount requestedThing requestedThingCount
    requestedThingDefName requireColonistCount requiredItems
    requiredPawnCount requiredPawns requiredWealth rescueDelay
    rescueShuttleAfterRaidDelay resource reward rewardDelayTicks rewardGiver
    rewardOnCompletion rewardValue rewards rewardsMarketValue roughOutlander
    roughTribe roundToDigits royalAskerNeedsResearchedFurniture sanguophage
    sanguophageCount sanguophageCountMinusOne sendAwayIfAllDespawned sender
    senderIsNull site site/MechCluster site/Outpost site/SleepingMechanoids
    siteFaction siteLabel sitePart0 sitePart1 sitePartsParams siteTile
    soldiers soldiers0 storeMoodThresholdAs storeNormalizedMoodThresholdAs
    studyRequirement tag targetMineable targetMineableThing terminalCount
    thrallCount threatDescription threatDescriptionParagraph threatsEnabled
    threatsInfoMechClustersMultiPrisoners threatsInfoMechClustersSingleHuman
    threatsInfoMechRaidsMultiHuman threatsInfoMechRaidsSingleHuman timeout
    timeoutTicks timer titleHeir titleHolder titlePreviousHeir venerateDate
    visitDurationTicks wastepackCount worker""".split()
)

# Symbols the engine injects into quest text with no <storeAs> anywhere.
INJECTED_SYMBOLS = {"resolvedQuestName", "questName", "questDescription"}

ROOT_SYMBOL = {
    "questNameRules": "questName",
    "questDescriptionRules": "questDescription",
}
RULE_PACK_FIELDS = (
    "questNameRules",
    "questDescriptionRules",
    "questDescriptionAndNameRules",
    "questContentRules",
    "questSubjectRules",
)

VAR_RE = re.compile(r"\$\(?\(?([A-Za-z_][A-Za-z0-9_]*)")
SYMBOL_RE = re.compile(r"\[([A-Za-z0-9_]+)\]")
RULE_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*(\((.*?)\))?\s*->(.*)$", re.S)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"
_ORDER = {ERROR: 0, WARN: 1, INFO: 2}


class Report:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str, str]] = []  # level, def, code, msg

    def add(self, level: str, defname: str, code: str, msg: str) -> None:
        self.items.append((level, defname, code, msg))

    @property
    def errors(self) -> int:
        return sum(1 for i in self.items if i[0] == ERROR)

    @property
    def warns(self) -> int:
        return sum(1 for i in self.items if i[0] == WARN)


# ---------------------------------------------------------------------------
# Corpus: node type names, and what each shipped QuestScriptDef stores
# ---------------------------------------------------------------------------


def _iter_quest_defs(path: Path):
    """Yield (defName, element) for every QuestScriptDef in an XML file."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return
    tags = [root] if root.tag == "QuestScriptDef" else root.findall(".//QuestScriptDef")
    for el in tags:
        name = el.findtext("defName")
        if name:
            yield name.strip(), el


def iter_parent_defs(path: Path):
    """Yield (Name, element) for abstract/named QuestScriptDefs - the ones a
    ParentName points at. RimWorld def inheritance is live here: a shipped quest
    routinely inherits its whole <root> tree and its text rules from one."""
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return
    tags = [root] if root.tag == "QuestScriptDef" else root.findall(".//QuestScriptDef")
    for el in tags:
        if el.get("Name"):
            yield el.get("Name"), el


def _merge(parent: ET.Element, child: ET.Element) -> ET.Element:
    """RimWorld def inheritance: same-tag nodes merge recursively and <li> lists
    APPEND to the parent's, unless the child carries Inherit="False"."""
    out = copy.deepcopy(parent)
    for c in child:
        if c.tag == "li":
            out.append(copy.deepcopy(c))
            continue
        existing = out.find(c.tag)
        if existing is None or (c.get("Inherit") or "").lower() == "false" or len(c) == 0:
            if existing is not None:
                out.remove(existing)
            out.append(copy.deepcopy(c))
        else:
            merged = _merge(existing, c)
            out.remove(existing)
            out.append(merged)
    return out


def resolve_inheritance(el: ET.Element, parents: dict) -> ET.Element:
    """Merge a def onto its ParentName chain."""
    pname = el.get("ParentName")
    if not pname or pname not in parents:
        return el
    merged = _merge(resolve_inheritance(parents[pname], parents), el)
    merged.attrib.pop("Name", None)
    merged.attrib.pop("Abstract", None)
    return merged


def build_corpus(game: Path) -> dict:
    """Index node type names and the shipped quest corpus."""
    asm = game / "RimWorldWin64_Data" / "Managed" / "Assembly-CSharp.dll"
    nodes: list[str] = []
    if asm.exists():
        out = subprocess.run(
            ["strings", "-n", "8", str(asm)], capture_output=True, text=True
        ).stdout
        nodes = sorted({
            ln.strip() for ln in out.splitlines()
            if re.fullmatch(r"QuestNode_[A-Za-z0-9_]+", ln.strip())
        })

    # Shipped quests all live under a .../Defs/QuestScriptDefs/... path. Scanning
    # only those keeps the index build to a second or two on a slow mount.
    stores: dict[str, list[str]] = {}
    parents: dict[str, str] = {}
    data = game / "Data"
    if data.exists():
        for xml in data.rglob("*.xml"):
            if not any("QuestScript" in part for part in xml.parts):
                continue
            for defname, el in _iter_quest_defs(xml):
                stores[defname] = sorted(collect_writes(el, corpus=None)[0])
            for name, el in iter_parent_defs(xml):
                parents[name] = ET.tostring(el, encoding="unicode")

    # Every quest a shipped IncidentDef names, so "will it ever fire?" knows about
    # a trigger that lives in another module.
    refs: list[str] = []
    for module in sorted((data.glob("*")) if data.exists() else []):
        inc = module / "Defs" / "IncidentDefs"
        if inc.is_dir():
            for xml in inc.rglob("*.xml"):
                try:
                    refs += _QSD_REF_RE.findall(xml.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    continue

    return {"nodes": nodes, "subscript_stores": stores, "parents": parents,
            "incident_refs": sorted(set(refs)), "game": str(game)}


def load_corpus(game: Path, refresh: bool) -> dict:
    if CACHE.exists() and not refresh:
        try:
            c = json.loads(CACHE.read_text())
            if c.get("game") == str(game) and c.get("nodes"):
                return c
        except (json.JSONDecodeError, OSError):
            pass
    c = build_corpus(game)
    try:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(c))
    except OSError:
        pass
    return c


# ---------------------------------------------------------------------------
# Slate analysis
# ---------------------------------------------------------------------------


def collect_writes(root: ET.Element, corpus: dict | None) -> tuple[set[str], set[str]]:
    """Return (slate vars written, subscript defNames referenced)."""
    written: set[str] = set(SEEDED_SLATE)
    subscripts: set[str] = set()
    for el in root.iter():
        cls = (el.get("Class") or "").split(".")[-1]

        # <storeAs>, <storeFactionAs>, <storeLoopCounterAs>, ...
        if re.fullmatch(r"store[A-Za-z0-9]*As", el.tag) and (el.text or "").strip():
            written.add(el.text.strip().lstrip("$"))

        if cls in DEFAULT_STORE and el.find("storeAs") is None:
            written.add(DEFAULT_STORE[cls])

        if cls in ("QuestNode_Set", "QuestNode_SetAndRestore"):
            name = el.findtext("name")
            if name:
                written.add(name.strip())

        if cls in ("QuestNode_SubScript", "QuestNode_Subscript"):
            callee = (el.findtext("def") or "").strip()
            if callee:
                subscripts.add(callee)
            prefix = (el.findtext("prefix") or "").strip()
            parms = el.find("parms")
            inner: set[str] = set()
            if parms is not None:
                inner |= {c.tag for c in parms}
            if corpus:
                inner |= set(corpus.get("subscript_stores", {}).get(callee, []))
            rets = el.find("returnVarNames")
            if rets is not None:
                inner |= {(c.text or "").strip() for c in rets if (c.text or "").strip()}
            for v in inner:
                written.add(f"{prefix}{v}" if prefix else v)
                if prefix:
                    written.add(v)

        # A list-valued var also registers <var>0, <var>1, ... - handled at read.
        if cls in ("QuestNode_AddToList", "QuestNode_AddRangeToList"):
            name = el.findtext("addTo") or el.findtext("name")
            if name:
                written.add(name.strip().lstrip("$"))

        # <addToList> is also a plain field on QuestNode_GeneratePawn and others.
        if el.tag == "addToList" and (el.text or "").strip():
            written.add(el.text.strip().lstrip("$"))
    return written, subscripts


def collect_reads(root: ET.Element) -> list[tuple[str, str]]:
    """Return (varname, containing tag) for every $var read in a field value."""
    out = []
    for el in root.iter():
        txt = (el.text or "").strip()
        if "$" in txt:
            for m in VAR_RE.finditer(txt):
                if m.group(1) in EXPR_FUNCS:
                    continue
                out.append((m.group(1), el.tag))
    return out


# ---------------------------------------------------------------------------
# Grammar
# ---------------------------------------------------------------------------


def parse_rules(pack: ET.Element) -> list[tuple[str, str, str]]:
    """Return (symbol, conditions, output) for each rule string in a RulePack."""
    rules = []
    strings = pack.find("rulesStrings")
    if strings is None:
        return rules
    for li in strings:
        raw = (li.text or "").strip()
        m = RULE_RE.match(raw)
        if m:
            rules.append((m.group(1), m.group(3) or "", m.group(4)))
    return rules


def is_conditional(conds: str) -> bool:
    """A rule is conditional if it constrains a slate var, not merely weighted."""
    if not conds.strip():
        return False
    for part in conds.split(","):
        part = part.strip()
        if not part:
            continue
        key = re.split(r"[=<>!\[]", part, maxsplit=1)[0].strip()
        if key not in RESERVED_RULE_PARAMS:
            return True
    return False


def symbol_resolves(sym: str, slate: set[str], defined: set[str]) -> bool:
    """QuestGenUtility.AddSlateVar trims the bracketed text until it hits a key:
    whole string, strip trailing digits, else truncate at the last '_', repeat."""
    if sym in defined or sym in INJECTED_SYMBOLS:
        return True
    s = sym
    while s:
        if s in slate:
            return True
        stripped = s.rstrip("0123456789")
        if stripped != s and stripped:
            s = stripped
            continue
        if "_" in s:
            s = s.rsplit("_", 1)[0]
            continue
        return False
    return False


# ---------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------


def check_def(defname: str, el: ET.Element, corpus: dict, rep: Report, src: Path) -> None:
    add = lambda lv, code, msg: rep.add(lv, defname, code, msg)
    nodes_known = set(corpus.get("nodes") or [])
    root = el.find("root")

    # --- structure -------------------------------------------------------
    if root is None:
        add(ERROR, "no-root", "<root> is missing. A QuestScriptDef without a node tree cannot generate.")
        return
    root_cls = (root.get("Class") or "").split(".")[-1]
    xml_composed = root_cls in ("QuestNode_Sequence", "")

    def fnum(tag, default=0.0):
        t = el.findtext(tag)
        try:
            return float((t or "").strip())
        except ValueError:
            return default

    weight = fnum("rootSelectionWeight")
    auto = (el.findtext("autoAccept") or "").strip().lower() == "true"
    special = (el.findtext("isRootSpecial") or "").strip().lower() == "true"
    selectable = (el.findtext("randomlySelectable") or "true").strip().lower() != "false"
    given_by = el.find("givenBy") is not None
    referenced = (defname in corpus.get("incident_refs", [])
                  or quest_referenced_by_incident(defname, src))
    fires = (weight > 0 and selectable) or special or given_by or referenced

    # A def with no text and no way to be offered is a Util_* sub-script, not a
    # playable quest. Vanilla ships 30 of them; the quest-level checks below would
    # be nonsense against one.
    shared_text = el.find("questDescriptionAndNameRules") is not None
    has_text = all(el.find(f) is not None for f in
                   ("questNameRules", "questDescriptionRules")) or shared_text
    fragment = not has_text and not fires
    if fragment:
        add(INFO, "sub-script",
            "No text rules and no firing route: read as a Util_* style sub-script and "
            "checked only for node names, slate and signals. If this was meant to be a "
            "playable quest, THAT is the defect - it will load and never occur.")

    # --- node class names ------------------------------------------------
    for node in el.iter():
        cls = node.get("Class")
        if not cls or not cls.split(".")[-1].startswith("QuestNode_"):
            continue
        short = cls.split(".")[-1]
        if "." in cls:
            add(INFO, "foreign-node",
                f"{cls} is another assembly's node. That is a hard dependency and a "
                f"load-order constraint - name the mod in <modDependencies> and confirm "
                f"the namespace by READING that assembly's metadata: point DLL in "
                f"src/RimMandrake/Utils/ilprobe/meta_core.py at the mod's dll, then look "
                f"for {short} in meta_core.typedefs (the name is there with its "
                f"namespace). Do NOT `strings` it - the blind-scan hook refuses a byte "
                f"scan of a .dll, and it earns the refusal: strings found 16 of 115 "
                f"names on our own companion, so a miss is not absence.")
        elif nodes_known and short not in nodes_known:
            near = [n for n in nodes_known if n.lower() == short.lower()]
            if near:
                add(WARN, "node-casing",
                    f"Class=\"{cls}\" differs in case from the real type {near[0]}. "
                    f"Vanilla itself ships both spellings of QuestNode_SubScript and "
                    f"QuestNode_Unset, so the loader tolerates it - but match the "
                    f"assembly, and never retype a class name you could copy.")
            else:
                add(ERROR, "unknown-node",
                    f"Class=\"{cls}\" is not a QuestNode type in Assembly-CSharp.dll. "
                    f"The def will fail to load. There are ~300 nodes and the "
                    f"near-misses are real - copy the name, do not recall it.")

    # --- slate -----------------------------------------------------------
    written, subscripts = collect_writes(el, corpus)
    # Vars a C# root or an unmodelled node injects are invisible here; the shipped
    # corpus supplies that vocabulary so ordinary text does not drown the report.
    known = written | CORPUS_SLATE
    opaque_root = not xml_composed
    known_defs = corpus.get("subscript_stores", {})
    for callee in sorted(subscripts):
        if known_defs and callee not in known_defs:
            add(WARN, "unknown-subscript",
                f"<QuestNode_SubScript><def>{callee}</def> is not a shipped "
                f"QuestScriptDef. If it is yours, fine; if it is a guess, generation aborts.")

    for var, tag in collect_reads(el):
        if var in known:
            continue
        base = var.rstrip("0123456789")
        if base in known:
            continue
        add(WARN, "unwritten-slate",
            f"<{tag}> reads ${var}, which nothing in this def stores. Either a typo, "
            f"or it comes from a sub-script - read the callee and confirm.")

    # --- grammar ---------------------------------------------------------
    packs = {f: el.find(f) for f in RULE_PACK_FIELDS}
    shared = parse_rules(packs["questDescriptionAndNameRules"]) if packs["questDescriptionAndNameRules"] is not None else []
    for field in ("questNameRules", "questDescriptionRules"):
        if not fragment and xml_composed and packs[field] is None and not shared:
            add(ERROR, "no-text",
                f"<{field}> is missing. Even fully hidden vanilla quests supply a "
                f"placeholder rather than omit it; the root symbol will not resolve.")

    for field, pack in packs.items():
        if pack is None:
            continue
        rules = parse_rules(pack) + (shared if field != "questDescriptionAndNameRules" else [])
        defined = {r[0] for r in rules}
        has_include = pack.find("include") is not None or pack.find("rulesFiles") is not None

        want = ROOT_SYMBOL.get(field)
        if want and want not in defined and not has_include and not shared \
                and xml_composed and not fragment:
            add(ERROR, "no-root-symbol",
                f"<{field}> defines no '{want}->' rule. The quest's "
                f"{'name' if want == 'questName' else 'description'} will be unresolvable.")

        # every conditional symbol needs an unconditional sibling
        conditional = [r[0] for r in rules if is_conditional(r[1])]
        unconditional = {r[0] for r in rules if not is_conditional(r[1])}
        lone = {s for s in conditional if conditional.count(s) == 1}
        for sym in sorted(lone - unconditional):
            if has_include:
                continue
            add(WARN, "no-fallback",
                f"<{field}> symbol '{sym}' has exactly one rule and it is conditional. "
                f"The instant that condition is false the WHOLE text is unresolvable - "
                f"add a bare '{sym}->' fallback (an empty one is the idiom). Vanilla "
                f"omits the fallback only where several conditional rules cover every "
                f"case between them.")

        for sym_name, conds, out in rules:
            for m in SYMBOL_RE.finditer(out):
                sym = m.group(1)
                if symbol_resolves(sym, known, defined) or has_include or opaque_root:
                    continue
                add(WARN, "unresolved-symbol",
                    f"<{field}> '{sym_name}' references [{sym}], which is neither a rule "
                    f"in this pack, nor stored in the slate, nor a name the shipped "
                    f"corpus uses. ONE unresolvable symbol fails the WHOLE rule - the "
                    f"text renders empty, not partially. This is what square brackets in "
                    f"a literal do: a title like '[XYZ] Blueprints' sends the resolver "
                    f"looking for a rule named XYZ.")
            # conditions naming a var that is never stored
            for part in conds.split(","):
                key = re.split(r"[=<>!\[]", part.strip(), maxsplit=1)[0].strip()
                if key and key not in RESERVED_RULE_PARAMS and key not in known:
                    if not opaque_root and not symbol_resolves(key, known, defined):
                        add(WARN, "condition-var",
                            f"<{field}> '{sym_name}' is conditioned on '{key}', which "
                            f"nothing stores in the slate; the condition can never be true.")

    # --- signals and ending ----------------------------------------------
    emitted: set[str] = set()
    for node in el.iter():
        if re.fullmatch(r"outSignal[A-Za-z0-9]*", node.tag):
            if node.tag == "outSignals" or list(node):
                emitted |= {(c.text or "").strip() for c in node if (c.text or "").strip()}
            elif (node.text or "").strip():
                emitted.add(node.text.strip())

    def signal_ok(sig: str, where: str) -> bool:
        if sig in emitted:
            return True
        if "." in sig:
            var, _, suffix = sig.rpartition(".")
            if var.lstrip("$") not in known:
                if not opaque_root:
                    add(WARN, "signal-var",
                        f"{where} listens for '{sig}' but nothing stores '{var}' in the "
                        f"slate. An object signal is <slateVarName>.<Suffix> - rename a "
                        f"storeAs and every inSignal on it silently stops firing, with no "
                        f"error. (A dotted name whose prefix is not a slate var is a "
                        f"namespaced custom signal, which is fine.)")
            elif suffix not in SIGNAL_SUFFIXES:
                add(ERROR, "bad-signal-suffix",
                    f"{where} listens for '{sig}': '{var}' is a slate object but "
                    f"'.{suffix}' is not one of the QuestTargetSignalPart suffixes, so it "
                    f"can never fire.")
                return False
            elif suffix not in SIGNAL_PRECEDENT:
                add(INFO, "signal-no-precedent",
                    f"{where} listens for '.{suffix}': legal, but no shipped def uses it, "
                    f"so there is nothing to copy. (For a dead quest pawn vanilla uses "
                    f".Destroyed, never .Killed.)")
            return True
        if not opaque_root and not subscripts:
            add(WARN, "unemitted-signal",
                f"{where} listens for custom signal '{sig}', which no outSignal in this "
                f"def emits. That branch is dead.")
        return False

    ends = [n for n in el.iter() if (n.get("Class") or "").split(".")[-1] == "QuestNode_End"]
    if not ends and xml_composed and not fragment and not subscripts:
        add(WARN, "no-end",
            "No QuestNode_End anywhere. QuestNode_End -> QuestPart_QuestEnd is the only "
            "exit, so unless one of these nodes emits that part itself, the quest can "
            "never resolve or fail. Four shipped defs trip this legitimately (a "
            "specialised node ends them); everything else that trips it is a bug.")

    for node in el.iter():
        cls = (node.get("Class") or "").split(".")[-1]
        for tag in ("inSignal", "inSignalEnable", "inSignalDisable", "inSignalLeave",
                    "inSignalRemovePawn", "inSignalChoiceUsed"):
            v = node.findtext(tag)
            if v and v.strip():
                signal_ok(v.strip(), f"<{cls or node.tag}> {tag}")
        lst = node.find("inSignals")
        if lst is not None:
            for c in lst:
                if (c.text or "").strip():
                    signal_ok(c.text.strip(), f"<{cls or node.tag}> inSignals")

    outcomes = {(e.findtext("outcome") or "").strip() for e in ends}
    if ends and "Success" not in outcomes and xml_composed and not fragment \
            and not subscripts:
        add(WARN, "no-success",
            "No QuestNode_End with <outcome>Success</outcome>. Success and failure are "
            "structural, not computed - one End per terminal branch, outcome hard-coded.")
    if ends and not any(o in ("Fail", "InvalidPreAcceptance") for o in outcomes) \
            and xml_composed and not fragment and not subscripts:
        add(WARN, "no-fail",
            "No End with outcome Fail. A quest that cannot be lost has no stakes, and "
            "with no map-loss branch it can also hang forever.")
    for e in ends:
        o = (e.findtext("outcome") or "").strip()
        if o and o not in ("Success", "Fail", "Unknown", "InvalidPreAcceptance"):
            add(ERROR, "bad-outcome",
                f"<outcome>{o}</outcome> is not a QuestEndOutcome. The four are "
                f"Success, Fail, Unknown, InvalidPreAcceptance.")

    # --- root fields: the ConfigErrors the game enforces ------------------
    expire_raw = (el.findtext("expireDaysRange") or "").strip()
    expire_max = 0.0
    if expire_raw:
        try:
            expire_max = max(float(x) for x in re.split(r"[~,]", expire_raw))
        except ValueError:
            expire_max = 0.0

    if weight > 0 and not auto and expire_max <= 0:
        add(ERROR, "config-expire",
            "rootSelectionWeight > 0 with no autoAccept and no expireDaysRange is a "
            "ConfigError the game reports at startup. Give the offer a window.")
    if auto and expire_max > 0:
        add(ERROR, "config-autoaccept",
            "autoAccept together with expireDaysRange is a ConfigError - an "
            "auto-accepted quest has no offer to expire.")
    # --- will it ever fire? ----------------------------------------------
    if fnum("defaultChallengeRating") > 0 and not fires:
        add(WARN, "config-challenge",
            "defaultChallengeRating > 0 on a def that is not a root quest (IsRootAny) is "
            "a ConfigError. A Util_* sub-script must not carry a star rating.")

    if not fires and not fragment:
        add(WARN, "never-fires",
            "This def takes none of the firing routes: no rootSelectionWeight (+ "
            "randomlySelectable, - isRootSpecial), no <givenBy>, and no IncidentDef "
            "beside it names it. It will load, appear in the def dump, and never occur. "
            "That is deliberate for a Util_* sub-script; otherwise pick a route - and "
            "give yourself a deterministic trigger rather than waiting on the storyteller.")
    if weight > 2.0:
        add(INFO, "weight-out-of-family",
            f"rootSelectionWeight {weight} is out of family - shipped values run 0.15-2.0. "
            f"The last-fired quest is already damped to 1%, so a quest that 'never fires' "
            f"is nearly always failing rootMinPoints / rootMinProgressScore / TestRun, "
            f"not under-weighted. Raise the weight last.")

    if not fragment and (el.findtext("everAcceptableInSpace") or "").strip().lower() != "true":
        add(INFO, "space-acceptance",
            "everAcceptableInSpace is unset, so Accept is greyed out while the colony is "
            "on a space map (AcceptanceRequirementNotSpace). Invisible in ground testing; "
            "set it true for any campaign that spends time off-planet.")


_INCIDENT_CACHE: dict[str, set[str]] = {}
_QSD_REF_RE = re.compile(r"<questScriptDef>\s*([A-Za-z0-9_]+)\s*</questScriptDef>")


def quest_referenced_by_incident(defname: str, src: Path) -> bool:
    """Does an IncidentDef anywhere in the same mod name this quest?

    Scanned once per mod and cached - the naive per-def sweep is minutes on a
    Windows mount."""
    mod_root = src.parent
    for cand in src.parents:
        if (cand / "About").is_dir() or cand.name == "Defs":
            mod_root = cand.parent if cand.name == "Defs" else cand
            break
    key = str(mod_root)
    if key not in _INCIDENT_CACHE:
        found: set[str] = set()
        try:
            for xml in mod_root.rglob("*.xml"):
                try:
                    txt = xml.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if "questScriptDef" in txt:
                    found |= set(_QSD_REF_RE.findall(txt))
        except OSError:
            pass
        _INCIDENT_CACHE[key] = found
    return defname in _INCIDENT_CACHE[key]


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--dir", type=Path, action="append", default=[],
                    help="validate every .xml under this directory")
    ap.add_argument("--game", type=Path, default=DEFAULT_GAME)
    ap.add_argument("--refresh", action="store_true", help="rebuild the corpus cache")
    ap.add_argument("--quiet", action="store_true", help="suppress INFO findings")
    args = ap.parse_args()

    files = list(args.paths)
    for d in args.dir:
        files += sorted(d.rglob("*.xml"))
    if not files:
        ap.error("give at least one XML path or --dir")

    corpus = load_corpus(args.game, args.refresh)
    if not corpus.get("nodes"):
        print(f"note: no Assembly-CSharp.dll under {args.game} - node names unchecked",
              file=sys.stderr)

    # Abstract parents: those beside the files being checked win over the shipped
    # ones of the same name.
    parents: dict[str, ET.Element] = {}
    for name, xml in (corpus.get("parents") or {}).items():
        try:
            parents[name] = ET.fromstring(xml)
        except ET.ParseError:
            continue
    for f in files:
        for name, el in iter_parent_defs(f):
            parents[name] = el

    rep = Report()
    checked = 0
    for f in files:
        found = False
        for defname, el in _iter_quest_defs(f):
            found = True
            checked += 1
            pname = el.get("ParentName")
            if pname and pname not in parents:
                rep.add(WARN, defname, "missing-parent",
                        f"ParentName=\"{pname}\" resolves to no QuestScriptDef here or in "
                        f"the shipped corpus. Everything it was meant to inherit - root "
                        f"tree, text rules - is absent, and the def will not load.")
            check_def(defname, resolve_inheritance(el, parents), corpus, rep, f)
        if not found and f in args.paths:
            try:
                ET.parse(f)
                rep.add(WARN, f.name, "no-quest", "no <QuestScriptDef> in this file")
            except ET.ParseError as e:
                rep.add(ERROR, f.name, "unparseable", f"XML will not parse: {e}")

    order = sorted(rep.items, key=lambda i: (_ORDER[i[0]], i[1], i[2]))
    for level, defname, code, msg in order:
        if args.quiet and level == INFO:
            continue
        print(f"{level:5} {defname}  [{code}]\n      {msg}")

    print(f"\n{checked} QuestScriptDef(s) checked - "
          f"{rep.errors} error(s), {rep.warns} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
