"""validation.py -- modcheck suite for RimMandrake: Terminal Biomes (mandrake.rm.terminalbiomes).

First script (debug_process.md section 2), item TERMINAL_BIOMES_FIRST_SCRIPT_1; grew from the Chill/Scald
def-level checks of 2026-10-03 (CHILL_NATIVE_COLD_TOLERANCE_1 and friends). Walk:
design/validation_walks/RimMandrake/TerminalBiomes.md (`## must be true`, each line ends in
`-> chain.component` or `-> UNCOVERED: why`). Fold-aware: folded into the composed mod `mandrake.rm.biomes`
('RimMandrake: Baroque Biomes'); the walk names this mod's lines so the composed script covers them.
NEVER RUN LIVE YET: every live shape below that is unproven degrades to UNMEASURED, never PASS.

WHY THE FIRST LIVE RUN REPORTED ZERO CHAINS ({}): the chains wrapped their checks in no `t.component(...)`, and a
chain records a result only through components. Every check below now runs inside a component.

Run offline: `python3 src/RimMandrake/TerminalBiomes/validation.py` -> `STATIC: PASS (0 findings)`.
Live: modcheck/northstar_driver on a tier carrying the composed biomes mod (or Terminal Biomes + Luminous Pigment +
Diving Interaction + Environmental Hazards, its dependencies), all five DLCs, plain open map.

WHAT IT PROVES, by state read: every shipped def resolves (control reads absent); every Mod Settings field
round-trips (38, generated from the settings class; the two enum fields degrade to UNMEASURED if the setter
cannot take an enum name); every biome terrain paints and reads back (a vanilla control proves the read);
the cryoponics vat's own class is wired (inspect line, with a vanilla grower as the absent control); a killed
wax-procession colony spoils into hydrocarbon flesh; each rostered biome has a live animal density above zero.
Offline-fact chains (cold-tolerant natives, roster, catch, saal name, wax def) run as components too.
NOT PROVEN HERE (UNMEASURED, named): every Scald/Twilight/Chill mechanic that needs its own map, weather or
a powered grid (the list is the chains at the bottom), and the toggle-off arm of any of them.
"""
import contextlib
import json
import re
import time
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR_C = -110.0
NATIVE_MIN_C = -150.0
FILES = ["RM_TheChillFauna.xml", "RM_TheChillFloorLife.xml"]
NATIVES = ["RM_Heemin", "RM_Oovanam", "RM_Hoolen", "RM_Vaunoom", "RM_Fessu", "RM_Krellik", "RM_Oddu",
           "RM_Oovu", "RM_Iliss", "RM_Tarnn", "RM_Zhiil"]


def static_checks():
    bad, seen = [], set()
    for f in FILES:
        root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", f)).getroot()
        for td in root.findall("ThingDef"):
            n = td.findtext("defName")
            if n not in NATIVES:
                continue
            seen.add(n)
            mn = td.findtext("statBases/ComfyTemperatureMin")
            mx = td.findtext("statBases/ComfyTemperatureMax")
            if mn is None or float(mn) > NATIVE_MIN_C:
                bad.append("%s ComfyTemperatureMin=%s, needs <= %g" % (n, mn, NATIVE_MIN_C))
            if mx is None or (mn is not None and float(mx) <= float(mn)):
                bad.append("%s ComfyTemperatureMax %s not above min" % (n, mx))
    for n in NATIVES:
        if n not in seen:
            bad.append("native ThingDef %s not found" % n)
    return bad


OFF_FLOOR = ["RM_Hoolen", "RM_Vaunoom", "AA_AuroraSylph", "AA_Skyeel"]
BIOME = os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheChill.xml")


def roster_checks():
    """wildAnimals parsed as XML (node name = animal, text = commonality; no <li>)."""
    bad = []
    root = ET.parse(BIOME).getroot()
    bd = [b for b in root.findall("BiomeDef") if b.findtext("defName") == "RM_TheChill"]
    if len(bd) != 1:
        return ["RM_TheChill BiomeDef not found exactly once"]
    wa = bd[0].find("wildAnimals")
    rows = {c.tag: c.text for c in wa} if wa is not None else {}
    if len(rows) < 6:
        bad.append("roster sanity probe: only %d rows (expected the 6 floor natives)" % len(rows))
    for n in ("RM_Heemin", "RM_Oovanam", "RM_Fessu", "RM_Krellik", "RM_Oddu", "RM_Oovu", "RM_Iliss", "RM_Tarnn", "RM_Zhiil"):
        if n not in rows:
            bad.append("floor native %s missing from wildAnimals" % n)
    for n in OFF_FLOOR:
        if n in rows:
            bad.append("%s must be off the floor roster (Q1a)" % n)
    if any(c.tag == "li" for c in (wa if wa is not None else [])):
        bad.append("<li> row in wildAnimals (discards the entry)")
    return bad


CATCH_FILE = os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_TheChillCatch.xml")
RARE_FILE = os.path.join(HERE, "Defs", "ThingSetMakerDefs", "RM_ChillRareCatch.xml")


def catch_checks():
    """CHILL_FREE_TIER_CATCH_1: fishTypes parsed as XML; every row a free-tier item, every catch alive on the floor."""
    bad = []
    bd = [b for b in ET.parse(BIOME).getroot().findall("BiomeDef") if b.findtext("defName") == "RM_TheChill"]
    if len(bd) != 1:
        return ["RM_TheChill BiomeDef not found exactly once"]
    ft = bd[0].find("fishTypes")
    rows = []
    for grp in (ft if ft is not None else []):
        if grp.tag == "rareCatchesSetMaker":
            if (grp.text or "").strip() != "RM_RareChillCatches":
                bad.append("rareCatchesSetMaker is %r, want RM_RareChillCatches" % grp.text)
            continue
        for c in grp:
            rows.append(c.tag)
            if c.get("MayRequire"):
                bad.append("%s row carries MayRequire %s" % (c.tag, c.get("MayRequire")))
    if len(rows) != 9:
        bad.append("sanity probe: %d fishTypes rows, expected 9" % len(rows))
    items = set()
    for f in (CATCH_FILE,):
        for td in ET.parse(f).getroot().findall("ThingDef"):
            items.add(td.findtext("defName"))
    wa = {c.tag for c in bd[0].find("wildAnimals")}
    for r in rows:
        if r.startswith("RUT_"):
            bad.append("%s is campaign-tier in the free fishTypes" % r)
        if r not in items:
            bad.append("%s not defined in RM_TheChillCatch.xml" % r)
        name = r[3:-5] if r.startswith("RM_") and r.endswith("Catch") else r
        if ("RM_" + name) not in wa:
            bad.append("catch %s has no floor resident RM_%s in wildAnimals" % (r, name))
    rare = ET.parse(RARE_FILE).getroot().findall("ThingSetMakerDef")
    if [r.findtext("defName") for r in rare] != ["RM_RareChillCatches"]:
        bad.append("free-tier rare table defName wrong")
    for li in rare[0].iter("li"):
        if (li.text or "").strip().startswith("RUT_") or li.get("MayRequire"):
            bad.append("rare table option %r is campaign-tier/guarded" % li.text)
    for fn in os.listdir(os.path.join(HERE, "Defs", "ThingSetMakerDefs")):
        if "RUT_RarePropaneCatches</defName>" in open(os.path.join(HERE, "Defs", "ThingSetMakerDefs", fn), encoding="utf-8").read():
            bad.append("%s still defines RUT_RarePropaneCatches (collides with campaign twin)" % fn)
    return bad


def ekkel_lore_checks():
    """SCALD_SIMMERLACE_EKKEL_LORE_1: creature and catch descriptions carry the simmerlace origin lore."""
    bad = []
    seen = set()
    for dp, _, fns in os.walk(os.path.join(HERE, "Defs")):
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            for d in ET.parse(os.path.join(dp, fn)).getroot():
                n = d.findtext("defName")
                if n in ("RM_Ekkel", "RM_EkkelCatch") and d.tag == "ThingDef":
                    seen.add(n)
                    if "simmerlace" not in (d.findtext("description") or "").lower():
                        bad.append("ThingDef %s description lacks the simmerlace lore" % n)
    for n in ("RM_Ekkel", "RM_EkkelCatch"):
        if n not in seen:
            bad.append("ThingDef %s not found" % n)
    return bad


def saal_name_checks():
    """SCALD_SAAL_ONE_NAME_1: creature and catch are both labelled saal; no label says noohm."""
    bad = []
    for dp, _, fns in os.walk(os.path.join(HERE, "Defs")):
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            root = ET.parse(os.path.join(dp, fn)).getroot()
            for d in root:
                if d.findtext("defName") in ("RM_Noohm", "RM_Saal") and d.tag in ("ThingDef", "PawnKindDef"):
                    if (d.findtext("label") or "").strip() != "saal":
                        bad.append("%s %s label is %r, want 'saal'" % (d.tag, d.findtext("defName"), d.findtext("label")))
                if "noohm" in (d.findtext("label") or "").lower():
                    bad.append("%s label says noohm" % fn)
    return bad


def wax_checks():
    """CHILL_WAX_PROCESSION_GIANT_1 (def/source level): race, kind, sheet, roster row, comp class, csproj, toggle."""
    bad = []
    races = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_ChillWaxProcession.xml")
    root = ET.parse(races).getroot()
    td = {d.findtext("defName"): d for d in root.findall("ThingDef")}
    for n in ("RM_Hesuun", "RM_DeadFilterSheet"):
        if n not in td:
            bad.append("ThingDef %s missing" % n)
    if not [k for k in root.findall("PawnKindDef") if k.findtext("race") == "RM_Hesuun"]:
        bad.append("PawnKindDef for RM_Hesuun missing")
    h = td.get("RM_Hesuun")
    if h is not None:
        mn = h.findtext("statBases/ComfyTemperatureMin")
        if mn is None or float(mn) > NATIVE_MIN_C:
            bad.append("RM_Hesuun ComfyTemperatureMin %s needs <= %g" % (mn, NATIVE_MIN_C))
        if h.findtext("race/trainability") != "None":
            bad.append("RM_Hesuun must be untameable")
        if h.find("comps/li[@Class='RimMandrake.TerminalBiomes.RM_CompProperties_WaxProcession']") is None:
            bad.append("RM_Hesuun lacks the procession comp")
    meat = h.findtext("race/meatDef") if h is not None else None
    items = os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_TheChillFloraProducts.xml")
    if meat and meat not in [d.findtext("defName") for d in ET.parse(items).getroot().findall("ThingDef")]:
        bad.append("meatDef %s not defined" % meat)
    bd = [b for b in ET.parse(BIOME).getroot().findall("BiomeDef") if b.findtext("defName") == "RM_TheChill"][0]
    if "RM_Hesuun" not in {c.tag for c in bd.find("wildAnimals")}:
        bad.append("RM_Hesuun missing from RM_TheChill wildAnimals")
    if "RM_Hesuun" + "Catch" in {c.tag for g in (list(bd.find("fishTypes")) if bd.find("fishTypes") is not None else []) for c in g}:
        bad.append("RM_Hesuun must not be fishable")
    src = os.path.join(HERE, "Source")
    if "RM_Comp_WaxProcession.cs" not in open(os.path.join(src, "RM_TerminalBiomes.csproj"), encoding="utf-8").read():
        bad.append("RM_Comp_WaxProcession.cs missing from csproj Compile list")
    if "ChillWaxProcessionActive" not in open(os.path.join(src, "RM_TerminalBiomesMod.cs"), encoding="utf-8").read():
        bad.append("Mod Settings toggle ChillWaxProcessionActive missing")
    if not os.path.exists(os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "RM_Hesuun", "RM_Hesuun.png")):
        bad.append("RM_Hesuun texture missing")
    return bad




# --------------------------------------------------------------------------- parsed facts (never hand-listed)

sys.path.insert(0, os.path.join(HERE, "..", "Utils"))      # `python3 validation.py` finds modcheck

SETTINGS = "RimMandrake.TerminalBiomes.RM_TerminalBiomesSettings"
MOD_CS = os.path.join(HERE, "Source", "RM_TerminalBiomesMod.cs")
BIOMES = ["RM_TheChill", "RM_TheScald", "RM_TwilightSea", "RM_GreySea", "RM_ChillCrater"]


def _settings_body():
    return open(MOD_CS, encoding="utf-8").read().split("class RM_TerminalBiomesSettings")[1].split("ExposeData")[0]


def settings_defaults():
    """{field: (type, default)} parsed from the settings class's `public static` initialisers. `=>` properties are
    skipped (the negative lookahead), and enum-typed fields are returned as ("enum:<Type>", "<Member>")."""
    src = open(os.path.join(HERE, "Source", "RM_MapComponent_ChannelCurrent.cs"), encoding="utf-8").read()
    enums = {m.group(1): re.findall(r"^\s*(\w+)\s*(?:=\s*\d+)?\s*,?\s*$", m.group(2), flags=re.M)
             for m in re.finditer(r"enum (\w+)\s*(?::\s*\w+)?\s*\{(.*?)\}", src, flags=re.S)}
    out = {}
    body = _settings_body()
    for typ, name, val in re.findall(r"public static (bool|float|int|string) (\w+)\s*=(?!>)\s*([^;]+);", body):
        v = val.strip()
        if typ == "bool":
            out[name] = (typ, v == "true")
        elif typ == "float":
            out[name] = (typ, float(v.rstrip("f")))
        elif typ == "int":
            out[name] = (typ, int(v))
        else:
            out[name] = (typ, v.strip('"'))
    for typ, name, member in re.findall(r"public static (RM_\w+) (\w+)\s*=(?!>)\s*\1\.(\w+);", body):
        out[name] = ("enum:" + typ, member)
    return out, enums


def enum_members(type_name):
    return settings_defaults()[1].get(type_name, [])


def shipped_defs():
    """(defType, defName) for every concrete top-level def in the mod's own Defs/ XML."""
    out = []
    for dp, _, files in os.walk(os.path.join(HERE, "Defs")):
        for f in sorted(files):
            if f.endswith(".xml"):
                for e in ET.parse(os.path.join(dp, f)).getroot():
                    n = e.findtext("defName")
                    if n and e.get("Abstract") != "True" and not e.get("MayRequire"):
                        out.append((e.tag.split(".")[-1], n))
    return out


def terrain_defs():
    return [n for ty, n in shipped_defs() if ty == "TerrainDef"]


def biome_facts():
    """{biome defName: (animalDensity, rows in wildAnimals or None)} for our five biomes, from the XML."""
    out = {}
    for f in os.listdir(os.path.join(HERE, "Defs", "BiomeDefs")):
        for b in ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", f)).getroot().findall("BiomeDef"):
            wa = b.find("wildAnimals")
            out[b.findtext("defName")] = (float(b.findtext("animalDensity") or 0), len(wa) if wa is not None else None)
    return out


def settings_checks():
    """Every settings field is Scribed and has a window control; every .cs is in the csproj; sanity probes."""
    bad = []
    sd, enums = settings_defaults()
    if len(sd) < 30:
        bad.append("sanity probe: only %d settings fields parsed from RM_TerminalBiomesMod.cs (expected 38; regex broke)" % len(sd))
    mod = open(MOD_CS, encoding="utf-8").read()
    window = mod.split("DoWindowContents")[1]
    for f, (ty, d) in sd.items():
        if '"%s"' % f not in mod:
            bad.append("settings field %s is not Scribed in ExposeData" % f)
        if not re.search(r"\b%s\b" % f, window):
            bad.append("settings field %s has no control in DoWindowContents" % f)
        if ty.startswith("enum:") and d not in enums.get(ty[5:], []):
            bad.append("enum field %s default %s is not a member of %s" % (f, d, ty[5:]))
    proj = open(os.path.join(HERE, "Source", "RM_TerminalBiomes.csproj"), encoding="utf-8").read()
    listed = {c.replace("\\", "/") for c in re.findall(r'Compile Include="([^"]+)"', proj)}
    for cs in listed:
        if not os.path.isfile(os.path.join(HERE, "Source", cs)):
            bad.append("csproj lists missing file " + cs)
    for f in os.listdir(os.path.join(HERE, "Source")):
        if f.endswith(".cs") and f not in listed:
            bad.append("%s is not in the csproj (EnableDefaultCompileItems false: compiles into nothing)" % f)
    defs = shipped_defs()
    if len(defs) < 100:
        bad.append("sanity probe: only %d shipped defs parsed (expected 150+)" % len(defs))
    if len(terrain_defs()) != 17:
        bad.append("sanity probe: %d terrain defs parsed, expected 17 (Scald 7, Grey Sea 5, Chill 2, Crater 1, Bank silt 2)" % len(terrain_defs()))
    bf = biome_facts()
    for b in BIOMES:
        if b not in bf:
            bad.append("BiomeDef %s not found" % b)
    for b, (dens, rows) in bf.items():
        if rows and dens <= 0:
            bad.append("%s has a %d-row wildAnimals roster but animalDensity %g: the roster is dead content" % (b, rows, dens))
    if not any(f.endswith(".dll") for f in os.listdir(os.path.join(HERE, "Assemblies"))):
        bad.append("no DLL in Assemblies")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "TerminalBiomes.md")):
        bad.append("the walk design/validation_walks/RimMandrake/TerminalBiomes.md is missing")
    return bad


# --------------------------------------------------------------------------- the suite

try:
    from modcheck import Suite, ExpectationFailed
except ImportError:                       # offline static run outside the modcheck path
    Suite = None

if Suite is not None:
    suite = Suite("TerminalBiomes")
    SD, _ENUMS = settings_defaults()
    suite.toggles = [f for f, (ty, _) in SD.items() if ty == "bool"]

    # ----------------------------------------------------------------------- helpers

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _fail(msg):
        raise ExpectationFailed(msg)

    class _Unmeasured(Exception):
        pass

    def _unmeasured(t, why):
        t._why = why
        t._record("UNMEASURED", why)
        t.upstream_failed = True
        raise _Unmeasured(why)

    @contextlib.contextmanager
    def _comp(t, name, **kw):
        """t.component() with the UNMEASURED fix-up (verdict stays UNMEASURED, detail names the reason, the
        chain is not poisoned for an independent next component)."""
        before = t.upstream_failed
        t._why = None
        with t.component(name, **kw) as tt:
            yield tt
        why = getattr(t, "_why", None)
        if why and not before:
            t.components[-1].detail = "UNMEASURED: %s" % why
            t.upstream_failed = False
        t._why = None
        if t.session is not None:
            c = t.components[-1]
            print("[tb] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
                  file=sys.stderr, flush=True)

    def _static(problems):
        if problems:
            _fail("; ".join(problems))

    def _sv(v):
        if isinstance(v, bool):
            return "True" if v else "False"
        if isinstance(v, float):
            return "%g" % v
        return str(v)

    def _same(got, want):
        if str(got).strip().lower() == str(want).strip().lower():
            return True
        try:
            return abs(float(got) - float(want)) < 1e-6
        except (TypeError, ValueError):
            return False

    def _put(t, field, value):
        s = t.session
        if s is None:
            return
        sv = _sv(value)
        r = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=sv)
        if not (r or {}).get("success"):
            raise ExpectationFailed("mod_settings_field set %s=%r failed: %r" % (field, sv, r))
        g = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not (g or {}).get("success") or not _same((g or {}).get("value"), sv):
            raise ExpectationFailed("mod_settings_field %s did not take: wrote %r, read back %r"
                                    % (field, sv, (g or {}).get("value")))

    def _get(t, field):
        g = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not (g or {}).get("success"):
            raise ExpectationFailed("mod_settings_field get %s failed: %r" % (field, g))
        return g.get("value")

    def _ok(r, what):
        if not isinstance(r, dict) or r.get("success") is False:
            _fail("%s failed: %r" % (what, r))
        return r

    def _things(t, defName, rect):
        r = _ok(t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=100), "list_things")
        if r.get("isCompleteList") is False:
            _unmeasured(t, "list_things truncated")
        return r.get("things") or []

    # ----------------------------------------------------------------------- 1. defs_resolve

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        """Every def the mod ships (parsed from its own Defs/ XML) resolves live; a control reads absent."""
        with _comp(t, "shipped_defs_resolve", beyond_toggle=True):
            want = ["%s/%s" % x for x in shipped_defs()]
            for i in range(0, len(want), 25):
                chunk = want[i:i + 25]
                r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=100)
                if _live(t):
                    if not isinstance(r, dict) or r.get("success") is not True:
                        _unmeasured(t, "get_defs could not be asked: %s" % str(r)[:140])
                    if r.get("notFound") or r.get("foundCount") != len(chunk):
                        _fail("shipped defs did not load (a def with an unresolvable field is discarded silently): "
                              "notFound=%r foundCount=%r of %d" % (r.get("notFound"), r.get("foundCount"), len(chunk)))
        with _comp(t, "control_absent_def_reads_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/RM_TerminalBiomes_NoSuchControl")
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True:
                    _unmeasured(t, "control ask failed: %s" % str(r)[:140])
                if r.get("foundCount") != 0 or not r.get("notFound"):
                    _fail("the probe cannot say absent: control returned %r" % r)

    # ----------------------------------------------------------------------- 2. settings round trips

    def _alt(typ, d):
        if typ == "bool":
            return not d
        if typ == "int":
            return d + 1
        if typ == "string":
            return "RM_NoSuchBiome"
        if typ.startswith("enum:"):
            mem = _ENUMS.get(typ[5:], [])
            return next((m for m in mem if m != d), d)
        return d * 2 + 1

    def _make_flip(field, typ, default):
        def chain(t):
            with _comp(t, "%s_round_trips" % field, toggle=field if typ == "bool" else None, beyond_toggle=typ != "bool"):
                try:
                    try:
                        _put(t, field, _alt(typ, default))
                    except ExpectationFailed as e:
                        if typ.startswith("enum:") and t.session is not None:
                            _unmeasured(t, "the bridge setter could not take an enum member name (%s); unproven shape" % str(e)[:200])
                        raise
                    _put(t, field, default)
                finally:
                    if t.session is not None:
                        try:
                            _put(t, field, default)
                        except Exception as e:
                            print("[tb] RESTORE FAILED %s: %s" % (field, e), file=sys.stderr, flush=True)
        chain.__doc__ = "Write alt, read back, write default, read back (numeric compare) for %s." % field
        return chain

    for _f, (_ty, _d) in SD.items():
        suite.chain("flip_%s" % _f)(_make_flip(_f, _ty, _d))

    # ----------------------------------------------------------------------- 3. offline facts, as components

    @suite.chain("natives_tolerate_floor")
    def natives_tolerate_floor(t):
        """Every RM_ Chill native is comfortable below the -110 C floor (source), and the live def says so too."""
        with _comp(t, "natives_comfy_min_below_floor_in_source", beyond_toggle=True):
            _static(static_checks())
        with _comp(t, "natives_comfy_min_below_floor_live", beyond_toggle=True):
            if _live(t):
                bad = []
                for n in NATIVES:
                    r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % n, fields="statBases", deep=True, limit=2)
                    if not isinstance(r, dict) or r.get("success") is not True:
                        _unmeasured(t, "get_defs ThingDef/%s statBases could not be asked: %s" % (n, str(r)[:140]))
                    rows = [d for d in (r.get("defs") or []) if d.get("defName") == n]
                    sb = ((rows[0].get("fields") or {}).get("statBases") if rows else None)
                    if not isinstance(sb, list) or not sb or not all(isinstance(x, dict) for x in sb):
                        _unmeasured(t, "get_defs returned statBases as %r, not a list of {stat, value} rows" % (sb,))
                    mn = [x.get("value") for x in sb if "ComfyTemperatureMin" in json.dumps(x)]
                    if not mn:
                        _unmeasured(t, "no ComfyTemperatureMin row in statBases of %s: %r" % (n, sb[:3]))
                    try:
                        if float(mn[0]) > NATIVE_MIN_C:
                            bad.append("%s ComfyTemperatureMin=%s" % (n, mn[0]))
                    except (TypeError, ValueError):
                        _unmeasured(t, "ComfyTemperatureMin of %s is not numeric: %r" % (n, mn[0]))
                if bad:
                    _fail("live natives not cold-tolerant (stale deploy?): %s" % bad)

    @suite.chain("floor_roster_trimmed")
    def floor_roster_trimmed(t):
        with _comp(t, "chill_roster_is_the_floor_natives", beyond_toggle=True):
            _static(roster_checks())

    @suite.chain("saal_one_name")
    def saal_one_name(t):
        with _comp(t, "creature_and_catch_both_labelled_saal", beyond_toggle=True):
            _static(saal_name_checks())
        with _comp(t, "ekkel_carries_simmerlace_lore", beyond_toggle=True):
            _static(ekkel_lore_checks())

    @suite.chain("catch_free_tier")
    def catch_free_tier(t):
        with _comp(t, "chill_catch_is_free_tier_and_alive_on_the_floor", beyond_toggle=True):
            _static(catch_checks())

    @suite.chain("settings_wiring")
    def settings_wiring(t):
        with _comp(t, "every_field_scribed_exposed_and_compiled", beyond_toggle=True):
            _static(settings_checks())

    @suite.chain("biome_animal_density")
    def biome_animal_density(t):
        """A rostered biome with animalDensity 0 spawns nothing (engine gate); the live def must carry the shipped density."""
        with _comp(t, "rostered_biomes_have_density_above_zero", beyond_toggle=True):
            if _live(t):
                for b, (dens, rows) in biome_facts().items():
                    if not rows:
                        continue
                    r = t.bridge_call("jawa/get_defs", defs="BiomeDef/%s" % b, fields="animalDensity", limit=2)
                    if not isinstance(r, dict) or r.get("success") is not True:
                        _unmeasured(t, "get_defs BiomeDef/%s could not be asked: %s" % (b, str(r)[:140]))
                    got = [((d.get("fields") or {}).get("animalDensity")) for d in (r.get("defs") or []) if d.get("defName") == b]
                    if not got or got[0] is None:
                        _unmeasured(t, "get_defs returned no animalDensity for %s: %r" % (b, r.get("defs")))
                    if not _same(got[0], dens) or float(got[0]) <= 0:
                        _fail("live %s animalDensity %r, shipped %g: its %d-row roster would never spawn" % (b, got[0], dens, rows))

    # ----------------------------------------------------------------------- 4. terrains paint and read back

    @suite.chain("terrains_paint")
    def terrains_paint(t):
        """Each of the 17 biome terrains can be painted on a cell and read back; a vanilla terrain is the control."""
        names = terrain_defs()
        P = {}
        with _comp(t, "site_ready_terrain_row", beyond_toggle=True):
            if _live(t):
                t.clear_area(size=24)
                x, z = t.anchor
                P["x"], P["z"] = x - 12, z
                r = t.bridge_call("jawa/set_terrain_batch", ops="Concrete:%d,%d,1,1" % (P["x"], P["z"] - 2))
                _ok(r, "set_terrain_batch")
        with _comp(t, "control_vanilla_terrain_reads_back", beyond_toggle=True):
            if _live(t):
                got = _ok(t.bridge_call("jawa/get_terrain_batch", rects="%d,%d,1,1" % (P["x"], P["z"] - 2)), "get_terrain_batch").get("distinctTerrains") or []
                if got != ["Concrete"]:
                    _unmeasured(t, "control: Concrete painted and read back as %r, so the terrain read cannot be trusted" % (got,))
        with _comp(t, "every_biome_terrain_paints_and_reads_back", beyond_toggle=True):
            if _live(t):
                ops = ";".join("%s:%d,%d,1,1" % (n, P["x"] + i, P["z"]) for i, n in enumerate(names))
                _ok(t.bridge_call("jawa/set_terrain_batch", ops=ops), "set_terrain_batch")
                wrong = []
                for i, n in enumerate(names):
                    d = _ok(t.bridge_call("jawa/get_terrain_batch", rects="%d,%d,1,1" % (P["x"] + i, P["z"])), "get_terrain_batch").get("distinctTerrains") or []
                    if d != [n]:
                        wrong.append("%s -> %r" % (n, d))
                if wrong:
                    _fail("terrains painted but read back differently (a defect in the terrain def, or the tool converts it): %s" % wrong)

    # ----------------------------------------------------------------------- 5. cryoponics vat

    @suite.chain("cryoponics_vat")
    def cryoponics_vat(t):
        """The vat's own class is live: its inspect string names the cryogenic bath, a vanilla grower's does not."""
        P = {}
        with _comp(t, "site_ready_vat_and_control_grower", beyond_toggle=True):
            if _live(t):
                t.clear_area(size=16)
                x, z = t.anchor
                t.bridge_call("jawa/spawn_batch", ops="RM_ChillCryoponicsVat:%d,%d;HydroponicsBasin:%d,%d" % (x, z, x + 5, z))
                for key, name, cx in (("vat", "RM_ChillCryoponicsVat", x), ("ctl", "HydroponicsBasin", x + 5)):
                    rows = _things(t, name, "%d,%d,4,4" % (cx - 1, z - 1))
                    if not rows:
                        _unmeasured(t, "SITE: %s did not spawn at %d,%d" % (name, cx, z))
                    P[key] = rows[0]["id"]
        with _comp(t, "vat_reports_a_cryogenic_bath_line", toggle="chillCryoponicsEnabled"):
            if _live(t):
                def line(tid):
                    r = _ok(t.bridge_call("jawa/inspect_string", thingIds=tid), "inspect_string")
                    row = next((x for x in (r.get("things") or []) if x.get("id") == tid), None)
                    if row is None or row.get("error"):
                        _unmeasured(t, "inspect_string unreadable for %s: %r" % (tid, row))
                    return " ".join(str(x) for x in (row.get("inspect") or []))
                if "Cryogenic bath" in line(P["ctl"]):
                    _fail("the vanilla control grower reports a cryogenic bath: the read cannot tell the vat apart")
                if "Cryogenic bath" not in line(P["vat"]):
                    _fail("the cryoponics vat has no 'Cryogenic bath' line: its thingClass RM_Building_CryoGrower is not live")
        with _comp(t, "powered_bath_runs_and_toggle_off_goes_offline", toggle="chillCryoponicsEnabled"):
            _unmeasured(t, "the 'running' state needs the vat on a powered grid and plants sown in it; no bridge tool wires a power net, "
                           "so only the class wiring above is provable on a bland map")

    # ----------------------------------------------------------------------- 6. wax procession colony

    @suite.chain("wax_procession")
    def wax_procession(t):
        """Killing a Hesuun colony spoils its carried sheet into hydrocarbon flesh (RM_Comp_WaxProcession.PostDestroy)."""
        P = {}
        with _comp(t, "wax_giant_wired_in_source", beyond_toggle=True):
            _static(wax_checks())
        with _comp(t, "site_ready_hesuun", beyond_toggle=True):
            if _live(t):
                t.clear_area(size=24)
                x, z = t.anchor
                P["x"], P["z"] = x, z
                P["pid"] = t.spawn_pawn("RM_Hesuun")
                if not P["pid"]:
                    _unmeasured(t, "spawn_pawn RM_Hesuun returned no pawn id")
                if _things(t, "RM_HydrocarbonFlesh", "%d,%d,24,24" % (x - 12, z - 12)):
                    _unmeasured(t, "SITE: hydrocarbon flesh already lies in the test area, so a post-kill appearance proves nothing")
        with _comp(t, "killed_colony_spoils_into_hydrocarbon_flesh", toggle="chillWaxProcessionEnabled"):
            if _live(t):
                r = t.bridge_call("jawa/pawn_force_incapacitate", pawn=P["pid"], action="kill")
                if not (r or {}).get("success"):
                    _unmeasured(t, "pawn_force_incapacitate kill failed: %s" % str(r)[:160])
                t.wait_ticks(60)
                rows = _things(t, "RM_HydrocarbonFlesh", "%d,%d,24,24" % (P["x"] - 12, P["z"] - 12))
                if not rows:
                    _fail("a killed RM_Hesuun left no RM_HydrocarbonFlesh: the comp's KillFinalize spoil path is dead "
                          "(or the pawn was removed without dying)")
                total = sum(int(x.get("stackCount") or x.get("count") or 0) for x in rows)
                if total and total < 12:
                    _fail("killed colony spoiled into %d flesh, the comp promises spoilCountPerSheet 12 for the carried sheet" % total)
        with _comp(t, "sheet_extruded_at_a_pause_after_the_walk", toggle="chillWaxProcessionEnabled"):
            _unmeasured(t, "the countdown is 90000 ticks of walking (ticksBetweenSheets) before the first sheet at a pause; a wait of "
                           "that length is not a bland-map check, and no tool seeds the comp's countdown")

    # ----------------------------------------------------------------------- 7. honest UNMEASURED

    def _um(chain, comp, why, toggle=None):
        def fn(t):
            with _comp(t, comp, toggle=toggle, beyond_toggle=toggle is None):
                _unmeasured(t, why)
        fn.__doc__ = "UNMEASURED: " + why
        suite.chain(chain)(fn)

    _um("scald_steam_sky", "steam_lock_pulses_weather_and_flash", "RUT_ScaldSteamLock/RM_GameCondition_WeatherPulse and the vent flash need a Scald map "
        "(an environmental-hazards weather pulse over a steam biome) and a way to read the running condition", "scaldS1SteamSkyEnabled")
    _um("scald_steam_catch", "condenser_collects_steam", "RUT_SteamCatch condensing needs a Scald map with a vent and ticks of steam; no reader for the "
        "condenser's stored resource", "scaldS2SteamCatchEnabled")
    _um("scald_vent_fields", "vents_scatter_and_erupt", "RUT_ScaldVent geysers are placed by a GenStep on a NEW Scald map; the gate acts at generation "
        "(worldgen-affecting), so a held bland map cannot show it", "scaldS4VentFieldsEnabled")
    _um("scald_sail_walker", "walker_surfaces_and_sails_scatter", "RUT_WalkerSurfacing and the sail scatterer need a Scald map and a Scald-gated incident",
        "scaldS5SailWalkerEnabled")
    _um("scald_wreck_salvage", "wrecks_scatter_and_yield_salvage", "RUT_ScaldWreckScatter runs at map generation on the Scald biome; needs a fresh Scald map",
        "scaldS6WreckSalvageEnabled")
    _um("scald_steam_exposure", "steam_carrier_inflicts_scald_exposure", "RUT_ScaldSteamCarrier and the RUT_ScaldExposure hediff need a Scald map under "
        "steam and an unprotected pawn; no way to start the condition on a bland map", "scaldS7SteamExposureEnabled")
    _um("twilight_suulk", "suulk_arrival_and_vaulisk_lure", "RM_SuulkArrival and the Vaulisk lure are Twilight-sea incidents and a GenStep; need the "
        "sea-floor map", "suulkEnabled")
    _um("twilight_channel_current", "current_carries_pawns_and_sink_outcome_applies", "RM_MapComponent_ChannelCurrent exists only on a generated "
        "Twilight map with channels; the sink outcome and undersurge frequency are read from a running current", "channelCurrentEnabled")
    _um("twilight_pane_strike", "veil_pane_falls_and_deck_accumulates", "RM_VeilFallPaneStrike and RM_VeilPane deck accumulation need a Twilight map "
        "with panes and the gravship launch gate", "twilightPaneStrikeEnabled")
    _um("twilight_well_drift", "well_ledger_drifts_and_sun_sphere_cultures", "RM_MapComponent_WellLedger and RM_Building_SunSphere stages run over "
        "days on a Twilight map", "twilightWellDriftEnabled")
    _um("twilight_cages_passable", "cage_passability_follows_the_setting", "RM_TwilightPassabilityApplier writes ThingDef.passability only from the "
        "settings WINDOW frame, which a bridge setter never triggers", "twilightCagesPassableBeneath")
    _um("cross_biome", "scald_mechanics_outside_the_scald", "WORLDGEN-AFFECTING and inert: crossBiomeEnabled is reserved for a future pass (mod "
        "header), so there is nothing to read", "crossBiomeEnabled")

    @suite.chain("grey_hull_crust")
    def grey_hull_crust(t):
        """GREYSEA_HULL_CRUST_BUILD_1: on a Grey map with a parked gravship, advancing the clock past the ruled
        ladder rimes the hull, salts an exterior door and grows crust that the launch-gate postfix counts."""
        with _comp(t, "ladder_rime_door_crust_gate", toggle="greyHullCrustEnabled"):
            if _live(t):
                r = t.bridge_call("jawa/static_call", type="RimMandrake.TerminalBiomes.RM_GreyHullCrustProof",
                                  method="ProofState", args="")
                res = str((r or {}).get("result", ""))
                if not res.startswith("crustDays="):
                    _unmeasured(t, "needs a parked gravship on an RM_GreySea floor map (seabed layer); proof said %r" % res[:120])
                else:
                    r = t.bridge_call("jawa/static_call", type="RimMandrake.TerminalBiomes.RM_GreyHullCrustProof",
                                      method="ProofAdvance", args="16")
                    res = str((r or {}).get("result", ""))
                    m = dict(kv.split("=", 1) for kv in res.split(" ") if "=" in kv)
                    if int(m.get("rime", 0)) < 1 or int(m.get("crust", 0)) < 1 or m.get("gate") == "accepted":
                        _fail("16 effective days did not rime + crust + gate the hull: %r" % res)

    @suite.chain("settings_restored")
    def settings_restored(t):
        """LAST: every field is back at its shipped (parsed) default; a leaked arm would corrupt the next run."""
        with _comp(t, "all_settings_at_shipped_defaults", beyond_toggle=True):
            if _live(t):
                bad = [(f, _get(t, f), _sv(d)) for f, (ty, d) in SD.items() if not _same(_get(t, f), _sv(d))]
                if bad:
                    _fail("settings left off their shipped default by an earlier arm: %s" % bad)
else:
    suite = None


if __name__ == "__main__":
    problems = (static_checks() + roster_checks() + catch_checks() + saal_name_checks() + ekkel_lore_checks()
                + wax_checks() + settings_checks())
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
