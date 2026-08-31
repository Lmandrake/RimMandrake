/* Ported from Ruthless Faction Pursuit (workshop 3621784437) by Matathias, GPLv3, with the
 * Harmony instance id changed to this fork's own packageId. See ../../LICENSE.txt and
 * About.xml for the fork's credit and scope. */
using HarmonyLib;
using RimWorld;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;
using Verse;

namespace RimMandrake.Utinni.EmpirePursuit
{
    [StaticConstructorOnStartup]
    public static class HarmonyPatcher
    {
        static HarmonyPatcher()
        {
            new Harmony("mandrake.rut.empirepursuit").PatchAll(Assembly.GetExecutingAssembly());
        }
    }

    [HarmonyPatch(typeof(IncidentWorker_RaidEnemy), "FactionCanBeGroupSource")]
    internal class IncidentWorker_RaidEnemy_FactionCanBeGroupSource
    {
        private static void Postfix(Faction f, ref bool __result)
        {
            if (__result)
            {
                /* Look through ScenParts to see if a Ruthless Pursuit faction can be used for normal raids */
                foreach (ScenPart_RuthlessPursuingMechanoids part in Find.Scenario.AllParts.OfType<ScenPart_RuthlessPursuingMechanoids>())
                {
                    if (part.PursuitFaction == f)
                    {
                        if (!part.FactionCanNormalRaid)
                        {
                            DebugUtility.DebugLog($"excluded faction {part.PursuitFaction.Name} from raid");
                            __result = false;
                        }
                        break;
                    }
                }
            }
        }
    }
}
