using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class BeamDraw : ThingWithComps
{
	private Vector3 a;

	private Vector3 b;

	private Matrix4x4 drawMatrix;

	private Material material;

	private ProjectileExtension projectileExt;

	private int ticksRemaining;

	public void Setup(Vector3 origin, Vector3 dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		a = Vector3Utility.Yto0(origin);
		b = Vector3Utility.Yto0(dest);
		Recache();
		ticksRemaining = projectileExt.beamLifetimeTicks;
		CompAffectsSky comp = ((ThingWithComps)this).GetComp<CompAffectsSky>();
		if (comp != null)
		{
			comp.StartFadeInHoldFadeOut(projectileExt.beamSkyFadeInTicks, projectileExt.beakSkyHoldTikcs, projectileExt.beakSkyFadeOutTicks, 1f);
		}
	}

	private void Recache()
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		projectileExt = ((Def)((Thing)this).def).GetModExtension<ProjectileExtension>() ?? new ProjectileExtension();
		ref Matrix4x4 reference = ref drawMatrix;
		Vector3 val = (a + b) / 2f + Vector3.up * ((BuildableDef)((Thing)this).def).Altitude;
		Quaternion val2 = Quaternion.LookRotation(b - a);
		float x = ((Thing)this).def.graphicData.drawSize.x;
		Vector3 val3 = b - a;
		((Matrix4x4)(ref reference)).SetTRS(val, val2, new Vector3(x, 1f, ((Vector3)(ref val3)).magnitude));
		material = MaterialPool.MatFrom(((Thing)this).def.graphicData.texPath, ShaderDatabase.MoteGlow);
	}

	public override void SpawnSetup(Map map, bool respawningAfterLoad)
	{
		((ThingWithComps)this).SpawnSetup(map, respawningAfterLoad);
		if (respawningAfterLoad)
		{
			Recache();
		}
	}

	protected override void Tick()
	{
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		if (ticksRemaining == projectileExt.beamLifetimeTicks)
		{
			if (projectileExt.flashIntensity > 0f)
			{
				FleckMaker.Static(b + Vector3.up * ((BuildableDef)((Thing)this).def).Altitude + Altitudes.AltIncVect / 2f, ((Thing)this).Map, FleckDefOf.ExplosionFlash, projectileExt.flashIntensity);
			}
			if (projectileExt.hitFleck != null)
			{
				FleckMaker.Static(b + Vector3.up * ((BuildableDef)((Thing)this).def).Altitude + Altitudes.AltIncVect, ((Thing)this).Map, projectileExt.hitFleck, 1f);
			}
		}
		ticksRemaining--;
		if (ticksRemaining <= 0)
		{
			((Thing)this).Destroy((DestroyMode)0);
		}
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		Graphics.DrawMesh(MeshPool.plane10, drawMatrix, FadedMaterialPool.FadedVersionOf(material, (float)ticksRemaining / (float)projectileExt.beamLifetimeTicks), 0);
	}

	public override void ExposeData()
	{
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		((ThingWithComps)this).ExposeData();
		Scribe_Values.Look<int>(ref ticksRemaining, "ticksRemaining", 0, false);
		Scribe_Values.Look<Vector3>(ref a, "a", default(Vector3), false);
		Scribe_Values.Look<Vector3>(ref b, "b", default(Vector3), false);
	}
}
