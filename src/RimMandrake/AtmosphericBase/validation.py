"""validation.py -- modcheck suite for RimMandrake AtmosphericBase (mandrake.rm.atmosphericbase).

ATMOSPHERIC_BASE_BUILD_PROGRAM_1, Phases 1-4. Phase 1: capability discovery, the hard exclusion list, the per-thing
take-over / take-back buttons, the scenario-decides switch, exact restore on release (and on the map being removed).
Phase 2: schemes as data (RM_AtmosphericSchemeDef), the framework's default groups and registered groups, and the
compositor driving ONE mood -- quantised to the palette (L4), written only on change (§2.6 step 6), unlit fixtures not
driven (L9), on real time (L10). Five Mod Settings.
Phase 3: moods held one per claimant and ORDERED by the consumer's rank (read, never computed); the top two take
territory over the union of their groups -- a wedge of the fixtures that turns on its own slow clock (L5: allocation,
never mixing). Phase 4: moods ranked below them, at most three (L6), flicker a few fixtures in their own palette, never
more than tremorMaxFraction of the driven fixtures at once. Ten more Mod Settings; defaults = the shipped gentle look
(one mood -> neither territory nor tremor ever acts).
Grounded in Source/, read whole: Kernel/RM_AtmosphericKernel.cs, RM_GlowAccess.cs, RM_EmitterDiscovery.cs,
RM_MapComponent_AtmosphericBase.cs, RM_AtmosphericDesignators.cs, RM_AtmosphericBaseAPI.cs, RM_AtmosphericBaseSettings.cs,
RM_AtmosphericBaseProof.cs, Kernel/RM_SchemeKernel.cs, RM_AtmosphericSchemeDef.cs, RM_AtmosphericCompositor.cs,
Kernel/RM_TerritoryKernel.cs.
Nothing here speaks for Phases 5-10 (gestures, sound, witness ledger, def hooks): not built. No rank supplier exists
(NINEFOLD_LOUDNESS_FRONT_1): every rank today is the pushing consumer's own number.

Three layers, cheapest first:
  1. static_findings(srcs) -- pure over the source text: no Harmony anywhere, no def mutated, every .cs compiled,
     every setting read where it does its job and Scribed, the exclusion list ahead of capability, the selftest seam
     never set by production code. Selftested by planted breaks in selftest_atmosphericbase.py.
  2. selftest_atmosphericbase_kernel.py -- the C# kernel + snapshot/restore against the REAL CompGlower fields, and
     the Phase 2 scheme kernel: validation laws, the pattern only ever an index, changed-only, the shipped schemes.
  3. take_over_proof -- RM_AtmosphericBaseProof.ProofTakeover through jawa/static_call on a live map. Leaves the map as
     it found it. A map with no eligible fixture, or no excluded glower, answers "-" and those bars are UNMEASURED.
  4. one_mood_proof -- RM_AtmosphericBaseProof.ProofCompositor: one held lit fixture, the shipped default scheme pushed
     as a proof mood, the SHIPPED compositor evaluated at explicit times. Its sweep counts are the end-of-Phase-2 cost
     re-measure's input (item ## verify), read on the owner's real list.
  5. territory_proof -- RM_AtmosphericBaseProof.ProofTerritory: up to 40 held lit fixtures, two territory moods and four
     tremor moods (one over L6's cap) pushed, the SHIPPED compositor evaluated at every step of one boundary turn.

🔴 NEVER RUN LIVE (either chain). Built offline 2026-10-11; the lit-fixture branch of SetGlowColorInternal (DeRegister/Register on
the glow grid) runs only in game, so `restored` and `drive` are first proven by the live proof, not by the selftest.
"""
import os
import re

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
_PROOF = "RimMandrake.AtmosphericBase.RM_AtmosphericBaseProof"

suite = Suite("AtmosphericBase")
suite.toggles = ["lightChannel", "playerTakeoverButton", "compositor", "defaultMood", "territory", "tremor"]

SETTINGS = ("lightChannel", "playerTakeoverButton", "compositor", "defaultMood", "defaultMoodGroup",
            "territory", "territoryPeriodSeconds", "territoryLeadShare", "territoryRagged",
            "tremor", "tremorCap", "tremorSlotSeconds", "tremorOneIn", "tremorFlickerSeconds", "tremorMaxFraction")
GATES = (   # (setting, file, class, member) -- the setting must be read inside that member
    ("lightChannel", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "TakeOverRefusal"),
    ("lightChannel", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "Drive"),
    ("lightChannel", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "MapComponentUpdate"),
    ("lightChannel", "RM_AtmosphericDesignators.cs", "RM_AtmosphericDesignators", "PlayerMayChoose"),
    ("playerTakeoverButton", "RM_AtmosphericDesignators.cs", "RM_AtmosphericDesignators", "PlayerMayChoose"),
    ("scenarioDecides", "RM_AtmosphericDesignators.cs", "RM_AtmosphericDesignators", "PlayerMayChoose"),
    ("PlayerMayChoose", "RM_AtmosphericDesignators.cs", "RM_Designator_TakeOverGlow", "CanDesignateThing"),
    ("PlayerMayChoose", "RM_AtmosphericDesignators.cs", "RM_Designator_ReleaseGlow", "CanDesignateThing"),
    ("TakeOverRefusal", "RM_AtmosphericDesignators.cs", "RM_Designator_TakeOverGlow", "CanDesignateThing"),
    ("TakeOverRefusal", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "TakeOver"),
    ("IsTaken", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "Drive"),
    ("RM_GlowAccess.Restore", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "Release"),
    ("WriteColor", "RM_GlowAccess.cs", "RM_GlowAccess", "Restore"),
    ("EnsureRegistered", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "MapComponentUpdate"),
    # Phase 2
    ("compositor.Update", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "MapComponentUpdate"),
    ("compositor.Forget", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "Release"),
    ("RM_PaletteGuard.IsMember", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "Drive"),
    ("RestoreFieldOnly", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "MapRemoved"),
    ("scheme.Valid", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "PushMood"),
    ("compositor", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("defaultMood", "RM_AtmosphericCompositor.cs", "RM_Compositor", "DefaultMood"),
    ("defaultMoodGroup", "RM_AtmosphericCompositor.cs", "RM_Compositor", "DefaultMood"),
    ("tracker.Want", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("g.Glows", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("RM_SchemeKernel.PaletteIndex", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("RM_SchemeKernel.Errors", "RM_AtmosphericSchemeDef.cs", "RM_AtmosphericSchemeDef", "ConfigErrors"),
    ("realtimeSinceStartup", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Update"),
    # Phases 3-4
    ("RankedMoods", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("CompareRank", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "RankedMoods"),
    ("set.territory &&", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("TerritoryTuning", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("RM_TerritoryKernel.Allocate", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("RM_TerritoryKernel.ClockStep", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("set.tremor &&", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("TremorTuning", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("RM_TremorKernel.Assign", "RM_AtmosphericCompositor.cs", "RM_Compositor", "Evaluate"),
    ("RestoreMoods", "RM_AtmosphericBaseProof.cs", "RM_AtmosphericBaseProof", "ProofCompositor"),
    ("RestoreMoods", "RM_AtmosphericBaseProof.cs", "RM_AtmosphericBaseProof", "ProofTerritory"),
)
WIRING = (  # (file, needle, why)
    ("RM_GlowAccess.cs", '"glowColorOverride"', "the colour override field is no longer what is snapshotted"),
    ("RM_GlowAccess.cs", '"SetGlowColorInternal"', "colour is no longer written through the game's own regrid path"),
    ("RM_MapComponent_AtmosphericBase.cs", 'Scribe_Collections.Look(ref taken, "taken", LookMode.Deep)', "held fixtures forget their prior glow on reload"),
    ("RM_MapComponent_AtmosphericBase.cs", 'Scribe_Values.Look(ref scenarioDecides', "a scenario's decision is lost on reload"),
    ("RM_AtmosphericDesignators.cs", "Find.ReverseDesignatorDatabase", "the buttons are never offered"),
    ("RM_AtmosphericDesignators.cs", "ReferenceEquals(list, registeredIn)", "a Reinit()'d designator list never gets the buttons back"),
    ("RM_MapComponent_AtmosphericBase.cs", 'Scribe_Collections.Look(ref moods, "moods", LookMode.Deep)', "pushed moods are lost on reload"),
    ("RM_MapComponent_AtmosphericBase.cs", 'Scribe_Deep.Look(ref legacyMood, "mood")', "a Phase 2 save's one mood is lost on load"),
    ("RM_AtmosphericCompositor.cs", "if (!tracker.Want(id, RM_ChangeTracker.Pack(scheme.shortHash, idx))) { skippedUnchanged++; return 0; }",
     "a driven fixture is rewritten when its value did not change (§2.6 step 6)"),
    ("RM_AtmosphericCompositor.cs", "if (!tracker.Want(id, RM_ChangeTracker.Substrate)) { skippedUnchanged++; continue; }",
     "a fixture is re-restored every evaluation (§2.6 step 6)"),
    ("RM_AtmosphericCompositor.cs", "comp.Drive(t, scheme.palette[idx])", "the compositor no longer writes a palette member by index (L4)"),
    ("RM_AtmosphericCompositor.cs", "int w = Show(comp, t, tremorMoods[tr.Key].scheme, tr.Value);", "a tremor flicker is not drawn from its own contributor's palette (L6)"),
    ("RM_AtmosphericCompositor.cs", "owner = isLead ? lead : second;", "a territory fixture no longer shows its allocated claimant (L5)"),
    ("RM_AtmosphericBaseSettings.cs", "TerritoryTuning => RM_TerritoryTuning.Clamp(", "territory tuning reaches the kernel unclamped"),
    ("RM_AtmosphericBaseSettings.cs", "TremorTuning => RM_TremorTuning.Clamp(", "tremor tuning reaches the kernel unclamped (L6 cap)"),
    ("Kernel/RM_TerritoryKernel.cs", "public const int LawCap = 3;", "the tremor's cap of three contributors (L6) moved"),
    ("RM_AtmosphericCompositor.cs", 'DefaultSchemeDefName = "RM_Scheme_Lamplight"', "the default scheme is no longer the shipped Lamplight"),
    ("Defs/RM_AtmosphericSchemes.xml", "<defName>RM_Scheme_Lamplight</defName>", "the default scheme the compositor names is not shipped"),
)
EXCLUSIONS = ("isPawn", "isPlant", "isApparelOrEquipment", "hologramMarked")


def load_sources():
    out = {}
    for dirpath, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ("bin", "obj")]
        for fn in files:
            if fn.endswith((".cs", ".csproj")):
                rel = os.path.relpath(os.path.join(dirpath, fn), SRC).replace(os.sep, "/")
                out[rel] = open(os.path.join(dirpath, fn), encoding="utf-8").read()
    p = os.path.join(HERE, "About", "About.xml")
    out["About.xml"] = open(p, encoding="utf-8").read()
    d = os.path.join(HERE, "Defs")
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else ():
        if fn.endswith(".xml"):
            out["Defs/" + fn] = open(os.path.join(d, fn), encoding="utf-8").read()
    return out


def _balanced(src, start):
    i, depth = src.index("{", start) + 1, 1
    j = i
    while j < len(src) and depth:
        depth += {"{": 1, "}": -1}.get(src[j], 0)
        j += 1
    return src[i:j]


def member_body(src, cls, member):
    """Text of `member` (method or property) inside `class cls`, comments removed; None when absent."""
    src = re.sub(r"//[^\n]*", "", src)
    m = re.search(r"class\s+%s\b" % re.escape(cls), src)
    if not m:
        return None
    body = _balanced(src, m.end())
    mm = re.search(r"\b%s\s*(?:\([^)]*\))?\s*\{" % re.escape(member), body)
    return _balanced(body, mm.start()) if mm else None


def _code(s):
    return re.sub(r"//[^\n]*", "", s)


def static_findings(srcs):
    """Pure over {relpath: text}. Each finding names its class in brackets."""
    bad = []
    prod = dict((k, v) for k, v in srcs.items() if not k.startswith("SelfTest/"))
    for fn, text in prod.items():
        if fn.endswith(".cs") and re.search(r"\bHarmony(Lib)?\b", _code(text)):
            bad.append("[no-harmony] %s references Harmony (spec: no Harmony; the buttons ride the reverse-designator list)" % fn)
        if fn.endswith(".cs") and re.search(r"\.comps\.Add\(|DefDatabase<[^>]+>\.Add\(|\.modExtensions\.Add\(", _code(text)):
            bad.append("[no-def-edit] %s mutates a def (the take-over must be per thing and reversible)" % fn)
        if fn.endswith(".cs") and re.search(r"glowRadiusOverride|RadiusField|\bGlowRadius\s*=(?!=)|ForceRegister", _code(text)):
            bad.append("[light-ledger] %s writes a light's radius; radius belongs to _Shared/LightLedger (LIGHT_LEDGER_ONE_1)" % fn)
        if fn.endswith(".cs") and "ColorWriterForSelfTest =" in _code(text):
            bad.append("[seam] %s sets the selftest colour writer in production code" % fn)
        if fn.endswith(".cs") and re.search(r"\bLerp(Unclamped)?\s*\(|\bLerpColor\b|Color\.Lerp", _code(text)):
            bad.append("[L4] %s interpolates a colour; every colour that reaches a fixture is a palette member" % fn)
    proj = srcs.get("RM_AtmosphericBase.csproj", "")
    if "Harmony" in re.sub(r"<!--.*?-->", "", proj, flags=re.S):
        bad.append("[no-harmony] RM_AtmosphericBase.csproj references Harmony")
    for fn in prod:
        if fn.endswith(".cs") and ('Compile Include="%s"' % fn.replace("/", "\\")) not in proj:
            bad.append("[wiring] %s is not in RM_AtmosphericBase.csproj and compiles into nothing" % fn)
    about = srcs.get("About.xml", "")
    after = re.findall(r"<li>([^<]+)</li>", (re.search(r"<loadAfter>(.*?)</loadAfter>", about, re.S) or [None, ""])[1])
    if after != ["Ludeon.RimWorld"]:
        bad.append("[about] loadAfter must be Ludeon.RimWorld only, got %r" % after)
    if "brrainz.harmony" in about:
        bad.append("[about] About.xml depends on Harmony")
    for setting, fn, cls, member in GATES:
        b = member_body(srcs.get(fn, ""), cls, member)
        if b is None:
            bad.append("[gate] %s: %s.%s not found" % (fn, cls, member))
        elif setting not in b:
            bad.append("[gate] %s.%s no longer reads %s" % (cls, member, setting))
    for fn, needle, why in WIRING:
        if needle not in srcs.get(fn, ""):
            bad.append("[wiring] %s lost `%s`: %s" % (fn, needle, why))
    cl = member_body(srcs.get("Kernel/RM_AtmosphericKernel.cs", ""), "RM_AtmosphericKernel", "Classify") or ""
    cap = cl.find("hasGlower")
    for ex in EXCLUSIONS:
        at = cl.find(ex)
        if at < 0:
            bad.append("[exclusion] Classify no longer tests %s" % ex)
        elif cap >= 0 and at > cap:
            bad.append("[exclusion] Classify tests %s AFTER capability, so a glowing %s could be driven" % (ex, ex))
    x = srcs.get("RM_AtmosphericBaseSettings.cs", "")
    for f in SETTINGS:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), x):
            bad.append("[settings] %s is not Scribed" % f)
        ui = x.split("DoWindowContents", 1)[-1]
        if not (re.search(r"ref %s," % f, ui) or re.search(r"\b%s\s*=\s*\w" % f, ui)):
            bad.append("[settings] %s has no control in DoWindowContents" % f)
    return bad


def _kv(t):
    r = t.bridge_call("jawa/static_call", type=_PROOF, method="ProofTakeover", args="go")
    if not t._guard():
        return None, ""
    text = (r or {}).get("result") if isinstance(r, dict) else None
    if text in (None, ""):
        t.upstream_reason = "UNMEASURED: RM_AtmosphericBaseProof.ProofTakeover answered nothing (DLL not deployed?): %s" % (
            str((r or {}).get("message") or (r or {}).get("error"))[:120])
        t.upstream_failed = True
        return None, ""
    text = str(text)
    if text.startswith("ERROR"):
        raise ExpectationFailed("ProofTakeover: %s" % text)
    kv = dict(re.findall(r"(\w+)=(\S+)", text))
    if kv.get("map") == "-":
        t.upstream_reason, t.upstream_failed = "UNMEASURED: no current map", True
        return None, ""
    return kv, text


def _unmeasured(t, why, text):
    t.upstream_reason, t.upstream_failed = "UNMEASURED: %s: %s" % (why, text[:200]), True


def _want(kv, text, keys):
    bad = dict((k, kv.get(k)) for k in keys if kv.get(k) != "True")
    if bad:
        raise ExpectationFailed("want True, got %s: %s" % (bad, text[:500]))


@suite.chain("take_over_proof")
def take_over_proof(t):
    with t.component("static_no_harmony_no_def_edit_gates_and_settings", beyond_toggle=True):
        bad = static_findings(load_sources())
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("compglower_members_bound_and_buttons_registered", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            _want(kv, text, ("bound", "buttons_registered"))
    with t.component("excluded_glowers_never_accepted", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("excluded_glowers", "0") == "0":
                _unmeasured(t, "this map holds no glowing pawn, plant, worn gear or hologram to test the exclusion on", text)
            elif kv.get("excluded_accepted") != "0":
                raise ExpectationFailed("%s excluded glower(s) would be taken over: %s" % (kv.get("excluded_accepted"), text[:400]))
    with t.component("take_drive_release_restores_exactly", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("eligible", "0") == "0":
                _unmeasured(t, "no untaken player-owned lit fixture on this map", text)
            else:
                _want(kv, text, ("offered", "take", "release_offered", "drive", "released", "restored", "drive_after_release_refused"))
    with t.component("untaken_neighbour_untouched", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("neighbour", "-") == "-":
                _unmeasured(t, "fewer than two eligible fixtures on this map", text)
            else:
                _want(kv, text, ("neighbour",))
    with t.component("light_channel_off_refuses_and_releases", toggle="lightChannel"):
        kv, text = _kv(t)
        if kv:
            if kv.get("eligible", "0") == "0":
                _unmeasured(t, "no eligible fixture on this map", text)
            elif kv.get("channel_off_releases", "-") == "-":
                _want(kv, text, ("channel_off",))
                _unmeasured(t, "the player already holds fixtures here, so the release-everything half is not exercised", text)
            else:
                _want(kv, text, ("channel_off", "channel_off_releases"))
    with t.component("button_switch_hides_the_button", toggle="playerTakeoverButton"):
        kv, text = _kv(t)
        if kv:
            if kv.get("eligible", "0") == "0":
                _unmeasured(t, "no eligible fixture on this map", text)
            else:
                _want(kv, text, ("button_off_hides",))
    with t.component("scenario_decides_hides_the_button", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("eligible", "0") == "0":
                _unmeasured(t, "no eligible fixture on this map", text)
            else:
                _want(kv, text, ("scenario_hides",))
    with t.component("release_after_save_reload_restores", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: release after a save and reload needs a save/load round trip on a held fixture; "
                                 "instrument missing (a site recipe that takes over, saves, reloads, then calls the proof)")
            t.upstream_failed = True


def _kv2(t):
    r = t.bridge_call("jawa/static_call", type=_PROOF, method="ProofCompositor", args="go")
    if not t._guard():
        return None, ""
    text = (r or {}).get("result") if isinstance(r, dict) else None
    if text in (None, ""):
        t.upstream_reason = "UNMEASURED: RM_AtmosphericBaseProof.ProofCompositor answered nothing (DLL not deployed?): %s" % (
            str((r or {}).get("message") or (r or {}).get("error"))[:120])
        t.upstream_failed = True
        return None, ""
    text = str(text)
    if text.startswith("ERROR"):
        raise ExpectationFailed("ProofCompositor: %s" % text)
    kv = dict(re.findall(r"(\w+)=(\S+)", text))
    if kv.get("map") == "-":
        t.upstream_reason, t.upstream_failed = "UNMEASURED: no current map", True
        return None, ""
    if kv.get("scheme") != "True":
        raise ExpectationFailed("the shipped default scheme RM_Scheme_Lamplight is missing or invalid: %s" % text[:300])
    if kv.get("lit", "-") == "-":
        _unmeasured(t, "no untaken player-owned LIT fixture on this map", text)
        return None, ""
    return kv, text


@suite.chain("one_mood_proof")
def one_mood_proof(t):
    with t.component("one_mood_drives_a_palette_member", beyond_toggle=True):
        kv, text = _kv2(t)
        if kv:
            _want(kv, text, ("push", "first_write", "quantised"))
            if not kv.get("showing", "").startswith("RM_Scheme_Lamplight:"):
                raise ExpectationFailed("the compositor does not report the pushed scheme as showing: %s" % text[:300])
            if kv.get("palette_violations") != "0":
                raise ExpectationFailed("a colour outside every palette reached Drive: %s" % text[:300])
    with t.component("only_changed_fixtures_are_written", beyond_toggle=True):
        kv, text = _kv2(t)
        if kv:
            if kv.get("same_time_writes") != "0":
                raise ExpectationFailed("re-evaluating at the same instant wrote %s fixture(s): %s" % (kv.get("same_time_writes"), text[:300]))
            if kv.get("changed_only", "-") == "-":
                _unmeasured(t, "other fixtures are held on this map, so the sweep's writes are not the proof fixture's alone", text)
            else:
                _want(kv, text, ("changed_only",))
    with t.component("untaken_neighbour_untouched_by_the_mood", beyond_toggle=True):
        kv, text = _kv2(t)
        if kv:
            if kv.get("neighbour", "-") == "-":
                _unmeasured(t, "fewer than two eligible fixtures on this map", text)
            else:
                _want(kv, text, ("neighbour",))
    with t.component("outside_the_group_shows_its_own_glow", beyond_toggle=True):
        kv, text = _kv2(t)
        if kv:
            _want(kv, text, ("outside_group_substrate",))
    with t.component("compositor_switch_off_shows_own_glow", toggle="compositor"):
        kv, text = _kv2(t)
        if kv:
            _want(kv, text, ("compositor_off_substrate", "compositor_on_drives"))
    with t.component("default_mood_switch", toggle="defaultMood"):
        kv, text = _kv2(t)
        if kv:
            _want(kv, text, ("mood_release_substrate", "default_runs"))
    with t.component("release_after_a_mood_restores_exactly", beyond_toggle=True):
        kv, text = _kv2(t)
        if kv:
            _want(kv, text, ("released_exact",))
    with t.component("unlit_fixture_not_driven", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: needs a held fixture with its power cut mid-mood; instrument missing "
                                 "(the proof cannot cut power on the owner's map without leaving a trace)")
            t.upstream_failed = True


def _kv3(t):
    r = t.bridge_call("jawa/static_call", type=_PROOF, method="ProofTerritory", args="go")
    if not t._guard():
        return None, ""
    text = (r or {}).get("result") if isinstance(r, dict) else None
    if text in (None, ""):
        t.upstream_reason = "UNMEASURED: RM_AtmosphericBaseProof.ProofTerritory answered nothing (DLL not deployed?): %s" % (
            str((r or {}).get("message") or (r or {}).get("error"))[:120])
        t.upstream_failed = True
        return None, ""
    text = str(text)
    if text.startswith("ERROR"):
        raise ExpectationFailed("ProofTerritory: %s" % text)
    kv = dict(re.findall(r"(\w+)=(\S+)", text))
    if kv.get("map") == "-":
        t.upstream_reason, t.upstream_failed = "UNMEASURED: no current map", True
        return None, ""
    if kv.get("schemes") != "True":
        raise ExpectationFailed("the shipped schemes RM_Scheme_Lamplight / RM_Scheme_Fireflies are missing or invalid: %s" % text[:300])
    try:
        lit = int(kv.get("lit", "0"))
    except ValueError:
        lit = 0
    if lit < 2:
        _unmeasured(t, "fewer than two untaken player-owned LIT fixtures on this map", text)
        return None, ""
    return kv, text


@suite.chain("territory_proof")
def territory_proof(t):
    with t.component("territory_every_fixture_one_claimant_one_palette", toggle="territory"):
        kv, text = _kv3(t)
        if kv:
            _want(kv, text, ("one_owner", "own_palette", "territory_off_one_mood"))
            if kv.get("palette_violations") != "0":
                raise ExpectationFailed("a colour outside every palette reached Drive: %s" % text[:300])
    with t.component("territory_both_presences_hold_ground", toggle="territory"):
        kv, text = _kv3(t)
        if kv:
            _want(kv, text, ("both_sides",))
    with t.component("territory_boundary_moves", toggle="territory"):
        kv, text = _kv3(t)
        if kv:
            _want(kv, text, ("boundary_moves",))
    with t.component("tremor_capped_at_three_in_own_palette", toggle="tremor"):
        kv, text = _kv3(t)
        if kv:
            if kv.get("tremor_seen", "0") == "0":
                _unmeasured(t, "no flicker fell inside the sampled turn on this few fixtures", text)
            else:
                _want(kv, text, ("tremor_cap_held", "tremor_fraction_held", "tremor_own_palette"))
    with t.component("territory_release_restores_exactly", beyond_toggle=True):
        kv, text = _kv3(t)
        if kv:
            _want(kv, text, ("released_exact",))
    with t.component("territory_boundary_visible_and_tremor_reads_as_presence", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: north-star bars territory_boundary_visible / tremor_reads_as_third_presence / "
                                 "never_tremor_reads_as_territory are owner-eye judgements on the authored canvas "
                                 "(ATMOSPHERIC_BASE_CANVAS_1), with ranks from NINEFOLD_LOUDNESS_FRONT_1; neither exists yet")
            t.upstream_failed = True
