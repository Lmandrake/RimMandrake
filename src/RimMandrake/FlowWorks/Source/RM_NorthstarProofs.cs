using System.Reflection;
using HarmonyLib;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// jawa/static_call read surface for the 2026-10-05 build pass's extension rows
	/// (northstar/extensions.py). Each method takes ONE string, reads live state through the shipping
	/// code's own predicates, and writes nothing except where its doc says so. Dev surface only:
	/// nothing in the game calls it. Multi-part arguments are ';'-separated: jawa/static_call splits its args on '|'
	/// into PARAMETERS, so a '|' inside one string arrives as a second argument and the call is refused.
	/// </summary>
	public static class RM_NorthstarProofs
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

		private static Pawn PawnById(Map map, string id)
		{
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.ThingID == id || p.thingIDNumber.ToString() == id)
				{
					return p;
				}
			}
			return null;
		}

		/// <summary>TANK_LOOP_REBUILD_BOTTLES_FIND_THE_RIVER. The extension harness has no HoseProbe channel and a new tank is
		/// Store (an unasked bottle pour goes only into a Fill tank), so this stages one tank: arg "x,z;Mode" or
		/// "x,z;Mode;LiquidDef;units" (Mode = Store|Fill|Empty|Dump; contents replaced, units 0 empties it). Writes the tank's
		/// mode and stock only. "TANK mode=M effective=M liquid=D units=n", or "REFUSED: ...".</summary>
		public static string ProofTank(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || (a.Length != 2 && a.Length != 4) || !Cell(a[0], out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z;Mode or x,z;Mode;LiquidDef;units on the current map";
			}
			Building_LiquidTank tank = null;
			foreach (Thing th in c.GetThingList(map))
			{
				tank = th as Building_LiquidTank;
				if (tank != null)
				{
					break;
				}
			}
			if (tank == null)
			{
				return "REFUSED: no RM_LiquidTank at " + c;
			}
			// IsDefined too: Enum.TryParse takes "7" or "Store,Fill" and would set a mode no gizmo can (night review 2026-10-13)
			if (!System.Enum.TryParse(a[1], out Machinery.RM_TankMode mode) || !System.Enum.IsDefined(typeof(Machinery.RM_TankMode), mode))
			{
				return "REFUSED: unknown mode " + a[1];
			}
			if (a.Length == 4)
			{
				LiquidDef liquid = DefDatabase<LiquidDef>.GetNamedSilentFail(a[2]);
				if (!int.TryParse(a[3], out int units) || (units > 0 && liquid == null) || units > tank.Capacity)
				{
					return "REFUSED: bad liquid/units " + a[2] + "/" + a[3] + " (capacity " + tank.Capacity + ")";
				}
				LiquidDef hadLiquid = tank.storedLiquid;
				int had = tank.storedUnits;
				if (had > 0 && !tank.TryRemoveLiquid(had))
				{
					return "REFUSED: tank would not give up its " + had + " units";
				}
				if (units > 0 && !tank.TryAddLiquid(liquid, units))
				{
					// C8b-F3: a refused refill puts the old stock back, never loses it
					if (had > 0 && hadLiquid != null)
					{
						tank.TryAddLiquid(hadLiquid, had);
					}
					return "REFUSED: tank would not take " + units + " " + a[2];
				}
			}
			tank.mode = mode;
			return "TANK mode=" + tank.mode + " effective=" + tank.EffectiveMode + " liquid=" + (tank.storedLiquid?.defName ?? "none")
				+ " units=" + tank.storedUnits;
		}

		/// <summary>WRITES. LIQUID_BOTTLE_LOOP_1 A1/A3 (the "use" half): arg "pawnId;x,z". The pawn drinks the filled
		/// container at x,z through vanilla Thing.Ingested, so IngestionOutcomeDoer_BottleResidue runs exactly as a real
		/// drink job reaches it (the outcome doers are called from Ingested). The job's walking and carrying are NOT
		/// proven here; the fill/wash givers are. "DRANK def by pawn at x,z residueAt=x,z", or "REFUSED: ...".</summary>
		public static string ProofBottle(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2 || !Cell(a[1], out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be pawnId;x,z on the current map";
			}
			Pawn p = PawnById(map, a[0]);
			if (p == null || p.needs == null)
			{
				return "REFUSED: no spawned pawn with needs " + a[0];
			}
			Thing bottle = null;
			foreach (Thing th in c.GetThingList(map))
			{
				RM_BottledLiquidExtension ext = th.def.GetModExtension<RM_BottledLiquidExtension>();
				if (ext != null && ext.liquid != null && th.def.IsIngestible)
				{
					bottle = th;
					break;
				}
			}
			if (bottle == null)
			{
				return "REFUSED: no drinkable filled container at " + a[1];
			}
			if (bottle.stackCount > 1)
			{
				bottle = bottle.SplitOff(1);
			}
			string def = bottle.def.defName;
			bottle.Ingested(p, bottle.GetStatValue(StatDefOf.Nutrition));
			return "DRANK " + def + " by " + p.ThingID + " at " + a[1] + " residueAt=" + p.PositionHeld.x + "," + p.PositionHeld.z;
		}

		/// <summary>SUPERDEEP_PRISON_ROOM_1. arg "px,pz;lx,lz" (a pit cell, a lip cell):
		/// "ROOM split=b pitRoom=b proper=b edge=b prison=b roomsOn=b pitId=n lipId=n".</summary>
		public static string ProofRoom(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2 || !Cell(a[0], out IntVec3 pc) || !Cell(a[1], out IntVec3 lc)
				|| !pc.InBounds(map) || !lc.InBounds(map))
			{
				return "REFUSED: arg must be px,pz;lx,lz on the current map";
			}
			Room pit = pc.GetRoom(map);
			Room lip = lc.GetRoom(map);
			if (pit == null || lip == null)
			{
				return "REFUSED: no room at " + (pit == null ? pc : lc);
			}
			return "ROOM split=" + (pit != lip) + " pitRoom=" + RM_PitRooms.IsPitRoom(pit) + " proper=" + pit.ProperRoom
				+ " edge=" + pit.TouchesMapEdge + " prison=" + pit.IsPrisonCell + " roomsOn=" + RM_PitRooms.RoomsOn
				+ " pitId=" + pit.ID + " lipId=" + lip.ID;
		}

		/// <summary>PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP (design §8.6). arg "x,z;K" (a cell and a climb band) →
		/// RM_PocketGrid.ProofPocket; or "pawn:&lt;id&gt;" → "CLIMB k=K held=b trapped=b cell=x,z depth=D " + its pocket line.</summary>
		public static string ProofClimb(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return "REFUSED: no current map";
			}
			arg = arg ?? "";
			if (arg.StartsWith("cost:"))
			{
				return ProofStepCost(map, arg.Substring(5));
			}
			if (arg.StartsWith("pawn:"))
			{
				Pawn p = PawnById(map, arg.Substring(5));
				if (p == null)
				{
					return "REFUSED: no spawned pawn " + arg.Substring(5);
				}
				int k = RM_PocketGrid.ClimbLimitOf(p);
				return "CLIMB k=" + k + " held=" + RM_SuperdeepTrap.IsHeld(p) + " trapped=" + RM_SuperdeepTrap.IsTrapped(p)
					+ " cell=" + p.Position.x + "," + p.Position.z + " | " + RM_PocketGrid.ProofPocket(map, p.Position, k);
			}
			bool mask = arg.StartsWith("mask:");
			string[] a = (mask ? arg.Substring(5) : arg).Split(';');
			if (a.Length != 2 || !Cell(a[0], out IntVec3 c) || !int.TryParse(a[1], out int band))
			{
				return "REFUSED: arg must be x,z;K or mask:x,z;K or pawn:<id> or cost:fx,fz;tx,tz;<pawnId>";
			}
			// PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: the band's connectivity byte at c, beside the pocket read.
			return mask ? RM_CliffMask.ProofMask(map, c, band) + " | " + RM_PocketGrid.ProofPocket(map, c, band)
				: RM_PocketGrid.ProofPocket(map, c, band);
		}

		/// <summary>PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS step cost (RM_PitTrapMath.StepCost, §8.2): the walked step from → to
		/// priced for THIS pawn exactly as Pawn_PathFollower.CostToMoveIntoCell asks it (the pawn noted for
		/// RM_Patch_PitStepCost, then PathGrid.CalculatedCostAt(to, perceivedStatic false, from)). Reads only.
		/// "COST from=x,z to=x,z fromD=a toD=b k=K mask=b climb=C factor=F cost=N" (climb = the deeper cell's dry cost).</summary>
		private static string ProofStepCost(Map map, string arg)
		{
			string[] a = arg.Split(';');
			if (a.Length != 3 || !Cell(a[0], out IntVec3 from) || !Cell(a[1], out IntVec3 to) || !from.InBounds(map) || !to.InBounds(map))
			{
				return "REFUSED: arg must be cost:fx,fz;tx,tz;<pawnId>";
			}
			Pawn p = PawnById(map, a[2]);
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (p == null || eng == null)
			{
				return "REFUSED: no spawned pawn " + a[2] + " or no excavation engine";
			}
			int fromD = eng.HollowDepthAt(from), toD = eng.HollowDepthAt(to);
			int climb = RM_ExcavationDepth.DryTerrainFor((byte)System.Math.Max(fromD, toD))?.pathCost ?? 0;
			Pawn was = RM_Patch_PathFollower_StepPawn.current;
			int cost;
			try
			{
				RM_Patch_PathFollower_StepPawn.current = p;
				cost = map.pathing.For(p).pathGrid.CalculatedCostAt(to, false, from);
			}
			finally
			{
				RM_Patch_PathFollower_StepPawn.current = was;
			}
			return "COST from=" + from.x + "," + from.z + " to=" + to.x + "," + to.z + " fromD=" + fromD + " toD=" + toD
				+ " k=" + RM_PocketGrid.ClimbLimitOf(p) + " mask=" + RM_CliffMask.On + " climb=" + climb
				+ " factor=" + RimMandrakeFlowWorksSettings.pitSlowClimbFactor.ToString("0.##") + " cost=" + cost;
		}

		/// <summary>POND_ELEVATION_BUILD_LAKES_RUN_DEEP (northstar/deep_lake_proof.py). ';'-separated, current map:
		/// "paint;x;z;w;h;rim" paints a rectangular lake (WaterShallow within <c>rim</c> squares of its edge, WaterDeep inside) —
		/// writes terrain only; "form;x,z" forms (or finds) the body at a square; "stock;x,z;fraction" sets that body's stock to
		/// fraction × capacity (a stand-in for pumps: the conservation of real pumping is the offline selftests'), then runs its
		/// recession and restore to rest (RM_LiquidStock.SettleRecession); "shape;x,z" reads. BODY/SHAPE lines are
		/// "key=value" tokens; REFUSED: reason otherwise.</summary>
		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES, owner R9 (2026-10-17: every square of connected still water stands
		/// at the same surface height, to within 1 cm, read from game state, not the picture): the per-body surface-gap read
		/// northstar/level_surface_bar.py makes. <paramref name="arg"/> = "x,z,w,h" (a rect of the current map) or "-" (the whole
		/// map). Returns "OK n worst G m;" then one "x,z:squares:gap:min:max" per body (metres; surfaces relative to ground,
		/// first square named), largest gap first, ';'-separated. Read only.</summary>
		public static string ProofLevelSurface(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation eng = map == null ? null : RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return "REFUSED no current map or no FlowWorks engine on it";
			}
			CellRect? rect = null;
			string[] p = (arg ?? "-").Split(',');
			if (p.Length == 4 && int.TryParse(p[0], out int x) && int.TryParse(p[1], out int z) && int.TryParse(p[2], out int w)
				&& int.TryParse(p[3], out int h))
			{
				rect = new CellRect(x, z, w, h);
			}
			else if ((arg ?? "-").Trim() != "-")
			{
				return "REFUSED arg must be x,z,w,h or -";
			}
			System.Globalization.CultureInfo inv = System.Globalization.CultureInfo.InvariantCulture;
			System.Collections.Generic.List<RM_SurfaceGap.Body> bodies = eng.SurfaceGaps(rect);
			var sb = new System.Text.StringBuilder();
			sb.Append("OK ").Append(bodies.Count).Append(" worst ")
				.Append((bodies.Count > 0 ? bodies[0].gapM : 0.0).ToString("F4", inv)).Append(" m;");
			for (int i = 0; i < bodies.Count; i++)
			{
				IntVec3 c = map.cellIndices.IndexToCell(bodies[i].firstCell);
				sb.Append(c.x).Append(',').Append(c.z).Append(':').Append(bodies[i].squares).Append(':')
					.Append(bodies[i].gapM.ToString("F4", inv)).Append(':').Append(bodies[i].minM.ToString("F4", inv)).Append(':')
					.Append(bodies[i].maxM.ToString("F4", inv)).Append(';');
			}
			return sb.ToString();
		}

		public static string ProofDeepLake(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation eng = map == null ? null : RM_SuperdeepTrap.EngineOf(map);
			string[] a = (arg ?? "").Split(';');
			if (eng == null || a.Length < 2)
			{
				return "REFUSED: needs paint;x;z;w;h;rim | form;x,z | stock;x,z;fraction | shape;x,z on a map with the engine";
			}
			if (a[0] == "paint")
			{
				if (a.Length != 6 || !int.TryParse(a[1], out int x0) || !int.TryParse(a[2], out int z0) || !int.TryParse(a[3], out int w)
					|| !int.TryParse(a[4], out int h) || !int.TryParse(a[5], out int rim))
				{
					return "REFUSED: paint;x;z;w;h;rim";
				}
				CellRect r = new CellRect(x0, z0, w, h);
				if (!r.InBounds(map))
				{
					return "REFUSED: the lake rect leaves the map";
				}
				int deep = 0, shallow = 0;
				foreach (IntVec3 c in r)
				{
					bool edge = c.x - x0 < rim || c.z - z0 < rim || x0 + w - 1 - c.x < rim || z0 + h - 1 - c.z < rim;
					map.terrainGrid.SetTerrain(c, edge ? TerrainDefOf.WaterShallow : TerrainDefOf.WaterDeep);
					if (edge) shallow++; else deep++;
				}
				return "PAINTED deep=" + deep + " shallow=" + shallow;
			}
			if (!Cell(a[1], out IntVec3 at) || !at.InBounds(map))
			{
				return "REFUSED: bad cell " + a[1];
			}
			RM_LiquidBody body = a[0] == "form" ? eng.Stock.BodyAt(map, at, eng) : eng.Stock.IndexedBodyAt(map, at);
			if (body == null)
			{
				return "REFUSED: no natural body at " + a[1];
			}
			if (a[0] == "form")
			{
				return "BODY id=" + body.id + " cells=" + body.cells.Count + " limitless=" + body.limitless + " truncated=" + body.truncated
					+ " capacity=" + body.capacity.ToString("F1") + " levelUnit=" + body.levelUnit.ToString("F3")
					+ " bedSum=" + RM_LiquidStock.BedSum(body, eng) + " deepest=" + eng.DeepestRecordedBed();
			}
			if (a[0] == "stock")
			{
				if (a.Length != 3 || !float.TryParse(a[2], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float f))
				{
					return "REFUSED: stock;x,z;fraction";
				}
				body.stock = UnityEngine.Mathf.Clamp01(f) * body.capacity;
				int rounds = eng.Stock.SettleRecession(map, body, eng);
				return "STOCK stock=" + body.stock.ToString("F1") + " capacity=" + body.capacity.ToString("F1") + " rounds=" + rounds
					+ " receded=" + body.receded.Count;
			}
			if (a[0] != "shape")
			{
				return "REFUSED: unknown mode " + a[0];
			}
			// The footprint read: wet/dry counts, the drawdown order (deepest dry bed vs shallowest wet bed), the steepest
			// N/S/E/W step between two dry squares (HollowDepthAt, what the climb rule reads) inside the deep water and anywhere,
			// the lakebed bands laid, and a terrain hash of the footprint (equal before draining and after refilling = exact).
			var inBody = new System.Collections.Generic.HashSet<IntVec3>(body.cells);
			int wet = 0, dry = 0, deepestDry = 0, maxDryBed = 0, minWetBed = int.MaxValue, stepAll = 0, stepDeep = 0;
			int lbShallow = 0, lbDeep = 0, lbAbyss = 0;
			IntVec3 deepestCell = IntVec3.Invalid, shelfCell = IntVec3.Invalid;
			long hash = 17;
			foreach (IntVec3 c in body.cells)
			{
				TerrainDef t = map.terrainGrid.TerrainAt(c);
				hash = unchecked(hash * 31 + (t?.shortHash ?? 0) * 7 + map.cellIndices.CellToIndex(c));
				int bed = eng.BedLevelsAt(c);
				if (eng.IsSourceCell(c))
				{
					wet++;
					minWetBed = System.Math.Min(minWetBed, bed);
					continue;
				}
				dry++;
				maxDryBed = System.Math.Max(maxDryBed, bed);
				int d = eng.HollowDepthAt(c);
				if (d > deepestDry) { deepestDry = d; deepestCell = c; }
				// the proof's walk-out start: the dry square just past the deep notch (5), nearest the lake's west edge
				if (d == RM_Volume.LevelsPerSquare + 1 && (!shelfCell.IsValid || c.x < shelfCell.x || (c.x == shelfCell.x && c.z < shelfCell.z)))
				{
					shelfCell = c;
				}
				if (t == RimMandrakeFlowWorks_DefOf.RM_Lakebed_Shallow) lbShallow++;
				else if (t == RimMandrakeFlowWorks_DefOf.RM_Lakebed_Deep) lbDeep++;
				else if (t == RimMandrakeFlowWorks_DefOf.RM_Lakebed_Abyss) lbAbyss++;
				foreach (IntVec3 n in new[] { c + IntVec3.East, c + IntVec3.North })
				{
					if (!inBody.Contains(n) || eng.IsSourceCell(n))
					{
						continue;
					}
					int s = System.Math.Abs(d - eng.HollowDepthAt(n));
					stepAll = System.Math.Max(stepAll, s);
					if (bed >= RM_Volume.LevelsPerSquare && eng.BedLevelsAt(n) >= RM_Volume.LevelsPerSquare)
					{
						stepDeep = System.Math.Max(stepDeep, s);
					}
				}
			}
			return "SHAPE wet=" + wet + " dry=" + dry + " receded=" + body.receded.Count + " deepestDry=" + deepestDry
				+ " maxDryBed=" + maxDryBed + " minWetBed=" + (wet > 0 ? minWetBed : 0) + " stepDeep=" + stepDeep + " stepAll=" + stepAll
				+ " lakebedShallow=" + lbShallow + " lakebedDeep=" + lbDeep + " lakebedAbyss=" + lbAbyss
				+ " deepestCell=" + (deepestCell.IsValid ? deepestCell.x + "," + deepestCell.z : "none")
				+ " shelfCell=" + (shelfCell.IsValid ? shelfCell.x + "," + shelfCell.z : "none")
				+ " hollows=" + RimMandrakeFlowWorksSettings.pondBedHollowEnabled + " stock=" + body.stock.ToString("F1")
				+ " capacity=" + body.capacity.ToString("F1") + " hash=" + hash;
		}

		/// <summary>PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS: build or remove a ramp without a job. arg "x,z;rot" (rot 0 N, 1 E, 2 S,
		/// 3 W; the ramp points uphill that way) spawns a wooden ramp for the player, honouring the placement rules; "x,z;off"
		/// destroys the ramp there. Returns "RAMP x,z rot=R joins=b gen=N" or REFUSED: reason.</summary>
		public static string ProofRamp(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 2 || !Cell(a[0], out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z;rot or x,z;off on the current map";
			}
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (a[1] == "off")
			{
				Thing r = RM_PitRamp.RampAt(map, c);
				if (r == null)
				{
					return "REFUSED: no ramp at " + a[0];
				}
				r.Destroy(DestroyMode.Deconstruct);
				return "RAMP " + a[0] + " removed gen=" + (eng?.ClimbGeneration ?? 0);
			}
			if (!int.TryParse(a[1], out int ri) || ri < 0 || ri > 3 || RM_PitRamp.Def == null)
			{
				return "REFUSED: rot must be 0..3 (or no RM_PitRamp def)";
			}
			var rot = new Rot4(ri);
			AcceptanceReport ok = new PlaceWorker_PitRamp().AllowsPlacing(RM_PitRamp.Def, c, rot, map);
			if (!ok.Accepted)
			{
				return "REFUSED: " + ok.Reason;
			}
			Thing ramp = ThingMaker.MakeThing(RM_PitRamp.Def, ThingDefOf.WoodLog);
			ramp.SetFaction(Faction.OfPlayer);
			GenSpawn.Spawn(ramp, c, map, rot);
			IntVec3 up = c + rot.FacingCell;
			bool joins = RM_PitRamp.Joins(map, c, up, RM_SuperdeepTrap.StepDepthAt(map, eng, c), RM_SuperdeepTrap.StepDepthAt(map, eng, up));
			return "RAMP " + a[0] + " rot=" + ri + " joins=" + joins + " gen=" + (eng?.ClimbGeneration ?? 0);
		}

		/// <summary>Capture down. arg = target pawn id: "VERDICT v held=b prisoner=b cell=x,z".</summary>
		public static string ProofCaptureDown(string pawnId)
		{
			Map map = Find.CurrentMap;
			Pawn p = map == null ? null : PawnById(map, pawnId);
			if (p == null)
			{
				return "REFUSED: no spawned pawn " + pawnId;
			}
			return "VERDICT " + RM_PitRooms.CaptureDownVerdict(p) + " held=" + RM_SuperdeepTrap.IsHeld(p)
				+ " prisoner=" + p.IsPrisonerOfColony + " cell=" + p.Position.x + "," + p.Position.z;
		}

		/// <summary>Lip service. arg "workerId;x,z;JobDefName": asks the PathFollower patch's own gate
		/// (ShouldServeFromLipFor) and the lip finder: "LIP serve=b kind=k lip=x,z lipSuperdeep=b dist=d".</summary>
		public static string ProofLip(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 3 || !Cell(a[1], out IntVec3 target) || !target.InBounds(map))
			{
				return "REFUSED: arg must be workerId;x,z;JobDefName";
			}
			Pawn w = PawnById(map, a[0]);
			JobDef job = DefDatabase<JobDef>.GetNamedSilentFail(a[2]);
			if (w == null || job == null)
			{
				return "REFUSED: no worker " + a[0] + " or no JobDef " + a[2];
			}
			bool serve = RM_PitRooms.ShouldServeFromLipFor(w, job, target, out RM_PitRoomMath.LipKind kind);
			if (!serve)
			{
				return "LIP serve=False kind=" + kind;
			}
			if (!RM_PitRooms.TryFindLipCell(w, target, kind, out IntVec3 lip))
			{
				return "LIP serve=True kind=" + kind + " lip=none";
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (ex == null)
			{
				return "REFUSED: no excavation engine on the current map";
			}
			return "LIP serve=True kind=" + kind + " lip=" + lip.x + "," + lip.z + " lipSuperdeep="
				+ ex.IsSuperdeepExcavation(lip) + " dist=" + lip.DistanceTo(target).ToString("0.##");
		}

		/// <summary>Phase 8 pump. arg "x,z" reads; "x,z;pour" / "x,z;draw" flips the mode as the gizmo does.
		/// "PUMP running=b moved=n pour=b tank=def:units".</summary>
		public static string ProofPump(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || !Cell(a[0], out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z[;pour|draw]";
			}
			Building_LiquidPump pump = c.GetFirstBuilding(map) as Building_LiquidPump;
			if (pump == null)
			{
				return "REFUSED: no RM_LiquidPump at " + c;
			}
			if (a.Length > 1)
			{
				if (a[1] != "pour" && a[1] != "draw")
				{
					return "REFUSED: verb must be pour or draw, got " + a[1];
				}
				pump.pourMode = a[1] == "pour";
			}
			PropertyInfo running = AccessTools.Property(typeof(Building_LiquidPump), "Running");
			Building_LiquidTank tank = null;
			foreach (IntVec3 n in GenAdj.CellsAdjacent8Way(pump))
			{
				if (n.InBounds(map) && n.GetFirstBuilding(map) is Building_LiquidTank t)
				{
					tank = t;
					break;
				}
			}
			return "PUMP running=" + (running?.GetValue(pump) ?? "?") + " moved=" + pump.Moved + " pour=" + pump.pourMode
				+ " tank=" + (tank == null ? "none" : (tank.storedLiquid?.defName ?? "empty") + ":" + tank.storedUnits);
		}

		/// <summary>EXCAVATION_WALL_ART_1 carrier. arg "x,z": regenerates the cell's section layer and reads it.
		/// "WALLS visible=b verts=n" (verts = the layer's built geometry for that whole section).</summary>
		public static string ProofWallFaces(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null || !Cell(arg, out IntVec3 c) || !c.InBounds(map))
			{
				return "REFUSED: arg must be x,z";
			}
			Section s = map.mapDrawer.SectionAt(c);
			SectionLayer layer = s?.GetLayer(typeof(SectionLayer_RMExcavationWalls));
			if (layer == null)
			{
				return "REFUSED: no SectionLayer_RMExcavationWalls on the section at " + c;
			}
			layer.Regenerate();
			int verts = 0;
			foreach (LayerSubMesh sm in layer.subMeshes)
			{
				verts += sm.verts.Count;
			}
			return "WALLS visible=" + layer.Visible + " verts=" + verts;
		}

		/// <summary>WRITES. arg "x;z;w;h": every excavated cell in the rect is drained (fill 0) and filled back in to the
		/// surface through the engine's own FillIn, so a plot an earlier chain or run dug starts pristine (MEASURED
		/// 2026-10-06: destroy_batch + Soil paint left a previous run's 3x3 pit under pit_fill_effects' 1x1 poison pit,
		/// the pirate stood on a dry cell, "got {}"; wall_faces read 76 -> 76 verts on cells already cut). The rect's dig-find
		/// rolled depths are forgotten too (DIG_RESET_REPAIR_ROLLED_DEPTH_REMEMBERS: they are saved and only grow, so a
		/// re-dug cell found nothing). "RESET cells=n levels=n rolled=n left=n".</summary>
		public static string ProofResetRect(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length != 4 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z)
				|| !int.TryParse(a[2], out int w) || !int.TryParse(a[3], out int h))
			{
				return "REFUSED: arg must be x;z;w;h on the current map";
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return "REFUSED: no excavation engine on the current map";
			}
			CellRect r = new CellRect(x, z, w, h).ClipInsideMap(map);
			int cells = 0, levels = 0, left = 0;
			// ExcavatedDepthAt, not DepthAt: DepthAt reads a natural liquid cell as SUPERDEEP, and FillIn cannot raise it
			// (the plot's Soil repaint removes it). MEASURED 2026-10-06: plot F "cells=1 levels=8 left=1".
			foreach (IntVec3 c in r)
			{
				if (eng.ExcavatedDepthAt(c) == 0)
				{
					continue;
				}
				cells++;
				eng.TrySetDriverFill(c, 0);
				for (int i = 0; i < 8 && eng.ExcavatedDepthAt(c) > 0; i++)
				{
					eng.FillIn(c);
					levels++;
				}
				if (eng.ExcavatedDepthAt(c) > 0)
				{
					left++;
				}
			}
			int rolled = eng.DigDiscovery?.ResetRolled(map, r) ?? 0;
			return "RESET cells=" + cells + " levels=" + levels + " rolled=" + rolled + " left=" + left;
		}
	}
}
