using HarmonyLib;
using RimWorld;
using System;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1: the shed arm (RM_VisslerArm) is a vanilla ingestible
    // (foodType Meat, rottable), so the engine's own hunger AI finds and eats it. This file is only
    // the Mod Settings gate: with visslerArmFoodEnabled off the arm reports itself not ingestible.
    [StaticConstructorOnStartup]
    public static class RM_VisslerArmPatches
    {
        private static ThingDef armDef;

        static RM_VisslerArmPatches()
        {
            try
            {
                armDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_VisslerArm");
                var target = AccessTools.PropertyGetter(typeof(Thing), "IngestibleNow");
                if (target == null)
                {
                    Log.Error("[RM LeaningScrub] vissler-arm-food: Thing.IngestibleNow not found, rule NOT armed.");
                    return;
                }
                new Harmony("mandrake.rm.leaningscrub").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_VisslerArmPatches), nameof(IngestibleNow_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM LeaningScrub] vissler-arm-food: patch failed, rule NOT armed. " + e);
            }
        }

        public static void IngestibleNow_Postfix(Thing __instance, ref bool __result)
        {
            if (__result && armDef != null && __instance.def == armDef
                && !RM_WindCalendar.On(RM_LeaningScrubSettings.visslerArmFoodEnabled))
            {
                __result = false;
            }
        }

        /// <summary>LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 A2 (jawa/static_call "on@x,z" / "off@x,z", a cleared pad): which
        /// of RM_LeaningScrub's wild animals the arm draws. For every roster kind that can eat it (meat eaters; flyers
        /// skipped), one wild animal, very hungry, stands beside an arm and asks the engine's own food search
        /// (FoodUtility.TryFindBestFoodSourceFor, what JobGiver_GetFood asks). "on": every eater picks the arm; "off"
        /// (visslerArmFoodEnabled false): none does. Each animal is removed before the next; the arm after.</summary>
        public static string ProofArmScavengers(string arg)
        {
            string mode = RM_FireStampProof.ParseMode(arg, out IntVec3 at);
            Map map = Find.CurrentMap;
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_LeaningScrub");
            if (map == null || armDef == null || biome == null) return "UNMEASURED: no map, RM_VisslerArm or RM_LeaningScrub";
            IntVec3 beside = at + new IntVec3(1, 0, 0);
            if (!at.IsValid || !at.InBounds(map) || !beside.InBounds(map) || !at.Standable(map) || !beside.Standable(map))
                return "UNMEASURED: the pad cells at " + at + " are not standable";
            bool savedMod = RM_LeaningScrubSettings.modEnabled, savedArm = RM_LeaningScrubSettings.visslerArmFoodEnabled;
            Thing arm = null;
            var found = new List<string>();
            var missed = new List<string>();
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                RM_LeaningScrubSettings.visslerArmFoodEnabled = mode != "off";
                arm = GenSpawn.Spawn(ThingMaker.MakeThing(armDef), at, map);
                foreach (PawnKindDef kind in biome.AllWildAnimals)
                {
                    if (kind?.race?.race == null || !kind.RaceProps.Animal || !kind.RaceProps.CanEverEat(armDef)) continue;
                    if (kind.race.GetStatValueAbstract(StatDefOf.MaxFlightTime) > 0f) continue;
                    Pawn p = null;
                    try
                    {
                        p = (Pawn)GenSpawn.Spawn(PawnGenerator.GeneratePawn(kind), beside, map);
                        if (p.needs?.food == null) continue;
                        p.needs.food.CurLevelPercentage = 0.05f;
                        bool ok = FoodUtility.TryFindBestFoodSourceFor(p, p, false, out Thing food, out ThingDef _,
                            canRefillDispenser: false, canUseInventory: false);
                        (ok && food == arm ? found : missed).Add(kind.defName + (ok && food != arm ? "->" + food?.def?.defName : ""));
                    }
                    finally
                    {
                        if (p != null && !p.Destroyed) p.Destroy();
                    }
                }
            }
            finally
            {
                if (arm != null && !arm.Destroyed) arm.Destroy();
                RM_LeaningScrubSettings.modEnabled = savedMod;
                RM_LeaningScrubSettings.visslerArmFoodEnabled = savedArm;
            }
            string st = "drawn=[" + string.Join(",", found) + "] notDrawn=[" + string.Join(",", missed) + "]";
            if (found.Count + missed.Count == 0) return "UNMEASURED: no meat-eating walker on the RM_LeaningScrub roster is loaded " + st;
            if (mode == "off") return found.Count == 0 ? "PASS off " + st : "FAIL: visslerArmFoodEnabled off but the arm drew " + st;
            return missed.Count == 0 ? "PASS " + st : "FAIL: a hungry meat eater beside the arm chose something else " + st;
        }
    }
}
