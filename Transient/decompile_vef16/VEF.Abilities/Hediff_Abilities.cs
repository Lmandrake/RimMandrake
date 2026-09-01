using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF.Abilities;

public class Hediff_Abilities : Hediff_Level
{
	public bool giveRandomAbilities = true;

	public override bool ShouldRemove => false;

	public override void PostAdd(DamageInfo? dinfo)
	{
		((Hediff_Level)this).PostAdd(dinfo);
		GiveRandomAbilityAtLevel(null);
	}

	public override void ChangeLevel(int levelOffset)
	{
		int num = base.level;
		((Hediff_Level)this).ChangeLevel(levelOffset);
		if (num != base.level && levelOffset > 0)
		{
			while (num < base.level)
			{
				GiveRandomAbilityAtLevel(num += 1);
			}
		}
	}

	public virtual void GiveRandomAbilityAtLevel(int? forLevel = null)
	{
		if (giveRandomAbilities)
		{
			forLevel = forLevel ?? base.level;
			CompAbilities comp = ((ThingWithComps)((Hediff)this).pawn).GetComp<CompAbilities>();
			List<AbilityDef> list = DefDatabase<AbilityDef>.AllDefsListForReading.Where((AbilityDef def) => !comp.HasAbility(def) && def.requiredHediff != null && def.requiredHediff.hediffDef == ((Hediff)this).def && def.requiredHediff.minimumLevel <= forLevel && (def.requiredTrait == null || ((Hediff)this).pawn.story.traits.HasTrait(def.requiredTrait))).ToList();
			AbilityDef abilityDef = default(AbilityDef);
			if (!GenCollection.TryRandomElement<AbilityDef>(list.Where((AbilityDef def) => def.requiredHediff.minimumLevel == forLevel), ref abilityDef))
			{
				abilityDef = GenCollection.RandomElement<AbilityDef>((IEnumerable<AbilityDef>)list);
			}
			comp.GiveAbility(abilityDef);
		}
	}

	public virtual IEnumerable<Gizmo> DrawGizmos()
	{
		yield break;
	}

	public virtual bool SatisfiesConditionForAbility(AbilityDef abilityDef)
	{
		return base.level >= abilityDef.requiredHediff.minimumLevel;
	}
}
