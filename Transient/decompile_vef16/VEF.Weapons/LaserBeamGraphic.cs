using System;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

internal class LaserBeamGraphic : Thing
{
	public LaserBeam laserBeam;

	private int ticks;

	private int colorIndex = 2;

	private Vector3 a;

	private Vector3 b;

	public Matrix4x4 drawingMatrix;

	private Material materialBeam;

	private Mesh mesh;

	public LaserBeamDef LaserBeamDef => ((Thing)(laserBeam?)).def as LaserBeamDef;

	public float Opacity => (float)Math.Sin(Math.Pow(1.0 - 1.0 * (double)ticks / (double)LaserBeamDef.lifetime, LaserBeamDef.impulse) * Math.PI);

	public override void ExposeData()
	{
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		((Thing)this).ExposeData();
		Scribe_References.Look<LaserBeam>(ref laserBeam, "laserBeam", false);
		Scribe_Values.Look<int>(ref ticks, "ticks", 0, false);
		Scribe_Values.Look<int>(ref colorIndex, "colorIndex", 0, false);
		Scribe_Values.Look<Vector3>(ref a, "a", default(Vector3), false);
		Scribe_Values.Look<Vector3>(ref b, "b", default(Vector3), false);
	}

	protected override void Tick()
	{
		if (LaserBeamDef == null || ticks++ > LaserBeamDef.lifetime)
		{
			((Thing)this).Destroy((DestroyMode)0);
		}
	}

	private void SetColor(Thing launcher)
	{
		IBeamColorThing beamColorThing = null;
		Pawn val = (Pawn)(object)((launcher is Pawn) ? launcher : null);
		if (val != null && val.equipment != null)
		{
			beamColorThing = val.equipment.Primary as IBeamColorThing;
		}
		if (beamColorThing == null)
		{
			beamColorThing = launcher as IBeamColorThing;
		}
		if (beamColorThing != null && beamColorThing.BeamColor != -1)
		{
			colorIndex = beamColorThing.BeamColor;
		}
	}

	public void Setup(Thing launcher, Vector3 origin, Vector3 destination)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		SetColor(launcher);
		a = origin;
		b = destination;
	}

	public void SetupDrawing()
	{
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		if (!((Object)(object)mesh != (Object)null))
		{
			materialBeam = LaserBeamDef.GetBeamMaterial(colorIndex) ?? ((ThingDef)LaserBeamDef).graphicData.Graphic.MatSingle;
			if (((ThingDef)LaserBeamDef).graphicData.graphicClass == typeof(Graphic_Random))
			{
				materialBeam = LaserBeamDef.GetBeamMaterial(Rand.RangeInclusive(0, LaserBeamDef.materials.Count)) ?? ((ThingDef)LaserBeamDef).graphicData.Graphic.MatSingle;
			}
			float beamWidth = LaserBeamDef.beamWidth;
			Quaternion val = Quaternion.LookRotation(b - a);
			Vector3 val2 = b - a;
			_ = ((Vector3)(ref val2)).normalized;
			val2 = b - a;
			float magnitude = ((Vector3)(ref val2)).magnitude;
			Vector3 val3 = default(Vector3);
			((Vector3)(ref val3))._002Ector(beamWidth, 1f, magnitude);
			Vector3 val4 = (a + b) / 2f;
			((Matrix4x4)(ref drawingMatrix)).SetTRS(val4, val, val3);
			float num = 1f * (float)materialBeam.mainTexture.width / (float)materialBeam.mainTexture.height;
			float num2 = ((LaserBeamDef.seam < 0f) ? num : LaserBeamDef.seam);
			float num3 = beamWidth / num / 2f * num2;
			float sv = ((magnitude <= num3 * 2f) ? 0.5f : (num3 * 2f / magnitude));
			mesh = MeshMakerLaser.Mesh(num2, sv);
		}
	}

	public override void SpawnSetup(Map map, bool respawningAfterLoad)
	{
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_018a: Unknown result type (might be due to invalid IL or missing references)
		//IL_018f: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a5: Unknown result type (might be due to invalid IL or missing references)
		((Thing)this).SpawnSetup(map, respawningAfterLoad);
		if (LaserBeamDef == null || LaserBeamDef.decorations == null || respawningAfterLoad)
		{
			return;
		}
		foreach (LaserBeamDecoration decoration in LaserBeamDef.decorations)
		{
			float num = decoration.spacing * LaserBeamDef.beamWidth;
			float num2 = decoration.initialOffset * LaserBeamDef.beamWidth;
			Vector3 val = b - a;
			Vector3 normalized = ((Vector3)(ref val)).normalized;
			float num3 = Vector3Utility.AngleFlat(b - a);
			Vector3 val2 = normalized * num;
			Vector3 val3 = a + val2 * 0.5f + normalized * num2;
			val = b - a;
			float num4 = ((Vector3)(ref val)).magnitude - num;
			int num5 = 0;
			while (num4 > 0f && ThingMaker.MakeThing(decoration.mote, (ThingDef)null) is MoteLaserDecoration moteLaserDecoration)
			{
				moteLaserDecoration.beam = this;
				((MoteThrown)moteLaserDecoration).airTimeLeft = LaserBeamDef.lifetime;
				((Mote)moteLaserDecoration).Scale = LaserBeamDef.beamWidth;
				((Mote)moteLaserDecoration).exactRotation = num3;
				((Mote)moteLaserDecoration).exactPosition = val3;
				((MoteThrown)moteLaserDecoration).SetVelocity(num3, decoration.speed);
				moteLaserDecoration.baseSpeed = decoration.speed;
				moteLaserDecoration.speedJitter = decoration.speedJitter;
				moteLaserDecoration.speedJitterOffset = decoration.speedJitterOffset * (float)num5;
				GenSpawn.Spawn((Thing)(object)moteLaserDecoration, IntVec3Utility.ToIntVec3(a), map, (WipeMode)0);
				val3 += val2;
				num4 -= num;
				num5++;
			}
		}
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		SetupDrawing();
		float opacity = Opacity;
		if (((ThingDef)LaserBeamDef).graphicData.graphicClass == typeof(Graphic_Flicker) && !Find.TickManager.Paused && Find.TickManager.TicksGame % LaserBeamDef.flickerFrameTime == 0)
		{
			materialBeam = LaserBeamDef.GetBeamMaterial(Rand.RangeInclusive(0, LaserBeamDef.materials.Count)) ?? ((ThingDef)LaserBeamDef).graphicData.Graphic.MatSingle;
		}
		Graphics.DrawMesh(mesh, drawingMatrix, FadedMaterialPool.FadedVersionOf(materialBeam, opacity), 0);
	}
}
