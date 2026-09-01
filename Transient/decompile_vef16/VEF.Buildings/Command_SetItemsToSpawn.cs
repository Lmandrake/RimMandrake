using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

[StaticConstructorOnStartup]
public class Command_SetItemsToSpawn : Command
{
	public CompConfigurableSpawner building;

	public Command_SetItemsToSpawn()
	{
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		foreach (object selectedObject in Find.Selector.SelectedObjects)
		{
			Building val = (Building)((selectedObject is Building) ? selectedObject : null);
			building = ThingCompUtility.TryGetComp<CompConfigurableSpawner>((Thing)(object)val);
			if (building != null)
			{
				if (building.currentThingList != null)
				{
					base.icon = (Texture)(object)ContentFinder<Texture2D>.Get(building.currentThingList.GizmoIcon, true);
					base.defaultLabel = TaggedString.op_Implicit(Translator.Translate(building.currentThingList.GizmoLabel));
					base.defaultDesc = TaggedString.op_Implicit(Translator.Translate(building.currentThingList.GizmoDescription));
				}
				else
				{
					base.icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/IP_SetOutput", true);
					base.defaultLabel = TaggedString.op_Implicit(Translator.Translate("IP_ChooseOutput"));
					base.defaultDesc = TaggedString.op_Implicit(Translator.Translate("IP_ChooseOutput"));
				}
			}
		}
	}

	public override void ProcessInput(Event ev)
	{
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Expected O, but got Unknown
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Expected O, but got Unknown
		((Command)this).ProcessInput(ev);
		List<FloatMenuOption> list = new List<FloatMenuOption>();
		foreach (ConfigurableSpawnerDef thingList in DefDatabase<ConfigurableSpawnerDef>.AllDefs.Where((ConfigurableSpawnerDef element) => element.building == ((Def)((Thing)((ThingComp)building).parent).def).defName))
		{
			if (building.CanAccept(thingList))
			{
				list.Add(new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate(thingList.listName)), (Action)delegate
				{
					building.currentThingList = thingList;
					building.ResetCountdown();
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 29f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			}
		}
		Find.WindowStack.Add((Window)new FloatMenu(list));
	}
}
