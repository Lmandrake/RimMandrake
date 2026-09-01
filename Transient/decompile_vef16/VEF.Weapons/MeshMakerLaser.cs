using System.Collections.Generic;
using UnityEngine;

namespace VEF.Weapons;

public static class MeshMakerLaser
{
	private static int textureSeamPrecision = 256;

	private static int geometrySeamPrecision = 512;

	private static Dictionary<int, Mesh> cachedMeshes = new Dictionary<int, Mesh>();

	public static Mesh Mesh(float st, float sv)
	{
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		//IL_014a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0214: Unknown result type (might be due to invalid IL or missing references)
		//IL_0225: Unknown result type (might be due to invalid IL or missing references)
		//IL_022a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0245: Unknown result type (might be due to invalid IL or missing references)
		//IL_024b: Expected O, but got Unknown
		if (st < 0f)
		{
			st = 0f;
		}
		if (st > 0.5f)
		{
			st = 0.5f;
		}
		if (sv < 0f)
		{
			sv = 0f;
		}
		if (sv > 0.5f)
		{
			sv = 0.5f;
		}
		int num = (int)(st / 0.5f * (float)textureSeamPrecision);
		int num2 = (int)(sv / 0.5f * (float)geometrySeamPrecision);
		int key = num2 + (textureSeamPrecision + 1) * geometrySeamPrecision;
		if (cachedMeshes.TryGetValue(key, out var value))
		{
			return value;
		}
		st = 0.5f * (float)num / (float)textureSeamPrecision;
		sv = 0.5f * (float)num2 / (float)geometrySeamPrecision;
		float num3 = 1f - st;
		float num4 = 0.5f - sv;
		Vector3[] vertices = (Vector3[])(object)new Vector3[8]
		{
			new Vector3(-0.5f, 0f, -0.5f),
			new Vector3(-0.5f, 0f, 0f - num4),
			new Vector3(0.5f, 0f, 0f - num4),
			new Vector3(0.5f, 0f, -0.5f),
			new Vector3(-0.5f, 0f, num4),
			new Vector3(0.5f, 0f, num4),
			new Vector3(-0.5f, 0f, 0.5f),
			new Vector3(0.5f, 0f, 0.5f)
		};
		Vector2[] uv = (Vector2[])(object)new Vector2[8]
		{
			new Vector2(0f, 0f),
			new Vector2(0f, st),
			new Vector2(1f, st),
			new Vector2(1f, 0f),
			new Vector2(0f, num3),
			new Vector2(1f, num3),
			new Vector2(0f, 1f),
			new Vector2(1f, 1f)
		};
		int[] array = new int[18]
		{
			0, 1, 2, 0, 2, 3, 1, 4, 5, 1,
			5, 2, 4, 6, 7, 4, 7, 5
		};
		value = new Mesh();
		((Object)value).name = "NewLaserMesh()";
		value.vertices = vertices;
		value.uv = uv;
		value.SetTriangles(array, 0);
		value.RecalculateNormals();
		value.RecalculateBounds();
		cachedMeshes[key] = value;
		return value;
	}
}
