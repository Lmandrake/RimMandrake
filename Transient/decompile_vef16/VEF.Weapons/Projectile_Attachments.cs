using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class Projectile_Attachments : Bullet
{
	public ProjectileExtension cachedProjectileExtension;

	private Effecter effecter;

	public ProjectileExtension CachedProjectileExtension
	{
		get
		{
			if (cachedProjectileExtension == null)
			{
				cachedProjectileExtension = ((Def)((Thing)this).def).GetModExtension<ProjectileExtension>();
			}
			return cachedProjectileExtension;
		}
	}

	protected override void Tick()
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Tick();
		if (Gen.IsHashIntervalTick((Thing)(object)this, CachedProjectileExtension.fleckRefreshInterval) && CachedProjectileExtension.attachedFleck != null)
		{
			try
			{
				FleckMaker.AttachedOverlay((Thing)(object)this, CachedProjectileExtension.attachedFleck, Vector3.zero, CachedProjectileExtension.fleckScale, -1f);
			}
			catch (Exception)
			{
			}
		}
		if (CachedProjectileExtension.attachedEffecter != null && effecter == null)
		{
			effecter = CachedProjectileExtension.attachedEffecter.SpawnAttached((Thing)(object)this, ((Thing)this).Map, 1f);
		}
		Effecter obj = effecter;
		if (obj != null)
		{
			obj.EffectTick(TargetInfo.op_Implicit((Thing)(object)this), TargetInfo.op_Implicit((Thing)(object)this));
		}
	}
}
