using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	/// <summary>
	/// Row 1 of the build ladder: "RUT_GasVent — self-igniting puffs, no
	/// depletion until actively pumped, and pump-removal triggering a violent
	/// map-wide flammable release that clears by wind."
	/// </summary>
	public class CompGasVent : ThingComp
	{
		private int ticksToNextIgnitionCheck;
		private int ticksToNextYieldCheck;
		private int remainingYield;
		private bool depleted;
		private bool wasPumped;

		public CompProperties_GasVent Props => (CompProperties_GasVent)props;

		private ThingDef PumpDef => Props.pumpBuildingDef ?? PropaneLakeMechanicsDefOf.RUT_VentPump;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				ticksToNextIgnitionCheck = Props.ignitionCheckIntervalTicks;
				ticksToNextYieldCheck = Props.yieldCheckIntervalTicks;
				remainingYield = Props.totalYield;
			}
		}

		private bool Enabled => PropaneLakeMechanicsMod.Settings == null || PropaneLakeMechanicsMod.Settings.gasVentsEnabled;

		private Thing FindAdjacentPump()
		{
			if (parent.Map == null)
			{
				return null;
			}
			foreach (IntVec3 c in GenAdj.CellsAdjacentCardinal(parent))
			{
				if (!c.InBounds(parent.Map))
				{
					continue;
				}
				foreach (Thing t in c.GetThingList(parent.Map))
				{
					if (t.def == PumpDef && t.Spawned)
					{
						return t;
					}
				}
			}
			return null;
		}

		public override void CompTick()
		{
			base.CompTick();
			if (!Enabled || parent.Map == null || depleted)
			{
				return;
			}

			// Self-ignition: "puffing gas sometimes self-ignites... doesn't
			// deplete until the player starts actively pumping it out" — the
			// puff/ignition roll runs regardless of pump state.
			ticksToNextIgnitionCheck--;
			if (ticksToNextIgnitionCheck <= 0)
			{
				ticksToNextIgnitionCheck = Props.ignitionCheckIntervalTicks;
				if (!depleted && Rand.Chance(Props.ignitionChancePerCheck))
				{
					FireUtility.TryStartFireIn(parent.Position, parent.Map, Rand.Range(0.3f, 0.7f), parent);
				}
			}

			bool isPumped = !depleted && FindAdjacentPump() != null;

			if (isPumped && !depleted)
			{
				ticksToNextYieldCheck--;
				if (ticksToNextYieldCheck <= 0)
				{
					ticksToNextYieldCheck = Props.yieldCheckIntervalTicks;
					remainingYield -= Props.yieldPerCheck;
					if (remainingYield <= 0)
					{
						remainingYield = 0;
						depleted = true;
					}
				}
			}

			// "Removing the pumping apparatus should trigger a violent release
			// map-wide" — only while the vent itself was still live (not already
			// depleted through honest extraction).
			if (wasPumped && !isPumped && !depleted)
			{
				TriggerViolentRelease();
			}
			wasPumped = isPumped;
		}

		private void TriggerViolentRelease()
		{
			var tracker = parent.Map.GetComponent<MapComponent_GasSaturationTracker>();
			tracker?.AddAmbientSurge(Props.releaseAmbientSurge);
			tracker?.AddSaturation(parent.Position, Props.releaseLocalSaturation, Props.releaseLocalRadius);
			GenExplosion.DoExplosion(parent.Position, parent.Map, 2.4f, DamageDefOf.Flame, parent, chanceToStartFire: 1f, doSoundEffects: true);
			Messages.Message("RUT_Message_GasVentRelease".Translate(parent.LabelShort), new TargetInfo(parent.Position, parent.Map), MessageTypeDefOf.ThreatBig);
		}

		public override string CompInspectStringExtra()
		{
			if (depleted)
			{
				return "RUT_GasVent_Depleted".Translate();
			}
			if (wasPumped)
			{
				return "RUT_GasVent_Pumping".Translate(remainingYield);
			}
			return "RUT_GasVent_Dormant".Translate();
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref ticksToNextIgnitionCheck, "ticksToNextIgnitionCheck");
			Scribe_Values.Look(ref ticksToNextYieldCheck, "ticksToNextYieldCheck");
			Scribe_Values.Look(ref remainingYield, "remainingYield");
			Scribe_Values.Look(ref depleted, "depleted");
			Scribe_Values.Look(ref wasPumped, "wasPumped");
		}
	}
}
