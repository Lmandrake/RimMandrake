// JawaBenchRunLockCore.cs - the run lock of BRIDGE v2.0 (no Verse, no Unity, no Harmony). Page:
// design/specs/2026-11-23-bridge-v2-life-cycle/boundary.md. Item RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK.
// While a scene run is live, the gate on every jawa tool (JawaBenchCompanionSafety) asks Refuse: a tool that can change the game
// is refused by the run's id, a tool that only reads is let through and counted. A tool that nobody reviewed as a read is a change.
//
// Compiled into bridgetools/SceneTickSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
using System;
using System.Collections.Generic;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchRunLockCore
    {
        /// <summary>What the lock did during one run. Called from the bridge's threads, read from the main thread.</summary>
        internal sealed class LockLog
        {
            private readonly object _gate = new object();
            private readonly SortedDictionary<string, int> _refused = new SortedDictionary<string, int>(StringComparer.Ordinal);
            private long _reads;

            internal void Refused(string tool) { lock (_gate) { int n; _refused.TryGetValue(tool, out n); _refused[tool] = n + 1; } }
            internal void Read() { lock (_gate) _reads++; }
            internal long Reads { get { lock (_gate) return _reads; } }

            /// <summary>tool -> how many calls of it were refused.</summary>
            internal Dictionary<string, object> Breaches()
            {
                var d = new Dictionary<string, object>();
                lock (_gate) foreach (var kv in _refused) d[kv.Key] = (double)kv.Value;
                return d;
            }
        }

        /// <summary>The hands that hold their own driver check: they answer status and cancel, and refuse a second start themselves.</summary>
        internal static readonly HashSet<string> OwnCheck = new HashSet<string>(StringComparer.Ordinal)
        { "jawa/session", "jawa/run_until", "jawa/act_batch", "jawa/companion_handshake" };

        /// <summary>The actions of a tool that end or read a run, or only read. Any other action of the tool is a change.</summary>
        internal static readonly Dictionary<string, string[]> ReadActions = new Dictionary<string, string[]>(StringComparer.Ordinal)
        {
            { "jawa/scene_slice", new[] { "status", "cancel" } }, { "jawa/safe_advance", new[] { "status", "cancel" } },
            { "jawa/first_exception", new[] { "read" } }, { "jawa/health", new[] { "status" } }, { "jawa/vitals", new[] { "status" } },
            { "jawa/quiet_site", new[] { "status" } }, { "jawa/damage_log", new[] { "read" } },
            // list, admit and digest read; prove reads the digest (the dirtying is the caller's act); reset changes the mod's state
            { "jawa/mod_hooks", new[] { "list", "admit", "digest", "prove" } },
            // state reads the gates' summary; arm and release change what the game lets through
            { "jawa/scene_gate", new[] { "state" } },
            // its "action" is type.method: the process text that the scene library reads to know whose session is open
            { "jawa/static_call", new[] { "system.environment.getenvironmentvariable" } },
        };

        /// <summary>Reviewed one by one 2026-11-24: the body changes nothing in the game. Beside them, a tool whose description begins
        /// READ ONLY. jawa/static_call is never a read by its description: what it calls is the caller's.</summary>
        internal static readonly HashSet<string> Reads = new HashSet<string>(StringComparer.Ordinal)
        {
            "jawa/read_paths", "jawa/cond_eval", "jawa/comp_read", "jawa/map_comp_read", "jawa/thing_read", "jawa/pawn_get", "jawa/pawn_stats",
            "jawa/thing_stats", "jawa/pawn_census", "jawa/pawn_roles", "jawa/list_pawns", "jawa/list_things", "jawa/list_things_batch",
            "jawa/get_pawns_batch", "jawa/get_power_nets_batch", "jawa/get_terrain_batch", "jawa/get_terrain_layers", "jawa/get_roof_batch",
            "jawa/get_def", "jawa/get_defs", "jawa/weather_get", "jawa/running_mods", "jawa/room_get", "jawa/cell_temperature", "jawa/inspect_string",
            "jawa/incident_journal", "jawa/incident_queue_peek", "jawa/thing_lineage", "jawa/drawn_positions", "jawa/alerts_list",
            "jawa/letter_list", "jawa/list_factions", "jawa/tps_report", "jawa/telemetry_mark", "jawa/drain_log", "jawa/heat_events",
        };

        internal const string NeverARead = "jawa/static_call";

        internal static bool DeclaredRead(string description)
        {
            string d = description ?? "";
            if (!d.StartsWith("READ ONLY", StringComparison.OrdinalIgnoreCase) && !d.StartsWith("READ-ONLY", StringComparison.OrdinalIgnoreCase)) return false;
            return d.Length == 9 || !char.IsLetterOrDigit(d[9]);
        }

        /// <summary>The call cannot change the game, or it is a hand with its own driver check.</summary>
        internal static bool Passes(string tool, bool declaredRead, string action)
        {
            if (tool == null) return false;
            if (OwnCheck.Contains(tool) || Reads.Contains(tool)) return true;
            string[] acts;
            if (ReadActions.TryGetValue(tool, out acts)) return Array.IndexOf(acts, (action ?? "").Trim().ToLowerInvariant()) >= 0;
            return declaredRead && tool != NeverARead;
        }

        /// <summary>Null when the call may run, else the refusal. `runId` is the live run, or null; `inside` is true for an act that the
        /// run itself does.</summary>
        internal static string Refuse(string tool, bool declaredRead, string action, string runId, bool inside, LockLog log)
        {
            if (runId == null || inside) return null;
            if (Passes(tool, declaredRead, action))
            {
                if (log != null && (!OwnCheck.Contains(tool))) log.Read();
                return null;
            }
            if (log != null) log.Refused(tool ?? "(unmapped)");
            return "REFUSED: RUN_ACTIVE. Run " + runId + " is live, and " + (tool ?? "this tool") + " is not reviewed as a read" +
                   (string.IsNullOrEmpty(action) ? "" : " (action " + action + ")") + ". Nothing was changed. Wait for the run to close " +
                   "(jawa/run_until, jawa/scene_slice or jawa/safe_advance action=status), or cancel it, or send the act as an act of the run.";
        }

        /// <summary>Null when a run may be armed, else the run or the step loop that holds the tick. One run at a time.</summary>
        internal static string RefuseArm(string liveId, string liveStage, bool advanceRunning, string stepOwner, string caller)
        {
            if (liveId != null && liveStage != "closed") return "run " + liveId + " is live (" + liveStage + ")";
            if (advanceRunning) return "jawa/safe_advance is running";
            if (stepOwner != null && stepOwner != caller) return stepOwner + " is running";
            return null;
        }
    }
}
