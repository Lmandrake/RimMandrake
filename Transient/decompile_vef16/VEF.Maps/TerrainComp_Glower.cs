using System;
using RimWorld;
using Verse;

namespace VEF.Maps;

public class TerrainComp_Glower : TerrainComp
{
	[Unsaved(false)]
	protected bool currentlyOn;

	[Unsaved(false)]
	private CompGlower instanceGlowerComp;

	private ColorInt colorInt;

	private float glowRadius;

	private float overlightRadius;

	public CompGlower AsThingComp
	{
		get
		{
			if (instanceGlowerComp != null)
			{
				return instanceGlowerComp;
			}
			return instanceGlowerComp = (CompGlower)this;
		}
	}

	public TerrainCompProperties_Glower Props => (TerrainCompProperties_Glower)props;

	public virtual bool ShouldBeLitNow
	{
		get
		{
			TerrainComp_PowerTrader comp = parent.GetComp<TerrainComp_PowerTrader>();
			if (comp != null && !comp.PowerOn)
			{
				return !Props.powered;
			}
			return true;
		}
	}

	public float OverlightRadius
	{
		get
		{
			return overlightRadius;
		}
		set
		{
			overlightRadius = value;
		}
	}

	public float GlowRadius
	{
		get
		{
			return glowRadius;
		}
		set
		{
			glowRadius = value;
		}
	}

	public ColorInt Color
	{
		get
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			return colorInt;
		}
		set
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			colorInt = value;
		}
	}

	public void UpdateLit()
	{
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		bool shouldBeLitNow = ShouldBeLitNow;
		if (currentlyOn != shouldBeLitNow)
		{
			currentlyOn = shouldBeLitNow;
			parent.Map.mapDrawer.MapMeshDirty(parent.Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things));
			(currentlyOn ? new Action<CompGlower>(parent.Map.glowGrid.RegisterGlower) : new Action<CompGlower>(parent.Map.glowGrid.DeRegisterGlower))(AsThingComp);
		}
	}

	public override void ReceiveCompSignal(string sig)
	{
		base.ReceiveCompSignal(sig);
		if (sig == CompSignals.PowerTurnedOff || sig == CompSignals.PowerTurnedOn)
		{
			UpdateLit();
		}
	}

	public override void PostPostLoad()
	{
		UpdateLit();
		if (ShouldBeLitNow)
		{
			parent.Map.glowGrid.RegisterGlower(AsThingComp);
		}
	}

	public override void PostRemove()
	{
		base.PostRemove();
		parent.Map.glowGrid.DeRegisterGlower(AsThingComp);
	}

	public override void Initialize(TerrainCompProperties props)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		base.Initialize(props);
		Color = Props.glowColor;
		GlowRadius = Props.glowRadius;
		OverlightRadius = Props.overlightRadius;
	}

	public static explicit operator CompGlower(TerrainComp_Glower inst)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Expected O, but got Unknown
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Expected O, but got Unknown
		//IL_0065: Expected O, but got Unknown
		CompGlower val = new CompGlower
		{
			parent = (ThingWithComps)ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.Steel)
		};
		((Thing)((ThingComp)val).parent).SetPositionDirect(inst.parent.Position);
		((ThingComp)val).Initialize((CompProperties)new CompProperties_Glower
		{
			glowColor = inst.Color,
			glowRadius = inst.GlowRadius,
			overlightRadius = inst.OverlightRadius
		});
		return val;
	}
}
