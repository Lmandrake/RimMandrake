using System;
using System.Collections.Generic;
using System.Linq;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using VEF.Things;
using Verse;

namespace VEF;

public static class DebugActions
{
	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void SpawnWorldObjectLayered()
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Expected O, but got Unknown
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		Ray val = Find.WorldCamera.ScreenPointToRay(Vector2.op_Implicit(UI.MousePositionOnUI * Prefs.UIScale));
		int worldLayerMask = WorldCameraManager.WorldLayerMask;
		PlanetLayer selected = PlanetLayer.Selected;
		PlanetLayer.Selected = Find.WorldGrid.FirstLayerOfDef(PlanetLayerDefOf.Surface);
		WorldTerrainColliderManager.EnsureRaycastCollidersUpdated();
		PlanetTile planetTile = PlanetTile.Invalid;
		RaycastHit val2 = default(RaycastHit);
		if (Physics.Raycast(val, ref val2, 1500f, worldLayerMask))
		{
			PlanetTile val4 = default(PlanetTile);
			foreach (WorldDrawLayerBase allVisibleDrawLayer in Find.World.renderer.AllVisibleDrawLayers)
			{
				WorldDrawLayer val3 = (WorldDrawLayer)(object)((allVisibleDrawLayer is WorldDrawLayer) ? allVisibleDrawLayer : null);
				if (val3 != null && val3.Raycastable && val3.TryGetTileFromRayHit(val2, ref val4))
				{
					planetTile = val4;
				}
			}
		}
		PlanetLayer.Selected = selected;
		List<DebugMenuOption> list = new List<DebugMenuOption>();
		int num = default(int);
		PlanetLayer val5 = default(PlanetLayer);
		foreach (KeyValuePair<int, PlanetLayer> planetLayer in Find.WorldGrid.PlanetLayers)
		{
			GenCollection.Deconstruct<int, PlanetLayer>(planetLayer, ref num, ref val5);
			PlanetLayer val6 = val5;
			PlanetLayer layer = val6;
			list.Add(new DebugMenuOption($"({val6.LayerID}) {((Def)val6.Def).defName}", (DebugMenuOptionMode)0, (Action)delegate
			{
				//IL_0012: Unknown result type (might be due to invalid IL or missing references)
				//IL_0018: Unknown result type (might be due to invalid IL or missing references)
				//IL_001d: Unknown result type (might be due to invalid IL or missing references)
				//IL_008c: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
				//IL_00bb: Expected O, but got Unknown
				planetTile = layer.GetClosestTile_NewTemp(planetTile, false);
				if (!((PlanetTile)(ref planetTile)).Valid)
				{
					Messages.Message("Invalid", MessageTypeDefOf.RejectInput, false);
				}
				else
				{
					List<DebugMenuOption> list2 = new List<DebugMenuOption>();
					foreach (WorldObjectDef allDef in DefDatabase<WorldObjectDef>.AllDefs)
					{
						WorldObjectDef localDef = allDef;
						list2.Add(new DebugMenuOption(((Def)localDef).defName, (DebugMenuOptionMode)0, (Action)delegate
						{
							//IL_0021: Unknown result type (might be due to invalid IL or missing references)
							//IL_0027: Unknown result type (might be due to invalid IL or missing references)
							//IL_002c: Unknown result type (might be due to invalid IL or missing references)
							//IL_0071: Unknown result type (might be due to invalid IL or missing references)
							planetTile = layer.GetClosestTile_NewTemp(planetTile, false);
							if (!((PlanetTile)(ref planetTile)).Valid)
							{
								Messages.Message("Invalid", MessageTypeDefOf.RejectInput, false);
							}
							else
							{
								WorldObject val7 = WorldObjectMaker.MakeWorldObject(localDef);
								val7.Tile = planetTile;
								Find.WorldObjects.Add(val7);
							}
						}));
					}
					Find.WindowStack.Add((Window)new Dialog_DebugOptionListLister((IEnumerable<DebugMenuOption>)list2, (string)null));
				}
			}));
		}
		Find.WindowStack.Add((Window)new Dialog_DebugOptionListLister((IEnumerable<DebugMenuOption>)list, (string)null));
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	private static void ChangeThingStylePlayerCrafted()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Expected O, but got Unknown
		var (thing, extension) = Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).Select(delegate(Thing x)
		{
			object item;
			if (x == null)
			{
				item = null;
			}
			else
			{
				ThingDef def = x.def;
				item = ((def != null) ? ((Def)def).GetModExtension<ThingDefExtension>() : null);
			}
			return (thing: x, extension: (ThingDefExtension)item);
		}).FirstOrDefault(((Thing thing, ThingDefExtension extension) x) => x.extension != null && !GenList.NullOrEmpty<ThingStyleChance>((IList<ThingStyleChance>)x.extension.playerCraftedStyles));
		if (thing == null || extension == null)
		{
			return;
		}
		List<DebugMenuOption> list = new List<DebugMenuOption>
		{
			new DebugMenuOption("Standard", (DebugMenuOptionMode)0, (Action)delegate
			{
				SetStyle(null);
			}),
			new DebugMenuOption("Random", (DebugMenuOptionMode)0, (Action)delegate
			{
				SetStyle(GenCollection.RandomElementByWeight<ThingStyleChance>((IEnumerable<ThingStyleChance>)extension.playerCraftedStyles, (Func<ThingStyleChance, float>)((ThingStyleChance x) => x.Chance)).StyleDef);
			})
		};
		foreach (ThingStyleChance style2 in extension.playerCraftedStyles)
		{
			list.Add(new DebugMenuOption(((Def)style2.StyleDef).defName, (DebugMenuOptionMode)0, (Action)delegate
			{
				SetStyle(style2.StyleDef);
			}));
		}
		Find.WindowStack.Add((Window)new Dialog_DebugOptionListLister((IEnumerable<DebugMenuOption>)list, (string)null));
		void SetStyle(ThingStyleDef style)
		{
			thing.StyleDef = style;
			thing.DirtyMapMesh(thing.Map);
		}
	}
}
