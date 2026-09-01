using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using KCSG;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace VEF.Storyteller;

public static class StructureSetGenerator
{
	public static List<CellRect> Generate(Map map, StructureSetDef structureSetDef, Faction faction, float points = 0f)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_018d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01df: Unknown result type (might be due to invalid IL or missing references)
		//IL_0267: Unknown result type (might be due to invalid IL or missing references)
		//IL_0268: Unknown result type (might be due to invalid IL or missing references)
		//IL_026a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0287: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0210: Unknown result type (might be due to invalid IL or missing references)
		//IL_0207: Unknown result type (might be due to invalid IL or missing references)
		//IL_021b: Unknown result type (might be due to invalid IL or missing references)
		//IL_07a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_07c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_07d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_07e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_07e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_07ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_07ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_0800: Unknown result type (might be due to invalid IL or missing references)
		//IL_07f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0814: Unknown result type (might be due to invalid IL or missing references)
		//IL_080b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0828: Unknown result type (might be due to invalid IL or missing references)
		//IL_081f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0833: Unknown result type (might be due to invalid IL or missing references)
		//IL_088f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0890: Unknown result type (might be due to invalid IL or missing references)
		//IL_0892: Unknown result type (might be due to invalid IL or missing references)
		//IL_08af: Unknown result type (might be due to invalid IL or missing references)
		//IL_08d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_08de: Unknown result type (might be due to invalid IL or missing references)
		//IL_08e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_04f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_04fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_044f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0456: Unknown result type (might be due to invalid IL or missing references)
		//IL_045b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0469: Unknown result type (might be due to invalid IL or missing references)
		//IL_046e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0470: Unknown result type (might be due to invalid IL or missing references)
		//IL_0475: Unknown result type (might be due to invalid IL or missing references)
		//IL_0479: Unknown result type (might be due to invalid IL or missing references)
		//IL_047e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0480: Unknown result type (might be due to invalid IL or missing references)
		//IL_0485: Unknown result type (might be due to invalid IL or missing references)
		//IL_048a: Unknown result type (might be due to invalid IL or missing references)
		//IL_08fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_08f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_049e: Unknown result type (might be due to invalid IL or missing references)
		//IL_04ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_04b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_04c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0902: Unknown result type (might be due to invalid IL or missing references)
		//IL_04e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0922: Unknown result type (might be due to invalid IL or missing references)
		//IL_051e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0530: Unknown result type (might be due to invalid IL or missing references)
		//IL_067c: Unknown result type (might be due to invalid IL or missing references)
		//IL_066a: Unknown result type (might be due to invalid IL or missing references)
		//IL_066f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0950: Unknown result type (might be due to invalid IL or missing references)
		//IL_0952: Unknown result type (might be due to invalid IL or missing references)
		//IL_0959: Unknown result type (might be due to invalid IL or missing references)
		//IL_0960: Unknown result type (might be due to invalid IL or missing references)
		//IL_0965: Unknown result type (might be due to invalid IL or missing references)
		//IL_0967: Unknown result type (might be due to invalid IL or missing references)
		//IL_0977: Unknown result type (might be due to invalid IL or missing references)
		//IL_097a: Unknown result type (might be due to invalid IL or missing references)
		//IL_098f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0996: Unknown result type (might be due to invalid IL or missing references)
		//IL_09a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_09ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_0930: Unknown result type (might be due to invalid IL or missing references)
		//IL_0941: Unknown result type (might be due to invalid IL or missing references)
		//IL_094b: Unknown result type (might be due to invalid IL or missing references)
		//IL_054c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0560: Unknown result type (might be due to invalid IL or missing references)
		//IL_0565: Unknown result type (might be due to invalid IL or missing references)
		//IL_056a: Unknown result type (might be due to invalid IL or missing references)
		//IL_05c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_05c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_05d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_05e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_05e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_05f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_05ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0609: Unknown result type (might be due to invalid IL or missing references)
		//IL_0655: Unknown result type (might be due to invalid IL or missing references)
		//IL_06a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_06a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_06a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_06ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_06b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_06b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_06b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_06c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0685: Unknown result type (might be due to invalid IL or missing references)
		//IL_0691: Unknown result type (might be due to invalid IL or missing references)
		//IL_069b: Unknown result type (might be due to invalid IL or missing references)
		//IL_09be: Unknown result type (might be due to invalid IL or missing references)
		//IL_09c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_059a: Unknown result type (might be due to invalid IL or missing references)
		//IL_05ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_0574: Unknown result type (might be due to invalid IL or missing references)
		//IL_0588: Unknown result type (might be due to invalid IL or missing references)
		//IL_058d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0592: Unknown result type (might be due to invalid IL or missing references)
		//IL_06dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_06d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_06f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_06ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0707: Unknown result type (might be due to invalid IL or missing references)
		List<CellRect> list = new List<CellRect>();
		IntVec3 center = map.Center;
		HashSet<StructureLayoutDef> usedDefs = new HashSet<StructureLayoutDef>();
		List<(StructurePatternOffset, StructureLayoutDef)> list2 = new List<(StructurePatternOffset, StructureLayoutDef)>();
		List<StructurePatternOffset> list3 = new List<StructurePatternOffset>();
		foreach (StructurePatternOffset layout in structureSetDef.structureLayouts)
		{
			if (layout.pointsRange.HasValue)
			{
				FloatRange value = layout.pointsRange.Value;
				if (!((FloatRange)(ref value)).Includes(points))
				{
					continue;
				}
			}
			if (layout.scatter || layout.radialCount > 0)
			{
				list3.Add(layout);
				continue;
			}
			List<StructureLayoutDef> list4 = DefDatabase<StructureLayoutDef>.AllDefsListForReading.Where((StructureLayoutDef def) => !usedDefs.Contains(def) && Regex.IsMatch(((Def)def).defName, "^" + layout.pattern + "$")).ToList();
			if (GenCollection.Any<StructureLayoutDef>(list4))
			{
				StructureLayoutDef structureLayoutDef = GenCollection.RandomElement<StructureLayoutDef>((IEnumerable<StructureLayoutDef>)list4);
				usedDefs.Add(structureLayoutDef);
				list2.Add((layout, structureLayoutDef));
			}
		}
		CellRect val = CellRect.CenteredOn(center, 1, 1);
		if (GenCollection.Any<(StructurePatternOffset, StructureLayoutDef)>(list2))
		{
			int num = int.MaxValue;
			int num2 = int.MaxValue;
			int num3 = int.MinValue;
			int num4 = int.MinValue;
			foreach (var item in list2)
			{
				CellRect val2 = CellRect.CenteredOn(new IntVec3(item.Item1.offset.x * item.Item2.Sizes.x, 0, item.Item1.offset.z * item.Item2.Sizes.z), item.Item2.Sizes);
				if (val2.minX < num)
				{
					num = val2.minX;
				}
				if (val2.minZ < num2)
				{
					num2 = val2.minZ;
				}
				if (val2.maxX > num3)
				{
					num3 = val2.maxX;
				}
				if (val2.maxZ > num4)
				{
					num4 = val2.maxZ;
				}
			}
			IntVec3 val3 = default(IntVec3);
			((IntVec3)(ref val3))._002Ector(-(num + (num3 - num) / 2), 0, -(num2 + (num4 - num2) / 2));
			(StructurePatternOffset, StructureLayoutDef) tuple = list2[0];
			val = CellRect.CenteredOn(center + val3 + new IntVec3(tuple.Item1.offset.x * tuple.Item2.Sizes.x, 0, tuple.Item1.offset.z * tuple.Item2.Sizes.z), tuple.Item2.Sizes.x, tuple.Item2.Sizes.z);
		}
		foreach (StructurePatternOffset layout2 in list3)
		{
			int randomInRange = ((IntRange)(ref layout2.count)).RandomInRange;
			for (int i = 0; i < randomInRange; i++)
			{
				int num5 = ((layout2.radialCount <= 0) ? 1 : layout2.radialCount);
				for (int j = 0; j < num5; j++)
				{
					List<StructureLayoutDef> list5 = DefDatabase<StructureLayoutDef>.AllDefsListForReading.Where((StructureLayoutDef def) => !usedDefs.Contains(def) && Regex.IsMatch(((Def)def).defName, "^" + layout2.pattern + "$")).ToList();
					if (!GenCollection.Any<StructureLayoutDef>(list5))
					{
						list5 = DefDatabase<StructureLayoutDef>.AllDefsListForReading.Where((StructureLayoutDef def) => Regex.IsMatch(((Def)def).defName, "^" + layout2.pattern + "$")).ToList();
					}
					if (!GenCollection.Any<StructureLayoutDef>(list5))
					{
						continue;
					}
					StructureLayoutDef structureLayoutDef2 = GenCollection.RandomElement<StructureLayoutDef>((IEnumerable<StructureLayoutDef>)list5);
					usedDefs.Add(structureLayoutDef2);
					Rot4? val4 = null;
					IntVec3 val6;
					Rot4 value2;
					if (layout2.radialCount > 0)
					{
						float num6 = 360f / (float)layout2.radialCount * (float)j;
						float num7 = layout2.radialDistance + (float)Mathf.Max(((CellRect)(ref val)).Width, ((CellRect)(ref val)).Height) / 2f;
						Vector3 val5 = Vector3.forward * num7;
						val5 = Quaternion.Euler(0f, num6, 0f) * val5;
						val6 = ((CellRect)(ref val)).CenterCell + IntVec3Utility.ToIntVec3(val5);
						if (layout2.faceCenter)
						{
							val4 = Rot4.FromAngleFlat(num6);
							value2 = val4.Value;
							val4 = new Rot4(((Rot4)(ref value2)).AsInt + layout2.rotationOffset);
						}
						if (layout2.randomRotated)
						{
							val4 = Rot4.Random;
						}
					}
					else
					{
						bool flag = false;
						val6 = IntVec3.Invalid;
						for (int k = 0; k < 100; k++)
						{
							if (layout2.putAnywhere)
							{
								((IntVec3)(ref val6))._002Ector(Rand.Range(0, map.Size.x), 0, Rand.Range(0, map.Size.z));
							}
							else if (k < 20)
							{
								val6 = center + new IntVec3(Rand.Range(-40, 40), 0, Rand.Range(-40, 40));
							}
							else if (k < 50)
							{
								val6 = center + new IntVec3(Rand.Range(-80, 80), 0, Rand.Range(-80, 80));
							}
							else
							{
								((IntVec3)(ref val6))._002Ector(Rand.Range(0, map.Size.x), 0, Rand.Range(0, map.Size.z));
							}
							CellRect checkRect = CellRect.CenteredOn(val6, structureLayoutDef2.Sizes.x + 2, structureLayoutDef2.Sizes.z + 2);
							if (((CellRect)(ref checkRect)).FullyContainedWithin(new CellRect(0, 0, map.Size.x, map.Size.z)) && !GenCollection.Any<CellRect>(list, (Predicate<CellRect>)((CellRect r) => ((CellRect)(ref r)).Overlaps(checkRect))))
							{
								flag = true;
								break;
							}
						}
						if (!flag)
						{
							continue;
						}
						if (layout2.randomRotated)
						{
							val4 = Rot4.Random;
						}
					}
					_003F val7;
					if (val4.HasValue)
					{
						value2 = val4.Value;
						if (((Rot4)(ref value2)).IsHorizontal)
						{
							val7 = new IntVec2(structureLayoutDef2.Sizes.z, structureLayoutDef2.Sizes.x);
							goto IL_06a0;
						}
					}
					val7 = structureLayoutDef2.Sizes;
					goto IL_06a0;
					IL_06a0:
					IntVec2 val8 = (IntVec2)val7;
					CellRect val9 = CellRect.CenteredOn(val6, val8.x, val8.z);
					GenOption.GetAllMineableIn(val9, map);
					LayoutUtils.CleanRect(structureLayoutDef2, map, val9, fullClean: true, (Rot4)(((_003F?)val4) ?? Rot4.North));
					List<Thing> spawnedThings = new List<Thing>();
					structureLayoutDef2.Generate(val9, map, spawnedThings, faction, forceNullFaction: false, val4);
					list.Add(val9);
					SpawnPawnsAndThings(map, val9, layout2, faction);
				}
			}
		}
		if (GenCollection.Any<(StructurePatternOffset, StructureLayoutDef)>(list2))
		{
			int num8 = int.MaxValue;
			int num9 = int.MaxValue;
			int num10 = int.MinValue;
			int num11 = int.MinValue;
			foreach (var item2 in list2)
			{
				CellRect val10 = CellRect.CenteredOn(new IntVec3(item2.Item1.offset.x * item2.Item2.Sizes.x, 0, item2.Item1.offset.z * item2.Item2.Sizes.z), item2.Item2.Sizes);
				if (val10.minX < num8)
				{
					num8 = val10.minX;
				}
				if (val10.minZ < num9)
				{
					num9 = val10.minZ;
				}
				if (val10.maxX > num10)
				{
					num10 = val10.maxX;
				}
				if (val10.maxZ > num11)
				{
					num11 = val10.maxZ;
				}
			}
			IntVec3 val11 = default(IntVec3);
			((IntVec3)(ref val11))._002Ector(-(num8 + (num10 - num8) / 2), 0, -(num9 + (num11 - num9) / 2));
			bool flag2 = false;
			foreach (var item3 in list2)
			{
				IntVec3 val12 = center + val11 + new IntVec3(item3.Item1.offset.x * item3.Item2.Sizes.x, 0, item3.Item1.offset.z * item3.Item2.Sizes.z);
				Rot4 val13 = (item3.Item1.randomRotated ? Rot4.Random : Rot4.North);
				IntVec2 val14 = (IntVec2)((item3.Item1.randomRotated && ((Rot4)(ref val13)).IsHorizontal) ? new IntVec2(item3.Item2.Sizes.z, item3.Item2.Sizes.x) : item3.Item2.Sizes);
				CellRect val15 = CellRect.CenteredOn(val12, val14.x, val14.z);
				GenOption.GetAllMineableIn(val15, map);
				LayoutUtils.CleanRect(item3.Item2, map, val15, fullClean: true, val13);
				List<Thing> spawnedThings2 = new List<Thing>();
				item3.Item2.Generate(val15, map, spawnedThings2, faction, forceNullFaction: false, val13);
				list.Add(val15);
				SpawnPawnsAndThings(map, val15, item3.Item1, faction);
				if (!flag2)
				{
					val = val15;
					flag2 = true;
				}
			}
		}
		MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects").AddRange(list);
		return list;
	}

	private static void SpawnPawnsAndThings(Map map, CellRect structureRect, StructurePatternOffset layout, Faction faction)
	{
		//IL_031e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0339: Unknown result type (might be due to invalid IL or missing references)
		//IL_034a: Expected O, but got Unknown
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0268: Unknown result type (might be due to invalid IL or missing references)
		//IL_0274: Unknown result type (might be due to invalid IL or missing references)
		//IL_0279: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_029e: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Expected O, but got Unknown
		List<IntVec3> list = ((CellRect)(ref structureRect)).Cells.Where((IntVec3 cell) => GenGrid.Walkable(cell, map) && (!layout.forceSpawnEnemiesIndoor || (GridsUtility.Roofed(cell, map) && !GridsUtility.UsesOutdoorTemperature(cell, map)))).ToList();
		if (!GenCollection.Any<IntVec3>(list))
		{
			return;
		}
		List<Pawn> list2 = new List<Pawn>();
		if (layout.spawnPawns != null)
		{
			foreach (PawnSpawnOption spawnPawn in layout.spawnPawns)
			{
				for (int i = 0; i < ((IntRange)(ref spawnPawn.count)).RandomInRange; i++)
				{
					IntVec3 val = GenCollection.RandomElement<IntVec3>((IEnumerable<IntVec3>)list);
					if (!((IntVec3)(ref val)).IsValid)
					{
						val = ((CellRect)(ref structureRect)).CenterCell;
					}
					IntVec3 val2 = CellFinder.RandomSpawnCellForPawnNear(val, map, 5);
					if (((IntVec3)(ref val2)).IsValid)
					{
						Pawn val3 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(spawnPawn.kind, faction, (PawnGenerationContext)2, (PlanetTile?)null, true, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
						if (val3.RaceProps.Humanlike && !GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)layout.weapons))
						{
							val3.equipment.DestroyAllEquipment((DestroyMode)0);
							val3.equipment.AddEquipment((ThingWithComps)ThingMaker.MakeThing(GenCollection.RandomElement<ThingDef>((IEnumerable<ThingDef>)layout.weapons), (ThingDef)null));
						}
						if (layout.unwaveringlyLoyal && val3.guest != null)
						{
							val3.guest.Recruitable = false;
						}
						GenSpawn.Spawn((Thing)(object)val3, val2, map, (WipeMode)0);
						list2.Add(val3);
					}
				}
			}
		}
		if (layout.spawnThings != null)
		{
			foreach (ThingSpawnOption spawnThing in layout.spawnThings)
			{
				int num = ((IntRange)(ref spawnThing.count)).RandomInRange;
				while (num > 0)
				{
					int num2 = Math.Min(num, spawnThing.thing.stackLimit);
					IntVec3 val4 = CellFinder.RandomSpawnCellForPawnNear(GenCollection.RandomElement<IntVec3>((IEnumerable<IntVec3>)list), map, 5);
					if (!((IntVec3)(ref val4)).IsValid)
					{
						break;
					}
					Thing val5 = ThingMaker.MakeThing(spawnThing.thing, (ThingDef)null);
					val5.stackCount = num2;
					GenSpawn.Spawn(val5, val4, map, (WipeMode)0);
					Hive val6 = (Hive)(object)((val5 is Hive) ? val5 : null);
					if (val6 != null)
					{
						((Thing)val6).SetFaction(Faction.OfInsects, (Pawn)null);
					}
					else if (val5.def.CanHaveFaction)
					{
						val5.SetFaction(faction, (Pawn)null);
					}
					ForbidUtility.SetForbidden(val5, true, false);
					num -= num2;
				}
			}
		}
		if (GenCollection.Any<Pawn>(list2))
		{
			LordMaker.MakeNewLord(faction, (LordJob)new LordJob_DefendPoint(GenCollection.RandomElement<IntVec3>((IEnumerable<IntVec3>)list), (float?)null, (float?)null, false, true), map, (IEnumerable<Pawn>)list2);
		}
	}
}
