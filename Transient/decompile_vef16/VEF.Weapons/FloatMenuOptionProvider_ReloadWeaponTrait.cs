using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

public class FloatMenuOptionProvider_ReloadWeaponTrait : FloatMenuOptionProvider
{
	protected override bool Drafted => true;

	protected override bool Undrafted => true;

	protected override bool Multiselect => false;

	public override IEnumerable<FloatMenuOption> GetOptionsFor(Thing clickedThing, FloatMenuContext context)
	{
		foreach (CompApplyWeaponTraits comp in GetReloadablesUsingAmmo(context.FirstSelectedPawn, clickedThing))
		{
			string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Reload", NamedArgumentUtility.Named((object)((ThingComp)comp).parent, "GEAR"), NamedArgumentUtility.Named((object)comp.AbilityDetailsForWeapon(comp.GetDetails()).ammoDef, "AMMO")) + " (" + comp.LabelRemaining + ")");
			List<Thing> chosenAmmo;
			if (!ReachabilityUtility.CanReach(context.FirstSelectedPawn, LocalTargetInfo.op_Implicit(clickedThing), (PathEndMode)3, (Danger)3, false, false, (TraverseMode)0))
			{
				string text2 = text + ": ";
				TaggedString val = Translator.Translate("NoPath");
				yield return new FloatMenuOption(TaggedString.op_Implicit(text2 + ((TaggedString)(ref val)).CapitalizeFirst()), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			else if (!comp.NeedsReload())
			{
				yield return new FloatMenuOption(TaggedString.op_Implicit(text + ": " + Translator.Translate("ReloadFull")), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			else if ((chosenAmmo = FindEnoughAmmo(context.FirstSelectedPawn, clickedThing.Position, comp)) == null)
			{
				yield return new FloatMenuOption(TaggedString.op_Implicit(text + ": " + Translator.Translate("ReloadNotEnough")), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			else if (context.FirstSelectedPawn.carryTracker.AvailableStackSpace(comp.AbilityDetailsForWeapon(comp.GetDetails()).ammoDef) < comp.MinAmmoNeeded())
			{
				yield return new FloatMenuOption(TaggedString.op_Implicit(text + ": " + TranslatorFormattedStringExtensions.Translate("ReloadCannotCarryEnough", NamedArgumentUtility.Named((object)comp.AbilityDetailsForWeapon(comp.GetDetails()).ammoDef, "AMMO"))), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			}
			else
			{
				Action action = delegate
				{
					context.FirstSelectedPawn.jobs.TryTakeOrderedJob(JobGiver_ReloadWeaponTrait.MakeReloadJob(comp, chosenAmmo), (JobTag?)(JobTag)0, false);
				};
				yield return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(text, action, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0), context.FirstSelectedPawn, LocalTargetInfo.op_Implicit(clickedThing), "ReservedBy", (ReservationLayerDef)null);
			}
		}
	}

	public static List<Thing> FindEnoughAmmo(Pawn pawn, IntVec3 rootCell, CompApplyWeaponTraits comp)
	{
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		if (comp == null)
		{
			return null;
		}
		IntRange val = default(IntRange);
		((IntRange)(ref val))._002Ector(comp.MinAmmoNeeded(), comp.MaxAmmoNeeded());
		return RefuelWorkGiverUtility.FindEnoughReservableThings(pawn, rootCell, val, (Predicate<Thing>)((Thing t) => t.def == comp.AbilityDetailsForWeapon(comp.GetDetails()).ammoDef));
	}

	private IEnumerable<CompApplyWeaponTraits> GetReloadablesUsingAmmo(Pawn pawn, Thing clickedThing)
	{
		Pawn_EquipmentTracker equipment = pawn.equipment;
		if (((equipment != null) ? equipment.Primary : null) != null)
		{
			CompApplyWeaponTraits comp = pawn.equipment.Primary.GetComp<CompApplyWeaponTraits>();
			if (comp?.AbilityDetailsForWeapon(comp.GetDetails()) != null && clickedThing.def == comp?.AbilityDetailsForWeapon(comp.GetDetails()).ammoDef)
			{
				yield return comp;
			}
		}
	}

	public static CompApplyWeaponTraits FindSomeReloadableComponent(Pawn pawn)
	{
		Pawn_EquipmentTracker equipment = pawn.equipment;
		if (((equipment != null) ? equipment.Primary : null) != null)
		{
			CompApplyWeaponTraits comp = pawn.equipment.Primary.GetComp<CompApplyWeaponTraits>();
			if (comp?.AbilityDetailsForWeapon(comp.GetDetails()) != null && comp.NeedsReload())
			{
				return comp;
			}
		}
		return null;
	}
}
