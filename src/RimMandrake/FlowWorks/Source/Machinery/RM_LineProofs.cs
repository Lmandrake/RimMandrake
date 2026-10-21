using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Pits;
using RimMandrake.Shared.Slack;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>
	/// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 7 (and POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS): the state reads and staging
	/// northstar/lines_proof.py makes through the bridge (jawa/static_call, one string in, one line out: a word, then key=value
	/// tokens; "REFUSED: ..." = the call could not run). Every read goes through the mod's own code: the placement gate
	/// (GenConstruct.CanPlaceBlueprintAt, patched by RM_LineCrossing), the hose band layer (RM_HoseBands), the liquid net's
	/// components, the pipe-pole seam (RM_PipePoles), the power net, and the counters the phase-2/3 code keeps.
	/// Contracts: lines_proof.OWED_PROOFS (selftest_lines_proof checks each method exists and answers its word).
	/// </summary>
	public static class RM_LineProofs
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

		private static string B(bool b) => b ? "True" : "False";

		private static string NoSpaces(string s) => string.IsNullOrEmpty(s) ? "-" : s.Replace(' ', '_').Replace('\n', '|');

		private static Map MapOk(IntVec3 c)
		{
			Map map = Find.CurrentMap;
			return map != null && c.InBounds(map) ? map : null;
		}

		/// <summary>"defName;x,z": may a blueprint of that def go on that square now (the production placement gate, stuff = the
		/// def's default). → "PLACE ok=b kind=K surface=S why=..."</summary>
		public static string ProofCanPlace(string arg)
		{
			string[] a = (arg ?? "").Split(';');
			if (a.Length != 2 || !Cell(a[1], out IntVec3 c) || MapOk(c) == null)
			{
				return "REFUSED: arg must be defName;x,z on the current map";
			}
			Map map = MapOk(c);
			ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(a[0]);
			if (def == null)
			{
				return "REFUSED: no ThingDef " + a[0];
			}
			ThingDef stuff = def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null;
			AcceptanceReport r = GenConstruct.CanPlaceBlueprintAt(def, c, Rot4.North, map, false, null, null, stuff);
			LineKind? kind = RM_LineCrossing.KindOf(def);
			return "PLACE ok=" + B(r.Accepted) + " kind=" + (kind.HasValue ? kind.Value.ToString() : "none") + " surface=" + RM_LineCrossing.SurfaceAt(map, c)
				+ " why=" + NoSpaces(r.Reason);
		}

		/// <summary>"x,z": what the square is to a line, and to a hose. → "SURFACE s=S hoseClosed=b band=N rules=b"</summary>
		public static string ProofSurface(string arg)
		{
			if (!Cell(arg, out IntVec3 c) || MapOk(c) == null)
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			Map map = MapOk(c);
			return "SURFACE s=" + RM_LineCrossing.SurfaceAt(map, c) + " hoseClosed=" + B(RM_HoseBands.Closed(map, c)) + " band=" + RM_HoseBands.BandAt(map, c)
				+ " rules=" + B(RM_MachinerySettings.lineCrossingRulesEnabled);
		}

		private static Thing NetThingAt(Map map, IntVec3 c) =>
			c.GetThingList(map).FirstOrDefault(t => RM_LiquidNet.RoleOfThing(t) != RM_NetRole.None);

		/// <summary>"x1,z1;x2,z2" (two liquid machines or tanks): do they share a liquid-net component, and what the pipe-pole seam
		/// adds now. → "NET same=b a=N b=N spans=S aerial=E fitting=F"</summary>
		public static string ProofNet(string arg)
		{
			string[] a = (arg ?? "").Split(';');
			if (a.Length != 2 || !Cell(a[0], out IntVec3 c1) || !Cell(a[1], out IntVec3 c2) || MapOk(c1) == null || MapOk(c2) == null)
			{
				return "REFUSED: arg must be x1,z1;x2,z2 on the current map";
			}
			Map map = MapOk(c1);
			Thing t1 = NetThingAt(map, c1), t2 = NetThingAt(map, c2);
			if (t1 == null || t2 == null)
			{
				return "REFUSED: no liquid machine or tank at " + (t1 == null ? a[0] : a[1]);
			}
			RM_NetComponents comps = RM_LiquidNet.Components(map);
			var s1 = new HashSet<RM_NetComponent>(comps.ComponentsOf(t1));
			var s2 = new HashSet<RM_NetComponent>(comps.ComponentsOf(t2));
			bool same = s1.Overlaps(s2);
			int spans = RM_PipePoles.UpSpans(map).Count;
			RM_PipeSpanEdges e = RM_PipePoles.EdgesFor(map);
			return "NET same=" + B(same) + " a=" + s1.Count + " b=" + s2.Count + " spans=" + spans + " aerial=" + e.AerialEdges + " fitting=" + e.FittingEdges;
		}

		/// <summary>"x1,z1;x2,z2" (two pipe poles): string a pipe span between them through Gimme Some Slack's own link
		/// (CompAerialAnchor.TryLink, found by name). → "LINK verdict=V strung=b spans=N"</summary>
		public static string ProofLinkPoles(string arg)
		{
			string[] a = (arg ?? "").Split(';');
			if (a.Length != 2 || !Cell(a[0], out IntVec3 c1) || !Cell(a[1], out IntVec3 c2) || MapOk(c1) == null || MapOk(c2) == null)
			{
				return "REFUSED: arg must be x1,z1;x2,z2 on the current map";
			}
			Map map = MapOk(c1);
			Thing p1 = c1.GetThingList(map).FirstOrDefault(t => RM_LineCrossing.KindOf(t.def) == LineKind.PipePole);
			Thing p2 = c2.GetThingList(map).FirstOrDefault(t => RM_LineCrossing.KindOf(t.def) == LineKind.PipePole);
			if (p1 == null || p2 == null)
			{
				return "REFUSED: no pipe pole at " + (p1 == null ? a[0] : a[1]);
			}
			Type anchor = GenTypes.GetTypeInAnyAssembly("RimMandrake.GimmeSomeSlack.Aerial.CompAerialAnchor");
			MethodInfo link = anchor?.GetMethod("TryLink", BindingFlags.Public | BindingFlags.Static);
			ThingComp comp = (p1 as ThingWithComps)?.AllComps.FirstOrDefault(x => anchor != null && anchor.IsInstanceOfType(x));
			if (link == null || comp == null)
			{
				return "REFUSED: Gimme Some Slack's CompAerialAnchor.TryLink is not loaded";
			}
			string verdict = link.Invoke(null, new object[] { comp, p2 })?.ToString() ?? "null";
			List<KeyValuePair<Thing, Thing>> spans = RM_PipePoles.UpSpans(map);
			bool strung = spans.Any(s => (s.Key == p1 && s.Value == p2) || (s.Key == p2 && s.Value == p1));
			return "LINK verdict=" + verdict + " strung=" + B(strung) + " spans=" + spans.Count;
		}

		/// <summary>"x,z": the powered building there (a CompPowerTrader), else the first power transmitter. → "POWER on=b
		/// net=N trader=b" (net = the power net's index on the map, -1 none).</summary>
		public static string ProofPower(string arg)
		{
			if (!Cell(arg, out IntVec3 c) || MapOk(c) == null)
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			Map map = MapOk(c);
			List<Thing> things = c.GetThingList(map);
			CompPowerTrader trader = things.Select(t => t.TryGetComp<CompPowerTrader>()).FirstOrDefault(x => x != null);
			CompPower any = trader ?? things.Select(t => t.TryGetComp<CompPower>()).FirstOrDefault(x => x != null);
			if (any == null)
			{
				return "REFUSED: nothing with power at " + arg;
			}
			int net = any.PowerNet == null ? -1 : map.powerNetManager.AllNetsListForReading.IndexOf(any.PowerNet);
			return "POWER on=" + B(trader != null ? trader.PowerOn : any.PowerNet != null) + " net=" + net + " trader=" + B(trader != null);
		}

		/// <summary>"x,z": the power cord there. → "CORD cut=b transmits=b net=N line=..." (line = its P9 crossing readout).</summary>
		public static string ProofCord(string arg)
		{
			if (!Cell(arg, out IntVec3 c) || MapOk(c) == null)
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			Map map = MapOk(c);
			Building_RM_PowerCord cord = c.GetThingList(map).OfType<Building_RM_PowerCord>().FirstOrDefault();
			if (cord == null)
			{
				return "REFUSED: no power cord at " + arg;
			}
			bool cut = cord.CutByLeaf;
			string line = RM_LineReadoutMath.CordLine(cut ? LineSurface.SolidGround : RM_LineCrossing.SurfaceAt(map, c), cut);
			int net = cord.PowerComp?.PowerNet == null ? -1 : map.powerNetManager.AllNetsListForReading.IndexOf(cord.PowerComp.PowerNet);
			return "CORD cut=" + B(cut) + " transmits=" + B(cord.TransmitsPowerNow) + " net=" + net + " line=" + NoSpaces(line);
		}

		private static CompHoseReel ReelAt(Map map, IntVec3 c) =>
			map.GetComponent<RM_MapComponent_Hoses>()?.Reels.FirstOrDefault(r => r.parent.OccupiedRect().Contains(c));

		/// <summary>"rx,rz" (any square of a reel): its laid hose. → "HOSELINE laid=b ramps=N ladders=N cut=b cells=N deck=N
		/// cover=N dug=N geom=G retract=... line=..." (deck/cover/dug = lay cells on a deck, a cover, a band other than the
		/// reel's; geom = RM_MapComponent_Hoses.GeometryHash of the lay; line = the P9 crossing readout).</summary>
		public static string ProofHoseLine(string arg)
		{
			if (!Cell(arg, out IntVec3 c) || MapOk(c) == null)
			{
				return "REFUSED: arg must be rx,rz on the current map";
			}
			Map map = MapOk(c);
			CompHoseReel r = ReelAt(map, c);
			if (r == null)
			{
				return "REFUSED: no hose reel at " + arg;
			}
			int ramps = 0, ladders = 0, deck = 0, cover = 0, dug = 0;
			var cells = new HashSet<IntVec3>();
			if (r.laid && r.lay != null)
			{
				RM_HoseBands.LevelChanges(map, r.lay.Flat, out ramps, out ladders);
				IList<V2> f = r.lay.Flat;
				for (int i = 1; i < f.Count; i++)
				{
					int k = Math.Max(1, (int)Math.Ceiling(V2.Dist(f[i - 1], f[i]) / 0.05));
					for (int j = 0; j <= k; j++)
					{
						Cell q = (f[i - 1] + (f[i] - f[i - 1]) * (j / (double)k)).Floor;
						cells.Add(new IntVec3(q.X, 0, q.Z));
					}
				}
				int home = RM_HoseBands.BandAt(map, r.parent.Position);
				foreach (IntVec3 q in cells)
				{
					if (!q.InBounds(map)) continue;
					LineSurface s = RM_LineCrossing.SurfaceAt(map, q);
					if (s == LineSurface.Deck || s == LineSurface.RopeDeck || s == LineSurface.DrawbridgeLeaf) deck++;
					if (s == LineSurface.Cover) cover++;
					if (RM_HoseBands.BandAt(map, q) != home) dug++;
				}
			}
			bool cut = RM_Drawbridges.HoseCut(r);
			return "HOSELINE laid=" + B(r.laid) + " ramps=" + ramps + " ladders=" + ladders + " cut=" + B(cut) + " cells=" + cells.Count + " deck=" + deck
				+ " cover=" + cover + " dug=" + dug + " geom=" + RM_MapComponent_Hoses.GeometryHash(r.lay) + " retract=" + NoSpaces(r.lastRetractReason)
				+ " line=" + NoSpaces(r.CrossingLines().Trim());
		}

		/// <summary>"rx,rz;Capped|Intake|Outflow": STAGING. Sets the reel's free-end role as the gizmo does (and bumps the net the
		/// way the gizmo does). → "ROLE role=R"</summary>
		public static string ProofHoseRole(string arg)
		{
			string[] a = (arg ?? "").Split(';');
			if (a.Length != 2 || !Cell(a[0], out IntVec3 c) || MapOk(c) == null || !Enum.TryParse(a[1], out RM_FreeEndRole role))
			{
				return "REFUSED: arg must be rx,rz;Capped|Intake|Outflow on the current map";
			}
			Map map = MapOk(c);
			CompHoseReel r = ReelAt(map, c);
			if (r == null)
			{
				return "REFUSED: no hose reel at " + a[0];
			}
			r.freeEndRole = role;
			RM_LiquidNet.Bump(map);
			return "ROLE role=" + r.freeEndRole;
		}

		/// <summary>"x,z,w,h": the dug water in that rect (decilitres, RM_MapComponent_Excavation.WaterDlAt). → "PITWATER dl=N
		/// wet=N cells=N"</summary>
		public static string ProofPitWater(string arg)
		{
			string[] p = (arg ?? "").Split(',');
			Map map = Find.CurrentMap;
			if (map == null || p.Length != 4 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z) || !int.TryParse(p[2], out int w)
				|| !int.TryParse(p[3], out int h) || w <= 0 || h <= 0)
			{
				return "REFUSED: arg must be x,z,w,h on the current map";
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return "REFUSED: no excavation engine";
			}
			long dl = 0;
			int wet = 0, cells = 0;
			foreach (IntVec3 c in CellRect.FromLimits(x, z, x + w - 1, z + h - 1).ClipInsideMap(map))
			{
				cells++;
				long v = eng.WaterDlAt(c);
				dl += v;
				if (v > 0) wet++;
			}
			return "PITWATER dl=" + dl + " wet=" + wet + " cells=" + cells;
		}

		/// <summary>"": the line counters (session statics: a load does not reset them; read before and after). → "LINES broken=N
		/// commits=N cordsDropped=N hosesCut=N tore=N liveFalls=N liveHalves=N leafReconnects=N netBumps=N shocks=N" (shocks =
		/// Gimme Some Slack's RM_FallenWireShock.shocks, -1 when it is not loaded).</summary>
		public static string ProofLineCounters(string arg)
		{
			int shocks = -1;
			FieldInfo f = GenTypes.GetTypeInAnyAssembly("RimMandrake.GimmeSomeSlack.Aerial.RM_FallenWireShock")?.GetField("shocks", BindingFlags.Public | BindingFlags.Static);
			if (f != null)
			{
				shocks = (int)f.GetValue(null);
			}
			return "LINES broken=" + RM_LineDigBreak.LinesBroken + " commits=" + RM_LineDigBreak.CommitsThatBroke + " cordsDropped=" + RM_DeckCollapseLines.CordsDropped
				+ " hosesCut=" + RM_DeckCollapseLines.HosesCut + " tore=" + RM_DeckCollapseLines.SquaresThatTore + " liveFalls=" + RM_MapComponent_FallenCords.LiveFalls
				+ " liveHalves=" + RM_MapComponent_FallenCords.LiveHalvesMade + " leafReconnects=" + Building_RM_PowerCord.LeafReconnects + " netBumps=" + RM_PipePoles.NetBumps
				+ " shocks=" + shocks;
		}
	}
}
