using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using VEF.Abilities;
using Verse;

namespace VEF.Weapons;

[StaticConstructorOnStartup]
public class BeamProjectile : Projectile_Explosive
{
	private static readonly Dictionary<ThingDef, ThingDef> DRAWERS;

	private static readonly Dictionary<Type, HashSet<ushort>> takenHashesPerDeftype;

	private static readonly Action<Def, Type, HashSet<ushort>> giveShortHash;

	public Vector3 Origin => ((Projectile)this).origin;

	public Vector3 Dest => ((Projectile)this).destination;

	public override int DamageAmount => Mathf.RoundToInt((float)((Projectile)this).DamageAmount * (ThingCompUtility.TryGetComp<CompAbilityProjectile>((Thing)(object)this)?.ability.GetPowerForPawn() ?? 1f));

	static BeamProjectile()
	{
		DRAWERS = new Dictionary<ThingDef, ThingDef>();
		takenHashesPerDeftype = (Dictionary<Type, HashSet<ushort>>)AccessTools.Field(typeof(ShortHashGiver), "takenHashesPerDeftype").GetValue(null);
		giveShortHash = (Action<Def, Type, HashSet<ushort>>)AccessTools.Method(typeof(ShortHashGiver), "GiveShortHash", (Type[])null, (Type[])null).CreateDelegate(typeof(Action<Def, Type, HashSet<ushort>>));
		foreach (ThingDef allDef in DefDatabase<ThingDef>.AllDefs)
		{
			if (allDef.thingClass != null && typeof(BeamProjectile).IsAssignableFrom(allDef.thingClass))
			{
				ThingDef val = BaseBeamDrawer();
				CompProperties_AffectsSky compProperties = allDef.GetCompProperties<CompProperties_AffectsSky>();
				ProjectileExtension modExtension = ((Def)allDef).GetModExtension<ProjectileExtension>();
				val.comps = new List<CompProperties>();
				val.graphicData = allDef.graphicData;
				((Def)val).modExtensions = new List<DefModExtension>();
				((Def)val).defName = ((Def)allDef).defName + "Drawer";
				if (compProperties != null)
				{
					val.comps.Add((CompProperties)(object)compProperties);
				}
				if (modExtension != null)
				{
					((Def)val).modExtensions.Add((DefModExtension)(object)modExtension);
				}
				DRAWERS.Add(allDef, val);
			}
		}
		foreach (ThingDef value in DRAWERS.Values)
		{
			GiveShortHash((Def)(object)value, typeof(ThingDef));
			DefGenerator.AddImpliedDef<ThingDef>(value, false);
		}
	}

	public static void GiveShortHash(Def def, Type defType)
	{
		giveShortHash(def, defType, takenHashesPerDeftype[defType]);
	}

	private static ThingDef BaseBeamDrawer()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Expected O, but got Unknown
		return new ThingDef
		{
			thingClass = typeof(BeamDraw),
			drawOffscreen = true,
			label = "beam",
			category = (ThingCategory)5,
			tickerType = (TickerType)1,
			altitudeLayer = (AltitudeLayer)28,
			useHitPoints = false,
			selectable = false,
			neverMultiSelect = true,
			drawerType = (DrawerType)1
		};
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
	}

	protected override void Impact(Thing hitThing, bool blockedByShield = false)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		BeamDraw obj = (BeamDraw)(object)ThingMaker.MakeThing(DRAWERS[((Thing)this).def], (ThingDef)null);
		obj.Setup(((Projectile)this).origin, ((Projectile)this).destination);
		IntVec3 val = IntVec3Utility.ToIntVec3(((Projectile)this).ExactPosition);
		Map map = ((Projectile)this).launcher.Map;
		GenSpawn.Spawn((Thing)(object)obj, val, map, (WipeMode)0);
		((Projectile_Explosive)this).Impact((Thing)null, false);
	}
}
