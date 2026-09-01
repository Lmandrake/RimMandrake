using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class CompMakeOtherPawnsFlee : ThingComp
{
	[Serializable]
	[CompilerGenerated]
	private sealed class _003C_003Ec
	{
		public static readonly _003C_003Ec _003C_003E9 = new _003C_003Ec();

		public static RegionEntryPredicate _003C_003E9__3_1;

		internal bool _003CCompTickInterval_003Eb__3_1(Region from, Region reg)
		{
			if (reg.door != null)
			{
				return reg.door.Open;
			}
			return true;
		}
	}

	private static readonly List<Thing> tmpPawns = new List<Thing>();

	public CompProperties_MakeOtherPawnsFlee Props => (CompProperties_MakeOtherPawnsFlee)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Expected O, but got Unknown
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Expected O, but got Unknown
		//IL_012e: Expected O, but got Unknown
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_0187: Unknown result type (might be due to invalid IL or missing references)
		//IL_0189: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.checkingInterval, delta) || ((Thing)base.parent).Map == null)
		{
			return;
		}
		Pawn pawn = default(Pawn);
		ref Pawn reference = ref pawn;
		ThingWithComps parent = base.parent;
		reference = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (pawn.CurJob.def != JobDefOf.AttackMelee && pawn.mindState.mentalStateHandler.CurStateDef != MentalStateDefOf.Manhunter && pawn.mindState.mentalStateHandler.CurStateDef != MentalStateDefOf.ManhunterPermanent)
		{
			return;
		}
		RegionProcessor val2 = default(RegionProcessor);
		foreach (Pawn item in ((Thing)base.parent).Map.mapPawns.AllPawnsSpawned.Where((Pawn x) => Props.pawnkinddefsToAffect.Contains(x.kindDef)).ToList())
		{
			_ = item;
			Region region = RegionAndRoomQuery.GetRegion((Thing)(object)pawn, (RegionType)14);
			if (region == null)
			{
				break;
			}
			object obj = _003C_003Ec._003C_003E9__3_1;
			if (obj == null)
			{
				RegionEntryPredicate val = (Region from, Region reg) => reg.door == null || reg.door.Open;
				_003C_003Ec._003C_003E9__3_1 = val;
				obj = (object)val;
			}
			RegionProcessor obj2 = val2;
			if (obj2 == null)
			{
				RegionProcessor val5 = delegate(Region reg)
				{
					//IL_006e: Unknown result type (might be due to invalid IL or missing references)
					List<Thing> list = reg.ListerThings.ThingsInGroup((ThingRequestGroup)16);
					for (int i = 0; i < list.Count; i++)
					{
						IAttackTarget val3;
						Pawn val4;
						if (list[i] != pawn && (val3 = (IAttackTarget)/*isinst with value type is only supported in some contexts*/) != null && !val3.ThreatDisabled((IAttackTargetSearcher)null) && (val4 = (Pawn)/*isinst with value type is only supported in some contexts*/) != null && (GenHostility.HostileTo((Thing)(object)val4, (Thing)(object)pawn) || val4.RaceProps.Humanlike) && GenSight.LineOfSightToThing(((Thing)pawn).Position, (Thing)(object)val4, ((Thing)pawn).Map, true, (Func<IntVec3, bool>)null))
						{
							tmpPawns.Add((Thing)(object)val4);
						}
					}
					return false;
				};
				RegionProcessor val6 = val5;
				val2 = val5;
				obj2 = val6;
			}
			RegionTraverser.BreadthFirstTraverse(region, (RegionEntryPredicate)obj, obj2, 9, (RegionType)14);
			if (GenCollection.Any<Thing>(tmpPawns))
			{
				IntVec3 fleeDest = CellFinderLoose.GetFleeDest(pawn, tmpPawns, 50f);
				tmpPawns.Clear();
				if (((IntVec3)(ref fleeDest)).IsValid && fleeDest != ((Thing)pawn).Position)
				{
					Job val7 = JobMaker.MakeJob(InternalDefOf.VEF_FleeAndCowerShort, LocalTargetInfo.op_Implicit(fleeDest));
					val7.checkOverrideOnExpire = true;
					val7.expiryInterval = 600;
					pawn.jobs.TryTakeOrderedJob(val7, (JobTag?)(JobTag)0, false);
				}
			}
		}
	}
}
