using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

[HotSwappable]
public class Projectile_TopAttackMissile : Projectile_Explosive
{
	private const float JAVELIN_HEIGHT = 12f;

	private const float JAVELIN_POWER = 3f;

	private const float ROTATION_INTENSITY = 10f;

	private Vector3 LookTowards
	{
		get
		{
			//IL_0082: Unknown result type (might be due to invalid IL or missing references)
			float num = ((Projectile)this).destination.x - ((Projectile)this).origin.x;
			float num2 = ((Projectile)this).destination.z - ((Projectile)this).origin.z;
			float distanceCoveredFraction = ((Projectile)this).DistanceCoveredFraction;
			float num3 = ((distanceCoveredFraction < 0.5f) ? 1f : (-1f));
			float num4 = Mathf.Pow(Mathf.Abs(2f * distanceCoveredFraction - 1f), 2f);
			float num5 = 120f * num3 * num4;
			return new Vector3(num, ((BuildableDef)((Thing)this).def).Altitude, num2 + num5);
		}
	}

	public override Quaternion ExactRotation => Quaternion.LookRotation(LookTowards);

	public override void Launch(Thing launcher, Vector3 origin, LocalTargetInfo usedTarget, LocalTargetInfo intendedTarget, ProjectileHitFlags hitFlags, bool preventFriendlyFire = false, Thing equipment = null, ThingDef targetCoverDef = null)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Launch(launcher, origin, usedTarget, intendedTarget, hitFlags, preventFriendlyFire, equipment, targetCoverDef);
		ThrowDustPuffThick(((Thing)this).DrawPos, ((Thing)this).Map, 3f);
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		float distanceCoveredFraction = ((Projectile)this).DistanceCoveredFraction;
		float num = 1f - Mathf.Pow(Mathf.Abs(2f * distanceCoveredFraction - 1f), 3f);
		float num2 = 12f * num;
		Vector3 val = drawLoc + new Vector3(0f, 0f, num2);
		Graphics.DrawMesh(MeshPool.GridPlane(((Thing)this).def.graphicData.drawSize), val, ((Projectile)this).ExactRotation, ((Projectile)this).DrawMat, 0);
		DrawShadow(drawLoc, num2);
		((ThingWithComps)this).Comps_PostDraw();
	}

	protected override void Tick()
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Tick();
		if (((Thing)this).Map == null)
		{
			return;
		}
		float distanceCoveredFraction = ((Projectile)this).DistanceCoveredFraction;
		float num = 1f - Mathf.Pow(Mathf.Abs(2f * distanceCoveredFraction - 1f), 3f);
		float num2 = 12f * num;
		Vector3 val = ((Projectile)this).ExactPosition + new Vector3(0f, 0f, num2);
		if (distanceCoveredFraction > 0.5f)
		{
			float angle = Vector3.Angle(((Projectile)this).origin, val);
			if (Rand.Chance(0.5f))
			{
				ThrowSmokeTrail(val, ((Thing)this).Map, angle, 1.2f);
			}
			ThrowRocketExhaust(val, ((Thing)this).Map, angle, 0.8f);
		}
	}

	private void DrawShadow(Vector3 drawLoc, float height)
	{
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).def.projectile.shadowSize > 0f)
		{
			float num = Mathf.Lerp(1f, 0.5f, height / 12f);
			Vector3 val = default(Vector3);
			((Vector3)(ref val))._002Ector(((Thing)this).def.projectile.shadowSize * num, 1f, ((Thing)this).def.projectile.shadowSize * num);
			Matrix4x4 val2 = default(Matrix4x4);
			Vector3 val3 = drawLoc;
			val3.y = Altitudes.AltitudeFor((AltitudeLayer)13);
			((Matrix4x4)(ref val2)).SetTRS(val3, Quaternion.identity, val);
			Graphics.DrawMesh(MeshPool.plane10, val2, MaterialPool.MatFrom("Things/Skyfaller/SkyfallerShadowCircle", ShaderDatabase.Transparent), 0);
		}
	}

	public void ThrowSmokeTrail(Vector3 loc, Map map, float angle, float size)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		FleckCreationData dataStatic = FleckMaker.GetDataStatic(loc, map, FleckDefOf.Smoke, size);
		dataStatic.rotationRate = Rand.Range(-30f, 30f);
		dataStatic.velocityAngle = Rand.Range(0, 360);
		dataStatic.velocitySpeed = Rand.Range(0.008f, 0.012f);
		map.flecks.CreateFleck(dataStatic);
	}

	public void ThrowRocketExhaust(Vector3 loc, Map map, float angle, float size)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		FleckCreationData dataStatic = FleckMaker.GetDataStatic(loc, map, FleckDefOf.ShotFlash, size);
		dataStatic.velocityAngle = angle;
		dataStatic.solidTimeOverride = 0.15f;
		dataStatic.velocitySpeed = 0.01f;
		map.flecks.CreateFleck(dataStatic);
	}

	public void ThrowDustPuffThick(Vector3 loc, Map map, float scale)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		FleckCreationData dataStatic = FleckMaker.GetDataStatic(loc, map, FleckDefOf.DustPuffThick, scale);
		dataStatic.rotationRate = Rand.Range(-60, 60);
		dataStatic.velocityAngle = Rand.Range(0, 360);
		dataStatic.velocitySpeed = Rand.Range(0.6f, 0.75f);
		map.flecks.CreateFleck(dataStatic);
	}
}
