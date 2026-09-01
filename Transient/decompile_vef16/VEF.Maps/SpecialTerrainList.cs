using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using UnityEngine;
using Verse;

namespace VEF.Maps;

public class SpecialTerrainList : MapComponent
{
	public List<TerrainInstance> terrainInstances = new List<TerrainInstance>();

	public Dictionary<IntVec3, TerrainInstance> terrains = new Dictionary<IntVec3, TerrainInstance>();

	public TerrainInstance[] terrainsArray;

	public HashSet<TerrainDef> terrainDefs = new HashSet<TerrainDef>();

	private bool dirty;

	private int index;

	private int cycles = 1;

	public SpecialTerrainList(Map map)
		: base(map)
	{
	}

	public override void ExposeData()
	{
		((MapComponent)this).ExposeData();
		Scribe_Collections.Look<IntVec3, TerrainInstance>(ref terrains, "terrains", (LookMode)1, (LookMode)2);
		terrainDefs = new HashSet<TerrainDef>((IEnumerable<TerrainDef>)terrains.Select((KeyValuePair<IntVec3, TerrainInstance> t) => t.Value.def).Distinct());
	}

	public override void MapComponentUpdate()
	{
		((MapComponent)this).MapComponentUpdate();
		foreach (KeyValuePair<IntVec3, TerrainInstance> terrain in terrains)
		{
			terrain.Value.Update();
		}
		foreach (TerrainDef terrainDef in terrainDefs)
		{
			if (((Def)terrainDef).modExtensions == null)
			{
				continue;
			}
			foreach (DefModExtension modExtension in ((Def)terrainDef).modExtensions)
			{
				if (modExtension is DefExtensionActive defExtensionActive)
				{
					defExtensionActive.DoWork(terrainDef);
				}
			}
		}
	}

	public void TerrainUpdate(long timeBudget)
	{
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Invalid comparison between Unknown and I4
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Invalid comparison between Unknown and I4
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Invalid comparison between Unknown and I4
		if (terrains.Count == 0)
		{
			return;
		}
		Stopwatch stopwatch = new Stopwatch();
		TerrainInstance[] array;
		if (terrainsArray == null || terrainsArray?.Length != terrains.Count || dirty)
		{
			array = (terrainsArray = terrains.Select((KeyValuePair<IntVec3, TerrainInstance> p) => p.Value).ToArray());
			index = 0;
			dirty = false;
		}
		else
		{
			array = terrainsArray;
		}
		int num = index;
		int num2 = 0;
		while (stopwatch.ElapsedTicks < timeBudget && num2 < array.Length / 6)
		{
			if (num >= array.Length)
			{
				num = 0;
				cycles++;
			}
			TerrainInstance terrainInstance = array[num];
			if ((int)terrainInstance.def.tickerType == 1)
			{
				terrainInstance.Tick();
			}
			else if ((int)terrainInstance.def.tickerType == 2 && cycles % 35 == 0)
			{
				terrainInstance.TickRare();
			}
			else if ((int)terrainInstance.def.tickerType == 3 && cycles % 250 == 0)
			{
				terrainInstance.TickLong();
			}
			num++;
			num2++;
		}
		stopwatch.Stop();
		index = num;
		if (Prefs.DevMode && Prefs.LogVerbose)
		{
			Log.Message($"ReGrowther: ticked {num2} out of {array.Length} in {stopwatch.ElapsedMilliseconds} ms and Cycled to {cycles}");
		}
	}

	public override void FinalizeInit()
	{
		((MapComponent)this).FinalizeInit();
		RefreshAllCurrentTerrain();
		CallPostLoad();
	}

	public void CallPostLoad()
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		foreach (IntVec3 key in terrains.Keys)
		{
			terrains[key].PostLoad();
		}
	}

	public void RefreshAllCurrentTerrain()
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		Reset();
		foreach (IntVec3 item in base.map)
		{
			if (base.map.terrainGrid.TerrainAt(item) is ActiveTerrainDef special)
			{
				RegisterAt(special, item);
			}
		}
	}

	public void RegisterAt(ActiveTerrainDef special, int i)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		RegisterAt(special, ((CellIndices)(ref base.map.cellIndices)).IndexToCell(i));
	}

	public void RegisterAt(ActiveTerrainDef special, IntVec3 cell)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		if (!terrains.ContainsKey(cell))
		{
			TerrainInstance terrainInstance = special.MakeTerrainInstance(base.map, cell);
			terrainInstance.Init();
			terrainInstances.Add(terrainInstance);
			terrains.Add(cell, terrainInstance);
			terrainDefs.Add((TerrainDef)(object)special);
			FixAt(terrainInstances.Count);
		}
	}

	public void Notify_RemovedTerrainAt(IntVec3 c)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		TerrainInstance terrainInstance = terrains[c];
		FixAt(terrainInstances.IndexOf(terrainInstance));
		terrains.Remove(c);
		terrainInstances.Remove(terrainInstance);
		terrainsArray = terrainInstances.ToArray();
		terrainInstance.PostRemove();
	}

	public int FixAt(int i = -1)
	{
		dirty = true;
		if (i != -1)
		{
			if (i >= index)
			{
				return i;
			}
			index = Mathf.Max(i - 1, 0);
		}
		return i;
	}

	public void Reset()
	{
		dirty = true;
		index = 0;
	}
}
