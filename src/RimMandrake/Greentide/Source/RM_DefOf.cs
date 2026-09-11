using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
	[DefOf]
	public static class RM_DefOf
	{
		public static JobDef RM_DigOutBuried;
		public static JobDef RM_FreeMired;
		public static HediffDef RM_Mired;
		public static DesignationDef RM_DesignationDigOutBuried;

		static RM_DefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_DefOf));
		}
	}
}
