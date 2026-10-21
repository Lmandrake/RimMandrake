using System.Collections.Generic;
using RimWorld;
using Verse;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>
	/// POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS: the flexible power cord (Defs/Machinery/RM_PowerCord.xml). Where it may lie
	/// and what a dig does to it come from its FlexCord tag (RM_LineCrossing, RM_LineDigBreak). This class adds the drawbridge
	/// leaf rule (design §P2, review answer 6): while the leaf under it is raised (RM_Drawbridges.LineCutAt) it transmits
	/// nothing, the way vanilla's Building_PowerSwitch does when off; RM_Drawbridges.NotifyToggled calls
	/// <see cref="Notify_LeafToggled"/> so the power net is rebuilt the moment a leaf square goes up or comes down.
	/// No setting of its own: the cut follows from a raised leaf, which only exists with drawbridgesEnabled.
	/// </summary>
	public class Building_RM_PowerCord : Building
	{
		/// <summary>State reads for the functional script: cords re-registered with the power net by a leaf toggle.</summary>
		public static int LeafReconnects;

		public bool CutByLeaf => Spawned && RM_Drawbridges.AnyRaised(Map) && RM_Drawbridges.LineCutAt(Map, new[] { Position });   // the cheap gate first: no array per net rebuild while every leaf is down

		public override bool TransmitsPowerNow => RM_PowerCordMath.TransmitsNow(base.TransmitsPowerNow, CutByLeaf);

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			// phase 7 (P9): cut by a raised leaf, else the deck it lies on (RM_LineReadoutMath.CordLine)
			bool leafCut = CutByLeaf;
			string cut = RM_LineReadoutMath.CordLine(leafCut ? LineSurface.SolidGround : RM_LineCrossing.SurfaceAt(Map, Position), leafCut);
			if (cut == null)
			{
				return s;
			}
			return s.NullOrEmpty() ? cut : s + "\n" + cut;
		}

		/// <summary>A leaf square went up or came down: every cord on it re-registers, so the net splits or rejoins now
		/// (PowerNetManager deregisters and re-registers the transmitter; TransmitsPowerNow decides which).</summary>
		public static int Notify_LeafToggled(Map map, List<IntVec3> changed)
		{
			if (map?.powerNetManager == null || changed == null)
			{
				return 0;
			}
			int n = 0;
			foreach (IntVec3 c in changed)
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				List<Thing> things = c.GetThingList(map);
				for (int i = 0; i < things.Count; i++)
				{
					if (things[i] is Building_RM_PowerCord cord && cord.PowerComp != null)
					{
						map.powerNetManager.Notfiy_TransmitterTransmitsPowerNowChanged(cord.PowerComp);
						n++;
					}
				}
			}
			LeafReconnects += n;
			return n;
		}
	}
}
