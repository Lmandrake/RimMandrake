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
	/// NOT here (phase 5): the liquid net's long-range edge. <see cref="UpSpans"/> and the span-change callback
	/// (<see cref="SpansChangedCount"/>) are the seam it will read.
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

		private static void OnSpansChanged(Map map) => SpansChangedCount++;

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
