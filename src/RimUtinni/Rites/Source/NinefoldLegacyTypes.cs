using System;
using System.Collections.Generic;
using System.Xml;
using HarmonyLib;
using Verse;

namespace RimMandrake.Utinni.Rites
{
    // ════════════════════════════════════════════════════════════════════
    // The save type alias for the Ninefold fold (see NinefoldLegacyTypesKernel.cs for why and what is mapped).
    //
    // Mechanism (decompiled 1.6, read 2026-10-22): ScribeExtractor.SaveableFromNode resolves a node's Class
    // attribute through BackCompatibility.GetBackCompatibleType, which asks every BackCompatibilityConverter in
    // the private static BackCompatibility.conversionChain before GenTypes. Without this converter the old name
    // resolves to nothing, the loader falls back to the abstract GameComponent and throws, and
    // Game.FillComponents then makes a FRESH GameComponent_Ninefold: every god's favour silently reset to zero.
    //
    // The chain is skipped only when the save's mod list and build equal the running game's
    // (CheckSaveIdenticalToCurrentEnvironment). A save naming RimMandrake.Ninefold.* was written with
    // mandrake.rm.ninefold loaded, which no longer exists, so its mod list always differs and the chain runs.
    // ════════════════════════════════════════════════════════════════════
    public class NinefoldLegacyTypeConverter : BackCompatibilityConverter
    {
        // Every save version: the alias is about the mod's history, not the game's.
        public override bool AppliesToVersion(int majorVer, int minorVer) => true;

        // No def was ever saved under an RM_ name this fold renames (RM_Tilt_ defs are never scribed).
        public override string BackCompatibleDefName(Type defType, string defName, bool forDefInjections = false, XmlNode node = null) => null;

        public override Type GetBackCompatibleType(Type baseType, string providedClassName, XmlNode node)
        {
            string mapped = NinefoldLegacyTypesKernel.MapTypeName(providedClassName);
            return mapped == null ? null : GenTypes.GetTypeInAnyAssembly(mapped);
        }

        public override void PostExposeData(object obj) { }

        private static bool registered;

        /// <summary>Puts the converter at the front of the game's chain. Called once from the Mod constructor,
        /// before any def or save loads. Loud on failure: a silent miss would reset every god's favour.</summary>
        public static void Register()
        {
            if (registered) return;
            List<BackCompatibilityConverter> chain = null;
            try
            {
                chain = AccessTools.Field(typeof(BackCompatibility), "conversionChain")?.GetValue(null)
                    as List<BackCompatibilityConverter>;
            }
            catch (Exception ex)
            {
                Log.Error("[Ninefold] could not read BackCompatibility.conversionChain: " + ex);
            }
            if (chain == null)
            {
                Log.Error("[Ninefold] BackCompatibility.conversionChain not found: saves written before the fold into "
                    + "Salvation Rites (class RimMandrake.Ninefold.*) will lose the nine gods' favour on load.");
                return;
            }
            chain.Insert(0, new NinefoldLegacyTypeConverter());
            registered = true;
        }
    }
}
