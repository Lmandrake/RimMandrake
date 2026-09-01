using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public class GaussProperties
{
	public static readonly List<AltitudeLayer> DefaultAltitudeLayersBlackList = new List<AltitudeLayer>(5)
	{
		(AltitudeLayer)18,
		(AltitudeLayer)19,
		(AltitudeLayer)5,
		(AltitudeLayer)4,
		(AltitudeLayer)7
	};

	public static readonly GaussProperties DefaultProperties = new GaussProperties();

	public bool includeInterceptChanceFromDistanceForFriendlyFire;

	public float chanceToHitUnintendedLayingTarget;

	public List<AltitudeLayer> altitudeLayersBlackList = DefaultAltitudeLayersBlackList;

	public StatDef damageModifierStat;

	public bool gaussDistortion;

	public bool lightningGlow;

	public Type damageWorkerClass = typeof(GaussProjectileDefaultDamageWorker);

	[Unsaved(false)]
	private GaussProjectileDamageWorker damageWorkerInt;

	public GaussProjectileDamageWorker Worker => damageWorkerInt ?? (damageWorkerInt = (GaussProjectileDamageWorker)Activator.CreateInstance(damageWorkerClass));

	public void ResolveReferences(ExpandableProjectileDef def)
	{
		if (damageModifierStat == null)
		{
			damageModifierStat = VEFDefOf.VEF_GaussProjectileDamageModifier;
		}
		if (this != DefaultProperties)
		{
			Worker.def = def;
		}
	}
}
