using System;
using System.Collections.Generic;
using System.Linq;
using LudeonTK;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Sounds;

internal class EditWindow_SoundTest : EditWindow
{
	private Vector2 scrollPosition;

	private Vector2 scrollPositionBis;

	private string search = "";

	private List<SoundDef> soundDefs;

	private SoundDef soundToTest;

	public override Vector2 InitialSize => new Vector2((float)UI.screenWidth * 0.5f, (float)UI.screenHeight * 0.75f);

	public override bool IsDebug => true;

	public EditWindow_SoundTest()
	{
		((Window)this).resizeable = false;
		((Window)this).draggable = false;
		((Window)this).preventCameraMotion = false;
		((Window)this).doCloseX = true;
	}

	public override void PostOpen()
	{
		((EditWindow)this).PostOpen();
		soundDefs = DefDatabase<SoundDef>.AllDefsListForReading.FindAll((SoundDef s) => !((Def)s).modContentPack.IsOfficialMod && !((Def)s).modContentPack.IsCoreMod && !s.sustain);
		soundToTest = null;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0255: Unknown result type (might be due to invalid IL or missing references)
		//IL_0298: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0301: Unknown result type (might be due to invalid IL or missing references)
		//IL_036b: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_041b: Unknown result type (might be due to invalid IL or missing references)
		//IL_04e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_045e: Unknown result type (might be due to invalid IL or missing references)
		//IL_047a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0550: Unknown result type (might be due to invalid IL or missing references)
		//IL_0558: Unknown result type (might be due to invalid IL or missing references)
		//IL_055d: Unknown result type (might be due to invalid IL or missing references)
		if (soundToTest == null)
		{
			Text.Anchor = (TextAnchor)4;
			float num = 0f;
			Rect val = default(Rect);
			((Rect)(ref val))._002Ector(0f, 10f + num, 150f, 30f);
			Widgets.Label(val, "Search:");
			Rect val2 = default(Rect);
			((Rect)(ref val2))._002Ector(((Rect)(ref val)).width + 10f, 10f + num, ((Rect)(ref inRect)).width - ((Rect)(ref val)).width - 116f, 30f);
			search = Widgets.TextField(val2, search);
			num += 50f;
			Rect val3 = new Rect(0f, 10f + num, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 65f);
			List<SoundDef> list = soundDefs.FindAll((SoundDef s) => ((Def)s).defName.ToLower().Contains(search.ToLower())).ToList();
			Rect val4 = default(Rect);
			((Rect)(ref val4))._002Ector(0f, 10f + num, ((Rect)(ref inRect)).width - 16f, 30f * (float)(Mathf.RoundToInt((float)(list.Count / 3)) + 1));
			Widgets.BeginScrollView(val3, ref scrollPosition, val4, true);
			int num2 = 0;
			int num3 = 0;
			for (int i = 0; i < list.Count; i++)
			{
				if (Widgets.ButtonText(new Rect((float)num2 * ((Rect)(ref val4)).width / 3f, 10f + num + (float)num3 * 30f, ((Rect)(ref val4)).width / 3f, 30f), ((Def)list[i]).defName, true, true, true, (TextAnchor?)null))
				{
					soundToTest = list[i];
					break;
				}
				num2++;
				if (num2 % 3 == 0)
				{
					num2 = 0;
					num3++;
				}
			}
			Widgets.EndScrollView();
		}
		else
		{
			Text.Anchor = (TextAnchor)4;
			float num4 = 0f;
			if (Widgets.ButtonText(new Rect(0f, 20f + num4, ((Rect)(ref inRect)).width, 30f), "Change sound (currently testing: " + ((Def)soundToTest).defName + ")", true, true, true, (TextAnchor?)null))
			{
				soundToTest = null;
			}
			else
			{
				Text.Anchor = (TextAnchor)0;
				num4 += 40f;
				Rect val5 = new Rect(0f, 10f + num4, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 115f);
				Rect val6 = default(Rect);
				((Rect)(ref val6))._002Ector(0f, 10f + num4, ((Rect)(ref inRect)).width - 16f, 200f * (float)soundToTest.subSounds.Count);
				Widgets.BeginScrollView(val5, ref scrollPositionBis, val6, true);
				for (int j = 0; j < soundToTest.subSounds.Count; j++)
				{
					Widgets.Label(new Rect(0f, 20f + num4, ((Rect)(ref inRect)).width, 30f), $"Subsound {j + 1} <volumeRange>");
					num4 += 30f;
					Widgets.FloatRange(new Rect(0f, 20f + num4, ((Rect)(ref inRect)).width, 30f), Rand.Int, ref soundToTest.subSounds[j].volumeRange, 0.5f, 500f, (string)null, (ToStringStyle)3, 0f, (GameFont)1, (Color?)null, 0f);
					num4 += 50f;
					Widgets.Label(new Rect(0f, 20f + num4, ((Rect)(ref inRect)).width, 30f), $"Subsound {j + 1} <pitchRange>");
					num4 += 30f;
					Widgets.FloatRange(new Rect(0f, 20f + num4, ((Rect)(ref inRect)).width, 30f), Rand.Int, ref soundToTest.subSounds[j].pitchRange, 0f, 100f, (string)null, (ToStringStyle)3, 0f, (GameFont)1, (Color?)null, 0f);
					num4 += 50f;
					Text.Anchor = (TextAnchor)4;
					if (Widgets.ButtonText(new Rect(0f, 20f + num4, ((Rect)(ref inRect)).width, 30f), $"Copy settings of subsound {j + 1}", true, true, true, (TextAnchor?)null))
					{
						GUIUtility.systemCopyBuffer = $"<volumeRange>{soundToTest.subSounds[j].volumeRange}</volumeRange>\n<pitchRange>{soundToTest.subSounds[j].pitchRange}</pitchRange>";
					}
					num4 += 30f;
					Text.Anchor = (TextAnchor)0;
				}
				Widgets.EndScrollView();
				Text.Anchor = (TextAnchor)4;
				if (Widgets.ButtonText(new Rect(0f, ((Rect)(ref inRect)).height - 50f, ((Rect)(ref inRect)).width, 30f), "Play sound", true, true, true, (TextAnchor?)null))
				{
					if (GenCollection.Any<SubSoundDef>(soundToTest.subSounds, (Predicate<SubSoundDef>)((SubSoundDef sub) => sub.onCamera)))
					{
						SoundStarter.PlayOneShotOnCamera(soundToTest, (Map)null);
					}
					else
					{
						Map currentMap = Find.CurrentMap;
						SoundStarter.PlayOneShot(soundToTest, SoundInfo.op_Implicit(new TargetInfo(currentMap.Center, currentMap, false)));
					}
				}
			}
		}
		Text.Anchor = (TextAnchor)0;
	}
}
