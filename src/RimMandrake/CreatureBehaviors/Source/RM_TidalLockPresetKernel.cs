namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING: the decision half of RM_TidalLockPresetGuard, Verse-free so the
    // offline selftest (Source/SelfTest, run by src/RimMandrake/Utils/selftest_tidal_lock_guard.py) compiles this
    // very file and sweeps every input.
    //
    // A save made without Worldbuilder (PAINT) records the tidal lock only in Alien Worlds'
    // <alienWorldsFrameworkPlanetType>. With Worldbuilder loaded (the full list) Alien Worlds ignores that field and
    // asks Worldbuilder for the save's <worldPresetName>; none ⇒ "Default" ⇒ the sun moves and the next save writes
    // Default (design/RimMandrake/world_physics_audit_2026-10-20.md §1). Restore the preset name only in exactly
    // that case: guard on, Worldbuilder backend, no preset name, the save's own planet type TidallyLocked.
    // A save that already names a preset, any other planet type (a quicktest world reads null or Default),
    // and the standalone backend (which already honours the saved type) are left alone.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_TidalLockPresetKernel
    {
        public const string LockedType = "TidallyLocked";

        /// <returns>the preset name to set, or null to leave the load alone.</returns>
        public static string PresetToRestore(bool guardOn, bool worldbuilderBackend, string presetName, string savedPlanetType)
        {
            if (!guardOn || !worldbuilderBackend) return null;
            if (!string.IsNullOrEmpty(presetName)) return null;
            return savedPlanetType == LockedType ? LockedType : null;
        }
    }
}
