using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.Util;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class DebugTools
{
	private static void DoTableInternalWeapons(string tag)
	{
		DebugTables.MakeTablesDialog<ThingDef>((IEnumerable<ThingDef>)DefDatabase<ThingDef>.AllDefs.Where((ThingDef td) => td.weaponTags?.Contains(tag) ?? false).OrderBy(delegate(ThingDef d)
		{
			ModContentPack modContentPack = ((Def)d).modContentPack;
			return ((modContentPack != null) ? modContentPack.Name : null) ?? "Core";
		}), new TableDataGetter<ThingDef>[4]
		{
			new TableDataGetter<ThingDef>("defName", (Func<ThingDef, string>)((ThingDef d) => ((Def)d).defName)),
			new TableDataGetter<ThingDef>("name", (Func<ThingDef, string>)((ThingDef d) => TaggedString.op_Implicit(((Def)d).LabelCap))),
			new TableDataGetter<ThingDef>("source", (Func<ThingDef, string>)delegate(ThingDef d)
			{
				ModContentPack modContentPack2 = ((Def)d).modContentPack;
				return ((modContentPack2 != null) ? modContentPack2.Name : null) ?? "Core";
			}),
			new TableDataGetter<ThingDef>("tags", (Func<ThingDef, string>)((ThingDef d) => GenText.ToSpaceList(d.weaponTags.Select((string t) => t.ToString()))))
		});
	}

	[DebugOutput("Weapons", false, name = "Weapons for tag")]
	public static void WeaponsByTag()
	{
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Expected O, but got Unknown
		Find.WindowStack.Add((Window)new FloatMenu(((IEnumerable<string>)(from tagName in DefDatabase<ThingDef>.AllDefs.Where((ThingDef td) => td.weaponTags != null).SelectMany((ThingDef t) => t.weaponTags).Distinct()
			orderby tagName
			select tagName)).Select((Func<string, FloatMenuOption>)((string tag) => new FloatMenuOption(tag, (Action)delegate
		{
			DoTableInternalWeapons(tag);
		}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0))).ToList()));
	}

	[DebugAction(/*Could not decode attribute arguments.*/)]
	private static List<DebugActionNode> SpawnFactionPawn()
	{
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Expected O, but got Unknown
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Expected O, but got Unknown
		List<DebugActionNode> list = new List<DebugActionNode>();
		foreach (Faction faction in Find.FactionManager.AllFactions)
		{
			DebugActionNode val = new DebugActionNode(((Def)faction.def).defName, (DebugActionType)1, (Action)null, (Action<Pawn>)null);
			foreach (PawnKindDef pawnKindDef in from kd in faction.def.GetKindDefs()
				orderby ((Def)kd).defName
				select kd)
			{
				val.AddChild(new DebugActionNode(((Def)pawnKindDef).defName, (DebugActionType)1, (Action)null, (Action<Pawn>)null)
				{
					category = DebugToolsSpawning.GetCategoryForPawnKind(pawnKindDef),
					action = delegate
					{
						//IL_0020: Unknown result type (might be due to invalid IL or missing references)
						Pawn obj = PawnGenerator.GeneratePawn(pawnKindDef, faction, (PlanetTile?)null);
						GenSpawn.Spawn((Thing)(object)obj, UI.MouseCell(), Find.CurrentMap, (WipeMode)0);
						DebugToolsSpawning.PostPawnSpawn(obj);
					}
				});
			}
			list.Add(val);
		}
		return list;
	}
}
