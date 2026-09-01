using UnityEngine;
using Verse;

namespace VEF.Apparels;

public class CompProperties_ShieldBubble : CompProperties
{
	public float EnergyShieldEnergyMax;

	public float EnergyShieldRechargeRate;

	public bool chargeFullyWhenMade;

	public float initialChargePct;

	public bool blockRangedAttack = true;

	public bool blockMeleeAttack;

	public bool dontAllowRangedAttack;

	public bool dontAllowMeleeAttack;

	public string shieldTexPath;

	public bool showWhenDrafted;

	public bool showAlways;

	public bool showOnHostiles = true;

	public bool showOnNeutralInCombat;

	public float minShieldSize = 1.5f;

	public float maxShieldSize = 2f;

	public Color shieldColor = Color.white;

	public float EnergyLossPerDamage = 1f;

	public bool disableRotation;

	public SoundDef absorbDamageSound;

	public SoundDef brokenSound;

	public SoundDef resetSound;

	public string tooltipKey;

	public CompProperties_ShieldBubble()
	{
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		base.compClass = typeof(CompShieldBubble);
	}
}
