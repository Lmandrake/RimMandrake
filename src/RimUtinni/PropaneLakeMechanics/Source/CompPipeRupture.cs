using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	/// <summary>
	/// Row 3's core original lift (§4): "rupture is actively, continuously
	/// dangerous for as long as the pipe stays pressurized... it does not go out
	/// on its own... the only way to end it is to cut supply." Attaches to
	/// RUT_PipeSegment alongside CompPipeNetwork.
	/// </summary>
	public class CompPipeRupture : ThingComp
	{
		private bool ruptured;
		private int ticksToNextJet;
		private int unresolvedTicks;
		private bool goodwillPenaltyApplied;

		public CompProperties_PipeRupture Props => (CompProperties_PipeRupture)props;

		private bool Enabled => PropaneLakeMechanicsMod.Settings == null || PropaneLakeMechanicsMod.Settings.pipeNetworksEnabled;

		public bool Ruptured => ruptured;

		public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
		{
			base.PostPostApplyDamage(dinfo, totalDamageDealt);
			if (!Enabled || ruptured || parent.Map == null)
			{
				return;
			}
			if (dinfo.Def == DamageDefOf.Flame && Rand.Chance(Props.ruptureChanceOnFlameHit))
			{
				TriggerRupture();
			}
			else if (dinfo.Def == DamageDefOf.Bomb && Rand.Chance(Props.ruptureChanceOnBombHit))
			{
				TriggerRupture();
			}
		}

		/// <summary>Public entry point for "a raid breach, sabotage, a scripted
		/// beat" (§4) — anything besides direct fire/bomb damage that should
		/// force a rupture (a future quest/incident calls this directly).</summary>
		public void TriggerRupture()
		{
			if (ruptured)
			{
				return;
			}
			ruptured = true;
			ticksToNextJet = 0;
			unresolvedTicks = 0;
			goodwillPenaltyApplied = false;
			Messages.Message("RUT_Message_PipeRupture".Translate(parent.LabelShort), new TargetInfo(parent.Position, parent.Map), MessageTypeDefOf.ThreatBig);
		}

		public override void CompTick()
		{
			base.CompTick();
			if (!ruptured || parent.Map == null)
			{
				return;
			}
			if (!Enabled)
			{
				// Settings toggled off mid-game: let the rupture lapse quietly
				// rather than leaving a jet nobody can ever shut off.
				ruptured = false;
				return;
			}

			CompPipeNetwork netComp = parent.GetComp<CompPipeNetwork>();
			MapComponent_PipeNetworks mgr = parent.Map.GetComponent<MapComponent_PipeNetworks>();
			bool pressurized = netComp != null && mgr != null && mgr.IsNetworkPressurized(netComp);
			if (!pressurized)
			{
				// "The only way to end it is to cut supply" — a reachable valve
				// was closed (or the pump stopped), and the jet stops with it.
				ruptured = false;
				unresolvedTicks = 0;
				goodwillPenaltyApplied = false;
				return;
			}

			ticksToNextJet--;
			if (ticksToNextJet <= 0)
			{
				ticksToNextJet = Props.jetIntervalTicks;
				FireUtility.TryStartFireIn(parent.Position, parent.Map, Rand.Range(0.5f, 1.1f), parent);
				parent.Map.GetComponent<MapComponent_GasSaturationTracker>()?.AddSaturation(parent.Position, Props.jetLocalSaturation, Props.jetSaturationRadius);
			}

			unresolvedTicks += 1;
			if (!goodwillPenaltyApplied && unresolvedTicks >= Props.goodwillPenaltyDelayTicks)
			{
				Faction owner = parent.Map.ParentFaction;
				if (owner != null && owner != Faction.OfPlayer)
				{
					owner.TryAffectGoodwillWith(Faction.OfPlayer, Props.goodwillPenalty);
					Messages.Message("RUT_Message_PipeRuptureGoodwill".Translate(owner.Name), MessageTypeDefOf.NegativeEvent);
				}
				goodwillPenaltyApplied = true;
			}
		}

		public override string CompInspectStringExtra()
		{
			return ruptured ? "RUT_PipeSegment_Ruptured".Translate() : null;
		}

		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			foreach (Gizmo g in base.CompGetGizmosExtra())
			{
				yield return g;
			}
			if (Prefs.DevMode && !ruptured)
			{
				yield return new Command_Action
				{
					defaultLabel = "DEV: Trigger rupture",
					action = TriggerRupture
				};
			}
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref ruptured, "ruptured");
			Scribe_Values.Look(ref ticksToNextJet, "ticksToNextJet");
			Scribe_Values.Look(ref unresolvedTicks, "unresolvedTicks");
			Scribe_Values.Look(ref goodwillPenaltyApplied, "goodwillPenaltyApplied");
		}
	}
}
