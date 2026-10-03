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
                 "restraintHours"]

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
        raise_body = hoist[hoist.index("public void RaiseCradle()"):hoist.index("public override IEnumerable<Gizmo> GetGizmos()")]
        if raise_body.find("GateOpen") < 0 or raise_body.find("GateOpen") > raise_body.find("TakeAll"):
            raise ExpectationFailed("RaiseCradle can empty a holder before checking its gate")
    with t.component("frame_defs_resolve_live", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_HoistFrame;ThingDef/RM_SealedPit;GenStepDef/RM_HoistFrames")
        if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
            raise ExpectationFailed("frame defs missing live: %r" % r)


# Live mechanics are NOT components here: a component with nothing to ask would record PASS. They are walk lines
# marked UNCOVERED until a drive exists (walk: design/validation_walks/RimMandrake/KeelHoist.md):
#   items + a downed wild animal down RM_LanternDeepMineshaft and back up, manifest 2 DOWN + 2 UP, beast restrained;
#   CanLaunch refused with the cable down ("Reel in the keel hoist first."), accepted after reel-in or tetherLock off;
#   a downed hostile humanlike lowered to a cell target arrives IsPrisonerOfColony;
#   a Forge home map with a foundry tower door gets a paired RM_HoistFrame beside it (RM_HoistFrames genstep);
#   RM_SealedPit owned by a faction with able members on the map refuses Raise cradle, and lifts once they are gone.
