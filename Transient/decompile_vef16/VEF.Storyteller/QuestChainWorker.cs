using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.Grammar;

namespace VEF.Storyteller;

public class QuestChainWorker
{
	public QuestChainDef def;

	private string _cachedDescription;

	private static readonly List<CreepJoinerBaseDef> requires = new List<CreepJoinerBaseDef>();

	private static readonly List<CreepJoinerBaseDef> exclude = new List<CreepJoinerBaseDef>();

	public QuestChainState State => GameComponent_QuestChains.Instance.GetStateFor(def);

	public void EnsureAllUniquePawnsCreated()
	{
		if (def.uniqueCharacters == null)
		{
			return;
		}
		foreach (PawnKindDef uniqueCharacter in def.uniqueCharacters)
		{
			UniqueCharacterExtension modExtension = ((Def)uniqueCharacter).GetModExtension<UniqueCharacterExtension>();
			if (State.GetUniquePawn(modExtension.tag) == null)
			{
				CreateAndStoreUniquePawn(uniqueCharacter, modExtension);
			}
		}
	}

	public virtual Pawn CreateAndStoreUniquePawn(PawnKindDef kind, UniqueCharacterExtension ext)
	{
		Pawn val = GeneratePawn(kind);
		Log.Message($"Creating unique pawn {val.Name} {((Thing)val).thingIDNumber} with faction {((Thing)val).Faction?.def} for quest chain {((Def)def).defName} with tag {ext.tag}");
		State.StoreUniquePawn(ext.tag, val, deepSave: true);
		InvalidateDescriptionCache();
		return val;
	}

	public virtual Pawn GeneratePawn(PawnKindDef kind)
	{
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_025c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0262: Invalid comparison between Unknown and I4
		Faction val = null;
		if (kind.defaultFactionDef != null)
		{
			val = Find.FactionManager.FirstFactionOfDef(kind.defaultFactionDef);
		}
		Pawn val2 = null;
		CreepJoinerFormKindDef val3 = (CreepJoinerFormKindDef)(object)((kind is CreepJoinerFormKindDef) ? kind : null);
		if (val3 != null)
		{
			requires.AddRange(val3.Requires);
			exclude.AddRange(val3.Excludes);
			float combatPower = ((PawnKindDef)val3).combatPower;
			CreepJoinerBenefitDef random = CreepJoinerUtility.GetRandom<CreepJoinerBenefitDef>(DefDatabase<CreepJoinerBenefitDef>.AllDefsListForReading, combatPower, requires, exclude);
			CreepJoinerDownsideDef random2 = CreepJoinerUtility.GetRandom<CreepJoinerDownsideDef>(DefDatabase<CreepJoinerDownsideDef>.AllDefsListForReading, combatPower, requires, exclude);
			CreepJoinerAggressiveDef random3 = CreepJoinerUtility.GetRandom<CreepJoinerAggressiveDef>(DefDatabase<CreepJoinerAggressiveDef>.AllDefsListForReading, combatPower, requires, exclude);
			CreepJoinerRejectionDef random4 = CreepJoinerUtility.GetRandom<CreepJoinerRejectionDef>(DefDatabase<CreepJoinerRejectionDef>.AllDefsListForReading, combatPower, requires, exclude);
			PawnGenerationRequest val4 = default(PawnGenerationRequest);
			((PawnGenerationRequest)(ref val4))._002Ector((PawnKindDef)(object)val3, (Faction)null, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), true, false, false, true, false, 1f, false, true, true, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, true, false, false, -1, 0, false);
			((PawnGenerationRequest)(ref val4)).AllowedDevelopmentalStages = (DevelopmentalStage)8;
			((PawnGenerationRequest)(ref val4)).ForceGenerateNewPawn = true;
			((PawnGenerationRequest)(ref val4)).AllowFood = true;
			((PawnGenerationRequest)(ref val4)).DontGiveWeapon = true;
			((PawnGenerationRequest)(ref val4)).OnlyUseForcedBackstories = GenCollection.Any<BackstoryDef>(((PawnKindDef)val3).fixedAdultBackstories);
			((PawnGenerationRequest)(ref val4)).MaximumAgeTraits = 1;
			((PawnGenerationRequest)(ref val4)).MinimumAgeTraits = 1;
			((PawnGenerationRequest)(ref val4)).IsCreepJoiner = true;
			((PawnGenerationRequest)(ref val4)).ForceNoIdeoGear = true;
			((PawnGenerationRequest)(ref val4)).MustBeCapableOfViolence = true;
			((PawnGenerationRequest)(ref val4)).Faction = val;
			val2 = PawnGenerator.GeneratePawn(val4);
			Pawn_CreepJoinerTracker creepjoiner = val2.creepjoiner;
			creepjoiner.form = val3;
			creepjoiner.benefit = random;
			creepjoiner.downside = random2;
			creepjoiner.aggressive = random3;
			creepjoiner.rejection = random4;
			ApplyExtraTraits(val2, random.traits);
			ApplyExtraTraits(val2, random2.traits);
			ApplyExtraHediffs(val2, random.hediffs);
			ApplyExtraHediffs(val2, random2.hediffs);
			ApplySkillOverrides(val2, random.skills);
			ApplyExtraAbilities(val2, random.abilities);
			ApplyExtraAbilities(val2, random2.abilities);
			val2.guest.Recruitable = false;
			creepjoiner.Notify_Created();
		}
		else
		{
			val2 = PawnGenerator.GeneratePawn(kind, val, (PlanetTile?)null);
		}
		RulePackDef val5 = (((int)val2.gender == 2 && kind.nameMakerFemale != null) ? kind.nameMakerFemale : kind.nameMaker);
		if (val5 != null)
		{
			val2.Name = NameResolvedFrom(val5);
		}
		exclude.Clear();
		requires.Clear();
		return val2;
	}

	private static Name NameResolvedFrom(RulePackDef nameMaker, bool forceNoNick = false, List<Rule> extraRules = null)
	{
		return (Name)(object)NameTriple.FromString(NameGenerator.GenerateName(nameMaker, (Predicate<string>)((string x) => !((Name)NameTriple.FromString(x, false)).UsedThisGame), false, (string)null, (string)null, extraRules), forceNoNick);
	}

	private static void ApplySkillOverrides(Pawn pawn, List<SkillValue> skills)
	{
		foreach (SkillValue skill2 in skills)
		{
			SkillRecord skill = pawn.skills.GetSkill(skill2.skill);
			skill.Level = ((IntRange)(ref skill2.range)).RandomInRange;
			skill.xpSinceMidnight = 0f;
			skill.xpSinceLastLevel = 0f;
		}
	}

	private static void ApplyExtraTraits(Pawn pawn, List<BackstoryTrait> traits)
	{
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Expected O, but got Unknown
		foreach (BackstoryTrait trait in traits)
		{
			if (!pawn.story.traits.HasTrait(trait.def))
			{
				pawn.story.traits.GainTrait(new Trait(trait.def, trait.degree, true), false);
			}
		}
	}

	private static void ApplyExtraHediffs(Pawn pawn, List<HediffDef> hediffs)
	{
		foreach (HediffDef hediff in hediffs)
		{
			pawn.health.AddHediff(hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}

	private static void ApplyExtraAbilities(Pawn pawn, List<AbilityDef> abilities)
	{
		foreach (AbilityDef ability in abilities)
		{
			pawn.abilities.GainAbility(ability);
		}
	}

	public virtual Pawn GetUniquePawn(string tag)
	{
		Pawn uniquePawn = State.GetUniquePawn(tag);
		if (uniquePawn != null)
		{
			return uniquePawn;
		}
		EnsureAllUniquePawnsCreated();
		return State.GetUniquePawn(tag);
	}

	public virtual string GetDescription()
	{
		if (_cachedDescription == null)
		{
			string description = ((Def)def).description;
			_cachedDescription = Regex.Replace(description, "\\[(\\w+?)_(\\w+?)\\]", delegate(Match match)
			{
				//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
				string value = match.Groups[1].Value;
				string value2 = match.Groups[2].Value;
				Pawn uniquePawn = GetUniquePawn(value);
				if (uniquePawn == null)
				{
					return match.Value;
				}
				string text;
				switch (value2)
				{
				case "FullName":
				{
					Name name2 = uniquePawn.Name;
					text = ((name2 != null) ? name2.ToStringFull : null) ?? ((Entity)uniquePawn).LabelCap;
					break;
				}
				case "ShortName":
				{
					Name name = uniquePawn.Name;
					text = ((name != null) ? name.ToStringShort : null) ?? ((Entity)uniquePawn).LabelShortCap;
					break;
				}
				case "Label":
					text = ((Entity)uniquePawn).LabelCap;
					break;
				default:
					text = "";
					break;
				}
				string text2 = text;
				return string.IsNullOrEmpty(text2) ? match.Value : ColoredText.Colorize(text2, PawnNameColorUtility.PawnNameColorOf(uniquePawn));
			});
		}
		return _cachedDescription;
	}

	public void InvalidateDescriptionCache()
	{
		_cachedDescription = null;
	}
}
