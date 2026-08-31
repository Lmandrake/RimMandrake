using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// The beggars at the player's gate are the people whose livelihood he burned
    /// down last month.
    ///
    /// This is the second of the displaced pool's three consumers and by far the
    /// cheapest: the beggars quest ships, it already walks strangers up to the
    /// colony and asks for food, and RimWorld's own name, backstory and memory
    /// systems do the rest. All we change is WHERE the strangers come from.
    ///
    /// ⛔ AND NOTHING ELSE CHANGES. No karma, no reputation number, no "the world
    /// disapproves" popup, no letter explaining the connection. If the player
    /// recognises the name, that is the entire feature. The moment it acquires a
    /// guilt statistic it becomes a mechanic instead of a memory.
    ///
    /// THREE THINGS THE DESIGN DOC GOT WRONG, corrected against the 1.6 source:
    ///
    ///   * There is no `GiveQuest_Beggars`. The class is
    ///     `RimWorld.QuestGen.QuestNode_Root_Beggars`.
    ///   * Beggars do NOT belong to an existing faction. The quest builds a hidden
    ///     temporary one from `FactionDefOf.Beggars` before generating anybody, so
    ///     a Hutt refinery survivor cannot simply be handed over -- the pawn has to
    ///     be MOVED into that generated faction. `Pawn.SetFaction` keeps the name,
    ///     traits, backstory, relations and memories, which is the whole point.
    ///   * The quest is Ideology-gated -- `QuestNode_Root_Beggars` opens with
    ///     `ModLister.CheckIdeology("Beggars")`. With Ideology off this patch is
    ///     inert, and that is not a bug.
    ///
    /// The target is the extension method every quest pawn passes through rather
    /// than `PawnGenerator.GeneratePawn`, which is the universal entry point for
    /// pawn generation in the whole game and would be reckless to intercept. The
    /// `Beggar` kind test narrows it the rest of the way.
    /// </summary>
    [HarmonyPatch(typeof(QuestGen_Pawns), nameof(QuestGen_Pawns.GeneratePawn),
        new[] { typeof(Quest), typeof(PawnGenerationRequest), typeof(bool) })]
    public static class Patch_QuestGen_Pawns_GeneratePawn
    {
        /// <summary>
        /// COMPILE-TIME PROOF THAT THE TARGET EXISTS WITH EXACTLY THIS SIGNATURE.
        ///
        /// `[HarmonyPatch]` resolves its target at startup, so a wrong parameter
        /// list costs a cold load to discover. Binding the method group to a
        /// delegate of the same shape makes the C# compiler check it against the
        /// real Assembly-CSharp instead: if the overload ever moves, the BUILD
        /// fails and nobody spends 25 minutes finding out.
        /// </summary>
        private static readonly System.Func<Quest, PawnGenerationRequest, bool, Pawn> TargetSignatureProof =
            QuestGen_Pawns.GeneratePawn;

        [HarmonyPrefix]
        public static bool SubstituteDisplacedBeggar(PawnGenerationRequest request, ref Pawn __result)
        {
            if (request.KindDef != PawnKindDefOf.Beggar)
            {
                return true;
            }
            DisplacedPool pool = DisplacedPool.Current;
            if (pool == null || pool.Count == 0)
            {
                return true;
            }

            List<Pawn> drawn = pool.DrawAny(1);
            if (drawn.Count == 0)
            {
                return true;
            }
            Pawn pawn = drawn[0];

            // Into the quest's hidden beggar faction. Everything that makes this
            // person recognisable rides along untouched.
            if (request.Faction != null && pawn.Faction != request.Faction)
            {
                pawn.SetFaction(request.Faction);
            }

            // The same bookkeeping the original does, in the same order. Skipping
            // it would leave a pawn the quest system does not know it owns.
            QuestGen.AddToGeneratedPawns(pawn);
            if (!pawn.IsWorldPawn())
            {
                Find.WorldPawns.PassToWorld(pawn);
            }

            __result = pawn;
            return false;
        }
    }
}
