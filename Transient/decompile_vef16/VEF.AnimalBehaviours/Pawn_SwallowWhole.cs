using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class Pawn_SwallowWhole : Pawn, IThingHolder
{
	public ThingOwner innerContainer;

	protected bool contentsKnown;

	public int tickCounter;

	private CompSwallowWhole comp;

	public CompSwallowWhole Comp
	{
		get
		{
			if (comp != null)
			{
				return comp;
			}
			comp = ThingCompUtility.TryGetComp<CompSwallowWhole>((Thing)(object)this);
			return comp;
		}
	}

	public Pawn_SwallowWhole()
	{
		innerContainer = (ThingOwner)(object)new ThingOwner<Thing>((IThingHolder)(object)this, false, (LookMode)2, true);
		comp = Comp;
	}

	public override void ExposeData()
	{
		((Pawn)this).ExposeData();
		Scribe_Deep.Look<ThingOwner>(ref innerContainer, "innerContainer", new object[1] { this });
	}

	public ThingOwner GetDirectlyHeldThings()
	{
		return innerContainer;
	}

	public void GetChildHolders(List<IThingHolder> outChildren)
	{
		ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, (IList<Thing>)GetDirectlyHeldThings());
	}

	public virtual void EjectContents()
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).Map != null)
		{
			innerContainer.TryDropAll(((Thing)this).Position, ((Thing)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, true);
		}
	}

	public void DestroyContents()
	{
		if (innerContainer != null && innerContainer.Any)
		{
			innerContainer.ClearAndDestroyContents((DestroyMode)0);
		}
	}

	public override void Destroy(DestroyMode mode = 0)
	{
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).Map != null && Comp.Props.createFilthWhenKilled)
		{
			EjectContents();
			IntVec3 val = default(IntVec3);
			for (int i = 0; i < 20; i++)
			{
				CellFinder.TryFindRandomReachableNearbyCell(((Thing)this).Position, ((Thing)this).Map, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val, 999999);
				FilthMaker.TryMakeFilth(val, ((Thing)this).Map, Comp.Props.filthToMake, 1, (FilthSourceFlags)0, true);
			}
			if (Comp.Props.playSoundWhenKilled)
			{
				SoundStarter.PlayOneShot(SoundDef.Named(Comp.Props.soundToPlay), SoundInfo.op_Implicit(new TargetInfo(((Thing)this).Position, ((Thing)this).Map, false)));
			}
		}
		((Pawn)this).Destroy(mode);
	}

	public override void Kill(DamageInfo? dinfo, Hediff exactCulprit = null)
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).Map != null && Comp.Props.createFilthWhenKilled)
		{
			EjectContents();
			IntVec3 val = default(IntVec3);
			for (int i = 0; i < 20; i++)
			{
				CellFinder.TryFindRandomReachableNearbyCell(((Thing)this).Position, ((Thing)this).Map, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val, 999999);
				FilthMaker.TryMakeFilth(val, ((Thing)this).Map, Comp.Props.filthToMake, 1, (FilthSourceFlags)0, true);
			}
			if (Comp.Props.playSoundWhenKilled)
			{
				SoundStarter.PlayOneShot(SoundDef.Named(Comp.Props.soundToPlay), SoundInfo.op_Implicit(new TargetInfo(((Thing)this).Position, ((Thing)this).Map, false)));
			}
		}
		((Pawn)this).Kill(dinfo, exactCulprit);
	}

	public virtual bool Accepts(Thing thing)
	{
		return innerContainer.CanAcceptAnyOf(thing, true);
	}

	public virtual bool TryAcceptThing(Thing thing, bool allowSpecialEffects = true)
	{
		if (!Accepts(thing))
		{
			return false;
		}
		bool flag;
		if (thing.holdingOwner != null)
		{
			thing.holdingOwner.Remove(thing);
			innerContainer.TryAdd(thing, thing.stackCount, false);
			flag = true;
		}
		else
		{
			flag = innerContainer.TryAdd(thing, true);
		}
		if (flag)
		{
			if (thing.Faction != null && thing.Faction.IsPlayer)
			{
				contentsKnown = true;
			}
			return true;
		}
		return false;
	}

	public override void TickRare()
	{
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		((Pawn)this).TickRare();
		if (innerContainer.Count < Comp.Props.stomachCapacity)
		{
			return;
		}
		tickCounter++;
		if (tickCounter <= Comp.Props.digestionPeriod)
		{
			return;
		}
		foreach (Thing item in (IEnumerable<Thing>)innerContainer)
		{
			Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
			if (val != null)
			{
				if (!val.Dead)
				{
					((Thing)val).Kill((DamageInfo?)null, (Hediff)null);
				}
				CompRottable val2 = ThingCompUtility.TryGetComp<CompRottable>((Thing)(object)val.Corpse);
				if (val2 != null && (int)val2.Stage == 0)
				{
					val2.RotProgress += 100000000f;
				}
			}
		}
		EjectContents();
		tickCounter = 0;
	}

	public override string GetInspectString()
	{
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		string text = "";
		return string.Concat(str1: (innerContainer.Count < Comp.Props.stomachCapacity) ? TaggedString.op_Implicit(text + ("\n" + TranslatorFormattedStringExtensions.Translate("VEF_StomachContents", NamedArgument.op_Implicit(innerContainer.Count)))) : TaggedString.op_Implicit(text + ("\n" + TranslatorFormattedStringExtensions.Translate("VEF_StomachContents", NamedArgument.op_Implicit(innerContainer.Count)) + TranslatorFormattedStringExtensions.Translate("VEF_DigestionTime", NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod((Comp.Props.digestionPeriod - tickCounter) * 250, true, false, true, true, false))))), str0: ((Pawn)this).GetInspectString());
	}
}
