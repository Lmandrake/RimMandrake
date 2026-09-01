using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

public class HeavyWeapon : DefModExtension
{
	public List<string> supportedTraits;

	public List<string> supportedArmors;

	public List<string> supportedGenes;

	public string disableOptionLabelKey;

	public int weaponHitPointsDeductionOnShot;

	public bool isHeavy;
}
