using RimWorld;
using Verse;

namespace VEF.Maps;

public class TerrainComp_FireSpreader : TerrainComp
{
	private int hashOffset;

	private bool hasFire;

	private int[] checkTimers = new int[8];

	private int checkCounter;

	private int overrideCooldown;

	private int tickCounter;

	private int warmupTicks = 1;

	public TerrainCompProperties_FireSpreader Props => (TerrainCompProperties_FireSpreader)props;

	public override void PlaceSetup()
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		base.PlaceSetup();
		hashOffset = ((CellIndices)(ref parent.Map.cellIndices)).CellToIndex(parent.Position);
	}

	public override void CompTick()
	{
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		base.CompTick();
		tickCounter++;
		if (overrideCooldown > 0)
		{
			overrideCooldown--;
			return;
		}
		int num = (tickCounter + hashOffset) % Props.spreadTimer;
		if (num >= 8)
		{
			return;
		}
		if (num == 0)
		{
			if (checkCounter >= 8)
			{
				hasFire = false;
				overrideCooldown = 2500 * Props.spreadTimer * 2;
			}
			else
			{
				hasFire = FireUtility.ContainsStaticFire(parent.Position, parent.Map);
			}
			checkCounter = 0;
		}
		if (!hasFire)
		{
			return;
		}
		if (warmupTicks > 0)
		{
			warmupTicks--;
			return;
		}
		if (checkTimers[num] > 0)
		{
			checkTimers[num]--;
			checkCounter++;
			return;
		}
		IntVec3 val = parent.Position + GenAdj.AdjacentCells[num];
		if (val != IntVec3.Invalid && GenGrid.InBounds(val, parent.Map))
		{
			TerrainDef terrain = GridsUtility.GetTerrain(val, parent.Map);
			if (parent.def == terrain)
			{
				FireUtility.TryStartFireIn(val, parent.Map, 1f, (Thing)null, (SimpleCurve)null);
			}
			checkTimers[num] = 2500 * Props.spreadTimer;
		}
		else
		{
			checkTimers[num] = int.MaxValue;
		}
	}

	public override void PostExposeData()
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Invalid comparison between Unknown and I4
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		base.PostExposeData();
		Scribe_Values.Look<int>(ref warmupTicks, "warmupTicks", 1, false);
		if ((int)Scribe.mode == 4)
		{
			hashOffset = ((CellIndices)(ref parent.Map.cellIndices)).CellToIndex(parent.Position);
		}
	}
}
