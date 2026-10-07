using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.KineticArms
{
    /// <summary>Marks a faction whose raiders may carry a kinetic weapon stolen from the ruins. Patched onto the vanilla
    /// pirate gang base (Patches/RM_KineticArms_PirateLooters.xml), so its children inherit it; a campaign faction gets it
    /// by its own Utinni patch.</summary>
    public class RM_KineticLooterExtension : DefModExtension
    {
        /// <summary>Weapon money a pawn of this faction counts as having, at least (poor salvagers like the Junkers).</summary>
        public float lootMoneyFloor = 0f;
    }

    /// <summary>
    /// Owner, 2026-10-06 (typed): "Mostly ruins only, but rare on raids that stole it from said ruins (pirates/outlaws)".
    /// After vanilla picks a raider's weapon, a looter-faction pawn that generated with a RANGED weapon swaps it, at the
    /// "looted kinetic weapon" chance, for a kinetic weapon his kind could afford (grenadiers get thudder grenades).
    /// Keyed on the FACTION, not the pawnkind: mercenary kinds are shared with outlanders, who never carry these.
    /// The chance is exact per pawn and independent of how many other guns the mod list adds.
    /// </summary>
    [HarmonyPatch(typeof(PawnWeaponGenerator), nameof(PawnWeaponGenerator.TryGenerateWeaponFor))]
    public static class RM_Patch_LootedKineticWeapons
    {
        /// <summary>The carried weapons, in RM_KineticMath.LootOption order: (settings toggle field, ThingDef, grenade).</summary>
        public static readonly (string field, string def, bool grenade)[] Carried =
        {
            ("enableThudder", "RM_Weapon_ThudderGrenade", true),
            ("enablePalmThumper", "RM_Gun_PalmThumper", false),
            ("enableSlamLauncher", "RM_Gun_SlamLauncher", false),
            ("enableRepulsorRifle", "RM_Gun_RepulsorRifle", false),
            ("enableGravRam", "RM_Gun_GravRam", false),
        };

        public static bool IsLooter(Faction f) => f?.def?.GetModExtension<RM_KineticLooterExtension>() != null;

        public static bool IsGrenadier(PawnKindDef k)
        {
            if (k?.weaponTags == null)
            {
                return false;
            }
            foreach (string t in k.weaponTags)
            {
                if (t != null && t.StartsWith("Grenade"))
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>The looted weapon this pawn would carry for the given rolls, or null. Public for the proof tool.</summary>
        public static ThingDef Pick(PawnKindDef kind, float roll1, float roll2, float moneyFloor = 0f)
        {
            var opts = new List<RM_KineticMath.LootOption>(Carried.Length);
            var defs = new List<ThingDef>(Carried.Length);
            foreach (var c in Carried)
            {
                ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(c.def);
                defs.Add(td);
                opts.Add(new RM_KineticMath.LootOption
                {
                    grenade = c.grenade,
                    price = td != null ? td.GetStatValueAbstract(StatDefOf.MarketValue) : float.MaxValue,
                    enabled = td != null && RimMandrakeKineticArmsMod.Enabled(c.field),
                });
            }
            float chance = RimMandrakeKineticArmsSettings.lootedOnRaiders ? RimMandrakeKineticArmsSettings.lootedChancePercent / 100f : 0f;
            int i = RM_KineticMath.PickLooted(opts, IsGrenadier(kind), RM_KineticMath.LootMoney(kind.weaponMoney.max, moneyFloor), chance, roll1, roll2);
            return i >= 0 ? defs[i] : null;
        }

        public static void Postfix(Pawn pawn)
        {
            if (pawn?.equipment == null || !IsLooter(pawn.Faction))
            {
                return;
            }
            ThingWithComps own = pawn.equipment.Primary;
            if (own == null || !own.def.IsRangedWeapon)
            {
                return; // melee drifters and thrashers keep their clubs
            }
            ThingDef td = Pick(pawn.kindDef, Rand.Value, Rand.Value, pawn.Faction.def.GetModExtension<RM_KineticLooterExtension>().lootMoneyFloor);
            if (td == null)
            {
                return;
            }
            var w = (ThingWithComps)ThingMaker.MakeThing(td, td.MadeFromStuff ? GenStuff.DefaultStuffFor(td) : null);
            PawnGenerator.PostProcessGeneratedGear(w, pawn);
            pawn.equipment.DestroyAllEquipment();
            pawn.equipment.AddEquipment(w);
        }
    }
}
