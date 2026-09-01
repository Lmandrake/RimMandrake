using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Memes;

public class ExtendedMemeProperties : DefModExtension
{
	public string neededMeme;

	public List<string> requiredMemes;

	public TraitDef forcedTrait;

	public int factionOpinionOffset;

	public List<AbilityDef> abilitiesGiven;

	public List<ThingDef> removedDesignators;
}
