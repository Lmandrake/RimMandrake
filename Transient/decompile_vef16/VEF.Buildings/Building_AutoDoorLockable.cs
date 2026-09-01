using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

[StaticConstructorOnStartup]
public class Building_AutoDoorLockable : Building_Door
{
	public static readonly Texture2D DoorStateButton = ContentFinder<Texture2D>.Get("UI/Overlays/DoorStateButton", true);

	private DoorAccess curDoorAccess;

	private Dictionary<DoorAccess, string> doorStates = new Dictionary<DoorAccess, string>
	{
		{
			DoorAccess.Default,
			TaggedString.op_Implicit(Translator.Translate("VEF.DoorLockDefault"))
		},
		{
			DoorAccess.Everyone,
			TaggedString.op_Implicit(Translator.Translate("VEF.DoorLockEveryone"))
		},
		{
			DoorAccess.OnlyColonistsAndAnimals,
			TaggedString.op_Implicit(Translator.Translate("VEF.DoorLockOnlyColonistsAndAnimals"))
		},
		{
			DoorAccess.OnlyColonistsAndAnimalsAndFriendlies,
			TaggedString.op_Implicit(Translator.Translate("VEF.DoorLockOnlyColonistsAndAnimalsAndFriendlies"))
		},
		{
			DoorAccess.OnlyDrafted,
			TaggedString.op_Implicit(Translator.Translate("VEF.DoorLockOnlyDrafted"))
		}
	};

	public Material DoorStateMaterial => (Material)(curDoorAccess switch
	{
		DoorAccess.Everyone => MaterialPool.MatFrom("UI/Overlays/DoorStateOverlay_Green"), 
		DoorAccess.OnlyColonistsAndAnimals => MaterialPool.MatFrom("UI/Overlays/DoorStateOverlay_Orange"), 
		DoorAccess.OnlyColonistsAndAnimalsAndFriendlies => MaterialPool.MatFrom("UI/Overlays/DoorStateOverlay_Blue"), 
		DoorAccess.OnlyDrafted => MaterialPool.MatFrom("UI/Overlays/DoorStateOverlay_Red"), 
		_ => MaterialPool.MatFrom("UI/Overlays/DoorStateOverlay_Green"), 
	});

	public override bool PawnCanOpen(Pawn p)
	{
		return curDoorAccess switch
		{
			DoorAccess.Default => ((Building_Door)this).PawnCanOpen(p), 
			DoorAccess.Everyone => true, 
			DoorAccess.OnlyColonistsAndAnimals => OnlyColonistsAndAnimals(p), 
			DoorAccess.OnlyColonistsAndAnimalsAndFriendlies => OnlyColonistsAndAnimalsAndFriendlies(p), 
			DoorAccess.OnlyDrafted => OnlyDrafted(p), 
			_ => true, 
		};
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		((Building_Door)this).DrawAt(drawLoc, flip);
		if (!((Building_Door)this).Open && Mathf.Clamp01((float)base.ticksSinceOpen / (float)((Building_Door)this).TicksToOpenNow) == 0f)
		{
			Vector3 drawPos = ((Thing)this).DrawPos;
			drawPos.y = Altitudes.AltitudeFor((AltitudeLayer)14) + 1f;
			Mesh plane = MeshPool.plane10;
			Vector3 val = drawPos;
			Rot4 rotation = ((Thing)this).Rotation;
			Graphics.DrawMesh(plane, val, ((Rot4)(ref rotation)).AsQuat, DoorStateMaterial, 0);
		}
	}

	public override IEnumerable<Gizmo> GetGizmos()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		Command_Action val = new Command_Action();
		val.action = delegate
		{
			//IL_0052: Unknown result type (might be due to invalid IL or missing references)
			//IL_005c: Expected O, but got Unknown
			//IL_007b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Expected O, but got Unknown
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			foreach (KeyValuePair<DoorAccess, string> doorState in doorStates)
			{
				list.Add(new FloatMenuOption(doorState.Value, (Action)delegate
				{
					curDoorAccess = doorState.Key;
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			}
			Find.WindowStack.Add((Window)new FloatMenu(list));
		};
		((Command)val).defaultLabel = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.DoorLockState", NamedArgument.op_Implicit(doorStates[curDoorAccess])));
		((Command)val).defaultDesc = TaggedString.op_Implicit(Translator.Translate("VEF.DoorLockStateDesc"));
		((Gizmo)val).Disabled = !base.powerComp.PowerOn;
		((Gizmo)val).disabledReason = TaggedString.op_Implicit(Translator.Translate("VEF.DoorLockStatePowerOff"));
		((Command)val).icon = (Texture)(object)DoorStateButton;
		yield return (Gizmo)(object)val;
	}

	private bool OnlyColonistsAndAnimals(Pawn p)
	{
		if (((Thing)p).Faction == ((Thing)this).Faction)
		{
			return true;
		}
		return false;
	}

	private bool OnlyColonistsAndAnimalsAndFriendlies(Pawn p)
	{
		if (((Thing)p).Faction != null && (((Thing)p).Faction == ((Thing)this).Faction || !FactionUtility.HostileTo(((Thing)p).Faction, ((Thing)this).Faction)))
		{
			return true;
		}
		return false;
	}

	private bool OnlyDrafted(Pawn p)
	{
		if (((Thing)p).Faction == ((Thing)this).Faction && p.Drafted)
		{
			return true;
		}
		return false;
	}

	public override void ExposeData()
	{
		((Building_Door)this).ExposeData();
		Scribe_Values.Look<DoorAccess>(ref curDoorAccess, "curDoorAccess", DoorAccess.Default, false);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((Building_Door)this).GetGizmos();
	}
}
