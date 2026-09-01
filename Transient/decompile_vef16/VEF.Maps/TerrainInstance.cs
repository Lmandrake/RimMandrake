using System;
using System.Collections.Generic;
using Verse;

namespace VEF.Maps;

public class TerrainInstance : IExposable
{
	public ActiveTerrainDef def;

	public List<TerrainComp> comps = new List<TerrainComp>();

	private Map mapInt;

	private IntVec3 positionInt;

	public Map Map
	{
		get
		{
			return mapInt;
		}
		set
		{
			mapInt = value;
		}
	}

	public IntVec3 Position
	{
		get
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			return positionInt;
		}
		set
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			positionInt = value;
		}
	}

	public virtual string Label
	{
		get
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			TaggedString val = ((Def)def).LabelCap;
			for (int i = 0; i < comps.Count; i++)
			{
				val = TaggedString.op_Implicit(comps[i].TransformLabel(TaggedString.op_Implicit(val)));
			}
			return TaggedString.op_Implicit(val);
		}
	}

	public virtual void Init()
	{
		InitializeComps();
	}

	public T GetComp<T>() where T : TerrainComp
	{
		for (int i = 0; i < comps.Count; i++)
		{
			if (comps[i] is T result)
			{
				return result;
			}
		}
		return null;
	}

	public void InitializeComps()
	{
		foreach (TerrainCompProperties terrainComp2 in def.terrainComps)
		{
			TerrainComp terrainComp = (TerrainComp)Activator.CreateInstance(terrainComp2.compClass);
			terrainComp.parent = this;
			comps.Add(terrainComp);
			terrainComp.Initialize(terrainComp2);
		}
	}

	public virtual void Tick()
	{
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].CompTick();
		}
	}

	public virtual void TickRare()
	{
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].CompTick();
		}
	}

	public virtual void TickLong()
	{
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].CompTick();
		}
	}

	public virtual void Update()
	{
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].CompUpdate();
		}
	}

	public virtual void PostPlacedDown()
	{
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].PlaceSetup();
		}
	}

	public virtual void PostRemove()
	{
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].PostRemove();
		}
	}

	public virtual void PostLoad()
	{
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].PostPostLoad();
		}
	}

	public virtual void BroadcastCompSignal(string sig)
	{
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].ReceiveCompSignal(sig);
		}
	}

	public virtual void ExposeData()
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Invalid comparison between Unknown and I4
		Scribe_References.Look<Map>(ref mapInt, "map", false);
		Scribe_Values.Look<IntVec3>(ref positionInt, "pos", default(IntVec3), false);
		Scribe_Defs.Look<ActiveTerrainDef>(ref def, "def");
		if ((int)Scribe.mode == 2)
		{
			InitializeComps();
		}
		for (int i = 0; i < comps.Count; i++)
		{
			comps[i].PostExposeData();
		}
	}
}
