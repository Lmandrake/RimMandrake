using System;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace VEF.Planet;

public class LordJob_SiegeCustom : LordJob
{
	private Faction faction;

	private IntVec3 siegeSpot;

	private float blueprintPoints;

	public override bool GuiltyOnDowned => true;

	public LordJob_SiegeCustom()
	{
	}

	public LordJob_SiegeCustom(Faction faction, IntVec3 siegeSpot, float blueprintPoints)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		this.faction = faction;
		this.siegeSpot = siegeSpot;
		this.blueprintPoints = blueprintPoints;
	}

	public override StateGraph CreateGraph()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Expected O, but got Unknown
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Expected O, but got Unknown
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Expected O, but got Unknown
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Expected O, but got Unknown
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Expected O, but got Unknown
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Expected O, but got Unknown
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Expected O, but got Unknown
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Expected O, but got Unknown
		//IL_0103: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Expected O, but got Unknown
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_014a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0154: Expected O, but got Unknown
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Expected O, but got Unknown
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_016a: Expected O, but got Unknown
		StateGraph val = new StateGraph();
		LordToil startingToil = val.AttachSubgraph(((LordJob)new LordJob_Travel(siegeSpot)).CreateGraph()).StartingToil;
		LordToil_SiegeCustom lordToil_SiegeCustom = new LordToil_SiegeCustom(siegeSpot, blueprintPoints);
		val.AddToil((LordToil)(object)lordToil_SiegeCustom);
		LordToil startingToil2 = val.AttachSubgraph(((LordJob)new LordJob_AssaultColony(faction, true, true, false, false, true, false, false)).CreateGraph()).StartingToil;
		Transition val2 = new Transition(startingToil, (LordToil)(object)lordToil_SiegeCustom, false, true);
		val2.AddTrigger((Trigger)new Trigger_Memo("TravelArrived"));
		val2.AddTrigger((Trigger)new Trigger_TicksPassed(5000));
		val.AddTransition(val2, false);
		Transition val3 = new Transition((LordToil)(object)lordToil_SiegeCustom, startingToil2, false, true);
		val3.AddTrigger((Trigger)new Trigger_Memo("NoBuilders"));
		val3.AddTrigger((Trigger)new Trigger_Memo("NoArtillery"));
		val3.AddTrigger((Trigger)new Trigger_PawnHarmed(0.08f, false, (Faction)null, (DutyDef)null, (int?)null));
		val3.AddTrigger((Trigger)new Trigger_FractionPawnsLost(0.3f));
		val3.AddTrigger((Trigger)new Trigger_TicksPassed((int)(60000f * Rand.Range(1.5f, 3f))));
		val3.AddPreAction((TransitionAction)new TransitionAction_Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageSiegersAssaulting", NamedArgument.op_Implicit(faction.def.pawnsPlural), NamedArgument.op_Implicit(faction))), MessageTypeDefOf.ThreatBig, (string)null, 1f, (Func<bool>)null));
		val3.AddPostAction((TransitionAction)new TransitionAction_WakeAll());
		val.AddTransition(val3, false);
		return val;
	}

	public override void ExposeData()
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		Scribe_References.Look<Faction>(ref faction, "faction", false);
		Scribe_Values.Look<IntVec3>(ref siegeSpot, "siegeSpot", default(IntVec3), false);
		Scribe_Values.Look<float>(ref blueprintPoints, "blueprintPoints", 0f, false);
	}
}
