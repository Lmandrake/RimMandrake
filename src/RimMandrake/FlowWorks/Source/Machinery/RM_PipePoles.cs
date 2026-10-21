using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>
	/// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P3):
	/// the pipe pole. A pole is a Gimme Some Slack aerial anchor of kind Pipe (Defs/Machinery/RM_PipePoles.xml, loaded only with
	/// GSS: MayRequire), so links, auto-link, the span mesh, cut / re-string, fallen halves and the wire-down alert are GSS's own
	/// code; GSS keeps a pipe span off every power net and gives it one strand, no drip loop and no sway. FlowWorks owns the
	/// rest: the def and its four looks (PipeLook), the solid-ground rule (LineKind.PipePole through the phase-1 gates, and
	/// <see cref="PlaceWorker_PipePole"/>), and the span's numbers (Mod Settings, handed to GSS here by name: FlowWorks holds no
	/// reference to GSS, the same soft seam as RM_GssLiveWire).
	///
	/// A span is two link records on the two pole comps, never a Thing on the cells it crosses: it is not walking ground, not a
	/// climb exit, not a deck and not in pawn topology or RM_SpanUtility.DeckAt (P3 "Not ground, not support").
	///
	/// Phase 5: the liquid net's long-range edge. <see cref="EdgesFor"/> turns <see cref="UpSpans"/> into pipe-neighbour pairs
	/// (RM_PipeSpanEdges, one logical edge per span between the two poles' join cells) that RM_LiquidNet.MapGraph walks with the
	/// cardinal ones, so the component cap counts the joined net; <see cref="OnSpansChanged"/> bumps the net's revision when
	/// the strung span set changed.
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_PipePoles
	{
		public const string PoleDef = "RM_PipePole";
		public const string GssProfiles = "RimMandrake.GimmeSomeSlack.Aerial.AerialLineProfiles";

		/// <summary>State reads: the GSS profile was handed over; span-change callbacks received from GSS.</summary>
		public static bool Registered { get; private set; }
		public static int SpansChangedCount;

		private static MethodInfo upSpans;

		static RM_PipePoles()
		{
			RegisterWithGss();
			// the pole's four looks join the pipe's style picker only when their style defs are loaded (they load with GSS)
			if (DefDatabase<ThingStyleDef>.GetNamedSilentFail(PipeStyles.StyleDefName(PoleDef, PipeStyles.Scrapper)) != null
				&& DefDatabase<ThingDef>.GetNamedSilentFail(PoleDef) != null)
			{
				PipeLook.Core.Register(new[] { PoleDef }, PipeStyles.StyleDefName);
			}
		}

		public static float MaxSpan() => RM_PipePoleMath.ClampSpan(RM_MachinerySettings.pipePoleMaxSpan);

		public static float Sag() => RM_PipePoleMath.ClampSag(RM_MachinerySettings.pipePoleSag);

		/// <summary>State reads (phase 5): liquid-net rebuilds a span change caused; callbacks that changed nothing.</summary>
		public static int NetBumps, NoChange;

		private sealed class SpanSig
		{
			public ulong last;
			public bool known;
		}

		private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Map, SpanSig> sigs =
			new System.Runtime.CompilerServices.ConditionalWeakTable<Map, SpanSig>();

		/// <summary>GSS calls this on every span topology change, of any kind (link, unlink, cut, re-string, an anchor gone or
		/// landed). The liquid net rebuilds only when the strung PIPE span set changed, so one cut is one rebuild.</summary>
		internal static void OnSpansChanged(Map map)
		{
			SpansChangedCount++;
			if (map == null)
			{
				return;
			}
			List<KeyValuePair<Thing, Thing>> spans = UpSpans(map);
			var ids = new List<KeyValuePair<long, long>>(spans.Count);
			foreach (KeyValuePair<Thing, Thing> sp in spans)
			{
				ids.Add(new KeyValuePair<long, long>(sp.Key.thingIDNumber, sp.Value.thingIDNumber));
			}
			SpanSig st = sigs.GetValue(map, _ => new SpanSig());
			if (RM_PipeSpanNetMath.Changed(ref st.last, ref st.known, RM_PipeSpanNetMath.Signature(ids)))
			{
				NetBumps++;
				RM_LiquidNet.Bump(map);
			}
			else
			{
				NoChange++;
			}
		}

		/// <summary>A pole's pipe cells in join order: under it, then cardinal, then diagonal (a pole is a fitting: a pipe joins it
		/// 8-way or under, owner 2026-10-20). The first is the pole's join cell, where its spans land.</summary>
		public static IList<object> JoinCells(Thing pole)
		{
			var l = new List<object>();
			if (pole == null || !pole.Spawned)
			{
				return l;
			}
			Map map = pole.Map;
			foreach (IntVec3 c in pole.OccupiedRect())
			{
				if (RM_LiquidNet.HasPipe(c, map))
				{
					l.Add(c);
				}
			}
			foreach (IntVec3[] dirs in new[] { GenAdj.CardinalDirections, GenAdj.DiagonalDirections })
			{
				for (int i = 0; i < dirs.Length; i++)
				{
					IntVec3 c = pole.Position + dirs[i];
					if (c.InBounds(map) && !pole.OccupiedRect().Contains(c) && RM_LiquidNet.HasPipe(c, map))
					{
						l.Add(c);
					}
				}
			}
			return l;
		}

		/// <summary>State read: the last edge table built (span edges, fitting edges).</summary>
		public static int LastAerialEdges, LastFittingEdges;

		/// <summary>The span edges the liquid net walks this revision (none while pipe poles are switched off).</summary>
		public static RM_PipeSpanEdges EdgesFor(Map map)
		{
			if (map == null || !RM_MachinerySettings.pipePolesEnabled)
			{
				return RM_PipeSpanEdges.Empty;
			}
			List<KeyValuePair<Thing, Thing>> spans = UpSpans(map);
			if (spans.Count == 0)
			{
				return RM_PipeSpanEdges.Empty;
			}
			var pairs = new List<KeyValuePair<object, object>>(spans.Count);
			foreach (KeyValuePair<Thing, Thing> sp in spans)
			{
				pairs.Add(new KeyValuePair<object, object>(sp.Key, sp.Value));
			}
			RM_PipeSpanEdges e = RM_PipeSpanEdges.Build(pairs, p => JoinCells(p as Thing),
				(a, b) => ((IntVec3)a).AdjacentToCardinal((IntVec3)b));
			LastAerialEdges = e.AerialEdges;
			LastFittingEdges = e.FittingEdges;
			return e;
		}

		/// <summary>Hand GSS live getters for the pipe kind's longest span and sag, and listen for span changes. GSS absent: a
		/// quiet no-op (the pole def does not load without it either).</summary>
		public static void RegisterWithGss()
		{
			if (Registered)
			{
				return;
			}
			try
			{
				Type t = GenTypes.GetTypeInAnyAssembly(GssProfiles);
				if (t == null)
				{
					return;
				}
				MethodInfo reg = t.GetMethod("RegisterPipeProfile", BindingFlags.Public | BindingFlags.Static, null,
					new[] { typeof(Func<float>), typeof(Func<float>) }, null);
				MethodInfo listen = t.GetMethod("RegisterSpansChanged", BindingFlags.Public | BindingFlags.Static, null,
					new[] { typeof(Action<Map>) }, null);
				upSpans = t.GetMethod("UpSpans", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(Map), typeof(string) }, null);
				if (reg == null)
				{
					Log.Warning("[FlowWorks] Gimme Some Slack is loaded but AerialLineProfiles.RegisterPipeProfile was not found; "
						+ "pipe poles use GSS's default span (12 cells, 2% sag) and ignore the pipe pole sliders.");
					return;
				}
				reg.Invoke(null, new object[] { new Func<float>(MaxSpan), new Func<float>(Sag) });
				listen?.Invoke(null, new object[] { new Action<Map>(OnSpansChanged) });
				Registered = true;
			}
			catch (Exception e)
			{
				Log.Warning("[FlowWorks] pipe pole hand-over to Gimme Some Slack failed; pipe poles use GSS's defaults: " + e.Message);
			}
		}

		public const string GssAerialComp = "RimMandrake.GimmeSomeSlack.Aerial.RM_MapComponent_Aerial";

		/// <summary>State read: span redraws asked of GSS (the sag slider moved).</summary>
		public static int Redraws;

		/// <summary>The sag slider moved: GSS drops its span meshes and re-prints the ground shadows on every map
		/// (RM_MapComponent_Aerial.Notify_SettingsChanged, found by name: no GSS reference). GSS absent: nothing to redraw.</summary>
		public static void RedrawSpans()
		{
			if (Current.ProgramState != ProgramState.Playing || Find.Maps == null)
			{
				return;
			}
			try
			{
				foreach (Map map in Find.Maps)
				{
					foreach (MapComponent c in map.components)
					{
						if (c != null && c.GetType().FullName == GssAerialComp)
						{
							c.GetType().GetMethod("Notify_SettingsChanged", BindingFlags.Public | BindingFlags.Instance, null, Type.EmptyTypes, null)?.Invoke(c, null);
							Redraws++;
						}
					}
				}
			}
			catch (Exception e)
			{
				Log.ErrorOnce("[FlowWorks] pipe span redraw (Gimme Some Slack) threw: " + e.Message, 0x5A1E9E);
			}
		}

		/// <summary>Phase-5 seam: every strung pipe span on the map, once each, as its two pole things (empty without GSS).</summary>
		public static List<KeyValuePair<Thing, Thing>> UpSpans(Map map)
		{
			if (map == null || upSpans == null)
			{
				return new List<KeyValuePair<Thing, Thing>>();
			}
			try
			{
				return upSpans.Invoke(null, new object[] { map, "Pipe" }) as List<KeyValuePair<Thing, Thing>> ?? new List<KeyValuePair<Thing, Thing>>();
			}
			catch (Exception e)
			{
				Log.ErrorOnce("[FlowWorks] AerialLineProfiles.UpSpans threw: " + e.Message, 0x5A1E9D);
				return new List<KeyValuePair<Thing, Thing>>();
			}
		}
	}

	/// <summary>On the pipe pole: hidden from the architect menu while pipe poles are switched off; refuses any square that is not
	/// solid ground (a bridge deck, a pit cover, a dug square), whatever the line crossing switch says, because a pole is a
	/// support (review answer 8), not a line choosing its ground. The phase-1 gates add the same rule at frame completion and
	/// auto-rebuild while that switch is on.</summary>
	public class PlaceWorker_PipePole : PlaceWorker
	{
		/// <summary>State read: refusals counted per AllowsPlacing call (a dragged ghost counts every frame: compare before/after
		/// one call, never read it as a blueprint count).</summary>
		public static int Refused;

		public override bool IsBuildDesignatorVisible(BuildableDef def) => RM_MachinerySettings.pipePolesEnabled;

		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			if (map == null || !loc.InBounds(map))
			{
				return AcceptanceReport.WasAccepted;
			}
			string why = RM_LineCrossingMath.RefusalReason(LineKind.PipePole, RM_LineCrossing.SurfaceAt(map, loc));
			if (why != null)
			{
				Refused++;
				return new AcceptanceReport(why);
			}
			return AcceptanceReport.WasAccepted;
		}
	}
}
