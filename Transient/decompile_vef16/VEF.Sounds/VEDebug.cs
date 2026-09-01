using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Sounds;

[StaticConstructorOnStartup]
public static class VEDebug
{
	public static readonly FieldRef<DebugWindowsOpener, WidgetRow> DebugWindowsOpener_widgetRow = AccessTools.FieldRefAccess<DebugWindowsOpener, WidgetRow>("widgetRow");

	private static void AddVEOptions()
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Invalid comparison between Unknown and I4
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Expected O, but got Unknown
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Expected O, but got Unknown
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Expected O, but got Unknown
		DebugWindowsOpener debugWindowOpener = Find.UIRoot.debugWindowOpener;
		if (!DebugWindowsOpener_widgetRow.Invoke(debugWindowOpener).ButtonIcon(TextureButton.VFELogo, "More options..", (Color?)null, (Color?)null, (Color?)null, true, -1f))
		{
			return;
		}
		List<FloatMenuOption> list = new List<FloatMenuOption>();
		if ((int)Current.ProgramState == 2)
		{
			list.Add(new FloatMenuOption("Sound test", (Action)delegate
			{
				if (!Find.WindowStack.TryRemove(typeof(EditWindow_SoundTest), true))
				{
					Find.WindowStack.Add((Window)(object)new EditWindow_SoundTest());
				}
			}, (MenuOptionPriority)5, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
		}
		list.Add(new FloatMenuOption("Restart", (Action)delegate
		{
			GenCommandLine.Restart();
		}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
		Find.WindowStack.Add((Window)new FloatMenu(list));
	}
}
