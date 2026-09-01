using System;
using Verse;

namespace VEF.Pawns;

public class PregnancyApproachDef : Def
{
	public string cancelLabel;

	public string iconPath;

	public CachedTexture icon;

	public float? pregnancyChanceForPartners;

	public float? pregnancyChanceFactorBase;

	public GeneDef requiredGene;

	public bool requireDifferentGender = true;

	public float lovinDurationMultiplier = 1f;

	public bool requireFertility;

	private Type workerClass = typeof(PregnancyApproachWorker);

	private PregnancyApproachWorker worker;

	public PregnancyApproachWorker Worker
	{
		get
		{
			if (worker == null)
			{
				worker = (PregnancyApproachWorker)Activator.CreateInstance(workerClass);
				worker.def = this;
			}
			return worker;
		}
	}

	public override void PostLoad()
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Expected O, but got Unknown
		((Editable)this).PostLoad();
		icon = new CachedTexture(iconPath);
	}
}
