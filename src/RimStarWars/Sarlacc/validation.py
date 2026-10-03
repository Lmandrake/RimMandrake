"""validation.py -- modcheck suite for RimStarWars: Sarlacc (mandrake.rsw.sarlacc).

First north-star script (SARLACC_FIRST_SCRIPT_1). Walk: design/validation_walks/RimStarWars/Sarlacc.md.
The sarlacc's native-habitat build: Stage I swimmer (Anomaly Devourer reuse), Stage II anchored mouth, Stage III
cistern and its drained throat, seven changed-return hediffs, and two once-per-map incidents that bring a swimmer
to root (the Long Shade swimmer's road, the Stillsand seep-root). Anomaly is a hard prerequisite.

CHAINS
  defs_resolve       every def under Defs/ (parsed from the XML) resolves live; a control name reads notFound.
  settings_roundtrip every `public static` field of RSW_SarlaccSettings: default / write / restore (numbers numerically).
  swimmer_reserve    a swimmer spawned (faction none) reads a "Water reserve" line on its inspect pane.
  rooting            reserveDrainMultiplier set huge runs the reserve out on the first tick: with rootingInPlayEnabled OFF the
                     swimmer stays (control), ON it roots into RSW_SarlaccAnchored where it stood and the swimmer is gone;
                     the rooting message names the reason when rootingMessagesEnabled is on.
  cistern            a cistern spawns and reads; the breach itself, the flood and the throat: UNMEASURED.
  incidents          the two swimmer incidents: UNMEASURED (biome-gated; fire_incident dry-run gives no usable gate read).
  changed_return     the seven hediffs resolve (defs_resolve); the swallow-and-survive grant: UNMEASURED.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.StarWars.Sarlacc.RSW_SarlaccSettings"
CONTROL_ABSENT = "ThingDef/RSW_SarlaccNoSuchDef_ZZ"
SWIMMER = "RSW_SarlaccSwimmer"
ANCHORED = "RSW_SarlaccAnchored"
CISTERN = "RSW_SarlaccCistern"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
HEDIFFS = ["RSW_TheWrung", "RSW_SaltEyed", "RSW_TheStillness", "RSW_TheTithe", "RSW_TheBloom", "RSW_Pressed",
           "RSW_TakenAndReturned"]


def shipped_defs():
    """[(DefType, defName)] for every non-abstract top-level def under Defs/, from the XML (never a hand list)."""
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
# A def whose tag is a namespaced class (the Stillsand cave row) is not a type get_defs is proven to resolve.
PLAIN = [p for p in SHIPPED if "." not in p[0]]
CUSTOM = [p for p in SHIPPED if "." in p[0]]


def settings_fields():
    """{name: type} for every scalar `public static` field of RSW_SarlaccSettings, read from the C#."""
    src = open(os.path.join(HERE, "Source", "RSW_SarlaccSettings.cs"), encoding="utf-8").read()
    body = src.split("class RSW_SarlaccSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if len(SHIPPED) < 15:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if len(fields) < 5:
        return ["settings probe found %d scalar fields (sanity probe failed)" % len(fields)]
    src = open(os.path.join(HERE, "Source", "RSW_SarlaccSettings.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "Sarlacc.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing, no error)" % fn)
    names = set(n for _t, n in SHIPPED)
    for h in HEDIFFS:
        if h not in names:
            bad.append("changed-return hediff %s not shipped" % h)
    cs = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "CompSarlaccSwimmer.cs"), encoding="utf-8").read())
    for h in HEDIFFS:
        if '"%s"' % h not in cs:
            bad.append("CompSarlaccSwimmer.cs does not grant %s" % h)
    # every C# class the XML names exists in the source
    allsrc = "".join(open(os.path.join(HERE, "Source", f), encoding="utf-8").read()
                     for f in os.listdir(os.path.join(HERE, "Source")) if f.endswith(".cs"))
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in files:
            txt = open(os.path.join(dp, fn), encoding="utf-8").read()
            for cls in re.findall(r'(?:Class|workerClass|thingClass)="?(?:>)?(RimMandrake\.StarWars\.Sarlacc\.\w+)', txt) + \
                    re.findall(r"<workerClass>RimMandrake\.StarWars\.Sarlacc\.(\w+)</workerClass>", txt):
                short = cls.split(".")[-1]
                if "class %s" % short not in allsrc:
                    bad.append("%s names class %s, which is not in Source/" % (fn, short))
    # the two incidents: biome gate is data, one per map, Anomaly-gated
    for fn, biome, marker in (("IncidentDefs_SwimmerRoad.xml", "RM_LongShade", None),
                              ("IncidentDefs_SwimmerSeep.xml", "RM_Stillsand", "RSW_DeepDesertSeep")):
        txt = open(os.path.join(HERE, "Defs", fn), encoding="utf-8").read()
        if "<li>%s</li>" % biome not in txt:
            bad.append("%s does not gate on biome %s" % (fn, biome))
        if marker and "<seepMarker>%s</seepMarker>" % marker not in txt:
            bad.append("%s does not name seep marker %s" % (fn, marker))
        if 'MayRequire="Ludeon.RimWorld.Anomaly"' not in txt:
            bad.append("%s lost its Anomaly guard" % fn)
    if "RSW_DeepDesertSeep" not in names:
        bad.append("seep marker def missing")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimStarWars", "Sarlacc.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "..", "RimMandrake", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _flat(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            for s in _flat(v):
                yield s
    elif isinstance(x, (list, tuple)):
        for v in x:
            for s in _flat(v):
                yield s


def _build_suite():
    suite = Suite("Sarlacc")
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

    def _set(t, **kv):
        """Write settings through the class; returns {field: old} for the restore."""
        old = {}
        for f, v in kv.items():
            old[f] = _raw(t, "get", f).get("value")
            if not _raw(t, "set", f, v).get("success"):
                raise ExpectationFailed("could not set %s" % f)
        return old

    def _restore(t, old):
        for f, v in old.items():
            if v is not None:
                try:
                    _raw(t, "set", f, v)
                except Exception as ex:
                    print("[sarlacc] RESTORE FAILED %s: %s" % (f, ex), file=sys.stderr, flush=True)

    def _things(t, defName, rect):
        r = t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=20)
        if not _live(t):
            return []
        if not isinstance(r, dict) or r.get("success") is False or "countMatched" not in r:
            raise ExpectationFailed("list_things(%s) unreadable: %r" % (defName, r))
        return list(r.get("things") or [])

    def _spawn_swimmer(t):
        """(pawn id, x, z, rect) or None. Faction none so it neither raids nor is raided."""
        t.clear_area(size=24)
        x, z = t.anchor if getattr(t, "anchor", None) else (0, 0)
        r = t.bridge_call("jawa/spawn_pawn", kindDef=SWIMMER, x=x, z=z, faction="none", count=1)
        if not _live(t):
            return None
        row = ((r or {}).get("pawns") or [{}])[0] if isinstance(r, dict) else {}
        if not row.get("id"):
            raise ExpectationFailed("swimmer did not spawn (Anomaly loaded?): %s" % str(r)[:200])
        t.session.track("pawn", row["id"], x=x, z=z)
        return row["id"], x, z, "%d,%d,24,24" % (x - 12, z - 12)

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
            names = ["%s/%s" % p for p in PLAIN]
            missing, ok = [], 0
            for i in range(0, len(names), 20):
                chunk = names[i:i + 20]
                r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=40)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                missing.extend(r.get("notFound") or [])
                ok += int(r.get("foundCount", 0))
            if _live(t) and (missing or ok != len(names)):
                raise ExpectationFailed("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))
        with t.component("stillsand_cave_row_resolves", beyond_toggle=True):
            for ty, n in CUSTOM:
                r = t.bridge_call("jawa/get_defs", defs="%s/%s" % (ty, n), fields="defName", limit=2)
                if _live(t):
                    if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                        _unmeasured(t, "%s/%s did not resolve: the row needs mandrake.rm.biomes loaded and a namespaced "
                                       "def type name is not proven for get_defs (%s)" % (ty, n, str(r)[:120]))
                        return

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 5:
                raise ExpectationFailed("settings probe found too few fields (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
                else:
                    new = str(float(old) + 1.0)
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

    @suite.chain("swimmer_reserve")
    def swimmer_reserve(t):
        with t.component("swimmer_reads_a_water_reserve", beyond_toggle=True):
            if not _live(t):
                return
            sw = _spawn_swimmer(t)
            r = t.bridge_call("jawa/inspect_string", thingIds=sw[0])
            rows = (r or {}).get("things") or []
            row = next((x for x in rows if x.get("id") == sw[0]), None)
            if row is None or row.get("error"):
                _unmeasured(t, "inspect_string could not read the spawned swimmer: %s" % str(r)[:200])
                return
            line = " ".join(str(x) for x in (row.get("inspect") or []))
            if "Water reserve" not in line:
                raise ExpectationFailed("a spawned swimmer reports no 'Water reserve' line (comp not attached?): %r" % line[:200])
        with t.component("probe_can_miss_the_line_control", beyond_toggle=True):
            if not _live(t):
                return
            # the same reader on a thing with no reserve comp must NOT show the line
            sw = _spawn_swimmer(t)
            seep = t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % ("RSW_DeepDesertSeep", sw[1] + 4, sw[2]))
            rows = _things(t, "RSW_DeepDesertSeep", sw[3])
            if not rows:
                _unmeasured(t, "control seep marker did not spawn: %s" % str(seep)[:160])
                return
            r = t.bridge_call("jawa/inspect_string", thingIds=rows[0]["id"])
            if "Water reserve" in " ".join(_flat(r)):
                raise ExpectationFailed("a seep marker reports a Water reserve line: the line check cannot say absent")

    @suite.chain("rooting")
    def rooting(t):
        with t.component("rooting_off_swimmer_stays", toggle="rootingInPlayEnabled"):
            if not _live(t):
                return
            sw = _spawn_swimmer(t)
            old = _set(t, rootingInPlayEnabled="False", reserveDrainMultiplier="1000000000")
            try:
                t.wait_ticks(40)
                if _things(t, ANCHORED, sw[3]):
                    raise ExpectationFailed("rootingInPlayEnabled off, yet a swimmer rooted (toggle dead)")
                r = t.bridge_call("jawa/inspect_string", thingIds=sw[0])
                row = next((x for x in ((r or {}).get("things") or []) if x.get("id") == sw[0]), None)
                if row is None or row.get("error"):
                    raise ExpectationFailed("the swimmer vanished with rooting off and no anchored mouth: %s" % str(r)[:200])
            finally:
                _restore(t, old)
        with t.component("exhausted_reserve_roots_where_it_stood", toggle="rootingInPlayEnabled"):
            if not _live(t):
                return
            sw = _spawn_swimmer(t)
            before = len(_things(t, ANCHORED, sw[3]))
            msgs0 = t.bridge_call("rimworld/list_messages", limit=200)
            old = _set(t, rootingInPlayEnabled="True", rootingMessagesEnabled="True", reserveDrainMultiplier="1000000000")
            try:
                t.wait_ticks(40)
                after = _things(t, ANCHORED, sw[3])
                if len(after) <= before:
                    raise ExpectationFailed("reserve exhausted (drain x1e9) but no %s appeared within 40 ticks" % ANCHORED)
                r = t.bridge_call("jawa/inspect_string", thingIds=sw[0])
                row = next((x for x in ((r or {}).get("things") or []) if x.get("id") == sw[0]), None)
                if row is not None and not row.get("error"):
                    raise ExpectationFailed("the swimmer pawn is still there after it rooted: %s" % str(row)[:200])
                msgs = t.bridge_call("rimworld/list_messages", limit=200)
                blob = list(_flat(msgs))
                if not blob:
                    _unmeasured(t, "rooted, but list_messages returned nothing at all (shape?): %s" % str(msgs)[:160])
                    return
                seen = lambda m: sum(1 for s in _flat(m) if "ran out of its birth-water reserve" in s)
                if seen(msgs) <= seen(msgs0):
                    raise ExpectationFailed("rooted with rootingMessagesEnabled on but no 'ran out of its birth-water reserve' message")
            finally:
                _restore(t, old)

    @suite.chain("cistern")
    def cistern(t):
        with t.component("cistern_spawns_and_reads", beyond_toggle=True):
            if not _live(t):
                return
            t.clear_area(size=24)
            cells = t.spawn(CISTERN, count=1, at="point") or [(0, 0)]
            rect = "%d,%d,24,24" % (cells[0][0] - 12, cells[0][1] - 12)
            if not _things(t, CISTERN, rect):
                raise ExpectationFailed("%s did not spawn (def dropped silently?)" % CISTERN)
        with t.component("breach_floods_and_becomes_throat", toggle="breachFloodVisualEnabled"):
            if _live(t):
                _unmeasured(t, "the breach is a CompInteractable done by a pawn at the reservoir wall; no bridge tool presses an "
                               "interactable comp, so WaterShallow flood cells, the three messages and the RSW_SarlaccThroat "
                               "swap cannot be driven")

    @suite.chain("incidents")
    def incidents(t):
        for name, why in (
            ("swimmer_road_longshade_only", "RSW_SwimmerRoad fires only on an RM_LongShade map (earliestDay 20, once per map, "
             "reads the CreatureBehaviors shade graph); needs a generated Long Shade map and game days"),
            ("swimmer_seep_stillsand_only", "RSW_SwimmerSeepRoot fires only on an RM_Stillsand map holding an RSW_DeepDesertSeep "
             "with brine cells (earliestDay 15, once per map); needs a generated Stillsand map; "
             "fire_incident dry-run reports success=False with canFireNow=False and gives no gate read"),
        ):
            with t.component(name, toggle="swimmerRoadEnabled" if "road" in name else "swimmerSeepEnabled"):
                if _live(t):
                    _unmeasured(t, why)
        with t.component("rooting_evacuates_the_patch", toggle="rootingEvacuatesPatch"):
            if _live(t):
                _unmeasured(t, "pawns standing on the patch being cleared when the road swimmer roots needs the road incident "
                               "on a Long Shade map")
        with t.component("take_signs_leave_sand_and_message", toggle="takeSignsEnabled"):
            if _live(t):
                _unmeasured(t, "the disturbed-sand decal and 'sand heaves' message need a completed swallow (a pawn eaten by "
                               "the Devourer comp), which no tool stages")

    @suite.chain("changed_return")
    def changed_return(t):
        with t.component("changed_return_granted_to_a_survivor", toggle="changedReturnHediffsEnabled"):
            if _live(t):
                _unmeasured(t, "one of the seven hediffs (a second at secondHediffChance) is granted when a swallowed pawn "
                               "survives and is spat free; needs a swallow to complete with the prey alive (CompDevourer "
                               "digestion is 10-60 s of game time and the grant is random per hediff). Defs resolve in defs_resolve")
        with t.component("anchored_mouth_tithe_strike", toggle="anchoredTitheEnabled"):
            if _live(t):
                _unmeasured(t, "a strike at mtbStrikeDays 20 is statistical (debug_process.md section 4); the roll cannot be forced")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
