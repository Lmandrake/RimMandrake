using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Hediffs;

public class HediffComp_Shield : HediffComp_Draw
{
	public float energy;

	public bool useEnergy;

	protected int ticksTillReset;

	protected Sustainer sustainer;

	protected Vector3 impactAngleVect;

	public HediffCompProperties_Shield Props => ((HediffComp)this).props as HediffCompProperties_Shield;

	public virtual bool ShieldActive
	{
		get
		{
			if (!(energy > 0f))
			{
				return !useEnergy;
			}
			return true;
		}
	}

	public override void DrawAt(Vector3 drawPos)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		drawPos.y = Altitudes.AltitudeFor((AltitudeLayer)28);
		drawPos += Props.graphic.drawOffset;
		Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(drawPos, Quaternion.AngleAxis(Props.doRandomRotation ? ((float)Rand.Range(0, 360)) : 0f, Vector3.up), new Vector3(Props.graphic.drawSize.x, 1f, Props.graphic.drawSize.y)), Graphic.MatSingleFor((Thing)(object)((HediffComp)this).Pawn), 0);
	}

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		base.CompPostPostAdd(dinfo);
		useEnergy = Props.maxEnergy > 0f;
		if (useEnergy)
		{
			if (Props.fullOnAdd)
			{
				energy = Props.maxEnergy;
			}
			else
			{
				energy = Props.energyPctOnReset * Props.maxEnergy;
			}
		}
		else
		{
			energy = -1f;
		}
	}

	public virtual void PreApplyDamage(ref DamageInfo dinfo, ref bool absorbed)
	{
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		if (absorbed || !ShieldActive)
		{
			return;
		}
		if (Props.breakOn.Contains(((DamageInfo)(ref dinfo)).Def))
		{
			Break();
			return;
		}
		bool flag = false;
		switch (Props.absorbAttackType)
		{
		case AttackType.Melee:
			flag = !((DamageInfo)(ref dinfo)).Def.isRanged;
			break;
		case AttackType.Ranged:
			flag = ((DamageInfo)(ref dinfo)).Def.isRanged || ((DamageInfo)(ref dinfo)).Def.isExplosive;
			break;
		case AttackType.Both:
			flag = true;
			break;
		}
		if (flag && Props.Absorbs(((DamageInfo)(ref dinfo)).Def) && AbsorbDamage(ref dinfo))
		{
			absorbed = true;
			impactAngleVect = Vector3Utility.HorizontalVectorFromAngle(((DamageInfo)(ref dinfo)).Angle);
			Vector3 val = GenThing.TrueCenter((Thing)(object)((HediffComp)this).Pawn) + Vector3Utility.RotatedBy(impactAngleVect, 180f) * 0.5f;
			float num = Mathf.Min(10f, 2f + ((DamageInfo)(ref dinfo)).Amount / 10f);
			if (Props.absorbedFleck != null)
			{
				FleckMaker.Static(val, ((Thing)((HediffComp)this).Pawn).Map, Props.absorbedFleck, num);
			}
			if (Props.doDust)
			{
				int num2 = (int)num;
				for (int i = 0; i < num2; i++)
				{
					FleckMaker.ThrowDustPuff(val, ((Thing)((HediffComp)this).Pawn).Map, Rand.Range(0.8f, 1.2f));
				}
			}
		}
		bool flag2 = false;
		switch (Props.damageOnAttack)
		{
		case AttackType.Melee:
			flag2 = !((DamageInfo)(ref dinfo)).Def.isRanged;
			break;
		case AttackType.Ranged:
			flag2 = ((DamageInfo)(ref dinfo)).Def.isRanged || ((DamageInfo)(ref dinfo)).Def.isExplosive;
			break;
		case AttackType.Both:
			flag2 = true;
			break;
		}
		if (flag2 && ((DamageInfo)(ref dinfo)).Instigator != null)
		{
			ApplyDamage(dinfo);
		}
	}

	protected virtual void ApplyDamage(DamageInfo dinfo)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		((DamageInfo)(ref dinfo)).Instigator.TakeDamage(new DamageInfo(Props.damageType, (float)Props.damageAmount, Props.armorPenetration, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
	}

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<float>(ref energy, "energy", 0f, false);
		Scribe_Values.Look<bool>(ref useEnergy, "useEnergy", false, false);
		Scribe_Values.Look<int>(ref ticksTillReset, "ticksTillReset", 0, false);
	}

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (useEnergy)
		{
			if (ticksTillReset > 0)
			{
				ticksTillReset--;
				if (ticksTillReset <= 0)
				{
					Reset();
				}
			}
			else if (energy <= Props.maxEnergy)
			{
				energy += Props.energyPerTick;
			}
		}
		if (ShieldActive && sustainer == null)
		{
			SoundDef obj = Props.sustainer;
			sustainer = ((obj != null) ? SoundStarter.TrySpawnSustainer(obj, SoundInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn)) : null);
			return;
		}
		Sustainer obj2 = sustainer;
		if (obj2 != null)
		{
			obj2.Maintain();
		}
	}

	protected virtual void Break()
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		energy = 0f;
		Sustainer obj = sustainer;
		if (obj != null)
		{
			obj.End();
		}
		SoundDef soundBroken = Props.soundBroken;
		if (soundBroken != null)
		{
			SoundStarter.PlayOneShot(soundBroken, SoundInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn));
		}
		if (Props.brokenFleck != null)
		{
			FleckMaker.Static(GenThing.TrueCenter((Thing)(object)((HediffComp)this).Pawn), ((Thing)((HediffComp)this).Pawn).Map, Props.brokenFleck, 12f);
		}
		if (Props.doDust)
		{
			for (int i = 0; i < 6; i++)
			{
				FleckMaker.ThrowDustPuff(GenThing.TrueCenter((Thing)(object)((HediffComp)this).Pawn) + Vector3Utility.HorizontalVectorFromAngle((float)Rand.Range(0, 360)) * Rand.Range(0.3f, 0.6f), ((Thing)((HediffComp)this).Pawn).Map, Rand.Range(0.8f, 1.2f));
			}
		}
		ticksTillReset = Props.rechargeDelay;
		if (ticksTillReset <= 0)
		{
			Reset();
		}
	}

	protected virtual bool AbsorbDamage(ref DamageInfo dinfo)
	{
		if (useEnergy)
		{
			float num = ((DamageInfo)(ref dinfo)).Amount * Props.energyLossPerDamage;
			if (num < energy)
			{
				energy -= num;
				((DamageInfo)(ref dinfo)).SetAmount(0f);
				return true;
			}
			Break();
			((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount - energy / Props.energyLossPerDamage);
			return false;
		}
		((DamageInfo)(ref dinfo)).SetAmount(0f);
		return true;
	}

	protected virtual void Reset()
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		ticksTillReset = 0;
		energy = Props.maxEnergy * Props.energyPctOnReset;
		SoundDef soundRecharge = Props.soundRecharge;
		if (soundRecharge != null)
		{
			SoundStarter.PlayOneShot(soundRecharge, SoundInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn));
		}
		if (Props.doDust)
		{
			FleckMaker.ThrowLightningGlow(GenThing.TrueCenter((Thing)(object)((HediffComp)this).Pawn), ((Thing)((HediffComp)this).Pawn).Map, 3f);
		}
	}

	public override void CompPostPostRemoved()
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		Sustainer obj = sustainer;
		if (obj != null)
		{
			obj.End();
		}
		SoundDef soundEnded = Props.soundEnded;
		if (soundEnded != null)
		{
			SoundStarter.PlayOneShot(soundEnded, SoundInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn));
		}
		base.CompPostPostRemoved();
	}

	public virtual bool AllowVerbCast(Verb verb)
	{
		if (Props.cannotUseAttackType == AttackType.None)
		{
			return true;
		}
		if (Props.cannotUseAttackType == AttackType.Both)
		{
			return false;
		}
		if (Props.cannotUseAttackType == AttackType.Melee)
		{
			return !(verb is Verb_MeleeAttack);
		}
		if (Props.cannotUseAttackType == AttackType.Ranged)
		{
			return !(verb is Verb_LaunchProjectile);
		}
		return true;
	}
}
