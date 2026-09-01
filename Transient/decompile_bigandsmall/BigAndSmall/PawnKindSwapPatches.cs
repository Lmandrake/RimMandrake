using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class PawnKindSwapPatches
{
	[HarmonyPatch(typeof(QuestNode_Root_WandererJoin_WalkIn), "GeneratePawn")]
	[HarmonyPrefix]
	public static bool GenerateWandererFactionPrefix(ref Pawn __result)
	{
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b8: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			FactionExtension modExtension = ((Def)Faction.OfPlayer.def).GetModExtension<FactionExtension>();
			if (modExtension != null)
			{
				FactionExtension.PawnKindSwap pawnKindSwap = modExtension.pawnKindSwaps.Where((FactionExtension.PawnKindSwap x) => x.eventsToSwapPawnKind.Contains("QuestNode_Root_WandererJoin_WalkIn")).FirstOrDefault();
				if (pawnKindSwap != null)
				{
					Slate slate = QuestGen.slate;
					Gender? val = null;
					PawnKindDef pawnKind = GenCollection.RandomElementByWeight<PawnkindChance>((IEnumerable<PawnkindChance>)pawnKindSwap.pawnKindSet, (Func<PawnkindChance, float>)((PawnkindChance x) => x.chance)).pawnKind;
					if (((Def)pawnKind).defName == "Villager")
					{
						return true;
					}
					Faction val2 = GenCollection.RandomElement<Faction>(Find.FactionManager.AllFactions.Where((Faction x) => x.def == pawnKind.defaultFactionDef));
					object obj;
					if (!pawnKindSwap.forcePawnKindIdeology)
					{
						obj = null;
					}
					else
					{
						FactionIdeosTracker ideos = val2.ideos;
						obj = ((ideos != null) ? ideos.PrimaryIdeo : null);
					}
					Ideo val3 = (Ideo)obj;
					PawnGenerationRequest val4 = default(PawnGenerationRequest);
					if (!slate.TryGet<PawnGenerationRequest>("overridePawnGenParams", ref val4, false))
					{
						((PawnGenerationRequest)(ref val4))._002Ector(pawnKind, val2, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), true, false, false, true, false, 20f, false, true, true, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, val, (string)null, (string)null, (RoyalTitleDef)null, val3, val3 == null, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, true, false, false, -1, 0, false);
					}
					if (Find.Storyteller.difficulty.ChildrenAllowed)
					{
						((PawnGenerationRequest)(ref val4)).AllowedDevelopmentalStages = (DevelopmentalStage)(((PawnGenerationRequest)(ref val4)).AllowedDevelopmentalStages | 4);
					}
					List<XenotypeChance> xenotypeChances = pawnKind.GetXenotypeChances();
					Pawn val5 = PawnGenerator.GeneratePawn(val4);
					if (val5?.genes != null && xenotypeChances != null && xenotypeChances.Count > 0)
					{
						for (int num = val5.genes.Endogenes.Count - 1; num >= 0; num--)
						{
							Gene val6 = val5.genes.Endogenes[num];
							val5.genes.RemoveGene(val6);
						}
						val5.genes.SetXenotype(xenotypeChances?.GetRandomXenotype());
					}
					if (!WorldPawnsUtility.IsWorldPawn(val5))
					{
						Find.WorldPawns.PassToWorld(val5, (PawnDiscardDecideMode)0);
					}
					__result = val5;
				}
				return false;
			}
		}
		catch (Exception ex)
		{
			Log.Error("Error in Override of GenerateWandererFactionPrefix:Using Vanilla Method as a fallback.\n" + ex.Message + "\n" + ex.StackTrace);
		}
		return true;
	}

	[HarmonyPatch(typeof(ThingSetMaker_RefugeePod), "Generate", new Type[]
	{
		typeof(ThingSetMakerParams),
		typeof(List<Thing>)
	})]
	[HarmonyPrefix]
	public static bool GenerateRefugeePodPrefix(ref ThingSetMakerParams parms, ref List<Thing> outThings)
	{
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			Faction ofPlayerSilentFail = Faction.OfPlayerSilentFail;
			if (ofPlayerSilentFail == null)
			{
				return true;
			}
			FactionExtension modExtension = ((Def)ofPlayerSilentFail.def).GetModExtension<FactionExtension>();
			if (modExtension != null)
			{
				FactionExtension.PawnKindSwap pawnKindSwap = modExtension.pawnKindSwaps.Where((FactionExtension.PawnKindSwap x) => x.eventsToSwapPawnKind.Contains("ThingSetMaker_RefugeePod")).FirstOrDefault();
				if (pawnKindSwap != null)
				{
					PawnKindDef pawnKind = GenCollection.RandomElementByWeight<PawnkindChance>((IEnumerable<PawnkindChance>)pawnKindSwap.pawnKindSet, (Func<PawnkindChance, float>)((PawnkindChance x) => x.chance)).pawnKind;
					if (((Def)pawnKind).defName == "SpaceRefugee")
					{
						return true;
					}
					Faction val = GenCollection.RandomElement<Faction>(Find.FactionManager.AllFactions.Where((Faction x) => x.def == pawnKind.defaultFactionDef));
					object obj;
					if (!pawnKindSwap.forcePawnKindIdeology)
					{
						obj = null;
					}
					else
					{
						FactionIdeosTracker ideos = val.ideos;
						obj = ((ideos != null) ? ideos.PrimaryIdeo : null);
					}
					Ideo val2 = (Ideo)obj;
					Faction val3 = DownedRefugeeQuestUtility.GetRandomFactionForRefugee(0.6f);
					if (pawnKindSwap.forcePawnKindIdeology)
					{
						val3 = val;
					}
					PawnKindDef obj2 = pawnKind;
					Faction obj3 = val3;
					PlanetTile? val4 = PlanetTile.op_Implicit(-1);
					Ideo val5 = val2;
					Pawn val6 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(obj2, obj3, (PawnGenerationContext)2, val4, false, false, false, true, false, 20f, false, true, true, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, val5, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
					List<XenotypeChance> xenotypeChances = pawnKind.GetXenotypeChances();
					if (val6?.genes != null && xenotypeChances.Count > 0)
					{
						for (int num = val6.genes.Endogenes.Count - 1; num >= 0; num--)
						{
							Gene val7 = val6.genes.Endogenes[num];
							val6.genes.RemoveGene(val7);
						}
						val6.genes.SetXenotype(GenCollection.RandomElementByWeight<XenotypeChance>((IEnumerable<XenotypeChance>)xenotypeChances, (Func<XenotypeChance, float>)((XenotypeChance x) => x.chance)).xenotype);
					}
					outThings.Add((Thing)(object)val6);
					HealthUtility.DamageUntilDowned(val6, true, (DamageDef)null, (ThingDef)null, (BodyPartGroupDef)null);
					return false;
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error("Error in Override of GenerateRefugeePodPrefix: Using Vanilla Method as a fallback.\n" + ex.Message + "\n" + ex.StackTrace);
		}
		return true;
	}
}
