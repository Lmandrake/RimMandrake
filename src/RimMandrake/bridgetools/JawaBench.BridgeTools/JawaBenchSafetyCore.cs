// JawaBenchSafetyCore.cs - the PURE half of the companion's safety surface (no Verse, no Unity, no Harmony).
//
// Items: COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT (campaign/test profiles, per-profile policy, tool families), BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD
// (game epochs, reserved expect* arguments, game-scoped dead-man quiet-world block), COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED
// (the handshake's stable key set). Doc: design/RimMandrake/companion_handshake.md.
//
// ⛔ Compiled into bridgetools/AwarenessSelfTest too (UnitsSafety.cs): a `using Verse;` here breaks that build.
//
// THE PROFILE LAW (owner rulings by question card 2026-10-10, relayed by the coordinator)
//   * Two runtime profiles. CAMPAIGN is the default: the bridge stays FULLY usable for authoring (spawn, edit,
//     incidents, raids, inhabited interactions, content edits). It switches OFF only what costs play speed or is
//     test-only: arbitrary invocation / debug actions, test-only tools, heavy diagnostics, the quiet-world block,
//     and the costly awareness hook (GeneratePawn). TEST is the permissive profile for test/diagnostic setups.
//   * Cheap always-on recorders stay ON in campaign, INCLUDING the TPS attribution that says where a slowdown comes
//     from, so a slowdown is explained, not hidden. Each profile DECLARES its recorder budget (share of play speed the
//     recorders may cost) as data in Policies below - campaign 10% "for now" - never as a constant inside a hook.
//   * TEST is granted ONLY by JawaBench/companion_profile.json ("profile": "test"; "gm" is accepted as an alias),
//     unexpired, and only while the loaded save is not one of its "campaignSaves". Nothing a bridge client sends
//     raises the profile. Anything unreadable resolves to CAMPAIGN.
//   * Every jawa tool belongs to a FAMILY (CampaignDenied names each denied tool and its family + reason; the rest are
//     authoring or read). The unit test fails when a must-stay-available authoring tool is denied or a must-be-off
//     tool is allowed. The compile-time GM flag (JAWA_GM_TOOLS) still decides whether the GM tools EXIST.
//   * RimBridgeServer's own tools (rimworld/*) are not ours and are not gated here.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchSafetyCore
    {
        internal const string Campaign = "campaign", Test = "test";
        internal const string HandshakeTool = "jawa/companion_handshake";
        internal const string ProfileFileName = "companion_profile.json";

        // ------------------------------------------------------------------ per-profile policy (DATA, read by installers/hooks)
        internal sealed class Policy
        {
            internal string Name;
            /// <summary>Declared ceiling on how much play speed the always-on recorders may cost, as a share (0.10 = the
            /// game may run up to 10% slower because of them). Reported and judged (BudgetVerdict); never enforced by
            /// silently switching a recorder off, which would hide the slowdown it explains.</summary>
            internal double RecorderBudgetShare;
            internal bool TpsSampler, TpsAttribution;        // cheap, always on: they explain a slowdown
            internal bool AwarenessCheapHooks;               // incident journal, spawn, context scopes
            internal bool AwarenessGenerationHook;           // GeneratePawn: the hottest hook
            internal bool WildSpawnerBlock;                  // quiet-world block (a test fixture)
            internal bool DenyCampaignFamilies;              // refuse the CampaignDenied tools
        }

        internal static readonly Policy CampaignPolicy = new Policy
        {
            Name = Campaign, RecorderBudgetShare = 0.10, TpsSampler = true, TpsAttribution = true, AwarenessCheapHooks = true,
            AwarenessGenerationHook = false, WildSpawnerBlock = false, DenyCampaignFamilies = true,
        };

        internal static readonly Policy TestPolicy = new Policy
        {
            Name = Test, RecorderBudgetShare = 1.00, TpsSampler = true, TpsAttribution = true, AwarenessCheapHooks = true,
            AwarenessGenerationHook = true, WildSpawnerBlock = true, DenyCampaignFamilies = false,
        };

        internal static Policy PolicyFor(string profile) => profile == Test ? TestPolicy : CampaignPolicy;

        /// <summary>within | over | unmeasured: recorder seconds against wall seconds of play, for a profile's budget.
        /// The share is recorder / (wall - recorder): the slowdown relative to play without the recorders.</summary>
        internal static string BudgetVerdict(double recorderSeconds, double playSeconds, Policy p, out double share)
        {
            share = double.NaN;
            if (p == null || double.IsNaN(recorderSeconds) || recorderSeconds < 0 || !(playSeconds > 0) || recorderSeconds >= playSeconds)
                return "unmeasured";
            share = recorderSeconds / (playSeconds - recorderSeconds);
            return share <= p.RecorderBudgetShare ? "within" : "over";
        }

        // ------------------------------------------------------------------ tool families denied in CAMPAIGN
        internal const string FDebugInvoke = "debug-invoke", FTestOnly = "test-only", FHeavyDiagnostic = "heavy-diagnostic",
                              FQuietWorld = "quiet-world";

        internal static readonly Dictionary<string, string> FamilyReasons = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [FDebugInvoke] = "arbitrary invocation / debug actions / def hot-reload: can do anything, including slow or destructive things",
            [FTestOnly] = "a test fixture or harness driver: freezes the game, injects faults or runs playtest drivers",
            [FHeavyDiagnostic] = "a whole-game diagnostic sweep (reflection over every assembly, every tile, every def): seconds of main thread",
            [FQuietWorld] = "a quiet-world test control that suppresses vanilla behaviour",
        };

        /// <summary>The tools CAMPAIGN refuses, each with its family. Everything else is authoring or read and stays
        /// available. Adding to this list is a decision about the owner's play, not a convenience.</summary>
        internal static readonly Dictionary<string, string> CampaignDenied = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["jawa/static_call"] = FDebugInvoke, ["jawa/debug_actions"] = FDebugInvoke, ["jawa/debug_action_yielders"] = FDebugInvoke,
            ["jawa/debug_settings"] = FDebugInvoke, ["jawa/hot_reload_defs"] = FDebugInvoke, ["jawa/stat_cache_bust"] = FDebugInvoke,
            ["jawa/tps_test_block"] = FTestOnly, ["jawa/tps_test_attribution"] = FTestOnly,
            ["jawa/playtest_start"] = FTestOnly, ["jawa/playtest_collect"] = FTestOnly, ["jawa/playtest_status"] = FTestOnly,
            ["jawa/gss_playtest_start"] = FTestOnly, ["jawa/gss_playtest_collect"] = FTestOnly, ["jawa/gss_playtest_status"] = FTestOnly,
            ["jawa/gss_stage"] = FTestOnly, ["jawa/oracle_selftest"] = FTestOnly, ["jawa/oracle_test_ohm_letter"] = FTestOnly,
            ["jawa/load_stall_probe"] = FTestOnly, ["jawa/flowworks_job_probe"] = FTestOnly, ["jawa/map_comp_timing"] = FTestOnly,
            ["jawa/telemetry_tier"] = FTestOnly,      // owner 2026-10-11: campaign never runs the T0/T1 test tier
            ["jawa/type_visibility"] = FHeavyDiagnostic, ["jawa/startup_types"] = FHeavyDiagnostic, ["jawa/forecast_incidents"] = FHeavyDiagnostic,
            ["jawa/world_cache_audit"] = FHeavyDiagnostic, ["jawa/tile_cache_audit"] = FHeavyDiagnostic, ["jawa/texture_audit"] = FHeavyDiagnostic,
            ["jawa/biome_art_audit"] = FHeavyDiagnostic, ["jawa/pawnkind_audit"] = FHeavyDiagnostic, ["jawa/world_mutators_audit"] = FHeavyDiagnostic,
            ["jawa/world_lint"] = FHeavyDiagnostic, ["jawa/rimdefdump_run"] = FHeavyDiagnostic, ["jawa/export_things"] = FHeavyDiagnostic,
            ["jawa/wild_spawner_block"] = FQuietWorld,
        };

        /// <summary>Tripwire for the unit test: authoring tools the owner ruled must stay usable in campaign.</summary>
        internal static readonly string[] MustStayInCampaign =
        {
            "jawa/spawn_pawn", "jawa/spawn_batch", "jawa/fire_raid", "jawa/raid_shape_fire", "jawa/incident_schedule",
            "jawa/inhabited_settlement_create", "jawa/lord_assault_spawn", "jawa/set_terrain", "jawa/set_pawn_backstory",
            "jawa/world_tile_set", "jawa/pawn_health", "jawa/destroy_batch", "jawa/map_info", "jawa/tps_report", "jawa/awareness",
            "jawa/incident_journal", "jawa/pawn_origin", "jawa/thing_explain", "jawa/bridge_arg_report", "jawa/harmony_patches",
        };

        /// <summary>Tripwire for the unit test: what the owner ruled OFF in campaign.</summary>
        internal static readonly string[] MustBeOffInCampaign =
        {
            "jawa/static_call", "jawa/debug_actions", "jawa/hot_reload_defs", "jawa/wild_spawner_block", "jawa/tps_test_block",
            "jawa/tps_test_attribution", "jawa/forecast_incidents", "jawa/type_visibility", "jawa/startup_types",
        };

        internal static bool Allowed(string tool, string effectiveProfile)
        {
            if (tool == HandshakeTool) return true;
            if (!PolicyFor(effectiveProfile).DenyCampaignFamilies) return true;
            return tool != null && !CampaignDenied.ContainsKey(tool);
        }

        internal static string FamilyOf(string tool) => tool != null && CampaignDenied.TryGetValue(tool, out var f) ? f : "authoring-or-read";

        internal static string RefusalText(string tool, string why)
        {
            string fam = FamilyOf(tool);
            string reason = FamilyReasons.TryGetValue(fam, out var r) ? r : fam;
            return "REFUSED in the CAMPAIGN profile: " + tool + " is " + fam + " (" + reason + "); profile: " + why + ". " +
                   "Authoring tools stay available. Test/diagnostic tools run only when <SaveData>/JawaBench/" + ProfileFileName +
                   " says {\"profile\": \"test\"}, is unexpired, and the loaded save is not one of its campaignSaves. " +
                   "Call jawa/companion_handshake to see the profile.";
        }

        // ------------------------------------------------------------------ the profile file
        internal sealed class ProfileFile
        {
            internal bool Present;
            internal string Profile, Error;
            internal string[] CampaignSaves = new string[0];
            internal DateTime? ExpiresUtc;

            /// <summary>{"profile": "test"|"gm"|"campaign", "expiresUtc": "ISO-8601", "campaignSaves": "a, b"} (flat JSON).
            /// Null or empty = no file. Anything unreadable is an Error, and an Error is CAMPAIGN.</summary>
            internal static ProfileFile Parse(string json, DateTime nowUtc)
            {
                var f = new ProfileFile();
                if (string.IsNullOrWhiteSpace(json)) return f;
                f.Present = true;
                string err = JawaBenchTpsSettings.ParseFlat(json, out var kv);
                if (err != null) { f.Error = "invalid profile file (" + err + ")"; return f; }
                foreach (var p in kv)
                {
                    switch (p.Key)
                    {
                        case "profile":
                            f.Profile = p.Value as string;
                            if (f.Profile == null) f.Error = "profile is not a string";
                            else if (f.Profile == "gm") f.Profile = Test;      // alias
                            break;
                        case "expiresUtc":
                            if (p.Value is string s && DateTime.TryParse(s, CultureInfo.InvariantCulture,
                                    DateTimeStyles.AdjustToUniversal | DateTimeStyles.AssumeUniversal, out var t)) f.ExpiresUtc = t;
                            else f.Error = "expiresUtc is not an ISO-8601 time";
                            break;
                        case "campaignSaves":
                            if (p.Value is string cs)
                                f.CampaignSaves = cs.Split(',').Select(x => x.Trim()).Where(x => x.Length > 0).ToArray();
                            else f.Error = "campaignSaves is not a comma-separated string";
                            break;
                        default:
                            break;      // unknown keys are tolerated (a newer launcher may add fields)
                    }
                }
                return f;
            }
        }

        /// <summary>The effective profile, with the reason. Anything short of a clean, unexpired test file is CAMPAIGN.</summary>
        internal static string Effective(ProfileFile f, DateTime nowUtc, string loadedSave, out string why)
        {
            if (f == null || !f.Present) { why = "no profile file: campaign by default"; return Campaign; }
            if (f.Error != null) { why = f.Error + ": campaign"; return Campaign; }
            if (f.Profile == Campaign) { why = "profile file says campaign"; return Campaign; }
            if (f.Profile != Test) { why = "unknown profile '" + f.Profile + "': campaign"; return Campaign; }
            if (f.ExpiresUtc.HasValue && nowUtc >= f.ExpiresUtc.Value)
            {
                why = "test profile expired at " + f.ExpiresUtc.Value.ToString("o", CultureInfo.InvariantCulture) + ": campaign";
                return Campaign;
            }
            if (loadedSave != null && f.CampaignSaves.Any(c => string.Equals(c, loadedSave.Trim(), StringComparison.OrdinalIgnoreCase)))
            {
                why = "loaded save '" + loadedSave + "' is a listed campaign save: campaign";
                return Campaign;
            }
            why = "profile file says test" + (f.ExpiresUtc.HasValue ? " until " + f.ExpiresUtc.Value.ToString("o", CultureInfo.InvariantCulture) : "");
            return Test;
        }

        // ------------------------------------------------------------------ game epochs (identity, not ticks)
        /// <summary>A counter that moves whenever the Game OBJECT changes. A reload of the same save at the same tick is
        /// a new object, so it is a new epoch. Weakly held: the tracker never keeps an old game alive.</summary>
        internal sealed class GameEpochs
        {
            private readonly object _gate = new object();
            private WeakReference _last;
            private int _epoch;

            /// <summary>0 when there is no game; otherwise the epoch of this game object.</summary>
            internal int For(object game)
            {
                lock (_gate)
                {
                    if (game == null) { _last = null; return 0; }
                    var prev = _last?.Target;
                    if (!ReferenceEquals(prev, game)) { _epoch++; _last = new WeakReference(game); }
                    return _epoch;
                }
            }

            internal int Last { get { lock (_gate) return _epoch; } }
        }

        /// <summary>Call arguments the companion reserves on EVERY jawa tool (read by the binder hook, never declared by
        /// a tool): a caller that cached a target names the world it was taken from, and a stale call is refused.</summary>
        internal static readonly string[] ReservedArgs = { "expectGameEpoch", "expectMapId", "expectCurrentMapId" };

        internal static string ParseExpect(object v, out int value)
        {
            value = 0;
            switch (v)
            {
                case int i: value = i; return null;
                case long l when l >= int.MinValue && l <= int.MaxValue: value = (int)l; return null;
                case double d when Math.Abs(d - Math.Round(d)) < 1e-9 && Math.Abs(d) < int.MaxValue: value = (int)Math.Round(d); return null;
                case string s when int.TryParse(s.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out var p): value = p; return null;
                default: return "not an integer: " + (v == null ? "null" : v.ToString());
            }
        }

        internal static string CheckExpect(int? expectEpoch, int currentEpoch)
        {
            if (!expectEpoch.HasValue || expectEpoch.Value == currentEpoch) return null;
            return "REFUSED: stale target - the caller expected game epoch " + expectEpoch.Value + " but the loaded game is epoch " +
                   currentEpoch + " (a load, a new game or a return to the menu happened since). Re-read targets via jawa/companion_handshake.";
        }

        internal static string CheckMaps(int? expectMapId, int? expectCurrentMapId, IList<int> mapIds, int currentMapId)
        {
            if (expectMapId.HasValue && (mapIds == null || !mapIds.Contains(expectMapId.Value)))
                return "REFUSED: stale target - map " + expectMapId.Value + " is not in this game (culled, abandoned or from another game). Maps now: " +
                       (mapIds == null ? "none" : string.Join(",", mapIds));
            if (expectCurrentMapId.HasValue && expectCurrentMapId.Value != currentMapId)
                return "REFUSED: stale target - the caller expected current map " + expectCurrentMapId.Value + " but the current map is " + currentMapId;
            return null;
        }

        // ------------------------------------------------------------------ quiet-world block (game-scoped, dead-man)
        /// <summary>A block that releases itself: on expiry (no renewal = the runner died), when the game object changes
        /// (new game or load), or when no game is loaded. The release reason is kept for the status tools.</summary>
        internal sealed class QuietBlock
        {
            internal const double DefaultMinutes = 30, MaxMinutes = 240;
            private readonly object _gate = new object();
            private WeakReference _game;
            private double _untilS;
            private bool _on;
            internal string By, LastRelease;

            internal void Block(object game, double nowS, double minutes, string by)
            {
                double m = double.IsNaN(minutes) || minutes <= 0 ? DefaultMinutes : Math.Min(minutes, MaxMinutes);
                lock (_gate) { _game = game == null ? null : new WeakReference(game); _untilS = nowS + m * 60.0; _on = game != null; By = by; }
            }

            internal void Release(string reason) { lock (_gate) { if (_on) LastRelease = reason; _on = false; _game = null; } }

            internal bool Active(object game, double nowS)
            {
                lock (_gate)
                {
                    if (!_on) return false;
                    if (game == null) { _on = false; LastRelease = "no-game"; _game = null; return false; }
                    if (!ReferenceEquals(_game?.Target, game)) { _on = false; LastRelease = "new-game"; _game = null; return false; }
                    if (nowS >= _untilS) { _on = false; LastRelease = "expired"; _game = null; return false; }
                    return true;
                }
            }

            internal bool On { get { lock (_gate) return _on; } }
            internal double UntilS { get { lock (_gate) return _untilS; } }
        }

        // ------------------------------------------------------------------ the handshake (stable schema)
        internal const string HandshakeSchema = "companion_handshake/1";   // not yet deployed anywhere: still /1

        /// <summary>The top-level keys, in order. Changing this list is a schema change: bump HandshakeSchema and update
        /// design/RimMandrake/companion_handshake.md in the same commit.</summary>
        internal static readonly string[] HandshakeKeys =
        {
            "schema", "success", "utc", "companionAssembly", "companionVersion", "companionSha", "companionMvid",
            "companionFileSha256", "companionPath", "compileProfile", "runtimeProfile", "effectiveProfile", "profileWhy",
            "profileFile", "policy", "gate", "hooks", "rimBridgeServer", "harmony", "game", "reservedArgs",
        };

        internal sealed class HandshakeInput
        {
            internal string Utc, CompanionAssembly, CompanionVersion, CompanionSha, CompanionMvid, CompanionFileSha256, CompanionPath;
            internal string CompileProfile, RuntimeProfile, EffectiveProfile, ProfileWhy, ProfileFile;
            internal object Policy, Gate, Hooks, RimBridgeServer, Harmony, Game;
        }

        internal static Dictionary<string, object> ComposeHandshake(HandshakeInput i)
        {
            var d = new Dictionary<string, object>(StringComparer.Ordinal)
            {
                ["schema"] = HandshakeSchema,
                ["success"] = true,
                ["utc"] = i.Utc,
                ["companionAssembly"] = i.CompanionAssembly,
                ["companionVersion"] = i.CompanionVersion,
                ["companionSha"] = i.CompanionSha,
                ["companionMvid"] = i.CompanionMvid,
                ["companionFileSha256"] = i.CompanionFileSha256,
                ["companionPath"] = i.CompanionPath,
                ["compileProfile"] = i.CompileProfile,
                ["runtimeProfile"] = i.RuntimeProfile,
                ["effectiveProfile"] = i.EffectiveProfile == Test ? Test : Campaign,   // anything unresolved reads CAMPAIGN
                ["profileWhy"] = i.ProfileWhy,
                ["profileFile"] = i.ProfileFile,
                ["policy"] = i.Policy,
                ["gate"] = i.Gate,
                ["hooks"] = i.Hooks,
                ["rimBridgeServer"] = i.RimBridgeServer,
                ["harmony"] = i.Harmony,
                ["game"] = i.Game,
                ["reservedArgs"] = ReservedArgs,
            };
            return d;
        }
    }
}
