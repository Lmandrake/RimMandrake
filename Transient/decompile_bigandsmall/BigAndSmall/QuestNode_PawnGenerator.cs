using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace BigAndSmall;

public class QuestNode_PawnGenerator : QuestNode
{
	[NoTranslate]
	public SlateRef<string> storeAs;

	[NoTranslate]
	public SlateRef<string> addToList;

	[NoTranslate]
	public SlateRef<IEnumerable<string>> addToLists;

	public SlateRef<bool> playerFaction;

	public SlateRef<List<XenotypeDef>> forcedXenotypes = SlateRef<List<XenotypeDef>>.op_Implicit((List<XenotypeDef>)null);

	public SlateRef<PawnKindDef> kindDef;

	public SlateRef<Faction> faction;

	public SlateRef<bool> forbidAnyTitle;

	public SlateRef<bool> ensureNonNumericName;

	public SlateRef<List<TraitDef>> forceOneTraitOf;

	public SlateRef<IEnumerable<TraitDef>> forcedTraits;

	public SlateRef<IEnumerable<TraitDef>> prohibitedTraits;

	public SlateRef<Pawn> extraPawnForExtraRelationChance;

	public SlateRef<float> relationWithExtraPawnChanceFactor;

	public SlateRef<bool?> allowAddictions;

	public SlateRef<float> biocodeWeaponChance;

	public SlateRef<float> biocodeApparelChance;

	public SlateRef<bool> mustBeCapableOfViolence;

	public SlateRef<bool> isChild;

	public SlateRef<bool> allowPregnant;

	public SlateRef<Gender?> fixedGender;

	protected override bool TestRunInt(Slate slate)
	{
		return true;
	}

	protected override void RunInt()
	{
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bc: Expected O, but got Unknown
		List<XenotypeDef> value = forcedXenotypes.GetValue(QuestGen.slate);
		XenotypeDef val = ((value != null) ? GenCollection.RandomElement<XenotypeDef>((IEnumerable<XenotypeDef>)value) : null);
		Slate slate = QuestGen.slate;
		Faction val2 = faction.GetValue(slate);
		IEnumerable<TraitDef> value2 = forcedTraits.GetValue(slate);
		List<TraitDef> value3 = forceOneTraitOf.GetValue(slate);
		TraitDef val3 = ((value3 != null) ? GenCollection.RandomElement<TraitDef>((IEnumerable<TraitDef>)value3) : null);
		if (playerFaction.GetValue(slate))
		{
			val2 = Faction.OfPlayer;
		}
		PawnKindDef value4 = kindDef.GetValue(slate);
		Faction obj = val2;
		PlanetTile? val4 = PlanetTile.op_Implicit(-1);
		bool value5 = mustBeCapableOfViolence.GetValue(slate);
		bool value6 = allowPregnant.GetValue(slate);
		bool num = allowAddictions.GetValue(slate) ?? true;
		IEnumerable<TraitDef> enumerable = value2;
		IEnumerable<TraitDef> value7 = prohibitedTraits.GetValue(slate);
		float value8 = biocodeWeaponChance.GetValue(slate);
		float value9 = biocodeApparelChance.GetValue(slate);
		bool value10 = forbidAnyTitle.GetValue(slate);
		float? num2 = 0f;
		float? num3 = null;
		float? num4 = null;
		Gender? value11 = fixedGender.GetValue(slate);
		XenotypeDef val5 = val;
		Pawn val6 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(value4, obj, (PawnGenerationContext)2, val4, false, false, false, true, value5, 1f, false, true, value6, true, num, false, false, false, false, value8, value9, extraPawnForExtraRelationChance.GetValue(slate), relationWithExtraPawnChanceFactor.GetValue(slate), (Predicate<Pawn>)null, (Predicate<Pawn>)null, enumerable, value7, num2, num3, num4, value11, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, value10, false, (List<GeneDef>)null, (List<GeneDef>)null, val5, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
		if (val3 != null && !val6.story.traits.HasTrait(val3))
		{
			val6.story.traits.GainTrait(new Trait(val3, 0, true), false);
		}
		if (ensureNonNumericName.GetValue(slate) && (val6.Name == null || val6.Name.Numerical))
		{
			val6.Name = PawnBioAndNameGenerator.GeneratePawnName(val6, (NameStyle)0, (string)null, false, (XenotypeDef)null);
		}
		if (storeAs.GetValue(slate) != null)
		{
			QuestGen.slate.Set<Pawn>(storeAs.GetValue(slate), val6, false);
		}
		if (addToList.GetValue(slate) != null)
		{
			QuestGenUtility.AddToOrMakeList(QuestGen.slate, addToList.GetValue(slate), (object)val6);
		}
		if (addToLists.GetValue(slate) != null)
		{
			foreach (string item in addToLists.GetValue(slate))
			{
				QuestGenUtility.AddToOrMakeList(QuestGen.slate, item, (object)val6);
			}
		}
		QuestGen.AddToGeneratedPawns(val6);
		if (!WorldPawnsUtility.IsWorldPawn(val6))
		{
			Find.WorldPawns.PassToWorld(val6, (PawnDiscardDecideMode)0);
		}
	}
}
