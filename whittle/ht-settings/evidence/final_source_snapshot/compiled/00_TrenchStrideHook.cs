using System;
using RimMandrake.HugeThings;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_TRENCHES_WIRE_MIND_THE_GAP (owner, by card 2026-10-18, BIG_CREATURES_DESIGN_WALLS_AND_SLOTS §8 Q3): titans STEP OVER a
    /// trench narrower than a quarter of their breadth (WallsSlots.StepsOverTrench); a wider one holds them as today.
    ///
    /// Trenches are FlowWorks' (its pocket grid, cliff masks, step floor and fall detector). Neither mod references the other: each
    /// loads alone. The registration point is one AppDomain slot under <see cref="Key"/> holding a BCL delegate,
    /// <c>Func&lt;Pawn, int&gt;</c>: the widest trench (cells across) this pawn steps over, 0 for none. No shared type, no
    /// reflection: FlowWorks reads the slot lazily (RM_TrenchStride.StrideOf) and, with HugeThings absent, finds it empty and
    /// every trench is judged as before. The key string is the whole contract; FlowWorks' copy is checked by both selftests.
    ///
    /// Only creatures carrying CompTitanicWake are judged (as every walls-and-slots rule), and only while the rule is on
    /// (RM_HugeThingsSettings.TrenchStepActive: giant animals, wake, clearing, walls-and-slots and its own toggle).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class TrenchStrideHook
    {
        /// <summary>The registration slot. FlowWorks: RM_TrenchStride.HookKey. Never rename one without the other.</summary>
        public const string Key = "RimMandrake.TrenchStride.v1";

        static TrenchStrideHook()
        {
            AppDomain.CurrentDomain.SetData(Key, (Func<Pawn, int>)Stride);
        }

        /// <summary>The widest trench this pawn steps over (0: none, or the rule is off, or it is not a titan).</summary>
        public static int Stride(Pawn p)
        {
            if (p == null || !RM_HugeThingsSettings.TrenchStepActive || p.TryGetComp<CompTitanicWake>() == null)
            {
                return 0;
            }
            return WallsSlots.WidestTrenchSteppedOver(WallsSlotsUtility.Breadth(p));
        }
    }
}
