using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_Projectile : DefModExtension
{
	public ThingDef projectile;

	public SoundDef soundOnImpact;

	public float forcedMissRadius;

	public ProjectileHitFlags hitFlags = (ProjectileHitFlags)1;

	public List<StatModifier> accuracyStatFactors = new List<StatModifier>();

	public List<StatModifier> accuracyStatOffsets = new List<StatModifier>();
}
