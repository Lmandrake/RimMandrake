using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_APPAREL_ISFLESH_GATE_1.
    ///
    /// `PawnApparelGenerator.GenerateStartingApparelFor` (RimWorld/PawnApparelGenerator.cs:686)
    /// opens with
    ///
    ///     if (!pawn.RaceProps.ToolUser || !pawn.RaceProps.IsFlesh || pawn.RaceProps.IsAnomalyEntity)
    ///         return;
    ///
    /// and `RaceProperties.IsFlesh => FleshType.isOrganic` (Verse/RaceProperties.cs:340).
    /// Every Droidworks race inherits `RSW_DW_Race_Base`'s
    /// `<fleshType>RSW_DW_FleshType_Droid</fleshType>` with `<isOrganic>false</isOrganic>`
    /// (Defs/Races_Base.xml, a deliberate ruling from droid_system_build_spec.md §1 and
    /// NOT reversed here), so that early return fires for every droid pawn before
    /// `apparelMoney` or `apparelTags` are ever read - measured live as 15/15 spawns
    /// coming back `apparel: []` across four kinds carrying real tags and adequate
    /// budgets.
    ///
    /// This transpiler rewrites exactly one instruction in that one method: the
    /// `callvirt RaceProperties::get_IsFlesh()` inside the guard becomes a call to
    /// <see cref="CountsAsFleshForApparel"/>, which is `IsFlesh` widened by "or the
    /// Droidworks droid fleshtype". The `ToolUser` and `IsAnomalyEntity` halves of the
    /// guard are untouched, `isOrganic` itself is untouched, and no other consumer of
    /// `IsFlesh` anywhere in the game is affected - a transpiler was chosen over a
    /// prefix precisely because the method body is 140 lines of vanilla apparel-budget
    /// logic that must keep running verbatim; reimplementing it in a prefix would fork
    /// it against every future RimWorld update.
    ///
    /// Untagged, zero-budget kinds (e.g. RSW_DW_OuterRim_GNKDroid) still generate
    /// nothing: this only lets the method reach the budget logic that already decides
    /// that.
    ///
    /// VFE Core postfixes this same method (recolour only) and does not transpile it,
    /// so the two compose.
    /// </summary>
    public static class Patch_ApparelForDroids
    {
        public static void Apply(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(PawnApparelGenerator),
                nameof(PawnApparelGenerator.GenerateStartingApparelFor));
            if (target == null)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] PawnApparelGenerator.GenerateStartingApparelFor "
                    + "not found by reflection - vanilla API has moved. Droid apparel gate NOT lifted; "
                    + "every Droidworks pawn will spawn bare.");
                return;
            }
            harmony.Patch(target,
                transpiler: new HarmonyMethod(typeof(Patch_ApparelForDroids), nameof(Transpiler)));
        }

        /// <summary>
        /// `IsFlesh`, widened to accept the Droidworks droid fleshtype. Null-safe on
        /// the DefOf so a def-load failure degrades to vanilla behaviour rather than
        /// throwing inside pawn generation.
        /// </summary>
        public static bool CountsAsFleshForApparel(RaceProperties props)
        {
            if (props == null) return false;
            if (props.IsFlesh) return true;
            var droid = DroidworksDefOf.RSW_DW_FleshType_Droid;
            return droid != null && props.FleshType == droid;
        }

        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
        {
            MethodInfo isFleshGetter = AccessTools.PropertyGetter(typeof(RaceProperties), nameof(RaceProperties.IsFlesh));
            MethodInfo replacement = AccessTools.Method(typeof(Patch_ApparelForDroids), nameof(CountsAsFleshForApparel));

            var list = new List<CodeInstruction>(instructions);
            if (isFleshGetter == null || replacement == null)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Could not resolve RaceProperties.IsFlesh or the "
                    + "replacement helper - droid apparel gate NOT lifted; every Droidworks pawn will spawn bare.");
                return list;
            }

            int hits = 0;
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i].Calls(isFleshGetter))
                {
                    list[i].opcode = OpCodes.Call;
                    list[i].operand = replacement;
                    hits++;
                }
            }

            if (hits != 1)
            {
                // Vanilla calls IsFlesh exactly once in this method, in the guard on its
                // first line. Any other count means the method changed shape and this
                // patch is no longer reasoning about what it thinks it is.
                Log.Error("[RimMandrake.StarWars.Droidworks] Expected exactly 1 RaceProperties.IsFlesh call in "
                    + "PawnApparelGenerator.GenerateStartingApparelFor, found " + hits
                    + ". Droidworks apparel generation may be wrong.");
            }

            return list;
        }
    }
}
