using Verse;

namespace BigAndSmall;

public class PilotedCompProps : HediffComp
{
	public CompProperties_Piloted Props => (CompProperties_Piloted)(object)base.props;
}
