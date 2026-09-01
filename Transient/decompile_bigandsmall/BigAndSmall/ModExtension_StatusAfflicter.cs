using Verse;

namespace BigAndSmall;

public class ModExtension_StatusAfflicter : DefModExtension
{
	public HediffDef hediffToAdd;

	public float severity = 0.01f;

	public HediffDef hediffToAddToPart;

	public float severityPart = 0.01f;

	public bool softScaleSeverityByBodySize;

	public bool scaleSeverityByDamage;
}
