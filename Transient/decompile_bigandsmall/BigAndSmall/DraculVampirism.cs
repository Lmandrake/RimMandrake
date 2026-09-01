using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class DraculVampirism : HediffWithComps
{
	public int stageOfMostPowerfulDracul;

	private bool checkedForHalfVampirism;

	private bool willBecomeHalfVampire;

	public int ticksToReanimate = 180000;

	public int timeOfDeath;

	public bool checkedForMaster;

	public Faction factionOfMaster;

	private bool checkedForAnimalUndead;

	public override void PostTick()
	{
		if (GeneUtility.IsBloodfeeder(((Hediff)this).pawn))
		{
			((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
		}
		else if (!((Hediff)this).pawn.RaceProps.Humanlike && !checkedForAnimalUndead)
		{
			foreach (Hediff item in ((Hediff)this).pawn.health?.hediffSet.hediffs)
			{
				if (((Def)item.def).defName == "VU_DraculAnimalVampirism" || GenCollection.Any<PawnExtension>(item.def.GetAllPawnExtensionsOnHediff(), (Predicate<PawnExtension>)((PawnExtension x) => x.isUnliving || x.isMechanical)))
				{
					((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
					break;
				}
			}
			checkedForAnimalUndead = true;
		}
		((HediffWithComps)this).PostTick();
		if (!checkedForHalfVampirism && ((Hediff)this).Severity > 0.8f)
		{
			if (Rand.Chance(0.66f))
			{
				willBecomeHalfVampire = true;
			}
			checkedForHalfVampirism = true;
		}
		if (willBecomeHalfVampire && HediffUtility.FullyImmune((Hediff)(object)this))
		{
			foreach (XenotypeDef item2 in DefDatabase<XenotypeDef>.AllDefsListForReading.Where((XenotypeDef x) => ((Def)x).defName == "VU_Dracul_HalfVampire"))
			{
				GeneHelpers.AddAllXenotypeGenes(((Hediff)this).pawn, item2, "Half-Vampire");
			}
		}
		TryAssignFactionOfMasterIfMissing();
	}

	public override void ExposeData()
	{
		Scribe_References.Look<Faction>(ref factionOfMaster, "factionOfMaster", false);
		Scribe_Values.Look<int>(ref ticksToReanimate, "ticksToReanimate", 0, false);
		Scribe_Values.Look<bool>(ref checkedForHalfVampirism, "checkedForHalfVampirism", false, false);
		((HediffWithComps)this).ExposeData();
	}

	private void TryAssignFactionOfMasterIfMissing()
	{
		if (factionOfMaster != null || checkedForMaster)
		{
			return;
		}
		checkedForMaster = true;
		Faction val = null;
		Pawn pawn = ((Hediff)this).pawn;
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Map map = ((Thing)pawn).Map;
			if (map == null)
			{
				obj = null;
			}
			else
			{
				MapPawns mapPawns = map.mapPawns;
				obj = ((mapPawns != null) ? mapPawns.AllPawns.Where((Pawn x) => !x.Dead && x.genes != null && DraculStageExtension.TryGetDraculStage(x).draculGene != null) : null);
			}
		}
		foreach (Pawn item in (IEnumerable<Pawn>)obj)
		{
			if (FactionUtility.HostileTo(((Thing)item).Faction, Faction.OfPlayer))
			{
				val = ((Thing)item).Faction;
			}
			else if (((Thing)((Hediff)this).pawn).Faction == Faction.OfPlayer)
			{
				factionOfMaster = ((Thing)((Hediff)this).pawn).Faction;
				break;
			}
		}
		if (factionOfMaster == null && val != null)
		{
			factionOfMaster = val;
		}
	}

	public void TrySetReanimateTime()
	{
		if (timeOfDeath == 0)
		{
			timeOfDeath = Find.TickManager.TicksGame;
			int num = 60000;
			if (!((Hediff)this).pawn.RaceProps.Humanlike)
			{
				ticksToReanimate = (int)((float)(num / (stageOfMostPowerfulDracul + 1)) * Rand.Range(0.5f, 1.5f));
			}
			else
			{
				ticksToReanimate = (int)((float)(num / (stageOfMostPowerfulDracul + 1)) * Rand.Range(0.5f, 3f));
			}
			ticksToReanimate = Mathf.Clamp(ticksToReanimate, num / 3, num * 2);
		}
	}

	public int GetFinalVampireLevel()
	{
		int num = 0;
		if (((Hediff)this).Severity < 0.5f)
		{
			num = -3;
		}
		else if (((Hediff)this).Severity < 0.8f)
		{
			num = -2;
		}
		else if (((Hediff)this).Severity >= 0.8f)
		{
			num = -1;
		}
		return num + stageOfMostPowerfulDracul;
	}

	public bool TryReanimate()
	{
		if (((Hediff)this).pawn.Dead && (double)((Hediff)this).Severity > 0.15)
		{
			TrySetReanimateTime();
			if (timeOfDeath + ticksToReanimate < Find.TickManager.TicksGame)
			{
				EjectCorpse();
				if (!((Hediff)this).pawn.RaceProps.Humanlike)
				{
					Hediff val = HediffMaker.MakeHediff(HediffDef.Named("VU_DraculAnimalVampirism"), ((Hediff)this).pawn, (BodyPartRecord)null);
					((Hediff)this).pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				else
				{
					int finalVampireLevel = GetFinalVampireLevel();
					((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
					string targetXenotype;
					if (finalVampireLevel <= 0)
					{
						targetXenotype = "VU_Dracul_Feral";
					}
					else if (finalVampireLevel <= 2)
					{
						targetXenotype = "VU_Dracul_Spawn";
					}
					else
					{
						targetXenotype = "VU_Dracul";
					}
					foreach (XenotypeDef item in DefDatabase<XenotypeDef>.AllDefsListForReading.Where((XenotypeDef x) => ((Def)x).defName == targetXenotype))
					{
						((Hediff)this).pawn.genes.SetXenotype(item);
					}
				}
				GameUtils.UnhealingRessurection(((Hediff)this).pawn);
				if (((Hediff)this).pawn.RaceProps.Humanlike)
				{
					SetFactionOfVampire();
				}
				if (factionOfMaster != Faction.OfPlayer)
				{
					if (Rand.Chance(0.75f))
					{
						((Hediff)this).pawn.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Berserk, (string)null, false, false, false, (Pawn)null, false, false, false);
					}
				}
				else if (Rand.Chance(0.25f))
				{
					((Hediff)this).pawn.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Berserk, (string)null, false, false, false, (Pawn)null, false, false, false);
				}
				return true;
			}
		}
		return false;
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

	public void SetFactionOfVampire()
	{
		if (factionOfMaster == null)
		{
			return;
		}
		if (((Thing)((Hediff)this).pawn).Faction.IsPlayer)
		{
			if (!factionOfMaster.IsPlayer && !FactionUtility.AllyOrNeutralTo(factionOfMaster, Faction.OfPlayer))
			{
				((Thing)((Hediff)this).pawn).SetFaction(factionOfMaster, (Pawn)null);
			}
		}
		else if (factionOfMaster.IsPlayer)
		{
			if (((Hediff)this).pawn.RaceProps.Humanlike)
			{
				if (ModsConfig.IdeologyActive)
				{
					GenGuest.EnslavePrisoner(GenCollection.RandomElement<Pawn>((IEnumerable<Pawn>)((Thing)((Hediff)this).pawn).Map.mapPawns.FreeColonists), ((Hediff)this).pawn);
				}
				else
				{
					((Thing)((Hediff)this).pawn).SetFaction(Faction.OfPlayer, (Pawn)null);
				}
			}
		}
		else
		{
			((Thing)((Hediff)this).pawn).SetFaction(factionOfMaster, (Pawn)null);
		}
	}
}
