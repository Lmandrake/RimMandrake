using Verse;

namespace VEF.Weapons;

public class CompProperties_LaserCapacitor : CompProperties
{
	public bool Overheats;

	public bool OverheatDestroys = true;

	public float OverheatChance = 0.05f;

	public string OverheatBlastDamageDef = "Burn";

	public int OverheatBlastExtraDamage = 5;

	public float OverheatBlastRadius = 1.5f;

	public float WarmUpReductionPerShot = 0.1f;

	public ThingDef OverheatMoteThrown;

	public float OverheatMoteSize = 0.5f;

	public string UiIconPath = string.Empty;

	public CompProperties_LaserCapacitor()
	{
		base.compClass = typeof(CompLaserCapacitor);
	}
}
