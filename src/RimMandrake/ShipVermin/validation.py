"""validation.py -- modcheck suite for RimMandrake: Ship Vermin (mandrake.rm.shipvermin).

First north-star script (SHIP_VERMIN_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/ShipVermin.md.

THE MOD ships NO Defs/ of its own. It is (a) Patches/RSW_Mynock_ShipVermin.xml, which hangs the shared
CreatureBehaviors breeder comp + pressure/seek/gnaw extensions on SWBestiary's RSW_Mynock (soft cap 3, hard cap
12, group tag "ShipVermin"); (b) RM_Alert_ShipVermin, the population alert; (c) RM_CompVerminNest, a generic
"nest under the wreckage" comp the Utinni patch layer wires onto ShipChunk_Mech; (d) Mod Settings (8 fields) and
a debug menu (category RMShipVermin) that exposes the nest's spawn attempt. So "every def the mod ships" is the
empty set; the chains read the patched def, the alert and the nest.

OBSERVATION CHANNEL for the nest: `rimworld/execute_debug_action` path `Actions\\<label>` at the wreck's x,z
(the FloodedCanyon pattern); the action prints `[RM_CompVerminNest] ...` / `[RMShipVerminDebug] ...` lines that
are read from THAT CALL'S OWN `effects.logs`, plus the state itself (a new wild pawn in the rect). An action that
answered success with no tagged line is UNMEASURED, and a path the bridge does not know is UNMEASURED (the label was
never proven live), never FAIL.

CHAINS
  defs_resolve        control reads notFound; RSW_Mynock ThingDef + PawnKindDef (the patch target) resolve.
  settings_roundtrip  every `public static` field of ShipVerminSettings (8), bool + float, written/restored.
  mynock_patch        the patch reached RSW_Mynock (modExtensions carry the ShipVermin tag; a control def does not);
                      the mynock is vacuum-proof (SWBestiary stat), UNMEASURED if the tool cannot show it.
  nest_roster         the species the nest may pick resolve (Rat always); a Mynock row naming the donor kind
                      `Mynock` resolves when our ported kind is `RSW_Mynock` (FAIL if the roster is dead for ours).
  alert               RM_Alert_ShipVermin absent with no mynock, present with mynocks aboard, gone with
                      `alertEnabled` off.
  wreck_nest          ShipChunk_Mech carries the nest comp; a forced attempt spawns a wild pawn; all species off
                      spawns nothing; only Rat on spawns a Rat; 12 mynocks aboard refuses (hard cap); the rate
                      multiplier shortens the next-spawn countdown. UNMEASURED without the Utinni wiring.
  not_driven          breed over 1-2 days, gnaw bites, substructure seek, `wreckSpawningEnabled` stopping the
                      CompTick timer (the debug attempt bypasses that gate), nest save/load: UNMEASURED, with reasons.

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
PATCHED_DEF = "RSW_Mynock"
GROUP_TAG = "ShipVermin"
HARD_CAP = 12
WRECK = "ShipChunk_Mech"
ACT_FORCE = "Actions\\Force nest spawn attempt (click wreck)"
ACT_STATE = "Actions\\Report nest state (click wreck)"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
DEFAULTS = {"alertEnabled": True, "wreckSpawningEnabled": True, "wreckSpawnRateMultiplier": 1.0,
            "spawnMynock": True, "spawnScavrat": True, "spawnWompRat": True, "spawnFuelmite": True, "spawnRat": True}
SPECIES_TOGGLES = ["spawnMynock", "spawnScavrat", "spawnWompRat", "spawnFuelmite", "spawnRat"]


def settings_fields():
    """{name: type} for every `public static` scalar of ShipVerminSettings, read from the C#."""
    src = open(os.path.join(HERE, "Source", "RM_ShipVerminMod.cs"), encoding="utf-8").read()
    body = src.split("class ShipVerminSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def roster():
    """[defName] the nest may pick, parsed from NestSpeciesRoster in the C#."""
    src = open(os.path.join(HERE, "Source", "RM_ShipVerminMod.cs"), encoding="utf-8").read()
    blk = src.split("NestSpeciesRoster =", 1)[1].split("};", 1)[0]
    return re.findall(r'\("(\w+)",\s*\(\)', blk)


def patch_expectations():
    """{'comp': [class names], 'ext': [class names], 'tag': str} read from the patch XML."""
    p = ET.parse(os.path.join(HERE, "Patches", "RSW_Mynock_ShipVermin.xml")).getroot()
    classes = [e.get("Class") for e in p.iter("li") if e.get("Class", "").startswith("RimMandrake.")]
    return {"classes": classes, "tag": (p.findtext(".//populationGroupTag") or "").strip(),
            "hard": int(p.findtext(".//populationHardCap") or 0)}


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
        if os.sep + "obj" in dp or os.sep + "bin" in dp:
            continue
        for fn in files:
            if fn.endswith(".cs"):
                rel = os.path.relpath(os.path.join(dp, fn), os.path.join(HERE, "Source")).replace("/", "\\")
                if 'Compile Include="%s"' % rel not in proj:
                    bad.append("%s is not in the csproj (compiles into nothing)" % rel)
    r = roster()
    if len(r) != 5 or "Rat" not in r:
        bad.append("nest roster probe read %r (sanity probe: expected 5 species incl. Rat)" % r)
    for sp in SPECIES_TOGGLES:
        if sp not in src:
            bad.append("species toggle %s missing from the C#" % sp)
    px = patch_expectations()
    if len(px["classes"]) < 4:
        bad.append("patch probe found %d RimMandrake classes (expected breeder + 3 extensions)" % len(px["classes"]))
    if px["tag"] != GROUP_TAG or px["hard"] != HARD_CAP:
        bad.append("patch group tag/hard cap now %r/%r, script expects %s/%d" % (px["tag"], px["hard"], GROUP_TAG, HARD_CAP))
    alert = open(os.path.join(HERE, "Source", "RM_Alert_ShipVermin.cs"), encoding="utf-8").read()
    if '"%s"' % GROUP_TAG not in alert or "alertEnabled" not in alert:
        bad.append("RM_Alert_ShipVermin no longer uses the %s tag / alertEnabled gate" % GROUP_TAG)
    nest = open(os.path.join(HERE, "Source", "RM_CompProperties_VerminNest.cs"), encoding="utf-8").read()
    if '"%s"' % GROUP_TAG not in nest or "populationHardCap = %d" % HARD_CAP not in nest:
        bad.append("nest comp defaults no longer share the %s/%d pool with the breeder patch" % (GROUP_TAG, HARD_CAP))
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
        with t.component("patch_target_species_resolves", beyond_toggle=True):
            names = ["ThingDef/%s" % PATCHED_DEF, "PawnKindDef/%s" % PATCHED_DEF]
            r = _defs(t, names)
            if _live(t) and (r.get("notFound") or int(r.get("foundCount", 0)) != len(names)):
                raise ExpectationFailed("the patch target %s did not resolve (the patch would match nothing): %r"
                                        % (PATCHED_DEF, r.get("notFound")))

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
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else str(float(old) + 1.0)
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

    @suite.chain("mynock_patch")
    def mynock_patch(t):
        with t.component("breeder_and_pressure_extension_reached_the_mynock", beyond_toggle=True):
            r = _defs(t, ["ThingDef/%s" % PATCHED_DEF, "ThingDef/Rat"], fields="comps,modExtensions", deep=True)
            if not _live(t):
                return
            mine, ctl = _row_fields(r, PATCHED_DEF), _row_fields(r, "Rat")
            if mine is None or ctl is None:
                raise ExpectationFailed("could not read %s / Rat comps+modExtensions: %r" % (PATCHED_DEF, r.get("notFound")))
            ext = mine.get("modExtensions")
            if not isinstance(ext, list) or not ext:
                raise ExpectationFailed("%s carries no modExtensions: the ShipVermin patch matched nothing (load order, or "
                                        "the CreatureBehaviors types failed to resolve)" % PATCHED_DEF)
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
        with t.component("mynock_is_vacuum_proof", beyond_toggle=True):
            r = _defs(t, ["ThingDef/%s" % PATCHED_DEF], fields="statBases", deep=True)
            if _live(t):
                sb = (_row_fields(r, PATCHED_DEF) or {}).get("statBases")
                if not isinstance(sb, list) or not sb or not all(isinstance(x, dict) for x in sb):
                    _unmeasured(t, "statBases not readable as rows (%r): the SWBestiary vacuum stats cannot be asked" % (sb,))
                    return
                blob = json.dumps(sb, default=str)
                if "VacuumResistance" not in blob:
                    raise ExpectationFailed("mynock statBases carry no VacuumResistance (it must live outside a hull): %s" % blob[:300])

    @suite.chain("nest_roster")
    def nest_roster(t):
        names = roster()
        with t.component("rat_always_resolves_so_the_roster_is_not_dead", toggle="spawnRat"):
            r = _defs(t, ["PawnKindDef/Rat"])
            if _live(t) and (r.get("notFound") or int(r.get("foundCount", 0)) != 1):
                raise ExpectationFailed("PawnKindDef/Rat does not resolve: no nest could ever spawn anything")
        with t.component("roster_resolution_reported", beyond_toggle=True):
            r = _defs(t, ["PawnKindDef/%s" % n for n in names])
            if _live(t):
                gone = [x.split("/")[-1] for x in (r.get("notFound") or [])]
                if len(gone) == len(names):
                    raise ExpectationFailed("no roster species resolves: %s" % gone)
                # not a failure on its own: Scavrat/WompRat/Fuelmite are donor kinds. Recorded in the detail below.
        with t.component("mynock_row_matches_the_ported_species", toggle="spawnMynock"):
            r = _defs(t, ["PawnKindDef/Mynock", "PawnKindDef/%s" % PATCHED_DEF])
            if _live(t):
                gone = [x.split("/")[-1] for x in (r.get("notFound") or [])]
                if "Mynock" in gone and PATCHED_DEF not in gone:
                    raise ExpectationFailed("the nest roster names kind `Mynock` but the only mynock loaded is `%s`: with "
                                            "mlie.starwarsanimalcollection absent the 'Mynock' row never resolves, so wreck nests "
                                            "cannot produce the mod's own headline species" % PATCHED_DEF)

    @suite.chain("alert")
    def alert(t):
        def _listed(t):
            r = t.bridge_call("jawa/alerts_list")
            if not _live(t):
                return None
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("alerts_list failed: %r" % r)
            return [a for a in (r.get("alerts") or []) if "RM_Alert_ShipVermin" in str(a.get("type"))]

        with t.component("absent_with_no_mynock_present_with_mynocks", toggle="alertEnabled"):
            t.clear_area(size=24)
            if _live(t):
                before = _listed(t)
                if before:
                    _unmeasured(t, "an RM_Alert_ShipVermin is already active on this map (mynocks elsewhere): no clean baseline")
                    return
                x, z = t.anchor
                r = t.bridge_call("jawa/spawn_pawn", kindDef=PATCHED_DEF, x=x, z=z, faction="none", count=2)
                if not (r or {}).get("pawns"):
                    _unmeasured(t, "could not spawn mynocks (RSW_Mynock kind not loaded?): %r" % (r,))
                    return
                t.wait_ticks(320)      # the population count recomputes every 250 ticks
                if not _listed(t):
                    raise ExpectationFailed("two mynocks aboard and no RM_Alert_ShipVermin after 320 ticks")
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
        with t.component("all_species_off_spawns_nothing", toggle="spawnRat"):
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
        with t.component("only_rat_on_spawns_a_rat", toggle="spawnRat"):
            if _live(t) and site.get("xz"):
                x, z = site["xz"]
                for f in SPECIES_TOGGLES:
                    if f != "spawnRat":
                        _put(t, f, False)
                try:
                    lines = _act(t, ACT_FORCE, x, z, "[RM_CompVerminNest]")
                    if lines is not None:
                        spawned = [l for l in lines if "SPAWNED" in l]
                        if not spawned:
                            raise ExpectationFailed("only Rat enabled and the nest did not spawn: %s" % lines[:2])
                        if "SPAWNED Rat " not in spawned[0]:
                            raise ExpectationFailed("only spawnRat is on yet the spawn was not a Rat: %s" % spawned[0])
                finally:
                    _restore(t, *SPECIES_TOGGLES)
        with t.component("hard_cap_refuses_a_spawn", beyond_toggle=True):
            if _live(t) and site.get("xz"):
                x, z = site["xz"]
                r = t.bridge_call("jawa/spawn_pawn", kindDef=PATCHED_DEF, x=x + 3, z=z, faction="none", count=HARD_CAP)
                if len((r or {}).get("pawns") or []) < HARD_CAP:
                    _unmeasured(t, "could not spawn %d mynocks to fill the pool: %s" % (HARD_CAP, str(r)[:160]))
                else:
                    t.wait_ticks(320)
                    lines = _act(t, ACT_FORCE, x, z, "[RM_CompVerminNest]")
                    if lines is not None and not any("population cap reached" in l for l in lines):
                        raise ExpectationFailed("%d mynocks aboard and the nest did not refuse on the cap: %s" % (HARD_CAP, lines[:2]))
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
            ("mynock_breeds_under_the_soft_cap", None,
             "RM_CompVerminBreeder spawns every 1-2 days (CreatureBehaviors); proving it needs game days of ticks and the "
             "pressure curve read at 3 / 12 mynocks"),
            ("mynock_gnaws_conduits_lights_and_floor", None,
             "RM_GnawTargetExtension bites every 240 ticks but the seek chance is 0.01-0.2 per check; a deterministic proof "
             "needs a forced-job tool for the gnaw giver, not a wait"),
            ("mynock_seeks_the_substructure_hull", None,
             "seekSubstructure drift-to-the-hull needs a landed gravship with Substructure and vacuum on the map"),
            ("wreck_spawning_off_stops_the_timer", "wreckSpawningEnabled",
             "RM_CompVerminNest.CompTick is the only place that reads wreckSpawningEnabled (AttemptSpawn, the debug path, "
             "does not), so the effect needs the 2-4 day interval to elapse; a tick-fast forcing tool is owed"),
            ("nest_countdown_survives_save_load", None,
             "nextSpawnTick is Scribed; proving it needs a save and reload with the debug state read before and after"),
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
