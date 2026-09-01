using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Planet;

public class CaravanArrivalAction_AttackMovingBase : CaravanArrivalAction_MovingBase
{
	public override string Label => TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("AttackSettlement", NamedArgument.op_Implicit(((WorldObject)movingBase).Label)));

	public override string ReportString => TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CaravanAttacking", NamedArgument.op_Implicit(((WorldObject)movingBase).Label)));

	public CaravanArrivalAction_AttackMovingBase()
	{
	}

	public CaravanArrivalAction_AttackMovingBase(MovingBase movingBase)
	{
		base.movingBase = movingBase;
	}

	public override FloatMenuAcceptanceReport StillValid(Caravan caravan, PlanetTile destinationTile)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		return FloatMenuAcceptanceReport.op_Implicit(FloatMenuAcceptanceReport.op_Implicit(base.StillValid(caravan, destinationTile)) && FloatMenuAcceptanceReport.op_Implicit(CanAttack(caravan, movingBase)));
	}

	public override void Arrived(Caravan caravan)
	{
		movingBase.Attack(caravan);
	}

	public static FloatMenuAcceptanceReport CanAttack(Caravan caravan, MovingBase movingBase)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		if (movingBase == null || !((WorldObject)movingBase).Spawned || !movingBase.Attackable)
		{
			return FloatMenuAcceptanceReport.op_Implicit(false);
		}
		return FloatMenuAcceptanceReport.op_Implicit(true);
	}

	public static IEnumerable<FloatMenuOption> GetFloatMenuOptions(Caravan caravan, MovingBase movingBase)
	{
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		return CaravanArrivalActionUtility.GetFloatMenuOptions<CaravanArrivalAction>((Func<FloatMenuAcceptanceReport>)(() => CanAttack(caravan, movingBase)), (Func<CaravanArrivalAction>)(() => CaravanArrivalAction_MovingBase.CreateCaravanArrivalAction((CaravanArrivalAction)(object)new CaravanArrivalAction_AttackMovingBase(movingBase), caravan, movingBase)), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("AttackSettlement", NamedArgument.op_Implicit(((WorldObject)movingBase).Label))), caravan, ((WorldObject)movingBase).Tile, (WorldObject)(object)movingBase, FactionUtility.AllyOrNeutralTo(((WorldObject)movingBase).Faction, Faction.OfPlayer) ? ((Action<Action>)delegate(Action action)
		{
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_008a: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			TaggedString val = (GenText.NullOrEmpty(movingBase.def.attackConfirmationMessage) ? TranslatorFormattedStringExtensions.Translate("ConfirmAttackFriendlyFaction", NamedArgument.op_Implicit(((WorldObject)movingBase).LabelCap), NamedArgument.op_Implicit(((WorldObject)movingBase).Faction.Name)) : GrammarResolverSimpleStringExtensions.Formatted(movingBase.def.attackConfirmationMessage, NamedArgument.op_Implicit(((WorldObject)movingBase).LabelCap), NamedArgument.op_Implicit(((WorldObject)movingBase).Faction.Name)));
			Find.WindowStack.Add((Window)(object)Dialog_MessageBox.CreateConfirmation(val, (Action)delegate
			{
				action();
			}, false, (string)null, (WindowLayer)1));
		}) : null);
	}
}
