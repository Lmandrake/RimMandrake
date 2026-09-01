using System;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class TemperatureGenerator : HediffComp
{
	public CompProperties_TempGenerator Props => (CompProperties_TempGenerator)(object)base.props;

	public float AmbientTemperature
	{
		get
		{
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
			//IL_009b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
			if (((Thing)((Hediff)base.parent).pawn).Spawned)
			{
				return GenTemperature.GetTemperatureForCell(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map);
			}
			if (((Thing)((Hediff)base.parent).pawn).ParentHolder != null)
			{
				float result = default(float);
				for (IThingHolder parentHolder = ((Thing)((Hediff)base.parent).pawn).ParentHolder; parentHolder != null; parentHolder = parentHolder.ParentHolder)
				{
					if (ThingOwnerUtility.TryGetFixedTemperature(parentHolder, (Thing)(object)((Hediff)base.parent).pawn, ref result))
					{
						return result;
					}
				}
			}
			if (((Thing)((Hediff)base.parent).pawn).SpawnedOrAnyParentSpawned)
			{
				return GenTemperature.GetTemperatureForCell(((Thing)((Hediff)base.parent).pawn).PositionHeld, ((Thing)((Hediff)base.parent).pawn).MapHeld);
			}
			if (PlanetTile.op_Implicit(((Thing)((Hediff)base.parent).pawn).Tile) >= 0)
			{
				return GenTemperature.GetTemperatureAtTile(((Thing)((Hediff)base.parent).pawn).Tile);
			}
			return 21f;
		}
	}

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_0162: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (Find.TickManager.TicksGame % 250 != 0 || ((HediffComp)this).Pawn == null || !((Thing)((HediffComp)this).Pawn).Spawned || HumanoidPawnScaler.GetCache(((HediffComp)this).Pawn) == null || ((Thing)((HediffComp)this).Pawn).Map == null)
		{
			return;
		}
		if (((HediffComp)this).Pawn != null)
		{
			_ = ((Thing)((HediffComp)this).Pawn).Spawned;
		}
		float ambientTemperature = AmbientTemperature;
		float num = 0f;
		num = ((!(Props.energyPerSecond > 0f)) ? ((ambientTemperature > 20f) ? 1f : Mathf.InverseLerp(-100f, 20f, ambientTemperature)) : ((ambientTemperature < 20f) ? 1f : Mathf.InverseLerp(200f, 20f, ambientTemperature)));
		if ((double)num < 0.1)
		{
			num = 0.1f;
		}
		float num2 = Props.energyPerSecond;
		if (Props.scaleToBodySize)
		{
			num2 = ((!(((Hediff)base.parent).pawn.BodySize < 1f)) ? (num2 * (1f + (((Hediff)base.parent).pawn.BodySize - 1f) * 0.33f)) : (num2 * ((Hediff)base.parent).pawn.BodySize));
		}
		float num3 = num2 * 4.1666665f * num;
		try
		{
			float num4 = GenTemperature.ControlTemperatureTempChange(((Thing)((Hediff)base.parent).pawn).PositionHeld, ((Thing)((Hediff)base.parent).pawn).Map, num3, Props.targetTemperature);
			if (!Mathf.Approximately(num4, 0f))
			{
				Room room = RegionAndRoomQuery.GetRoom((Thing)(object)((Hediff)base.parent).pawn, (RegionType)15);
				room.Temperature += num4;
			}
		}
		catch (Exception ex)
		{
			Log.Warning("Error while controlling temperature: " + ex);
		}
	}
}
