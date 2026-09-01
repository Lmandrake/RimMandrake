using System;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace VEF.Maps;

public class LordJob_DefendShip : LordJob
{
	private Faction faction;

	private IntVec3 baseCenter;

	public LordJob_DefendShip()
	{
	}

	public LordJob_DefendShip(Faction faction, IntVec3 baseCenter)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		this.faction = faction;
		this.baseCenter = baseCenter;
	}

	public override StateGraph CreateGraph()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Expected O, but got Unknown
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Expected O, but got Unknown
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Expected O, but got Unknown
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Expected O, but got Unknown
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Expected O, but got Unknown
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Expected O, but got Unknown
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Expected O, but got Unknown
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Expected O, but got Unknown
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Expected O, but got Unknown
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Expected O, but got Unknown
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Expected O, but got Unknown
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Expected O, but got Unknown
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Expected O, but got Unknown
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Expected O, but got Unknown
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Expected O, but got Unknown
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_015b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_0164: Unknown result type (might be due to invalid IL or missing references)
		//IL_0177: Unknown result type (might be due to invalid IL or missing references)
		//IL_0181: Expected O, but got Unknown
		//IL_0181: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Expected O, but got Unknown
		StateGraph val = new StateGraph();
		LordToil_DefendBase val3 = (LordToil_DefendBase)(object)(val.StartingToil = (LordToil)new LordToil_DefendBase(baseCenter));
		LordToil_DefendBase val4 = new LordToil_DefendBase(baseCenter);
		val.AddToil((LordToil)(object)val4);
		LordToil_AssaultColony val5 = new LordToil_AssaultColony(true, false);
		((LordToil)val5).useAvoidGrid = true;
		val.AddToil((LordToil)(object)val5);
		Transition val6 = new Transition((LordToil)(object)val3, (LordToil)(object)val4, false, true);
		val6.AddSource((LordToil)(object)val5);
		val6.AddTrigger((Trigger)new Trigger_BecameNonHostileToPlayer());
		val.AddTransition(val6, false);
		Transition val7 = new Transition((LordToil)(object)val4, (LordToil)(object)val3, false, true);
		val7.AddTrigger((Trigger)new Trigger_BecamePlayerEnemy());
		val.AddTransition(val7, false);
		Transition val8 = new Transition((LordToil)(object)val3, (LordToil)(object)val5, false, true);
		val8.AddTrigger((Trigger)new Trigger_FractionPawnsLost(0.2f));
		val8.AddTrigger((Trigger)new Trigger_PawnHarmed(0.4f, false, (Faction)null, (DutyDef)null, (int?)null));
		val8.AddTrigger((Trigger)new Trigger_ChanceOnTickInterval(2500, 0.03f));
		val8.AddTrigger((Trigger)new Trigger_TicksPassed(251999));
		val8.AddTrigger((Trigger)new Trigger_ChanceOnPlayerHarmNPCBuilding(0.4f));
		val8.AddTrigger((Trigger)new Trigger_OnClamor(ClamorDefOf.Ability));
		val8.AddPostAction((TransitionAction)new TransitionAction_WakeAll());
		TaggedString val9 = TranslatorFormattedStringExtensions.Translate("MessageDefendersAttacking", NamedArgument.op_Implicit(faction.def.pawnsPlural), NamedArgument.op_Implicit(faction.Name), NamedArgument.op_Implicit(Faction.OfPlayer.def.pawnsPlural));
		TaggedString val10 = ((TaggedString)(ref val9)).CapitalizeFirst();
		val8.AddPreAction((TransitionAction)new TransitionAction_Message(TaggedString.op_Implicit(val10), MessageTypeDefOf.ThreatBig, (string)null, 1f, (Func<bool>)null));
		val.AddTransition(val8, false);
		return val;
	}

	public override void ExposeData()
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		((LordJob)this).ExposeData();
		Scribe_References.Look<Faction>(ref faction, "faction", false);
		Scribe_Values.Look<IntVec3>(ref baseCenter, "baseCenter", default(IntVec3), false);
	}
}
