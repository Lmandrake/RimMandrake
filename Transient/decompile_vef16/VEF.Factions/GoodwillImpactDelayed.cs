using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

public class GoodwillImpactDelayed : IExposable
{
	public int impactInTicks;

	public int goodwillImpact;

	public Faction factionToImpact;

	public HistoryEventDef historyEvent;

	public string letterLabel;

	public string letterDesc;

	public string relationInfoKey;

	public LetterDef letterType;

	public bool RemoveAfterImpact = true;

	public virtual void DoImpact()
	{
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		Faction.OfPlayer.TryAffectGoodwillWith(factionToImpact, goodwillImpact, true, true, historyEvent, (GlobalTargetInfo?)null);
		if (!GenText.NullOrEmpty(relationInfoKey))
		{
			letterDesc = TaggedString.op_Implicit(letterDesc + ("\n\n" + TranslatorFormattedStringExtensions.Translate(relationInfoKey, NamedArgumentUtility.Named((object)factionToImpact, "FACTION"), NamedArgument.op_Implicit(Faction.OfPlayer.GoodwillWith(factionToImpact)), NamedArgument.op_Implicit(goodwillImpact))));
		}
		Find.LetterStack.ReceiveLetter(TaggedString.op_Implicit(letterLabel), TaggedString.op_Implicit(letterDesc), letterType, (LookTargets)null, factionToImpact, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
	}

	public void ExposeData()
	{
		Scribe_Values.Look<int>(ref impactInTicks, "impactInTicks", 0, false);
		Scribe_Values.Look<int>(ref goodwillImpact, "goodwillImpact", 0, false);
		Scribe_Values.Look<string>(ref letterLabel, "letterLabel", (string)null, false);
		Scribe_Values.Look<string>(ref letterDesc, "letterDesc", (string)null, false);
		Scribe_Values.Look<string>(ref relationInfoKey, "relationInfoKey", (string)null, false);
		Scribe_References.Look<Faction>(ref factionToImpact, "factionToImpact", false);
		Scribe_Defs.Look<HistoryEventDef>(ref historyEvent, "historyEvent");
		Scribe_Defs.Look<LetterDef>(ref letterType, "letterType");
		Scribe_Values.Look<bool>(ref RemoveAfterImpact, "RemoveAfterImpact", false, false);
	}
}
