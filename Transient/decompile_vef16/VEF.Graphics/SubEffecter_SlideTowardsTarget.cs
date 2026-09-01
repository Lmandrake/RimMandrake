using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class SubEffecter_SlideTowardsTarget : SubEffecter
{
	public int tick;

	public SubEffecterDef_SlideTowardsTarget Def => (SubEffecterDef_SlideTowardsTarget)(object)base.def;

	private float SlideProgress => (float)tick / (float)Def.ticksToEnd;

	public SubEffecter_SlideTowardsTarget(SubEffecterDef subDef, Effecter parent)
		: base(subDef, parent)
	{
	}

	public override void SubEffectTick(TargetInfo A, TargetInfo B)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		((SubEffecter)this).SubEffectTick(A, B);
		tick++;
		if (Rand.Value < base.def.chancePerTick)
		{
			MakeMote(A, B, -1);
		}
	}

	public override void SubTrigger(TargetInfo A, TargetInfo B, int overrideSpawnTick = -1, bool force = false)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		((SubEffecter)this).SubTrigger(A, B, overrideSpawnTick, force);
		MakeMote(A, B, overrideSpawnTick);
	}

	private void MakeMote(TargetInfo A, TargetInfo B, int overrideSpawnTick)
	{
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_01af: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_022c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_0246: Unknown result type (might be due to invalid IL or missing references)
		//IL_02dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0271: Unknown result type (might be due to invalid IL or missing references)
		//IL_0277: Invalid comparison between Unknown and I4
		//IL_0258: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0307: Unknown result type (might be due to invalid IL or missing references)
		//IL_0321: Unknown result type (might be due to invalid IL or missing references)
		//IL_032f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0331: Unknown result type (might be due to invalid IL or missing references)
		//IL_036f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0284: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ec: Unknown result type (might be due to invalid IL or missing references)
		Map val = ((TargetInfo)(ref A)).Map ?? ((TargetInfo)(ref B)).Map;
		if (val == null || base.def.fleckDef == null)
		{
			return;
		}
		Thing thing = ((TargetInfo)(ref A)).Thing;
		Pawn_EquipmentTracker val2 = ((Pawn)(((thing is Pawn) ? thing : null)?)).equipment;
		Vector3 val3;
		if (!Def.endPointZOverrideByWeapon)
		{
			val3 = Def.endPoint;
		}
		else
		{
			Vector3 endPoint = Def.endPoint;
			float? obj;
			if (val2 == null)
			{
				obj = null;
			}
			else
			{
				ThingWithComps primary = val2.Primary;
				obj = ((primary != null) ? new float?(((Thing)primary).DrawSize.x) : ((float?)null));
			}
			endPoint.z = (obj ?? Def.endPoint.z) * ((FloatRange)(ref Def.endPointFactor)).RandomInRange;
			val3 = endPoint;
		}
		Vector3 val4 = val3;
		IntVec3 val5 = ((TargetInfo)(ref B)).CenterCell - ((TargetInfo)(ref A)).CenterCell;
		float angleFlat = ((IntVec3)(ref val5)).AngleFlat;
		float num;
		if (!Def.ticksToEndOverrideByWeaponWarmup)
		{
			num = SlideProgress;
		}
		else
		{
			float? obj2;
			if (val2 == null)
			{
				obj2 = null;
			}
			else
			{
				CompEquippable primaryEq = val2.PrimaryEq;
				if (primaryEq == null)
				{
					obj2 = null;
				}
				else
				{
					Verb primaryVerb = primaryEq.PrimaryVerb;
					obj2 = ((primaryVerb != null) ? new float?(primaryVerb.WarmupProgress) : ((float?)null));
				}
			}
			num = obj2 ?? SlideProgress;
		}
		float num2 = num;
		if ((num2 >= 1f || num2 <= 0f) ? true : false)
		{
			return;
		}
		num2 = Mathf.Max(((FloatRange)(ref Def.minimumProgress)).RandomInRange, num2);
		Vector3 val6 = Vector3Utility.RotatedBy(val4, angleFlat);
		Vector3 val7 = Vector3.Lerp(((TargetInfo)(ref A)).CenterVector3 + val6 * ((FloatRange)(ref Def.startPointFactor)).RandomInRange, ((TargetInfo)(ref A)).CenterVector3 + val6, num2);
		if (GenView.ShouldSpawnMotesAt(val7, val, base.def.fleckDef.drawOffscreen))
		{
			float velocityAngle = (base.def.fleckUsesAngleForVelocity ? (((FloatRange)(ref base.def.angle)).RandomInRange + angleFlat) : 0f);
			FleckAttachLink invalid = FleckAttachLink.Invalid;
			if (base.def.fleckDef.useAttachLink && (int)((SubEffecter)this).EffectiveSpawnLocType == 0 && ((TargetInfo)(ref A)).IsValid)
			{
				((FleckAttachLink)(ref invalid))._002Ector(A);
			}
			if (base.def.fleckDef.useAttachLink && (int)((SubEffecter)this).EffectiveSpawnLocType == 5 && ((TargetInfo)(ref B)).IsValid)
			{
				((FleckAttachLink)(ref invalid))._002Ector(B);
			}
			Vector3 value = new Vector3(Mathf.Lerp(((FloatRange)(ref Def.scaleXByStart)).RandomInRange, ((FloatRange)(ref Def.scaleXByEnd)).RandomInRange, num2), 1f, Mathf.Lerp(((FloatRange)(ref Def.scaleYByStart)).RandomInRange, ((FloatRange)(ref Def.scaleYByEnd)).RandomInRange, num2)) * (base.parent?.scale ?? 1f);
			val.flecks.CreateFleck(new FleckCreationData
			{
				def = base.def.fleckDef,
				exactScale = value,
				spawnPosition = val7,
				rotationRate = ((FloatRange)(ref base.def.rotationRate)).RandomInRange,
				rotation = ((FloatRange)(ref base.def.rotation)).RandomInRange + angleFlat - 90f,
				instanceColor = ((SubEffecter)this).EffectiveColor,
				velocitySpeed = ((FloatRange)(ref base.def.speed)).RandomInRange,
				velocityAngle = velocityAngle,
				ageTicksOverride = overrideSpawnTick,
				orbitSpeed = (base.def.orbitOrigin ? ((FloatRange)(ref base.def.orbitSpeed)).RandomInRange : 0f),
				orbitSnapStrength = base.def.orbitSnapStrength,
				link = invalid
			});
		}
	}
}
