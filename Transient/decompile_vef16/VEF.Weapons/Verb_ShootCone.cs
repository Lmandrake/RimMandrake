using System;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class Verb_ShootCone : Verb_Shoot
{
	private Material lineMat;

	public VerbProps_ShootCone VerbProps => ((Verb)this).verbProps as VerbProps_ShootCone;

	private Material LineMat
	{
		get
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			if ((Object)(object)lineMat == (Object)null)
			{
				lineMat = MaterialPool.MatFrom(GenDraw.LineTexPath, ShaderDatabase.Transparent, Color.white);
			}
			return lineMat;
		}
	}

	public override void DrawHighlight(LocalTargetInfo target)
	{
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		if (((VerbProperties)VerbProps).range <= GenRadial.MaxRadialPatternRadius)
		{
			DrawConeRounded(VerbProps.coneAngle);
		}
		else
		{
			DrawLines();
		}
		if (((LocalTargetInfo)(ref target)).IsValid)
		{
			GenDraw.DrawTargetHighlight(target);
			((Verb)this).DrawHighlightFieldRadiusAroundTarget(target);
		}
	}

	private void DrawLines()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 position = ((Verb)this).Caster.Position;
		Vector3 val = ((IntVec3)(ref position)).ToVector3Shifted();
		Quaternion val2 = Quaternion.Euler(0f, (float)(-VerbProps.coneAngle) / 2f, 0f);
		Quaternion val3 = Quaternion.Euler(0f, (float)VerbProps.coneAngle / 2f, 0f);
		Rot4 rotation = ((Verb)this).Caster.Rotation;
		Vector3 val4 = val + ((Rot4)(ref rotation)).AsQuat * val2 * new Vector3(0f, 0f, ((Verb)this).verbProps.range);
		rotation = ((Verb)this).Caster.Rotation;
		Vector3 val5 = val + ((Rot4)(ref rotation)).AsQuat * val3 * new Vector3(0f, 0f, ((Verb)this).verbProps.range);
		GenDraw.DrawLineBetween(val, val4, Altitudes.AltitudeFor((AltitudeLayer)39), LineMat, 0.5f);
		GenDraw.DrawLineBetween(val, val5, Altitudes.AltitudeFor((AltitudeLayer)39), LineMat, 0.5f);
	}

	private void DrawConeRounded(float angle)
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 pos = ((Verb)this).Caster.Position;
		Rot4 rotation = ((Verb)this).caster.Rotation;
		Func<IntVec3, bool> func = (IntVec3 c) => InCone(c, pos, rotation, angle);
		GenDraw.DrawRadiusRing(pos, ((Verb)this).verbProps.range, Color.white, func);
	}

	public override bool CanHitTarget(LocalTargetInfo targ)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		if (((Verb)this).CanHitTarget(targ))
		{
			return InCone(((LocalTargetInfo)(ref targ)).Cell, ((Verb)this).caster.Position, ((Verb)this).caster.Rotation, VerbProps.coneAngle);
		}
		return false;
	}

	public bool InCone(IntVec3 evaluatedCell, IntVec3 from, Rot4 rotation, float degrees)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		Quaternion val = Quaternion.LookRotation(((IntVec3)(ref evaluatedCell)).ToVector3() - ((IntVec3)(ref from)).ToVector3(), Vector3.up);
		if (GenGeo.AngleDifferenceBetween(((Quaternion)(ref val)).eulerAngles.y, ((Rot4)(ref rotation)).AsAngle) <= degrees / 2f)
		{
			return true;
		}
		return false;
	}
}
