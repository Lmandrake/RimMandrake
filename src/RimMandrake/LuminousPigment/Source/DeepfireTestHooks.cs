// DeepfireTestHooks.cs - LuminousPigment's reset and digest hooks for the bridge's scene repeats (RMTestHooks.cs, the shared file;
// found by JawaBench's jawa/mod_hooks through reflection). Item RIMMANDRAKE_GIVE_ONE_MOD_A_DIGEST_HOOK_SO_A_DIRTY_RESET_CAN_SHOW.
// The state is GameComponent_Deepfire's per-game counters: the first-coat god events per def key and the impress cap per faction.
// The dirtying act a scene can do: jawa/static_call RimMandrake.LuminousPigment.GameComponent_Deepfire NoteGodCoatEvent <key>,
// the call DeepfireGodDeltas makes at each first coat.
using RimMandrake.Shared.TestHooks;

namespace RimMandrake.LuminousPigment
{
    public static class DeepfireTestHooks
    {
        /// <summary>Clears both counters of the current game; answers how many entries each held.</summary>
        [RMReset]
        public static string Reset(string scope) { return GameComponent_Deepfire.ClearSceneCounters(); }

        /// <summary>The counters that Reset clears, rendered by RM_DeepfireSceneDigest.Render.</summary>
        [RMDigest]
        public static string Digest(string scope) { return GameComponent_Deepfire.SceneDigest(); }
    }
}
