using System;
using System.Collections.Generic;
using System.Linq;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace BigAndSmall.Debugging;

public static class BigAndSmallDebugActions
{
	public const int lblPad = 0;

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static List<DebugActionNode> TransformToRace()
	{
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Expected O, but got Unknown
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Expected O, but got Unknown
		List<DebugActionNode> list = new List<DebugActionNode>();
		foreach (ThingDef def in DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x != null && x.race?.intelligence == (Intelligence?)2 && !x.IsCorpse))
		{
			list.Add(new DebugActionNode($"{((Def)def).defName}\t ({((Def)def).LabelCap})", (DebugActionType)1, (Action)delegate
			{
				//IL_000a: Unknown result type (might be due to invalid IL or missing references)
				foreach (Pawn item in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>())
				{
					item.SwapThingDef(def, state: true, 100);
				}
			}, (Action<Pawn>)null));
		}
		foreach (ThingDef def2 in DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x != null && x.race?.intelligence == (Intelligence?)2 && !x.IsCorpse))
		{
			list.Add(new DebugActionNode($"[FORCE]: {((Def)def2).defName}\t ({((Def)def2).LabelCap})", (DebugActionType)1, (Action)delegate
			{
				//IL_000a: Unknown result type (might be due to invalid IL or missing references)
				foreach (Pawn item2 in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>())
				{
					item2.SwapThingDef(def2, state: true, 999, force: true, null, permitFusion: false);
				}
			}, (Action<Pawn>)null));
		}
		return list;
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static List<DebugActionNode> SpawnColonistOfXeno()
	{
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Expected O, but got Unknown
		List<DebugActionNode> list = new List<DebugActionNode>();
		foreach (XenotypeDef xeno in from x in DefDatabase<XenotypeDef>.AllDefs
			select (x) into kd
			orderby ((Def)kd).defName
			select kd)
		{
			PawnKindDef localKindDef = PawnKindDefOf.Colonist;
			list.Add(new DebugActionNode($"{((Def)xeno).defName}\t ({((Def)xeno).LabelCap})", (DebugActionType)1, (Action)null, (Action<Pawn>)null)
			{
				category = DebugToolsSpawning.GetCategoryForPawnKind(localKindDef),
				action = delegate
				{
					//IL_0028: Unknown result type (might be due to invalid IL or missing references)
					Faction val = FactionUtility.DefaultFactionFrom(localKindDef.defaultFactionDef);
					Pawn val2 = PawnGenerator.GeneratePawn(localKindDef, val, (PlanetTile?)null);
					GenSpawn.Spawn((Thing)(object)val2, UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
					DebugToolsSpawning.PostPawnSpawn(val2);
					DebugUIPatches.SetXenotypeAndRace(val2, xeno);
					if (BS.Settings.recruitDevSpawned)
					{
						((Thing)val2).SetFaction(Faction.OfPlayer, (Pawn)null);
					}
				}
			});
		}
		return list;
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static List<DebugActionNode> SpawnVillagerOfXeno()
	{
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Expected O, but got Unknown
		List<DebugActionNode> list = new List<DebugActionNode>();
		foreach (XenotypeDef xeno in from x in DefDatabase<XenotypeDef>.AllDefs
			select (x) into kd
			orderby ((Def)kd).defName
			select kd)
		{
			PawnKindDef localKindDef = PawnKindDefOf.Villager;
			list.Add(new DebugActionNode($"{((Def)xeno).defName}\t ({((Def)xeno).LabelCap})", (DebugActionType)1, (Action)null, (Action<Pawn>)null)
			{
				category = DebugToolsSpawning.GetCategoryForPawnKind(localKindDef),
				action = delegate
				{
					//IL_0028: Unknown result type (might be due to invalid IL or missing references)
					Faction val = FactionUtility.DefaultFactionFrom(localKindDef.defaultFactionDef);
					Pawn val2 = PawnGenerator.GeneratePawn(localKindDef, val, (PlanetTile?)null);
					GenSpawn.Spawn((Thing)(object)val2, UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
					DebugToolsSpawning.PostPawnSpawn(val2);
					DebugUIPatches.SetXenotypeAndRace(val2, xeno);
					if (BS.Settings.recruitDevSpawned)
					{
						((Thing)val2).SetFaction(Faction.OfPlayer, (Pawn)null);
					}
				}
			});
		}
		return list;
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void SpawnRandomHumanKind()
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		IEnumerable<PawnKindDef> enumerable = DefDatabase<PawnKindDef>.AllDefs.Where(delegate(PawnKindDef x)
		{
			ThingDef race = x.race;
			if (race != null && race.race.Humanlike)
			{
				ThingDef race2 = x.race;
				if (race2 == null)
				{
					return false;
				}
				return !race2.IsHumanlikeAnimal();
			}
			return false;
		});
		if (enumerable.Any())
		{
			GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(GenCollection.RandomElement<PawnKindDef>(enumerable), (Faction)null, (PlanetTile?)null), UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void SpawnRandomAnimal()
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		IEnumerable<PawnKindDef> enumerable = DefDatabase<PawnKindDef>.AllDefs.Where(delegate(PawnKindDef x)
		{
			ThingDef race = x.race;
			return race != null && race.race.Animal;
		});
		if (enumerable.Any())
		{
			GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(GenCollection.RandomElement<PawnKindDef>(enumerable), (Faction)null, (PlanetTile?)null), UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void SpawnRandomSapientAnimal()
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		IEnumerable<PawnKindDef> enumerable = DefDatabase<PawnKindDef>.AllDefs.Where(delegate(PawnKindDef x)
		{
			ThingDef race = x.race;
			return race != null && race.race.Animal;
		});
		if (enumerable.Any())
		{
			GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(GenCollection.RandomElement<PawnKindDef>(enumerable), (Faction)null, (PlanetTile?)null).SwapAnimalToSapientVersion(), UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void SpawnRandomMechanoid()
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		IEnumerable<PawnKindDef> enumerable = DefDatabase<PawnKindDef>.AllDefs.Where(delegate(PawnKindDef x)
		{
			ThingDef race = x.race;
			return race != null && race.race.IsMechanoid;
		});
		if (enumerable.Any())
		{
			GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(GenCollection.RandomElement<PawnKindDef>(enumerable), (Faction)null, (PlanetTile?)null), UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void SpawnRandomSapientMechanoid()
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		IEnumerable<PawnKindDef> enumerable = DefDatabase<PawnKindDef>.AllDefs.Where(delegate(PawnKindDef x)
		{
			ThingDef race = x.race;
			return race != null && race.race.IsMechanoid;
		});
		if (enumerable.Any())
		{
			GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(GenCollection.RandomElement<PawnKindDef>(enumerable), (Faction)null, (PlanetTile?)null).SwapAnimalToSapientVersion(), UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static List<DebugActionNode> SpawnRandomPawnOf()
	{
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Expected O, but got Unknown
		List<DebugActionNode> list = new List<DebugActionNode>();
		foreach (XenotypeDef xeno in from x in DefDatabase<XenotypeDef>.AllDefs
			select (x) into kd
			orderby ((Def)kd).defName
			select kd)
		{
			list.Add(new DebugActionNode($"{((Def)xeno).defName}\t ({((Def)xeno).LabelCap})", (DebugActionType)1, (Action)null, (Action<Pawn>)null)
			{
				action = delegate
				{
					//IL_0050: Unknown result type (might be due to invalid IL or missing references)
					PawnKindDef obj = GenCollection.RandomElementWithFallback<PawnKindDef>(DefDatabase<PawnKindDef>.AllDefs.Where(delegate(PawnKindDef x)
					{
						if (x.race == ThingDefOf.Human && x.showInDebugSpawner)
						{
							RaceProperties raceProps = x.RaceProps;
							if (raceProps == null)
							{
								return false;
							}
							return raceProps.Humanlike;
						}
						return false;
					}), PawnKindDefOf.Colonist);
					Faction val = FactionUtility.DefaultFactionFrom(obj.defaultFactionDef);
					Pawn val2 = PawnGenerator.GeneratePawn(obj, val, (PlanetTile?)null);
					GenSpawn.Spawn((Thing)(object)val2, UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
					DebugToolsSpawning.PostPawnSpawn(val2);
					DebugUIPatches.SetXenotypeAndRace(val2, xeno);
					if (BS.Settings.recruitDevSpawned)
					{
						((Thing)val2).SetFaction(Faction.OfPlayer, (Pawn)null);
					}
				}
			});
		}
		return list;
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static List<DebugActionNode> SpawnColonistOfRace()
	{
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Expected O, but got Unknown
		List<DebugActionNode> list = new List<DebugActionNode>();
		foreach (ThingDef def in DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x != null && x.race?.intelligence == (Intelligence?)2 && !x.IsCorpse))
		{
			PawnKindDef localKindDef = PawnKindDefOf.Villager;
			list.Add(new DebugActionNode($"{((Def)def).defName}\t ({((Def)def).LabelCap})", (DebugActionType)1, (Action)null, (Action<Pawn>)null)
			{
				category = DebugToolsSpawning.GetCategoryForPawnKind(localKindDef),
				action = delegate
				{
					//IL_0028: Unknown result type (might be due to invalid IL or missing references)
					Faction val = FactionUtility.DefaultFactionFrom(localKindDef.defaultFactionDef);
					Pawn val2 = PawnGenerator.GeneratePawn(localKindDef, val, (PlanetTile?)null);
					GenSpawn.Spawn((Thing)(object)val2, UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
					DebugToolsSpawning.PostPawnSpawn(val2);
					val2.SwapThingDef(def, state: true, 9999);
					if (BS.Settings.recruitDevSpawned)
					{
						((Thing)val2).SetFaction(Faction.OfPlayer, (Pawn)null);
					}
				}
			});
		}
		return list;
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void ForceRefreshCacheOnPawn()
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		foreach (Pawn item in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>())
		{
			HumanoidPawnScaler.GetCache(item, forceRefresh: true);
			Log.Message("Forced refresh on " + ((Entity)item).LabelCap);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void MakeSapientVersionOf()
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		foreach (Pawn item in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>())
		{
			item.SwapAnimalToSapientVersion();
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void ClearCacheForPawn()
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		foreach (Pawn pawn in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>())
		{
			BigAndSmallCache.ScribedCache.RemoveWhere((BSCache x) => x.pawn == pawn);
			BigAndSmallCache.refreshQueue.Clear();
			BigAndSmallCache.queuedJobs.Clear();
			BigAndSmallCache.schedulePostUpdate.Clear();
			BigAndSmallCache.scheduleFullUpdate.Clear();
			DictCache<Pawn, BSCache>.Cache.TryRemove(pawn, out var _);
			HumanoidPawnScaler.GetCache(pawn, forceRefresh: true);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void ClearJunk()
	{
		DebugToolsGeneral.GenericRectTool("Clear Junk", (Action<CellRect>)delegate(CellRect rect)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			ClearAreaOfJunk(rect, Find.CurrentMap);
		}, false);
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void DebugEditCustomizableGraphic()
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		using IEnumerator<Pawn> enumerator = Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>().GetEnumerator();
		if (enumerator.MoveNext())
		{
			EditPawnWindow editPawnWindow = new EditPawnWindow((ILoadReferenceable)(object)enumerator.Current);
			Find.WindowStack.Add((Window)(object)editPawnWindow);
		}
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static List<DebugActionNode> MiscDebug()
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Expected O, but got Unknown
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Expected O, but got Unknown
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Expected O, but got Unknown
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Expected O, but got Unknown
		//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Expected O, but got Unknown
		//IL_0121: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Expected O, but got Unknown
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Expected O, but got Unknown
		//IL_0183: Unknown result type (might be due to invalid IL or missing references)
		//IL_018d: Expected O, but got Unknown
		return new List<DebugActionNode>
		{
			new DebugActionNode("Set Graphics Dirty", (DebugActionType)1, (Action)delegate
			{
				//IL_000a: Unknown result type (might be due to invalid IL or missing references)
				foreach (Pawn item in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>())
				{
					item.Drawer.renderer.SetAllGraphicsDirty();
				}
			}, (Action<Pawn>)null),
			new DebugActionNode("Set Age to 0", (DebugActionType)1, (Action)delegate
			{
				//IL_000a: Unknown result type (might be due to invalid IL or missing references)
				foreach (Pawn item2 in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>())
				{
					item2.ageTracker.AgeBiologicalTicks = 0L;
				}
			}, (Action<Pawn>)null),
			new DebugActionNode("Remove Custom Graphics", (DebugActionType)1, (Action)delegate
			{
				RemoveCustomGraphics();
			}, (Action<Pawn>)null),
			new DebugActionNode("Set Custom Color A", (DebugActionType)1, (Action)delegate
			{
				SetCustomColor(0);
			}, (Action<Pawn>)null),
			new DebugActionNode("Set Custom Color B", (DebugActionType)1, (Action)delegate
			{
				SetCustomColor(1);
			}, (Action<Pawn>)null),
			new DebugActionNode("Set Custom Color C", (DebugActionType)1, (Action)delegate
			{
				SetCustomColor(2);
			}, (Action<Pawn>)null),
			new DebugActionNode("Randomise Faction", (DebugActionType)1, (Action)delegate
			{
				DebugToolsGeneral.GenericRectTool("Randomize Faction", (Action<CellRect>)delegate(CellRect rect)
				{
					//IL_0002: Unknown result type (might be due to invalid IL or missing references)
					//IL_0007: Unknown result type (might be due to invalid IL or missing references)
					//IL_000c: Unknown result type (might be due to invalid IL or missing references)
					Enumerator enumerator3 = ((CellRect)(ref rect)).GetEnumerator();
					try
					{
						Faction val = default(Faction);
						while (((Enumerator)(ref enumerator3)).MoveNext())
						{
							foreach (Pawn item3 in GridsUtility.GetThingList(((Enumerator)(ref enumerator3)).Current, Find.CurrentMap).OfType<Pawn>())
							{
								if (Find.FactionManager.TryGetRandomNonColonyHumanlikeFaction(ref val, false, false, (TechLevel)0, (TechLevel)0, false, false))
								{
									((Thing)item3).SetFaction(val, (Pawn)null);
								}
							}
						}
					}
					finally
					{
						((IDisposable)(Enumerator)(ref enumerator3)/*cast due to .constrained prefix*/).Dispose();
					}
				}, false);
			}, (Action<Pawn>)null),
			new DebugActionNode("Test Apparel Restrictions", (DebugActionType)1, (Action)delegate
			{
				//IL_000a: Unknown result type (might be due to invalid IL or missing references)
				foreach (Pawn item4 in Find.CurrentMap.thingGrid.ThingsAt(UI.MouseCell()).OfType<Pawn>())
				{
					ApparelRestrictions.DebugTestAllWearable(item4);
				}
			}, (Action<Pawn>)null)
		};
	}

	public static void RemoveCustomGraphics()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 val = UI.MouseCell();
		foreach (Thing item in Find.CurrentMap.thingGrid.ThingsAt(val).ToList())
		{
			Pawn val2 = (Pawn)(object)((item is Pawn) ? item : null);
			if (val2 == null)
			{
				continue;
			}
			if (val2.apparel != null)
			{
				foreach (Apparel item2 in val2.apparel.WornApparel)
				{
					CustomizableGraphic.Replace((Thing)(object)item2, null);
				}
			}
			CustomizableGraphic.Replace(item, null);
		}
		foreach (Pawn item3 in Find.CurrentMap.thingGrid.ThingsAt(val).OfType<Pawn>())
		{
			item3.Drawer.renderer.SetAllGraphicsDirty();
		}
	}

	public static void SetCustomColor(int slot)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Expected O, but got Unknown
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Expected O, but got Unknown
		//IL_014c: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Expected O, but got Unknown
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e0: Expected O, but got Unknown
		List<FloatMenuOption> list = new List<FloatMenuOption>();
		IntVec3 cell = UI.MouseCell();
		list.Add(new FloatMenuOption("Random", (Action)delegate
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			SetColor_All(GenColor.RandomColorOpaque());
		}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
		foreach (Ideo i in Find.IdeoManager.IdeosListForReading)
		{
			if (!i.classicMode && (Object)(object)i.Icon != (Object)(object)BaseContent.BadTex)
			{
				list.Add(new FloatMenuOption(i.name, (Action)delegate
				{
					//IL_000c: Unknown result type (might be due to invalid IL or missing references)
					SetColor_All(i.Color);
				}, i.Icon, i.Color, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (HorizontalJustification)0, false));
			}
		}
		foreach (ColorDef c in DefDatabase<ColorDef>.AllDefs)
		{
			list.Add(new FloatMenuOption(((Def)c).defName, (Action)delegate
			{
				//IL_000c: Unknown result type (might be due to invalid IL or missing references)
				SetColor_All(c.color);
			}, BaseContent.WhiteTex, c.color, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (HorizontalJustification)0, false));
		}
		foreach (Pawn item in Find.CurrentMap.thingGrid.ThingsAt(cell).OfType<Pawn>())
		{
			item.Drawer.renderer.SetAllGraphicsDirty();
		}
		Find.WindowStack.Add((Window)new FloatMenu(list));
		void SetColor_All(Color color)
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
			//IL_0161: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_011f: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
			List<Thing> list2 = new List<Thing>();
			foreach (Thing item2 in Find.CurrentMap.thingGrid.ThingsAt(cell))
			{
				Pawn val = (Pawn)(object)((item2 is Pawn) ? item2 : null);
				if (val != null && val.apparel != null)
				{
					foreach (Apparel item3 in val.apparel.WornApparel)
					{
						list2.Add((Thing)(object)item3);
					}
				}
				else
				{
					list2.Add(item2);
				}
			}
			foreach (Thing item4 in list2)
			{
				CustomizableGraphic customizableGraphic = CustomizableGraphic.Get(item4, createIfMissing: true);
				if (slot == 0)
				{
					customizableGraphic.colorA = color;
				}
				else if (slot == 1)
				{
					customizableGraphic.colorB = color;
				}
				else if (slot == 2)
				{
					customizableGraphic.colorC = color;
				}
				Log.Message($"Debug-Set {((Entity)item4).LabelCap}'s color slot {slot} to {color}.\nResult: {item4} - {customizableGraphic}");
			}
			foreach (Pawn item5 in Find.CurrentMap.thingGrid.ThingsAt(cell).OfType<Pawn>())
			{
				item5.Drawer.renderer.renderTree.SetDirty();
			}
		}
	}

	public static void ClearAreaOfJunk(CellRect r, Map map)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		((CellRect)(ref r)).ClipInsideMap(map);
		Enumerator enumerator = ((CellRect)(ref r)).GetEnumerator();
		try
		{
			while (((Enumerator)(ref enumerator)).MoveNext())
			{
				IntVec3 current = ((Enumerator)(ref enumerator)).Current;
				map.roofGrid.SetRoof(current, (RoofDef)null);
			}
		}
		finally
		{
			((IDisposable)(Enumerator)(ref enumerator)/*cast due to .constrained prefix*/).Dispose();
		}
		enumerator = ((CellRect)(ref r)).GetEnumerator();
		try
		{
			while (((Enumerator)(ref enumerator)).MoveNext())
			{
				foreach (Thing item in GridsUtility.GetThingList(((Enumerator)(ref enumerator)).Current, map).ToList())
				{
					if ((item.def.destroyable && item.def.EverHaulable) || item.def.filth != null)
					{
						item.Destroy((DestroyMode)0);
					}
				}
			}
		}
		finally
		{
			((IDisposable)(Enumerator)(ref enumerator)/*cast due to .constrained prefix*/).Dispose();
		}
	}
}
