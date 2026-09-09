using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Harmony bootstrap plus the def-time auto-attach pass for card #2:
    /// "tiers auto-attach by bodySize, with a curated developer override".
    ///
    /// WHY A DEF-LOAD-TIME COMP INJECTION AND NOT A RUNTIME ONE. Adding a
    /// ThingComp to an already-spawned pawn's live comps list has no safe
    /// public API: ThingWithComps.AllComps returns a shared static empty list
    /// when a Thing has no comps yet (Verse/ThingWithComps.cs), so appending
    /// to what AllComps hands back would corrupt that shared list for every
    /// comp-less Thing in the game. Instead this appends a
    /// CompProperties_TitanicWake to the ThingDef's own `comps` list (a plain
    /// public field, Verse/ThingDef.cs) once, here, before any pawn of that
    /// race is ever made - after that, vanilla's completely ordinary
    /// PostMake/InitializeComps flow attaches it exactly as if the mod's XML
    /// had declared it directly.
    ///
    /// Runs as this type's own [StaticConstructorOnStartup] cctor, which - per
    /// RimWorld's startup order - fires after every Def is loaded and
    /// ResolveReferences/ConfigErrors has run, so GetModExtension and
    /// race.baseBodySize are both fully resolved by the time
    /// TitanicTierUtility.DefQualifies reads them.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RM_TitanicCreaturesMod
    {
        public const string HarmonyId = "mandrake.rm.titaniccreatures";

        static RM_TitanicCreaturesMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            harmony.PatchAll(Assembly.GetExecutingAssembly());

            int qualifyingRaces = InjectWakeComps();

            int patches = harmony.GetPatchedMethods().Count();
            Log.Message("[RimMandrake.TitanicCreatures] ready: " + patches + " patches, " +
                        qualifyingRaces + " races auto-tiered.");
        }

        private static int InjectWakeComps()
        {
            int count = 0;
            foreach (ThingDef td in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (!TitanicTierUtility.DefQualifies(td))
                {
                    continue;
                }
                count++;
                if (td.comps.Any(c => c.compClass == typeof(CompTitanicWake)))
                {
                    continue; // already declared explicitly in XML - don't double-attach
                }
                td.comps.Add(new CompProperties_TitanicWake());
            }
            return count;
        }
    }
}
