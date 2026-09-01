using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class Ability_Spawn : Ability
{
	public override bool CanAutoCast => false;

	public override void Cast(params GlobalTargetInfo[] targets)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets);
		AbilityExtension_Spawn modExtension = ((Def)def).GetModExtension<AbilityExtension_Spawn>();
		if (modExtension?.thing != null)
		{
			for (int i = 0; i < targets.Length; i++)
			{
				Spawn(targets[i], modExtension.thing, this);
			}
		}
	}

	public override bool ValidateTarget(LocalTargetInfo target, bool showMessages = true)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		AbilityExtension_Spawn modExtension = ((Def)def).GetModExtension<AbilityExtension_Spawn>();
		if (GridsUtility.Filled(((LocalTargetInfo)(ref target)).Cell, ((Thing)pawn).Map) || (GridsUtility.GetFirstBuilding(((LocalTargetInfo)(ref target)).Cell, ((Thing)pawn).Map) != null && modExtension != null && !modExtension.allowOnBuildings))
		{
			if (showMessages)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("AbilityOccupiedCells", NamedArgument.op_Implicit(((Def)def).LabelCap))), LookTargets.op_Implicit(((LocalTargetInfo)(ref target)).ToTargetInfo(((Thing)pawn).Map)), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		return base.ValidateTarget(target, showMessages);
	}

	public static void Spawn(GlobalTargetInfo target, ThingDef def, Ability ability)
	{
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		Thing val = ThingMaker.MakeThing(def, (ThingDef)null);
		CompDuration compDuration = ThingCompUtility.TryGetComp<CompDuration>(val);
		if (compDuration != null)
		{
			compDuration.durationTicksLeft = ability.GetDurationForPawn();
		}
		CompAbilitySpawn compAbilitySpawn = ThingCompUtility.TryGetComp<CompAbilitySpawn>(val);
		if (compAbilitySpawn != null)
		{
			compAbilitySpawn.pawn = ability.pawn;
			compAbilitySpawn.source = ability;
		}
		if (val.def.CanHaveFaction)
		{
			val.SetFactionDirect(((Thing)ability.pawn).Faction);
		}
		GenSpawn.Spawn(val, ((GlobalTargetInfo)(ref target)).Cell, ((GlobalTargetInfo)(ref target)).Map, (WipeMode)0);
	}
}
