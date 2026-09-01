using UnityEngine;
using Verse;

namespace VEF.Weapons;

public static class SmokeMaker
{
	public static void ThrowMoteDef(ThingDef moteDef, Vector3 loc, Map map, float size, float velocity, float angle, float rotation)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Expected O, but got Unknown
		if (GenView.ShouldSpawnMotesAt(loc, map, true) && !map.moteCounter.SaturatedLowPriority)
		{
			MoteThrown val = (MoteThrown)ThingMaker.MakeThing(moteDef, (ThingDef)null);
			((Mote)val).Scale = Rand.Range(1f, 2f) * size;
			((Mote)val).rotationRate = rotation;
			((Mote)val).exactPosition = loc;
			val.SetVelocity(angle, velocity);
			GenSpawn.Spawn((Thing)val, IntVec3Utility.ToIntVec3(loc), map, (WipeMode)0);
		}
	}

	public static void ThrowFleckDef(FleckDef fleckDef, Vector3 loc, Map map, float size, float velocity, float angle, float rotation)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		FleckCreationData val = default(FleckCreationData);
		val.def = fleckDef;
		val.spawnPosition = loc;
		val.scale = Rand.Range(1f, 2f) * size;
		val.rotationRate = rotation;
		val.velocitySpeed = velocity;
		val.velocityAngle = angle;
		map.flecks.CreateFleck(val);
	}

	public static void ThrowSmokeTrail(Vector3 loc, float size, Map map, string defName)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Expected O, but got Unknown
		if (GenView.ShouldSpawnMotesAt(loc, map, true) && !map.moteCounter.Saturated)
		{
			MoteThrown val = (MoteThrown)ThingMaker.MakeThing(ThingDef.Named(defName), (ThingDef)null);
			((Mote)val).Scale = Rand.Range(2f, 3f) * size;
			((Mote)val).exactPosition = loc;
			((Mote)val).rotationRate = Rand.Range(-0.5f, 0.5f);
			val.SetVelocity((float)Rand.Range(30, 40), Rand.Range(0.008f, 0.012f));
			GenSpawn.Spawn((Thing)val, IntVec3Utility.ToIntVec3(loc), map, (WipeMode)0);
		}
	}

	public static void ThrowFlintLockSmoke(Vector3 loc, Map map, float size)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Expected O, but got Unknown
		if (GenView.ShouldSpawnMotesAt(loc, map, true) && !map.moteCounter.SaturatedLowPriority)
		{
			MoteThrown val = (MoteThrown)ThingMaker.MakeThing(InternalDefOf.VEF_FlintlockSmoke, (ThingDef)null);
			((Mote)val).Scale = Rand.Range(1.5f, 2.5f) * size;
			((Mote)val).rotationRate = Rand.Range(-30f, 30f);
			((Mote)val).exactPosition = loc;
			val.SetVelocity((float)Rand.Range(30, 40), Rand.Range(0.5f, 0.7f));
			GenSpawn.Spawn((Thing)val, IntVec3Utility.ToIntVec3(loc), map, (WipeMode)0);
		}
	}
}
