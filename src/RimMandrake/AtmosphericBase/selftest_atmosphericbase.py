#!/usr/bin/env python3
"""selftest_atmosphericbase.py -- offline proof for AtmosphericBase's take_over_proof (Phase 1) and one_mood_proof (Phase 2) chains.

Run bare: python3 src/RimMandrake/AtmosphericBase/selftest_atmosphericbase.py   (exit 0 = clean)

A mock jawa/static_call answers RM_AtmosphericBaseProof.ProofTakeover the way the shipped C# does. Clean must PASS
(map-dependent bars UNMEASURED, never PASS, when the map has nothing to test on; the save/reload stub always
UNMEASURED; a stale DLL UNMEASURED); each planted break must redden its own component. Statically, planted source
breaks must redden static_findings, and the shipped source must be clean.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from modcheck import Suite                                     # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
CHAIN = "take_over_proof"
STUB = "release_after_save_reload_restores"
MOOD = "one_mood_proof"
MOOD_STUB = "unlit_fixture_not_driven"
STUBS = (STUB, MOOD_STUB)


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def proof_text(brk, eligible=2, excluded=3, held=0, no_map=False):
    if no_map:
        return "bound=True map=-"
    T = lambda k: "False" if k in brk else "True"  # noqa: E731
    d = dict(bound=T("bound"), buttons_registered=T("buttons_registered"), taken_before=held,
             excluded_glowers=excluded, excluded_accepted=(1 if "excluded_accepted" in brk else 0),
             ExcludedPawn=excluded, ExcludedPlant=0, ExcludedWornOrEquipment=0, ExcludedHologram=0, eligible=eligible)
    if eligible == 0:
        return " ".join("%s=%s" % kv for kv in d.items()) + " take=- drive=- restored=- neighbour=- channel_off=- scenario_hides=- button_off_hides=-"
    for k in ("offered", "scenario_hides", "button_off_hides", "channel_off", "take", "release_offered", "drive", "released",
              "restored", "drive_after_release_refused"):
        d[k] = T(k)
    d["neighbour"] = "-" if eligible < 2 else T("neighbour")
    d["before"] = "[color=none]"
    d["after"] = "[color=none]"
    d["channel_off_releases"] = "-" if held else T("channel_off_releases")
    return " ".join("%s=%s" % kv for kv in d.items())


def mood_text(brk, eligible=2, lit=True, held=0, no_map=False, scheme_ok=True):
    """What the shipped ProofCompositor answers. `held` = OTHER fixtures already held on the map."""
    if no_map:
        return "scheme=True schemes=2 map=-"
    s = "scheme=%s schemes=2" % ("True" if scheme_ok else "False")
    if not scheme_ok:
        return s + " eligible=-"
    s += " eligible=%d lit=%s" % (eligible, "True" if lit and eligible else "-")
    if not (lit and eligible):
        return s
    T = lambda k: "False" if k in brk else "True"  # noqa: E731
    d = dict(push=T("push"), first_write=T("first_write"),
             showing=("RM_Scheme_Fireflies:1" if "showing" in brk else "RM_Scheme_Lamplight:1"),
             same_time_writes=(3 if "same_time_writes" in brk else 0),
             sweep_evals=480, sweep_fixture_writes_max=8, transitions=8, quantised=T("quantised"), taken=1 + held,
             changed_only=("-" if held else T("changed_only")), neighbour=("-" if eligible < 2 else T("neighbour")),
             outside_group_substrate=T("outside_group_substrate"), compositor_off_substrate=T("compositor_off_substrate"),
             compositor_on_drives=T("compositor_on_drives"), mood_release_substrate=T("mood_release_substrate"),
             default_runs=T("default_runs"), released_exact=T("released_exact"),
             palette_violations=(1 if "palette_violations" in brk else 0))
    return s + " " + " ".join("%s=%s" % kv for kv in d.items())


def make_ext(brk, stale=False, mood=None, **kw):
    def ext(game, tool, p):
        if tool != "jawa/static_call" or p.get("type") != V._PROOF:
            return None
        if stale:
            return {"success": False, "message": "no public static method %s" % p.get("method")}
        if p.get("method") == "ProofCompositor":
            return {"success": True, "result": mood_text(brk, **(mood or {}))}
        return {"success": True, "result": proof_text(brk, **kw)}
    return ext


def run(brk=(), stale=False, mood=None, **kw):
    suite = Suite("AtmosphericBaseProofs")
    suite.chain(CHAIN)(V.take_over_proof)
    suite.chain(MOOD)(V.one_mood_proof)
    game = MockGame()
    game.ext = make_ext(set(brk), stale=stale, mood=mood, **kw)
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])


def main():
    srcs = V.load_sources()
    check("static_findings clean on the shipped source", V.static_findings(srcs) == [], V.static_findings(srcs))

    clean = run()
    check("clean: every non-stub bar PASSes", all(v == "PASS" for k, v in clean.items() if k not in STUBS), clean)
    check("clean: the save/reload stub is UNMEASURED, never PASS", clean.get(STUB) == "UNMEASURED", clean)
    check("clean: the unlit stub is UNMEASURED, never PASS", clean.get(MOOD_STUB) == "UNMEASURED", clean)
    check("clean: the Phase 2 chain ran (8 components)", sum(1 for k in clean if k in (
        "one_mood_drives_a_palette_member", "only_changed_fixtures_are_written", "untaken_neighbour_untouched_by_the_mood",
        "outside_the_group_shows_its_own_glow", "compositor_switch_off_shows_own_glow", "default_mood_switch",
        "release_after_a_mood_restores_exactly", MOOD_STUB)) == 8, sorted(clean))

    m = run(mood=dict(lit=False))
    check("mood: no lit fixture -> every proof bar UNMEASURED, never PASS",
          all(m[k] == "UNMEASURED" for k in m if k.startswith(("one_mood", "only_changed", "default_mood", "compositor_switch"))), m)
    check("mood: other fixtures held -> changed-only UNMEASURED", run(mood=dict(held=3))["only_changed_fixtures_are_written"] == "UNMEASURED")
    check("mood: one eligible fixture -> neighbour UNMEASURED", run(mood=dict(eligible=1))["untaken_neighbour_untouched_by_the_mood"] == "UNMEASURED")
    check("mood: shipped scheme missing -> FAIL, not UNMEASURED", run(mood=dict(scheme_ok=False))["one_mood_drives_a_palette_member"] == "FAIL")
    check("mood: stale DLL -> UNMEASURED", run(stale=True)["one_mood_drives_a_palette_member"] == "UNMEASURED")
    for brk, comp in (("push", "one_mood_drives_a_palette_member"), ("first_write", "one_mood_drives_a_palette_member"),
                      ("quantised", "one_mood_drives_a_palette_member"), ("showing", "one_mood_drives_a_palette_member"),
                      ("palette_violations", "one_mood_drives_a_palette_member"),
                      ("same_time_writes", "only_changed_fixtures_are_written"), ("changed_only", "only_changed_fixtures_are_written"),
                      ("neighbour", "untaken_neighbour_untouched_by_the_mood"),
                      ("outside_group_substrate", "outside_the_group_shows_its_own_glow"),
                      ("compositor_off_substrate", "compositor_switch_off_shows_own_glow"),
                      ("compositor_on_drives", "compositor_switch_off_shows_own_glow"),
                      ("mood_release_substrate", "default_mood_switch"), ("default_runs", "default_mood_switch"),
                      ("released_exact", "release_after_a_mood_restores_exactly")):
        got = run((brk,))
        check("mood break %-26s reddens %s" % (brk, comp), got.get(comp) == "FAIL", got.get(comp))

    got = run(eligible=0)
    for k in ("take_drive_release_restores_exactly", "untaken_neighbour_untouched", "light_channel_off_refuses_and_releases",
              "button_switch_hides_the_button", "scenario_decides_hides_the_button"):
        check("no eligible fixture: %s UNMEASURED, never PASS" % k, got.get(k) == "UNMEASURED", got.get(k))
    check("no eligible fixture: the exclusion bar still PASSes", got.get("excluded_glowers_never_accepted") == "PASS", got)
    check("no excluded glower on the map: exclusion bar UNMEASURED", run(excluded=0)["excluded_glowers_never_accepted"] == "UNMEASURED")
    check("one eligible fixture: neighbour bar UNMEASURED", run(eligible=1)["untaken_neighbour_untouched"] == "UNMEASURED")
    check("player already holds fixtures: channel-off bar UNMEASURED, not PASS",
          run(held=2)["light_channel_off_refuses_and_releases"] == "UNMEASURED")
    check("no current map: proof bars UNMEASURED", run(no_map=True)["take_drive_release_restores_exactly"] == "UNMEASURED")
    check("stale DLL: proof bars UNMEASURED, never PASS", run(stale=True)["compglower_members_bound_and_buttons_registered"] == "UNMEASURED")

    for brk, comp in (("bound", "compglower_members_bound_and_buttons_registered"),
                      ("buttons_registered", "compglower_members_bound_and_buttons_registered"),
                      ("excluded_accepted", "excluded_glowers_never_accepted"),
                      ("offered", "take_drive_release_restores_exactly"),
                      ("take", "take_drive_release_restores_exactly"),
                      ("drive", "take_drive_release_restores_exactly"),
                      ("restored", "take_drive_release_restores_exactly"),
                      ("drive_after_release_refused", "take_drive_release_restores_exactly"),
                      ("neighbour", "untaken_neighbour_untouched"),
                      ("channel_off", "light_channel_off_refuses_and_releases"),
                      ("channel_off_releases", "light_channel_off_refuses_and_releases"),
                      ("button_off_hides", "button_switch_hides_the_button"),
                      ("scenario_hides", "scenario_decides_hides_the_button")):
        got = run((brk,))
        check("break %-28s reddens %s" % (brk, comp), got.get(comp) == "FAIL", got.get(comp))

    def mutate(fn, old, new, tag, must):
        mut = dict(srcs)
        check("source break (%s) is findable in the shipped text" % tag, old in mut[fn], old)
        mut[fn] = mut[fn].replace(old, new, 1)
        got = V.static_findings(mut)
        check("source break %-34s reddens static_findings" % tag, any(must in g for g in got), got)

    MC = "RM_MapComponent_AtmosphericBase.cs"
    DS = "RM_AtmosphericDesignators.cs"
    K = "Kernel/RM_AtmosphericKernel.cs"
    mutate(MC, "using Verse;", "using HarmonyLib;\nusing Verse;", "Harmony creeps in", "[no-harmony]")
    mutate(MC, "public void Prune()", "public void Hack(ThingDef d) { d.comps.Add(null); }\n        public void Prune()", "a def is mutated", "[no-def-edit]")
    mutate(MC, "if (!RM_AtmosphericBaseSettings.Cur.lightChannel) return \"the light", "if (false) return \"the light", "take-over ignores the channel", "[gate]")
    mutate(DS, "s.playerTakeoverButton && ", "", "button switch ignored", "[gate]")
    mutate(DS, "&& !c.scenarioDecides", "", "scenario decision ignored", "[gate]")
    mutate(MC, "if (g != null) RM_GlowAccess.Restore(g, rec.prior);", "", "release forgets to restore", "[gate]")
    mutate("RM_GlowAccess.cs", "WriteColor(g, s.hadColor ? s.color : (ColorInt?)null);", "", "restore drops the colour", "[gate]")
    mutate("RM_GlowAccess.cs", "        public static void Restore", "        static void R(CompGlower g) { RadiusField.SetValue(g, 1f); }\n        public static void Restore",
           "radius written outside the ledger", "[light-ledger]")
    mutate(K, "if (f.isPlant) return RM_EmitterVerdict.ExcludedPlant;\n", "", "plant exclusion removed", "[exclusion]")
    mutate(K, "            if (f.hologramMarked || LooksLikeHologram(f.defName, f.thingClassName)) return RM_EmitterVerdict.ExcludedHologram;\n",
           "", "hologram exclusion removed", "[exclusion]")
    mutate(K, "            if (f.isPawn) return RM_EmitterVerdict.ExcludedPawn;\n", "", "pawn exclusion removed", "[exclusion]")
    mutate("RM_AtmosphericBaseProof.cs", "private static string B(", "private static void S() { RM_GlowAccess.ColorWriterForSelfTest = null; }\n        private static string B(",
           "selftest seam set in prod", "[seam]")
    mutate("RM_AtmosphericBase.csproj", 'Compile Include="RM_AtmosphericBaseProof.cs"', 'Compile Include="X.cs"', "proof left out of csproj", "[wiring]")
    mutate("RM_AtmosphericBaseSettings.cs", 'Scribe_Values.Look(ref lightChannel, "lightChannel", true);', "", "setting unscribed", "[settings]")
    mutate("About.xml", "<li>Ludeon.RimWorld</li>\n  </loadAfter>", "<li>Ludeon.RimWorld</li>\n    <li>brrainz.harmony</li>\n  </loadAfter>",
           "loadAfter grows", "[about]")
    mutate(DS, "ReferenceEquals(list, registeredIn)", "list == null", "Reinit no longer re-adds", "[wiring]")
    CO = "RM_AtmosphericCompositor.cs"
    mutate(CO, "if (!g.Glows) { skippedUnlit++; continue; }", "", "unlit fixtures driven (L9)", "[gate]")
    mutate(CO, "if (!tracker.Want(id, RM_ChangeTracker.Pack(", "if (false && !tracker.Want(id, RM_ChangeTracker.Pack(", "changed-only lost", "[wiring]")
    mutate(CO, "comp.Drive(t, mood.scheme.palette[idx])", "comp.Drive(t, new ColorInt(1, 2, 3, 0))", "a computed colour", "[wiring]")
    mutate(CO, "        public static RM_MoodClaim DefaultMood()", "        static ColorInt X(ColorInt a, ColorInt b) => ColorInt.Lerp(a, b, 0.5f);\n        public static RM_MoodClaim DefaultMood()",
           "a colour interpolated", "[L4]")
    mutate(CO, "Evaluate(comp, UnityEngine.Time.realtimeSinceStartup)", "Evaluate(comp, Find.TickManager.TicksGame / 60.0)", "game time, not real time (L10)", "[gate]")
    mutate(MC, "if (!RM_PaletteGuard.IsMember(color))", "if (false)", "palette guard off", "[gate]")
    mutate(MC, "compositor.Update(this);", "", "compositor never runs", "[gate]")
    mutate(MC, "if (g != null && rec.prior != null) RM_GlowAccess.RestoreFieldOnly(g, rec.prior);", "", "map removal forgets to restore", "[gate]")
    mutate(MC, 'Scribe_Deep.Look(ref mood, "mood");', "", "mood unscribed", "[wiring]")
    mutate("RM_AtmosphericSchemeDef.cs", "foreach (string e in RM_SchemeKernel.Errors(Data)) yield return e;", "", "scheme laws unchecked at load", "[gate]")
    mutate("RM_AtmosphericBaseSettings.cs", 'Scribe_Values.Look(ref defaultMoodGroup, "defaultMoodGroup", 0);', "", "group setting unscribed", "[settings]")
    mutate("Defs/RM_AtmosphericSchemes.xml", "<defName>RM_Scheme_Lamplight</defName>", "<defName>RM_Scheme_Lamp</defName>", "default scheme not shipped", "[wiring]")

    if FAILS:
        print("\n%d AtmosphericBase selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall AtmosphericBase selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
