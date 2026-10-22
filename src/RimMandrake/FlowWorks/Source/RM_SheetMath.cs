using System;
using System.Collections.Generic;
using System.IO;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED, Stage 0: the OFFLINE sheet-water kernel
	/// (design/RimMandrake/canal_overflow_flooding_2026-10-21.md §3 Option C as amended by §6, owner answers §5).
	///
	/// A volume-carrying sheet of liquid standing ABOVE ground on undug cells, in whole decilitres. Pulsed (pillar 2,
	/// owner: engine-pulse movement is fine), integer, snapshot fluxes, cell-index order, no Rand. Nothing here is wired
	/// to the game yet: Stage 1 hangs it off RM_MapComponent_Excavation's pulse and feeds it the per-cell topology.
	///
	/// The ledger closes to the dL:
	///   In(all sources) == Standing + Returned + JoinedLake + Soaked + Evaporated + Burned + Purged
	/// Returned (into a dug cell / pit / limited lake with room) is an internal transfer the engine credits; the others
	/// are the disclosed exits (D6). Nothing is ever clamped away: a refused offer or flux stays where it was.
	///
	/// Owner rulings carried as data here: D2 sources (pump, rain, flood, fill-in, gravity feed); D3 crop timer (a crop
	/// under standing overflow dies after <see cref="Params.CropKillPulses"/>, i.e. 1 week; before that it irrigates,
	/// reported per cell); D4 doors leak slowly (edge conductance <see cref="Params.DoorLeakPermille"/>); D8 sheets lie
	/// level (each connected saturated puddle is levelled exactly every pulse, <see cref="Params.LevelBasins"/>; the
	/// diffusion sweeps only spread it to new ground); D9 retention and micro-relief are physical (they decide where a
	/// spill stops and where puddles linger); D10 a sheet below its fluid's freezing point turns to its own ice tier,
	/// keeping every dL, and thaws back; lowering the sheet cap stops further filling and deletes nothing.
	///
	/// ⛔ Verse-free: compiled into Source/SelfTest/ as the production file.
	/// </summary>
	public static class RM_SheetMath
	{
		public const int KernelVersion = 2; // 2: D8 levelling, D10 ice tier (no v1 saves exist)

		/// <summary>1 cm of liquid over one square (2 m²) = 20 L = 200 dL.</summary>
		public const int DlPerCm = RM_Volume.UnitsPerLevel / RM_Volume.CentimetresPerNotch;

		/// <summary>One RimWorld week at the default 250-tick pulse: 7 × 60,000 / 250.</summary>
		public static int PulsesFor(int ticks, int pulseIntervalTicks) =>
			pulseIntervalTicks <= 0 ? 0 : (ticks + pulseIntervalTicks - 1) / pulseIntervalTicks;

		public const int TicksPerWeek = 7 * 60000;

		/// <summary>What a cell is to the sheet. The engine maps the map onto these (Stage 1); the kernel never reads Verse.</summary>
		public enum Kind : byte
		{
			Open = 0,      // undug, open ground: may hold sheet
			Blocked = 1,   // wall, edifice, foundation, closed sluice, map edge
			Door = 2,      // holds sheet; every edge touching it passes DoorLeakPermille of the normal flux (D4)
			Grate = 3,     // FlowWorks grate/open sluice/flow door: passes like open ground
			Receiver = 4,  // dug cell, pit, SUPERDEEP or LIMITED lake: takes mobile water up to its room (internal transfer)
			Sink = 5,      // limitless natural water: takes all mobile water, disclosed as "joined the lake"
		}

		public enum Source : byte { Pump = 0, Rain = 1, Flood = 2, FillIn = 3, Gravity = 4 }
		public const int SourceCount = 5;

		/// <summary>Ice (D10) is its own tier: the same dL, frozen in place. It is drawn as ice, neither flows, returns nor
		/// soaks, and pauses the D3 crop timer; it thaws back to the depth tier its dL calls for.</summary>
		public enum Tier : byte { None = 0, Film = 1, Sheet = 2, Pool = 3, Ice = 4 }

		/// <summary>Per-fluid behaviour (index = fluid id; 0 is "none" and never used).</summary>
		public struct FluidRule
		{
			public int InfiltrationPermille; // × the cell's soak rate
			public int EvaporationPermille;  // × the cell's evaporation rate
			public int FreezeDeciC;          // D10: freezes at or below this (tenths of °C); water 0
			public bool NeverFreezes;        // fuels and the like
		}

		public sealed class Params
		{
			public int SweepsPerPulse = 3;
			public int RetentionDl = DlPerCm;            // held moisture: below this nothing flows (§6 item 6)
			public int MinReceiveDl = DlPerCm / 2;        // q_min: a dry cell is never wetted by less (§6 item 6)
			public int SheetCapDl = 50 * DlPerCm;         // 0.5 m
			public int MaxWetCells = 4000;
			public int MaxDonorsPerSweep = int.MaxValue;  // the work cap, separate from the wet cap (§6 item 5)
			public int ReliefDl = DlPerCm;                // micro-relief amplitude ±1 cm (D9: physical)
			public bool LevelBasins = true;               // D8: sheets lie level (false = the diffusion kernel alone, for tests)
			public int ThawMarginDeciC = 10;              // D10: ice thaws only 1 °C above the freezing point (no flapping)
			public int DoorLeakPermille = 50;             // D4: a door edge passes 5% of the normal flux
			public int SheetUpDl = 3 * DlPerCm, SheetDownDl = 2 * DlPerCm;
			public int PoolUpDl = 15 * DlPerCm, PoolDownDl = 13 * DlPerCm;
			public int CropKillPulses = PulsesFor(TicksPerWeek, 250); // D3: 1 week of standing overflow
			public Tier CropStandMinTier = Tier.Sheet;    // "standing overflow"; a film only irrigates
			public int SleepAfterPulses = 4;
		}

		public struct SpillOffer
		{
			public int[] LipNearestFirst; // cells nearest the inflow first (§6 item 8); the engine walks the body outward
			public int AmountDl;
			public byte Fluid;
			public Source From;
		}

		/// <summary>Disclosed per-pulse effects for the engine to apply (Stage 2): irrigation and crop deaths.</summary>
		public sealed class PulseReport
		{
			public readonly List<(int cell, int dl)> Soaked = new List<(int, int)>();
			public readonly List<int> CropKilled = new List<int>();
			public readonly List<(int cell, Tier from, Tier to)> TierChanged = new List<(int, Tier, Tier)>();
			public readonly List<(int cell, int dl)> Returned = new List<(int, int)>(); // credit these through the engine
			public void Clear() { Soaked.Clear(); CropKilled.Clear(); TierChanged.Clear(); Returned.Clear(); }
		}

		/// <summary>The map's topology and rates as the engine sees it this pulse. NOT persisted by the kernel: the
		/// engine rebuilds it from authoritative state (§6 item 7).</summary>
		public sealed class World
		{
			public readonly int W, H;
			public readonly Kind[] Kinds;
			public readonly int[] RoomDl;          // Receiver: room left; Sink ignores it
			public readonly byte[] BodyFluid;      // Receiver/Sink: the body's fluid (0 = empty, takes any)
			public readonly int[] SoakMilliDl;     // per pulse, by base-terrain class (0 on rock, floors, ice, mud, water)
			public readonly int[] EvapMilliDl;     // per pulse, by temperature and roof (0 at or below 0 °C)
			public readonly int[] TempDeciC;       // D10: outdoor/room temperature in tenths of °C (default 20 °C)
			public FluidRule[] Fluids = new FluidRule[256];

			public World(int w, int h)
			{
				W = w; H = h;
				int n = w * h;
				Kinds = new Kind[n]; RoomDl = new int[n]; BodyFluid = new byte[n];
				SoakMilliDl = new int[n]; EvapMilliDl = new int[n]; TempDeciC = new int[n];
				for (int c = 0; c < n; c++) TempDeciC[c] = 200;
				for (int f = 1; f < 256; f++) Fluids[f] = new FluidRule { InfiltrationPermille = 1000, EvaporationPermille = 1000 };
			}

			public World Clone()
			{
				var c = new World(W, H);
				Array.Copy(Kinds, c.Kinds, Kinds.Length); Array.Copy(RoomDl, c.RoomDl, RoomDl.Length);
				Array.Copy(BodyFluid, c.BodyFluid, BodyFluid.Length);
				Array.Copy(SoakMilliDl, c.SoakMilliDl, SoakMilliDl.Length); Array.Copy(EvapMilliDl, c.EvapMilliDl, EvapMilliDl.Length);
				Array.Copy(TempDeciC, c.TempDeciC, TempDeciC.Length);
				c.Fluids = (FluidRule[])Fluids.Clone();
				return c;
			}

			public static bool HoldsSheet(Kind k) => k == Kind.Open || k == Kind.Door || k == Kind.Grate;
		}

		/// <summary>Everything a continuation needs (§6 item 4). Save/Load round-trips it exactly.</summary>
		public sealed class State
		{
			public readonly int W, H;
			public int[] Dl;            // sheet water per cell
			public byte[] Fluid;        // 0 = dry
			public int[] SoakRem, EvapRem; // milli-dL remainders
			public Tier[] Tiers;        // hysteresis state
			public int[] Stand;         // D3: consecutive pulses at CropStandMinTier or above (saturates at kill+1)
			public byte[] Calm;         // pulses without incident flux; >= SleepAfterPulses = asleep (skips flow only)
			public uint Salt;
			public long Pulse;
			public readonly long[] In = new long[SourceCount];
			public long Returned, JoinedLake, Soaked, Evaporated, Burned, Purged;
			internal readonly List<int> Occ = new List<int>(); // wet cells, ascending; rebuilt on load
			internal readonly List<(int cell, Tier was)> Dried = new List<(int, Tier)>(); // reported by the next pulse; not saved (a dry cell has no picture to keep)

			public State(int w, int h, uint salt)
			{
				W = w; H = h; Salt = salt;
				int n = w * h;
				Dl = new int[n]; Fluid = new byte[n]; SoakRem = new int[n]; EvapRem = new int[n];
				Tiers = new Tier[n]; Stand = new int[n]; Calm = new byte[n];
			}

			public long TotalIn { get { long s = 0; for (int i = 0; i < SourceCount; i++) s += In[i]; return s; } }
			public long Standing { get { long s = 0; foreach (int c in Occ) s += Dl[c]; return s; } }
			public long TotalOut => Returned + JoinedLake + Soaked + Evaporated + Burned + Purged;
			public int WetCount => Occ.Count;
			public bool LedgerCloses => TotalIn == Standing + TotalOut;
		}

		// ── relief (§3 step 2, §6 item 13): a fixed integer hash with a persisted salt ──

		public static int Relief(uint salt, int cell, int amplitude)
		{
			if (amplitude <= 0) return 0;
			uint x = (uint)cell * 0x9E3779B1u ^ salt;
			x ^= x >> 16; x *= 0x7FEB352Du; x ^= x >> 15; x *= 0x846CA68Bu; x ^= x >> 16;
			return (int)(x % (uint)(2 * amplitude + 1)) - amplitude;
		}

		private static readonly int[] DX = { 0, 1, 0, -1 }; // N, E, S, W in RimWorld's (x, z): index = z * W + x
		private static readonly int[] DZ = { 1, 0, -1, 0 };

		private static int Neighbour(int w, int h, int cell, int d)
		{
			int x = cell % w + DX[d], z = cell / w + DZ[d];
			return x < 0 || z < 0 || x >= w || z >= h ? -1 : z * w + x;
		}

		private static bool Compatible(byte a, byte b) => a == 0 || b == 0 || a == b;

		// ── spill (§3 step 1, §6 items 1/8): offer → accepted dL; the caller debits exactly that ──

		/// <summary>Resolves every offer of this pulse at once, in a stable order that does not depend on the order the
		/// caller collected them in (fluid, then first lip cell, then source, then amount, then the lip list). Each offer
		/// fills its lips nearest-first up to the sheet cap; a dry lip is taken only under the wet-cell cap, and never by
		/// a different fluid. Returns the dL accepted per offer, in the caller's order. The rest is refused back to the
		/// inflow (back-pressure), never destroyed.</summary>
		public static int[] ResolveSpills(State s, World w, Params p, IList<SpillOffer> offers)
		{
			var order = new int[offers.Count];
			for (int i = 0; i < order.Length; i++) order[i] = i;
			Array.Sort(order, (a, b) => CompareOffers(offers[a], offers[b]));
			var accepted = new int[offers.Count];
			bool added = false;
			foreach (int oi in order)
			{
				SpillOffer o = offers[oi];
				if (o.AmountDl <= 0 || o.Fluid == 0 || o.LipNearestFirst == null) continue;
				int left = o.AmountDl;
				foreach (int c in o.LipNearestFirst)
				{
					if (left == 0) break;
					if (c < 0 || c >= s.Dl.Length || !World.HoldsSheet(w.Kinds[c])) continue;
					if (!Compatible(s.Fluid[c], o.Fluid)) continue;
					if (s.Tiers[c] == Tier.Ice) continue; // D10: an iced lip takes no new spill; the next lip is tried
					if (s.Dl[c] == 0 && s.Occ.Count >= p.MaxWetCells) continue;
					int room = p.SheetCapDl - s.Dl[c];
					if (room <= 0) continue;
					int take = Math.Min(room, left);
					if (s.Dl[c] == 0) { s.Occ.Add(c); added = true; }
					s.Dl[c] += take; s.Fluid[c] = o.Fluid;
					left -= take;
					WakeAround(s, w, c);
				}
				accepted[oi] = o.AmountDl - left;
				s.In[(int)o.From] += accepted[oi];
			}
			if (added) s.Occ.Sort();
			return accepted;
		}

		private static int CompareOffers(SpillOffer a, SpillOffer b)
		{
			int r = a.Fluid.CompareTo(b.Fluid); if (r != 0) return r;
			int la = a.LipNearestFirst?.Length ?? 0, lb = b.LipNearestFirst?.Length ?? 0;
			r = (la > 0 ? a.LipNearestFirst[0] : -1).CompareTo(lb > 0 ? b.LipNearestFirst[0] : -1); if (r != 0) return r;
			r = ((int)a.From).CompareTo((int)b.From); if (r != 0) return r;
			r = a.AmountDl.CompareTo(b.AmountDl); if (r != 0) return r;
			r = la.CompareTo(lb); if (r != 0) return r;
			for (int i = 0; i < la; i++) { r = a.LipNearestFirst[i].CompareTo(b.LipNearestFirst[i]); if (r != 0) return r; }
			return 0;
		}

		/// <summary>A topology or neighbour change wakes the cell and its four neighbours (§3 step 6, §6 item 9).</summary>
		public static void WakeAround(State s, World w, int cell)
		{
			s.Calm[cell] = 0;
			for (int d = 0; d < 4; d++) { int n = Neighbour(s.W, s.H, cell, d); if (n >= 0) s.Calm[n] = 0; }
		}

		// ── the pulse ──

		private struct Flux { public int From, To, Dl, MinNew; public byte Fluid; }

		/// <summary>One engine pulse: freeze/thaw (D10), K relax sweeps, basin levelling (D8), return/absorb, losses on every wet cell, tiers, crop timer, sleep.
		/// Spills are resolved before it by <see cref="ResolveSpills"/>.</summary>
		public static void Pulse(State s, World w, Params p, PulseReport rep)
		{
			rep?.Clear();
			int n = s.Dl.Length;
			var touched = new bool[n];
			Freeze(s, w, p, rep);
			for (int k = 0; k < p.SweepsPerPulse; k++) Sweep(s, w, p, touched);
			if (p.LevelBasins) Level(s, w, p, touched);
			ReturnAndAbsorb(s, w, p, rep, touched);
			Losses(s, w, p, rep);
			Tiers(s, p, rep);
			// sleep counters: every wet cell with no flux this pulse gets calmer; a touched one wakes itself and its
			// neighbours (a neighbour that moved may have opened a gradient)
			foreach (int c in s.Occ)
				if (!touched[c]) s.Calm[c] = (byte)Math.Min(255, s.Calm[c] + 1);
			for (int c = 0; c < n; c++) if (touched[c]) WakeAround(s, w, c);
			s.Pulse++;
		}

		private static void Sweep(State s, World w, Params p, bool[] touched)
		{
			int W = s.W, H = s.H;
			var props = new List<Flux>();
			var f4 = new int[4]; var nb4 = new int[4];
			int donors = 0;
			// Phase A: proposals from the snapshot (nothing is applied until phase D, so order cannot matter)
			foreach (int i in s.Occ)
			{
				if (s.Calm[i] >= p.SleepAfterPulses) continue;
				if (!World.HoldsSheet(w.Kinds[i])) continue;
				if (s.Tiers[i] == Tier.Ice) continue;
				int mobile = s.Dl[i] - p.RetentionDl;
				if (mobile <= 0) continue;
				if (donors++ >= p.MaxDonorsPerSweep) break;
				long Hi = (long)s.Dl[i] + Relief(s.Salt, i, p.ReliefDl);
				long sum = 0;
				for (int d = 0; d < 4; d++)
				{
					f4[d] = 0; int j = nb4[d] = Neighbour(W, H, i, d);
					if (j < 0 || !World.HoldsSheet(w.Kinds[j])) continue;
					if (!Compatible(s.Fluid[j], s.Fluid[i])) continue;
					if (s.Tiers[j] == Tier.Ice) continue;
					long Hj = (long)s.Dl[j] + Relief(s.Salt, j, p.ReliefDl);
					long diff = Hi - Hj;
					if (diff < 2) continue;
					long f = diff / 5;
					if (w.Kinds[i] == Kind.Door || w.Kinds[j] == Kind.Door) f = f * p.DoorLeakPermille / 1000;
					if (f < 1) f = 1; // no dead zone (§6 item 13): f ≤ diff/2 always, so no overshoot
					f4[d] = (int)Math.Min(f, int.MaxValue);
					sum += f4[d];
				}
				if (sum == 0) continue;
				if (sum > mobile)
				{
					// virtual-pipes outflow limit in integers; the remainder 1 dL each in N,E,S,W order
					long given = 0; var want = (int[])f4.Clone();
					for (int d = 0; d < 4; d++) { f4[d] = (int)(want[d] * (long)mobile / sum); given += f4[d]; }
					for (int d = 0; d < 4 && given < mobile; d++) if (f4[d] < want[d]) { f4[d]++; given++; }
				}
				for (int d = 0; d < 4; d++)
				{
					if (f4[d] <= 0) continue;
					int j = nb4[d];
					// never dust-thin new cells; except under a door, whose leak is slow by design (D4) and would
					// otherwise never wet the door cell at all
					int minNew = w.Kinds[i] == Kind.Door || w.Kinds[j] == Kind.Door ? 1 : p.MinReceiveDl;
					if (s.Dl[j] == 0 && f4[d] < minNew) continue;
					props.Add(new Flux { From = i, To = j, Dl = f4[d], MinNew = minNew, Fluid = s.Fluid[i] });
				}
			}
			if (props.Count == 0) return;
			// Phase B: fluid arbitration on dry receivers: the lowest fluid id wins; the loser stays upstream
			var winner = new Dictionary<int, byte>();
			foreach (var fx in props)
				if (s.Dl[fx.To] == 0 && (!winner.TryGetValue(fx.To, out byte b) || fx.Fluid < b)) winner[fx.To] = fx.Fluid;
			// Phase C: receiver room and the wet-cell cap resolved before commit, in donor-index then N,E,S,W order
			var reserved = new Dictionary<int, int>();
			int wet = s.Occ.Count;
			var acc = new List<Flux>(props.Count);
			foreach (var fx0 in props)
			{
				Flux fx = fx0;
				int j = fx.To;
				if (s.Dl[j] == 0 && winner[j] != fx.Fluid) continue;
				reserved.TryGetValue(j, out int r);
				bool dryNew = s.Dl[j] == 0 && r == 0;
				if (dryNew && wet >= p.MaxWetCells) continue;
				int room = p.SheetCapDl - s.Dl[j] - r;
				if (room <= 0) continue;
				if (fx.Dl > room) fx.Dl = room;
				if (dryNew && fx.Dl < fx.MinNew) continue;
				reserved[j] = r + fx.Dl;
				if (dryNew) wet++;
				acc.Add(fx);
			}
			// Phase D: commit
			bool added = false;
			foreach (var fx in acc)
			{
				s.Dl[fx.From] -= fx.Dl;
				if (s.Dl[fx.To] == 0) { s.Occ.Add(fx.To); added = true; }
				s.Dl[fx.To] += fx.Dl; s.Fluid[fx.To] = fx.Fluid;
				touched[fx.From] = touched[fx.To] = true;
				WakeAround(s, w, fx.To);
			}
			Compact(s, added);
		}

		/// <summary>§3 step 3 / §6 item 1: mobile water beside a Receiver with room drains into it (internal transfer,
		/// reported for the engine to credit); beside a Sink it joins the lake (disclosed). A full or foreign-fluid
		/// receiver refuses.</summary>
		private static void ReturnAndAbsorb(State s, World w, Params p, PulseReport rep, bool[] touched)
		{
			var credit = new Dictionary<int, int>();
			foreach (int i in s.Occ)
			{
				if (!World.HoldsSheet(w.Kinds[i])) continue;
				if (s.Tiers[i] == Tier.Ice) continue;
				int mobile = s.Dl[i] - p.RetentionDl;
				for (int d = 0; d < 4 && mobile > 0; d++)
				{
					int j = Neighbour(s.W, s.H, i, d);
					if (j < 0) continue;
					Kind kj = w.Kinds[j];
					if (kj != Kind.Receiver && kj != Kind.Sink) continue;
					if (!Compatible(w.BodyFluid[j], s.Fluid[i])) continue;
					int give;
					if (kj == Kind.Sink) { give = mobile; s.JoinedLake += give; }
					else
					{
						give = Math.Min(mobile, w.RoomDl[j]);
						if (give <= 0) continue;
						w.RoomDl[j] -= give; s.Returned += give;
						if (w.BodyFluid[j] == 0) w.BodyFluid[j] = s.Fluid[i];
						credit.TryGetValue(j, out int c0); credit[j] = c0 + give;
					}
					s.Dl[i] -= give; mobile -= give; touched[i] = true;
				}
			}
			if (rep != null) { var keys = new List<int>(credit.Keys); keys.Sort(); foreach (int k in keys) rep.Returned.Add((k, credit[k])); }
			Compact(s, false);
		}

		/// <summary>§3 step 4, §6 item 3: losses run on EVERY wet cell every pulse (asleep or not), integer dL with the
		/// remainder carried. Soak is reported per cell: it is the irrigation (D3).</summary>
		private static void Losses(State s, World w, Params p, PulseReport rep)
		{
			foreach (int c in s.Occ)
			{
				FluidRule fr = w.Fluids[s.Fluid[c]];
				long soakRate = s.Tiers[c] == Tier.Ice ? 0 : (long)w.SoakMilliDl[c] * fr.InfiltrationPermille / 1000; // frozen: no soak
				long evapRate = (long)w.EvapMilliDl[c] * fr.EvaporationPermille / 1000;
				if (soakRate > 0)
				{
					long acc = s.SoakRem[c] + soakRate;
					int take = (int)Math.Min(acc / 1000, s.Dl[c]);
					s.SoakRem[c] = (int)(acc % 1000);
					if (take > 0) { s.Dl[c] -= take; s.Soaked += take; rep?.Soaked.Add((c, take)); }
				}
				if (evapRate > 0)
				{
					long acc = s.EvapRem[c] + evapRate;
					int take = (int)Math.Min(acc / 1000, s.Dl[c]);
					s.EvapRem[c] = (int)(acc % 1000);
					if (take > 0) { s.Dl[c] -= take; s.Evaporated += take; }
				}
				// a loss lowers this cell: a sleeping neighbour still holding MOBILE water wakes (no stranded water);
				// neighbours at or below retention stay asleep, so a settled puddle stays cheap
				if (soakRate > 0 || evapRate > 0)
					for (int d = 0; d < 4; d++)
					{
						int j = Neighbour(s.W, s.H, c, d);
						if (j >= 0 && s.Dl[j] > p.RetentionDl) s.Calm[j] = 0;
					}
			}
			Compact(s, false);
		}

		/// <summary>§3 step 5: tiers with hysteresis; only a tier change is reported (bounds picture writes). Then the
		/// D3 crop timer: consecutive pulses at CropStandMinTier or above; fires once at CropKillPulses; resets below.</summary>
		private static void Tiers(State s, Params p, PulseReport rep)
		{
			// cells that dried this pulse are no longer in Occ but may still carry a tier: they are swept by Compact
			foreach (int c in s.Occ)
			{
				if (s.Tiers[c] == Tier.Ice) continue; // D10: ice holds its tier until Freeze thaws it; the crop timer pauses
				Tier t0 = s.Tiers[c], t = NextTier(t0, s.Dl[c], p);
				if (t != t0) { s.Tiers[c] = t; rep?.TierChanged.Add((c, t0, t)); }
				if (t >= p.CropStandMinTier)
				{
					if (s.Stand[c] <= p.CropKillPulses) s.Stand[c]++;
					if (s.Stand[c] == p.CropKillPulses) rep?.CropKilled.Add(c);
				}
				else s.Stand[c] = 0;
			}
			if (rep != null)
				foreach (var (c, was) in s.Dried) rep.TierChanged.Add((c, was, Tier.None));
			s.Dried.Clear();
		}

		public static Tier NextTier(Tier t, int dl, Params p)
		{
			if (dl <= 0) return Tier.None;
			Tier r = t == Tier.None || t == Tier.Ice ? Tier.Film : t;
			if (r < Tier.Sheet && dl >= p.SheetUpDl) r = Tier.Sheet;
			if (r < Tier.Pool && dl >= p.PoolUpDl) r = Tier.Pool;
			if (r == Tier.Pool && dl < p.PoolDownDl) r = Tier.Sheet;
			if (r == Tier.Sheet && dl < p.SheetDownDl) r = Tier.Film;
			return r;
		}

		/// <summary>D10: a wet cell at or below its fluid's freezing point turns to the Ice tier, keeping its dL; ice thaws
		/// only <see cref="Params.ThawMarginDeciC"/> above it, back to the depth tier its dL calls for. Runs first in the
		/// pulse, so a cell frozen this pulse neither flows nor returns.</summary>
		private static void Freeze(State s, World w, Params p, PulseReport rep)
		{
			foreach (int c in s.Occ)
			{
				FluidRule fr = w.Fluids[s.Fluid[c]];
				Tier t0 = s.Tiers[c];
				if (t0 != Tier.Ice)
				{
					if (fr.NeverFreezes || w.TempDeciC[c] > fr.FreezeDeciC) continue;
					s.Tiers[c] = Tier.Ice;
					s.Calm[c] = 0;
				}
				else
				{
					if (!fr.NeverFreezes && w.TempDeciC[c] < fr.FreezeDeciC + p.ThawMarginDeciC) continue;
					s.Tiers[c] = NextTier(Tier.None, s.Dl[c], p);
					WakeAround(s, w, c);
				}
				rep?.TierChanged.Add((c, t0, s.Tiers[c]));
			}
		}

		/// <summary>D8, owner card 2026-10-22: "sheets lie level". Every connected puddle of SATURATED liquid (cells at or
		/// above retention, same fluid, not ice, not over the sheet cap, joined N/E/S/W; a door is never a member, so its
		/// leak stays slow, D4) is levelled exactly: one surface L over relief r_c, each cell holding clamp(L − r_c,
		/// retention, cap), the dL left over laid 1 dL each on the lowest cells (relief, then index). Diffusion still does
		/// the spreading onto new ground (finite extent, §6 item 6); this removes its slow tail and its 1-dL staircase.
		/// Conserves each puddle to the dL. A puddle whose every cell is asleep is skipped (levelling is idempotent).
		/// Over-cap cells (a lowered cap, D10) are left out and drain by the sweeps.</summary>
		private static void Level(State s, World w, Params p, bool[] touched)
		{
			var seen = new bool[s.Dl.Length];
			var comp = new List<int>();
			var stack = new Stack<int>();
			foreach (int seed in s.Occ)
			{
				if (seen[seed] || !LevelMember(s, w, p, seed)) continue;
				comp.Clear();
				seen[seed] = true; stack.Push(seed);
				bool awake = false;
				while (stack.Count > 0)
				{
					int c = stack.Pop();
					comp.Add(c);
					if (s.Calm[c] < p.SleepAfterPulses) awake = true;
					for (int d = 0; d < 4; d++)
					{
						int j = Neighbour(s.W, s.H, c, d);
						if (j < 0 || seen[j] || s.Fluid[j] != s.Fluid[seed] || !LevelMember(s, w, p, j)) continue;
						seen[j] = true; stack.Push(j);
					}
				}
				if (!awake || comp.Count < 2) continue;
				LevelPuddle(s, p, comp, touched);
			}
		}

		private static bool LevelMember(State s, World w, Params p, int c) =>
			s.Dl[c] >= p.RetentionDl && s.Dl[c] <= p.SheetCapDl && s.Tiers[c] != Tier.Ice
			&& (w.Kinds[c] == Kind.Open || w.Kinds[c] == Kind.Grate);

		private static void LevelPuddle(State s, Params p, List<int> comp, bool[] touched)
		{
			int m = comp.Count, R = p.RetentionDl, cap = p.SheetCapDl;
			var rel = new long[m];
			long V = 0, lo = long.MaxValue, hi = long.MinValue;
			for (int k = 0; k < m; k++)
			{
				rel[k] = Relief(s.Salt, comp[k], p.ReliefDl);
				V += s.Dl[comp[k]];
				lo = Math.Min(lo, rel[k] + R); hi = Math.Max(hi, rel[k] + cap);
			}
			long Fill(long L)
			{
				long t = 0;
				for (int k = 0; k < m; k++) t += Math.Max(R, Math.Min(cap, L - rel[k]));
				return t;
			}
			// the highest surface L with Fill(L) ≤ V: Fill(lo) = m·R ≤ V (every member is saturated), Fill(hi) = m·cap ≥ V
			long a = lo, b = hi;
			while (a < b) { long mid = a + (b - a + 1) / 2; if (Fill(mid) <= V) a = mid; else b = mid - 1; }
			long L0 = a, left = V - Fill(L0);
			// the cells that would rise by one at L0 + 1 take the remainder, lowest relief first, then cell index
			var next = new int[m];
			var order = new List<int>(m);
			for (int k = 0; k < m; k++)
			{
				long h0 = L0 - rel[k];
				next[k] = (int)Math.Max(R, Math.Min(cap, h0));
				if (h0 + 1 > R && h0 + 1 <= cap) order.Add(k);
			}
			order.Sort((x, y) => { int r = rel[x].CompareTo(rel[y]); return r != 0 ? r : comp[x].CompareTo(comp[y]); });
			for (int q = 0; q < order.Count && left > 0; q++) { next[order[q]]++; left--; }
			if (left != 0) throw new InvalidOperationException("sheet levelling lost " + left + " dL"); // unreachable: Fill(L0+1) > V
			for (int k = 0; k < m; k++)
			{
				int c = comp[k];
				if (next[k] == s.Dl[c]) continue;
				s.Dl[c] = next[k];
				touched[c] = true;
			}
		}

		/// <summary>Drops dried cells from the wet list (fluid, remainders, timers and tier cleared) and re-sorts if cells
		/// were added. A dried cell is dry: its loss remainders go with it, which is not water (they are &lt; 1 dL).</summary>
		private static void Compact(State s, bool resort)
		{
			if (resort) { s.Occ.Sort(); Dedupe(s.Occ); }
			int k = 0;
			for (int i = 0; i < s.Occ.Count; i++)
			{
				int c = s.Occ[i];
				if (s.Dl[c] > 0) { s.Occ[k++] = c; continue; }
				if (s.Tiers[c] != Tier.None) s.Dried.Add((c, s.Tiers[c]));
				s.Fluid[c] = 0; s.SoakRem[c] = 0; s.EvapRem[c] = 0; s.Stand[c] = 0; s.Calm[c] = 0; s.Tiers[c] = Tier.None;
			}
			s.Occ.RemoveRange(k, s.Occ.Count - k);
		}

		private static void Dedupe(List<int> l)
		{
			int k = 0;
			for (int i = 0; i < l.Count; i++) if (k == 0 || l[k - 1] != l[i]) l[k++] = l[i];
			l.RemoveRange(k, l.Count - k);
		}

		/// <summary>"Dry all spilled liquid now" (§3, §6 item 14 D7): a disclosed purge, never a silent one.</summary>
		public static long PurgeAll(State s)
		{
			long sum = 0;
			foreach (int c in s.Occ) { sum += s.Dl[c]; s.Dl[c] = 0; }
			s.Purged += sum;
			Compact(s, false);
			return sum;
		}

		// ── persistence (§6 item 4): everything a continuation needs, versioned ──

		public static byte[] Save(State s)
		{
			using (var ms = new MemoryStream())
			using (var bw = new BinaryWriter(ms))
			{
				bw.Write(KernelVersion); bw.Write(s.W); bw.Write(s.H); bw.Write(s.Salt); bw.Write(s.Pulse);
				for (int i = 0; i < SourceCount; i++) bw.Write(s.In[i]);
				bw.Write(s.Returned); bw.Write(s.JoinedLake); bw.Write(s.Soaked); bw.Write(s.Evaporated); bw.Write(s.Burned); bw.Write(s.Purged);
				// sparse: only wet cells carry state (a dry cell's fields are all zero by Compact)
				bw.Write(s.Occ.Count);
				foreach (int c in s.Occ)
				{
					bw.Write(c); bw.Write(s.Dl[c]); bw.Write(s.Fluid[c]); bw.Write(s.SoakRem[c]); bw.Write(s.EvapRem[c]);
					bw.Write((byte)s.Tiers[c]); bw.Write(s.Stand[c]); bw.Write(s.Calm[c]);
				}
				bw.Flush();
				return ms.ToArray();
			}
		}

		public static State Load(byte[] data)
		{
			using (var br = new BinaryReader(new MemoryStream(data)))
			{
				int ver = br.ReadInt32();
				if (ver != KernelVersion) throw new InvalidDataException("sheet kernel version " + ver + ", this build reads " + KernelVersion);
				int w = br.ReadInt32(), h = br.ReadInt32();
				var s = new State(w, h, br.ReadUInt32());
				s.Pulse = br.ReadInt64();
				for (int i = 0; i < SourceCount; i++) s.In[i] = br.ReadInt64();
				s.Returned = br.ReadInt64(); s.JoinedLake = br.ReadInt64(); s.Soaked = br.ReadInt64();
				s.Evaporated = br.ReadInt64(); s.Burned = br.ReadInt64(); s.Purged = br.ReadInt64();
				int nWet = br.ReadInt32();
				for (int k = 0; k < nWet; k++)
				{
					int c = br.ReadInt32();
					s.Dl[c] = br.ReadInt32(); s.Fluid[c] = br.ReadByte(); s.SoakRem[c] = br.ReadInt32(); s.EvapRem[c] = br.ReadInt32();
					s.Tiers[c] = (Tier)br.ReadByte(); s.Stand[c] = br.ReadInt32(); s.Calm[c] = br.ReadByte();
					s.Occ.Add(c);
				}
				s.Occ.Sort();
				return s;
			}
		}

		/// <summary>A stable 64-bit FNV-1a over the whole persisted state (the save bytes are canonical).</summary>
		public static ulong Hash(State s)
		{
			ulong h = 14695981039346656037UL;
			foreach (byte b in Save(s)) { h ^= b; h *= 1099511628211UL; }
			return h;
		}
	}
}
