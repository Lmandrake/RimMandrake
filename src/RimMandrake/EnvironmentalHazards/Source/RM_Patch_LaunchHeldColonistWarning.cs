using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // LAUNCH_HELD_COLONIST_WARNING_1 (decision taken by question card 2026-10-08: "Warn at launch").
    // Vanilla 1.6 GravshipUtility.PreLaunchConfirmation(Building_GravEngine, Action) builds the
    // launch confirmation text and adds a Dialog_MessageBox in the same call (its only caller is
    // RitualOutcomeEffectWorker_GravshipLaunch). This postfix appends one more warning block to that
    // dialog's public `text` field, naming every colonist or colony prisoner held inside something
    // that is not ours: a brine jacket (RM_Building_BrineEncasement), a Hwelgrue's gut
    // (RM_CompGutSwallow), a Titanoslime (RM_CompEngulfer), or anything else of that shape. Generic
    // on purpose: it reads ParentHolder, so no hard dependency on DivingInteraction/TheRot/
    // GelatinousSlime. What happens if the player launches anyway is unchanged vanilla: the colonist
    // is recorded lost with a letter (HOLDER_SAFETY_LAUNCH_1's RimSage read).
    //
    // GimmeSomeSlack's launch handling (9401f7a73) is NOT on this hook: it rides
    // CompAerialAnchor.PostDeSpawn during GravshipUtility.GenerateGravship, after the confirm.
    [StaticConstructorOnStartup]
    public static class RM_Patch_LaunchHeldColonistWarning
    {
        static RM_Patch_LaunchHeldColonistWarning()
        {
            MethodBase target = AccessTools.Method(typeof(GravshipUtility), nameof(GravshipUtility.PreLaunchConfirmation));
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] launch held-colonist warning: GravshipUtility.PreLaunchConfirmation "
                    + "not found -- warning NOT armed. The engine signature this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target, postfix: new HarmonyMethod(
                    typeof(RM_Patch_LaunchHeldColonistWarning), nameof(PreLaunchConfirmation_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] launch held-colonist warning: patch failed, warning NOT armed. " + e);
            }
        }

        public static void PreLaunchConfirmation_Postfix(Building_GravEngine engine)
        {
            try
            {
                if (!RM_EnvironmentalHazardsSettings.launchHeldColonistWarningEnabled || engine?.Map == null)
                {
                    return;
                }

                List<string> lines = HeldLines(engine.Map);
                if (lines.Count == 0)
                {
                    return;
                }

                // The dialog vanilla just added is the newest Dialog_MessageBox on the stack.
                Dialog_MessageBox dialog = Find.WindowStack.Windows.OfType<Dialog_MessageBox>().LastOrDefault();
                if (dialog == null)
                {
                    return;
                }

                dialog.text += "\n\n" + ("GravEngineWarning".Translate() + ": ").Colorize(ColorLibrary.RedReadable)
                    + "Held inside something, and will be lost if the ship leaves without freeing them" + ":\n"
                    + lines.ToLineList("  - ", capitalizeItems: true);
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM EnvironmentalHazards] launch held-colonist warning failed; the launch dialog is unchanged. " + e,
                    0x4C48434C);
            }
        }

        public static List<string> HeldLines(Map map)
        {
            List<string> lines = new List<string>();
            foreach (Pawn p in map.mapPawns.AllPawnsUnspawned)
            {
                bool ours = p.Faction == Faction.OfPlayer || p.IsPrisonerOfColony;
                Thing holder = p.SpawnedParentOrMe;
                bool hasHolder = holder != null && holder != p && holder.Spawned && holder.Map == map;
                bool holderIsOurs = hasHolder && holder.Faction == Faction.OfPlayer;
                bool inTransporter = p.ParentHolder is ActiveTransporterInfo;
                if (RM_RoomCoolerKernel.ShouldNameHeld(ours, p.Dead, p.Spawned, inTransporter, hasHolder, holderIsOurs))
                {
                    lines.Add(p.NameFullColored.Resolve() + " (inside " + holder.LabelShort + ")");
                }
            }
            return lines;
        }
    }
}
