using System;
using UnityEngine;
using Verse;

namespace VEF.AI;

public class Command_ToggleWithRClick : Command_Toggle
{
	public Action rightClickAction;

	public override void ProcessInput(Event ev)
	{
		if (ev.button == 1)
		{
			rightClickAction?.Invoke();
		}
		else
		{
			((Command_Toggle)this).ProcessInput(ev);
		}
	}
}
