using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class HediffComp_CorpseDecayer : HediffComp
{
	public bool flagOnce;

	public HediffCompProperties_CorpseDecayer Props => (HediffCompProperties_CorpseDecayer)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_0233: Unknown result type (might be due to invalid IL or missing references)
		//IL_025e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_020c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0218: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		Pawn pawn = ((HediffComp)this).Pawn;
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.tickInterval, delta) || ((Thing)pawn).Map == null)
		{
			return;
		}
		CellRect val = GenAdj.OccupiedRect(((Thing)pawn).Position, ((Thing)pawn).Rotation, IntVec2.One);
		val = ((CellRect)(ref val)).ExpandedBy(Props.radius);
		IntVec3 val4 = default(IntVec3);
		foreach (IntVec3 cell in ((CellRect)(ref val)).Cells)
		{
			if (GenGrid.InBounds(cell, ((Thing)pawn).Map))
			{
				foreach (Thing item in new HashSet<Thing>(GridsUtility.GetThingList(cell, ((Thing)pawn).Map)))
				{
					Corpse val2 = (Corpse)(object)((item is Corpse) ? item : null);
					if (val2 == null || !((Thing)val2.InnerPawn).def.race.IsFlesh)
					{
						continue;
					}
					((Thing)val2).HitPoints = ((Thing)val2).HitPoints - 5;
					if (pawn?.needs?.food != null)
					{
						Need_Food food = pawn.needs.food;
						((Need)food).CurLevel = ((Need)food).CurLevel + Props.nutritionGained;
					}
					if (ModLister.HasActiveModWithName("Alpha Animals") && ((Thing)pawn).Faction == Faction.OfPlayer && ((Thing)val2.InnerPawn).def.race.Humanlike)
					{
						pawn.health.AddHediff(HediffDef.Named("AA_CorpseFeast"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
					}
					CompRottable val3 = ThingCompUtility.TryGetComp<CompRottable>((Thing)(object)val2);
					if ((int)val3.Stage == 0)
					{
						val3.RotProgress += 100000f;
					}
					if (((Thing)val2).HitPoints < 0)
					{
						((Thing)val2).Destroy((DestroyMode)0);
						for (int i = 0; i < 20; i++)
						{
							CellFinder.TryFindRandomReachableNearbyCell(((Thing)pawn).Position, ((Thing)pawn).Map, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val4, 999999);
							FilthMaker.TryMakeFilth(val4, ((Thing)pawn).Map, ThingDefOf.Filth_CorpseBile, GenText.LabelIndefinite(pawn), 1, (FilthSourceFlags)0);
							SoundStarter.PlayOneShot(SoundDef.Named(Props.corpseSound), SoundInfo.op_Implicit(new TargetInfo(((Thing)pawn).Position, ((Thing)pawn).Map, false)));
						}
					}
					FilthMaker.TryMakeFilth(cell, ((Thing)pawn).Map, ThingDefOf.Filth_CorpseBile, GenText.LabelIndefinite(pawn), 1, (FilthSourceFlags)0);
					if (Props.causeThoughtNearby)
					{
						foreach (Thing item2 in GenRadial.RadialDistinctThingsAround(((Thing)pawn).Position, ((Thing)pawn).Map, (float)Props.radiusForThought, true))
						{
							Pawn val5 = (Pawn)(object)((item2 is Pawn) ? item2 : null);
							if (val5 != null && val5.needs?.mood?.thoughts != null && !WildManUtility.AnimalOrWildMan(val5) && val5.RaceProps.IsFlesh && val5 != pawn && !val5.Dead && !val5.Downed && StatExtension.GetStatValue((Thing)(object)val5, StatDefOf.PsychicSensitivity, true, -1) > 0f)
							{
								pawn.needs.mood.thoughts.memories.TryGainMemory(Props.thought, (Pawn)null, (Precept)null);
							}
						}
					}
					flagOnce = true;
				}
			}
			if (flagOnce)
			{
				flagOnce = false;
				break;
			}
		}
	}
}
