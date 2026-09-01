using System;
using System.Buffers;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Plants;

public class Plant_Blooming : Plant
{
	public int realAge;

	public bool isBlooming;

	public bool hasWeeds;

	public bool alreadyBloomed;

	public bool plantAwaitingExtraction;

	public bool plantAwaitingWeedRemoval;

	public int lowTempBloomStopCounter = 15;

	public const int lowTempBloomStopCounterBase = 15;

	public int itemProducedCounter;

	public int filthProducedCounter;

	public BloomingPlantExtension cachedExtension;

	public Graphic cachedGraphic;

	private MapComponent_BloomingPlants cachedMapComp;

	private CompGlowerBlooming cachedGlowingComp;

	public int cachedDeadlyTemperature = -200;

	public List<string> randomWeedMaterials = new List<string> { "UI/Overlays/Weeds/WeedsA", "UI/Overlays/Weeds/WeedsB", "UI/Overlays/Weeds/WeedsC" };

	public string randomWeedMaterial;

	private Graphic BloomGraphic
	{
		get
		{
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			if (cachedGraphic == null)
			{
				string text = GetExtension.bloomGraphicPath;
				if (GetExtension.alternateBloomGraphicPath != "" && PlantsMapComp.alternateBloomingTextures)
				{
					text = GetExtension.alternateBloomGraphicPath;
				}
				cachedGraphic = GraphicDatabase.Get(((Thing)this).def.graphicData.graphicClass, text, ((BuildableDef)((Thing)this).def).graphic.Shader, ((Thing)this).def.graphicData.drawSize, ((Thing)this).def.graphicData.color, ((Thing)this).def.graphicData.colorTwo, (string)null);
			}
			return cachedGraphic;
		}
	}

	public BloomingPlantExtension GetExtension
	{
		get
		{
			if (cachedExtension == null)
			{
				cachedExtension = ((Def)((Thing)this).def).GetModExtension<BloomingPlantExtension>();
			}
			return cachedExtension;
		}
	}

	public MapComponent_BloomingPlants PlantsMapComp
	{
		get
		{
			if (cachedMapComp == null)
			{
				cachedMapComp = ((Thing)this).Map.GetComponent<MapComponent_BloomingPlants>();
			}
			return cachedMapComp;
		}
	}

	public override Graphic Graphic
	{
		get
		{
			if (((Plant)this).Growth >= 1f && isBlooming && !((Plant)this).LeaflessNow)
			{
				return BloomGraphic;
			}
			return ((Plant)this).Graphic;
		}
	}

	public int SeasonAsInt(Season season)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Expected I4, but got Unknown
		return (season - 1) switch
		{
			0 => 0, 
			1 => 1, 
			2 => 2, 
			3 => 3, 
			_ => 1, 
		};
	}

	public override void SpawnSetup(Map map, bool respawningAfterLoad)
	{
		((Plant)this).SpawnSetup(map, respawningAfterLoad);
		if (!respawningAfterLoad)
		{
			cachedDeadlyTemperature = Rand.Range(GetExtension.DeadlyColdTemperature, GetExtension.DeadlyColdTemperature - 8);
			if (GetExtension.itemProducedWhenBlooming != null)
			{
				itemProducedCounter = GetExtension.longTicksPerItemProduced;
			}
			if (GetExtension.filthProducedWhenBlooming != null)
			{
				filthProducedCounter = GetExtension.longTicksPerFilthProduced;
			}
			randomWeedMaterial = GenCollection.RandomElement<string>((IEnumerable<string>)randomWeedMaterials);
		}
		cachedGlowingComp = ((ThingWithComps)this).GetComp<CompGlowerBlooming>();
	}

	protected override void TickInterval(int delta)
	{
		((Plant)this).TickInterval(delta);
		if (((Plant)this).Growth >= 1f)
		{
			realAge += delta * 2000;
		}
		CheckIfBlooming();
	}

	public override void TickLong()
	{
		((Plant)this).TickLong();
		if (((Plant)this).Growth >= 1f)
		{
			realAge += 2000;
		}
		CheckIfBlooming();
	}

	public void CheckIfBlooming()
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_02aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b0: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).Map == null)
		{
			return;
		}
		if (GenLocalDate.DayOfYear(((Thing)this).Map) == 1)
		{
			alreadyBloomed = false;
		}
		float temperature = GridsUtility.GetTemperature(((Thing)this).Position, ((Thing)this).Map);
		float num = ((Thing)this).Map.glowGrid.GroundGlowAt(((Thing)this).Position, false, false);
		if (temperature < (float)cachedDeadlyTemperature)
		{
			((Thing)this).TakeDamage(new DamageInfo(DamageDefOf.Rotting, (float)GetExtension.DamageWhenBelowDeadlyTemp, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
		if (temperature < (float)GetExtension.BloomTemperatureMin || temperature > (float)GetExtension.BloomTemperatureMax)
		{
			lowTempBloomStopCounter--;
			if (lowTempBloomStopCounter < 0)
			{
				TryEndBloom();
				lowTempBloomStopCounter = 15;
			}
		}
		else
		{
			lowTempBloomStopCounter = 15;
		}
		if (GetExtension.BloomLightMax < 1f && num > GetExtension.BloomLightMax)
		{
			TryEndBloom();
		}
		if (DetectBloomingByDate())
		{
			if (!isBlooming)
			{
				TryDoBloom();
			}
		}
		else if (isBlooming)
		{
			TryEndBloom();
		}
		if (!isBlooming)
		{
			return;
		}
		if (GetExtension.itemProducedWhenBlooming != null)
		{
			itemProducedCounter--;
			if (itemProducedCounter <= 0)
			{
				Thing obj = ThingMaker.MakeThing(GetExtension.itemProducedWhenBlooming, (ThingDef)null);
				obj.stackCount = GetExtension.itemProducedAmount;
				GenPlace.TryPlaceThing(obj, ((Thing)this).Position, ((Thing)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
				itemProducedCounter = GetExtension.longTicksPerItemProduced;
			}
		}
		if (GetExtension.filthProducedWhenBlooming != null)
		{
			filthProducedCounter--;
			if (filthProducedCounter <= 0)
			{
				IntVec3 val = default(IntVec3);
				for (int i = 0; i < ((IntRange)(ref GetExtension.filthProducedAmount)).RandomInRange; i++)
				{
					CellFinder.TryFindRandomReachableNearbyCell(((Thing)this).Position, ((Thing)this).Map, GetExtension.filthProducedRadius, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val, 999999);
					FilthMaker.TryMakeFilth(val, ((Thing)this).Map, GetExtension.filthProducedWhenBlooming, 1, (FilthSourceFlags)0, true);
				}
				filthProducedCounter = GetExtension.longTicksPerFilthProduced;
			}
		}
		if (GetExtension.hediffWhenBlooming == null)
		{
			return;
		}
		foreach (Pawn item in ((Thing)this).Map.mapPawns.AllPawnsSpawned)
		{
			if (item != null && !item.IsAnimal && !item.Dead && !item.Downed && (item.IsColonist || !GetExtension.hediffOnlyAffectsColonists) && IntVec3Utility.DistanceTo(((Thing)item).PositionHeld, ((Thing)this).PositionHeld) <= GetExtension.hediffRadius)
			{
				GiveOrUpdateHediff(item);
			}
		}
	}

	public bool DetectBloomingByDate()
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Invalid comparison between Unknown and I4
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Invalid comparison between Unknown and I4
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).Map == null)
		{
			return false;
		}
		Season val = GenDate.Season((long)Find.TickManager.TicksAbs, Find.WorldGrid.LongLatOf(((Thing)this).Map.Tile));
		if ((int)val == 5 || (int)val == 6)
		{
			int num = GenLocalDate.DayOfYear(((Thing)this).Map);
			int num2 = SeasonAsInt(GetExtension.BloomSeasonStart) * 15 + (GetExtension.BloomDayStart - 1);
			int num3 = SeasonAsInt(GetExtension.BloomSeasonStop) * 15 + (GetExtension.BloomDayEnd - 1);
			if (num2 < num3)
			{
				if (num >= num2)
				{
					return num < num3;
				}
				return false;
			}
			if (num < num2)
			{
				return num < num3;
			}
			return true;
		}
		int day = GenLocalDate.DayOfQuadrum(((Thing)this).Map) + 1;
		int num4 = OrdinalPosition(val, day);
		int num5 = OrdinalPosition(GetExtension.BloomSeasonStart, GetExtension.BloomDayStart);
		int num6 = OrdinalPosition(GetExtension.BloomSeasonStop, GetExtension.BloomDayEnd);
		if (num5 < num6)
		{
			if (num4 >= num5)
			{
				return num4 < num6;
			}
			return false;
		}
		if (num4 < num5)
		{
			return num4 < num6;
		}
		return true;
	}

	private int OrdinalPosition(Season season, int day)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return SeasonAsInt(season) * 15 + (day - 1);
	}

	private void GiveOrUpdateHediff(Pawn target)
	{
		Hediff val = target.health.hediffSet.GetFirstHediffOfDef(GetExtension.hediffWhenBlooming, false);
		if (val == null)
		{
			val = target.health.AddHediff(GetExtension.hediffWhenBlooming, target.health.hediffSet.GetBrain(), (DamageInfo?)null, (DamageResult)null);
			val.Severity = GetExtension.hediffSeverity;
		}
		HediffComp_Disappears val2 = HediffUtility.TryGetComp<HediffComp_Disappears>(val);
		if (val2 == null)
		{
			Log.ErrorOnce("CompCauseHediff_AoE has a hediff in props which does not have a HediffComp_Disappears", 78945945);
		}
		else
		{
			val2.ticksToDisappear = 4000;
		}
	}

	public void TryDoBloom()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		float temperature = GridsUtility.GetTemperature(((Thing)this).Position, ((Thing)this).Map);
		if (!isBlooming && !alreadyBloomed && temperature >= (float)GetExtension.BloomTemperatureMin && temperature <= (float)GetExtension.BloomTemperatureMax && (GetExtension.BloomLightMax == 1f || ((Thing)this).Map.glowGrid.GroundGlowAt(((Thing)this).Position, false, false) <= GetExtension.BloomLightMax))
		{
			if (!GetExtension.CanBloomAgain)
			{
				alreadyBloomed = true;
			}
			isBlooming = true;
			((Thing)this).Map.mapDrawer.MapMeshDirty(((Thing)this).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things));
			if (cachedGlowingComp != null)
			{
				((CompGlower)cachedGlowingComp).UpdateLit(((Thing)this).Map);
			}
		}
	}

	public void TryEndBloom()
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		if (isBlooming)
		{
			isBlooming = false;
			((Thing)this).Map.mapDrawer.MapMeshDirty(((Thing)this).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things));
			if (cachedGlowingComp != null)
			{
				((CompGlower)cachedGlowingComp).UpdateLit(((Thing)this).Map);
			}
		}
	}

	public override void ExposeData()
	{
		((Plant)this).ExposeData();
		Scribe_Values.Look<int>(ref realAge, "realAge", 0, false);
		Scribe_Values.Look<bool>(ref isBlooming, "isBlooming", false, false);
		Scribe_Values.Look<bool>(ref hasWeeds, "hasWeeds", false, false);
		Scribe_Values.Look<bool>(ref alreadyBloomed, "alreadyBloomed", false, false);
		Scribe_Values.Look<int>(ref lowTempBloomStopCounter, "lowTempBloomStopCounter", 15, false);
		Scribe_Values.Look<int>(ref itemProducedCounter, "itemProducedCounter", 0, false);
		Scribe_Values.Look<int>(ref filthProducedCounter, "filthProducedCounter", 0, false);
		Scribe_Values.Look<string>(ref randomWeedMaterial, "randomWeedMaterial", "", false);
	}

	public override string GetInspectString()
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Invalid comparison between Unknown and I4
		//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ec: Invalid comparison between Unknown and I4
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0207: Unknown result type (might be due to invalid IL or missing references)
		//IL_020c: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0236: Unknown result type (might be due to invalid IL or missing references)
		//IL_022a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0247: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0311: Unknown result type (might be due to invalid IL or missing references)
		//IL_0267: Unknown result type (might be due to invalid IL or missing references)
		//IL_0334: Unknown result type (might be due to invalid IL or missing references)
		//IL_028f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
		if (((Thing)this).def.plant.showGrowthInInspectPane)
		{
			if ((int)((Plant)this).LifeStage == 1)
			{
				stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("PercentGrowth", NamedArgument.op_Implicit(((Plant)this).GrowthPercentString))));
				stringBuilder.Append(TaggedString.op_Implicit(Translator.Translate("GrowthRate") + ": " + GenText.ToStringPercent(((Plant)this).GrowthRate)));
				if (!((Plant)this).Blighted)
				{
					string[] array = ArrayPool<string>.Shared.Rent(4);
					int count2 = 0;
					if (((Plant)this).Resting)
					{
						AddCondition(array, ref count2, TaggedString.op_Implicit(Translator.Translate("PlantResting")));
					}
					if (!((Plant)this).HasEnoughLightToGrow)
					{
						AddCondition(array, ref count2, TaggedString.op_Implicit(Translator.Translate("PlantNeedsLightLevel") + " " + GenText.ToStringPercent(((Thing)this).def.plant.growMinGlow)));
					}
					float growthRateFactor_Temperature = ((Plant)this).GrowthRateFactor_Temperature;
					if (growthRateFactor_Temperature < 0.99f)
					{
						if (Mathf.Approximately(growthRateFactor_Temperature, 0f) || !PlantUtility.GrowthSeasonNow(((Thing)this).Position, ((Thing)this).Map, ((Thing)this).def))
						{
							AddCondition(array, ref count2, TaggedString.op_Implicit(Translator.Translate("OutOfIdealTemperatureRangeNotGrowing")));
						}
						else
						{
							AddCondition(array, ref count2, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("OutOfIdealTemperatureRange", NamedArgument.op_Implicit(Mathf.Max(1, Mathf.RoundToInt(growthRateFactor_Temperature * 100f)).ToString()))));
						}
					}
					if (((Plant)this).GrowthRateFactor_Drought < 0.99f)
					{
						AddCondition(array, ref count2, ((Def)GameConditionDefOf.Drought).label);
					}
					string text = string.Join(", ", array, 0, count2);
					ArrayPool<string>.Shared.Return(array);
					if (!GenText.NullOrEmpty(text))
					{
						stringBuilder.Append(" (").Append(text).Append(')');
					}
				}
				stringBuilder.AppendLine();
			}
			else if ((int)((Plant)this).LifeStage == 2)
			{
				stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_RealAge", NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod(realAge, true, false, true, true, false)))));
				stringBuilder.AppendLine(TaggedString.op_Implicit(((Plant)this).HarvestableNow ? Translator.Translate("ReadyToHarvest") : Translator.Translate("Mature")));
				float temperature = GridsUtility.GetTemperature(((Thing)this).Position, ((Thing)this).Map);
				if (isBlooming)
				{
					stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("VPE_FlowerIsBlooming")));
				}
				else if (temperature < (float)GetExtension.BloomTemperatureMin)
				{
					stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("VPE_TempTooLowForBlooming")));
				}
				else if (temperature > (float)GetExtension.BloomTemperatureMax)
				{
					stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("VPE_TempTooHighForBlooming")));
				}
			}
			if (((Plant)this).DyingBecauseExposedToLight)
			{
				stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("DyingBecauseExposedToLight")));
			}
			if (((Plant)this).DyingBecauseExposedToVacuum)
			{
				stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("DyingBecauseExposedToVacuum")));
			}
			if (((Plant)this).DyingBecauseOfTerrainTags)
			{
				stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("DyingBecauseOfTerrain")));
			}
			if (((Plant)this).Blighted)
			{
				stringBuilder.AppendLine(string.Format("{0} ({1})", Translator.Translate("Blighted"), GenText.ToStringPercent(((Plant)this).Blight.Severity)));
			}
		}
		string text2 = ((ThingWithComps)this).InspectStringPartsFromComps();
		if (!GenText.NullOrEmpty(text2))
		{
			stringBuilder.Append(text2);
		}
		return GenText.TrimEndNewlines(stringBuilder.ToString());
		static void AddCondition(string[] conditions, ref int count, string condition)
		{
			if (count < conditions.Length)
			{
				conditions[count++] = condition;
			}
			else
			{
				Log.Error("Too many conditions for plant growth inspect string");
			}
		}
	}

	public override IEnumerable<Gizmo> GetGizmos()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		if (DebugSettings.ShowDevGizmos && !GetExtension.ImmuneToWeeds)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = "Increase age 1 year",
				action = delegate
				{
					//IL_0025: Unknown result type (might be due to invalid IL or missing references)
					if (((Plant)this).Growth >= 1f)
					{
						realAge += 3600000;
					}
					else
					{
						Messages.Message(TaggedString.op_Implicit(Translator.Translate("VPE_MustBeGrown")), LookTargets.op_Implicit((Thing)(object)this), MessageTypeDefOf.RejectInput, (Quest)null, false);
					}
				}
			};
			if (!hasWeeds)
			{
				yield return (Gizmo)new Command_Action
				{
					defaultLabel = "Cause weeds",
					action = delegate
					{
						hasWeeds = true;
					}
				};
			}
		}
		if ((int)((Plant)this).LifeStage == 2 && !hasWeeds && !GetExtension.CantBeExtracted)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VPE_ExtractFlower")),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VPE_ExtractFlower_Desc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Gizmo/ExtractFlower", true),
				hotKey = KeyBindingDefOf.Misc6,
				Disabled = plantAwaitingExtraction,
				action = delegate
				{
					if (((Thing)this).Map != null && PlantsMapComp != null)
					{
						PlantsMapComp.AddObjectToMap((Thing)(object)this);
						plantAwaitingExtraction = true;
					}
				}
			};
			if (plantAwaitingExtraction)
			{
				yield return (Gizmo)new Command_Action
				{
					defaultLabel = TaggedString.op_Implicit(Translator.Translate("VPE_CancelExtractFlower")),
					defaultDesc = TaggedString.op_Implicit(Translator.Translate("VPE_CancelExtractFlower_Desc")),
					icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Designators/Cancel", true),
					hotKey = KeyBindingDefOf.Misc7,
					action = delegate
					{
						if (((Thing)this).Map != null && PlantsMapComp != null)
						{
							PlantsMapComp.RemoveObjectFromMap((Thing)(object)this);
							plantAwaitingExtraction = false;
						}
					}
				};
			}
		}
		if (!hasWeeds)
		{
			yield break;
		}
		yield return (Gizmo)new Command_Action
		{
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("VPE_RemoveWeeds")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("VPE_RemoveWeeds_Desc")),
			icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Gizmo/RemoveWeeds_Gizmo", true),
			hotKey = KeyBindingDefOf.Misc8,
			Disabled = plantAwaitingWeedRemoval,
			action = delegate
			{
				if (((Thing)this).Map != null && PlantsMapComp != null)
				{
					PlantsMapComp.AddWeedToMap((Thing)(object)this);
					plantAwaitingWeedRemoval = true;
				}
			}
		};
		if (!plantAwaitingWeedRemoval)
		{
			yield break;
		}
		yield return (Gizmo)new Command_Action
		{
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("VPE_CancelWeedRemoval")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("VPE_CancelWeedRemoval_Desc")),
			icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Designators/Cancel", true),
			hotKey = KeyBindingDefOf.Misc7,
			action = delegate
			{
				if (((Thing)this).Map != null && PlantsMapComp != null)
				{
					PlantsMapComp.RemoveWeedFromMap((Thing)(object)this);
					plantAwaitingWeedRemoval = false;
				}
			}
		};
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		((ThingWithComps)this).DrawAt(drawLoc, flip);
		if (((Thing)this).Map != null)
		{
			Vector3 drawPos = ((Thing)this).DrawPos;
			drawPos.y = Altitudes.AltitudeFor((AltitudeLayer)39) + 0.18181819f;
			MapComponent_BloomingPlants plantsMapComp = PlantsMapComp;
			if (plantsMapComp != null && plantsMapComp.flowersOrderedForExtraction_InMap.Contains((Thing)(object)this))
			{
				float num = ((float)Math.Sin((Time.realtimeSinceStartup + 397f * (float)(((Thing)this).thingIDNumber % 571)) * 4f) + 1f) * 0.5f;
				num = 0.3f + num * 0.7f;
				Material val = FadedMaterialPool.FadedVersionOf(MaterialPool.MatFrom("UI/Gizmo/ExtractFlowerOverlay", ShaderDatabase.MetaOverlay), num);
				Graphics.DrawMesh(MeshPool.plane08, drawPos, Quaternion.identity, val, 0);
			}
			if (hasWeeds)
			{
				Material val2 = FadedMaterialPool.FadedVersionOf(MaterialPool.MatFrom(randomWeedMaterial, ShaderDatabase.MetaOverlay), 0.8f);
				Graphics.DrawMesh(MeshPool.plane08, drawPos, Quaternion.identity, val2, 0);
			}
		}
	}

	public override IEnumerable<StatDrawEntry> SpecialDisplayStats()
	{
		foreach (StatDrawEntry item in _003C_003En__1())
		{
			yield return item;
		}
		yield return new StatDrawEntry(StatCategoryDefOf.Basics, TaggedString.op_Implicit(Translator.Translate("VPE_AgeBeautyModifier")), "+" + GetExtension.AgeBeautyModifier, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_AgeBeautyModifier_Desc", NamedArgument.op_Implicit(GetExtension.MaxAgeBeautyModifier))), 4170, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		yield return new StatDrawEntry(StatCategoryDefOf.Basics, TaggedString.op_Implicit(Translator.Translate("VPE_BloomBeautyModifier")), "x" + GetExtension.BloomBeautyModifier, TaggedString.op_Implicit(Translator.Translate("VPE_BloomBeautyModifier_Desc")), 4171, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		yield return new StatDrawEntry(StatCategoryDefOf.Basics, TaggedString.op_Implicit(Translator.Translate("VPE_BloomingPeriod")), ((object)(Season)(ref GetExtension.BloomSeasonStart)/*cast due to .constrained prefix*/).ToString() + " " + GetExtension.BloomDayStart + " to " + ((object)(Season)(ref GetExtension.BloomSeasonStop)/*cast due to .constrained prefix*/).ToString() + " " + GetExtension.BloomDayEnd, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_BloomingPeriod_Desc", NamedArgument.op_Implicit(GetExtension.MaxAgeBeautyModifier))), 4172, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		if (GetExtension.BloomTemperatureMin != -250)
		{
			yield return new StatDrawEntry(StatCategoryDefOf.Basics, TaggedString.op_Implicit(Translator.Translate("VPE_BloomTemperatureMin")), GenText.ToStringTemperature((float)GetExtension.BloomTemperatureMin, "F0"), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_BloomTemperatureMin_Desc", NamedArgument.op_Implicit(GetExtension.CanBloomAgain ? Translator.Translate("VPE_CanBloom") : Translator.Translate("VPE_CantBloom")))), 4173, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		}
		if (GetExtension.BloomTemperatureMax != 999)
		{
			yield return new StatDrawEntry(StatCategoryDefOf.Basics, TaggedString.op_Implicit(Translator.Translate("VPE_BloomTemperatureMax")), GenText.ToStringTemperature((float)GetExtension.BloomTemperatureMax, "F0"), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_BloomTemperatureMax_Desc", NamedArgument.op_Implicit(GetExtension.CanBloomAgain ? Translator.Translate("VPE_CanBloom") : Translator.Translate("VPE_CantBloom")))), 4173, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		}
		if (GetExtension.DeadlyColdTemperature != -250)
		{
			yield return new StatDrawEntry(StatCategoryDefOf.Basics, TaggedString.op_Implicit(Translator.Translate("VPE_DeadlyColdTemperature")), GenText.ToStringTemperature((float)GetExtension.DeadlyColdTemperature, "F0"), TaggedString.op_Implicit(Translator.Translate("VPE_DeadlyColdTemperature_Desc")), 4174, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		}
		yield return new StatDrawEntry(StatCategoryDefOf.Basics, TaggedString.op_Implicit(Translator.Translate("VPE_LeaflessBeauty")), GetExtension.LeaflessBeauty.ToString(), TaggedString.op_Implicit(Translator.Translate("VPE_LeaflessBeauty_Desc")), 3001, (string)null, (IEnumerable<Hyperlink>)null, false, false);
	}

	public override void DeSpawn(DestroyMode mode = 0)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).Map != null && PlantsMapComp != null)
		{
			PlantsMapComp.RemoveObjectFromMap((Thing)(object)this);
		}
		((Plant)this).DeSpawn(mode);
	}

	public override void Destroy(DestroyMode mode = 0)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)this).Map != null && PlantsMapComp != null)
		{
			PlantsMapComp.RemoveObjectFromMap((Thing)(object)this);
		}
		((ThingWithComps)this).Destroy(mode);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((Plant)this).GetGizmos();
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<StatDrawEntry> _003C_003En__1()
	{
		return ((Plant)this).SpecialDisplayStats();
	}
}
