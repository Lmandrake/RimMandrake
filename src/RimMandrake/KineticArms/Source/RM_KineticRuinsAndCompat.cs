using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.KineticArms
{
    /// <summary>
    /// Ruins loot (owner, card 2026-10-06 22:37: kinetic weapons are FOUND in Ancient Danger ruins). Added as one more
    /// option of vanilla's MapGen_AncientTempleContents (Patches/RM_KineticArms_RuinsLoot.xml), the loot table every
    /// ancient-danger temple rolls. Ancient Dangers are vanilla, so this lives in the RM mod and works without the
    /// campaign; in the campaign those ancients are Rakata (UtinniPatches AncientsAreRakata.xml), which is the whole
    /// "Rakatan technology" framing with no second patch. Picks at GENERATE time among the weapons whose Mod Settings
    /// toggle is on (a ThingFilter's tags resolve once at load, so a filter could not honour a toggle). Kicker mines and
    /// pulse cannons are minified by ThingSetMaker.PostProcess. Chance and shell stack are PROVISIONAL.
    /// </summary>
    public class RM_ThingSetMaker_KineticRuins : ThingSetMaker
    {
        private static List<bool> EnabledFlags(out List<ThingDef> defs)
        {
            defs = new List<ThingDef>();
            var on = new List<bool>();
            foreach (var w in RimMandrakeKineticArmsMod.Weapons)
            {
                ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(w.def);
                defs.Add(td);
                on.Add(td != null && RimMandrakeKineticArmsMod.Enabled(w.field));
            }
            return on;
        }

        protected override bool CanGenerateSub(ThingSetMakerParams parms)
        {
            if (!RimMandrakeKineticArmsSettings.foundInRuins)
            {
                return false;
            }
            return EnabledFlags(out _).Contains(true);
        }

        /// <summary>The one roll that decides a temple's kinetic loot; public for the proof tool (fixed rolls).</summary>
        public static Thing Make(float roll1, float roll2, float roll3)
        {
            List<bool> on = EnabledFlags(out List<ThingDef> defs);
            float chance = RimMandrakeKineticArmsSettings.foundInRuins ? RimMandrakeKineticArmsSettings.ruinsChancePercent / 100f : 0f;
            int i = RM_KineticMath.PickRuins(on, chance, roll1, roll2);
            if (i < 0)
            {
                return null;
            }
            ThingDef td = defs[i];
            Thing t = ThingMaker.MakeThing(td, td.MadeFromStuff ? GenStuff.DefaultStuffFor(td) : null);
            t.stackCount = Mathf.Min(td.stackLimit, RM_KineticMath.RuinsStack(td.stackLimit > 1, roll3));
            ThingSetMakerUtility.AssignQuality(t, QualityGenerator.Reward);
            return t;
        }

        protected override void Generate(ThingSetMakerParams parms, List<Thing> outThings)
        {
            Thing t = Make(Rand.Value, Rand.Value, Rand.Value);
            if (t != null)
            {
                outThings.Add(t);
            }
        }

        protected override IEnumerable<ThingDef> AllGeneratableThingsDebugSub(ThingSetMakerParams parms)
        {
            EnabledFlags(out List<ThingDef> defs);
            foreach (ThingDef d in defs)
            {
                if (d != null)
                {
                    yield return d;
                }
            }
        }
    }

    /// <summary>"Kicker mines hidden from enemies" (design §4, default on = vanilla trap rules: hostiles do not know of
    /// it). Off: every hostile pawn knows where the plate is and paths around it. KnowsOfTrap is not virtual, so a
    /// postfix scoped to our class.</summary>
    [HarmonyPatch(typeof(Building_Trap), nameof(Building_Trap.KnowsOfTrap))]
    public static class RM_Patch_KickerMine_KnowsOfTrap
    {
        public static void Postfix(Building_Trap __instance, Pawn p, ref bool __result)
        {
            if (!__result && __instance is RM_Building_KickerMine && !RimMandrakeKineticArmsSettings.kickerHidden
                && p?.Faction != null && p.Faction.HostileTo(__instance.Faction))
            {
                __result = true;
            }
        }
    }

    /// <summary>Owner Q3 (card 2026-10-06): kinetic blasts SWAY Gimme Some Slack's overhead cords; only real explosions cut
    /// them. Every Kinetic Arms DamageDef carries this marker; Gimme Some Slack's explosion hook skips a damage def that
    /// carries a DefModExtension of this exact class NAME (it cannot reference this assembly). The "Kinetic blasts cut
    /// aerial cords" setting (default off) removes the marker at runtime.</summary>
    public class RM_KineticBlastExtension : DefModExtension
    {
    }

    public static class RM_KineticArmsFx
    {
        private static FleckDef ring;
        private static bool looked;

        /// <summary>The class's signature pale shock ring (art kba_RM_Explosion_KineticRing), drawn once per blast.</summary>
        public static void Ring(Map map, IntVec3 c, float radius)
        {
            if (map == null || !c.InBounds(map))
            {
                return;
            }
            if (!looked)
            {
                ring = DefDatabase<FleckDef>.GetNamedSilentFail("RM_Fleck_KineticRing");
                looked = true;
            }
            if (ring != null)
            {
                FleckMaker.Static(c.ToVector3Shifted(), map, ring, Mathf.Max(1f, radius * 1.2f));
            }
        }
    }
}
