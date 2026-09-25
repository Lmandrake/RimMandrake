using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	public class CompProperties_VWakeAgitation : CompProperties
	{
		/// <summary>How far a running pump reaches to agitate the creature —
		/// "the loud pumping agitates them and makes them start to look around
		/// more swiftly" (the_propane_lakes.md §4).</summary>
		public float pumpDetectionRadius = 40f;

		public int checkIntervalTicks = 250;

		public CompProperties_VWakeAgitation()
		{
			compClass = typeof(CompVWakeAgitation);
		}
	}

	/// <summary>
	/// Closes RUT_VWake's own documented gap (RUT_PropaneLakeFauna.xml header:
	/// "'Agitated by pumping' is the ONE piece of this row not built... the
	/// creature exists and is dangerous now; the specific pump-noise hook wires
	/// on top later with no def rework, only a new comp reading this race's own
	/// aggression state"). Patched onto RUT_VWake's existing comps list — no
	/// change to the ThingDef's own authored fields.
	/// </summary>
	public class CompVWakeAgitation : ThingComp
	{
		public CompProperties_VWakeAgitation Props => (CompProperties_VWakeAgitation)props;

		private bool Enabled => PropaneLakeMechanicsMod.Settings == null || PropaneLakeMechanicsMod.Settings.vWakeAgitationEnabled;

		public override void CompTick()
		{
			base.CompTick();
			if (!(parent is Pawn pawn) || !pawn.Spawned || pawn.Dead)
			{
				return;
			}
			if (!pawn.IsHashIntervalTick(Props.checkIntervalTicks))
			{
				return;
			}
			if (!Enabled)
			{
				RemoveAgitation(pawn);
				return;
			}

			bool agitated = AnyPumpRunningNearby(pawn);
			Hediff existing = pawn.health.hediffSet.GetFirstHediffOfDef(PropaneLakeMechanicsDefOf.RUT_PropaneAgitation);
			if (agitated && existing == null)
			{
				pawn.health.AddHediff(PropaneLakeMechanicsDefOf.RUT_PropaneAgitation);
			}
			else if (!agitated && existing != null)
			{
				pawn.health.RemoveHediff(existing);
			}
		}

		private void RemoveAgitation(Pawn pawn)
		{
			Hediff existing = pawn.health.hediffSet.GetFirstHediffOfDef(PropaneLakeMechanicsDefOf.RUT_PropaneAgitation);
			if (existing != null)
			{
				pawn.health.RemoveHediff(existing);
			}
		}

		private bool AnyPumpRunningNearby(Pawn pawn)
		{
			if (pawn.Map == null)
			{
				return false;
			}
			float radiusSq = Props.pumpDetectionRadius * Props.pumpDetectionRadius;
			foreach (Thing pump in pawn.Map.listerThings.ThingsOfDef(PropaneLakeMechanicsDefOf.RUT_PipePump))
			{
				if (!pump.Spawned)
				{
					continue;
				}
				if ((pump.Position - pawn.Position).LengthHorizontalSquared > radiusSq)
				{
					continue;
				}
				CompPipePump pumpComp = pump.TryGetComp<CompPipePump>();
				if (pumpComp != null && pumpComp.Running)
				{
					return true;
				}
			}
			return false;
		}
	}
}
