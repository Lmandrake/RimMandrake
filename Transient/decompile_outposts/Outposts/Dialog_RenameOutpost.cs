using Verse;

namespace Outposts;

public class Dialog_RenameOutpost : Dialog_Rename<Outpost>
{
	private readonly Outpost outpost;

	public Dialog_RenameOutpost(Outpost outpost)
		: base(outpost)
	{
		this.outpost = outpost;
		base.curName = outpost.Name;
	}
}
