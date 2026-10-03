"""validation.py -- modcheck suite for RimMandrake: The Gelatinous Slime
(`mandrake.rm.gelatinousslime`, FOLDED into `mandrake.rm.biomes`). First script, 2026-10-01.
Item GELATINOUS_SLIME_FIRST_SCRIPT_1. Walk: design/validation_walks/RimMandrake/GelatinousSlime.md.

PACKAGING. `src/RimMandrake/GelatinousSlime` is the SOURCE; the biome ships composed inside
`mandrake.rm.biomes` (Biomes.compose.json), so a run loads the `baroque_wave0` tier
(`modset_builder.py --tier baroque_wave0`, EXPECT_MODS = mandrake.rm.biomes). `modcheck run
GelatinousSlime` would append the dev folder's id with no closure: drive northstar_plan.py instead.

WHAT IT PROVES (intended function, each line sourced from About.xml / the C# / defs):
  defs     every non-abstract def this mod ships RESOLVES live (parsed from our own Defs/ at import, so
           a silently discarded def -- the Aptitude `<li>` trap, a missing type -- is a FAIL, not a gap);
           terrain tag RM_SlimeTerrain on all five terrains (the whole exposure mechanic keys on it);
           the cure-geography patch actually landed on Desert/ExtremeDesert/AridShrubland/Ocean
           (a patch that matches nothing logs nothing -- GELATINOUSSLIME_FIRST_LOAD_ERRORS_1 fault 3).
  ladder   standing on slime applies RM_Slimification; off-slime controls and resistant pawns do not;
           severity moves at the RULED rate (7 d on the body, stage 1 wipes off, stages 2-3 hold, drying
           biome decays); severity 1.0 dissolves a colonist with no corpse + smear + raw slime; stage 3+
           ends panic (law 2); the standing alert lists the pawn.
  items    antidote clears the film (also on a comatose patient) and charges ToxicBuildup; raw slime cures
           poison AND charges the fee in the same bite; Slime-marked costs opinion.
  titano   spawn roll spreads over stages; titanoslimeMaxStage clamps; a cut stage>=2 titanoslime sheds a
           gelatid when titanoslimeSheds is on and does not when off.
  settings all 16 SlimeSettings fields: shipped defaults, write+read-back, and the effect where a bridge can
           see it (flavorReadMarks, titanoslimeMaxStage, titanoslimeSheds).

SITE. Components that need no map (defs) run anywhere. Pawn chains build their own 40x40 site (left half
RM_Slime_Rich, right half Concrete) at the map centre. They run on ANY biome: the predicted rate mirrors
`HediffComp_Slimification.SeverityChangePerDay` and reads the MAP BIOME's live decayPerDay, so a drying
map is predicted to decay and a normal one to grow. `drying_biome_decays` is UNMEASURED unless the map is
one (run the chain once on a Desert site). Biome-gated mechanics (farm conversion, visitor trickle, seeker
mark) need an RM_GelatinousSlime map: UNCOVERED in the walk with the reason.

Every bridge call here uses parameters the live tool declares (lint_calls.py). Result shapes read off the
C# [Tool] ResultDescription; shapes not yet MEASURED live are marked UNPROVEN and a component that cannot
read one records UNMEASURED, never PASS.
"""
import contextlib
import json
import os
import re
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

suite = Suite("GelatinousSlime")
SETTINGS = "RimMandrake.GelatinousSlime.SlimeSettings"
FIELDS = {"rarityFactor": 1, "flavorEntryRecorded": True, "flavorReadMarks": True,
          "titanoslimeSpawnFactor": 1, "titanoslimeEngulfs": True, "titanoslimeGrows": True,
          "preferHigherPriorityArchive": True, "titanoslimeReversible": False,
          "titanoslimeMaxStage": 5, "titanoslimeSheds": True,
          "slimificationEnabled": True, "slimificationClockDays": 7, "fieldConversionEnabled": True,
          "fieldConversionRate": 1, "visitorsEnabled": True, "visitorArrivalRate": 1, "gappoChannels": True, "fubbumHunts": True, "dwommoFlies": True, "glurroSalve": True}
suite.toggles = list(FIELDS)

HERE = os.path.dirname(os.path.abspath(__file__))
SLIME_TERRAINS = ["RM_Slime_Hardened", "RM_Slime_Rich", "RM_Slime_Grass", "RM_Slime_Mud", "RM_Slime_Liquid"]
SLIME_TERRAIN = "RM_Slime_Rich"
SMEAR = "RM_Filth_SlimeSmear"
RAW = "RM_RawSlime"
ANTIDOTE = "RM_SlimeAntidote"
HEDIFF = "RM_Slimification"
RESIST_GENE = "RM_Gene_SlimeResistance"
SITE = 40
# Mirror of HediffComp_Slimification (Source/Slimification.cs). A deliberate rate change in the C# must
# change these in the same commit, with the reason (debug_process.md rung 5).
GROW_PER_DAY, FAST_PER_DAY, REVERT_PER_DAY, REVERT_CEILING = 1.0 / 7, 1.0 / 3, 0.5, 0.2
CHECK, DAY = 200.0, 60000.0
DRYING = {}      # filled by drying_biomes_tagged: biome -> decayPerDay (live)
_ST = {}         # shared between chains of one run


# --------------------------------------------------------------------------- source-derived manifests

def _our_defs():
    """[(DefType, defName)] for every non-abstract top-level def in this mod's Defs/ (read at import)."""
    out = []
    root = os.path.join(HERE, "Defs")
    for dp, _, fns in os.walk(root):
        for fn in sorted(fns):
            if not fn.endswith(".xml"):
                continue
            try:
                tree = ET.parse(os.path.join(dp, fn)).getroot()
            except ET.ParseError:
                continue
            for el in tree:
                if not isinstance(el.tag, str):
                    continue
                nm = el.find("defName")
                if nm is None or (el.get("Abstract") or "").lower() == "true":
                    continue
                out.append((el.tag, nm.text.strip()))
    return out


def _patch_decay():
    """{biome: decayPerDay} the shipped DryingBiomes.xml adds (the expected landing)."""
    out = {}
    p = os.path.join(HERE, "Patches", "DryingBiomes.xml")
    if not os.path.isfile(p):
        return out
    for op in ET.parse(p).getroot().iter("Operation"):
        xp = op.find("xpath")
        m = re.search(r'defName="([^"]+)"', xp.text if xp is not None else "")
        d = op.find(".//decayPerDay")
        if m and d is not None:
            out[m.group(1)] = float(d.text)
    return out


OUR_DEFS = _our_defs()
EXPECT_DECAY = _patch_decay()


# --------------------------------------------------------------------------- helpers

class _Unmeasured(Exception):
    pass


def _fail(msg):
    raise ExpectationFailed(msg)


def _unmeasured(t, why):
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, **kw):
    """t.component() whose failure does not poison the NEXT independent component; `_unmeasured`
    keeps the verdict UNMEASURED with the real reason."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    why = getattr(t, "_why", None)
    if why and not before and t.components:
        t.components[-1].detail = "UNMEASURED: %s" % why
    if not before:
        t.upstream_failed = False
    t._why = None


def _ok(t, r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _unmeasured(t, "%s failed or unreadable: %s" % (what, str(r)[:200]))
    return r


def _defs(t, specs, fields=None, deep=False):
    """get_defs rows keyed by 'Type/name'. Returns (rows, notFound). Never reads a failed call as absent."""
    rows, nf = {}, []
    for i in range(0, len(specs), 60):
        chunk = specs[i:i + 60]
        r = _ok(t, t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields=fields or "", deep=bool(deep),
                                 limit=200), "jawa/get_defs")
        if r.get("malformed"):
            _unmeasured(t, "get_defs malformed entries: %s" % r.get("malformed"))
        nf += list(r.get("notFound") or [])
        for row in r.get("defs") or []:
            rows[row.get("requested")] = row
    return rows, nf


def _clock(t):
    s = t.session
    v = s._ticks() if s is not None else None
    return v


def _prep_site(t):
    t.clear_area(size=SITE)
    x, z = t.anchor
    h = SITE // 2
    t.bridge_call("jawa/set_terrain_batch",
                  ops="%s:%d,%d,%d,%d;Concrete:%d,%d,%d,%d" % (SLIME_TERRAIN, x - h, z - h, h, SITE,
                                                              x, z - h, h, SITE))
    t.bridge_call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (x - h, z - h, SITE, SITE))
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
    t.bridge_call("jawa/log_autoopen_suppress")


def _terrain_at(t, x, z):
    r = _ok(t, t.bridge_call("jawa/get_terrain_batch", rects="%d,%d,1,1" % (x, z)), "get_terrain_batch")
    d = r.get("distinctTerrains") or []
    return d[0] if len(d) == 1 else None


def _check_site(t):
    x, z = t.anchor
    a, b = _terrain_at(t, x - 10, z), _terrain_at(t, x + 10, z)
    if a != SLIME_TERRAIN or b != "Concrete":
        _fail("site terrain did not take: slime half reads %r, concrete half %r" % (a, b))


def _slime_xz(t, i):
    x, z = t.anchor
    return x - 10, z - 15 + 3 * i


def _plain_xz(t, i):
    x, z = t.anchor
    return x + 10, z - 15 + 3 * i


def _spawn(t, kind, x, z, faction="player", draft=True):
    r = _ok(t, t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1),
            "spawn_pawn " + kind)
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if not pid:
        _unmeasured(t, "spawn_pawn %s returned no id: %s" % (kind, str(r)[:160]))
    if draft and faction == "player":
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
        t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)
    return pid


def _rows(t, corpses=False):
    r = _ok(t, t.bridge_call("jawa/list_pawns", includeHealth=True, includeCorpses=corpses, limit=300),
            "list_pawns")
    return {p.get("id"): p for p in (r.get("pawns") or [])}


def _hed(row):
    """{hediff def: severity} off a list_pawns row (health block is NESTED), or None if no pawn."""
    if row is None:
        return None
    return {h.get("def"): float(h.get("severity") or 0) for h in ((row.get("health") or {}).get("hediffs") or [])}


def _add_hediff(t, pid, hediff, sev):
    r = t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff=hediff, severity=sev)
    if not (r or {}).get("success"):
        _unmeasured(t, "pawn_health add %s failed: %s" % (hediff, str(r)[:160]))


def _things(t, defs, rect):
    r = _ok(t, t.bridge_call("jawa/list_things", defName=defs, rect=rect, limit=500), "list_things")
    if r.get("isCompleteList") is False:
        _unmeasured(t, "list_things truncated")
    return r.get("things") or []


def _rect(x, z, r):
    return "%d,%d,%d,%d" % (x - r, z - r, 2 * r + 1, 2 * r + 1)


def _map_decay(t):
    """(biome, live decayPerDay or None) for the current map."""
    r = _ok(t, t.bridge_call("jawa/map_info"), "map_info")
    biome = r.get("mapBiome")
    if not biome:
        _unmeasured(t, "map_info carries no mapBiome")
    rows, nf = _defs(t, ["BiomeDef/%s" % biome], fields="modExtensions", deep=True)
    return biome, _decay_of(rows.get("BiomeDef/%s" % biome))


def _decay_of(row):
    if row is None:
        return None
    for ext in (row.get("fields") or {}).get("modExtensions") or []:
        if isinstance(ext, dict) and "decayPerDay" in ext:
            return float(ext["decayPerDay"])
    return None


def _rate(on_slime, sev, fast, decay):
    """Mirror of SeverityChangePerDay (priority: drying > on the body > fast clock > ordinary country)."""
    if decay:
        return -abs(decay)
    if on_slime:
        return FAST_PER_DAY if fast else GROW_PER_DAY
    if fast:
        return FAST_PER_DAY
    return -REVERT_PER_DAY if sev < REVERT_CEILING else 0.0


def _expect(rate, ticks):
    return rate * (ticks // CHECK) * CHECK / DAY


def _check_delta(name, sev0, sev1, rate, ticks):
    exp = _expect(rate, ticks)
    slack = abs(rate) * CHECK / DAY * 1.5 + 0.0015     # phase of the 200-tick hash gate + float noise
    got = sev1 - sev0
    if abs(got - exp) > max(slack, 0.35 * abs(exp)):
        _fail("%s: severity moved %+.5f over %d ticks, ruled rate predicts %+.5f (rate %+.4f/day)"
              % (name, got, ticks, exp, rate))


# --------------------------------------------------------------------------- chain 1: static / defs

@suite.chain("defs_static")
def defs_static(t):
    with _comp(t, "settings_defaults", toggle="titanoslimeReversible"):
        if t._guard():
            bad = {}
            for f, want in FIELDS.items():
                r = _ok(t, t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f),
                        "mod_settings_field get " + f)
                v = (r or {}).get("value")
                try:
                    same = (str(v).lower() == str(want).lower()) if isinstance(want, bool) else abs(float(v) - want) < 1e-6
                except (TypeError, ValueError):
                    same = False
                if not same:
                    bad[f] = v
            if bad:
                _fail("settings not at shipped defaults (titanoslimeReversible must be False -- owner ruling "
                      "2026-09-21): %s" % bad)

    with _comp(t, "all_defs_resolve"):
        if t._guard():
            if len(OUR_DEFS) < 100:
                _unmeasured(t, "manifest read only %d defs from Defs/ (expected >100)" % len(OUR_DEFS))
            specs = ["%s/%s" % d for d in OUR_DEFS]
            rows, nf = _defs(t, specs)
            miss = sorted(set(nf))
            if miss:
                _fail("%d of %d shipped defs do not resolve live (silently discarded or wrong type): %s"
                      % (len(miss), len(specs), miss[:12]))

    with _comp(t, "fubbum_hunter_def", toggle="fubbumHunts"):
        # GELATINOUSSLIME_FUBBUM_HUNTER_1: predator whose prey ceiling covers the gelatid, not a colonist
        if t._guard():
            rows, nf = _defs(t, ["ThingDef/RM_Fubbum", "ThingDef/RM_Gelatid"], fields="race", deep=True)
            fr, gr = rows.get("ThingDef/RM_Fubbum"), rows.get("ThingDef/RM_Gelatid")
            if fr is None:
                _fail("ThingDef/RM_Fubbum absent live")
            if gr is None:
                _unmeasured(t, "ThingDef/RM_Gelatid did not resolve; cannot compare prey size")
            race = (fr.get("fields") or {}).get("race")
            grace = (gr.get("fields") or {}).get("race")
            if not isinstance(race, dict) or not isinstance(grace, dict):
                _unmeasured(t, "race not serialised as a dict: %s" % str(race)[:120])
            try:
                mp, gb = float(race.get("maxPreyBodySize")), float(grace.get("baseBodySize"))
            except (TypeError, ValueError):
                _unmeasured(t, "maxPreyBodySize/baseBodySize unreadable: %s / %s" % (race.get("maxPreyBodySize"), grace.get("baseBodySize")))
            if str(race.get("predator")).lower() != "true":
                _fail("RM_Fubbum is not a predator live (race.predator %r); with fubbumHunts on it must be" % race.get("predator"))
            if not (gb <= mp < 1.0):
                _fail("maxPreyBodySize %.2f must cover the gelatid (%.2f) and stay under an adult colonist (1.0)" % (mp, gb))
            for k in ("manhunterOnDamageChance", "manhunterOnTameFailChance"):
                if float(race.get(k, 1) or 0) != 0:
                    _fail("%s %r != 0: the fubbum must never turn manhunter" % (k, race.get(k)))

    with _comp(t, "dwommo_flight_def", toggle="dwommoFlies"):
        # GELATINOUSSLIME_DWOMMO_FLIER_1: flight is a STAT (CanEverFly = MaxFlightTime > 0), never a node.
        # Def-level (shipped XML) check first; it needs no live map.
        x = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", "Dwommo.xml")).getroot()
        th = next((e for e in x.findall("ThingDef") if e.findtext("defName") == "RM_Dwommo"), None)
        if th is None:
            _fail("RM_Dwommo ThingDef missing from Defs/ThingDefs_Races/Dwommo.xml")
        try:
            mft = float(th.findtext("statBases/MaxFlightTime"))
        except (TypeError, ValueError):
            mft = 0.0
        if not mft > 0:
            _fail("shipped RM_Dwommo MaxFlightTime must be > 0 (CanEverFly reads the stat); got %r" % mft)
        if th.find("statBases/FlightCooldown") is None or not float(th.findtext("race/flightSpeedFactor") or 0) > 0:
            _fail("RM_Dwommo needs FlightCooldown and race flightSpeedFactor")
        if "Spastic" in ET.tostring(x, encoding="unicode") or x.find(".//flyingAnimationFramePathPrefix") is not None:
            _fail("RM_Dwommo must carry no Spastic wing node and no flip-book prefix until real frames exist")
        # Live: the loaded def's stat. With the switch on it must be > 0. Needs the running game, not a map.
        if t._guard():
            rows, nf = _defs(t, ["ThingDef/RM_Dwommo"], fields="statBases", deep=True)
            row = rows.get("ThingDef/RM_Dwommo")
            if row is None:
                _fail("ThingDef/RM_Dwommo absent live")
            sb = (row.get("fields") or {}).get("statBases")
            live = None
            if isinstance(sb, list):
                for m in sb:
                    if isinstance(m, dict) and "MaxFlightTime" in str(m.get("stat")):
                        live = m.get("value")
            elif isinstance(sb, dict):
                live = sb.get("MaxFlightTime")
            if live is None:
                _unmeasured(t, "statBases not serialised with MaxFlightTime: %s" % str(sb)[:120])
            if not float(live) > 0:
                _fail("RM_Dwommo MaxFlightTime %r live; with dwommoFlies on it must be > 0" % live)

    with _comp(t, "glurro_salve_defs", toggle="glurroSalve"):
        # GELATINOUSSLIME_GLURRO_SALVE_1: creature milks the salve, butchers to the concentrate; both slow, neither cures.
        gx = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", "Glurro.xml")).getroot()
        gl = next((e for e in gx.findall("ThingDef") if e.findtext("defName") == "RM_Glurro"), None)
        if gl is None:
            _fail("RM_Glurro ThingDef missing from Defs/ThingDefs_Races/Glurro.xml")
        mk = gl.find("comps/li[@Class='CompProperties_Milkable']")
        if mk is None or mk.findtext("milkDef") != "RM_GlurroSalve":
            _fail("RM_Glurro must carry CompProperties_Milkable with milkDef RM_GlurroSalve")
        if gl.findtext("butcherProducts/RM_GlurroSalveConcentrate") is None:
            _fail("RM_Glurro must yield RM_GlurroSalveConcentrate when butchered")
        if not any("SlimeResistantExtension" in (e.get("Class") or "") for e in gl.findall("modExtensions/li")):
            _fail("RM_Glurro must be slime resistant (it is never read)")
        ix = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Items", "GlurroSalve.xml")).getroot()
        st = {}
        for e in ix.findall("ThingDef"):
            try:
                st[e.findtext("defName")] = float(e.findtext("modExtensions/li/strength"))
            except (TypeError, ValueError):
                st[e.findtext("defName")] = None
        a, b = st.get("RM_GlurroSalve"), st.get("RM_GlurroSalveConcentrate")
        if a is None or b is None:
            _fail("salve/concentrate need a GlurroSalveExtension strength: %s" % st)
        if not (0 < a < b < 1):
            _fail("strengths must satisfy 0 < salve < concentrate < 1 (slows, never stops): %r %r" % (a, b))
        if t._guard():
            rows, nf = _defs(t, ["ThingDef/RM_Glurro", "ThingDef/RM_GlurroSalve", "ThingDef/RM_GlurroSalveConcentrate"])
            if nf:
                _fail("glurro defs not resolving live (foundCount != 3): %s" % nf)

    with _comp(t, "terrain_tagged"):
        if t._guard():
            rows, nf = _defs(t, ["TerrainDef/%s" % n for n in SLIME_TERRAINS], fields="tags")
            if nf:
                _fail("slime terrain(s) missing: %s" % nf)
            bad = [n for n in SLIME_TERRAINS
                   if "RM_SlimeTerrain" not in ((rows["TerrainDef/%s" % n].get("fields") or {}).get("tags") or [])]
            if bad:
                _fail("terrain(s) without tag RM_SlimeTerrain (exposure never fires on them): %s" % bad)

    with _comp(t, "slimification_def_ladder"):
        if t._guard():
            rows, nf = _defs(t, ["HediffDef/%s" % HEDIFF], fields="stages,comps,maxSeverity,scenarioCanAdd", deep=True)
            row = rows.get("HediffDef/%s" % HEDIFF)
            if row is None:
                _fail("RM_Slimification absent")
            f = row.get("fields") or {}
            st = f.get("stages") or []
            if not isinstance(st, list) or len(st) != 4:
                _unmeasured(t, "stages not readable as 4 dicts: %s" % str(st)[:160])
            mins = [round(float(s.get("minSeverity", -1)), 2) for s in st]
            if mins != [0.0, 0.2, 0.5, 0.9]:
                _fail("stage thresholds %s != [0, 0.2, 0.5, 0.9]" % mins)
            if float(st[2].get("painFactor", 1)) != 0 or float(st[3].get("painFactor", 1)) != 0:
                _fail("stages 3-4 must carry painFactor 0 (placid)")
            giving = [i for i, s in enumerate(st) if s.get("mentalStateGivers")]
            if giving:
                _fail("stage(s) %s grant a mental state: law 2 (never hostile) broken in XML" % giving)
            if float(f.get("maxSeverity", 0)) != 1.0:
                _fail("maxSeverity %r != 1.0" % f.get("maxSeverity"))
            comps = json.dumps(f.get("comps") or [])
            if "HediffComp_Slimification" not in comps:
                _fail("RM_Slimification carries no HediffComp_Slimification comp (rate/dissolution dead): %s"
                      % comps[:200])

    with _comp(t, "drying_biomes_tagged"):
        if t._guard():
            if not EXPECT_DECAY:
                _unmeasured(t, "could not read Patches/DryingBiomes.xml manifest")
            spec = ["BiomeDef/%s" % b for b in EXPECT_DECAY] + ["BiomeDef/TemperateForest", "BiomeDef/RM_GelatinousSlime"]
            rows, nf = _defs(t, spec, fields="modExtensions", deep=True)
            bad = []
            for b, want in EXPECT_DECAY.items():
                got = _decay_of(rows.get("BiomeDef/%s" % b))
                if got is None or abs(got - want) > 1e-6:
                    bad.append("%s: live %r, shipped %r" % (b, got, want))
                DRYING[b] = got
            for ctl in ("TemperateForest", "RM_GelatinousSlime"):
                row = rows.get("BiomeDef/%s" % ctl)
                if row is not None and _decay_of(row) is not None:
                    bad.append("%s must NOT be a drying biome but carries decayPerDay" % ctl)
            if bad:
                _fail("cure geography not as shipped (a patch that matches nothing logs nothing): %s" % bad)

    with _comp(t, "visitor_genstep_registered"):
        if t._guard():
            rows, nf = _defs(t, ["MapGeneratorDef/Base_Player"], fields="genSteps")
            row = rows.get("MapGeneratorDef/Base_Player")
            if row is None:
                _unmeasured(t, "MapGeneratorDef/Base_Player did not resolve")
            gs = (row.get("fields") or {}).get("genSteps")
            if not isinstance(gs, list):
                _unmeasured(t, "genSteps not serialisable: %s" % str(gs)[:120])
            if "RM_SlimeVisitorSeed" not in gs:
                _fail("RM_SlimeVisitorSeed not in Base_Player.genSteps (MapGen patch matched nothing)")

    with _comp(t, "gene_archive_resolves", toggle="preferHigherPriorityArchive"):
        if t._guard():
            rows, nf = _defs(t, ["RimMandrake.GelatinousSlime.GeneArchiveDef/RM_Archive_Default"], fields="priority,targetGenes,riderGenes")
            row = rows.get("RimMandrake.GelatinousSlime.GeneArchiveDef/RM_Archive_Default")
            if row is None:
                _fail("RM_Archive_Default absent")
            f = row.get("fields") or {}
            tg, rg = f.get("targetGenes") or [], f.get("riderGenes") or []
            if int(f.get("priority", -1)) != 0:
                _fail("default archive priority %r != 0 (a campaign archive must outrank it)" % f.get("priority"))
            if len(tg) < 17 or not rg:
                _fail("default archive offers %d targets / %d riders (17+ / 1+ shipped)" % (len(tg), len(rg)))
            grows, gnf = _defs(t, ["GeneDef/%s" % g for g in tg + rg])
            if gnf:
                _fail("archive names gene(s) that do not exist live: %s" % gnf[:8])


# --------------------------------------------------------------------------- chain 2: exposure + ladder

@suite.chain("exposure_and_ladder")
def exposure_and_ladder(t):
    P = {}
    with t.component("site_ready_ladder"):
        if t._guard():
            _prep_site(t)
            _check_site(t)
            x, z = t.anchor
            P["exposed"] = _spawn(t, "Colonist", *_slime_xz(t, 0))
            P["control"] = _spawn(t, "Colonist", *_plain_xz(t, 0))
            P["resist"] = _spawn(t, "Colonist", *_slime_xz(t, 1))
            r = t.bridge_call("jawa/pawn_genes", pawn=P["resist"], action="add", gene=RESIST_GENE, xenogene=False)
            if not (r or {}).get("success") or RESIST_GENE not in (r.get("endogenes") or []):
                _unmeasured(t, "could not give %s: %s" % (RESIST_GENE, str(r)[:160]))
            P["gelatid"] = _spawn(t, "RM_Gelatid", *_slime_xz(t, 2), faction="none", draft=False)
            # severity-controlled pawns (rate table)
            for key, sev, slime in (("grow", 0.30, True), ("revert", 0.15, False),
                                    ("hold2", 0.35, False), ("hold3", 0.60, False)):
                xz = _slime_xz(t, 3) if slime else _plain_xz(t, {"revert": 1, "hold2": 2, "hold3": 3}[key])
                P[key] = _spawn(t, "Colonist", *xz)
                _add_hediff(t, P[key], HEDIFF, sev)
            # GELATINOUSSLIME_GLURRO_SALVE_1: same seed as "grow" plus the salve hediff
            P["salved"] = _spawn(t, "Colonist", *_slime_xz(t, 4))
            _add_hediff(t, P["salved"], HEDIFF, 0.30)
            _add_hediff(t, P["salved"], "RM_GlurroSalved", 0.5)
            _ST["biome"], _ST["decay"] = _map_decay(t)
            rows0 = _rows(t)
            _ST["sev0"] = {k: (_hed(rows0.get(P[k])) or {}).get(HEDIFF) for k in ("grow", "revert", "hold2", "hold3", "salved")}
            if None in _ST["sev0"].values():
                _unmeasured(t, "seeded hediff not readable back: %s" % _ST["sev0"])
            _ST["tick0"] = _clock(t)
            t.wait_ticks(1200)
    with _comp(t, "exposure_applies_on_slime"):
        if t._guard():
            h = _hed(_rows(t).get(P["exposed"]))
            if h is None:
                _unmeasured(t, "exposed pawn vanished")
            if HEDIFF not in h:
                _fail("colonist stood 1200 ticks on RM_Slime_Rich and was never read (hediffs %s): "
                      "MapComponent_SlimeExposure / terrain tag dead" % sorted(h))
            _ST["exposed_sev"], _ST["exposed_tick"] = h[HEDIFF], _clock(t)
    with _comp(t, "exposure_skips_off_slime_and_resistant"):
        if t._guard():
            rows = _rows(t)
            bad = {k: sorted(_hed(rows.get(P[k])) or []) for k in ("control", "resist", "gelatid")
                   if HEDIFF in (_hed(rows.get(P[k])) or {})}
            if bad:
                _fail("pawns that must never be read carry RM_Slimification: %s (control=off-slime, "
                      "resist=%s gene, gelatid=resistant by identity)" % (bad, RESIST_GENE))
            if any(rows.get(P[k]) is None for k in ("control", "resist", "gelatid")):
                _unmeasured(t, "a control pawn vanished, cannot prove absence")
            t.wait_ticks(2000)
    with _comp(t, "growth_rate_on_slime"):
        if t._guard():
            rows = _rows(t)
            now = _clock(t)
            ticks = now - _ST["tick0"]
            _ST["ticks"], _ST["rows"] = ticks, rows
            s1 = (_hed(rows.get(P["exposed"])) or {}).get(HEDIFF)
            if s1 is None and _ST["decay"] is None:
                _unmeasured(t, "exposed pawn lost the hediff")
            if s1 is not None:
                _check_delta("exposed colonist on slime", _ST["exposed_sev"], s1,
                             _rate(True, s1, False, _ST["decay"]), now - _ST["exposed_tick"])
            g1 = (_hed(rows.get(P["grow"])) or {}).get(HEDIFF)
            if g1 is None and _ST["decay"] is None:
                _fail("seeded sev .30 hediff vanished on slime in a non-drying biome")
            if g1 is not None:
                _check_delta("seeded sev .30 on slime", _ST["sev0"]["grow"], g1,
                             _rate(True, 0.3, False, _ST["decay"]), ticks)
    with _comp(t, "glurro_salve_slows_growth", toggle="glurroSalve"):
        # salved pawn (salve strength 0.5) on slime: growth ~half the unsalved rate, still > 0 (never stops)
        if t._guard():
            if _ST["decay"] is not None:
                _unmeasured(t, "map biome %s is a drying biome: growth is not running, a slowdown cannot be seen" % _ST["biome"])
            rows, ticks = _ST["rows"], _ST["ticks"]
            sv = (_hed(rows.get(P["salved"])) or {}).get(HEDIFF)
            if sv is None:
                _unmeasured(t, "salved pawn lost the hediff or was not readable")
            if (_hed(rows.get(P["salved"])) or {}).get("RM_GlurroSalved") is None:
                _unmeasured(t, "RM_GlurroSalved gone before the read (decays 0.25/day; expected present)")
            if not sv > _ST["sev0"]["salved"]:
                _fail("salved pawn's slimification did not advance at all (%.4f -> %.4f): the salve may only slow it"
                      % (_ST["sev0"]["salved"], sv))
            _check_delta("salved sev .30 on slime (half speed)", _ST["sev0"]["salved"], sv, GROW_PER_DAY * 0.5, ticks)

    with _comp(t, "stage1_wipes_off_stages_2_3_hold"):
        if t._guard():
            rows, ticks = _ST["rows"], _ST["ticks"]
            dec = _ST["decay"]
            for key, sev in (("revert", 0.15), ("hold2", 0.35), ("hold3", 0.60)):
                now = (_hed(rows.get(P[key])) or {}).get(HEDIFF)
                rate = _rate(False, sev, False, dec)
                if now is None:
                    # the hediff is removed when severity reaches 0: legitimate only if the ruled rate gets there
                    if _ST["sev0"][key] + _expect(rate, ticks) > 0.01:
                        _fail("%s: hediff vanished but the ruled rate (%+.3f/day) leaves %.3f"
                              % (key, rate, _ST["sev0"][key] + _expect(rate, ticks)))
                    continue
                _check_delta("off-slime sev %.2f" % sev, _ST["sev0"][key], now, rate, ticks)
            if dec is None:
                if abs((_hed(rows.get(P["hold2"])) or {}).get(HEDIFF, 0) - _ST["sev0"]["hold2"]) > 0.002:
                    _fail("stage-2 film moved in ordinary country (must hold)")
    with _comp(t, "drying_biome_decays"):
        if t._guard():
            if _ST["decay"] is None:
                _unmeasured(t, "map biome %s is not a drying biome; rerun this chain on a Desert/AridShrubland "
                               "site (prediction above already covers the non-drying branch)" % _ST["biome"])
            rows = _rows(t)
            for key, sev in (("grow", 0.30), ("hold2", 0.35), ("hold3", 0.60)):
                now = (_hed(rows.get(P[key])) or {}).get(HEDIFF, 0.0)
                if now >= _ST["sev0"][key]:
                    _fail("%s did not decay on drying biome %s (%.4f -> %.4f); even slime ground loses to dry "
                          "country" % (key, _ST["biome"], _ST["sev0"][key], now))
    with _comp(t, "standing_alert_lists_pawn"):
        if t._guard():
            t.wait_ticks(120)
            r = _ok(t, t.bridge_call("jawa/alerts_list"), "alerts_list")
            al = [a for a in (r.get("alerts") or []) if "Alert_Slimification" in str(a.get("type"))]
            if _ST["decay"] is not None:
                _unmeasured(t, "drying map: the film decays out of stage 2+, alert may legitimately be absent")
            if not al:
                _fail("no Alert_Slimification although a stage-3 colonist exists: %s" % [a.get("type") for a in r.get("alerts") or []][:12])
    with _comp(t, "stage3_ends_panic_law2"):
        if t._guard():
            st = "PanicFlee"
            for key in ("hold3", "revert"):
                r = t.bridge_call("jawa/pawn_mental", pawn=P[key], action="start", state=st)
                if not (r or {}).get("started"):
                    _unmeasured(t, "could not start %s on %s: %s" % (st, key, str(r)[:140]))
            t.wait_ticks(600)
            hi = (t.bridge_call("jawa/pawn_mental", pawn=P["hold3"], action="list", limit=1) or {}).get("currentState")
            lo = (t.bridge_call("jawa/pawn_mental", pawn=P["revert"], action="list", limit=1) or {}).get("currentState")
            if lo != st:
                _unmeasured(t, "control (stage 1) left %s by itself (%r): the differential is invalid" % (st, lo))
            if hi == st:
                _fail("stage-3 pawn still in %s after 600 ticks while the stage-1 control is: law 2 not enforced" % st)


# --------------------------------------------------------------------------- chain 3: dissolution

@suite.chain("dissolution")
def dissolution(t):
    P = {}
    with t.component("site_ready_dissolution"):
        if t._guard():
            _prep_site(t)
            _check_site(t)
            P["pawn"] = _spawn(t, "Colonist", *_slime_xz(t, 4))
            P["pos"] = _slime_xz(t, 4)
            _add_hediff(t, P["pawn"], HEDIFF, 1.0)
    with _comp(t, "returned_to_the_flow"):
        if t._guard():
            t.wait_ticks(700)
            rows = _rows(t, corpses=True)
            if P["pawn"] in rows:
                _fail("severity-1.0 colonist still present after 700 ticks (dead=%s): no dissolution / corpse left"
                      % rows[P["pawn"]].get("dead"))
            x, z = P["pos"]
            smear = _things(t, SMEAR, _rect(x, z, 4))
            raw = _things(t, RAW, _rect(x, z, 4))
            if not raw:
                _fail("no %s where the colonist dissolved" % RAW)
            if not smear:
                _fail("no %s where the colonist dissolved (filth refused by the terrain?)" % SMEAR)


# --------------------------------------------------------------------------- chain 4: antidote

@suite.chain("antidote")
def antidote(t):
    P = {}
    with t.component("site_ready_antidote"):
        if t._guard():
            _prep_site(t)
            _check_site(t)
            P["doc1"] = _spawn(t, "Colonist", *_plain_xz(t, 0), draft=False)
            P["doc2"] = _spawn(t, "Colonist", *_plain_xz(t, 2), draft=False)
            P["awake"] = _spawn(t, "Colonist", *_plain_xz(t, 1))
            P["coma"] = _spawn(t, "Colonist", *_plain_xz(t, 3))
            P["ctl"] = _spawn(t, "Colonist", *_plain_xz(t, 5))
            for k in ("awake", "coma", "ctl"):
                _add_hediff(t, P[k], HEDIFF, 0.55)
            _add_hediff(t, P["coma"], "XenogerminationComa", 1.0)
            x, z = t.anchor
            r = t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d;%s:%d,%d" % (ANTIDOTE, x + 6, z - 6, ANTIDOTE, x + 6, z))
            ids = [a.get("id") for a in _things(t, ANTIDOTE, _rect(x + 6, z - 3, 8))]
            if len(ids) < 2:
                _unmeasured(t, "antidote stacks not spawned (%s): %s" % (ids, str(r)[:140]))
            P["ids"] = ids
    with _comp(t, "antidote_clears_film_and_poisons"):
        if t._guard():
            for doc, pat, item in (("doc1", "awake", P["ids"][0]), ("doc2", "coma", P["ids"][1])):
                r = t.bridge_call("jawa/ordered_job", pawnId=P[doc], jobDef="UseItem", targetAId=item,
                                  targetBId=P[pat], count=1, waitTicks=0, timeoutSeconds=30)
                if not (r or {}).get("accepted"):
                    _unmeasured(t, "UseItem order for %s refused (HARNESS: reservation/shape): %s" % (pat, str(r)[:160]))
            t.wait_ticks(1200)
            rows = _rows(t)
            for pat in ("awake", "coma"):
                h = _hed(rows.get(P[pat]))
                if h is None:
                    _unmeasured(t, "%s patient vanished" % pat)
                if HEDIFF in h:
                    _fail("%s patient still slimified (%.2f) after the antidote" % (pat, h[HEDIFF]))
                if h.get("ToxicBuildup", 0) < 0.08:
                    _fail("%s patient took no ToxicBuildup (the cure is honestly a poisoning; got %r)"
                          % (pat, h.get("ToxicBuildup")))
            if HEDIFF not in (_hed(rows.get(P["ctl"])) or {}):
                _fail("untreated control lost the film by itself: the clear above proves nothing")
            x, z = t.anchor
            if _things(t, ANTIDOTE, _rect(x + 6, z - 3, 8)):
                _fail("antidote stack(s) not consumed")


# --------------------------------------------------------------------------- chain 5: eating raw slime

@suite.chain("raw_slime_bargain")
def raw_slime_bargain(t):
    P = {}
    with t.component("site_ready_eat"):
        if t._guard():
            _prep_site(t)
            _check_site(t)
            P["eater"] = _spawn(t, "Colonist", *_plain_xz(t, 0), draft=False)
            t.bridge_call("jawa/pawn_need", pawn=P["eater"], action="need", need="Food", level=0.4)
            _add_hediff(t, P["eater"], "ToxicBuildup", 0.4)
            x, z = t.anchor
            t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d,8" % (RAW, x + 8, z - 15 + 1))
            P["ids"] = [a.get("id") for a in _things(t, RAW, _rect(x + 8, z - 14, 3))]
            if not P["ids"]:
                _unmeasured(t, "raw slime not spawned")
    with _comp(t, "raw_slime_cures_poison_and_charges_fee"):
        if t._guard():
            r = t.bridge_call("jawa/ordered_job", pawnId=P["eater"], jobDef="Ingest", targetAId=P["ids"][0],
                              count=2, waitTicks=0, timeoutSeconds=30)
            if not (r or {}).get("accepted"):
                _unmeasured(t, "Ingest order refused: %s" % str(r)[:160])
            t.wait_ticks(900)
            h = _hed(_rows(t).get(P["eater"]))
            if h is None:
                _unmeasured(t, "eater vanished")
            ate = HEDIFF in h
            cured = "ToxicBuildup" not in h
            if not cured and not ate:
                _unmeasured(t, "pawn did not eat within 900 ticks (still poisoned, no film)")
            if not cured:
                _fail("ate raw slime (film %.2f) but ToxicBuildup survived: the antitoxin half is dead" % h[HEDIFF])
            if not ate:
                _fail("raw slime cured the poison but charged NO slimification: the bargain became a free heal")
            if not 0.05 <= h[HEDIFF] <= 0.99:
                _fail("dose fee %.3f outside 0.05..0.99 (0.06 per ingested count + 0.01)" % h[HEDIFF])


# --------------------------------------------------------------------------- chain 6: read-marks flavour

@suite.chain("read_marks_flavour")
def read_marks_flavour(t):
    P = []
    with t.component("site_ready_marks"):
        if t._guard():
            _prep_site(t)
            _check_site(t)
            for i in range(8):
                xz = (_slime_xz(t, 0)[0] - 4 * (i % 2), _slime_xz(t, i)[1])
                pid = _spawn(t, "Colonist", *xz)
                _add_hediff(t, pid, HEDIFF, 0.30)
                P.append(pid)
    with _comp(t, "read_marks_follow_setting", toggle="flavorReadMarks"):
        if t._guard():
            x, z = t.anchor
            rect = "%d,%d,%d,%d" % (x - SITE // 2, z - SITE // 2, SITE // 2, SITE)
            try:
                t.set_setting(SETTINGS, {"flavorReadMarks": True})
                t.wait_ticks(5000)
                on = len(_things(t, SMEAR, rect))
                t.bridge_call("jawa/destroy_batch", rects=rect, categories="Filth")
                if _things(t, SMEAR, rect):
                    _unmeasured(t, "could not clear smears between arms")
                t.set_setting(SETTINGS, {"flavorReadMarks": False})
                t.wait_ticks(5000)
                off = len(_things(t, SMEAR, rect))
            finally:
                t.set_setting(SETTINGS, {"flavorReadMarks": True})
            if on == 0:
                _fail("setting ON: 8 stage-2 colonists x ~25 checks left no smear (expected ~12; "
                      "P(0 by chance) < 0.01%)")
            if off != 0:
                _fail("setting OFF still produced %d smear(s)" % off)


# --------------------------------------------------------------------------- chain 7: Slime-marked

@suite.chain("slime_marked_opinion")
def slime_marked_opinion(t):
    P = {}
    with t.component("site_ready_marked"):
        if t._guard():
            _prep_site(t)
            _check_site(t)
            P["a"] = _spawn(t, "Colonist", *_plain_xz(t, 0))
            P["b"] = _spawn(t, "Colonist", *_plain_xz(t, 1))
    with _comp(t, "marked_colonist_is_liked_less"):
        if t._guard():
            def op():
                r = _ok(t, t.bridge_call("jawa/read_opinion", pawn=P["a"], other=P["b"]), "read_opinion")
                v = r.get("opinionOfPawn")      # b's opinion of a
                if v is None:
                    _unmeasured(t, "read_opinion carries no opinionOfPawn")
                return float(v)
            base = op()
            _add_hediff(t, P["a"], "RM_SlimeMarked", 1.0)
            one = op()
            r = t.bridge_call("jawa/pawn_severity_adjust", pawn=P["a"], hediff="RM_SlimeMarked", offset=3.0)
            if not (r or {}).get("success"):
                _unmeasured(t, "severity_adjust on RM_SlimeMarked failed: %s" % str(r)[:140])
            four = op()
            if base - one < 8:
                _fail("one entry cost %.1f opinion (shipped stage 1: -12)" % (base - one))
            if one - four < 8:
                _fail("heavily-filed (sev>=4) cost only %.1f more than one entry (stage 3: -36)" % (one - four))


# --------------------------------------------------------------------------- chain 8: small probes

@suite.chain("seeker_and_weather")
def seeker_and_weather(t):
    with t.component("site_ready_probes"):
        if t._guard():
            _prep_site(t)
            _check_site(t)
    with _comp(t, "blank_seeker_reports_unprimed"):
        if t._guard():
            x, z = t.anchor
            t.bridge_call("jawa/spawn_batch", ops="RM_GeneSeeker:%d,%d" % (x + 5, z))
            ids = [a.get("id") for a in _things(t, "RM_GeneSeeker", _rect(x + 5, z, 2))]
            if not ids:
                _unmeasured(t, "RM_GeneSeeker did not spawn")
            r = _ok(t, t.bridge_call("jawa/inspect_string", thingIds=ids[0]), "inspect_string")   # UNPROVEN shape
            rows = r.get("things") or r.get("results") or []
            txt = json.dumps(rows)
            if not rows:
                _unmeasured(t, "inspect_string rows unreadable: %s" % str(r)[:160])
            if "Not primed" not in txt:
                _fail("blank seeker does not say 'Not primed' (CompGeneSeeker missing/ renamed): %s" % txt[:200])
    with _comp(t, "slime_rain_can_fall"):
        if t._guard():
            try:
                r = t.bridge_call("jawa/weather_set", weather="RM_Weather_SlimeRain", lockWeather=True)
                if not (r or {}).get("success"):
                    _fail("weather_set RM_Weather_SlimeRain refused: %s" % str(r)[:160])
                w = _ok(t, t.bridge_call("jawa/weather_get"), "weather_get")
                cur = ((w.get("weather") or {}).get("current"))
                if cur != "RM_Weather_SlimeRain":
                    _fail("current weather %r after forcing slime rain" % cur)
            finally:
                t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)


# --------------------------------------------------------------------------- chain 9: titanoslime

def _stage(t, pid):
    r = _ok(t, t.bridge_call("jawa/inspect_string", thingIds=pid), "inspect_string")     # UNPROVEN shape
    m = re.search(r"Stage (\d+) of (\d+)", json.dumps(r.get("things") or r.get("results") or []))
    return int(m.group(1)) if m else None


def _spawn_titans(t, n):
    ids = []
    for i in range(n):
        x, z = _slime_xz(t, 0)
        ids.append(_spawn(t, "RM_Titanoslime", x - 3 - 2 * (i % 4), z + 3 * (i // 4) + 1, faction="none", draft=False))
    return ids


@suite.chain("titanoslime")
def titanoslime(t):
    S = {}
    with t.component("site_ready_titan"):
        if t._guard():
            _prep_site(t)
            _check_site(t)
    with _comp(t, "stage_roll_spreads", toggle="titanoslimeMaxStage"):
        if t._guard():
            ids = _spawn_titans(t, 16)
            st = [_stage(t, i) for i in ids]
            if None in st:
                _unmeasured(t, "stage unreadable from inspect string for some titanoslime")
            S["ids"], S["stages"] = ids, st
            if max(st) < 2:
                _fail("16 titanoslimes rolled stages %s: 40%% should be stage>=2 (mass 4/12); roll dead" % st)
            # clamp arm
            try:
                t.set_setting(SETTINGS, {"titanoslimeMaxStage": 1})
                cl = _spawn_titans(t, 6)
                cst = [_stage(t, i) for i in cl]
            finally:
                t.set_setting(SETTINGS, {"titanoslimeMaxStage": 5})
            if any(s != 1 for s in cst):
                _fail("titanoslimeMaxStage=1 still spawned stages %s" % cst)
    for arm, sheds in (("sheds_when_cut", True), ("does_not_shed_when_setting_off", False)):
        with _comp(t, arm, toggle="titanoslimeSheds" if sheds else None):
            if t._guard():
                pool = [i for i, s in zip(S.get("ids", []), S.get("stages", [])) if s and s >= 2]
                if not pool:
                    _unmeasured(t, "no stage>=2 titanoslime in the roll to cut")
                target = pool.pop(0 if sheds else -1)
                if sheds is False and len(pool) < 0:
                    _unmeasured(t, "no second target")
                def gelatids():
                    return sum(1 for r in _rows(t).values() if r.get("kind") == "RM_Gelatid")
                before = gelatids()
                try:
                    t.set_setting(SETTINGS, {"titanoslimeSheds": sheds})
                    for _ in range(6):
                        t.bridge_call("jawa/damage", damageDef="Blunt", amount=35, thingId=target, armorPenetration=1.0)
                        if gelatids() > before:
                            break
                finally:
                    t.set_setting(SETTINGS, {"titanoslimeSheds": True})
                after = gelatids()
                if sheds and after <= before:
                    _fail("cut stage>=2 titanoslime shed no gelatid in 6 x 35 Blunt (setting ON): %d -> %d" % (before, after))
                if not sheds and after > before:
                    _fail("setting OFF yet %d gelatid(s) shed" % (after - before))


# --------------------------------------------------------------------------- chain 10: settings write + read-back

def _flip(t, comp, field, off):
    with _comp(t, comp, toggle=field):
        if t._guard():
            try:
                t.set_setting(SETTINGS, {field: off})
            finally:
                t.set_setting(SETTINGS, {field: FIELDS[field]})


@suite.chain("settings_flip")
def settings_flip(t):
    # every field has a write+read-back component or an effect component above; these close the rest
    for field, off in (("rarityFactor", 0), ("titanoslimeSpawnFactor", 0), ("flavorEntryRecorded", False),
                       ("titanoslimeEngulfs", False), ("titanoslimeGrows", False),
                       ("titanoslimeReversible", True), ("preferHigherPriorityArchive", False),
                       ("slimificationEnabled", False), ("slimificationClockDays", 2),
                       ("fieldConversionEnabled", False), ("fieldConversionRate", 4),
                       ("visitorsEnabled", False), ("visitorArrivalRate", 4), ("gappoChannels", False), ("fubbumHunts", False), ("dwommoFlies", False), ("glurroSalve", False)):
        _flip(t, "%s_setting_flips" % field, field, off)
