using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using VEF.Planet;
using Verse;

namespace VEF.Weapons;

[StaticConstructorOnStartup]
public class StatPart_Ammo : StatPart
{
	private static StatDef statRangedCooldownFactor;

	static StatPart_Ammo()
	{
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			statRangedCooldownFactor = StatDef.Named("VEF_RangedCooldownFactor");
		});
	}

	public override void TransformValue(StatRequest req, ref float val)
	{
		if (!((StatRequest)(ref req)).HasThing)
		{
			return;
		}
		IThingHolder parentHolder = ((StatRequest)(ref req)).Thing.ParentHolder;
		Pawn_EquipmentTracker val2 = (Pawn_EquipmentTracker)(object)((parentHolder is Pawn_EquipmentTracker) ? parentHolder : null);
		if (val2 == null)
		{
			return;
		}
		foreach (ThingWithComps item in GetAllEquipment(val2))
		{
			EquipmentOffsetConditions modExtension = ((Def)((Thing)item).def).GetModExtension<EquipmentOffsetConditions>();
			if (modExtension == null || modExtension.IsValid(((StatRequest)(ref req)).Thing, ((Thing)item).def))
			{
				val *= StatExtension.GetStatValue((Thing)(object)item, statRangedCooldownFactor, true, -1);
			}
		}
	}

	private static IEnumerable<ThingWithComps> GetAllEquipment(Pawn_EquipmentTracker eq)
	{
		List<ThingWithComps> list = eq.AllEquipmentListForReading.ToList();
		Pawn pawn = eq.pawn;
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_ApparelTracker apparel = pawn.apparel;
			obj = ((apparel != null) ? apparel.WornApparel : null);
		}
		if (obj != null)
		{
			list.AddRange((IEnumerable<ThingWithComps>)eq.pawn.apparel.WornApparel.ToList());
		}
		return list;
	}

	public override string ExplanationPart(StatRequest req)
	{
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		if (((StatRequest)(ref req)).HasThing)
		{
			IThingHolder parentHolder = ((StatRequest)(ref req)).Thing.ParentHolder;
			Pawn_EquipmentTracker val = (Pawn_EquipmentTracker)(object)((parentHolder is Pawn_EquipmentTracker) ? parentHolder : null);
			if (val != null)
			{
				StringBuilder stringBuilder = new StringBuilder();
				foreach (var (val2, equipmentOffsetConditions) in from apparel in GetAllEquipment(val)
					let conds = ((Def)((Thing)apparel).def).GetModExtension<EquipmentOffsetConditions>()
					where conds != null || Math.Abs(StatExtension.GetStatValue((Thing)(object)apparel, statRangedCooldownFactor, true, -1) - 1f) > 0.001f
					select (apparel: apparel, conds: conds))
				{
					stringBuilder.AppendLine((equipmentOffsetConditions == null || equipmentOffsetConditions.IsValid(((StatRequest)(ref req)).Thing, ((Thing)val2).def)) ? $"{((Def)((Thing)val2).def).LabelCap}: {statRangedCooldownFactor.Worker.ValueToString(StatExtension.GetStatValue((Thing)(object)val2, statRangedCooldownFactor, true, -1), true, (ToStringNumberSense)2)}" : string.Format("{0}: {1} {2} {3}", ((Def)((Thing)val2).def).LabelCap, ((Def)((StatRequest)(ref req)).Thing.def).LabelCap, Translator.Translate("VEF.IsToo"), (((StatRequest)(ref req)).Thing.def.techLevel > equipmentOffsetConditions.techLevels.Max()) ? Translator.Translate("VEF.Advanced") : Translator.Translate("VEF.Primitive")));
				}
				return stringBuilder.ToString();
			}
		}
		return "";
	}
}
