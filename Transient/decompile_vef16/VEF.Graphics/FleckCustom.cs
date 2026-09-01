using UnityEngine;
using Verse;

namespace VEF.Graphics;

public struct FleckCustom : IFleck
{
	public FleckDef def;

	public FleckDrawPosition position;

	public float exactRotation;

	public Vector3 originalScale;

	public Vector3 exactScale;

	public Color instanceColor;

	public float solidTimeOverride;

	public float ageSecs;

	public int ageTicks;

	public int setupTick;

	public Vector3 spawnPosition;

	public float SolidTime
	{
		get
		{
			if (!(solidTimeOverride < 0f))
			{
				return solidTimeOverride;
			}
			return def.solidTime;
		}
	}

	public Vector3 DrawPos => ((FleckDrawPosition)(ref position)).ExactPosition;

	public float Lifespan => def.fadeInTime + SolidTime + def.fadeOutTime;

	public bool EndOfLife => ageSecs >= Lifespan;

	public float Alpha
	{
		get
		{
			float num = ageSecs;
			if (num <= def.fadeInTime)
			{
				if (def.fadeInTime > 0f)
				{
					return num / def.fadeInTime;
				}
				return 1f;
			}
			if (num <= def.fadeInTime + SolidTime)
			{
				return 1f;
			}
			if (def.fadeOutTime > 0f)
			{
				return 1f - Mathf.InverseLerp(def.fadeInTime + SolidTime, def.fadeInTime + SolidTime + def.fadeOutTime, num);
			}
			return 1f;
		}
	}

	public Vector3 ExactScale => exactScale;

	public Vector3 AddedScale => ExactScale - originalScale;

	public void Setup(FleckCreationData creationData)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
		def = creationData.def;
		exactScale = Vector3.one;
		instanceColor = (Color)(((_003F?)creationData.instanceColor) ?? Color.white);
		solidTimeOverride = creationData.solidTimeOverride ?? (-1f);
		ageSecs = 0f;
		exactScale = (Vector3)(((_003F?)creationData.exactScale) ?? new Vector3(creationData.scale, 1f, creationData.scale));
		originalScale = ExactScale;
		position = new FleckDrawPosition(creationData.spawnPosition, 0f, Vector3.zero, def.unattachedDrawOffset);
		spawnPosition = creationData.spawnPosition;
		exactRotation = creationData.rotation;
		setupTick = Find.TickManager.TicksGame;
		if (creationData.ageTicksOverride != -1)
		{
			ForceSpawnTick(creationData.ageTicksOverride);
		}
	}

	public bool TimeInterval(float deltaTime, Map map)
	{
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		if (EndOfLife)
		{
			return true;
		}
		ageSecs += deltaTime;
		ageTicks++;
		if (def.growthRate != 0f)
		{
			float num = Mathf.Sign(exactScale.x);
			float num2 = Mathf.Sign(exactScale.z);
			exactScale = new Vector3(exactScale.x + num * (def.growthRate * deltaTime), exactScale.y, exactScale.z + num2 * (def.growthRate * deltaTime));
			exactScale.x = ((num > 0f) ? Mathf.Max(exactScale.x, 0.0001f) : Mathf.Min(exactScale.x, -0.0001f));
			exactScale.z = ((num2 > 0f) ? Mathf.Max(exactScale.z, 0.0001f) : Mathf.Min(exactScale.z, -0.0001f));
		}
		if (def.scalers != null)
		{
			CurvedScalerExt.ScaleAtTime(def.scalers, ageSecs);
		}
		return false;
	}

	public void Draw(DrawBatch batch)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		Draw(Altitudes.AltitudeFor(def.altitudeLayer, def.altitudeLayerIncOffset), batch);
	}

	public void Draw(float altitude, DrawBatch batch)
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		position.worldPosition.y = altitude;
		int num = setupTick + ((object)(Vector3)(ref spawnPosition)/*cast due to .constrained prefix*/).GetHashCode();
		((Graphic_Fleck)def.GetGraphicData(num).Graphic).DrawFleck(new FleckDrawData
		{
			alpha = Alpha,
			color = instanceColor,
			drawLayer = 0,
			pos = DrawPos,
			rotation = exactRotation,
			scale = ExactScale,
			ageSecs = ageSecs,
			id = num
		}, batch);
	}

	public void ForceSpawnTick(int tick)
	{
		ageTicks = Find.TickManager.TicksGame - tick;
		ageSecs = GenTicks.TicksToSeconds(ageTicks);
	}

	public Vector3 GetPosition()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		return position.worldPosition;
	}
}
