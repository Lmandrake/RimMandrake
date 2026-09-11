using System;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.LoreStages
{
    // The production DefResolver: turn ("BiomeDef", "RUT_Scarlands") into the
    // live Def, by the same two engine calls the XML loader itself uses.
    //
    // Split out of LoreStageApplier so the offline selftest can compile the
    // applier without dragging GenTypes/DefDatabase — both of which need a real
    // loaded mod set — into a process that has neither.
    public static class LoreStageDefDatabase
    {
        private static readonly Dictionary<string, Type> TypeCache = new Dictionary<string, Type>();

        public static Def Resolve(string defTypeName, string defName)
        {
            if (defTypeName.NullOrEmpty() || defName.NullOrEmpty()) return null;

            if (!TypeCache.TryGetValue(defTypeName, out Type type))
            {
                // Same lookup DirectXmlLoader uses for a def's root tag, so a
                // table may name a modded Def subclass either bare or
                // namespace-qualified.
                type = GenTypes.GetTypeInAnyAssembly(defTypeName, "Verse")
                       ?? GenTypes.GetTypeInAnyAssembly(defTypeName, "RimWorld")
                       ?? GenTypes.GetTypeInAnyAssembly(defTypeName);
                TypeCache[defTypeName] = type;
            }

            if (type == null || !typeof(Def).IsAssignableFrom(type)) return null;

            // SilentFail, not GetDef: a ladder naming a def from an absent mod
            // must be a skipped row, not a red startup error.
            return GenDefDatabase.GetDefSilentFail(type, defName, specialCaseForSoundDefs: false);
        }
    }
}
