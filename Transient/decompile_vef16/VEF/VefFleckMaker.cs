using RimWorld;
using UnityEngine;
using Verse;

namespace VEF;

public class VefFleckMaker
{
	public static void MakeLightningGlow(Map map, Vector3 effectPos, float angle, float speed, float scale)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		map.flecks.CreateFleck(new FleckCreationData
		{
			def = FleckDefOf.LightningGlow,
			spawnPosition = effectPos,
			scale = scale,
			ageTicksOverride = -1,
			rotationRate = 0f,
			velocityAngle = angle,
			velocitySpeed = speed,
			solidTimeOverride = 0f
		});
	}

	public static void MakeGaussDistortion(Map map, Vector3 effectPos, float angle, float speed, float scale)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		FleckCreationData dataStatic = FleckMaker.GetDataStatic(effectPos, map, VEFDefOf.VEF_GaussDistortion, scale);
		dataStatic.rotationRate = 90f;
		dataStatic.velocityAngle = angle + Rand.Range(-15f, 15f);
		dataStatic.velocitySpeed = speed;
		map.flecks.CreateFleck(dataStatic);
	}
}
