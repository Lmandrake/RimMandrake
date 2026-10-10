// Units for the companion's safety core (JawaBenchSafetyCore.cs, the PRODUCTION file):
//   COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT   campaign/test profile resolution, per-profile policy + budget, tool families
//   BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD   game epochs by identity, reserved expect* arguments, quiet-world block
//   COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED  the handshake's stable key set
//   AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE      the install.generation-early option
// The tool census reads the companion's OWN source files (staged beside this harness), so every family list is
// checked against the real tool surface (no phantom names) and the owner's must-stay / must-be-off tripwires hold.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using A = JawaBench.BridgeTools.JawaBenchAwarenessCore;
using S = JawaBench.BridgeTools.JawaBenchSafetyCore;

namespace JawaBench.BridgeTools
{
    internal static class SafetyUnits
    {
        internal static void Run(Action<bool, string, string> c)
        {
            void check(bool ok, string name, string why = "") => c(ok, name, why);
            var t0 = new DateTime(2026, 10, 10, 12, 0, 0, DateTimeKind.Utc);

            // --- profile resolution: default CAMPAIGN, test only by an unexpired file, campaign saves always campaign
            var none = S.ProfileFile.Parse(null, t0);
            check(S.Effective(none, t0, null, out var why0) == S.Campaign && why0.Contains("no profile file"), "profile_default_is_campaign", why0);
            var tst = S.ProfileFile.Parse("{\"profile\": \"test\"}", t0);
            check(S.Effective(tst, t0, "test save", out var why1) == S.Test, "profile_file_test_is_test", why1);
            check(S.Effective(S.ProfileFile.Parse("{\"profile\": \"gm\"}", t0), t0, null, out _) == S.Test, "profile_gm_is_alias_for_test");
            var exp = S.ProfileFile.Parse("{\"profile\": \"test\", \"expiresUtc\": \"2026-10-10T11:00:00Z\"}", t0);
            check(S.Effective(exp, t0, null, out var why2) == S.Campaign && why2.Contains("expired"), "profile_expired_test_is_campaign", why2);
            var camp = S.ProfileFile.Parse("{\"profile\": \"test\", \"campaignSaves\": \"Ashkarr Campaign, Other\"}", t0);
            check(S.Effective(camp, t0, "Ashkarr Campaign", out var why3) == S.Campaign && why3.Contains("campaign save"), "campaign_save_forces_campaign", why3);
            check(S.Effective(camp, t0, "quicktest", out _) == S.Test, "non_campaign_save_keeps_test");
            var bad = S.ProfileFile.Parse("{\"profile\": gm", t0);
            check(S.Effective(bad, t0, null, out var why4) == S.Campaign && why4.Contains("invalid"), "invalid_profile_file_is_campaign", why4);
            var odd = S.ProfileFile.Parse("{\"profile\": \"godmode\"}", t0);
            check(S.Effective(odd, t0, null, out var why5) == S.Campaign && why5.Contains("godmode"), "unknown_profile_value_is_campaign", why5);

            // --- per-profile policy is DATA: the declared recorder budget and the switches the installers read
            var cp = S.PolicyFor(S.Campaign); var tp = S.PolicyFor(S.Test);
            check(Math.Abs(cp.RecorderBudgetShare - 0.10) < 1e-12 && tp.RecorderBudgetShare > cp.RecorderBudgetShare, "budget_declared_per_profile_campaign_10pct", cp.RecorderBudgetShare + " / " + tp.RecorderBudgetShare);
            check(cp.TpsSampler && cp.TpsAttribution && cp.AwarenessCheapHooks, "campaign_keeps_cheap_recorders_and_attribution");
            check(!cp.AwarenessGenerationHook && !cp.WildSpawnerBlock && tp.AwarenessGenerationHook && tp.WildSpawnerBlock, "campaign_switches_off_costly_and_test_recorders");
            check(S.PolicyFor(null) == cp && S.PolicyFor("weird") == cp, "unknown_profile_gets_campaign_policy");
            check(S.BudgetVerdict(9, 109, cp, out var sh1) == "within" && Math.Abs(sh1 - 0.09) < 1e-9, "budget_within", sh1.ToString());
            check(S.BudgetVerdict(12, 112, cp, out _) == "over" && S.BudgetVerdict(12, 112, tp, out _) == "within", "budget_over_in_campaign_within_in_test");
            check(S.BudgetVerdict(double.NaN, 100, cp, out _) == "unmeasured" && S.BudgetVerdict(1, 0, cp, out _) == "unmeasured", "budget_unmeasured_never_within");

            // --- the tool census: every [Tool] in the companion source, classified by the production family table
            var dir = CompanionDir();
            check(dir != null, "companion_sources_found", "could not locate JawaBench.BridgeTools beside the harness");
            var tools = new List<string>();
            if (dir != null)
                foreach (var f in Directory.GetFiles(dir, "*.cs"))
                    foreach (Match m in Regex.Matches(File.ReadAllText(f), "\\[Tool\\(\\s*\"(jawa/[A-Za-z0-9_/]+)\""))
                        tools.Add(m.Groups[1].Value);
            tools = tools.Distinct().ToList();
            check(tools.Count >= 300, "census_sees_the_surface", "only " + tools.Count + " tools found");
            check(tools.Contains("jawa/static_call") && tools.Contains("jawa/tps_report"), "census_sanity_probe_known_tools", string.Join(",", tools.Take(5)));
            var on = S.MustBeOffInCampaign.Where(t => S.Allowed(t, S.Campaign)).ToList();
            check(on.Count == 0, "debug_test_tools_refused_in_campaign", string.Join(",", on));
            var off = S.MustStayInCampaign.Where(t => !S.Allowed(t, S.Campaign)).ToList();
            check(off.Count == 0, "authoring_tools_stay_in_campaign", string.Join(",", off));
            var phantom = S.CampaignDenied.Keys.Concat(S.MustStayInCampaign).Concat(S.MustBeOffInCampaign).Where(t => !tools.Contains(t)).Distinct().ToList();
            check(phantom.Count == 0, "family_lists_name_real_tools", string.Join(",", phantom));
            var noReason = S.CampaignDenied.Where(kv => !S.FamilyReasons.ContainsKey(kv.Value)).Select(kv => kv.Key).ToList();
            check(noReason.Count == 0, "every_denied_tool_has_a_family_reason", string.Join(",", noReason));
            int denied = tools.Count(t => !S.Allowed(t, S.Campaign));
            check(denied > 0 && denied < tools.Count / 5, "campaign_denies_a_small_set", denied + " of " + tools.Count);
            check(tools.All(t => S.Allowed(t, S.Test)), "test_profile_allows_every_tool");
            check(S.Allowed(S.HandshakeTool, S.Campaign), "handshake_is_always_allowed");
            check(S.Allowed("jawa/some_new_authoring_tool", S.Campaign), "unlisted_tool_stays_available_in_campaign");
            check(S.RefusalText("jawa/static_call", "no profile file").Contains("companion_profile.json") && S.RefusalText("jawa/static_call", "x").Contains("debug-invoke"),
                  "refusal_names_family_and_how_to_enable", S.RefusalText("jawa/static_call", "x"));

            // --- game epochs by object identity (equal-tick reloads are a NEW object)
            var ep = new S.GameEpochs();
            object g1 = new object(), g2 = new object();
            int e1 = ep.For(g1);
            check(e1 == 1 && ep.For(g1) == 1, "same_game_same_epoch", e1.ToString());
            int e2 = ep.For(g2);
            check(e2 == 2, "new_game_object_new_epoch_even_at_equal_tick", e2.ToString());
            check(ep.For(null) == 0 && ep.For(g2) == 3, "no_game_is_epoch_zero_and_next_game_is_new", "");
            check(S.CheckExpect(null, 3) == null && S.CheckExpect(3, 3) == null, "expect_epoch_match_or_absent_passes");
            check(S.CheckExpect(2, 3) != null && S.CheckExpect(2, 3).Contains("stale"), "expect_epoch_mismatch_refused", S.CheckExpect(2, 3));
            var maps = new List<int> { 1, 2 };
            check(S.CheckMaps(null, null, maps, 1) == null && S.CheckMaps(2, 1, maps, 1) == null, "map_expectations_match_pass");
            check(S.CheckMaps(5, null, maps, 1) != null, "culled_or_foreign_map_refused", S.CheckMaps(5, null, maps, 1));
            check(S.CheckMaps(null, 2, maps, 1) != null, "switched_current_map_refused", S.CheckMaps(null, 2, maps, 1));
            check(S.ParseExpect(3L, out var v1) == null && v1 == 3 && S.ParseExpect(4.0, out var v2) == null && v2 == 4
                  && S.ParseExpect("5", out var v3) == null && v3 == 5, "expect_args_accept_json_number_forms");
            check(S.ParseExpect("x", out _) != null && S.ParseExpect(4.5, out _) != null, "expect_args_reject_non_integers");
            check(S.ReservedArgs.Contains("expectGameEpoch") && S.ReservedArgs.Contains("expectMapId") && S.ReservedArgs.Contains("expectCurrentMapId"), "reserved_args_named");

            // --- quiet-world block: game-scoped and dead-man (TTL), release reasons recorded
            var qb = new S.QuietBlock();
            check(!qb.Active(g1, 0), "quiet_block_off_by_default");
            qb.Block(g1, 0, 30, "test");
            check(qb.Active(g1, 10) && qb.Active(g1, 29 * 60), "quiet_block_active_within_ttl");
            check(!qb.Active(g2, 30) && qb.LastRelease == "new-game", "quiet_block_released_on_new_game", qb.LastRelease);
            check(!qb.Active(g1, 40), "quiet_block_stays_released_after_new_game");
            qb.Block(g1, 100, 30, "test");
            check(!qb.Active(g1, 100 + 30 * 60 + 1) && qb.LastRelease == "expired", "quiet_block_dead_man_expiry", qb.LastRelease);
            qb.Block(g1, 0, 100000, "test");
            check(qb.Active(g1, 239 * 60) && !qb.Active(g1, 241 * 60), "quiet_block_ttl_capped_240min");
            qb.Block(g1, 0, 30, "test"); qb.Release("released");
            check(!qb.Active(g1, 1) && qb.LastRelease == "released", "quiet_block_explicit_release");
            qb.Block(g1, 0, 30, "test");
            object gone = null;
            check(!qb.Active(gone, 1) && qb.LastRelease == "no-game", "quiet_block_released_when_game_left", qb.LastRelease);

            // --- awareness install option: GeneratePawn lazy unless asked
            check(!A.Switches.Parse(null).Option(A.OptGenerationEarly), "generation_hook_lazy_by_default");
            var o = A.Switches.Parse("{\"install.generation-early\": true}");
            check(o.Option(A.OptGenerationEarly) && o.Note == "ok", "generation_early_option_parses", o.Note);
            check(A.Switches.Parse("{\"install.generation-early\": 1}").Note.Contains("not a bool"), "generation_option_must_be_bool");

            // --- handshake: one stable key set, in order
            var h = S.ComposeHandshake(new S.HandshakeInput { CompanionSha = "abc", CompileProfile = "gm", RuntimeProfile = "none" });
            check(h.Keys.SequenceEqual(S.HandshakeKeys), "handshake_keys_stable", string.Join(",", h.Keys));
            check((string)h["schema"] == S.HandshakeSchema && S.HandshakeSchema == "companion_handshake/1", "handshake_schema_versioned");
            check((string)h["effectiveProfile"] == "campaign" && (bool)h["success"], "handshake_unresolved_profile_reads_campaign");
        }

        /// <summary>The companion's sources: staged beside this harness (bridgetools/JawaBench.BridgeTools), found by
        /// walking up from the running assembly. Null when not found (the census then FAILS, never passes).</summary>
        private static string CompanionDir()
        {
            var d = new DirectoryInfo(AppContext.BaseDirectory);
            for (int i = 0; i < 8 && d != null; i++, d = d.Parent)
            {
                var c = Path.Combine(d.FullName, "JawaBench.BridgeTools");
                if (File.Exists(Path.Combine(c, "JawaBench.BridgeTools.csproj"))) return c;
            }
            return null;
        }
    }
}
