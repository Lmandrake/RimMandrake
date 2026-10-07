"""validation.py -- modcheck suite for RimMandrake: The Bazaar (mandrake.rm.bazaar).

First north-star script (THE_BAZAAR_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/TheBazaar.md.
Design: design/RimMandrake/bazaar_trade_window_design.md (whole-deal haggle duel, broker tab: both owner-ruled, NOT built).

HONEST SCOPE. Ships: BAZAAR_WINDOW_GRID_1 slice 1 (four plugin def classes, an inert Dialog_Trade subclass nothing
constructs) and BAZAAR_PRICE_ENGINE_1 slice 2 (RM_BazaarEconomy, RM_BazaarSeedRuleDef rules, the session-guarded
Tradeable.GetPriceFor postfix, intel layer defs + L1..L4 workers, four protocol-droid module items/hediffs, settings).
The chains prove what exists and report the rest UNMEASURED with the reason, never a fake pass or fail:

  defs_and_types      shipped XML defs (vanilla-typed ones) resolve live; every C# type resolves live; log clean.
  settings_roundtrip  every `public static` field of RM_BazaarSettings round-trips.
  intercept_state     no Harmony patch of this mod on WindowStack.Add (still true). Red = intercept landed: extend.
  price_engine        our postfix sits on Tradeable.GetPriceFor; the economy/water/wealth proofs need a live Bazaar
                      session, which cannot exist before the intercept: UNMEASURED with that reason.
  unshipped           grid, intel rendering, haggle duel, broker tab, banter: UNMEASURED (not built).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "RimMandrake.Bazaar."
SETTINGS = NS + "RM_BazaarSettings"
HARMONY_ID = "mandrake.rm.bazaar"
TYPES = [NS + n for n in ("RM_BazaarColumnDef", "RM_BazaarBadgeDef", "RM_BazaarTabDef", "RM_BazaarIntelLayerDef",
                          "RM_BazaarSession", "RM_Window_Bazaar", "RM_BazaarSettings", "RM_BazaarMod",
                          "RM_BazaarEconomy", "RM_BazaarSeedRuleDef", "RM_BazaarTags", "RM_Patch_GetPriceFor",
                          "RM_BazaarIntel", "BazaarColumnWorker_PriceContext", "BazaarColumnWorker_LocalEconomy",
                          "BazaarBadgeWorker_GoodDeal", "BazaarBadgeWorker_Scarcity")]
# Vanilla-typed defs the mod ships; jawa/get_defs can resolve these by "DefType/defName".
SHIPPED_DEFS = ["ThingDef/RM_HagglerModule", "ThingDef/RM_ManifestDecoder", "ThingDef/RM_TransponderScanner",
                "ThingDef/RM_PriceAlmanac", "HediffDef/RM_HagglerModuleFitted", "HediffDef/RM_ManifestDecoderFitted",
                "HediffDef/RM_TransponderScannerFitted", "HediffDef/RM_PriceAlmanacFitted"]
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
INTERCEPT_SHIPPED = False     # flip to True in the slice that lands the WindowStack.Add intercept, and add its chains


def settings_fields():
    """{name: type} for every scalar `public static` field of RM_BazaarSettings, read from the C#."""
    src = open(os.path.join(HERE, "Source", "RM_BazaarSettings.cs"), encoding="utf-8").read()
    body = src.split("class RM_BazaarSettings", 1)[1].split("class RM_BazaarMod", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def _probe_works():
    """The settings regex must be able to see a field: proven on a sample, since the real file has none."""
    return bool(_FIELD.search("public static bool sampleToggle = true;"))


def xml_checks(cstext):
    """Every workerClass names a class declared in Source/; every requiredModule names a HediffDef we ship;
    every seed target sets exactly one of thingDef/tradeTag/category; every settingsToggle is a settings field."""
    import xml.etree.ElementTree as ET
    bad, hediffs, layers = [], set(), []
    defs_dir = os.path.join(HERE, "Defs")
    xmls = [os.path.join(r, f) for r, _d, fs in os.walk(defs_dir) for f in fs if f.endswith(".xml")]
    if len(xmls) < 3:
        return ["only %d Defs XML files found (sanity probe failed)" % len(xmls)]
    seen = {"worker": 0, "rule": 0}
    for path in xmls:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as e:
            bad.append("%s does not parse: %s" % (os.path.basename(path), e))
            continue
        for el in root:
            if el.tag == "HediffDef" and el.findtext("defName"):
                hediffs.add(el.findtext("defName"))
            if el.tag.endswith("RM_BazaarIntelLayerDef"):
                layers.append(el)
            wc = el.findtext("workerClass")
            if wc:
                seen["worker"] += 1
                if not re.search(r"\bclass\s+%s\b" % re.escape(wc.split(".")[-1]), cstext):
                    bad.append("workerClass %s is not declared in Source/" % wc)
            if el.tag.endswith("RM_BazaarSeedRuleDef"):
                seen["rule"] += 1
                for li in el.findall("targets/li"):
                    n = sum(1 for k in ("thingDef", "tradeTag", "category") if (li.findtext(k) or "").strip())
                    if n != 1:
                        bad.append("%s: a target sets %d of thingDef/tradeTag/category" % (el.findtext("defName"), n))
    if seen["worker"] < 4 or seen["rule"] < 1 or len(layers) < 8:
        bad.append("XML sanity probe: workers=%d rules=%d layers=%d" % (seen["worker"], seen["rule"], len(layers)))
    fields = settings_fields()
    for el in layers:
        mod = el.findtext("requiredModule")
        if mod and mod not in hediffs:
            bad.append("%s requiredModule %s is not a HediffDef we ship" % (el.findtext("defName"), mod))
        tog = el.findtext("settingsToggle")
        if tog and tog not in fields:
            bad.append("%s settingsToggle %s is not a settings field" % (el.findtext("defName"), tog))
    for d in SHIPPED_DEFS:
        if d.split("/")[1] not in open(os.path.join(defs_dir, "Modules", "RM_BazaarModules.xml"), encoding="utf-8").read():
            bad.append("SHIPPED_DEFS lists %s but Modules XML lacks it" % d)
    return bad


def static_checks():
    bad = []
    if not _probe_works():
        return ["settings regex cannot see a sample field (sanity probe failed)"]
    srcdir = os.path.join(HERE, "Source")
    files = []
    for root, _dirs, names in os.walk(srcdir):
        for f in names:
            if f.endswith(".cs") and "/obj" not in root.replace(os.sep, "/"):
                files.append(os.path.relpath(os.path.join(root, f), srcdir).replace(os.sep, "/"))
    files.sort()
    if len(files) < 13:
        bad.append("only %d .cs files found (sanity probe failed)" % len(files))
    proj = open(os.path.join(srcdir, "RimMandrake_Bazaar.csproj"), encoding="utf-8").read()
    for f in files:
        if 'Compile Include="%s"' % f.replace("/", "\\") not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % f)
    alltext = "\n".join(open(os.path.join(srcdir, f), encoding="utf-8").read() for f in files)
    for ty in TYPES:
        if not re.search(r"\b(class|abstract class)\s+%s\b" % ty.split(".")[-1], alltext):
            bad.append("type %s not declared in Source/" % ty)
    bad.extend(xml_checks(alltext))
    sset = open(os.path.join(srcdir, "RM_BazaarSettings.cs"), encoding="utf-8").read()
    scribed = sset.split("ExposeData", 1)[1].split("DoWindowContents", 1)[0]
    ui = sset.split("DoWindowContents", 1)[1]
    for n in settings_fields():
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    code = re.sub(r"//[^\n]*", "", alltext)
    if not INTERCEPT_SHIPPED and re.search(r"typeof\(WindowStack\)|nameof\(WindowStack", code):
        bad.append("a WindowStack patch target appeared but INTERCEPT_SHIPPED is False: extend intercept_state")
    if re.search(r"typeof\(StatWorker|nameof\(Thing\.MarketValue\)|\"MarketValue\"|typeof\(StatExtension", code):
        bad.append("a MarketValue/StatWorker hook appeared: the engine must stay read-side (item Watch-out)")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "TheBazaar.md")):
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
    suite = Suite("TheBazaar")
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        kw = dict(typeName=SETTINGS, action=action, field=field)
        if value is not None:
            kw["value"] = str(value)
        r = t.session.call("jawa/mod_settings_field", **kw)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    @suite.chain("defs_and_types")
    def defs_and_types(t):
        with t.component("shipped_defs_resolve", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_BazaarNoSuchDef_ZZ", fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
            missing = []
            for d in SHIPPED_DEFS:
                r = t.bridge_call("jawa/get_defs", defs=d, fields="defName", limit=2)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs(%s) could not be asked: %r" % (d, r))
                if int(r.get("foundCount", 0)) < 1:
                    missing.append(d)
            if _live(t) and missing:
                raise ExpectationFailed("shipped defs absent live: %s" % missing)
        with t.component("types_resolve", beyond_toggle=True):
            bad = []
            for ty in TYPES:
                r = t.bridge_call("jawa/type_probe", typeName=ty)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("type_probe(%s) failed: %r" % (ty, r))
                if r.get("resolved") is not True:
                    bad.append("%s did not resolve" % ty)
                elif r.get("mvidMatchesFile") is False:
                    bad.append("%s: loaded DLL is not the file on disk (redeployed after launch?)" % ty)
            probe = t.bridge_call("jawa/type_probe", typeName=NS + "NoSuchType_Probe")
            if _live(t):
                if (probe or {}).get("resolved") is not False:
                    raise ExpectationFailed("sanity probe: an absent type resolved or the probe errored: %r" % probe)
                if bad:
                    raise ExpectationFailed("; ".join(bad))
        with t.component("no_bazaar_log_errors", beyond_toggle=True):
            r = t.bridge_call("jawa/drain_log", contains="Bazaar", errorsOnly=True, limit=50)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("drain_log failed: %r" % r)
                if (r.get("totalInBuffer") or 0) >= 1000:
                    _unmeasured(t, "log buffer full: load-time lines rolled out; read Player.log's first exception")
                    return
                if r.get("messages"):
                    raise ExpectationFailed("Bazaar log errors: %s" % [m.get("text", "")[:160] for m in r["messages"][:3]])

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if not _probe_works():
                raise ExpectationFailed("settings regex is blind (cannot see a sample field)")
            # RM_BazaarSettings has NO scalar field at slice 1 by design (its own comment); fields are generated below.
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
                if not _same(ty, _raw(t, "get", field).get("value"), old):
                    raise ExpectationFailed("%s did not restore to %r" % (field, old))

    @suite.chain("intercept_state")
    def intercept_state(t):
        with t.component("window_stack_add_not_patched", beyond_toggle=True):
            r = t.bridge_call("jawa/harmony_patches", typeName="WindowStack", methodName="Add")
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked: %s" % str(r)[:160])
                    return
                owners = []
                for m in (r.get("methods") or []):
                    for kind in ("prefixes", "postfixes", "transpilers", "finalizers"):
                        owners.extend(p.get("owner") for p in (m.get(kind) or []))
                mine = HARMONY_ID in owners
                if mine and not INTERCEPT_SHIPPED:
                    raise ExpectationFailed("the Bazaar now patches WindowStack.Add but this script still says slice 1: "
                                            "set INTERCEPT_SHIPPED and add the grid/haggle chains")
                if INTERCEPT_SHIPPED and not mine:
                    raise ExpectationFailed("INTERCEPT_SHIPPED is set but no %s patch sits on WindowStack.Add" % HARMONY_ID)

    @suite.chain("price_engine")
    def price_engine(t):
        with t.component("getpricefor_postfix_is_ours", beyond_toggle=True):
            r = t.bridge_call("jawa/harmony_patches", typeName="Tradeable", methodName="GetPriceFor")
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked: %s" % str(r)[:160])
                    return
                owners = [p.get("owner") for m in (r.get("methods") or []) for p in (m.get("postfixes") or [])]
                if HARMONY_ID not in owners:
                    raise ExpectationFailed("no %s postfix on Tradeable.GetPriceFor (owners: %s)" % (HARMONY_ID, owners))
        for name in ("desert_water_reads_about_2x", "economy_round_trips_save_load", "colony_wealth_identical"):
            with t.component(name, beyond_toggle=True):
                if _live(t):
                    _unmeasured(t, "needs a live Bazaar session; RM_BazaarSession.Current is only raised by "
                                   "RM_Window_Bazaar, which nothing constructs until the WindowStack.Add intercept lands")

    @suite.chain("unshipped")
    def unshipped(t):
        for name, why in (
            ("grid_searchable_sortable", "the grid body is not built (design section 2, slice 2+)"),
            ("intel_layers_render_gated", "L1..L4 workers exist but nothing draws them until the grid body lands; "
                                          "module layers also need Droidworks' install recipe (not built)"),
            ("whole_deal_haggle_duel", "the duel and its patience meter are not built (design section 5, owner ruling "
                                       "2026-09-13); needs a trade session driven through the bridge"),
            ("broker_tab_needs_flowworks", "the broker tab is not built (design sections 2 and 7)"),
            ("banter_degrades_without_cli", "banter (Oracle consumer) is not built (design section 6)"),
        ):
            with t.component(name, beyond_toggle=True):
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
