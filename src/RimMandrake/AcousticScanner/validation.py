"""validation.py -- modcheck suite for RimMandrake: Acoustic Scanner (mandrake.rm.acousticscanner).

First north-star script (ACOUSTIC_SCANNER_FIRST_SCRIPT_1, debug_process.md section 2). NEVER RUN LIVE YET: the
live shapes it assumes are listed in the walk's anti-guessing notes, and every one that is absent reads
UNMEASURED, never PASS.

WHAT IT PROVES (state reads, never a screenshot hunt):
  * defs_resolve: the sounder and its research project resolve in the running game; a control def that does
    not exist reads absent (so the probe can say "no"); the sounder is gated by RM_AcousticSounding and the
    research sits after BasicGravtech; the payload class and settings class are loaded.
  * settings_roundtrip: every Mod Settings field the C# declares writes, reads back and restores.
  * sounder_gating: the sounder's own inspect line is its CanPulse state: refuses unpowered, refuses off the
    ship, refuses with the master switch off, relaxes with requireLandedShip off, reads ready on a
    powered sounder on substructure with a grav engine on the map.
  * pulse: firing the gizmo starts the cooldown and sends the reading letter.
UNMEASURED (reason recorded): the banded overlay itself (not saved, no reader), biome payload content (needs a
map whose biome carries the extension), and the dust/thump/shake effects (visual/audio).

STATIC (offline): `python3 validation.py` runs `static_checks()` with no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_TYPE = "RimMandrake.AcousticScanner.RM_AcousticScannerSettings"
PAYLOAD_TYPE = "RimMandrake.AcousticScanner.RM_AcousticPayloadExtension"
MOD_NAME = "RimMandrake: Acoustic Scanner"

# Shipped defaults, read off RM_AcousticScannerMod.cs; static_checks() re-reads the C# and fails on drift.
DEFAULTS = {"enabled": True, "requireLandedShip": True, "cooldownHours": 24.0, "overlayHours": 6.0,
            "bandSize": 11, "rangeCells": 60.0, "pulseEffects": True}
# a value different from the default for each field, for the write arm of the round trip
ALT = {"enabled": False, "requireLandedShip": False, "cooldownHours": 3.0, "overlayHours": 2.0,
       "bandSize": 9, "rangeCells": 80.0, "pulseEffects": False}
DEFS = ["ThingDef/RM_AcousticSounder", "ResearchProjectDef/RM_AcousticSounding"]
CONTROL_ABSENT = "ThingDef/RM_AcousticSounder_NoSuchDef_Control"
PAYLOAD_BIOMES = ["RM_FloodedCanyon", "RM_Stillsand", "RUT_CrackedLands"]    # the criteria's live-probe biomes; every owned BiomeDef carries a payload (owned_biomes)
SOUNDER = "RM_AcousticSounder"
ENGINE = "GravEngine"
PULSE_LABEL = "Sound the ground"
# The inspect line the sounder shows per CanPulse outcome (Languages/English/Keyed).
TXT = {"ready": "Ready to sound", "nopower": "No power", "notship": "substructure of a landed gravship",
       "off": "switched off", "cooldown": "Transducer settling"}


# ---------------------------------------------------------------------------------------------- static

def _strip_cs(text):
    return re.sub(r"//[^\n]*", "", text)


def settings_from_cs():
    """{field: default literal} for every public field of RM_AcousticScannerSettings (static or instance)."""
    src = _strip_cs(open(os.path.join(HERE, "Source", "RM_AcousticScannerMod.cs"), encoding="utf-8").read())
    body = src.split("class RM_AcousticScannerSettings", 1)[1].split("public void DoWindowContents", 1)[0]
    out = {}
    for m in re.finditer(r"public\s+(?:static\s+)?(bool|float|int)\s+(\w+)\s*=(?!>)\s*([^;]+);", body):
        if "const" in m.group(0):
            continue
        out[m.group(2)] = (m.group(1), m.group(3).strip())
    return out


def _literal(kind, raw):
    raw = raw.strip()
    if kind == "bool":
        return raw == "true"
    return float(raw.rstrip("f")) if kind == "float" else int(raw)


SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
# defs a payload may name that live outside src/: vanilla terrains and donor races/plants on our rosters
DONOR_DEFS = {"WaterShallow", "WaterMovingShallow", "WaterDeep", "WaterMovingChestDeep", "HotSpring", "Mud",
              "Terrorworm", "AB_RimeNodules"}


def _src_xml():
    for dp, dns, fns in os.walk(SRC):
        dns[:] = [d for d in dns if d not in ("__pycache__", "Source", "Textures", "Assemblies")]
        for fn in fns:
            if fn.endswith(".xml"):
                yield os.path.join(dp, fn)


def payload_patch_files():
    return sorted(p for p in _src_xml() if os.sep + "Patches" + os.sep in p
                  and PAYLOAD_TYPE in open(p, encoding="utf-8", errors="replace").read())


def _defs_roots():
    for p in _src_xml():
        if os.sep + "Patches" + os.sep in p:
            continue
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        if r.tag == "Defs":
            yield r


def src_def_names():
    return {el.findtext("defName") for r in _defs_roots() for el in r if el.findtext("defName")}


def owned_biomes():
    """Every concrete BiomeDef defined in src/, parsed as elements."""
    return {b.findtext("defName") for r in _defs_roots() for b in r.findall("BiomeDef")
            if b.findtext("defName") and b.get("Abstract") != "True"}


def static_checks():
    """Return a list of failure strings; empty means pass. Needs no game."""
    bad = []
    cs = settings_from_cs()
    if not cs:       # sanity probe: the regex must find the settings, or "no drift" means nothing
        return ["settings regex found 0 fields in RM_AcousticScannerMod.cs: the probe is blind"]
    for f, (kind, raw) in cs.items():
        if f not in DEFAULTS:
            bad.append("C# settings field %s is not in DEFAULTS" % f)
        elif _literal(kind, raw) != DEFAULTS[f]:
            bad.append("default drift on %s: C# %s vs script %r" % (f, raw, DEFAULTS[f]))
    for f in DEFAULTS:
        if f not in cs:
            bad.append("DEFAULTS field %s is gone from the C#" % f)
        if f not in ALT or ALT[f] == DEFAULTS[f]:
            bad.append("ALT value for %s missing or equal to the default" % f)
    mod = open(os.path.join(HERE, "Source", "RM_AcousticScannerMod.cs"), encoding="utf-8").read()
    for f in cs:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), mod):
            bad.append("settings field %s is not Scribed" % f)
        if not re.search(r"\b%s\b" % f, mod.split("DoWindowContents(Rect")[1]) and f != "bandSize":
            bad.append("settings field %s has no control in DoWindowContents" % f)
    if "BandSizeClamped" not in mod or "MinBandSize = 7" not in mod:
        bad.append("band size floor (MinBandSize 7, BandSizeClamped) is gone: readings could become exact")
    # every .cs is compiled (EnableDefaultCompileItems false)
    csproj = open(os.path.join(HERE, "Source", "RM_AcousticScanner.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Include="%s"' % fn not in csproj:
            bad.append("%s is not a <Compile Include> in the csproj" % fn)
    # defs parse and say what the mod says
    th = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_AcousticSounder.xml")).getroot()[0]
    rs = ET.parse(os.path.join(HERE, "Defs", "ResearchProjectDefs", "RM_AcousticSounding.xml")).getroot()[0]
    if th.findtext("defName") != SOUNDER:
        bad.append("sounder def name changed")
    if th.findtext("thingClass") != "RimMandrake.AcousticScanner.RM_Building_AcousticSounder":
        bad.append("sounder thingClass wrong")
    if th.findtext("placeWorkers/li") != "PlaceWorker_OnSubstructure":
        bad.append("sounder is not substructure-only")
    if th.findtext("researchPrerequisites/li") != "RM_AcousticSounding":
        bad.append("sounder is not gated by RM_AcousticSounding")
    if th.find("comps/li[@Class='CompProperties_Power']") is None:
        bad.append("sounder carries no power comp")
    if rs.findtext("prerequisites/li") != "BasicGravtech":
        bad.append("research does not follow BasicGravtech")
    # Keyed text: every key the C# translates exists, and the inspect strings this script reads are the shipped ones
    keyed_dir = os.path.join(HERE, "Languages", "English", "Keyed")
    keyed = "".join(open(os.path.join(keyed_dir, f), encoding="utf-8").read() for f in os.listdir(keyed_dir))
    srcall = "".join(open(os.path.join(HERE, "Source", f), encoding="utf-8").read()
                     for f in os.listdir(os.path.join(HERE, "Source")) if f.endswith(".cs"))
    keys = set(re.findall(r'"(RM_Acoustic_\w+)"', srcall)) - {"RM_Acoustic_Tier"}   # Tier+Faint/Moderate/Strong is built dynamically
    for tier in ("Faint", "Moderate", "Strong"):
        keys.add("RM_Acoustic_Tier" + tier)
    if not keys:
        bad.append("sanity probe: found no RM_Acoustic_ keys in the C#")
    for k in sorted(keys):
        if "<%s>" % k not in keyed:
            bad.append("translation key %s used in C# is not in Languages/English/Keyed" % k)
    for k, frag in TXT.items():
        if frag not in keyed:
            bad.append("script reads inspect text %r (%s) but Keyed no longer says it" % (frag, k))
    if PULSE_LABEL not in keyed:
        bad.append("gizmo label %r is not in Keyed" % PULSE_LABEL)
    # the payload patches: parse, FindMod-guarded by this mod's name, target a BiomeDef, no top-level MayRequire
    patch_files = payload_patch_files()
    if len(patch_files) < 3:   # sanity probe: the glob must find the three original payload files at least
        bad.append("sanity probe: payload glob found %d patch files (expected >= 3)" % len(patch_files))
    known = src_def_names()
    targeted = set()
    for p in patch_files:
        if not os.path.exists(p):
            bad.append("payload patch missing: %s" % os.path.basename(p))
            continue
        raw = open(p, encoding="utf-8").read()
        if MOD_NAME not in raw:
            bad.append("%s is not FindMod-guarded on %r" % (os.path.basename(p), MOD_NAME))
        if re.search(r"<Operation[^>]*MayRequire", raw):
            bad.append("%s uses MayRequire on an Operation (inert)" % os.path.basename(p))
        root = ET.parse(p).getroot()
        for xp in root.iter("xpath"):
            m = re.search(r'BiomeDef\[defName="(\w+)"\]', xp.text or "")
            if m:
                targeted.add(m.group(1))
        for ext in root.iter("li"):
            if ext.get("Class") == PAYLOAD_TYPE:
                if not ext.findall("targets/li"):
                    bad.append("%s: payload has no targets" % os.path.basename(p))
                for t in ext.findall("targets/li"):
                    if not (t.findtext("label") or "").strip():
                        bad.append("%s: a target has no label" % os.path.basename(p))
                    if not any(t.find(k) is not None for k in ("thingDefs", "pawnRaces", "terrainDefs", "hiddenCaves")):
                        bad.append("%s: target %r matches nothing" % (os.path.basename(p), t.findtext("label")))
                    for k in ("thingDefs", "pawnRaces", "terrainDefs"):
                        for li in t.findall(k + "/li"):
                            if li.text not in known and li.text not in DONOR_DEFS:
                                bad.append("%s: %s names %r, defined nowhere in src/ and not a listed donor/vanilla def"
                                           % (os.path.basename(p), k, li.text))
    # owner card 2026-10-06: the payload goes on EVERY BiomeDef of ours (zero-tile biomes included)
    owned = owned_biomes()
    if len(owned) < 20:        # sanity probe: the BiomeDef census must see the biome mods
        bad.append("sanity probe: owned-BiomeDef census found only %d" % len(owned))
    for b in sorted(owned - targeted):
        bad.append("owned BiomeDef %s carries no acoustic payload" % b)
    for b in sorted(targeted - owned):
        bad.append("a payload targets %s, which is not a BiomeDef defined in src/" % b)
    for b in PAYLOAD_BIOMES:
        if b not in targeted:
            bad.append("live-probe biome %s lost its payload" % b)
    # the walk exists and declares coverage for every line
    walk = os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "AcousticScanner.md")
    if not os.path.exists(walk):
        bad.append("walk design/validation_walks/RimMandrake/AcousticScanner.md is missing")
    else:
        w = open(walk, encoding="utf-8").read().split("## must be true", 1)[-1].split("\n## ", 1)[0]
        for ln in w.splitlines():
            if ln.startswith("- ") and "→" not in ln:
                bad.append("walk line has no coverage arrow: %s" % ln[:70])
    return bad


# ---------------------------------------------------------------------------------------------- live

def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("AcousticScanner")
    suite.toggles = ["enabled", "requireLandedShip", "pulseEffects"]
    state = {}

    def _unmeasured(t, why):
        """UNMEASURED, never FAIL: __exit__ turns upstream_failed into verdict UNMEASURED."""
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _live(t):
        return t.session is not None

    def _set(t, field, value):
        t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=field,
                      value=str(value))

    def _get(t, field):
        r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="get", field=field)
        return (r or {}).get("value")

    def _restore(t, field):
        if t.session is not None:
            try:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set",
                               field=field, value=str(DEFAULTS[field]))
            except Exception as ex:
                print("[acousticscanner] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)

    def _same(got, want):
        if isinstance(want, bool):
            return str(got).strip().lower() == str(want).lower()
        try:
            return abs(float(got) - float(want)) < 1e-6      # numerics compared as numbers ('3' vs 3.0)
        except (TypeError, ValueError):
            return False

    def _defs_read(t, defs, **kw):
        r = t.bridge_call("jawa/get_defs", defs=";".join(defs), limit=50, **kw)
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("get_defs could not ask: %r" % (r,))
        return r

    def _inspect(t, thing_id):
        r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
        row = next((x for x in ((r or {}).get("things") or []) if x.get("id") == thing_id), None)
        if row is None or row.get("error"):
            raise ExpectationFailed("inspect_string failed for %s: %r" % (thing_id, row or r))
        return " ".join(str(x) for x in (row.get("inspect") or []))

    def _thing_id(t, defName, rect):
        rows = (t.bridge_call("jawa/list_things", defName=defName, rect=rect) or {}).get("things") or []
        return rows[0]["id"] if rows else None

    def _site(t):
        """Clear a pad, lay a 7x7 substructure patch under the anchor, spawn the sounder on it. Returns
        (sounder id, pad rect) or None after recording UNMEASURED."""
        x, z = t.anchor
        t.clear_area(size=30)
        rect = "%d,%d,%d,%d" % (x - 12, z - 12, 24, 24)
        sub = t.bridge_call("jawa/set_substructure_batch", action="set",
                            rect="%d,%d,7,7" % (x - 3, z - 3), doLeavings=False, readBack=0)
        if isinstance(sub, dict) and sub.get("success") is False:
            _unmeasured(t, "set_substructure_batch refused the add: %r" % (sub,))
            return None
        t.spawn(SOUNDER, count=1, at="point")
        sid = _thing_id(t, SOUNDER, rect)
        if sid is None:
            _unmeasured(t, "the sounder did not spawn on the pad (spawn_batch refused it)")
            return None
        # LIVE 2026-10-03: a spawned sounder is unclaimed, and GetGizmos yields nothing but vanilla's 'Claim' unless
        # Faction == Player (so the 'Sound the ground' gizmo was never listed). Claim it as a player would.
        t.bridge_call("jawa/set_thing_props", thing=sid, faction="Player")
        state.update(sid=sid, rect=rect)
        return sid, rect

    def _engine(t, present):
        x, z = t.anchor
        if present:
            t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (ENGINE, x + 9, z))
        else:
            t.bridge_call("jawa/destroy_batch", rects="%d,%d,5,5" % (x + 7, z - 2), categories="All")

    # ------------------------------------------------------------------ chain 1: defs resolve
    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("defs_resolve", beyond_toggle=True):
            if not _live(t):
                return
            r = _defs_read(t, DEFS)
            if r.get("notFound") or int(r.get("foundCount", 0)) != len(DEFS):
                raise ExpectationFailed("shipped defs did not resolve: found %r notFound %r"
                                        % (r.get("foundCount"), r.get("notFound")))
        with t.component("probe_can_say_absent", beyond_toggle=True):
            if not _live(t):
                return
            r = _defs_read(t, [CONTROL_ABSENT])
            if int(r.get("foundCount", 0)) != 0 or CONTROL_ABSENT.split("/")[1] not in " ".join(
                    str(x) for x in (r.get("notFound") or [])):
                raise ExpectationFailed("control: a def that does not exist did not read absent: %r" % (r,))
        with t.component("classes_loaded", beyond_toggle=True):
            if not _live(t):
                return
            for tn in (SETTINGS_TYPE, PAYLOAD_TYPE):
                r = t.bridge_call("jawa/type_probe", typeName=tn)
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("type %s is not loaded in the running game: %r" % (tn, r))
        with t.component("research_gate", beyond_toggle=True):
            if not _live(t):
                return
            r = _defs_read(t, DEFS, fields="researchPrerequisites,prerequisites", deep=True)
            rows = {d.get("defName"): (d.get("fields") or {}) for d in (r.get("defs") or [])}

            def names(v):
                return [x.get("defName") if isinstance(x, dict) else str(x) for x in (v or [])]
            gate = names(rows.get(SOUNDER, {}).get("researchPrerequisites"))
            pre = names(rows.get("RM_AcousticSounding", {}).get("prerequisites"))
            if not gate or not pre:
                _unmeasured(t, "get_defs did not return the prerequisite lists: %r" % (rows,))
                return
            if "RM_AcousticSounding" not in gate:
                raise ExpectationFailed("the sounder is not gated by RM_AcousticSounding: %r" % gate)
            if "BasicGravtech" not in pre:
                raise ExpectationFailed("acoustic sounding does not follow BasicGravtech: %r" % pre)

    # ------------------------------------------------------------------ chain 2: settings round trip
    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        for field in sorted(DEFAULTS):
            with t.component("%s_roundtrip" % field, beyond_toggle=True):
                if not _live(t):
                    continue
                try:
                    if not _same(_get(t, field), DEFAULTS[field]):
                        raise ExpectationFailed("%s does not read its shipped default %r: got %r"
                                                % (field, DEFAULTS[field], _get(t, field)))
                    _set(t, field, ALT[field])
                    if not _same(_get(t, field), ALT[field]):
                        raise ExpectationFailed("%s write did not take: wrote %r read %r"
                                                % (field, ALT[field], _get(t, field)))
                finally:
                    _restore(t, field)
                if not _same(_get(t, field), DEFAULTS[field]):
                    raise ExpectationFailed("%s did not restore to %r" % (field, DEFAULTS[field]))
        with t.component("nonexistent_field_fails_loudly", beyond_toggle=True):
            if not _live(t):
                return
            r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="get",
                              field="noSuchField_control")
            if isinstance(r, dict) and r.get("success") is True:
                raise ExpectationFailed("control: a field that does not exist read as success: %r" % (r,))

    # ------------------------------------------------------------------ chain 3: gating (CanPulse via inspect)
    @suite.chain("sounder_gating")
    def sounder_gating(t):
        site = None
        with t.component("unpowered_refuses", beyond_toggle=True):
            if not _live(t):
                return
            site = _site(t)
            if site is None:
                return
            if TXT["nopower"] not in _inspect(t, site[0]):
                raise ExpectationFailed("an unpowered sounder does not say 'No power': %r" % _inspect(t, site[0]))
        sid = state.get("sid")
        with t.component("off_the_ship_refuses", toggle="requireLandedShip"):
            if not _live(t) or sid is None:
                return
            pw = t.bridge_call("jawa/power_net", thing=sid, forcePowerOn=True)
            if isinstance(pw, dict) and pw.get("success") is False:
                _unmeasured(t, "power_net forcePowerOn refused: %r" % (pw,))
                return
            t.wait_ticks(10)
            txt = _inspect(t, sid)
            if TXT["nopower"] in txt:
                _unmeasured(t, "forcePowerOn did not power the sounder (still 'No power')")
                return
            if TXT["notship"] not in txt:
                raise ExpectationFailed("powered, on substructure, but no grav engine on the map: the sounder "
                                        "should refuse with the not-on-ship line: %r" % txt)
        with t.component("ready_on_landed_ship", beyond_toggle=True):
            if not _live(t) or sid is None:
                return
            _engine(t, True)
            t.wait_ticks(10)
            if TXT["ready"] not in _inspect(t, sid):
                raise ExpectationFailed("powered sounder on substructure with a grav engine on the map is not "
                                        "ready: %r" % _inspect(t, sid))
        with t.component("master_off_refuses", toggle="enabled"):
            if not _live(t) or sid is None:
                return
            _set(t, "enabled", False)
            try:
                t.wait_ticks(5)
                if TXT["off"] not in _inspect(t, sid):
                    raise ExpectationFailed("enabled=false but the sounder does not say it is switched off: %r"
                                            % _inspect(t, sid))
            finally:
                _restore(t, "enabled")
            t.wait_ticks(5)
            if TXT["ready"] not in _inspect(t, sid):
                raise ExpectationFailed("did not return to ready after enabled restored: %r" % _inspect(t, sid))
        with t.component("require_ship_off_relaxes", toggle="requireLandedShip"):
            if not _live(t) or sid is None:
                return
            _engine(t, False)
            t.wait_ticks(10)
            if TXT["notship"] not in _inspect(t, sid):
                raise ExpectationFailed("removing the grav engine did not make the sounder refuse (control)")
            _set(t, "requireLandedShip", False)
            try:
                t.wait_ticks(5)
                if TXT["ready"] not in _inspect(t, sid):
                    raise ExpectationFailed("requireLandedShip=false but the engine-less sounder still refuses: %r"
                                            % _inspect(t, sid))
            finally:
                _restore(t, "requireLandedShip")

    # ------------------------------------------------------------------ chain 4: the pulse
    @suite.chain("pulse")
    def pulse(t):
        with t.component("pulse_starts_cooldown_and_sends_letter", toggle="enabled"):
            if not _live(t):
                return
            if _site(t) is None:
                return
            sid = state["sid"]
            t.bridge_call("jawa/power_net", thing=sid, forcePowerOn=True)
            _engine(t, True)
            t.wait_ticks(10)
            if TXT["ready"] not in _inspect(t, sid):
                _unmeasured(t, "could not stage a ready sounder (inspect: %r)" % _inspect(t, sid))
                return
            before = (t.bridge_call("jawa/letter_list") or {})
            n0 = len(before.get("letters") or [])
            t.bridge_call("rimworld/set_god_mode", enabled=True)
            try:
                x, z = t.anchor
                t.bridge_call("rimworld/click_cell", x=x, z=z)
                giz = (t.bridge_call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
                g = next((q for q in giz if (q.get("label") or "").startswith(PULSE_LABEL)), None)
                if g is None:
                    _unmeasured(t, "no %r gizmo among the selected thing's gizmos: %r"
                                % (PULSE_LABEL, [q.get("label") for q in giz]))
                    return
                r = t.bridge_call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
                if isinstance(r, dict) and r.get("success") is False:
                    _unmeasured(t, "execute_gizmo refused: %r" % (r,))
                    return
            finally:
                t.bridge_call("rimworld/set_god_mode", enabled=False)
                t.bridge_call("rimworld/clear_selection")
            t.wait_ticks(10)
            if TXT["cooldown"] not in _inspect(t, sid):
                raise ExpectationFailed("a pulse fired but the sounder shows no cooldown: %r" % _inspect(t, sid))
            after = (t.bridge_call("jawa/letter_list") or {}).get("letters") or []
            if len(after) <= n0 or "Sounding reading" not in " ".join(str(x) for x in after):
                raise ExpectationFailed("a pulse fired but no 'Sounding reading' letter arrived: %r" % after[-3:])
        with t.component("banded_overlay_never_exact", beyond_toggle=True):
            if not _live(t):
                return
            _unmeasured(t, "the overlay's bands live in a non-saved map component with no bridge reader; the "
                           "band-size floor is proven statically (static_checks), the drawing needs eyes")
        with t.component("biome_payload_reads", beyond_toggle=True):
            if not _live(t):
                return
            _unmeasured(t, "payload content needs a map whose biome carries RM_AcousticPayloadExtension (%s) with "
                           "its targets placed; an ordinary quicktest map reads 'nothing unusual'. Follow-up: "
                           "ACOUSTIC_SCANNER_BIOME_SITE_1" % ", ".join(PAYLOAD_BIOMES))
        with t.component("pulse_effects", toggle="pulseEffects"):
            if not _live(t):
                return
            _unmeasured(t, "dust puffs, the thump and the camera shake are visual/audio; pulseEffects is "
                           "round-tripped in settings_roundtrip")

    return suite


try:
    suite = _build_suite()
except ImportError:      # run outside the modcheck path: the static check below needs no game
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
