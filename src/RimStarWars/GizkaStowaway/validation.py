"""validation.py -- modcheck suite for RimStarWars: Gizka Stowaway (mandrake.rsw.gizkastowaway).

First north-star script (GIZKA_STOWAWAY_FIRST_SCRIPT_1). Walk: design/validation_walks/RimStarWars/GizkaStowaway.md.
The KotOR ship-pest as a found-aboard EVENT: four player-action hooks (gravship landing, wreck deconstruction,
completed trade, quest success; Harmony, owner mandrake.rsw.gizkastowaway) deliver exactly one tame gizka; event
lineage carries the per-pawn hediff RSW_GizkaFecundity (replicates while fed AND warm, capped); the Infestation
stage chews powered buildings; five exits (cull guilt, sell, poison bait, cold, farm). Separately the DONOR gizka's
own breeding is patched wild-wide (Patches/RSW_GizkaDonorPatches.xml, MarketValue 100 -> 15) and scaled by the
global breeding slider. The creature itself is the donor's (Star Wars Animal Collection) or SWBestiary's RSW_Gizka.

CHAINS
  defs_resolve        every def under Defs/ resolves live; a control name reads notFound; the fecundity comp loaded.
  settings_roundtrip  every public field of RSW_GizkaSettings (INSTANCE fields; the tool reads both kinds), found by
                      regex; bool / int / float round-tripped numerically.
  harmony_wiring      each of the five patched engine methods carries a patch owned by mandrake.rsw.gizkastowaway.
  fecundity_state     a gizka given RSW_GizkaFecundity carries it, a control gizka does not.
  bait_poison         the poison hediff, given to a gizka, advances (state read); the bait item and recipe resolve.
  donor_patch         the donor/port gizka def exists and its MarketValue reads 15 (UNMEASURED when no gizka is loaded).
  mechanics_unmeasured  the four discovery triggers, replication and its cap, chewing, cold stall, cull guilt, the
                      global rate slider: each says what it needs.

STATIC (offline): `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import contextlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.StarWars.GizkaStowaway.RSW_GizkaSettings"
HARMONY_ID = "mandrake.rsw.gizkastowaway"
FECUNDITY = "RSW_GizkaFecundity"
POISON = "RSW_GizkaBaitPoison"
GIZKA_KINDS = ("Gizka", "RSW_Gizka")          # donor (mlie.starwarsanimalcollection) / SWBestiary port
CONTROL_ABSENT = "ThingDef/RSW_GizkaNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+(?:static\s+)?(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
# the toggle that gates each hook (None: the master switch)
HOOK_TOGGLE = {"PostGravshipLanded": "triggerGravship", "Destroy": "triggerSalvage", "TryExecute": "triggerTrade",
               "End": "triggerQuest", "Kill": "cullGuiltEnabled"}


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


def _read(rel):
    return open(os.path.join(HERE, *rel.split("/")), encoding="utf-8").read()


def _settings_body():
    src = re.sub(r"//[^\n]*", "", _read("Source/RSW_GizkaSettings.cs"))
    return src.split("class RSW_GizkaSettings", 1)[1].split("DoWindowContents", 1)[0]


def settings_fields():
    """{name: (type, initializer)} for every scalar field of RSW_GizkaSettings (before ExposeData's methods)."""
    body = _settings_body().split("ExposeData", 1)[0]
    return dict((m.group(2), (m.group(1), m.group(3).strip())) for m in _FIELD.finditer(body))


def hooks():
    """[(TargetType, method)] for every [HarmonyPatch(typeof(X), nameof(X.M))] in the C#."""
    return re.findall(r"\[HarmonyPatch\(typeof\((\w+)\),\s*nameof\(\w+\.(\w+)\)\)\]",
                      _read("Source/RSW_GizkaHarmonyPatches.cs"))


def _num(s):
    return float(s.strip().rstrip("fF"))


def static_checks():
    bad = []
    if len(SHIPPED) < 5:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no field (sanity probe failed)"]
    body = _settings_body()
    scribed = body.split("ExposeData", 1)[1].split("public void", 1)[0]
    ui = _read("Source/RSW_GizkaSettings.cs").split("DoSettingsWindowContents", 1)[1]
    for n, (ty, init) in fields.items():
        m = re.search(r'Scribe_Values\.Look\(ref\s+%s,\s*"%s",\s*([^)]+)\)' % (n, n), scribed)
        if not m:
            bad.append("settings field %s is not Scribed under its own name" % n)
        else:
            d = m.group(1).strip()
            same = (d.lower() == init.lower()) if ty == "bool" else abs(_num(d) - _num(init)) < 1e-9
            if not same:
                bad.append("settings field %s: Scribe default %s differs from initializer %s" % (n, d, init))
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in the settings window" % n)
    proj = _read("Source/RimMandrakeGizkaStowaway.csproj")
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    hk = hooks()
    if len(hk) != 5:
        bad.append("expected 5 Harmony patches, parsed %d (%r)" % (len(hk), hk))
    for _ty, m in hk:
        if m not in HOOK_TOGGLE:
            bad.append("hook method %s has no entry in this script's HOOK_TOGGLE" % m)
    if '"%s"' % HARMONY_ID not in _read("Source/RSW_GizkaHarmonyPatches.cs"):
        bad.append("Harmony id is no longer %s" % HARMONY_ID)
    if any(ty == "IncidentDef" for ty, _n in SHIPPED):
        bad.append("an IncidentDef shipped: the design rejects a storyteller threat roll")
    kinds = set(ty for ty, _n in SHIPPED)
    for need in ("HediffDef", "ThingDef", "RecipeDef", "ThoughtDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    # the fecundity numbers the design rules
    h = [e for e in ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "RSW_GizkaHediffs.xml")).getroot()
         if e.findtext("defName") == FECUNDITY][0]
    c = h.find("comps/li")
    if not 0 < float(c.findtext("baseReplicateIntervalDays")) <= 10:
        bad.append("fecundity base interval is outside the slow-burn band (0, 10] days")
    if float(c.findtext("intervalStretchAtCap")) <= 1:
        bad.append("interval does not stretch toward the cap (anti-exponential law)")
    if float(c.findtext("minBreedingTemperature")) <= 0:
        bad.append("minBreedingTemperature is not above freezing: venting a room would not be an exit")
    pz = [e for e in ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "RSW_GizkaHediffs.xml")).getroot()
          if e.findtext("defName") == POISON][0]
    if not float(pz.findtext("lethalSeverity")) <= float(pz.findtext("maxSeverity")):
        bad.append("poison lethalSeverity is unreachable")
    if POISON not in _read("Defs/ThingDefs_Items/RSW_GizkaBait.xml"):
        bad.append("bait does not give the poison hediff")
    # donor patches: guarded by FindMod, never MayRequire on an Operation; scam stays pocket change
    p = _read("Patches/RSW_GizkaDonorPatches.xml")
    ET.fromstring(p.encode("utf-8"))
    if re.search(r"<Operation[^>]*MayRequire", p):
        bad.append("donor patch uses MayRequire on an Operation (inert in 1.6)")
    if p.count("<MarketValue>15</MarketValue>") != 2:
        bad.append("MarketValue 15 is not patched on both Gizka and RSW_Gizka")
    for dn in GIZKA_KINDS + ("EggGizkaFertilized", "RSW_EggGizkaFertilized"):
        if 'defName="%s"' % dn not in p:
            bad.append("donor patch does not target %s" % dn)
    if 'GizkaDefNames' not in _read("Source/RSW_GizkaSettings.cs"):
        bad.append("global-rate tuning table is gone")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimStarWars", "GizkaStowaway.md")):
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


def _same(ty, a, b):
    if ty == "bool":
        return str(a).lower() == str(b).lower()
    try:
        return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return False


def _raw(t, action, field, value=None):
    kw = dict(typeName=SETTINGS, action=action, field=field)
    if value is not None:
        kw["value"] = str(value)
    r = t.session.call("jawa/mod_settings_field", **kw)
    return r if isinstance(r, dict) else {}


def _map_centre(t):
    r = t.bridge_call("jawa/map_info")
    if _live(t) and isinstance(r, dict) and r.get("sizeX") and r.get("sizeZ"):
        return int(r["sizeX"]) // 2, int(r["sizeZ"]) // 2
    return t.anchor


def _spawn(t, kind, x, z, faction="player"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s) returned no pawn: %r" % (kind, r))
    t.session.track("pawn", pid, x=x, z=z)
    return pid


def _snap(t, pid):
    r = t.bridge_call("jawa/pawn_get", pawn=pid)
    if not _live(t):
        return {}
    snap = (r or {}).get("pawn") or r or {}
    return snap if isinstance(snap, dict) else {}


def _hediff_row(snap, name):
    if "hediffs" not in snap:
        return "unreadable", None
    for h in snap["hediffs"] or []:
        if isinstance(h, dict):
            if name in (h.get("def"), h.get("defName"), h.get("hediff")):
                return "present", h
        elif str(h) == name:
            return "present", {}
    return "absent", None


def _gizka_kind(t):
    """The first gizka PawnKindDef that resolves live, or None (neither the donor nor SWBestiary is loaded)."""
    for k in GIZKA_KINDS:
        r = t.bridge_call("jawa/get_defs", defs="PawnKindDef/" + k, fields="defName", limit=2)
        if _live(t) and isinstance(r, dict) and r.get("success") is not False and int(r.get("foundCount", 0)) == 1:
            return k
    return None


def _build_suite():
    suite = Suite("GizkaStowaway")
    suite.toggles = sorted(settings_fields())

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
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=60)
            if _live(t):
                _ok(r, "get_defs")
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    _fail("%d of %d defs resolved; notFound=%r" % (int(r.get("foundCount", 0)), len(names),
                                                                  (r.get("notFound") or [])[:8]))
        with _comp(t, "fecundity_comp_type_loaded", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="HediffDef/" + FECUNDITY, fields="comps", deep=True, limit=2)
            if _live(t):
                _ok(r, "get_defs fecundity comps")
                blob = str((((r.get("defs") or [{}])[0]).get("fields") or {}).get("comps"))
                if "GizkaFecundity" not in blob:
                    _unmeasured(t, "get_defs comps did not name GizkaFecundity (shape %s)" % blob[:120])

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with _comp(t, "settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                _fail("settings probe found no field (blind regex)")
        for field, (ty, _init) in sorted(settings_fields().items()):
            with _comp(t, "%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    _fail("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else (str(int(float(old)) + 1) if ty == "int" else str(float(old) + 1.0))
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        _fail("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        _fail("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    _fail("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("harmony_wiring")
    def harmony_wiring(t):
        for ty, method in hooks():
            with _comp(t, "%s_%s_patched_by_this_mod" % (ty, method), toggle=HOOK_TOGGLE.get(method)):
                r = t.bridge_call("jawa/harmony_patches", typeName=ty, methodName=method)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked about %s.%s: %s" % (ty, method, str(r)[:160]))
                owners = []
                for m in (r.get("methods") or []):
                    for kind in ("prefixes", "postfixes"):
                        owners.extend(p.get("owner") for p in (m.get(kind) or []))
                if HARMONY_ID not in owners:
                    _fail("%s.%s carries no patch from %s (owners: %s)"
                          % (ty, method, HARMONY_ID, sorted(set(o for o in owners if o))[:8]))

    @suite.chain("fecundity_state")
    def fecundity_state(t):
        with _comp(t, "gizka_with_fecundity_carries_it_control_does_not", toggle="stowawayEventsEnabled"):
            kind = _gizka_kind(t)
            if _live(t) and kind is None:
                _unmeasured(t, "no gizka PawnKindDef (Gizka / RSW_Gizka) resolves: neither the donor nor SWBestiary is loaded")
            cx, cz = _map_centre(t)
            t.clear_area(size=12)
            if _live(t):
                sick = _spawn(t, kind, cx, cz)
                ctrl = _spawn(t, kind, cx + 4, cz, faction="player")
                _ok(t.bridge_call("jawa/pawn_health", pawn=sick, action="add", hediff=FECUNDITY, severity=1.0),
                    "pawn_health add")
                state, _r = _hediff_row(_snap(t, sick), FECUNDITY)
                if state == "unreadable":
                    _unmeasured(t, "jawa/pawn_get has no hediffs list")
                if state != "present":
                    _fail("a gizka given %s does not carry it" % FECUNDITY)
                if _hediff_row(_snap(t, ctrl), FECUNDITY)[0] == "present":
                    _fail("the control gizka carries %s without being given it" % FECUNDITY)

    @suite.chain("bait_poison")
    def bait_poison(t):
        with _comp(t, "bait_item_and_recipe_resolve", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RSW_GizkaBait;RecipeDef/RSW_MakeGizkaBait;HediffDef/" + POISON,
                              fields="defName", limit=6)
            if _live(t):
                _ok(r, "get_defs bait")
                if r.get("notFound") or int(r.get("foundCount", 0)) != 3:
                    _fail("bait defs did not all resolve: %r" % r)
        with _comp(t, "poison_hediff_advances_on_a_gizka", beyond_toggle=True):
            kind = _gizka_kind(t)
            if _live(t) and kind is None:
                _unmeasured(t, "no gizka PawnKindDef resolves (donor / SWBestiary not loaded)")
            cx, cz = _map_centre(t)
            if _live(t):
                pid = _spawn(t, kind, cx + 8, cz)
                _ok(t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff=POISON, severity=0.15), "pawn_health add")
                s0 = _hediff_row(_snap(t, pid), POISON)[1] or {}
                if "severity" not in s0:
                    _unmeasured(t, "pawn_get hediff rows carry no severity field")
                t.wait_ticks(1500)
                s1 = _hediff_row(_snap(t, pid), POISON)[1]
                if s1 is None:
                    _fail("the poison hediff vanished from a live gizka after 1500 ticks")
                if float(s1.get("severity", -1)) <= float(s0["severity"]):
                    _fail("poison severity did not advance (%s -> %s)" % (s0["severity"], s1.get("severity")))

    @suite.chain("donor_patch")
    def donor_patch(t):
        with _comp(t, "gizka_market_value_flattened_to_15", beyond_toggle=True):
            kind = _gizka_kind(t)
            if _live(t) and kind is None:
                _unmeasured(t, "no gizka def resolves: the FindMod-guarded donor patch correctly no-ops without a donor")
            if _live(t):
                r = t.bridge_call("jawa/get_defs", defs="ThingDef/" + kind, fields="statBases", deep=True, limit=2)
                _ok(r, "get_defs gizka statBases")
                sb = (((r.get("defs") or [{}])[0]).get("fields") or {}).get("statBases")
                if not isinstance(sb, list) or not all(isinstance(x, dict) for x in sb):
                    _unmeasured(t, "get_defs returned statBases in an unreadable shape: %r" % (sb,))
                mv = [x for x in sb if "MarketValue" in (str(x.get("stat")), str(x.get("defName")), str(x.get("name")))]
                if not mv:
                    _unmeasured(t, "no MarketValue row in statBases: %r" % (sb[:6],))
                if abs(float(mv[0].get("value", -1)) - 15.0) > 1e-6:
                    _fail("%s MarketValue reads %r, patched to 15 (patch did not apply / stale deploy)" % (kind, mv[0]))

    @suite.chain("mechanics_unmeasured")
    def mechanics_unmeasured(t):
        for name, toggle, why in (
            ("gravship_landing_delivers_one_tame_gizka", "triggerGravship",
             "needs a real gravship landing (Scenario.PostGravshipLanded) and a 35 percent roll; the postfix is attached (harmony_wiring)"),
            ("salvage_trade_quest_hooks_deliver", "triggerSalvage",
             "wreck deconstruction, a completed trade and a quest success each need a driven game event and a chance roll"),
            ("fecundity_replicates_while_fed_and_warm", "breedingRate",
             "a replication interval of ~4 days needs game days of ticks and a fed warm gizka"),
            ("population_cap_stops_breeding", "populationCap",
             "needs a colony grown to the cap (22 per map) over game days"),
            ("infestation_stage_chews_powered_buildings", "chewingEnabled",
             "needs the Infestation stage (~3x the cute count) with a powered building in a shared room"),
            ("cold_below_breeding_gate_stalls_replication", "stowawayEventsEnabled",
             "needs a gizka room vented below 12 C and days of ticks; no verb sets a room temperature"),
            ("cull_weighs_on_watching_colonists", "cullGuiltEnabled",
             "needs a slaughter with colonist witnesses; the Pawn.Kill prefix is attached (harmony_wiring)"),
            ("global_breeding_slider_rescales_donor_fields", "globalBreedingRate",
             "RSW_GizkaDonorTuning.Apply runs on WriteSettings or its button, not on a bridge field write; the live "
             "egg-layer fields have no reader here"),
        ):
            with _comp(t, name, toggle=toggle):
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
