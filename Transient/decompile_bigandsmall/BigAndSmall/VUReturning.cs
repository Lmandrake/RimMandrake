using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class VUReturning : HediffWithComps
{
	public int ticksToReanimate = 180000;

	public int timeOfDeath;

	public static int lastCheckTick = -99999;

	public static bool deadRisingMode = false;

	public static bool zombieApocalypseMode = false;

	public static float durationDeadRisingMod = 1f;

	public static float durationZombieApocalypseMod = 3f;

	public static float ZombieApocalypseChance => 0f;

	public static float DeadRisingChance => 0.1f;

	public static float ReturnChance => 0.2f;

	public static float ReturnChanceApoc => 0.75f;

	public static float ReturnChanceColonist => 0.15f;

	public float PychoticWanderingChance => 0.5f;

	public float BerserkChance => 0.33f;

	public float BerserkChanceApoc => 0.75f;

	public float BerserkLoseFaction => 0.5f;

	public float BerserkLoseFactionApoc => 0.5f;

	public float ManhunterChance => 0.65f;

	public float PermanentBerserk => 0f;

	public float PermanentBerserkApoc => 0f;

	public override void ExposeData()
	{
		Scribe_Values.Look<int>(ref ticksToReanimate, "ticksToReanimate", 0, false);
		Scribe_Values.Look<int>(ref timeOfDeath, "timeOfDeath", 0, false);
		((HediffWithComps)this).ExposeData();
	}

	public void TrySetReanimateTime()
	{
		if (timeOfDeath != 0)
		{
			return;
		}
		timeOfDeath = Find.TickManager.TicksGame;
		int num = 60000;
		if (zombieApocalypseMode)
		{
			if (Rand.Chance(0.1f))
			{
				ticksToReanimate = (int)((float)num * Rand.Range(-0.05f, 0.1f));
			}
			else if (Rand.Chance(0.1f))
			{
				ticksToReanimate = (int)((float)num * Rand.Range(0.001f, 0.1f));
			}
			else if (Rand.Chance(0.5f))
			{
				ticksToReanimate = (int)((float)num * Rand.Range(0.45f, 0.55f));
			}
			else if (Rand.Chance(0.5f))
			{
				ticksToReanimate = (int)((float)num * Rand.Range(0.9f, 1f));
			}
			else
			{
				ticksToReanimate = (int)((float)num * Rand.Range(1f, 40f));
			}
		}
		else if (Rand.Chance(0.1f))
		{
			ticksToReanimate = (int)((float)num * Rand.Range(0.001f, 0.1f));
		}
		else if (Rand.Chance(0.5f))
		{
			ticksToReanimate = (int)((float)num * Rand.Range(0.9f, 1f));
		}
		else if (Rand.Chance(0.25f))
		{
			ticksToReanimate = (int)((float)num * Rand.Range(2.7f, 3.4f));
		}
		else if (Rand.Chance(0.5f))
		{
			ticksToReanimate = (int)((float)num * Rand.Range(3f, 10f));
		}
		else
		{
			ticksToReanimate = (int)((float)num * Rand.Range(10f, 80f));
		}
	}

	public bool TryReanimate(bool forceTrigger = false)
	{
		//IL_038f: Unknown result type (might be due to invalid IL or missing references)
		//IL_034f: Unknown result type (might be due to invalid IL or missing references)
		//IL_031c: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e6: Unknown result type (might be due to invalid IL or missing references)
		if (((Hediff)this).pawn.Dead)
		{
			if (((Hediff)this).pawn.IsUndead() || !((Hediff)this).pawn.RaceProps.IsFlesh)
			{
				((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
				return false;
			}
			Hediff val = default(Hediff);
			if (((Hediff)this).pawn.health.hediffSet.TryGetHediff(BSDefs.BS_Soulless, ref val))
			{
				((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
				return false;
			}
			TrySetReanimateTime();
			if (timeOfDeath + ticksToReanimate < Find.TickManager.TicksGame)
			{
				EjectCorpse();
				Faction val2 = Find.FactionManager.AllFactions.FirstOrDefault((Faction x) => ((Def)x.def).defName == "BS_ZombieFaction");
				HediffDef val3 = null;
				if (((Hediff)this).pawn.RaceProps.Humanlike)
				{
					((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
					XenotypeDef returnedXeno = GlobalSettings.GetRandomReturnedXenotype;
					if (((Thing)((Hediff)this).pawn).Faction == Faction.OfPlayerSilentFail)
					{
						returnedXeno = GlobalSettings.GetRandomReturnedColonistXenotype;
					}
					if (returnedXeno == null)
					{
						Log.Warning("Returned Xenotype is null!");
						return false;
					}
					ModifyReturnedByRotStage(((Hediff)this).pawn, ref returnedXeno);
					Pawn pawn = ((Hediff)this).pawn;
					XenotypeDef def = returnedXeno;
					string label = ((Def)returnedXeno).label;
					Pawn_GeneTracker genes = ((Hediff)this).pawn.genes;
					GeneHelpers.AddAllXenotypeGenes(pawn, def, label + " " + ((genes != null) ? genes.XenotypeLabel : null));
				}
				else
				{
					val3 = GetAnimalReturnedHediff(((Hediff)this).pawn);
				}
				GameUtils.UnhealingRessurection(((Hediff)this).pawn);
				if (val3 != null)
				{
					((Hediff)this).pawn.health.AddHediff(val3, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				if ((!zombieApocalypseMode && Rand.Chance(BerserkChance)) || (zombieApocalypseMode && Rand.Chance(BerserkChanceApoc)))
				{
					if (val2 != null)
					{
						if ((zombieApocalypseMode && Rand.Chance(BerserkLoseFactionApoc)) || (!zombieApocalypseMode && Rand.Chance(BerserkLoseFaction)))
						{
							((Thing)((Hediff)this).pawn).SetFaction(val2, (Pawn)null);
						}
						else
						{
							((Thing)((Hediff)this).pawn).SetFaction(val2, (Pawn)null);
							if (((Thing)((Hediff)this).pawn).Faction == Faction.OfPlayerSilentFail && Faction.OfPlayerSilentFail != null)
							{
								Pawn pawn2 = ((Hediff)this).pawn;
								if (pawn2 != null)
								{
									Pawn_GuestTracker guest = pawn2.guest;
									if (guest != null)
									{
										_ = guest.resistance;
										if (true)
										{
											((Hediff)this).pawn.guest.resistance = 0f;
										}
									}
								}
								Pawn pawn3 = ((Hediff)this).pawn;
								if (pawn3 != null)
								{
									Pawn_GuestTracker guest2 = pawn3.guest;
									if (guest2 != null)
									{
										_ = guest2.will;
										if (true)
										{
											((Hediff)this).pawn.guest.will = Rand.Range(1, 5);
										}
									}
								}
							}
						}
					}
					float num = (zombieApocalypseMode ? PermanentBerserkApoc : PermanentBerserk);
					if (Rand.Chance(ManhunterChance))
					{
						if (Rand.Chance(num))
						{
							((Hediff)this).pawn.mindState.mentalStateHandler.TryStartMentalState(BSDefs.BS_LostManhunterPermanent, TaggedString.op_Implicit(Translator.Translate("BS_ZombieReason")), false, true, false, (Pawn)null, false, false, false);
						}
						else
						{
							((Hediff)this).pawn.mindState.mentalStateHandler.TryStartMentalState(BSDefs.BS_LostManhunter, TaggedString.op_Implicit(Translator.Translate("BS_ZombieReason")), false, true, false, (Pawn)null, false, false, false);
						}
					}
					else
					{
						((Hediff)this).pawn.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Berserk, TaggedString.op_Implicit(Translator.Translate("BS_ZombieReason")), false, true, false, (Pawn)null, false, false, false);
					}
				}
				else if (Rand.Chance(PychoticWanderingChance))
				{
					((Hediff)this).pawn.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Wander_Psychotic, TaggedString.op_Implicit(Translator.Translate("BS_ZombieReason")), false, true, false, (Pawn)null, false, false, false);
				}
				((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
				return true;
			}
		}
		else
		{
			((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
		}
		return false;
	}

	public static HediffDef GetAnimalReturnedHediff(Pawn pawn)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Invalid comparison between Unknown and I4
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Invalid comparison between Unknown and I4
		RotStage rotStage = RottableUtility.GetRotStage((Thing)(object)pawn);
		HediffDef result = BSDefs.VU_AnimalReturned;
		if ((int)rotStage == 2)
		{
			result = BSDefs.VU_AnimalReturnedSkeletal;
		}
		else if ((int)rotStage == 1)
		{
			result = BSDefs.VU_AnimalReturnedRotted;
		}
		return result;
	}

	public static void ModifyReturnedByRotStage(Pawn pawn, ref XenotypeDef returnedXeno)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Invalid comparison between Unknown and I4
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		if ((int)RottableUtility.GetRotStage((Thing)(object)pawn) == 2 && (returnedXeno == BSDefs.VU_Returned || returnedXeno == BSDefs.VU_Returned_Intact))
		{
			returnedXeno = BSDefs.VU_ReturnedSkeletal;
		}
		else if ((int)RottableUtility.GetRotStage((Thing)(object)pawn) == 0 && returnedXeno == BSDefs.VU_ReturnedSkeletal)
		{
			returnedXeno = BSDefs.VU_Returned_Intact;
		}
	}

	private void EjectCorpse()
	{
		IThingHolder parentHolder = ((Thing)((Hediff)this).pawn).ParentHolder;
		while (parentHolder is Corpse)
		{
			parentHolder = parentHolder.ParentHolder;
		}
		Building_Casket val = (Building_Casket)(object)((parentHolder is Building_Casket) ? parentHolder : null);
		if (val != null)
		{
			val.EjectContents();
		}
	}
}
