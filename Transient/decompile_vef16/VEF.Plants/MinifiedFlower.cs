using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Plants;

public class MinifiedFlower : MinifiedThing, IThingHolderTickable, IThingHolder
{
	private int ticksTillDeath;

	public const int InitialTicksTillDeath = 180000;

	public const float DyingYieldPercentage = 0.5f;

	public bool ShouldTickContents => false;

	public int TicksTillDeath => ticksTillDeath;

	public Plant_Blooming InnerFlower => (Plant_Blooming)(object)((MinifiedThing)this).InnerThing;

	public override Graphic Graphic
	{
		get
		{
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
			if (base.cachedGraphic == null)
			{
				base.cachedGraphic = GraphicUtility.ExtractInnerGraphicFor(((MinifiedThing)this).InnerThing.Graphic, ((MinifiedThing)this).InnerThing, (int?)null);
				Vector2 minifiedDrawSize = ((MinifiedThing)this).GetMinifiedDrawSize(((IntVec2)(ref ((MinifiedThing)this).InnerThing.def.size)).ToVector2(), 1.1f);
				Vector2 val = default(Vector2);
				((Vector2)(ref val))._002Ector(minifiedDrawSize.x / (float)((MinifiedThing)this).InnerThing.def.size.x * base.cachedGraphic.drawSize.x, minifiedDrawSize.y / (float)((MinifiedThing)this).InnerThing.def.size.z * base.cachedGraphic.drawSize.y);
				base.cachedGraphic = base.cachedGraphic.GetCopy(val, ShaderTypeDefOf.Cutout.Shader);
			}
			return base.cachedGraphic;
		}
	}

	protected override Graphic LoadCrateFrontGraphic()
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		return GraphicDatabase.Get<Graphic_Single>("Things/Item/Minified/BurlapBag", ShaderDatabase.Cutout, ((MinifiedThing)this).GetMinifiedDrawSize(((IntVec2)(ref ((MinifiedThing)this).InnerThing.def.size)).ToVector2(), 1.1f) * 1.16f, Color.white);
	}

	public override void Destroy(DestroyMode mode = 0)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		if (((MinifiedThing)this).InnerThing == null)
		{
			((MinifiedThing)this).Destroy(mode);
			return;
		}
		Caravan anyParent = ThingOwnerUtility.GetAnyParent<Caravan>((Thing)(object)this);
		IThingHolder parentHolder = ((Thing)this).ParentHolder;
		ActiveTransporterInfo val = (ActiveTransporterInfo)(object)((parentHolder is ActiveTransporterInfo) ? parentHolder : null);
		ThingDef harvestedThingDef = ((MinifiedThing)this).InnerThing.def.plant.harvestedThingDef;
		int num = (int)((float)((Plant)((MinifiedThing)this).InnerThing).YieldNow() * 0.5f);
		List<Thing> list = new List<Thing>();
		while (num > 0)
		{
			int num2 = Mathf.Min(num, harvestedThingDef.stackLimit);
			Thing val2 = ThingMaker.MakeThing(harvestedThingDef, (ThingDef)null);
			val2.stackCount = num2;
			list.Add(val2);
			num -= num2;
		}
		IntVec3 val3 = ((anyParent == null) ? ((Thing)this).PositionHeld : IntVec3.Invalid);
		Map val4 = ((anyParent == null) ? ((Thing)this).MapHeld : null);
		if (((Thing)this).ParentHolder != null)
		{
			((Thing)this).ParentHolder.GetDirectlyHeldThings().Remove((Thing)(object)this);
		}
		((MinifiedThing)this).Destroy(mode);
		if (anyParent != null)
		{
			foreach (Thing item in list)
			{
				anyParent.AddPawnOrItem(item, true);
			}
			return;
		}
		if (val != null)
		{
			foreach (Thing item2 in list)
			{
				val.innerContainer.TryAdd(item2, true);
			}
			return;
		}
		if (val4 == null)
		{
			return;
		}
		foreach (Thing item3 in list)
		{
			GenPlace.TryPlaceThing(item3, val3, val4, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
		}
	}

	public override void PostMake()
	{
		((ThingWithComps)this).PostMake();
		ticksTillDeath = 180000;
	}

	protected override void Tick()
	{
		((MinifiedThing)this).Tick();
		ticksTillDeath--;
		if (ticksTillDeath <= 0)
		{
			((Thing)this).Destroy((DestroyMode)0);
		}
	}

	public override IEnumerable<Gizmo> GetGizmos()
	{
		yield return (Gizmo)(object)new Designator_ReplantFlower();
		if (DebugSettings.ShowDevGizmos)
		{
			Command_Action val = new Command_Action();
			((Command)val).defaultLabel = "DEV: Destroy";
			val.action = delegate
			{
				((Thing)this).Destroy((DestroyMode)0);
			};
			yield return (Gizmo)(object)val;
			Command_Action val2 = new Command_Action();
			((Command)val2).defaultLabel = "DEV: Die in 1 hour";
			val2.action = delegate
			{
				ticksTillDeath = 2500;
			};
			yield return (Gizmo)(object)val2;
			Command_Action val3 = new Command_Action();
			((Command)val3).defaultLabel = "DEV: Die in 1 day";
			val3.action = delegate
			{
				ticksTillDeath = 60000;
			};
			yield return (Gizmo)(object)val3;
		}
	}

	public override string GetInspectString()
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_MinifiedFlowerWillDieIn", NamedArgumentUtility.Named((object)GenDate.ToStringTicksToPeriod(ticksTillDeath, true, false, true, true, false), "time")));
	}

	public override void ExposeData()
	{
		((MinifiedThing)this).ExposeData();
		Scribe_Values.Look<int>(ref ticksTillDeath, "ticksTillDeath", 0, false);
	}
}
