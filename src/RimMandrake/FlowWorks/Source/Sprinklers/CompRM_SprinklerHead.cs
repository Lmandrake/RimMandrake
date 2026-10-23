using System.Collections.Generic;
using System.Text;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>
	/// What both sprinkler comps share (design §4): registration with the map's pulse clock, the hourly pulse through
	/// RM_Sprinkle.Pulse, the state and inspect line, save. Being this comp makes its thing a Machine on the liquid net
	/// (RM_LiquidNet.RoleOfKind), so it draws from the tanks its pipe run joins.
	/// </summary>
	public abstract class CompRM_SprinklerBase : ThingComp
	{
		public RM_SprinklerState state = RM_SprinklerState.Idle;
		public int lastUnits, lastCells, lastNeed, lastAvailable, totalUnits, nextPulseTick = -1;
		public LiquidDef lastLiquid;

		/// <summary>The feature's switch (native: sprinklersEnabled; VFE: the adapter).</summary>
		public abstract bool FeatureEnabled { get; }

		public virtual bool SwitchOn => parent.GetComp<CompFlickable>()?.SwitchIsOn ?? true;

		/// <summary>The cells this pulse waters (the comp's whole difference).</summary>
		protected abstract List<IntVec3> CellsForPulse();

		public float CoverRadius { get; protected set; }

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			RM_MapComponent_Sprinklers.Of(parent.Map)?.Register(this);
		}

		public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
		{
			base.PostDeSpawn(map, mode);
			RM_MapComponent_Sprinklers.Of(map)?.Deregister(this);
		}

		/// <summary>Called by RM_MapComponent_Sprinklers every 250 ticks.</summary>
		public virtual void RareTick(int now)
		{
			if (nextPulseTick < 0 || now >= nextPulseTick)
			{
				nextPulseTick = now + RM_SprinklerKernel.PulseTicks;
				DoPulse();
			}
			if (state == RM_SprinklerState.Spraying && ShowsOwnSpray) RM_Sprinkle.ThrowSpray(parent, lastLiquid, CoverRadius);
		}

		protected virtual bool ShowsOwnSpray => true;

		public RM_Sprinkle.Result DoPulse()
		{
			List<IntVec3> cells = FeatureEnabled && SwitchOn ? CellsForPulse() : new List<IntVec3>();
			RM_Sprinkle.Result r = RM_Sprinkle.Pulse(parent, cells, FeatureEnabled, SwitchOn);
			Record(r);
			return r;
		}

		protected virtual void Record(RM_Sprinkle.Result r)
		{
			state = r.state;
			lastLiquid = r.liquid ?? lastLiquid;
			lastUnits = r.units;
			lastCells = r.cells;
			lastNeed = r.need;
			lastAvailable = r.available;
			totalUnits += r.units;
		}

		protected static string L(int units) => (units / (float)RM_Volume.UnitsPerLitre).ToString("0.#") + " L";

		public string StatusLine()
		{
			string liq = lastLiquid?.label ?? "water";
			switch (state)
			{
				case RM_SprinklerState.Spraying: return "Spraying " + liq + " · " + L(lastUnits) + "/h · " + lastCells + " cells";
				case RM_SprinklerState.Dry: return "Dry: net has " + L(lastAvailable) + " of " + liq + ", needs " + L(lastNeed);
				case RM_SprinklerState.Clogged: return "Clogged: " + liq + " too thick to spray";
				case RM_SprinklerState.NoPressure: return "No pressure: no pump on this network";
				case RM_SprinklerState.NoLiquid: return "Dry: nothing in the tanks on this network";
				case RM_SprinklerState.NoCells: return "Nothing to water";
				case RM_SprinklerState.Budget: return "Valve shut: daily budget or reserve floor reached";
				case RM_SprinklerState.SwitchedOff: return "Switched off";
				case RM_SprinklerState.Disabled: return "Sprinklers are off in Mod Settings";
				default: return "Waiting for its first spray";
			}
		}

		public override string CompInspectStringExtra()
		{
			var sb = new StringBuilder(StatusLine());
			if (RM_LiquidNet.TooLarge(parent)) sb.Append("\nNetwork too large");
			return sb.ToString();
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref state, "rmSprinklerState", RM_SprinklerState.Idle);
			Scribe_Values.Look(ref lastUnits, "rmSprinklerLastUnits");
			Scribe_Values.Look(ref lastCells, "rmSprinklerLastCells");
			Scribe_Values.Look(ref lastNeed, "rmSprinklerLastNeed");
			Scribe_Values.Look(ref lastAvailable, "rmSprinklerLastAvailable");
			Scribe_Values.Look(ref totalUnits, "rmSprinklerTotalUnits");
			Scribe_Values.Look(ref nextPulseTick, "rmSprinklerNextPulse", -1);
			Scribe_Defs.Look(ref lastLiquid, "rmSprinklerLastLiquid");
		}
	}

	/// <summary>The native head's tuning; radius &lt;= 0 reads the Mod Setting (sprinklerNativeRadius).</summary>
	public class CompProperties_RM_SprinklerHead : CompProperties
	{
		public float radius = -1f;

		public CompProperties_RM_SprinklerHead()
		{
			compClass = typeof(CompRM_SprinklerHead);
		}
	}

	/// <summary>
	/// The native FlowWorks head RM_SprinklerHead (design §2, rudimentary): a nozzle set on a universal pipe; no power, but a
	/// working pump on its network (OQ-S2); sprays every covered, unsealed cell in line of sight (OQ-S7), dark ones too (§1.6).
	/// It takes the look of the pipe it is built on (OQ-S6 art in the four pipe looks).
	/// </summary>
	public class CompRM_SprinklerHead : CompRM_SprinklerBase
	{
		public CompProperties_RM_SprinklerHead Props => (CompProperties_RM_SprinklerHead)props;

		public override bool FeatureEnabled => RM_SprinklerSettings.sprinklersEnabled;

		public float Radius => Props.radius > 0f ? Props.radius : RM_SprinklerSettings.sprinklerNativeRadius;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			CoverRadius = Radius;
			if (!respawningAfterLoad) MatchPipeLook();
		}

		/// <summary>Take the look of the pipe under the head (art only).</summary>
		private void MatchPipeLook() => RM_SprinklerLook.MatchPipeUnder(parent);

		protected override List<IntVec3> CellsForPulse()
		{
			CoverRadius = Radius;
			List<IntVec3> covered = RM_Sprinkle.Covered(parent, CoverRadius);
			var cells = new List<IntVec3>(covered.Count);
			foreach (IntVec3 c in covered) if (!RM_Sprinkle.Sealed(c, parent.Map)) cells.Add(c);
			return cells;
		}
	}

	/// <summary>The things set ON a pipe (the sprinkler head, the pipe faucet) join the pipe's style picker (the same four
	/// looks, the build button's menu) once their style defs load, and a new one takes the look of the pipe under it.</summary>
	[StaticConstructorOnStartup]
	public static class RM_SprinklerLook
	{
		public const string HeadDef = "RM_SprinklerHead";
		/// <summary>FAUCET_REDRAW_BORROWED_BLEED_WELL: the faucet's four looks (Defs/Thirst/RM_PipeFaucet.xml).</summary>
		public const string FaucetDef = "RM_PipeFaucet";

		static RM_SprinklerLook()
		{
			foreach (string d in new[] { HeadDef, FaucetDef })
			{
				if (DefDatabase<ThingStyleDef>.GetNamedSilentFail(PipeStyles.StyleDefName(d, PipeStyles.Scrapper)) != null)
				{
					PipeLook.Core.Register(new[] { d }, PipeStyles.StyleDefName);
				}
			}
		}

		/// <summary>Give <paramref name="onPipe"/> the look of the pipe in its cell (art only); no-op for an unstyled def.</summary>
		public static void MatchPipeUnder(Thing onPipe)
		{
			if (onPipe?.Map == null || !PipeLook.IsStyled(onPipe.def)) return;
			foreach (Thing t in onPipe.Position.GetThingList(onPipe.Map))
			{
				if (!RM_LiquidNet.IsPipe(t)) continue;
				string look = PipeLook.LookOfThing(t);
				if (look != null && look != PipeLook.LookOfThing(onPipe)) PipeLook.SetLook(onPipe, look);
				return;
			}
		}
	}

	/// <summary>OQ-S2 + §2: a sprinkler head stands on a universal pipe.</summary>
	public class PlaceWorker_RM_OnPipe : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			if (RM_LiquidNet.HasPipe(loc, map)) return true;
			foreach (Thing t in loc.GetThingList(map))
			{
				// a pipe blueprint or frame counts: you may plan the run and its heads together
				if ((t is Blueprint || t is Frame) && t.def.entityDefToBuild is ThingDef td && td.GetModExtension<RM_UniversalPipeExtension>() != null) return true;
			}
			return "Must be placed on a universal pipe.";
		}
	}
}
