using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace Outposts;

public class Dialog_CreateCamp : Window
{
	private const float LINE_HEIGHT = 100f;

	private readonly Caravan creator;

	private readonly Dictionary<WorldObjectDef, Pair<string, string>> validity;

	private float? prevHeight;

	private Vector2 scrollPosition = new Vector2(0f, 0f);

	public override Vector2 InitialSize => new Vector2(800f, Mathf.Min(1000f, (float)UI.screenHeight - 200f));

	public Dialog_CreateCamp(Caravan creator)
		: base((IWindowDrawing)null)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0126: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0184: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		base.doCloseButton = true;
		base.doCloseX = true;
		base.doWindowBackground = true;
		this.creator = creator;
		validity = new Dictionary<WorldObjectDef, Pair<string, string>>();
		foreach (WorldObjectDef outpost in OutpostsMod.Outposts)
		{
			MethodInfo method = outpost.worldObjectClass.GetMethod("CanSpawnOnWith", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic, null, new Type[2]
			{
				typeof(PlanetTile),
				typeof(List<Pawn>)
			}, null);
			MethodInfo method2 = outpost.worldObjectClass.GetMethod("RequirementsString", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic, null, new Type[2]
			{
				typeof(PlanetTile),
				typeof(List<Pawn>)
			}, null);
			OutpostExtension modExtension = ((Def)outpost).GetModExtension<OutpostExtension>();
			string text = modExtension?.CanSpawnOnWithExt(((WorldObject)creator).Tile, creator.HumanColonists()) ?? ((string)method?.Invoke(null, new object[2]
			{
				((WorldObject)creator).Tile,
				creator.HumanColonists()
			}));
			string text2 = GenText.TrimEndNewlines(modExtension?.RequirementsStringBase(((WorldObject)creator).Tile, creator.HumanColonists()) ?? ((string)method2?.Invoke(null, new object[2]
			{
				((WorldObject)creator).Tile,
				creator.HumanColonists()
			})) ?? "");
			validity.Add(outpost, new Pair<string, string>(text, text2));
		}
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		Rect val = GenUI.ContractedBy(inRect, 5f);
		((Rect)(ref val)).height = ((Rect)(ref val)).height - 45f;
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref val)).width - 50f, prevHeight ?? ((float)OutpostsMod.Outposts.Count * 110f));
		Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
		Rect inRect2 = default(Rect);
		((Rect)(ref inRect2))._002Ector(10f, 0f, ((Rect)(ref val2)).width, 100f);
		foreach (WorldObjectDef outpost in OutpostsMod.Outposts)
		{
			DoOutpostDisplay(ref inRect2, outpost);
			((Rect)(ref inRect2)).y = ((Rect)(ref inRect2)).y + (((Rect)(ref inRect2)).height + 5f);
			Widgets.DrawLineHorizontal(((Rect)(ref inRect2)).x, ((Rect)(ref inRect2)).y, ((Rect)(ref inRect2)).width);
			((Rect)(ref inRect2)).y = ((Rect)(ref inRect2)).y + 5f;
		}
		prevHeight = ((Rect)(ref inRect2)).y;
		Widgets.EndScrollView();
	}

	private void DoOutpostDisplay(ref Rect inRect, WorldObjectDef outpostDef)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_017d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0183: Unknown result type (might be due to invalid IL or missing references)
		//IL_018e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0239: Unknown result type (might be due to invalid IL or missing references)
		GameFont font = Text.Font;
		TextAnchor anchor = Text.Anchor;
		Text.Font = (GameFont)0;
		((Rect)(ref inRect)).height = Text.CalcHeight(((Def)outpostDef).description, ((Rect)(ref inRect)).width - 90f) + 60f;
		Rect val = GenUI.LeftPartPixels(inRect, 50f);
		Rect val2 = GenUI.RightPartPixels(inRect, ((Rect)(ref inRect)).width - 60f);
		Texture2D expandingIconTexture = outpostDef.ExpandingIconTexture;
		GUI.color = ((WorldObject)creator).Faction.Color;
		Widgets.DrawTextureFitted(val, (Texture)(object)expandingIconTexture, 1f, new Vector2((float)((Texture)expandingIconTexture).width, (float)((Texture)expandingIconTexture).height), new Rect(0f, 0f, 1f, 1f), 0f, (Material)null, 1f);
		GUI.color = Color.white;
		Text.Font = (GameFont)2;
		Widgets.Label(GenUI.TopPartPixels(val2, 30f), GenText.CapitalizeFirst(((Def)outpostDef).label, (Def)(object)outpostDef));
		Rect val3 = GenUI.LeftPartPixels(GenUI.BottomPartPixels(val2, 30f), 100f);
		Rect val4 = GenUI.RightPartPixels(GenUI.BottomPartPixels(val2, 30f), ((Rect)(ref val2)).width - 120f);
		Text.Font = (GameFont)0;
		Widgets.Label(new Rect(((Rect)(ref val2)).x, ((Rect)(ref val2)).y + 30f, ((Rect)(ref val2)).width, ((Rect)(ref val2)).height - 60f), ((Def)outpostDef).description);
		Text.Font = (GameFont)1;
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(val4, validity[outpostDef].First);
		Text.Font = font;
		Text.Anchor = anchor;
		if (Widgets.ButtonText(val3, TaggedString.op_Implicit(Translator.Translate("Outposts.Dialog.Create")), true, true, true, (TextAnchor?)null))
		{
			if (GenText.NullOrEmpty(validity[outpostDef].First))
			{
				Outpost outpost = (Outpost)(object)WorldObjectMaker.MakeWorldObject(outpostDef);
				outpost.Name = NameGenerator.GenerateName(((WorldObject)creator).Faction.def.settlementNameMaker, from o in Find.WorldObjects.AllWorldObjects.OfType<Outpost>()
					select o.Name, false, (string)null);
				((WorldObject)outpost).Tile = ((WorldObject)creator).Tile;
				((WorldObject)outpost).SetFaction(((WorldObject)creator).Faction);
				Find.WorldObjects.Add((WorldObject)(object)outpost);
				foreach (Pawn item in GenList.ListFullCopy<Pawn>(creator.PawnsListForReading))
				{
					outpost.AddPawn(item);
				}
				((Window)this).Close(true);
				Find.WorldSelector.Select((WorldObject)(object)outpost, true);
			}
			else
			{
				Messages.Message(validity[outpostDef].First, MessageTypeDefOf.RejectInput, false);
			}
		}
		TooltipHandler.TipRegion(inRect, TipSignal.op_Implicit(validity[outpostDef].Second));
	}
}
