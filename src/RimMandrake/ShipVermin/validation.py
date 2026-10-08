"""validation.py -- modcheck suite for RimMandrake: Ship Vermin (mandrake.rm.shipvermin).

First north-star script (SHIP_VERMIN_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/ShipVermin.md.

THE MOD ships its own franchise-free cast (SHIPVERMIN_FREE_TIER_BEASTS_1, owner 2026-10-07): RM_Skivvik (hull
leech: CreatureBehaviors breeder comp + pressure/seek/gnaw extensions, soft cap 3, hard cap 12, group tag
"ShipVermin"), RM_Rattagh, RM_Gorrud and RM_Fethrik (fuel spew, RM_FethrikFuelSpew), in Defs/. Also (b)
RM_Alert_ShipVermin, the population alert; (c) RM_CompVerminNest, a generic "nest under the wreckage" comp the
Utinni patch layer wires onto ShipChunk_Mech; (d) Mod Settings and a debug menu (category RMShipVermin) that
exposes the nest's spawn attempt. It depends on no RSW/RUT mod: SWBestiary's own
Patches/ShipVermin/RSW_ShipVermin_CanonCast.xml (FindMod-guarded on this mod's name) gives RSW_Mynock the same
mechanics and swaps the canon kinds into the four nest slots via RM_ShipVerminCanonSwapExtension.

OBSERVATION CHANNEL for the nest: `rimworld/execute_debug_action` path `Actions\\<label>` at the wreck's x,z
(the FloodedCanyon pattern); the action prints `[RM_CompVerminNest] ...` / `[RMShipVerminDebug] ...` lines that
are read from THAT CALL'S OWN `effects.logs`, plus the state itself (a new wild pawn in the rect). An action that
answered success with no tagged line is UNMEASURED, and a path the bridge does not know is UNMEASURED (the label was
never proven live), never FAIL.

CHAINS
  defs_resolve        control reads notFound; the four free species (ThingDef + PawnKindDef) resolve.
  settings_roundtrip  every `public static` field of ShipVerminSettings (8), bool + float, written/restored.
  hull_leech          RM_Skivvik carries the breeder + ShipVermin pressure tag (a control def does not) and is
                      vacuum-proof; with SWBestiary loaded RSW_Mynock carries the same tag (UNMEASURED without it).
  nest_roster         every roster slot resolves; with SWBestiary loaded each free kind carries the canon swap.
  alert               RM_Alert_ShipVermin absent with no hull leech, present with two aboard, gone with
                      `alertEnabled` off.
  wreck_nest          ShipChunk_Mech carries the nest comp; a forced attempt spawns a wild pawn; all slots off
                      spawns nothing; only the rattagh slot on spawns that slot's kind; 12 hull leeches aboard
                      refuses (hard cap); the rate multiplier shortens the next-spawn countdown. UNMEASURED
                      without the Utinni wiring.
  not_driven          breed over 1-2 days, gnaw bites, substructure seek, `wreckSpawningEnabled` stopping the
                      CompTick timer (the debug attempt bypasses that gate), nest save/load, fuel spew grant:
                      UNMEASURED, with reasons.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
SETTINGS = "RimMandrake.ShipVermin.ShipVerminSettings"
CONTROL_ABSENT = "ThingDef/RM_ShipVerminNoSuchDef_ZZ"
PATCHED_DEF = "RM_Skivvik"          # the hull leech: the species carrying the breeder/pressure mechanics
CANON_LEECH = "RSW_Mynock"          # its canon twin, given the same mechanics by SWBestiary's patch
CAST_XML = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_ShipVermin_Cast.xml")
CANON_PATCH = os.path.join(SRC, "RimStarWars", "SWBestiary", "Patches", "ShipVermin", "RSW_ShipVermin_CanonCast.xml")
SLOTS = {"RM_Skivvik": ("spawnSkivvik", "RSW_Mynock"), "RM_Rattagh": ("spawnRattagh", "RSW_Scavrat"),
         "RM_Gorrud": ("spawnGorrud", "RSW_WompRat"), "RM_Fethrik": ("spawnFethrik", "RSW_Zhakka")}
GROUP_TAG = "ShipVermin"
HARD_CAP = 12
WRECK = "ShipChunk_Mech"
ACT_FORCE = "Actions\\Force nest spawn attempt (click wreck)"
ACT_STATE = "Actions\\Report nest state (click wreck)"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
DEFAULTS = {"alertEnabled": True, "wreckSpawningEnabled": True, "wreckSpawnRateMultiplier": 1.0,
            "spawnSkivvik": True, "spawnRattagh": True, "spawnGorrud": True, "spawnFethrik": True,
            "fuelSpewEnabled": True}
SPECIES_TOGGLES = ["spawnSkivvik", "spawnRattagh", "spawnGorrud", "spawnFethrik"]


def settings_fields():
    """{name: type} for every `public static` scalar of ShipVerminSettings, read from the C#."""
    src = open(os.path.join(HERE, "Source", "RM_ShipVerminMod.cs"), encoding="utf-8").read()
    body = src.split("class ShipVerminSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def roster():
    """[defName] the nest may pick, parsed from NestSpeciesRoster in the C#."""
    src = open(os.path.join(HERE, "Source", "RM_ShipVerminMod.cs"), encoding="utf-8").read()
    blk = src.split("NestSpeciesRoster =", 1)[1].split("};", 1)[0]
    return re.findall(r'\("(\w+)",\s*\(\)\s*=>', blk)


def _strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def patch_expectations():
    """{'classes': [class names], 'tag': str, 'hard': int} read from RM_Skivvik's own ThingDef."""
    root = ET.parse(CAST_XML).getroot()
    td = [d for d in root.findall("ThingDef") if d.findtext("defName") == PATCHED_DEF]
    if not td:
        return {"classes": [], "tag": "", "hard": 0}
    p = td[0]
    classes = [e.get("Class") for e in p.iter("li") if e.get("Class", "").startswith("RimMandrake.")]
    return {"classes": classes, "tag": (p.findtext(".//populationGroupTag") or "").strip(),
            "hard": int(p.findtext(".//populationHardCap") or 0)}


def mechanics_numbers(elem):
    """{class: [(tag, text)...]} for every RimMandrake.* li under elem, for a same-tuning comparison."""
    out = {}
    for e in elem.iter("li"):
        c = e.get("Class", "")
        if c.startswith("RimMandrake.CreatureBehaviors."):
            out[c] = sorted((x.tag, (x.text or "").strip()) for x in e.iter() if x is not e and len(x) == 0)
    return out


def franchise_free_checks():
    """SHIPVERMIN_FREE_TIER_BEASTS_1 A1, statically: no RSW/RUT dependency, no RSW_ name outside comments."""
    bad = []
    about = ET.parse(os.path.join(HERE, "About", "About.xml")).getroot()
    deps = [e.text.strip() for e in about.iter("packageId") if e.text] + \
           [e.text.strip() for e in about.iter("li") if e.text and "." in e.text and not e.text.strip().startswith("1.")]
    for d in deps:
        if d.startswith("mandrake.rsw.") or d.startswith("mandrake.rut."):
            bad.append("About.xml names franchise mod %s (RM tier must not depend on it)" % d)
    probe = 0
    for dp, _d, files in os.walk(HERE):
        if "__pycache__" in dp or os.sep + "obj" in dp or os.sep + "bin" in dp or os.sep + "About" in dp:
            continue
        for fn in files:
            path = os.path.join(dp, fn)
            if fn.endswith(".xml"):
                text = _strip_xml_comments(open(path, encoding="utf-8").read())
            elif fn.endswith(".cs"):
                text = re.sub(r"//[^\n]*", "", open(path, encoding="utf-8").read())
            else:
                continue
            probe += 1
            for m in re.findall(r"\b(RSW_\w+|RUT_\w+|RimMandrake\.StarWars\.\w+|RimMandrake\.Utinni\.\w+)", text):
                bad.append("%s names franchise content %s" % (os.path.relpath(path, HERE), m))
    if probe < 3:
        bad.append("franchise sweep read %d files (sanity probe: expected the Defs + Source files)" % probe)
    return bad


def canon_patch_checks(mod_name):
    """The SWBestiary patch is guarded on this mod's NAME, swaps every slot, and gives the canon leech
    exactly RM_Skivvik's mechanics numbers."""
    bad = []
    if not os.path.isfile(CANON_PATCH):
        return ["canon cast patch missing: %s" % CANON_PATCH]
    root = ET.parse(CANON_PATCH).getroot()
    guards = [op for op in root.iter("Operation") if op.get("Class") == "PatchOperationFindMod"]
    names = [li.text.strip() for op in guards for li in op.findall("./mods/li") if li.text]
    if mod_name not in names:
        bad.append("canon patch FindMod guard %r does not name this mod (%r): it would never apply" % (names, mod_name))
    text = open(CANON_PATCH, encoding="utf-8").read()
    for free, (_toggle, canon) in sorted(SLOTS.items()):
        if not re.search(r'defName="%s"\]/modExtensions</xpath>\s*<value>\s*<li Class="RimMandrake\.ShipVermin\.'
                         r'RM_ShipVerminCanonSwapExtension">\s*<kind>%s</kind>' % (free, canon), text):
            bad.append("canon patch does not swap %s -> %s" % (free, canon))
    cast = [d for d in ET.parse(CAST_XML).getroot().findall("ThingDef") if d.findtext("defName") == PATCHED_DEF]
    if cast and mechanics_numbers(cast[0]) != mechanics_numbers(root):
        bad.append("RSW_Mynock's patched mechanics differ from RM_Skivvik's (same-tuning rule)")
    return bad


def static_checks():
    bad = []
    fields = settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    if sorted(fields) != sorted(DEFAULTS):
        bad.append("settings fields changed: %s (update DEFAULTS and the walk)" % sorted(fields))
    src = open(os.path.join(HERE, "Source", "RM_ShipVerminMod.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RM_ShipVermin.csproj"), encoding="utf-8").read()
    for dp, _d, files in os.walk(os.path.join(HERE, "Source")):
        if os.sep + "obj" in dp or os.sep + "bin" in dp or os.sep + "SelfTest" in dp:   # the offline fuzz project has its own csproj
            continue
        for fn in files:
            if fn.endswith(".cs"):
                rel = os.path.relpath(os.path.join(dp, fn), os.path.join(HERE, "Source")).replace("/", "\\")
                if 'Compile Include="%s"' % rel not in proj:
                    bad.append("%s is not in the csproj (compiles into nothing)" % rel)
    r = roster()
    if sorted(r) != sorted(SLOTS):
        bad.append("nest roster probe read %r (sanity probe: expected the four free slots %s)" % (r, sorted(SLOTS)))
    cast = ET.parse(CAST_XML).getroot()
    for kind in SLOTS:
        for dt in ("ThingDef", "PawnKindDef"):
            if not [d for d in cast.findall(dt) if d.findtext("defName") == kind]:
                bad.append("%s/%s is not defined in %s" % (dt, kind, os.path.basename(CAST_XML)))
    bad += franchise_free_checks()
    bad += canon_patch_checks((ET.parse(os.path.join(HERE, "About", "About.xml")).getroot().findtext("name") or "").strip())
    for sp in SPECIES_TOGGLES:
        if sp not in src:
            bad.append("species toggle %s missing from the C#" % sp)
    px = patch_expectations()
    if len(px["classes"]) < 4:
        bad.append("%s carries %d RimMandrake classes (expected breeder + 3 extensions)" % (PATCHED_DEF, len(px["classes"])))
    if px["tag"] != GROUP_TAG or px["hard"] != HARD_CAP:
        bad.append("%s group tag/hard cap now %r/%r, script expects %s/%d" % (PATCHED_DEF, px["tag"], px["hard"], GROUP_TAG, HARD_CAP))
    alert = open(os.path.join(HERE, "Source", "RM_Alert_ShipVermin.cs"), encoding="utf-8").read()
    if '"%s"' % GROUP_TAG not in alert or "alertEnabled" not in alert:
        bad.append("RM_Alert_ShipVermin no longer uses the %s tag / alertEnabled gate" % GROUP_TAG)
    nest = open(os.path.join(HERE, "Source", "RM_CompProperties_VerminNest.cs"), encoding="utf-8").read()
    if '"%s"' % GROUP_TAG not in nest or "populationHardCap = %d" % HARD_CAP not in nest:
        bad.append("nest comp defaults no longer share the %s/%d pool with the hull leech's breeder" % (GROUP_TAG, HARD_CAP))
    dbg = open(os.path.join(HERE, "Source", "Debug", "RM_ShipVerminDebugActions.cs"), encoding="utf-8").read()
    for label in ("Force nest spawn attempt (click wreck)", "Report nest state (click wreck)"):
        if label not in dbg:
            bad.append("debug action label %r gone: the nest chain's path is stale" % label)
    wire = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "WreckVerminNest_ShipChunk.xml")
    if os.path.isfile(wire) and WRECK not in open(wire, encoding="utf-8").read():
        bad.append("the Utinni wiring patch no longer targets %s" % WRECK)
    if not os.path.isfile(os.path.join(SRC, "..", "design", "validation_walks", "RimMandrake", "ShipVermin.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite("ShipVermin")
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

    def _put(t, field, value):
        if t.session is None:
            return
        if not _raw(t, "set", field, value).get("success"):
            raise ExpectationFailed("could not set %s=%s" % (field, value))

    def _restore(t, *fields):
        if t.session is None:
            return
        for field in fields:
            try:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                               value=str(DEFAULTS[field]))
            except Exception as ex:
                print("[shipvermin] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    def _defs(t, names, fields="defName", deep=False):
        if deep:
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields=fields, limit=40, deep=True)
        else:
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields=fields, limit=40)
        if _live(t) and (not isinstance(r, dict) or r.get("success") is False):
            raise ExpectationFailed("get_defs failed: %r" % r)
        return r or {}

    def _row_fields(r, name):
        for d in (r.get("defs") or []):
            if d.get("defName") == name:
                return d.get("fields") or {}
        return None

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("free_cast_resolves", beyond_toggle=True):
            names = ["%s/%s" % (dt, k) for k in sorted(SLOTS) for dt in ("ThingDef", "PawnKindDef")]
            r = _defs(t, names)
            if _live(t) and (r.get("notFound") or int(r.get("foundCount", 0)) != len(names)):
                raise ExpectationFailed("the free cast did not fully resolve: %r" % (r.get("notFound"),))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                raise ExpectationFailed("settings probe found no field (blind regex)")
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

    @suite.chain("hull_leech")
    def hull_leech(t):
        with t.component("breeder_and_pressure_extension_on_the_hull_leech", beyond_toggle=True):
            r = _defs(t, ["ThingDef/%s" % PATCHED_DEF, "ThingDef/Rat"], fields="comps,modExtensions", deep=True)
            if not _live(t):
                return
            mine, ctl = _row_fields(r, PATCHED_DEF), _row_fields(r, "Rat")
            if mine is None or ctl is None:
                raise ExpectationFailed("could not read %s / Rat comps+modExtensions: %r" % (PATCHED_DEF, r.get("notFound")))
            ext = mine.get("modExtensions")
            if not isinstance(ext, list) or not ext:
                raise ExpectationFailed("%s carries no modExtensions (the CreatureBehaviors types failed to resolve?)"
                                        % PATCHED_DEF)
            blob, cblob = json.dumps(ext, default=str), json.dumps(ctl.get("modExtensions"), default=str)
            if GROUP_TAG in cblob:
                _unmeasured(t, "the control def (Rat) also reads %s: the probe cannot separate patched from unpatched" % GROUP_TAG)
                return
            if GROUP_TAG not in blob and "VerminPressureExtension" not in blob:
                raise ExpectationFailed("%s modExtensions carry neither the %s tag nor the pressure extension: %s"
                                        % (PATCHED_DEF, GROUP_TAG, blob[:300]))
            cblob2 = json.dumps(mine.get("comps"), default=str)
            if "VerminBreeder" not in cblob2 and not (isinstance(mine.get("comps"), list) and mine.get("comps")
                                                      and not all(isinstance(c, dict) for c in mine.get("comps"))):
                raise ExpectationFailed("%s carries no VerminBreeder comp: %s" % (PATCHED_DEF, cblob2[:300]))
        with t.component("hull_leech_is_vacuum_proof", beyond_toggle=True):
            r = _defs(t, ["ThingDef/%s" % PATCHED_DEF], fields="statBases", deep=True)
            if _live(t):
                sb = (_row_fields(r, PATCHED_DEF) or {}).get("statBases")
                if not isinstance(sb, list) or not sb or not all(isinstance(x, dict) for x in sb):
                    _unmeasured(t, "statBases not readable as rows (%r): the vacuum stats cannot be asked" % (sb,))
                    return
                blob = json.dumps(sb, default=str)
                if "VacuumResistance" not in blob:
                    raise ExpectationFailed("%s statBases carry no VacuumResistance (it must live outside a hull): %s"
                                            % (PATCHED_DEF, blob[:300]))
        with t.component("canon_leech_carries_the_same_mechanics", beyond_toggle=True):
            r = _defs(t, ["ThingDef/%s" % CANON_LEECH], fields="modExtensions", deep=True)
            if _live(t):
                if CANON_LEECH in [x.split("/")[-1] for x in (r.get("notFound") or [])]:
                    _unmeasured(t, "%s not loaded (SWBestiary absent on this list): the canon slot cannot be asked" % CANON_LEECH)
                    return
                blob = json.dumps((_row_fields(r, CANON_LEECH) or {}).get("modExtensions"), default=str)
                if GROUP_TAG not in blob and "VerminPressureExtension" not in blob:
                    raise ExpectationFailed("SWBestiary is loaded but %s carries no %s pressure extension: the "
                                            "FindMod-guarded canon patch did not apply: %s" % (CANON_LEECH, GROUP_TAG, blob[:300]))

    @suite.chain("nest_roster")
    def nest_roster(t):
        names = roster()
        with t.component("every_free_slot_resolves", beyond_toggle=True):
            r = _defs(t, ["PawnKindDef/%s" % n for n in names])
            if _live(t):
                gone = [x.split("/")[-1] for x in (r.get("notFound") or [])]
                if gone:
                    raise ExpectationFailed("nest roster slots do not resolve (the nest cannot fill them): %s" % gone)
        with t.component("canon_kinds_swap_into_the_slots", beyond_toggle=True):
            canon = ["PawnKindDef/%s" % SLOTS[n][1] for n in names]
            r = _defs(t, canon)
            if _live(t):
                if int(r.get("foundCount", 0)) == 0:
                    _unmeasured(t, "no canon kind loaded (SWBestiary absent): the swap cannot be asked")
                    return
                r2 = _defs(t, ["PawnKindDef/%s" % n for n in names], fields="modExtensions", deep=True)
                missing = []
                for n in names:
                    blob = json.dumps((_row_fields(r2, n) or {}).get("modExtensions"), default=str)
                    if "CanonSwap" not in blob and SLOTS[n][1] not in blob:
                        missing.append(n)
                if missing:
                    raise ExpectationFailed("SWBestiary is loaded but these free kinds carry no canon swap: %s" % missing)

    @suite.chain("alert")
    def alert(t):
        def _listed(t):
            r = t.bridge_call("jawa/alerts_list")
            if not _live(t):
                return None
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("alerts_list failed: %r" % r)
            return [a for a in (r.get("alerts") or []) if "RM_Alert_ShipVermin" in str(a.get("type"))]

        with t.component("absent_with_no_leech_present_with_leeches", toggle="alertEnabled"):
            t.clear_area(size=24)
            if _live(t):
                before = _listed(t)
                if before:
                    _unmeasured(t, "an RM_Alert_ShipVermin is already active on this map (vermin elsewhere): no clean baseline")
                    return
                x, z = t.anchor
                r = t.bridge_call("jawa/spawn_pawn", kindDef=PATCHED_DEF, x=x, z=z, faction="none", count=2)
                if not (r or {}).get("pawns"):
                    _unmeasured(t, "could not spawn %s: %r" % (PATCHED_DEF, r))
                    return
                t.wait_ticks(320)      # the population count recomputes every 250 ticks
                if not _listed(t):
                    raise ExpectationFailed("two hull leeches aboard and no RM_Alert_ShipVermin after 320 ticks")
        with t.component("alert_off_hides_it", toggle="alertEnabled"):
            if _live(t):
                _put(t, "alertEnabled", False)
                try:
                    t.wait_ticks(60)
                    if _listed(t):
                        raise ExpectationFailed("alertEnabled=false but RM_Alert_ShipVermin is still listed (toggle dead)")
                finally:
                    _restore(t, "alertEnabled")

    def _log_texts(r):
        out = []
        for row in ((r or {}).get("effects") or {}).get("logs") or []:
            out.append(row if isinstance(row, str) else str(row.get("text") or row.get("message") or row.get("msg") or ""))
        return out

    def _act(t, path, x, z, tag):
        """Run a debug action at (x, z); return its tagged log lines, or None (and UNMEASURED) when it cannot be read."""
        r = t.bridge_call("rimworld/execute_debug_action", path=path, x=x, z=z)
        if not _live(t):
            return None
        if not isinstance(r, dict) or r.get("success") is not True:
            _unmeasured(t, "execute_debug_action %r did not succeed (label never proven live): %s" % (path, str(r)[:200]))
            return None
        lines = [l for l in _log_texts(r) if tag in l]
        if not lines:
            _unmeasured(t, "debug action %s answered success but logged no %s line (logCount=%s): check Player.log for "
                           "'Reached max messages limit' before blaming the mod" % (path, tag, (r.get("effects") or {}).get("logCount")))
            return None
        return lines

    def _rect(t, r=8):
        x, z = t.anchor
        return "%d,%d,%d,%d" % (x - r, z - r, 2 * r + 1, 2 * r + 1)

    def _pawns(t):
        r = t.bridge_call("jawa/list_pawns", rect=_rect(t), limit=80)
        if not _live(t):
            return []
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("list_pawns unreadable: %r" % r)
        return list(r.get("pawns") or [])

    @suite.chain("wreck_nest")
    def wreck_nest(t):
        site = {}
        with t.component("wreck_carries_the_nest_comp", beyond_toggle=True):
            r = _defs(t, ["ThingDef/%s" % WRECK], fields="comps", deep=True)
            if _live(t):
                if r.get("notFound"):
                    _unmeasured(t, "%s is not loaded (Odyssey DLC / Utinni wiring absent)" % WRECK)
                    return
                comps = (_row_fields(r, WRECK) or {}).get("comps")
                if not isinstance(comps, list) or not comps:
                    _unmeasured(t, "comps for %s unreadable (%r)" % (WRECK, comps))
                    return
                if all(not isinstance(c, dict) for c in comps):
                    blob = json.dumps(comps, default=str)
                else:
                    blob = json.dumps(comps, default=str)
                if "VerminNest" not in blob:
                    _unmeasured(t, "%s carries no VerminNest comp in this mod list (the wiring lives in mandrake.rut.patches, "
                                   "which this tier may not load): %s" % (WRECK, blob[:160]))
                    return
                site["ok"] = True
        with t.component("forced_attempt_spawns_a_wild_pawn", beyond_toggle=True):
            if _live(t) and site.get("ok"):
                t.clear_area(size=24)
                t.spawn(WRECK, count=1, at="point")
                x, z = t.anchor
                site["xz"] = (x, z)
                n0 = len(_pawns(t))
                lines = _act(t, ACT_FORCE, x, z, "[RM_CompVerminNest]")
                if lines is not None:
                    if not any("SPAWNED" in l for l in lines):
                        raise ExpectationFailed("forced attempt on a clear map did not spawn: %s" % lines[:2])
                    if len(_pawns(t)) <= n0:
                        raise ExpectationFailed("the log says SPAWNED but no new pawn is in the rect (%d -> %d)" % (n0, len(_pawns(t))))
        with t.component("all_species_off_spawns_nothing", toggle="spawnRattagh"):
            if _live(t) and site.get("xz"):
                x, z = site["xz"]
                for f in SPECIES_TOGGLES:
                    _put(t, f, False)
                try:
                    n0 = len(_pawns(t))
                    lines = _act(t, ACT_FORCE, x, z, "[RM_CompVerminNest]")
                    if lines is not None:
                        if any("SPAWNED" in l for l in lines) or len(_pawns(t)) > n0:
                            raise ExpectationFailed("every species toggle is off yet the nest spawned: %s" % lines[:2])
                        if not any("PickEnabledNestSpecies" in l for l in lines):
                            raise ExpectationFailed("refused for the wrong reason (expected the empty-roster branch): %s" % lines[:2])
                finally:
                    _restore(t, *SPECIES_TOGGLES)
        with t.component("only_rattagh_slot_on_spawns_that_slot", toggle="spawnRattagh"):
            if _live(t) and site.get("xz"):
                x, z = site["xz"]
                for f in SPECIES_TOGGLES:
                    if f != "spawnRattagh":
                        _put(t, f, False)
                try:
                    lines = _act(t, ACT_FORCE, x, z, "[RM_CompVerminNest]")
                    if lines is not None:
                        spawned = [l for l in lines if "SPAWNED" in l]
                        if not spawned:
                            raise ExpectationFailed("only the rattagh slot enabled and the nest did not spawn: %s" % lines[:2])
                        ok = ("SPAWNED RM_Rattagh ", "SPAWNED %s " % SLOTS["RM_Rattagh"][1])
                        if not any(o in spawned[0] for o in ok):
                            raise ExpectationFailed("only spawnRattagh is on yet the spawn was not that slot's kind: %s" % spawned[0])
                finally:
                    _restore(t, *SPECIES_TOGGLES)
        with t.component("hard_cap_refuses_a_spawn", beyond_toggle=True):
            if _live(t) and site.get("xz"):
                x, z = site["xz"]
                r = t.bridge_call("jawa/spawn_pawn", kindDef=PATCHED_DEF, x=x + 3, z=z, faction="none", count=HARD_CAP)
                if len((r or {}).get("pawns") or []) < HARD_CAP:
                    _unmeasured(t, "could not spawn %d %s to fill the pool: %s" % (HARD_CAP, PATCHED_DEF, str(r)[:160]))
                else:
                    t.wait_ticks(320)
                    lines = _act(t, ACT_FORCE, x, z, "[RM_CompVerminNest]")
                    if lines is not None and not any("population cap reached" in l for l in lines):
                        raise ExpectationFailed("%d hull leeches aboard and the nest did not refuse on the cap: %s" % (HARD_CAP, lines[:2]))
        with t.component("rate_multiplier_shortens_next_spawn", toggle="wreckSpawnRateMultiplier"):
            if _live(t) and site.get("ok"):
                def _ticks_left(mult):
                    _put(t, "wreckSpawnRateMultiplier", mult)
                    try:
                        t.clear_area(size=24)
                        t.spawn(WRECK, count=1, at="point")
                        x, z = t.anchor
                        lines = _act(t, ACT_STATE, x, z, "ticksUntilNextSpawn=")
                        if lines is None:
                            return None
                        m = re.search(r"ticksUntilNextSpawn=(-?\d+)", lines[0])
                        return int(m.group(1)) if m else None
                    finally:
                        _restore(t, "wreckSpawnRateMultiplier")
                slow = _ticks_left(1.0)
                fast = _ticks_left(3.0) if slow is not None else None
                if slow is not None and fast is not None:
                    # default interval 2-4 days / 3 = 0.67-1.33 days is always below 2 days (the shortest 1x draw)
                    if not fast < slow:
                        raise ExpectationFailed("3x rate left %d ticks until the next spawn vs %d at 1x" % (fast, slow))
                elif t.upstream_failed is False:
                    _unmeasured(t, "could not read ticksUntilNextSpawn from the state action")

    @suite.chain("not_driven")
    def not_driven(t):
        for name, toggle, why in (
            ("hull_leech_breeds_under_the_soft_cap", None,
             "RM_CompVerminBreeder spawns every 1-2 days (CreatureBehaviors); proving it needs game days of ticks and the "
             "pressure curve read at 3 / 12 hull leeches"),
            ("hull_leech_gnaws_conduits_lights_and_floor", None,
             "RM_GnawTargetExtension bites every 240 ticks but the seek chance is 0.01-0.2 per check; a deterministic proof "
             "needs a forced-job tool for the gnaw giver, not a wait"),
            ("hull_leech_seeks_the_substructure_hull", None,
             "seekSubstructure drift-to-the-hull needs a landed gravship with Substructure and vacuum on the map"),
            ("wreck_spawning_off_stops_the_timer", "wreckSpawningEnabled",
             "RM_CompVerminNest.CompTick is the only place that reads wreckSpawningEnabled (AttemptSpawn, the debug path, "
             "does not), so the effect needs the 2-4 day interval to elapse; a tick-fast forcing tool is owed"),
            ("nest_countdown_survives_save_load", None,
             "nextSpawnTick is Scribed; proving it needs a save and reload with the debug state read before and after"),
            ("fethrik_gains_its_fuel_spew", "fuelSpewEnabled",
             "RM_CompInnateAbility grants RM_FethrikFuelSpew on a rare tick; needs a spawned fethrik, ~250 ticks and an "
             "abilities read on the pawn (no such read is wired here yet)"),
        ):
            with t.component(name, toggle=toggle, beyond_toggle=toggle is None):
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
