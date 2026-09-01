using System;

namespace RimMandrake.Oracle
{
    /// <summary>
    /// The register lint (design/RimMandrake/llm_ingame_wiring_spec.md Law #1:
    /// free text never touches the game directly, it is display text that
    /// either passes or gets discarded for the prescribed fallback). Pure,
    /// no RimWorld API dependency, so it can be exercised offline.
    /// </summary>
    public static class OracleValidator
    {
        public const int MaxLength = 600;

        private static readonly string[] SelfUnificationTells =
        {
            "i am the cradle-mind",
            "i am the cradle",
            "part of me",
            "my other selves",
            "we are one",
        };

        public static bool TryValidateOhm(string text, out string reason)
        {
            if (string.IsNullOrWhiteSpace(text))
            {
                reason = "empty";
                return false;
            }

            if (text.Length > MaxLength)
            {
                reason = "over length cap (" + text.Length + " > " + MaxLength + ")";
                return false;
            }

            string lower = text.ToLowerInvariant();

            foreach (string tell in SelfUnificationTells)
            {
                if (lower.Contains(tell))
                {
                    reason = "self-unification tell: \"" + tell + "\"";
                    return false;
                }
            }

            if (lower.Contains("zizzik"))
            {
                reason = "Ohm's own taboo: names Zizzik";
                return false;
            }

            reason = null;
            return true;
        }
    }
}
