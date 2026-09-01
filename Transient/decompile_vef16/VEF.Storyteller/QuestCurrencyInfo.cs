using Verse;

namespace VEF.Storyteller;

public class QuestCurrencyInfo : IExposable
{
	public float amount;

	public virtual void Buy(QuestInfo questInfo)
	{
	}

	public virtual string GetCurrencyInfo()
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VSE.CostGoodwill", NamedArgument.op_Implicit(amount)));
	}

	public void ExposeData()
	{
		Scribe_Values.Look<float>(ref amount, "amount", 0f, false);
	}
}
