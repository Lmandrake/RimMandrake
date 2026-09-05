using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1 (broad pass). divine_satiation_engine.md
    // §3① / §3⑧ distinguish HOW a thing dies, which Patch_BattleResolved (the
    // sibling that scores Sh'kaar on every violent death) deliberately left for
    // a later pass. Ishko is pleased by "killing at a remove -- the ranged shot,
    // which hurts the enemy before he can reach you and keeps the hand unseen"
    // and displeased by "melee -- to fight hand-to-hand is to be dragged out of
    // cover, into the open, seen and gripped". Sh'kaar's "purest war" is melee,
    // gorging him more than a ranged shot -- so a melee kill earns him a little
    // MORE on top of Patch_BattleResolved's flat violent-death delta.
    //
    // Verified against decompiled source (RimSage): Pawn.Kill(DamageInfo? dinfo,
    // Hediff) is the death choke; DamageInfo.Weapon (ThingDef) and .Instigator
    // carry the manner and the killer. A bare-handed pawn kill (null weapon,
    // pawn instigator) reads as melee. This is a SIBLING postfix to
    // Patch_BattleResolved and does not touch its Sh'kaar base delta.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.Kill))]
    public static class Patch_KillManner
    {
        [HarmonyPostfix]
        public static void Postfix(DamageInfo? dinfo)
        {
            if (!dinfo.HasValue) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            DamageInfo d = dinfo.Value;
            bool byPlayer = d.Instigator is Pawn ip && ip.Faction == Faction.OfPlayer;
            ThingDef weapon = d.Weapon;

            bool ranged = weapon != null && weapon.IsRangedWeapon;
            bool melee = (weapon != null && weapon.IsMeleeWeapon)
                         || (weapon == null && d.Instigator is Pawn); // bare-handed

            if (ranged && byPlayer)
            {
                comp.ApplyDelta(God.Ishko, EventMagnitude.Small,
                    "a kill at a remove, the hand unseen");
            }
            else if (melee)
            {
                comp.ApplyDelta(God.Shkaar, EventMagnitude.Small, "melee, the close exposed war");
                if (byPlayer)
                {
                    comp.ApplyDelta(God.Ishko, -EventMagnitude.Small,
                        "our hand in the open, gripped");
                }
            }
        }
    }
}
