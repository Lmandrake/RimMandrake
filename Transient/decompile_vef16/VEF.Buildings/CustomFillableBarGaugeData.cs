using System;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CustomFillableBarGaugeData
{
	public float margin = 0.15f;

	public bool horizontalBar;

	public bool rotateBarWithBuilding = true;

	public Vector3 centerPositionOffsetNorth = Vector3.zero;

	public Vector3 centerPositionOffsetSouth = Vector3.zero;

	public Vector3 centerPositionOffsetEast = Vector3.zero;

	public Vector3 centerPositionOffsetWest = Vector3.zero;

	public Vector2 sizeNorth = new Vector2(1f, 0.2f);

	public Vector2 sizeSouth = new Vector2(1f, 0.2f);

	public Vector2 sizeEast = new Vector2(1f, 0.2f);

	public Vector2 sizeWest = new Vector2(1f, 0.2f);

	public Color barFilledColor = new Color(0.6f, 0.56f, 0.13f);

	public Color barUnfilledColor = new Color(0.3f, 0.3f, 0.3f);

	public Color? barFullColor;

	private Material barFilledMat;

	private Material barUnfilledMat;

	private Material barFullColorMat;

	public virtual void DrawGauge(Thing parent, float fuelPercentage)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		GenDraw.DrawFillableBar(GetFillableBarRequest(parent, fuelPercentage));
	}

	public virtual FillableBarRequest GetFillableBarRequest(Thing parent, float fuelPercentage)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		FillableBarRequest result = default(FillableBarRequest);
		result.center = parent.DrawPos + Vector3.up * 0.1f + OffsetFor(parent.Rotation);
		result.size = SizeFor(parent.Rotation);
		result.fillPercent = fuelPercentage;
		result.filledMat = ((fuelPercentage >= 1f) ? barFullColorMat : barFilledMat);
		result.unfilledMat = barUnfilledMat;
		result.margin = margin;
		result.rotation = RotationFor(parent.Rotation);
		return result;
	}

	private Vector3 OffsetFor(Rot4 rotation)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		return (Vector3)(((Rot4)(ref rotation)).AsInt switch
		{
			0 => centerPositionOffsetNorth, 
			2 => centerPositionOffsetSouth, 
			1 => centerPositionOffsetEast, 
			3 => centerPositionOffsetWest, 
			_ => Vector3.zero, 
		});
	}

	private Vector2 SizeFor(Rot4 rotation)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		return (Vector2)(((Rot4)(ref rotation)).AsInt switch
		{
			0 => sizeNorth, 
			2 => sizeSouth, 
			1 => sizeEast, 
			3 => sizeWest, 
			_ => new Vector2(1f, 0.2f), 
		});
	}

	private Rot4 RotationFor(Rot4 rotation)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		bool num = horizontalBar;
		bool flag = rotateBarWithBuilding;
		if (!num)
		{
			if (!flag)
			{
				return Rot4.East;
			}
			return ((Rot4)(ref rotation)).Rotated((RotationDirection)1);
		}
		if (!flag)
		{
			return Rot4.North;
		}
		return rotation;
	}

	public virtual void ResolveReferences()
	{
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			barFilledMat = SolidColorMaterials.SimpleSolidColorMaterial(barFilledColor, false);
			barUnfilledMat = SolidColorMaterials.SimpleSolidColorMaterial(barUnfilledColor, false);
			if (barFullColor.HasValue)
			{
				barFullColorMat = SolidColorMaterials.SimpleSolidColorMaterial(barFullColor.Value, false);
			}
			else
			{
				barFullColorMat = barFilledMat;
			}
		});
	}
}
