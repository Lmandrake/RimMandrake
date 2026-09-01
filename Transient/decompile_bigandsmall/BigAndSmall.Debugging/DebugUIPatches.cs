using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace BigAndSmall.Debugging;

[HarmonyPatch]
public static class DebugUIPatches
{
	[HarmonyPatch(typeof(GeneUIUtility), "DoDebugButton")]
	[HarmonyPostfix]
	public static void DoDebugButton_Postfix(ref Rect buttonRect, Thing target, GeneSet genesOverride)
	{
		DoGeneDebugButton(ref buttonRect, target);
	}

	public static void DoGeneDebugButton(ref Rect buttonRect, Thing target, string title = "Big & Small")
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Expected O, but got Unknown
		//IL_0275: Unknown result type (might be due to invalid IL or missing references)
		//IL_027f: Expected O, but got Unknown
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Expected O, but got Unknown
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fd: Expected O, but got Unknown
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Expected O, but got Unknown
		//IL_0143: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Expected O, but got Unknown
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0175: Expected O, but got Unknown
		//IL_0193: Unknown result type (might be due to invalid IL or missing references)
		//IL_019d: Expected O, but got Unknown
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Expected O, but got Unknown
		//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ed: Expected O, but got Unknown
		//IL_020b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0215: Expected O, but got Unknown
		//IL_0233: Unknown result type (might be due to invalid IL or missing references)
		//IL_023d: Expected O, but got Unknown
		//IL_025b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0265: Expected O, but got Unknown
		if (!(target is Pawn))
		{
			return;
		}
		Pawn pawn = (Pawn)(object)((target is Pawn) ? target : null);
		float x2 = ((Rect)(ref buttonRect)).size.x;
		buttonRect = new Rect(((Rect)(ref buttonRect)).x - x2 - 10f, ((Rect)(ref buttonRect)).y, ((Rect)(ref buttonRect)).width, ((Rect)(ref buttonRect)).height);
		if (!Widgets.ButtonText(buttonRect, title, true, true, true, (TextAnchor?)null))
		{
			return;
		}
		List<FloatMenuOption> list2 = new List<FloatMenuOption>(1)
		{
			new FloatMenuOption("Set to Race...", (Action)delegate
			{
				//IL_0067: Unknown result type (might be due to invalid IL or missing references)
				//IL_0083: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b2: Expected O, but got Unknown
				List<DebugMenuOption> list = new List<DebugMenuOption>();
				foreach (ThingDef def in DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x != null && x.race?.intelligence == (Intelligence?)2 && !x.IsCorpse))
				{
					list.Add(new DebugMenuOption($"{((Def)def).defName}\t ({((Def)def).LabelCap})", (DebugMenuOptionMode)0, (Action)delegate
					{
						pawn.SwapThingDef(def, state: true, 999, force: true, null, permitFusion: false);
					}));
				}
				Find.WindowStack.Add((Window)new Dialog_DebugOptionListLister((IEnumerable<DebugMenuOption>)list, (string)null));
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0)
		};
		if (ModsConfig.BiotechActive)
		{
			List<FloatMenuOption> collection = new List<FloatMenuOption>(11)
			{
				new FloatMenuOption("Apply/Append RaceDef", (Action)delegate
				{
					//IL_0067: Unknown result type (might be due to invalid IL or missing references)
					//IL_0083: Unknown result type (might be due to invalid IL or missing references)
					//IL_0102: Unknown result type (might be due to invalid IL or missing references)
					//IL_0128: Unknown result type (might be due to invalid IL or missing references)
					//IL_014d: Unknown result type (might be due to invalid IL or missing references)
					//IL_0157: Expected O, but got Unknown
					List<DebugMenuOption> list3 = new List<DebugMenuOption>();
					foreach (ThingDef def2 in DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x != null && x.race?.intelligence == (Intelligence?)2 && !x.IsCorpse))
					{
						list3.Add(new DebugMenuOption($"{((Def)def2).defName}\t ({((Def)def2).LabelCap})", (DebugMenuOptionMode)0, (Action)delegate
						{
							pawn.SwapThingDef(def2, state: true, 100);
						}));
					}
					foreach (ThingDef def3 in DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x != null && x.race?.intelligence == (Intelligence?)2 && !x.IsCorpse))
					{
						list3.Add(new DebugMenuOption($"{((Def)def3).defName}\t ({((Def)def3).LabelCap})" + " (force)", (DebugMenuOptionMode)0, (Action)delegate
						{
							pawn.SwapThingDef(def3, state: true, 999, force: true, null, permitFusion: false);
						}));
					}
					Find.WindowStack.Add((Window)new Dialog_DebugOptionListLister((IEnumerable<DebugMenuOption>)list3, (string)null));
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Set exact xenotype + race", (Action)delegate
				{
					//IL_0045: Unknown result type (might be due to invalid IL or missing references)
					//IL_0061: Unknown result type (might be due to invalid IL or missing references)
					//IL_0086: Unknown result type (might be due to invalid IL or missing references)
					//IL_0090: Expected O, but got Unknown
					List<DebugMenuOption> list4 = new List<DebugMenuOption>();
					foreach (XenotypeDef allDef in DefDatabase<XenotypeDef>.AllDefs)
					{
						XenotypeDef xenotype = allDef;
						list4.Add(new DebugMenuOption($"{((Def)xenotype).defName}\t ({((Def)xenotype).LabelCap})", (DebugMenuOptionMode)0, (Action)delegate
						{
							SetXenotypeAndRace(pawn, xenotype);
						}));
					}
					Find.WindowStack.Add((Window)new Dialog_DebugOptionListLister((IEnumerable<DebugMenuOption>)list4, (string)null));
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Apply xenotype", (Action)delegate
				{
					//IL_0045: Unknown result type (might be due to invalid IL or missing references)
					//IL_0061: Unknown result type (might be due to invalid IL or missing references)
					//IL_0086: Unknown result type (might be due to invalid IL or missing references)
					//IL_0090: Expected O, but got Unknown
					List<DebugMenuOption> list5 = new List<DebugMenuOption>();
					foreach (XenotypeDef allDef2 in DefDatabase<XenotypeDef>.AllDefs)
					{
						XenotypeDef xenotype2 = allDef2;
						list5.Add(new DebugMenuOption($"{((Def)xenotype2).defName}\t ({((Def)xenotype2).LabelCap})", (DebugMenuOptionMode)0, (Action)delegate
						{
							pawn.genes.SetXenotype(xenotype2);
							pawn.TrySwapToXenotypeThingDef();
						}));
					}
					Find.WindowStack.Add((Window)new Dialog_DebugOptionListLister((IEnumerable<DebugMenuOption>)list5, (string)null));
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Spawn Xenogerm", (Action)delegate
				{
					CompTargetEffect_CreateXenogerm.CreateXenogerm(pawn, archite: true, endoGenes: true, xenoGenes: true, inactive: true);
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Reapply Genes", (Action)delegate
				{
					foreach (XenotypeDef allDef3 in DefDatabase<XenotypeDef>.AllDefs)
					{
						_ = allDef3;
						List<GeneDef> list6 = pawn.genes.Endogenes.Select((Gene g) => g.def).ToList();
						List<GeneDef> list7 = pawn.genes.Xenogenes.Select((Gene g) => g.def).ToList();
						GeneHelpers.RemoveAllGenesSlow(pawn);
						foreach (GeneDef item in list6)
						{
							pawn.genes.AddGene(item, false);
						}
						foreach (GeneDef item2 in list7)
						{
							pawn.genes.AddGene(item2, true);
						}
					}
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Remove overriden genes", (Action)delegate
				{
					foreach (Gene allInactiveGene in GeneHelpers.GetAllInactiveGenes(pawn))
					{
						pawn.genes.RemoveGene(allInactiveGene);
					}
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Remove all Endogenes", (Action)delegate
				{
					foreach (Gene item3 in pawn.genes.Endogenes.Select((Gene g) => g).ToList())
					{
						pawn.genes.RemoveGene(item3);
					}
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Remove all Xenogenes", (Action)delegate
				{
					foreach (Gene item4 in pawn.genes.Xenogenes.Select((Gene g) => g).ToList())
					{
						pawn.genes.RemoveGene(item4);
					}
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Discombobulate", (Action)delegate
				{
					Discombobulator.Discombobulate(pawn, addComa: false);
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Set to random xenotype", (Action)delegate
				{
					GeneHelpers.RemoveAllGenesSlow(pawn);
					pawn.genes.SetXenotype(GenCollection.RandomElement<XenotypeDef>(DefDatabase<XenotypeDef>.AllDefs));
					pawn.TrySwapToXenotypeThingDef();
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
				new FloatMenuOption("Set to Baseline Human [Force]", (Action)delegate
				{
					GeneHelpers.RemoveAllGenesSlow_ExceptColor(pawn);
					pawn.SwapThingDef(ThingDefOf.Human, state: true, 999, force: true, null, permitFusion: false);
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0)
			};
			list2.AddRange(collection);
		}
		Find.WindowStack.Add((Window)new FloatMenu(list2));
	}

	public static void SetXenotypeAndRace(Pawn pawn, XenotypeDef xenotype)
	{
		GeneHelpers.RemoveAllGenesSlow(pawn);
		pawn.genes.SetXenotype(xenotype);
		pawn.TrySwapToXenotypeThingDef();
	}
}
