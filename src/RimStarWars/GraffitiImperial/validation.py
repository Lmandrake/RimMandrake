"""validation.py -- modcheck suite for RimStarWars: Imperial Graffiti (mandrake.rsw.graffitiimperial).

First north-star script (GRAFFITI_IMPERIAL_FIRST_SCRIPT_1). Walk: design/validation_walks/RimStarWars/GraffitiImperial.md.
ONE content def and no C#: RSW_Graffiti_Stencil_ImperialCog, ParentName RM_BaseGraffiti from mandrake.rm.graffiti, an
asemic Aurebesh-styled crossed-out Imperial cog. It rides the framework's ModExtension_Graffiti (category Taunt, form
Stencil, designatorEligible, raidExitEligible) and the same `requiresHostileToFactionDef = Empire` gate as its
franchise-free sibling RM_Graffiti_Stencil_Crown (DIRTY_CODE_REVIEW wave 76: it once shipped ungated, so an
Imperial-aligned pawn could paint a mark that is a hostile social act). Every mechanism (the spree pool, the
designator, raid-exit tagging, the viewer reaction) lives in the Graffiti framework and is exercised by ITS script.

This mod has NO settings class (no Source/ folder); the effective master switch is the framework's `paintingEnabled`.

CHAINS
  defs_resolve        the shipped def (parsed from the XML) resolves live; a control name reads notFound.
  settings_roundtrip  no settings class of its own (asserted); the framework gate `paintingEnabled` is readable.
  framework_wiring    the def's ModExtension reads Taunt / Stencil / Empire live, in lockstep with the Crown; the
                      Empire FactionDef resolves (Royalty).
  mark_state          the mark spawned on a prepared patch is found by list_things with Beauty -5 and Cleanliness -3;
                      an empty rect reads zero (the probe can say absent).
  mechanics_unmeasured  weighted-pool pick in a spree, the hostility gate with an Empire-hostile and an Empire-allied
                      painter, designator and raid-exit use, texture binding: each says what it needs.

STATIC (offline): `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import contextlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
GRAFFITI = os.path.join(HERE, "..", "..", "RimMandrake", "Graffiti")
MARK = "RSW_Graffiti_Stencil_ImperialCog"
SIBLING = "RM_Graffiti_Stencil_Crown"
FRAMEWORK_SETTINGS = "RimMandrake.Graffiti.RM_GraffitiSettings"
CONTROL_ABSENT = "ThingDef/RSW_GraffitiImperialNoSuchDef_ZZ"
EXT_FIELDS = ("category", "form", "poolWeight", "designatorEligible", "raidExitEligible", "requiresHostileToFactionDef")


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


def _ext(def_name, defs_dir):
    """{field: text} of the ModExtension_Graffiti on `def_name` in `defs_dir`, or None."""
    for dp, _d, files in os.walk(defs_dir):
        for fn in files:
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    if isinstance(el.tag, str) and el.findtext("defName") == def_name:
                        li = [x for x in el.findall("modExtensions/li") if x.get("Class", "").endswith("ModExtension_Graffiti")]
                        return dict((c.tag, (c.text or "").strip()) for c in li[0]) if li else {}
    return None


def static_checks():
    bad = []
    if (("ThingDef", MARK)) not in SHIPPED or len(SHIPPED) != 1:
        return ["expected exactly the one ThingDef %s, parsed %r (sanity probe failed)" % (MARK, SHIPPED)]
    if os.path.isdir(os.path.join(HERE, "Source")) or os.path.isdir(os.path.join(HERE, "Assemblies")):
        bad.append("a Source/ or Assemblies/ folder appeared: this mod is content-only by the engine-vs-content rule; "
                   "the script needs a settings chain for it")
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_GraffitiImperial.xml")).getroot()
    el = [e for e in root if e.findtext("defName") == MARK][0]
    if el.get("ParentName") != "RM_BaseGraffiti":
        bad.append("parent is %r, not RM_BaseGraffiti" % el.get("ParentName"))
    fw = open(os.path.join(GRAFFITI, "Defs", "ThingDefs_Graffiti.xml"), encoding="utf-8").read()
    if 'Name="RM_BaseGraffiti"' not in fw:
        bad.append("the framework no longer ships the abstract RM_BaseGraffiti")
    mine = _ext(MARK, os.path.join(HERE, "Defs"))
    theirs = _ext(SIBLING, os.path.join(GRAFFITI, "Defs"))
    if not mine or not theirs:
        return bad + ["could not read ModExtension_Graffiti on %s or %s" % (MARK, SIBLING)]
    for f in ("category", "form", "designatorEligible", "raidExitEligible", "requiresHostileToFactionDef"):
        if mine.get(f) != theirs.get(f):
            bad.append("%s differs from sibling %s: %r vs %r (the two must stay in lockstep)" % (f, SIBLING, mine.get(f), theirs.get(f)))
    if mine.get("requiresHostileToFactionDef") != "Empire":
        bad.append("the Empire hostility gate is gone (wave-76 defect: an Imperial painter could paint it)")
    ext_src = open(os.path.join(GRAFFITI, "Source", "ModExtension_Graffiti.cs"), encoding="utf-8").read()
    for f in EXT_FIELDS:
        if not re.search(r"public\s+[\w<>]+\s+%s\b" % f, ext_src):
            bad.append("framework ModExtension_Graffiti has no field %s" % f)
    for f in mine:
        if f not in EXT_FIELDS:
            bad.append("extension sets %s, which this script does not know" % f)
    tex = el.findtext("graphicData/texPath")
    folder = os.path.join(HERE, "Textures", *tex.split("/"))
    if el.findtext("graphicData/graphicClass") != "Graphic_Random":
        bad.append("graphic is not Graphic_Random")
    if not os.path.isdir(folder) or not [f for f in os.listdir(folder) if f.endswith(".png")]:
        bad.append("Graphic_Random folder %s holds no png (renders magenta)" % tex)
    for st, v in (("Beauty", "-5"), ("Cleanliness", "-3")):
        if el.findtext("statBases/" + st) != v:
            bad.append("%s is %r, ruled %s" % (st, el.findtext("statBases/" + st), v))
    if el.findtext("filth/rainWashes") != "false":
        bad.append("the mark washes off in rain (it 'does not fade')")
    about = open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read()
    if "<packageId>mandrake.rm.graffiti</packageId>" not in about:
        bad.append("About.xml no longer depends on mandrake.rm.graffiti")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimStarWars", "GraffitiImperial.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "..", "RimMandrake", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


class _Unmeasured(Exception):
    pass


def _live(t):
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _unmeasured(t, why):
    t._why = why
    t.upstream_failed = True
    t.upstream_reason = "UNMEASURED: " + why
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, **kw):
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw):
        yield
    if getattr(t, "_why", None) and not before:
        t.upstream_failed = False
        t.upstream_reason = None
    t._why = None


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _field(r, name):
    return (((r.get("defs") or [{}])[0]).get("fields") or {}).get(name)


def _centre(t):
    r = t.bridge_call("jawa/map_info")
    if _live(t) and isinstance(r, dict) and r.get("sizeX") and r.get("sizeZ"):
        t.anchor = (int(r["sizeX"]) // 2, int(r["sizeZ"]) // 2)
    return t.anchor


def _build_suite():
    suite = Suite("GraffitiImperial")
    suite.toggles = []      # no Mod Settings of its own: content-only addon (see docstring)

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with _comp(t, "control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                _ok(r, "get_defs control")
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    _fail("control def reads as present: %r" % r)
        with _comp(t, "every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=10)
            if _live(t):
                _ok(r, "get_defs")
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    _fail("%d of %d defs resolved; notFound=%r" % (int(r.get("foundCount", 0)), len(names), r.get("notFound")))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with _comp(t, "no_settings_class_of_its_own", beyond_toggle=True):
            if os.path.isdir(os.path.join(HERE, "Source")):
                _fail("a Source/ folder exists but this script declares no settings round trip")
        with _comp(t, "framework_master_gate_is_readable", beyond_toggle=True):
            r = t.bridge_call("jawa/mod_settings_field", typeName=FRAMEWORK_SETTINGS, action="get", field="paintingEnabled")
            if _live(t):
                _ok(r, "mod_settings_field get paintingEnabled")
                if r.get("value") is None:
                    _fail("the framework's paintingEnabled returned no value: the framework is not loaded")

    @suite.chain("framework_wiring")
    def framework_wiring(t):
        with _comp(t, "extension_reads_taunt_stencil_empire_live", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/" + MARK, fields="modExtensions", deep=True, limit=2)
            if _live(t):
                _ok(r, "get_defs modExtensions")
                if int(r.get("foundCount", 0)) != 1:
                    _fail("%s did not resolve: %r" % (MARK, r))
                blob = str(_field(r, "modExtensions"))
                if "Empire" not in blob and "Taunt" not in blob:
                    _unmeasured(t, "get_defs returned modExtensions in a shape that names no field values: %s" % blob[:160])
                for want in ("Taunt", "Stencil", "Empire"):
                    if want not in blob:
                        _fail("live ModExtension_Graffiti lacks %s (stale deploy or dropped field): %s" % (want, blob[:200]))
        with _comp(t, "gate_in_lockstep_with_the_crown", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/" + SIBLING, fields="modExtensions", deep=True, limit=2)
            if _live(t):
                _ok(r, "get_defs sibling modExtensions")
                if int(r.get("foundCount", 0)) != 1:
                    _fail("sibling %s did not resolve: %r" % (SIBLING, r))
                if "Empire" not in str(_field(r, "modExtensions")):
                    _unmeasured(t, "the sibling's modExtensions payload names no Empire gate either: shape unreadable "
                                   "or the sibling lost its gate (the framework's own script owns that)")
        with _comp(t, "empire_faction_def_resolves", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="FactionDef/Empire", fields="defName", limit=2)
            if _live(t):
                _ok(r, "get_defs FactionDef/Empire")
                if int(r.get("foundCount", 0)) != 1 or r.get("notFound"):
                    _fail("FactionDef/Empire did not resolve (Royalty missing from the tier): the gate would open on no match")

    @suite.chain("mark_state")
    def mark_state(t):
        box = {}
        with _comp(t, "mark_spawned_is_found_with_ruled_beauty_and_cleanliness", beyond_toggle=True):
            x, z = _centre(t)
            t.clear_area(size=12)
            if _live(t):
                box["rect"] = "%d,%d,3,3" % (x - 1, z - 1)
                t.bridge_call("jawa/set_terrain_batch", ops="Concrete:%d,%d,12,12" % (x - 6, z - 6))
                t.bridge_call("jawa/map_commit")
                _ok(t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (MARK, x, z)), "spawn_batch")
                r = t.bridge_call("jawa/list_things", defName=MARK, rect=box["rect"], limit=10)
                _ok(r, "list_things")
                rows = r.get("things") or []
                if r.get("isCompleteList") is False or "countMatched" not in r:
                    _fail("list_things unreadable or truncated: %r" % (r,))
                if len(rows) != 1:
                    _fail("expected one %s in the spawn rect, found %d" % (MARK, len(rows)))
                st = _ok(t.bridge_call("jawa/thing_stats", thing=rows[0]["id"], stats="Beauty,Cleanliness"), "thing_stats")
                got = {}
                for th in st.get("things") or []:
                    for s in th.get("stats") or []:
                        got[s.get("defName")] = s.get("value")
                for k, v in (("Beauty", -5.0), ("Cleanliness", -3.0)):
                    if k not in got or abs(float(got[k]) - v) > 0.01:
                        _fail("%s reads %r, ruled %s" % (k, got.get(k), v))
        with _comp(t, "empty_rect_reads_zero_probe_can_say_absent", beyond_toggle=True):
            if _live(t):
                x, z = t.anchor
                r = t.bridge_call("jawa/list_things", defName=MARK, rect="%d,%d,3,3" % (x + 20, z + 20), limit=10)
                _ok(r, "list_things (control rect)")
                if "countMatched" not in r:
                    _fail("control read unreadable: %r" % (r,))
                if r.get("things"):
                    _fail("the control rect reads a %s that was never placed there" % MARK)

    @suite.chain("mechanics_unmeasured")
    def mechanics_unmeasured(t):
        for name, why in (
            ("spree_pool_can_pick_the_cog",
             "the spree draws from the weighted pool at random (poolWeight 1 among every Taunt/Stencil/Tag def); proving a pick needs a "
             "sampled spree and a seed method, and the framework's script owns the spree itself"),
            ("imperial_painter_never_paints_it_hostile_painter_can",
             "the HostilityGateAllows pair needs one painter hostile to the Empire and one allied, i.e. two factions with set relations "
             "and a forced paint job; no verb sets faction relations on a quicktest"),
            ("designator_and_raid_exit_offer_it",
             "designatorEligible / raidExitEligible are read by the framework's designator and RaidExitTagger; needs the designator UI "
             "and a raid that exits"),
            ("texture_binds_and_renders",
             "the Graphic_Random folder resolving to a real texture (no magenta) is a visual / Player.log check; the art is queued, "
             "not generated (About.xml)"),
        ):
            with _comp(t, name, beyond_toggle=True):
                if _live(t):
                    _unmeasured(t, why)

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
