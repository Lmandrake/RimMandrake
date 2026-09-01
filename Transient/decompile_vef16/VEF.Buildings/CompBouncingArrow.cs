using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

[StaticConstructorOnStartup]
public class CompBouncingArrow : ThingComp
{
	private static readonly Material ArrowMatWhite = MaterialPool.MatFrom("UI/Overlays/Arrow", ShaderDatabase.CutoutFlying, Color.white);

	public bool doBouncingArrow;

	public MapParent originalMapParent;

	private bool stopDrawing;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		CompProperties_BouncingArrow compProperties = ((Thing)base.parent).def.GetCompProperties<CompProperties_BouncingArrow>();
		if (compProperties != null && compProperties.startBouncingArrowUponSpawning)
		{
			doBouncingArrow = true;
		}
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostDeSpawn(map, mode);
		doBouncingArrow = false;
	}

	private void CheckStopDrawing()
	{
		if (!stopDrawing && originalMapParent != null)
		{
			ThingWithComps parent = base.parent;
			object obj;
			if (parent == null)
			{
				obj = null;
			}
			else
			{
				Map mapHeld = ((Thing)parent).MapHeld;
				obj = ((mapHeld != null) ? mapHeld.Parent : null);
			}
			if (obj != originalMapParent)
			{
				stopDrawing = true;
				doBouncingArrow = false;
			}
		}
		if (stopDrawing)
		{
			return;
		}
		ThingWithComps parent2 = base.parent;
		object obj2;
		if (parent2 == null)
		{
			obj2 = null;
		}
		else
		{
			Map mapHeld2 = ((Thing)parent2).MapHeld;
			obj2 = ((mapHeld2 != null) ? mapHeld2.Parent : null);
		}
		MapParent val = (MapParent)obj2;
		if (val == null || !val.Map.IsPlayerHome)
		{
			PocketMapParent val2 = (PocketMapParent)(object)((val is PocketMapParent) ? val : null);
			if (val2 == null || !val2.sourceMap.IsPlayerHome)
			{
				return;
			}
		}
		stopDrawing = true;
		doBouncingArrow = false;
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref doBouncingArrow, "doBouncingArrow", false, false);
		Scribe_References.Look<MapParent>(ref originalMapParent, "originalMapParent", false);
		Scribe_Values.Look<bool>(ref stopDrawing, "stopDrawing", false, false);
	}

	public override void PostDraw()
	{
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostDraw();
		if (!((Thing)base.parent).Spawned)
		{
			return;
		}
		CheckStopDrawing();
		if (doBouncingArrow && !stopDrawing)
		{
			int num = Find.TickManager.TicksGame % 1000;
			if (num < 500)
			{
				num = 1000 - num;
			}
			Vector3 val = ((Thing)base.parent).DrawPos + Vector3.forward * (1f + (float)num / 1000f);
			val.y = Altitudes.AltitudeFor((AltitudeLayer)34) + 1f;
			float num2 = 1f - (float)num / 2000f;
			Quaternion val2 = Quaternion.AngleAxis(180f, Vector3.up);
			ArrowMatWhite.color = new Color(1f, 1f, 1f, num2);
			Graphics.DrawMesh(MeshPool.plane10, val, val2, ArrowMatWhite, 0);
		}
	}
}
