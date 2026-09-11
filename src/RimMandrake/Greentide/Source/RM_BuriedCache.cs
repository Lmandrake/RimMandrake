using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1 (M8, swallow half). One buried stack at one
	/// cell. Nothing is destroyed — RM_JobDriver_DigOutBuried restores the
	/// exact def/stuff/stackCount once dug out.
	/// </summary>
	public class RM_BuriedCache : IExposable
	{
		public IntVec3 cell;
		public ThingDef thingDef;
		public ThingDef stuffDef;
		public int stackCount;
		public int buriedTick;

		public RM_BuriedCache()
		{
		}

		public RM_BuriedCache(IntVec3 cell, ThingDef thingDef, ThingDef stuffDef, int stackCount, int buriedTick)
		{
			this.cell = cell;
			this.thingDef = thingDef;
			this.stuffDef = stuffDef;
			this.stackCount = stackCount;
			this.buriedTick = buriedTick;
		}

		public void ExposeData()
		{
			Scribe_Values.Look(ref cell, "cell");
			Scribe_Defs.Look(ref thingDef, "thingDef");
			Scribe_Defs.Look(ref stuffDef, "stuffDef");
			Scribe_Values.Look(ref stackCount, "stackCount");
			Scribe_Values.Look(ref buriedTick, "buriedTick");
		}
	}
}
