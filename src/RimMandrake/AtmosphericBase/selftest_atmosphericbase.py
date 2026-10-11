#!/usr/bin/env python3
"""selftest_atmosphericbase.py -- offline proof for AtmosphericBase's take_over_proof chain (Phase 1).

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


def make_ext(brk, stale=False, **kw):
    def ext(game, tool, p):
        if tool != "jawa/static_call" or p.get("type") != V._PROOF:
            return None
        if stale:
            return {"success": False, "message": "no public static method ProofTakeover"}
        return {"success": True, "result": proof_text(brk, **kw)}
    return ext


def run(brk=(), stale=False, **kw):
    suite = Suite("AtmosphericBaseProofs")
    suite.chain(CHAIN)(V.take_over_proof)
    game = MockGame()
    game.ext = make_ext(set(brk), stale=stale, **kw)
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])


def main():
    srcs = V.load_sources()
    check("static_findings clean on the shipped source", V.static_findings(srcs) == [], V.static_findings(srcs))

    clean = run()
    check("clean: every non-stub bar PASSes", all(v == "PASS" for k, v in clean.items() if k != STUB), clean)
    check("clean: the save/reload stub is UNMEASURED, never PASS", clean.get(STUB) == "UNMEASURED", clean)

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

    if FAILS:
        print("\n%d AtmosphericBase selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall AtmosphericBase selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
