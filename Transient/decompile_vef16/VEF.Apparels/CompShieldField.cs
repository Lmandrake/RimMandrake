using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using VEF.AnimalBehaviours;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace VEF.Apparels;

[StaticConstructorOnStartup]
public class CompShieldField : ThingComp, PawnGizmoProvider
{
	[HarmonyPatch(typeof(Pawn), "SpawnSetup")]
	private class SpawnSetup_Patch
	{
		public static void Postfix(Pawn __instance)
		{
			Pawn_ApparelTracker apparel = __instance.apparel;
			if (((apparel != null) ? apparel.WornApparel : null) == null)
			{
				return;
			}
			foreach (Apparel item in __instance.apparel.WornApparel)
			{
				((ThingWithComps)item).GetComp<CompShieldField>()?.Initialize();
			}
		}
	}

	public bool initialized;

	public bool active;

	public Dictionary<Thing, int> affectedThings = new Dictionary<Thing, int>();

	protected IntVec3 lastCachedCells = IntVec3.Invalid;

	protected float lastCachedShieldRadius = -1f;

	public HashSet<IntVec3> coveredCells;

	public HashSet<IntVec3> scanCells;

	private const int CacheUpdateInterval = 15;

	private const float EdgeCellRadius = 5f;

	private const float EnergyLossPerDamage = 0.033f;

	private int lastTimeActivated;

	private int lastTimeDisabled;

	private int lastTimeDisarmed;

	private static readonly Material BaseBubbleMat = MaterialPool.MatFrom("Other/ShieldBubble", ShaderDatabase.MoteGlow);

	private static readonly MaterialPropertyBlock MatPropertyBlock = new MaterialPropertyBlock();

	private List<Thing> affectedThingsKeysWorkingList;

	private List<int> affectedThingsValuesWorkingList;

	private CompPowerTrader cachedPowerComp;

	private bool checkedPowerComp;

	private float energy;

	private Vector3 impactAngleVect;

	private int lastAbsorbDamageTick;

	private int shieldBuffer;

	private int ticksToRecharge;

	private bool toggleIsActive = true;

	public static Dictionary<Map, List<CompShieldField>> listerShieldGensByMaps = new Dictionary<Map, List<CompShieldField>>();

	private float _cachedEnergyGainPerTick;

	private float _cachedMaxEnergy;

	private float _cachedShieldRadius;

	private bool _isCacheValid;

	private Sustainer sustainer;

	public Thing HostThing
	{
		get
		{
			ThingWithComps parent = base.parent;
			Apparel val = (Apparel)(object)((parent is Apparel) ? parent : null);
			if (val != null && val.Wearer != null)
			{
				return (Thing)(object)val.Wearer;
			}
			return (Thing)(object)base.parent;
		}
	}

	public Faction HostFaction
	{
		get
		{
			Thing hostThing = HostThing;
			if (hostThing == null)
			{
				return null;
			}
			return hostThing.Faction;
		}
	}

	public bool Indestructible => Props.shieldEnergyMaxStat == null;

	public float Energy
	{
		get
		{
			return energy;
		}
		set
		{
			energy = Mathf.Clamp(value, 0f, MaxEnergy);
			if (energy == 0f)
			{
				Notify_EnergyDepleted();
			}
		}
	}

	public CompProperties_ShieldField Props => base.props as CompProperties_ShieldField;

	public float EnergyGainPerTick
	{
		get
		{
			if (!_isCacheValid)
			{
				UpdateStatsCache();
			}
			return _cachedEnergyGainPerTick;
		}
	}

	public float MaxEnergy
	{
		get
		{
			if (!_isCacheValid)
			{
				UpdateStatsCache();
			}
			return _cachedMaxEnergy;
		}
	}

	public float ShieldRadius
	{
		get
		{
			if (!_isCacheValid)
			{
				UpdateStatsCache();
			}
			return _cachedShieldRadius;
		}
	}

	public LocalTargetInfo TargetCurrentlyAimingAt => LocalTargetInfo.Invalid;

	public float TargetPriorityFactor => 1f;

	public IEnumerable<Thing> ThingsWithinRadius
	{
		get
		{
			Thing hostThing = HostThing;
			Map map = ((hostThing != null) ? hostThing.MapHeld : null);
			if (map == null || coveredCells == null)
			{
				yield break;
			}
			foreach (IntVec3 coveredCell in coveredCells)
			{
				List<Thing> thingList = map.thingGrid.ThingsListAtFast(coveredCell);
				for (int i = 0; i < thingList.Count; i++)
				{
					yield return thingList[i];
				}
			}
		}
	}

	public IEnumerable<Thing> ThingsWithinScanArea
	{
		get
		{
			Thing hostThing = HostThing;
			Map map = ((hostThing != null) ? hostThing.MapHeld : null);
			if (map == null || scanCells == null)
			{
				yield break;
			}
			Vector3 hostCenter = Vector3Utility.Yto0(GenThing.TrueCenter(HostThing));
			float shieldRadius = ShieldRadius;
			foreach (IntVec3 scanCell in scanCells)
			{
				List<Thing> thingList = map.thingGrid.ThingsListAtFast(scanCell);
				for (int i = 0; i < thingList.Count; i++)
				{
					Thing val = thingList[i];
					if (Vector3.Distance(hostCenter, Vector3Utility.Yto0(GenThing.TrueCenter(val))) <= shieldRadius)
					{
						yield return val;
					}
				}
			}
		}
	}

	private bool CanFunction
	{
		get
		{
			if ((!Props.toggleable || toggleIsActive) && (PowerTraderComp == null || PowerTraderComp.PowerOn) && !BreakdownableUtility.IsBrokenDown((Thing)(object)base.parent))
			{
				return !(HostThing is Apparel);
			}
			return false;
		}
	}

	private CompPowerTrader PowerTraderComp
	{
		get
		{
			if (!checkedPowerComp)
			{
				cachedPowerComp = base.parent.GetComp<CompPowerTrader>();
				checkedPowerComp = true;
			}
			return cachedPowerComp;
		}
	}

	public bool IsApparel => base.parent is Apparel;

	private bool IsBuiltIn => !IsApparel;

	public bool ManuallyActivated
	{
		get
		{
			if (lastTimeActivated > 0)
			{
				return Find.TickManager.TicksGame - lastTimeActivated < Props.workingTimeTicks;
			}
			return false;
		}
	}

	public bool ReactivatedThisTick => Find.TickManager.TicksGame - lastAbsorbDamageTick == Props.cooldownTicks;

	public static IEnumerable<CompShieldField> ListerShieldGensActiveIn(Map map)
	{
		if (!listerShieldGensByMaps.TryGetValue(map, out var list))
		{
			yield break;
		}
		int count = list.Count;
		for (int i = 0; i < count; i++)
		{
			CompShieldField compShieldField = list[i];
			if (compShieldField.active && (compShieldField.Energy > 0f || compShieldField.Indestructible))
			{
				yield return compShieldField;
			}
		}
	}

	private void UpdateStatsCache()
	{
		if (Props.rechargeRateStat != null)
		{
			_cachedEnergyGainPerTick = StatExtension.GetStatValue((Thing)(object)base.parent, Props.rechargeRateStat, true, -1) / 60f;
		}
		if (Props.shieldEnergyMaxStat != null)
		{
			_cachedMaxEnergy = StatExtension.GetStatValue((Thing)(object)base.parent, Props.shieldEnergyMaxStat, true, -1);
		}
		_cachedShieldRadius = StatExtension.GetStatValue((Thing)(object)base.parent, Props.shieldRadiusStat, true, -1);
		_isCacheValid = true;
	}

	public (HashSet<Thing> thingsWithinRadius, List<Thing> projectilesWithinScanArea) GetThingsInAreas()
	{
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		HashSet<Thing> hashSet = new HashSet<Thing>();
		List<Thing> list = new List<Thing>();
		Thing hostThing = HostThing;
		Map val = ((hostThing != null) ? hostThing.MapHeld : null);
		if (val == null)
		{
			return (thingsWithinRadius: hashSet, projectilesWithinScanArea: list);
		}
		if (scanCells != null && coveredCells != null)
		{
			Vector3 val2 = Vector3Utility.Yto0(GenThing.TrueCenter(HostThing));
			float shieldRadius = ShieldRadius;
			foreach (Thing item in val.listerThings.ThingsInGroup((ThingRequestGroup)60))
			{
				if (scanCells.Contains(item.Position) && Vector3.Distance(val2, Vector3Utility.Yto0(GenThing.TrueCenter(item))) <= shieldRadius)
				{
					list.Add(item);
				}
			}
			if (GenCollection.Any<Thing>(list))
			{
				foreach (IntVec3 coveredCell in coveredCells)
				{
					List<Thing> list2 = val.thingGrid.ThingsListAtFast(coveredCell);
					GenCollection.AddRange<Thing>(hashSet, list2);
				}
			}
		}
		return (thingsWithinRadius: hashSet, projectilesWithinScanArea: list);
	}

	public void AbsorbDamage(float amount, DamageDef def, Thing source)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		AbsorbDamage(amount, def, Vector3Utility.AngleFlat(GenThing.TrueCenter(HostThing) - GenThing.TrueCenter(source)));
	}

	public void AbsorbDamage(float amount, DamageDef def, float angle)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ce: Unknown result type (might be due to invalid IL or missing references)
		SoundStarter.PlayOneShot(SoundDefOf.EnergyShield_AbsorbDamage, SoundInfo.op_Implicit(new TargetInfo(HostThing.Position, HostThing.Map, false)));
		impactAngleVect = Vector3Utility.HorizontalVectorFromAngle(angle);
		Vector3 val = GenThing.TrueCenter(HostThing) + Vector3Utility.RotatedBy(impactAngleVect, 180f) * (ShieldRadius / 2f);
		float num = Mathf.Min(10f, 2f + amount / 10f);
		FleckMaker.Static(GenThing.TrueCenter(HostThing), HostThing.Map, FleckDefOf.ExplosionFlash, 12f);
		int num2 = (int)num;
		for (int i = 0; i < num2; i++)
		{
			FleckMaker.ThrowDustPuff(val, HostThing.Map, Rand.Range(0.8f, 1.2f));
		}
		if (!Indestructible)
		{
			float num3 = amount * EnergyLossMultiplier(def) * 0.033f;
			Energy -= num3;
			if (Rand.Chance(num3 * Props.shortCircuitChancePerEnergyLost))
			{
				CellRect val2 = GenAdj.OccupiedRect(HostThing);
				GenExplosion.DoExplosion(((CellRect)(ref val2)).RandomCell, HostThing.Map, 1.9f, DamageDefOf.Flame, (Thing)null, -1, -1f, (SoundDef)null, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
			}
		}
		if (Props.disarmedByEmpForTicks != -1 && def == DamageDefOf.EMP)
		{
			BreakShield(new DamageInfo(def, amount, 0f, angle, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
		lastAbsorbDamageTick = Find.TickManager.TicksGame;
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		coveredCells = null;
		scanCells = null;
		if (listerShieldGensByMaps.TryGetValue(map, out var value))
		{
			value.Remove(this);
			if (value.Count == 0)
			{
				listerShieldGensByMaps.Remove(map);
			}
		}
		((ThingComp)this).PostDeSpawn(map, mode);
	}

	public override void CompDrawWornExtras()
	{
		((ThingComp)this).CompDrawWornExtras();
		if (IsApparel)
		{
			Draw();
		}
	}

	public override void PostDraw()
	{
		((ThingComp)this).PostDraw();
		if (IsBuiltIn)
		{
			Draw();
		}
	}

	private void Draw()
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_015e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0163: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		if (!active || (!(Energy > 0f) && !Indestructible))
		{
			return;
		}
		float num = ShieldRadius * 2f;
		Color val = Props.shieldColour;
		if (!Indestructible)
		{
			float healthPercent = Energy / MaxEnergy;
			num *= Mathf.Lerp(0.9f, 1.1f, healthPercent);
			if (Props.healthColorPoints != null && GenCollection.Any<HealthColorPoint>(Props.healthColorPoints))
			{
				HealthColorPoint healthColorPoint = GenCollection.FirstOrDefault<HealthColorPoint>(Props.healthColorPoints, (Predicate<HealthColorPoint>)((HealthColorPoint p) => p.healthPercent >= healthPercent));
				HealthColorPoint healthColorPoint2 = Props.healthColorPoints.LastOrDefault((HealthColorPoint p) => p.healthPercent < healthPercent);
				if (healthColorPoint == null)
				{
					float num2 = Mathf.InverseLerp(healthColorPoint2.healthPercent, 1f, healthPercent);
					val = Color.Lerp(healthColorPoint2.color, Props.shieldColour, num2);
				}
				else if (healthColorPoint2 == null)
				{
					val = healthColorPoint.color;
				}
				else
				{
					float num3 = Mathf.InverseLerp(healthColorPoint2.healthPercent, healthColorPoint.healthPercent, healthPercent);
					val = Color.Lerp(healthColorPoint2.color, healthColorPoint.color, num3);
				}
			}
		}
		Vector3 val2 = GenThing.TrueCenter(HostThing);
		val2.y = Altitudes.AltitudeFor((AltitudeLayer)28);
		int num4 = Find.TickManager.TicksGame - lastAbsorbDamageTick;
		if (num4 < 8)
		{
			float num5 = (float)(8 - num4) / 8f * 0.05f;
			val2 += impactAngleVect * num5;
			num -= num5;
		}
		float num6 = Rand.Range(0, 45);
		Vector3 val3 = default(Vector3);
		((Vector3)(ref val3))._002Ector(num, 1f, num);
		Matrix4x4 val4 = default(Matrix4x4);
		((Matrix4x4)(ref val4)).SetTRS(val2, Quaternion.AngleAxis(num6, Vector3.up), val3);
		MatPropertyBlock.SetColor(ShaderPropertyIDs.Color, val);
		Graphics.DrawMesh(MeshPool.plane10, val4, BaseBubbleMat, 0, (Camera)null, 0, MatPropertyBlock);
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Collections.Look<Thing, int>(ref affectedThings, "affectedThings", (LookMode)3, (LookMode)1, ref affectedThingsKeysWorkingList, ref affectedThingsValuesWorkingList, true, false, false);
		Scribe_Values.Look<int>(ref ticksToRecharge, "ticksToRecharge", 0, false);
		Scribe_Values.Look<float>(ref energy, "energy", 0f, false);
		Scribe_Values.Look<int>(ref shieldBuffer, "shieldBuffer", 0, false);
		Scribe_Values.Look<bool>(ref active, "active", false, false);
		Scribe_Values.Look<int>(ref lastTimeActivated, "lastTimeActivated", 0, false);
		Scribe_Values.Look<int>(ref lastTimeDisabled, "lastTimeDisabled", 0, false);
		Scribe_Values.Look<int>(ref lastTimeDisarmed, "lastTimeDisarmed", 0, false);
		Scribe_Values.Look<bool>(ref toggleIsActive, "toggleIsActive", true, false);
		Scribe_Values.Look<bool>(ref initialized, "initialized", false, false);
	}

	public bool CanActivateShield()
	{
		if (Props.manualActivation && lastTimeDisabled > 0 && Find.TickManager.TicksGame - lastTimeDisabled < Props.cooldownTicks)
		{
			return false;
		}
		if (Props.disarmedByEmpForTicks != -1 && lastTimeDisarmed > 0 && Find.TickManager.TicksGame - lastTimeDisarmed < Props.disarmedByEmpForTicks)
		{
			return false;
		}
		return true;
	}

	public override IEnumerable<Gizmo> CompGetWornGizmosExtra()
	{
		if (HostThing.Faction == Faction.OfPlayer)
		{
			if (!Indestructible && Find.Selector.SingleSelectedThing == HostThing)
			{
				yield return (Gizmo)(object)new Gizmo_EnergyShieldGeneratorStatus
				{
					shieldGenerator = this
				};
			}
			if (Props.manualActivation)
			{
				Command_ActionWithCooldown obj = new Command_ActionWithCooldown(lastTimeDisabled, Props.cooldownTicks)
				{
					defaultLabel = TaggedString.op_Implicit(Translator.Translate(Props.activationLabelKey)),
					defaultDesc = TaggedString.op_Implicit(Translator.Translate(Props.activationDescKey)),
					icon = (Texture)(object)ContentFinder<Texture2D>.Get(Props.activationIconTexPath, true),
					action = delegate
					{
						lastTimeActivated = Find.TickManager.TicksGame;
						lastTimeDisabled = 0;
						active = true;
					}
				};
				((Gizmo)obj).Disabled = ManuallyActivated || !CanActivateShield();
				yield return (Gizmo)(object)obj;
			}
		}
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
	}

	public override string CompInspectStringExtra()
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
		if (!active)
		{
			TaggedString val = Translator.Translate("InactiveFacility");
			stringBuilder.AppendLine(TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()));
		}
		stringBuilder.AppendLine(((ThingComp)this).CompInspectStringExtra());
		return GenText.TrimEndNewlines(stringBuilder.ToString());
	}

	public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
	{
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		if (((DamageInfo)(ref dinfo)).Def == DamageDefOf.EMP && !Indestructible)
		{
			if (Props.disarmedByEmpForTicks != -1)
			{
				BreakShield(dinfo);
			}
			else
			{
				Energy = 0f;
			}
		}
		((ThingComp)this).PostPreApplyDamage(ref dinfo, ref absorbed);
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		Initialize();
	}

	public override void Notify_Equipped(Pawn pawn)
	{
		((ThingComp)this).Notify_Equipped(pawn);
		Initialize();
	}

	public void Initialize()
	{
		if (base.parent == null)
		{
			return;
		}
		if (Props == null)
		{
			ModContentPack modContentPack = ((Def)((Thing)base.parent).def).modContentPack;
			string text = ((modContentPack != null) ? modContentPack.Name : null);
			string text2 = ((object)((Thing)base.parent).def)?.ToString() + " has " + ((object)this).GetType()?.ToString() + " but lacks CompProperties_ShieldField properties. It must be set in XML in order to work.";
			if (!GenText.NullOrEmpty(text))
			{
				text2 = text2 + " Report about it to " + text + " author";
			}
			Log.Error(text2);
		}
		if (HostThing.Map != null)
		{
			if (!listerShieldGensByMaps.TryGetValue(HostThing.Map, out var value))
			{
				value = (listerShieldGensByMaps[HostThing.Map] = new List<CompShieldField>());
			}
			if (!value.Contains(this))
			{
				value.Add(this);
			}
			UpdateShieldCoverage(forcedRecache: true);
		}
		if (!initialized)
		{
			if (!Indestructible)
			{
				energy = MaxEnergy * Props.initialEnergyPercentage;
			}
			initialized = true;
		}
	}

	private void UpdateShieldCoverage(bool forcedRecache)
	{
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		if (HostThing.Map != null && (coveredCells == null || forcedRecache || !((IntVec3)(ref lastCachedCells)).IsValid || lastCachedCells != HostThing.Position || !Mathf.Approximately(lastCachedShieldRadius, ShieldRadius) || Gen.IsHashIntervalTick(HostThing, 30000, 15)))
		{
			coveredCells = new HashSet<IntVec3>(from x in GenRadial.RadialCellsAround(HostThing.Position, ShieldRadius, true)
				where GenGrid.InBounds(x, HostThing.Map)
				select x);
			if (ShieldRadius < 6f)
			{
				scanCells = coveredCells;
			}
			else
			{
				scanCells = new HashSet<IntVec3>(GenRadial.RadialCellsAround(HostThing.Position, ShieldRadius - 5f, ShieldRadius));
			}
			lastCachedCells = HostThing.Position;
			lastCachedShieldRadius = ShieldRadius;
		}
	}

	public bool ThreatDisabled(IAttackTargetSearcher disabledFor)
	{
		if (!Indestructible && Energy == 0f)
		{
			return true;
		}
		if (!VerbUtility.IsEMP(disabledFor.CurrentEffectiveVerb))
		{
			return true;
		}
		return !CanFunction;
	}

	public override void CompTick()
	{
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		if (Gen.IsHashIntervalTick((Thing)(object)base.parent, 15))
		{
			UpdateCache();
		}
		if (Props.workingTimeTicks != -1 && lastTimeActivated > 0 && Find.TickManager.TicksGame - lastTimeActivated >= Props.workingTimeTicks)
		{
			lastTimeDisabled = Find.TickManager.TicksGame;
			lastTimeActivated = 0;
		}
		if (ReactivatedThisTick && Props.reactivateEffect != null)
		{
			Effecter val = new Effecter(Props.reactivateEffect);
			val.Trigger(TargetInfo.op_Implicit((Thing)(object)base.parent), TargetInfo.Invalid, -1);
			val.Cleanup();
		}
		if (CanFunction)
		{
			if (!Indestructible)
			{
				if (ticksToRecharge > 0)
				{
					ticksToRecharge--;
					if (ticksToRecharge == 0 && Props.rechargeRateStat == null)
					{
						Energy = MaxEnergy;
					}
				}
				else
				{
					Energy += EnergyGainPerTick;
				}
			}
			if (active)
			{
				if (Props.activeSound != null)
				{
					if (sustainer == null || sustainer.Ended)
					{
						sustainer = SoundStarter.TrySpawnSustainer(Props.activeSound, SoundInfo.InMap(TargetInfo.op_Implicit(HostThing), (MaintenanceType)0));
					}
					Sustainer obj = sustainer;
					if (obj != null)
					{
						obj.Maintain();
					}
				}
				if (PowerTraderComp != null)
				{
					PowerTraderComp.PowerOutput = 0f - ((CompPower)PowerTraderComp).Props.PowerConsumption;
				}
				if (Energy > 0f || Indestructible)
				{
					EnergyShieldTick();
				}
			}
			else if (PowerTraderComp != null)
			{
				PowerTraderComp.PowerOutput = 0f - Props.inactivePowerConsumption;
			}
			if (Props.activeSound != null && !active && sustainer != null && !sustainer.Ended)
			{
				sustainer.End();
			}
		}
		else if (PowerTraderComp != null)
		{
			PowerTraderComp.PowerOutput = 0f - Props.inactivePowerConsumption;
		}
		((ThingComp)this).CompTick();
	}

	private void BreakShield(DamageInfo dinfo)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		float fTheta;
		Vector3 center;
		if (active)
		{
			SoundStarter.PlayOneShot(VEFDefOf.EnergyShield_Broken, SoundInfo.op_Implicit(new TargetInfo(HostThing)));
			int num = Mathf.CeilToInt(ShieldRadius * 2f);
			fTheta = (float)Math.PI * 2f / (float)num;
			center = GenThing.TrueCenter(HostThing);
			for (int i = 0; i < num; i++)
			{
				FleckMaker.ConnectingLine(PosAtIndex(i), PosAtIndex((i + 1) % num), FleckDefOf.LineEMP, HostThing.Map, 1.5f);
			}
		}
		Thing hostThing = HostThing;
		Pawn val = (Pawn)(object)((hostThing is Pawn) ? hostThing : null);
		if (val != null)
		{
			((DamageInfo)(ref dinfo)).SetAmount((float)Props.disarmedByEmpForTicks / 30f);
			val.stances.stunner.Notify_DamageApplied(dinfo);
		}
		if (!Indestructible)
		{
			Energy = 0f;
		}
		lastTimeDisarmed = Find.TickManager.TicksGame;
		Vector3 PosAtIndex(int index)
		{
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			return new Vector3(ShieldRadius * Mathf.Cos(fTheta * (float)index) + center.x, 0f, ShieldRadius * Mathf.Sin(fTheta * (float)index) + center.z);
		}
	}

	public bool WithinBoundary(IntVec3 sourcePos, IntVec3 checkedPos)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		if (!coveredCells.Contains(sourcePos) || !coveredCells.Contains(checkedPos))
		{
			if (!coveredCells.Contains(sourcePos))
			{
				return !coveredCells.Contains(checkedPos);
			}
			return false;
		}
		return true;
	}

	private float EnergyLossMultiplier(DamageDef damageDef)
	{
		if (damageDef == DamageDefOf.EMP)
		{
			return 4f;
		}
		return 1f;
	}

	private void EnergyShieldTick()
	{
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		(HashSet<Thing>, List<Thing>) thingsInAreas = GetThingsInAreas();
		foreach (Thing item in thingsInAreas.Item2)
		{
			Projectile val = (Projectile)(object)((item is Projectile) ? item : null);
			if (val != null && val.BlockableByShield(this) && !thingsInAreas.Item1.Contains(val.Launcher))
			{
				if (!(val is Projectile_Explosive) || ((Thing)val).def.projectile.damageDef == DamageDefOf.EMP)
				{
					float amount = val.DamageAmount;
					DamageDef damageDef = ((Thing)val).def.projectile.damageDef;
					Quaternion exactRotation = val.ExactRotation;
					AbsorbDamage(amount, damageDef, ((Quaternion)(ref exactRotation)).eulerAngles.y);
				}
				IntVec3 position = ((Thing)val).Position;
				IntVec3 val2 = HostThing.Position - ((Thing)val).Position;
				Rot4 val3 = Rot4.FromAngleFlat(((IntVec3)(ref val2)).AngleFlat);
				val3 = ((Rot4)(ref val3)).Opposite;
				((Thing)val).Position = position + ((Rot4)(ref val3)).FacingCell;
				NonPublicFields.Projectile_usedTarget.Invoke(val) = new LocalTargetInfo(((Thing)val).Position);
				NonPublicMethods.Projectile_ImpactSomething(val);
			}
		}
	}

	private void Notify_EnergyDepleted()
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		SoundStarter.PlayOneShot(VEFDefOf.EnergyShield_Broken, SoundInfo.op_Implicit(new TargetInfo(HostThing.Position, HostThing.Map, false)));
		FleckMaker.Static(GenThing.TrueCenter(HostThing), HostThing.Map, FleckDefOf.ExplosionFlash, 12f);
		for (int i = 0; i < 6; i++)
		{
			FleckMaker.ThrowDustPuff(GenThing.TrueCenter(HostThing) + Vector3Utility.HorizontalVectorFromAngle((float)Rand.Range(0, 360)) * Rand.Range(0.3f, 0.6f), HostThing.Map, Rand.Range(0.8f, 1.2f));
		}
		ticksToRecharge = Props.rechargeTicksWhenDepleted;
	}

	private void UpdateCache()
	{
		Thing hostThing = HostThing;
		if (((hostThing != null) ? hostThing.Map : null) == null)
		{
			return;
		}
		UpdateShieldCoverage(forcedRecache: false);
		if (affectedThings == null)
		{
			affectedThings = new Dictionary<Thing, int>();
		}
		List<Thing> list = null;
		foreach (KeyValuePair<Thing, int> affectedThing in affectedThings)
		{
			if (affectedThing.Value <= 0)
			{
				if (list == null)
				{
					list = new List<Thing>();
				}
				list.Add(affectedThing.Key);
			}
			else
			{
				affectedThings[affectedThing.Key] = affectedThing.Value - 15;
			}
		}
		if (list != null)
		{
			for (int i = 0; i < list.Count; i++)
			{
				affectedThings.Remove(list[i]);
			}
		}
		bool flag = ShouldBeActive();
		if (!Props.manualActivation && CanFunction)
		{
			active = CanFunction && (Props.activeAlways || flag || shieldBuffer > 0);
		}
		if (active)
		{
			active = CanActivateShield();
		}
		if (flag && shieldBuffer < 15)
		{
			shieldBuffer = 15;
		}
		else
		{
			shieldBuffer--;
		}
		bool ShouldBeActive()
		{
			if ((HostFaction != null && GenHostility.AnyHostileActiveThreatTo(HostThing.Map, HostFaction, false, false)) || GenCollection.Any<Thing>(HostThing.Map.listerThings.ThingsOfDef(VEFDefOf.Tornado)))
			{
				return true;
			}
			return HostThing.Map.listerThings.ThingsInGroup((ThingRequestGroup)60).Where(IsValidProjectile).Concat(HostThing.Map.listerThings.ThingsInGroup((ThingRequestGroup)43).Where(IsValidTransporter))
				.Any();
		}
	}

	private bool IsValidProjectile(Thing t)
	{
		Projectile val = (Projectile)(object)((t is Projectile) ? t : null);
		if (val == null)
		{
			return false;
		}
		if (val.Launcher == null)
		{
			return false;
		}
		if (HostThing.Faction == null)
		{
			return false;
		}
		if (val.BlockableByShield(this))
		{
			return GenHostility.HostileTo(val.Launcher, HostThing.Faction);
		}
		return false;
	}

	private bool IsValidTransporter(Thing t)
	{
		DropPodIncoming val = (DropPodIncoming)(object)((t is DropPodIncoming) ? t : null);
		if (val != null)
		{
			List<Pawn> list = ((IEnumerable<Thing>)((Skyfaller)val).innerContainer).Where((Thing thing) => thing is Pawn).Cast<Pawn>().ToList();
			foreach (ActiveTransporter item in ((IEnumerable<Thing>)((Skyfaller)val).innerContainer).Where((Thing thing) => thing is ActiveTransporter).Cast<ActiveTransporter>().ToList())
			{
				List<Pawn> collection = ((IEnumerable<Thing>)item.Contents.innerContainer).Where((Thing thing) => thing is Pawn).Cast<Pawn>().ToList();
				list.AddRange(collection);
			}
			if (GenCollection.Any<Pawn>(list.Where((Pawn pawn) => GenHostility.HostileTo((Thing)(object)pawn, HostThing.Faction)).ToList()))
			{
				return true;
			}
		}
		return false;
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		ThingWithComps parent = base.parent;
		if ((parent is Apparel || parent is Pawn) ? true : false)
		{
			yield break;
		}
		foreach (Gizmo gizmo in GetGizmos())
		{
			yield return gizmo;
		}
	}

	public IEnumerable<Gizmo> GetGizmos()
	{
		if (HostThing.Faction == Faction.OfPlayer || DebugSettings.ShowDevGizmos)
		{
			if (!Indestructible && Find.Selector.SingleSelectedThing == base.parent)
			{
				yield return (Gizmo)(object)new Gizmo_EnergyShieldGeneratorStatus
				{
					shieldGenerator = this
				};
			}
			if (Props.toggleable)
			{
				yield return (Gizmo)new Command_Toggle
				{
					defaultLabel = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.toggleLabelKey, NamedArgument.op_Implicit(toggleIsActive ? Translator.Translate("On") : Translator.Translate("Off")))),
					defaultDesc = TaggedString.op_Implicit(Translator.Translate(Props.toggleDescKey)),
					icon = (Texture)(object)ContentFinder<Texture2D>.Get(Props.toggleIconPath, true),
					toggleAction = delegate
					{
						toggleIsActive = !toggleIsActive;
						UpdateCache();
					},
					isActive = () => toggleIsActive
				};
			}
			if (Props.manualActivation)
			{
				Command_ActionWithCooldown obj = new Command_ActionWithCooldown(lastTimeDisabled, Props.cooldownTicks)
				{
					defaultLabel = TaggedString.op_Implicit(Translator.Translate(Props.activationLabelKey)),
					defaultDesc = TaggedString.op_Implicit(Translator.Translate(Props.activationDescKey)),
					icon = (Texture)(object)ContentFinder<Texture2D>.Get(Props.activationIconTexPath, true),
					action = delegate
					{
						lastTimeActivated = Find.TickManager.TicksGame;
						lastTimeDisabled = 0;
						active = true;
					}
				};
				((Gizmo)obj).Disabled = ManuallyActivated || !CanActivateShield();
				yield return (Gizmo)(object)obj;
			}
		}
		if (!DebugSettings.ShowDevGizmos || HostThing.Map == null)
		{
			yield break;
		}
		yield return (Gizmo)new Command_Action
		{
			defaultLabel = "DEV: 0 energy",
			action = delegate
			{
				Energy = 0f;
			}
		};
		yield return (Gizmo)new Command_Action
		{
			defaultLabel = "DEV: 1 energy",
			action = delegate
			{
				Energy = 0.01f;
			}
		};
		yield return (Gizmo)new Command_Action
		{
			defaultLabel = "DEV: Max energy",
			action = delegate
			{
				Energy = MaxEnergy;
			}
		};
		yield return (Gizmo)new Command_Action
		{
			defaultLabel = "DEV: Flash interception cells",
			action = delegate
			{
				//IL_0010: Unknown result type (might be due to invalid IL or missing references)
				//IL_0015: Unknown result type (might be due to invalid IL or missing references)
				//IL_0026: Unknown result type (might be due to invalid IL or missing references)
				foreach (IntVec3 scanCell in scanCells)
				{
					HostThing.Map.debugDrawer.FlashCell(scanCell, 0f, (string)null, 150);
				}
			}
		};
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingComp)this).CompGetWornGizmosExtra();
	}
}
