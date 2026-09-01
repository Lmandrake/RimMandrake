using Verse;

namespace BigAndSmall;

public class UnfinishedMechanicalRace : UnfinishedThing
{
	public override string LabelNoCount => TaggedString.op_Implicit(((Def)((Thing)this).def).LabelCap);
}
