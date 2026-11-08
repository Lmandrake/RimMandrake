using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    // A wall memory's label and its description are formatted with different arguments: the label's {0} is the other pawn (the painter,
    // the subject, the scrubber), the description's {0} is the pawn who has the memory (Thought.Description formats with PAWN first). Live,
    // pass 10: Brick's "Mocked on the wall by Karen" said "Brick painted me up there". Our descriptions mean the other pawn by {0}, as the
    // labels do, and a memory with nobody behind it (fine work by a hand nobody knows) says "someone" rather than an unresolved symbol.
    [StaticConstructorOnStartup]
    public static class ThoughtDescriptionPatch
    {
        static ThoughtDescriptionPatch()
        {
            new Harmony("mandrake.rm.graffiti.thoughtdescription").Patch(
                AccessTools.PropertyGetter(typeof(Thought), nameof(Thought.Description)),
                postfix: new HarmonyMethod(typeof(ThoughtDescriptionPatch), nameof(Postfix)));
        }

        public static void Postfix(Thought __instance, ref string __result)
        {
            if (!(__instance is Thought_Memory m) || !GraffitiTemperament.IsOurs(m.def) || m.pawn == null) return;
            string raw = m.CurStage?.description ?? m.def.description;
            if (raw == null || !raw.Contains("{0}")) return;
            string desc = raw.Replace("{0}", m.otherPawn?.LabelShort ?? "someone").Formatted(m.pawn.Named("PAWN")).Resolve();
            string nullified = ThoughtUtility.ThoughtNullifiedMessage(m.pawn, m.def);
            if (!nullified.NullOrEmpty()) desc += "\n\n(" + nullified + ")";
            __result = desc;
        }
    }
}
