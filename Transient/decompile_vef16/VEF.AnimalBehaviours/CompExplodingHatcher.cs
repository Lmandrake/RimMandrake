using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompExplodingHatcher : ThingComp
{
	private float gestateProgress;

	public Pawn hatcheeParent;

	public Pawn otherParent;

	public Faction hatcheeFaction;

	public CompProperties_ExplodingHatcher Props => (CompProperties_ExplodingHatcher)(object)base.props;

	private CompTemperatureRuinable FreezerComp => base.parent.GetComp<CompTemperatureRuinable>();

	public bool TemperatureDamaged
	{
		get
		{
			if (FreezerComp != null)
			{
				return FreezerComp.Ruined;
			}
			return false;
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<float>(ref gestateProgress, "gestateProgress", 0f, false);
		Scribe_References.Look<Pawn>(ref hatcheeParent, "hatcheeParent", false);
		Scribe_References.Look<Pawn>(ref otherParent, "otherParent", false);
		Scribe_References.Look<Faction>(ref hatcheeFaction, "hatcheeFaction", false);
	}

	public override void CompTick()
	{
		if (!TemperatureDamaged)
		{
			float num = 1f / (Props.hatcherDaystoHatch * 60000f);
			gestateProgress += num;
			if (gestateProgress > 1f)
			{
				Hatch();
			}
		}
	}

	public void Hatch()
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_022b: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			PawnGenerationRequest val = default(PawnGenerationRequest);
			((PawnGenerationRequest)(ref val))._002Ector(Props.hatcherPawn, hatcheeFaction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, true, false, false, true, 1f, false, false, true, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false);
			for (int i = 0; i < ((Thing)base.parent).stackCount; i++)
			{
				Pawn val2 = PawnGenerator.GeneratePawn(val);
				if (PawnUtility.TrySpawnHatchedOrBornPawn(val2, (Thing)(object)base.parent, (IntVec3?)null))
				{
					if (val2 != null)
					{
						if (hatcheeParent != null)
						{
							if (val2.playerSettings != null && hatcheeParent.playerSettings != null && ((Thing)hatcheeParent).Faction == hatcheeFaction)
							{
								val2.playerSettings.AreaRestrictionInPawnCurrentMap = hatcheeParent.playerSettings.AreaRestrictionInPawnCurrentMap;
							}
							if (val2.RaceProps.IsFlesh)
							{
								val2.relations.AddDirectRelation(PawnRelationDefOf.Parent, hatcheeParent);
							}
						}
						if (otherParent != null && (hatcheeParent == null || hatcheeParent.gender != otherParent.gender) && val2.RaceProps.IsFlesh)
						{
							val2.relations.AddDirectRelation(PawnRelationDefOf.Parent, otherParent);
						}
						if (((Thing)base.parent).Map != null)
						{
							List<Thing> list = new List<Thing>();
							IReadOnlyList<Pawn> allPawnsSpawned = ((Thing)val2).Map.mapPawns.AllPawnsSpawned;
							for (int j = 0; j < allPawnsSpawned.Count; j++)
							{
								if (allPawnsSpawned[j] != null && ((Def)((Thing)allPawnsSpawned[j]).def).defName == ((Def)((Thing)val2).def).defName)
								{
									list.Add((Thing)(object)allPawnsSpawned[j]);
								}
							}
							Thing item = (Thing)(object)val2;
							list.Add(item);
							if (AnimalBehaviours_Settings.flagExplodingAnimalEggs)
							{
								GenExplosion.DoExplosion(((Thing)base.parent).Position, ((Thing)base.parent).Map, Props.range, DefDatabase<DamageDef>.GetNamed(Props.damageDef, true), (Thing)(object)base.parent, Props.damage, -1f, SoundDef.Named(Props.soundDef), (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, list, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
							}
						}
					}
					if (((Thing)base.parent).Spawned)
					{
						FilthMaker.TryMakeFilth(((Thing)base.parent).Position, ((Thing)base.parent).Map, ThingDefOf.Filth_AmnioticFluid, 1, (FilthSourceFlags)0, true);
					}
				}
				else
				{
					Find.WorldPawns.PassToWorld(val2, (PawnDiscardDecideMode)2);
				}
			}
		}
		finally
		{
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
	}

	public override void PreAbsorbStack(Thing otherStack, int count)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		float num = (float)count / (float)(((Thing)base.parent).stackCount + count);
		float num2 = ((ThingWithComps)otherStack).GetComp<CompExplodingHatcher>().gestateProgress;
		gestateProgress = Mathf.Lerp(gestateProgress, num2, num);
	}

	public override void PostSplitOff(Thing piece)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		CompExplodingHatcher comp = ((ThingWithComps)piece).GetComp<CompExplodingHatcher>();
		comp.gestateProgress = gestateProgress;
		comp.hatcheeParent = hatcheeParent;
		comp.otherParent = otherParent;
		comp.hatcheeFaction = hatcheeFaction;
	}

	public override void PrePreTraded(TradeAction action, Pawn playerNegotiator, ITrader trader)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Invalid comparison between Unknown and I4
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Invalid comparison between Unknown and I4
		((ThingComp)this).PrePreTraded(action, playerNegotiator, trader);
		if ((int)action == 1)
		{
			hatcheeFaction = Faction.OfPlayer;
		}
		else if ((int)action == 2)
		{
			hatcheeFaction = trader.Faction;
		}
	}

	public override void PostPostGeneratedForTrader(TraderKindDef trader, PlanetTile forTile, Faction forFaction)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostPostGeneratedForTrader(trader, forTile, forFaction);
		hatcheeFaction = forFaction;
	}

	public override string CompInspectStringExtra()
	{
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		if (!TemperatureDamaged)
		{
			if (AnimalBehaviours_Settings.flagExplodingAnimalEggs)
			{
				return TaggedString.op_Implicit(Translator.Translate("EggProgress") + ": " + GenText.ToStringPercent(gestateProgress) + "\n" + Translator.Translate("VEF_WarningEggExplodes"));
			}
			return TaggedString.op_Implicit(Translator.Translate("EggProgress") + ": " + GenText.ToStringPercent(gestateProgress));
		}
		return null;
	}
}
