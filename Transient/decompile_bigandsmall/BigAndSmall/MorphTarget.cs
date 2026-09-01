using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class MorphTarget
{
	public class HediffToBodypart
	{
		public HediffDef hediff;

		public List<BodyPartDef> bodyparts = new List<BodyPartDef>();
	}

	public ThingDef raceThingDef;

	public XenotypeDef xenotype;

	public XenotypeDef fakeXenotype;

	public List<HediffDef> hediffs;

	public List<HediffToBodypart> hediffsToParts;

	public List<GeneDef> endoGenes;

	public List<GeneDef> xenoGenes;

	public List<GeneDef> removeGenes;

	public List<HediffDef> removeHediffs;

	public List<TraitDef> addTraits;

	public List<TraitDef> removeTraits;

	public bool isRetromorph;

	public Gender? preferredGenders;

	public bool ignoreGender;

	public float morphWeight = 1f;

	public void ExecuteMorph(Pawn pawn)
	{
		//IL_02b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c2: Expected O, but got Unknown
		if (xenotype != null)
		{
			GeneHelpers.ChangeXenotypeFast(pawn, xenotype);
		}
		if (raceThingDef != null)
		{
			pawn.SwapThingDef(raceThingDef, state: true, 200, force: true);
		}
		if (endoGenes != null)
		{
			foreach (GeneDef endoGene in endoGenes)
			{
				pawn.genes.AddGene(endoGene, false);
			}
		}
		if (xenoGenes != null)
		{
			foreach (GeneDef xenoGene in xenoGenes)
			{
				pawn.genes.AddGene(xenoGene, true);
			}
		}
		if (removeGenes != null)
		{
			foreach (GeneDef geneDef in removeGenes)
			{
				Gene val = GenCollection.FirstOrDefault<Gene>(pawn.genes.GenesListForReading, (Predicate<Gene>)((Gene g) => g.def == geneDef));
				if (val != null)
				{
					pawn.genes.RemoveGene(val);
				}
			}
		}
		if (hediffs != null)
		{
			foreach (HediffDef hediff in hediffs)
			{
				pawn.health.AddHediff(hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
		if (hediffsToParts != null)
		{
			HashSet<BodyPartRecord> hashSet = new HashSet<BodyPartRecord>();
			foreach (BodyPartRecord notMissingPart in pawn.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null))
			{
				hashSet.Add(notMissingPart);
			}
			HashSet<BodyPartRecord> partsToConsider = hashSet;
			foreach (var (hediffDef, targetPart) in hediffsToParts.Select((HediffToBodypart h) => (hediff: h.hediff, bodyparts: h.bodyparts)))
			{
				hediffDef.TryAddToAllMatchingParts(pawn, targetPart, partsToConsider);
			}
		}
		if (removeHediffs != null)
		{
			foreach (HediffDef removeHediff in removeHediffs)
			{
				removeHediff.TryRemoveAllOfType(pawn);
			}
		}
		if (addTraits != null)
		{
			foreach (TraitDef addTrait in addTraits)
			{
				pawn.story.traits.GainTrait(new Trait(addTrait, 0, false), false);
			}
		}
		if (removeTraits != null)
		{
			foreach (TraitDef traitDef in removeTraits)
			{
				Trait val2 = GenCollection.FirstOrDefault<Trait>(pawn.story.traits.allTraits, (Predicate<Trait>)((Trait t) => t.def == traitDef));
				if (val2 != null)
				{
					pawn.story.traits.RemoveTrait(val2, false);
				}
			}
		}
		if (fakeXenotype != null)
		{
			pawn.genes.SetXenotypeDirect(fakeXenotype);
		}
	}

	public float GetMorphWeight()
	{
		float num = morphWeight;
		if (xenotype != null)
		{
			num += xenotype.GetMorphWeight();
		}
		return num;
	}

	public Gender GetPrefferedGender()
	{
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		if (xenotype != null)
		{
			if (!ignoreGender)
			{
				List<DefModExtension> modExtensions = ((Def)xenotype).modExtensions;
				if (modExtensions == null || !GenCollection.Any<DefModExtension>(modExtensions, (Predicate<DefModExtension>)((DefModExtension mx) => mx is XenotypeExtension xenotypeExtension && xenotypeExtension.morphIgnoreGender)))
				{
					_ = xenotype.genes;
					if (preferredGenders == (Gender?)2 || GenCollection.Any<GeneDef>(xenotype.genes, (Predicate<GeneDef>)((GeneDef x) => x == BSDefs.Body_FemaleOnly || ((Def)x).defName == "AG_Female")))
					{
						return (Gender)2;
					}
					if (preferredGenders == (Gender?)1 || GenCollection.Any<GeneDef>(xenotype.genes, (Predicate<GeneDef>)((GeneDef x) => x == BSDefs.Body_MaleOnly || ((Def)x).defName == "AG_Male")))
					{
						return (Gender)1;
					}
					goto IL_0102;
				}
			}
			return (Gender)3;
		}
		goto IL_0102;
		IL_0102:
		return (Gender)0;
	}
}
