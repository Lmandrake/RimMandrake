using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class MeleeReachCombatUtility
{
	public static float GetMeleeReachRange(this Pawn caster, Verb verb)
	{
		ThingDef val = ((verb == null) ? null : ((Thing)(verb.EquipmentSource?)).def);
		if (val != null && StatExtension.StatBaseDefined((BuildableDef)(object)val, VEFDefOf.VEF_MeleeWeaponRange))
		{
			return StatExtension.GetStatValueAbstract((BuildableDef)(object)val, VEFDefOf.VEF_MeleeWeaponRange, (ThingDef)null);
		}
		return 1.42f;
	}

	public static Verb GetMeleeVerb(this Pawn pawn)
	{
		object obj = pawn.jobs.curJob?.verbToUse;
		if (obj == null)
		{
			Pawn_EquipmentTracker equipment = pawn.equipment;
			if (equipment == null)
			{
				return null;
			}
			CompEquippable primaryEq = equipment.PrimaryEq;
			if (primaryEq == null)
			{
				return null;
			}
			obj = primaryEq.PrimaryVerb;
		}
		return (Verb)obj;
	}

	public static bool IsVanillaMeleeAttack(Verb verb)
	{
		Thing caster = verb.Caster;
		Pawn val = (Pawn)(object)((caster is Pawn) ? caster : null);
		if (val != null && val.GetMeleeReachRange(verb) > 1.42f)
		{
			return false;
		}
		return true;
	}
}
