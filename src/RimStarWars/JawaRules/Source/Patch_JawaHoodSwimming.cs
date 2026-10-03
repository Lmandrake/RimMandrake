using System;
using Verse;

namespace RimMandrake.StarWars.JawaRules
{
    // JAWA_SWIM_HOOD_KEEP_1 — owner, 2026-09-25: "Jawa should never be seen without a
    // hood." A swimming Jawa lost the real (dyed) hood. MEASURED in the decompiled 1.6
    // engine (RimSage, 2026-10-03):
    //   * PawnRenderer.ParallelGetPreRenderResults: when pawn.Swimming it masks the flags
    //     with 0xFFFFFF1F (clears Headgear 0x20, Clothes 0x40, NeverAimWeapon 0x80) and
    //     sets NoBody.
    //   * PawnRenderNodeWorker_Apparel_Head.CanDrawNow (the worker every Overhead apparel
    //     node gets from DynamicPawnRenderNodeSetup_Apparel) returns false unless both
    //     Clothes and Headgear are set, so the worn hood is dropped.
    //   * The head itself is NOT culled: PawnRenderNodeWorker_Head only lowers it by 0.5
    //     (OffsetFor, parms.swimming). The hood's parent chain (Head -> Apparel root)
    //     therefore still draws, and re-allowing the hood node is enough.
    //
    // Fix: a postfix on PawnRenderNodeWorker_Apparel_Head.CanDrawNow. Only when vanilla
    // said no, the pawn is swimming (not a portrait), the toggle is on, and the node's
    // apparel def carries RSW_KeepHoodWhileSwimming (added to guy762_JawaHood by
    // Patches/RSW_JawaHood.xml) does it re-ask the SAME worker with Clothes|Headgear put
    // back. Every other vanilla gate (rotDrawMode, skip flags, bed visibility,
    // HatsOnlyOnMap) still decides. Rendering runs in parallel (ParallelPreDraw), hence the
    // [ThreadStatic] re-entry guard. No Scribe, no state.
    public class RSW_KeepHoodWhileSwimming : DefModExtension
    {
    }

    public static class JawaHoodRender
    {
        public const PawnRenderFlags ApparelFlags = PawnRenderFlags.Clothes | PawnRenderFlags.Headgear;

        public static bool IsKeptHood(ThingDef def)
        {
            return def != null && def.HasModExtension<RSW_KeepHoodWhileSwimming>();
        }

        // True when the swim rule applies to this draw: toggle on, swimming, not a portrait.
        public static bool SwimForceApplies(PawnDrawParms parms)
        {
            return RSW_JawaRulesSettings.swimHoodEnabled && parms.swimming && !parms.Portrait;
        }

        // The flags a kept hood is drawn under: vanilla's, plus Clothes|Headgear back
        // while the swim rule applies.
        public static PawnDrawParms EffectiveParms(PawnDrawParms parms)
        {
            if (SwimForceApplies(parms))
            {
                parms.flags |= ApparelFlags;
            }
            return parms;
        }
    }

    public static class Patch_ApparelHead_CanDrawNow_SwimHood
    {
        [ThreadStatic] private static bool reentry;

        public static void Postfix(PawnRenderNodeWorker_Apparel_Head __instance,
                                   PawnRenderNode __0, PawnDrawParms __1, ref bool __result)
        {
            if (__result || reentry)
            {
                return;
            }
            try
            {
                if (!JawaHoodRender.SwimForceApplies(__1) || !JawaHoodRender.IsKeptHood(__0?.apparel?.def))
                {
                    return;
                }
                reentry = true;
                __result = __instance.CanDrawNow(__0, JawaHoodRender.EffectiveParms(__1));
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RimMandrake.StarWars.JawaRules] swim-hood: " + e.Message, 0x4A57A7);
            }
            finally
            {
                reentry = false;
            }
        }
    }
}
