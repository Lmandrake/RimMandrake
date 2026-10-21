using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Races
{
    /// <summary>
    /// FACE_OPTOUT_REPAIR_ONLY_AT_HOME. The xenotypes Facial Animation must not draw a face on, shipped as data
    /// (Defs/Misc/RSW_FacialAnimationOptOut.xml). FA reads its skip list only from the player's own settings file, so
    /// before this def the opt-out existed on the owner's machine alone.
    /// </summary>
    public class RSW_FacialAnimationOptOutDef : Def
    {
        public List<string> xenotypes = new List<string>();
    }

    /// <summary>Which pawns FA must skip. Built once, on first use (defs are loaded by then).</summary>
    public static class RSW_FacialAnimationOptOut
    {
        private static HashSet<string> defNames;
        private static HashSet<string> labels;

        private static void Build()
        {
            defNames = new HashSet<string>();
            labels = new HashSet<string>();
            foreach (RSW_FacialAnimationOptOutDef d in DefDatabase<RSW_FacialAnimationOptOutDef>.AllDefsListForReading)
            {
                foreach (string x in d.xenotypes)
                {
                    if (string.IsNullOrEmpty(x))
                    {
                        continue;
                    }
                    defNames.Add(x);
                    XenotypeDef xd = DefDatabase<XenotypeDef>.GetNamedSilentFail(x);
                    if (xd != null && !string.IsNullOrEmpty(xd.label))
                    {
                        labels.Add(xd.label);
                    }
                }
            }
        }

        /// <summary>True when FA should not draw on this pawn. Mirrors FA's own key: the xenotype defName, or (as FA
        /// does) the def whose translated label equals the pawn's xenotype name.</summary>
        public static bool Skips(Pawn pawn)
        {
            Pawn_GeneTracker genes = pawn?.genes;
            if (genes == null)
            {
                return false;
            }
            if (defNames == null)
            {
                Build();
            }
            string dn = genes.Xenotype?.defName;
            if (dn != null && defNames.Contains(dn))
            {
                return true;
            }
            string name = genes.xenotypeName;
            return !string.IsNullOrEmpty(name) && labels.Contains(name);
        }
    }

    /// <summary>
    /// Postfix on FacialAnimation.FacialAnimationModSettings.ShouldDrawRaceXenoType(Pawn) : bool, FA's only per-pawn
    /// race/xenotype gate (called from DrawFaceGraphicsComp.CheckEnableDrawing when the pawn's render nodes are built).
    /// Resolved by name, so this assembly has no reference to FA: without FA, Prepare returns false and nothing is
    /// patched or logged. It only ever turns a true into false, so the player's own FA ignore list still applies.
    /// </summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Facial Animation opt-out", typeof(RSW_StarWarsRacesSettings), nameof(RSW_StarWarsRacesSettings.hideFacialAnimationFace))]
    public static class Patch_FA_ShouldDrawRaceXenoType
    {
        public const string TargetType = "FacialAnimation.FacialAnimationModSettings";
        public const string TargetMethodName = "ShouldDrawRaceXenoType";

        private static MethodBase Target()
        {
            System.Type t = AccessTools.TypeByName(TargetType);
            return t == null ? null : AccessTools.Method(t, TargetMethodName, new[] { typeof(Pawn) });
        }

        public static bool Prepare()
        {
            MethodBase m = Target();
            return m is MethodInfo mi && mi.ReturnType == typeof(bool);
        }

        public static MethodBase TargetMethod()
        {
            return Target();
        }

        public static void Postfix(Pawn pawn, ref bool __result)
        {
            if (__result && RSW_StarWarsRacesSettings.hideFacialAnimationFace && RSW_FacialAnimationOptOut.Skips(pawn))
            {
                __result = false;
            }
        }
    }
}
