using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	/// <summary>
	/// Groups every CompPipeNetwork member on the map into connected components
	/// by 4-way cell adjacency, lazily — rebuilt only when dirtied by a spawn or
	/// despawn, and only when a query actually needs it. RUT_PipeSegment,
	/// RUT_PipeValve and RUT_PipePump are all members; "pressurized" reads the
	/// pump(s) and valve(s) of the SAME group a rupture belongs to.
	/// </summary>
	public class MapComponent_PipeNetworks : MapComponent
	{
		private List<List<CompPipeNetwork>> networks = new List<List<CompPipeNetwork>>();
		private bool dirty = true;
		private readonly HashSet<CompPipeNetwork> allMembers = new HashSet<CompPipeNetwork>();
		private readonly HashSet<CompPipeNetwork> visited = new HashSet<CompPipeNetwork>();
		private readonly Queue<CompPipeNetwork> frontier = new Queue<CompPipeNetwork>();

		public MapComponent_PipeNetworks(Map map) : base(map)
		{
		}

		public void Notify_MemberChanged()
		{
			dirty = true;
		}

		private void RebuildIfDirty()
		{
			if (!dirty)
			{
				return;
			}
			dirty = false;
			networks.Clear();
			allMembers.Clear();
			visited.Clear();

			foreach (Thing t in map.listerThings.AllThings)
			{
				if (t is ThingWithComps twc)
				{
					CompPipeNetwork comp = twc.GetComp<CompPipeNetwork>();
					if (comp != null)
					{
						allMembers.Add(comp);
					}
				}
			}

			foreach (CompPipeNetwork start in allMembers)
			{
				if (visited.Contains(start))
				{
					continue;
				}
				var group = new List<CompPipeNetwork>();
				frontier.Clear();
				frontier.Enqueue(start);
				visited.Add(start);
				while (frontier.Count > 0)
				{
					CompPipeNetwork cur = frontier.Dequeue();
					group.Add(cur);
					foreach (IntVec3 c in GenAdj.CellsAdjacentCardinal(cur.parent))
					{
						if (!c.InBounds(map))
						{
							continue;
						}
						foreach (Thing t in c.GetThingList(map))
						{
							if (t is ThingWithComps twc2)
							{
								CompPipeNetwork neighbour = twc2.GetComp<CompPipeNetwork>();
								if (neighbour != null && !visited.Contains(neighbour))
								{
									visited.Add(neighbour);
									frontier.Enqueue(neighbour);
								}
							}
						}
					}
				}
				networks.Add(group);
			}
		}

		private List<CompPipeNetwork> GroupOf(CompPipeNetwork member)
		{
			RebuildIfDirty();
			foreach (List<CompPipeNetwork> group in networks)
			{
				if (group.Contains(member))
				{
					return group;
				}
			}
			return null;
		}

		/// <summary>Any pump in the same network as `member` is currently
		/// running — used by CompVWakeAgitation ("agitated by pumping"),
		/// independent of valve state.</summary>
		public bool IsNetworkPumping(CompPipeNetwork member)
		{
			List<CompPipeNetwork> group = GroupOf(member);
			if (group == null)
			{
				return false;
			}
			foreach (CompPipeNetwork c in group)
			{
				CompPipePump pump = c.parent.GetComp<CompPipePump>();
				if (pump != null && pump.Running)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Pressurized: a running pump exists AND no valve in the same
		/// network has been closed. Closing ANY reachable valve depressurizes
		/// the whole network — the ruled "manual shutoff valve... reach the pump
		/// and operate it" simplified to network granularity rather than
		/// per-segment path routing.</summary>
		public bool IsNetworkPressurized(CompPipeNetwork member)
		{
			List<CompPipeNetwork> group = GroupOf(member);
			if (group == null)
			{
				return false;
			}
			bool anyRunningPump = false;
			foreach (CompPipeNetwork c in group)
			{
				CompPipeValve valve = c.parent.GetComp<CompPipeValve>();
				if (valve != null && valve.Closed)
				{
					return false;
				}
				CompPipePump pump = c.parent.GetComp<CompPipePump>();
				if (pump != null && pump.Running)
				{
					anyRunningPump = true;
				}
			}
			return anyRunningPump;
		}
	}
}
