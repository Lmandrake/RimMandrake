using System.Collections.Generic;
using RimWorld;
using VEF.CacheClearing;
using Verse;

namespace VEF.Genes;

[StaticConstructorOnStartup]
public static class StaticCollectionsClass
{
	public static IDictionary<Thing, ThingDef> meat_gene_pawns;

	public static IDictionary<Thing, ThingDef> leather_gene_pawns;

	public static IDictionary<Thing, List<ThingDef>> defs_treated_as_human_meat;

	public static IDictionary<Thing, List<ThingDef>> defs_treated_as_human_leather;

	public static IDictionary<Thing, ThingDef> bloodtype_gene_pawns;

	public static IDictionary<Thing, ThingDef> bloodsmear_gene_pawns;

	public static IDictionary<Thing, string> bloodIcon_gene_pawns;

	public static IDictionary<Thing, EffecterDef> bloodEffect_gene_pawns;

	public static IDictionary<Thing, FleshTypeDef> woundsFromFleshtype_gene_pawns;

	public static IDictionary<Thing, float> diseaseProgressionFactor_gene_pawns;

	public static IDictionary<Thing, ThingDef> vomitType_gene_pawns;

	public static IDictionary<Thing, EffecterDef> vomitEffect_gene_pawns;

	public static IDictionary<Thing, SkillDef> noSkillLoss_gene_pawns;

	public static IDictionary<Thing, float> skillLossMultiplier_gene_pawns;

	public static HashSet<Pawn> skillDegradation_gene_pawns;

	public static IDictionary<Thing, SkillDef> skillRecreation_gene_pawns;

	[NoCacheClearing]
	public static HashSet<GeneDef> hidden_genes;

	public static IDictionary<Thing, float> pregnancySpeedFactor_gene_pawns;

	public static HashSet<Pawn> swappedgender_gene_pawns;

	public static Dictionary<Thing, ExtendedMoveSpeedFactorByTerrainTag> moveSpeedFactorByTerrainTag_gene_pawns;

	static StaticCollectionsClass()
	{
		meat_gene_pawns = new Dictionary<Thing, ThingDef>();
		leather_gene_pawns = new Dictionary<Thing, ThingDef>();
		defs_treated_as_human_meat = new Dictionary<Thing, List<ThingDef>>();
		defs_treated_as_human_leather = new Dictionary<Thing, List<ThingDef>>();
		bloodtype_gene_pawns = new Dictionary<Thing, ThingDef>();
		bloodsmear_gene_pawns = new Dictionary<Thing, ThingDef>();
		bloodIcon_gene_pawns = new Dictionary<Thing, string>();
		bloodEffect_gene_pawns = new Dictionary<Thing, EffecterDef>();
		woundsFromFleshtype_gene_pawns = new Dictionary<Thing, FleshTypeDef>();
		diseaseProgressionFactor_gene_pawns = new Dictionary<Thing, float>();
		vomitType_gene_pawns = new Dictionary<Thing, ThingDef>();
		vomitEffect_gene_pawns = new Dictionary<Thing, EffecterDef>();
		noSkillLoss_gene_pawns = new Dictionary<Thing, SkillDef>();
		skillLossMultiplier_gene_pawns = new Dictionary<Thing, float>();
		skillDegradation_gene_pawns = new HashSet<Pawn>();
		skillRecreation_gene_pawns = new Dictionary<Thing, SkillDef>();
		hidden_genes = new HashSet<GeneDef>();
		pregnancySpeedFactor_gene_pawns = new Dictionary<Thing, float>();
		swappedgender_gene_pawns = new HashSet<Pawn>();
		moveSpeedFactorByTerrainTag_gene_pawns = new Dictionary<Thing, ExtendedMoveSpeedFactorByTerrainTag>();
		ClearCaches.clearCacheTypes.Add(typeof(StaticCollectionsClass));
		foreach (GeneDef item in DefDatabase<GeneDef>.AllDefsListForReading)
		{
			GeneExtension modExtension = ((Def)item).GetModExtension<GeneExtension>();
			if (modExtension != null && modExtension.hideGene)
			{
				hidden_genes.Add(item);
			}
		}
	}

	public static void AddMeatGenePawnToList(Thing thing, ThingDef thingDef)
	{
		if (!meat_gene_pawns.ContainsKey(thing))
		{
			meat_gene_pawns[thing] = thingDef;
		}
	}

	public static void RemoveMeatGenePawnFromList(Thing thing)
	{
		if (meat_gene_pawns.ContainsKey(thing))
		{
			meat_gene_pawns.Remove(thing);
		}
	}

	public static void AddLeatherGenePawnToList(Thing thing, ThingDef thingDef)
	{
		if (!leather_gene_pawns.ContainsKey(thing))
		{
			leather_gene_pawns[thing] = thingDef;
		}
	}

	public static void RemoveLeatherGenePawnFromList(Thing thing)
	{
		if (leather_gene_pawns.ContainsKey(thing))
		{
			leather_gene_pawns.Remove(thing);
		}
	}

	public static void AddDefsTreatedAsHumanMeatGenePawnToList(Thing thing, List<ThingDef> thingDefs)
	{
		if (!defs_treated_as_human_meat.ContainsKey(thing))
		{
			defs_treated_as_human_meat[thing] = thingDefs;
		}
	}

	public static void RemoveDefsTreatedAsHumanMeatGenePawnFromList(Thing thing)
	{
		if (defs_treated_as_human_meat.ContainsKey(thing))
		{
			defs_treated_as_human_meat.Remove(thing);
		}
	}

	public static void AddDefsTreatedAsHumanLeatherGenePawnToList(Thing thing, List<ThingDef> thingDefs)
	{
		if (!defs_treated_as_human_leather.ContainsKey(thing))
		{
			defs_treated_as_human_leather[thing] = thingDefs;
		}
	}

	public static void RemoveDefsTreatedAsHumanLeatherGenePawnFromList(Thing thing)
	{
		if (defs_treated_as_human_leather.ContainsKey(thing))
		{
			defs_treated_as_human_leather.Remove(thing);
		}
	}

	public static void AddBloodtypeGenePawnToList(Thing thing, ThingDef thingDef)
	{
		if (!bloodtype_gene_pawns.ContainsKey(thing))
		{
			bloodtype_gene_pawns[thing] = thingDef;
		}
	}

	public static void RemoveBloodtypeGenePawnFromList(Thing thing)
	{
		if (bloodtype_gene_pawns.ContainsKey(thing))
		{
			bloodtype_gene_pawns.Remove(thing);
		}
	}

	public static void AddBloodSmearGenePawnToList(Thing thing, ThingDef thingDef)
	{
		if (!bloodsmear_gene_pawns.ContainsKey(thing))
		{
			bloodsmear_gene_pawns[thing] = thingDef;
		}
	}

	public static void RemoveBloodSmearGenePawnFromList(Thing thing)
	{
		if (bloodsmear_gene_pawns.ContainsKey(thing))
		{
			bloodsmear_gene_pawns.Remove(thing);
		}
	}

	public static void AddBloodIconGenePawnToList(Thing thing, string icon)
	{
		if (!bloodIcon_gene_pawns.ContainsKey(thing))
		{
			bloodIcon_gene_pawns[thing] = icon;
		}
	}

	public static void RemoveBloodIconGenePawnFromList(Thing thing)
	{
		if (bloodIcon_gene_pawns.ContainsKey(thing))
		{
			bloodIcon_gene_pawns.Remove(thing);
		}
	}

	public static void AddBloodEffectGenePawnToList(Thing thing, EffecterDef effect)
	{
		if (!bloodEffect_gene_pawns.ContainsKey(thing))
		{
			bloodEffect_gene_pawns[thing] = effect;
		}
	}

	public static void RemoveBloodEffectGenePawnFromList(Thing thing)
	{
		if (bloodEffect_gene_pawns.ContainsKey(thing))
		{
			bloodEffect_gene_pawns.Remove(thing);
		}
	}

	public static void AddWoundsFromFleshtypeGenePawnToList(Thing thing, FleshTypeDef fleshtype)
	{
		if (!woundsFromFleshtype_gene_pawns.ContainsKey(thing))
		{
			woundsFromFleshtype_gene_pawns[thing] = fleshtype;
		}
	}

	public static void RemoveWoundsFromFleshtypeGenePawnFromList(Thing thing)
	{
		if (woundsFromFleshtype_gene_pawns.ContainsKey(thing))
		{
			woundsFromFleshtype_gene_pawns.Remove(thing);
		}
	}

	public static void AddDiseaseProgressionFactorGenePawnToList(Thing thing, float factor)
	{
		if (!diseaseProgressionFactor_gene_pawns.ContainsKey(thing))
		{
			diseaseProgressionFactor_gene_pawns[thing] = factor;
		}
	}

	public static void RemoveDiseaseProgressionFactorGenePawnFromList(Thing thing)
	{
		if (diseaseProgressionFactor_gene_pawns.ContainsKey(thing))
		{
			diseaseProgressionFactor_gene_pawns.Remove(thing);
		}
	}

	public static void AddPregnancySpeedFactorGenePawnToList(Thing thing, float factor)
	{
		if (!pregnancySpeedFactor_gene_pawns.ContainsKey(thing))
		{
			pregnancySpeedFactor_gene_pawns[thing] = factor;
		}
	}

	public static void RemovePregnancySpeedFactorGenePawnFromList(Thing thing)
	{
		if (pregnancySpeedFactor_gene_pawns.ContainsKey(thing))
		{
			pregnancySpeedFactor_gene_pawns.Remove(thing);
		}
	}

	public static void AddVomitTypeGenePawnToList(Thing thing, ThingDef thingDef)
	{
		if (!vomitType_gene_pawns.ContainsKey(thing))
		{
			vomitType_gene_pawns[thing] = thingDef;
		}
	}

	public static void RemoveVomitTypeGenePawnFromList(Thing thing)
	{
		if (vomitType_gene_pawns.ContainsKey(thing))
		{
			vomitType_gene_pawns.Remove(thing);
		}
	}

	public static void AddVomitEffectGenePawnToList(Thing thing, EffecterDef effect)
	{
		if (!vomitEffect_gene_pawns.ContainsKey(thing))
		{
			vomitEffect_gene_pawns[thing] = effect;
		}
	}

	public static void RemoveVomitEffectGenePawnFromList(Thing thing)
	{
		if (vomitEffect_gene_pawns.ContainsKey(thing))
		{
			vomitEffect_gene_pawns.Remove(thing);
		}
	}

	public static void AddNoSkillLossGenePawnToList(Thing thing, SkillDef skill)
	{
		if (!noSkillLoss_gene_pawns.ContainsKey(thing))
		{
			noSkillLoss_gene_pawns[thing] = skill;
		}
	}

	public static void RemoveNoSkillLossGenePawnFromList(Thing thing)
	{
		if (noSkillLoss_gene_pawns.ContainsKey(thing))
		{
			noSkillLoss_gene_pawns.Remove(thing);
		}
	}

	public static void AddSkillLossMultiplierGenePawnToList(Thing thing, float multiplier)
	{
		if (!skillLossMultiplier_gene_pawns.ContainsKey(thing))
		{
			skillLossMultiplier_gene_pawns[thing] = multiplier;
		}
	}

	public static void RemoveSkillLossMultiplierGenePawnFromList(Thing thing)
	{
		if (skillLossMultiplier_gene_pawns.ContainsKey(thing))
		{
			skillLossMultiplier_gene_pawns.Remove(thing);
		}
	}

	public static void AddSkillDegradationGenePawnToList(Pawn pawn)
	{
		if (!skillDegradation_gene_pawns.Contains(pawn))
		{
			skillDegradation_gene_pawns.Add(pawn);
		}
	}

	public static void RemoveSkillDegradationGenePawnFromList(Pawn pawn)
	{
		if (skillDegradation_gene_pawns.Contains(pawn))
		{
			skillDegradation_gene_pawns.Remove(pawn);
		}
	}

	public static void AddSwappedGenderGenePawnToList(Pawn pawn)
	{
		if (!swappedgender_gene_pawns.Contains(pawn))
		{
			swappedgender_gene_pawns.Add(pawn);
		}
	}

	public static void AddSkillRecreationGenePawnToList(Thing thing, SkillDef skill)
	{
		if (!skillRecreation_gene_pawns.ContainsKey(thing))
		{
			skillRecreation_gene_pawns[thing] = skill;
		}
	}

	public static void RemoveSkillRecreationGenePawnFromList(Thing thing)
	{
		if (skillRecreation_gene_pawns.ContainsKey(thing))
		{
			skillRecreation_gene_pawns.Remove(thing);
		}
	}

	public static void AddMoveSpeedFactorByTerrainTag(Thing thing, object effectHolder, Dictionary<string, List<MoveSpeedFactor>> speedFactors)
	{
		if (!moveSpeedFactorByTerrainTag_gene_pawns.TryGetValue(thing, out var value))
		{
			value = (moveSpeedFactorByTerrainTag_gene_pawns[thing] = new ExtendedMoveSpeedFactorByTerrainTag());
		}
		value.Add(effectHolder, speedFactors);
	}

	public static void RemoveMoveSpeedFactorByTerrainTag(Thing thing, object effectHolder)
	{
		if (moveSpeedFactorByTerrainTag_gene_pawns.TryGetValue(thing, out var value))
		{
			value.Remove(effectHolder);
			if (value.Empty)
			{
				moveSpeedFactorByTerrainTag_gene_pawns.Remove(thing);
			}
		}
	}
}
