#if RM_PROOFS
// RMTestAttribute.cs - marks a scene for jawa/run_scenes, the shared in-game scene runner
// (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE). Compiled into a mod's PROOF build only (RM_PROOFS), so a player's
// release DLL never carries it. The runner lives in the JawaBench companion and reads this attribute by its TYPE NAME,
// so each mod compiles its own internal copy and neither side references the other.
//
//     [RMTest("storeroom_bomb_pit", Ticks = 900, Outside = "haulables -3,-5,7,2 >= 1")]
//     public static object Scene(string scene, int x, int z) { ...stage at (x, z)...; return (Func<object>)(() => judge); }
//
// The method stages the scene and returns its judge (a zero-argument delegate answering a verdict line or rows), or a
// refusal string. Full contract: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneRunnerCore.cs.
using System;

namespace RimMandrake.Shared.SceneRunner
{
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = true, Inherited = false)]
    internal sealed class RMTestAttribute : Attribute
    {
        public RMTestAttribute(string name) { Name = name; }

        /// <summary>The scene's name in the row table and the runner's scenes= list.</summary>
        public string Name { get; }

        /// <summary>Ticks the runner steps between staging and judging (0 = the runner's default, 300).</summary>
        public int Ticks { get; set; }

        /// <summary>Vanilla counts the RUNNER reads after the ticks, from outside the mod: "kind dx,dz,w,h op n" joined by
        /// ';' (kind haulables | pawns | colonists; op &gt;= | &lt;= | ==; rect relative to the scene origin). A suite keeps at
        /// least one, so a judge that shares the mod's blind spot cannot pass alone.</summary>
        public string Outside { get; set; }
    }
}
#endif
