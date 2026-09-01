using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class CompLaserCapacitor : ThingComp
{
	public LocalTargetInfo lastFiringLocation = LocalTargetInfo.op_Implicit((Thing)null);

	public int shotstack;

	public float originalwarmupTime;

	public bool hotshot;

	public bool initalized;

	public CompProperties_LaserCapacitor Props => (CompProperties_LaserCapacitor)(object)base.props;

	public CompEquippable equippable => ThingCompUtility.TryGetComp<CompEquippable>((Thing)(object)base.parent);

	protected virtual bool IsWorn => GetWearer != null;

	protected virtual Pawn GetWearer
	{
		get
		{
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Expected O, but got Unknown
			if (((ThingComp)this).ParentHolder != null && ((ThingComp)this).ParentHolder is Pawn_EquipmentTracker)
			{
				return (Pawn)((ThingComp)this).ParentHolder.ParentHolder;
			}
			return null;
		}
	}

	private Texture2D CommandTex
	{
		get
		{
			if (!GenText.NullOrEmpty(Props.UiIconPath))
			{
				return ContentFinder<Texture2D>.Get(Props.UiIconPath, true);
			}
			return ((BuildableDef)((Thing)base.parent).def).uiIcon;
		}
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (!IsWorn)
		{
			_ = base.parent;
		}
		else
		{
			_ = GetWearer;
		}
		if (Find.Selector.SingleSelectedThing == GetWearer && GetWearer.Drafted && (GetWearer.IsColonist || GetWearer.IsColonyMech))
		{
			int groupKey = 700000101;
			yield return (Gizmo)new Command_Toggle
			{
				icon = (Texture)(object)CommandTex,
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VWEL_ToggleHotshotLabel")),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VWEL_ToggleHotshotDesc")),
				isActive = () => hotshot,
				toggleAction = delegate
				{
					hotshot = !hotshot;
				},
				activateSound = SoundDef.Named("Click"),
				groupKey = groupKey,
				hotKey = KeyBindingDefOf.Misc2
			};
		}
	}

	public override void PostExposeData()
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostExposeData();
		Scribe_TargetInfo.Look(ref lastFiringLocation, "lastFiringLocation", LocalTargetInfo.Invalid);
		Scribe_Values.Look<int>(ref shotstack, "shotstack", 0, false);
		Scribe_Values.Look<float>(ref originalwarmupTime, "originalwarmupTime", 0f, false);
		Scribe_Values.Look<bool>(ref hotshot, "hotshot", false, false);
		Scribe_Values.Look<bool>(ref initalized, "initalized", false, false);
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		if (!respawningAfterLoad && initalized)
		{
			originalwarmupTime = ((Thing)base.parent).def.Verbs[0].warmupTime;
		}
	}

	public void CriticalOverheatExplosion(Verb_Shoot __instance)
	{
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		Map map = ((Verb)__instance).caster.Map;
		if (((Verb_LaunchProjectile)__instance).Projectile.projectile.explosionEffect != null)
		{
			Effecter obj = ((Verb_LaunchProjectile)__instance).Projectile.projectile.explosionEffect.Spawn();
			obj.Trigger(new TargetInfo(((Thing)((Verb)__instance).EquipmentSource).Position, map, false), new TargetInfo(((Thing)((Verb)__instance).EquipmentSource).Position, map, false), -1);
			obj.Cleanup();
		}
		IntVec3 position = ((Verb)__instance).caster.Position;
		Map val = map;
		float overheatBlastRadius = Props.OverheatBlastRadius;
		DamageDef named = DefDatabase<DamageDef>.GetNamed(Props.OverheatBlastDamageDef, true);
		Thing equipmentSource = (Thing)(object)((Verb)__instance).EquipmentSource;
		int overheatBlastExtraDamage = Props.OverheatBlastExtraDamage;
		float armorPenetration = ((Verb_LaunchProjectile)__instance).Projectile.projectile.GetArmorPenetration((Thing)(object)((Verb)__instance).EquipmentSource, (StringBuilder)null);
		SoundDef val2 = ((((Verb_LaunchProjectile)__instance).Projectile.projectile.soundExplode == null) ? named.soundExplosion : ((Verb_LaunchProjectile)__instance).Projectile.projectile.soundExplode);
		_ = ((Thing)((Verb)__instance).EquipmentSource).def;
		_ = ((Thing)((Verb)__instance).EquipmentSource).def;
		_ = ((Verb)__instance).EquipmentSource;
		_ = ((Verb_LaunchProjectile)__instance).Projectile.projectile.postExplosionSpawnThingDef;
		_ = ((Verb_LaunchProjectile)__instance).Projectile.projectile.postExplosionSpawnChance;
		_ = ((Verb_LaunchProjectile)__instance).Projectile.projectile.postExplosionSpawnThingCount;
		_ = ((Verb_LaunchProjectile)__instance).Projectile.projectile.preExplosionSpawnThingDef;
		GenExplosion.DoExplosion(position, val, overheatBlastRadius, named, equipmentSource, overheatBlastExtraDamage, armorPenetration, val2, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
	}
}
