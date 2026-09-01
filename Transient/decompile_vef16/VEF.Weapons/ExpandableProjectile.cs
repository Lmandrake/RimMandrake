using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Weapons;

public class ExpandableProjectile : Bullet
{
	private int curDuration;

	public Vector3 startingPosition;

	private Vector3 prevPosition;

	private int curProjectileIndex;

	private int curProjectileFadeOutIndex;

	protected bool stopped;

	private float maxRange;

	private int prevTick;

	public bool doFinalAnimations;

	public bool pawnMoved;

	public Vector3? curPosition;

	protected bool customImpact;

	public List<Thing> hitThings;

	public override int UpdateRateTicks
	{
		get
		{
			if (((Thing)this).Spawned && Find.CurrentMap == ((Thing)this).Map)
			{
				return 1;
			}
			return Mathf.Max(Mathf.Min(def.tickDamageRate, TickFrameRate), 1);
		}
	}

	public virtual int DamageAmount => ((ThingDef)def).projectile.GetDamageAmount(((Projectile)this).equipment, (StringBuilder)null);

	public float ProgressPct => (float)curDuration / (float)def.lifeTimeDuration;

	public bool IsMoving
	{
		get
		{
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			if (!stopped && ((Thing)this).DrawPos != prevPosition)
			{
				prevPosition = ((Thing)this).DrawPos;
				return true;
			}
			return false;
		}
	}

	public ExpandableProjectileDef def => ((Thing)this).def as ExpandableProjectileDef;

	private Material ProjectileMat
	{
		get
		{
			if (!doFinalAnimations || def.lifeTimeDuration - curDuration > def.graphicData.MaterialsFadeOut.Length - 1)
			{
				Material result = def.graphicData.Materials[curProjectileIndex];
				if (prevTick != Find.TickManager.TicksAbs && Find.TickManager.TicksAbs - TickFrameRate >= prevTick)
				{
					if (def.graphicData.Materials.Length - 1 != curProjectileIndex)
					{
						curProjectileIndex++;
					}
					prevTick = Find.TickManager.TicksAbs;
				}
				return result;
			}
			Material result2 = def.graphicData.MaterialsFadeOut[curProjectileFadeOutIndex];
			if (prevTick != Find.TickManager.TicksAbs && Find.TickManager.TicksAbs - TickFrameRate >= prevTick)
			{
				if (def.graphicData.MaterialsFadeOut.Length - 1 != curProjectileFadeOutIndex)
				{
					curProjectileFadeOutIndex++;
				}
				prevTick = Find.TickManager.TicksAbs;
			}
			return result2;
		}
	}

	public int TickFrameRate
	{
		get
		{
			if (!doFinalAnimations)
			{
				return def.tickFrameRate;
			}
			if (def.finalTickFrameRate > 0)
			{
				return def.finalTickFrameRate;
			}
			return def.tickFrameRate;
		}
	}

	public bool LauncherIsVehicle
	{
		get
		{
			if (VanillaExpandedFramework_VehicleFramework_Turret_Patch.VFLoaded && VanillaExpandedFramework_VehicleFramework_Turret_Patch.VehicleType.IsAssignableFrom(((object)((Projectile)this).launcher).GetType()))
			{
				return true;
			}
			return false;
		}
	}

	public Vector3 StartingPosition
	{
		get
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_0089: Unknown result type (might be due to invalid IL or missing references)
			//IL_0076: Unknown result type (might be due to invalid IL or missing references)
			//IL_007b: Unknown result type (might be due to invalid IL or missing references)
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0083: Unknown result type (might be due to invalid IL or missing references)
			if (LauncherIsVehicle || ((Projectile)this).launcher == null)
			{
				return startingPosition;
			}
			CellRect val;
			if (!(((Projectile)this).launcher is Pawn))
			{
				val = GenAdj.OccupiedRect(((Projectile)this).launcher);
				startingPosition = ((CellRect)(ref val)).CenterVector3;
			}
			else if (!pawnMoved)
			{
				Thing launcher = ((Projectile)this).launcher;
				Pawn val2 = (Pawn)(object)((launcher is Pawn) ? launcher : null);
				if (val2 != null && !val2.Dead)
				{
					if (val2.pather.MovingNow)
					{
						pawnMoved = true;
					}
					else
					{
						val = GenAdj.OccupiedRect((Thing)(object)val2);
						startingPosition = ((CellRect)(ref val)).CenterVector3;
					}
				}
			}
			return startingPosition;
		}
	}

	public Vector3 CurPosition
	{
		get
		{
			//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_009d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0096: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			if (stopped)
			{
				if (curPosition.HasValue)
				{
					return curPosition.Value;
				}
				return ((Thing)this).DrawPos;
			}
			if (def.reachMaxRangeAlways)
			{
				Vector3 val = new Vector3(GenThing.TrueCenter(((Projectile)this).launcher).x, 0f, GenThing.TrueCenter(((Projectile)this).launcher).z);
				Vector3 drawPos = ((Thing)this).DrawPos;
				float num = Vector3.Distance(val, drawPos);
				if (maxRange - num < 0f)
				{
					if (curPosition.HasValue)
					{
						return curPosition.Value;
					}
					return ((Thing)this).DrawPos;
				}
				return ((Thing)this).DrawPos;
			}
			return ((Thing)this).DrawPos;
		}
	}

	public override Vector3 ExactPosition
	{
		get
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0097: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0064: Unknown result type (might be due to invalid IL or missing references)
			//IL_006c: Unknown result type (might be due to invalid IL or missing references)
			//IL_006d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Unknown result type (might be due to invalid IL or missing references)
			Vector3 val = ((Projectile)this).ExactPosition;
			Map map = ((Thing)this).Map;
			if (map != null && !GenGrid.InBounds(val, map))
			{
				Vector3 val2 = default(Vector3);
				((Vector3)(ref val2))._002Ector(((Projectile)this).origin.x, 0f, ((Projectile)this).origin.z);
				Vector3 val3 = new Vector3(val.x, 0f, val.z) - val2;
				Vector3 normalized = ((Vector3)(ref val3)).normalized;
				float num = 0.1f;
				Vector3 val4;
				while (true)
				{
					val4 = val - normalized * num;
					if (GenGrid.InBounds(val4, map))
					{
						break;
					}
					num += 0.1f;
				}
				val = val4;
			}
			return val;
		}
	}

	public override void Launch(Thing launcher, Vector3 origin, LocalTargetInfo usedTarget, LocalTargetInfo intendedTarget, ProjectileHitFlags hitFlags, bool preventFriendlyFire = false, Thing equipment = null, ThingDef targetCoverDef = null)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Launch(launcher, origin, usedTarget, intendedTarget, hitFlags, preventFriendlyFire, equipment, targetCoverDef);
		if (VanillaExpandedFramework_VehicleFramework_Turret_Patch.VFLoaded && VanillaExpandedFramework_VehicleFramework_Turret_Patch.currentFiringVehicleTurret != null)
		{
			Vector3 val = (Vector3)VanillaExpandedFramework_VehicleFramework_Turret_Patch.turretLocation.Invoke(VanillaExpandedFramework_VehicleFramework_Turret_Patch.currentFiringVehicleTurret, (object[])null);
			float num = (float)VanillaExpandedFramework_VehicleFramework_Turret_Patch.turretRotation.Invoke(VanillaExpandedFramework_VehicleFramework_Turret_Patch.currentFiringVehicleTurret, (object[])null);
			Vector2 val2 = VanillaExpandedFramework_VehicleFramework_Turret_Patch.aimPieOffset.Invoke(VanillaExpandedFramework_VehicleFramework_Turret_Patch.currentFiringVehicleTurret);
			startingPosition = val + Vector3Utility.RotatedBy(new Vector3(val2.x, 0.03658537f, val2.y), num);
		}
		if (def.reachMaxRangeAlways && equipment != null)
		{
			SetDestinationToMax(equipment);
		}
	}

	public void SetDestinationToMax(Thing equipment)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0100: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		maxRange = Mathf.Min((float)Mathf.Max(((Thing)this).Map.Size.x, ((Thing)this).Map.Size.z), GetMaxRange(equipment));
		Vector3 val = default(Vector3);
		((Vector3)(ref val))._002Ector(((Projectile)this).origin.x, 0f, ((Projectile)this).origin.z);
		Vector3 val2 = default(Vector3);
		((Vector3)(ref val2))._002Ector(((Projectile)this).destination.x, 0f, ((Projectile)this).destination.z);
		float num = Vector3.Distance(val, val2);
		float num2 = maxRange - num;
		Vector3 val3 = val2 - val;
		Vector3 normalized = ((Vector3)(ref val3)).normalized;
		int num3 = 1;
		while (true)
		{
			if ((float)num3 >= num2)
			{
				((Projectile)this).destination = ((Projectile)this).destination + normalized * (float)num3;
				break;
			}
			if (!GenGrid.InBounds(IntVec3Utility.ToIntVec3(((Projectile)this).destination + normalized * (float)num3), ((Thing)this).Map))
			{
				((Projectile)this).destination = ((Projectile)this).destination + normalized * (float)(num3 + 10);
				break;
			}
			num3++;
		}
		((Projectile)this).ticksToImpact = Mathf.CeilToInt(((Projectile)this).StartingTicksToImpact);
	}

	private float GetMaxRange(Thing equipment)
	{
		if (VanillaExpandedFramework_VehicleFramework_Turret_Patch.currentFiringVehicleTurret != null)
		{
			return (float)VanillaExpandedFramework_VehicleFramework_Turret_Patch.maxRangeInfo.Invoke(VanillaExpandedFramework_VehicleFramework_Turret_Patch.currentFiringVehicleTurret, (object[])null);
		}
		CompEquippable val = ThingCompUtility.TryGetComp<CompEquippable>(equipment);
		if (val != null)
		{
			return val.PrimaryVerb.verbProps.range;
		}
		throw new Exception("[VEF] Couldn't determine max range for " + ((Entity)this).Label);
	}

	public override void SpawnSetup(Map map, bool respawningAfterLoad)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		((ThingWithComps)this).SpawnSetup(map, respawningAfterLoad);
		if (!respawningAfterLoad)
		{
			IntVec3 position = ((Thing)this).Position;
			startingPosition = ((IntVec3)(ref position)).ToVector3Shifted();
			startingPosition.y = 0f;
		}
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		DrawProjectile();
	}

	public void DrawProjectile()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		Vector3 val = CurPosition;
		val.y = 0f;
		Vector3 val2 = StartingPosition;
		val2.y = 0f;
		Vector3 val3 = default(Vector3);
		((Vector3)(ref val3))._002Ector(((Projectile)this).destination.x, ((Projectile)this).destination.y, ((Projectile)this).destination.z);
		val3.y = 0f;
		Quaternion val4 = Quaternion.LookRotation(val - val2);
		Vector3 pos = (val2 + val) / 2f;
		pos.y = 10f;
		pos = AdjustPos(val, val2, pos);
		float num = Vector3.Distance(val2, val) * def.totalSizeScale;
		float num2 = Vector3.Distance(val2, val3);
		float num3 = num / num2;
		Vector3 val5 = default(Vector3);
		((Vector3)(ref val5))._002Ector(num * def.widthScaleFactor * num3, 0f, num * def.heightScaleFactor);
		Matrix4x4 val6 = default(Matrix4x4);
		((Matrix4x4)(ref val6)).SetTRS(pos, val4, val5);
		Graphics.DrawMesh(MeshPool.plane10, val6, ProjectileMat, 0);
		DrawProjectileInternal(pos);
	}

	protected virtual void DrawProjectileInternal(Vector3 pos)
	{
	}

	private Vector3 AdjustPos(Vector3 currentPos, Vector3 startingPosition, Vector3 pos)
	{
		//IL_013a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0126: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		if (((Projectile)this).launcher is Pawn)
		{
			if (!LauncherIsVehicle)
			{
				if (((Projectile)this).launcher.Rotation == Rot4.West)
				{
					Vector3 startingPositionOffset = def.startingPositionOffset;
					startingPositionOffset.x = 0f - startingPositionOffset.x;
					pos += Quaternion.Euler(0f, Vector3Utility.AngleFlat(startingPosition - currentPos), 0f) * startingPositionOffset;
				}
				else if (((Projectile)this).launcher.Rotation == Rot4.East)
				{
					pos += Quaternion.Euler(0f, Vector3Utility.AngleFlat(startingPosition - currentPos), 0f) * def.startingPositionOffset;
				}
				else if (((Projectile)this).launcher.Rotation == Rot4.South || ((Projectile)this).launcher.Rotation == Rot4.North)
				{
					Vector3 startingPositionOffset2 = def.startingPositionOffset;
					startingPositionOffset2.x = 0f;
					pos += Quaternion.Euler(0f, Vector3Utility.AngleFlat(startingPosition - currentPos), 0f) * startingPositionOffset2;
				}
			}
		}
		else
		{
			pos += Quaternion.Euler(0f, Vector3Utility.AngleFlat(startingPosition - currentPos), 0f) * def.startingPositionOffset;
		}
		return pos;
	}

	public HashSet<IntVec3> MakeProjectileLine(Vector3 start, Vector3 end, Map map)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		ShootLine val = default(ShootLine);
		((ShootLine)(ref val))._002Ector(IntVec3Utility.ToIntVec3(start), IntVec3Utility.ToIntVec3(end));
		IEnumerable<IntVec3> points = ((ShootLine)(ref val)).Points();
		Vector3 val2 = CurPosition;
		val2.y = 0f;
		Vector3 val3 = StartingPosition;
		val3.y = 0f;
		Vector3 pos = (val3 + val2) / 2f;
		pos.y = 10f;
		pos = AdjustPos(val2, val3, pos);
		float num = Vector3.Distance(val3, val2) * def.totalSizeScale;
		float num2 = Vector3.Distance(val3, val2);
		float num3 = num / num2;
		float width = num * def.widthScaleFactor * num3;
		float height = num * def.heightScaleFactor;
		IntVec3 centerOfLine = IntVec3Utility.ToIntVec3(pos);
		IntVec3 startPosition = IntVec3Utility.ToIntVec3(StartingPosition);
		IntVec3 endPosition = IntVec3Utility.ToIntVec3(CurPosition);
		return GetCellsToDamage(start, points, width, height, centerOfLine, startPosition, endPosition);
	}

	protected virtual HashSet<IntVec3> GetCellsToDamage(Vector3 start, IEnumerable<IntVec3> points, float width, float height, IntVec3 centerOfLine, IntVec3 startPosition, IntVec3 endPosition)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_014f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0182: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		HashSet<IntVec3> hashSet = new HashSet<IntVec3>();
		if (points.Any())
		{
			foreach (IntVec3 cell in GenRadial.RadialCellsAround(IntVec3Utility.ToIntVec3(start), height, true))
			{
				if (!(IntVec3Utility.DistanceTo(startPosition, cell) > def.minDistanceToAffect))
				{
					continue;
				}
				int num = IntVec3Utility.DistanceToSquared(startPosition, endPosition);
				int num2 = IntVec3Utility.DistanceToSquared(cell, endPosition);
				int num3 = IntVec3Utility.DistanceToSquared(centerOfLine, endPosition);
				if (!(def.wideAtStart ? (num >= num2) : (num3 >= num2)))
				{
					continue;
				}
				IntVec3 val = GenCollection.MinBy<IntVec3, int>(points, (Func<IntVec3, int>)((IntVec3 x) => IntVec3Utility.DistanceToSquared(x, cell)));
				if (width / height * def.arcSize > (float)IntVec3Utility.DistanceToSquared(val, cell))
				{
					hashSet.Add(cell);
					if (def.debugMode)
					{
						((Thing)this).Map.debugDrawer.FlashCell(cell, 0.5f, (string)null, 50);
					}
				}
			}
			foreach (IntVec3 point in points)
			{
				float num4 = IntVec3Utility.DistanceTo(startPosition, point);
				if (num4 > def.minDistanceToAffect && num4 <= IntVec3Utility.DistanceTo(startPosition, endPosition))
				{
					if (def.debugMode)
					{
						((Thing)this).Map.debugDrawer.FlashCell(point, 0.5f, (string)null, 50);
					}
					hashSet.Add(point);
				}
			}
		}
		return hashSet;
	}

	protected virtual void StopMotion(Thing hitThing = null, bool reachedMaxDistance = false, bool blockedByShield = false)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_0188: Unknown result type (might be due to invalid IL or missing references)
		//IL_018f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c8: Unknown result type (might be due to invalid IL or missing references)
		if (stopped)
		{
			return;
		}
		stopped = true;
		curPosition = (((Projectile)this).destination = ((Thing)this).DrawPos);
		Map map = ((Thing)this).Map;
		if (!(map != null && hitThing == null && reachedMaxDistance) || blockedByShield)
		{
			return;
		}
		SoundDef impactSound = def.impactSound;
		if (impactSound != null)
		{
			SoundStarter.PlayOneShot(impactSound, SoundInfo.op_Implicit(new TargetInfo(((Thing)this).Position, map, false)));
		}
		if (def.triggerWaterSplashes && GridsUtility.GetTerrain(((Thing)this).Position, map).takeSplashes)
		{
			FleckMaker.WaterSplash(((Projectile)this).ExactPosition, map, Mathf.Min(Mathf.Sqrt((float)DamageAmount), 1f), 4f);
		}
		else if (def.impactFleck != null && GenView.ShouldSpawnMotesAt(((Projectile)this).ExactPosition, ((Thing)this).Map, true))
		{
			float num = ((FloatRange)(ref def.impactFleckAngle)).RandomInRange;
			if (def.impactFleckUsesProjectileAngle)
			{
				num += Vector3Utility.AngleToFlat(((Projectile)this).destination, startingPosition) - 90f;
			}
			FleckCreationData dataStatic = FleckMaker.GetDataStatic(((Projectile)this).ExactPosition, map, def.impactFleck, 1f);
			dataStatic.rotation = ((FloatRange)(ref def.impactFleckRotation)).RandomInRange;
			dataStatic.rotationRate = ((FloatRange)(ref def.impactFleckRotationRate)).RandomInRange;
			dataStatic.velocityAngle = num;
			dataStatic.velocitySpeed = ((FloatRange)(ref def.impactFleckSpeed)).RandomInRange;
			FleckCreationData val = dataStatic;
			map.flecks.CreateFleck(val);
		}
		if (def.filthOnUninterrupted != null && Rand.Chance(def.filthOnUninterruptedChance) && !GridsUtility.Filled(((Thing)this).Position, ((Thing)this).Map))
		{
			FilthMaker.TryMakeFilth(((Thing)this).Position, ((Thing)this).Map, def.filthOnUninterrupted, ((IntRange)(ref def.filthOnUninterruptedCount)).RandomInRange, (FilthSourceFlags)0, true);
		}
	}

	protected override void TickInterval(int delta)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).TickInterval(delta);
		if (Gen.IsHashIntervalTick((Thing)(object)this, def.tickDamageRate, delta))
		{
			foreach (IntVec3 item in MakeProjectileLine(StartingPosition, ((Thing)this).DrawPos, ((Thing)this).Map))
			{
				if (!((Thing)this).Destroyed)
				{
					DoDamage(item);
				}
			}
		}
		if (!doFinalAnimations && (!IsMoving || pawnMoved))
		{
			doFinalAnimations = true;
			int num = def.lifeTimeDuration - def.graphicData.MaterialsFadeOut.Length;
			if (num > curDuration)
			{
				curDuration = num;
			}
			if (!def.reachMaxRangeAlways && pawnMoved)
			{
				StopMotion();
			}
		}
		if (!Gen.IsHashIntervalTick((Thing)(object)this, TickFrameRate, delta) || def.lifeTimeDuration <= 0)
		{
			return;
		}
		curDuration++;
		if (curDuration > def.lifeTimeDuration)
		{
			if (!stopped)
			{
				StopMotion(null, reachedMaxDistance: true);
			}
			((Thing)this).Destroy((DestroyMode)0);
		}
		else if (def.stopMotionOnFadeoutStarted && !stopped && curDuration > def.lifeTimeDuration - def.graphicData.MaterialsFadeOut.Length - 1)
		{
			StopMotion(null, reachedMaxDistance: true);
		}
	}

	public virtual bool IsDamagable(Thing t)
	{
		if (t.def != def && t != ((Projectile)this).launcher)
		{
			if (!t.def.useHitPoints)
			{
				return t is Pawn;
			}
			return true;
		}
		return false;
	}

	public virtual void DoDamage(IntVec3 pos)
	{
	}

	protected override void Impact(Thing hitThing, bool blockedByShield = false)
	{
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Expected O, but got Unknown
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Expected O, but got Unknown
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_022d: Unknown result type (might be due to invalid IL or missing references)
		if (stopped)
		{
			return;
		}
		if (hitThings == null)
		{
			hitThings = new List<Thing>();
		}
		if (def.dealsDamageOnce && hitThings.Contains(hitThing))
		{
			return;
		}
		Map map = ((Thing)this).Map;
		IntVec3 position = ((Thing)this).Position;
		NotifyImpact(hitThing, map, position);
		if (hitThing != null && (!def.disableVanillaDamageMethod || customImpact))
		{
			int damageAmount = DamageAmount;
			hitThings.Add(hitThing);
			BattleLogEntry_RangedImpact val = ((((Projectile)this).equipmentDef != null) ? new BattleLogEntry_RangedImpact(((Projectile)this).launcher, hitThing, ((LocalTargetInfo)(ref ((Projectile)this).intendedTarget)).Thing, ((Projectile)this).equipmentDef, (ThingDef)(object)def, ((Projectile)this).targetCoverDef) : new BattleLogEntry_RangedImpact(((Projectile)this).launcher, hitThing, ((LocalTargetInfo)(ref ((Projectile)this).intendedTarget)).Thing, ThingDef.Named("Gun_Autopistol"), (ThingDef)(object)def, ((Projectile)this).targetCoverDef));
			Find.BattleLog.Add((LogEntry)(object)val);
			DamageDef damageDef = ((ThingDef)def).projectile.damageDef;
			float num = damageAmount;
			float armorPenetration = ((Projectile)this).ArmorPenetration;
			Quaternion exactRotation = ((Projectile)this).ExactRotation;
			DamageInfo val2 = default(DamageInfo);
			((DamageInfo)(ref val2))._002Ector(damageDef, num, armorPenetration, ((Quaternion)(ref exactRotation)).eulerAngles.y, ((Projectile)this).launcher, (BodyPartRecord)null, ((Projectile)this).equipmentDef, (SourceCategory)0, ((LocalTargetInfo)(ref ((Projectile)this).intendedTarget)).Thing, true, true, (QualityCategory)2, true, false);
			hitThing.TakeDamage(val2).AssociateWithLog((LogEntry_DamageResult)(object)val);
			Pawn val3 = (Pawn)(object)((hitThing is Pawn) ? hitThing : null);
			if (val3 != null && val3.stances != null && val3.BodySize <= ((ThingDef)def).projectile.stoppingPower + 0.001f)
			{
				val3.stances.stagger.StaggerFor(95, 0.17f);
			}
			if (((ThingDef)def).projectile.extraDamages != null)
			{
				DamageInfo val4 = default(DamageInfo);
				foreach (ExtraDamage extraDamage in ((ThingDef)def).projectile.extraDamages)
				{
					if (Rand.Chance(extraDamage.chance))
					{
						DamageDef obj = extraDamage.def;
						float amount = extraDamage.amount;
						float num2 = extraDamage.AdjustedArmorPenetration();
						exactRotation = ((Projectile)this).ExactRotation;
						((DamageInfo)(ref val4))._002Ector(obj, amount, num2, ((Quaternion)(ref exactRotation)).eulerAngles.y, ((Projectile)this).launcher, (BodyPartRecord)null, ((Projectile)this).equipmentDef, (SourceCategory)0, ((LocalTargetInfo)(ref ((Projectile)this).intendedTarget)).Thing, true, true, (QualityCategory)2, true, false);
						hitThing.TakeDamage(val4).AssociateWithLog((LogEntry_DamageResult)(object)val);
					}
				}
			}
		}
		if (hitThing != null && !stopped && ShouldStopMotionWhenHitting(hitThing))
		{
			StopMotion(hitThing, reachedMaxDistance: false, blockedByShield);
		}
	}

	private void NotifyImpact(Thing hitThing, Map map, IntVec3 position)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		BulletImpactData val = default(BulletImpactData);
		val.bullet = (Bullet)(object)this;
		val.hitThing = hitThing;
		val.impactPosition = position;
		BulletImpactData val2 = val;
		try
		{
			if (hitThing != null)
			{
				hitThing.Notify_BulletImpactNearby(val2);
			}
		}
		catch
		{
		}
		for (int i = 0; i < 9; i++)
		{
			IntVec3 val3 = position + GenRadial.RadialPattern[i];
			if (!GenGrid.InBounds(val3, map))
			{
				continue;
			}
			List<Thing> thingList = GridsUtility.GetThingList(val3, map);
			for (int j = 0; j < thingList.Count; j++)
			{
				if (thingList[j] != hitThing)
				{
					try
					{
						thingList[j].Notify_BulletImpactNearby(val2);
					}
					catch
					{
					}
				}
			}
		}
	}

	protected virtual bool ShouldStopMotionWhenHitting(Thing hitThing)
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Invalid comparison between Unknown and I4
		if (def.stopWhenHit && (def.stopAtBuildingWithCover <= 0f || hitThing.def.fillPercent >= def.stopAtBuildingWithCover))
		{
			return true;
		}
		if (def.stopWhenNaturalRockHit && (int)hitThing.def.category == 3)
		{
			if (hitThing.def.building.isNaturalRock)
			{
				goto IL_008c;
			}
			ThingDef unsmoothedThing = hitThing.def.building.unsmoothedThing;
			if (unsmoothedThing != null)
			{
				BuildingProperties building = unsmoothedThing.building;
				if (building != null && building.isNaturalRock)
				{
					goto IL_008c;
				}
			}
		}
		if (def.stopWhenZeroDamageAfterHit && DamageAmount <= 0)
		{
			return true;
		}
		if (def.stopWhenHitAt.Contains(((Def)hitThing.def).defName))
		{
			return true;
		}
		return false;
		IL_008c:
		return true;
	}

	public override void ExposeData()
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).ExposeData();
		Scribe_Values.Look<Vector3>(ref startingPosition, "startingPosition", default(Vector3), false);
		Scribe_Values.Look<bool>(ref doFinalAnimations, "doFinalAnimations", false, false);
		Scribe_Values.Look<bool>(ref pawnMoved, "pawnMoved", false, false);
		Scribe_Values.Look<int>(ref curDuration, "curDuration", 0, false);
		Scribe_Values.Look<int>(ref curProjectileIndex, "curProjectileIndex", 0, false);
		Scribe_Values.Look<int>(ref curProjectileFadeOutIndex, "curProjectileFadeOutIndex", 0, false);
		Scribe_Values.Look<int>(ref prevTick, "prevTick", 0, false);
		Scribe_Values.Look<Vector3>(ref prevPosition, "prevPosition", default(Vector3), false);
		Scribe_Values.Look<bool>(ref stopped, "stopped", false, false);
		Scribe_Values.Look<Vector3?>(ref curPosition, "curPosition", (Vector3?)null, false);
		Scribe_Values.Look<float>(ref maxRange, "maxRange", 0f, false);
		Scribe_Collections.Look<Thing>(ref hitThings, "hitThings", (LookMode)3, Array.Empty<object>());
	}
}
