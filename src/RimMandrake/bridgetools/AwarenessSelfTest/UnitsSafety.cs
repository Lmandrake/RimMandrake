// Units for the companion's safety core (JawaBenchSafetyCore.cs, the PRODUCTION file):
//   COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT   runtime profile resolution + the tool census against the allow-list
//   BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD   game epochs by identity, reserved expect* arguments, quiet-world block
//   COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED  the handshake's stable key set
//   AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE      the install.generation-early option
// The tool census reads the companion's OWN source files (staged beside this harness), so a new [Tool] that is
// not reviewed can never be "safe" by omission: the allow-list is the only way in.
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

            // --- profile resolution: default safe, gm only by an unexpired file, campaign saves always safe
            var none = S.ProfileFile.Parse(null, t0);
            check(S.Effective(none, t0, null, out var why0) == S.Safe && why0.Contains("no profile file"), "profile_default_is_safe", why0);
            var gm = S.ProfileFile.Parse("{\"profile\": \"gm\"}", t0);
            check(S.Effective(gm, t0, "test save", out var why1) == S.Gm, "profile_file_gm_is_gm", why1);
            var exp = S.ProfileFile.Parse("{\"profile\": \"gm\", \"expiresUtc\": \"2026-10-10T11:00:00Z\"}", t0);
            check(S.Effective(exp, t0, null, out var why2) == S.Safe && why2.Contains("expired"), "profile_expired_gm_is_safe", why2);
            var camp = S.ProfileFile.Parse("{\"profile\": \"gm\", \"campaignSaves\": \"Ashkarr Campaign, Other\"}", t0);
            check(S.Effective(camp, t0, "Ashkarr Campaign", out var why3) == S.Safe && why3.Contains("campaign"), "campaign_save_forces_safe", why3);
            check(S.Effective(camp, t0, "quicktest", out _) == S.Gm, "non_campaign_save_keeps_gm");
            var bad = S.ProfileFile.Parse("{\"profile\": gm", t0);
            check(S.Effective(bad, t0, null, out var why4) == S.Safe && why4.Contains("invalid"), "invalid_profile_file_is_safe", why4);
            var odd = S.ProfileFile.Parse("{\"profile\": \"godmode\"}", t0);
            check(S.Effective(odd, t0, null, out var why5) == S.Safe && why5.Contains("godmode"), "unknown_profile_value_is_safe", why5);

            // --- the tool census: every [Tool] in the companion source, classified by the production allow-list
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
            var leaks = S.MustNeverBeSafe.Where(t => S.Allowed(t, S.Safe)).ToList();
            check(leaks.Count == 0, "dangerous_tools_refused_in_safe", string.Join(",", leaks));
            var missingDanger = S.MustNeverBeSafe.Where(t => !tools.Contains(t)).ToList();
            check(missingDanger.Count == 0, "danger_list_names_real_tools", string.Join(",", missingDanger));
            var safeAllowed = tools.Where(t => S.Allowed(t, S.Safe)).ToList();
            var verbLeaks = safeAllowed.Where(S.NameLooksMutating).ToList();
            check(verbLeaks.Count == 0, "no_mutating_verb_in_safe_profile", string.Join(",", verbLeaks));
            var phantom = S.SafeAllowList.Where(t => !tools.Contains(t) && t != S.HandshakeTool).ToList();
            check(phantom.Count == 0, "allow_list_names_real_tools", string.Join(",", phantom));
            check(safeAllowed.Count > 0 && safeAllowed.Count < tools.Count / 2, "safe_profile_is_a_small_reviewed_set", safeAllowed.Count + " of " + tools.Count);
            check(tools.All(t => S.Allowed(t, S.Gm)), "gm_profile_allows_every_tool");
            check(S.Allowed(S.HandshakeTool, S.Safe), "handshake_is_always_allowed");
            check(!S.Allowed("jawa/some_new_tool", S.Safe), "unreviewed_tool_is_refused_in_safe");
            check(S.RefusalText("jawa/static_call", "no profile file").Contains("companion_profile.json"), "refusal_says_how_to_enable", S.RefusalText("jawa/static_call", "x"));

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
            var h = S.ComposeHandshake(new S.HandshakeInput { CompanionSha = "abc", CompileProfile = "gm", RuntimeProfile = "safe" });
            check(h.Keys.SequenceEqual(S.HandshakeKeys), "handshake_keys_stable", string.Join(",", h.Keys));
            check((string)h["schema"] == S.HandshakeSchema && S.HandshakeSchema == "companion_handshake/1", "handshake_schema_versioned");
            check((string)h["effectiveProfile"] == "safe" && (bool)h["success"], "handshake_reports_effective_profile");
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
