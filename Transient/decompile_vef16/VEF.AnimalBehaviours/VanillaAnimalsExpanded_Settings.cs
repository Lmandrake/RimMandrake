using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class VanillaAnimalsExpanded_Settings : ModSettings
{
	private static Vector2 scrollPosition = Vector2.zero;

	public Dictionary<string, bool> pawnSpawnStates = new Dictionary<string, bool>();

	private List<string> pawnKeys;

	private List<bool> boolValues;

	private string searchKey;

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Collections.Look<string, bool>(ref pawnSpawnStates, "pawnSpawnStates", (LookMode)1, (LookMode)1, ref pawnKeys, ref boolValues, true, false, false);
	}

	public void DoWindowContents(Rect inRect)
	{
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Expected O, but got Unknown
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_014f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		//IL_0235: Unknown result type (might be due to invalid IL or missing references)
		//IL_023a: Unknown result type (might be due to invalid IL or missing references)
		//IL_023f: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height);
		Text.Anchor = (TextAnchor)3;
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref val)).x + 5f, ((Rect)(ref val)).y, 60f, 24f);
		Widgets.Label(val2, Translator.Translate("VEF_AnimalsSearch"));
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref val2)).xMax + 5f, ((Rect)(ref val2)).y, 200f, 24f);
		searchKey = Widgets.TextField(val3, searchKey);
		Text.Anchor = (TextAnchor)0;
		List<string> list = (from x in pawnSpawnStates.Keys.ToList()
			orderby ((Def)(DefDatabase<ThingDef>.GetNamedSilentFail(x)?)).label
			where x.ToLower().Contains(searchKey.ToLower())
			select x).ToList();
		Listing_Standard val4 = new Listing_Standard();
		Rect val5 = default(Rect);
		((Rect)(ref val5))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref val3)).yMax + 35f, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 70f);
		Rect val6 = default(Rect);
		((Rect)(ref val6))._002Ector(((Rect)(ref val)).x, ((Rect)(ref val5)).y, ((Rect)(ref inRect)).width - 30f, (float)(list.Count * 24));
		Widgets.BeginScrollView(val5, ref scrollPosition, val6, true);
		((Listing)val4).Begin(val6);
		Rect val8 = default(Rect);
		for (int num = list.Count - 1; num >= 0; num--)
		{
			bool value = pawnSpawnStates[list[num]];
			if (DefDatabase<PawnKindDef>.GetNamedSilentFail(list[num]) == null)
			{
				pawnSpawnStates.Remove(list[num]);
			}
			else
			{
				Rect val7 = new Rect(0f, (float)(num * 24), 24f, 24f);
				((Rect)(ref val8))._002Ector(30f, (float)(num * 24), ((Rect)(ref inRect)).width - 100f, 24f);
				Widgets.ThingIcon(val7, PawnKindDef.Named(list[num]).race, (ThingDef)null, (ThingStyleDef)null, 1f, (Color?)null, (int?)null, 1f);
				Widgets.CheckboxLabeled(val8, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF_DisableAnimal", NamedArgument.op_Implicit(((Def)PawnKindDef.Named(list[num])).LabelCap))), ref value, false, (Texture2D)null, (Texture2D)null, false, false);
				pawnSpawnStates[list[num]] = value;
			}
		}
		((Listing)val4).End();
		Widgets.EndScrollView();
		((ModSettings)this).Write();
	}
}
