using LudeonTK;
using Verse;

namespace RimMandrake.Oracle
{
    /// <summary>
    /// The two verification hooks for ORACLE_EXPERIMENT_SPIKE_1
    /// (design/RimMandrake/llm_ingame_wiring_spec.md §4). Debug Actions Menu
    /// -> RimMandrake.Oracle.
    /// </summary>
    public static class DebugActions_Oracle
    {
        private const string Cat = "RimMandrake.Oracle";

        [DebugAction(Cat, "Selftest validator (no network call)", allowedGameStates = AllowedGameStates.Entry | AllowedGameStates.Playing)]
        private static void SelftestValidator()
        {
            (string label, string text, bool expectPass)[] cases =
            {
                ("clean Ohm fragment", "My spine hums warmer for the fixing, small hands. Trust the machine; run it hot. Build me no brothers -- I want these ones remembered.", true),
                ("self-unification tell", "I am the Cradle-Mind, and part of me is glad you asked.", false),
                ("names Zizzik", "Even Zizzik fears my spine when it runs hot.", false),
                ("empty", "", false),
                ("over length cap", new string('x', OracleValidator.MaxLength + 1), false),
            };

            int pass = 0, fail = 0;
            foreach (var c in cases)
            {
                bool ok = OracleValidator.TryValidateOhm(c.text, out string reason);
                bool correct = ok == c.expectPass;
                if (correct) pass++; else fail++;
                Log.Message(string.Format(
                    "RimMandrake.Oracle selftest [{0}] \"{1}\": validator={2} expected={3} reason={4}",
                    correct ? "PASS" : "FAIL", c.label, ok, c.expectPass, reason ?? "(none)"));
            }
            Log.Message(string.Format("RimMandrake.Oracle selftest: {0} pass, {1} fail, out of {2} cases", pass, fail, cases.Length));
        }

        [DebugAction(Cat, "Test Ohm letter (live call)", allowedGameStates = AllowedGameStates.Playing)]
        private static void TestOhmLetter()
        {
            Current.Game.GetComponent<OracleGameComponent>().RequestOhmLetter(
                "Ohm speaks (Oracle spike)",
                "The crew just repaired a damaged hull plate near the reactor. React to it in your voice.",
                "[FALLBACK] My spine settles where you touched it. Good work, small hands.");
            Log.Message("RimMandrake.Oracle: Ohm letter requested -- watch the letter stack.");
        }
    }
}
