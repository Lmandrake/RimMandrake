using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ReturningSoul : Gene
{
	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		//IL_0330: Unknown result type (might be due to invalid IL or missing references)
		//IL_033a: Expected O, but got Unknown
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_018f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		((Gene)this).Notify_PawnDied(dinfo, culprit);
		ReturningSoulModExt modExtension = ((Def)base.def).GetModExtension<ReturningSoulModExt>();
		if (modExtension == null)
		{
			Log.Error("ReturningSoul gene is missing its ModExt. Please add it to the gene.");
			return;
		}
		Corpse corpse = base.pawn.Corpse;
		if (MakeCorpse_Patch.corpse == null)
		{
			corpse = MakeCorpse_Patch.corpse;
		}
		bool num = base.pawn.health.hediffSet.HasHediff(BSDefs.BS_BurnReturnDenial, false);
		string text = ((object)base.pawn.Name).ToString();
		if (!num)
		{
			if (!dinfo.HasValue)
			{
				goto IL_011f;
			}
			object obj;
			DamageInfo valueOrDefault;
			if (!dinfo.HasValue)
			{
				obj = null;
			}
			else
			{
				valueOrDefault = dinfo.GetValueOrDefault();
				obj = ((DamageInfo)(ref valueOrDefault)).Def;
			}
			if (obj != DamageDefOf.Flame)
			{
				object obj2;
				if (!dinfo.HasValue)
				{
					obj2 = null;
				}
				else
				{
					valueOrDefault = dinfo.GetValueOrDefault();
					obj2 = ((Def)(((DamageInfo)(ref valueOrDefault)).Def?)).defName;
				}
				if (!((string)obj2 == "Burn"))
				{
					goto IL_011f;
				}
			}
		}
		if (((Thing)base.pawn).Faction == Faction.OfPlayerSilentFail)
		{
			Find.LetterStack.ReceiveLetter(TranslatorFormattedStringExtensions.Translate("BS_ReturningSoul_FireTitle", NamedArgument.op_Implicit(text)), TranslatorFormattedStringExtensions.Translate("BS_ReturningSoul_Fire", NamedArgument.op_Implicit(text)), LetterDefOf.NegativeEvent, LookTargets.op_Implicit((Thing)(object)base.pawn), (Faction)null, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
		}
		return;
		IL_011f:
		Pawn pawn = base.pawn;
		if (pawn != null)
		{
			Pawn_HealthTracker health = pawn.health;
			bool? obj3;
			if (health == null)
			{
				obj3 = null;
			}
			else
			{
				HediffSet hediffSet = health.hediffSet;
				Hediff val = default(Hediff);
				obj3 = ((hediffSet != null) ? new bool?(hediffSet.TryGetHediff(BSDefs.BS_Soulless, ref val)) : ((bool?)null));
			}
			bool? flag = obj3;
			if (flag == true)
			{
				if (((Thing)base.pawn).Faction == Faction.OfPlayerSilentFail)
				{
					Find.LetterStack.ReceiveLetter(TranslatorFormattedStringExtensions.Translate("BS_WasKilled_Title", NamedArgument.op_Implicit(text)), TranslatorFormattedStringExtensions.Translate("BS_WasKilledSoulless", NamedArgument.op_Implicit(text)), LetterDefOf.NegativeEvent, LookTargets.op_Implicit((Thing)(object)base.pawn), (Faction)null, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
				}
				return;
			}
		}
		if (ModLister.CheckAnomaly("Returning soul"))
		{
			try
			{
				FilthMaker.TryMakeFilth(((Thing)corpse).Position, ((Thing)corpse).Map, ThingDefOf.Filth_Ash, 11, (FilthSourceFlags)0, true);
			}
			catch
			{
			}
		}
		if (base.pawn.IsColonist)
		{
			ReturningSoulHolder item = new ReturningSoulHolder
			{
				pawn = base.pawn,
				ticksToReturn = (int)(Rand.Range(0.5f, 5f) * 60000f * BS.Settings.immortalReturnTimeFactor),
				corpseReturn = modExtension.corpseReturn,
				addCorpseGenes = modExtension.addCorpseGenes,
				addCorpseBionics = modExtension.addCorpseBionics
			};
			ReturningSoulManager.instance.ProcessSouls();
			ReturningSoulManager.instance.returningSouls.Add(item);
		}
		else
		{
			if (modExtension.corpseReturn)
			{
				try
				{
					base.pawn.story.hairDef = GenCollection.RandomElement<HairDef>((IEnumerable<HairDef>)DefDatabase<HairDef>.AllDefsListForReading);
					base.pawn.story.bodyType = GenCollection.RandomElement<BodyTypeDef>((IEnumerable<BodyTypeDef>)DefDatabase<BodyTypeDef>.AllDefsListForReading);
					base.pawn.story.bodyType = GenCollection.RandomElement<BodyTypeDef>((IEnumerable<BodyTypeDef>)DefDatabase<BodyTypeDef>.AllDefsListForReading);
				}
				catch
				{
				}
			}
			try
			{
				PawnKindDef kindDef = base.pawn.kindDef;
				string weapon = GenCollection.RandomElement<string>((IEnumerable<string>)kindDef.weaponTags);
				Thing val2 = ThingMaker.MakeThing(GenCollection.RandomElement<ThingDef>(DefDatabase<ThingDef>.AllDefsListForReading.Where((ThingDef x) => x.weaponTags != null && x.weaponTags.Contains(weapon))), (ThingDef)null);
				base.pawn.equipment.AddEquipment((ThingWithComps)val2);
			}
			catch (Exception ex)
			{
				Log.Error($"Failed to add new weapon to {base.pawn.Name}: {ex.Message}\n{ex.StackTrace}");
			}
		}
		ResurrectionUtility.TryResurrect(base.pawn, (ResurrectionParams)null);
		((Entity)base.pawn).DeSpawn((DestroyMode)0);
	}
}
