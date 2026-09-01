using RimWorld;
using Verse;

namespace BigAndSmall;

public abstract class CompProperties_AbilityEngluf_Abstract : CompProperties_AbilityEffect
{
	public FloatRange relativeSizeThreshold = new FloatRange(0.35f, 0.8f);

	public float? max;

	public int maxAgeStage = 3;

	public float internalBaseDamage = 10f;

	public float selfDamageMultiplier = 0.2f;

	public DamageDef damageDef;

	public bool alliesAttackBack = true;

	public bool dealsDamage = true;

	public float healPerDay = -1f;

	public float regularHealingMultiplier = -1f;

	public bool healsScars;

	public bool canHealBrain;

	public float bodyPartsRegeneratedPerDay;

	public float GetSizeThreshold(Pawn pawn)
	{
		float nutritionMultiplier = StatWorker_MaxNutritionFromSize.GetNutritionMultiplier(HumanoidPawnScaler.GetCacheUltraSpeed(pawn).scaleMultiplier.linear);
		float num = (StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.MaxNutrition, true, -1) / nutritionMultiplier * StatExtension.GetStatValueAbstract((BuildableDef)(object)((Thing)pawn).def, StatDefOf.MaxNutrition, (ThingDef)null) - 1f) / 4f;
		return ((FloatRange)(ref relativeSizeThreshold)).ClampToRange(((FloatRange)(ref relativeSizeThreshold)).LerpThroughRange(num));
	}
}
