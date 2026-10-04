"""validation.py -- modcheck suite for RimMandrake: Keel Hoist (mandrake.rm.keelhoist). First script.

Item HOIST_SHIP_PART_BUILD_1; design design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md §2 (RULED).
Walk: design/validation_walks/RimMandrake/KeelHoist.md (## must be true carries the coverage arrows).

Offline components read the shipped XML/C# (no game); live ones ask the bridge and record UNMEASURED with
no session. Learned while building (2026-10-03, RimSage-read):
  * Dialog_EnterPortal's pawn list is private and passes allowCapturableDownedPawns false, and
    CaravanFormingUtility.CanListAsAutoCapturable only ever admits humanlikes, so a downed WILD animal is not
    sendable through any vanilla portal. The hoist adds both through a postfix scoped to RM_KeelHoist.
  * There is no animal prisoner status; "arrives captured" for a beast is RM_HoistRestraint (Moving setMax 0).
  * PortalContainerProxy drops a hauled thing straight onto the other map; the hoist swaps in its own proxy so
    the hidden transit timer applies. A rider who walks in is spawned below by JobDriver_EnterPortal and lifted
    back into transit next tick (despawning inside OnEntered would break the job's own post-spawn code).
"""
import os
import re
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

suite = Suite("KeelHoist")
suite.toggles = ["masterEnabled", "requireGravEngine", "tetherLock", "colonistsMayRide",
                 "downedStrangersAndBeasts", "openLineMeter", "cycleTimeMultiplier", "cableRange",
                 "restraintHours", "pitSales", "pitPriceMultiplier", "pitArenaHints", "arenaFighterBonus",
                 "pitSites", "chuteEnabled", "chuteHouseCut", "chuteJackpotChance", "chuteBustChance", "chuteHours"]

HERE = os.path.dirname(os.path.abspath(__file__))


def _live(t):
    return t.session is not None and not t.upstream_failed


def _xml(*parts):
    return ET.parse(os.path.join(HERE, *parts)).getroot()


def _src(name):
    with open(os.path.join(HERE, "Source", name), encoding="utf-8") as f:
        return f.read()


@suite.chain("defs_and_wiring")
def defs_and_wiring(t):
    """The hoist, its research row and the restraint hediff exist, and the ship-part rules are in the defs."""
    t.clear_area(size=6)
    with t.component("hoist_is_a_researched_ship_part", beyond_toggle=True):
        d = _xml("Defs", "ThingDefs_Buildings", "RM_KeelHoist.xml").find("ThingDef")
        if d is None or d.findtext("defName") != "RM_KeelHoist":   # sanity probe: the instrument sees the def
            raise ExpectationFailed("RM_KeelHoist ThingDef not read from its file")
        if d.findtext("thingClass") != "RimMandrake.KeelHoist.RM_KeelHoist":
            raise ExpectationFailed("thingClass is %r" % d.findtext("thingClass"))
        if "RimMandrake.KeelHoist.PlaceWorker_NeedsGravEngine" not in [li.text for li in d.findall("placeWorkers/li")]:
            raise ExpectationFailed("hoist is not limited to a gravship")
        if [li.text for li in d.findall("researchPrerequisites/li")] != ["RM_KeelHoist"]:
            raise ExpectationFailed("hoist is not gated on its research row")
        r = _xml("Defs", "ResearchProjectDefs", "RM_KeelHoist.xml").find("ResearchProjectDef")
        if [li.text for li in r.findall("prerequisites/li")] != ["BasicGravtech"]:
            raise ExpectationFailed("research row is not on the gravship branch")
        t.screenshot()
    with t.component("defs_resolve_live", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs="ThingDef/RM_KeelHoist;ResearchProjectDef/RM_KeelHoist;HediffDef/RM_HoistRestraint")
        if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
            raise ExpectationFailed("defs missing live: %r" % r)
        t.screenshot()


@suite.chain("source_rules")
def source_rules(t):
    """Static reads of the C# for the rules the item names; each is a guard against a ruled-out shortcut."""
    t.clear_area(size=6)
    hoist, patches = _src("RM_KeelHoist.cs"), _src("KeelHoistPatches.cs")
    with t.component("no_pocket_map_ever", beyond_toggle=True):
        body = hoist[hoist.index("public override Map GetOtherMap()"):hoist.index("public override IntVec3 GetDestinationLocation()")]
        if "base.GetOtherMap" in body or "GeneratePocketMap" in hoist:
            raise ExpectationFailed("the hoist can fall through to MapPortal's pocket-map generation")
    with t.component("shared_sendable_list_untouched", beyond_toggle=True):
        if re.search(r"HarmonyPatch\(typeof\(CaravanFormingUtility\)", patches):
            raise ExpectationFailed("AllSendablePawns is patched; the item forbids it (every caravan reads it)")
        if "is RM_KeelHoist" not in patches:
            raise ExpectationFailed("the Dialog_EnterPortal postfix is not scoped to the hoist")
    with t.component("tether_lock_on_can_launch", beyond_toggle=False):
        if "HarmonyPatch(typeof(Building_GravEngine), nameof(Building_GravEngine.CanLaunch))" not in patches:
            raise ExpectationFailed("no tether-lock postfix on Building_GravEngine.CanLaunch")
    with t.component("csproj_lists_every_source", beyond_toggle=True):
        proj = _src("RM_KeelHoist.csproj")
        missing = [f for f in os.listdir(os.path.join(HERE, "Source"))
                   if f.endswith(".cs") and 'Compile Include="%s"' % f not in proj]
        if missing:
            raise ExpectationFailed("compiled into nothing (EnableDefaultCompileItems false): %s" % missing)


@suite.chain("fixed_site_frames")
def fixed_site_frames(t):
    """HOIST_FIXED_SITE_FRAMES_1: the head-frame is genstep-placed only; the Foundry tower door carries it."""
    t.clear_area(size=6)
    with t.component("frame_not_player_buildable", beyond_toggle=True):
        defs = {d.findtext("defName"): d for d in _xml("Defs", "ThingDefs_Buildings", "RM_HoistFrame.xml").findall("ThingDef")}
        if set(defs) != {"RM_HoistFrame", "RM_SealedPit"}:   # sanity probe: the instrument sees both defs
            raise ExpectationFailed("read %s" % sorted(defs))
        for name, d in defs.items():
            for field in ("designationCategory", "researchPrerequisites", "costList"):
                if d.find(field) is not None:
                    raise ExpectationFailed("%s carries %s, so a player could build it" % (name, field))
    with t.component("genstep_registered_and_tower_wired", beyond_toggle=True):
        reg = _xml("Patches", "RM_HoistFrames_Register.xml")
        if "RM_HoistFrames" not in [li.text for li in reg.iter("li")]:
            raise ExpectationFailed("RM_HoistFrames not added to Base_Player")
        tower = ET.parse(os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches",
                                      "RUT_FoundryTowerHoistFrame.xml")).getroot()
        op = tower.find("Operation")
        if op is None or op.findtext("xpath") != '/Defs/ThingDef[defName="RM_HoistFrame"]':
            raise ExpectationFailed("tower wiring is not guarded on RM_HoistFrame existing")
        if not [li for li in tower.iter("li") if li.get("Class") == "RimMandrake.KeelHoist.RM_HoistFrameSiteExtension"]:
            raise ExpectationFailed("tower door does not get RM_HoistFrameSiteExtension")
    with t.component("holder_lift_waits_for_gate", beyond_toggle=True):
        hoist = _src("RM_KeelHoist.cs")
        raise_body = hoist[hoist.index("void RaiseCradle()"):hoist.index("public override IEnumerable<Gizmo> GetGizmos()")]
        if raise_body.find("GateOpen") < 0 or raise_body.find("GateOpen") > raise_body.find("TakeAll"):
            raise ExpectationFailed("RaiseCradle can empty a holder before checking its gate")
    with t.component("frame_defs_resolve_live", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_HoistFrame;ThingDef/RM_SealedPit;GenStepDef/RM_HoistFrames")
        if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
            raise ExpectationFailed("frame defs missing live: %r" % r)


HUTT_XML = os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Defs", "HuttSlavePit", "RUT_HuttSlavePit.xml")
PROOF = "RimMandrake.KeelHoist.RM_PitBuyerProof"


def _proof(t, method, arg):
    """jawa/static_call into RM_PitBuyerProof. No session -> UNMEASURED (never a silent PASS)."""
    if t.session is None:
        t.upstream_reason = "UNMEASURED: no bridge session for %s" % method
        t.upstream_failed = True
        return None
    r = t.bridge_call("jawa/static_call", type=PROOF, method=method, args=arg)
    text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
    if text.startswith("UNMEASURED"):
        t.upstream_reason = text
        t.upstream_failed = True
        return None
    return text


@suite.chain("hutt_slave_pit")
def hutt_slave_pit(t):
    """HUTT_SLAVE_PIT_SITE_BUILD_1: the generic buyer pit (RM_PitBuyer.cs) and the Hutt site that uses it (RUT XML).
    Live: ProofLayOut lays the RUT_HuttSlavePit site part out on the CURRENT map (needs the Hutt Cartel faction in
    the world for keepers), ProofSell lowers a fresh colony prisoner through the head-frame and runs both trips,
    ProofGate raises the cradle while keepers stand (refused) then after killing them (lifted, arriving prisoners)."""
    t.clear_area(size=8)
    with t.component("hutt_site_defs_are_data_on_generic_classes", beyond_toggle=True):
        root = ET.parse(HUTT_XML).getroot()
        names = {(d.tag, d.findtext("defName")) for d in root}
        want = {("ThingDef", "RUT_HuttSlavePitShaft"), ("SitePartDef", "RUT_HuttSlavePit"), ("QuestScriptDef", "RUT_Quest_HuttSlavePit")}
        if names != want:   # sanity probe: the instrument reads exactly the three defs
            raise ExpectationFailed("read %s" % sorted(names))
        for d in root:
            if d.get("MayRequire") != "mandrake.rm.keelhoist":
                raise ExpectationFailed("%s is not MayRequire'd on the keel hoist" % d.findtext("defName"))
        shaft = root.find("ThingDef")
        if shaft.findtext("thingClass") != "RimMandrake.KeelHoist.RM_SealedHolder" or \
                shaft.find("modExtensions/li[@Class='RimMandrake.KeelHoist.RM_PitBuyerExtension']") is None:
            raise ExpectationFailed("the shaft is not a buyer holder")
        ext = root.find("SitePartDef/modExtensions/li")
        if ext is None or ext.findtext("holderDef") != "RUT_HuttSlavePitShaft" or ext.findtext("factionDef") != "RUT_Jawa_HuttCartel":
            raise ExpectationFailed("site part does not lay out the shaft for the Hutt Cartel")
        if "RimMandrake.KeelHoist.RM_QuestNode_BuyerPitSite" not in [li.get("Class") for li in root.iter("li")]:
            raise ExpectationFailed("the quest never makes the site")
    with t.component("no_free_colonist_is_ever_sold", beyond_toggle=True):
        holder, patches = _src("RM_HoistFrame.cs"), _src("KeelHoistPatches.cs")
        can = holder[holder.index("public virtual bool CanAccept"):holder.index("public bool Accept(")]
        acc = holder[holder.index("public bool Accept("):holder.index("public List<Pawn> TakeAll()")]
        if "p.IsColonist && !p.IsSlave" not in can or acc.find("CanAccept") < 0 or acc.find("CanAccept") > acc.find("DeSpawn"):
            raise ExpectationFailed("a colonist can reach the pit before the refusal")
        if "IsColonist && !p.IsSlave" not in patches:
            raise ExpectationFailed("the lowering dialog still lists free colonists for a buyer pit")
    with t.component("pit_laid_out_with_frame_and_keepers", toggle="pitSites"):
        text = _proof(t, "ProofLayOut", "RUT_HuttSlavePit")
        if text is not None:
            if not text.startswith("LAIDOUT") or "frame=none" in text or "keepers=0" in text or "chute=none" in text:
                raise ExpectationFailed("layout: %s" % text[:240])
            # LIVE 2026-10-03: gate=True beside keepers=3 on the bland map. GateOpen() is open BY DESIGN on a map whose
            # parent faction is the player (Map.ParentFaction == OfPlayer), and the bland colony IS that map, so the
            # sealed-while-keepers-stand half is not measurable here (ProofGate below says so for itself).
            t.screenshot()
    with t.component("lowered_prisoner_sold_for_silver", toggle="pitSales"):
        text = _proof(t, "ProofSell", "Slave")
        if text is not None:
            m = re.search(r"silverOnMap=(\d+)", text)
            if not text.startswith("SOLD") or not m or int(m.group(1)) < 1:
                raise ExpectationFailed("sale: %s" % text[:240])
    with t.component("oubliette_sealed_until_taken", beyond_toggle=True):
        sealed = _proof(t, "ProofGate", "hold")
        if sealed is not None:
            if "open=False" not in sealed or not re.search(r"heldBefore=(\d+) heldAfter=\1\b", sealed):
                raise ExpectationFailed("pit opened while its keepers stand: %s" % sealed[:240])
            taken = _proof(t, "ProofGate", "conquer")
            if taken is not None and ("open=True" not in taken or "heldAfter=0" not in taken):
                raise ExpectationFailed("taken pit did not give up its slaves: %s" % taken[:240])


CHUTE_PROOF = "RimMandrake.KeelHoist.RM_ChanceChuteProof"


def _setting_default(src, name):
    m = re.search(r"public static (?:float|bool) %s = ([0-9.]+|true|false)f?;" % name, src)
    if not m:
        raise ExpectationFailed("default of %s not read from KeelHoistMod.cs" % name)
    return float(m.group(1)) if m.group(1)[0].isdigit() else m.group(1) == "true"


@suite.chain("chance_chute")
def chance_chute(t):
    """HUTT_LOTTERY_CHUTE_BUILD_1: the chance chute at a house's site (RM_ChanceChute.cs). Live needs the Hutt pit
    laid out on the current map first (hutt_slave_pit chain's ProofLayOut places the chute with the house's faction)."""
    t.clear_area(size=8)
    with t.component("chute_placed_by_the_site_only", beyond_toggle=True):
        d = _xml("Defs", "ThingDefs_Buildings", "RM_ChanceChute.xml").find("ThingDef")
        if d is None or d.findtext("defName") != "RM_ChanceChute":   # sanity probe
            raise ExpectationFailed("RM_ChanceChute not read")
        for field in ("designationCategory", "researchPrerequisites", "costList"):
            if d.find(field) is not None:
                raise ExpectationFailed("the chute carries %s, so a player could build it" % field)
        if ET.parse(HUTT_XML).getroot().find("SitePartDef/modExtensions/li").findtext("chuteDef") != "RM_ChanceChute":
            raise ExpectationFailed("the Hutt site does not lay out a chute")
    with t.component("house_edge_at_shipped_odds", toggle="chuteEnabled"):
        src = _src("KeelHoistMod.cs")
        cut, jack, bust = (_setting_default(src, n) for n in ("chuteHouseCut", "chuteJackpotChance", "chuteBustChance"))
        ev = (1 - cut) * (jack * 3 + bust * 0.3 + (1 - jack - bust) * 0.9)
        chute = _src("RM_ChanceChute.cs")
        if "return 3f;" not in chute or "return 0.3f;" not in chute or "Rand.Range(0.7f, 1.1f)" not in chute:
            raise ExpectationFailed("the roll is not the ruled 3x / 0.3x / 0.7-1.1x shape")
        if not (0 < cut < 1) or ev >= 1:
            raise ExpectationFailed("shipped odds return %.3f of a stake; the house must keep an edge" % ev)
        text = None
        if t.session is not None:
            r = t.bridge_call("jawa/static_call", type=CHUTE_PROOF, method="ProofOdds", args="5000")
            text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
            m = re.search(r"meanPayout=(\d+)", text)
            if not m or int(m.group(1)) >= 1000:
                raise ExpectationFailed("live odds do not favour the house: %s" % text[:200])
    with t.component("staked_pawns_are_recorded_never_vanished", beyond_toggle=True):
        chute = _src("RM_ChanceChute.cs")
        body = chute[chute.index("protected override string ReceiveBelow"):chute.index("protected override void Tick()")]
        if "PassToWorld" not in body or "stakedLabels.Add" not in body or "Destroy" in body.split("else")[0]:
            raise ExpectationFailed("a staked pawn is not passed to the world and named")
        text = _proof_cls(t, CHUTE_PROOF, "ProofStake", "Slave")
        if text is not None:
            if not text.startswith("STAKED") or "timerSet=True" not in text or "stakedPawnWorld=True" not in text \
                    or "stakedPawnFaction=none" in text:
                raise ExpectationFailed("stake: %s" % text[:240])


def _proof_cls(t, cls, method, arg):
    if t.session is None:
        t.upstream_reason = "UNMEASURED: no bridge session for %s" % method
        t.upstream_failed = True
        return None
    r = t.bridge_call("jawa/static_call", type=cls, method=method, args=arg)
    text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
    if text.startswith("UNMEASURED"):
        t.upstream_reason = text
        t.upstream_failed = True
        return None
    return text


# ============================================================================ static gates and formulas
# KEELHOIST_COVERAGE_GAPS_1 (offline half). Pure reads of the shipped C#/XML, no game; every function takes the source
# texts as a dict so selftest_keelhoist.py can plant a break in memory. The live behaviours (a hoist cycle with cargo, the
# tether lock refusing a real launch, a beast arriving restrained) stay UNMEASURED: they need a live gravship + hoist.

def load_srcs():
    d = os.path.join(HERE, "Source")
    return dict((f, _src(f)) for f in sorted(os.listdir(d)) if f.endswith(".cs"))


def method_body(src, header_re):
    """Text of the first brace-balanced block after the first match of header_re, or None."""
    m = re.search(header_re, src)
    if not m:
        return None
    i = src.find("{", m.end())
    semi = src.find(";", m.end())
    if semi >= 0 and (i < 0 or semi < i):
        return src[m.end():semi]          # expression-bodied member
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(src)):
        depth += (src[j] == "{") - (src[j] == "}")
        if depth == 0:
            return src[i:j + 1]
    return None


# setting -> (file, method header regex, how the OFF arm must degrade). 'guard' = an early-out `if (... !setting ...) {... return}`
# that precedes anything else; 'used' = the setting is read inside the method.
GATES = [
    ("masterEnabled", "RM_KeelHoist.cs", r"public override bool IsEnterable\(", "guard"),
    ("masterEnabled", "RM_KeelHoist.cs", r"public override IEnumerable<Gizmo> GetGizmos\(\)", "used"),
    ("masterEnabled", "RM_HoistFrame.cs", r"public override void Generate\(Map map", "guard"),
    ("requireGravEngine", "PlaceWorker_NeedsGravEngine.cs", r"public override AcceptanceReport AllowsPlacing\(", "guard"),
    ("tetherLock", "KeelHoistPatches.cs", r"public static void Postfix\(Building_GravEngine", "guard"),
    ("colonistsMayRide", "RM_KeelHoist.cs", r"public override void OnEntered\(", "used"),
    ("colonistsMayRide", "KeelHoistPatches.cs", r"public static void Postfix\(Dialog_EnterPortal", "used"),
    ("downedStrangersAndBeasts", "RM_KeelHoist.cs", r"public static bool TryCapture\(", "guard"),
    ("downedStrangersAndBeasts", "KeelHoistPatches.cs", r"public static void Postfix\(Dialog_EnterPortal", "used"),
    ("openLineMeter", "KeelHoistPatches.cs", r"public override void MapComponentTick\(\)", "guard"),
    ("cycleTimeMultiplier", "RM_KeelHoist.cs", r"public static int CycleTicksFor\(", "used"),
    ("cableRange", "RM_KeelHoist.cs", r"public bool IsValidCableTarget\(", "used"),
    ("restraintHours", "RM_KeelHoist.cs", r"public static bool TryCapture\(", "used"),
    ("pitSales", "RM_HoistFrame.cs", r"public bool KeepersBuying", "used"),
]


def gate_findings(srcs):
    out = []
    for setting, fn, header, kind in GATES:
        body = method_body(srcs.get(fn, ""), header)
        if body is None:
            out.append("%s: cannot read %s in %s (gate check blind)" % (setting, header, fn))
            continue
        if ("KeelHoistSettings." + setting) not in body:
            out.append("%s is never read in %s %s: the toggle does nothing there" % (setting, fn, header))
            continue
        if kind == "guard":
            first_if = re.search(r"if\s*\((?:[^{};]*)\)\s*\{[^{}]*\breturn\b", body)
            if not first_if or ("!KeelHoistSettings." + setting) not in first_if.group(0):
                out.append("%s: no early-out guard `if (!%s ...) { ... return }` in %s" % (setting, setting, fn))
    # the tether lock must refuse by ACCEPTANCE REPORT with the user-facing sentence, and only while the cable is down
    tl = method_body(srcs.get("KeelHoistPatches.cs", ""), r"public static void Postfix\(Building_GravEngine") or ""
    if "hoist.CableDown" not in tl or "new AcceptanceReport(" not in tl or "ValidSubstructureAt" not in tl:
        out.append("tether lock: must refuse via AcceptanceReport only for a hoist whose cable is down and that stands on this ship's substructure")
    return out


SLIDER_RE = re.compile(r"(\w+) = (?:Mathf\.Round\()?list\.Slider\(\1, ([0-9.]+)f, ([0-9.]+)f\)")


def settings_findings(srcs):
    """Every setting: declared field default == Scribe default; each toggle in suite.toggles exists; every slider's range
    contains its shipped default (a default outside the slider cannot be reached again after one drag)."""
    src = srcs.get("KeelHoistMod.cs", "")
    out = []
    fields = dict((m.group(2), m.group(3)) for m in re.finditer(r"public static (bool|float) (\w+) = ([0-9.]+|true|false)f?;", src))
    if len(fields) < 19:
        return ["only %d settings fields parsed from KeelHoistMod.cs: parse failure" % len(fields)]
    scribe = dict((m.group(1), m.group(2)) for m in re.finditer(r'Scribe_Values\.Look\(ref (\w+), "\1", ([0-9.]+|true|false)f?\);', src))
    for name, dv in sorted(fields.items()):
        if name not in scribe:
            out.append("%s is not saved (no Scribe_Values.Look)" % name)
        elif scribe[name] != dv:
            out.append("%s default %s but its Scribe default is %s" % (name, dv, scribe[name]))
    for name in suite.toggles:
        if name not in fields:
            out.append("declared toggle %s is not a settings field" % name)
    sliders = dict((m.group(1), (float(m.group(2)), float(m.group(3)))) for m in SLIDER_RE.finditer(src))
    for name, (lo, hi) in sliders.items():
        if name in fields and not lo <= float(fields[name]) <= hi:
            out.append("%s default %s lies outside its slider %s..%s" % (name, fields[name], lo, hi))
    for name, dv in fields.items():
        if dv not in ("true", "false") and name not in sliders:
            out.append("float setting %s has no slider in the settings window" % name)
        if dv in ("true", "false") and not re.search(r"CheckboxLabeled\([^;]*ref %s," % name, src):
            out.append("bool setting %s has no checkbox in the settings window" % name)
    return out


def cycle_formula(srcs):
    """(base, floor, mass_divisor) parsed from CycleTicksFor and BaseCycleTicks, or None."""
    base = re.search(r"public const int BaseCycleTicks = (\d+);", srcs.get("RM_KeelHoist.cs", ""))
    body = method_body(srcs.get("RM_KeelHoist.cs", ""), r"public static int CycleTicksFor\(") or ""
    f = re.search(r"Mathf\.Max\((\d+), Mathf\.RoundToInt\(BaseCycleTicks \* KeelHoistSettings\.cycleTimeMultiplier \* \(1f \+ mass / (\d+)f\)\)\)", body)
    if not base or not f:
        return None
    return int(base.group(1)), int(f.group(1)), int(f.group(2))


def cycle_ticks(formula, mass, mult):
    base, floor, div = formula
    return max(floor, int(round(base * mult * (1.0 + mass / float(div)) + 1e-9)))


def open_line_step(srcs, level, cable_open):
    rise = re.search(r"RisePerHour = ([0-9.]+)f;", srcs.get("KeelHoistPatches.cs", ""))
    fall = re.search(r"FallPerHour = ([0-9.]+)f;", srcs.get("KeelHoistPatches.cs", ""))
    if not rise or not fall:
        return None
    return level + float(rise.group(1)) if cable_open else max(0.0, level - float(fall.group(1)))


def formula_findings(srcs, hediff_root):
    out = []
    fm = cycle_formula(srcs)
    if fm is None:
        return ["CycleTicksFor no longer has the parsed shape Max(floor, Round(BaseCycleTicks * cycleTimeMultiplier * (1 + mass/div)))"]
    base, floor, div = fm
    if base != 625:
        out.append("BaseCycleTicks is %d, the ruled quarter hour is 625 (2500/4)" % base)
    if cycle_ticks(fm, 0, 1.0) != 625:
        out.append("a weightless load at the default multiplier takes %d ticks, not 625" % cycle_ticks(fm, 0, 1.0))
    if div != 50:
        out.append("mass divisor is %d, ruled 50 (a 50 kg load doubles the cycle time)" % div)
    if cycle_ticks(fm, div, 1.0) != 2 * cycle_ticks(fm, 0, 1.0):
        out.append("a load of %d kg does not double the cycle time" % div)
    if not (cycle_ticks(fm, 10, 1.0) < cycle_ticks(fm, 40, 1.0) < cycle_ticks(fm, 90, 1.0)):
        out.append("cycle time is not strictly increasing with mass")
    lo, hi = 0.25, 4.0
    for mm in SLIDER_RE.finditer(srcs.get("KeelHoistMod.cs", "")):
        if mm.group(1) == "cycleTimeMultiplier":
            lo, hi = float(mm.group(2)), float(mm.group(3))
    if not (cycle_ticks(fm, 0, lo) < cycle_ticks(fm, 0, 1.0) < cycle_ticks(fm, 0, hi)):
        out.append("the multiplier slider ends do not bracket the default cycle time")
    if cycle_ticks(fm, 0, lo) <= floor:
        out.append("the slider's fastest setting (%.2fx) hits the %d-tick floor: the slider's low end is dead" % (lo, floor))
    if "t.GetStatValue(StatDefOf.Mass) * t.stackCount" not in method_body(srcs.get("RM_KeelHoist.cs", ""), r"public static int CycleTicksFor\(") \
            or "p.GetStatValue(StatDefOf.Mass)" not in srcs.get("RM_KeelHoist.cs", ""):
        out.append("a stack's mass is not item mass x stackCount, or a pawn's is not its own Mass stat")
    # Open Line meter: +1 per open hour, -0.5 per closed hour, floored at 0
    if open_line_step(srcs, 0.0, True) is None:
        out.append("Open Line constants RisePerHour/FallPerHour not parseable")
    else:
        up = 0.0
        for _ in range(10):
            up = open_line_step(srcs, up, True)
        down = up
        for _ in range(30):
            down = open_line_step(srcs, down, False)
        if up != 10.0 or open_line_step(srcs, 0.3, False) != 0.0 or down != 0.0 or open_line_step(srcs, 2.0, False) != 1.5:
            out.append("Open Line meter arithmetic: 10 open hours -> %s (want 10), fall from 2.0 -> %s (want 1.5), floor 0" % (up, open_line_step(srcs, 2.0, False)))
    if "TicksGame % GenDate.TicksPerHour != 137" not in srcs.get("KeelHoistPatches.cs", ""):
        out.append("Open Line meter is not stepped once per hour")
    # restraint: ticksToDisappear = restraintHours * 2500, and the shipped default 24 h equals the hediff's own 60000
    cap = method_body(srcs.get("RM_KeelHoist.cs", ""), r"public static bool TryCapture\(") or ""
    if "Mathf.RoundToInt(KeelHoistSettings.restraintHours * GenDate.TicksPerHour)" not in cap or "ticksToDisappear" not in cap:
        out.append("restraint duration is not restraintHours x TicksPerHour written to ticksToDisappear")
    mod = srcs.get("KeelHoistMod.cs", "")
    rh = re.search(r"public static float restraintHours = ([0-9.]+)f;", mod)
    dis = hediff_root.findtext(".//HediffCompProperties_Disappears/disappearsAfterTicks") if hediff_root is not None else None
    dis = dis or next((e.text for e in hediff_root.iter("disappearsAfterTicks")), None) if hediff_root is not None else None
    if not rh or not dis or int(float(rh.group(1)) * 2500) != int(dis):
        out.append("hediff disappearsAfterTicks %s disagrees with restraintHours default %s x 2500" % (dis, rh.group(1) if rh else None))
    if hediff_root is None or hediff_root.findtext(".//capMods/li/capacity") != "Moving" or hediff_root.findtext(".//capMods/li/setMax") != "0":
        out.append("RM_HoistRestraint no longer caps Moving at 0 (the beast would walk out of the cradle)")
    if "HediffMaker.MakeHediff(KeelHoistDefOf.RM_HoistRestraint" not in cap or "p.Faction == null" not in cap:
        out.append("only an unowned (wild) animal may be restrained")
    return out


@suite.chain("static_gates_and_formulas")
def static_gates_and_formulas(t):
    """KEELHOIST_COVERAGE_GAPS_1 offline half: every settings toggle is read where it must gate (off arm degrades, never errors),
    the cycle-time and Open Line formulas hold their ruled numbers, and the restraint hediff matches its setting. Order:
    cheap-and-wrong first (a failing component marks later ones UNMEASURED)."""
    srcs = load_srcs()
    with t.component("settings_are_saved_declared_and_reachable", beyond_toggle=True):
        if len(srcs) < 7:   # sanity probe: all seven source files read
            raise ExpectationFailed("read only %d source files" % len(srcs))
        bad = settings_findings(srcs)
        if bad:
            raise ExpectationFailed("; ".join(bad[:4]))
    with t.component("every_gate_reads_its_toggle_where_it_must", beyond_toggle=True):
        bad = gate_findings(srcs)
        if bad:
            raise ExpectationFailed("; ".join(bad[:4]))
    with t.component("cycle_time_open_line_and_restraint_formulas_hold", beyond_toggle=True):
        bad = formula_findings(srcs, _xml("Defs", "HediffDefs", "RM_HoistRestraint.xml").find("HediffDef"))
        if bad:
            raise ExpectationFailed("; ".join(bad[:4]))
    for name, why in (
        ("hoist_cycle_moves_cargo_down_and_up", "needs a live gravship, a powered hoist and a target (instrument: a proof hook driving LowerCableTo/BeginTransit)"),
        ("tether_lock_refuses_a_real_launch", "needs a launchable gravship with the cable down (instrument: CanLaunch call on a live engine)"),
        ("beast_arrives_restrained_live", "needs a downed wild animal lowered live (RM_HoistRestraint is checked statically above)"),
    ):
        with t.component(name, beyond_toggle=True):
            if _live(t):
                t.upstream_reason = "UNMEASURED: " + why
                t.upstream_failed = True


# Live mechanics are NOT components here: a component with nothing to ask would record PASS. They are walk lines
# marked UNCOVERED until a drive exists (walk: design/validation_walks/RimMandrake/KeelHoist.md):
#   items + a downed wild animal down RM_LanternDeepMineshaft and back up, manifest 2 DOWN + 2 UP, beast restrained;
#   CanLaunch refused with the cable down ("Reel in the keel hoist first."), accepted after reel-in or tetherLock off;
#   a downed hostile humanlike lowered to a cell target arrives IsPrisonerOfColony;
#   a Forge home map with a foundry tower door gets a paired RM_HoistFrame beside it (RM_HoistFrames genstep);
#   RM_SealedPit owned by a faction with able members on the map refuses Raise cradle, and lifts once they are gone.
#   (Hutt pit) a caravan or a peacefully landed gravship reaches RUT_HuttSlavePit (GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1)
#   and sells a downed WILD beast through the dialog; the arena-week price bonus is read off the inspect string.
