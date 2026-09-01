using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;
using Verse.Grammar;

namespace VEF.Storyteller;

public class QuestNode_Site : QuestNode
{
	public SlateRef<SitePartDef> sitePartDef;

	public SlateRef<IntRange> distanceRange;

	public SlateRef<bool> keepSiteWhenQuestActive;

	public virtual Predicate<Map, PlanetTile> TileValidator
	{
		get
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			_ = distanceRange;
			return delegate(Map map, PlanetTile tile)
			{
				//IL_0010: Unknown result type (might be due to invalid IL or missing references)
				//IL_0015: Unknown result type (might be due to invalid IL or missing references)
				//IL_001b: Unknown result type (might be due to invalid IL or missing references)
				//IL_001d: Unknown result type (might be due to invalid IL or missing references)
				//IL_0029: Unknown result type (might be due to invalid IL or missing references)
				//IL_0033: Unknown result type (might be due to invalid IL or missing references)
				if (map == null)
				{
					return true;
				}
				IntRange value = distanceRange.GetValue(QuestGen.slate);
				float num = Find.WorldGrid.ApproxDistanceInTiles(tile, map.Tile);
				return num >= (float)value.min && num <= (float)value.max;
			};
		}
	}

	public virtual List<BiomeDef> AllowedBiomes { get; }

	protected bool TryFindSiteTile(Map map, out PlanetTile tile)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		tile = PlanetTile.Invalid;
		if (map == null)
		{
			return false;
		}
		List<BiomeDef> allowedBiomes = AllowedBiomes;
		if (allowedBiomes != null && !Find.WorldGrid.Tiles.Any((SurfaceTile t) => allowedBiomes.Contains(((Tile)t).PrimaryBiome)))
		{
			allowedBiomes = null;
		}
		Slate slate = QuestGen.slate;
		IntRange value = distanceRange.GetValue(slate);
		TileQueryParams val = default(TileQueryParams);
		((TileQueryParams)(ref val))._002Ector(map.Tile, (float)value.min, (float)value.max, (LandmarkMode)0, true, (Hilliness)0, (Hilliness)0, true, true, true);
		TileQueryParams val2 = default(TileQueryParams);
		((TileQueryParams)(ref val2))._002Ector(map.Tile, 0f, float.MaxValue, (LandmarkMode)0, true, (Hilliness)0, (Hilliness)0, false, true, true);
		List<PlanetTile> list = ((PlanetLayer)Find.WorldGrid.Surface).FastTileFinder.Query(val, allowedBiomes, (List<LandmarkDef>)null, val2);
		if (!GenCollection.Empty<PlanetTile>(list))
		{
			tile = GenCollection.RandomElement<PlanetTile>((IEnumerable<PlanetTile>)list);
			return true;
		}
		tile = TileFinder.RandomSettlementTileFor((PlanetLayer)(object)Find.WorldGrid.Surface, (Faction)null, false, (Predicate<PlanetTile>)null);
		return ((PlanetTile)(ref tile)).Valid;
	}

	public static bool IsValidTile(PlanetTile tile, List<BiomeDef> allowedBiomes = null)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Invalid comparison between Unknown and I4
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		Tile tile2 = ((PlanetTile)(ref tile)).Tile;
		if (!tile2.PrimaryBiome.canBuildBase || !tile2.PrimaryBiome.implemented || (int)tile2.hilliness == 5)
		{
			return false;
		}
		if (Find.WorldObjects.AnyMapParentAt(tile) || Current.Game.FindMap(tile) != null || Find.WorldObjects.AnyWorldObjectOfDefAt(WorldObjectDefOf.AbandonedSettlement, tile))
		{
			return false;
		}
		if (allowedBiomes != null && allowedBiomes.Count > 0 && !allowedBiomes.Contains(tile2.PrimaryBiome))
		{
			return false;
		}
		return true;
	}

	protected override bool TestRunInt(Slate slate)
	{
		return true;
	}

	protected Site GenerateSite(float points, PlanetTile tile, Faction parentFaction, Slate slate, out string siteMapGeneratedSignal, out string siteMapRemovedSignal, bool failWhenMapRemoved = true, int timeoutTicks = 0)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Expected O, but got Unknown
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Expected O, but got Unknown
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		SitePartParams val = new SitePartParams
		{
			points = points,
			threatPoints = points
		};
		Site val2 = QuestGen_Sites.GenerateSite((IEnumerable<SitePartDefWithParams>)new List<SitePartDefWithParams>
		{
			new SitePartDefWithParams(sitePartDef.GetValue(slate), val)
		}, tile, parentFaction, false, (RulePack)null, (WorldObjectDef)null);
		((MapParent)val2).doorsAlwaysOpenForPlayerPawns = true;
		if (parentFaction != null && ((WorldObject)val2).Faction != parentFaction)
		{
			((WorldObject)val2).SetFaction(parentFaction);
		}
		QuestGen.slate.Set<Site>("site", val2, false);
		QuestGen_Sites.SpawnWorldObject(QuestGen.quest, (WorldObject)(object)val2, (List<ThingDef>)null, (string)null);
		if (timeoutTicks > 0)
		{
			QuestGen_Delay.WorldObjectTimeout(QuestGen.quest, (WorldObject)(object)val2, timeoutTicks, (string)null, (string)null, false, (List<string>)null, true);
		}
		siteMapRemovedSignal = QuestGenUtility.HardcodedSignalWithQuestID("site.MapRemoved");
		siteMapGeneratedSignal = QuestGenUtility.HardcodedSignalWithQuestID("site.MapGenerated");
		if (failWhenMapRemoved)
		{
			QuestGen_Signal.SignalPassActivable(QuestGen.quest, (Action)delegate
			{
				QuestGen_End.End(QuestGen.quest, (QuestEndOutcome)2, 0, (Faction)null, (string)null, (SignalListenMode)0, true, false);
			}, siteMapGeneratedSignal, siteMapRemovedSignal, (string)null, (IEnumerable<string>)null, (string)null, false);
		}
		if (keepSiteWhenQuestActive.GetValue(slate))
		{
			QuestGen.quest.AddPart((QuestPart)(object)new QuestPart_KeepSite
			{
				mapParent = (MapParent)(object)val2
			});
		}
		return val2;
	}

	protected bool PrepareQuest(out Map map, out float points, out PlanetTile tile, out Slate slate)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		slate = QuestGen.slate;
		points = slate.Get<float>("points", 0f, false);
		map = QuestGen_Get.GetMap(false, (int?)0, true);
		if (map == null)
		{
			tile = PlanetTile.Invalid;
			return false;
		}
		if (!TryFindSiteTile(map, out tile))
		{
			return false;
		}
		slate.Set<Faction>("playerFaction", Faction.OfPlayer, false);
		slate.Set<Map>("map", map, false);
		QuestGenUtility.RunAdjustPointsForDistantFight();
		return true;
	}

	protected override void RunInt()
	{
	}
}
