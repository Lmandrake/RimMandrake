using Verse;

namespace VEF.Cooking;

public class Thought_Hediff_Extension : DefModExtension
{
	public HediffDef hediffToAffect;

	public BodyPartDef partToAffect;

	public float percentage = 1f;

	public HediffDef secondHediffToAffect;

	public BodyPartDef secondPartToAffect;

	public float secondPercentage = 1f;

	public bool increaseJoy;

	public float extraJoy;
}
