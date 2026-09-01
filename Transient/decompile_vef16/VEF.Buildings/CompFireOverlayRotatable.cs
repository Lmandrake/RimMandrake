using LudeonTK;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

[StaticConstructorOnStartup]
public class CompFireOverlayRotatable : CompFireOverlayBase
{
	protected CompRefuelable refuelableComp;

	public Graphic cachedGraphic;

	[TweakValue("0M", -1f, 1f)]
	public static float yOffset;

	[TweakValue("0M", -1f, 1f)]
	public static float xOffset;

	[TweakValue("0M", -1f, 1f)]
	public static float zOffset;

	public Graphic FireGraphic
	{
		get
		{
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			if (cachedGraphic == null)
			{
				cachedGraphic = GraphicDatabase.Get<Graphic_Flicker>(Props.texPath, ShaderDatabase.TransparentPostLight, Props.size, Props.color);
			}
			return cachedGraphic;
		}
	}

	public CompProperties_FireOverlayRotatable Props => (CompProperties_FireOverlayRotatable)(object)((ThingComp)this).props;

	public override void PostDraw()
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0100: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0163: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostDraw();
		if (refuelableComp == null || refuelableComp.HasFuel)
		{
			Vector3 val = ((Thing)((ThingComp)this).parent).DrawPos;
			Rot4 rotation = ((Thing)((ThingComp)this).parent).Rotation;
			switch (((Rot4)(ref rotation)).AsByte)
			{
			case 0:
			{
				Vector3 val5 = val;
				rotation = ((Thing)((ThingComp)this).parent).Rotation;
				val = val5 + Quaternion.Euler(0f, ((Rot4)(ref rotation)).AsAngle, 0f) * Props.northOffset;
				break;
			}
			case 1:
			{
				Vector3 val4 = val;
				rotation = ((Thing)((ThingComp)this).parent).Rotation;
				val = val4 + Quaternion.Euler(0f, ((Rot4)(ref rotation)).AsAngle, 0f) * Props.eastOffset;
				break;
			}
			case 2:
			{
				Vector3 val3 = val;
				rotation = ((Thing)((ThingComp)this).parent).Rotation;
				val = val3 + Quaternion.Euler(0f, ((Rot4)(ref rotation)).AsAngle, 0f) * Props.southOffset;
				break;
			}
			case 3:
			{
				Vector3 val2 = val;
				rotation = ((Thing)((ThingComp)this).parent).Rotation;
				val = val2 + Quaternion.Euler(0f, ((Rot4)(ref rotation)).AsAngle, 0f) * Props.westOffset;
				break;
			}
			}
			val.y += 0.05f;
			FireGraphic.Draw(val, ((Thing)((ThingComp)this).parent).Rotation, (Thing)(object)((ThingComp)this).parent, 0f);
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		refuelableComp = ((ThingComp)this).parent.GetComp<CompRefuelable>();
	}

	public override void CompTick()
	{
		if ((refuelableComp == null || refuelableComp.HasFuel) && base.startedGrowingAtTick < 0)
		{
			base.startedGrowingAtTick = GenTicks.TicksAbs;
		}
	}
}
