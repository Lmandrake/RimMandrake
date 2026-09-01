using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Maps;

[StaticConstructorOnStartup]
public static class ActiveTerrainUtility
{
	public static readonly Material NeedsPowerMat;

	static ActiveTerrainUtility()
	{
		NeedsPowerMat = MaterialPool.MatFrom("UI/Overlays/NeedsPower", ShaderDatabase.MetaOverlay);
	}

	public static int HashCodeToMod(this object obj, int mod)
	{
		return Math.Abs(obj.GetHashCode()) % mod;
	}

	public static CompTempControl GetTempControl(this Room room, TempControlType targetType)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		foreach (IntVec3 cell in room.Cells)
		{
			Building firstBuilding = GridsUtility.GetFirstBuilding(cell, room.Map);
			if (firstBuilding != null && ((ThingWithComps)(object)firstBuilding).Powered())
			{
				CompTempControl comp = ((ThingWithComps)firstBuilding).GetComp<CompTempControl>();
				if (comp != null && (comp.AnalyzeType() & targetType) != 0)
				{
					return comp;
				}
			}
		}
		return null;
	}

	public static TempControlType AnalyzeType(this CompTempControl tempControl)
	{
		float energyPerSecond = tempControl.Props.energyPerSecond;
		if (!(energyPerSecond > 0f))
		{
			if (!(energyPerSecond < 0f))
			{
				return TempControlType.None;
			}
			return TempControlType.Cooler;
		}
		return TempControlType.Heater;
	}

	public static TempControlType AnalyzeType(this TerrainComp_TempControl tempControl)
	{
		float energyPerSecond = tempControl.Props.energyPerSecond;
		if (!(energyPerSecond > 0f))
		{
			if (!(energyPerSecond < 0f))
			{
				return TempControlType.None;
			}
			return TempControlType.Cooler;
		}
		return TempControlType.Heater;
	}

	public static bool Powered(this ThingWithComps t)
	{
		CompPowerTrader comp = t.GetComp<CompPowerTrader>();
		if (comp == null)
		{
			return true;
		}
		return comp.PowerOn;
	}

	public static bool Powered(this TerrainInstance t)
	{
		return t.GetComp<TerrainComp_PowerTrader>()?.PowerOn ?? true;
	}

	public static void RenderPulsingNeedsPowerOverlay(IntVec3 loc)
	{
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		Vector3 val = ((IntVec3)(ref loc)).ToVector3ShiftedWithAltitude((AltitudeLayer)39);
		float num = ((float)Math.Sin((Time.realtimeSinceStartup + 397f * (float)loc.HashCodeToMod(37)) * 4f) + 1f) * 0.5f;
		num = 0.3f + num * 0.7f;
		Material val2 = FadedMaterialPool.FadedVersionOf(NeedsPowerMat, num);
		Graphics.DrawMesh(MeshPool.plane08, val, Quaternion.identity, val2, 0);
	}

	public static CompPowerTraderFloor TryFindNearestPowerConduitFloor(IntVec3 center, Map map)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		CellRect val = CellRect.CenteredOn(center, 6);
		Building val2 = null;
		float num = float.MaxValue;
		IntVec3 val3 = default(IntVec3);
		for (int i = val.minZ; i <= val.maxZ; i++)
		{
			for (int j = val.minX; j <= val.maxX; j++)
			{
				((IntVec3)(ref val3))._002Ector(j, 0, i);
				Building transmitter = GridsUtility.GetTransmitter(val3, map);
				if (transmitter != null && ((ThingWithComps)transmitter).GetComp<CompPowerTraderFloor>() != null)
				{
					IntVec3 val4 = val3 - center;
					int lengthHorizontalSquared = ((IntVec3)(ref val4)).LengthHorizontalSquared;
					if (num > (float)lengthHorizontalSquared)
					{
						val2 = transmitter;
						num = lengthHorizontalSquared;
					}
				}
			}
		}
		if (val2 == null)
		{
			return null;
		}
		return ((ThingWithComps)val2).GetComp<CompPowerTraderFloor>();
	}

	public static TerrainInstance MakeTerrainInstance(this ActiveTerrainDef tDef, Map map, IntVec3 loc)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		TerrainInstance obj = (TerrainInstance)Activator.CreateInstance(tDef.terrainInstanceClass);
		obj.def = tDef;
		obj.Map = map;
		obj.Position = loc;
		return obj;
	}
}
