// Unit groups for the canonical-save guard (design/specs/2026-11-23-canonical-save-guard/boundary.md): the PRODUCTION
// JawaBenchSafetyCore.Effective / IsCanonical / LoadedSave, JawaBenchCanonicalSaves (generated) and JawaBenchTpsLifecycle.
// RM_PLANT puts a fault in what a group reads; that group must then go red.
using System;
using System.Linq;
using L = JawaBench.BridgeTools.JawaBenchTpsLifecycle;
using S = JawaBench.BridgeTools.JawaBenchSafetyCore;

namespace JawaBench.BridgeTools
{
    internal static class CanonicalGuardUnits
    {
        const string R3 = "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3", Frozen = "CANONICAL_ASHKARR_START_2026-09-12";
        static readonly DateTime T0 = new DateTime(2026, 11, 23, 0, 0, 0, DateTimeKind.Utc);
        static void Check(string n, Func<bool> f) => Program.Check(n, f);
        static S.ProfileFile File(string saves) => S.ProfileFile.Parse("{\"profile\": \"test\", \"campaignSaves\": \"" + saves + "\"}", T0);
        static string[] Names() => Program.Plant == "lacks_r3" ? JawaBenchCanonicalSaves.Names.Where(n => n != R3).ToArray() : JawaBenchCanonicalSaves.Names;
        static string[] Starts() => Program.Plant == "starts_too_wide" ? new[] { "CANONICAL_", "RM_" } : Program.Plant == "no_starts" ? new string[0] : JawaBenchCanonicalSaves.Starts;
        // each plant is one way the guard could be broken in what it reads
        static string Eff(string save, string saves = "")
            => S.Effective(File(Program.Plant == "file_names_dropped" ? "" : saves), T0, Program.Plant == "unknown_reads_as_new_game" ? (save ?? "").Trim() : save, Names(), Starts(), out _);
        static string Load(bool game, bool sampler, bool hook, bool tracked, bool unknown, string name)
            => S.LoadedSave(game, sampler, hook || Program.Plant == "hook_assumed", tracked, unknown, name, out _);
        static L Entered(string request, double now = 3)
        {
            var life = new L(null);
            life.OnFrame(null, false, 1);
            if (request != "(none)") life.OnLoadRequested(request, 2);
            life.OnFrame(new object(), true, now);
            return life;
        }

        internal static void Run()
        {
            // the two lists that were on disk on 2026-11-23: ArchBig's, and ArchSmall's (empty; Steve1 and Steve2 the same)
            foreach (var l in new[] { "", "CANONICAL_ASHKARR_START_2026-09-12, Ashkarr, Ashkarr autosave" })
            {
                string g = l == "" ? "empty_list" : "archbig_list";
                Check("gstart.r3_" + g, () => Eff(R3, l) == S.Campaign);
                Check("gstart.frozen_" + g, () => Eff(Frozen, l) == S.Campaign);
            }
            Check("gstart.the_live_call_uses_the_compiled_list", () => S.Effective(File(""), T0, R3, out var why) == S.Campaign && why.Contains("canonical"));

            foreach (var f in new[] { R3.ToLowerInvariant(), R3 + ".rws", R3 + ".RWS", " " + R3 + " ", "C:\\x\\Saves\\" + R3 + ".rws", "Saves/" + R3 })
                Check("gforms.form_" + f.Replace(' ', '_'), () => Eff(f) == S.Campaign);
            Check("gforms.any_canonical_start", () => Eff("canonical_ashkarr_start_2026-10-18_donorfree") == S.Campaign);
            Check("gforms.only_contains_a_guarded_name", () => Eff("RM_x_" + R3) == S.Test && Eff("test_CANONICAL_copy") == S.Test && Eff(R3 + "_mycopy") == S.Test);

            Check("gfree.a_test_save", () => Eff("RM_TestSite_calm_v3") == S.Test && Eff("EK_VISIT5_WALK_20261123") == S.Test && Eff("Autosave-3") == S.Test);
            Check("gfree.a_new_game", () => Eff("") == S.Test);
            Check("gfree.no_file_new_game", () => S.Effective(S.ProfileFile.Parse(null, T0), T0, "", out _) == S.Test);
            Check("gfree.the_tracker_names_a_test_save", () => Load(true, true, true, true, false, "RM_TestSite_calm_v3") == "RM_TestSite_calm_v3" && Eff("RM_TestSite_calm_v3") == S.Test);
            Check("gfree.no_game", () => Load(false, false, false, false, false, null) == "");

            Check("gblind.unknown_name", () => Eff(null) == S.Campaign);
            Check("gblind.blank_name", () => Eff("  ") == S.Campaign && Eff(".rws") == S.Campaign);
            Check("gblind.empty_compiled_list", () => S.Effective(File(""), T0, "RM_TestSite_calm_v3", new string[0], Starts(), out _) == S.Campaign
                                                      && S.Effective(File(""), T0, "RM_TestSite_calm_v3", null, null, out _) == S.Campaign);
            Check("gblind.no_file_loaded_save", () => S.Effective(S.ProfileFile.Parse(null, T0), T0, "RM_TestSite_calm_v3", out _) == S.Campaign);
            Check("gblind.load_hook_absent", () => Load(true, true, false, true, false, "") == null);
            Check("gblind.not_tracked", () => Load(true, true, true, false, false, "") == null && Load(true, false, false, false, false, "") == null);
            Check("gblind.tracker_says_unknown", () => Load(true, true, true, true, true, "") == null);
            Check("gblind.a_load_with_no_name", () => Entered(null).SaveUnknown && Entered(" ").SaveUnknown);
            Check("gblind.a_stale_load_is_unknown", () => Entered(R3, 3600).SaveUnknown);
            Check("gblind.a_new_game_is_known", () => !Entered("(none)").SaveUnknown && Entered("(none)").SaveName == "");
            Check("gblind.a_named_load_is_known", () => !Entered(R3).SaveUnknown && Entered(R3).SaveName == R3);

            Check("gfile.a_name_in_the_file_is_guarded", () => Eff("My Look", "My Look, Other") == S.Campaign && Eff("other", "My Look, Other") == S.Campaign);
            Check("gfile.no_file_content_frees_r3", () => new[] { "", "x", "x, y", "-" + R3, "!" + R3 }.All(l => Eff(R3, l) == S.Campaign));
            Check("gfile.gm_and_old_expiry_free_nothing", () => S.Effective(S.ProfileFile.Parse("{\"profile\": \"gm\", \"expiresUtc\": \"2036-01-01T00:00:00Z\"}", T0), T0, R3, out _) == S.Campaign);
        }
    }
}
