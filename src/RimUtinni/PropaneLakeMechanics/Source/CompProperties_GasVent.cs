using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	public class CompProperties_GasVent : CompProperties
	{
		/// <summary>How often the vent rolls to self-ignite its puff.</summary>
		public int ignitionCheckIntervalTicks = 2500;

		/// <summary>Chance per check that the puff self-ignites (§3: "puffing gas
		/// sometimes self-ignites").</summary>
		public float ignitionChancePerCheck = 0.12f;

		/// <summary>The building that must be adjacent and active for the vent to
		/// be considered "actively pumped" — defaults to RUT_VentPump.</summary>
		public ThingDef pumpBuildingDef;

		/// <summary>Total extractable volume once pumped (a found resource with a
		/// lifespan, §3's CompVentYield idea folded into this comp rather than a
		/// separate class — same data, one comp).</summary>
		public int totalYield = 3000;

		/// <summary>How much yield is drawn per pumped tick-check.</summary>
		public int yieldPerCheck = 4;

		/// <summary>How often (ticks) the pumped-yield check runs.</summary>
		public int yieldCheckIntervalTicks = 250;

		/// <summary>The ambient saturation surge added map-wide when a still-live
		/// vent's pump is torn out from under it (§3: "removing the pumping
		/// apparatus should trigger a violent release map-wide").</summary>
		public float releaseAmbientSurge = 55f;

		/// <summary>Local saturation added at the vent's own position on release,
		/// on top of the ambient surge.</summary>
		public float releaseLocalSaturation = 100f;

		public float releaseLocalRadius = 6f;

		public CompProperties_GasVent()
		{
			compClass = typeof(CompGasVent);
		}
	}
}
