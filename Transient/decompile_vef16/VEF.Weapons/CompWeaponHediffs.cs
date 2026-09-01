using System;
using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

public class CompWeaponHediffs : ThingComp
{
	public Pawn wearer;

	public List<Hediff> wearerHediffs = new List<Hediff>();

	public CompProperties_WeaponHediffs Props => base.props as CompProperties_WeaponHediffs;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		AssignHediffs();
	}

	public override void CompTick()
	{
		((ThingComp)this).CompTick();
		AssignHediffs();
	}

	public void AssignHediffs()
	{
		ThingWithComps parent = base.parent;
		if (parent == null)
		{
			return;
		}
		List<HediffDef> hediffs = Props.hediffs;
		IThingHolder parentHolder = ((Thing)parent).ParentHolder;
		Pawn_EquipmentTracker val = (Pawn_EquipmentTracker)(object)((parentHolder is Pawn_EquipmentTracker) ? parentHolder : null);
		if ((val == null || val.pawn != wearer) && wearer != null)
		{
			foreach (Hediff wearerHediff in wearerHediffs)
			{
				wearer.health.hediffSet.hediffs.Remove(wearerHediff);
			}
			wearerHediffs.Clear();
			wearer = null;
		}
		IThingHolder parentHolder2 = ((Thing)parent).ParentHolder;
		Pawn_EquipmentTracker tracker2 = (Pawn_EquipmentTracker)(object)((parentHolder2 is Pawn_EquipmentTracker) ? parentHolder2 : null);
		if (tracker2 == null || tracker2.pawn == null)
		{
			return;
		}
		if (tracker2.pawn == wearer)
		{
			List<Hediff> list = wearerHediffs;
			if (((list != null) ? new bool?(GenCollection.Any<Hediff>(list, (Predicate<Hediff>)((Hediff x) => x?.pawn == tracker2.pawn))) : ((bool?)null)) ?? true)
			{
				return;
			}
		}
		wearerHediffs = new List<Hediff>();
		foreach (HediffDef item in hediffs)
		{
			Hediff val2 = HediffMaker.MakeHediff(item, tracker2.pawn, (BodyPartRecord)null);
			tracker2.pawn.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			wearerHediffs.Add(val2);
		}
		wearer = tracker2.pawn;
	}

	public override void PostExposeData()
	{
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Invalid comparison between Unknown and I4
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Pawn>(ref wearer, ((object)this).GetType()?.ToString() + "_wearer", false);
		Scribe_Collections.Look<Hediff>(ref wearerHediffs, ((object)this).GetType()?.ToString() + "_wearerHediffs", (LookMode)3, Array.Empty<object>());
		if ((int)Scribe.mode == 4)
		{
			AssignHediffs();
		}
	}
}
