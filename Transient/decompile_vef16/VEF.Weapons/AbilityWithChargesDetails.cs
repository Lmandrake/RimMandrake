using RimWorld;
using Verse;

namespace VEF.Weapons;

public class AbilityWithChargesDetails
{
	public AbilityDef abilityDef;

	public int maxCharges;

	public ThingDef ammoDef;

	public int ammoCountPerCharge;

	public int baseReloadTicks = 60;

	public SoundDef soundReload;

	public string chargeNoun = "charge";

	public string cooldownGerund = "on cooldown";

	public NamedArgument ChargeNounArgument => NamedArgumentUtility.Named((object)chargeNoun, "CHARGENOUN");
}
