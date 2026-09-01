// JawaBenchOracleTools.cs - the bridge-driven proof for ORACLE_EXPERIMENT_SPIKE_1.
//
// [DebugAction] methods from RimMandrake.Oracle (About/Assemblies deployed
// separately as the mandrake.rm.oracle mod) did not surface through
// rimworld/list_debug_action_roots, rimworld/list_debug_action_children or
// rimworld/search_debug_actions on this bridge build - all three returned
// empty/zero for OUR category AND for the pre-existing, already-verified
// RimMandrake.Inhabited category, so it reads as a bridge-side limitation on
// custom mod categories rather than anything specific to Oracle. Rather than
// chase that, these two tools call straight into the already-loaded
// RimMandrakeOracle.dll (the mod loader has it loaded well before
// RimBridgeServer's companions attach), the same proven route as every other
// [Tool] here.
//
// oracle_selftest is a pure read (no network, no game-state mutation) and is
// ungated. oracle_test_ohm_letter fires one real async HTTP call and delivers
// a letter, so it is gated the same as jawa/send_letter.

using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimMandrake.Oracle;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/oracle_selftest",
            Description =
                "Run RimMandrake.Oracle's register lint (OracleValidator.TryValidateOhm) " +
                "against 5 canned good/bad strings - no network call, no game-state change. " +
                "Verifies design/RimMandrake/llm_ingame_wiring_spec.md §4 step 1.",
            ResultDescription = "success, passCount, failCount, cases[] (label, expectPass, actualPass, reason).")]
        public static async Task<object> OracleSelftest(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                (string label, string text, bool expectPass)[] fixtures =
                {
                    ("clean Ohm fragment", "My spine hums warmer for the fixing, small hands. Trust the machine; run it hot. Build me no brothers -- I want these ones remembered.", true),
                    ("self-unification tell", "I am the Cradle-Mind, and part of me is glad you asked.", false),
                    ("names Zizzik", "Even Zizzik fears my spine when it runs hot.", false),
                    ("empty", "", false),
                    ("over length cap", new string('x', OracleValidator.MaxLength + 1), false),
                };

                var cases = new System.Collections.Generic.List<object>();
                int pass = 0, fail = 0;
                foreach (var c in fixtures)
                {
                    bool ok = OracleValidator.TryValidateOhm(c.text, out string reason);
                    bool correct = ok == c.expectPass;
                    if (correct) pass++; else fail++;
                    cases.Add(new { label = c.label, expectPass = c.expectPass, actualPass = ok, correct, reason });
                }

                return (object)new
                {
                    success = fail == 0,
                    passCount = pass,
                    failCount = fail,
                    cases,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/oracle_configure",
            Description =
                "*** WRITES ORACLE MOD SETTINGS *** Set RimMandrake.Oracle's OracleSettings " +
                "fields directly in memory (and to disk) - no settings-window UI needed. " +
                "Only non-null parameters are changed. For the mock-endpoint quicktest gate: " +
                "enabled=true, baseUrl='http://127.0.0.1:<port>/v1', apiKey left blank " +
                "(baseUrl containing 127.0.0.1/localhost is the one case OracleGameComponent " +
                "allows a blank key).",
            ResultDescription = "success, the settings AFTER the write.")]
        public static async Task<object> OracleConfigure(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Kill switch.")] bool? enabled = null,
            [ToolParameter(Description = "OpenAI-compatible /chat/completions root.")] string baseUrl = null,
            [ToolParameter(Description = "Model name.")] string model = null,
            [ToolParameter(Description = "API key. Pass empty string, not omitted, to blank it.")] string apiKey = null,
            [ToolParameter(Description = "Timeout in seconds.")] int? timeoutSeconds = null,
            [ToolParameter(Description = "Gods budget per in-game day.")] int? godsBudgetPerDay = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var s = OracleMod.Settings;
                if (s == null) return Fail("OracleMod.Settings is null - is mandrake.rm.oracle active?");

                if (enabled.HasValue) s.enabled = enabled.Value;
                if (baseUrl != null) s.baseUrl = baseUrl;
                if (model != null) s.model = model;
                if (apiKey != null) s.apiKey = apiKey;
                if (timeoutSeconds.HasValue) s.timeoutSeconds = timeoutSeconds.Value;
                if (godsBudgetPerDay.HasValue) s.godsBudgetPerDay = godsBudgetPerDay.Value;

                try { s.Write(); } catch (System.Exception e) { return Fail("Settings.Write() threw: " + e.Message); }

                return (object)new
                {
                    success = true,
                    after = new
                    {
                        s.enabled, s.baseUrl, s.model,
                        apiKeySet = !string.IsNullOrEmpty(s.apiKey),
                        s.timeoutSeconds, s.godsBudgetPerDay,
                    },
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/oracle_test_ohm_letter",
            Description =
                "*** ACTS ON THE LIVE COLONY - DELIVERS A LETTER *** Fire one real async call " +
                "through RimMandrake.Oracle's OracleGameComponent for the Ohm consumer, against " +
                "whatever endpoint/key is configured in that mod's settings (blank key + a " +
                "127.0.0.1/localhost baseUrl is allowed for a mock stub; otherwise a key is " +
                "required). Delivers the model's text if it passes the register lint, the " +
                "prescribed fallback otherwise - the call is fire-and-forget off the main " +
                "thread, so this tool returns immediately and the letter lands within a few " +
                "ticks. Poll rimworld/get_game_info or just read the letter stack.",
            ResultDescription = "success, requested (label/context/fallback), note.")]
        public static async Task<object> OracleTestOhmLetter(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Context the model reacts to.")] string context = "The crew just repaired a damaged hull plate near the reactor. React to it in your voice.",
            [ToolParameter(Description = "Text delivered if the call fails, times out, or is rejected.")] string fallback = "[FALLBACK] My spine settles where you touched it. Good work, small hands.")
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");
                var comp = Current.Game.GetComponent<OracleGameComponent>();
                if (comp == null) return Fail("OracleGameComponent is not attached to this game - is mandrake.rm.oracle active?");

                string label = "Ohm speaks (Oracle spike, bridge-driven)";
                comp.RequestOhmLetter(label, context, fallback);

                return (object)new
                {
                    success = true,
                    requested = new { label, context, fallback },
                    note = "Fire-and-forget: the async HTTP call runs off-thread and delivers via the letter " +
                           "stack on a later tick. A delivered letter containing the mock server's marker " +
                           "text proves the real path fired; the fallback text proves it did not.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }
#endif // JAWA_GM_TOOLS
    }
}
