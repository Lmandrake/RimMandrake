using System;
using Verse;

namespace FactionLoadout.UISupport;

public class Tab
{
	public readonly string Name;

	private readonly Action<Listing_Standard> draw;

	public Tab(string name, Action<Listing_Standard> draw)
	{
		Name = name;
		this.draw = draw;
	}

	public virtual void Draw(Listing_Standard ui)
	{
		DrawRegionTitle(ui, Name);
		draw?.Invoke(ui);
	}

	protected static void DrawRegionTitle(Listing_Standard ui, string title)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		((Listing)ui).GapLine(26f);
		Widgets.Label(((Listing)ui).GetRect(42f, 1f), "<size=26><b><color=#73fff2>" + title + "</color></b></size>");
	}
}
