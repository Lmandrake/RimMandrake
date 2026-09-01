using System.Linq;
using Verse;

namespace BigAndSmall;

public class GeneEater : Gene
{
	public static Thing lastEatenThing;

	public static int lastEatenThingTicks;

	public override void Notify_IngestedThing(Thing thing, int numTaken)
	{
		((Gene)this).Notify_IngestedThing(thing, numTaken);
		if (lastEatenThing == thing && Find.TickManager.TicksGame - lastEatenThingTicks < 6000)
		{
			return;
		}
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		Thing obj = ((thing is Corpse) ? thing : null);
		Pawn val2 = ((obj != null) ? ((Corpse)obj).InnerPawn : null);
		if (val == null && val2 == null)
		{
			return;
		}
		lastEatenThing = thing;
		Pawn target = val ?? val2;
		int num = (Rand.Chance(0.75f) ? Rand.Range(1, 2) : (Rand.Chance(0.5f) ? Rand.Range(3, 5) : ((!Rand.Chance(0.5f)) ? 99 : Rand.Range(6, 12))));
		CompProperties_IncorporateEffect.IncorporateGenes(base.pawn, target, num * 2, stealTraits: false, userPicks: false, num, excludeBodySwap: true);
		foreach (Gene item in base.pawn.genes.GenesListForReading.Where((Gene x) => ((Def)x.def).defName.Contains("BS_Diet_Herbivore")))
		{
			base.pawn.genes.RemoveGene(item);
		}
	}
}
