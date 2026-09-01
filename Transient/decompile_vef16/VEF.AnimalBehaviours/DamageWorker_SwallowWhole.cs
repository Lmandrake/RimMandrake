using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class DamageWorker_SwallowWhole : DamageWorker_Cut
{
	protected override void ApplySpecialEffectsToPart(Pawn pawn, float totalDamage, DamageInfo dinfo, DamageResult result)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Unknown result type (might be due to invalid IL or missing references)
		//IL_0120: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		//IL_0164: Unknown result type (might be due to invalid IL or missing references)
		//IL_0175: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		((DamageWorker_Cut)this).ApplySpecialEffectsToPart(pawn, totalDamage, dinfo, result);
		if (!(((DamageInfo)(ref dinfo)).Instigator is Pawn_SwallowWhole pawn_SwallowWhole) || ((Thing)pawn_SwallowWhole).Map == null || pawn.Downed || pawn.Dead || !(((Def)((Thing)pawn).def).defName != "AA_PhoenixOwlcat"))
		{
			return;
		}
		CompSwallowWhole compSwallowWhole = ThingCompUtility.TryGetComp<CompSwallowWhole>((Thing)(object)pawn_SwallowWhole);
		if (compSwallowWhole != null && pawn_SwallowWhole.innerContainer.Count < compSwallowWhole.Props.stomachCapacity && pawn.RaceProps.baseBodySize < compSwallowWhole.Props.maximumBodysize)
		{
			Need_Food food = ((Pawn)pawn_SwallowWhole).needs.food;
			((Need)food).CurLevel = ((Need)food).CurLevel + (float)compSwallowWhole.Props.nutritionGained;
			Patch_TakeDamage.instigatorToSet = (Thing)(object)pawn_SwallowWhole;
			try
			{
				HealthUtility.DamageUntilDowned(pawn, true, (DamageDef)null, (ThingDef)null, (BodyPartGroupDef)null);
			}
			catch (Exception ex)
			{
				Log.Error("Failed to swallow pawn: " + ex);
			}
			Patch_TakeDamage.instigatorToSet = null;
			if (compSwallowWhole.Props.soundPlayedWhenEating != null)
			{
				SoundStarter.PlayOneShot(SoundDef.Named(compSwallowWhole.Props.soundPlayedWhenEating), SoundInfo.op_Implicit(new TargetInfo(((Thing)pawn_SwallowWhole).Position, ((Thing)pawn_SwallowWhole).Map, false)));
			}
			if (compSwallowWhole.Props.sendLetterWhenEating && pawn != null && ((Thing)pawn).Faction != null && ((Thing)pawn).Faction.IsPlayer)
			{
				Find.LetterStack.ReceiveLetter(Translator.Translate(compSwallowWhole.Props.letterLabel), TranslatorFormattedStringExtensions.Translate(compSwallowWhole.Props.letterText, NamedArgument.op_Implicit((Thing)(object)pawn)), LetterDefOf.ThreatBig, LookTargets.op_Implicit((Thing)(object)pawn_SwallowWhole), (Faction)null, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
			}
			pawn_SwallowWhole.TryAcceptThing((Thing)(object)pawn);
		}
	}
}
