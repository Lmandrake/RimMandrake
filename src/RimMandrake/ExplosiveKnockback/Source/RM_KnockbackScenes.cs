#if RM_PROOFS
// Proof build only (RM_PROOFS): the Explosive Knockback suite for jawa/run_scenes, the shared in-game scene runner
// (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE). The first ported suite: the showcase sc_storeroom_bomb_pit and its
// pit-filled control, staged and judged by the SAME RM_KnockbackProof.Stage / Verdict code knockback_runner.py drives one
// bridge call at a time, so the two routes must give identical verdict rows. NOT YET RUN LIVE.
//   python.exe src\RimMandrake\Utils\scene_runner.py --type RimMandrake.ExplosiveKnockback.RM_KnockbackScenes
using System;
using System.Collections.Generic;
using System.Reflection;
using RimMandrake.Shared.SceneRunner;

namespace RimMandrake.ExplosiveKnockback
{
    public static class RM_KnockbackScenes
    {
        private static Dictionary<FieldInfo, object> player;

        /// <summary>One scene of RM_KnockbackProof as a runner scene: Stage at (x, z), then the judge is its Verdict.
        /// Outside: the vanilla count of haulable things resting on the pit's two rows (offsets x -3..3, z -5..-4 in
        /// RM_KnockbackProof_StoreroomBombPit.cs) after the blast, read by the runner, never by this mod.</summary>
        [RMTest("storeroom_bomb_pit", Ticks = 900, Outside = "haulables -3,-5,7,2 >= 1")]
        [RMTest("storeroom_bomb_pit_control", Ticks = 900)]
        public static object Scene(string scene, int x, int z)
        {
            string staged = RM_KnockbackProof.Stage(scene + "," + x + "," + z);
            if (!staged.StartsWith("STAGED")) return staged;
            return (Func<object>)(() => RM_KnockbackProof.Verdict(scene));
        }

        /// <summary>The suite's plots: RM_KnockbackProof's own (a 15-cell pitch that skips natural pond beds).</summary>
        public static string Origins(string n) => RM_KnockbackProof.Origins(n);

        /// <summary>Remember the player's value of every setting, put every setting at its default (the scenes are judged on
        /// defaults, as knockback_runner.py's Settings reset does) and empty the journal.</summary>
        public static string SuiteBegin(string _)
        {
            player = new Dictionary<FieldInfo, object>();
            foreach (FieldInfo f in typeof(RimMandrakeExplosiveKnockbackSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (!f.IsLiteral && !f.IsInitOnly) player[f] = f.GetValue(null);
            RimMandrakeExplosiveKnockbackMod.Reset();
            RM_KnockbackJournal.Clear();
            return "settings at defaults (" + player.Count + " player values kept), journal cleared";
        }

        /// <summary>Put the player's values back (the runner calls this after the last scene, also when one threw).</summary>
        public static string SuiteEnd(string _)
        {
            if (player == null) return "nothing kept";
            foreach (KeyValuePair<FieldInfo, object> kv in player) kv.Key.SetValue(null, kv.Value);
            int n = player.Count;
            player = null;
            return "player values back on " + n + " settings";
        }
    }
}
#endif
