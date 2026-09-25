using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	[DefOf]
	public static class PropaneLakeMechanicsDefOf
	{
		public static ThingDef RUT_GasVent;

		public static ThingDef RUT_VentPump;

		public static ThingDef RUT_PipeSegment;

		public static ThingDef RUT_PipeValve;

		public static ThingDef RUT_PipePump;

		public static HediffDef RUT_PropaneAgitation;

		public static IncidentDef RUT_SaturationHeistRaid;

		static PropaneLakeMechanicsDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(PropaneLakeMechanicsDefOf));
		}
	}
}
