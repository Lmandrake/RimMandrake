using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public class WeaponTraitDefExtension : DefModExtension
{
	public ThingDef projectileOverride;

	public Dictionary<ThingDef, ThingDef> projectileOverrides;

	public bool lowPreferenceProjectileOverride;

	public SoundDef soundOverride;

	public SoundDef meleeSoundOverride;

	public DamageDef meleeDamageOverride;

	public Dictionary<ThingDef, GraphicData> graphicOverrides;

	public float graphicOverridePriority = 100f;

	public AbilityDef abilityToAdd;

	public HediffDef killHediff;

	public float killHediffSeverity = 1f;

	public float sizeMultiplier = 1f;

	public bool randomprojectiles;

	public bool refreshMaxHitPointsStat;

	public List<ConditionalStatAffecter> conditionalStatAffecters;

	public AbilityWithChargesDetails abilityWithCharges;

	public List<VerbProperties> verbsOverride;

	public Dictionary<ThingDef, List<VerbProperties>> verbsOverrides;

	public FloatRange coolDownRange = FloatRange.Zero;

	public List<float> burstShotCountRange;

	public int limitedUses;

	public List<FactionRelationImpacts> factionRelationImpacts;

	public bool drawDuplicate;
}
