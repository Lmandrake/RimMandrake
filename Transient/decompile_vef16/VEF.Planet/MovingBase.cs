using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Planet;

[HotSwappable]
[StaticConstructorOnStartup]
public class MovingBase : MapParent
{
	public MovingBase_PathFollower pather;

	public MovingBase_Tweener tweener;

	private Material cachedMat;

	public static readonly Texture2D AttackCommand = ContentFinder<Texture2D>.Get("UI/Commands/AttackSettlement", true);

	public override Vector3 DrawPos => tweener.TweenedPos;

	public MovingBaseDef def => ((WorldObject)this).def as MovingBaseDef;

	public override Material Material
	{
		get
		{
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			if ((Object)(object)cachedMat == (Object)null)
			{
				cachedMat = MaterialPool.MatFrom(((WorldObject)this).def.expandingIconTexture, ShaderDatabase.WorldOverlayTransparentLit, ((WorldObject)this).Faction.Color, 3550);
			}
			return cachedMat;
		}
	}

	public override Texture2D ExpandingIcon
	{
		get
		{
			if (!pather.Moving)
			{
				return ContentFinder<Texture2D>.Get(((WorldObject)this).def.texture, true);
			}
			return ((WorldObject)this).ExpandingIcon;
		}
	}

	public int TicksPerMove => def.ticksPerMove;

	public virtual bool Attackable => true;

	public MovingBase()
	{
		pather = new MovingBase_PathFollower(this);
		tweener = new MovingBase_Tweener(this);
	}

	public override bool ShouldRemoveMapNow(out bool alsoRemoveWorldObject)
	{
		alsoRemoveWorldObject = false;
		if (!((MapParent)this).Map.IsPlayerHome)
		{
			return !((MapParent)this).Map.mapPawns.AnyPawnBlockingMapRemoval;
		}
		return false;
	}

	public override IEnumerable<Gizmo> GetCaravanGizmos(Caravan caravan)
	{
		foreach (Gizmo item in _003C_003En__0(caravan))
		{
			yield return item;
		}
		if (Attackable)
		{
			Command_Action val = new Command_Action();
			((Command)val).icon = (Texture)(object)AttackCommand;
			((Command)val).defaultLabel = TaggedString.op_Implicit(Translator.Translate("CommandAttackSettlement"));
			((Command)val).defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.CommandAttackMovingBaseDesc", NamedArgument.op_Implicit(((Def)def).label)));
			val.action = delegate
			{
				Attack(caravan);
			};
			yield return (Gizmo)(object)val;
		}
	}

	public void Attack(Caravan caravan)
	{
		if (((MapParent)this).HasMap)
		{
			LongEventHandler.QueueLongEvent((Action)delegate
			{
				AttackNow(caravan);
			}, "GeneratingMapForNewEncounter", false, (Action<Exception>)null, true, false, (Action)null);
		}
		else
		{
			AttackNow(caravan);
		}
	}

	private void AttackNow(Caravan caravan)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		bool mapWasGenerated = !((MapParent)this).HasMap;
		Map orGenerateMap = GetOrGenerateMapUtility.GetOrGenerateMap(((WorldObject)this).Tile, (WorldObjectDef)null, (IEnumerable<GenStepWithParams>)null);
		DoMapGeneration(caravan, mapWasGenerated, orGenerateMap);
	}

	protected virtual void DoMapGeneration(Caravan caravan, bool mapWasGenerated, Map map)
	{
	}

	public MovingBase BaseVisitedNow(Caravan caravan)
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		if (!((WorldObject)caravan).Spawned || caravan.pather.Moving)
		{
			return null;
		}
		List<MovingBase> list = (from x in Find.WorldObjects.AllWorldObjects.OfType<MovingBase>()
			where x.def == def
			select x).ToList();
		for (int i = 0; i < list.Count; i++)
		{
			MovingBase movingBase = list[i];
			if (((WorldObject)movingBase).Tile == ((WorldObject)caravan).Tile)
			{
				return movingBase;
			}
		}
		return null;
	}

	public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Caravan caravan)
	{
		foreach (FloatMenuOption item in _003C_003En__1(caravan))
		{
			yield return item;
		}
		foreach (FloatMenuOption item2 in GetFloatMenuOptions_MovingBase(caravan))
		{
			yield return item2;
		}
	}

	protected virtual IEnumerable<FloatMenuOption> GetFloatMenuOptions_MovingBase(Caravan caravan)
	{
		foreach (FloatMenuOption floatMenuOption in CaravanArrivalAction_AttackMovingBase.GetFloatMenuOptions(caravan, this))
		{
			yield return floatMenuOption;
		}
	}

	public override void SpawnSetup()
	{
		((WorldObject)this).SpawnSetup();
		tweener.ResetTweenedPosToRoot();
	}

	public PlanetTile BestGotoDestNear(PlanetTile tile)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		Predicate<PlanetTile> predicate = (PlanetTile t) => !Find.World.Impassable(t) && CanReach(tile);
		if (predicate(tile))
		{
			return tile;
		}
		PlanetTile result = default(PlanetTile);
		GenWorldClosest.TryFindClosestTile(tile, predicate, ref result, 50, true);
		return result;
	}

	public bool CanReach(PlanetTile tile)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		return Find.WorldReachability.CanReach(((WorldObject)this).Tile, tile);
	}

	public override void PostRemove()
	{
		((MapParent)this).PostRemove();
		pather.StopDead();
	}

	protected override void TickInterval(int delta)
	{
		((MapParent)this).TickInterval(delta);
		if (!((MapParent)this).HasMap)
		{
			pather.PatherTick(delta);
			if (Gen.IsHashIntervalTick((WorldObject)(object)this, 30, delta))
			{
				tweener.TweenerTick();
			}
		}
	}

	public override void ExposeData()
	{
		((MapParent)this).ExposeData();
		Scribe_Deep.Look<MovingBase_PathFollower>(ref pather, "pather", new object[1] { this });
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0(Caravan caravan)
	{
		return ((WorldObject)this).GetCaravanGizmos(caravan);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<FloatMenuOption> _003C_003En__1(Caravan caravan)
	{
		return ((MapParent)this).GetFloatMenuOptions(caravan);
	}
}
