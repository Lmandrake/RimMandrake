using System;
using System.Collections.Generic;
using System.Reflection;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_SHIP_READINESS_1 — the Baroque Biomes "Pyrelands" roster toggle gates this mod's MECHANICS, not only
    /// worldgen (design/RimMandrake/biome_mod_unification_spec.md §5, arm 2).
    ///
    /// Found by reflection, never by an assembly reference: Pyrelands still ships standalone (mandrake.rm.pyrelands) where
    /// RimMandrake.Biomes.dll is absent, and a hard reference would fail to load there. Shell absent = the toggle does not
    /// exist = on. Resolved once at startup; the call itself is one cached delegate and one dictionary lookup.
    /// Also announces itself in the shell's RM_BiomesSettings.mechanicsGated set, so the shell's tooltip tells the player
    /// that this entry's switch stops behaviour on existing maps too.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class PyrelandsMechanicsGate
    {
        public const string RosterKey = "Pyrelands";
        public const string ShellType = "RimMandrake.Biomes.RM_BiomesSettings";

        private static readonly Func<string, bool> shellEnabled;

        public static bool ShellPresent => shellEnabled != null;

        /// <summary>What every Pyrelands mechanic reads: RM_PyrelandsSettings.pyrelandsEnabled ("Mod enabled") AND, when the
        /// shell is loaded, its "Pyrelands" toggle. Never Scribed; each switch keeps its own saved state.</summary>
        public static bool On => RM_FireEcoKernel.MechanicsOn(RM_PyrelandsSettings.pyrelandsEnabled, ShellPresent, ShellOn);

        /// <summary>The shell's toggle for "Pyrelands"; true when the shell is not loaded.</summary>
        public static bool ShellOn => shellEnabled == null || shellEnabled(RosterKey);

        static PyrelandsMechanicsGate()
        {
            Type t = GenTypes.GetTypeInAnyAssembly(ShellType);
            if (t == null) return;
            MethodInfo m = t.GetMethod("Enabled", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(string) }, null);
            if (m == null || m.ReturnType != typeof(bool))
            {
                Log.Warning("[Pyrelands] " + ShellType + " is loaded but has no static bool Enabled(string): the Baroque Biomes "
                            + "toggle cannot gate Pyrelands mechanics; only this mod's own \"Mod enabled\" switch does.");
                return;
            }
            shellEnabled = (Func<string, bool>)Delegate.CreateDelegate(typeof(Func<string, bool>), m);
            if (t.GetField("mechanicsGated", BindingFlags.Public | BindingFlags.Static)?.GetValue(null) is HashSet<string> gated)
                gated.Add(RosterKey);
            Log.Message("[Pyrelands] Baroque Biomes toggle \"" + RosterKey + "\" gates Pyrelands mechanics (now "
                        + (ShellOn ? "on" : "OFF") + ").");
        }
    }
}
