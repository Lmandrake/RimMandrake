// JawaBenchSafetyCore.cs - the PURE half of the companion's safety surface (no Verse, no Unity, no Harmony).
//
// Items: COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT (runtime profile + allow-list), BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD
// (game epochs, reserved expect* arguments, game-scoped dead-man quiet-world block), COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED
// (the handshake's stable key set). Doc: design/RimMandrake/companion_handshake.md.
//
// ⛔ Compiled into bridgetools/AwarenessSelfTest too (UnitsSafety.cs): a `using Verse;` here breaks that build.
//
// THE PROFILE LAW
//   * The DEFAULT is SAFE. Only tools on SafeAllowList (reviewed read-only; audit 2026-10-10) run in the safe profile.
//     Every other jawa tool - including any tool added later and never reviewed - is refused. Fail closed.
//   * GM is granted ONLY by JawaBench/companion_profile.json saying "profile": "gm", unexpired, and only while the
//     loaded save is not one of its "campaignSaves". Nothing a bridge client can send raises the profile.
//   * The compile-time GM flag (JAWA_GM_TOOLS) still decides whether the world-acting GM tools EXIST; the runtime
//     profile decides whether anything beyond the allow-list may RUN. Both are reported by the handshake.
//   * RimBridgeServer's own built-in tools (rimworld/*) are NOT ours and are not gated here: stripping companion
//     exports does not make the host read-only (GPT bridge review 4.8).

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchSafetyCore
    {
        internal const string Safe = "safe", Gm = "gm";
        internal const string HandshakeTool = "jawa/companion_handshake";
        internal const string ProfileFileName = "companion_profile.json";

        /// <summary>Reviewed read-only tools (static audit 2026-10-10: no game, file, setting or RNG mutation found in
        /// the body; several are still COSTLY on a large map - see companion_handshake.md). Adding a tool here is a
        /// review decision, never a convenience.</summary>
        internal static readonly string[] SafeAllowList =
        {
            HandshakeTool, "jawa/tps_report", "jawa/awareness", "jawa/incident_journal", "jawa/pawn_origin", "jawa/thing_explain",
            "jawa/harmony_patches", "jawa/running_mods", "jawa/mod_inventory", "jawa/dlc_status", "jawa/savegame_mod_match",
            "jawa/startup_types", "jawa/map_info", "jawa/list_pawns", "jawa/list_things", "jawa/list_factions", "jawa/letter_list",
            "jawa/alerts_list", "jawa/weather_get", "jawa/gravship_status", "jawa/time_clock", "jawa/time_date_at",
            "jawa/world_info_get", "jawa/world_stats", "jawa/pawn_get", "jawa/pawn_stats", "jawa/thing_stats", "jawa/stat_explain",
            "jawa/get_def", "jawa/get_defs", "jawa/inspect_string", "jawa/story_stats", "jawa/room_get", "jawa/power_net",
            "jawa/pipe_net_info", "jawa/comp_read", "jawa/map_comp_read", "jawa/faction_relations_get", "jawa/faction_name_get",
            "jawa/faction_leader_get", "jawa/faction_ideo_get", "jawa/scenario_parts_get", "jawa/world_layers", "jawa/world_tile_get",
            "jawa/world_landmarks_get", "jawa/world_features_get", "jawa/world_mutators_get", "jawa/world_objects_get",
            "jawa/world_links_get", "jawa/incident_queue_peek", "jawa/tale_list", "jawa/social_list", "jawa/pawn_census",
            "jawa/research_availability", "jawa/lore_stage_get", "jawa/anomaly_monolith_get", "jawa/bill_list",
            "jawa/visibility_report", "jawa/cell_temperature", "jawa/thing_ambient_temp", "jawa/tile_settleable",
            "jawa/world_neighbors", "jawa/read_opinion", "jawa/read_psychic_sensitivity", "jawa/pawn_break_thresholds",
            "jawa/time_perf", "jawa/manhunter_preview", "jawa/type_probe", "jawa/type_visibility", "jawa/shadegrid_read",
            "jawa/flowworks_engine_state", "jawa/gss_playtest_status", "jawa/playtest_status", "jawa/prefab_list",
        };

        /// <summary>Tools that must NEVER run in the safe profile (the unit test fails if one is allowed). Not the
        /// enforcement list - the allow-list is - but the tripwire that catches a careless allow-list edit.</summary>
        internal static readonly string[] MustNeverBeSafe =
        {
            "jawa/static_call", "jawa/wild_spawner_block", "jawa/spawn_pawn", "jawa/spawn_batch", "jawa/spawn_fill_area",
            "jawa/fire_raid", "jawa/fire_quest", "jawa/storyteller_fire", "jawa/incident_schedule", "jawa/hot_reload_defs",
            "jawa/autosave_now", "jawa/prefs", "jawa/set_game_speed", "jawa/time_set_ticks", "jawa/kill_hostiles",
            "jawa/destroy_batch", "jawa/destroy_bulk", "jawa/explosion_at", "jawa/set_terrain", "jawa/world_tile_set",
            "jawa/pawn_health", "jawa/research_finish_project", "jawa/storyteller_swap", "jawa/debug_actions",
            "jawa/weather_roll_next", "jawa/map_zones", "jawa/bridge_arg_report", "jawa/damage_log", "jawa/raid_preview",
            "jawa/forecast_incidents", "jawa/log_autoopen_suppress", "jawa/take_screenshot", "jawa/clear_area", "jawa/wipe_cell",
            "jawa/lord_assault_spawn", "jawa/map_drop", "jawa/order_pawn", "jawa/set_draft", "jawa/trade_execute",
            "jawa/gravship_launch", "jawa/tps_test_attribution",
        };

        private static readonly HashSet<string> AllowSet = new HashSet<string>(SafeAllowList, StringComparer.Ordinal);

        internal static bool Allowed(string tool, string effectiveProfile)
        {
            if (tool == HandshakeTool) return true;
            if (effectiveProfile == Gm) return true;
            return tool != null && AllowSet.Contains(tool);
        }

        private static readonly HashSet<string> MutatingWords = new HashSet<string>(StringComparer.Ordinal)
        {
            "set", "spawn", "destroy", "fire", "kill", "add", "remove", "create", "place", "paint", "drop", "grant", "force",
            "start", "launch", "land", "clear", "wipe", "import", "commit", "reset", "apply", "finish", "edit", "swap", "send",
            "damage", "explosion", "dig", "configure", "assign", "train", "marry", "resurrect", "restore", "transfer", "move",
            "poke", "suppress", "block", "stage", "capture", "execute", "run", "build", "fill", "collapse", "minify", "refuel",
            "split", "recount", "bust", "rebuild", "fix", "make", "order", "select", "attack", "found", "roll", "zones", "call",
        };

        /// <summary>A name-level tripwire for the test: a safe tool whose NAME carries a mutating verb is suspect.</summary>
        internal static bool NameLooksMutating(string tool)
        {
            if (tool == null) return true;
            var words = tool.Replace("jawa/", "").Split('_', '/');
            if (words.Length > 1 && words[words.Length - 1] == "get") return false;   // lore_stage_get: a noun phrase read back
            foreach (var w in words) if (MutatingWords.Contains(w)) return true;
            return false;
        }

        internal static string RefusalText(string tool, string why)
        {
            return "REFUSED by the companion's SAFE profile: " + tool + " is not on the reviewed read-only list (" + why + "). " +
                   "GM tools run only when <SaveData>/JawaBench/" + ProfileFileName + " says {\"profile\": \"gm\"}, is unexpired, " +
                   "and the loaded save is not one of its campaignSaves. Call jawa/companion_handshake to see the profile.";
        }

        // ------------------------------------------------------------------ the profile file
        internal sealed class ProfileFile
        {
            internal bool Present;
            internal string Profile, Error;
            internal string[] CampaignSaves = new string[0];
            internal DateTime? ExpiresUtc;

            /// <summary>{"profile": "gm"|"safe", "expiresUtc": "ISO-8601", "campaignSaves": "a, b"} (flat JSON). Null or
            /// empty = no file. Anything unreadable is an Error, and an Error is SAFE.</summary>
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

        /// <summary>The effective profile, with the reason. Anything short of a clean, unexpired gm file is SAFE.</summary>
        internal static string Effective(ProfileFile f, DateTime nowUtc, string loadedSave, out string why)
        {
            if (f == null || !f.Present) { why = "no profile file: safe by default"; return Safe; }
            if (f.Error != null) { why = f.Error + ": safe"; return Safe; }
            if (f.Profile == Safe) { why = "profile file says safe"; return Safe; }
            if (f.Profile != Gm) { why = "unknown profile '" + f.Profile + "': safe"; return Safe; }
            if (f.ExpiresUtc.HasValue && nowUtc >= f.ExpiresUtc.Value)
            {
                why = "gm profile expired at " + f.ExpiresUtc.Value.ToString("o", CultureInfo.InvariantCulture) + ": safe";
                return Safe;
            }
            if (loadedSave != null && f.CampaignSaves.Any(c => string.Equals(c, loadedSave.Trim(), StringComparison.OrdinalIgnoreCase)))
            {
                why = "loaded save '" + loadedSave + "' is a listed campaign save: safe";
                return Safe;
            }
            why = "profile file says gm" + (f.ExpiresUtc.HasValue ? " until " + f.ExpiresUtc.Value.ToString("o", CultureInfo.InvariantCulture) : "");
            return Gm;
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
        internal const string HandshakeSchema = "companion_handshake/1";

        /// <summary>The top-level keys, in order. Changing this list is a schema change: bump HandshakeSchema and update
        /// design/RimMandrake/companion_handshake.md in the same commit.</summary>
        internal static readonly string[] HandshakeKeys =
        {
            "schema", "success", "utc", "companionAssembly", "companionVersion", "companionSha", "companionMvid",
            "companionFileSha256", "companionPath", "compileProfile", "runtimeProfile", "effectiveProfile", "profileWhy",
            "profileFile", "gate", "hooks", "rimBridgeServer", "harmony", "game", "reservedArgs",
        };

        internal sealed class HandshakeInput
        {
            internal string Utc, CompanionAssembly, CompanionVersion, CompanionSha, CompanionMvid, CompanionFileSha256, CompanionPath;
            internal string CompileProfile, RuntimeProfile, EffectiveProfile, ProfileWhy, ProfileFile;
            internal object Gate, Hooks, RimBridgeServer, Harmony, Game;
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
                ["effectiveProfile"] = i.EffectiveProfile == Gm ? Gm : Safe,   // anything unresolved reads SAFE
                ["profileWhy"] = i.ProfileWhy,
                ["profileFile"] = i.ProfileFile,
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
