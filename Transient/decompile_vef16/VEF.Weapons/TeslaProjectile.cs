using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Weapons;

public class TeslaProjectile : Bullet
{
	[HarmonyPatch]
	public static class ProjectilePatches
	{
		[HarmonyTargetMethods]
		public static IEnumerable<MethodBase> GetMethods()
		{
			yield return AccessTools.Method(typeof(Projectile), "ImpactSomething", (Type[])null, (Type[])null);
			yield return AccessTools.Method(typeof(Projectile), "CheckForFreeIntercept", (Type[])null, (Type[])null);
		}

		public static void Postfix()
		{
			wasDeflected = false;
		}
	}

	public int curLifetime;

	protected int numBounces;

	protected List<TeslaProjectile> allProjectiles = new List<TeslaProjectile>();

	protected List<Thing> prevTargets = new List<Thing>();

	private Thing holder;

	private Thing mainLauncher;

	private bool shotAnything;

	public static bool wasDeflected;

	private static readonly Func<Building_TurretGun, Thing, bool> isValidTarget = (Func<Building_TurretGun, Thing, bool>)Delegate.CreateDelegate(typeof(Func<Building_TurretGun, Thing, bool>), AccessTools.Method(typeof(Building_TurretGun), "IsValidTarget", (Type[])null, (Type[])null));

	public static bool destroyAll;

	public Thing Holder
	{
		get
		{
			if (holder == null)
			{
				return ((Projectile)this).launcher;
			}
			return holder;
		}
	}

	protected virtual int GetDamageAmount => ((Thing)this).def.projectile.GetDamageAmount(1f, (Thing)null, (StringBuilder)null);

	protected virtual int MaxBounceCount => Props.maxBounceCount;

	public TeslaChainingProps Props => ((Def)((Thing)this).def).GetModExtension<TeslaChainingProps>();

	public Thing PrimaryEquipment
	{
		get
		{
			Thing primaryLauncher = PrimaryLauncher;
			return ((Building_TurretGun)(((primaryLauncher is Building_TurretGun) ? primaryLauncher : null)?)).gun;
		}
	}

	public Verb PrimaryVerb
	{
		get
		{
			Thing primaryLauncher = PrimaryLauncher;
			Building_TurretGun val = (Building_TurretGun)(object)((primaryLauncher is Building_TurretGun) ? primaryLauncher : null);
			if (val != null)
			{
				return ((Building_Turret)val).AttackVerb;
			}
			return null;
		}
	}

	private Thing PrimaryLauncher
	{
		get
		{
			if (mainLauncher != null)
			{
				return mainLauncher;
			}
			foreach (TeslaProjectile allProjectile in allProjectiles)
			{
				if (allProjectile.mainLauncher != null)
				{
					return allProjectile.mainLauncher;
				}
			}
			return null;
		}
	}

	protected virtual DamageInfo GetDamageInfo(Thing hitThing)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		return new DamageInfo(Props.damageDef, (float)GetDamageAmount, ((Thing)this).def.projectile.GetArmorPenetration(((Projectile)this).launcher, (StringBuilder)null), Vector3Utility.AngleToFlat(Holder.DrawPos, hitThing.DrawPos), ((Projectile)this).Launcher, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
	}

	protected override void Impact(Thing hitThing, bool blockedByShield = false)
	{
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Expected O, but got Unknown
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		bool isRanged = ((Thing)this).def.projectile.damageDef.isRanged;
		((Thing)this).def.projectile.damageDef.isRanged = true;
		((Bullet)this).Impact(hitThing, false);
		((Thing)this).def.projectile.damageDef.isRanged = isRanged;
		if (mainLauncher == null)
		{
			mainLauncher = ((Projectile)this).launcher;
		}
		if (((Projectile)this).equipmentDef == null)
		{
			((Projectile)this).equipmentDef = ThingDef.Named("Gun_Autopistol");
		}
		if (wasDeflected)
		{
			wasDeflected = false;
			if (Rand.Chance(0.3f))
			{
				DestroyAll();
			}
		}
		else if (hitThing == null && !shotAnything)
		{
			shotAnything = true;
		}
		else
		{
			if (hitThing == null || shotAnything)
			{
				return;
			}
			BattleLogEntry_RangedImpact val = new BattleLogEntry_RangedImpact(((Projectile)this).launcher, hitThing, ((LocalTargetInfo)(ref ((Projectile)this).intendedTarget)).Thing, ((Projectile)this).equipmentDef, ((Thing)this).def, ((Projectile)this).targetCoverDef);
			Find.BattleLog.Add((LogEntry)(object)val);
			DamageInfo damageInfo = GetDamageInfo(hitThing);
			hitThing.TakeDamage(damageInfo).AssociateWithLog((LogEntry_DamageResult)(object)val);
			if (Props.addFire && ThingCompUtility.TryGetComp<CompAttachBase>(hitThing) != null && hitThing.Map != null)
			{
				((AttachableThing)(Fire)GenSpawn.Spawn(ThingDefOf.Fire, hitThing.Position, hitThing.Map, (WipeMode)0)).AttachTo(hitThing);
			}
			if (Props.impactRadius > 0f)
			{
				GenExplosion.DoExplosion(hitThing.Position, ((Thing)this).Map, Props.impactRadius, Props.explosionDamageDef, ((Projectile)this).Launcher, ((Thing)this).def.projectile.GetDamageAmount(1f, (Thing)null, (StringBuilder)null), -1f, (SoundDef)null, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
			}
			SoundDef impactSound = Props.impactSound;
			if (impactSound != null)
			{
				SoundStarter.PlayOneShot(impactSound, SoundInfo.op_Implicit(hitThing));
			}
			RegisterHit(hitThing);
			if (numBounces < MaxBounceCount)
			{
				Thing val2 = NextTarget(hitThing);
				if (val2 != null)
				{
					FireAt(val2);
				}
			}
			shotAnything = true;
		}
	}

	private void RegisterHit(Thing hitThing)
	{
		RegisterHit(this, hitThing);
		foreach (TeslaProjectile allProjectile in allProjectiles)
		{
			RegisterHit(allProjectile, hitThing);
		}
	}

	private void RegisterHit(TeslaProjectile projectile, Thing hitThing)
	{
		if (!projectile.prevTargets.Contains(hitThing))
		{
			projectile.prevTargets.Add(hitThing);
		}
		projectile.curLifetime = 0;
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		Vector3 val = GenThing.TrueCenter(Holder);
		Vector3 val2 = ((Thing)this).DrawPos;
		if (((Vector3)(ref val2)).magnitude > ((Vector3)(ref val)).magnitude)
		{
			Vector3 val3 = val;
			val = val2;
			val2 = val3;
		}
		Mesh plane = MeshPool.plane10;
		Vector3 val4 = val2 + (val - val2) / 2f;
		Quaternion val5 = Quaternion.AngleAxis(Vector3Utility.AngleToFlat(val, val2) + 90f, Vector3.up);
		Vector3 val6 = val - val2;
		Graphics.DrawMesh(plane, Matrix4x4.TRS(val4, val5, new Vector3(1f, 1f, ((Vector3)(ref val6)).magnitude)), ((Thing)this).Graphic.MatSingle, 0);
	}

	public void FireAt(Thing target)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		TeslaProjectile teslaProjectile = (TeslaProjectile)(object)GenSpawn.Spawn(((Thing)this).def, ((Thing)this).Position, ((Thing)this).Map, (WipeMode)0);
		((Projectile)teslaProjectile).Launch(((Projectile)this).launcher, LocalTargetInfo.op_Implicit(target), LocalTargetInfo.op_Implicit(target), ((Projectile)this).HitFlags, false, PrimaryEquipment);
		teslaProjectile.holder = (Thing)(object)this;
		if (mainLauncher != null)
		{
			teslaProjectile.mainLauncher = mainLauncher;
		}
		allProjectiles.Add(teslaProjectile);
		prevTargets.Add(target);
		if (teslaProjectile.prevTargets == null)
		{
			teslaProjectile.prevTargets = new List<Thing>();
		}
		teslaProjectile.prevTargets.AddRange(prevTargets);
		numBounces++;
		teslaProjectile.numBounces = numBounces;
		teslaProjectile.curLifetime = curLifetime;
	}

	private bool IsValidTarget(Thing thing)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		Thing primaryLauncher = PrimaryLauncher;
		Building_TurretGun val = (Building_TurretGun)(object)((primaryLauncher is Building_TurretGun) ? primaryLauncher : null);
		if (val != null && !isValidTarget(val, thing))
		{
			return false;
		}
		Verb primaryVerb = PrimaryVerb;
		if (primaryVerb != null && !primaryVerb.targetParams.CanTarget(TargetInfo.op_Implicit(thing), (ITargetingSource)null))
		{
			return false;
		}
		return true;
	}

	private Thing NextTarget(Thing currentTarget)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return (from t in (from t in GenRadial.RadialDistinctThingsAround(currentTarget.PositionHeld, ((Thing)this).Map, Props.bounceRange, false)
				where (Props.targetFriendly || GenHostility.HostileTo(t, ((Projectile)this).launcher)) && IsValidTarget(t)
				select t).Except((IEnumerable<Thing>)(object)new Thing[2]
			{
				(Thing)this,
				((LocalTargetInfo)(ref ((Projectile)this).usedTarget)).Thing
			}).Except(prevTargets)
			orderby IntVec3Utility.DistanceTo(t.Position, Holder.Position)
			select t).FirstOrDefault();
	}

	protected override void Tick()
	{
		((Projectile)this).Tick();
		if (shotAnything)
		{
			curLifetime++;
		}
		if (curLifetime > Props.maxLifetime)
		{
			DestroyAll();
		}
		else if (Holder.Destroyed)
		{
			DestroyAll();
		}
		else if (GenCollection.Any<TeslaProjectile>(allProjectiles, (Predicate<TeslaProjectile>)((TeslaProjectile x) => ((Thing)x).Destroyed)))
		{
			DestroyAll();
		}
	}

	public void DestroyAll()
	{
		destroyAll = true;
		for (int num = allProjectiles.Count - 1; num >= 0; num--)
		{
			if (!((Thing)allProjectiles[num]).Destroyed)
			{
				((Thing)allProjectiles[num]).Destroy((DestroyMode)0);
			}
		}
		((Thing)this).Destroy((DestroyMode)0);
		destroyAll = false;
	}

	public override void Destroy(DestroyMode mode = 0)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		if (destroyAll)
		{
			((ThingWithComps)this).Destroy(mode);
		}
	}

	public override void ExposeData()
	{
		((Projectile)this).ExposeData();
		Scribe_References.Look<Thing>(ref mainLauncher, "mainLauncher", false);
		Scribe_References.Look<Thing>(ref holder, "holder", false);
		Scribe_Values.Look<int>(ref numBounces, "numBounces", 0, false);
		Scribe_Values.Look<int>(ref curLifetime, "curLifetime", 0, false);
		Scribe_Values.Look<bool>(ref shotAnything, "firedOnce", false, false);
		Scribe_Collections.Look<TeslaProjectile>(ref allProjectiles, "allProjectiles", (LookMode)3, Array.Empty<object>());
		Scribe_Collections.Look<Thing>(ref prevTargets, "prevTargets", (LookMode)3, Array.Empty<object>());
	}
}
