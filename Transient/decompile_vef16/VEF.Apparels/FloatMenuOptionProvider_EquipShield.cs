using System;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Apparels;

public class FloatMenuOptionProvider_EquipShield : FloatMenuOptionProvider
{
	protected override bool Drafted => true;

	protected override bool Undrafted => true;

	protected override bool Multiselect => false;

	protected override bool AppliesInt(FloatMenuContext context)
	{
		return context.FirstSelectedPawn.equipment != null;
	}

	protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
	{
		return AddShieldFloatMenuOption(context.FirstSelectedPawn, clickedThing, clickedThing);
	}

	public static FloatMenuOption AddShieldFloatMenuOption(Pawn pawn, Thing equipment, Thing owner)
	{
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0120: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Expected O, but got Unknown
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Expected O, but got Unknown
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_018a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c0: Expected O, but got Unknown
		//IL_0228: Unknown result type (might be due to invalid IL or missing references)
		//IL_022d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0200: Unknown result type (might be due to invalid IL or missing references)
		//IL_0217: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Expected O, but got Unknown
		//IL_0307: Unknown result type (might be due to invalid IL or missing references)
		//IL_0318: Unknown result type (might be due to invalid IL or missing references)
		//IL_0328: Expected O, but got Unknown
		//IL_02d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0285: Unknown result type (might be due to invalid IL or missing references)
		//IL_028a: Unknown result type (might be due to invalid IL or missing references)
		if (equipment.IsShield(out var _) && ApparelUtility.HasPartsToWear(pawn, equipment.def))
		{
			string labelShort = ((Entity)equipment).LabelShort;
			if (equipment.def.IsWeapon && pawn.WorkTagIsDisabled((WorkTags)8))
			{
				return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotEquip", NamedArgument.op_Implicit(labelShort)) + " (" + TranslatorFormattedStringExtensions.Translate("IsIncapableOfViolenceLower", NamedArgument.op_Implicit(((Entity)pawn).LabelShort), NamedArgument.op_Implicit((Thing)(object)pawn)) + ")"), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			if (!ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit(equipment), (PathEndMode)3, (Danger)3, false, false, (TraverseMode)0))
			{
				return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotEquip", NamedArgument.op_Implicit(labelShort)) + " (" + Translator.Translate("NoPath") + ")"), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			if (!pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) || !pawn.CanUseShields())
			{
				return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotEquip", NamedArgument.op_Implicit(labelShort)) + " (" + Translator.Translate("Incapable") + ")"), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			if (FireUtility.IsBurning(equipment))
			{
				return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotEquip", NamedArgument.op_Implicit(labelShort)) + " (" + Translator.Translate("BurningLower") + ")"), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.EquipShield", NamedArgument.op_Implicit(labelShort)));
			if (equipment.def.IsRangedWeapon && pawn.story != null && pawn.story.traits.HasTrait(TraitDefOf.Brawler))
			{
				text = TaggedString.op_Implicit(text + " " + Translator.Translate("EquipWarningBrawler"));
			}
			ThingWithComps primary = pawn.equipment.Primary;
			if (primary != null && !((Thing)primary).def.UsableWithShields())
			{
				text += string.Format(" {0}", TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.EquipWarningShieldUnusable", NamedArgument.op_Implicit(((Def)((Thing)primary).def).label)));
			}
			return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(text, (Action)delegate
			{
				//IL_0023: Unknown result type (might be due to invalid IL or missing references)
				//IL_002e: Unknown result type (might be due to invalid IL or missing references)
				//IL_0033: Unknown result type (might be due to invalid IL or missing references)
				//IL_0044: Expected O, but got Unknown
				//IL_004b: Unknown result type (might be due to invalid IL or missing references)
				ForbidUtility.SetForbidden(equipment, false, true);
				pawn.jobs.TryTakeOrderedJob(new Job(VEFDefOf.VFEC_EquipShield, LocalTargetInfo.op_Implicit(owner), LocalTargetInfo.op_Implicit(equipment)), (JobTag?)(JobTag)0, false);
				FleckMaker.Static(owner.DrawPos, owner.MapHeld, FleckDefOf.FeedbackEquip, 1f);
				PlayerKnowledgeDatabase.KnowledgeDemonstrated(ConceptDefOf.EquippingWeapons, (KnowledgeAmount)6);
			}, (MenuOptionPriority)5, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0), pawn, LocalTargetInfo.op_Implicit(owner), "ReservedBy", (ReservationLayerDef)null);
		}
		return null;
	}
}
