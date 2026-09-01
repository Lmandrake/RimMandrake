using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace BigAndSmall;

public class PilotExtension : DefModExtension
{
	public List<XenotypeChance> xenotypeChances = new List<XenotypeChance>();

	public List<PawnKindDef> pilotPawnkind = new List<PawnKindDef>();

	public GeneDef pilotableGene;

	public Hediff pilotableHediff;

	public void GeneratePilot(Pawn pPawn)
	{
		//IL_0347: Unknown result type (might be due to invalid IL or missing references)
		//IL_03dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e8: Expected O, but got Unknown
		Hediff val = pPawn.health.hediffSet.hediffs.Where((Hediff x) => x is Piloted).FirstOrDefault();
		if (val == null)
		{
			if (ModsConfig.BiotechActive && pilotableGene != null)
			{
				pPawn.genes.AddGene(pilotableGene, false);
			}
			Pawn_GeneTracker genes = pPawn.genes;
			foreach (Gene item in (genes != null) ? genes.GenesListForReading : null)
			{
				foreach (PawnExtension item2 in item.def.GetAllPawnExtensionsOnGene())
				{
					HediffDef val2 = item2.applyBodyHediff?.Where(delegate(HediffToBody x)
					{
						List<HediffCompProperties> comps = x.hediff.comps;
						return comps != null && GenCollection.Any<HediffCompProperties>(comps, (Predicate<HediffCompProperties>)((HediffCompProperties x) => x is CompProperties_Piloted));
					})?.FirstOrDefault()?.hediff;
					if (val2 != null)
					{
						val = HediffMaker.MakeHediff(val2, pPawn, (BodyPartRecord)null);
						pPawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
						goto end_IL_0130;
					}
				}
				continue;
				end_IL_0130:
				break;
			}
		}
		if (val == null)
		{
			val = HediffMaker.MakeHediff(DefDatabase<HediffDef>.GetNamed(((Def)pilotableHediff?.def).defName ?? "BS_Piloted", true), pPawn, (BodyPartRecord)null);
			pPawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
		if (val is Piloted piloted)
		{
			Faction faction = ((Thing)pPawn).Faction;
			PawnKindDef val3 = null;
			val3 = ((!GenCollection.Any<PawnKindDef>(pilotPawnkind)) ? GenCollection.RandomElement<PawnKindDef>(from x in ((Thing)pPawn).Faction.def.pawnGroupMakers.SelectMany((PawnGroupMaker x) => x.options)
				select x.kind into x
				where x.isFighter && (GenList.NullOrEmpty<DefModExtension>((IList<DefModExtension>)((Def)x).modExtensions) || !GenCollection.Any<DefModExtension>(((Def)x).modExtensions, (Predicate<DefModExtension>)((DefModExtension x) => x is PilotExtension)))
				select x) : GenCollection.RandomElement<PawnKindDef>((IEnumerable<PawnKindDef>)pilotPawnkind));
			XenotypeDef xenotype = GenCollection.RandomElementByWeight<XenotypeChance>((IEnumerable<XenotypeChance>)xenotypeChances, (Func<XenotypeChance, float>)((XenotypeChance x) => x.chance)).xenotype;
			List<XenotypeDef> list = xenotypeChances.Select((XenotypeChance x) => x.xenotype).ToList();
			PawnKindDef obj = val3;
			List<XenotypeDef> list2 = list;
			XenotypeDef val4 = xenotype;
			Pawn val5 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(obj, faction, (PawnGenerationContext)2, (PlanetTile?)null, true, false, false, false, true, 0f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 0f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, val4, (CustomXenotype)null, list2, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
			if (val5 != null)
			{
				if (val5.equipment.Primary != null && ((Thing)val5.equipment.Primary).def.weaponTags.Contains("BS_GiantWeapon"))
				{
					val5.equipment.Remove(val5.equipment.Primary);
				}
				HumanoidPawnScaler.GetCache(val5, forceRefresh: true);
				if (val5.BodySize > piloted.MaxCapacity)
				{
					TraitDef namedSilentFail = DefDatabase<TraitDef>.GetNamedSilentFail("Dwarfism");
					if (namedSilentFail != null)
					{
						val5.story.traits.GainTrait(new Trait(namedSilentFail, 0, false), false);
					}
				}
				piloted.AddPilot((Thing)(object)val5);
				((Hediff)piloted).pawn.health.Notify_HediffChanged((Hediff)(object)piloted);
			}
			else
			{
				Log.Error("BigAndSmall: Error equipping and adding pilot for " + (object)pPawn.Name);
			}
		}
		else
		{
			Log.Error($"BigAndSmall: Error generating pilotedHediff for {pPawn.Name}. The Pilot Hediff could not be generated");
		}
	}
}
