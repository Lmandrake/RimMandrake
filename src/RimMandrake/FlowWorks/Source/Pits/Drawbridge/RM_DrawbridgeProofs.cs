using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS: the state reads and staging northstar/drawbridge_proof.py makes through the bridge
	/// (jawa/static_call, one string in, one line out: a word, then key=value tokens). Every read goes through the mod's own
	/// code path (MakeDrawbridge, Order, the work giver, Tip, the plank job and ledger). "REFUSED: ..." = the call could not run.
	/// Bank letters are record-relative: A is the bridge record's index-0 end (DRAW reports where that is as firstAt=x,z).
	/// </summary>
	public static class RM_DrawbridgeProofs
	{
		private static bool Cell(string s, out IntVec3 c)
		{
			c = IntVec3.Invalid;
			string[] p = (s ?? "").Split(',');
			if (p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
			{
				return false;
			}
			c = new IntVec3(x, 0, z);
			return true;
		}

		private static string Xz(IntVec3 c) => c.x + "," + c.z;

		private static Pawn PawnById(Map map, string id)
		{
			return map != null && int.TryParse(id, out int n) ? map.mapPawns.AllPawnsSpawned.FirstOrDefault(x => x.thingIDNumber == n) : null;
		}

		/// <summary>The drawbridge leaf holding the deck square at c (false off a leaf).</summary>
		private static bool LeafAt(Map map, IntVec3 c, out SuspensionBridgeRecord r, out DrawbridgeLeaf l)
		{
			l = null;
			r = map == null || !c.InBounds(map) ? null : RM_MapComponent_SuspensionBridges.Of(map)?.RecordAt(c);
			if (r == null || !r.IsDrawbridge || !r.TryIndexOf(c, out _, out int i))
			{
				return false;
			}
			l = RM_Drawbridges.LeafOf(r, i);
			return l != null;
		}

		private static string Pending(DrawbridgeLeaf l)
		{
			return l.pendingOrder == RM_DrawbridgeMath.OrderRaise ? "raise" : l.pendingOrder == RM_DrawbridgeMath.OrderLower ? "lower" : "none";
		}

		private static string NoSpaces(string s) => (s ?? "-").Replace(' ', '_');

		/// <summary>"x1,z1;x2,z2;timber|steel;A|B[;winch]": RM_SuspensionProofs.ProofBuild (god) over the rectangle, then
		/// MakeDrawbridge with the colony bank A (record index 0) or B; 'winch' spawns one player winch house per leaf on the
		/// square beyond its hinge anchor (lane 0), linked by its own SpawnSetup (LinkWinch). A winch square holding a building
		/// is refused, never wiped (items and pawns there are moved aside).
		/// → "DRAW ok=b leaves=N tier=T hinges=A,B winchAt=x,z|x,z firstAt=x,z reason=..."</summary>
		public static string ProofMakeDrawbridge(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length < 4 || !Cell(a[0], out IntVec3 c1) || !Cell(a[1], out IntVec3 c2)
				|| (a[2] != "timber" && a[2] != "steel") || (a[3] != "A" && a[3] != "B"))
			{
				return "REFUSED: arg must be x1,z1;x2,z2;timber|steel;A|B[;winch] on the current map";
			}
			string tier = a[2];
			bool winch = a.Length > 4 && a[4] == "winch";
			string Fail(string why, int leaves = 0) => "DRAW ok=False leaves=" + leaves + " tier=" + tier + " hinges=- winchAt=- firstAt=- reason=" + NoSpaces(why);
			string build = RM_SuspensionProofs.ProofBuild(a[0] + ";" + a[1] + ";" + tier + ";god");
			if (!build.StartsWith("BUILD ok=True"))
			{
				return Fail("build:" + build);
			}
			RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(map);
			SuspensionBridgeRecord r = CellRect.FromLimits(c1, c2).Cells.Select(c => comp?.RecordAt(c)).FirstOrDefault(x => x != null);
			if (r == null)
			{
				return Fail("no bridge record in the rectangle");
			}
			if (!RM_Drawbridges.MakeDrawbridge(r, a[3] == "A", out string why))
			{
				return Fail(why);
			}
			List<string> at = new List<string>();
			if (winch)
			{
				ThingDef def = tier == "steel" ? RM_DrawbridgeDefOf.RM_DrawbridgeWinch_Steel : RM_DrawbridgeDefOf.RM_DrawbridgeWinch_Timber;
				foreach (DrawbridgeLeaf l in r.leaves)
				{
					IntVec3 c = r.Cell(0, l.hingeAtFirst ? -1 : r.length);
					if (!c.InBounds(map) || c.GetEdifice(map) != null)
					{
						return Fail("winch square " + Xz(c) + " is off the map or built on", r.leaves.Count);
					}
					Thing w = ThingMaker.MakeThing(def);
					w.SetFaction(Faction.OfPlayer);
					GenSpawn.Spawn(w, c, map, WipeMode.VanishOrMoveAside);
					if (l.winch != w)
					{
						return Fail("winch at " + Xz(c) + " did not link to its leaf", r.leaves.Count);
					}
					at.Add(Xz(c));
				}
			}
			return "DRAW ok=True leaves=" + r.leaves.Count + " tier=" + tier + " hinges=" + string.Join(",", r.leaves.Select(l => l.hingeAtFirst ? "A" : "B"))
				+ " winchAt=" + (at.Count > 0 ? string.Join("|", at) : "-") + " firstAt=" + Xz(r.Cell(0, 0)) + " reason=-";
		}

		/// <summary>"x,z" (a deck square): that leaf's saved state. → "LEAF leaf=k/n progress=P full=F target=raised|lowered
		/// raised=a/b frozen=b winch=b powered=b hold=b auto=b pending=raise|lower|none tip=b hinge=A|B version=V";
		/// "LEAF none" off a leaf (an off-map square included).</summary>
		public static string ProofLeaf(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || !Cell(arg, out IntVec3 c))
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			if (!LeafAt(map, c, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				return "LEAF none";
			}
			int full = RM_Drawbridges.FullTicks(r, l);
			int up = 0;
			for (int i = l.first; i <= l.last; i++)
			{
				if (RM_DrawbridgeMath.IsRaised(l.Span, i, l.progress, full))
				{
					up++;
				}
			}
			bool hasWinch = l.winch != null && l.winch.Spawned;
			return "LEAF leaf=" + (r.leaves.IndexOf(l) + 1) + "/" + r.leaves.Count + " progress=" + l.progress + " full=" + full
				+ " target=" + (l.targetRaised ? "raised" : "lowered") + " raised=" + up + "/" + l.Span.Length + " frozen=" + l.frozen
				+ " winch=" + hasWinch + " powered=" + (hasWinch && l.winch.Powered) + " hold=" + l.holdRaised + " auto=" + l.autoLowering
				+ " pending=" + Pending(l) + " tip=" + l.tipCommitted + " hinge=" + (l.hingeAtFirst ? "A" : "B") + " version=" + l.version;
		}

		/// <summary>"x,z;raise|lower[;instant]": RM_Drawbridges.DevSetTarget. 'instant' (staging only, never a claim) also sets
		/// the progress to the target and runs what one drive step runs there: the production Tip (once per raise), Apply and
		/// Fall. → "DEVSET target=raised|lowered progress=N"</summary>
		public static string ProofDevSet(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length < 2 || !Cell(a[0], out IntVec3 c) || (a[1] != "raise" && a[1] != "lower"))
			{
				return "REFUSED: arg must be x,z;raise|lower[;instant]";
			}
			if (!LeafAt(map, c, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				return "REFUSED: not a drawbridge leaf square";
			}
			bool raise = a[1] == "raise";
			RM_Drawbridges.DevSetTarget(l, raise);
			if (a.Length > 2 && a[2] == "instant")
			{
				l.progress = raise ? RM_Drawbridges.FullTicks(r, l) : 0;
				List<Pawn> fallers = null;
				if (l.progress > 0 && !l.tipCommitted)
				{
					fallers = RM_Drawbridges.Tip(map, r, l);
					l.tipCommitted = true;
				}
				if (l.progress == 0)
				{
					l.tipCommitted = false;
				}
				RM_Drawbridges.Apply(map, r, l);
				if (fallers != null && fallers.Count > 0)
				{
					RM_Drawbridges.Fall(map, r, fallers);
				}
			}
			return "DEVSET target=" + (l.targetRaised ? "raised" : "lowered") + " progress=" + l.progress;
		}

		/// <summary>"x,z;raise|lower[;now]": RM_Drawbridges.Order (the gizmo's action). 'now' also applies what the work job
		/// applies when its colonist arrives (JobDriver_WorkDrawbridge: target from the pending order, order cleared, a raise
		/// ends an auto-lower) without the walk. → "ORDER pending=raise|lower|none hold=b locked=b target=raised|lowered"</summary>
		public static string ProofOrder(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length < 2 || !Cell(a[0], out IntVec3 c) || (a[1] != "raise" && a[1] != "lower"))
			{
				return "REFUSED: arg must be x,z;raise|lower[;now]";
			}
			if (!LeafAt(map, c, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				return "REFUSED: not a drawbridge leaf square";
			}
			RM_Drawbridges.Order(map, r, l, a[1] == "raise");
			if (a.Length > 2 && a[2] == "now" && WorkGiver_Drawbridge.NeedsHands(r, l, out bool raise))
			{
				l.targetRaised = raise;
				l.pendingOrder = RM_DrawbridgeMath.OrderNone;
				if (raise)
				{
					l.autoLowering = false;
				}
			}
			return "ORDER pending=" + Pending(l) + " hold=" + l.holdRaised + " locked=" + (RM_Drawbridges.FreeHostileCount(map, true) > 0)
				+ " target=" + (l.targetRaised ? "raised" : "lowered");
		}

		/// <summary>"pawnId;x,z": would that pawn get a job working that leaf? The loaded WorkGiver_Drawbridge asked as its
		/// scanner asks: each work spot (the winch house, then the far anchor) the pawn can reach, JobOnThing forced.
		/// → "WORK job=b spot=winch|far|none raise=b why=-|no_order|unreachable_winch|refused_at_far|..."</summary>
		public static string ProofWorkJob(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			Pawn p = a.Length == 2 ? PawnById(map, a[0]) : null;
			if (p == null || !Cell(a[1], out IntVec3 c))
			{
				return "REFUSED: arg must be pawnId;x,z";
			}
			if (!LeafAt(map, c, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				return "REFUSED: not a drawbridge leaf square";
			}
			WorkGiver_Drawbridge giver = DefDatabase<WorkGiverDef>.AllDefsListForReading
				.FirstOrDefault(d => d.giverClass == typeof(WorkGiver_Drawbridge))?.Worker as WorkGiver_Drawbridge;
			if (giver == null)
			{
				return "REFUSED: no WorkGiverDef uses WorkGiver_Drawbridge";
			}
			bool needs = WorkGiver_Drawbridge.NeedsHands(r, l, out bool raise);
			if (!needs)
			{
				return "WORK job=False spot=none raise=" + raise + " why=no_order";
			}
			List<string> why = new List<string>();
			foreach ((Thing spot, string name) in new (Thing, string)[] { (l.winch, "winch"), (WorkGiver_Drawbridge.FarAnchor(map, r, l), "far") })
			{
				if (spot == null || !spot.Spawned)
				{
					why.Add("no_" + name);
					continue;
				}
				if (!p.CanReach(spot, giver.PathEndMode, Danger.Deadly))
				{
					why.Add("unreachable_" + name);
					continue;
				}
				if (giver.JobOnThing(p, spot, true) != null)
				{
					return "WORK job=True spot=" + name + " raise=" + raise + " why=-";
				}
				why.Add("refused_at_" + name);
			}
			return "WORK job=False spot=none raise=" + raise + " why=" + string.Join(",", why);
		}

		/// <summary>"x,z;on|off": the leaf's winch house's CompPowerTrader.PowerOn forced and held (the drive re-asserts it
		/// every step, and it is saved). → "POWER powered=b winch=b"</summary>
		public static string ProofWinchPower(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2 || !Cell(a[0], out IntVec3 c) || (a[1] != "on" && a[1] != "off"))
			{
				return "REFUSED: arg must be x,z;on|off";
			}
			if (!LeafAt(map, c, out _, out DrawbridgeLeaf l))
			{
				return "REFUSED: not a drawbridge leaf square";
			}
			Building_DrawbridgeWinch w = l.winch != null && l.winch.Spawned ? l.winch : null;
			if (w == null)
			{
				return "POWER powered=False winch=False";
			}
			w.proofPower = a[1] == "on" ? 1 : 2;
			w.HoldProofPower();
			return "POWER powered=" + w.Powered + " winch=True";
		}

		/// <summary>"x,z": the production tip plan for that leaf if it left its seat now (Tip with a preview: nobody moved).
		/// → "PREVIEW riders=N land=L fall=F free=S" (free = legal landing squares on the hinge bank within TipReach)</summary>
		public static string ProofTipPreview(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || !Cell(arg, out IntVec3 c))
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			if (!LeafAt(map, c, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				return "REFUSED: not a drawbridge leaf square";
			}
			int[] pv = new int[4];
			RM_Drawbridges.Tip(map, r, l, pv);
			return "PREVIEW riders=" + pv[0] + " land=" + pv[1] + " fall=" + pv[2] + " free=" + pv[3];
		}

		/// <summary>"pawnId;lipx,z;farx,z": give the pawn an RM_RaidPlank (unless it carries one) and start the production
		/// PlankJob over that line. → "GIVE ok=b job=defName|- plank=thingId reserved=b" (reserved: the ledger already holds a
		/// laid plank on this line)</summary>
		public static string ProofGivePlank(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			Pawn p = a.Length == 3 ? PawnById(map, a[0]) : null;
			if (p == null || !Cell(a[1], out IntVec3 lip) || !Cell(a[2], out IntVec3 far) || p.inventory == null || p.jobs == null)
			{
				return "REFUSED: arg must be pawnId;lipx,z;farx,z (a spawned pawn with an inventory)";
			}
			if (!RM_RaidPlanks.LineOf(map, lip, far, out List<IntVec3> cells, out int[] depths))
			{
				return "REFUSED: lip and far must be on one cardinal line on the map";
			}
			Thing plank = RM_RaidPlanks.CarriedPlank(p);
			if (plank == null)
			{
				p.inventory.innerContainer.TryAdd(ThingMaker.MakeThing(RM_DrawbridgeRaidDefOf.RM_RaidPlank));
				plank = RM_RaidPlanks.CarriedPlank(p);
			}
			long line = RM_DrawbridgeMath.PlankLedger.LineKey(map.cellIndices.CellToIndex(lip), map.cellIndices.CellToIndex(far));
			bool reserved = !RM_RaidPlanks.LedgerOf(map).CanCommit(-1, line);
			Job job = plank == null ? null : RM_RaidPlanks.PlankJob(p, cells, depths);
			if (job != null)
			{
				p.jobs.StartJob(job, JobCondition.InterruptForced);
			}
			bool ok = job != null && p.CurJob == job;
			return "GIVE ok=" + ok + " job=" + (ok ? job.def.defName : "-") + " plank=" + (plank?.thingIDNumber.ToString() ?? "-") + " reserved=" + reserved;
		}

		/// <summary>"pawnId": drop the carried plank, then end the pawn's job (InterruptForced). The plank goes first so the
		/// pawn's next think cannot take the same lay job straight back. → "INT ended=b dropped=b"</summary>
		public static string ProofInterrupt(string arg)
		{
			Map map = Find.CurrentMap;
			Pawn p = PawnById(map, arg);
			if (p == null || p.jobs == null)
			{
				return "REFUSED: arg must be a spawned pawn's id";
			}
			Job was = p.CurJob;
			Thing plank = RM_RaidPlanks.CarriedPlank(p);
			bool dropped = plank != null && p.inventory.innerContainer.TryDrop(plank, p.Position, map, ThingPlaceMode.Near, out _);
			if (p.CurJob == was && was != null)
			{
				p.jobs.EndCurrentJob(JobCondition.InterruptForced);
			}
			return "INT ended=" + (was != null && p.CurJob != was) + " dropped=" + dropped;
		}

		/// <summary>"lipx,z;farx,z": what is laid over that line. → "PLEDGER crossings=N laidCells=K reserved=0|1" (crossings:
		/// raid-plank bridge records whose two ends are this line's; laidCells: laid plank squares between the ends; reserved:
		/// the map's PlankLedger holds the line as laid)</summary>
		public static string ProofPlankLedger(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2 || !Cell(a[0], out IntVec3 lip) || !Cell(a[1], out IntVec3 far)
				|| !RM_RaidPlanks.LineOf(map, lip, far, out List<IntVec3> cells, out _))
			{
				return "REFUSED: arg must be lipx,z;farx,z on one cardinal line on the map";
			}
			int crossings = 0;
			foreach (SuspensionBridgeRecord r in RM_MapComponent_SuspensionBridges.Of(map)?.Bridges ?? new List<SuspensionBridgeRecord>())
			{
				IntVec3 e0 = r.Cell(0, 0), e1 = r.Cell(0, r.length - 1);
				if (r.raidPlank && ((e0 == lip && e1 == far) || (e0 == far && e1 == lip)))
				{
					crossings++;
				}
			}
			int laid = 0;
			for (int i = 1; i < cells.Count - 1; i++)
			{
				laid += cells[i].GetThingList(map).Count(t => t.def == RM_DrawbridgeRaidDefOf.RM_RaidPlank_Laid);
			}
			long line = RM_DrawbridgeMath.PlankLedger.LineKey(map.cellIndices.CellToIndex(lip), map.cellIndices.CellToIndex(far));
			return "PLEDGER crossings=" + crossings + " laidCells=" + laid + " reserved=" + (RM_RaidPlanks.LedgerOf(map).CanCommit(-1, line) ? 0 : 1);
		}
	}
}
