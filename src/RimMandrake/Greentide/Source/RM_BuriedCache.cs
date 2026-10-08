using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1 (M8, swallow half). One buried stack at one
	/// cell. Nothing is destroyed — RM_JobDriver_DigOutBuried restores the
	/// def/stuff/stackCount once dug out (in stacks no larger than the def's limit).
	/// The fields live in the Verse-free kernel's Cache; these are the typed views.
	/// </summary>
	public class RM_BuriedCache : RM_SwallowKernel.Cache, IExposable
	{
		public IntVec3 cell
		{
			get { return new IntVec3(X, 0, Z); }
			set { X = value.x; Z = value.z; }
		}

		public ThingDef thingDef
		{
			get { return (ThingDef)Def; }
			set { Def = value; }
		}

		public ThingDef stuffDef
		{
			get { return (ThingDef)Stuff; }
			set { Stuff = value; }
		}

		public int stackCount
		{
			get { return Count; }
			set { Count = value; }
		}

		public int buriedTick
		{
			get { return Tick; }
			set { Tick = value; }
		}

		public RM_BuriedCache()
		{
		}

		public void ExposeData()
		{
			IntVec3 c = cell;
			ThingDef td = thingDef, sd = stuffDef;
			int sc = stackCount, bt = buriedTick;
			Scribe_Values.Look(ref c, "cell");
			Scribe_Defs.Look(ref td, "thingDef");
			Scribe_Defs.Look(ref sd, "stuffDef");
			Scribe_Values.Look(ref sc, "stackCount");
			Scribe_Values.Look(ref bt, "buriedTick");
			cell = c; thingDef = td; stuffDef = sd; stackCount = sc; buriedTick = bt;
		}
	}
}
