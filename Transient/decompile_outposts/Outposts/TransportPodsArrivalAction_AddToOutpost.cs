using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace Outposts;

public class TransportPodsArrivalAction_AddToOutpost : TransportersArrivalAction
{
	private Outpost outpost;

	public override bool GeneratesMap => true;

	public TransportPodsArrivalAction_AddToOutpost()
	{
	}

	public TransportPodsArrivalAction_AddToOutpost(Outpost addTo)
	{
		outpost = addTo;
	}

	public override void Arrived(List<ActiveTransporterInfo> transporters, PlanetTile tile)
	{
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		List<Thing> list = new List<Thing>();
		foreach (Thing item in transporters.SelectMany((ActiveTransporterInfo pod) => (IEnumerable<Thing>)pod.innerContainer).OfType<Thing>())
		{
			list.Add(item);
			if (item is Pawn)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.AddedFromTransportPods", NamedArgument.op_Implicit(((Entity)item).LabelShortCap), NamedArgument.op_Implicit(((WorldObject)outpost).LabelCap))), LookTargets.op_Implicit((WorldObject)(object)outpost), MessageTypeDefOf.TaskCompletion, true);
			}
		}
		foreach (Thing item2 in list)
		{
			if (item2 is Pawn)
			{
				outpost.AddPawn((Pawn)(object)((item2 is Pawn) ? item2 : null));
			}
			else
			{
				outpost.AddItem(item2);
			}
		}
	}

	public override void ExposeData()
	{
		((TransportersArrivalAction)this).ExposeData();
		Scribe_References.Look<Outpost>(ref outpost, "outpost", false);
	}

	public override FloatMenuAcceptanceReport StillValid(IEnumerable<IThingHolder> pods, PlanetTile destinationTile)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		return FloatMenuAcceptanceReport.op_Implicit(((WorldObject)outpost).Tile == destinationTile);
	}

	public static IEnumerable<FloatMenuOption> GetFloatMenuOptions(IEnumerable<IThingHolder> pods, Action<PlanetTile, TransportersArrivalAction> launchAction, Outpost outpost)
	{
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		return TransportersArrivalActionUtility.GetFloatMenuOptions<TransportPodsArrivalAction_AddToOutpost>((Func<FloatMenuAcceptanceReport>)(() => FloatMenuAcceptanceReport.op_Implicit(true)), (Func<TransportPodsArrivalAction_AddToOutpost>)(() => new TransportPodsArrivalAction_AddToOutpost(outpost)), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.AddTo", NamedArgument.op_Implicit(((WorldObject)outpost).LabelCap))), launchAction, ((WorldObject)outpost).Tile, (Action<Action>)delegate(Action launch)
		{
			launch();
		});
	}
}
