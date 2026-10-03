"""northstar_driver plan for Atlas (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Atlas \\
      --plan src/RimUtinni/Atlas/northstar_plan.py
Live (bridge held, game up with a quicktest world and the Atlas deployed):
  python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Atlas \\
      --plan src/RimUtinni/Atlas/northstar_plan.py --deploy-mod Atlas

The mock below is an in-memory model of exactly what the suite asserts: the Atlas's
debug-action log lines (REPORT / POLL / FORGOT), its settings fields, and three pieces
of evidence (a finished research row, a forced weather, a spawned pawn). It proves the
SCRIPT, never the game. ATLAS_MOCK_BREAK=<comma list> re-introduces one defect each, so
every check can be seen red:
  no_poll        a poll lights nothing even with the evidence present
  off_ignored    detectionEnabled=False does not stop a poll
  missing_entry  one entry is absent from the live report (a discarded def)
  bad_default    rewardsEnabled ships ON
Dev tooling, never deployed."""
import glob
import os
import xml.etree.ElementTree as ET

MOD = "Atlas"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rut.atlas",)
NEED_GOD = False
RECT = None

HERE = os.path.dirname(os.path.abspath(__file__))
_EVIDENCE = {   # entry -> (kind, subject) for the three entries the suite lights
    "RUT_Atlas_ScrapShrine": ("research", "RUT_Rites_ScrapShrine"),
    "RUT_Atlas_BoilingRain": ("weather", "RUT_BoilingRain"),
    "RUT_Atlas_Mynock": ("pawn", "RSW_Mynock"),
}
_DEFAULTS = {
    "detectionEnabled": "True", "pollIntervalTicks": "250", "hintsAllowed": "True",
    "showTrueNameOnHint": "False", "showUnavailable": "True", "showCounters": "True",
    "toastsEnabled": "True", "flipAnimation": "True", "lightsPulse": "True",
    "rewardsEnabled": "False", "rewardScale": "1",
}


def _breaks():
    return set(x for x in os.environ.get("ATLAS_MOCK_BREAK", "").split(",") if x)


def _entries():
    out = []
    for f in glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True):
        for e in ET.parse(f).getroot().findall("RimMandrake.Utinni.Atlas.AtlasEntryDef"):
            out.append(e.findtext("defName"))
    return sorted(out)


class _Atlas(object):
    def __init__(self):
        self.entries = _entries()
        self.lit = set()
        self.research = set()
        self.weather = None
        self.pawns = []
        self.log = []
        self.settings = dict(_DEFAULTS)
        if "bad_default" in _breaks():
            self.settings["rewardsEnabled"] = "True"

    def evidence(self, entry):
        kind, subj = _EVIDENCE.get(entry, (None, None))
        return ((kind == "research" and subj in self.research)
                or (kind == "weather" and subj == self.weather)
                or (kind == "pawn" and subj in self.pawns))

    def poll(self):
        brk = _breaks()
        on = self.settings["detectionEnabled"] == "True" or "off_ignored" in brk
        n = 0
        if on and "no_poll" not in brk:
            for e in self.entries:
                if e not in self.lit and self.evidence(e):
                    self.lit.add(e)
                    n += 1
        self.log.append("[Atlas] POLL lit=%d detection=%s" % (n, self.settings["detectionEnabled"]))

    def report(self):
        for i, e in enumerate(self.entries):
            if "missing_entry" in _breaks() and i == 0:
                continue
            self.log.append("[Atlas] REPORT entry=%s available=True lit=%s triggers=X" % (e, e in self.lit))


def mock_extension(game, tool, p):
    a = getattr(game, "_atlas", None)
    if a is None:
        a = game._atlas = _Atlas()
    if tool == "rimworld/execute_debug_action":
        path = str(p.get("path"))
        if path.endswith("Report entry availability"):
            a.report()
        elif path.endswith("Poll all triggers now"):
            a.poll()
        elif path.endswith("Forget all entries"):
            a.lit.clear()
            a.log.append("[Atlas] FORGOT all")
        else:
            return {"success": False, "message": "no such debug action %s" % path}
        return {"success": True}
    if tool == "jawa/drain_log":
        want = p.get("contains") or ""
        lim = int(p.get("limit") or 200)
        msgs = [{"text": m} for m in a.log if want in m][-lim:]
        return {"success": True, "messages": msgs}
    if tool == "jawa/mod_settings_field":
        f = p["field"]
        if f not in a.settings:
            return {"success": False, "message": "no field %s" % f}
        if p.get("action") == "set":
            v = str(p["value"])
            a.settings[f] = v
        return {"success": True, "value": a.settings[f]}
    if tool == "jawa/get_defs":
        if str(p.get("defs")) == "MainButtonDef/RUT_Atlas":
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{
                "defName": "RUT_Atlas", "found": True,
                "fields": {"tabWindowClass": "RimMandrake.Utinni.Atlas.MainTabWindow_Atlas"}}]}
        return None
    if tool == "jawa/research_finish_project":
        a.research.add(p.get("project"))
        return {"success": True}
    if tool == "jawa/weather_set":
        a.weather = p.get("weather")
        return {"success": True}
    if tool == "jawa/spawn_pawn":
        a.pawns.append(p.get("kindDef") or p.get("kind") or p.get("pawnKind") or "RSW_Mynock")
        return None     # fall through: the base mock records the pawn and returns its id
    return None
