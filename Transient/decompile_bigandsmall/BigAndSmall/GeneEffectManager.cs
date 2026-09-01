using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class GeneEffectManager
{
	private static Action<Pawn_GeneTracker, GeneDef> notifyGenesChangedDelegate;

	public static Action<Pawn_SkillTracker> dirtyAptitudesDelegate;

	public static void GainOrRemovePassion(bool disabled, Gene gene)
	{
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		if (gene.def.passionMod != null && gene.def.prerequisite == null)
		{
			if (disabled)
			{
				SkillRecord skill = gene.pawn.skills.GetSkill(gene.def.passionMod.skill);
				skill.passion = gene.NewPassionForOnRemoval(skill);
			}
			else
			{
				SkillRecord skill2 = gene.pawn.skills.GetSkill(gene.def.passionMod.skill);
				gene.passionPreAdd = skill2.passion;
				skill2.passion = gene.def.passionMod.NewPassionFor(skill2);
			}
			((int?)null).GetValueOrDefault();
			if (dirtyAptitudesDelegate == null)
			{
				dirtyAptitudesDelegate = AccessTools.MethodDelegate<Action<Pawn_SkillTracker>>(AccessTools.Method(typeof(Pawn_SkillTracker), "DirtyAptitudes", (Type[])null, (Type[])null), (object)null, true, (Type[])null);
			}
			dirtyAptitudesDelegate(gene.pawn.skills);
		}
	}

	public static void GainOrRemoveAbilities(bool disabled, Gene gene)
	{
		try
		{
			if (gene?.pawn?.abilities == null || gene?.def?.abilities == null)
			{
				return;
			}
			foreach (AbilityDef ability in gene.def.abilities)
			{
				if (disabled)
				{
					bool flag = false;
					foreach (Gene item in from x in gene.pawn.GetAllActiveGenes()
						where x != gene
						select x)
					{
						if (item != gene && item?.def?.abilities != null && item.def.abilities.Contains(ability))
						{
							flag = true;
							break;
						}
					}
					if (!flag)
					{
						Pawn_AbilityTracker abilities = gene.pawn.abilities;
						if (abilities != null)
						{
							abilities.RemoveAbility(ability);
						}
					}
				}
				else
				{
					Pawn_AbilityTracker abilities2 = gene.pawn.abilities;
					if (abilities2 != null)
					{
						abilities2.GainAbility(ability);
					}
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error("Error in GainOrRemoveAbilities: \n" + ex.Message + "\n" + ex.StackTrace);
		}
	}

	public static void ApplyForcedTraits(bool disabled, Gene gene)
	{
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Expected O, but got Unknown
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Expected O, but got Unknown
		Pawn pawn = gene.pawn;
		if (GenList.NullOrEmpty<GeneticTraitData>((IList<GeneticTraitData>)gene.def.forcedTraits) || pawn.story == null)
		{
			return;
		}
		foreach (GeneticTraitData forcedTrait in gene.def.forcedTraits)
		{
			_ = forcedTrait;
			if (disabled)
			{
				for (int i = 0; i < gene.def.forcedTraits.Count; i++)
				{
					Trait trait = new Trait(gene.def.forcedTraits[i].def, gene.def.forcedTraits[i].degree, false);
					trait.sourceGene = gene;
					pawn.story.traits.allTraits.RemoveAll((Trait tr) => tr.def == trait.def && tr.sourceGene == gene);
				}
			}
			else
			{
				for (int j = 0; j < gene.def.forcedTraits.Count; j++)
				{
					Trait val = new Trait(gene.def.forcedTraits[j].def, gene.def.forcedTraits[j].degree, false)
					{
						sourceGene = gene
					};
					pawn.story.traits.GainTrait(val, true);
				}
			}
		}
	}
}
