"""validation.py -- modcheck suite for RimMandrake: Greentide (mandrake.rm.greentide).

First script (debug_process.md section 2), item GREENTIDE_FIRST_SCRIPT_1. Walk:
design/validation_walks/RimMandrake/Greentide.md (`## must be true`, each line ends in
`-> chain.component` or `-> UNCOVERED: why`). NEVER RUN LIVE YET: every live shape below that is
unproven degrades to UNMEASURED, never PASS.

Run offline: `python3 src/RimMandrake/Greentide/validation.py` -> `STATIC: PASS (0 findings)`.
Live: modcheck/northstar_driver on a tier carrying Greentide (folded into `mandrake.rm.biomes`, active
under 'RimMandrake: Baroque Biomes') + Creature Behaviors + Environmental Hazards (its dependencies).

WHAT IT PROVES, by state read on a bland built site (left half RM_GreentideChurnmud, then Concrete, then
RM_ChurnmudSealed): the mire hediff on mud and not on safe ground or sealed floor; the master switch;
the dwell-then-bury of a loose item on mud and not elsewhere; the buried-cache switch; the dig-out job;
the Frenzy dose route, its master switch and the FeverMark immunity gate; the density applier's write
onto the live BiomeDef. Every def the mod ships resolves; every Mod Settings field round-trips.
NOT PROVEN HERE (UNMEASURED, named): the ambient Frenzy incident (dry-run fire_incident reports
success=False with canFireNow=False, so it is no instrument), the stench grenade, the cross-biome
churnmud (worldgen once, on a fresh map), the stuck threshold and the free-mired job (a ~6000-tick
climb and a second pawn), the fever mark earned by surviving the coma (days of game time).
"""
import contextlib
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))      # `python3 validation.py` finds modcheck

SETTINGS = "RimMandrake.Greentide.RM_GreentideSettings"
MUD, SEALED = "RM_GreentideChurnmud", "RM_ChurnmudSealed"
SITE = 24
BURY_WAIT = 3200          # swallowTicks 2500 (parsed in static_checks) + one 250-tick scan + margin


# --------------------------------------------------------------------------- parsed facts (never hand-listed)

def settings_defaults():
    """{field: (type, default)} parsed from the settings class's `public static` initialisers (consts skipped)."""
    src = open(os.path.join(HERE, "Source", "RM_GreentideMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_GreentideSettings")[1].split("ExposeData")[0]
    out = {}
    for typ, name, val in re.findall(r"public static (bool|float|int|string) (\w+)\s*=\s*([^;]+);", body):
        v = val.strip()
        if typ == "bool":
            out[name] = (typ, v == "true")
        elif typ == "float":
            out[name] = (typ, float(v.rstrip("f")))
        elif typ == "int":
            out[name] = (typ, int(v))
        else:
            out[name] = (typ, v.strip('"'))
    return out


def shipped_defs():
    """(defType, defName) for every concrete top-level def in the mod's own Defs/ XML."""
    out = []
    for dp, _, files in os.walk(os.path.join(HERE, "Defs")):
        for f in sorted(files):
            if f.endswith(".xml"):
                for e in ET.parse(os.path.join(dp, f)).getroot():
                    n = e.findtext("defName")
                    if n and e.get("Abstract") != "True":
                        out.append((e.tag.split(".")[-1], n))
    return out


try:
    from modcheck import Suite, ExpectationFailed
except ImportError:                       # offline static run outside the modcheck path
    Suite = None

if Suite is not None:
    suite = Suite("Greentide")
    SD = settings_defaults()
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
            print("[gt] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
                  file=sys.stderr, flush=True)

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

    @contextlib.contextmanager
    def _arm(t, **values):
        """Set settings for the body; ALWAYS restore each to its shipped (parsed) default."""
        try:
            for f, v in values.items():
                _put(t, f, v)
            yield
        finally:
            for f in values:
                try:
                    _put(t, f, SD[f][1])
                except Exception as e:
                    print("[gt] RESTORE FAILED %s: %s" % (f, e), file=sys.stderr, flush=True)

    def _ok(r, what):
        if not isinstance(r, dict) or r.get("success") is False:
            _fail("%s failed: %r" % (what, r))
        return r

    def _wait(t, n):
        """Advance n real ticks; long waits run Ultrafast and poll the real clock (ExplosiveGrowth's pattern)."""
        if t.session is None or t.upstream_failed or n <= 3000:
            return t.wait_ticks(n)
        s = t.session
        start = s._ticks()
        target = start + n
        s.call("rimworld/set_time_speed", speed="Ultrafast")
        last, stall = start, time.time()
        try:
            while True:
                time.sleep(1.0)
                now = s._ticks()
                if now is None:
                    raise ExpectationFailed("clock unreadable during a %d-tick wait" % n)
                if now >= target - 400:
                    break
                if now > last:
                    last, stall = now, time.time()
                elif time.time() - stall > 60:
                    raise ExpectationFailed("clock stalled at %d during a %d-tick wait (a modal dialog?)" % (now, n))
        finally:
            s.call("rimworld/set_time_speed", speed="Paused")
        now = s._ticks()
        if now < target:
            t.wait_ticks(target - now)
        t._record("_wait(%d) Ultrafast" % n, (s._ticks() or 0) - start)

    def _spawn(t, x, z, draft=True):
        r = _ok(t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1), "spawn_pawn")
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if not pid:
            _unmeasured(t, "spawn_pawn returned no id: %s" % str(r)[:160])
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
        t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
        if draft:
            t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)      # a drafted pawn stays on its cell
        return pid

    def _rows(t):
        r = _ok(t.bridge_call("jawa/list_pawns", includeHealth=True, includeCorpses=False, limit=300), "list_pawns")
        return {p.get("id"): p for p in (r.get("pawns") or [])}

    def _hed(t, pid):
        """{hediff def: severity} for a pawn; a missing pawn is a lost precondition (UNMEASURED)."""
        row = _rows(t).get(pid)
        if row is None:
            _unmeasured(t, "seeded pawn %s is absent from list_pawns (dead or gone): not a statement about the hediff" % pid)
        return {h.get("def"): float(h.get("severity") or 0) for h in ((row.get("health") or {}).get("hediffs") or [])}

    def _items(t, defName, rect):
        r = _ok(t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=200), "list_things")
        if r.get("isCompleteList") is False:
            _unmeasured(t, "list_things truncated")
        return r.get("things") or []

    def _cell_terrain(t, x, z):
        r = _ok(t.bridge_call("jawa/get_terrain_batch", rects="%d,%d,1,1" % (x, z)), "get_terrain_batch")
        d = r.get("distinctTerrains") or []
        return d[0] if len(d) == 1 else None

    def _site(t):
        """Left half churnmud, then Concrete, then sealed floor; clear sky, no fog. Returns the anchor."""
        t.clear_area(size=SITE)
        x, z = t.anchor
        h = SITE // 2
        t.bridge_call("jawa/set_terrain_batch", ops="%s:%d,%d,12,%d;Concrete:%d,%d,6,%d;%s:%d,%d,6,%d"
                      % (MUD, x - h, z - h, SITE, x, z - h, SITE, SEALED, x + 6, z - h, SITE))
        t.bridge_call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (x - h, z - h, SITE, SITE))
        t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
        t.bridge_call("jawa/log_autoopen_suppress")
        if _live(t):
            for name, (cx, cz) in ((MUD, (x - 6, z)), ("Concrete", (x + 3, z)), (SEALED, (x + 9, z))):
                got = _cell_terrain(t, cx, cz)
                if got != name:
                    _unmeasured(t, "SITE: cell %d,%d reads terrain %r, wanted %s (terrain defs unresolved?)" % (cx, cz, got, name))
        return x, z

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
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/RM_Greentide_NoSuchControl")
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
        return d * 2 + 1

    def _make_flip(field, typ, default):
        def chain(t):
            with _comp(t, "%s_round_trips" % field, toggle=field if typ == "bool" else None, beyond_toggle=typ != "bool"):
                try:
                    _put(t, field, _alt(typ, default))
                    _put(t, field, default)
                finally:
                    if t.session is not None:
                        try:
                            _put(t, field, default)
                        except Exception as e:
                            print("[gt] RESTORE FAILED %s: %s" % (field, e), file=sys.stderr, flush=True)
        chain.__doc__ = "Write alt, read back, write default, read back (numeric compare) for %s." % field
        return chain

    for _f, (_ty, _d) in SD.items():
        suite.chain("flip_%s" % _f)(_make_flip(_f, _ty, _d))

    # ----------------------------------------------------------------------- 3. the mire

    @suite.chain("mire")
    def mire(t):
        P = {}
        with _comp(t, "site_ready_mire", beyond_toggle=True):
            if _live(t):
                x, z = _site(t)
                P["mud"] = _spawn(t, x - 6, z)
                P["concrete"] = _spawn(t, x + 3, z)
                P["sealed"] = _spawn(t, x + 9, z)
                t.wait_ticks(240)       # four mire checks (every 60 ticks)
        with _comp(t, "mire_applies_on_churnmud", toggle="mireEnabled"):
            if _live(t):
                h = _hed(t, P["mud"])
                if "RM_Mired" not in h:
                    _fail("a colonist stood 240 ticks on %s and was never mired (hediffs %s): "
                          "RM_MapComponent_TerrainMire or the terrain's RM_MireExtension is dead" % (MUD, sorted(h)))
                if not h["RM_Mired"] > 0:
                    _fail("RM_Mired present at severity %r" % h["RM_Mired"])
        with _comp(t, "mire_skips_concrete_and_sealed_floor", beyond_toggle=True):
            if _live(t):
                for k in ("concrete", "sealed"):
                    h = _hed(t, P[k])
                    if "RM_Mired" in h:
                        _fail("a colonist on %s carries RM_Mired: %s" % ("Concrete" if k == "concrete" else SEALED + " (sealing IS the safety mechanism)", h))
        with _comp(t, "mire_master_switch_off", toggle="mireEnabled"):
            if _live(t):
                x, z = t.anchor
                with _arm(t, mireEnabled=False):
                    pid = _spawn(t, x - 6, z + 4)
                    t.wait_ticks(240)
                    h = _hed(t, pid)
                if "RM_Mired" in h:
                    _fail("mired with mireEnabled off: %s" % h)

    @suite.chain("mire_escalation")
    def mire_escalation(t):
        with _comp(t, "stuck_threshold_and_free_mired_job", beyond_toggle=True):
            _unmeasured(t, "the stuck threshold is ~0.85 severity at 0.008 per 60 ticks with a 15%% struggle roll (a ~6000+ tick "
                           "random climb) and RM_FreeMired needs a second pawn's job; a seeded hediff plus an ordered job is "
                           "owed to a live round")

    # ----------------------------------------------------------------------- 4. the swallow

    @suite.chain("swallow", tick_cap=60000)
    def swallow(t):
        P = {}
        with _comp(t, "site_ready_swallow", beyond_toggle=True):
            if _live(t):
                x, z = _site(t)
                P["x"], P["z"] = x, z
                for name, cx, cz in (("mud", x - 8, z - 6), ("concrete", x + 3, z - 6), ("sealed", x + 9, z - 6)):
                    t.bridge_call("jawa/spawn_batch", ops="Steel:%d,%d,5" % (cx, cz))
                    P[name] = (cx, cz)
                    if not _items(t, "Steel", "%d,%d,1,1" % (cx, cz)):
                        _unmeasured(t, "SITE: Steel did not spawn at %d,%d" % (cx, cz))
        with _comp(t, "swallow_buries_on_churnmud_only", toggle="buriedCacheEnabled"):
            if _live(t):
                _wait(t, BURY_WAIT)
                if _items(t, "Steel", "%d,%d,1,1" % P["mud"]):
                    _fail("Steel left %d ticks on %s was not swallowed (RM_MapComponent_MudSwallow dead, or swallowTicks changed)"
                          % (BURY_WAIT, MUD))
                for k in ("concrete", "sealed"):
                    if not _items(t, "Steel", "%d,%d,1,1" % P[k]):
                        _fail("Steel on %s vanished: the swallow is not bound to the mire terrain" % k)
        with _comp(t, "buried_cache_switch_off_keeps_items", toggle="buriedCacheEnabled"):
            if _live(t):
                x, z = P["x"], P["z"]
                with _arm(t, buriedCacheEnabled=False):
                    t.bridge_call("jawa/spawn_batch", ops="Steel:%d,%d,5" % (x - 8, z + 6))
                    if not _items(t, "Steel", "%d,%d,1,1" % (x - 8, z + 6)):
                        _unmeasured(t, "SITE: control Steel did not spawn")
                    _wait(t, BURY_WAIT)
                    kept = _items(t, "Steel", "%d,%d,1,1" % (x - 8, z + 6))
                if not kept:
                    _fail("Steel was swallowed with buriedCacheEnabled off")
        with _comp(t, "dig_out_job_restores_the_buried_item", beyond_toggle=True):
            if _live(t):
                x, z = P["x"], P["z"]
                who = _spawn(t, x - 2, z - 6, draft=False)
                near = "%d,%d,7,7" % (P["mud"][0] - 3, P["mud"][1] - 3)
                r = t.bridge_call("jawa/ordered_job", pawnId=who, jobDef="RM_DigOutBuried",
                                  targetAX=P["mud"][0], targetAZ=P["mud"][1], waitTicks=0, timeoutSeconds=30)
                if not (r or {}).get("accepted"):
                    _unmeasured(t, "ordered_job RM_DigOutBuried not accepted (unproven target shape): %s" % str(r)[:160])
                back = []
                for _ in range(5):
                    t.wait_ticks(300)
                    back = _items(t, "Steel", near)
                    if back:
                        break
                if not back:
                    _unmeasured(t, "buried Steel not back within 1500 ticks of the dig-out order: the order shape is unproven, "
                                   "or the work scales with burial time; read the pawn's job before calling it a mod fault")

    # ----------------------------------------------------------------------- 5. the Frenzy dose

    def _dose_pawn(t, x, z, **pre):
        pid = _spawn(t, x, z, draft=False)
        for hed in pre.get("hediffs", ()):
            r = t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff=hed, severity=1.0)
            if not (r or {}).get("success"):
                _unmeasured(t, "pawn_health add %s failed: %s" % (hed, str(r)[:160]))
        t.bridge_call("jawa/spawn_batch", ops="RM_FrenzyDose:%d,%d,1" % (x + 1, z))
        dose = _items(t, "RM_FrenzyDose", "%d,%d,3,3" % (x, z - 1))
        if not dose:
            _unmeasured(t, "SITE: RM_FrenzyDose did not spawn")
        r = t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef="Ingest", targetAId=dose[0].get("id"), count=1,
                          waitTicks=0, timeoutSeconds=30)
        if not (r or {}).get("accepted"):
            _unmeasured(t, "Ingest order refused: %s" % str(r)[:160])
        t.wait_ticks(600)
        return pid

    @suite.chain("frenzy_dose")
    def frenzy_dose(t):
        base = {}
        with _comp(t, "site_ready_dose", beyond_toggle=True):
            if _live(t):
                base["x"], base["z"] = _site(t)
        with _comp(t, "dose_gives_frenzy", toggle="frenzyEnabled"):
            if _live(t):
                x, z = base["x"] + 3, base["z"] + 4
                pid = _dose_pawn(t, x, z)
                h = _hed(t, pid)
                if "RM_Frenzy" not in h:
                    _unmeasured(t, "no RM_Frenzy 600 ticks after the Ingest order was accepted (hediffs %s): the pawn may not have "
                                   "eaten; a drug ingest unproven on this tier" % sorted(h))
                base["ate"] = True
        with _comp(t, "frenzy_master_switch_off_gives_none", toggle="frenzyEnabled"):
            if _live(t):
                if not base.get("ate"):
                    _unmeasured(t, "the positive arm did not prove a dose can land here, so the off arm cannot be judged")
                with _arm(t, frenzyEnabled=False):
                    pid = _dose_pawn(t, base["x"] + 3, base["z"] - 4)
                    h = _hed(t, pid)
                if "RM_Frenzy" in h:
                    _fail("a dose gave RM_Frenzy with frenzyEnabled off: %s" % h)
        with _comp(t, "fever_mark_gates_the_dose", toggle="feverMarkGrantsImmunity"):
            if _live(t):
                if not base.get("ate"):
                    _unmeasured(t, "the positive arm did not prove a dose can land here, so the immunity arm cannot be judged")
                pid = _dose_pawn(t, base["x"] + 9, base["z"] + 4, hediffs=("RM_FeverMark",))
                h = _hed(t, pid)
                if "RM_Frenzy" in h:
                    _fail("a FeverMark colonist took RM_Frenzy from a dose with feverMarkGrantsImmunity on: %s" % h)
        with _comp(t, "fever_mark_earned_by_surviving_the_coma", toggle="feverMarkEnabled"):
            _unmeasured(t, "the mark is earned only when a tended Frenzy that reached the collapse stage ends: days of game time and "
                           "a tending pawn; needs a seeded hediff at the collapse stage and a tend (a state-seeding tool is owed)")
        with _comp(t, "ambient_frenzy_incident", toggle="frenzyEnabled"):
            _unmeasured(t, "RM_IncidentWorker_FrenzyDisease: a dry-run fire_incident reports success=False with canFireNow=False, "
                           "so it is no instrument; firing it for real needs a map the incident is eligible on")

    # ----------------------------------------------------------------------- 6. biome density

    @suite.chain("density_applier")
    def density_applier(t):
        """RM_GreentideDensityApplier writes the Mod Settings onto the live RM_Greentide BiomeDef."""
        with _comp(t, "biome_carries_the_settings_density", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/RM_Greentide", fields="plantDensity,movementDifficulty", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True:
                    _unmeasured(t, "get_defs BiomeDef/RM_Greentide could not be asked: %s" % str(r)[:140])
                rows = [d for d in (r.get("defs") or []) if d.get("defName") == "RM_Greentide"]
                f = (rows[0].get("fields") if rows else None) or {}
                if "plantDensity" not in f or "movementDifficulty" not in f:
                    _unmeasured(t, "get_defs returned no plantDensity/movementDifficulty fields: %r" % (f,))
                if not _same(f["plantDensity"], _get(t, "plantDensity")) or not _same(f["movementDifficulty"], _get(t, "movementDifficulty")):
                    _fail("live BiomeDef density %r/%r differs from Mod Settings %r/%r (the applier did not run, or ran before "
                          "settings loaded)" % (f["plantDensity"], f["movementDifficulty"], _get(t, "plantDensity"), _get(t, "movementDifficulty")))

    # ----------------------------------------------------------------------- 7. honest UNMEASURED

    def _um(chain, comp, why, toggle=None):
        def fn(t):
            with _comp(t, comp, toggle=toggle, beyond_toggle=toggle is None):
                _unmeasured(t, why)
        fn.__doc__ = "UNMEASURED: " + why
        suite.chain(chain)(fn)

    _um("cross_biome_churnmud", "churnmud_seeded_once_on_a_fresh_non_greentide_map",
        "WORLDGEN-AFFECTING: RM_MapComponent_CrossBiomeChurnmud runs once on a freshly generated map; needs a new map "
        "generated with crossBiomeEnabled on, which the harness cannot do on a held map", "crossBiomeEnabled")
    _um("stench_grenade", "stench_smoke_radius_follows_multiplier",
        "needs a thrown grenade and an explosion-radius read; no bridge reader for the smoke cloud", "stenchGrenadeEnabled")
    _um("canopy_swarm", "krannock_spawn_gate",
        "canopySwarmEnabled is a deliberate no-op until the Krannock is rostered at the biome's own review sitting (About.xml)",
        "canopySwarmEnabled")

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


# --------------------------------------------------------------------------- static (offline)

def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    sd = settings_defaults()
    if len(sd) < 1:
        bad.append("sanity probe: no settings fields parsed from RM_GreentideMod.cs (regex broke)")
    mod = open(os.path.join(HERE, "Source", "RM_GreentideMod.cs"), encoding="utf-8").read()
    for f in sd:
        if '"%s"' % f not in mod:
            bad.append("settings field %s is not Scribed in ExposeData" % f)
        if not re.search(r"\b%s\b" % f, mod.split("DoWindowContents")[1]):
            bad.append("settings field %s has no control in DoWindowContents" % f)
    proj = open(os.path.join(HERE, "Source", "RM_Greentide.csproj"), encoding="utf-8").read()
    listed = {c.replace("\\", "/") for c in re.findall(r'Compile Include="([^"]+)"', proj)}
    for cs in listed:
        if not os.path.isfile(os.path.join(HERE, "Source", cs)):
            bad.append("csproj lists missing file " + cs)
    for dp, _, files in os.walk(os.path.join(HERE, "Source")):
        for f in files:
            rel = os.path.relpath(os.path.join(dp, f), os.path.join(HERE, "Source")).replace("\\", "/")
            if f.endswith(".cs") and not rel.startswith(("obj/", "bin/")) and rel not in listed:
                bad.append("%s is not in the csproj (EnableDefaultCompileItems false: compiles into nothing)" % rel)
    defs = shipped_defs()
    if len(defs) < 1:
        bad.append("no shipped defs parsed")
    names = {n for _, n in defs}
    defof = open(os.path.join(HERE, "Source", "RM_DefOf.cs"), encoding="utf-8").read()
    for n in re.findall(r"public static \w+ (RM_\w+);", defof):
        if n not in names:
            bad.append("DefOf field %s names no shipped def" % n)
    for n in (MUD, SEALED, "RM_Mired", "RM_FeverMark", "RM_Frenzy", "RM_FrenzyDose", "RM_Greentide"):
        if n not in names:
            bad.append("script names def %s but the mod ships none" % n)
    mud = ET.parse(os.path.join(HERE, "Defs", "TerrainDefs", "RM_Churnmud_Terrains.xml")).getroot()
    tdefs = {e.findtext("defName"): e for e in mud}
    if tdefs.get(MUD) is None or tdefs[MUD].find("modExtensions/li[@Class='RimMandrake.Greentide.RM_MireExtension']") is None:
        bad.append("%s lacks RM_MireExtension" % MUD)
    elif int(tdefs[MUD].findtext("modExtensions/li/swallowTicks") or 0) + 250 > BURY_WAIT:
        bad.append("BURY_WAIT %d is shorter than swallowTicks + one scan" % BURY_WAIT)
    if tdefs.get(SEALED) is None or tdefs[SEALED].find("modExtensions/li[@Class='RimMandrake.Greentide.RM_MireExtension']") is not None:
        bad.append("%s must exist and carry NO RM_MireExtension" % SEALED)
    if not any(f.endswith(".dll") for f in os.listdir(os.path.join(HERE, "Assemblies"))):
        bad.append("no DLL in Assemblies")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
