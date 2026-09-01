using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

[HotSwappable]
public class FlamethrowProjectile : ExpandableProjectile
{
	public HashSet<IntVec3> affectedCells = new HashSet<IntVec3>();

	public override void DoDamage(IntVec3 pos)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Expected O, but got Unknown
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		base.DoDamage(pos);
		try
		{
			if (!(pos != ((Projectile)this).launcher.Position) || ((Thing)this).Map == null || !GenGrid.InBounds(pos, ((Thing)this).Map))
			{
				return;
			}
			if (!affectedCells.Contains(pos))
			{
				FilthMaker.TryMakeFilth(pos, ((Thing)this).Map, ThingDefOf.Filth_Ash, 1, (FilthSourceFlags)0, true);
				ThrowSmoke(((IntVec3)(ref pos)).ToVector3Shifted(), ((Thing)this).Map, 1f);
				ThrowMicroSparks(((IntVec3)(ref pos)).ToVector3Shifted(), ((Thing)this).Map);
				affectedCells.Add(pos);
			}
			List<Thing> list = ((Thing)this).Map.thingGrid.ThingsListAt(pos);
			for (int num = list.Count - 1; num >= 0; num--)
			{
				if (IsDamagable(list[num]))
				{
					if (!list.Where((Thing x) => x.def == ThingDefOf.Fire).Any())
					{
						CompAttachBase obj = ThingCompUtility.TryGetComp<CompAttachBase>(list[num]);
						Fire val = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire, (ThingDef)null);
						val.fireSize = 1f;
						GenSpawn.Spawn((Thing)(object)val, list[num].Position, list[num].Map, Rot4.North, (WipeMode)0, false, false);
						if (obj != null)
						{
							((AttachableThing)val).AttachTo(list[num]);
							Thing obj2 = list[num];
							Pawn val2 = (Pawn)(object)((obj2 is Pawn) ? obj2 : null);
							if (val2 != null)
							{
								val2.jobs.StopAll(false, true);
								val2.records.Increment(RecordDefOf.TimesOnFire);
							}
						}
					}
					customImpact = true;
					Impact(list[num]);
					customImpact = false;
				}
			}
		}
		catch
		{
		}
	}

	public override void ExposeData()
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Invalid comparison between Unknown and I4
		base.ExposeData();
		Scribe_Collections.Look<IntVec3>(ref affectedCells, "affectedCells", (LookMode)1);
		if ((int)Scribe.mode == 4 && affectedCells == null)
		{
			affectedCells = new HashSet<IntVec3>();
		}
	}

	public static void ThrowSmoke(Vector3 loc, Map map, float size)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		FleckCreationData dataStatic = FleckMaker.GetDataStatic(loc, map, FleckDefOf.Smoke, Rand.Range(1.5f, 2.5f) * size);
		dataStatic.rotationRate = Rand.Range(-30f, 30f);
		dataStatic.velocityAngle = Rand.Range(30, 40);
		dataStatic.velocitySpeed = Rand.Range(0.5f, 0.7f);
		dataStatic.instanceColor = Color.black;
		map.flecks.CreateFleck(dataStatic);
	}

	public static void ThrowMicroSparks(Vector3 loc, Map map)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		loc -= new Vector3(0.5f, 0f, 0.5f);
		loc += new Vector3(Rand.Value, 0f, Rand.Value);
		FleckCreationData dataStatic = FleckMaker.GetDataStatic(loc, map, FleckDefOf.MicroSparks, Rand.Range(0.8f, 1.2f));
		dataStatic.rotationRate = Rand.Range(-12f, 12f);
		dataStatic.velocityAngle = Rand.Range(35, 45);
		dataStatic.velocitySpeed = 1.2f;
		map.flecks.CreateFleck(dataStatic);
	}

	public override bool IsDamagable(Thing t)
	{
		if (base.IsDamagable(t))
		{
			return t.def != ThingDefOf.Fire;
		}
		return false;
	}
}
