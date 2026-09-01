using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace Outposts;

public class LordJob_Deliver : LordJob
{
	private IntVec3 deliverLoc;

	public LordJob_Deliver()
	{
	}

	public LordJob_Deliver(IntVec3 deliverLoc)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		this.deliverLoc = deliverLoc;
	}

	public override void ExposeData()
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		((LordJob)this).ExposeData();
		Scribe_Values.Look<IntVec3>(ref deliverLoc, "deliverLoc", default(IntVec3), false);
	}

	public override StateGraph CreateGraph()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Expected O, but got Unknown
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Expected O, but got Unknown
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Expected O, but got Unknown
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Expected O, but got Unknown
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Expected O, but got Unknown
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Expected O, but got Unknown
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Expected O, but got Unknown
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Expected O, but got Unknown
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Expected O, but got Unknown
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Expected O, but got Unknown
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Expected O, but got Unknown
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Expected O, but got Unknown
		StateGraph val = new StateGraph();
		LordToil_Travel val3 = (LordToil_Travel)(object)(val.StartingToil = (LordToil)new LordToil_Travel(deliverLoc)
		{
			maxDanger = (Danger)3,
			useAvoidGrid = true
		});
		LordToil_ExitMap val4 = new LordToil_ExitMap((LocomotionUrgency)0, true, false);
		val.AddToil((LordToil)(object)val4);
		LordToil_Drop lordToil_Drop = new LordToil_Drop();
		val.AddToil((LordToil)(object)lordToil_Drop);
		Transition val5 = new Transition((LordToil)(object)val3, (LordToil)(object)lordToil_Drop, false, true);
		val5.AddTrigger((Trigger)new Trigger_Memo("TravelArrived"));
		val5.AddTrigger((Trigger)new Trigger_PawnHarmed(1f, false, (Faction)null, (DutyDef)null, (int?)null));
		val.AddTransition(val5, false);
		Transition val6 = new Transition((LordToil)(object)lordToil_Drop, (LordToil)(object)val4, false, true);
		val6.AddTrigger((Trigger)new Trigger_Memo("AllDropped"));
		val.AddTransition(val6, false);
		LordToil_GotoDropLoc lordToil_GotoDropLoc = new LordToil_GotoDropLoc();
		val.AddToil((LordToil)(object)lordToil_GotoDropLoc);
		Transition val7 = new Transition((LordToil)(object)lordToil_Drop, (LordToil)(object)lordToil_GotoDropLoc, false, true);
		val7.AddTrigger((Trigger)new Trigger_Memo("AllDropped"));
		val.AddTransition(val7, false);
		Transition val8 = new Transition((LordToil)(object)lordToil_GotoDropLoc, (LordToil)(object)lordToil_Drop, false, true);
		val8.AddTrigger((Trigger)new Trigger_Memo("TravelArrived"));
		val.AddTransition(val8, false);
		return val;
	}
}
