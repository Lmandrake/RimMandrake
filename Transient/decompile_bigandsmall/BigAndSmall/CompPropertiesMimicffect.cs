using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompPropertiesMimicffect : CompAbilityEffect
{
	public CompPropertiesMimic Props => (CompPropertiesMimic)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Expected O, but got Unknown
		Pawn pawn = ((AbilityComp)this).parent.pawn;
		Corpse val = (Corpse)((LocalTargetInfo)(ref target)).Thing;
		if (val == null)
		{
			Log.Warning($"Target {((LocalTargetInfo)(ref target)).Thing} is not a corpse");
		}
		else
		{
			DoMimic(pawn, val, Props.genesToRetain);
		}
	}

	public static bool ShouldSkipGene(GeneDef def)
	{
		List<PawnExtension> allPawnExtensions = ((Def)(object)def).GetAllPawnExtensions();
		if (allPawnExtensions != null)
		{
			foreach (PawnExtension item in allPawnExtensions)
			{
				if (!GenList.NullOrEmpty<MorphTarget>((IList<MorphTarget>)item.morphTargets))
				{
					return true;
				}
				if (item.morphSettings != null)
				{
					return true;
				}
			}
		}
		return false;
	}

	public static void DoMimic(Pawn pawn, Corpse corpse, List<GeneDef> genesToRetain, bool spawnGibblets = true, bool addCorpseGenes = true, bool addCorpseRace = true)
	{
		//IL_0250: Unknown result type (might be due to invalid IL or missing references)
		//IL_0255: Unknown result type (might be due to invalid IL or missing references)
		//IL_02dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_030b: Unknown result type (might be due to invalid IL or missing references)
		CompProperticesMimicOffEffect.EndMimicry(pawn, genesToRetain);
		Pawn innerPawn = corpse.InnerPawn;
		if (innerPawn == null)
		{
			Log.Warning($"Target {corpse} is not a pawn");
			return;
		}
		if (addCorpseGenes && innerPawn.genes != null)
		{
			List<GeneDef> list = (from x in (from gene in ((corpse != null) ? corpse.InnerPawn : null).GetAllActiveGenes()
					select gene.def).ToList()
				where !ShouldSkipGene(x)
				select x).ToList();
			pawn.genes.Xenogenes.RemoveAll((Gene gene) => !genesToRetain.Contains(gene.def));
			foreach (GeneDef item in list)
			{
				pawn.genes.AddGene(item, true);
			}
			try
			{
				List<string> sizeTraitDefNames = new List<string> { "Gigantism", "Large", "Small", "Dwarfism" };
				List<Trait> list2 = pawn.story.traits.allTraits.Where((Trait trait) => sizeTraitDefNames.Contains(((Def)trait.def).defName)).ToList();
				for (int num = list2.Count - 1; num >= 0; num--)
				{
					Trait val = list2[num];
					pawn.story.traits.RemoveTrait(val, false);
				}
				foreach (Trait item2 in innerPawn.story.traits.allTraits.Where((Trait trait) => sizeTraitDefNames.Contains(((Def)trait.def).defName)))
				{
					pawn.story.traits.GainTrait(item2, false);
				}
			}
			catch (Exception ex)
			{
				Log.Error($"Error transferring size traits for {pawn}: {ex.Message}\n{ex.StackTrace}");
			}
		}
		ThingDef def = ((Thing)innerPawn).def;
		if (def != null && def.race.Humanlike)
		{
			pawn.story.bodyType = innerPawn.story.bodyType;
			pawn.gender = innerPawn.gender;
			pawn.story.hairDef = innerPawn.story.hairDef;
			pawn.story.headType = innerPawn.story.headType;
		}
		if (addCorpseRace)
		{
			_ = ((Thing)(pawn?)).def;
			ThingDef val2 = ((Thing)innerPawn).def;
			if (!val2.race.Humanlike)
			{
				ThingDef val3 = HumanlikeAnimals.HumanLikeAnimalFor(val2);
				if (val3 != null)
				{
					val2 = val3;
				}
			}
			if (val2.race.Humanlike)
			{
				pawn.SwapThingDef(val2, state: true, 999, force: true, null, permitFusion: false);
			}
		}
		((Thing)pawn).Position = ((Thing)corpse).Position;
		Pawn_ApparelTracker apparel = innerPawn.apparel;
		if (apparel != null)
		{
			apparel.DropAll(((Thing)pawn).Position, true, true, (Predicate<Apparel>)null);
		}
		if (spawnGibblets)
		{
			Gibblets.SpawnGibblets(corpse.InnerPawn, ((Thing)pawn).Position, ((Thing)pawn).Map);
		}
	}

	public override void PostApplied(List<LocalTargetInfo> targets, Map map)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).PostApplied(targets, map);
		foreach (LocalTargetInfo target in targets)
		{
			LocalTargetInfo current = target;
			Corpse val = (Corpse)((LocalTargetInfo)(ref current)).Thing;
			if ((int)val != 0)
			{
				((Thing)val).Destroy((DestroyMode)0);
			}
		}
		if (CompProperties_IncorporateEffect.RemoveGenesOverLimit(((AbilityComp)this).parent.pawn, -15))
		{
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageMimicryGenesRemoved", NamedArgument.op_Implicit(((Entity)((AbilityComp)this).parent.pawn).LabelShort))), LookTargets.op_Implicit((Thing)(object)((AbilityComp)this).parent.pawn), MessageTypeDefOf.NegativeEvent, true);
		}
	}
}
