using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Hediffs;

public class HediffCompProperties_Shield : HediffCompProperties_Draw
{
	public List<DamageDef> breakOn;

	public List<DamageDef> absorb;

	public AttackType absorbAttackType = AttackType.Ranged;

	public AttackType cannotUseAttackType = AttackType.Ranged;

	public float maxEnergy = -1f;

	public float energyPerTick = -1f;

	public int rechargeDelay = -1;

	public float energyLossPerDamage = 0.033f;

	public bool fullOnAdd = true;

	public float energyPctOnReset = 0.2f;

	public SoundDef sustainer;

	public SoundDef soundBroken;

	public SoundDef soundRecharge;

	public SoundDef soundEnded;

	public FleckDef absorbedFleck;

	public FleckDef brokenFleck;

	public bool doDust = true;

	public AttackType damageOnAttack;

	public DamageDef damageType;

	public int damageAmount = -1;

	public float armorPenetration = -1f;

	public bool doRandomRotation = true;

	public override void ResolveReferences(HediffDef parent)
	{
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Expected O, but got Unknown
		((HediffCompProperties)this).ResolveReferences(parent);
		if (breakOn == null)
		{
			breakOn = ((maxEnergy > 0f) ? new List<DamageDef> { DamageDefOf.EMP } : new List<DamageDef>());
		}
		if (graphic == null)
		{
			graphic = new GraphicData
			{
				graphicClass = typeof(Graphic_Single),
				texPath = "Other/ShieldBubble",
				shaderType = ShaderTypeDefOf.Transparent
			};
		}
	}

	public bool Absorbs(DamageDef def)
	{
		if (absorb != null)
		{
			return absorb.Contains(def);
		}
		return true;
	}

	public override void PostLoad()
	{
		base.PostLoad();
		ShieldsSystem.ApplyShieldPatches();
	}
}
