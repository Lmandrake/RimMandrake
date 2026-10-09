"""validation.py -- modcheck suite for RimUtinni WasteRun (mandrake.rut.wasterun).
WARCASKET_WASTE_RUN_REMAINDER_1 FIRST SCRIPT. Walk: design/validation_walks/RimUtinni/WasteRun.md.

Grounded in the mod's whole source: Defs/QuestScriptDefs/RUT_WasteRun.xml, Defs/IncidentDefs,
Defs/HistoryEventDefs, Patches/RUT_CaskBay_WasteRunPlanner.xml, Source/*.cs.

WHAT IS PROVEN OFFLINE (static_checks, run `python3 validation.py`): every destination in the C# enum has
a QuestNode_Signal listening on the exact signal name the cask-bay command sends; every history event
the quest records is defined; the comp patch names a class that exists; every settings field is Scribed
and listed in suite.toggles; the walk exists.

WHAT IS UNMEASURED UNTIL THE FIRST LIVE RUN: that the quest generates (jawa/fire_quest), that the
RM_CaskBay gizmo appears, and that choosing a destination fires the signal. No bridge tool presses a
Command_Action or sends a quest signal: filed as WASTE_RUN_SIGNAL_DEBUG_HOOK_1.
THEORY RULED OUT while writing: a runtime QuestNode_RandomNode would re-roll per signal. It does not:
the node runs ONCE at generation, so the Slime outcome is fixed when the quest is offered.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.join(HERE, "..", "..", "RimMandrake", "Utils")
if os.path.isdir(_UTILS) and _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)

from modcheck import Suite, ExpectationFailed

suite = Suite("WasteRun")
suite.toggles = ["masterEnabled", "offerEnabled", "dropOnEmpireEnabled", "freezeColdSideEnabled",
                 "entombAssailantsEnabled", "propaneLakeEnabled", "slimeExperimentEnabled",
                 "throatCaskEnabled", "throatRadiationEnabled", "throatShipFaultsEnabled",
                 "throatBurstEnabled", "throatDecayEnabled"]
SETTINGS = "RimMandrake.Utinni.WasteRun.WasteRunSettings"
QUEST = "RUT_WasteRun"
HISTORY = ["RUT_WasteRunDroppedOnEmpire", "RUT_WasteRunFrozen", "RUT_WasteRunEntombed",
           "RUT_WasteRunPropaneIgnited", "RUT_WasteRunSlimeNeutralized", "RUT_WasteRunSlimeBloomed",
           "RUT_WasteRunSlimeUnknown"]
_FIELD = re.compile(r"public static (bool|int|float) (\w+)\s*=")


def _live(t):
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _src(*parts):
    return open(os.path.join(HERE, *parts), encoding="utf-8").read()


def settings_fields():
    body = re.sub(r"//[^\n]*", "", _src("Source", "WasteRunSettings.cs")).split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(body))


@suite.chain("defs_and_load")
def defs_and_load(t):
    shipped = ["QuestScriptDef/%s" % QUEST, "ThingDef/RUT_ThroatCask", "ThoughtDef/RUT_ThroatCaskNear", "IncidentDef/RUT_WasteRunOffer"] + ["HistoryEventDef/%s" % h for h in HISTORY]
    with t.component("defs_resolve"):
        r = t.bridge_call("jawa/get_defs", defs=";".join(shipped), fields="defName")
        if _live(t):
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound") or r.get("foundCount") != len(shipped):
                _fail("shipped defs did not all resolve: %s" % str(r)[:240])
    with t.component("absent_def_is_refused"):
        r = t.bridge_call("jawa/get_defs", defs="QuestScriptDef/RUT_WasteRunDoesNotExist", fields="defName")
        if _live(t) and (not isinstance(r, dict) or r.get("foundCount")):
            _fail("get_defs answered for a def that does not exist: %s" % str(r)[:200])
    with t.component("cask_bay_gained_planner_comp"):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_CaskBay", fields="comps")
        if _live(t):
            if "WasteRunPlanner" not in str(r):
                _fail("RM_CaskBay has no RUT_CompProperties_WasteRunPlanner (patch matched nothing?): %s" % str(r)[:240])


@suite.chain("settings_roundtrip")
def settings_roundtrip(t):
    with t.component("settings_probe_finds_fields", beyond_toggle=True):
        if sorted(settings_fields()) != sorted(suite.toggles):
            _fail("suite.toggles %s differs from the C# fields %s" % (sorted(suite.toggles), sorted(settings_fields())))
    for field in sorted(settings_fields()):
        with t.component("%s_round_trips" % field, toggle=field):
            if not _live(t):
                continue
            def raw(action, value=None):
                kw = dict(typeName=SETTINGS, action=action, field=field)
                if value is not None:
                    kw["value"] = str(value)
                r = t.session.call("jawa/mod_settings_field", **kw)
                return r if isinstance(r, dict) else {}
            old = raw("get").get("value")
            if old is None:
                _fail("%s: get returned no value" % field)
            new = "False" if str(old).lower() == "true" else "True"
            try:
                raw("set", new)
                if str(raw("get").get("value")).lower() != new.lower():
                    _fail("%s: wrote %s, read back differently" % (field, new))
            finally:
                raw("set", old)


def static_checks():
    bad = []
    quest = _src("Defs", "QuestScriptDefs", "RUT_WasteRun.xml")
    kernel = _src("Source", "WasteRunKernel.cs")
    enum = re.search(r"enum WasteDestination\s*\{([^}]*)\}", kernel)
    names = [n.strip() for n in enum.group(1).split(",")] if enum else []
    if len(names) != 5:
        bad.append("expected 5 destinations in the enum, found %r (sanity probe)" % names)
    for n in names:
        if "<inSignal>WasteDest_%s</inSignal>" % n not in quest:
            bad.append("destination %s has no QuestNode_Signal listening on WasteDest_%s" % (n, n))
    # CONTROL: the check must be able to fail.
    if "<inSignal>WasteDest_NotADestination</inSignal>" in quest:
        bad.append("control signal present: static check is blind")
    events = open(os.path.join(HERE, "Defs", "HistoryEventDefs", "RUT_WasteRunEvents.xml"), encoding="utf-8").read()
    for h in re.findall(r"<historyDef>(\w+)</historyDef>|<reason>(\w+)</reason>", quest):
        h = h[0] or h[1]
        if "<defName>%s</defName>" % h not in events:
            bad.append("quest records undefined history event %s" % h)
    for h in HISTORY:
        if h not in events:
            bad.append("history event %s missing from Defs" % h)
    if "WasteRunKernel.QuestScriptDefName = \"%s\"" % QUEST not in kernel.replace("const string QuestScriptDefName", "WasteRunKernel.QuestScriptDefName").replace(" =", " ="):
        if 'QuestScriptDefName = "%s"' % QUEST not in kernel:
            bad.append("kernel QuestScriptDefName does not match the quest defName")
    csproj = _src("Source", "RimMandrake.Utinni.WasteRun.csproj")
    for fn in os.listdir(os.path.join(HERE, "Source")):
        if fn.endswith(".cs") and 'Include="%s"' % fn not in csproj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    settings = _src("Source", "WasteRunSettings.cs")
    for f in settings_fields():
        if '"%s"' % f not in settings.split("ExposeData", 1)[1]:
            bad.append("settings field %s is not Scribed" % f)
    if sorted(settings_fields()) != sorted(suite.toggles):
        bad.append("suite.toggles differs from the settings fields")
    patch = _src("Patches", "RUT_CaskBay_WasteRunPlanner.xml")
    comp = re.search(r'Class="([\w.]+)"\s*/>', patch)
    if not comp or comp.group(1).split(".")[-1] not in _src("Source", "WasteRunDisposal.cs"):
        bad.append("patch names a comp class that is not in the source")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimUtinni", "WasteRun.md")):
        bad.append("walk missing")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
