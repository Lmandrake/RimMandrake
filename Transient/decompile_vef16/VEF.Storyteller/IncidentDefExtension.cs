using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class IncidentDefExtension : DefModExtension
{
	private static readonly IncidentDefExtension DefaultValues = new IncidentDefExtension();

	public FactionDef forcedFaction;

	public IntRange forcedPointsRange = IntRange.Zero;

	public RaidStrategyDef forcedStrategy;

	public static IncidentDefExtension Get(Def def)
	{
		return def.GetModExtension<IncidentDefExtension>() ?? DefaultValues;
	}
}
