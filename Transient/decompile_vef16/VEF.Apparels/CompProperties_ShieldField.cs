using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Apparels;

public class CompProperties_ShieldField : CompProperties
{
	public bool activeAlways;

	public float initialEnergyPercentage;

	public int rechargeTicksWhenDepleted;

	public float shortCircuitChancePerEnergyLost;

	public float inactivePowerConsumption;

	public Color shieldColour = Color.white;

	public StatDef rechargeRateStat;

	public StatDef shieldEnergyMaxStat;

	public StatDef shieldRadiusStat;

	public int workingTimeTicks = -1;

	public int cooldownTicks = -1;

	public bool manualActivation;

	public string activationLabelKey;

	public string activationDescKey;

	public string activationIconTexPath;

	public int disarmedByEmpForTicks = -1;

	public SoundDef activeSound;

	public bool toggleable;

	public string toggleIconPath = "UI/ToggleIcon";

	public string toggleLabelKey;

	public string toggleDescKey;

	public EffecterDef reactivateEffect;

	public List<HealthColorPoint> healthColorPoints;

	public CompProperties_ShieldField()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		base.compClass = typeof(CompShieldField);
	}
}
