"""validation.py -- modcheck suite for RimUtinni: Scavenger's Atlas (mandrake.rut.atlas).

The first script (design/RimMandrake/debug_process.md §2). Walk:
design/validation_walks/RimUtinni/Atlas.md. Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Atlas \\
      --plan src/RimUtinni/Atlas/northstar_plan.py

Grounded in Source/: GameComponent_Atlas (PollAll / Discover / records), AtlasTriggers
(the eleven trigger kinds), AtlasSettings (eleven scalar fields + disabledCategories),
AtlasDebugActions (the READ-BACK channel: "Report entry availability" logs one
`[Atlas] REPORT entry=<defName> available=<bool> lit=<bool>` line per entry; "Poll all
triggers now" logs `[Atlas] POLL lit=<n> detection=<bool>`; "Forget all entries" logs
`[Atlas] FORGOT all`). The Atlas's state lives in a GameComponent with no bridge getter,
so the debug-action log line is the read-back, per suite.expect_log_contains's docstring.

Each lighting chain starts from "Forget all entries", builds its own evidence, polls
deterministically through the debug action (never waits for the 250-tick cadence) and
reads the entry's REPORT line back. Three kinds are exercised, one per completion rule
(owner ruling Q6): USED/PERFORMED via a finished research row (the scrap shrine rite),
LIVED-THROUGH via forced weather (boiling rain), SEEN via a spawned creature (mynock).

Likely first-live-run corrections:
  1. the debug-action PATH. DesertVehicleReskin's working call is
     "Actions\\\\<label>" with no category segment; this suite copies that shape.
  2. jawa/weather_set may start a transition; WeatherManager.curWeather is what the
     trigger reads. If the poll misses it, add t.wait_ticks before polling.
  3. the spawned mynock must stand on an unfogged cell (the SEEN rule); the test
     anchor is in the colony's open area, which a quicktest map has unfogged.
"""
import glob
import os
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

suite = Suite("Atlas")

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.Utinni.Atlas.AtlasSettings"
PKG = "mandrake.rut.atlas"
DEBUG = "Actions\\%s"
A_REPORT, A_POLL, A_FORGET = "Report entry availability", "Poll all triggers now", "Forget all entries"

# Shipped defaults, read off AtlasSettings.cs (public static field initialisers).
DEFAULTS = {
    "detectionEnabled": True, "pollIntervalTicks": 250, "hintsAllowed": True,
    "showTrueNameOnHint": False, "showUnavailable": True, "showCounters": True,
    "toastsEnabled": True, "flipAnimation": True, "lightsPulse": True,
    "rewardsEnabled": False, "rewardScale": 1.0,
}
ALT = {"pollIntervalTicks": 500, "rewardScale": 2.0}
suite.toggles = sorted(DEFAULTS)


def _entry_names():
    names = []
    for f in glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True):
        for e in ET.parse(f).getroot().findall("RimMandrake.Utinni.Atlas.AtlasEntryDef"):
            names.append(e.findtext("defName"))
    return sorted(names)


ENTRIES = _entry_names()


def _live(t):
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _debug(t, label):
    r = t.bridge_call("rimworld/execute_debug_action", path=DEBUG % label)
    if _live(t) and not (r or {}).get("success", False):
        _fail("execute_debug_action(%s) did not succeed: %r" % (label, r))
    return r


def _log_lines(t, contains, limit=400):
    r = t.bridge_call("jawa/drain_log", limit=limit, contains=contains)
    return [m.get("text", "") for m in ((r or {}).get("messages") or [])]


def _report(t):
    """entry defName -> {"available": bool, "lit": bool}, from the LAST report."""
    _debug(t, A_REPORT)
    rows = {}
    for line in _log_lines(t, "[Atlas] REPORT entry=", limit=2000):
        parts = dict(p.split("=", 1) for p in line.split() if "=" in p)
        if "entry" in parts:
            rows[parts["entry"]] = {"available": parts.get("available") == "True",
                                    "lit": parts.get("lit") == "True"}
    return rows


def _poll(t):
    _debug(t, A_POLL)
    lines = _log_lines(t, "[Atlas] POLL lit=")
    return lines[-1] if lines else None


def _get_setting(t, field):
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
    return (r or {}).get("value")


def _same(got, want):
    if isinstance(want, bool):
        return str(got) == str(want)
    try:
        return abs(float(got) - float(want)) < 1e-6
    except (TypeError, ValueError):
        return False


def _set(t, field, value):
    t.set_setting(SETTINGS, {field: value})


def _expect_lit(t, entry, want=True):
    rows = _report(t)
    if not _live(t):
        return
    row = rows.get(entry)
    if row is None:
        _fail("no REPORT line for %s (rows read: %d)" % (entry, len(rows)))
    if not row["available"]:
        _fail("%s reads available=False: its subject is not loaded in this environment" % entry)
    if row["lit"] != want:
        _fail("%s lit=%s, wanted lit=%s" % (entry, row["lit"], want))


# --------------------------------------------------------------------------- chain: log

@suite.chain("log")
def log_chain(t):
    with t.component("log_clean", beyond_toggle=True):
        if _live(t):
            for tag in ("Config error in " + PKG, "RimMandrake.Utinni.Atlas", "[Atlas] trigger",
                        "RUT_Atlas_"):
                bad = [m for m in _log_lines(t, tag)
                       if "error" in m.lower() or "exception" in m.lower()]
                t._record("drain_log(%r) error lines -> %r" % (tag, bad), not bad)
                if bad:
                    _fail("error-looking log line mentioning %r: %r" % (tag, bad[:3]))


# --------------------------------------------------------------------------- chain: defs

@suite.chain("defs")
def defs_chain(t):
    with t.component("tab_def", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="MainButtonDef/RUT_Atlas", fields="tabWindowClass")
        if _live(t):
            if not (r or {}).get("success") or (r or {}).get("foundCount") != 1:
                _fail("MainButtonDef RUT_Atlas not found: %r" % r)
            got = str(((r.get("defs") or [{}])[0].get("fields") or {}).get("tabWindowClass"))
            if "MainTabWindow_Atlas" not in got:
                _fail("RUT_Atlas.tabWindowClass is %r, not MainTabWindow_Atlas" % got)

    with t.component("entries_resolve", beyond_toggle=True):
        rows = _report(t)
        if _live(t):
            missing = [e for e in ENTRIES if e not in rows]
            if missing:
                _fail("%d of %d entries in Defs/ are missing from the live report (discarded "
                      "defs?): %s" % (len(missing), len(ENTRIES), missing))
            absent = sorted(e for e, r in rows.items() if not r["available"])
            t._record("entries absent from this world (subject mod not loaded): %s" % absent, True)


# --------------------------------------------------------------------------- chain: settings

@suite.chain("settings")
def settings_chain(t):
    with t.component("defaults", beyond_toggle=True):
        if _live(t):
            wrong = {f: _get_setting(t, f) for f, w in DEFAULTS.items() if not _same(_get_setting(t, f), w)}
            if wrong:
                _fail("settings not at shipped defaults (or missing): %s" % wrong)
            bogus = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get",
                                  field="noSuchField_probe")
            if (bogus or {}).get("success") is not False:
                _fail("sanity probe: a nonexistent field did not fail loudly: %r" % bogus)


def _roundtrip(field):
    def body(t):
        with t.component("%s_roundtrip" % field, toggle=field):
            if _live(t):
                try:
                    _set(t, field, ALT.get(field, not DEFAULTS[field]))
                finally:
                    _set(t, field, DEFAULTS[field])
                if not _same(_get_setting(t, field), DEFAULTS[field]):
                    _fail("%s did not restore to its shipped default" % field)
    return body


for _f in sorted(DEFAULTS):
    suite.chain("settings_%s" % _f)(_roundtrip(_f))


# --------------------------------------------------------------------------- lighting chains

@suite.chain("research_lights")
def research_lights(t):
    """PERFORMED: a found rite is a research row; finishing it lights the scrap shrine."""
    _debug(t, A_FORGET)
    with t.component("unlit_before", toggle="detectionEnabled"):
        _expect_lit(t, "RUT_Atlas_ScrapShrine", want=False)
    with t.component("lit_after_research", toggle="detectionEnabled"):
        r = t.bridge_call("jawa/research_finish_project", project="RUT_Rites_ScrapShrine")
        if _live(t) and not (r or {}).get("success", False):
            _fail("research_finish_project(RUT_Rites_ScrapShrine) failed: %r" % r)
        _poll(t)
        _expect_lit(t, "RUT_Atlas_ScrapShrine", want=True)


@suite.chain("detection_off")
def detection_off(t):
    """detectionEnabled off: a poll lights nothing even with the evidence present.
    The evidence is laid here, not borrowed from research_lights, so this check cannot
    pass vacuously when chains run alone or in another order."""
    _debug(t, A_FORGET)
    with t.component("poll_lights_nothing_when_off", toggle="detectionEnabled"):
        if _live(t):
            try:
                _set(t, "detectionEnabled", False)
                r = t.bridge_call("jawa/research_finish_project", project="RUT_Rites_ScrapShrine")
                if not (r or {}).get("success", False):
                    _fail("research_finish_project(RUT_Rites_ScrapShrine) failed: %r" % r)
                line = _poll(t) or ""
                if "lit=0" not in line or "detection=False" not in line:
                    _fail("poll with detection off reported %r" % line)
                _expect_lit(t, "RUT_Atlas_ScrapShrine", want=False)
            finally:
                _set(t, "detectionEnabled", True)


@suite.chain("weather_lights")
def weather_lights(t):
    """LIVED THROUGH: forcing the boiling rain on the map lights its entry."""
    _debug(t, A_FORGET)
    with t.component("lit_under_boiling_rain", toggle="detectionEnabled"):
        r = t.bridge_call("jawa/weather_set", weather="RUT_BoilingRain")
        if _live(t) and not (r or {}).get("success", False):
            _fail("weather_set(RUT_BoilingRain) failed: %r" % r)
        _poll(t)
        _expect_lit(t, "RUT_Atlas_BoilingRain", want=True)
        t.screenshot()  # live evidence; under --mock the driver substitutes a desktop capture


@suite.chain("seen_lights")
def seen_lights(t):
    """SEEN: a mynock standing on an unfogged cell lights its entry."""
    t.clear_area(size=12)
    _debug(t, A_FORGET)
    with t.component("lit_when_seen", toggle="detectionEnabled"):
        pawn = t.spawn_pawn("RSW_Mynock")
        if _live(t) and not pawn:
            _fail("spawn_pawn(RSW_Mynock) returned nothing")
        _poll(t)
        _expect_lit(t, "RUT_Atlas_Mynock", want=True)
        t.screenshot()  # live evidence; under --mock the driver substitutes a desktop capture
