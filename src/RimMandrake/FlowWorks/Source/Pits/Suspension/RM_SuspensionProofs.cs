using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS: the state reads northstar/suspension_bridge_proof.py makes through the bridge
	/// (jawa/static_call, one string in, one line out). Every read is the mod's own code path: the designator's TryDesignate,
	/// the component's span load, TryKnockOff, the vanilla blueprint check. "REFUSED: ..." = the call could not run.
	/// </summary>
	public static class RM_SuspensionProofs
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

		private static Designator_SuspensionBridge DesignatorFor(string tier)
		{
			switch ((tier ?? "").ToLowerInvariant())
			{
				case "rope": return new Designator_SuspensionBridge_Rope();
				case "steel": return new Designator_SuspensionBridge_Steel();
				case "heavy": return new Designator_SuspensionBridge_Heavy();
				case "steelgrated": return new Designator_SuspensionBridge_SteelGrated();
				case "heavygrated": return new Designator_SuspensionBridge_HeavyGrated();
				default: return new Designator_SuspensionBridge_Timber();
			}
		}

		/// <summary>"x1,z1;x2,z2;tier[;god]": drag the bridge over the rectangle x1..x2 × z1..z2 (god = built at once).
		/// → "BUILD ok=b anchors=N decks=N blueprints=N reason=..."</summary>
		public static string ProofBuild(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length < 3 || !Cell(a[0], out IntVec3 c1) || !Cell(a[1], out IntVec3 c2))
			{
				return "REFUSED: arg must be x1,z1;x2,z2;tier[;god] on the current map";
			}
			bool god = a.Length > 3 && a[3] == "god";
			bool was = DebugSettings.godMode;
			DebugSettings.godMode = god;
			string reason;
			List<IntVec3> cells = CellRect.FromLimits(c1, c2).Cells.ToList();
			try
			{
				reason = DesignatorFor(a[2]).TryDesignate(cells);
			}
			finally
			{
				DebugSettings.godMode = was;
			}
			int anchors = 0, decks = 0, bps = 0;
			foreach (IntVec3 c in cells)
			{
				foreach (Thing t in c.GetThingList(map))
				{
					if (t is Building_SuspensionAnchor) anchors++;
					else if (t is Building_SuspensionDeck) decks++;
					else if ((t.def.IsBlueprint || t.def.IsFrame) && RM_SuspensionDefOf.IsPartDef(t.def)) bps++;
				}
			}
			return "BUILD ok=" + (reason == null) + " anchors=" + anchors + " decks=" + decks + " blueprints=" + bps
				+ " reason=" + (reason ?? "-");
		}

		/// <summary>"x,z": the span holding that deck square. → "SPAN tier= load= rating= state= decks=N line=Load a / b kg"</summary>
		public static string ProofSpan(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || !Cell(arg, out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			RM_MapComponent_SuspensionBridges b = map.GetComponent<RM_MapComponent_SuspensionBridges>();
			SuspensionBridgeRecord r = b?.RecordAt(c);
			if (r == null || !r.TryIndexOf(c, out _, out int i))
			{
				return "SPAN none";
			}
			int span = RM_SuspensionMath.SegmentOf(i <= 0 ? 1 : i >= r.length - 1 ? r.length - 2 : i, r.Supports);
			float load = b.SpanLoad(r, span);
			List<Building_SpanDeck> decks = b.SpanDecks(r.Cell(0, RM_SuspensionMath.SegmentCells(span, r.Supports, r.length)[0]));
			return "SPAN tier=" + RM_SuspensionMath.TierLabel(r.tier) + " load=" + load.ToString("0.0") + " rating=" + r.RatingKg.ToString("0")
				+ " state=" + RM_SuspensionMath.Classify(load, r.RatingKg) + " decks=" + decks.Count + " railings=" + r.railings
				+ " line=" + RM_SuspensionMath.LoadLine(load, r.RatingKg);
		}

		/// <summary>"x,z;on|off": the bridge's railings switch, built at once (god). → "RAILS on=b railed=N"</summary>
		public static string ProofRails(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2 || !Cell(a[0], out IntVec3 c))
			{
				return "REFUSED: arg must be x,z;on|off";
			}
			RM_MapComponent_SuspensionBridges b = map.GetComponent<RM_MapComponent_SuspensionBridges>();
			SuspensionBridgeRecord r = b?.RecordAt(c);
			if (r == null)
			{
				return "RAILS none";
			}
			bool was = DebugSettings.godMode;
			DebugSettings.godMode = true;
			try
			{
				b.SetRailings(r, a[1] == "on");
			}
			finally
			{
				DebugSettings.godMode = was;
			}
			int railed = 0;
			for (int lane = 0; lane < r.width; lane++)
			{
				for (int i = 0; i < r.length; i++)
				{
					if (RM_MapComponent_SuspensionBridges.RailedAt(map, r.Cell(lane, i))) railed++;
				}
			}
			return "RAILS on=" + r.railings + " railed=" + railed;
		}

		/// <summary>"pawnId;trials": stagger-roll that pawn off its deck square `trials` times (the production TryKnockOff at the
		/// stagger chance); a fall is counted and the pawn put back. → "KNOCK trials=N fell=N railed=b edge=b"</summary>
		public static string ProofKnock(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2 || !int.TryParse(a[0], out int id) || !int.TryParse(a[1], out int trials))
			{
				return "REFUSED: arg must be pawnId;trials";
			}
			Pawn p = map.mapPawns.AllPawnsSpawned.FirstOrDefault(x => x.thingIDNumber == id);
			if (p == null || RM_MapComponent_SuspensionBridges.DeckAt(map, p.Position) == null)
			{
				return "REFUSED: pawn not on a suspension bridge deck";
			}
			IntVec3 home = p.Position;
			bool railed = RM_MapComponent_SuspensionBridges.RailedAt(map, home);
			bool edge = RM_MapComponent_SuspensionBridges.OpenEdgeBeside(map, home).IsValid;
			int fell = 0;
			for (int t = 0; t < trials; t++)
			{
				if (RM_MapComponent_SuspensionBridges.TryKnockOff(p, RM_SuspensionMath.StaggerFallChance, "staggered"))
				{
					fell++;
					if (!p.Spawned || p.Dead)
					{
						break;
					}
					p.Position = home;
					p.Notify_Teleported(true, true);
				}
			}
			return "KNOCK trials=" + trials + " fell=" + fell + " railed=" + railed + " edge=" + edge;
		}

		/// <summary>"" → "SWING x,z@tick ..." (every square dropped by a swing-down, oldest first).</summary>
		public static string ProofSwing(string arg)
		{
			RM_MapComponent_SuspensionBridges b = Find.CurrentMap?.GetComponent<RM_MapComponent_SuspensionBridges>();
			return b == null ? "REFUSED: no current map" : "SWING " + string.Join(" ", b.swingLog);
		}

		/// <summary>"x,z": the vanilla Bridge blueprint check on that square. → "VANILLA accepted=b reason=..."</summary>
		public static string ProofVanillaBridge(string arg)
		{
			Map map = Find.CurrentMap;
			TerrainDef bridge = DefDatabase<TerrainDef>.GetNamedSilentFail("Bridge");
			if (map == null || bridge == null || !Cell(arg, out IntVec3 c))
			{
				return "REFUSED: arg must be x,z (and the Bridge terrain must exist)";
			}
			AcceptanceReport r = GenConstruct.CanPlaceBlueprintAt(bridge, c, Rot4.North, map);
			return "VANILLA accepted=" + r.Accepted + " reason=" + (r.Reason ?? "-");
		}

		/// <summary>"pawnId;x,z": the path that pawn would walk to x,z now. → "PATH found=b cells=N decked=N"</summary>
		public static string ProofPath(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2 || !int.TryParse(a[0], out int id) || !Cell(a[1], out IntVec3 dest))
			{
				return "REFUSED: arg must be pawnId;x,z";
			}
			Pawn p = map.mapPawns.AllPawnsSpawned.FirstOrDefault(x => x.thingIDNumber == id);
			if (p == null)
			{
				return "REFUSED: no such pawn";
			}
			using (PawnPath path = map.pathFinder.FindPathNow(p.Position, dest, p))
			{
				if (path == null || !path.Found)
				{
					return "PATH found=False cells=0 decked=0";
				}
				int decked = path.NodesReversed.Count(n => RM_MapComponent_SuspensionBridges.DeckAt(map, n) != null);
				return "PATH found=True cells=" + path.NodesLeftCount + " decked=" + decked;
			}
		}

		// ── SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP ──────────────────────────────────────────────────────────────────

		/// <summary>"x,z": the grate reads on that square. → "GRATE grated=b deck=b fire=b attach=0.75 splash=0.5 scorches=N
		/// drainedDl=N"</summary>
		public static string ProofGrate(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || !Cell(arg, out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			Building_SpanDeck deck = RM_SpanUtility.DeckAt(map, c);
			bool grated = RM_GrateEffects.GrateAt(map, c) != null;
			bool fire = RM_GrateEffects.GratePassesFire(map, c);
			return "GRATE grated=" + grated + " deck=" + (deck != null) + " fire=" + fire
				+ " attach=" + RM_FireMath.AttachChance(false, deck != null, false, fire).ToString("0.00")
				+ " splash=" + (deck == null ? 1f : deck.Grated ? RM_SuspensionMath.GrateSplashChance(1f) : 0f).ToString("0.00")
				+ " scorches=" + RM_GrateEffects.Scorches + " drainedDl=" + RM_GrateEffects.DrainedDl;
		}

		/// <summary>"x,z;litres;liquidDefName": spill that much liquid on that square through the production spill
		/// (RM_LiquidSpill.Spill, what a hose end, a tank leak or a sprinkler calls). → "POUR dl=N bodyBefore=N bodyAfter=N
		/// rise=N filthBefore=N filthAfter=N" (body = every dug square's water within 12 squares, decilitres; filth = filth on
		/// the square).</summary>
		public static string ProofPour(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 3 || !Cell(a[0], out IntVec3 c) || !c.InBounds(map) || !int.TryParse(a[1], out int litres))
			{
				return "REFUSED: arg must be x,z;litres;liquidDefName";
			}
			LiquidTypes.LiquidDef liquid = DefDatabase<LiquidTypes.LiquidDef>.GetNamedSilentFail(a[2]);
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (liquid == null || ex == null)
			{
				return "REFUSED: no such LiquidDef or no excavation component";
			}
			long Body()
			{
				long sum = 0;
				foreach (IntVec3 n in GenRadial.RadialCellsAround(c, 12f, true))
				{
					if (n.InBounds(map) && ex.IsExcavated(n))
					{
						sum += ex.WaterDlAt(n);
					}
				}
				return sum;
			}
			int Filth() => c.GetThingList(map).Count(t => t is Filth);
			long b0 = Body();
			int f0 = Filth();
			int dl = litres * RM_Volume.UnitsPerLitre;
			Machinery.RM_LiquidSpill.Spill(map, c, liquid, dl);
			long b1 = Body();
			return "POUR dl=" + dl + " bodyBefore=" + b0 + " bodyAfter=" + b1 + " rise=" + (b1 - b0) + " filthBefore=" + f0
				+ " filthAfter=" + Filth();
		}
	}
}
