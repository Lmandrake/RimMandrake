using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompCustomizableGraphic : ThingComp
{
	private class Command_ActionSameThingAndStyleDef : Command_Action
	{
		public ThingDef targetDef;

		public ThingStyleDef targetStyleDef;

		public override bool GroupsWith(Gizmo other)
		{
			if (other is Command_ActionSameThingAndStyleDef command_ActionSameThingAndStyleDef && command_ActionSameThingAndStyleDef.targetDef == targetDef && command_ActionSameThingAndStyleDef.targetStyleDef == targetStyleDef)
			{
				return ((Command)this).GroupsWith(other);
			}
			return false;
		}
	}

	public int? tempSelectedGraphicIndex;

	public CompProperties_CustomizableGraphic Props => base.props as CompProperties_CustomizableGraphic;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		if (!respawningAfterLoad && !((Thing)base.parent).overrideGraphicIndex.HasValue)
		{
			ThingStyleDef styleDef = ((Thing)base.parent).StyleDef;
			if (styleDef == null || !Props.defaultStyleIndex.TryGetValue(styleDef, out var value))
			{
				value = Props.defaultIndex;
			}
			if (value >= 0)
			{
				((Thing)base.parent).overrideGraphicIndex = value;
			}
		}
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		if (!((Thing)base.parent).Spawned || base.parent is Blueprint_Install)
		{
			yield break;
		}
		(ThingDef, ThingStyleDef, Color) thingDefStyleDrawColor = GetThingDefStyleDrawColor();
		ThingDef def = thingDefStyleDrawColor.Item1;
		ThingStyleDef style = thingDefStyleDrawColor.Item2;
		Color color = thingDefStyleDrawColor.Item3;
		ThingStyleDef obj = style;
		if (IsSupportedGraphicType(((obj != null) ? obj.Graphic : null) ?? ((BuildableDef)def).graphic))
		{
			yield return (Gizmo)(object)new Command_ActionSameThingAndStyleDef
			{
				defaultLabel = (Props.gizmoLabel ?? TaggedString.op_Implicit(Translator.Translate("VFE.ChangeVisualLabel"))),
				defaultDesc = (Props.gizmoDescription ?? TaggedString.op_Implicit(Translator.Translate("VFE.ChangeVisualDesc"))),
				icon = (Texture)(object)Props.Icon,
				targetDef = def,
				targetStyleDef = style,
				action = delegate
				{
					//IL_000d: Unknown result type (might be due to invalid IL or missing references)
					SelectGraphicMenu(def, style, color, Props);
				}
			};
		}
	}

	private (ThingDef, ThingStyleDef, Color) GetThingDefStyleDrawColor()
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		ThingWithComps parent = base.parent;
		Frame val = (Frame)(object)((parent is Frame) ? parent : null);
		if (val != null)
		{
			return (val.BuildDef, ((Thing)val).StyleDef, ((Thing)val).DrawColor);
		}
		ThingWithComps parent2 = base.parent;
		Blueprint_Build val2 = (Blueprint_Build)(object)((parent2 is Blueprint_Build) ? parent2 : null);
		if (val2 != null)
		{
			return (val2.BuildDef, ((Thing)val2).StyleDef, (val2.stuffToUse == null) ? Color.white : ((BuildableDef)val2.BuildDef).GetColorForStuff(val2.stuffToUse));
		}
		ThingWithComps parent3 = base.parent;
		Blueprint_Install val3 = (Blueprint_Install)(object)((parent3 is Blueprint_Install) ? parent3 : null);
		if (val3 != null)
		{
			Thing thingToInstall = val3.ThingToInstall;
			return (thingToInstall.def, thingToInstall.StyleDef, thingToInstall.DrawColor);
		}
		return (((Thing)base.parent).def, ((Thing)base.parent).StyleDef, ((Thing)base.parent).DrawColor);
	}

	private static void SelectGraphicMenu(ThingDef def, ThingStyleDef style, Color color, CompProperties_CustomizableGraphic props)
	{
		//IL_01fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		//IL_0216: Expected O, but got Unknown
		//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e6: Expected O, but got Unknown
		ThingStyleDef obj = style;
		Graphic val = ((obj != null) ? obj.Graphic : null) ?? ((BuildableDef)def).graphic;
		Graphic_Indexed val2 = (Graphic_Indexed)(object)((val is Graphic_Indexed) ? val : null);
		int subGraphicsCount;
		Func<int, Graphic> func;
		if (val2 == null)
		{
			Graphic_Random val3 = (Graphic_Random)(object)((val is Graphic_Random) ? val : null);
			if (val3 == null)
			{
				return;
			}
			subGraphicsCount = val3.SubGraphicsCount;
			func = (int i) => val3.SubGraphicAtIndex(i);
		}
		else
		{
			subGraphicsCount = val2.SubGraphicsCount;
			func = (int i) => val2.SubGraphicAtIndex(i);
		}
		List<FloatMenuOption> list = new List<FloatMenuOption>();
		List<CompCustomizableGraphic> comps = (from x in Find.Selector.SelectedObjects.OfType<ThingWithComps>()
			select x.GetComp<CompCustomizableGraphic>()).Where(delegate(CompCustomizableGraphic x)
		{
			if (x == null || ((ThingComp)x).parent is Blueprint_Install)
			{
				return false;
			}
			var (val4, val5, _) = x.GetThingDefStyleDrawColor();
			return val4 == def && val5 == style;
		}).ToList();
		if (style == null || props.styledGraphicData == null || !props.styledGraphicData.TryGetValue(style, out var value))
		{
			value = props.defaultGraphicData;
		}
		for (int j = 0; j < subGraphicsCount; j++)
		{
			int index = j;
			Graphic val6 = func(j);
			string text;
			int num;
			if (value != null && j < value.Count)
			{
				text = value[j].name;
				num = value[j].sortingPriority;
			}
			else
			{
				text = val6.path.Substring(val6.path.LastIndexOf('/') + 1);
				num = 0;
			}
			list.Add(new FloatMenuOption(text, (Action)delegate
			{
				SelectGraphic(comps, index);
			}, ContentFinder<Texture2D>.Get(val6.path, true), color, (MenuOptionPriority)4, (Action<Rect>)delegate
			{
				SelectTemporaryGraphics(comps, index);
			}, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, num, (HorizontalJustification)0, false));
		}
		if (GenCollection.Any<FloatMenuOption>(list))
		{
			FloatMenu val7 = new FloatMenu(list)
			{
				onCloseCallback = delegate
				{
					SelectTemporaryGraphics(comps, null);
				}
			};
			Find.WindowStack.Add((Window)(object)val7);
		}
		else
		{
			Log.Error($"Tried to select custom graphic for {def}, but no custom graphic found.");
		}
	}

	public static void SelectGraphic(List<CompCustomizableGraphic> comps, int graphicIndex)
	{
		foreach (CompCustomizableGraphic comp in comps)
		{
			comp.SelectGraphic(graphicIndex);
		}
	}

	public void SelectGraphic(int graphicIndex)
	{
		SelectGraphic(graphicIndex, temporary: false, IsSupportedGraphicType(((Thing)base.parent).Graphic));
		Blueprint_Install val = InstallBlueprintUtility.ExistingBlueprintFor((Thing)(object)base.parent);
		if (val != null)
		{
			((ThingWithComps)val).GetComp<CompCustomizableGraphic>()?.SelectGraphic(graphicIndex, temporary: false, IsSupportedGraphicType(((Thing)val).Graphic));
		}
	}

	private static void SelectTemporaryGraphics(List<CompCustomizableGraphic> comps, int? graphicIndex)
	{
		foreach (CompCustomizableGraphic comp in comps)
		{
			if (((Thing)((ThingComp)comp).parent).Spawned)
			{
				comp.SelectGraphic(graphicIndex, temporary: true, IsSupportedGraphicType(((Thing)((ThingComp)comp).parent).Graphic));
			}
		}
	}

	private void SelectGraphic(int? graphicIndex, bool temporary, bool canChangeGraphic)
	{
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		bool flag = graphicIndex == ((Thing)base.parent).OverrideGraphicIndex;
		if (flag && temporary)
		{
			return;
		}
		if (!graphicIndex.HasValue)
		{
			if (tempSelectedGraphicIndex.HasValue)
			{
				((Thing)base.parent).overrideGraphicIndex = tempSelectedGraphicIndex;
			}
		}
		else
		{
			if (temporary)
			{
				int? num = tempSelectedGraphicIndex;
				if (!num.HasValue)
				{
					tempSelectedGraphicIndex = ((Thing)base.parent).overrideGraphicIndex;
				}
			}
			else
			{
				tempSelectedGraphicIndex = null;
			}
			((Thing)base.parent).overrideGraphicIndex = graphicIndex;
		}
		if (!flag && canChangeGraphic && ((Thing)base.parent).Spawned)
		{
			((Thing)base.parent).Map.mapDrawer.SectionAt(((Thing)base.parent).Position).RegenerateAllLayers();
		}
	}

	public override void PostExposeData()
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Invalid comparison between Unknown and I4
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int?>(ref tempSelectedGraphicIndex, "tempSelectedGraphicIndex", (int?)null, false);
		if ((int)Scribe.mode == 4 && tempSelectedGraphicIndex.HasValue)
		{
			((Thing)base.parent).overrideGraphicIndex = tempSelectedGraphicIndex;
			tempSelectedGraphicIndex = null;
		}
	}

	private static bool IsSupportedGraphicType(Graphic graphic)
	{
		if (graphic is Graphic_Indexed || graphic is Graphic_Random)
		{
			return true;
		}
		return false;
	}

	public void Rotate(RotationDirection direction)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Invalid comparison between I4 and Unknown
		if ((int)direction == 0 || !IsSupportedGraphicType(((Thing)base.parent).Graphic))
		{
			return;
		}
		int num = ((Thing)base.parent).OverrideGraphicIndex ?? (-1);
		if (num < 0)
		{
			return;
		}
		List<CompProperties_CustomizableGraphic.CustomizableGraphicOptionData> value;
		if (((Thing)base.parent).StyleDef == null)
		{
			if (Props.defaultGraphicData == null)
			{
				return;
			}
			value = Props.defaultGraphicData;
		}
		else if (Props.styledGraphicData == null || !Props.styledGraphicData.TryGetValue(((Thing)base.parent).StyleDef, out value))
		{
			return;
		}
		if (num >= value.Count)
		{
			return;
		}
		for (int i = 0; i < (int)direction; i++)
		{
			num = value[num].clockwiseRotationIndex;
			if (num < 0 || num >= value.Count)
			{
				break;
			}
		}
		if (num >= 0 && num < value.Count)
		{
			SelectGraphic(num);
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingComp)this).CompGetGizmosExtra();
	}
}
