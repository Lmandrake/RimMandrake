using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Maps;

public class TerrainComp_MoteSpawner : TerrainComp
{
	public bool spawnAfterLoad = true;

	public TerrainCompProperties_MoteSpawner Props => (TerrainCompProperties_MoteSpawner)props;

	public override void PostPostLoad()
	{
		base.PostPostLoad();
	}

	public bool CanSpawnInRequiredTimeRanges()
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		int num = GenLocalDate.HourInteger(parent.Map);
		if (Props.reqTimeRangeToSpawn != null)
		{
			foreach (IntRange item in Props.reqTimeRangeToSpawn)
			{
				if (num >= item.min && num <= item.max)
				{
					return true;
				}
			}
			return false;
		}
		return true;
	}

	public override void CompTick()
	{
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		base.CompTick();
		if (Find.TickManager.TicksGame % ((IntRange)(ref Props.tickInterval)).RandomInRange != 0 || (Props.spawnChance > 0f && !Rand.Chance(Props.spawnChance)) || !CanSpawnInRequiredTimeRanges())
		{
			return;
		}
		_ = Props.reqTempRangeToSpawn;
		if (((FloatRange)(ref Props.reqTempRangeToSpawn)).Includes(GridsUtility.GetTemperature(parent.Position, parent.Map)))
		{
			IntVec3 position;
			if (Props.size.min > 0f)
			{
				position = parent.Position;
				ThrowMote(((IntVec3)(ref position)).ToVector3Shifted(), parent.Map, ((FloatRange)(ref Props.size)).RandomInRange);
			}
			else
			{
				position = parent.Position;
				ThrowMote(((IntVec3)(ref position)).ToVector3Shifted(), parent.Map, 1f);
			}
			spawnAfterLoad = false;
		}
	}

	public void ThrowMote(Vector3 loc, Map map, float size)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Expected O, but got Unknown
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		if (GenView.ShouldSpawnMotesAt(loc, map, true))
		{
			MoteThrown val = (MoteThrown)ThingMaker.MakeThing(Props.moteDef, (ThingDef)null);
			((Mote)val).Scale = size;
			_ = Props.rotationRate;
			((Mote)val).rotationRate = ((FloatRange)(ref Props.rotationRate)).RandomInRange;
			((Mote)val).exactPosition = loc;
			_ = Props.velocityAngle;
			_ = Props.velocitySpeed;
			val.SetVelocity(((FloatRange)(ref Props.velocityAngle)).RandomInRange, ((FloatRange)(ref Props.velocitySpeed)).RandomInRange);
			_ = Props.instanceColor;
			((Mote)val).instanceColor = Props.instanceColor;
			GenSpawn.Spawn((Thing)(object)val, IntVec3Utility.ToIntVec3(loc), map, (WipeMode)0);
		}
	}
}
