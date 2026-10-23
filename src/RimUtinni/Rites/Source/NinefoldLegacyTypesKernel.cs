using System;

namespace RimMandrake.Utinni.Rites
{
    /// <summary>
    /// The save type alias for the Ninefold fold (owner, 2026-10-22: "the Nine Gods belong in Salvation Rites").
    /// Until then the engine was its own mod, mandrake.rm.ninefold, in namespace RimMandrake.Ninefold, and saves
    /// name its scribed classes by that full name: all 18 CANONICAL_ASHKARR_START_*.rws saves carry
    /// <c>&lt;li Class="RimMandrake.Ninefold.GameComponent_Ninefold"&gt;</c> (the nine gods' favour), and 6 carry
    /// <c>RimMandrake.Ninefold.MapComponent_NinefoldOfferings</c> (measured 2026-10-22). No save may be edited, so
    /// the old name is mapped to the new one at load time (NinefoldLegacyTypes.cs hands this to the game's
    /// BackCompatibility chain). Class names did not change in the fold, only the namespace, so the map is a plain
    /// namespace swap. No Verse type here: the offline selftest (Source/SelfTest) compiles this file and checks the
    /// map against the class names actually found in the canonical saves.
    /// </summary>
    public static class NinefoldLegacyTypesKernel
    {
        public const string OldNamespace = "RimMandrake.Ninefold";
        public const string NewNamespace = "RimMandrake.Utinni.Rites";

        /// <summary>
        /// The full type name under the new namespace for a type name saved under the retired one, or null when the
        /// name is not a retired Ninefold name (the game then resolves it as usual).
        /// </summary>
        public static string MapTypeName(string savedName)
        {
            if (string.IsNullOrEmpty(savedName)) return null;
            string prefix = OldNamespace + ".";
            if (!savedName.StartsWith(prefix, StringComparison.Ordinal)) return null;
            string rest = savedName.Substring(prefix.Length);
            if (rest.Length == 0) return null;
            return NewNamespace + "." + rest;
        }
    }
}
