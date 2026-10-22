using System;
using System.Globalization;
using RimWorld;
using Verse;
using static RimMandrake.FlowWorks.RM_SheetMath;

namespace RimMandrake.FlowWorks.Sheet
{
	/// <summary>CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED: the bridge surface northstar/sheet_overflow_proof.py reads
	/// (jawa/static_call; contracts in that script's OWED_PROOFS). One string arg each, one line out: a word then key=value
	/// tokens; "REFUSED: why" on bad args. Read-only except ProofSheetSpill / ProofSheetFillIn (staging through the production
	/// entries) and ProofSheetPerf "reset".</summary>
	public static class RM_SheetProofs
	{
		private static string B(bool b) => b ? "True" : "False";

		private static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);

		private static bool Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused)
		{
			map = Find.CurrentMap;
			sheet = map?.GetComponent<RM_MapComponent_Sheet>();
			refused = map == null ? "REFUSED: no current map" : sheet == null ? "REFUSED: no RM_MapComponent_Sheet on the current map" : null;
			return refused == null;
		}

		private static bool Cell(string s, Map map, out IntVec3 c)
		{
			c = IntVec3.Invalid;
			string[] p = (s ?? "").Split(',');
			if (p.Length != 2 || !int.TryParse(p[0].Trim(), out int x) || !int.TryParse(p[1].Trim(), out int z))
			{
				return false;
			}
			c = new IntVec3(x, 0, z);
			return c.InBounds(map);
		}

		private static long DestroyedDl(Map map)
		{
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			return ex == null ? 0 : (long)Math.Round(ex.OverflowDestroyedTotal * (double)RM_Volume.UnitsPerLevel);
		}

		/// <summary>'-' → SHEETLEDGER (all dL; params = the kernel Params in force).</summary>
		public static string ProofSheetLedger(string arg)
		{
			if (!Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused))
			{
				return refused;
			}
			Params p = sheet.ProofParams;
			State s = sheet.ProofState;
			long In(Source k) => s == null ? 0 : s.In[(int)k];
			return "SHEETLEDGER enabled=" + B(RM_SheetSettings.sheetOverflowEnabled)
				+ " in=" + (s?.TotalIn ?? 0) + " inPump=" + In(Source.Pump) + " inRain=" + In(Source.Rain) + " inFlood=" + In(Source.Flood)
				+ " inFillIn=" + In(Source.FillIn) + " inGravity=" + In(Source.Gravity)
				+ " standing=" + (s?.Standing ?? 0) + " wet=" + (s?.WetCount ?? 0) + " returned=" + (s?.Returned ?? 0)
				+ " joined=" + (s?.JoinedLake ?? 0) + " soaked=" + (s?.Soaked ?? 0) + " evaporated=" + (s?.Evaporated ?? 0)
				+ " burned=" + (s?.Burned ?? 0) + " purged=" + (s?.Purged ?? 0) + " closes=" + B(s == null || s.LedgerCloses)
				+ " releaseLost=" + (map.GetComponent<RM_MapComponent_Excavation>()?.ReleaseLostDl ?? 0) + " burning=" + sheet.BurningCount
				+ " destroyedDl=" + DestroyedDl(map) + " pulse=" + (s?.Pulse ?? 0) + " pulseTicks=" + RimMandrakeFlowWorksSettings.PulseIntervalTicks
				+ " retention=" + p.RetentionDl + " minReceive=" + p.MinReceiveDl + " cap=" + p.SheetCapDl + " maxWet=" + p.MaxWetCells
				+ " irrigated=" + sheet.IrrigatedTotal;
		}

		/// <summary>x;z;w;h → SHEETRECT (edgeMaxDl = the deepest wet square with a dry open neighbour: the frontier).</summary>
		public static string ProofSheetRect(string arg)
		{
			if (!Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused))
			{
				return refused;
			}
			string[] a = (arg ?? "").Split(';');
			if (a.Length != 4 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z) || !int.TryParse(a[2], out int w)
				|| !int.TryParse(a[3], out int h) || w <= 0 || h <= 0)
			{
				return "REFUSED: arg must be x;z;w;h";
			}
			long dl = 0;
			int wet = 0, maxDl = 0, edge = 0, ice = 0, film = 0, sh = 0, pool = 0;
			foreach (IntVec3 c in CellRect.FromLimits(x, z, x + w - 1, z + h - 1).ClipInsideMap(map))
			{
				int v = sheet.DlAt(c);
				if (v <= 0)
				{
					continue;
				}
				dl += v;
				wet++;
				maxDl = Math.Max(maxDl, v);
				switch (sheet.TierAt(c))
				{
					case Tier.Ice: ice++; break;
					case Tier.Film: film++; break;
					case Tier.Sheet: sh++; break;
					case Tier.Pool: pool++; break;
				}
				for (int d = 0; d < 4; d++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[d];
					if (n.InBounds(map) && sheet.DlAt(n) == 0 && sheet.KindAt(n) == Kind.Open)
					{
						edge = Math.Max(edge, v);
						break;
					}
				}
			}
			return "SHEETRECT dl=" + dl + " wet=" + wet + " maxDl=" + maxDl + " edgeMaxDl=" + edge + " ice=" + ice + " film=" + film
				+ " sheet=" + sh + " pool=" + pool;
		}

		/// <summary>x,z → SHEETCELL dl tier kind stand.</summary>
		public static string ProofSheetCell(string arg)
		{
			if (!Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused))
			{
				return refused;
			}
			if (!Cell(arg, map, out IntVec3 c))
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			State s = sheet.ProofState;
			int stand = s == null ? 0 : s.Stand[map.cellIndices.CellToIndex(c)];
			return "SHEETCELL dl=" + sheet.DlAt(c) + " tier=" + sheet.TierAt(c) + " kind=" + sheet.KindAt(c) + " stand=" + stand
				+ " fluid=" + (sheet.FluidAt(c)?.defName ?? "-") + " burning=" + B(sheet.IsBurning(c));
		}

		/// <summary>x,z;dl;Source[;FluidDef] → STAGING through RM_MapComponent_Sheet.Offer (the production entry; the switches are
		/// respected). The fluid defaults to water; any FlowWorks FluidDef spills (owner 2026-10-22, all liquids).</summary>
		public static string ProofSheetSpill(string arg)
		{
			if (!Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused))
			{
				return refused;
			}
			string[] a = (arg ?? "").Split(';');
			if ((a.Length != 3 && a.Length != 4) || !Cell(a[0], map, out IntVec3 c) || !long.TryParse(a[1], out long dl) || dl <= 0
				|| !Enum.TryParse(a[2].Trim(), out Source src))
			{
				return "REFUSED: arg must be x,z;dl;Pump|Rain|Flood|FillIn|Gravity[;FluidDef]";
			}
			FluidDef fluid = a.Length == 4 ? DefDatabase<FluidDef>.GetNamedSilentFail(a[3].Trim()) : RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;
			if (fluid == null)
			{
				return "REFUSED: no FluidDef '" + a[3].Trim() + "'";
			}
			long got = sheet.Offer(c, dl, fluid, src);
			return "SPILL offered=" + dl + " accepted=" + got;
		}

		/// <summary>x,z → the engine's own fill-in of a wet dug square (FillIn → Displace). homeless = what no channel took.</summary>
		public static string ProofSheetFillIn(string arg)
		{
			if (!Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused))
			{
				return refused;
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null || !Cell(arg, map, out IntVec3 c) || !ex.IsExcavated(c))
			{
				return "REFUSED: arg must be x,z of a dug square on the current map";
			}
			long in0 = sheet.ProofState?.In[(int)Source.FillIn] ?? 0, d0 = DestroyedDl(map);
			ex.FillIn(c);
			long spilled = (sheet.ProofState?.In[(int)Source.FillIn] ?? 0) - in0, destroyed = DestroyedDl(map) - d0;
			return "FILLIN homeless=" + (spilled + destroyed) + " spilled=" + spilled + " destroyed=" + destroyed;
		}

		/// <summary>'-' → SHEETHASH (hash of RM_SheetMath.Save(state): the whole continuation state, §6 item 4).</summary>
		public static string ProofSheetHash(string arg)
		{
			if (!Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused))
			{
				return refused;
			}
			State s = sheet.ProofState;
			if (s == null)
			{
				return "SHEETHASH hash=0 pulse=0";
			}
			byte[] data = Save(s);
			ulong h = 1469598103934665603UL;
			foreach (byte b in data)
			{
				h = unchecked((h ^ b) * 1099511628211UL);
			}
			return "SHEETHASH hash=" + h.ToString("x16") + " pulse=" + s.Pulse;
		}

		/// <summary>'-' → what the loaded build carries (and which RM_SheetSettings fields a row may set).</summary>
		public static string ProofSheetFeatures(string arg)
		{
			return "FEATURES crops=True soak=" + B(RM_MapComponent_Sheet.SoakApi != null) + " capSetting=True capField=sheetCapCm"
				+ " cropDelayField=cropDrownPulses gravity=True floods=True pawns=True fire=True fuel=True";
		}

		/// <summary>'reset' | '-' → SHEETPERF since the last reset (averages per pulse; §6 item 12 records each separately).</summary>
		public static string ProofSheetPerf(string arg)
		{
			if (!Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused))
			{
				return refused;
			}
			if ((arg ?? "").Trim() == "reset")
			{
				sheet.PerfReset();
				return "SHEETPERF reset=True";
			}
			int n = Math.Max(1, sheet.perfPulses);
			return "SHEETPERF pulses=" + sheet.perfPulses + " kernelMs=" + F(sheet.perfKernelMs / n) + " pulseMs=" + F(sheet.perfPulseMs / n)
				+ " maxPulseMs=" + F(sheet.perfMaxPulseMs) + " allocB=" + sheet.perfAllocB + " dirtySections=" + sheet.perfDirty
				+ " terrainWrites=0 active=" + sheet.WetCells + " wetMax=" + sheet.perfWetMax;
		}
	
		/// <summary>x,z → lights the burnable spill there (D5) as a fire beside it would: 'SHEETFIRE lit=T|F burning=N burned=dL'.</summary>
		public static string ProofSheetIgnite(string arg)
		{
			if (!Ctx(out Map map, out RM_MapComponent_Sheet sheet, out string refused))
			{
				return refused;
			}
			if (!Cell(arg, map, out IntVec3 c))
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			bool lit = sheet.TryLight(c);
			return "SHEETFIRE lit=" + B(lit) + " burning=" + sheet.BurningCount + " burned=" + (sheet.ProofState?.Burned ?? 0);
		}
	}
}
