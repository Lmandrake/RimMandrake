using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

internal class HeavyWeaponsSettings : ModSettings
{
	public Dictionary<string, bool> weaponStates = new Dictionary<string, bool>();

	public Dictionary<string, int> weaponHPStates = new Dictionary<string, int>();

	private List<string> weaponsKeys1;

	private List<bool> boolValues;

	private List<string> weaponsKeys2;

	private List<int> floatValues;

	private static Vector2 scrollPosition = Vector2.zero;

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Collections.Look<string, bool>(ref weaponStates, "weaponStates", (LookMode)1, (LookMode)1, ref weaponsKeys1, ref boolValues, true, false, false);
		Scribe_Collections.Look<string, int>(ref weaponHPStates, "weaponHPStates", (LookMode)1, (LookMode)1, ref weaponsKeys2, ref floatValues, true, false, false);
	}

	public void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Expected O, but got Unknown
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		List<string> list = (from x in weaponStates.Keys.ToList()
			orderby x descending
			select x).ToList();
		Rect val = new Rect(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref inRect)).width - 30f, (float)(list.Count * 74));
		Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
		Listing_Standard val3 = new Listing_Standard();
		((Listing)val3).Begin(val2);
		for (int num = list.Count - 1; num >= 0; num--)
		{
			bool flag = weaponStates[list[num]];
			ThingDef named = DefDatabase<ThingDef>.GetNamed(list[num], false);
			if (named != null)
			{
				val3.CheckboxLabeled("Enable HP deduction per shot for " + ((Def)named).label + ":", ref flag, (string)null, 0f, 1f);
				weaponStates[list[num]] = flag;
				if (!flag)
				{
					weaponHPStates[list[num]] = 0;
				}
				val3.Label("Adjust HP deduction per shot for " + ((Def)named).label + ": " + weaponHPStates[list[num]], -1f, (TipSignal?)null);
				float num2 = val3.Slider((float)weaponHPStates[list[num]], 0f, 100f);
				weaponHPStates[list[num]] = (int)num2;
			}
		}
		((Listing)val3).End();
		Widgets.EndScrollView();
		((ModSettings)this).Write();
	}
}
