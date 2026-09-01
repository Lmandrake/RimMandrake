using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Hediffs;

public class HediffCompProperties_Spreadable : HediffCompProperties
{
	public float radiusToSpread;

	public float severityToInfect;

	public float baseDiseaseContractChance;

	public IntRange spreadingTickInterval;

	public float socialInteractionTransmissionChance;

	public bool requiresLineOfSightToSpread;

	public List<RaceCategory> speciesCanCatch;

	public List<ThingDef> apparelsPreventingSpreading;

	public List<StatModifier> statsPreventingSpreading;

	public FleckDef fleckDefOnPawn;

	public IntRange fleckSpawnInterval;

	public Color fleckColor;

	public float fleckScale = 1f;

	public string spreadingMessageWarningKey;

	public HediffCompProperties_Spreadable()
	{
		base.compClass = typeof(HediffComp_Spreadable);
	}
}
