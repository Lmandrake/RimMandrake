using System;
using System.Collections.Generic;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

[StaticConstructorOnStartup]
public class Command_SetStoneType : Command
{
	public CompRockSpawner building;

	public Command_SetStoneType()
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		base.defaultDesc = TaggedString.op_Implicit(Translator.Translate("VFE_ChooseMineDesc"));
		base.defaultLabel = TaggedString.op_Implicit(Translator.Translate("VFE_ChooseMine"));
		base.icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Commands/VFE_RandomChunks", true);
	}

	public override void ProcessInput(Event ev)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Expected O, but got Unknown
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Expected O, but got Unknown
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Expected O, but got Unknown
		((Command)this).ProcessInput(ev);
		List<FloatMenuOption> list = new List<FloatMenuOption>();
		IEnumerable<ThingDef> enumerable = Find.World.NaturalRockTypesIn(((Thing)((ThingComp)building).parent).Map.Tile);
		List<ThingDef> list2 = new List<ThingDef>();
		foreach (ThingDef item in enumerable)
		{
			list2.Add(item.building.mineableThing);
		}
		list.Add(new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("VFE_ChunkRandomMine")), (Action)delegate
		{
			building.RockTypeToMine = null;
		}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 29f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
		foreach (ThingDef chunk in list2)
		{
			list.Add(new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VFE_ChunkToMine", NamedArgument.op_Implicit(((Def)chunk).LabelCap))), (Action)delegate
			{
				building.RockTypeToMine = chunk;
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 29f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
		}
		Find.WindowStack.Add((Window)new FloatMenu(list));
	}
}
