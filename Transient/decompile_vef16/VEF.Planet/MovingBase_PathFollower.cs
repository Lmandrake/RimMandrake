using System;
using System.Collections.Generic;
using System.Text;
using HarmonyLib;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Planet;

public class MovingBase_PathFollower : IExposable
{
	private MovingBase movingBase;

	private bool moving;

	private bool paused;

	public PlanetTile nextTile = PlanetTile.Invalid;

	public PlanetTile previousTileForDrawingIfInDoubt = PlanetTile.Invalid;

	public float nextTileCostLeft;

	public float nextTileCostTotal = 1f;

	private PlanetTile destTile;

	public WorldPath curPath;

	public PlanetTile lastPathedTargetTile;

	public const int MaxMoveTicks = 30000;

	private const int MaxCheckAheadNodes = 20;

	private const int MinCostWalk = 50;

	private const int MinCostAmble = 60;

	public const float DefaultPathCostToPayPerTick = 1f;

	public const int FinalNoRestPushMaxDurationTicks = 10000;

	private static readonly FieldRef<WorldPathPool, List<WorldPath>> pathsField = AccessTools.FieldRefAccess<WorldPathPool, List<WorldPath>>("paths");

	public PlanetTile Destination => destTile;

	public bool Moving
	{
		get
		{
			if (moving)
			{
				return ((WorldObject)movingBase).Spawned;
			}
			return false;
		}
	}

	public bool MovingNow
	{
		get
		{
			if (moving && !paused)
			{
				return true;
			}
			return false;
		}
	}

	public bool Paused
	{
		get
		{
			if (Moving)
			{
				return paused;
			}
			return false;
		}
		set
		{
			if (value != paused)
			{
				if (!value)
				{
					paused = false;
				}
				else if (!Moving)
				{
					Log.Error("Tried to pause movingBase movement of " + Gen.ToStringSafe<MovingBase>(movingBase) + " but it's not moving.");
				}
				else
				{
					paused = true;
				}
			}
		}
	}

	public MovingBase_PathFollower(MovingBase movingBase)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		this.movingBase = movingBase;
	}

	public void ExposeData()
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Invalid comparison between Unknown and I4
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		Scribe_Values.Look<bool>(ref moving, "moving", true, false);
		Scribe_Values.Look<bool>(ref paused, "paused", false, false);
		Scribe_Values.Look<PlanetTile>(ref nextTile, "nextTile", PlanetTile.op_Implicit(0), false);
		Scribe_Values.Look<PlanetTile>(ref previousTileForDrawingIfInDoubt, "previousTileForDrawingIfInDoubt", PlanetTile.op_Implicit(0), false);
		Scribe_Values.Look<float>(ref nextTileCostLeft, "nextTileCostLeft", 0f, false);
		Scribe_Values.Look<float>(ref nextTileCostTotal, "nextTileCostTotal", 0f, false);
		Scribe_Values.Look<PlanetTile>(ref destTile, "destTile", PlanetTile.op_Implicit(0), false);
		if ((int)Scribe.mode == 4 && (int)Current.ProgramState != 0 && moving && !StartPath(destTile, repathImmediately: true, resetPauseStatus: false))
		{
			StopDead();
		}
	}

	public bool StartPath(PlanetTile destTile, bool repathImmediately = false, bool resetPauseStatus = true)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		pathsField.Invoke(Find.WorldPathPool).Clear();
		if (resetPauseStatus)
		{
			paused = false;
		}
		if (!IsPassable(((WorldObject)movingBase).Tile) && !TryRecoverFromUnwalkablePosition())
		{
			return false;
		}
		if (moving && curPath != null && this.destTile == destTile)
		{
			return true;
		}
		if (!movingBase.CanReach(destTile))
		{
			PatherFailed();
			return false;
		}
		this.destTile = destTile;
		if (!((PlanetTile)(ref nextTile)).Valid || !IsNextTilePassable())
		{
			nextTile = ((WorldObject)movingBase).Tile;
			nextTileCostLeft = 0f;
			previousTileForDrawingIfInDoubt = PlanetTile.Invalid;
		}
		if (AtDestinationPosition())
		{
			PatherArrived();
			return true;
		}
		if (curPath != null)
		{
			curPath.ReleaseToPool();
		}
		curPath = null;
		moving = true;
		if (repathImmediately && TrySetNewPath() && nextTileCostLeft <= 0f && moving)
		{
			TryEnterNextPathTile();
		}
		return true;
	}

	public void StopDead()
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		if (curPath != null)
		{
			curPath.ReleaseToPool();
		}
		curPath = null;
		moving = false;
		paused = false;
		nextTile = ((WorldObject)movingBase).Tile;
		previousTileForDrawingIfInDoubt = PlanetTile.Invalid;
		nextTileCostLeft = 0f;
	}

	public void PatherTick(int delta)
	{
		if (!paused)
		{
			if (nextTileCostLeft > 0f)
			{
				nextTileCostLeft -= CostToPayThisTick(delta);
			}
			else if (moving)
			{
				TryEnterNextPathTile();
			}
		}
	}

	public void Notify_Teleported_Int()
	{
		StopDead();
	}

	private bool IsPassable(PlanetTile tile)
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		return !Find.World.Impassable(tile);
	}

	public bool IsNextTilePassable()
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		return IsPassable(nextTile);
	}

	private bool TryRecoverFromUnwalkablePosition()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		PlanetTile val = default(PlanetTile);
		if (GenWorldClosest.TryFindClosestTile(((WorldObject)movingBase).Tile, (Predicate<PlanetTile>)((PlanetTile t) => IsPassable(t)), ref val, int.MaxValue, true))
		{
			Log.Warning(string.Concat(movingBase, " on unwalkable tile ", ((WorldObject)movingBase).Tile, ". Teleporting to ", val));
			((WorldObject)movingBase).Tile = val;
			return true;
		}
		Log.Error(string.Concat(movingBase, " on unwalkable tile ", ((WorldObject)movingBase).Tile, ". Could not find walkable position nearby. Removed."));
		((WorldObject)movingBase).Destroy();
		return false;
	}

	private void PatherArrived()
	{
		StopDead();
	}

	private void PatherFailed()
	{
		StopDead();
	}

	private void TryEnterNextPathTile()
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		if (!IsNextTilePassable())
		{
			PatherFailed();
			return;
		}
		((WorldObject)movingBase).Tile = nextTile;
		if (!NeedNewPath() || TrySetNewPath())
		{
			if (AtDestinationPosition())
			{
				PatherArrived();
			}
			else if (curPath.NodesLeftCount == 0)
			{
				Log.Error(string.Concat(movingBase, " ran out of path nodes. Force-arriving."));
				PatherArrived();
			}
			else
			{
				SetupMoveIntoNextTile();
			}
		}
	}

	private void SetupMoveIntoNextTile()
	{
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		if (curPath.NodesLeftCount < 2)
		{
			Log.Error(string.Concat(movingBase, " at ", ((WorldObject)movingBase).Tile, " ran out of path nodes while pathing to ", destTile, "."));
			PatherFailed();
			return;
		}
		nextTile = curPath.ConsumeNextNode();
		previousTileForDrawingIfInDoubt = PlanetTile.Invalid;
		if (Find.World.Impassable(nextTile))
		{
			Log.Error(string.Concat(movingBase, " entering ", nextTile, " which is unwalkable."));
		}
		int num = CostToMove(((WorldObject)movingBase).Tile, nextTile);
		nextTileCostTotal = num;
		nextTileCostLeft = num;
	}

	private int CostToMove(PlanetTile start, PlanetTile end)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		return CostToMove(movingBase, start, end, null);
	}

	public static int CostToMove(MovingBase movingBase, PlanetTile start, PlanetTile end, int? ticksAbs = null)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		return CostToMove(movingBase.TicksPerMove, start, end, ticksAbs);
	}

	public static int CostToMove(int movingBaseTicksPerMove, PlanetTile start, PlanetTile end, int? ticksAbs = null, bool perceivedStatic = false, StringBuilder explanation = null, string movingBaseTicksPerMoveExplanation = null, bool immobile = false)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01da: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		if (start == end)
		{
			return 0;
		}
		if (explanation != null)
		{
			explanation.Append(movingBaseTicksPerMoveExplanation);
			explanation.AppendLine();
		}
		StringBuilder stringBuilder = ((explanation != null) ? new StringBuilder() : null);
		float num = ((!perceivedStatic || explanation != null) ? WorldPathGrid.CalculatedMovementDifficultyAt(end, perceivedStatic, ticksAbs, stringBuilder) : Find.WorldPathGrid.PerceivedMovementDifficultyAt(end));
		float roadMovementDifficultyMultiplier = Find.WorldGrid.GetRoadMovementDifficultyMultiplier(start, end, stringBuilder);
		if (explanation != null && !immobile)
		{
			explanation.AppendLine();
			explanation.Append(TaggedString.op_Implicit(Translator.Translate("TileMovementDifficulty") + ":"));
			explanation.AppendLine();
			explanation.Append(GenText.Indented(stringBuilder.ToString(), "  "));
			explanation.AppendLine();
			explanation.Append("  = " + (num * roadMovementDifficultyMultiplier).ToString("0.#"));
		}
		int num2 = (int)((float)movingBaseTicksPerMove * num * roadMovementDifficultyMultiplier);
		num2 = Mathf.Clamp(num2, 1, 30000);
		if (explanation != null)
		{
			explanation.AppendLine();
			if (immobile)
			{
				explanation.Append(TaggedString.op_Implicit(Translator.Translate("EncumberedMerchantGuildTilesPerDayTip")));
			}
			else
			{
				explanation.AppendLine();
				explanation.Append(TaggedString.op_Implicit(Translator.Translate("FinalMerchantGuildMovementSpeed") + ":"));
				int num3 = Mathf.CeilToInt((float)num2 / 1f);
				explanation.AppendLine();
				explanation.Append(TaggedString.op_Implicit("  " + (60000f / (float)movingBaseTicksPerMove).ToString("0.#") + " / " + (num * roadMovementDifficultyMultiplier).ToString("0.#") + " = " + (60000f / (float)num3).ToString("0.#") + " " + Translator.Translate("TilesPerDay")));
			}
		}
		return num2;
	}

	public static bool IsValidFinalPushDestination(PlanetTile tile)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		List<WorldObject> allWorldObjects = Find.WorldObjects.AllWorldObjects;
		for (int i = 0; i < allWorldObjects.Count; i++)
		{
			if (allWorldObjects[i].Tile == tile && !(allWorldObjects[i] is MovingBase))
			{
				return true;
			}
		}
		return false;
	}

	private float CostToPayThisTick(int delta)
	{
		float num = delta;
		if (num < nextTileCostTotal / 30000f)
		{
			num = nextTileCostTotal / 30000f;
		}
		return num;
	}

	private bool TrySetNewPath()
	{
		WorldPath val = GenerateNewPath();
		if (!val.Found)
		{
			PatherFailed();
			return false;
		}
		if (curPath != null)
		{
			curPath.ReleaseToPool();
		}
		curPath = val;
		return true;
	}

	private WorldPath GenerateNewPath()
	{
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		pathsField.Invoke(Find.WorldPathPool)?.Clear();
		PlanetTile val = ((moving && ((PlanetTile)(ref nextTile)).Valid && IsNextTilePassable()) ? nextTile : ((WorldObject)movingBase).Tile);
		lastPathedTargetTile = destTile;
		PlanetTile tile = ((WorldObject)movingBase).Tile;
		WorldPath val2 = ((PlanetTile)(ref tile)).Layer.Pather.FindPath(val, destTile, (Caravan)null, (Func<float, bool>)null);
		if (val2.Found && val != ((WorldObject)movingBase).Tile)
		{
			if (val2.NodesLeftCount >= 2 && val2.Peek(1) == ((WorldObject)movingBase).Tile)
			{
				val2.ConsumeNextNode();
				if (moving)
				{
					previousTileForDrawingIfInDoubt = nextTile;
					nextTile = ((WorldObject)movingBase).Tile;
					nextTileCostLeft = nextTileCostTotal - nextTileCostLeft;
				}
			}
			else
			{
				val2.AddNodeAtStart(((WorldObject)movingBase).Tile);
			}
		}
		return val2;
	}

	private bool AtDestinationPosition()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		return ((WorldObject)movingBase).Tile == destTile;
	}

	private bool NeedNewPath()
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		if (!moving)
		{
			return false;
		}
		if (curPath == null || !curPath.Found || curPath.NodesLeftCount == 0)
		{
			return true;
		}
		for (int i = 0; i < 20 && i < curPath.NodesLeftCount; i++)
		{
			PlanetTile val = curPath.Peek(i);
			if (Find.World.Impassable(val))
			{
				return true;
			}
		}
		return false;
	}
}
