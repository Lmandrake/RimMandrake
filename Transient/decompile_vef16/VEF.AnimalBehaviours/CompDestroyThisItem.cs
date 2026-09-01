using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompDestroyThisItem : ThingComp
{
	public bool itemNeedsDestruction;

	public CompProperties_DestroyThisItem Props => (CompProperties_DestroyThisItem)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		if (((Thing)base.parent).Map != null)
		{
			((Thing)base.parent).Map.GetComponent<DestroyableObjects_MapComponent>()?.AddObjectToMap((Thing)(object)base.parent);
		}
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		if (map != null)
		{
			map.GetComponent<DestroyableObjects_MapComponent>()?.RemoveObjectFromMap((Thing)(object)base.parent);
		}
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		if (previousMap != null)
		{
			previousMap.GetComponent<DestroyableObjects_MapComponent>()?.RemoveObjectFromMap((Thing)(object)base.parent);
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref itemNeedsDestruction, "itemNeedsDestruction", false, false);
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (itemNeedsDestruction)
		{
			yield return (Gizmo)new Command_Action
			{
				action = CancelObjectForDestruction,
				hotKey = KeyBindingDefOf.Misc2,
				defaultDesc = TaggedString.op_Implicit(Translator.Translate(Props.buttonCancelDesc)),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get(Props.buttonCancelIcon, true),
				defaultLabel = TaggedString.op_Implicit(Translator.Translate(Props.buttonCancelLabel))
			};
		}
		else
		{
			yield return (Gizmo)new Command_Action
			{
				action = SetObjectForDestruction,
				hotKey = KeyBindingDefOf.Misc2,
				defaultDesc = TaggedString.op_Implicit(Translator.Translate(Props.buttonDesc)),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get(Props.buttonIcon, true),
				defaultLabel = TaggedString.op_Implicit(Translator.Translate(Props.buttonLabel))
			};
		}
	}

	private void SetObjectForDestruction()
	{
		itemNeedsDestruction = true;
	}

	private void CancelObjectForDestruction()
	{
		itemNeedsDestruction = false;
	}
}
