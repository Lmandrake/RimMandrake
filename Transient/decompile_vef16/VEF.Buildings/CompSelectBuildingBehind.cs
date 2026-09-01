using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompSelectBuildingBehind : ThingComp
{
	private Texture2D cachedCommandTex;

	public Thing building;

	public CompProperties_SelectBuildingBehind Props => (CompProperties_SelectBuildingBehind)(object)base.props;

	private Texture2D CommandTex
	{
		get
		{
			if ((Object)(object)cachedCommandTex == (Object)null)
			{
				cachedCommandTex = ContentFinder<Texture2D>.Get(Props.commandButtonImage, true);
			}
			return cachedCommandTex;
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		List<Thing> list = ((Thing)base.parent).Map.thingGrid.ThingsListAt(((Thing)base.parent).Position);
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i] is Building && ((Def)list[i].def).defName == Props.buildingToSelect)
			{
				building = list[i];
			}
		}
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		if (((Thing)base.parent).Faction == Faction.OfPlayer)
		{
			yield return (Gizmo)new Command_Action
			{
				hotKey = KeyBindingDefOf.Command_TogglePower,
				icon = (Texture)(object)CommandTex,
				defaultLabel = TaggedString.op_Implicit(Translator.Translate(Props.commandButtonText)),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate(Props.commandButtonDesc)),
				action = delegate
				{
					Find.Selector.Deselect((object)base.parent);
					Find.Selector.Select((object)building, true, true);
				}
			};
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingComp)this).CompGetGizmosExtra();
	}
}
