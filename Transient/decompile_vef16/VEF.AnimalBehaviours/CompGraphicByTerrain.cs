using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

[StaticConstructorOnStartup]
public class CompGraphicByTerrain : ThingComp
{
	public Graphic dessicatedGraphic;

	public string terrainName = "";

	public CompAnimalProduct animalProductComp;

	public string currentName = "";

	public int indexTerrain;

	public CompProperties_GraphicByTerrain Props => (CompProperties_GraphicByTerrain)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<string>(ref terrainName, "terrainName", "", false);
	}

	public override void CompTickInterval(int delta)
	{
		if (Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.changeGraphicsInterval, delta))
		{
			ChangeTheGraphics();
		}
		((ThingComp)this).CompTickInterval(delta);
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		_ = base.parent;
		animalProductComp = ThingCompUtility.TryGetComp<CompAnimalProduct>((Thing)(object)base.parent);
		ChangeTheGraphics();
	}

	public void RemoveHediffs(Pawn pawn)
	{
		if (Props.hediffToApply != null)
		{
			foreach (string item in Props.hediffToApply)
			{
				Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(DefDatabase<HediffDef>.GetNamed(item, true), false);
				if (firstHediffOfDef != null)
				{
					pawn.health.RemoveHediff(firstHediffOfDef);
				}
			}
		}
		if (Props.waterHediffToApply != "")
		{
			Hediff firstHediffOfDef2 = pawn.health.hediffSet.GetFirstHediffOfDef(DefDatabase<HediffDef>.GetNamed(Props.waterHediffToApply, true), false);
			if (firstHediffOfDef2 != null)
			{
				pawn.health.RemoveHediff(firstHediffOfDef2);
			}
		}
		if (Props.lowTemperatureHediffToApply != "")
		{
			Hediff firstHediffOfDef3 = pawn.health.hediffSet.GetFirstHediffOfDef(DefDatabase<HediffDef>.GetNamed(Props.lowTemperatureHediffToApply, true), false);
			if (firstHediffOfDef3 != null)
			{
				pawn.health.RemoveHediff(firstHediffOfDef3);
			}
		}
		if (Props.snowyHediffToApply != "")
		{
			Hediff firstHediffOfDef4 = pawn.health.hediffSet.GetFirstHediffOfDef(DefDatabase<HediffDef>.GetNamed(Props.snowyHediffToApply, true), false);
			if (firstHediffOfDef4 != null)
			{
				pawn.health.RemoveHediff(firstHediffOfDef4);
			}
		}
	}

	public void ChangeTheGraphics()
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_023b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_032c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0189: Unknown result type (might be due to invalid IL or missing references)
		//IL_027d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0358: Unknown result type (might be due to invalid IL or missing references)
		//IL_0379: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ab: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)base.parent).Map == null || !AnimalBehaviours_Settings.flagGraphicChanging)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		_ = val.ageTracker.CurKindLifeStage.bodyGraphicData.drawSize;
		if (Props.waterOverride && GridsUtility.GetTerrain(((Thing)base.parent).Position, ((Thing)base.parent).Map).IsWater)
		{
			currentName = "Water";
			if (terrainName != currentName)
			{
				terrainName = ((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName;
				RemoveHediffs(val);
				if (Props.waterHediffToApply != "")
				{
					val.health.AddHediff(DefDatabase<HediffDef>.GetNamed(Props.waterHediffToApply, true), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				if (Props.provideSeasonalItems && animalProductComp != null)
				{
					animalProductComp.seasonalItemIndex = Props.waterSeasonalItemsIndex;
				}
				val.Drawer.renderer.SetAllGraphicsDirty();
			}
			return;
		}
		if (Props.lowTemperatureOverride && ((Thing)base.parent).Map.mapTemperature.OutdoorTemp < (float)Props.temperatureThreshold)
		{
			currentName = "Cold";
			if (terrainName != currentName)
			{
				terrainName = ((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName;
				RemoveHediffs(val);
				if (Props.lowTemperatureHediffToApply != "")
				{
					val.health.AddHediff(DefDatabase<HediffDef>.GetNamed(Props.lowTemperatureHediffToApply, true), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				if (Props.provideSeasonalItems && animalProductComp != null)
				{
					animalProductComp.seasonalItemIndex = Props.lowTemperatureSeasonalItemsIndex;
				}
				val.Drawer.renderer.SetAllGraphicsDirty();
			}
			return;
		}
		if (Props.snowOverride && GridsUtility.GetSnowDepth(((Thing)base.parent).Position, ((Thing)base.parent).Map) > 0f)
		{
			currentName = "Snowy";
			if (terrainName != currentName)
			{
				terrainName = ((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName;
				RemoveHediffs(val);
				if (Props.snowyHediffToApply != "")
				{
					val.health.AddHediff(DefDatabase<HediffDef>.GetNamed(Props.snowyHediffToApply, true), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				if (Props.provideSeasonalItems && animalProductComp != null)
				{
					animalProductComp.seasonalItemIndex = Props.snowySeasonalItemsIndex;
				}
				val.Drawer.renderer.SetAllGraphicsDirty();
			}
			return;
		}
		List<string> terrains = Props.terrains;
		if (terrains != null && terrains.Contains(((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName))
		{
			indexTerrain = Props.terrains.IndexOf(((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName);
			currentName = ((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName;
			if (terrainName != currentName)
			{
				terrainName = ((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName;
				RemoveHediffs(val);
				if (Props.hediffToApply != null)
				{
					val.health.AddHediff(DefDatabase<HediffDef>.GetNamed(Props.hediffToApply[indexTerrain], true), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				if (Props.provideSeasonalItems && animalProductComp != null)
				{
					animalProductComp.seasonalItemIndex = Props.seasonalItemsIndexes[indexTerrain];
				}
				val.Drawer.renderer.SetAllGraphicsDirty();
			}
			return;
		}
		currentName = "Normal";
		if (terrainName != currentName)
		{
			terrainName = "Normal";
			RemoveHediffs(val);
			if (Props.provideSeasonalItems && animalProductComp != null)
			{
				animalProductComp.seasonalItemIndex = 0;
			}
			val.Drawer.renderer.SetAllGraphicsDirty();
		}
	}
}
