"""validation.py -- modcheck suite for RimMandrake: Oasis Maker (mandrake.rm.oasismaker).

First north-star script (OASIS_MAKER_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/OasisMaker.md.
RM_OasisMaker: a treasure-class, minifiable, non-buildable ancient building. Placed on shaded ground beside standing rock it
attunes, then grows an oasis ring by ring (Sand -> Gravel -> Soil -> SoilRich at the margin; the centre climbs to WaterShallow),
never converting rock, floors or existing water, and freezing (never reversing) when it loses shade or rock.

CHAINS
  defs_resolve        RM_OasisMaker (parsed from the XML) resolves live; a control name reads notFound.
  settings_roundtrip  every `public static` field of RM_OasisMakerSettings (bool/int/float): default / write / restore.
  def_wiring          minifiedDef MinifiedThing, tradeTags has ExoticMisc, the placeWorker is ours, and the def is not buildable
                      (no designationCategory): the acquisition ruling (trade or scenario start only).
  dormant_on_bare_sand  on a cleared pad of plain Sand with no roof and no rock the machine reads Dormant after 600 ticks.
  site_growth         on a roofed Sand pad ringed by rough granite: reads Attuning; with masterEnabled off and fast settings it
                      does NOT finish; with masterEnabled on and fast settings it reads "The oasis is made.", the centre holds
                      WaterShallow and the rock strips are still Granite_Rough; then removing the roof freezes it (Dormant) and
                      the converted terrain stays. Every setting is restored in a finally.
  placement_gate      the green/red ghost and the refusal message: UNMEASURED (needs a placement ghost).
  slow_timing         the shipped 2-day attuning and ~3-day first ring at default settings: UNMEASURED (game days).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.OasisMaker.RM_OasisMakerSettings"
DEF = "RM_OasisMaker"
CONTROL_ABSENT = "ThingDef/RM_OasisMakerNoSuchDef_ZZ"
ROCK = "Granite_Rough"        # vanilla rough stone: SmoothableStone affordance, so RM_OasisPlacementScorer.IsRockCell counts it
BARE = "Sand"
FAST = {"attuningDays": "0", "baseRingDays": "0.001"}      # settings numbers, not a mod change: ring time ~60 ticks
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def shipped_defs():
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def settings_fields():
    src = open(os.path.join(HERE, "Source", "RM_OasisMakerSettings.cs"), encoding="utf-8").read()
    body = src.split("class RM_OasisMakerSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if (("ThingDef", DEF)) not in SHIPPED:
        return ["ThingDef %s not parsed from Defs/ (sanity probe failed): %r" % (DEF, SHIPPED[:3])]
    fields = settings_fields()
    if len(fields) < 5:
        return ["settings probe found %d fields (sanity probe failed, expected 11)" % len(fields)]
    src = open(os.path.join(HERE, "Source", "RM_OasisMakerSettings.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    for n in FAST:
        if n not in fields:
            bad.append("the fast-growth setting %s no longer exists: site_growth would time out" % n)
    proj = open(os.path.join(HERE, "Source", "RM_OasisMaker.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    d = [el for el in ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_OasisMaker.xml")).getroot()
         if el.findtext("defName") == DEF][0]
    if d.findtext("minifiedDef") != "MinifiedThing":
        bad.append("minifiedDef is not MinifiedThing")
    if "ExoticMisc" not in [li.text for li in d.findall("tradeTags/li")]:
        bad.append("tradeTags lacks ExoticMisc: the machine is no longer sold")
    if d.find("designationCategory") is not None or d.find("costList") is not None:
        bad.append("the def is buildable: the ruling is trade + scenario start only")
    if "RimMandrake.OasisMaker.RM_PlaceWorker_OasisMaker" not in [li.text for li in d.findall("placeWorkers/li")]:
        bad.append("the placeWorker is not wired")
    comp = open(os.path.join(HERE, "Source", "RM_CompOasisMaker.cs"), encoding="utf-8").read()
    for needle in ("Dormant.", "Attuning.", "The oasis is made."):
        if needle not in comp:
            bad.append("inspect string %r is gone from RM_CompOasisMaker.cs: site_growth reads it" % needle)
    kernel = open(os.path.join(HERE, "Source", "Kernel", "RM_OasisKernel.cs"), encoding="utf-8").read()   # the ladders live in the kernel
    for needle in ('"Sand", "Gravel", "Soil", "SoilRich"', '"WaterShallow"'):
        if needle not in kernel:
            bad.append("terrain ladder %s changed: site_growth reads WaterShallow" % needle)
    if "isNaturalRock" not in open(os.path.join(HERE, "Source", "RM_OasisPlacementScorer.cs"), encoding="utf-8").read():
        bad.append("the scorer no longer counts natural rock")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "OasisMaker.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


class _patient(object):
    """Raise the bridge client's 30 s reply timeout for a tick wait, then restore it (Contagion/validation.py pattern)."""
    def __init__(self, t, secs=240.0):
        self.rb = getattr(getattr(t, "session", None), "_rb", None)
        self.secs, self.old = secs, None

    def __enter__(self):
        if self.rb is not None and hasattr(self.rb, "timeout"):
            self.old = self.rb.timeout
            self.rb.timeout = self.secs
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.secs)
        return self

    def __exit__(self, *a):
        if self.old is not None:
            self.rb.timeout = self.old
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.old)


def _build_suite():
    suite = Suite("OasisMaker")
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    def _flat(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k)
                for s in _flat(v):
                    yield s
        elif isinstance(o, (list, tuple)):
            for v in o:
                for s in _flat(v):
                    yield s
        elif o is not None:
            yield str(o)

    def _inspect(t, thing_id):
        r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
        rows = (r or {}).get("things") or []
        row = next((x for x in rows if x.get("id") == thing_id), None)
        if row is None or row.get("error"):
            raise ExpectationFailed("inspect_string failed for %s: %r" % (thing_id, row or r))
        return " ".join(str(x) for x in (row.get("inspect") or []))

    def _machine(t, rect):
        r = t.bridge_call("jawa/list_things", defName=DEF, rect=rect, limit=5)
        rows = (r or {}).get("things") or []
        if not isinstance(r, dict) or r.get("success") is False or not rows:
            raise ExpectationFailed("no %s found in %s after spawning it: %r" % (DEF, rect, str(r)[:200]))
        return rows[0]

    def _terrain_ops(t, rect):
        r = t.bridge_call("jawa/get_terrain_batch", rects=rect)
        if not isinstance(r, dict) or r.get("success") is False or r.get("ops") is None:
            raise ExpectationFailed("get_terrain_batch unreadable for %s: %r" % (rect, str(r)[:200]))
        return str(r.get("ops"))

    def _pad(t, roof):
        """A cleared 25x25 pad: plain Sand, no roof; with roof=True a 19x19 roof and rough granite rows 7 north and south."""
        x, z = t.anchor
        t.clear_area(size=25)
        t.bridge_call("jawa/set_roof_batch", ops="%d,%d,25,25" % (x - 12, z - 12), roofDef="None")
        t.bridge_call("jawa/set_terrain_batch", ops="%s:%d,%d,25,25" % (BARE, x - 12, z - 12), layer="top")
        if roof:
            t.bridge_call("jawa/set_terrain_batch", ops="%s:%d,%d,17,1;%s:%d,%d,17,1" % (ROCK, x - 8, z + 7, ROCK, x - 8, z - 7),
                          layer="top")
            t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,19,19" % (x - 9, z - 9))
        t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=10)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    raise ExpectationFailed("%r of %d defs resolved; notFound=%r" % (r.get("foundCount"), len(names), r.get("notFound")))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 5:
                raise ExpectationFailed("settings probe found %d fields (blind regex)" % len(settings_fields()))
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else (str(int(float(old)) + 1) if ty == "int" else str(float(old) + 1.0))
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("def_wiring")
    def def_wiring(t):
        row = {}
        with t.component("def_readable", beyond_toggle=True):
            if _live(t):
                r = t.bridge_call("jawa/get_defs", defs="ThingDef/" + DEF,
                                  fields="minifiedDef,tradeTags,placeWorkers,designationCategory,costList", deep=True, limit=2)
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read ThingDef %s: %r" % (DEF, r))
                row.update(rows[0].get("fields") or {})
        with t.component("minified_trade_tagged_and_placeworker_ours", beyond_toggle=True):
            if _live(t):
                if "MinifiedThing" not in " ".join(_flat(row.get("minifiedDef"))):
                    raise ExpectationFailed("minifiedDef is %r, not MinifiedThing" % (row.get("minifiedDef"),))
                tags = list(_flat(row.get("tradeTags")))
                if "ExoticMisc" not in tags:
                    if tags and all(x in ("List`1", "String") or "[" in x for x in tags):
                        _unmeasured(t, "tradeTags returned as a bare type name: %r" % (tags,))
                        return
                    raise ExpectationFailed("tradeTags %r lacks ExoticMisc: the machine is not sold" % (tags,))
                pw = " ".join(_flat(row.get("placeWorkers")))
                if "RM_PlaceWorker_OasisMaker" not in pw:
                    raise ExpectationFailed("placeWorkers %r does not name RM_PlaceWorker_OasisMaker (a def that loads but "
                                            "places anywhere)" % pw[:160])
        with t.component("not_buildable_trade_or_start_only", beyond_toggle=True):
            if _live(t):
                dc = row.get("designationCategory")
                cl = row.get("costList")
                if dc not in (None, "", "null", "None") or (isinstance(cl, list) and cl):
                    raise ExpectationFailed("the machine became buildable (designationCategory=%r costList=%r): the ruling is "
                                            "trade + scenario start only" % (dc, cl))

    @suite.chain("dormant_on_bare_sand")
    def dormant_on_bare_sand(t):
        with t.component("no_shade_no_rock_stays_dormant", toggle="masterEnabled"):
            if not _live(t):
                return
            _pad(t, roof=False)
            t.spawn(DEF, count=1, at="point")
            x, z = t.anchor
            m = _machine(t, "%d,%d,5,5" % (x - 2, z - 2))
            with _patient(t):
                t.wait_ticks(600)
            text = _inspect(t, m["id"])
            if "Dormant" not in text:
                raise ExpectationFailed("a machine on a roofless sand pad with no rock reads %r, not Dormant (the hard floor "
                                        "is not holding)" % text[:120])

    @suite.chain("site_growth")
    def site_growth(t):
        box = {}
        with t.component("valid_site_attunes", toggle="masterEnabled"):
            if _live(t):
                _pad(t, roof=True)
                x, z = t.anchor
                if ROCK not in _terrain_ops(t, "%d,%d,17,1" % (x - 8, z + 7)):
                    _unmeasured(t, "set_terrain_batch did not lay %s on the pad (a natural base terrain set through "
                                   "layer='top' was refused), so the rock floor cannot be built here" % ROCK)
                else:
                    t.spawn(DEF, count=1, at="point")
                    box["rect"] = "%d,%d,5,5" % (x - 2, z - 2)
                    box["m"] = _machine(t, box["rect"])
                    with _patient(t):
                        t.wait_ticks(600)
                    text = _inspect(t, box["m"]["id"])
                    if "Attuning" not in text:
                        raise ExpectationFailed("a machine under a roof with %s strips reads %r, not Attuning (either the pad "
                                                "did not take or the scorer no longer counts shade/rock; %s is assumed to "
                                                "carry the SmoothableStone affordance)" % (ROCK, text[:120], ROCK))
        old = {}
        if _live(t):
            for k in list(FAST) + ["masterEnabled"]:
                old[k] = _raw(t, "get", k).get("value")
        try:
            with t.component("master_off_stops_growth", toggle="masterEnabled"):
                if _live(t):
                    _raw(t, "set", "masterEnabled", "False")
                    for k, v in FAST.items():
                        _raw(t, "set", k, v)
                    with _patient(t):
                        t.wait_ticks(1500)
                    text = _inspect(t, box["m"]["id"])
                    if "oasis is made" in text or "Working" in text:
                        raise ExpectationFailed("with masterEnabled off the machine still progressed: %r (toggle dead)" % text[:120])
            with t.component("fast_settings_finish_an_oasis", toggle="attuningDays"):
                if _live(t):
                    _raw(t, "set", "masterEnabled", "True")
                    with _patient(t):
                        t.wait_ticks(4000)
                    text = _inspect(t, box["m"]["id"])
                    if "The oasis is made." not in text:
                        raise ExpectationFailed("fast settings (attuningDays 0, baseRingDays 0.001) did not finish the oasis in "
                                                "4000 ticks: %r" % text[:120])
            with t.component("centre_holds_water_and_rock_is_never_converted", toggle="baseRingDays"):
                if _live(t):
                    x, z = t.anchor
                    centre = _terrain_ops(t, "%d,%d,7,7" % (x - 3, z - 3))
                    if "WaterShallow" not in centre:
                        raise ExpectationFailed("no WaterShallow within 3 cells of the machine after the oasis is made: %s" % centre[:200])
                    north = _terrain_ops(t, "%d,%d,17,1" % (x - 8, z + 7))
                    south = _terrain_ops(t, "%d,%d,17,1" % (x - 8, z - 7))
                    for name, ops in (("north", north), ("south", south)):
                        if ROCK not in ops or any(k in ops for k in ("Gravel", "Soil", "WaterShallow", "Marsh", "Mud")):
                            raise ExpectationFailed("the %s rock strip was converted or lost (%s): the oasis must never take stone: %s"
                                                    % (name, ROCK, ops[:200]))
                    box["centre"] = centre
            with t.component("losing_shade_freezes_and_nothing_reverses", toggle="masterEnabled"):
                if _live(t):
                    x, z = t.anchor
                    t.bridge_call("jawa/set_roof_batch", ops="%d,%d,19,19" % (x - 9, z - 9), roofDef="None")
                    with _patient(t):
                        t.wait_ticks(600)
                    text = _inspect(t, box["m"]["id"])
                    if "Dormant" not in text:
                        raise ExpectationFailed("with the roof gone the machine reads %r, not Dormant" % text[:120])
                    after = _terrain_ops(t, "%d,%d,7,7" % (x - 3, z - 3))
                    if "WaterShallow" not in after:
                        raise ExpectationFailed("the pool reverted when the machine froze (it never takes anything back): %s" % after[:200])
        finally:
            if _live(t) or t.session is not None:
                for k, v in old.items():
                    if v is not None:
                        try:
                            _raw(t, "set", k, v)
                        except Exception as ex:
                            print("[oasismaker] RESTORE FAILED %s: %s" % (k, ex), file=sys.stderr, flush=True)

    @suite.chain("placement_gate")
    def placement_gate(t):
        with t.component("ghost_is_red_below_the_floor_with_a_reason", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "AllowsPlacing and DrawGhost run only from a held placement ghost in the UI; the machine is "
                               "not buildable, so no blueprint route exists either (the tool cannot place a ghost)")

    @suite.chain("slow_timing")
    def slow_timing(t):
        with t.component("shipped_attuning_and_ring_times", toggle="attuningDays"):
            if _live(t):
                _unmeasured(t, "the shipped 2-day attuning and 3-day innermost ring at default settings are game days; "
                               "site_growth proves the same state machine at fast settings")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
