using RimWorld;
using Verse;

namespace VEF.Plants;

public class BloomingPlantExtension : DefModExtension
{
	public int AgeBeautyModifier;

	public int MaxAgeBeautyModifier;

	public float BloomBeautyModifier;

	public int LeaflessBeauty;

	public int WeededBeauty = -4;

	public Season BloomSeasonStart;

	public int BloomDayStart = 1;

	public Season BloomSeasonStop;

	public int BloomDayEnd = 1;

	public bool CanBloomAgain = true;

	public int BloomTemperatureMin = -250;

	public int BloomTemperatureMax = 999;

	public int DeadlyColdTemperature = -250;

	public int DamageWhenBelowDeadlyTemp = 30;

	public float BloomLightMax = 1f;

	public string bloomGraphicPath;

	public string alternateBloomGraphicPath = "";

	public bool ImmuneToWeeds;

	public bool DisableJoyGiver;

	public bool CantBeExtracted;

	public ThingDef itemProducedWhenBlooming;

	public int longTicksPerItemProduced = 1;

	public int itemProducedAmount = 1;

	public ThingDef filthProducedWhenBlooming;

	public int longTicksPerFilthProduced = 1;

	public IntRange filthProducedAmount = IntRange.One;

	public float filthProducedRadius = 1f;

	public HediffDef hediffWhenBlooming;

	public float hediffRadius = 1f;

	public float hediffSeverity = 1f;

	public bool hediffOnlyAffectsColonists = true;
}
