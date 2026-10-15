using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE. Owner, on the Ashwallow art sheet (2026-10-11): "have its legs curl inward
    /// along its body to help it seal up into a dome when it's half-buried ... plus the behavior to assume the defensive
    /// stance when under heat attack."
    ///
    /// Before this, the dome (RM_JobDriver_Burrow + RM_Burrowed) started only when a FREE ground fire came within the race's
    /// detectionRadius (RM_JobGiver_BurrowOnFire, asked at Animal_PreWander). A flamethrower, a burn from an attached fire or
    /// an incendiary beam hit the animal standing up. Two halves here, both opted in per race by RM_BurrowOnFireExtension:
    ///
    /// 1. Pawn.PostApplyDamage postfix: a heat-category hit (DamageDef.armorCategory == Heat — data-driven, so Flame, Burn,
    ///    Beam and every modded incendiary, the same gate Patch_FurnaceBeastHeatImmunity uses) starts RM_Burrow at once,
    ///    InterruptForced, and sets the driver's heat hold; a hit while already domed only extends the hold. Postfix, after
    ///    vanilla: mindState.Notify_DamageTaken has already run, so an animal that went manhunter keeps its rage (refused).
    /// 2. PawnRenderNode_AnimalPart.GraphicFor postfix: while RM_Burrowed holds, the body draws the race's domeTexPath
    ///    (Graphic_Multi, the body's own drawSize, shader and colours). RM_Burrowed sets forceRenderTreeRecache, so the
    ///    swap lands on the hediff's add and remove. No texture at that path = the standing body, said once in the log.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RM_BurrowHeatReaction
    {
        internal static readonly DamageArmorCategoryDef HeatCategory;

        // domeTexPath -> its south texture exists (checked once per path; ContentFinder is not free)
        private static readonly Dictionary<string, bool> domeArtPresent = new Dictionary<string, bool>();

        static RM_BurrowHeatReaction()
        {
            HeatCategory = DefDatabase<DamageArmorCategoryDef>.GetNamedSilentFail("Heat");
            if (HeatCategory == null)
            {
                Log.Error("[RimMandrake.Pyrelands] burrow heat reaction: no DamageArmorCategoryDef named 'Heat' - a heat hit "
                        + "will NOT dome a burrower (ground fires still do).");
            }
            var harmony = new Harmony("mandrake.rm.pyrelands.burrowdome");
            try
            {
                harmony.Patch(AccessTools.Method(typeof(Pawn), nameof(Pawn.PostApplyDamage)),
                    postfix: new HarmonyMethod(typeof(RM_BurrowHeatReaction), nameof(Postfix_PostApplyDamage)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] burrow heat reaction: PostApplyDamage patch FAILED, a heat hit will NOT "
                        + "dome a burrower: " + e.Message);
            }
            try
            {
                harmony.Patch(AccessTools.Method(typeof(PawnRenderNode_AnimalPart), nameof(PawnRenderNode_AnimalPart.GraphicFor)),
                    postfix: new HarmonyMethod(typeof(RM_BurrowHeatReaction), nameof(Postfix_GraphicFor)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] burrow dome pose: GraphicFor patch FAILED, a domed burrower draws "
                        + "standing: " + e.Message);
            }
        }

        public static void Postfix_PostApplyDamage(Pawn __instance, DamageInfo dinfo)
        {
            Pawn pawn = __instance;
            try
            {
                RM_BurrowOnFireExtension ext = pawn?.def?.GetModExtension<RM_BurrowOnFireExtension>();
                if (ext == null)
                {
                    return;   // every other pawn in the game leaves on this first comparison
                }
                bool heat = HeatCategory != null && dinfo.Def != null && dinfo.Def.armorCategory == HeatCategory;
                if (!RM_FireEcoKernel.DomeOnHeatHit(heat, ext.domeOnHeatHit, PyrelandsMechanicsGate.On,
                        RM_PyrelandsSettings.burrowOnFireEnabled, RM_PyrelandsSettings.burrowDomeOnHeatHit,
                        !pawn.Dead && pawn.Spawned, pawn.Downed, pawn.InMentalState))
                {
                    return;
                }
                if (pawn.jobs == null || pawn.health?.hediffSet == null)
                {
                    return;
                }
                int now = Find.TickManager.TicksGame;
                if (pawn.jobs.curDriver is RM_JobDriver_Burrow already)
                {
                    already.NoteHeatHit(now, ext.heatHoldTicks);
                    return;
                }
                pawn.jobs.StartJob(JobMaker.MakeJob(PyrelandsMechanicsDefOf.RM_Burrow), JobCondition.InterruptForced,
                    null, false, true);
                if (pawn.jobs.curDriver is RM_JobDriver_Burrow started)
                {
                    started.NoteHeatHit(now, ext.heatHoldTicks);
                }
                else
                {
                    Log.WarningOnce("[RimMandrake.Pyrelands] burrow heat reaction: " + pawn.ThingID + " was hit by heat but "
                                  + "RM_Burrow did not start (current job " + (pawn.CurJobDef?.defName ?? "none") + ").",
                                    0x5EA7D0E ^ pawn.thingIDNumber);
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] burrow heat reaction: " + e, 0x5EA7D0F);
            }
        }

        public static void Postfix_GraphicFor(Pawn pawn, ref Graphic __result)
        {
            try
            {
                if (__result == null || pawn == null || pawn.Dead)
                {
                    return;
                }
                string path = pawn.def?.GetModExtension<RM_BurrowOnFireExtension>()?.domeTexPath;
                if (path.NullOrEmpty() || pawn.Drawer?.renderer?.CurRotDrawMode != RotDrawMode.Fresh
                    || pawn.health?.hediffSet == null || !pawn.health.hediffSet.HasHediff(PyrelandsMechanicsDefOf.RM_Burrowed))
                {
                    return;
                }
                if (!DomeArtPresent(path))
                {
                    return;
                }
                __result = GraphicDatabase.Get<Graphic_Multi>(path, __result.Shader, __result.drawSize, __result.Color,
                    __result.ColorTwo);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] burrow dome pose: " + e, 0x5EA7D10);
            }
        }

        /// <summary>Script probe (jawa/static_call, Pawn by ThingID): "burrowed=;job=;heatHoldUntil=;now=;fireNear=;
        /// domeTexPath=;domeArt=;bodyGraphic=". bodyGraphic is the body node's graphic as of the LAST draw (the tree
        /// rebuilds lazily), so read it after a tick with the pawn on screen.</summary>
        public static string ProbeDome(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned)
            {
                return "spawned=false";
            }
            RM_BurrowOnFireExtension ext = pawn.def.GetModExtension<RM_BurrowOnFireExtension>();
            var driver = pawn.jobs?.curDriver as RM_JobDriver_Burrow;
            string body = "none";
            if (pawn.Drawer?.renderer?.renderTree != null
                && pawn.Drawer.renderer.renderTree.TryGetNodeByTag(PawnRenderNodeTagDefOf.Body, out PawnRenderNode node))
            {
                body = node?.PrimaryGraphic?.path ?? "none";
            }
            string path = ext?.domeTexPath;
            return "burrowed=" + (pawn.health?.hediffSet?.HasHediff(PyrelandsMechanicsDefOf.RM_Burrowed) ?? false)
                 + ";job=" + (pawn.CurJobDef?.defName ?? "none")
                 + ";heatHoldUntil=" + (driver?.HeatHoldUntil ?? -1)
                 + ";now=" + Find.TickManager.TicksGame
                 + ";fireNear=" + RM_JobGiver_BurrowOnFire.FireIsNear(pawn, pawn.Map, ext?.detectionRadius ?? PyrelandsTuning.BurrowDetectionRadius)
                 + ";domeTexPath=" + (path ?? "none")
                 + ";domeArt=" + (!path.NullOrEmpty() && DomeArtPresent(path))
                 + ";bodyGraphic=" + body;
        }

        internal static bool DomeArtPresent(string path)
        {
            if (!domeArtPresent.TryGetValue(path, out bool present))
            {
                present = ContentFinder<Texture2D>.Get(path + "_south", false) != null;
                domeArtPresent[path] = present;
                if (!present)
                {
                    Log.Warning("[RimMandrake.Pyrelands] burrow dome pose: no texture at " + path + "_south - a domed "
                              + "burrower draws its standing body until the dome art is installed.");
                }
            }
            return present;
        }
    }
}
