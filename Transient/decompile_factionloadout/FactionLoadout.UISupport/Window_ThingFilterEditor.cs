using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

public class Window_ThingFilterEditor : Window
{
	private readonly ThingFilter filter;

	private readonly UIState filterState = new UIState();

	public override Vector2 InitialSize => new Vector2(400f, 600f);

	public Window_ThingFilterEditor(ThingFilter filter)
		: base((IWindowDrawing)null)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Expected O, but got Unknown
		this.filter = filter;
		base.doCloseButton = true;
		base.closeOnClickedOutside = true;
		base.absorbInputAroundWindow = true;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		ThingFilterUI.DoThingFilterConfigWindow(new Rect(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - Window.CloseButSize.y - 4f), filterState, filter, (ThingFilter)null, 1, (IEnumerable<ThingDef>)null, (IEnumerable<SpecialThingFilterDef>)null, false, false, false, (List<ThingDef>)null, (Map)null);
	}
}
