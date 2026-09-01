using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ReturningSoulHolder : IExposable
{
	public Pawn pawn;

	public int ticksToReturn = 9999;

	public int attempts;

	public bool corpseReturn;

	public bool addCorpseGenes;

	public bool addCorpseBionics;

	public void ExposeData()
	{
		Scribe_Deep.Look<Pawn>(ref pawn, "pawn", Array.Empty<object>());
		Scribe_Values.Look<int>(ref ticksToReturn, "ticksToReturn", 0, false);
		Scribe_Values.Look<int>(ref attempts, "attempts", 0, false);
		Scribe_Values.Look<bool>(ref corpseReturn, "corpseReturn", false, false);
		Scribe_Values.Look<bool>(ref addCorpseGenes, "addCorpseGenes", false, false);
		Scribe_Values.Look<bool>(ref addCorpseBionics, "addCorpseBionics", false, false);
	}

	public bool Tick(int tickCount)
	{
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		ticksToReturn -= tickCount;
		if (ticksToReturn <= 0)
		{
			bool flag = false;
			foreach (Map item in Find.Maps.Where((Map x) => x.IsPlayerHome))
			{
				flag = TryRessurectFromCorpse(item);
			}
			if (flag)
			{
				return true;
			}
			foreach (Map map in Find.Maps)
			{
				flag = TryRessurectFromCorpse(map);
			}
			if (flag)
			{
				return true;
			}
			ticksToReturn = (int)Rand.Range(0.5f, 5f) * 60000;
			attempts++;
			string text = ((object)pawn.Name).ToString();
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ReturningSoul_Failed", NamedArgument.op_Implicit(text))), MessageTypeDefOf.NegativeEvent, true);
			if (attempts > Rand.Range(1, 6))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ReturningSoul_FailedPermanent", NamedArgument.op_Implicit(text))), MessageTypeDefOf.NegativeEvent, true);
				((Thing)pawn).Destroy((DestroyMode)0);
				return true;
			}
		}
		return false;
	}

	private bool TryRessurectFromCorpse(Map map)
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0261: Unknown result type (might be due to invalid IL or missing references)
		//IL_0294: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ae: Unknown result type (might be due to invalid IL or missing references)
		List<Corpse> list = GenCollection.InRandomOrder<Corpse>(map.listerThings.ThingsInGroup((ThingRequestGroup)8).OfType<Corpse>(), (IList<Corpse>)null).ToList();
		if (((Thing)pawn).Faction != Faction.OfPlayerSilentFail && Faction.OfPlayerSilentFail != null)
		{
			((Thing)pawn).SetFaction(Faction.OfPlayerSilentFail, (Pawn)null);
		}
		if (!corpseReturn)
		{
			IntVec3 val = DropCellFinder.FindRaidDropCenterDistant(map, true, true);
			GenSpawn.Spawn((Thing)(object)pawn, val, map, (WipeMode)0);
			FilthMaker.TryMakeFilth(val, map, ThingDefOf.Filth_Ash, 5, (FilthSourceFlags)0, true);
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ReturningSoul_Success", NamedArgument.op_Implicit(((object)pawn.Name).ToString()))), MessageTypeDefOf.PositiveEvent, true);
			return true;
		}
		foreach (Corpse item in list)
		{
			Pawn innerPawn = item.InnerPawn;
			if (innerPawn == null)
			{
				continue;
			}
			RaceProperties raceProps = innerPawn.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) != true || !item.InnerPawn.RaceProps.IsFlesh || RottableUtility.IsDessicated((Thing)(object)item))
			{
				continue;
			}
			GenSpawn.Spawn((Thing)(object)pawn, ((Thing)item).Position, map, (WipeMode)0);
			pawn.health.hediffSet.hediffs.Clear();
			if (addCorpseBionics)
			{
				foreach (Hediff item2 in item.InnerPawn.health.hediffSet.hediffs.Where((Hediff x) => x.def.spawnThingOnRemoved != null && (x.def.addedPartProps?.betterThanNatural ?? false)))
				{
					BodyPartRecord originalBodyPart = item2.Part;
					BodyPartRecord val2 = pawn.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null).FirstOrDefault((BodyPartRecord x) => ((Def)x.def).label == ((Def)originalBodyPart.def).label || ((Def)x.def).defName == ((Def)originalBodyPart.def).defName);
					if (val2 != null)
					{
						Hediff obj = HediffMaker.MakeHediff(item2.def, pawn, val2);
						Hediff_AddedPart val3 = (Hediff_AddedPart)(object)((obj is Hediff_AddedPart) ? obj : null);
						pawn.health.AddHediff((Hediff)(object)val3, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
					}
				}
			}
			CompPropertiesMimicffect.DoMimic(pawn, item, new List<GeneDef>(1) { BSDefs.BS_ReturningSoul }, spawnGibblets: false, addCorpseGenes);
			FilthMaker.TryMakeFilth(((Thing)pawn).Position, ((Thing)pawn).Map, ThingDefOf.Filth_Ash, 5, (FilthSourceFlags)0, true);
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ReturningSoulCorpse_Success", NamedArgument.op_Implicit(((object)pawn.Name).ToString()), NamedArgument.op_Implicit(((object)item.InnerPawn.Name).ToString()))), MessageTypeDefOf.PositiveEvent, true);
			((Thing)item).Destroy((DestroyMode)0);
			return true;
		}
		return false;
	}
}
