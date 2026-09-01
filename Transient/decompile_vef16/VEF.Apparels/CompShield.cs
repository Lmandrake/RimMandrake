using System;
using RimWorld;
using Verse;

namespace VEF.Apparels;

public class CompShield : ThingComp
{
	public bool equippedOffHand;

	public CompProperties_Shield Props => (CompProperties_Shield)(object)base.props;

	public Pawn EquippingPawn
	{
		get
		{
			ThingWithComps parent = base.parent;
			Apparel val = (Apparel)(object)((parent is Apparel) ? parent : null);
			if (val != null)
			{
				return val.Wearer;
			}
			return null;
		}
	}

	public bool UsableNow
	{
		get
		{
			if (EquippingPawn != null)
			{
				Pawn_EquipmentTracker equipment = EquippingPawn.equipment;
				if (!EquippingPawn.CanUseShields())
				{
					return false;
				}
				ThingWithComps primary = equipment.Primary;
				if (primary != null)
				{
					if (ModCompatibilityCheck.DualWield && NonPublicMethods.DualWield.Ext_Pawn_EquipmentTracker_TryGetOffHandEquipment(EquippingPawn.equipment, out var _))
					{
						return false;
					}
					if (((Thing)primary).def.UsableWithShields())
					{
						return true;
					}
					return false;
				}
			}
			return true;
		}
	}

	public bool CoversBodyPart(BodyPartRecord partRec)
	{
		if (Props.coveredBodyPartGroups == null)
		{
			return false;
		}
		return GenCollection.Any<BodyPartGroupDef>(Props.coveredBodyPartGroups, (Predicate<BodyPartGroupDef>)((BodyPartGroupDef p) => GenCollection.Any<BodyPartGroupDef>(partRec.groups, (Predicate<BodyPartGroupDef>)((BodyPartGroupDef p2) => p == p2))));
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		try
		{
			if (!respawningAfterLoad || !(((object)base.parent).GetType() == typeof(ThingWithComps)) || !(((Thing)base.parent).def.thingClass != typeof(ThingWithComps)))
			{
				return;
			}
			Apparel_Shield apparel_Shield = ThingMaker.MakeThing(ThingDef.Named(((Def)((Thing)base.parent).def).defName), ((Thing)base.parent).Stuff) as Apparel_Shield;
			((Thing)apparel_Shield).HitPoints = ((Thing)base.parent).HitPoints;
			QualityCategory val = default(QualityCategory);
			if (QualityUtility.TryGetQuality((Thing)(object)base.parent, ref val))
			{
				CompQuality compQuality = ((ThingWithComps)apparel_Shield).compQuality;
				if (compQuality != null)
				{
					compQuality.SetQuality(val, (ArtGenerationContext?)(ArtGenerationContext)1);
				}
			}
			GenSpawn.Spawn((Thing)(object)apparel_Shield, ((Thing)base.parent).Position, ((Thing)base.parent).Map, (WipeMode)0);
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
		catch
		{
		}
	}

	public override void PostExposeData()
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Invalid comparison between Unknown and I4
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		Scribe_Values.Look<bool>(ref equippedOffHand, "equippedOffHand", false, false);
		((ThingComp)this).PostExposeData();
		if ((int)Scribe.mode != 4 || !(((object)base.parent).GetType() == typeof(ThingWithComps)) || !(((Thing)base.parent).def.thingClass != typeof(ThingWithComps)))
		{
			return;
		}
		try
		{
			IThingHolder parentHolder = ((ThingComp)this).ParentHolder;
			Pawn_EquipmentTracker val = (Pawn_EquipmentTracker)(object)((parentHolder is Pawn_EquipmentTracker) ? parentHolder : null);
			if (val != null)
			{
				Apparel_Shield apparel_Shield = ThingMaker.MakeThing(ThingDef.Named(((Def)((Thing)base.parent).def).defName), ((Thing)base.parent).Stuff) as Apparel_Shield;
				((Thing)apparel_Shield).HitPoints = ((Thing)base.parent).HitPoints;
				QualityCategory val2 = default(QualityCategory);
				if (QualityUtility.TryGetQuality((Thing)(object)base.parent, ref val2))
				{
					CompQuality compQuality = ((ThingWithComps)apparel_Shield).compQuality;
					if (compQuality != null)
					{
						compQuality.SetQuality(val2, (ArtGenerationContext?)(ArtGenerationContext)1);
					}
				}
				val.Remove(base.parent);
				val.pawn.AddShield((Apparel)(object)apparel_Shield);
				((Thing)base.parent).Destroy((DestroyMode)0);
				return;
			}
			IThingHolder parentHolder2 = ((ThingComp)this).ParentHolder;
			Pawn_ApparelTracker val3 = (Pawn_ApparelTracker)(object)((parentHolder2 is Pawn_ApparelTracker) ? parentHolder2 : null);
			if (val3 == null)
			{
				return;
			}
			Apparel_Shield apparel_Shield2 = ThingMaker.MakeThing(ThingDef.Named(((Def)((Thing)base.parent).def).defName), ((Thing)base.parent).Stuff) as Apparel_Shield;
			((Thing)apparel_Shield2).HitPoints = ((Thing)base.parent).HitPoints;
			QualityCategory val4 = default(QualityCategory);
			if (QualityUtility.TryGetQuality((Thing)(object)base.parent, ref val4))
			{
				CompQuality compQuality2 = ((ThingWithComps)apparel_Shield2).compQuality;
				if (compQuality2 != null)
				{
					compQuality2.SetQuality(val4, (ArtGenerationContext?)(ArtGenerationContext)1);
				}
			}
			_003F val5 = val3;
			ThingWithComps parent = base.parent;
			((Pawn_ApparelTracker)val5).Remove((Apparel)(object)((parent is Apparel) ? parent : null));
			val3.pawn.AddShield((Apparel)(object)apparel_Shield2);
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
		catch
		{
		}
	}
}
