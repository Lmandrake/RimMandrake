"""validation.py -- modcheck suite for RimUtinni: The Reckoning (mandrake.rut.eggreckoning, folder EggReckoning).

First script (debug_process.md section 2), item EGG_RECKONING_FIRST_SCRIPT_1. Walk:
design/validation_walks/RimUtinni/EggReckoning.md (`## must be true`, each line ends in
`-> chain.component` or `-> UNCOVERED: why`). NEVER RUN LIVE YET: every live shape below that is unproven
degrades to UNMEASURED, never PASS.

Run offline: `python3 src/RimUtinni/EggReckoning/validation.py` -> `STATIC: PASS (0 findings)`.
Live: modcheck/northstar_driver on a tier carrying RimUtinni Patches (the Hutt Cartel faction) + the composed
biomes mod (Webwork's egg and spider; Webwork is folded into `mandrake.rm.biomes`) + this mod, all five DLCs.

WHAT IT PROVES, by state read:
  * defs_resolve: every def the mod ships, and every def its C# looks up by name (the egg, the spider kind,
    the Hutt Cartel faction), resolves live; a control probe reads absent.
  * flip_reckoningEnabled: the one Mod Settings field round-trips.
  * route_wiring: with the toggle on, the load-time patcher leaves the shipped routes in place (the rumor
    route in the random pool at 0.15, the Cartel offer trader-given and not random-selectable).
  * quest_offer: the Cartel-offer quest generates when the world has a Cartel settlement in reach.
  * egg_never_hatches_outside_the_quest: ruling 2 and 7, as a guard: an egg left on a plain map for an hour
    stays an egg and no spider appears.
NOT PROVEN HERE (UNMEASURED, named): the toggle-off effect (the patcher runs only from WriteSettings and
the bridge's setter writes a static field without calling it), the three solution paths, the plant watcher,
the night-window hatch, the discovery roll and its goodwill cost (an outpost site map plus a night).
"""
import contextlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))      # `python3 validation.py` finds modcheck

SETTINGS = "RimMandrake.Utinni.EggReckoning.EggReckoningSettings"
SETTINGS_CS = os.path.join(HERE, "Source", "EggReckoningSettings.cs")
QUEST_XML = os.path.join(HERE, "Defs", "QuestScriptDefs", "RUT_Reckoning.xml")
RUMOR, OFFER = "RUT_Reckoning_Rumor", "RUT_Reckoning_CartelOffer"
EGG, SPIDER = "RM_OllathrixEgg", "RM_Ollathrix"
WEBWORK = os.path.join(HERE, "..", "..", "RimMandrake", "Webwork")


# --------------------------------------------------------------------------- parsed facts (never hand-listed)

def settings_defaults():
    """{field: (type, default)} parsed from the settings class's `public static` initialisers."""
    src = open(SETTINGS_CS, encoding="utf-8").read()
    body = src.split("class EggReckoningSettings")[1].split("ExposeData")[0]
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


def code_looked_up_defs():
    """Defs another mod ships that this mod's C# looks up by name: `DefDatabase<T>.GetNamedSilentFail("X")` and the
    Cartel faction constant. A missing one is a silent no-op in the mod, so the script resolves each live."""
    out, seen = [], set()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if not fn.endswith(".cs"):
            continue
        src = open(os.path.join(HERE, "Source", fn), encoding="utf-8").read()
        found = re.findall(r"DefDatabase<(\w+)>\.GetNamedSilentFail\(\"(\w+)\"\)", src)
        found += [("FactionDef", m) for m in re.findall(r'HuttCartelFactionDefName\s*=\s*"(\w+)"', src)]
        for d in found:
            if d not in seen and d[1] not in (RUMOR, OFFER):
                seen.add(d)
                out.append(d)
    return out


def hatch_constants():
    src = open(os.path.join(HERE, "Source", "RM_QuestPart_EggHatch.cs"), encoding="utf-8").read()
    return {k: float(re.search(r"public \w+ %s = ([\d.]+)f?;" % k, src).group(1))
            for k in ("fixedBiologicalAgeYears", "discoveryChancePerHour", "nightStartHour", "nightEndHour")}


def route_values():
    """{defName: {field: text}} for the two concrete routes, from the XML (the parent supplies nothing numeric)."""
    root = ET.parse(QUEST_XML).getroot()
    out = {}
    for e in root.findall("QuestScriptDef"):
        n = e.findtext("defName")
        if n:
            out[n] = {k: e.findtext(k) for k in ("rootSelectionWeight", "rootMinPoints", "randomlySelectable")}
            out[n]["givenBy"] = [li.text for li in e.findall("givenBy/li")]
    return out


try:
    from modcheck import Suite, ExpectationFailed
except ImportError:                       # offline static run outside the modcheck path
    Suite = None

if Suite is not None:
    suite = Suite("EggReckoning")
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
            print("[egr] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
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

    def _ok(r, what):
        if not isinstance(r, dict) or r.get("success") is False:
            _fail("%s failed: %r" % (what, r))
        return r

    # ----------------------------------------------------------------------- 1. defs_resolve

    def _resolve(t, pairs, what):
        want = ["%s/%s" % x for x in pairs]
        for i in range(0, len(want), 25):
            chunk = want[i:i + 25]
            r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=100)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True:
                    _unmeasured(t, "get_defs could not be asked: %s" % str(r)[:140])
                if r.get("notFound") or r.get("foundCount") != len(chunk):
                    _fail("%s did not load (a def with an unresolvable field is discarded silently): "
                          "notFound=%r foundCount=%r of %d" % (what, r.get("notFound"), r.get("foundCount"), len(chunk)))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        """Every def the mod ships, and every def its C# looks up by name, resolves live; a control reads absent."""
        with _comp(t, "shipped_defs_resolve", beyond_toggle=True):
            _resolve(t, shipped_defs(), "shipped defs")
        with _comp(t, "defs_the_code_looks_up_resolve", beyond_toggle=True):
            _resolve(t, code_looked_up_defs(), "defs named by the C# (egg, spider kind, Cartel faction)")
        with _comp(t, "control_absent_def_reads_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="QuestScriptDef/RUT_Reckoning_NoSuchControl")
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True:
                    _unmeasured(t, "control ask failed: %s" % str(r)[:140])
                if r.get("foundCount") != 0 or not r.get("notFound"):
                    _fail("the probe cannot say absent: control returned %r" % r)

    # ----------------------------------------------------------------------- 2. settings round trip

    def _alt(typ, d):
        if typ == "bool":
            return not d
        if typ == "int":
            return d + 1
        if typ == "string":
            return "x"
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
                            print("[egr] RESTORE FAILED %s: %s" % (field, e), file=sys.stderr, flush=True)
        chain.__doc__ = "Write alt, read back, write default, read back (numeric compare) for %s." % field
        return chain

    for _f, (_ty, _d) in SD.items():
        suite.chain("flip_%s" % _f)(_make_flip(_f, _ty, _d))

    # ----------------------------------------------------------------------- 3. route wiring

    def _fields(t, name, fields):
        r = t.bridge_call("jawa/get_defs", defs="QuestScriptDef/%s" % name, fields=fields, deep=True, limit=2)
        if not _live(t):
            return {}
        if not isinstance(r, dict) or r.get("success") is not True:
            _unmeasured(t, "get_defs QuestScriptDef/%s could not be asked: %s" % (name, str(r)[:140]))
        rows = [d for d in (r.get("defs") or []) if d.get("defName") == name]
        if not rows:
            _fail("QuestScriptDef %s is not in the running game" % name)
        return rows[0].get("fields") or {}

    @suite.chain("route_wiring")
    def route_wiring(t):
        want = route_values()
        with _comp(t, "toggle_on_leaves_the_rumor_route_in_the_pool", toggle="reckoningEnabled"):
            f = _fields(t, RUMOR, "rootSelectionWeight,rootMinPoints")
            if _live(t):
                if _get(t, "reckoningEnabled").strip().lower() != "true":
                    _unmeasured(t, "reckoningEnabled is not at its shipped default on entry, so the on-state cannot be judged")
                if "rootSelectionWeight" not in f:
                    _unmeasured(t, "get_defs returned no rootSelectionWeight field: %r" % (f,))
                if not _same(f["rootSelectionWeight"], want[RUMOR]["rootSelectionWeight"]):
                    _fail("with reckoningEnabled on, %s weight is %r, shipped %s (the patcher zeroed it, or the def changed)"
                          % (RUMOR, f["rootSelectionWeight"], want[RUMOR]["rootSelectionWeight"]))
                if "rootMinPoints" in f and not _same(f["rootMinPoints"], want[RUMOR]["rootMinPoints"]):
                    _fail("%s rootMinPoints %r, shipped %s" % (RUMOR, f["rootMinPoints"], want[RUMOR]["rootMinPoints"]))
        with _comp(t, "toggle_on_leaves_the_cartel_offer_trader_given_and_not_random", toggle="reckoningEnabled"):
            f = _fields(t, OFFER, "givenBy,randomlySelectable,rootSelectionWeight")
            if _live(t):
                if "givenBy" not in f or "randomlySelectable" not in f:
                    _unmeasured(t, "get_defs returned no givenBy/randomlySelectable fields: %r" % (f,))
                if "Traders" not in json.dumps(f["givenBy"]):
                    _fail("with reckoningEnabled on, %s givenBy is %r, shipped %s (the patcher cleared it)"
                          % (OFFER, f["givenBy"], want[OFFER]["givenBy"]))
                if str(f["randomlySelectable"]).lower() != "false":
                    _fail("%s is randomly selectable (%r): the Cartel offer must come only from a trader"
                          % (OFFER, f["randomlySelectable"]))
                if "rootSelectionWeight" in f and _same(f["rootSelectionWeight"], 0) is False:
                    _fail("%s carries a random-pool weight %r although it is trader-given only" % (OFFER, f["rootSelectionWeight"]))
        with _comp(t, "toggle_off_removes_both_routes", toggle="reckoningEnabled"):
            _unmeasured(t, "EggReckoningPatcher.Apply runs only from the mod's WriteSettings and at startup; jawa/mod_settings_field "
                           "writes the static field without calling either, and rimworld/update_mod_settings cannot reach a static "
                           "field, so flipping the toggle live cannot move the def fields (a companion [Tool] that calls Apply is owed)")

    # ----------------------------------------------------------------------- 4. the offer

    @suite.chain("quest_offer")
    def quest_offer(t):
        with _comp(t, "cartel_offer_generates_when_the_world_allows", beyond_toggle=True):
            if _live(t):
                before = {json.dumps(q, sort_keys=True) for q in
                          (_ok(t.bridge_call("jawa/quest_lifecycle", action="list"), "quest_lifecycle(list)").get("quests") or [])}
                r = t.bridge_call("jawa/fire_quest", questDef=OFFER, accept=False)
                if not (r or {}).get("success"):
                    _unmeasured(t, "fire_quest could not generate %s (RM_QuestNode_GetHuttCartelSettlement needs a RUT_Jawa_HuttCartel "
                                   "settlement within 80 tiles, and an Outpost-capable faction for the site): %s" % (OFFER, str(r)[:300]))
                rows = _ok(t.bridge_call("jawa/quest_lifecycle", action="list"), "quest_lifecycle(list)").get("quests") or []
                new = [q for q in rows if json.dumps(q, sort_keys=True) not in before]
                if not new:
                    _unmeasured(t, "quest_lifecycle(list) shows no new quest after fire_quest succeeded: %s" % str(r)[:200])
                txt = json.dumps(new[0], sort_keys=True).lower()
                if "ollathrix" not in txt and re.search(r"descr|text", txt):
                    _fail("the generated quest's text does not offer the egg path (no 'ollathrix' in it): %s" % txt[:300])

    # ----------------------------------------------------------------------- 5. the egg never hatches outside the quest

    @suite.chain("egg_guard", tick_cap=12000)
    def egg_guard(t):
        """Rulings 2 and 7: RM_OllathrixEgg carries no hatcher and only the quest's own part spawns a spider."""
        P = {}
        with _comp(t, "site_ready_egg_and_colonist", beyond_toggle=True):
            if _live(t):
                t.clear_area(size=12)
                x, z = t.anchor
                P["x"], P["z"] = x, z
                t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (EGG, x, z))
                P["col"] = t.spawn_pawn("Colonist")
                r = _ok(t.bridge_call("jawa/list_things", defName=EGG, rect="%d,%d,3,3" % (x - 1, z - 1), limit=10), "list_things")
                if not (r.get("things") or []):
                    _unmeasured(t, "SITE: %s did not spawn at %d,%d (egg def unresolved?)" % (EGG, x, z))
        with _comp(t, "egg_stays_an_egg_and_no_spider_appears", beyond_toggle=True):
            if _live(t):
                t.wait_ticks(3000)
                r = _ok(t.bridge_call("jawa/list_things", defName=EGG, rect="%d,%d,3,3" % (P["x"] - 1, P["z"] - 1), limit=10), "list_things")
                pr = _ok(t.bridge_call("jawa/list_pawns", includeCorpses=False, limit=300), "list_pawns")
                rows = pr.get("pawns") or []
                if P.get("col") not in {p.get("id") for p in rows}:
                    _unmeasured(t, "control colonist %s missing from list_pawns: the pawn read cannot see pawns" % P.get("col"))
                spiders = [p for p in rows if SPIDER.lower() in json.dumps(p).lower()]
                if spiders:
                    _fail("a %s pawn exists on a map with an unplanted egg and no quest: %s" % (SPIDER, json.dumps(spiders[0])[:200]))
                if not (r.get("things") or []):
                    _unmeasured(t, "the egg is gone after 3000 ticks with no spider present; rot (15 days) cannot explain it, "
                                   "so something removed it and the guard cannot judge")

    # ----------------------------------------------------------------------- 6. honest UNMEASURED

    def _um(chain, comp, why, toggle=None):
        def fn(t):
            with _comp(t, comp, toggle=toggle, beyond_toggle=toggle is None):
                _unmeasured(t, why)
        fn.__doc__ = "UNMEASURED: " + why
        suite.chain(chain)(fn)

    _um("path_pay_the_cartel", "trade_request_silver_closes_the_debt",
        "needs an accepted quest, a trade request raised against the Cartel and silver delivered to it; no bridge tool answers a trade request")
    _um("path_defeat_the_outpost", "all_enemies_defeated_completes_and_costs_goodwill",
        "needs the site map generated and its garrison killed (an Outpost at threat 300+); a combat map the harness cannot build on a held map")
    _um("path_plant_the_egg", "undetected_egg_hatches_in_the_night_window",
        "needs the outpost map (roofed unfogged cell), RM_QuestPart_EggPlantWatcher's signals and a 23:00-02:00 night; owed to a joint live round")
    _um("hatch_juvenile_hostile", "hatched_spider_is_a_four_year_old_manhunter",
        "needs the hatch part to fire; the age (4.0 y) and manhunter state are read from the spawned pawn, not provable without the quest")
    _um("discovery_cost", "found_egg_costs_goodwill_and_undiscovered_kill_costs_none",
        "needs the 3 percent-per-hour discovery roll on the live site and a goodwill read for the target's faction")

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
        bad.append("sanity probe: no settings fields parsed from EggReckoningSettings.cs (regex broke)")
    mod = open(SETTINGS_CS, encoding="utf-8").read()
    for f in sd:
        if '"%s"' % f not in mod:
            bad.append("settings field %s is not Scribed in ExposeData" % f)
        if not re.search(r"\b%s\b" % f, mod.split("DoWindowContents")[1]):
            bad.append("settings field %s has no control in DoWindowContents" % f)
    if "WriteSettings" not in mod or "EggReckoningPatcher.Apply()" not in mod:
        bad.append("the mod no longer re-applies the patcher from WriteSettings (toggle_off_removes_both_routes' reason is stale)")
    proj = open(os.path.join(HERE, "Source", "RimMandrake.Utinni.EggReckoning.csproj"), encoding="utf-8").read()
    listed = {c.replace("\\", "/") for c in re.findall(r'Compile Include="([^"]+)"', proj)}
    for cs in listed:
        if not os.path.isfile(os.path.join(HERE, "Source", cs)):
            bad.append("csproj lists missing file " + cs)
    for f in os.listdir(os.path.join(HERE, "Source")):
        if f.endswith(".cs") and f not in listed:
            bad.append("%s is not in the csproj (EnableDefaultCompileItems false: compiles into nothing)" % f)
    defs = shipped_defs()
    names = {n for _, n in defs}
    if len(defs) < 5:
        bad.append("sanity probe: only %d shipped defs parsed (expected 2 routes + 3 history events)" % len(defs))
    for n in (RUMOR, OFFER):
        if n not in names:
            bad.append("script names def %s but the mod ships none" % n)
    # routes
    rv = route_values()
    if rv.get(RUMOR, {}).get("rootSelectionWeight") != "0.15" or rv.get(OFFER, {}).get("givenBy") != ["Traders"] \
            or rv.get(OFFER, {}).get("randomlySelectable") != "false":
        bad.append("route facts the script asserts live (rumor 0.15, offer given by Traders, not random) differ from the XML: %r" % rv)
    # every history event the quest names is shipped
    qtxt = open(QUEST_XML, encoding="utf-8").read()
    for ev in set(re.findall(r"<(?:goodwillChangeReason|successHistoryEvent|failedOrExpiredHistoryEvent)>(\w+)<", qtxt)):
        if ev not in names:
            bad.append("quest names history event %s but no def ships it" % ev)
    # signals the custom nodes emit are consumed
    out_sigs = set(re.findall(r"<outSignal(?:Planted|Discovered|Hatched|FoundBeforeHatch)>(\w+)</", qtxt))
    in_sigs = set(re.findall(r"<inSignal(?:Enable)?>([\w.]+)</", qtxt))
    if len(out_sigs) != 4 or not out_sigs <= in_sigs:
        bad.append("custom-node out-signals %s are not all consumed (in-signals %s)" % (sorted(out_sigs), sorted(in_sigs)))
    # hatch numbers the walk quotes
    hc = hatch_constants()
    if (hc["fixedBiologicalAgeYears"], hc["discoveryChancePerHour"], hc["nightStartHour"], hc["nightEndHour"]) != (4.0, 0.03, 23, 2):
        bad.append("hatch constants differ from the ruled 4.0 y / 3 percent / 23:00-02:00: %r" % hc)
    # the egg is quest-only: no hatcher on the shared item, and the spider is a ThingDef + PawnKindDef in Webwork
    egg = open(os.path.join(WEBWORK, "Defs", "ThingDefs_Items", "RM_OllathrixEgg.xml"), encoding="utf-8").read()
    if re.search(r"<li Class=\"CompProperties_Hatcher\"", re.sub(r"<!--.*?-->", "", egg, flags=re.S)):
        bad.append("RM_OllathrixEgg carries a CompProperties_Hatcher (rulings 2 and 7: it must never hatch outside the quest)")
    spider = open(os.path.join(WEBWORK, "Defs", "ThingDefs_Races", "RM_Ollathrix.xml"), encoding="utf-8").read()
    if "<PawnKindDef" not in spider or "<defName>RM_Ollathrix</defName>" not in spider:
        bad.append("Webwork no longer ships the RM_Ollathrix kind")
    # dependency chain: Webwork is folded into the composed biomes mod the About.xml requires
    about = open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read()
    for pid in ("mandrake.rm.biomes", "mandrake.rut.patches"):
        if "<packageId>%s</packageId>" % pid not in about:
            bad.append("About.xml lacks dependency %s" % pid)
    compose = open(os.path.join(HERE, "..", "..", "RimMandrake", "Biomes.compose.json"), encoding="utf-8").read()
    if '"key": "Webwork"' not in compose:
        bad.append("Webwork is not in Biomes.compose.json, so the egg and spider are not in the required composed mod")
    if not os.path.isfile(os.path.join(HERE, "..", "UtinniPatches", "Defs", "FactionDefs", "JawaHuttCartel.xml")):
        bad.append("the Hutt Cartel faction file is gone from UtinniPatches")
    if not any(f.endswith(".dll") for f in os.listdir(os.path.join(HERE, "Assemblies"))):
        bad.append("no DLL in Assemblies")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
