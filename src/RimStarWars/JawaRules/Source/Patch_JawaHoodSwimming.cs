using System;
using System.Collections.Generic;
using RimWorld;
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
        public const PawnRenderFlags ApparelFlags = PawnRenderFlags.Clothes | PawnRenderFlags.Headgear;   // = RSW_HoodKernel.ApparelFlags (0x60), checked by the lint

        public static bool IsKeptHood(ThingDef def)
        {
            return def != null && def.HasModExtension<RSW_KeepHoodWhileSwimming>();
        }

        // True when the swim rule applies to this draw: toggle on, swimming, not a portrait.
        public static bool SwimForceApplies(PawnDrawParms parms)
        {
            return RSW_HoodKernel.SwimForceApplies(RSW_JawaRulesSettings.swimHoodEnabled, parms.swimming, parms.Portrait);
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
        [ThreadStatic] internal static bool reentry;

        public static void Postfix(PawnRenderNodeWorker_Apparel_Head __instance,
                                   PawnRenderNode __0, PawnDrawParms __1, ref bool __result)
        {
            if (__result || reentry)
            {
                return;
            }
            try
            {
                bool applies = JawaHoodRender.SwimForceApplies(__1);
                __result = RSW_HoodKernel.Postfix(__result, reentry, applies, applies && JawaHoodRender.IsKeptHood(__0?.apparel?.def), (int)__1.flags,
                    flags =>
                    {
                        PawnDrawParms again = __1;
                        again.flags = (PawnRenderFlags)flags;
                        reentry = true;
                        return __instance.CanDrawNow(__0, again);
                    });
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

    // JAWA_SWIM_HOOD_KEEP_1, MEASURED live on the full list 2026-10-09 (bridge6, extended ProofHood: worker is
    // PawnRenderNodeWorker_Apparel_Head, applies/kept True, base gates True, yet the re-ask said False with
    // headgearVisibleRestored=False): ReGrowthCore's postfix on PawnRenderNodeWorker_Apparel_Head.HeadgearVisible sets
    // __result = false whenever pawn.jobs.curJob.swimming ("IsBathingNow" = JobDriver_Bathe OR curJob.swimming), so
    // restoring Clothes|Headgear could never win. (StandaloneHotSpring's twin postfix only fires inside its own bath
    // toil.) Fix: a Priority.Last postfix on HeadgearVisible that, ONLY while our own kept-hood re-ask is running
    // (Patch_ApparelHead_CanDrawNow_SwimHood.reentry), replaces the answer with vanilla's own HeadgearVisible rule
    // (flags, bed, portrait/HatsOnlyOnMap). Outside that re-ask every mod's verdict stands untouched.
    public static class Patch_HeadgearVisible_KeptHoodReask
    {
        [HarmonyLib.HarmonyPriority(HarmonyLib.Priority.Last)]
        public static void Postfix(PawnDrawParms parms, ref bool __result)
        {
            if (__result || !Patch_ApparelHead_CanDrawNow_SwimHood.reentry)
            {
                return;
            }
            __result = VanillaHeadgearVisible(parms);
        }

        // Verse.PawnRenderNodeWorker_Apparel_Head.HeadgearVisible, 1.6, as decompiled (RimSage 2026-10-09).
        public static bool VanillaHeadgearVisible(PawnDrawParms parms)
        {
            if (!parms.flags.FlagSet(PawnRenderFlags.Clothes) || !parms.flags.FlagSet(PawnRenderFlags.Headgear)) return false;
            if (!parms.Portrait && parms.bed != null && !parms.bed.def.building.bed_showSleeperBody) return false;
            if (parms.Portrait && Prefs.HatsOnlyOnMap) return parms.flags.FlagSet(PawnRenderFlags.StylingStation);
            return true;
        }
    }

    // SWIM_HOOD_CANDRAW_PROOF_1: jawa/static_call proof read (type=RimMandrake.StarWars.JawaRules.JawaHoodProof
    // method=ProofHood args=""). Finds the worn guy762_JawaHood render node on the first SWIMMING hooded pawn on the current
    // map (else the first hooded pawn, swimming=false) and asks the real, patched PawnRenderNodeWorker_Apparel_Head.CanDrawNow
    // under the flags vanilla leaves a swimmer (Clothes, Headgear, NeverAimWeapon cleared). Pure read: nothing drawn or changed.
    public static class JawaHoodProof
    {
        public static string ProofHood(string unused)
        {
            try
            {
                Map map = Find.CurrentMap;
                if (map == null) return "ERROR no current map";
                int hooded = 0, swimmingHooded = 0;
                Pawn pick = null; PawnRenderNode pickNode = null;
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int i = 0; i < pawns.Count; i++)
                {
                    Pawn p = pawns[i];
                    PawnRenderNode node = FindHood(p?.Drawer?.renderer?.renderTree?.rootNode);
                    if (node == null) continue;
                    hooded++;
                    bool sw = p.Swimming;
                    if (sw) swimmingHooded++;
                    if (pick == null || (sw && !pick.Swimming)) { pick = p; pickNode = node; }
                }
                if (pick == null) return "hooded=0 swimmingHooded=0 note=no spawned pawn wears guy762_JawaHood (ERROR for the criterion: nothing to measure)";
                bool swimming = pick.Swimming;
                PawnDrawParms parms = new PawnDrawParms();
                parms.pawn = pick;
                parms.facing = pick.Rotation;
                parms.flags = PawnRenderFlags.Clothes | PawnRenderFlags.Headgear;
                if (swimming)
                {
                    // what PawnRenderer.ParallelGetPreRenderResults leaves a swimmer (0xFFFFFF1F)
                    parms.flags &= ~(PawnRenderFlags.Clothes | PawnRenderFlags.Headgear | PawnRenderFlags.NeverAimWeapon);
                    parms.swimming = true;
                }
                bool canDraw = pickNode.Worker.CanDrawNow(pickNode, parms);
                // JAWA_SWIM_HOOD_KEEP_1 discriminators (bridge6): which gate says no.
                PawnDrawParms restored = parms;
                restored.flags |= PawnRenderFlags.Clothes | PawnRenderFlags.Headgear;
                bool restoredCan = pickNode.Worker.CanDrawNow(pickNode, restored);
                PawnDrawParms dry = restored; dry.swimming = false;
                bool baseCan = pickNode.Worker is PawnRenderNodeWorker_Apparel_Head ? BaseGate(pickNode, dry) : false;
                bool hgVisible = PawnRenderNodeWorker_Apparel_Head.HeadgearVisible(restored);
                return "hooded=" + hooded + " swimmingHooded=" + swimmingHooded + " pawn=" + pick.LabelShortCap
                    + " swimming=" + swimming + " canDraw=" + canDraw + " flags=" + (int)parms.flags
                    + " toggle=" + RSW_JawaRulesSettings.swimHoodEnabled
                    + " worker=" + pickNode.Worker.GetType().FullName
                    + " applies=" + JawaHoodRender.SwimForceApplies(parms) + " kept=" + JawaHoodRender.IsKeptHood(pickNode.apparel?.def)
                    + " restoredCan=" + restoredCan + " headgearVisibleRestored=" + hgVisible + " baseGate=" + baseCan
                    + " skipFlag=" + pickNode.Props.skipFlag + " rotDrawMode=" + pickNode.Props.rotDrawMode + " parmsRot=" + parms.rotDrawMode
                    + " facing=" + parms.facing + " debugEnabled=" + pickNode.DebugEnabled;
            }
            catch (Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }

        // The PawnRenderNodeWorker base gates only (rotDrawMode, facing, skip flags, side, linked parts, DebugEnabled),
        // re-stated so a reader can tell a base-gate refusal from the apparel-head flag gate.
        private static bool BaseGate(PawnRenderNode node, PawnDrawParms parms)
        {
            if (!node.Props.rotDrawMode.HasFlag(parms.rotDrawMode)) return false;
            if (node.Props.visibleFacing != null && !node.Props.visibleFacing.Contains(parms.facing)) return false;
            if (node.Props.skipFlag != RenderSkipFlagDefOf.None && parms.skipFlags.HasFlag(node.Props.skipFlag)) return false;
            return node.DebugEnabled;
        }

        private static PawnRenderNode FindHood(PawnRenderNode n)
        {
            if (n == null) return null;
            if (n is PawnRenderNode_Apparel a && a.apparel?.def != null && JawaHoodRender.IsKeptHood(a.apparel.def)) return n;
            if (n.children != null)
            {
                for (int i = 0; i < n.children.Length; i++)
                {
                    PawnRenderNode r = FindHood(n.children[i]);
                    if (r != null) return r;
                }
            }
            return null;
        }
    }
}
